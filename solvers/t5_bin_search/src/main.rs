//! Zero-dependency Rust std-only binary Covering Array solver for t=5, v=2.
//!
//! Supports two modes:
//!   - `--mode comp`: Complement-symmetric mode (N = 2M, M <= 64, u64 columns, 16 canonical patterns/5-set)
//!   - `--mode free`: Unconstrained mode (N <= 128, u128 columns, 32 patterns/5-set)
//!
//! Search kernel: Bit-parallel Hamming-distance-1 focused candidate generation +
//! Tabu search with aspiration + PAWS/SWT clause weighting + optional step-down reduction.

use std::env;
use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

// ---------- Fast PRNG (SplitMix64 / Xoshiro256**) ----------

#[derive(Clone)]
struct Rng {
    s: [u64; 4],
}

impl Rng {
    fn new(mut seed: u64) -> Self {
        let mut s = [0u64; 4];
        for slot in &mut s {
            seed = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = seed;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            *slot = z ^ (z >> 31);
        }
        Self { s }
    }

    #[inline(always)]
    fn next_u64(&mut self) -> u64 {
        let result = self.s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        result
    }

    #[inline(always)]
    fn gen_range(&mut self, upper: usize) -> usize {
        debug_assert!(upper > 0);
        ((self.next_u64() as u128 * upper as u128) >> 64) as usize
    }
}

// ---------- Mode & Precomputed 5-Tuple Geometry ----------

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Mode {
    Comp,
    Free,
}

#[derive(Clone, Copy, Default)]
#[repr(C)]
struct Cell {
    cov: u8,
    w: u8,
}

/// Group of incident 5-tuples for a fixed column `c`, fixed (a, b, d), and contiguous range of `e`
/// that does not cross `c` (so bit positions of a, b, d, e, c are constant across the range).
#[derive(Clone, Copy)]
struct IncGroup {
    a: u8,
    b: u8,
    d: u8,
    e_start: u8,
    len: u8,
    sh_a: u8,
    sh_b: u8,
    sh_d: u8,
    sh_e: u8,
    sh_c: u8,
    tid_off: u32,
}

struct Geometry {
    k: usize,
    stride: usize, // 16 for Comp, 32 for Free
    num_tuples: usize,
    tuples: Vec<[u8; 5]>,
    inc_groups: Vec<Vec<IncGroup>>,
    inc_bases: Vec<Vec<u32>>, // pre-multiplied by stride!
}

impl Geometry {
    fn new(k: usize, mode: Mode) -> Self {
        assert!((5..=31).contains(&k), "k must be in 5..=31");
        let stride = match mode {
            Mode::Comp => 16,
            Mode::Free => 32,
        };

        // Enumerate all C(k, 5) sorted 5-tuples and assign dense IDs
        let mut tuples = Vec::new();
        let mut tid_map = std::collections::HashMap::new();
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    for c3 in (c2 + 1)..k {
                        for c4 in (c3 + 1)..k {
                            let id = tuples.len() as u32;
                            let t = [c0 as u8, c1 as u8, c2 as u8, c3 as u8, c4 as u8];
                            tuples.push(t);
                            tid_map.insert(t, id);
                        }
                    }
                }
            }
        }
        let num_tuples = tuples.len();

        let mut inc_groups = Vec::with_capacity(k);
        let mut inc_bases = Vec::with_capacity(k);

        for c in 0..k {
            let mut groups = Vec::new();
            let mut bases = Vec::new();
            for a in 0..k {
                if a == c {
                    continue;
                }
                for b in (a + 1)..k {
                    if b == c {
                        continue;
                    }
                    for d in (b + 1)..k {
                        if d == c {
                            continue;
                        }
                        // e ranges over (d+1)..k excluding c -> up to 2 contiguous segments
                        let segs: [(usize, usize); 2] = if c > d {
                            [(d + 1, c), (c + 1, k)]
                        } else {
                            [(d + 1, k), (k, k)]
                        };
                        for &(es, ee) in &segs {
                            if es >= ee {
                                continue;
                            }
                            // Determine sorted bit positions for (a, b, d, e, c) using representative e = es
                            let mut arr = [(a, 0u8), (b, 1u8), (d, 2u8), (es, 3u8), (c, 4u8)];
                            arr.sort_unstable_by_key(|x| x.0);
                            let mut sh = [0u8; 5];
                            for (pos, &(_, tag)) in arr.iter().enumerate() {
                                sh[tag as usize] = pos as u8;
                            }
                            let tid_off = bases.len() as u32;
                            for e in es..ee {
                                let mut t = [a as u8, b as u8, d as u8, e as u8, c as u8];
                                t.sort_unstable();
                                let tid = tid_map[&t];
                                bases.push(tid * stride as u32);
                            }
                            groups.push(IncGroup {
                                a: a as u8,
                                b: b as u8,
                                d: d as u8,
                                e_start: es as u8,
                                len: (ee - es) as u8,
                                sh_a: sh[0],
                                sh_b: sh[1],
                                sh_d: sh[2],
                                sh_e: sh[3],
                                sh_c: sh[4],
                                tid_off,
                            });
                        }
                    }
                }
            }
            inc_groups.push(groups);
            inc_bases.push(bases);
        }

        Self {
            k,
            stride,
            num_tuples,
            tuples,
            inc_groups,
            inc_bases,
        }
    }
}

#[inline(always)]
fn canon_comp(p: usize) -> usize {
    if p >= 16 {
        p ^ 31
    } else {
        p
    }
}

// ---------- Search State ----------

const BASE_W: u8 = 16;

struct State {
    mode: Mode,
    m: usize, // number of active rows (M in Comp, N in Free)
    rows: Vec<u32>,
    cols_comp: Vec<u64>,
    cols_free: Vec<u128>,
    cells: Vec<Cell>,       // len = num_tuples * stride
    uncovered: Vec<u32>,    // list of uncovered cell indices (base + pat)
    unc_pos: Vec<u32>,      // index in `uncovered` or u32::MAX
    weighted: Vec<u32>,     // cell indices with w > BASE_W
}

impl State {
    fn from_rows(mode: Mode, geom: &Geometry, rows: Vec<u32>) -> Self {
        let m = rows.len();
        let k = geom.k;
        match mode {
            Mode::Comp => assert!(m <= 64, "Comp mode supports M <= 64 (N <= 128)"),
            Mode::Free => assert!(m <= 128, "Free mode supports N <= 128"),
        }
        let mut cols_comp = vec![0u64; k];
        let mut cols_free = vec![0u128; k];
        for (r, &rv) in rows.iter().enumerate() {
            for c in 0..k {
                if ((rv >> c) & 1) != 0 {
                    if mode == Mode::Comp {
                        cols_comp[c] |= 1u64 << r;
                    } else {
                        cols_free[c] |= 1u128 << r;
                    }
                }
            }
        }

        let total = geom.num_tuples * geom.stride;
        let mut cells = vec![Cell { cov: 0, w: BASE_W }; total];

        for (tid, t) in geom.tuples.iter().enumerate() {
            let base = tid * geom.stride;
            let (c0, c1, c2, c3, c4) = (
                t[0] as usize,
                t[1] as usize,
                t[2] as usize,
                t[3] as usize,
                t[4] as usize,
            );
            for &rv in &rows {
                let p = (((rv >> c0) & 1)
                    | (((rv >> c1) & 1) << 1)
                    | (((rv >> c2) & 1) << 2)
                    | (((rv >> c3) & 1) << 3)
                    | (((rv >> c4) & 1) << 4)) as usize;
                let idx = base + if mode == Mode::Comp { canon_comp(p) } else { p };
                cells[idx].cov = cells[idx].cov.saturating_add(1);
            }
        }

        let mut uncovered = Vec::new();
        let mut unc_pos = vec![u32::MAX; total];
        for idx in 0..total {
            if cells[idx].cov == 0 {
                unc_pos[idx] = uncovered.len() as u32;
                uncovered.push(idx as u32);
            }
        }

        Self {
            mode,
            m,
            rows,
            cols_comp,
            cols_free,
            cells,
            uncovered,
            unc_pos,
            weighted: Vec::new(),
        }
    }

    #[inline(always)]
    fn unc(&self) -> usize {
        self.uncovered.len()
    }

    /// Evaluate flipping `(r, c)` without mutating state. Returns `(delta_w, delta_unc)`.
    #[inline]
    fn eval_flip(&self, geom: &Geometry, r: usize, c: usize) -> (i32, i32) {
        let rv = self.rows[r];
        let bc = (rv >> c) & 1;
        let groups = &geom.inc_groups[c];
        let bases = &geom.inc_bases[c];
        let cells = self.cells.as_slice();
        let mut delta_unc: i32 = 0;
        let mut delta_w: i32 = 0;

        if self.mode == Mode::Comp {
            for g in groups {
                let p_base = ((((rv >> g.a) & 1) << g.sh_a)
                    | (((rv >> g.b) & 1) << g.sh_b)
                    | (((rv >> g.d) & 1) << g.sh_d)
                    | (bc << g.sh_c)) as usize;
                let bit_c = 1usize << g.sh_c;
                let sh_e = g.sh_e as usize;
                let mut e_bits = rv >> g.e_start;
                let off = g.tid_off as usize;
                let slice = &bases[off..off + g.len as usize];
                for &base in slice {
                    let p_old = p_base | (((e_bits & 1) as usize) << sh_e);
                    e_bits >>= 1;
                    let p_new = p_old ^ bit_c;
                    let po = canon_comp(p_old);
                    let pn = canon_comp(p_new);
                    let b = base as usize;
                    // Safety: b + po and b + pn < geom.num_tuples * 16 == cells.len()
                    let co = unsafe { *cells.get_unchecked(b + po) };
                    let cn = unsafe { *cells.get_unchecked(b + pn) };
                    let mo = (co.cov == 1) as i32;
                    let mn = (cn.cov == 0) as i32;
                    delta_unc += mo - mn;
                    delta_w += mo * (co.w as i32) - mn * (cn.w as i32);
                }
            }
        } else {
            for g in groups {
                let p_base = ((((rv >> g.a) & 1) << g.sh_a)
                    | (((rv >> g.b) & 1) << g.sh_b)
                    | (((rv >> g.d) & 1) << g.sh_d)
                    | (bc << g.sh_c)) as usize;
                let bit_c = 1usize << g.sh_c;
                let sh_e = g.sh_e as usize;
                let mut e_bits = rv >> g.e_start;
                let off = g.tid_off as usize;
                let slice = &bases[off..off + g.len as usize];
                for &base in slice {
                    let p_old = p_base | (((e_bits & 1) as usize) << sh_e);
                    e_bits >>= 1;
                    let p_new = p_old ^ bit_c;
                    let b = base as usize;
                    let co = unsafe { *cells.get_unchecked(b + p_old) };
                    let cn = unsafe { *cells.get_unchecked(b + p_new) };
                    let mo = (co.cov == 1) as i32;
                    let mn = (cn.cov == 0) as i32;
                    delta_unc += mo - mn;
                    delta_w += mo * (co.w as i32) - mn * (cn.w as i32);
                }
            }
        }

        (delta_w, delta_unc)
    }

    #[inline(always)]
    fn add_uncovered(&mut self, idx: usize) {
        debug_assert_eq!(self.unc_pos[idx], u32::MAX);
        self.unc_pos[idx] = self.uncovered.len() as u32;
        self.uncovered.push(idx as u32);
    }

    #[inline(always)]
    fn remove_uncovered(&mut self, idx: usize) {
        let pos = self.unc_pos[idx] as usize;
        debug_assert!(pos < self.uncovered.len());
        let last = self.uncovered.pop().unwrap();
        if pos < self.uncovered.len() {
            self.uncovered[pos] = last;
            self.unc_pos[last as usize] = pos as u32;
        }
        self.unc_pos[idx] = u32::MAX;
    }

    /// Apply flip `(r, c)` incrementally.
    fn apply_flip(&mut self, geom: &Geometry, r: usize, c: usize) {
        let rv = self.rows[r];
        let bc = (rv >> c) & 1;
        let groups = &geom.inc_groups[c];
        let bases = &geom.inc_bases[c];

        if self.mode == Mode::Comp {
            for g in groups {
                let p_base = ((((rv >> g.a) & 1) << g.sh_a)
                    | (((rv >> g.b) & 1) << g.sh_b)
                    | (((rv >> g.d) & 1) << g.sh_d)
                    | (bc << g.sh_c)) as usize;
                let bit_c = 1usize << g.sh_c;
                let sh_e = g.sh_e as usize;
                let mut e_bits = rv >> g.e_start;
                let off = g.tid_off as usize;
                let slice = &bases[off..off + g.len as usize];
                for &base in slice {
                    let p_old = p_base | (((e_bits & 1) as usize) << sh_e);
                    e_bits >>= 1;
                    let p_new = p_old ^ bit_c;
                    let io = base as usize + canon_comp(p_old);
                    let inew = base as usize + canon_comp(p_new);
                    let co = self.cells[io].cov;
                    self.cells[io].cov = co - 1;
                    if co == 1 {
                        self.add_uncovered(io);
                    }
                    let cn = self.cells[inew].cov;
                    self.cells[inew].cov = cn + 1;
                    if cn == 0 {
                        self.remove_uncovered(inew);
                    }
                }
            }
            self.cols_comp[c] ^= 1u64 << r;
        } else {
            for g in groups {
                let p_base = ((((rv >> g.a) & 1) << g.sh_a)
                    | (((rv >> g.b) & 1) << g.sh_b)
                    | (((rv >> g.d) & 1) << g.sh_d)
                    | (bc << g.sh_c)) as usize;
                let bit_c = 1usize << g.sh_c;
                let sh_e = g.sh_e as usize;
                let mut e_bits = rv >> g.e_start;
                let off = g.tid_off as usize;
                let slice = &bases[off..off + g.len as usize];
                for &base in slice {
                    let p_old = p_base | (((e_bits & 1) as usize) << sh_e);
                    e_bits >>= 1;
                    let p_new = p_old ^ bit_c;
                    let io = base as usize + p_old;
                    let inew = base as usize + p_new;
                    let co = self.cells[io].cov;
                    self.cells[io].cov = co - 1;
                    if co == 1 {
                        self.add_uncovered(io);
                    }
                    let cn = self.cells[inew].cov;
                    self.cells[inew].cov = cn + 1;
                    if cn == 0 {
                        self.remove_uncovered(inew);
                    }
                }
            }
            self.cols_free[c] ^= 1u128 << r;
        }

        self.rows[r] = rv ^ (1u32 << c);
    }

    /// Generate all Hamming-distance-1 `(row, col)` candidates for an uncovered cell `cell_idx`.
    fn gen_hd1_candidates(&self, geom: &Geometry, cell_idx: usize, out: &mut Vec<(usize, usize)>) {
        out.clear();
        let tid = cell_idx / geom.stride;
        let pat = cell_idx % geom.stride;
        let t = geom.tuples[tid];
        let cs = [
            t[0] as usize,
            t[1] as usize,
            t[2] as usize,
            t[3] as usize,
            t[4] as usize,
        ];

        if self.mode == Mode::Comp {
            let valid = if self.m == 64 {
                u64::MAX
            } else {
                (1u64 << self.m) - 1
            };
            let mut m = [0u64; 5];
            let mut nm = [0u64; 5];
            for j in 0..5 {
                let col = self.cols_comp[cs[j]];
                m[j] = if ((pat >> j) & 1) != 0 {
                    col
                } else {
                    (!col) & valid
                };
                nm[j] = (!m[j]) & valid;
            }
            // HD-1 to `pat` OR HD-1 to `31 ^ pat`
            let masks = [
                (nm[0] & m[1] & m[2] & m[3] & m[4]) | (m[0] & nm[1] & nm[2] & nm[3] & nm[4]),
                (m[0] & nm[1] & m[2] & m[3] & m[4]) | (nm[0] & m[1] & nm[2] & nm[3] & nm[4]),
                (m[0] & m[1] & nm[2] & m[3] & m[4]) | (nm[0] & nm[1] & m[2] & nm[3] & nm[4]),
                (m[0] & m[1] & m[2] & nm[3] & m[4]) | (nm[0] & nm[1] & nm[2] & m[3] & nm[4]),
                (m[0] & m[1] & m[2] & m[3] & nm[4]) | (nm[0] & nm[1] & nm[2] & nm[3] & m[4]),
            ];
            for j in 0..5 {
                let mut bits = masks[j];
                let col_idx = cs[j];
                while bits != 0 {
                    let r = bits.trailing_zeros() as usize;
                    out.push((r, col_idx));
                    bits &= bits - 1;
                }
            }
        } else {
            let valid = if self.m == 128 {
                u128::MAX
            } else {
                (1u128 << self.m) - 1
            };
            let mut m = [0u128; 5];
            let mut nm = [0u128; 5];
            for j in 0..5 {
                let col = self.cols_free[cs[j]];
                m[j] = if ((pat >> j) & 1) != 0 {
                    col
                } else {
                    (!col) & valid
                };
                nm[j] = (!m[j]) & valid;
            }
            let masks = [
                nm[0] & m[1] & m[2] & m[3] & m[4],
                m[0] & nm[1] & m[2] & m[3] & m[4],
                m[0] & m[1] & nm[2] & m[3] & m[4],
                m[0] & m[1] & m[2] & nm[3] & m[4],
                m[0] & m[1] & m[2] & m[3] & nm[4],
            ];
            for j in 0..5 {
                let mut bits = masks[j];
                let col_idx = cs[j];
                while bits != 0 {
                    let r = bits.trailing_zeros() as usize;
                    out.push((r, col_idx));
                    bits &= bits - 1;
                }
            }
        }
    }

    fn paws_increase(&mut self, rng: &mut Rng, max_w: u8) {
        if max_w <= BASE_W {
            return;
        }
        let mut need_smooth = false;
        let len = self.uncovered.len();
        let samples = len.min(128);
        for i in 0..samples {
            let idx = if len <= 128 {
                self.uncovered[i] as usize
            } else {
                self.uncovered[rng.gen_range(len)] as usize
            };
            let w = self.cells[idx].w;
            if w == BASE_W {
                self.weighted.push(idx as u32);
            }
            if w < max_w {
                let nw = w + 1;
                self.cells[idx].w = nw;
                if nw >= max_w {
                    need_smooth = true;
                }
            } else {
                need_smooth = true;
            }
        }
        if need_smooth {
            self.paws_smooth();
        }
    }

    fn paws_smooth(&mut self) {
        let cells = &mut self.cells;
        self.weighted.retain(|&idx| {
            let c = &mut cells[idx as usize];
            if c.w > BASE_W {
                c.w -= 1;
            }
            c.w > BASE_W
        });
    }

    /// Compute for each active row `r` how many `(tid, pat)` have `cov == 1` exclusively due to `r`.
    fn row_unique_counts(&self, geom: &Geometry) -> Vec<usize> {
        let mut uniq = vec![0usize; self.m];
        for (tid, t) in geom.tuples.iter().enumerate() {
            let base = tid * geom.stride;
            let (c0, c1, c2, c3, c4) = (
                t[0] as usize,
                t[1] as usize,
                t[2] as usize,
                t[3] as usize,
                t[4] as usize,
            );
            for (r, &rv) in self.rows.iter().enumerate() {
                let p = (((rv >> c0) & 1)
                    | (((rv >> c1) & 1) << 1)
                    | (((rv >> c2) & 1) << 2)
                    | (((rv >> c3) & 1) << 3)
                    | (((rv >> c4) & 1) << 4)) as usize;
                let idx = base + if self.mode == Mode::Comp { canon_comp(p) } else { p };
                if self.cells[idx].cov == 1 {
                    uniq[r] += 1;
                }
            }
        }
        uniq
    }
}

// ---------- Array I/O & Projections ----------

fn read_array_file(path: &PathBuf) -> Result<(Vec<u32>, usize), String> {
    let text = fs::read_to_string(path).map_err(|e| format!("Cannot read {:?}: {}", path, e))?;
    let mut rows = Vec::new();
    let mut k_opt = None;
    for (ln, line) in text.lines().enumerate() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        let toks: Vec<&str> = trimmed.split_whitespace().collect();
        let k = match k_opt {
            None => {
                if toks.len() > 31 {
                    return Err(format!("k={} > 31 not supported", toks.len()));
                }
                k_opt = Some(toks.len());
                toks.len()
            }
            Some(prev) => {
                if toks.len() != prev {
                    return Err(format!("Line {}: expected {} cols, got {}", ln + 1, prev, toks.len()));
                }
                prev
            }
        };
        let mut bits = 0u32;
        for (c, tok) in toks.iter().enumerate() {
            match *tok {
                "0" => {}
                "1" => bits |= 1u32 << c,
                other => return Err(format!("Line {} col {}: invalid symbol {:?}", ln + 1, c, other)),
            }
        }
        let _ = k;
        rows.push(bits);
    }
    let k = k_opt.ok_or_else(|| "Empty array file".to_string())?;
    Ok((rows, k))
}

/// Extract complementary pairs `{r, ~r}` from a full binary array.
fn extract_comp_base_rows(rows: &[u32], k: usize) -> Result<Vec<u32>, String> {
    let mask = (1u32 << k) - 1;
    let n = rows.len();
    if n % 2 != 0 {
        return Err(format!("Cannot extract comp pairs from odd N={}", n));
    }
    let mut used = vec![false; n];
    let mut base = Vec::with_capacity(n / 2);
    for i in 0..n {
        if used[i] {
            continue;
        }
        let target = (!rows[i]) & mask;
        let mut found = None;
        for j in (i + 1)..n {
            if !used[j] && rows[j] == target {
                found = Some(j);
                break;
            }
        }
        if let Some(j) = found {
            used[i] = true;
            used[j] = true;
            base.push(rows[i]);
        } else {
            return Err(format!("Row {} has no exact complement pair in file", i));
        }
    }
    Ok(base)
}

/// Expand `comp` base rows to full `2M` rows, or return `free` rows directly.
fn expand_rows(mode: Mode, rows: &[u32], k: usize) -> Vec<u32> {
    match mode {
        Mode::Free => rows.to_vec(),
        Mode::Comp => {
            let mask = (1u32 << k) - 1;
            let mut out = Vec::with_capacity(rows.len() * 2);
            for &r in rows {
                out.push(r);
            }
            for &r in rows {
                out.push((!r) & mask);
            }
            out
        }
    }
}

fn write_array_file(path: &PathBuf, mode: Mode, rows: &[u32], k: usize) -> Result<(), String> {
    let full = expand_rows(mode, rows, k);
    let f = File::create(path).map_err(|e| format!("Cannot create {:?}: {}", path, e))?;
    let mut w = BufWriter::new(f);
    for &r in &full {
        for c in 0..k {
            if c > 0 {
                w.write_all(b" ").map_err(|e| e.to_string())?;
            }
            let ch = if ((r >> c) & 1) != 0 { b"1" } else { b"0" };
            w.write_all(ch).map_err(|e| e.to_string())?;
        }
        w.write_all(b"\n").map_err(|e| e.to_string())?;
    }
    w.flush().map_err(|e| e.to_string())
}

fn drop_col_from_rows(rows: &[u32], k: usize, col_drop: usize) -> Vec<u32> {
    let low_mask = (1u32 << col_drop) - 1;
    rows.iter()
        .map(|&r| (r & low_mask) | ((r >> (col_drop + 1)) << col_drop))
        .collect::<Vec<_>>()
        .into_iter()
        .map(|x| x & ((1u32 << (k - 1)) - 1))
        .collect()
}

/// Greedily project `k_cur -> target_k` by dropping the column whose removal minimizes
/// the number of thinly-covered (`cov == 1` or `cov == 2`) cells (maximizes slack for row deletion).
fn project_columns_greedy(mode: Mode, mut rows: Vec<u32>, mut k_cur: usize, target_k: usize) -> Vec<u32> {
    while k_cur > target_k {
        let geom = Geometry::new(k_cur, mode);
        let st = State::from_rows(mode, &geom, rows.clone());
        // Count how many cov==1 cells each column participates in
        let mut col_thin = vec![0usize; k_cur];
        for (tid, t) in geom.tuples.iter().enumerate() {
            let base = tid * geom.stride;
            let mut thin = 0usize;
            for p in 0..geom.stride {
                let cv = st.cells[base + p].cov;
                if cv == 0 {
                    thin += 1000;
                } else if cv == 1 {
                    thin += 10;
                } else if cv == 2 {
                    thin += 1;
                }
            }
            for &c in t {
                col_thin[c as usize] += thin;
            }
        }
        // Drop column participating in MOST thin tuples (leaves healthiest remaining k-1 cols)
        let mut best_c = 0;
        let mut best_score = col_thin[0];
        for c in 1..k_cur {
            if col_thin[c] > best_score {
                best_score = col_thin[c];
                best_c = c;
            }
        }
        eprintln!(
            "[project] k={} -> {}: dropping col {} (thin_score={}, min={}, max={})",
            k_cur,
            k_cur - 1,
            best_c,
            best_score,
            col_thin.iter().min().unwrap(),
            col_thin.iter().max().unwrap()
        );
        rows = drop_col_from_rows(&rows, k_cur, best_c);
        k_cur -= 1;
    }
    rows
}

fn greedy_drop_rows(mode: Mode, geom: &Geometry, mut rows: Vec<u32>, target_m: usize, drop_rank: usize) -> Vec<u32> {
    let mut step = 0usize;
    while rows.len() > target_m {
        let st = State::from_rows(mode, geom, rows.clone());
        let uniq = st.row_unique_counts(geom);
        let mut order: Vec<usize> = (0..rows.len()).collect();
        order.sort_by_key(|&r| (uniq[r], r));
        let pick_idx = if step == 0 {
            drop_rank.min(order.len() - 1)
        } else {
            0
        };
        let drop_r = order[pick_idx];
        rows.remove(drop_r);
        step += 1;
    }
    rows
}

// ---------- Self-Test (Gate 0 G0-1) ----------

fn run_self_test() -> Result<(), String> {
    println!("=== G0-1 Self-Test: 10,000 random flips in comp & free on k=12 and k=25 ===");
    let cases = [
        (Mode::Comp, 12usize, 26usize, 10_000usize),
        (Mode::Free, 12usize, 52usize, 10_000usize),
        (Mode::Comp, 25usize, 59usize, 10_000usize),
        (Mode::Free, 25usize, 118usize, 10_000usize),
    ];

    for (ci, &(mode, k, m, flips)) in cases.iter().enumerate() {
        let t0 = Instant::now();
        let geom = Geometry::new(k, mode);
        let mut rng = Rng::new(0xDEAD_BEEF_0000_0001 + ci as u64);
        let mask = (1u32 << k) - 1;
        let rows: Vec<u32> = (0..m).map(|_| (rng.next_u64() as u32) & mask).collect();
        let mut st = State::from_rows(mode, &geom, rows);
        let mut cands = Vec::new();
        let mut hd1_checked = 0usize;

        for step in 0..flips {
            // Periodically verify HD-1 candidate generator soundness
            if step % 250 == 0 && !st.uncovered.is_empty() {
                let u_idx = st.uncovered[rng.gen_range(st.uncovered.len())] as usize;
                st.gen_hd1_candidates(&geom, u_idx, &mut cands);
                let tid = u_idx / geom.stride;
                let pat = u_idx % geom.stride;
                let t = geom.tuples[tid];
                // Verify every generated (r, c) actually covers u_idx after flipping!
                for &(r, c) in &cands {
                    let rv_after = st.rows[r] ^ (1u32 << c);
                    let p_after = (((rv_after >> t[0]) & 1)
                        | (((rv_after >> t[1]) & 1) << 1)
                        | (((rv_after >> t[2]) & 1) << 2)
                        | (((rv_after >> t[3]) & 1) << 3)
                        | (((rv_after >> t[4]) & 1) << 4)) as usize;
                    let p_eff = if mode == Mode::Comp {
                        canon_comp(p_after)
                    } else {
                        p_after
                    };
                    if p_eff != pat {
                        return Err(format!(
                            "HD-1 bug in {:?} k={}: ({},{}) gave pat {} != {}",
                            mode, k, r, c, p_eff, pat
                        ));
                    }
                }
                // Also verify completeness against brute force over all rows & 5 cols
                let mut bf_count = 0usize;
                for r in 0..m {
                    for &c_u8 in &t {
                        let c = c_u8 as usize;
                        let rv_after = st.rows[r] ^ (1u32 << c);
                        let p_after = (((rv_after >> t[0]) & 1)
                            | (((rv_after >> t[1]) & 1) << 1)
                            | (((rv_after >> t[2]) & 1) << 2)
                            | (((rv_after >> t[3]) & 1) << 3)
                            | (((rv_after >> t[4]) & 1) << 4)) as usize;
                        let p_eff = if mode == Mode::Comp {
                            canon_comp(p_after)
                        } else {
                            p_after
                        };
                        if p_eff == pat {
                            bf_count += 1;
                        }
                    }
                }
                if bf_count != cands.len() {
                    return Err(format!(
                        "HD-1 completeness mismatch in {:?} k={}: gen={} vs bf={}",
                        mode,
                        k,
                        cands.len(),
                        bf_count
                    ));
                }
                hd1_checked += 1;
            }

            let r = rng.gen_range(m);
            let c = rng.gen_range(k);
            let unc_before = st.unc() as i32;
            let (_, delta_unc) = st.eval_flip(&geom, r, c);
            st.apply_flip(&geom, r, c);
            let unc_after = st.unc() as i32;
            if unc_before + delta_unc != unc_after {
                return Err(format!(
                    "eval_flip mismatch in {:?} k={} step {}: {} + {} != {}",
                    mode, k, step, unc_before, delta_unc, unc_after
                ));
            }
            // Check exact brute-force state every 2500 flips (and at final step)
            if (step + 1) % 2500 == 0 {
                let bf = State::from_rows(mode, &geom, st.rows.clone());
                if bf.unc() != st.unc() {
                    return Err(format!(
                        "Brute-force unc mismatch in {:?} k={} step {}: {} vs {}",
                        mode,
                        k,
                        step,
                        st.unc(),
                        bf.unc()
                    ));
                }
                for i in 0..st.cells.len() {
                    if bf.cells[i].cov != st.cells[i].cov {
                        return Err(format!(
                            "Cell cov mismatch at idx {} in {:?} k={}",
                            i, mode, k
                        ));
                    }
                    let in_list = st.unc_pos[i] != u32::MAX;
                    if in_list != (bf.cells[i].cov == 0) {
                        return Err(format!("unc_pos mismatch at idx {}", i));
                    }
                }
                if mode == Mode::Comp && bf.cols_comp != st.cols_comp {
                    return Err("cols_comp mismatch".to_string());
                }
                if mode == Mode::Free && bf.cols_free != st.cols_free {
                    return Err("cols_free mismatch".to_string());
                }
            }
        }
        println!(
            "  PASS {:?} k={} m={}: {} flips, {} HD-1 checks, 0 mismatches ({:.3}s)",
            mode,
            k,
            m,
            flips,
            hd1_checked,
            t0.elapsed().as_secs_f64()
        );
    }
    println!("G0-1 SELF-TEST: ALL PASS (0 mismatches)");
    Ok(())
}

// ---------- Multi-threaded Focused-Tabu (Fractional SWT) & Focused-SA ----------

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Algo {
    Hybrid, // T0: Mix-SA (pf), T1: Mix-SA (pf_hi / lower T_end) or Tabu
    Tabu,
    Sa,
    BestSa,
    MixSa, // Mixed Metropolis SA: prob `pf` Best-HD1, prob `1-pf` random cell (r, c)
}

struct SearchConfig {
    mode: Mode,
    algo: Algo,
    k: usize,
    target_m: usize,
    fix_const: usize, // number of leading rows locked (1 in comp = {0^k,1^k}, 2 in free = 0^k,1^k)
    time_limit_secs: f64,
    seed: u64,
    threads: usize,
    tenure_range: Option<(u64, u64)>,
    smooth_every: Option<u32>,
    max_w: u8,
    t_start: f64,
    t_end: f64,
    pf: f64,
    out_path: Option<PathBuf>,
}

struct SearchResult {
    best_unc: usize,
    best_rows: Vec<u32>,
    total_steps: u64,
    total_evals: u64,
    elapsed_secs: f64,
}

fn run_search(geom: &Arc<Geometry>, init_per_thread: Vec<Vec<u32>>, cfg: &SearchConfig) -> SearchResult {
    let start = Instant::now();
    let stop_flag = Arc::new(AtomicBool::new(false));
    let global_best_unc = Arc::new(AtomicU32::new(u32::MAX));
    let global_best_rows: Arc<Mutex<Vec<u32>>> = Arc::new(Mutex::new(init_per_thread[0].clone()));
    let total_steps = Arc::new(AtomicU64::new(0));
    let total_evals = Arc::new(AtomicU64::new(0));

    // Check if any init state is already unc == 0
    for (ti, init_rows) in init_per_thread.iter().enumerate() {
        let st = State::from_rows(cfg.mode, geom, init_rows.clone());
        let u = st.unc() as u32;
        if u < global_best_unc.load(Ordering::Relaxed) {
            global_best_unc.store(u, Ordering::Relaxed);
            *global_best_rows.lock().unwrap() = init_rows.clone();
            if let Some(ref p) = cfg.out_path {
                let _ = write_array_file(p, cfg.mode, init_rows, cfg.k);
            }
        }
        if u == 0 {
            println!(
                "[init] Thread {} init already has unc=0! (N={})",
                ti,
                if cfg.mode == Mode::Comp {
                    cfg.target_m * 2
                } else {
                    cfg.target_m
                }
            );
            return SearchResult {
                best_unc: 0,
                best_rows: init_rows.clone(),
                total_steps: 0,
                total_evals: 0,
                elapsed_secs: start.elapsed().as_secs_f64(),
            };
        }
    }

    let mut handles = Vec::with_capacity(cfg.threads);
    for tid in 0..cfg.threads {
        let geom_c = Arc::clone(geom);
        let stop_c = Arc::clone(&stop_flag);
        let best_unc_c = Arc::clone(&global_best_unc);
        let best_rows_c = Arc::clone(&global_best_rows);
        let steps_c = Arc::clone(&total_steps);
        let evals_c = Arc::clone(&total_evals);
        let init_rows = init_per_thread[tid % init_per_thread.len()].clone();
        let mode = cfg.mode;
        // Worker kind: 0 = Tabu, 1 = 1-Eval SA, 2 = Best-HD1 SA, 3 = Mix-SA (random-cell + pf Best-HD1)
        let worker_kind: u8 = match cfg.algo {
            Algo::Tabu => 0,
            Algo::Sa => 1,
            Algo::BestSa => 2,
            Algo::MixSa => 3,
            Algo::Hybrid => if tid % 2 == 0 { 3 } else { 0 },
        };
        let k = cfg.k;
        let m = cfg.target_m;
        let fix_const = cfg.fix_const;
        let time_limit = cfg.time_limit_secs;
        let out_path = cfg.out_path.clone();
        let max_w = cfg.max_w;
        let pf = if worker_kind == 3 && tid % 2 == 1 {
            (cfg.pf * 2.5).min(0.25)
        } else {
            cfg.pf
        };
        let t_start = if (worker_kind == 2 || worker_kind == 3) && tid % 2 == 1 {
            cfg.t_start * 1.35
        } else {
            cfg.t_start
        };
        let t_end = if (worker_kind == 2 || worker_kind == 3) && tid % 2 == 1 {
            cfg.t_end * 0.75
        } else {
            cfg.t_end
        };

        let seed = cfg.seed.wrapping_add((tid as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15));
        let (t_min, t_max) = cfg.tenure_range.unwrap_or_else(|| {
            if tid % 2 == 0 {
                (7, 15)
            } else {
                (10, 22)
            }
        });
        let smooth_every = cfg.smooth_every.unwrap_or(if tid % 2 == 0 { 6 } else { 10 });

        let handle = thread::spawn(move || {
            let mut rng = Rng::new(seed);
            let mut st = State::from_rows(mode, &geom_c, init_rows);
            let mut tabu = vec![0u64; m * k];
            let mut cands: Vec<(usize, usize)> = Vec::with_capacity(64);
            let mut local_best = st.unc();
            let mut step: u64 = 0;
            let mut evals: u64 = 0;
            let mut flushed_steps: u64 = 0;
            let mut flushed_evals: u64 = 0;
            let mut paws_ticks: u32 = 0;
            let mut last_log = Instant::now();

            let flush_mask: u64 = if worker_kind == 1 || worker_kind == 3 { 255 } else { 31 };
            let cycle_secs = time_limit.min(90.0).max(5.0);
            let ln_ratio = (t_end / t_start).ln();

            while !stop_c.load(Ordering::Relaxed) {
                if (step & flush_mask) == 0 {
                    let ds = step - flushed_steps;
                    let de = evals - flushed_evals;
                    if ds > 0 {
                        steps_c.fetch_add(ds, Ordering::Relaxed);
                        flushed_steps = step;
                    }
                    if de > 0 {
                        evals_c.fetch_add(de, Ordering::Relaxed);
                        flushed_evals = evals;
                    }
                    let el = start.elapsed().as_secs_f64();
                    if el >= time_limit {
                        stop_c.store(true, Ordering::Relaxed);
                        break;
                    }
                    if tid == 0 && last_log.elapsed().as_secs_f64() >= 10.0 {
                        let tot_s = steps_c.load(Ordering::Relaxed);
                        let tot_e = evals_c.load(Ordering::Relaxed);
                        let gbest = best_unc_c.load(Ordering::Relaxed);
                        let frac = (el % cycle_secs) / cycle_secs;
                        let temp = t_start * (ln_ratio * frac).exp();
                        println!(
                            "  [{:6.1}s] steps={} ({:.0}/s) evals={} ({:.0}/s) T={:.2} T0_unc={} best_unc={}",
                            el,
                            tot_s,
                            tot_s as f64 / el.max(1e-6),
                            tot_e,
                            tot_e as f64 / el.max(1e-6),
                            temp,
                            st.unc(),
                            gbest
                        );
                        last_log = Instant::now();
                    }
                }

                let cur_unc = st.unc();
                if cur_unc == 0 {
                    best_unc_c.store(0, Ordering::Relaxed);
                    {
                        let mut guard = best_rows_c.lock().unwrap();
                        *guard = st.rows.clone();
                        if let Some(ref p) = out_path {
                            let _ = write_array_file(p, mode, &st.rows, k);
                        }
                    }
                    stop_c.store(true, Ordering::Relaxed);
                    break;
                }

                if worker_kind == 3 {
                    // Mixed Metropolis SA: prob `pf` Best-HD1, prob `1-pf` random cell (r, c)
                    let u_pick = (rng.next_u64() >> 11) as f64 * (1.0 / ((1u64 << 53) as f64));
                    let (cr, cc, du) = if pf > 0.0 && u_pick < pf {
                        let u_idx = st.uncovered[rng.gen_range(cur_unc)] as usize;
                        st.gen_hd1_candidates(&geom_c, u_idx, &mut cands);
                        if fix_const > 0 {
                            cands.retain(|&(r, _)| r >= fix_const);
                        }
                        if cands.is_empty() {
                            let r = fix_const + rng.gen_range(m - fix_const);
                            let c = rng.gen_range(k);
                            let (_, d) = st.eval_flip(&geom_c, r, c);
                            evals += 1;
                            (r, c, d)
                        } else {
                            let mut b_du = i32::MAX;
                            let mut b_cnt = 0usize;
                            let mut b_rc = (0usize, 0usize);
                            for &(r, c) in &cands {
                                let (_, d) = st.eval_flip(&geom_c, r, c);
                                evals += 1;
                                if d < b_du {
                                    b_du = d;
                                    b_cnt = 1;
                                    b_rc = (r, c);
                                } else if d == b_du {
                                    b_cnt += 1;
                                    if rng.gen_range(b_cnt) == 0 {
                                        b_rc = (r, c);
                                    }
                                }
                            }
                            (b_rc.0, b_rc.1, b_du)
                        }
                    } else {
                        let r = fix_const + rng.gen_range(m - fix_const);
                        let c = rng.gen_range(k);
                        let (_, d) = st.eval_flip(&geom_c, r, c);
                        evals += 1;
                        (r, c, d)
                    };
                    step += 1;

                    let accept = if du <= 0 {
                        true
                    } else {
                        let el = start.elapsed().as_secs_f64();
                        let frac = (el % cycle_secs) / cycle_secs;
                        let temp = t_start * (ln_ratio * frac).exp();
                        let prob = (-(du as f64) / temp).exp();
                        let u01 = (rng.next_u64() >> 11) as f64 * (1.0 / ((1u64 << 53) as f64));
                        u01 < prob
                    };

                    if accept {
                        st.apply_flip(&geom_c, cr, cc);
                        let new_unc = st.unc();
                        if new_unc < local_best {
                            local_best = new_unc;
                            if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                                let mut guard = best_rows_c.lock().unwrap();
                                if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                                    best_unc_c.store(new_unc as u32, Ordering::Relaxed);
                                    *guard = st.rows.clone();
                                    if let Some(ref p) = out_path {
                                        let _ = write_array_file(p, mode, &st.rows, k);
                                    }
                                    if new_unc == 0 || new_unc <= 25 || new_unc % 10 == 0 {
                                        println!(
                                            "  [{:6.1}s] T{}(MSA) NEW best_unc={} (step={}, evals={})",
                                            start.elapsed().as_secs_f64(),
                                            tid,
                                            new_unc,
                                            step,
                                            evals
                                        );
                                    }
                                }
                            }
                            if new_unc == 0 {
                                stop_c.store(true, Ordering::Relaxed);
                                break;
                            }
                        }
                    }
                    continue;
                }

                let u_idx = st.uncovered[rng.gen_range(cur_unc)] as usize;
                st.gen_hd1_candidates(&geom_c, u_idx, &mut cands);
                if fix_const > 0 {
                    cands.retain(|&(r, _)| r >= fix_const);
                }

                if worker_kind == 1 || worker_kind == 2 {
                    let (cr, cc, du) = if cands.is_empty() {
                        let t = geom_c.tuples[u_idx / geom_c.stride];
                        let r = fix_const + rng.gen_range(m - fix_const);
                        let c = t[rng.gen_range(5)] as usize;
                        let (_, d) = st.eval_flip(&geom_c, r, c);
                        evals += 1;
                        (r, c, d)
                    } else if worker_kind == 1 {
                        let (r, c) = cands[rng.gen_range(cands.len())];
                        let (_, d) = st.eval_flip(&geom_c, r, c);
                        evals += 1;
                        (r, c, d)
                    } else {
                        // Best-HD1 SA (Torres-Jimenez N2): evaluate all HD-1 candidates, pick min du
                        let mut b_du = i32::MAX;
                        let mut b_cnt = 0usize;
                        let mut b_rc = (0usize, 0usize);
                        for &(r, c) in &cands {
                            let (_, d) = st.eval_flip(&geom_c, r, c);
                            evals += 1;
                            if d < b_du {
                                b_du = d;
                                b_cnt = 1;
                                b_rc = (r, c);
                            } else if d == b_du {
                                b_cnt += 1;
                                if rng.gen_range(b_cnt) == 0 {
                                    b_rc = (r, c);
                                }
                            }
                        }
                        (b_rc.0, b_rc.1, b_du)
                    };
                    step += 1;

                    let accept = if du <= 0 {
                        true
                    } else {
                        let el = start.elapsed().as_secs_f64();
                        let frac = (el % cycle_secs) / cycle_secs;
                        let temp = t_start * (ln_ratio * frac).exp();
                        let prob = (-(du as f64) / temp).exp();
                        let u01 = (rng.next_u64() >> 11) as f64 * (1.0 / ((1u64 << 53) as f64));
                        u01 < prob
                    };

                    if accept {
                        st.apply_flip(&geom_c, cr, cc);
                        let new_unc = st.unc();
                        if new_unc < local_best {
                            local_best = new_unc;
                            if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                                let mut guard = best_rows_c.lock().unwrap();
                                if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                                    best_unc_c.store(new_unc as u32, Ordering::Relaxed);
                                    *guard = st.rows.clone();
                                    if let Some(ref p) = out_path {
                                        let _ = write_array_file(p, mode, &st.rows, k);
                                    }
                                    if new_unc == 0 || new_unc <= 25 || new_unc % 10 == 0 {
                                        println!(
                                            "  [{:6.1}s] T{}({}) NEW best_unc={} (step={}, evals={})",
                                            start.elapsed().as_secs_f64(),
                                            tid,
                                            if worker_kind == 2 { "BSA" } else { "SA" },
                                            new_unc,
                                            step,
                                            evals
                                        );
                                    }
                                }
                            }
                            if new_unc == 0 {
                                stop_c.store(true, Ordering::Relaxed);
                                break;
                            }
                        }
                    }
                    continue;
                }

                // Focused-Tabu + Bounded Fractional SWT
                let chosen: (usize, usize);
                let chosen_dw: i32;

                if cands.is_empty() {
                    let t = geom_c.tuples[u_idx / geom_c.stride];
                    chosen = (fix_const + rng.gen_range(m - fix_const), t[rng.gen_range(5)] as usize);
                    chosen_dw = 0;
                } else {
                    let mut best_nt_dw = i32::MAX;
                    let mut best_nt_du = i32::MAX;
                    let mut best_nt_cnt = 0usize;
                    let mut best_nt = (0usize, 0usize);

                    let mut best_all_dw = i32::MAX;
                    let mut best_all_du = i32::MAX;
                    let mut best_all_cnt = 0usize;
                    let mut best_all = (0usize, 0usize);

                    for &(r, c) in &cands {
                        let (dw, du) = st.eval_flip(&geom_c, r, c);
                        evals += 1;

                        if dw < best_all_dw || (dw == best_all_dw && du < best_all_du) {
                            best_all_dw = dw;
                            best_all_du = du;
                            best_all_cnt = 1;
                            best_all = (r, c);
                        } else if dw == best_all_dw && du == best_all_du {
                            best_all_cnt += 1;
                            if rng.gen_range(best_all_cnt) == 0 {
                                best_all = (r, c);
                            }
                        }

                        let new_unc = (cur_unc as i32 + du) as usize;
                        let is_tabu = tabu[r * k + c] > step;
                        if !is_tabu || new_unc < local_best || new_unc == 0 {
                            if dw < best_nt_dw || (dw == best_nt_dw && du < best_nt_du) {
                                best_nt_dw = dw;
                                best_nt_du = du;
                                best_nt_cnt = 1;
                                best_nt = (r, c);
                            } else if dw == best_nt_dw && du == best_nt_du {
                                best_nt_cnt += 1;
                                if rng.gen_range(best_nt_cnt) == 0 {
                                    best_nt = (r, c);
                                }
                            }
                        }
                    }

                    if best_nt_cnt > 0 {
                        chosen = best_nt;
                        chosen_dw = best_nt_dw;
                    } else {
                        chosen = best_all;
                        chosen_dw = best_all_dw;
                    }
                }

                if max_w > BASE_W && chosen_dw >= 0 {
                    paws_ticks += 1;
                    if paws_ticks >= smooth_every {
                        paws_ticks = 0;
                        st.paws_smooth();
                    } else {
                        st.paws_increase(&mut rng, max_w);
                    }
                }

                let (cr, cc) = chosen;
                st.apply_flip(&geom_c, cr, cc);
                step += 1;
                let tenure = t_min + rng.gen_range((t_max - t_min + 1) as usize) as u64;
                tabu[cr * k + cc] = step + tenure;

                let new_unc = st.unc();
                if new_unc < local_best {
                    local_best = new_unc;
                    if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                        let mut guard = best_rows_c.lock().unwrap();
                        if (new_unc as u32) < best_unc_c.load(Ordering::Relaxed) {
                            best_unc_c.store(new_unc as u32, Ordering::Relaxed);
                            *guard = st.rows.clone();
                            if let Some(ref p) = out_path {
                                let _ = write_array_file(p, mode, &st.rows, k);
                            }
                            if new_unc == 0 || new_unc <= 25 || new_unc % 10 == 0 {
                                println!(
                                    "  [{:6.1}s] T{}(TABU) NEW best_unc={} (step={}, evals={})",
                                    start.elapsed().as_secs_f64(),
                                    tid,
                                    new_unc,
                                    step,
                                    evals
                                );
                            }
                        }
                    }
                    if new_unc == 0 {
                        stop_c.store(true, Ordering::Relaxed);
                        break;
                    }
                }
            }

            steps_c.fetch_add(step - flushed_steps, Ordering::Relaxed);
            evals_c.fetch_add(evals - flushed_evals, Ordering::Relaxed);
        });
        handles.push(handle);
    }

    for h in handles {
        let _ = h.join();
    }

    let elapsed_secs = start.elapsed().as_secs_f64();
    let best_unc = global_best_unc.load(Ordering::Relaxed) as usize;
    let best_rows = global_best_rows.lock().unwrap().clone();
    SearchResult {
        best_unc,
        best_rows,
        total_steps: total_steps.load(Ordering::Relaxed),
        total_evals: total_evals.load(Ordering::Relaxed),
        elapsed_secs,
    }
}

// ---------- CLI ----------

fn parse_tenure(s: &str) -> Result<(u64, u64), String> {
    let parts: Vec<&str> = s.split(',').collect();
    if parts.len() != 2 {
        return Err(format!("Expected tenure min,max, got {}", s));
    }
    let a: u64 = parts[0].parse().map_err(|_| "bad tenure min")?;
    let b: u64 = parts[1].parse().map_err(|_| "bad tenure max")?;
    if a == 0 || b < a {
        return Err("invalid tenure bounds".to_string());
    }
    Ok((a, b))
}

fn main() -> Result<(), String> {
    let args: Vec<String> = env::args().collect();
    if args.iter().any(|a| a == "--self-test") {
        return run_self_test();
    }

    let mut mode = Mode::Comp;
    let mut algo = Algo::Hybrid;
    let mut k: usize = 25;
    let mut target_n: usize = 118;
    let mut step_down_to: Option<usize> = None;
    let mut time_limit_secs: f64 = 30.0;
    let mut seed: u64 = 1001;
    let mut threads: usize = 2;
    let mut init_arg = String::from("random");
    let mut out_path: Option<PathBuf> = None;
    let mut tenure_range: Option<(u64, u64)> = None;
    let mut smooth_every: Option<u32> = None;
    let mut max_w: u8 = 22; // fractional SWT: BASE_W=16 -> max 1.375x ratio
    let mut t_start: f64 = 2.0;
    let mut t_end: f64 = 0.25;
    let mut pf: f64 = 0.02;
    let mut drop_rank: usize = 0;
    let mut use_fix_const: bool = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--mode" => {
                i += 1;
                mode = match args[i].as_str() {
                    "comp" => Mode::Comp,
                    "free" => Mode::Free,
                    other => return Err(format!("Unknown --mode {}", other)),
                };
            }
            "--algo" => {
                i += 1;
                algo = match args[i].as_str() {
                    "hybrid" => Algo::Hybrid,
                    "tabu" => Algo::Tabu,
                    "sa" => Algo::Sa,
                    "best-sa" => Algo::BestSa,
                    "mix-sa" => Algo::MixSa,
                    other => return Err(format!("Unknown --algo {}", other)),
                };
            }
            "--k" => {
                i += 1;
                k = args[i].parse().map_err(|_| "bad --k")?;
            }
            "--n" => {
                i += 1;
                target_n = args[i].parse().map_err(|_| "bad --n")?;
            }
            "--step-down" => {
                i += 1;
                step_down_to = Some(args[i].parse().map_err(|_| "bad --step-down")?);
            }
            "--time-limit-secs" => {
                i += 1;
                time_limit_secs = args[i].parse().map_err(|_| "bad --time-limit-secs")?;
            }
            "--seed" => {
                i += 1;
                seed = args[i].parse().map_err(|_| "bad --seed")?;
            }
            "--threads" => {
                i += 1;
                threads = args[i].parse().map_err(|_| "bad --threads")?;
            }
            "--init" => {
                i += 1;
                init_arg = args[i].clone();
            }
            "--out" => {
                i += 1;
                out_path = Some(PathBuf::from(&args[i]));
            }
            "--tenure" => {
                i += 1;
                tenure_range = Some(parse_tenure(&args[i])?);
            }
            "--smooth" => {
                i += 1;
                smooth_every = Some(args[i].parse().map_err(|_| "bad --smooth")?);
            }
            "--max-w" => {
                i += 1;
                max_w = args[i].parse().map_err(|_| "bad --max-w")?;
            }
            "--t-start" => {
                i += 1;
                t_start = args[i].parse().map_err(|_| "bad --t-start")?;
            }
            "--t-end" => {
                i += 1;
                t_end = args[i].parse().map_err(|_| "bad --t-end")?;
            }
            "--pf" => {
                i += 1;
                pf = args[i].parse().map_err(|_| "bad --pf")?;
            }
            "--drop-rank" => {
                i += 1;
                drop_rank = args[i].parse().map_err(|_| "bad --drop-rank")?;
            }
            "--fix-const" => {
                use_fix_const = true;
            }
            other => return Err(format!("Unknown arg: {}", other)),
        }
        i += 1;
    }

    let fix_const = if use_fix_const {
        if mode == Mode::Comp { 1 } else { 2 }
    } else {
        0
    };

    if mode == Mode::Comp && target_n % 2 != 0 {
        return Err(format!("--mode comp requires even --n, got {}", target_n));
    }
    if let Some(sd) = step_down_to {
        if mode == Mode::Comp && sd % 2 != 0 {
            return Err(format!("--mode comp requires even --step-down, got {}", sd));
        }
    }

    let geom = Arc::new(Geometry::new(k, mode));
    let target_m = if mode == Mode::Comp {
        target_n / 2
    } else {
        target_n
    };
    let mask = (1u32 << k) - 1;

    let base_rows_init: Vec<u32> = if init_arg == "random" {
        let mut rng = Rng::new(seed);
        let mut v: Vec<u32> = (0..target_m)
            .map(|_| (rng.next_u64() as u32) & mask)
            .collect();
        if fix_const >= 1 {
            v[0] = 0;
        }
        if fix_const >= 2 {
            v[1] = mask;
        }
        v
    } else {
        let p = PathBuf::from(&init_arg);
        let (raw_rows, k_in) = read_array_file(&p)?;
        if k_in < k {
            return Err(format!("Init file has k={} < target k={}", k_in, k));
        }
        let mut work_rows = match mode {
            Mode::Comp => extract_comp_base_rows(&raw_rows, k_in)?,
            Mode::Free => raw_rows,
        };
        if k_in > k {
            work_rows = project_columns_greedy(mode, work_rows, k_in, k);
        }
        if fix_const >= 1 && !work_rows.is_empty() {
            let r0 = work_rows[0];
            for r in &mut work_rows {
                *r ^= r0;
            }
            if fix_const >= 2 {
                if let Some(pos) = work_rows.iter().skip(1).position(|&x| x == mask) {
                    work_rows.swap(1, pos + 1);
                } else {
                    work_rows[1] = mask;
                }
            }
        }
        work_rows
    };

    if let Some(final_n) = step_down_to {
        let overall_start = Instant::now();
        let mut cur_rows = base_rows_init;
        let final_m = if mode == Mode::Comp {
            final_n / 2
        } else {
            final_n
        };
        let step_sz = if mode == Mode::Comp { 2 } else { 1 };
        println!(
            "=== Step-Down {:?} ({:?}) k={} from N={} down to N={} (budget {:.1}s, threads={}, seed={}, pf={}, fix_const={}) ===",
            mode,
            algo,
            k,
            cur_rows.len() * step_sz,
            final_n,
            time_limit_secs,
            threads,
            seed,
            pf,
            fix_const
        );

        while cur_rows.len() > final_m {
            let remaining = time_limit_secs - overall_start.elapsed().as_secs_f64();
            if remaining <= 0.2 {
                println!("[step-down] Time budget exhausted.");
                break;
            }
            let next_m = cur_rows.len() - 1;
            let next_n = next_m * step_sz;
            let mut inits = Vec::with_capacity(threads);
            for t in 0..threads {
                let mut rows_copy = cur_rows.clone();
                if fix_const > 0 {
                    let st = State::from_rows(mode, &geom, rows_copy.clone());
                    let uniq = st.row_unique_counts(&geom);
                    let mut order: Vec<usize> = (fix_const..rows_copy.len()).collect();
                    order.sort_by_key(|&r| (uniq[r], r));
                    let drop_r = order[(drop_rank + t).min(order.len() - 1)];
                    rows_copy.remove(drop_r);
                    inits.push(rows_copy);
                } else {
                    inits.push(greedy_drop_rows(mode, &geom, rows_copy, next_m, drop_rank + t));
                }
            }
            let init_unc0 = State::from_rows(mode, &geom, inits[0].clone()).unc();
            println!(
                "\n--- Step-Down -> N={} (m={}, init_unc={}, rem_budget={:.1}s) ---",
                next_n, next_m, init_unc0, remaining
            );
            let step_out = out_path.as_ref().map(|p| {
                let stem = p.file_stem().unwrap().to_string_lossy();
                let ext = p.extension().map(|e| e.to_string_lossy().to_string()).unwrap_or_else(|| "txt".to_string());
                let parent = p.parent().unwrap_or_else(|| std::path::Path::new("."));
                parent.join(format!("{}_N{}.{}", stem, next_n, ext))
            });
            let cfg = SearchConfig {
                mode,
                algo,
                k,
                target_m: next_m,
                fix_const,
                time_limit_secs: remaining,
                seed: seed.wrapping_add(next_n as u64 * 1009),
                threads,
                tenure_range,
                smooth_every,
                max_w,
                t_start,
                t_end,
                pf,
                out_path: step_out.clone(),
            };
            let res = run_search(&geom, inits, &cfg);
            let sps = res.total_steps as f64 / res.elapsed_secs.max(1e-6);
            let eps = res.total_evals as f64 / res.elapsed_secs.max(1e-6);
            println!(
                "SUMMARY N={} best_unc={} elapsed={:.2}s steps={} ({:.0}/s) evals={} ({:.0}/s)",
                next_n, res.best_unc, res.elapsed_secs, res.total_steps, sps, res.total_evals, eps
            );
            if res.best_unc == 0 {
                if let Some(ref p) = step_out {
                    write_array_file(p, mode, &res.best_rows, k)?;
                    println!("  SAVED SOLVED N={} -> {:?}", next_n, p);
                }
                if let Some(ref p) = out_path {
                    write_array_file(p, mode, &res.best_rows, k)?;
                }
                cur_rows = res.best_rows;
            } else {
                println!("[step-down] Stopped at N={} with best_unc={}", next_n, res.best_unc);
                break;
            }
        }
    } else {
        let mut inits = Vec::with_capacity(threads);
        if init_arg == "random" {
            for t in 0..threads {
                let mut rng = Rng::new(seed.wrapping_add((t as u64 + 1) * 0x517C_C1B7_2722_0A95));
                let mut v: Vec<u32> = (0..target_m).map(|_| (rng.next_u64() as u32) & mask).collect();
                if fix_const >= 1 {
                    v[0] = 0;
                }
                if fix_const >= 2 {
                    v[1] = mask;
                }
                inits.push(v);
            }
        } else if base_rows_init.len() > target_m {
            for t in 0..threads {
                if fix_const > 0 {
                    let mut rows_copy = base_rows_init.clone();
                    let mut step_d = 0usize;
                    while rows_copy.len() > target_m {
                        let st = State::from_rows(mode, &geom, rows_copy.clone());
                        let uniq = st.row_unique_counts(&geom);
                        let mut order: Vec<usize> = (fix_const..rows_copy.len()).collect();
                        order.sort_by_key(|&r| (uniq[r], r));
                        let pick = if step_d == 0 { (drop_rank + t).min(order.len() - 1) } else { 0 };
                        rows_copy.remove(order[pick]);
                        step_d += 1;
                    }
                    inits.push(rows_copy);
                } else {
                    inits.push(greedy_drop_rows(mode, &geom, base_rows_init.clone(), target_m, drop_rank + t));
                }
            }
        } else if base_rows_init.len() < target_m {
            for t in 0..threads {
                let mut rows = base_rows_init.clone();
                let mut rng = Rng::new(seed.wrapping_add((t as u64 + 1) * 7919));
                while rows.len() < target_m {
                    rows.push((rng.next_u64() as u32) & mask);
                }
                inits.push(rows);
            }
        } else {
            for _ in 0..threads {
                inits.push(base_rows_init.clone());
            }
        }

        let init_unc0 = State::from_rows(mode, &geom, inits[0].clone()).unc();
        println!(
            "=== Search {:?} ({:?}) k={} N={} (m={}, init_unc={}, budget={:.1}s, threads={}, seed={}, pf={}, fix_const={}) ===",
            mode, algo, k, target_n, target_m, init_unc0, time_limit_secs, threads, seed, pf, fix_const
        );
        let cfg = SearchConfig {
            mode,
            algo,
            k,
            target_m,
            fix_const,
            time_limit_secs,
            seed,
            threads,
            tenure_range,
            smooth_every,
            max_w,
            t_start,
            t_end,
            pf,
            out_path: out_path.clone(),
        };
        let res = run_search(&geom, inits, &cfg);
        let sps = res.total_steps as f64 / res.elapsed_secs.max(1e-6);
        let eps = res.total_evals as f64 / res.elapsed_secs.max(1e-6);
        println!(
            "SUMMARY k={} N={} mode={:?} algo={:?} best_unc={} elapsed={:.2}s steps={} ({:.0}/s) evals={} ({:.0}/s)",
            k, target_n, mode, algo, res.best_unc, res.elapsed_secs, res.total_steps, sps, res.total_evals, eps
        );
        if let Some(ref p) = out_path {
            write_array_file(p, mode, &res.best_rows, k)?;
            println!("  WROTE best (unc={}) -> {:?}", res.best_unc, p);
        }
    }

    Ok(())
}
