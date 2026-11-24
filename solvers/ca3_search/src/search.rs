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
    pub reheat_steps: u64,
    pub lock_rows: usize,
    pub lock_cols: usize,
    /// Optional stop if no improvement for this many accepted moves (0 = disabled)
    pub max_stagnation: u64,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            tenure_base: 8,
            tenure_jitter: 7,
            noise_prob: 0.01,
            use_weights: false,
            reheat_steps: 250_000,
            lock_rows: 0,
            lock_cols: 0,
            max_stagnation: 0,
        }
    }
}

pub struct SearchResult {
    pub best_uncovered: usize,
    pub best_mat: Vec<u8>,
    /// Total candidate-step iterations (or accepted moves + evaluated steps)
    pub moves: u64,
    #[allow(dead_code)]
    pub accepted_moves: u64,
    pub reheats: u64,
}

#[inline(always)]
fn is_editable(r: usize, c: usize, lock_rows: usize, lock_cols: usize) -> bool {
    r >= lock_rows || c >= lock_cols
}

/// Focused WalkSAT + Tabu + Adaptive-Thermostat Metropolis (SA) Hybrid for CaState.
/// - Picks an uncovered triple and evaluates all matching-2 (fallback matching-1) focused moves.
/// - Uses Metropolis acceptance on uphill moves (delta > 0) instead of forcing large +5..+10 jumps.
/// - Mixes in lightweight random-cell Metropolis moves to reshape count==1 bottlenecks at delta<=0.
/// - Self-tuning adaptive temperature (cooling during descent, warming to melt rigid local minima)
///   plus periodic exact full-focused polish when uncovered <= 24.
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

    let mut tabu = vec![0u32; n * k * v];
    let mut best_unc = state.uncovered();
    let mut best_mat = state.mat.clone();

    let mut iters: u64 = 0;
    let mut accepted: u64 = 0;
    let mut step_u32: u32 = 1;
    let mut no_improve_iters: u64 = 0;
    let mut no_improve_since_best: u64 = 0;
    let mut reheats: u64 = 0;
    let mut max_weight: u32 = 1;

    // Adaptive SA temperature thermostat
    let mut temp: f64 = 0.85;
    let temp_min: f64 = 0.22;
    let temp_max: f64 = 2.80;
    let mut window_accepts: u32 = 0;
    let mut window_uphill_trials: u32 = 0;
    let mut consec_rejects: u32 = 0;

    let mut cands: Vec<(usize, usize, u8)> = Vec::with_capacity(64);
    let mut fallback: Vec<(usize, usize, u8)> = Vec::with_capacity(48);

    while state.uncovered() > 0 {
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
        if cfg.max_stagnation > 0 && no_improve_since_best >= cfg.max_stagnation {
            break;
        }
        if step_u32 > 4_000_000_000 {
            tabu.fill(0);
            step_u32 = 1;
        }

        iters += 1;

        // 15% of steps: fast random editable cell move (1 eval_move) to melt count==1 structure
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
                let (du, _dw) = state.eval_move(r, c, nv, false);
                let cur_unc = state.uncovered() as i32;
                let asp = (cur_unc + du) < (best_unc as i32);
                let is_tabu = !asp && tabu[(r * k + c) * v + nv as usize] > step_u32;
                if !is_tabu {
                    let accept = if du <= 0 {
                        true
                    } else {
                        window_uphill_trials += 1;
                        rng.gen_f64() < (-(du as f64) / temp).exp()
                    };
                    if accept {
                        if du > 0 {
                            window_accepts += 1;
                        }
                        consec_rejects = 0;
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
                            no_improve_iters = 0;
                            no_improve_since_best = 0;
                            on_improve(best_unc, &best_mat, iters);
                            if new_unc == 0 {
                                break;
                            }
                        }
                    }
                }
            }
            continue;
        }

        // Focused WalkSAT step: pick 1 uncovered interaction uniformly at random
        let ulen = state.uncovered_list.len();
        let u_idx = state.uncovered_list[rng.gen_usize(ulen)] as usize;
        let t_idx = u_idx / v3;
        let tup = u_idx % v3;
        let v0 = (tup / v2) as u8;
        let v1 = ((tup / v) % v) as u8;
        let v2_val = (tup % v) as u8;
        let [c0, c1, c2] = state.triple_cols[t_idx];
        let (c0, c1, c2) = (c0 as usize, c1 as usize, c2 as usize);

        cands.clear();
        fallback.clear();

        let mat = &state.mat;
        for r in 0..n {
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
            } else if cands.is_empty() && fallback.len() < 40 {
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

        let active_cands: &[(usize, usize, u8)] = if !cands.is_empty() {
            &cands
        } else if !fallback.is_empty() {
            &fallback
        } else {
            let cols = [(c0, v0), (c1, v1), (c2, v2_val)];
            for _ in 0..12 {
                let r = rng.gen_usize(n);
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

        let cur_unc = state.uncovered() as i32;

        // Evaluate all candidates for this uncovered triple and select best non-tabu
        let mut best_nt_score = (i64::MAX, i32::MAX);
        let mut best_nt_move = active_cands[0];
        let mut nt_ties = 0u64;

        let mut best_all_score = (i64::MAX, i32::MAX);
        let mut best_all_move = active_cands[0];
        let mut all_ties = 0u64;

        for &(r, c, nv) in active_cands {
            let (du, dw) = state.eval_move(r, c, nv, cfg.use_weights);
            let score = (dw, du);
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

        let (chosen, chosen_du, chosen_dw) = if nt_ties > 0 {
            (best_nt_move, best_nt_score.1, best_nt_score.0)
        } else {
            (best_all_move, best_all_score.1, best_all_score.0)
        };

        // Metropolis acceptance gate:
        // Always accept improving or neutral moves (chosen_du <= 0).
        // For uphill moves (chosen_du > 0), accept with exp(-chosen_du / eff_temp),
        // giving a modest effective temperature boost when clause weights favor the move (chosen_dw <= 0).
        let accept = if chosen_du <= 0 {
            true
        } else {
            window_uphill_trials += 1;
            let eff_temp = if cfg.use_weights && chosen_dw <= 0 {
                (temp * 1.35).min(temp_max)
            } else {
                temp
            };
            let prob = (-(chosen_du as f64) / eff_temp).exp();
            rng.gen_f64() < prob || rng.chance(cfg.noise_prob * 0.25)
        };

        if accept {
            if chosen_du > 0 {
                window_accepts += 1;
            }
            consec_rejects = 0;

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
                no_improve_iters = 0;
                no_improve_since_best = 0;
                // Cool gently on improvement to exploit basin
                temp = (temp * 0.96).max(temp_min);
                on_improve(best_unc, &best_mat, iters);
                if new_unc == 0 {
                    break;
                }
            } else {
                no_improve_iters += 1;
                no_improve_since_best += 1;
            }
        } else {
            consec_rejects += 1;
            no_improve_iters += 1;
            no_improve_since_best += 1;

            // Optional lightweight clause weighting on rejected stubborn triple
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

            // If rejecting many moves in a row (rigid crystal!), warm up temperature rapidly!
            if consec_rejects >= 32 {
                temp = (temp * 1.06).min(temp_max);
                consec_rejects = 0;
            }
        }

        // Self-tuning thermostat every 256 uphill trials:
        // Target uphill acceptance rate ~ 12%..22% (keeps unc near floor while allowing basin crossing)
        if window_uphill_trials >= 256 {
            let rate = window_accepts as f64 / window_uphill_trials as f64;
            let cur_u = state.uncovered();
            if cur_u > best_unc + 25 || rate > 0.25 {
                // Drifting too high -> cool down to pull back to floor
                temp = (temp * 0.92).max(temp_min);
            } else if rate < 0.08 {
                // Frozen -> warm up slightly
                temp = (temp * 1.08).min(temp_max);
            }
            window_accepts = 0;
            window_uphill_trials = 0;
        }

        // Periodic reheat / cyclic temperature wave when stagnant
        if cfg.reheat_steps > 0 && no_improve_iters >= cfg.reheat_steps {
            reheats += 1;
            no_improve_iters = 0;

            if reheats % 3 == 0 {
                // Return to best_mat and heat up to explore a fresh trajectory out of best basin
                state.mat.copy_from_slice(&best_mat);
                state.recompute_counts();
                state.reset_weights();
                max_weight = 1;
                tabu.fill(0);
                step_u32 = 1;
                temp = 1.65;
            } else {
                // Thermal pulse without destroying current basin
                temp = (temp * 1.5).clamp(1.2, temp_max);
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
        noise_prob: 0.01,
        use_weights: true,
        reheat_steps: 50_000,
        lock_rows: 0,
        lock_cols: 0,
        max_stagnation: 0,
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

    // 10,000 raw incremental moves without recompute_counts verifying exact delta & final counts
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
