use crate::orbit::SearchAlgo;
use crate::rng::Rng;
use crate::state::CaState;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

#[derive(Clone, Debug)]
pub struct SearchConfig {
    pub algo: SearchAlgo,
    pub tenure_min: u32,
    pub tenure_max: u32,
    pub noise_prob: f64,
    pub use_weights: bool,
    pub t_start: f64,
    pub t_end: f64,
    pub full_scan_thresh: usize,
    pub lock_rows: usize,
    pub lock_cols: usize,
    pub log_interval_secs: f64,
    pub label: String,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            algo: SearchAlgo::TabuCw,
            tenure_min: 7,
            tenure_max: 10,
            noise_prob: 0.002,
            use_weights: true,
            t_start: 0.55,
            t_end: 0.16,
            full_scan_thresh: 80,
            lock_rows: 0,
            lock_cols: 0,
            log_interval_secs: 30.0,
            label: "ca".to_string(),
        }
    }
}

pub struct SearchResult {
    pub best_uncovered: usize,
    pub best_mat: Vec<u8>,
    pub moves: u64,
    #[allow(dead_code)]
    pub accepted_moves: u64,
    pub reheats: u64,
    pub best_at_60s: usize,
    pub best_at_120s: usize,
    pub last_improve_sec: f64,
}

#[inline(always)]
fn is_editable(r: usize, c: usize, lock_rows: usize, lock_cols: usize) -> bool {
    r >= lock_rows || c >= lock_cols
}

#[inline]
fn gather_ca_candidates_dedup(
    state: &CaState,
    u_idx: usize,
    lock_r: usize,
    lock_c: usize,
    seen: &mut [u32],
    stamp: u32,
    cands: &mut Vec<(usize, usize, u8)>,
    fallback: &mut Vec<(usize, usize, u8)>,
    collect_fallback: bool,
) {
    let n = state.n;
    let k = state.k;
    let v = state.v;
    let v2 = state.v2;
    let v3 = state.v3;
    let t_idx = u_idx / v3;
    let tup = u_idx % v3;
    let v0 = (tup / v2) as u8;
    let v1 = ((tup / v) % v) as u8;
    let v2_val = (tup % v) as u8;
    let [c0, c1, c2] = state.triple_cols[t_idx];
    let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);

    let r_start = if lock_c == k { lock_r } else { 0 };
    let mat = &state.mat;

    for r in r_start..n {
        let off = r * k;
        let a0 = unsafe { *mat.get_unchecked(off + c0) };
        let a1 = unsafe { *mat.get_unchecked(off + c1) };
        let a2 = unsafe { *mat.get_unchecked(off + c2) };
        let m0 = a0 == v0;
        let m1 = a1 == v1;
        let m2 = a2 == v2_val;

        if m1 && m2 {
            if is_editable(r, c0, lock_r, lock_c) {
                let key = (off + c0) * v + v0 as usize;
                if unsafe { *seen.get_unchecked(key) } != stamp {
                    unsafe { *seen.get_unchecked_mut(key) = stamp };
                    cands.push((r, c0, v0));
                }
            }
        } else if m0 && m2 {
            if is_editable(r, c1, lock_r, lock_c) {
                let key = (off + c1) * v + v1 as usize;
                if unsafe { *seen.get_unchecked(key) } != stamp {
                    unsafe { *seen.get_unchecked_mut(key) = stamp };
                    cands.push((r, c1, v1));
                }
            }
        } else if m0 && m1 {
            if is_editable(r, c2, lock_r, lock_c) {
                let key = (off + c2) * v + v2_val as usize;
                if unsafe { *seen.get_unchecked(key) } != stamp {
                    unsafe { *seen.get_unchecked_mut(key) = stamp };
                    cands.push((r, c2, v2_val));
                }
            }
        } else if collect_fallback && cands.is_empty() && fallback.len() < 48 {
            if m0 {
                if is_editable(r, c1, lock_r, lock_c) {
                    fallback.push((r, c1, v1));
                }
                if is_editable(r, c2, lock_r, lock_c) {
                    fallback.push((r, c2, v2_val));
                }
            } else if m1 {
                if is_editable(r, c0, lock_r, lock_c) {
                    fallback.push((r, c0, v0));
                }
                if is_editable(r, c2, lock_r, lock_c) {
                    fallback.push((r, c2, v2_val));
                }
            } else if m2 {
                if is_editable(r, c0, lock_r, lock_c) {
                    fallback.push((r, c0, v0));
                }
                if is_editable(r, c1, lock_r, lock_c) {
                    fallback.push((r, c1, v1));
                }
            }
        }
    }
}

#[inline]
fn pick_ca_uncovered_50_50(state: &CaState, rng: &mut Rng) -> usize {
    let ulen = state.uncovered_list.len();
    if rng.chance(0.5) {
        state.uncovered_list[rng.gen_usize(ulen)] as usize
    } else if ulen <= 256 {
        let mut best_w = 0u32;
        let mut best_u = state.uncovered_list[0] as usize;
        let mut ties = 0u64;
        for &ui in &state.uncovered_list {
            let w = unsafe { *state.weights.get_unchecked(ui as usize) };
            if w > best_w {
                best_w = w;
                best_u = ui as usize;
                ties = 1;
            } else if w == best_w {
                ties += 1;
                if rng.gen_usize(ties as usize) == 0 {
                    best_u = ui as usize;
                }
            }
        }
        best_u
    } else {
        let mut best_u = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        let mut best_w = state.weights[best_u];
        for _ in 0..7 {
            let ui = state.uncovered_list[rng.gen_usize(ulen)] as usize;
            let w = state.weights[ui];
            if w > best_w {
                best_w = w;
                best_u = ui;
            }
        }
        best_u
    }
}

/// Non-freezing Focused Tabu + Dynamic Clause Weighting (PAWS/SWT) for CaState.
fn search_ca_tabu_cw<F>(
    state: &mut CaState,
    rng: &mut Rng,
    cfg: &SearchConfig,
    deadline: Instant,
    stop: &AtomicBool,
    max_moves: Option<u64>,
    mut on_improve: F,
) -> SearchResult
where
    F: FnMut(usize, &[u8], u64),
{
    let n = state.n;
    let k = state.k;
    let v = state.v;
    let v2 = state.v2;
    let v3 = state.v3;
    let lock_r = cfg.lock_rows;
    let lock_c = cfg.lock_cols;
    let total_cells_v = n * k * v;

    let t0 = Instant::now();
    let mut tabu = vec![0u32; total_cells_v];
    let mut seen = vec![0u32; total_cells_v];
    let mut stamp: u32 = 1;

    // Fractional SWT weights in integer fixed-point: base = 16 (1.0), max = 26 (1.625x)
    const BASE_W: u32 = 16;
    const MAX_W: u32 = 26;
    state.weights.fill(BASE_W);

    let mut best_unc = state.uncovered();
    let mut best_mat = state.mat.clone();
    let mut best_at_60s = best_unc;
    let mut best_at_120s = best_unc;
    let mut recorded_60 = false;
    let mut recorded_120 = false;
    let mut last_improve_sec = 0.0f64;

    let mut moves: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut plateau_steps: u32 = 0;
    let mut max_weight: u32 = BASE_W;
    let mut smoothings: u64 = 0;
    let mut last_log = t0;

    let tenure_span = (cfg.tenure_max.saturating_sub(cfg.tenure_min) + 1) as usize;
    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(2048);
    let mut fallback: Vec<(usize, usize, u8)> = Vec::with_capacity(64);

    while state.uncovered() > 0 {
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
                    "    [{}] t={:5.1}s | cur_unc={:4} | best_unc={:4} (last@{:5.1}s) | max_w={:2} sm={} | {:.0} mv/s",
                    cfg.label,
                    el,
                    state.uncovered(),
                    best_unc,
                    last_improve_sec,
                    max_weight,
                    smoothings,
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
        fallback.clear();

        let mut picked_u = 0usize;
        if ulen <= cfg.full_scan_thresh {
            for si in 0..ulen {
                let u_idx = state.uncovered_list[si] as usize;
                if si == 0 {
                    picked_u = u_idx;
                }
                gather_ca_candidates_dedup(
                    state,
                    u_idx,
                    lock_r,
                    lock_c,
                    &mut seen,
                    stamp,
                    &mut cands,
                    &mut fallback,
                    si == 0,
                );
            }
        } else {
            // Sample 8 uncovered triples (50/50 max-weight vs uniform) to descend reliably into full_scan_thresh
            for si in 0..8 {
                let u_idx = pick_ca_uncovered_50_50(state, rng);
                if si == 0 {
                    picked_u = u_idx;
                }
                gather_ca_candidates_dedup(
                    state,
                    u_idx,
                    lock_r,
                    lock_c,
                    &mut seen,
                    stamp,
                    &mut cands,
                    &mut fallback,
                    si == 0,
                );
            }
        }

        let active: &[(usize, usize, u8)] = if !cands.is_empty() {
            &cands
        } else if !fallback.is_empty() {
            &fallback
        } else {
            let t_idx = picked_u / v3;
            let tup = picked_u % v3;
            let v0 = (tup / v2) as u8;
            let v1 = ((tup / v) % v) as u8;
            let v2_val = (tup % v) as u8;
            let [c0, c1, c2] = state.triple_cols[t_idx];
            let cols = [(c0 as usize, v0), (c1 as usize, v1), (c2 as usize, v2_val)];
            let r_lo = if lock_c == k { lock_r } else { 0 };
            for _ in 0..16 {
                let r = r_lo + rng.gen_usize(n - r_lo);
                let (c, tv) = cols[rng.gen_usize(3)];
                if is_editable(r, c, lock_r, lock_c) && state.mat[r * k + c] != tv {
                    fallback.push((r, c, tv));
                }
            }
            if fallback.is_empty() {
                let r = r_lo + rng.gen_usize(n - r_lo);
                let c = if r < lock_r && lock_c < k {
                    lock_c + rng.gen_usize(k - lock_c)
                } else {
                    rng.gen_usize(k)
                };
                let nv = ((state.mat[r * k + c] as usize + 1 + rng.gen_usize(v - 1)) % v) as u8;
                fallback.push((r, c, nv));
            }
            &fallback
        };

        let cur_unc = ulen as i32;
        let (chosen_move, min_nt_raw_du) = if rng.chance(cfg.noise_prob) {
            let mv = active[rng.gen_usize(active.len())];
            (mv, -1)
        } else {
            let mut best_asp_score = (i32::MAX, i64::MAX);
            let mut best_asp_move = active[0];
            let mut asp_ties = 0u64;

            let mut best_nt_score = (i64::MAX, i32::MAX);
            let mut best_nt_move = active[0];
            let mut nt_ties = 0u64;
            let mut min_nt_du = i32::MAX;

            let mut best_all_score = (i64::MAX, i32::MAX);
            let mut best_all_move = active[0];
            let mut all_ties = 0u64;

            for &(r, c, nv) in active {
                let (du, dw) = state.eval_move(r, c, nv, true);
                let asp = (cur_unc + du) < (best_unc as i32);
                if asp {
                    let ascore = (du, dw);
                    if ascore < best_asp_score {
                        best_asp_score = ascore;
                        best_asp_move = (r, c, nv);
                        asp_ties = 1;
                    } else if ascore == best_asp_score {
                        asp_ties += 1;
                        if rng.gen_usize(asp_ties as usize) == 0 {
                            best_asp_move = (r, c, nv);
                        }
                    }
                }

                let score = (dw, du);
                if score < best_all_score {
                    best_all_score = score;
                    best_all_move = (r, c, nv);
                    all_ties = 1;
                } else if score == best_all_score {
                    all_ties += 1;
                    if rng.gen_usize(all_ties as usize) == 0 {
                        best_all_move = (r, c, nv);
                    }
                }

                let is_tabu = tabu[(r * k + c) * v + nv as usize] > step_u32;
                if !is_tabu {
                    if du < min_nt_du {
                        min_nt_du = du;
                    }
                    if score < best_nt_score {
                        best_nt_score = score;
                        best_nt_move = (r, c, nv);
                        nt_ties = 1;
                    } else if score == best_nt_score {
                        nt_ties += 1;
                        if rng.gen_usize(nt_ties as usize) == 0 {
                            best_nt_move = (r, c, nv);
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

        // PAWS / SWT Clause Weighting ONLY on true plateau / local minimum (no raw-improving non-tabu move)
        if min_nt_raw_du >= 0 {
            plateau_steps += 1;
            for &ui in &state.uncovered_list {
                let w = unsafe { state.weights.get_unchecked_mut(ui as usize) };
                *w += 1;
                if *w > max_weight {
                    max_weight = *w;
                }
            }
            if plateau_steps >= 500 || max_weight > MAX_W {
                let mut new_max = BASE_W;
                for w in &mut state.weights {
                    let excess = w.saturating_sub(BASE_W);
                    let nw = BASE_W + ((excess * 3) >> 2);
                    *w = nw;
                    if nw > new_max {
                        new_max = nw;
                    }
                }
                max_weight = new_max;
                plateau_steps = 0;
                smoothings += 1;
            }
        }

        let (r, c, nv) = chosen_move;
        let old_v = state.apply_move(r, c, nv);
        let tenure = cfg.tenure_min + rng.gen_usize(tenure_span) as u32;
        tabu[(r * k + c) * v + old_v as usize] = step_u32 + tenure;
        moves += 1;
        step_u32 += 1;

        let new_unc = state.uncovered();
        if new_unc < best_unc {
            best_unc = new_unc;
            best_mat.copy_from_slice(&state.mat);
            last_improve_sec = t0.elapsed().as_secs_f64();
            on_improve(best_unc, &best_mat, moves);
            if new_unc == 0 {
                break;
            }
        }
    }

    if !recorded_60 {
        best_at_60s = best_unc;
    }
    if !recorded_120 {
        best_at_120s = best_unc;
    }

    state.mat.copy_from_slice(&best_mat);
    state.recompute_counts();

    SearchResult {
        best_uncovered: best_unc,
        best_mat,
        moves,
        accepted_moves: moves,
        reheats: smoothings,
        best_at_60s,
        best_at_120s,
        last_improve_sec,
    }
}

/// Sweet-Spot Geometric SA (T_start -> T_end) transitioning directly into Full-Scan Tabu-CW when unc <= full_scan_thresh.
fn search_ca_sa<F>(
    state: &mut CaState,
    rng: &mut Rng,
    cfg: &SearchConfig,
    deadline: Instant,
    stop: &AtomicBool,
    max_moves: Option<u64>,
    mut on_improve: F,
) -> SearchResult
where
    F: FnMut(usize, &[u8], u64),
{
    let n = state.n;
    let k = state.k;
    let v = state.v;
    let v2 = state.v2;
    let v3 = state.v3;
    let lock_r = cfg.lock_rows;
    let lock_c = cfg.lock_cols;
    let total_cells_v = n * k * v;

    let t_start_time = Instant::now();
    let total_secs = deadline
        .saturating_duration_since(t_start_time)
        .as_secs_f64()
        .max(1e-3);

    let mut tabu = vec![0u32; total_cells_v];
    let mut seen = vec![0u32; total_cells_v];
    let mut stamp: u32 = 1;

    let mut best_unc = state.uncovered();
    let mut best_mat = state.mat.clone();
    let mut best_at_60s = best_unc;
    let mut best_at_120s = best_unc;
    let mut recorded_60 = false;
    let mut recorded_120 = false;
    let mut last_improve_sec = 0.0f64;

    let mut iters: u64 = 0;
    let mut accepted: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut last_log_time = t_start_time;
    let mut plateau_steps: u32 = 0;
    const BASE_W: u32 = 16;
    const MAX_W: u32 = 26;
    state.weights.fill(BASE_W);
    let mut max_weight: u32 = BASE_W;
    let mut smoothings: u64 = 0;
    let mut temp = cfg.t_start;

    let tenure_span = (cfg.tenure_max.saturating_sub(cfg.tenure_min) + 1) as usize;
    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(2048);
    let mut fallback: Vec<(usize, usize, u8)> = Vec::with_capacity(64);

    while state.uncovered() > 0 {
        if let Some(lim) = max_moves {
            if iters >= lim {
                break;
            }
        }
        if (iters & 1023) == 0 {
            let now = Instant::now();
            let el = now.saturating_duration_since(t_start_time).as_secs_f64();
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
            let prog = (el / total_secs).clamp(0.0, 1.0);
            temp = cfg.t_start * (cfg.t_end / cfg.t_start).powf(prog);

            if cfg.log_interval_secs > 0.0
                && now.saturating_duration_since(last_log_time).as_secs_f64()
                    >= cfg.log_interval_secs
            {
                println!(
                    "    [{}] t={:5.1}s | T={:.4} | cur_unc={:4} | best_unc={:4} (last@{:5.1}s) | max_w={:2} | {:.0} it/s",
                    cfg.label,
                    el,
                    temp,
                    state.uncovered(),
                    best_unc,
                    last_improve_sec,
                    max_weight,
                    iters as f64 / el.max(1e-9)
                );
                last_log_time = now;
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

        iters += 1;
        let ulen = state.uncovered_list.len();

        // Transition into exact deduplicated Full-Scan Tabu-CW whenever unc <= full_scan_thresh!
        if ulen <= cfg.full_scan_thresh {
            cands.clear();
            fallback.clear();
            for si in 0..ulen {
                let u_idx = state.uncovered_list[si] as usize;
                gather_ca_candidates_dedup(
                    state,
                    u_idx,
                    lock_r,
                    lock_c,
                    &mut seen,
                    stamp,
                    &mut cands,
                    &mut fallback,
                    si == 0,
                );
            }
            let active: &[(usize, usize, u8)] = if !cands.is_empty() {
                &cands
            } else {
                &fallback
            };
            if !active.is_empty() {
                let cur_unc = ulen as i32;
                let mut best_asp_score = (i32::MAX, i64::MAX);
                let mut best_asp_move = active[0];
                let mut asp_ties = 0u64;
                let mut best_nt_score = (i64::MAX, i32::MAX);
                let mut best_nt_move = active[0];
                let mut nt_ties = 0u64;
                let mut best_all_score = (i64::MAX, i32::MAX);
                let mut best_all_move = active[0];
                let mut all_ties = 0u64;

                for &(r, c, nv) in active {
                    let (du, dw) = state.eval_move(r, c, nv, true);
                    let asp = (cur_unc + du) < (best_unc as i32);
                    if asp {
                        let ascore = (du, dw);
                        if ascore < best_asp_score {
                            best_asp_score = ascore;
                            best_asp_move = (r, c, nv);
                            asp_ties = 1;
                        } else if ascore == best_asp_score {
                            asp_ties += 1;
                            if rng.gen_usize(asp_ties as usize) == 0 {
                                best_asp_move = (r, c, nv);
                            }
                        }
                    }
                    let score = (dw, du);
                    if score < best_all_score {
                        best_all_score = score;
                        best_all_move = (r, c, nv);
                        all_ties = 1;
                    } else if score == best_all_score {
                        all_ties += 1;
                        if rng.gen_usize(all_ties as usize) == 0 {
                            best_all_move = (r, c, nv);
                        }
                    }
                    let is_tabu = tabu[(r * k + c) * v + nv as usize] > step_u32;
                    if !is_tabu {
                        if score < best_nt_score {
                            best_nt_score = score;
                            best_nt_move = (r, c, nv);
                            nt_ties = 1;
                        } else if score == best_nt_score {
                            nt_ties += 1;
                            if rng.gen_usize(nt_ties as usize) == 0 {
                                best_nt_move = (r, c, nv);
                            }
                        }
                    }
                }
                let (chosen, chosen_du) = if asp_ties > 0 {
                    (best_asp_move, best_asp_score.0)
                } else if nt_ties > 0 {
                    (best_nt_move, best_nt_score.1)
                } else {
                    (best_all_move, best_all_score.1)
                };

                if chosen_du >= 0 {
                    plateau_steps += 1;
                    for &ui in &state.uncovered_list {
                        let w = unsafe { state.weights.get_unchecked_mut(ui as usize) };
                        *w += 1;
                        if *w > max_weight {
                            max_weight = *w;
                        }
                    }
                    if plateau_steps >= 500 || max_weight > MAX_W {
                        let mut nm = BASE_W;
                        for w in &mut state.weights {
                            let excess = w.saturating_sub(BASE_W);
                            let nw = BASE_W + ((excess * 3) >> 2);
                            *w = nw;
                            if nw > nm {
                                nm = nw;
                            }
                        }
                        max_weight = nm;
                        plateau_steps = 0;
                        smoothings += 1;
                    }
                }

                let (r, c, nv) = chosen;
                let old_v = state.apply_move(r, c, nv);
                let tenure = cfg.tenure_min + rng.gen_usize(tenure_span) as u32;
                tabu[(r * k + c) * v + old_v as usize] = step_u32 + tenure;
                accepted += 1;
                step_u32 += 1;

                let new_unc = state.uncovered();
                if new_unc < best_unc {
                    best_unc = new_unc;
                    best_mat.copy_from_slice(&state.mat);
                    last_improve_sec = t_start_time.elapsed().as_secs_f64();
                    on_improve(best_unc, &best_mat, iters);
                    if new_unc == 0 {
                        break;
                    }
                }
                continue;
            }
        }

        // Sweet-Spot SA mode (unc > full_scan_thresh)
        if rng.chance(0.15) {
            let r = if lock_r < n && lock_c == k {
                lock_r + rng.gen_usize(n - lock_r)
            } else {
                rng.gen_usize(n)
            };
            let c = if r < lock_r && lock_c < k {
                lock_c + rng.gen_usize(k - lock_c)
            } else {
                rng.gen_usize(k)
            };
            if is_editable(r, c, lock_r, lock_c) {
                let old_v = state.mat[r * k + c];
                let nv = ((old_v as usize + 1 + rng.gen_usize(v - 1)) % v) as u8;
                let (du, _) = state.eval_move(r, c, nv, false);
                if du <= 0 || rng.gen_f64() < (-(du as f64) / temp).exp() {
                    let ov = state.apply_move(r, c, nv);
                    let tenure = cfg.tenure_min + rng.gen_usize(tenure_span) as u32;
                    tabu[(r * k + c) * v + ov as usize] = step_u32 + tenure;
                    accepted += 1;
                    step_u32 += 1;
                    let new_unc = state.uncovered();
                    if new_unc < best_unc {
                        best_unc = new_unc;
                        best_mat.copy_from_slice(&state.mat);
                        last_improve_sec = t_start_time.elapsed().as_secs_f64();
                        on_improve(best_unc, &best_mat, iters);
                        if new_unc == 0 {
                            break;
                        }
                    }
                }
            }
            continue;
        }

        let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        cands.clear();
        fallback.clear();
        gather_ca_candidates_dedup(
            state,
            u_idx,
            lock_r,
            lock_c,
            &mut seen,
            stamp,
            &mut cands,
            &mut fallback,
            true,
        );

        let active_cands: &[(usize, usize, u8)] = if !cands.is_empty() {
            &cands
        } else if !fallback.is_empty() {
            &fallback
        } else {
            let t_idx = u_idx / v3;
            let tup = u_idx % v3;
            let v0 = (tup / v2) as u8;
            let v1 = ((tup / v) % v) as u8;
            let v2_val = (tup % v) as u8;
            let [c0, c1, c2] = state.triple_cols[t_idx];
            let cols = [(c0 as usize, v0), (c1 as usize, v1), (c2 as usize, v2_val)];
            let r_lo = if lock_c == k { lock_r } else { 0 };
            for _ in 0..12 {
                let r = r_lo + rng.gen_usize(n - r_lo);
                let (c, tv) = cols[rng.gen_usize(3)];
                if is_editable(r, c, lock_r, lock_c) && state.mat[r * k + c] != tv {
                    fallback.push((r, c, tv));
                }
            }
            if fallback.is_empty() {
                continue;
            }
            &fallback
        };

        let cur_unc = ulen as i32;
        let mut best_nt_du = i32::MAX;
        let mut best_nt_move = active_cands[0];
        let mut nt_ties = 0u64;
        let mut best_all_du = i32::MAX;
        let mut best_all_move = active_cands[0];
        let mut all_ties = 0u64;

        for &(r, c, nv) in active_cands {
            let (du, _) = state.eval_move(r, c, nv, false);
            let asp = (cur_unc + du) < (best_unc as i32);
            let is_tabu = !asp && tabu[(r * k + c) * v + nv as usize] > step_u32;
            if du < best_all_du {
                best_all_du = du;
                best_all_move = (r, c, nv);
                all_ties = 1;
            } else if du == best_all_du {
                all_ties += 1;
                if rng.gen_usize(all_ties as usize) == 0 {
                    best_all_move = (r, c, nv);
                }
            }
            if !is_tabu {
                if du < best_nt_du {
                    best_nt_du = du;
                    best_nt_move = (r, c, nv);
                    nt_ties = 1;
                } else if du == best_nt_du {
                    nt_ties += 1;
                    if rng.gen_usize(nt_ties as usize) == 0 {
                        best_nt_move = (r, c, nv);
                    }
                }
            }
        }
        let (chosen, chosen_du) = if nt_ties > 0 {
            (best_nt_move, best_nt_du)
        } else {
            (best_all_move, best_all_du)
        };
        if chosen_du <= 0 || rng.gen_f64() < (-(chosen_du as f64) / temp).exp() {
            let (r, c, nv) = chosen;
            let old_v = state.apply_move(r, c, nv);
            let tenure = cfg.tenure_min + rng.gen_usize(tenure_span) as u32;
            tabu[(r * k + c) * v + old_v as usize] = step_u32 + tenure;
            accepted += 1;
            step_u32 += 1;
            let new_unc = state.uncovered();
            if new_unc < best_unc {
                best_unc = new_unc;
                best_mat.copy_from_slice(&state.mat);
                last_improve_sec = t_start_time.elapsed().as_secs_f64();
                on_improve(best_unc, &best_mat, iters);
                if new_unc == 0 {
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
    state.mat.copy_from_slice(&best_mat);
    state.recompute_counts();

    SearchResult {
        best_uncovered: best_unc,
        best_mat,
        moves: iters,
        accepted_moves: accepted,
        reheats: smoothings,
        best_at_60s,
        best_at_120s,
        last_improve_sec,
    }
}

pub fn search_ca<F>(
    state: &mut CaState,
    rng: &mut Rng,
    cfg: &SearchConfig,
    deadline: Instant,
    stop: &AtomicBool,
    max_moves: Option<u64>,
    on_improve: F,
) -> SearchResult
where
    F: FnMut(usize, &[u8], u64),
{
    match cfg.algo {
        SearchAlgo::TabuCw => {
            search_ca_tabu_cw(state, rng, cfg, deadline, stop, max_moves, on_improve)
        }
        SearchAlgo::Sa | SearchAlgo::HybridSaCw => {
            search_ca_sa(state, rng, cfg, deadline, stop, max_moves, on_improve)
        }
    }
}

pub fn ca_sanity_test(
    mat: Vec<u8>,
    n: usize,
    k: usize,
    v: usize,
) -> Result<(f64, usize, usize), String> {
    let mut state = CaState::from_matrix(mat, n, k, v);
    state.verify_incremental()?;
    let start_unc = state.uncovered();
    let mut rng = Rng::from_seed(0xDEADBEEF_42);
    let cfg = SearchConfig {
        algo: SearchAlgo::TabuCw,
        tenure_min: 7,
        tenure_max: 10,
        noise_prob: 0.002,
        use_weights: true,
        t_start: 0.55,
        t_end: 0.16,
        full_scan_thresh: 80,
        lock_rows: 0,
        lock_cols: 0,
        log_interval_secs: 0.0,
        label: "sanity".to_string(),
    };
    let t0 = Instant::now();
    let stop = AtomicBool::new(false);
    let res = search_ca(
        &mut state,
        &mut rng,
        &cfg,
        t0 + Duration::from_secs(30),
        &stop,
        Some(10_000),
        |_, _, _| {},
    );
    let dt = t0.elapsed().as_secs_f64().max(1e-9);

    let mut state2 = CaState::from_matrix(res.best_mat.clone(), n, k, v);
    let mut rng2 = Rng::from_seed(0x12345678_9ABC);
    for _ in 0..10_000 {
        let r = rng2.gen_usize(n);
        let c = rng2.gen_usize(k);
        let nv = rng2.gen_usize(v) as u8;
        let before = state2.uncovered() as i32;
        let (du, _) = state2.eval_move(r, c, nv, true);
        state2.apply_move(r, c, nv);
        let after = state2.uncovered() as i32;
        if after - before != du {
            return Err(format!(
                "eval_move delta mismatch: predicted {}, actual {}",
                du,
                after - before
            ));
        }
    }
    state2.verify_incremental()?;
    Ok((res.moves as f64 / dt, start_unc, res.best_uncovered))
}
