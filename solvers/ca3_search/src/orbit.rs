use crate::rng::Rng;
use crate::state::CaState;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

#[inline(always)]
fn sub_mod(a: u32, b: u32, v: u32) -> u32 {
    if a >= b {
        a - b
    } else {
        a + v - b
    }
}

#[inline(always)]
fn add_mod(a: u32, b: u32, v: u32) -> u32 {
    let s = a + b;
    if s >= v {
        s - v
    } else {
        s
    }
}

#[inline(always)]
fn neg_mod(a: u32, v: u32) -> u32 {
    if a == 0 {
        0
    } else {
        v - a
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OrbitGroup {
    /// Cyclic group Z_v: x -> x + b (mod v), orbit size v (for v=5: 5)
    Zv,
    /// Dihedral-affine group G_{2v}: x -> s*x + b (mod v), s in {1, v-1}, b in Z_v (odd v >= 3; for v=5: G10, orbit size 10)
    G2v,
}

impl OrbitGroup {
    pub fn name(&self) -> &'static str {
        match self {
            OrbitGroup::Zv => "z5",
            OrbitGroup::G2v => "g10",
        }
    }

    pub fn orbit_size(&self, v: usize) -> usize {
        match self {
            OrbitGroup::Zv => v,
            OrbitGroup::G2v => {
                assert!(v % 2 == 1 && v >= 3, "G2v requires odd v >= 3");
                2 * v
            }
        }
    }

    pub fn orbits_per_triple(&self, v: usize) -> usize {
        match self {
            OrbitGroup::Zv => v * v,
            OrbitGroup::G2v => {
                assert!(v % 2 == 1 && v >= 3, "G2v requires odd v >= 3");
                // (0,0) constant orbit + (v^2 - 1)/2 non-constant orbits
                (v * v + 1) / 2
            }
        }
    }
}

#[derive(Clone, Copy, Debug)]
struct OrbitColTriple {
    /// triple_idx * num_orbits_per_triple
    base: u32,
    c_o1: u16,
    c_o2: u16,
    /// Position of `c` in (c0, c1, c2): 0, 1, or 2
    pos: u8,
}

/// Quotient orbit state for Z_v (order v) or G_{2v} (order 2v, e.g. G10 for v=5).
/// For Z_v: each triple has v^2 orbits indexed by (d1, d2) = ((a1-a0) mod v, (a2-a0) mod v).
/// For G_{2v} (odd v): each triple has (v^2+1)/2 orbits:
///   orbit 0 = (0,0) (constant tuples, covered by v constant rows),
///   orbits 1..(v^2-1)/2 = canonical min((d1,d2), ((-d1) mod v, (-d2) mod v)) lexicographically.
#[derive(Clone)]
pub struct OrbitState {
    pub group: OrbitGroup,
    pub num_starters: usize,
    pub k: usize,
    pub v: usize,
    pub num_orbits_per_triple: usize,
    pub has_const_rows: bool,
    pub num_triples: usize,
    pub tpc: usize,
    /// Starter matrix of size num_starters * k, values in 0..v
    pub starters: Vec<u8>,
    /// Lookup table: orb_map[d1 * v + d2] -> canonical orbit id in 0..num_orbits_per_triple
    pub orb_map: Vec<u32>,
    /// Canonical representative (d1, d2) for each canonical orbit id
    pub orb_reps: Vec<(u32, u32)>,
    /// Flat orbit counts of size num_triples * num_orbits_per_triple
    pub counts: Vec<u16>,
    pub uncovered_list: Vec<u32>,
    pub uncovered_pos: Vec<i32>,
    pub weights: Vec<u32>,
    pub triple_cols: Vec<[u16; 3]>,
    col_triples: Vec<OrbitColTriple>,
}

fn build_orbit_tables(group: OrbitGroup, v: usize) -> (Vec<u32>, Vec<(u32, u32)>) {
    let v_u32 = v as u32;
    let mut orb_map = vec![0u32; v * v];
    let mut orb_reps = Vec::new();
    match group {
        OrbitGroup::Zv => {
            for d1 in 0..v_u32 {
                for d2 in 0..v_u32 {
                    let id = (d1 * v_u32 + d2) as usize;
                    orb_map[id] = id as u32;
                    orb_reps.push((d1, d2));
                }
            }
        }
        OrbitGroup::G2v => {
            assert!(v % 2 == 1 && v >= 3, "G2v requires odd v >= 3");
            // Orbit 0 is (0, 0)
            orb_map[0] = 0;
            orb_reps.push((0, 0));
            let mut next_id = 1u32;
            for d1 in 0..v_u32 {
                for d2 in 0..v_u32 {
                    if d1 == 0 && d2 == 0 {
                        continue;
                    }
                    let nd1 = neg_mod(d1, v_u32);
                    let nd2 = neg_mod(d2, v_u32);
                    if (d1, d2) < (nd1, nd2) {
                        let id = next_id;
                        next_id += 1;
                        orb_map[(d1 * v_u32 + d2) as usize] = id;
                        orb_map[(nd1 * v_u32 + nd2) as usize] = id;
                        orb_reps.push((d1, d2));
                    }
                }
            }
            debug_assert_eq!(orb_reps.len(), (v * v + 1) / 2);
        }
    }
    (orb_map, orb_reps)
}

impl OrbitState {
    pub fn new_random(
        group: OrbitGroup,
        num_starters: usize,
        k: usize,
        v: usize,
        has_const_rows: bool,
        rng: &mut Rng,
    ) -> Self {
        let mut starters = vec![0u8; num_starters * k];
        for s in 0..num_starters {
            for c in 0..k {
                starters[s * k + c] = rng.gen_usize(v) as u8;
            }
        }
        Self::from_starters(group, starters, num_starters, k, v, has_const_rows)
    }

    pub fn from_starters(
        group: OrbitGroup,
        starters: Vec<u8>,
        num_starters: usize,
        k: usize,
        v: usize,
        has_const_rows: bool,
    ) -> Self {
        assert!(k >= 3 && v >= 2 && v <= 64);
        assert_eq!(starters.len(), num_starters * k);

        let (orb_map, orb_reps) = build_orbit_tables(group, v);
        let num_orbits_per_triple = orb_reps.len();
        debug_assert_eq!(num_orbits_per_triple, group.orbits_per_triple(v));

        let num_triples = k * (k - 1) * (k - 2) / 6;
        let tpc = (k - 1) * (k - 2) / 2;

        let mut triple_cols = Vec::with_capacity(num_triples);
        let mut per_col: Vec<Vec<OrbitColTriple>> = vec![Vec::with_capacity(tpc); k];

        let mut t_idx = 0u32;
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    triple_cols.push([c0 as u16, c1 as u16, c2 as u16]);
                    let base = t_idx * (num_orbits_per_triple as u32);
                    per_col[c0].push(OrbitColTriple {
                        base,
                        c_o1: c1 as u16,
                        c_o2: c2 as u16,
                        pos: 0,
                    });
                    per_col[c1].push(OrbitColTriple {
                        base,
                        c_o1: c0 as u16,
                        c_o2: c2 as u16,
                        pos: 1,
                    });
                    per_col[c2].push(OrbitColTriple {
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

        let total = num_triples * num_orbits_per_triple;
        let mut st = Self {
            group,
            num_starters,
            k,
            v,
            num_orbits_per_triple,
            has_const_rows,
            num_triples,
            tpc,
            starters,
            orb_map,
            orb_reps,
            counts: vec![0u16; total],
            uncovered_list: Vec::new(),
            uncovered_pos: vec![-1i32; total],
            weights: vec![1u32; total],
            triple_cols,
            col_triples,
        };
        st.recompute_counts();
        st
    }

    #[inline(always)]
    fn canon_orb(&self, d1: u32, d2: u32) -> u32 {
        unsafe { *self.orb_map.get_unchecked((d1 * (self.v as u32) + d2) as usize) }
    }

    pub fn recompute_counts(&mut self) {
        self.counts.fill(0);
        self.uncovered_list.clear();
        self.uncovered_pos.fill(-1);

        let v = self.v as u32;
        let nopt = self.num_orbits_per_triple;

        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                self.counts[t_idx * nopt] = 1; // orbit 0 = (0, 0) permanently covered by constant rows
            }
        }

        for s in 0..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let a0 = row[c0 as usize] as u32;
                let a1 = row[c1 as usize] as u32;
                let a2 = row[c2 as usize] as u32;
                let d1 = sub_mod(a1, a0, v);
                let d2 = sub_mod(a2, a0, v);
                let orb = self.canon_orb(d1, d2) as usize;
                let idx = t_idx * nopt + orb;
                self.counts[idx] += 1;
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

    #[inline(always)]
    pub fn eval_move(&self, s: usize, c: usize, new_val: u8, use_weights: bool) -> (i32, i64) {
        let row_off = s * self.k;
        let old_val = unsafe { *self.starters.get_unchecked(row_off + c) as u32 };
        let new_val = new_val as u32;
        if old_val == new_val {
            return (0, 0);
        }
        let v = self.v as u32;
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
                0 => {
                    let d1_old = sub_mod(o1, old_val, v);
                    let d2_old = sub_mod(o2, old_val, v);
                    let d1_new = sub_mod(o1, new_val, v);
                    let d2_new = sub_mod(o2, new_val, v);
                    (self.canon_orb(d1_old, d2_old), self.canon_orb(d1_new, d2_new))
                }
                1 => {
                    let d2 = sub_mod(o2, o1, v);
                    let d1_old = sub_mod(old_val, o1, v);
                    let d1_new = sub_mod(new_val, o1, v);
                    (self.canon_orb(d1_old, d2), self.canon_orb(d1_new, d2))
                }
                _ => {
                    let d1 = sub_mod(o2, o1, v);
                    let d2_old = sub_mod(old_val, o1, v);
                    let d2_new = sub_mod(new_val, o1, v);
                    (self.canon_orb(d1, d2_old), self.canon_orb(d1, d2_new))
                }
            };
            // Critical for G2v (G10): a cell change can map (d1, d2) -> (-d1, -d2),
            // which is the SAME canonical orbit! In that case, net count delta is 0.
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
        let row_off = s * self.k;
        let old_val = self.starters[row_off + c];
        if old_val == new_val {
            return old_val;
        }
        let old_u32 = old_val as u32;
        let new_u32 = new_val as u32;
        let v = self.v as u32;
        let t_start = c * self.tpc;
        let t_end = t_start + self.tpc;

        for ti in t_start..t_end {
            let ct = unsafe { *self.col_triples.get_unchecked(ti) };
            let o1 = unsafe { *self.starters.get_unchecked(row_off + ct.c_o1 as usize) as u32 };
            let o2 = unsafe { *self.starters.get_unchecked(row_off + ct.c_o2 as usize) as u32 };
            let (orb_old, orb_new) = match ct.pos {
                0 => {
                    let d1_old = sub_mod(o1, old_u32, v);
                    let d2_old = sub_mod(o2, old_u32, v);
                    let d1_new = sub_mod(o1, new_u32, v);
                    let d2_new = sub_mod(o2, new_u32, v);
                    (self.canon_orb(d1_old, d2_old), self.canon_orb(d1_new, d2_new))
                }
                1 => {
                    let d2 = sub_mod(o2, o1, v);
                    let d1_old = sub_mod(old_u32, o1, v);
                    let d1_new = sub_mod(new_u32, o1, v);
                    (self.canon_orb(d1_old, d2), self.canon_orb(d1_new, d2))
                }
                _ => {
                    let d1 = sub_mod(o2, o1, v);
                    let d2_old = sub_mod(old_u32, o1, v);
                    let d2_new = sub_mod(new_u32, o1, v);
                    (self.canon_orb(d1, d2_old), self.canon_orb(d1, d2_new))
                }
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

    /// Expands starters (+ optional v constant rows) into a full CaState of size
    /// `num_starters * orbit_size + (if has_const_rows { v } else { 0 })`.
    pub fn expand_exact_to_ca(&self) -> CaState {
        let const_n = if self.has_const_rows { self.v } else { 0 };
        let orb_sz = self.group.orbit_size(self.v);
        let n = self.num_starters * orb_sz + const_n;
        let mut mat = Vec::with_capacity(n * self.k);
        if self.has_const_rows {
            for b in 0..self.v {
                for _ in 0..self.k {
                    mat.push(b as u8);
                }
            }
        }
        match self.group {
            OrbitGroup::Zv => {
                for s in 0..self.num_starters {
                    let row = &self.starters[s * self.k..(s + 1) * self.k];
                    for b in 0..self.v {
                        for &val in row {
                            mat.push(((val as usize + b) % self.v) as u8);
                        }
                    }
                }
            }
            OrbitGroup::G2v => {
                for s in 0..self.num_starters {
                    let row = &self.starters[s * self.k..(s + 1) * self.k];
                    // s_mult = +1
                    for b in 0..self.v {
                        for &val in row {
                            mat.push(((val as usize + b) % self.v) as u8);
                        }
                    }
                    // s_mult = -1 (i.e., v - 1 mod v)
                    for b in 0..self.v {
                        for &val in row {
                            let neg = (self.v - (val as usize % self.v)) % self.v;
                            mat.push(((neg + b) % self.v) as u8);
                        }
                    }
                }
            }
        }
        CaState::from_matrix(mat, n, self.k, self.v)
    }

    pub fn verify_incremental(&self) -> Result<(), String> {
        let mut fresh = vec![0u16; self.num_triples * self.num_orbits_per_triple];
        let v = self.v as u32;
        let nopt = self.num_orbits_per_triple;
        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                fresh[t_idx * nopt] = 1;
            }
        }
        for s in 0..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for (t_idx, &[c0, c1, c2]) in self.triple_cols.iter().enumerate() {
                let a0 = row[c0 as usize] as u32;
                let a1 = row[c1 as usize] as u32;
                let a2 = row[c2 as usize] as u32;
                let d1 = sub_mod(a1, a0, v);
                let d2 = sub_mod(a2, a0, v);
                let orb = self.canon_orb(d1, d2) as usize;
                let idx = t_idx * nopt + orb;
                fresh[idx] += 1;
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
                    return Err(format!("orbit uncovered_pos mismatch at {}", idx));
                }
            } else if self.uncovered_pos[idx] != -1 {
                return Err(format!(
                    "covered orbit {} has uncovered_pos={}",
                    idx, self.uncovered_pos[idx]
                ));
            }
        }
        if diffs > 0 {
            return Err(format!("orbit count diffs: {}", diffs));
        }
        if fresh_unc != self.uncovered_list.len() {
            return Err(format!(
                "orbit uncovered len {} != fresh {}",
                self.uncovered_list.len(),
                fresh_unc
            ));
        }
        Ok(())
    }

    #[inline]
    fn push_focused_candidates_for_diff(
        &self,
        c0: usize,
        c1: usize,
        c2: usize,
        d1: u32,
        d2: u32,
        cands: &mut Vec<(usize, usize, u8)>,
    ) {
        let v_u32 = self.v as u32;
        let d21 = sub_mod(d2, d1, v_u32);
        let k = self.k;
        for s in 0..self.num_starters {
            let off = s * k;
            let a0 = unsafe { *self.starters.get_unchecked(off + c0) as u32 };
            let a1 = unsafe { *self.starters.get_unchecked(off + c1) as u32 };
            let a2 = unsafe { *self.starters.get_unchecked(off + c2) as u32 };
            if sub_mod(a2, a1, v_u32) == d21 {
                let t0 = sub_mod(a1, d1, v_u32) as u8;
                if t0 as u32 != a0 {
                    cands.push((s, c0, t0));
                }
            }
            if sub_mod(a2, a0, v_u32) == d2 {
                let t1 = add_mod(a0, d1, v_u32) as u8;
                if t1 as u32 != a1 {
                    cands.push((s, c1, t1));
                }
            }
            if sub_mod(a1, a0, v_u32) == d1 {
                let t2 = add_mod(a0, d2, v_u32) as u8;
                if t2 as u32 != a2 {
                    cands.push((s, c2, t2));
                }
            }
        }
    }

    #[inline]
    fn gather_focused_candidates(&self, u_idx: usize, cands: &mut Vec<(usize, usize, u8)>) {
        let nopt = self.num_orbits_per_triple;
        let t_idx = u_idx / nopt;
        let orb_id = u_idx % nopt;
        let (d1, d2) = self.orb_reps[orb_id];
        let [c0, c1, c2] = self.triple_cols[t_idx];
        let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);
        self.push_focused_candidates_for_diff(c0, c1, c2, d1, d2, cands);
        if self.group == OrbitGroup::G2v && (d1 != 0 || d2 != 0) {
            let v_u32 = self.v as u32;
            let nd1 = neg_mod(d1, v_u32);
            let nd2 = neg_mod(d2, v_u32);
            self.push_focused_candidates_for_diff(c0, c1, c2, nd1, nd2, cands);
        }
    }
}

#[derive(Clone, Debug)]
pub struct OrbitSearchConfig {
    pub tenure_base: u32,
    pub tenure_jitter: u32,
    pub noise_prob: f64,
    pub use_weights: bool,
    pub t_start: f64,
    pub t_end: f64,
    pub endgame_threshold: usize,
    pub log_interval_secs: f64,
    pub thread_id: usize,
}

impl Default for OrbitSearchConfig {
    fn default() -> Self {
        Self {
            tenure_base: 8,
            tenure_jitter: 7,
            noise_prob: 0.008,
            use_weights: true,
            t_start: 1.8,
            t_end: 0.05,
            endgame_threshold: 25,
            log_interval_secs: 30.0,
            thread_id: 0,
        }
    }
}

pub struct OrbitSearchResult {
    pub best_uncovered_orbits: usize,
    pub best_starters: Vec<u8>,
    pub moves: u64,
    pub reheats: u64,
}

/// Time-based geometric SA (T_start -> T_end over full budget, max 1 late reheat)
/// + Endgame Exact Full-Focused-Neighborhood Tabu (with clause weighting on plateaus when unc <= 25).
pub fn search_orbit(
    state: &mut OrbitState,
    rng: &mut Rng,
    cfg: &OrbitSearchConfig,
    deadline: Instant,
    stop: &AtomicBool,
    max_moves: Option<u64>,
) -> OrbitSearchResult {
    let k = state.k;
    let v = state.v;
    let v_u32 = v as u32;
    let num_s = state.num_starters;

    let t_start_time = Instant::now();
    let total_secs = deadline
        .saturating_duration_since(t_start_time)
        .as_secs_f64()
        .max(1e-3);
    let mut sched_t0 = cfg.t_start;
    let mut sched_start = t_start_time;
    let mut sched_dur = total_secs;

    let mut tabu = vec![0u32; num_s * k * v];
    let mut best_unc = state.uncovered_orbits();
    let mut best_starters = state.starters.clone();

    let mut iters: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut last_improve_time = t_start_time;
    let mut last_log_time = t_start_time;
    let mut reheats: u64 = 0;
    let mut max_weight: u32 = 1;
    let mut temp = sched_t0;

    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(640);

    while state.uncovered_orbits() > 0 {
        if let Some(lim) = max_moves {
            if iters >= lim {
                break;
            }
        }
        if (iters & 4095) == 0 {
            let now = Instant::now();
            if stop.load(Ordering::Relaxed) || now >= deadline {
                break;
            }
            let prog = (now.saturating_duration_since(sched_start).as_secs_f64() / sched_dur)
                .clamp(0.0, 1.0);
            temp = sched_t0 * (cfg.t_end / sched_t0).powf(prog);

            // At most ONE gentle late reheat if completely stagnant for >= 30% of budget while in mid-run
            let overall_prog =
                now.saturating_duration_since(t_start_time).as_secs_f64() / total_secs;
            let stag_secs = now.saturating_duration_since(last_improve_time).as_secs_f64();
            if reheats == 0
                && overall_prog >= 0.45
                && overall_prog <= 0.80
                && stag_secs >= total_secs * 0.28
                && total_secs >= 20.0
            {
                reheats += 1;
                state.starters.copy_from_slice(&best_starters);
                state.recompute_counts();
                state.weights.fill(1);
                tabu.fill(0);
                step_u32 = 1;
                max_weight = 1;
                sched_t0 = (cfg.t_start * 0.35).max(0.45);
                sched_start = now;
                sched_dur = deadline
                    .saturating_duration_since(now)
                    .as_secs_f64()
                    .max(1e-3);
                temp = sched_t0;
                last_improve_time = now;
                if cfg.log_interval_secs > 0.0 {
                    println!(
                        "    [orbit-{}:t={}] late-reheat #1 at {:.1}s -> T={:.3}, best_orb={}",
                        state.group.name(),
                        cfg.thread_id,
                        now.saturating_duration_since(t_start_time).as_secs_f64(),
                        temp,
                        best_unc
                    );
                }
            }

            if cfg.log_interval_secs > 0.0
                && now.saturating_duration_since(last_log_time).as_secs_f64()
                    >= cfg.log_interval_secs
            {
                let el = now.saturating_duration_since(t_start_time).as_secs_f64();
                println!(
                    "    [orbit-{}:t={}] t={:5.1}s | T={:.4} | cur_orb={:3} | best_orb={:3} | {:.0} it/s",
                    state.group.name(),
                    cfg.thread_id,
                    el,
                    temp,
                    state.uncovered_orbits(),
                    best_unc,
                    iters as f64 / el.max(1e-9)
                );
                last_log_time = now;
            }
        }

        if step_u32 > 4_000_000_000 {
            tabu.fill(0);
            step_u32 = 1;
        }

        iters += 1;
        let ulen = state.uncovered_list.len();

        // ENDGAME MODE (unc <= endgame_threshold): Exact Full-Focused-Neighborhood Tabu + Clause Weighting
        if ulen <= cfg.endgame_threshold && (temp <= 0.45 || rng.chance(0.75)) {
            cands.clear();
            for si in 0..ulen {
                let u_idx = state.uncovered_list[si] as usize;
                state.gather_focused_candidates(u_idx, &mut cands);
            }
            if !cands.is_empty() {
                let cur_unc = ulen as i32;
                let chosen = if rng.chance(cfg.noise_prob * 0.5) {
                    cands[rng.gen_usize(cands.len())]
                } else {
                    let mut best_nt_score = (i64::MAX, i32::MAX);
                    let mut best_nt_move = cands[0];
                    let mut nt_ties = 0u64;

                    let mut best_all_score = (i64::MAX, i32::MAX);
                    let mut best_all_move = cands[0];
                    let mut all_ties = 0u64;

                    for &(s, c, nv) in &cands {
                        let (du, dw) = state.eval_move(s, c, nv, cfg.use_weights);
                        // Primary: improving true unc first if du < 0, otherwise weighted score
                        let score = if du < 0 {
                            (i64::MIN / 2 + du as i64, du)
                        } else {
                            (dw, du)
                        };
                        let asp = (cur_unc + du) < (best_unc as i32);
                        let is_tabu = !asp && tabu[(s * k + c) * v + nv as usize] > step_u32;

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

                        if !is_tabu {
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

                    if nt_ties > 0 {
                        if cfg.use_weights && best_nt_score.1 > 0 {
                            for &ui in &state.uncovered_list {
                                let w = &mut state.weights[ui as usize];
                                *w += 1;
                                if *w > max_weight {
                                    max_weight = *w;
                                }
                            }
                            if max_weight > 200 {
                                for wv in &mut state.weights {
                                    *wv = (*wv >> 1).max(1);
                                }
                                max_weight >>= 1;
                            }
                        }
                        best_nt_move
                    } else {
                        best_all_move
                    }
                };

                let (s, c, nv) = chosen;
                let old_v = state.apply_move(s, c, nv);
                let tenure =
                    cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
                tabu[(s * k + c) * v + old_v as usize] = step_u32 + tenure;
                step_u32 += 1;

                let new_unc = state.uncovered_orbits();
                if new_unc < best_unc {
                    best_unc = new_unc;
                    best_starters.copy_from_slice(&state.starters);
                    last_improve_time = Instant::now();
                    if new_unc == 0 {
                        break;
                    }
                }
                continue;
            }
        }

        // SA MODE: 15% fast random starter-cell Metropolis move (zero/low-cost restructuring)
        if rng.chance(0.15) {
            let s = rng.gen_usize(num_s);
            let c = rng.gen_usize(k);
            let old_v = state.starters[s * k + c];
            let nv = ((old_v as usize + 1 + rng.gen_usize(v - 1)) % v) as u8;
            let (du, _) = state.eval_move(s, c, nv, false);
            let accept = if du <= 0 {
                true
            } else {
                rng.gen_f64() < (-(du as f64) / temp).exp()
            };
            if accept {
                let ov = state.apply_move(s, c, nv);
                let tenure =
                    cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
                tabu[(s * k + c) * v + ov as usize] = step_u32 + tenure;
                step_u32 += 1;
                let new_unc = state.uncovered_orbits();
                if new_unc < best_unc {
                    best_unc = new_unc;
                    best_starters.copy_from_slice(&state.starters);
                    last_improve_time = Instant::now();
                    if new_unc == 0 {
                        break;
                    }
                }
            }
            continue;
        }

        // SA Focused step: pick 1 uncovered orbit, evaluate all focused candidates, Metropolis gate
        let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        cands.clear();
        state.gather_focused_candidates(u_idx, &mut cands);

        if cands.is_empty() {
            let nopt = state.num_orbits_per_triple;
            let t_idx = u_idx / nopt;
            let orb_id = u_idx % nopt;
            let (d1, d2) = state.orb_reps[orb_id];
            let [c0, c1, c2] = state.triple_cols[t_idx];
            let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);
            let s = rng.gen_usize(num_s);
            let off = s * k;
            let a0 = state.starters[off + c0] as u32;
            let t1 = add_mod(a0, d1, v_u32) as u8;
            if t1 != state.starters[off + c1] {
                cands.push((s, c1, t1));
            }
            let t2 = add_mod(a0, d2, v_u32) as u8;
            if t2 != state.starters[off + c2] {
                cands.push((s, c2, t2));
            }
            if cands.is_empty() {
                continue;
            }
        }

        let cur_unc = ulen as i32;
        let mut best_nt_du = i32::MAX;
        let mut best_nt_move = cands[0];
        let mut nt_ties = 0u64;

        let mut best_all_du = i32::MAX;
        let mut best_all_move = cands[0];
        let mut all_ties = 0u64;

        for &(s, c, nv) in &cands {
            let (du, _) = state.eval_move(s, c, nv, false);
            let asp = (cur_unc + du) < (best_unc as i32);
            let is_tabu = !asp && tabu[(s * k + c) * v + nv as usize] > step_u32;

            if du < best_all_du {
                best_all_du = du;
                best_all_move = (s, c, nv);
                all_ties = 1;
            } else if du == best_all_du {
                all_ties += 1;
                if rng.gen_usize(all_ties as usize) == 0 {
                    best_all_move = (s, c, nv);
                }
            }

            if !is_tabu {
                if du < best_nt_du {
                    best_nt_du = du;
                    best_nt_move = (s, c, nv);
                    nt_ties = 1;
                } else if du == best_nt_du {
                    nt_ties += 1;
                    if rng.gen_usize(nt_ties as usize) == 0 {
                        best_nt_move = (s, c, nv);
                    }
                }
            }
        }

        let (chosen, chosen_du) = if nt_ties > 0 {
            (best_nt_move, best_nt_du)
        } else {
            (best_all_move, best_all_du)
        };

        let accept = if chosen_du <= 0 {
            true
        } else {
            rng.gen_f64() < (-(chosen_du as f64) / temp).exp()
        };

        if accept {
            let (s, c, nv) = chosen;
            let old_v = state.apply_move(s, c, nv);
            let tenure = cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
            tabu[(s * k + c) * v + old_v as usize] = step_u32 + tenure;
            step_u32 += 1;

            let new_unc = state.uncovered_orbits();
            if new_unc < best_unc {
                best_unc = new_unc;
                best_starters.copy_from_slice(&state.starters);
                last_improve_time = Instant::now();
                if new_unc == 0 {
                    break;
                }
            }
        }
    }

    state.starters.copy_from_slice(&best_starters);
    state.recompute_counts();

    OrbitSearchResult {
        best_uncovered_orbits: best_unc,
        best_starters,
        moves: iters,
        reheats,
    }
}

pub fn orbit_sanity_test(
    group: OrbitGroup,
    k: usize,
    v: usize,
    num_starters: usize,
    has_const: bool,
) -> Result<(f64, usize, usize), String> {
    let mut rng = Rng::from_seed(0xC0FFEE_1234 ^ (group.orbit_size(v) as u64));
    let mut st = OrbitState::new_random(group, num_starters, k, v, has_const, &mut rng);
    st.verify_incremental()?;

    let cfg = OrbitSearchConfig {
        tenure_base: 7,
        tenure_jitter: 5,
        noise_prob: 0.008,
        use_weights: true,
        t_start: 1.5,
        t_end: 0.1,
        endgame_threshold: 25,
        log_interval_secs: 0.0,
        thread_id: 0,
    };
    let t0 = Instant::now();
    let stop = AtomicBool::new(false);
    let res = search_orbit(
        &mut st,
        &mut rng,
        &cfg,
        t0 + Duration::from_secs(30),
        &stop,
        Some(10_000),
    );
    let dt = t0.elapsed().as_secs_f64().max(1e-9);
    st.verify_incremental()?;

    // 10,000 raw incremental moves without recompute_counts verifying exact eval_move delta & final counts
    let mut st2 = OrbitState::from_starters(group, st.starters.clone(), num_starters, k, v, has_const);
    let mut rng2 = Rng::from_seed(0xABCDEF_5678 ^ (group.orbit_size(v) as u64));
    for step in 0..10_000 {
        let s = rng2.gen_usize(num_starters);
        let c = rng2.gen_usize(k);
        let nv = rng2.gen_usize(v) as u8;
        let before = st2.uncovered_orbits() as i32;
        let (du, _) = st2.eval_move(s, c, nv, true);
        st2.apply_move(s, c, nv);
        let after = st2.uncovered_orbits() as i32;
        if after - before != du {
            return Err(format!(
                "orbit({}) eval_move delta mismatch at step {}: predicted {}, actual {}",
                group.name(),
                step,
                du,
                after - before
            ));
        }
    }
    st2.verify_incremental()?;

    // Verify exact expansion invariant: expanded.uncovered() == orbit_size * st2.uncovered_orbits()
    // (holds identically whenever has_const == true, since all uncovered orbits are non-constant!)
    let expanded = st2.expand_exact_to_ca();
    expanded.verify_incremental()?;
    let orb_sz = group.orbit_size(v);
    if has_const && expanded.uncovered() != orb_sz * st2.uncovered_orbits() {
        return Err(format!(
            "orbit({}) expansion mismatch: expanded.uncovered={} != {}*orbit_unc={}",
            group.name(),
            expanded.uncovered(),
            orb_sz,
            orb_sz * st2.uncovered_orbits()
        ));
    }
    Ok((res.moves as f64 / dt, res.best_uncovered_orbits, expanded.n))
}
