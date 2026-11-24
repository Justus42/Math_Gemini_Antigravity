use crate::rng::Rng;
use crate::state::CaState;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProjGroup {
    /// PGL(2, 5) acting on P^1(F_5) = {0,1,2,3,4,5} (5 = inf), order 120.
    /// Non-constant orbits per triple: aab(30), aba(30), baa(30), D(120).
    Pgl25,
    /// PSL(2, 5) acting on P^1(F_5) = {0,1,2,3,4,5} (5 = inf), order 60.
    /// Non-constant orbits per triple: aab(30), aba(30), baa(30), D1(60), D2(60).
    Psl25,
}

impl ProjGroup {
    pub fn name(&self) -> &'static str {
        match self {
            ProjGroup::Pgl25 => "pgl25",
            ProjGroup::Psl25 => "psl25",
        }
    }

    pub fn order(&self) -> usize {
        match self {
            ProjGroup::Pgl25 => 120,
            ProjGroup::Psl25 => 60,
        }
    }

    pub fn orbits_per_triple(&self) -> usize {
        match self {
            ProjGroup::Pgl25 => 5, // const(6), aab(30), aba(30), baa(30), D(120)
            ProjGroup::Psl25 => 6, // const(6), aab(30), aba(30), baa(30), D1(60), D2(60)
        }
    }
}

#[inline]
fn inv_mod5(x: u8) -> u8 {
    match x % 5 {
        1 => 1,
        2 => 3,
        3 => 2,
        4 => 4,
        _ => panic!("no inverse for 0 mod 5"),
    }
}

/// Generates exact group permutations on P^1(F_5) = {0,1,2,3,4,5} (5 = inf):
/// - PGL(2,5): det = ad - bc != 0 (mod 5) -> 120 distinct permutations.
/// - PSL(2,5): det in {1, 4} (squares mod 5) -> 60 distinct permutations.
pub fn generate_proj_group(group: ProjGroup) -> Vec<[u8; 6]> {
    let mut perms: Vec<[u8; 6]> = Vec::with_capacity(group.order());
    for a in 0..5u8 {
        for b in 0..5u8 {
            for c in 0..5u8 {
                for d in 0..5u8 {
                    let det = ((a as i32 * d as i32 - b as i32 * c as i32).rem_euclid(5)) as u8;
                    if det == 0 {
                        continue;
                    }
                    if group == ProjGroup::Psl25 && det != 1 && det != 4 {
                        continue;
                    }
                    let mut p = [0u8; 6];
                    for z in 0..5u8 {
                        let num = (a * z + b) % 5;
                        let den = (c * z + d) % 5;
                        p[z as usize] = if den == 0 {
                            5
                        } else {
                            (num * inv_mod5(den)) % 5
                        };
                    }
                    // z = inf = 5
                    p[5] = if c == 0 { 5 } else { (a * inv_mod5(c)) % 5 };
                    if !perms.contains(&p) {
                        perms.push(p);
                    }
                }
            }
        }
    }
    perms.sort();
    assert_eq!(
        perms.len(),
        group.order(),
        "unexpected group order for {}",
        group.name()
    );
    perms
}

/// Generates a fixed coset representative set R_30 subset of PSL(2,5) (hence also subset of PGL(2,5))
/// containing exactly 1 element g per ordered pair (g(0), g(5)) with g(0) != g(5).
pub fn generate_r30(perms: &[[u8; 6]]) -> Vec<[u8; 6]> {
    let mut seen_pair = [[false; 6]; 6];
    let mut r30 = Vec::with_capacity(30);
    for &p in perms {
        let x = p[0] as usize;
        let y = p[5] as usize;
        debug_assert_ne!(x, y);
        if !seen_pair[x][y] {
            seen_pair[x][y] = true;
            r30.push(p);
        }
    }
    assert_eq!(r30.len(), 30, "R_30 must have exactly 30 coset reps");
    r30
}

/// Builds exact tuple_to_orbit[216] lookup and orbit_sizes vector directly from the group action:
///   orbit 0: aaa (size 6)
///   orbit 1: aab (size 30)
///   orbit 2: aba (size 30)
///   orbit 3: baa (size 30)
///   Pgl25: orbit 4 = D (size 120)
///   Psl25: orbit 4 = D1 (size 60, containing (0,1,5)), orbit 5 = D2 (size 60)
fn build_proj_orbit_table(group: ProjGroup, perms: &[[u8; 6]]) -> ([u8; 216], Vec<usize>) {
    let mut map = [255u8; 216];
    let seeds: Vec<(usize, [u8; 3], usize)> = match group {
        ProjGroup::Pgl25 => vec![
            (0, [0, 0, 0], 6),
            (1, [0, 0, 5], 30),
            (2, [0, 5, 0], 30),
            (3, [5, 0, 0], 30),
            (4, [0, 1, 5], 120),
        ],
        ProjGroup::Psl25 => vec![
            (0, [0, 0, 0], 6),
            (1, [0, 0, 5], 30),
            (2, [0, 5, 0], 30),
            (3, [5, 0, 0], 30),
            (4, [0, 1, 5], 60),
            (5, [0, 2, 5], 60),
        ],
    };

    let mut sizes = vec![0usize; seeds.len()];
    for &(oid, [a, b, c], expected_sz) in &seeds {
        let mut cnt = 0usize;
        for p in perms {
            let x = p[a as usize] as usize;
            let y = p[b as usize] as usize;
            let z = p[c as usize] as usize;
            let idx = (x * 6 + y) * 6 + z;
            if map[idx] == 255 {
                map[idx] = oid as u8;
                cnt += 1;
            } else {
                assert_eq!(map[idx], oid as u8, "overlapping orbit at tuple {}", idx);
            }
        }
        assert_eq!(
            cnt,
            expected_sz,
            "orbit {} size mismatch for {}: got {}, expected {}",
            oid,
            group.name(),
            cnt,
            expected_sz
        );
        sizes[oid] = cnt;
    }
    for (idx, &m) in map.iter().enumerate() {
        assert_ne!(m, 255, "unassigned tuple {} in {}", idx, group.name());
    }
    (map, sizes)
}

#[derive(Clone, Copy, Debug)]
struct ProjColTriple {
    /// triple_idx * num_orbits_per_triple
    base: u32,
    c_o1: u16,
    c_o2: u16,
    /// Position of `c` in (c0, c1, c2): 0, 1, or 2
    pos: u8,
}

/// Mixed-starter quotient orbit state for PGL(2,5) and PSL(2,5) on P^1(F_5) (v=6):
/// - `num_gen` general starters over {0,1,2,3,4,5}, expanded by all |G| group elements (120 or 60 rows each)
/// - `num_bin` binary starters over {0, 5}, expanded by R_30 (30 rows each)
/// - optional `6` constant rows covering orbit 0 (aaa)
/// Total rows: N = |G| * num_gen + 30 * num_bin + (if has_const_rows { 6 } else { 0 }).
#[derive(Clone)]
pub struct ProjOrbitState {
    pub group: ProjGroup,
    pub num_gen: usize,
    pub num_bin: usize,
    pub num_starters: usize,
    pub k: usize,
    pub has_const_rows: bool,
    pub nopt: usize,
    pub num_triples: usize,
    pub tpc: usize,
    /// Starter matrix of size (num_gen + num_bin) * k.
    /// Rows 0..num_gen take values in 0..=5; rows num_gen..num_starters take values in {0, 5}.
    pub starters: Vec<u8>,
    pub tuple_to_orbit: [u8; 216],
    pub orbit_sizes: Vec<usize>,
    pub perms: Vec<[u8; 6]>,
    pub r30: Vec<[u8; 6]>,
    pub counts: Vec<u16>,
    pub uncovered_list: Vec<u32>,
    pub uncovered_pos: Vec<i32>,
    pub weights: Vec<u32>,
    pub triple_cols: Vec<[u16; 3]>,
    col_triples: Vec<ProjColTriple>,
}

impl ProjOrbitState {
    pub fn new_random(
        group: ProjGroup,
        num_gen: usize,
        num_bin: usize,
        k: usize,
        has_const_rows: bool,
        rng: &mut Rng,
    ) -> Self {
        let num_starters = num_gen + num_bin;
        let mut starters = vec![0u8; num_starters * k];
        for s in 0..num_gen {
            for c in 0..k {
                starters[s * k + c] = rng.gen_usize(6) as u8;
            }
        }
        for s in num_gen..num_starters {
            for c in 0..k {
                starters[s * k + c] = if rng.gen_usize(2) == 0 { 0 } else { 5 };
            }
        }
        Self::from_starters(group, starters, num_gen, num_bin, k, has_const_rows)
    }

    pub fn from_starters(
        group: ProjGroup,
        starters: Vec<u8>,
        num_gen: usize,
        num_bin: usize,
        k: usize,
        has_const_rows: bool,
    ) -> Self {
        let num_starters = num_gen + num_bin;
        assert!(k >= 3 && num_starters >= 1);
        assert_eq!(starters.len(), num_starters * k);
        for s in 0..num_gen {
            for c in 0..k {
                assert!(starters[s * k + c] < 6);
            }
        }
        for s in num_gen..num_starters {
            for c in 0..k {
                let val = starters[s * k + c];
                assert!(
                    val == 0 || val == 5,
                    "binary starter row {} col {} has invalid symbol {} (must be 0 or 5)",
                    s,
                    c,
                    val
                );
            }
        }

        let perms = generate_proj_group(group);
        let r30 = generate_r30(&perms);
        let (tuple_to_orbit, orbit_sizes) = build_proj_orbit_table(group, &perms);
        let nopt = group.orbits_per_triple();
        let num_triples = k * (k - 1) * (k - 2) / 6;
        let tpc = (k - 1) * (k - 2) / 2;

        let mut triple_cols = Vec::with_capacity(num_triples);
        let mut per_col: Vec<Vec<ProjColTriple>> = vec![Vec::with_capacity(tpc); k];

        let mut t_idx = 0u32;
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    triple_cols.push([c0 as u16, c1 as u16, c2 as u16]);
                    let base = t_idx * (nopt as u32);
                    per_col[c0].push(ProjColTriple {
                        base,
                        c_o1: c1 as u16,
                        c_o2: c2 as u16,
                        pos: 0,
                    });
                    per_col[c1].push(ProjColTriple {
                        base,
                        c_o1: c0 as u16,
                        c_o2: c2 as u16,
                        pos: 1,
                    });
                    per_col[c2].push(ProjColTriple {
                        base,
                        c_o1: c0 as u16,
                        c_o2: c1 as u16,
                        pos: 2,
                    });
                    t_idx += 1;
                }
            }
        }

        let mut col_triples = Vec::with_capacity(k * tpc);
        for c in 0..k {
            col_triples.extend_from_slice(&per_col[c]);
        }

        let total = num_triples * nopt;
        let mut st = Self {
            group,
            num_gen,
            num_bin,
            num_starters,
            k,
            has_const_rows,
            nopt,
            num_triples,
            tpc,
            starters,
            tuple_to_orbit,
            orbit_sizes,
            perms,
            r30,
            counts: vec![0u16; total],
            uncovered_list: Vec::new(),
            uncovered_pos: vec![-1i32; total],
            weights: vec![16u32; total],
            triple_cols,
            col_triples,
        };
        st.recompute_counts();
        st
    }

    pub fn expanded_n(&self) -> usize {
        self.num_gen * self.group.order()
            + self.num_bin * 30
            + if self.has_const_rows { 6 } else { 0 }
    }

    #[inline(always)]
    fn orb_of(&self, a: u32, b: u32, c: u32) -> u32 {
        unsafe { *self.tuple_to_orbit.get_unchecked(((a * 6 + b) * 6 + c) as usize) as u32 }
    }

    pub fn recompute_counts(&mut self) {
        self.counts.fill(0);
        self.uncovered_list.clear();
        self.uncovered_pos.fill(-1);

        let nopt = self.nopt;
        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                self.counts[t_idx * nopt] = 1; // orbit 0 = aaa covered by 6 constant rows
            }
        }

        for s in 0..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let orb = self.orb_of(
                    row[c0 as usize] as u32,
                    row[c1 as usize] as u32,
                    row[c2 as usize] as u32,
                ) as usize;
                self.counts[t_idx * nopt + orb] += 1;
            }
        }

        for (idx, &cnt) in self.counts.iter().enumerate() {
            if cnt == 0 {
                let pos = self.uncovered_list.len() as i32;
                self.uncovered_list.push(idx as u32);
                self.uncovered_pos[idx] = pos;
            }
        }
    }

    #[inline(always)]
    pub fn uncovered_orbits(&self) -> usize {
        self.uncovered_list.len()
    }

    /// Computes exact weighted expanded uncovered tuple count:
    ///   Pgl25: 120 * unc_D + 30 * unc_2sym (+ 6 * unc_const)
    ///   Psl25: 60 * (unc_D1 + unc_D2) + 30 * unc_2sym (+ 6 * unc_const)
    pub fn expected_expanded_uncovered(&self) -> usize {
        let nopt = self.nopt;
        let mut total = 0usize;
        for &u_idx in &self.uncovered_list {
            let orb = (u_idx as usize) % nopt;
            total += self.orbit_sizes[orb];
        }
        total
    }

    #[inline(always)]
    pub fn eval_move(&self, s: usize, c: usize, new_val: u8, use_weights: bool) -> (i32, i64) {
        let row_off = s * self.k;
        let old_val = unsafe { *self.starters.get_unchecked(row_off + c) as u32 };
        let new_val = new_val as u32;
        if old_val == new_val {
            return (0, 0);
        }
        let row = &self.starters[row_off..row_off + self.k];
        let cts = &self.col_triples[c * self.tpc..(c + 1) * self.tpc];
        let counts = &self.counts;
        let weights = &self.weights;

        let mut delta_unc: i32 = 0;
        let mut delta_w: i32 = 0;

        for ct in cts {
            let o1 = unsafe { *row.get_unchecked(ct.c_o1 as usize) as u32 };
            let o2 = unsafe { *row.get_unchecked(ct.c_o2 as usize) as u32 };
            let (orb_old, orb_new) = match ct.pos {
                0 => (self.orb_of(old_val, o1, o2), self.orb_of(new_val, o1, o2)),
                1 => (self.orb_of(o1, old_val, o2), self.orb_of(o1, new_val, o2)),
                _ => (self.orb_of(o1, o2, old_val), self.orb_of(o1, o2, new_val)),
            };
            if orb_old == orb_new {
                continue;
            }
            let idx_old = (ct.base + orb_old) as usize;
            let idx_new = (ct.base + orb_new) as usize;
            let c_old = unsafe { *counts.get_unchecked(idx_old) };
            let c_new = unsafe { *counts.get_unchecked(idx_new) };
            let lose = (c_old == 1) as i32;
            let gain = (c_new == 0) as i32;
            delta_unc += lose - gain;
            if use_weights {
                let w_old = unsafe { *weights.get_unchecked(idx_old) as i32 };
                let w_new = unsafe { *weights.get_unchecked(idx_new) as i32 };
                delta_w += lose * w_old - gain * w_new;
            }
        }
        if !use_weights {
            (delta_unc, delta_unc as i64)
        } else {
            (delta_unc, delta_w as i64)
        }
    }

    #[inline]
    pub fn apply_move(&mut self, s: usize, c: usize, new_val: u8) -> u8 {
        debug_assert!(if s < self.num_gen {
            new_val < 6
        } else {
            new_val == 0 || new_val == 5
        });
        let row_off = s * self.k;
        let old_val = self.starters[row_off + c];
        if old_val == new_val {
            return old_val;
        }
        let old_u32 = old_val as u32;
        let new_u32 = new_val as u32;
        let t_start = c * self.tpc;
        let t_end = t_start + self.tpc;

        for ti in t_start..t_end {
            let ct = unsafe { *self.col_triples.get_unchecked(ti) };
            let o1 = unsafe { *self.starters.get_unchecked(row_off + ct.c_o1 as usize) as u32 };
            let o2 = unsafe { *self.starters.get_unchecked(row_off + ct.c_o2 as usize) as u32 };
            let (orb_old, orb_new) = match ct.pos {
                0 => (self.orb_of(old_u32, o1, o2), self.orb_of(new_u32, o1, o2)),
                1 => (self.orb_of(o1, old_u32, o2), self.orb_of(o1, new_u32, o2)),
                _ => (self.orb_of(o1, o2, old_u32), self.orb_of(o1, o2, new_u32)),
            };
            if orb_old == orb_new {
                continue;
            }
            let idx_old = (ct.base + orb_old) as usize;
            let idx_new = (ct.base + orb_new) as usize;

            let c_old = unsafe { self.counts.get_unchecked_mut(idx_old) };
            debug_assert!(*c_old >= 1);
            *c_old -= 1;
            if *c_old == 0 {
                let pos = self.uncovered_list.len() as i32;
                self.uncovered_list.push(idx_old as u32);
                unsafe {
                    *self.uncovered_pos.get_unchecked_mut(idx_old) = pos;
                }
            }

            let c_new = unsafe { self.counts.get_unchecked_mut(idx_new) };
            let was_zero = *c_new == 0;
            *c_new += 1;
            if was_zero {
                let pos = unsafe { *self.uncovered_pos.get_unchecked(idx_new) } as usize;
                let last_idx = self.uncovered_list.pop().unwrap();
                if pos < self.uncovered_list.len() {
                    self.uncovered_list[pos] = last_idx;
                    unsafe {
                        *self.uncovered_pos.get_unchecked_mut(last_idx as usize) = pos as i32;
                    }
                }
                unsafe {
                    *self.uncovered_pos.get_unchecked_mut(idx_new) = -1;
                }
            }
        }
        self.starters[row_off + c] = new_val;
        old_val
    }

    /// Expands mixed starters into a full CaState of exact size:
    ///   N = |G| * num_gen + 30 * num_bin + (if has_const_rows { 6 } else { 0 }).
    pub fn expand_exact_to_ca(&self) -> CaState {
        let n = self.expanded_n();
        let mut mat = Vec::with_capacity(n * self.k);
        if self.has_const_rows {
            for sym in 0..6u8 {
                for _ in 0..self.k {
                    mat.push(sym);
                }
            }
        }
        // General starters expanded by all |G| group elements
        for s in 0..self.num_gen {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for p in &self.perms {
                for &val in row {
                    mat.push(p[val as usize]);
                }
            }
        }
        // Binary {0, 5} starters expanded by fixed coset reps R_30 (30 rows each)
        for s in self.num_gen..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for p in &self.r30 {
                for &val in row {
                    mat.push(p[val as usize]);
                }
            }
        }
        debug_assert_eq!(mat.len(), n * self.k);
        CaState::from_matrix(mat, n, self.k, 6)
    }

    pub fn verify_incremental(&self) -> Result<(), String> {
        let mut fresh = vec![0u16; self.num_triples * self.nopt];
        let nopt = self.nopt;
        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                fresh[t_idx * nopt] = 1;
            }
        }
        for s in 0..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let orb = self.orb_of(
                    row[c0 as usize] as u32,
                    row[c1 as usize] as u32,
                    row[c2 as usize] as u32,
                ) as usize;
                fresh[t_idx * nopt + orb] += 1;
            }
        }
        let mut diffs = 0usize;
        let mut fresh_unc = 0usize;
        for idx in 0..fresh.len() {
            if fresh[idx] != self.counts[idx] {
                diffs += 1;
            }
            if fresh[idx] == 0 {
                fresh_unc += 1;
                let pos = self.uncovered_pos[idx];
                if pos < 0
                    || (pos as usize) >= self.uncovered_list.len()
                    || self.uncovered_list[pos as usize] != idx as u32
                {
                    return Err(format!("proj uncovered_pos mismatch at {}", idx));
                }
            } else if self.uncovered_pos[idx] != -1 {
                return Err(format!(
                    "covered proj orbit {} has uncovered_pos={}",
                    idx, self.uncovered_pos[idx]
                ));
            }
        }
        if diffs > 0 {
            return Err(format!("proj count diffs: {}", diffs));
        }
        if fresh_unc != self.uncovered_list.len() {
            return Err(format!(
                "proj uncovered len {} != fresh {}",
                self.uncovered_list.len(),
                fresh_unc
            ));
        }
        Ok(())
    }

    #[inline]
    fn gather_focused_dedup(
        &self,
        u_idx: usize,
        seen: &mut [u32],
        stamp: u32,
        cands: &mut Vec<(usize, usize, u8)>,
    ) {
        let nopt = self.nopt;
        let t_idx = u_idx / nopt;
        let target_orb = (u_idx % nopt) as u32;
        let [c0, c1, c2] = self.triple_cols[t_idx];
        let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);
        let k = self.k;

        // Binary starters can only cover 2-symbol orbits (1, 2, 3) or const (0), never D/D1/D2 (>= 4).
        let s_end = if target_orb >= 4 {
            self.num_gen
        } else {
            self.num_starters
        };

        for s in 0..s_end {
            let off = s * k;
            let a0 = unsafe { *self.starters.get_unchecked(off + c0) as u32 };
            let a1 = unsafe { *self.starters.get_unchecked(off + c1) as u32 };
            let a2 = unsafe { *self.starters.get_unchecked(off + c2) as u32 };

            if s < self.num_gen {
                // General starter: values 0..6
                for nv in 0..6u32 {
                    if nv != a0 && self.orb_of(nv, a1, a2) == target_orb {
                        let key = (off + c0) * 6 + nv as usize;
                        if unsafe { *seen.get_unchecked(key) } != stamp {
                            unsafe { *seen.get_unchecked_mut(key) = stamp };
                            cands.push((s, c0, nv as u8));
                        }
                    }
                    if nv != a1 && self.orb_of(a0, nv, a2) == target_orb {
                        let key = (off + c1) * 6 + nv as usize;
                        if unsafe { *seen.get_unchecked(key) } != stamp {
                            unsafe { *seen.get_unchecked_mut(key) = stamp };
                            cands.push((s, c1, nv as u8));
                        }
                    }
                    if nv != a2 && self.orb_of(a0, a1, nv) == target_orb {
                        let key = (off + c2) * 6 + nv as usize;
                        if unsafe { *seen.get_unchecked(key) } != stamp {
                            unsafe { *seen.get_unchecked_mut(key) = stamp };
                            cands.push((s, c2, nv as u8));
                        }
                    }
                }
            } else {
                // Binary starter: only flip 0 <-> 5
                let nv0 = if a0 == 0 { 5u32 } else { 0u32 };
                if self.orb_of(nv0, a1, a2) == target_orb {
                    let key = (off + c0) * 6 + nv0 as usize;
                    if unsafe { *seen.get_unchecked(key) } != stamp {
                        unsafe { *seen.get_unchecked_mut(key) = stamp };
                        cands.push((s, c0, nv0 as u8));
                    }
                }
                let nv1 = if a1 == 0 { 5u32 } else { 0u32 };
                if self.orb_of(a0, nv1, a2) == target_orb {
                    let key = (off + c1) * 6 + nv1 as usize;
                    if unsafe { *seen.get_unchecked(key) } != stamp {
                        unsafe { *seen.get_unchecked_mut(key) = stamp };
                        cands.push((s, c1, nv1 as u8));
                    }
                }
                let nv2 = if a2 == 0 { 5u32 } else { 0u32 };
                if self.orb_of(a0, a1, nv2) == target_orb {
                    let key = (off + c2) * 6 + nv2 as usize;
                    if unsafe { *seen.get_unchecked(key) } != stamp {
                        unsafe { *seen.get_unchecked_mut(key) = stamp };
                        cands.push((s, c2, nv2 as u8));
                    }
                }
            }
        }
    }
}

#[derive(Clone, Debug)]
pub struct ProjSearchConfig {
    pub tenure_min: u32,
    pub tenure_max: u32,
    pub noise_prob: f64,
    pub full_scan_thresh: usize,
    /// Optional restart after this many moves without improving current-restart best (0 = off)
    pub restart_stagnation: u64,
    pub base_seed: u64,
    pub log_interval_secs: f64,
    pub thread_id: usize,
}

pub struct ProjSearchResult {
    pub best_uncovered_orbits: usize,
    pub best_expanded_uncovered: usize,
    pub best_starters: Vec<u8>,
    pub moves: u64,
    pub smoothings: u64,
    pub restarts: u64,
    pub best_at_60s: usize,
    pub best_at_120s: usize,
    pub last_improve_sec: f64,
}

/// Non-freezing Focused Tabu + fractional fixed-point SWT (BASE_W=16..MAX_W=26)
/// for mixed PGL(2,5) / PSL(2,5) starter search.
pub fn search_proj_tabu_cw(
    state: &mut ProjOrbitState,
    rng: &mut Rng,
    cfg: &ProjSearchConfig,
    deadline: Instant,
    stop: &AtomicBool,
    max_moves: Option<u64>,
) -> ProjSearchResult {
    let k = state.k;
    let num_s = state.num_starters;
    let nopt = state.nopt;
    let total_cells_v = num_s * k * 6;

    // Base weight proportional to true expanded orbit size:
    //   size 30 (2-sym) -> 16, size 60 (D1/D2) -> 32, size 120 (D) -> 64.
    // Prevents general starters from collapsing into binary rows and directly minimizes true expanded_unc!
    let mut orb_base_w = vec![16u32; nopt];
    for oid in 0..nopt {
        orb_base_w[oid] = ((state.orbit_sizes[oid] / 30) as u32 * 16).max(16);
    }
    const MAX_EXCESS: u32 = 10;
    for (idx, w) in state.weights.iter_mut().enumerate() {
        *w = orb_base_w[idx % nopt];
    }

    let t0 = Instant::now();
    let mut tabu = vec![0u32; total_cells_v];
    let mut seen = vec![0u32; total_cells_v];
    let mut stamp: u32 = 1;

    let mut best_unc = state.uncovered_orbits();
    let mut best_exp_unc = state.expected_expanded_uncovered();
    let mut best_starters = state.starters.clone();
    let mut best_in_restart = best_unc;
    let mut best_at_60s = best_unc;
    let mut best_at_120s = best_unc;
    let mut recorded_60 = false;
    let mut recorded_120 = false;
    let mut last_improve_sec = 0.0f64;

    let mut moves: u64 = 0;
    let mut stag_moves: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut plateau_steps: u32 = 0;
    let mut max_excess: u32 = 0;
    let mut smoothings: u64 = 0;
    let mut restarts: u64 = 0;
    let mut last_log = t0;

    let tenure_span = (cfg.tenure_max.saturating_sub(cfg.tenure_min) + 1) as usize;
    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(total_cells_v);

    while state.uncovered_orbits() > 0 {
        if let Some(lim) = max_moves {
            if moves >= lim {
                break;
            }
        }
        if (moves & 1023) == 0 {
            let now = Instant::now();
            let el = now.saturating_duration_since(t0).as_secs_f64();
            if !recorded_60 && el >= 60.0 {
                best_at_60s = best_unc;
                recorded_60 = true;
            }
            if !recorded_120 && el >= 120.0 {
                best_at_120s = best_unc;
                recorded_120 = true;
            }
            if stop.load(Ordering::Relaxed) || now >= deadline {
                break;
            }
            if cfg.log_interval_secs > 0.0
                && now.saturating_duration_since(last_log).as_secs_f64() >= cfg.log_interval_secs
            {
                println!(
                    "    [proj-{}:t={}] t={:5.1}s | cur_orb={:3} | best_orb={:3} (exp={:4}, last@{:5.1}s) | exc={:2} rst={} | {:.0} mv/s",
                    state.group.name(),
                    cfg.thread_id,
                    el,
                    state.uncovered_orbits(),
                    best_unc,
                    best_exp_unc,
                    last_improve_sec,
                    max_excess,
                    restarts,
                    moves as f64 / el.max(1e-9)
                );
                last_log = now;
            }
        }

        if step_u32 > 4_000_000_000 {
            tabu.fill(0);
            step_u32 = 1;
        }
        if stamp == u32::MAX {
            seen.fill(0);
            stamp = 1;
        } else {
            stamp += 1;
        }

        let ulen = state.uncovered_list.len();
        cands.clear();

        if ulen <= cfg.full_scan_thresh {
            for si in 0..ulen {
                let u_idx = state.uncovered_list[si] as usize;
                state.gather_focused_dedup(u_idx, &mut seen, stamp, &mut cands);
            }
        } else {
            for _ in 0..8 {
                let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
                state.gather_focused_dedup(u_idx, &mut seen, stamp, &mut cands);
            }
        }

        if cands.is_empty() {
            for s in 0..num_s {
                for c in 0..k {
                    let ov = state.starters[s * k + c];
                    if s < state.num_gen {
                        for nv in 0..6u8 {
                            if nv != ov {
                                cands.push((s, c, nv));
                            }
                        }
                    } else {
                        cands.push((s, c, if ov == 0 { 5 } else { 0 }));
                    }
                }
            }
        }

        let cur_unc = ulen as i32;
        let (chosen_move, min_nt_raw_du) = if rng.chance(cfg.noise_prob) {
            let mv = cands[rng.gen_usize(cands.len())];
            (mv, -1)
        } else {
            let mut best_asp_score = (i32::MAX, i64::MAX);
            let mut best_asp_move = cands[0];
            let mut asp_ties = 0u64;

            let mut best_nt_score = (i64::MAX, i32::MAX);
            let mut best_nt_move = cands[0];
            let mut nt_ties = 0u64;
            let mut min_nt_du = i32::MAX;

            let mut best_all_score = (i64::MAX, i32::MAX);
            let mut best_all_move = cands[0];
            let mut all_ties = 0u64;

            for &(s, c, nv) in &cands {
                let (du, dw) = state.eval_move(s, c, nv, true);
                let asp = (cur_unc + du) < (best_in_restart as i32) || (cur_unc + du) == 0;
                if asp {
                    let ascore = (du, dw);
                    if ascore < best_asp_score {
                        best_asp_score = ascore;
                        best_asp_move = (s, c, nv);
                        asp_ties = 1;
                    } else if ascore == best_asp_score {
                        asp_ties += 1;
                        if rng.gen_usize(asp_ties as usize) == 0 {
                            best_asp_move = (s, c, nv);
                        }
                    }
                }

                let score = (dw, du);
                if score < best_all_score {
                    best_all_score = score;
                    best_all_move = (s, c, nv);
                    all_ties = 1;
                } else if score == best_all_score {
                    all_ties += 1;
                    if rng.gen_usize(all_ties as usize) == 0 {
                        best_all_move = (s, c, nv);
                    }
                }

                let is_tabu = tabu[(s * k + c) * 6 + nv as usize] > step_u32;
                if !is_tabu {
                    if du < min_nt_du {
                        min_nt_du = du;
                    }
                    if score < best_nt_score {
                        best_nt_score = score;
                        best_nt_move = (s, c, nv);
                        nt_ties = 1;
                    } else if score == best_nt_score {
                        nt_ties += 1;
                        if rng.gen_usize(nt_ties as usize) == 0 {
                            best_nt_move = (s, c, nv);
                        }
                    }
                }
            }

            if asp_ties > 0 {
                (best_asp_move, -1)
            } else if nt_ties > 0 {
                (best_nt_move, min_nt_du)
            } else {
                (best_all_move, best_all_score.1)
            }
        };

        // Fractional SWT Clause Weighting ONLY on true plateau/local minimum
        if min_nt_raw_du >= 0 {
            plateau_steps += 1;
            for &ui in &state.uncovered_list {
                let uidx = ui as usize;
                let bw = orb_base_w[uidx % nopt];
                let w = unsafe { state.weights.get_unchecked_mut(uidx) };
                *w += 1;
                let exc = w.saturating_sub(bw);
                if exc > max_excess {
                    max_excess = exc;
                }
            }
            if plateau_steps >= 500 || max_excess > MAX_EXCESS {
                let mut new_max_exc = 0u32;
                for (idx, w) in state.weights.iter_mut().enumerate() {
                    let bw = orb_base_w[idx % nopt];
                    let excess = w.saturating_sub(bw);
                    let new_exc = (excess * 3) >> 2;
                    *w = bw + new_exc;
                    if new_exc > new_max_exc {
                        new_max_exc = new_exc;
                    }
                }
                max_excess = new_max_exc;
                plateau_steps = 0;
                smoothings += 1;
            }
        }

        let (s, c, nv) = chosen_move;
        let old_v = state.apply_move(s, c, nv);
        let tenure = cfg.tenure_min + rng.gen_usize(tenure_span) as u32;
        tabu[(s * k + c) * 6 + old_v as usize] = step_u32 + tenure;
        moves += 1;
        stag_moves += 1;
        step_u32 += 1;

        let new_unc = state.uncovered_orbits();
        if new_unc < best_in_restart {
            best_in_restart = new_unc;
            stag_moves = 0;
            if new_unc < best_unc
                || (new_unc == best_unc && state.expected_expanded_uncovered() < best_exp_unc)
            {
                best_unc = new_unc;
                best_exp_unc = state.expected_expanded_uncovered();
                best_starters.copy_from_slice(&state.starters);
                last_improve_sec = t0.elapsed().as_secs_f64();
                if new_unc == 0 {
                    break;
                }
            }
        } else if cfg.restart_stagnation > 0 && stag_moves >= cfg.restart_stagnation {
            restarts += 1;
            let rst_seed = cfg
                .base_seed
                .wrapping_add(restarts.wrapping_mul(0x9e37_79b9_7f4a_7c15))
                ^ (restarts << 32);
            *rng = Rng::from_seed(rst_seed);
            for sr in 0..state.num_gen {
                for col in 0..k {
                    state.starters[sr * k + col] = rng.gen_usize(6) as u8;
                }
            }
            for sr in state.num_gen..num_s {
                for col in 0..k {
                    state.starters[sr * k + col] = if rng.gen_usize(2) == 0 { 0 } else { 5 };
                }
            }
            state.recompute_counts();
            for (idx, w) in state.weights.iter_mut().enumerate() {
                *w = orb_base_w[idx % nopt];
            }
            tabu.fill(0);
            step_u32 = 1;
            max_excess = 0;
            plateau_steps = 0;
            best_in_restart = state.uncovered_orbits();
            stag_moves = 0;
            if best_in_restart < best_unc
                || (best_in_restart == best_unc
                    && state.expected_expanded_uncovered() < best_exp_unc)
            {
                best_unc = best_in_restart;
                best_exp_unc = state.expected_expanded_uncovered();
                best_starters.copy_from_slice(&state.starters);
                last_improve_sec = t0.elapsed().as_secs_f64();
                if best_in_restart == 0 {
                    break;
                }
            }
        }
    }

    if !recorded_60 {
        best_at_60s = best_unc;
    }
    if !recorded_120 {
        best_at_120s = best_unc;
    }

    state.starters.copy_from_slice(&best_starters);
    state.recompute_counts();

    ProjSearchResult {
        best_uncovered_orbits: best_unc,
        best_expanded_uncovered: best_exp_unc,
        best_starters,
        moves,
        smoothings,
        restarts,
        best_at_60s,
        best_at_120s,
        last_improve_sec,
    }
}

/// Mandatory 10,000-move incremental + exact weighted expansion sanity check for PGL(2,5) and PSL(2,5).
pub fn proj_sanity_test(
    group: ProjGroup,
    num_gen: usize,
    num_bin: usize,
    k: usize,
    has_const: bool,
) -> Result<(f64, usize, usize, usize), String> {
    let seed = 0x9E37_79B9 ^ (group.order() as u64) ^ ((k as u64) << 16);
    let mut rng = Rng::from_seed(seed);
    let mut st = ProjOrbitState::new_random(group, num_gen, num_bin, k, has_const, &mut rng);
    st.verify_incremental()?;

    let cfg = ProjSearchConfig {
        tenure_min: 7,
        tenure_max: 10,
        noise_prob: 0.002,
        full_scan_thresh: 500,
        restart_stagnation: 4000,
        base_seed: seed,
        log_interval_secs: 0.0,
        thread_id: 0,
    };
    let t0 = Instant::now();
    let stop = AtomicBool::new(false);
    let res = search_proj_tabu_cw(
        &mut st,
        &mut rng,
        &cfg,
        t0 + Duration::from_secs(30),
        &stop,
        Some(10_000),
    );
    let dt = t0.elapsed().as_secs_f64().max(1e-9);
    st.verify_incremental()?;

    // 10,000 raw incremental eval_move/apply_move checks without recompute_counts
    let mut st2 =
        ProjOrbitState::from_starters(group, st.starters.clone(), num_gen, num_bin, k, has_const);
    let mut rng2 = Rng::from_seed(0x517C_C1B7 ^ (group.order() as u64));
    for step in 0..10_000 {
        let s = rng2.gen_usize(st2.num_starters);
        let c = rng2.gen_usize(k);
        let nv = if s < num_gen {
            rng2.gen_usize(6) as u8
        } else if rng2.gen_usize(2) == 0 {
            0u8
        } else {
            5u8
        };
        let before = st2.uncovered_orbits() as i32;
        let (du, _) = st2.eval_move(s, c, nv, true);
        st2.apply_move(s, c, nv);
        let after = st2.uncovered_orbits() as i32;
        if after - before != du {
            return Err(format!(
                "proj({}) eval_move delta mismatch at step {}: predicted {}, actual {}",
                group.name(),
                step,
                du,
                after - before
            ));
        }
    }
    st2.verify_incremental()?;

    // Verify exact weighted expansion invariant:
    //   pgl25: expanded.unc == 120 * unc_D + 30 * unc_2sym
    //   psl25: expanded.unc == 60 * (unc_D1 + unc_D2) + 30 * unc_2sym
    let expanded = st2.expand_exact_to_ca();
    expanded.verify_incremental()?;
    let expected_unc = st2.expected_expanded_uncovered();
    if expanded.uncovered() != expected_unc {
        return Err(format!(
            "proj({}) weighted expansion mismatch: expanded.unc={} != expected={}",
            group.name(),
            expanded.uncovered(),
            expected_unc
        ));
    }

    Ok((
        res.moves as f64 / dt,
        res.best_uncovered_orbits,
        res.best_expanded_uncovered,
        expanded.n,
    ))
}
