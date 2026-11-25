//! Zero-dependency Rust std-only post-optimization reducer for t = 4 covering arrays.
//!
//! Techniques:
//!   - Exact incremental coverage tracking over all C(k, 4) * v^4 tuples (`cov: Vec<u16>`).
//!   - 0-break don't-care absorption: transfers uniquely-covered 4-tuples from candidate
//!     low-unique rows into don't-care cells of other rows before row deletion.
//!   - Minimum-unique row deletion + Focused HD-1 Tabu Search with aspiration and PAWS/SWT
//!     dynamic tuple weighting.
//!   - Multi-threaded worker pool (default 2 threads) sharing the global best valid array
//!     with atomic snapshot writes, full-recompute verification on every `unc == 0` hit,
//!     `--resume`, `--stagnation-secs`, and mandatory `--time-limit-secs`.

use std::env;
use std::fs::{self, File};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};
use std::process;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

// ---------- Fast PRNG (SplitMix64 + Xoshiro256**) ----------

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

// ---------- Geometry & Exact Incremental t = 4 State ----------

/// Precomputed 4-set incident on column `c`.
#[derive(Clone, Copy)]
struct ColQuad {
    tid_off: u32, // tid * v^4
    o1: u8,
    o2: u8,
    o3: u8,
    w_c: u16,
    w1: u16,
    w2: u16,
    w3: u16,
}

struct Ca4State {
    n: usize,
    k: usize,
    v: usize,
    v2: usize,
    v3: usize,
    v4: usize,
    /// Row-major: rows[r * k + c]
    rows: Vec<u8>,
    /// Column-major mirror: cols[c * n + r]
    cols: Vec<u8>,
    quads: Vec<[u8; 4]>,
    col_quads: Vec<Vec<ColQuad>>,
    /// Exact coverage counts: cov[tid * v4 + tup_idx]
    cov: Vec<u16>,
    /// PAWS/SWT dynamic weights per tuple slot (starts at 1)
    weights: Vec<u16>,
    /// Dense list of uncovered global tuple indices: tid * v4 + tup_idx
    unc_list: Vec<u32>,
    /// Position of idx in unc_list, or u32::MAX if covered
    unc_pos: Vec<u32>,
    /// Track weighted slots (> 1) for fast periodic decay
    weighted_slots: Vec<u32>,
}

impl Ca4State {
    fn from_rows(row_vecs: &[Vec<u8>], v: usize) -> Self {
        assert!(!row_vecs.is_empty(), "Input array must have >= 1 row");
        let n = row_vecs.len();
        let k = row_vecs[0].len();
        assert!(k >= 4 && k <= 64, "k must be in 4..=64");
        assert!(v >= 2 && v <= 16, "v must be in 2..=16");
        let v2 = v * v;
        let v3 = v2 * v;
        let v4 = v3 * v;
        assert!(v4 <= u16::MAX as usize, "v^4 must fit in u16");

        let mut rows = vec![0u8; n * k];
        let mut cols = vec![0u8; k * n];
        for r in 0..n {
            assert_eq!(row_vecs[r].len(), k, "Ragged row {}", r);
            for c in 0..k {
                let sym = row_vecs[r][c];
                assert!((sym as usize) < v, "Symbol {} >= v={}", sym, v);
                rows[r * k + c] = sym;
                cols[c * n + r] = sym;
            }
        }

        let mut quads = Vec::new();
        let mut col_quads = vec![Vec::new(); k];
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    for c3 in (c2 + 1)..k {
                        let tid = quads.len() as u32;
                        let tid_off = tid * (v4 as u32);
                        quads.push([c0 as u8, c1 as u8, c2 as u8, c3 as u8]);
                        col_quads[c0].push(ColQuad {
                            tid_off,
                            o1: c1 as u8,
                            o2: c2 as u8,
                            o3: c3 as u8,
                            w_c: v3 as u16,
                            w1: v2 as u16,
                            w2: v as u16,
                            w3: 1,
                        });
                        col_quads[c1].push(ColQuad {
                            tid_off,
                            o1: c0 as u8,
                            o2: c2 as u8,
                            o3: c3 as u8,
                            w_c: v2 as u16,
                            w1: v3 as u16,
                            w2: v as u16,
                            w3: 1,
                        });
                        col_quads[c2].push(ColQuad {
                            tid_off,
                            o1: c0 as u8,
                            o2: c1 as u8,
                            o3: c3 as u8,
                            w_c: v as u16,
                            w1: v3 as u16,
                            w2: v2 as u16,
                            w3: 1,
                        });
                        col_quads[c3].push(ColQuad {
                            tid_off,
                            o1: c0 as u8,
                            o2: c1 as u8,
                            o3: c2 as u8,
                            w_c: 1,
                            w1: v3 as u16,
                            w2: v2 as u16,
                            w3: v as u16,
                        });
                    }
                }
            }
        }

        let total_slots = quads.len() * v4;
        let mut st = Self {
            n,
            k,
            v,
            v2,
            v3,
            v4,
            rows,
            cols,
            quads,
            col_quads,
            cov: vec![0u16; total_slots],
            weights: vec![1u16; total_slots],
            unc_list: Vec::new(),
            unc_pos: vec![u32::MAX; total_slots],
            weighted_slots: Vec::new(),
        };
        st.rebuild_cov();
        st
    }

    fn to_row_vecs(&self) -> Vec<Vec<u8>> {
        let mut out = Vec::with_capacity(self.n);
        for r in 0..self.n {
            out.push(self.rows[r * self.k..(r + 1) * self.k].to_vec());
        }
        out
    }

    fn rebuild_cov(&mut self) {
        self.cov.fill(0);
        self.unc_list.clear();
        self.unc_pos.fill(u32::MAX);
        let k = self.k;
        let v = self.v;
        let v2 = self.v2;
        let v3 = self.v3;
        let v4 = self.v4;

        for r in 0..self.n {
            let row = &self.rows[r * k..(r + 1) * k];
            for (tid, &[c0, c1, c2, c3]) in self.quads.iter().enumerate() {
                let idx = tid * v4
                    + (row[c0 as usize] as usize) * v3
                    + (row[c1 as usize] as usize) * v2
                    + (row[c2 as usize] as usize) * v
                    + (row[c3 as usize] as usize);
                self.cov[idx] += 1;
            }
        }

        for (idx, &c) in self.cov.iter().enumerate() {
            if c == 0 {
                let pos = self.unc_list.len() as u32;
                self.unc_list.push(idx as u32);
                self.unc_pos[idx] = pos;
            }
        }
    }

    fn reset_weights(&mut self) {
        for &idx in &self.weighted_slots {
            self.weights[idx as usize] = 1;
        }
        self.weighted_slots.clear();
    }

    fn bump_unc_weights(&mut self, max_w: u16) {
        for &idx in &self.unc_list {
            let w = &mut self.weights[idx as usize];
            if *w == 1 {
                self.weighted_slots.push(idx);
            }
            if *w < max_w {
                *w += 1;
            }
        }
    }

    fn decay_weights(&mut self) {
        let mut i = 0;
        while i < self.weighted_slots.len() {
            let idx = self.weighted_slots[i] as usize;
            let w = self.weights[idx];
            if w > 2 {
                self.weights[idx] = w - 1;
                i += 1;
            } else {
                self.weights[idx] = 1;
                self.weighted_slots.swap_remove(i);
            }
        }
    }

    /// Independent full recompute of uncovered tuple count from `self.rows` only.
    fn full_recompute_unc(&self) -> (usize, Vec<u16>) {
        let mut fresh = vec![0u16; self.quads.len() * self.v4];
        for r in 0..self.n {
            let row = &self.rows[r * self.k..(r + 1) * self.k];
            for (tid, &[c0, c1, c2, c3]) in self.quads.iter().enumerate() {
                let idx = tid * self.v4
                    + (row[c0 as usize] as usize) * self.v3
                    + (row[c1 as usize] as usize) * self.v2
                    + (row[c2 as usize] as usize) * self.v
                    + (row[c3 as usize] as usize);
                fresh[idx] += 1;
            }
        }
        let unc = fresh.iter().filter(|&&c| c == 0).count();
        (unc, fresh)
    }

    #[inline(always)]
    fn unc(&self) -> usize {
        self.unc_list.len()
    }

    #[inline(always)]
    fn add_unc(&mut self, idx: usize) {
        debug_assert_eq!(self.unc_pos[idx], u32::MAX);
        let pos = self.unc_list.len() as u32;
        self.unc_list.push(idx as u32);
        self.unc_pos[idx] = pos;
    }

    #[inline(always)]
    fn rem_unc(&mut self, idx: usize) {
        let pos = self.unc_pos[idx] as usize;
        debug_assert!(pos < self.unc_list.len());
        let last = *self.unc_list.last().unwrap();
        self.unc_list[pos] = last;
        self.unc_pos[last as usize] = pos as u32;
        self.unc_list.pop();
        self.unc_pos[idx] = u32::MAX;
    }

    /// Exact O(C(k-1, 3)) delta in (raw_unc, weighted_unc) for changing (r, c) -> new_val.
    #[inline]
    fn eval_change(&self, r: usize, c: usize, new_val: u8) -> (i32, i32) {
        let row = &self.rows[r * self.k..(r + 1) * self.k];
        let old_val = row[c];
        if old_val == new_val {
            return (0, 0);
        }
        let ov = old_val as usize;
        let nv = new_val as usize;
        let cov = &self.cov;
        let weights = &self.weights;
        let mut d_unc = 0i32;
        let mut d_w = 0i32;

        // SAFETY: all indices are precomputed within bounds of `row`, `cov`, `weights`.
        for cq in &self.col_quads[c] {
            let base = (cq.tid_off as usize)
                + (unsafe { *row.get_unchecked(cq.o1 as usize) } as usize) * (cq.w1 as usize)
                + (unsafe { *row.get_unchecked(cq.o2 as usize) } as usize) * (cq.w2 as usize)
                + (unsafe { *row.get_unchecked(cq.o3 as usize) } as usize) * (cq.w3 as usize);
            let wc = cq.w_c as usize;
            let old_idx = base + ov * wc;
            let new_idx = base + nv * wc;
            let c_old = unsafe { *cov.get_unchecked(old_idx) };
            let c_new = unsafe { *cov.get_unchecked(new_idx) };
            if c_old == 1 {
                d_unc += 1;
                d_w += unsafe { *weights.get_unchecked(old_idx) } as i32;
            }
            if c_new == 0 {
                d_unc -= 1;
                d_w -= unsafe { *weights.get_unchecked(new_idx) } as i32;
            }
        }
        (d_unc, d_w)
    }

    /// Count how many 4-tuples touching (r, c) are uniquely covered (`cov == 1`).
    #[inline]
    fn cell_breaks(&self, r: usize, c: usize) -> usize {
        let row = &self.rows[r * self.k..(r + 1) * self.k];
        let ov = row[c] as usize;
        let cov = &self.cov;
        let mut breaks = 0usize;
        for cq in &self.col_quads[c] {
            let idx = (cq.tid_off as usize)
                + ov * (cq.w_c as usize)
                + (unsafe { *row.get_unchecked(cq.o1 as usize) } as usize) * (cq.w1 as usize)
                + (unsafe { *row.get_unchecked(cq.o2 as usize) } as usize) * (cq.w2 as usize)
                + (unsafe { *row.get_unchecked(cq.o3 as usize) } as usize) * (cq.w3 as usize);
            if unsafe { *cov.get_unchecked(idx) } == 1 {
                breaks += 1;
            }
        }
        breaks
    }

    /// Apply change (r, c) -> new_val and update cov / unc_list incrementally.
    fn apply_change(&mut self, r: usize, c: usize, new_val: u8) {
        let k = self.k;
        let n = self.n;
        let old_val = self.rows[r * k + c];
        if old_val == new_val {
            return;
        }
        let ov = old_val as usize;
        let nv = new_val as usize;

        let row_start = r * k;
        let cq_len = self.col_quads[c].len();
        for i in 0..cq_len {
            let cq = self.col_quads[c][i];
            let base = (cq.tid_off as usize)
                + (self.rows[row_start + cq.o1 as usize] as usize) * (cq.w1 as usize)
                + (self.rows[row_start + cq.o2 as usize] as usize) * (cq.w2 as usize)
                + (self.rows[row_start + cq.o3 as usize] as usize) * (cq.w3 as usize);
            let wc = cq.w_c as usize;
            let old_idx = base + ov * wc;
            let new_idx = base + nv * wc;

            let oc = self.cov[old_idx];
            debug_assert!(oc >= 1);
            self.cov[old_idx] = oc - 1;
            if oc == 1 {
                self.add_unc(old_idx);
            }

            let nc = self.cov[new_idx];
            self.cov[new_idx] = nc + 1;
            if nc == 0 {
                self.rem_unc(new_idx);
            }
        }

        self.rows[row_start + c] = new_val;
        self.cols[c * n + r] = new_val;
    }

    /// Compute number of uniquely-covered 4-tuples (`cov == 1`) for every row.
    fn compute_row_unique_counts(&self) -> Vec<u32> {
        let mut counts = vec![0u32; self.n];
        let k = self.k;
        let v = self.v;
        let v2 = self.v2;
        let v3 = self.v3;
        let v4 = self.v4;
        for r in 0..self.n {
            let row = &self.rows[r * k..(r + 1) * k];
            let mut u = 0u32;
            for (tid, &[c0, c1, c2, c3]) in self.quads.iter().enumerate() {
                let idx = tid * v4
                    + (row[c0 as usize] as usize) * v3
                    + (row[c1 as usize] as usize) * v2
                    + (row[c2 as usize] as usize) * v
                    + (row[c3 as usize] as usize);
                if self.cov[idx] == 1 {
                    u += 1;
                }
            }
            counts[r] = u;
        }
        counts
    }

    /// Delete row `target_r` (swap-remove with last row), updating cov, unc_list, rows, cols.
    fn delete_row(&mut self, target_r: usize) {
        assert!(target_r < self.n && self.n > 1);
        let k = self.k;
        let old_n = self.n;
        let last_r = old_n - 1;
        let v = self.v;
        let v2 = self.v2;
        let v3 = self.v3;
        let v4 = self.v4;

        // Decrement coverage for target_r
        let row_start = target_r * k;
        for tid in 0..self.quads.len() {
            let [c0, c1, c2, c3] = self.quads[tid];
            let idx = tid * v4
                + (self.rows[row_start + c0 as usize] as usize) * v3
                + (self.rows[row_start + c1 as usize] as usize) * v2
                + (self.rows[row_start + c2 as usize] as usize) * v
                + (self.rows[row_start + c3 as usize] as usize);
            let oc = self.cov[idx];
            debug_assert!(oc >= 1);
            self.cov[idx] = oc - 1;
            if oc == 1 {
                self.add_unc(idx);
            }
        }

        // Swap-remove in row-major storage
        if target_r != last_r {
            for c in 0..k {
                self.rows[target_r * k + c] = self.rows[last_r * k + c];
            }
        }
        self.n = old_n - 1;
        self.rows.truncate(self.n * k);

        // Rebuild compact column-major mirror
        self.cols.resize(k * self.n, 0);
        for r in 0..self.n {
            for c in 0..k {
                self.cols[c * self.n + r] = self.rows[r * k + c];
            }
        }
    }

    /// Try 0-break don't-care absorption to move uniquely-covered 4-tuples out of `target_r`
    /// into don't-care cells of other rows (without increasing `unc`).
    /// Returns number of absorbed tuples (so `target_r`'s unique count drops by at least this).
    fn absorb_row_zero_break(&mut self, target_r: usize, evals: &mut u64) -> usize {
        debug_assert_eq!(self.unc(), 0);
        let k = self.k;
        let n = self.n;
        let v = self.v;
        let v2 = self.v2;
        let v3 = self.v3;
        let v4 = self.v4;

        // Collect all uniquely-covered 4-tuples of target_r
        let mut unique_tuples: Vec<(usize, u8, u8, u8, u8)> = Vec::new();
        {
            let row = &self.rows[target_r * k..(target_r + 1) * k];
            for (tid, &[c0, c1, c2, c3]) in self.quads.iter().enumerate() {
                let y0 = row[c0 as usize];
                let y1 = row[c1 as usize];
                let y2 = row[c2 as usize];
                let y3 = row[c3 as usize];
                let idx = tid * v4
                    + (y0 as usize) * v3
                    + (y1 as usize) * v2
                    + (y2 as usize) * v
                    + (y3 as usize);
                if self.cov[idx] == 1 {
                    unique_tuples.push((tid, y0, y1, y2, y3));
                }
            }
        }

        let mut absorbed = 0usize;
        for (tid, y0, y1, y2, y3) in unique_tuples {
            let [c0, c1, c2, c3] = self.quads[tid];
            let idx = tid * v4
                + (y0 as usize) * v3
                + (y1 as usize) * v2
                + (y2 as usize) * v
                + (y3 as usize);
            if self.cov[idx] > 1 {
                // Already absorbed by an earlier move!
                absorbed += 1;
                continue;
            }
            // Scan for an HD-1 row r2 != target_r whose mismatching cell has 0 breaks
            let col0 = &self.cols[(c0 as usize) * n..(c0 as usize + 1) * n];
            let col1 = &self.cols[(c1 as usize) * n..(c1 as usize + 1) * n];
            let col2 = &self.cols[(c2 as usize) * n..(c2 as usize + 1) * n];
            let col3 = &self.cols[(c3 as usize) * n..(c3 as usize + 1) * n];

            let mut chosen: Option<(usize, usize, u8)> = None;
            for r2 in 0..n {
                if r2 == target_r {
                    continue;
                }
                let m0 = (col0[r2] == y0) as u8;
                let m1 = (col1[r2] == y1) as u8;
                let m2 = (col2[r2] == y2) as u8;
                let m3 = (col3[r2] == y3) as u8;
                if m0 + m1 + m2 + m3 == 3 {
                    let (mc, ny) = if m0 == 0 {
                        (c0 as usize, y0)
                    } else if m1 == 0 {
                        (c1 as usize, y1)
                    } else if m2 == 0 {
                        (c2 as usize, y2)
                    } else {
                        (c3 as usize, y3)
                    };
                    *evals += 1;
                    if self.cell_breaks(r2, mc) == 0 {
                        chosen = Some((r2, mc, ny));
                        break;
                    }
                }
            }
            if let Some((r2, mc, ny)) = chosen {
                self.apply_change(r2, mc, ny);
                absorbed += 1;
            }
        }
        absorbed
    }

    /// Collect all HD-1 candidate moves (r, c, new_val) that cover uncovered tuple `idx`.
    fn collect_hd1_candidates(&self, idx: usize, out: &mut Vec<(usize, u8, u8)>) {
        out.clear();
        let tid = idx / self.v4;
        let rem = idx % self.v4;
        let y0 = (rem / self.v3) as u8;
        let rem = rem % self.v3;
        let y1 = (rem / self.v2) as u8;
        let rem = rem % self.v2;
        let y2 = (rem / self.v) as u8;
        let y3 = (rem % self.v) as u8;

        let [c0, c1, c2, c3] = self.quads[tid];
        let n = self.n;
        let col0 = &self.cols[(c0 as usize) * n..(c0 as usize + 1) * n];
        let col1 = &self.cols[(c1 as usize) * n..(c1 as usize + 1) * n];
        let col2 = &self.cols[(c2 as usize) * n..(c2 as usize + 1) * n];
        let col3 = &self.cols[(c3 as usize) * n..(c3 as usize + 1) * n];

        for r in 0..n {
            let m0 = (unsafe { *col0.get_unchecked(r) } == y0) as u8;
            let m1 = (unsafe { *col1.get_unchecked(r) } == y1) as u8;
            let m2 = (unsafe { *col2.get_unchecked(r) } == y2) as u8;
            let m3 = (unsafe { *col3.get_unchecked(r) } == y3) as u8;
            if m0 + m1 + m2 + m3 == 3 {
                if m0 == 0 {
                    out.push((r, c0, y0));
                } else if m1 == 0 {
                    out.push((r, c1, y1));
                } else if m2 == 0 {
                    out.push((r, c2, y2));
                } else {
                    out.push((r, c3, y3));
                }
            }
        }
    }
}

// ---------- File I/O ----------

fn load_array(path: &Path) -> Vec<Vec<u8>> {
    let f = File::open(path).unwrap_or_else(|e| {
        eprintln!("ERROR opening {}: {}", path.display(), e);
        process::exit(2);
    });
    let reader = BufReader::new(f);
    let mut rows = Vec::new();
    for (ln, line_res) in reader.lines().enumerate() {
        let line = line_res.expect("read line");
        let s = line.trim();
        if s.is_empty() {
            continue;
        }
        let row: Vec<u8> = s
            .split_whitespace()
            .map(|tok| {
                tok.parse::<u8>().unwrap_or_else(|_| {
                    eprintln!("ERROR parsing int on line {}: {:?}", ln + 1, tok);
                    process::exit(2);
                })
            })
            .collect();
        rows.push(row);
    }
    rows
}

fn write_array_atomic(path: &Path, rows: &[Vec<u8>]) {
    if let Some(parent) = path.parent() {
        if !parent.as_os_str().is_empty() {
            fs::create_dir_all(parent).expect("create parent dirs");
        }
    }
    let tmp_path = path.with_extension("tmp_write");
    {
        let f = File::create(&tmp_path).expect("create tmp array");
        let mut w = BufWriter::new(f);
        for row in rows {
            for (i, &val) in row.iter().enumerate() {
                if i > 0 {
                    w.write_all(b" ").unwrap();
                }
                write!(w, "{}", val).unwrap();
            }
            w.write_all(b"\n").unwrap();
        }
        w.flush().unwrap();
    }
    fs::rename(&tmp_path, path).expect("atomic rename");
}

// ---------- Gate 0 Self-Test (>= 10,000 incremental vs brute-force checks) ----------

fn run_self_test(steps: usize, seed: u64) {
    let t0 = Instant::now();
    let mut rng = Rng::new(seed);

    // Test 1: small t=4, k=8, v=3 (N=120) -> 6000 single-cell moves + 5 row deletions
    // Test 2: target-scale t=4, k=11, v=8 (N=250) -> 6000 single-cell moves + 5 row deletions
    let configs = [(120usize, 8usize, 3usize, steps / 2), (250usize, 11usize, 8usize, steps - steps / 2)];
    let mut total_checks = 0usize;
    let mut total_deletes = 0usize;

    for (n_init, k, v, n_moves) in configs {
        let mut init_rows = Vec::with_capacity(n_init);
        for _ in 0..n_init {
            let mut r = Vec::with_capacity(k);
            for _ in 0..k {
                r.push(rng.gen_range(v) as u8);
            }
            init_rows.push(r);
        }
        let mut st = Ca4State::from_rows(&init_rows, v);
        let (fu0, fcov0) = st.full_recompute_unc();
        assert_eq!(st.unc(), fu0, "Initial unc mismatch");
        assert_eq!(st.cov, fcov0, "Initial cov mismatch");

        let check_every = if k >= 10 { 250 } else { 50 };
        for step in 1..=n_moves {
            let r = rng.gen_range(st.n);
            let c = rng.gen_range(st.k);
            let old_val = st.rows[r * st.k + c];
            let mut new_val = rng.gen_range(st.v) as u8;
            if new_val == old_val {
                new_val = ((old_val as usize + 1) % st.v) as u8;
            }
            let prev_unc = st.unc() as i32;
            let (pred_du, _) = st.eval_change(r, c, new_val);
            st.apply_change(r, c, new_val);
            let actual_du = (st.unc() as i32) - prev_unc;
            if pred_du != actual_du {
                eprintln!(
                    "SELF-TEST FAIL (k={}, v={}, step={}): pred_du={} != actual_du={}",
                    k, v, step, pred_du, actual_du
                );
                process::exit(1);
            }
            total_checks += 1;

            if step % check_every == 0 || step == n_moves {
                let (fu, fcov) = st.full_recompute_unc();
                if st.unc() != fu || st.cov != fcov {
                    eprintln!(
                        "SELF-TEST FAIL (k={}, v={}, step={}): full recompute mismatch unc {} vs {}",
                        k, v, step, st.unc(), fu
                    );
                    process::exit(1);
                }
                // Verify unc_list / unc_pos bijection
                for (pos, &idx) in st.unc_list.iter().enumerate() {
                    assert_eq!(st.cov[idx as usize], 0);
                    assert_eq!(st.unc_pos[idx as usize], pos as u32);
                }
            }
        }

        // Verify delete_row + compute_row_unique_counts against brute force
        for _ in 0..5 {
            let uniq = st.compute_row_unique_counts();
            let dr = rng.gen_range(st.n);
            let prev_unc = st.unc();
            let pred_add = uniq[dr] as usize;
            st.delete_row(dr);
            let (fu, fcov) = st.full_recompute_unc();
            assert_eq!(st.unc(), prev_unc + pred_add, "delete_row unc delta mismatch");
            assert_eq!(st.unc(), fu, "delete_row full recompute unc mismatch");
            assert_eq!(st.cov, fcov, "delete_row full recompute cov mismatch");
            total_deletes += 1;
        }
    }

    println!(
        "SELF_TEST_PASS: {} incremental cell deltas + {} row deletions verified against brute force (0 deviations, elapsed={:.3}s)",
        total_checks,
        total_deletes,
        t0.elapsed().as_secs_f64()
    );
}

// ---------- CLI & Main Search Loop ----------

struct Config {
    input: PathBuf,
    output: Option<PathBuf>,
    snapshot_dir: Option<PathBuf>,
    v: usize,
    threads: usize,
    seed: u64,
    time_limit_secs: f64,
    stagnation_secs: f64,
    target_n: usize,
    tabu_tenure: usize,
    rand_walk_pct: usize,
    paws_inc_interval: u64,
    paws_decay_interval: u64,
    max_weight: u16,
    absorb: bool,
    self_test: bool,
    self_test_steps: usize,
}

fn parse_args() -> Config {
    let args: Vec<String> = env::args().collect();
    let mut cfg = Config {
        input: PathBuf::new(),
        output: None,
        snapshot_dir: None,
        v: 8,
        threads: 2,
        seed: 5201,
        time_limit_secs: 30.0,
        stagnation_secs: 0.0,
        target_n: 0,
        tabu_tenure: 11,
        rand_walk_pct: 3,
        paws_inc_interval: 128,
        paws_decay_interval: 1024,
        max_weight: 12,
        absorb: true,
        self_test: false,
        self_test_steps: 12000,
    };

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--self-test" => {
                cfg.self_test = true;
            }
            "--self-test-steps" => {
                i += 1;
                cfg.self_test_steps = args[i].parse().expect("self-test-steps");
            }
            "--input" | "--resume" => {
                i += 1;
                cfg.input = PathBuf::from(&args[i]);
            }
            "--out" => {
                i += 1;
                cfg.output = Some(PathBuf::from(&args[i]));
            }
            "--snapshot-dir" => {
                i += 1;
                cfg.snapshot_dir = Some(PathBuf::from(&args[i]));
            }
            "--v" => {
                i += 1;
                cfg.v = args[i].parse().expect("v");
            }
            "--threads" => {
                i += 1;
                cfg.threads = args[i].parse().expect("threads");
            }
            "--seed" => {
                i += 1;
                cfg.seed = args[i].parse().expect("seed");
            }
            "--time-limit-secs" => {
                i += 1;
                cfg.time_limit_secs = args[i].parse().expect("time-limit-secs");
            }
            "--stagnation-secs" => {
                i += 1;
                cfg.stagnation_secs = args[i].parse().expect("stagnation-secs");
            }
            "--target-n" => {
                i += 1;
                cfg.target_n = args[i].parse().expect("target-n");
            }
            "--tabu-tenure" => {
                i += 1;
                cfg.tabu_tenure = args[i].parse().expect("tabu-tenure");
            }
            "--rand-walk-pct" => {
                i += 1;
                cfg.rand_walk_pct = args[i].parse().expect("rand-walk-pct");
            }
            "--no-absorb" => {
                cfg.absorb = false;
            }
            other => {
                eprintln!("Unknown argument: {}", other);
                process::exit(2);
            }
        }
        i += 1;
    }
    cfg
}

struct SharedBest {
    best_n: AtomicUsize,
    best_rows: Mutex<Vec<Vec<u8>>>,
    last_improve_ms: AtomicU64,
    stop: AtomicBool,
    total_steps: AtomicU64,
    total_evals: AtomicU64,
    total_absorbed: AtomicU64,
}

fn worker_loop(
    wid: usize,
    cfg: Arc<Config>,
    shared: Arc<SharedBest>,
    start_instant: Instant,
) {
    let mut rng = Rng::new(cfg.seed.wrapping_add((wid as u64).wrapping_mul(1_000_003)));
    let time_limit = Duration::from_secs_f64(cfg.time_limit_secs);
    let stag_limit_ms = if cfg.stagnation_secs > 0.0 {
        (cfg.stagnation_secs * 1000.0) as u64
    } else {
        u64::MAX
    };

    let mut local_evals = 0u64;
    let mut local_steps = 0u64;
    let mut cands: Vec<(usize, u8, u8)> = Vec::with_capacity(256);

    loop {
        if shared.stop.load(Ordering::Relaxed) || start_instant.elapsed() >= time_limit {
            break;
        }
        let now_ms = start_instant.elapsed().as_millis() as u64;
        let last_ms = shared.last_improve_ms.load(Ordering::Relaxed);
        if now_ms.saturating_sub(last_ms) >= stag_limit_ms {
            shared.stop.store(true, Ordering::Relaxed);
            break;
        }

        // Load latest global best valid array
        let base_rows = {
            let guard = shared.best_rows.lock().unwrap();
            guard.clone()
        };
        let cur_best_n = base_rows.len();
        if cfg.target_n > 0 && cur_best_n <= cfg.target_n {
            shared.stop.store(true, Ordering::Relaxed);
            break;
        }

        let mut st = Ca4State::from_rows(&base_rows, cfg.v);

        // If input is ALREADY valid (unc == 0), pick a low-unique row to absorb & delete!
        if st.unc() == 0 {
            let uniq = st.compute_row_unique_counts();

            // First check if any row has unique == 0 (instant free delete!)
            let mut ranked: Vec<(u32, usize)> =
                uniq.iter().enumerate().map(|(r, &u)| (u, r)).collect();
            ranked.sort_unstable_by_key(|&(u, _)| u);

            let min_u = ranked[0].0;
            let pick_idx = if min_u == 0 {
                ranked[0].1
            } else {
                // Diversify across threads among the top low-unique rows
                let top_k = ranked.len().min(if wid == 0 { 4 } else { 12 });
                ranked[rng.gen_range(top_k)].1
            };

            if min_u > 0 && cfg.absorb && uniq[pick_idx] <= 120 {
                let abs_cnt = st.absorb_row_zero_break(pick_idx, &mut local_evals);
                if abs_cnt > 0 {
                    shared.total_absorbed.fetch_add(abs_cnt as u64, Ordering::Relaxed);
                }
            }

            st.delete_row(pick_idx);

            if st.unc() == 0 {
                // Instant deletion succeeded!
                commit_new_best(&st, wid, &cfg, &shared, start_instant);
                continue;
            }
        }

        // Repair loop: Focused HD-1 Tabu + PAWS dynamic tuple weighting
        let n = st.n;
        let k = st.k;
        let v = st.v;
        let mut tabu: Vec<u64> = vec![0u64; n * k * v];
        let mut step_num = 0u64;
        let mut best_unc_this_attempt = st.unc();
        let mut steps_since_best = 0u64;
        // Restart attempt if stuck for too long on a single deleted row
        let attempt_patience = 25_000u64;

        while st.unc() > 0 {
            if (step_num & 255) == 0 {
                if shared.stop.load(Ordering::Relaxed) || start_instant.elapsed() >= time_limit {
                    break;
                }
                let now_ms = start_instant.elapsed().as_millis() as u64;
                let last_ms = shared.last_improve_ms.load(Ordering::Relaxed);
                if now_ms.saturating_sub(last_ms) >= stag_limit_ms {
                    shared.stop.store(true, Ordering::Relaxed);
                    break;
                }
                // Sync immediately if another worker improved best_n!
                if shared.best_n.load(Ordering::Relaxed) < cur_best_n {
                    break;
                }
            }

            if steps_since_best >= attempt_patience {
                // Abandon this deleted row choice and pick a fresh row from best_rows
                break;
            }

            step_num += 1;
            local_steps += 1;
            steps_since_best += 1;

            // Pick a random uncovered 4-tuple
            let u_idx = st.unc_list[rng.gen_range(st.unc_list.len())] as usize;
            st.collect_hd1_candidates(u_idx, &mut cands);

            if cands.is_empty() {
                // Rare fallback: pick random row and force one of the 4 columns
                let tid = u_idx / st.v4;
                let rem = u_idx % st.v4;
                let vals = [
                    (rem / st.v3) as u8,
                    ((rem % st.v3) / st.v2) as u8,
                    ((rem % st.v2) / st.v) as u8,
                    (rem % st.v) as u8,
                ];
                let pos = rng.gen_range(4);
                let c = st.quads[tid][pos] as usize;
                let r = rng.gen_range(n);
                st.apply_change(r, c, vals[pos]);
                continue;
            }

            // Random walk escape
            let chosen = if rng.gen_range(100) < cfg.rand_walk_pct {
                let (r, c, nv) = cands[rng.gen_range(cands.len())];
                (r, c as usize, nv)
            } else {
                let cur_unc = st.unc() as i32;
                let mut best_mv: Option<(usize, usize, u8)> = None;
                let mut best_score = i32::MAX;
                let mut best_ties = 0usize;

                let mut fb_mv: Option<(usize, usize, u8)> = None;
                let mut fb_score = i32::MAX;

                for &(r, c_u8, nv) in &cands {
                    let c = c_u8 as usize;
                    local_evals += 1;
                    let (du, dw) = st.eval_change(r, c, nv);
                    let new_unc = cur_unc + du;
                    // Immediate aspiration if unc == 0!
                    if new_unc == 0 {
                        best_mv = Some((r, c, nv));
                        break;
                    }
                    let is_tabu = tabu[(r * k + c) * v + (nv as usize)] > step_num;
                    let aspire = (new_unc as usize) < best_unc_this_attempt;
                    let score = dw * 4 + du;

                    if score < fb_score {
                        fb_score = score;
                        fb_mv = Some((r, c, nv));
                    }

                    if !is_tabu || aspire {
                        if score < best_score {
                            best_score = score;
                            best_mv = Some((r, c, nv));
                            best_ties = 1;
                        } else if score == best_score {
                            best_ties += 1;
                            if rng.gen_range(best_ties) == 0 {
                                best_mv = Some((r, c, nv));
                            }
                        }
                    }
                }
                best_mv.unwrap_or_else(|| fb_mv.unwrap())
            };

            let (r, c, nv) = chosen;
            let ov = st.rows[r * k + c] as usize;
            let tenure = cfg.tabu_tenure + rng.gen_range(5);
            tabu[(r * k + c) * v + ov] = step_num + (tenure as u64);
            st.apply_change(r, c, nv);

            if st.unc() < best_unc_this_attempt {
                best_unc_this_attempt = st.unc();
                steps_since_best = 0;
            }

            if (step_num % cfg.paws_inc_interval) == 0 {
                st.bump_unc_weights(cfg.max_weight);
            }
            if (step_num % cfg.paws_decay_interval) == 0 {
                st.decay_weights();
            }
        }

        if st.unc() == 0 {
            commit_new_best(&st, wid, &cfg, &shared, start_instant);
        } else {
            st.reset_weights();
        }
    }

    shared.total_evals.fetch_add(local_evals, Ordering::Relaxed);
    shared.total_steps.fetch_add(local_steps, Ordering::Relaxed);
}

fn commit_new_best(
    st: &Ca4State,
    wid: usize,
    cfg: &Config,
    shared: &SharedBest,
    start_instant: Instant,
) {
    // Mandatory independent full-recompute check before accepting any unc == 0 hit!
    let (fu, _) = st.full_recompute_unc();
    assert_eq!(fu, 0, "INTERNAL ERROR: incremental unc==0 failed full recompute ({})", fu);

    let new_n = st.n;
    let mut guard = shared.best_rows.lock().unwrap();
    if new_n < shared.best_n.load(Ordering::Relaxed) {
        let rows = st.to_row_vecs();
        *guard = rows.clone();
        shared.best_n.store(new_n, Ordering::Relaxed);
        shared
            .last_improve_ms
            .store(start_instant.elapsed().as_millis() as u64, Ordering::Relaxed);
        drop(guard);

        if let Some(ref out_p) = cfg.output {
            write_array_atomic(out_p, &rows);
        }
        if let Some(ref sdir) = cfg.snapshot_dir {
            let fname = format!("CA_{}_4_{}_{}.txt", new_n, st.k, st.v);
            write_array_atomic(&sdir.join(fname), &rows);
        }
        println!(
            "[t={:6.2}s][w{}] NEW_VALID: CA({}; 4, {}, {}) (full_recompute_unc=0)",
            start_instant.elapsed().as_secs_f64(),
            wid,
            new_n,
            st.k,
            st.v
        );
    }
}

fn main() {
    let cfg = parse_args();
    if cfg.self_test {
        run_self_test(cfg.self_test_steps, cfg.seed);
        return;
    }

    if cfg.input.as_os_str().is_empty() {
        eprintln!("Usage: t4_postop --input <file> --v <v> --out <file> --time-limit-secs <S> [--threads 2] [--seed 5201] [--stagnation-secs S] [--target-n N]");
        process::exit(2);
    }

    let start_instant = Instant::now();
    let init_rows = load_array(&cfg.input);
    let init_n = init_rows.len();
    let k = init_rows[0].len();
    let init_state = Ca4State::from_rows(&init_rows, cfg.v);
    let init_unc = init_state.unc();
    let init_min_u = if init_unc == 0 {
        let u = init_state.compute_row_unique_counts();
        *u.iter().min().unwrap_or(&0)
    } else {
        0
    };

    println!(
        "t4_postop start: input={} CA({}; 4, {}, {}) init_unc={} min_row_unique={} threads={} seed={} time_limit={:.1}s stagnation={:.1}s absorb={}",
        cfg.input.display(),
        init_n,
        k,
        cfg.v,
        init_unc,
        init_min_u,
        cfg.threads,
        cfg.seed,
        cfg.time_limit_secs,
        cfg.stagnation_secs,
        cfg.absorb
    );

    // If input is valid and --out is set, save initial baseline if no improvement occurs? No, only write on improvement or initial valid if requested; keep best_rows initialized.
    let shared = Arc::new(SharedBest {
        best_n: AtomicUsize::new(if init_unc == 0 { init_n } else { usize::MAX }),
        best_rows: Mutex::new(init_rows),
        last_improve_ms: AtomicU64::new(0),
        stop: AtomicBool::new(false),
        total_steps: AtomicU64::new(0),
        total_evals: AtomicU64::new(0),
        total_absorbed: AtomicU64::new(0),
    });

    let cfg_arc = Arc::new(cfg);
    let mut handles = Vec::new();
    for wid in 0..cfg_arc.threads {
        let c = Arc::clone(&cfg_arc);
        let s = Arc::clone(&shared);
        handles.push(thread::spawn(move || {
            worker_loop(wid, c, s, start_instant);
        }));
    }
    for h in handles {
        h.join().expect("worker panic");
    }

    let elapsed = start_instant.elapsed().as_secs_f64();
    let final_n = shared.best_n.load(Ordering::Relaxed);
    let saved = if init_unc == 0 && final_n <= init_n {
        init_n - final_n
    } else {
        0
    };
    let steps = shared.total_steps.load(Ordering::Relaxed);
    let evals = shared.total_evals.load(Ordering::Relaxed);
    let absorbed = shared.total_absorbed.load(Ordering::Relaxed);
    let evals_per_sec = if elapsed > 0.0 {
        (evals as f64) / elapsed
    } else {
        0.0
    };
    let steps_per_sec = if elapsed > 0.0 {
        (steps as f64) / elapsed
    } else {
        0.0
    };

    println!(
        "t4_postop done: init_N={} final_N={} saved={} absorbed_tuples={} steps={} ({:.0} steps/s) evals={} ({:.0} evals/s) elapsed={:.2}s",
        init_n, final_n, saved, absorbed, steps, steps_per_sec, evals, evals_per_sec, elapsed
    );
}
