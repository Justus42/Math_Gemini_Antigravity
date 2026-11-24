use crate::rng::Rng;
use crate::state::CaState;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

#[derive(Clone, Debug)]
pub struct SearchConfig {
    pub tenure_base: u32,
    pub tenure_jitter: u32,
    pub noise_prob: f64,
    pub use_weights: bool,
    pub t_start: f64,
    pub t_end: f64,
    pub endgame_threshold: usize,
    pub lock_rows: usize,
    pub lock_cols: usize,
    pub log_interval_secs: f64,
    pub label: String,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            tenure_base: 8,
            tenure_jitter: 7,
            noise_prob: 0.008,
            use_weights: true,
            t_start: 1.8,
            t_end: 0.05,
            endgame_threshold: 25,
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
}

#[inline(always)]
fn is_editable(r: usize, c: usize, lock_rows: usize, lock_cols: usize) -> bool {
    r >= lock_rows || c >= lock_cols
}

#[inline]
fn gather_ca_candidates_for_triple(
    state: &CaState,
    u_idx: usize,
    lock_r: usize,
    lock_c: usize,
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

    // If all cols of rows 0..lock_r are locked (lock_c == k), scan only lock_r..n!
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
                cands.push((r, c0, v0));
            }
        } else if m0 && m2 {
            if is_editable(r, c1, lock_r, lock_c) {
                cands.push((r, c1, v1));
            }
        } else if m0 && m1 {
            if is_editable(r, c2, lock_r, lock_c) {
                cands.push((r, c2, v2_val));
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

/// Time-based Geometric SA (T_start -> T_end over full budget, max 1 late reheat)
/// + Endgame Exact Full-Focused-Neighborhood Tabu (when uncovered <= 25, with clause weighting).
pub fn search_ca<F>(
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

    let t_start_time = Instant::now();
    let total_secs = deadline
        .saturating_duration_since(t_start_time)
        .as_secs_f64()
        .max(1e-3);
    let mut sched_t0 = cfg.t_start;
    let mut sched_start = t_start_time;
    let mut sched_dur = total_secs;

    let mut tabu = vec![0u32; n * k * v];
    let mut best_unc = state.uncovered();
    let mut best_mat = state.mat.clone();

    let mut iters: u64 = 0;
    let mut accepted: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut last_improve_time = t_start_time;
    let mut last_log_time = t_start_time;
    let mut reheats: u64 = 0;
    let mut max_weight: u32 = 1;
    let mut temp = sched_t0;

    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(640);
    let mut fallback: Vec<(usize, usize, u8)> = Vec::with_capacity(64);

    while state.uncovered() > 0 {
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

            // At most ONE gentle late reheat if completely stagnant for >= 28% of budget
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
                state.mat.copy_from_slice(&best_mat);
                state.recompute_counts();
                state.reset_weights();
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
                        "    [{}] late-reheat #1 at {:.1}s -> T={:.3}, best_unc={}",
                        cfg.label,
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
                    "    [{}] t={:5.1}s | T={:.4} | cur_unc={:4} | best_unc={:4} | {:.0} it/s",
                    cfg.label,
                    el,
                    temp,
                    state.uncovered(),
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
            fallback.clear();
            for si in 0..ulen {
                let u_idx = state.uncovered_list[si] as usize;
                gather_ca_candidates_for_triple(
                    state,
                    u_idx,
                    lock_r,
                    lock_c,
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
                let chosen = if rng.chance(cfg.noise_prob * 0.5) {
                    active[rng.gen_usize(active.len())]
                } else {
                    let mut best_nt_score = (i64::MAX, i32::MAX);
                    let mut best_nt_move = active[0];
                    let mut nt_ties = 0u64;

                    let mut best_all_score = (i64::MAX, i32::MAX);
                    let mut best_all_move = active[0];
                    let mut all_ties = 0u64;

                    for &(r, c, nv) in active {
                        let (du, dw) = state.eval_move(r, c, nv, cfg.use_weights);
                        let score = if du < 0 {
                            (i64::MIN / 2 + du as i64, du)
                        } else {
                            (dw, du)
                        };
                        let asp = (cur_unc + du) < (best_unc as i32);
                        let is_tabu = !asp && tabu[(r * k + c) * v + nv as usize] > step_u32;

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

                let (r, c, nv) = chosen;
                let old_v = state.apply_move(r, c, nv);
                let tenure =
                    cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
                tabu[(r * k + c) * v + old_v as usize] = step_u32 + tenure;
                accepted += 1;
                step_u32 += 1;

                let new_unc = state.uncovered();
                if new_unc < best_unc {
                    best_unc = new_unc;
                    best_mat.copy_from_slice(&state.mat);
                    last_improve_time = Instant::now();
                    on_improve(best_unc, &best_mat, iters);
                    if new_unc == 0 {
                        break;
                    }
                }
                continue;
            }
        }

        // SA MODE: 15% fast random editable cell Metropolis move
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
                let accept = if du <= 0 {
                    true
                } else {
                    rng.gen_f64() < (-(du as f64) / temp).exp()
                };
                if accept {
                    let ov = state.apply_move(r, c, nv);
                    let tenure =
                        cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
                    tabu[(r * k + c) * v + ov as usize] = step_u32 + tenure;
                    accepted += 1;
                    step_u32 += 1;

                    let new_unc = state.uncovered();
                    if new_unc < best_unc {
                        best_unc = new_unc;
                        best_mat.copy_from_slice(&state.mat);
                        last_improve_time = Instant::now();
                        on_improve(best_unc, &best_mat, iters);
                        if new_unc == 0 {
                            break;
                        }
                    }
                }
            }
            continue;
        }

        // SA Focused step: pick 1 uncovered interaction uniformly at random
        let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        cands.clear();
        fallback.clear();
        gather_ca_candidates_for_triple(state, u_idx, lock_r, lock_c, &mut cands, &mut fallback, true);

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

        let accept = if chosen_du <= 0 {
            true
        } else {
            rng.gen_f64() < (-(chosen_du as f64) / temp).exp()
        };

        if accept {
            let (r, c, nv) = chosen;
            let old_v = state.apply_move(r, c, nv);
            let tenure = cfg.tenure_base + rng.gen_usize(cfg.tenure_jitter as usize + 1) as u32;
            tabu[(r * k + c) * v + old_v as usize] = step_u32 + tenure;
            accepted += 1;
            step_u32 += 1;

            let new_unc = state.uncovered();
            if new_unc < best_unc {
                best_unc = new_unc;
                best_mat.copy_from_slice(&state.mat);
                last_improve_time = Instant::now();
                on_improve(best_unc, &best_mat, iters);
                if new_unc == 0 {
                    break;
                }
            }
        }
    }

    state.mat.copy_from_slice(&best_mat);
    state.recompute_counts();

    SearchResult {
        best_uncovered: best_unc,
        best_mat,
        moves: iters,
        accepted_moves: accepted,
        reheats,
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
        tenure_base: 8,
        tenure_jitter: 6,
        noise_prob: 0.008,
        use_weights: true,
        t_start: 1.5,
        t_end: 0.1,
        endgame_threshold: 25,
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
