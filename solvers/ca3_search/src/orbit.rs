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

#[derive(Clone, Copy, Debug)]
struct OrbitColTriple {
    /// triple_idx * v^2
    base: u32,
    c_o1: u16,
    c_o2: u16,
    /// Position of `c` in (c0, c1, c2): 0, 1, or 2
    pos: u8,
}

/// Quotient Z_v-orbit state for cyclic development of t=3 covering arrays.
/// Each starter row s = (s_0, ..., s_{k-1}) generates v cyclic shifts:
///   row(s, d)[c] = (s_c + d) mod v,  d = 0..v-1.
/// Each column triple has v^2 Z_v-orbits indexed by (d1, d2) = ((a1-a0) mod v, (a2-a0) mod v).
/// If `has_const_rows` is true, the v constant rows (0..0)..(v-1..v-1) permanently cover orbit (0,0).
#[derive(Clone)]
pub struct OrbitState {
    pub num_starters: usize,
    pub k: usize,
    pub v: usize,
    pub v2: usize,
    pub has_const_rows: bool,
    pub num_triples: usize,
    pub tpc: usize,
    /// Starter matrix of size num_starters * k, values in 0..v
    pub starters: Vec<u8>,
    /// Flat orbit counts of size num_triples * v^2
    pub counts: Vec<u16>,
    pub uncovered_list: Vec<u32>,
    pub uncovered_pos: Vec<i32>,
    pub weights: Vec<u32>,
    pub triple_cols: Vec<[u16; 3]>,
    col_triples: Vec<OrbitColTriple>,
}

impl OrbitState {
    pub fn new_random(
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
        Self::from_starters(starters, num_starters, k, v, has_const_rows)
    }

    pub fn from_starters(
        starters: Vec<u8>,
        num_starters: usize,
        k: usize,
        v: usize,
        has_const_rows: bool,
    ) -> Self {
        assert!(k >= 3 && v >= 2 && v <= 64);
        assert_eq!(starters.len(), num_starters * k);

        let v2 = v * v;
        let num_triples = k * (k - 1) * (k - 2) / 6;
        let tpc = (k - 1) * (k - 2) / 2;

        let mut triple_cols = Vec::with_capacity(num_triples);
        let mut per_col: Vec<Vec<OrbitColTriple>> = vec![Vec::with_capacity(tpc); k];

        let mut t_idx = 0u32;
        for c0 in 0..k {
            for c1 in (c0 + 1)..k {
                for c2 in (c1 + 1)..k {
                    triple_cols.push([c0 as u16, c1 as u16, c2 as u16]);
                    let base = t_idx * (v2 as u32);
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

        let total = num_triples * v2;
        let mut st = Self {
            num_starters,
            k,
            v,
            v2,
            has_const_rows,
            num_triples,
            tpc,
            starters,
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

    pub fn recompute_counts(&mut self) {
        self.counts.fill(0);
        self.uncovered_list.clear();
        self.uncovered_pos.fill(-1);

        let v = self.v as u32;
        let v2 = self.v2;

        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                self.counts[t_idx * v2] = 1; // orbit (0, 0) permanently covered by constant rows
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
                let idx = t_idx * v2 + (d1 * v + d2) as usize;
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
        let mut delta_w: i64 = 0;

        for ct in cts {
            let o1 = unsafe { *row.get_unchecked(ct.c_o1 as usize) as u32 };
            let o2 = unsafe { *row.get_unchecked(ct.c_o2 as usize) as u32 };
            let (orb_old, orb_new) = match ct.pos {
                0 => {
                    let d1_old = sub_mod(o1, old_val, v);
                    let d2_old = sub_mod(o2, old_val, v);
                    let d1_new = sub_mod(o1, new_val, v);
                    let d2_new = sub_mod(o2, new_val, v);
                    (d1_old * v + d2_old, d1_new * v + d2_new)
                }
                1 => {
                    let d2 = sub_mod(o2, o1, v);
                    let d1_old = sub_mod(old_val, o1, v);
                    let d1_new = sub_mod(new_val, o1, v);
                    (d1_old * v + d2, d1_new * v + d2)
                }
                _ => {
                    let d1 = sub_mod(o1, o2, v); // careful: pos==2 has c_o1=c0, c_o2=c1!
                    // Wait: in OrbitColTriple for pos==2: c_o1=c0, c_o2=c1!
                    // So d1 = (c1 - c0) = sub_mod(o2, o1, v)
                    let _ = d1;
                    let d1_c = sub_mod(o2, o1, v);
                    let d2_old = sub_mod(old_val, o1, v);
                    let d2_new = sub_mod(new_val, o1, v);
                    (d1_c * v + d2_old, d1_c * v + d2_new)
                }
            };
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
                delta_w += (lose * w_old - gain * w_new) as i64;
            }
        }
        if !use_weights {
            delta_w = delta_unc as i64;
        }
        (delta_unc, delta_w)
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
                    (d1_old * v + d2_old, d1_new * v + d2_new)
                }
                1 => {
                    let d2 = sub_mod(o2, o1, v);
                    let d1_old = sub_mod(old_u32, o1, v);
                    let d1_new = sub_mod(new_u32, o1, v);
                    (d1_old * v + d2, d1_new * v + d2)
                }
                _ => {
                    let d1 = sub_mod(o2, o1, v);
                    let d2_old = sub_mod(old_u32, o1, v);
                    let d2_new = sub_mod(new_u32, o1, v);
                    (d1 * v + d2_old, d1 * v + d2_new)
                }
            };
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

    /// Expands starters (+ optional v constant rows + optional extra random/greedy rows to reach target_n)
    /// into a full CaState.
    pub fn expand_to_ca(&self, target_n: usize, rng: &mut Rng) -> CaState {
        let const_n = if self.has_const_rows { self.v } else { 0 };
        let cyclic_n = self.num_starters * self.v + const_n;
        assert!(
            target_n >= cyclic_n,
            "target_n={} < cyclic_n={}",
            target_n,
            cyclic_n
        );
        let mut mat = Vec::with_capacity(target_n * self.k);
        if self.has_const_rows {
            for d in 0..self.v {
                for _ in 0..self.k {
                    mat.push(d as u8);
                }
            }
        }
        for s in 0..self.num_starters {
            let row = &self.starters[s * self.k..(s + 1) * self.k];
            for d in 0..self.v {
                for &val in row {
                    mat.push(((val as usize + d) % self.v) as u8);
                }
            }
        }
        for _ in cyclic_n..target_n {
            for _ in 0..self.k {
                mat.push(rng.gen_usize(self.v) as u8);
            }
        }
        CaState::from_matrix(mat, target_n, self.k, self.v)
    }

    pub fn verify_incremental(&self) -> Result<(), String> {
        let mut fresh = vec![0u16; self.num_triples * self.v2];
        let v = self.v as u32;
        if self.has_const_rows {
            for t_idx in 0..self.num_triples {
                fresh[t_idx * self.v2] = 1;
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
                let idx = t_idx * self.v2 + (d1 * v + d2) as usize;
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
}

pub struct OrbitSearchConfig {
    pub tenure_base: u32,
    pub tenure_jitter: u32,
    pub noise_prob: f64,
    pub use_weights: bool,
    pub reheat_steps: u64,
    pub restart_steps: u64,
}

pub struct OrbitSearchResult {
    pub best_uncovered_orbits: usize,
    pub best_starters: Vec<u8>,
    pub moves: u64,
    pub restarts: u64,
}

/// Focused WalkSAT + Tabu + Adaptive-Thermostat Metropolis (SA) Hybrid in Z_v-orbit quotient space.
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
    let v2 = state.v2;
    let num_s = state.num_starters;

    let mut tabu = vec![0u32; num_s * k * v];
    let mut best_unc = state.uncovered_orbits();
    let mut best_starters = state.starters.clone();
    let mut best_in_restart = best_unc;

    let mut iters: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut no_improve_reheat: u64 = 0;
    let mut no_improve_restart: u64 = 0;
    let mut restarts: u64 = 0;
    let mut max_weight: u32 = 1;

    let mut temp: f64 = 0.85;
    let temp_min: f64 = 0.20;
    let temp_max: f64 = 2.60;
    let mut window_accepts: u32 = 0;
    let mut window_uphill: u32 = 0;
    let mut consec_rejects: u32 = 0;

    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(64);

    while state.uncovered_orbits() > 0 {
        if let Some(lim) = max_moves {
            if iters >= lim {
                break;
            }
        }
        if (iters & 4095) == 0 {
            if stop.load(Ordering::Relaxed) || Instant::now() >= deadline {
                break;
            }
        }
        if step_u32 > 4_000_000_000 {
            tabu.fill(0);
            step_u32 = 1;
        }

        iters += 1;

        // 12% fast random starter-cell Metropolis move
        if rng.chance(0.12) {
            let s = rng.gen_usize(num_s);
            let c = rng.gen_usize(k);
            let old_v = state.starters[s * k + c];
            let nv = ((old_v as usize + 1 + rng.gen_usize(v - 1)) % v) as u8;
            let (du, _dw) = state.eval_move(s, c, nv, false);
            let cur_unc = state.uncovered_orbits() as i32;
            let asp = (cur_unc + du) < (best_in_restart as i32);
            let is_tabu = !asp && tabu[(s * k + c) * v + nv as usize] > step_u32;
            if !is_tabu {
                let accept = if du <= 0 {
                    true
                } else {
                    window_uphill += 1;
                    rng.gen_f64() < (-(du as f64) / temp).exp()
                };
                if accept {
                    if du > 0 {
                        window_accepts += 1;
                    }
                    consec_rejects = 0;
                    let ov = state.apply_move(s, c, nv);
                    let tenure =
                        cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
                    tabu[(s * k + c) * v + ov as usize] = step_u32 + tenure;
                    step_u32 += 1;
                    let new_unc = state.uncovered_orbits();
                    if new_unc < best_in_restart {
                        best_in_restart = new_unc;
                        no_improve_reheat = 0;
                        no_improve_restart = 0;
                        temp = (temp * 0.96).max(temp_min);
                        if new_unc < best_unc {
                            best_unc = new_unc;
                            best_starters.copy_from_slice(&state.starters);
                            if new_unc == 0 {
                                break;
                            }
                        }
                    }
                }
            }
            continue;
        }

        // Focused step: pick 1 random uncovered orbit
        let ulen = state.uncovered_list.len();
        let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        let t_idx = u_idx / v2;
        let orb = (u_idx % v2) as u32;
        let d1 = orb / v_u32;
        let d2 = orb % v_u32;
        let d21 = sub_mod(d2, d1, v_u32);
        let [c0, c1, c2] = state.triple_cols[t_idx];
        let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);

        cands.clear();
        for s in 0..num_s {
            let off = s * k;
            let a0 = unsafe { *state.starters.get_unchecked(off + c0) as u32 };
            let a1 = unsafe { *state.starters.get_unchecked(off + c1) as u32 };
            let a2 = unsafe { *state.starters.get_unchecked(off + c2) as u32 };
            if sub_mod(a2, a1, v_u32) == d21 {
                let t0 = sub_mod(a1, d1, v_u32) as u8;
                cands.push((s, c0, t0));
            }
            if sub_mod(a2, a0, v_u32) == d2 {
                let t1 = add_mod(a0, d1, v_u32) as u8;
                cands.push((s, c1, t1));
            }
            if sub_mod(a1, a0, v_u32) == d1 {
                let t2 = add_mod(a0, d2, v_u32) as u8;
                cands.push((s, c2, t2));
            }
        }

        if cands.is_empty() {
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

        let cur_unc = state.uncovered_orbits() as i32;
        let mut best_nt_score = (i64::MAX, i32::MAX);
        let mut best_nt_move = cands[0];
        let mut nt_ties = 0u64;

        let mut best_all_score = (i64::MAX, i32::MAX);
        let mut best_all_move = cands[0];
        let mut all_ties = 0u64;

        for &(s, c, nv) in &cands {
            let (du, dw) = state.eval_move(s, c, nv, cfg.use_weights);
            let score = (dw, du);
            let asp = (cur_unc + du) < (best_in_restart as i32);
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

        let (chosen, chosen_du, chosen_dw) = if nt_ties > 0 {
            (best_nt_move, best_nt_score.1, best_nt_score.0)
        } else {
            (best_all_move, best_all_score.1, best_all_score.0)
        };

        let accept = if chosen_du <= 0 {
            true
        } else {
            window_uphill += 1;
            let eff_temp = if cfg.use_weights && chosen_dw <= 0 {
                (temp * 1.35).min(temp_max)
            } else {
                temp
            };
            rng.gen_f64() < (-(chosen_du as f64) / eff_temp).exp()
                || rng.chance(cfg.noise_prob * 0.25)
        };

        if accept {
            if chosen_du > 0 {
                window_accepts += 1;
            }
            consec_rejects = 0;
            let (s, c, nv) = chosen;
            let old_v = state.apply_move(s, c, nv);
            let tenure = cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
            tabu[(s * k + c) * v + old_v as usize] = step_u32 + tenure;
            step_u32 += 1;

            let new_unc = state.uncovered_orbits();
            if new_unc < best_in_restart {
                best_in_restart = new_unc;
                no_improve_reheat = 0;
                no_improve_restart = 0;
                temp = (temp * 0.96).max(temp_min);
                if new_unc < best_unc {
                    best_unc = new_unc;
                    best_starters.copy_from_slice(&state.starters);
                    if new_unc == 0 {
                        break;
                    }
                }
            } else {
                no_improve_reheat += 1;
                no_improve_restart += 1;
            }
        } else {
            consec_rejects += 1;
            no_improve_reheat += 1;
            no_improve_restart += 1;
            if cfg.use_weights && consec_rejects % 4 == 0 {
                let w = &mut state.weights[u_idx];
                *w += 1;
                if *w > max_weight {
                    max_weight = *w;
                }
                if max_weight > 128 {
                    for wv in &mut state.weights {
                        *wv = (*wv >> 1).max(1);
                    }
                    max_weight >>= 1;
                }
            }
            if consec_rejects >= 32 {
                temp = (temp * 1.06).min(temp_max);
                consec_rejects = 0;
            }
        }

        if window_uphill >= 256 {
            let rate = window_accepts as f64 / window_uphill as f64;
            let cur_u = state.uncovered_orbits();
            if cur_u > best_in_restart + 15 || rate > 0.25 {
                temp = (temp * 0.92).max(temp_min);
            } else if rate < 0.08 {
                temp = (temp * 1.08).min(temp_max);
            }
            window_accepts = 0;
            window_uphill = 0;
        }

        if cfg.restart_steps > 0 && no_improve_restart >= cfg.restart_steps {
            restarts += 1;
            for val in &mut state.starters {
                *val = rng.gen_usize(v) as u8;
            }
            state.recompute_counts();
            state.weights.fill(1);
            tabu.fill(0);
            step_u32 = 1;
            max_weight = 1;
            temp = 0.85;
            best_in_restart = state.uncovered_orbits();
            no_improve_reheat = 0;
            no_improve_restart = 0;
        } else if cfg.reheat_steps > 0 && no_improve_reheat >= cfg.reheat_steps {
            temp = (temp * 1.5).clamp(1.2, temp_max);
            no_improve_reheat = 0;
        }
    }

    state.starters.copy_from_slice(&best_starters);
    state.recompute_counts();

    OrbitSearchResult {
        best_uncovered_orbits: best_unc,
        best_starters,
        moves: iters,
        restarts,
    }
}

pub fn orbit_sanity_test(k: usize, v: usize, num_starters: usize, has_const: bool) -> Result<(f64, usize), String> {
    let mut rng = Rng::from_seed(0xC0FFEE_1234);
    let mut st = OrbitState::new_random(num_starters, k, v, has_const, &mut rng);
    let cfg = OrbitSearchConfig {
        tenure_base: 7,
        tenure_jitter: 5,
        noise_prob: 0.01,
        use_weights: true,
        reheat_steps: 50_000,
        restart_steps: 0,
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

    // Also run 10,000 raw incremental moves without recompute_counts to verify eval_move & apply_move
    let mut st2 = OrbitState::from_starters(st.starters.clone(), num_starters, k, v, has_const);
    let mut rng2 = Rng::from_seed(0xABCDEF_5678);
    for _ in 0..10_000 {
        let s = rng2.gen_usize(num_starters);
        let c = rng2.gen_usize(k);
        let nv = rng2.gen_usize(v) as u8;
        let before = st2.uncovered_orbits() as i32;
        let (du, _) = st2.eval_move(s, c, nv, true);
        st2.apply_move(s, c, nv);
        let after = st2.uncovered_orbits() as i32;
        if after - before != du {
            return Err(format!(
                "orbit eval_move delta mismatch: predicted {}, actual {}",
                du,
                after - before
            ));
        }
    }
    st2.verify_incremental()?;

    // Also verify expanded CaState has uncovered == v * orbit.uncovered_orbits()
    let target_n = num_starters * v + if has_const { v } else { 0 };
    let expanded = st2.expand_to_ca(target_n, &mut rng);
    expanded.verify_incremental()?;
    if expanded.uncovered() != v * st2.uncovered_orbits() {
        return Err(format!(
            "expansion mismatch: expanded.uncovered={} != v*orbit={}",
            expanded.uncovered(),
            v * st2.uncovered_orbits()
        ));
    }
    Ok((res.moves as f64 / dt, res.best_uncovered_orbits))
}
