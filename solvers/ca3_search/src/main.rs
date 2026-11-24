mod io;
mod orbit;
mod rng;
mod search;
mod state;

use io::{
    delete_row, project_drop_col, read_matrix, write_matrix_atomic, write_meta_atomic,
    CheckpointMeta,
};
use orbit::{orbit_sanity_test, search_orbit, OrbitSearchConfig, OrbitState};
use rng::Rng;
use search::{ca_sanity_test, search_ca, SearchConfig};
use state::CaState;

use std::env;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

struct Args {
    mode: String,
    input: Option<PathBuf>,
    resume: Option<PathBuf>,
    v: usize,
    k: usize,
    n: Option<usize>,
    min_n: Option<usize>,
    threads: usize,
    seed: u64,
    time_limit_secs: f64,
    checkpoint_dir: PathBuf,
    prefix: Option<String>,
    use_weights: bool,
    noise: f64,
    tenure: u32,
    reheat: u64,
    drop_col: Option<String>,
    probe_secs: f64,
    stage1_frac: f64,
    const_rows: Option<usize>,
    unfreeze_frac: f64,
    restart_steps: u64,
}

fn parse_args() -> Result<Args, String> {
    let raw: Vec<String> = env::args().collect();
    if raw.len() < 2 || raw[1] == "-h" || raw[1] == "--help" {
        return Err(
            "Usage: ca3_search <sanity|reduce|extend|orbit> [options]\n\
             Common: --v <5> --k <9> --n <N> --min-n <N> --threads <2> --seed <42> \
             --time-limit-secs <60> --checkpoint-dir <dir> --prefix <name> \
             --no-weights --noise <0.008> --tenure <8> --reheat <250000>\n\
             reduce: --input <file> [--drop-col <idx|all>] [--probe-secs <1.5>] [--resume <file>]\n\
             extend: --input <file> --n <target_n> [--stage1-frac <0.25>]\n\
             orbit:  --n <target_n> --k <k> --v <v> [--const-rows <0|v>] [--unfreeze-frac <0.25>] [--restart-steps <400000>]"
                .to_string(),
        );
    }

    let mut args = Args {
        mode: raw[1].clone(),
        input: None,
        resume: None,
        v: 5,
        k: 9,
        n: None,
        min_n: None,
        threads: 2,
        seed: 42,
        time_limit_secs: 60.0,
        checkpoint_dir: PathBuf::from("/tmp/ca3_checkpoints"),
        prefix: None,
        use_weights: true,
        noise: 0.008,
        tenure: 8,
        reheat: 250_000,
        drop_col: None,
        probe_secs: 1.5,
        stage1_frac: 0.25,
        const_rows: None,
        unfreeze_frac: 0.25,
        restart_steps: 400_000,
    };

    let mut i = 2;
    while i < raw.len() {
        let flag = raw[i].as_str();
        let next_val = |idx: &mut usize| -> Result<String, String> {
            if *idx + 1 >= raw.len() {
                Err(format!("missing value for {}", raw[*idx]))
            } else {
                *idx += 1;
                Ok(raw[*idx].clone())
            }
        };
        match flag {
            "--input" => args.input = Some(PathBuf::from(next_val(&mut i)?)),
            "--resume" => args.resume = Some(PathBuf::from(next_val(&mut i)?)),
            "--v" => args.v = next_val(&mut i)?.parse().map_err(|e| format!("--v: {}", e))?,
            "--k" => args.k = next_val(&mut i)?.parse().map_err(|e| format!("--k: {}", e))?,
            "--n" => args.n = Some(next_val(&mut i)?.parse().map_err(|e| format!("--n: {}", e))?),
            "--min-n" => {
                args.min_n = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--min-n: {}", e))?,
                )
            }
            "--threads" => {
                args.threads = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--threads: {}", e))?
            }
            "--seed" => {
                args.seed = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--seed: {}", e))?
            }
            "--time-limit-secs" => {
                args.time_limit_secs = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--time-limit-secs: {}", e))?
            }
            "--checkpoint-dir" => args.checkpoint_dir = PathBuf::from(next_val(&mut i)?),
            "--prefix" => args.prefix = Some(next_val(&mut i)?),
            "--no-weights" => args.use_weights = false,
            "--noise" => {
                args.noise = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--noise: {}", e))?
            }
            "--tenure" => {
                args.tenure = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--tenure: {}", e))?
            }
            "--reheat" => {
                args.reheat = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--reheat: {}", e))?
            }
            "--drop-col" => args.drop_col = Some(next_val(&mut i)?),
            "--probe-secs" => {
                args.probe_secs = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--probe-secs: {}", e))?
            }
            "--stage1-frac" => {
                args.stage1_frac = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--stage1-frac: {}", e))?
            }
            "--const-rows" => {
                args.const_rows = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--const-rows: {}", e))?,
                )
            }
            "--unfreeze-frac" => {
                args.unfreeze_frac = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--unfreeze-frac: {}", e))?
            }
            "--restart-steps" => {
                args.restart_steps = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--restart-steps: {}", e))?
            }
            other => return Err(format!("unknown argument: {}", other)),
        }
        i += 1;
    }

    if args.threads == 0 {
        args.threads = 1;
    }
    Ok(args)
}

fn thread_seed(base_seed: u64, tid: usize) -> u64 {
    base_seed ^ ((tid as u64).wrapping_add(1).wrapping_mul(0x9e3779b97f4a7c15))
}

fn pick_min_excl_row(state: &CaState, rng: &mut Rng, rank_jitter: usize) -> (usize, usize) {
    let excl = state.row_exclusivities();
    let mut order: Vec<(usize, usize)> = excl.into_iter().enumerate().collect();
    order.sort_by_key(|&(_, e)| e);
    let min_e = order[0].1;
    if rank_jitter == 0 {
        // Tie-break uniformly among all minimum-exclusivity rows
        let tied_count = order.iter().take_while(|&&(_, e)| e == min_e).count();
        let chosen = order[rng.gen_usize(tied_count)];
        return chosen;
    }
    let pool = (rank_jitter + 1).min(order.len());
    order[rng.gen_usize(pool)]
}

struct GlobalBest {
    n: usize,
    k: usize,
    v: usize,
    uncovered: usize,
    mat: Vec<u8>,
    best_thread: usize,
    best_seed: u64,
    last_write: Instant,
    solved_n: Option<usize>,
}

fn save_checkpoint(
    dir: &PathBuf,
    prefix: &str,
    mode: &str,
    gb: &GlobalBest,
    total_moves: u64,
    elapsed_secs: f64,
    base_seed: u64,
    extra: &str,
) {
    let mps = total_moves as f64 / elapsed_secs.max(1e-9);
    let mat_path = dir.join(format!("{}_best.txt", prefix));
    let meta_path = dir.join(format!("{}_meta.json", prefix));
    if let Err(e) = write_matrix_atomic(&mat_path, &gb.mat, gb.n, gb.k) {
        eprintln!("[WARN] checkpoint matrix write failed: {}", e);
    }
    let meta = CheckpointMeta {
        mode,
        n: gb.n,
        k: gb.k,
        v: gb.v,
        uncovered: gb.uncovered,
        total_moves,
        moves_per_sec: mps,
        elapsed_secs,
        base_seed,
        best_thread: gb.best_thread,
        best_seed: gb.best_seed,
        extra,
    };
    if let Err(e) = write_meta_atomic(&meta_path, &meta) {
        eprintln!("[WARN] checkpoint meta write failed: {}", e);
    }
    if gb.uncovered == 0 {
        let solved_path = dir.join(format!("SOLVED_CA_{}_3_{}_{}.txt", gb.n, gb.k, gb.v));
        if let Err(e) = write_matrix_atomic(&solved_path, &gb.mat, gb.n, gb.k) {
            eprintln!("[WARN] solved matrix write failed: {}", e);
        } else {
            println!(
                "*** SOLUTION_FOUND: CA({}; 3, {}, {}) saved to {} (elapsed={:.2}s, thread={}, seed={}) ***",
                gb.n,
                gb.k,
                gb.v,
                solved_path.display(),
                elapsed_secs,
                gb.best_thread,
                gb.best_seed
            );
        }
    }
}

fn run_sanity(args: &Args) -> Result<(), String> {
    println!("=== SANITY CHECK (t=3, k={}, v={}) ===", args.k, args.v);
    let (mat, n, k, v) = if let Some(ref path) = args.input {
        let lm = read_matrix(path)?;
        let (m, k_use) = if lm.k == args.k + 1 {
            (project_drop_col(&lm.mat, lm.n, lm.k, 0), args.k)
        } else {
            (lm.mat, lm.k)
        };
        let st = CaState::from_matrix(m.clone(), lm.n, k_use, args.v);
        let mut rng = Rng::from_seed(args.seed);
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng, 0);
        println!(
            "Loaded {} ({}x{} -> drop row {} with min_excl={})",
            path.display(),
            lm.n,
            k_use,
            del_r,
            min_e
        );
        (delete_row(&m, lm.n, k_use, del_r), lm.n - 1, k_use, args.v)
    } else {
        let n = args.n.unwrap_or(184);
        let mut rng = Rng::from_seed(args.seed);
        let mut m = vec![0u8; n * args.k];
        for x in &mut m {
            *x = rng.gen_usize(args.v) as u8;
        }
        (m, n, args.k, args.v)
    };

    let (ca_mps, start_unc, end_unc) = ca_sanity_test(mat, n, k, v)?;
    println!(
        "[PASS] CaState 10,000-move incremental check: 0 discrepancies | throughput = {:.0} moves/sec | unc: {} -> {}",
        ca_mps, start_unc, end_unc
    );

    let target_n = args.n.unwrap_or(180);
    let num_starters = (target_n.saturating_sub(v)) / v;
    let (orb_mps, orb_unc) = orbit_sanity_test(k, v, num_starters.max(1), true)?;
    println!(
        "[PASS] OrbitState 10,000-move incremental + expansion check: 0 discrepancies | throughput = {:.0} moves/sec | best_unc_orbits = {}",
        orb_mps, orb_unc
    );
    Ok(())
}

/// Multi-thread reduce loop: runs at current N until uncovered==0 or deadline.
/// If uncovered==0 is achieved and current_n > min_n, deletes min-exclusivity row and continues to current_n - 1!
fn run_reduce_multithread(
    initial_mat: Vec<u8>,
    mut cur_n: usize,
    k: usize,
    v: usize,
    min_n: usize,
    args: &Args,
    t_start: Instant,
    deadline: Instant,
    prefix: &str,
    extra_label: &str,
) -> Result<(), String> {
    let mut cur_mat = initial_mat;
    let total_moves_all = Arc::new(AtomicU64::new(0));

    loop {
        if Instant::now() >= deadline {
            break;
        }
        let check_st = CaState::from_matrix(cur_mat.clone(), cur_n, k, v);
        let start_unc = check_st.uncovered();
        println!(
            "[reduce] Starting N={} (k={}, v={}), initial uncovered={}, remaining={:.1}s",
            cur_n,
            k,
            v,
            start_unc,
            deadline.saturating_duration_since(Instant::now()).as_secs_f64()
        );

        let solved_flag = Arc::new(AtomicBool::new(false));
        let gb = Arc::new(Mutex::new(GlobalBest {
            n: cur_n,
            k,
            v,
            uncovered: start_unc,
            mat: cur_mat.clone(),
            best_thread: 0,
            best_seed: args.seed,
            last_write: Instant::now() - Duration::from_secs(60),
            solved_n: if start_unc == 0 { Some(cur_n) } else { None },
        }));

        if start_unc == 0 {
            let guard = gb.lock().unwrap();
            save_checkpoint(
                &args.checkpoint_dir,
                prefix,
                "reduce",
                &guard,
                total_moves_all.load(Ordering::Relaxed),
                t_start.elapsed().as_secs_f64(),
                args.seed,
                extra_label,
            );
        } else {
            let mut handles = Vec::with_capacity(args.threads);
            let round_moves = Arc::new(AtomicU64::new(0));

            for tid in 0..args.threads {
                let mat_clone = cur_mat.clone();
                let solved_c = Arc::clone(&solved_flag);
                let gb_c = Arc::clone(&gb);
                let rm_c = Arc::clone(&round_moves);
                let tm_c = Arc::clone(&total_moves_all);
                let ckpt_dir = args.checkpoint_dir.clone();
                let pfx = prefix.to_string();
                let ext = extra_label.to_string();
                let seed_t = thread_seed(args.seed ^ (cur_n as u64 * 1009), tid);
                let base_seed = args.seed;

                // Slight parameter diversity across threads
                let cfg = SearchConfig {
                    tenure_base: args.tenure + (tid as u32) * 2,
                    tenure_jitter: 7 + (tid as u32) * 3,
                    noise_prob: args.noise * (1.0 + 0.35 * tid as f64),
                    use_weights: args.use_weights,
                    reheat_steps: args.reheat + (tid as u64) * 50_000,
                    lock_rows: 0,
                    lock_cols: 0,
                    max_stagnation: 0,
                };

                handles.push(thread::spawn(move || {
                    let mut rng = Rng::from_seed(seed_t);
                    let mut state = CaState::from_matrix(mat_clone, cur_n, k, v);
                    // Thread > 0 applies 1-2 light random flips only if starting from identical matrix to diverge immediately
                    if tid > 0 && state.uncovered() > 0 {
                        for _ in 0..2 {
                            let r = rng.gen_usize(cur_n);
                            let c = rng.gen_usize(k);
                            let nv = rng.gen_usize(v) as u8;
                            state.apply_move(r, c, nv);
                        }
                    }
                    let mut last_reported_moves = 0u64;
                    let res = search_ca(
                        &mut state,
                        &mut rng,
                        &cfg,
                        deadline,
                        &solved_c,
                        None,
                        |new_unc, best_m, cur_m| {
                            let dm = cur_m - last_reported_moves;
                            last_reported_moves = cur_m;
                            rm_c.fetch_add(dm, Ordering::Relaxed);
                            tm_c.fetch_add(dm, Ordering::Relaxed);

                            let mut guard = gb_c.lock().unwrap();
                            if new_unc < guard.uncovered {
                                guard.uncovered = new_unc;
                                guard.mat.copy_from_slice(best_m);
                                guard.best_thread = tid;
                                guard.best_seed = seed_t;
                                let elapsed = t_start.elapsed().as_secs_f64();
                                if new_unc == 0 {
                                    guard.solved_n = Some(cur_n);
                                    solved_c.store(true, Ordering::Relaxed);
                                }
                                if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2) {
                                    guard.last_write = Instant::now();
                                    save_checkpoint(
                                        &ckpt_dir,
                                        &pfx,
                                        "reduce",
                                        &guard,
                                        tm_c.load(Ordering::Relaxed),
                                        elapsed,
                                        base_seed,
                                        &ext,
                                    );
                                }
                            }
                        },
                    );
                    let rem = res.moves - last_reported_moves;
                    rm_c.fetch_add(rem, Ordering::Relaxed);
                    tm_c.fetch_add(rem, Ordering::Relaxed);
                }));
            }

            for h in handles {
                let _ = h.join();
            }

            let guard = gb.lock().unwrap();
            let elapsed = t_start.elapsed().as_secs_f64();
            let tot = total_moves_all.load(Ordering::Relaxed);
            save_checkpoint(
                &args.checkpoint_dir,
                prefix,
                "reduce",
                &guard,
                tot,
                elapsed,
                args.seed,
                extra_label,
            );
            println!(
                "[reduce] N={} finished: best_uncovered={}, total_moves={} ({:.0} moves/sec), elapsed={:.2}s",
                cur_n,
                guard.uncovered,
                tot,
                tot as f64 / elapsed.max(1e-9),
                elapsed
            );
        }

        let (solved, solved_mat) = {
            let guard = gb.lock().unwrap();
            (guard.uncovered == 0, guard.mat.clone())
        };

        if solved && cur_n > min_n && Instant::now() < deadline {
            // Delete minimum-exclusivity row and keep reducing!
            let st = CaState::from_matrix(solved_mat.clone(), cur_n, k, v);
            let mut rng = Rng::from_seed(args.seed ^ (cur_n as u64 * 31337));
            let (del_r, min_e) = pick_min_excl_row(&st, &mut rng, 0);
            println!(
                "[reduce] Solved N={}! Deleting row {} (min_excl={}) -> N={}",
                cur_n,
                del_r,
                min_e,
                cur_n - 1
            );
            cur_mat = delete_row(&solved_mat, cur_n, k, del_r);
            cur_n -= 1;
        } else {
            break;
        }
    }
    Ok(())
}

fn run_reduce(args: &Args) -> Result<(), String> {
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or("reduce");

    if let Some(ref resume_path) = args.resume {
        let lm = read_matrix(resume_path)?;
        let st = CaState::from_matrix(lm.mat.clone(), lm.n, lm.k, args.v);
        let min_n = args.min_n.unwrap_or(lm.n.saturating_sub(5));
        println!(
            "[reduce] Resuming from {} ({}x{}, v={}, uncovered={})",
            resume_path.display(),
            lm.n,
            lm.k,
            args.v,
            st.uncovered()
        );
        return run_reduce_multithread(
            lm.mat,
            lm.n,
            lm.k,
            args.v,
            min_n,
            args,
            t_start,
            deadline,
            prefix,
            &format!("resume={}", resume_path.display()),
        );
    }

    let input_path = args
        .input
        .as_ref()
        .ok_or_else(|| "reduce mode requires --input <path> or --resume <path>".to_string())?;
    let lm = read_matrix(input_path)?;

    if args.drop_col.as_deref() == Some("all") {
        let k_proj = lm.k - 1;
        let target_n = args.n.unwrap_or(lm.n - 1);
        let min_n = args.min_n.unwrap_or(target_n.saturating_sub(4));
        println!(
            "[reduce] Probing all {} column projections of {} ({}x{} -> {}x{}), {:.2}s/proj across {} threads...",
            lm.k,
            input_path.display(),
            lm.n,
            lm.k,
            target_n,
            k_proj,
            args.probe_secs,
            args.threads
        );

        struct ProbeRes {
            drop_col: usize,
            min_excl: usize,
            del_row: usize,
            best_unc: usize,
            moves: u64,
            best_mat: Vec<u8>,
        }

        let results: Arc<Mutex<Vec<ProbeRes>>> = Arc::new(Mutex::new(Vec::new()));
        let next_dc = Arc::new(AtomicU64::new(0));
        let k_in = lm.k;
        let n_in = lm.n;
        let v = args.v;
        let base_mat = Arc::new(lm.mat);

        let mut handles = Vec::with_capacity(args.threads);
        for tid in 0..args.threads {
            let res_c = Arc::clone(&results);
            let dc_c = Arc::clone(&next_dc);
            let bm_c = Arc::clone(&base_mat);
            let probe_dur = Duration::from_secs_f64(args.probe_secs);
            let seed_base = args.seed;
            let cfg = SearchConfig {
                tenure_base: args.tenure,
                tenure_jitter: 7,
                noise_prob: args.noise,
                use_weights: args.use_weights,
                reheat_steps: 150_000,
                lock_rows: 0,
                lock_cols: 0,
                max_stagnation: 0,
            };

            handles.push(thread::spawn(move || {
                let stop = AtomicBool::new(false);
                loop {
                    let dc = dc_c.fetch_add(1, Ordering::Relaxed) as usize;
                    if dc >= k_in || Instant::now() >= deadline {
                        break;
                    }
                    let proj = project_drop_col(&bm_c, n_in, k_in, dc);
                    let mut st = CaState::from_matrix(proj.clone(), n_in, k_proj, v);
                    let mut rng = Rng::from_seed(thread_seed(seed_base ^ (dc as u64 * 997), tid));
                    let mut cur_m = proj;
                    let mut cur_n = n_in;
                    let mut first_min_excl = 0usize;
                    let mut first_del_r = 0usize;
                    while cur_n > target_n {
                        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng, 0);
                        if cur_n == n_in {
                            first_min_excl = min_e;
                            first_del_r = del_r;
                        }
                        cur_m = delete_row(&cur_m, cur_n, k_proj, del_r);
                        cur_n -= 1;
                        st = CaState::from_matrix(cur_m.clone(), cur_n, k_proj, v);
                    }
                    let p_deadline = (Instant::now() + probe_dur).min(deadline);
                    let sr = search_ca(&mut st, &mut rng, &cfg, p_deadline, &stop, None, |_, _, _| {});
                    res_c.lock().unwrap().push(ProbeRes {
                        drop_col: dc,
                        min_excl: first_min_excl,
                        del_row: first_del_r,
                        best_unc: sr.best_uncovered,
                        moves: sr.moves,
                        best_mat: sr.best_mat,
                    });
                }
            }));
        }
        for h in handles {
            let _ = h.join();
        }

        let mut list = results.lock().unwrap();
        list.sort_by_key(|r| r.drop_col);
        println!("Probe summary (N={}, k={}, v={}):", target_n, k_proj, v);
        for r in list.iter() {
            println!(
                "  drop_col={:2} | del_row={:3} (min_excl={:2}) | probe_best_unc={:3} | moves={}",
                r.drop_col, r.del_row, r.min_excl, r.best_unc, r.moves
            );
        }
        let best_idx = list
            .iter()
            .enumerate()
            .min_by_key(|(_, r)| (r.best_unc, r.min_excl))
            .map(|(i, _)| i)
            .ok_or_else(|| "no probe results".to_string())?;
        let best_dc = list[best_idx].drop_col;
        let best_probe_unc = list[best_idx].best_unc;
        let best_mat = list[best_idx].best_mat.clone();
        drop(list);

        println!(
            "[reduce] Selected best projection: drop_col={} (probe_best_unc={}), launching main search...",
            best_dc, best_probe_unc
        );
        return run_reduce_multithread(
            best_mat,
            target_n,
            k_proj,
            v,
            min_n,
            args,
            t_start,
            deadline,
            prefix,
            &format!("drop_col={}", best_dc),
        );
    }

    // Single projection or direct input
    let (mut cur_mat, k_use) = if let Some(ref dc_str) = args.drop_col {
        let dc: usize = dc_str
            .parse()
            .map_err(|e| format!("invalid --drop-col '{}': {}", dc_str, e))?;
        (project_drop_col(&lm.mat, lm.n, lm.k, dc), lm.k - 1)
    } else {
        (lm.mat, lm.k)
    };
    let mut cur_n = lm.n;
    let target_n = args.n.unwrap_or(cur_n - 1);
    let min_n = args.min_n.unwrap_or(target_n.saturating_sub(4));
    let mut rng = Rng::from_seed(args.seed);
    while cur_n > target_n {
        let st = CaState::from_matrix(cur_mat.clone(), cur_n, k_use, args.v);
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng, 0);
        println!(
            "[reduce] Deleting row {} (min_excl={}) from N={} -> N={}",
            del_r,
            min_e,
            cur_n,
            cur_n - 1
        );
        cur_mat = delete_row(&cur_mat, cur_n, k_use, del_r);
        cur_n -= 1;
    }

    run_reduce_multithread(
        cur_mat,
        cur_n,
        k_use,
        args.v,
        min_n,
        args,
        t_start,
        deadline,
        prefix,
        &format!("input={}", input_path.display()),
    )
}

fn run_extend(args: &Args) -> Result<(), String> {
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or("extend");
    let input_path = args
        .input
        .as_ref()
        .ok_or_else(|| "extend mode requires --input <base_ca_file>".to_string())?;
    let lm = read_matrix(input_path)?;
    let n_base = lm.n;
    let k_base = lm.k;
    let k = k_base + 1;
    let v = args.v;
    let target_n = args
        .n
        .ok_or_else(|| "extend mode requires --n <target_n>".to_string())?;
    if target_n < n_base {
        return Err(format!("target_n={} < base n={}", target_n, n_base));
    }
    let repair_rows = target_n - n_base;
    let stage1_secs = args.time_limit_secs * args.stage1_frac.clamp(0.0, 0.9);
    let stage1_deadline = t_start + Duration::from_secs_f64(stage1_secs);

    println!(
        "[extend] Base {} ({}x{}, v={}) -> target CA({}; 3, {}, {}) (+{} repair rows), stage1={:.1}s, total={:.1}s, threads={}",
        input_path.display(),
        n_base,
        k_base,
        v,
        target_n,
        k,
        v,
        repair_rows,
        stage1_secs,
        args.time_limit_secs,
        args.threads
    );

    let solved_flag = Arc::new(AtomicBool::new(false));
    let total_moves = Arc::new(AtomicU64::new(0));
    let gb = Arc::new(Mutex::new(GlobalBest {
        n: target_n,
        k,
        v,
        uncovered: usize::MAX,
        mat: vec![0u8; target_n * k],
        best_thread: 0,
        best_seed: args.seed,
        last_write: Instant::now() - Duration::from_secs(60),
        solved_n: None,
    }));

    let base_mat = Arc::new(lm.mat);
    let mut handles = Vec::with_capacity(args.threads);

    for tid in 0..args.threads {
        let bm_c = Arc::clone(&base_mat);
        let solved_c = Arc::clone(&solved_flag);
        let gb_c = Arc::clone(&gb);
        let tm_c = Arc::clone(&total_moves);
        let ckpt_dir = args.checkpoint_dir.clone();
        let pfx = prefix.to_string();
        let seed_t = thread_seed(args.seed, tid);
        let base_seed = args.seed;
        let use_weights = args.use_weights;
        let tenure = args.tenure + (tid as u32) * 2;
        let noise = args.noise * (1.0 + 0.35 * tid as f64);
        let reheat = args.reheat + (tid as u64) * 50_000;

        handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut state =
                CaState::build_extended_greedy(&bm_c, n_base, k_base, target_n, v, &mut rng);
            let init_unc = state.uncovered();
            println!(
                "  [extend t={}] Greedy init uncovered={} (seed={})",
                tid, init_unc, seed_t
            );

            {
                let mut guard = gb_c.lock().unwrap();
                if init_unc < guard.uncovered {
                    guard.uncovered = init_unc;
                    guard.mat.copy_from_slice(&state.mat);
                    guard.best_thread = tid;
                    guard.best_seed = seed_t;
                    if init_unc == 0 {
                        solved_c.store(true, Ordering::Relaxed);
                        save_checkpoint(
                            &ckpt_dir,
                            &pfx,
                            "extend",
                            &guard,
                            tm_c.load(Ordering::Relaxed),
                            t_start.elapsed().as_secs_f64(),
                            base_seed,
                            "stage=init",
                        );
                    }
                }
            }

            // Stage 1: optimize col k-1 of base rows + all cols of repair rows
            if !solved_c.load(Ordering::Relaxed) && Instant::now() < stage1_deadline {
                let cfg1 = SearchConfig {
                    tenure_base: tenure,
                    tenure_jitter: 7,
                    noise_prob: noise,
                    use_weights,
                    reheat_steps: reheat / 2,
                    lock_rows: n_base,
                    lock_cols: k_base,
                    max_stagnation: 300_000,
                };
                let mut last_m = 0u64;
                let res1 = search_ca(
                    &mut state,
                    &mut rng,
                    &cfg1,
                    stage1_deadline,
                    &solved_c,
                    None,
                    |new_unc, best_m, cur_m| {
                        let dm = cur_m - last_m;
                        last_m = cur_m;
                        tm_c.fetch_add(dm, Ordering::Relaxed);
                        let mut guard = gb_c.lock().unwrap();
                        if new_unc < guard.uncovered {
                            guard.uncovered = new_unc;
                            guard.mat.copy_from_slice(best_m);
                            guard.best_thread = tid;
                            guard.best_seed = seed_t;
                            if new_unc == 0 {
                                solved_c.store(true, Ordering::Relaxed);
                            }
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2) {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    "extend",
                                    &guard,
                                    tm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    "stage=1_locked",
                                );
                            }
                        }
                    },
                );
                tm_c.fetch_add(res1.moves - last_m, Ordering::Relaxed);
                println!(
                    "  [extend t={}] Stage 1 done: best_unc={}, moves={} -> unfreezing full array",
                    tid, res1.best_uncovered, res1.moves
                );
            }

            // Stage 2: Unfreeze entire array!
            if !solved_c.load(Ordering::Relaxed) && Instant::now() < deadline {
                state.reset_weights();
                let cfg2 = SearchConfig {
                    tenure_base: tenure,
                    tenure_jitter: 8,
                    noise_prob: noise,
                    use_weights,
                    reheat_steps: reheat,
                    lock_rows: 0,
                    lock_cols: 0,
                    max_stagnation: 0,
                };
                let mut last_m = 0u64;
                let res2 = search_ca(
                    &mut state,
                    &mut rng,
                    &cfg2,
                    deadline,
                    &solved_c,
                    None,
                    |new_unc, best_m, cur_m| {
                        let dm = cur_m - last_m;
                        last_m = cur_m;
                        tm_c.fetch_add(dm, Ordering::Relaxed);
                        let mut guard = gb_c.lock().unwrap();
                        if new_unc < guard.uncovered {
                            guard.uncovered = new_unc;
                            guard.mat.copy_from_slice(best_m);
                            guard.best_thread = tid;
                            guard.best_seed = seed_t;
                            if new_unc == 0 {
                                solved_c.store(true, Ordering::Relaxed);
                            }
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2) {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    "extend",
                                    &guard,
                                    tm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    "stage=2_free",
                                );
                            }
                        }
                    },
                );
                tm_c.fetch_add(res2.moves - last_m, Ordering::Relaxed);
                println!(
                    "  [extend t={}] Stage 2 done: best_unc={}, moves={}, reheats={}",
                    tid, res2.best_uncovered, res2.moves, res2.reheats
                );
            }
        }));
    }

    for h in handles {
        let _ = h.join();
    }

    let guard = gb.lock().unwrap();
    let elapsed = t_start.elapsed().as_secs_f64();
    let tot = total_moves.load(Ordering::Relaxed);
    save_checkpoint(
        &args.checkpoint_dir,
        prefix,
        "extend",
        &guard,
        tot,
        elapsed,
        args.seed,
        &format!("base={}_r={}", n_base, repair_rows),
    );
    println!(
        "[extend] SUMMARY N={}: best_uncovered={}, total_moves={} ({:.0} moves/sec), elapsed={:.2}s",
        target_n,
        guard.uncovered,
        tot,
        tot as f64 / elapsed.max(1e-9),
        elapsed
    );
    Ok(())
}

fn run_orbit(args: &Args) -> Result<(), String> {
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or("orbit");
    let k = args.k;
    let v = args.v;
    let target_n = args.n.unwrap_or(180);
    let const_rows = args.const_rows.unwrap_or(v);
    if const_rows != 0 && const_rows != v {
        return Err(format!("--const-rows must be 0 or v={}", v));
    }
    let has_const = const_rows == v;
    let num_starters = (target_n - const_rows) / v;
    let free_rows = (target_n - const_rows) % v;

    let unfreeze_secs = args.time_limit_secs * args.unfreeze_frac.clamp(0.0, 0.9);
    let cyclic_secs = (args.time_limit_secs - unfreeze_secs).max(0.0);
    let cyclic_deadline = t_start + Duration::from_secs_f64(cyclic_secs);

    println!(
        "[orbit] Target CA({}; 3, {}, {}): {} Z_{}-starters + {} const rows + {} free rows | cyclic={:.1}s, unfreeze={:.1}s, threads={}",
        target_n,
        k,
        v,
        num_starters,
        v,
        const_rows,
        free_rows,
        cyclic_secs,
        unfreeze_secs,
        args.threads
    );

    let solved_flag = Arc::new(AtomicBool::new(false));
    let total_orbit_moves = Arc::new(AtomicU64::new(0));
    let total_polish_moves = Arc::new(AtomicU64::new(0));

    let best_orbit: Arc<Mutex<(usize, Vec<u8>, usize, u64)>> = Arc::new(Mutex::new((
        usize::MAX,
        vec![0u8; num_starters * k],
        0,
        args.seed,
    )));

    // Phase 1: Pure cyclic Z_v orbit search across all threads
    let mut handles = Vec::with_capacity(args.threads);
    for tid in 0..args.threads {
        let solved_c = Arc::clone(&solved_flag);
        let bo_c = Arc::clone(&best_orbit);
        let om_c = Arc::clone(&total_orbit_moves);
        let seed_t = thread_seed(args.seed, tid);
        let cfg = OrbitSearchConfig {
            tenure_base: args.tenure + (tid as u32) * 2,
            tenure_jitter: 6 + (tid as u32) * 2,
            noise_prob: args.noise * (1.0 + 0.4 * tid as f64),
            use_weights: args.use_weights,
            reheat_steps: 80_000 + (tid as u64) * 30_000,
            restart_steps: args.restart_steps + (tid as u64) * 150_000,
        };

        handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut st = OrbitState::new_random(num_starters, k, v, has_const, &mut rng);
            let res = search_orbit(&mut st, &mut rng, &cfg, cyclic_deadline, &solved_c, None);
            om_c.fetch_add(res.moves, Ordering::Relaxed);
            println!(
                "  [orbit t={}] Cyclic done: best_unc_orbits={} (expanded_unc={}), moves={}, restarts={}",
                tid,
                res.best_uncovered_orbits,
                res.best_uncovered_orbits * v,
                res.moves,
                res.restarts
            );
            let mut guard = bo_c.lock().unwrap();
            if res.best_uncovered_orbits < guard.0 {
                guard.0 = res.best_uncovered_orbits;
                guard.1 = res.best_starters;
                guard.2 = tid;
                guard.3 = seed_t;
                if res.best_uncovered_orbits == 0 {
                    solved_c.store(true, Ordering::Relaxed);
                }
            }
        }));
    }
    for h in handles {
        let _ = h.join();
    }

    let (best_orb_unc, best_starters, best_tid, best_seed_orb) = best_orbit.lock().unwrap().clone();
    let cyclic_elapsed = t_start.elapsed().as_secs_f64();
    let orb_moves = total_orbit_moves.load(Ordering::Relaxed);
    println!(
        "[orbit] Cyclic phase summary: best_unc_orbits={} (expanded_unc={}), orbit_moves={} ({:.0} moves/sec), elapsed={:.2}s",
        best_orb_unc,
        best_orb_unc * v,
        orb_moves,
        orb_moves as f64 / cyclic_elapsed.max(1e-9),
        cyclic_elapsed
    );

    // Expand best cyclic solution into full CaState
    let orb_state = OrbitState::from_starters(best_starters, num_starters, k, v, has_const);
    let mut exp_rng = Rng::from_seed(args.seed ^ 0x5555_AAAA);
    let expanded_ca = orb_state.expand_to_ca(target_n, &mut exp_rng);
    let exp_unc = expanded_ca.uncovered();

    let gb = Arc::new(Mutex::new(GlobalBest {
        n: target_n,
        k,
        v,
        uncovered: exp_unc,
        mat: expanded_ca.mat.clone(),
        best_thread: best_tid,
        best_seed: best_seed_orb,
        last_write: Instant::now() - Duration::from_secs(60),
        solved_n: if exp_unc == 0 { Some(target_n) } else { None },
    }));

    // Checkpoint cyclic result
    {
        let guard = gb.lock().unwrap();
        save_checkpoint(
            &args.checkpoint_dir,
            prefix,
            "orbit",
            &guard,
            orb_moves,
            cyclic_elapsed,
            args.seed,
            &format!("starters={}_const={}_phase=cyclic", num_starters, const_rows),
        );
    }

    // Phase 2: Optional Unfreeze Polishing on expanded full matrix
    if exp_unc > 0 && Instant::now() < deadline && unfreeze_secs > 0.1 {
        println!(
            "[orbit] Launching unfreeze polishing from expanded_unc={} for {:.1}s across {} threads...",
            exp_unc,
            deadline.saturating_duration_since(Instant::now()).as_secs_f64(),
            args.threads
        );
        let polish_solved = Arc::new(AtomicBool::new(false));
        let mut p_handles = Vec::with_capacity(args.threads);
        let exp_mat = Arc::new(expanded_ca.mat);

        for tid in 0..args.threads {
            let em_c = Arc::clone(&exp_mat);
            let ps_c = Arc::clone(&polish_solved);
            let gb_c = Arc::clone(&gb);
            let pm_c = Arc::clone(&total_polish_moves);
            let ckpt_dir = args.checkpoint_dir.clone();
            let pfx = prefix.to_string();
            let seed_t = thread_seed(args.seed ^ 0x7777_1111, tid);
            let base_seed = args.seed;
            let cfg = SearchConfig {
                tenure_base: args.tenure + (tid as u32) * 2,
                tenure_jitter: 7,
                noise_prob: args.noise * (1.0 + 0.35 * tid as f64),
                use_weights: args.use_weights,
                reheat_steps: args.reheat,
                lock_rows: 0,
                lock_cols: 0,
                max_stagnation: 0,
            };

            p_handles.push(thread::spawn(move || {
                let mut rng = Rng::from_seed(seed_t);
                let mut state = CaState::from_matrix((*em_c).clone(), target_n, k, v);
                if tid > 0 {
                    for _ in 0..2 {
                        let r = rng.gen_usize(target_n);
                        let c = rng.gen_usize(k);
                        let nv = rng.gen_usize(v) as u8;
                        state.apply_move(r, c, nv);
                    }
                }
                let mut last_m = 0u64;
                let res = search_ca(
                    &mut state,
                    &mut rng,
                    &cfg,
                    deadline,
                    &ps_c,
                    None,
                    |new_unc, best_m, cur_m| {
                        let dm = cur_m - last_m;
                        last_m = cur_m;
                        pm_c.fetch_add(dm, Ordering::Relaxed);
                        let mut guard = gb_c.lock().unwrap();
                        if new_unc < guard.uncovered {
                            guard.uncovered = new_unc;
                            guard.mat.copy_from_slice(best_m);
                            guard.best_thread = tid;
                            guard.best_seed = seed_t;
                            if new_unc == 0 {
                                ps_c.store(true, Ordering::Relaxed);
                            }
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2) {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    "orbit",
                                    &guard,
                                    orb_moves + pm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    &format!(
                                        "starters={}_const={}_phase=unfreeze",
                                        num_starters, const_rows
                                    ),
                                );
                            }
                        }
                    },
                );
                pm_c.fetch_add(res.moves - last_m, Ordering::Relaxed);
                println!(
                    "  [orbit-unfreeze t={}] done: best_unc={}, moves={}",
                    tid, res.best_uncovered, res.moves
                );
            }));
        }
        for h in p_handles {
            let _ = h.join();
        }
    }

    let guard = gb.lock().unwrap();
    let elapsed = t_start.elapsed().as_secs_f64();
    let pol_moves = total_polish_moves.load(Ordering::Relaxed);
    let tot_moves = orb_moves + pol_moves;
    save_checkpoint(
        &args.checkpoint_dir,
        prefix,
        "orbit",
        &guard,
        tot_moves,
        elapsed,
        args.seed,
        &format!(
            "starters={}_const={}_orb_unc={}_pol_moves={}",
            num_starters, const_rows, best_orb_unc, pol_moves
        ),
    );
    println!(
        "[orbit] FINAL SUMMARY N={} ({} starters + {} const): best_uncovered={} (cyclic_unc={}), total_moves={} (orb={}, pol={}), elapsed={:.2}s",
        target_n,
        num_starters,
        const_rows,
        guard.uncovered,
        best_orb_unc * v,
        tot_moves,
        orb_moves,
        pol_moves,
        elapsed
    );
    Ok(())
}

fn main() {
    let args = match parse_args() {
        Ok(a) => a,
        Err(msg) => {
            eprintln!("{}", msg);
            std::process::exit(2);
        }
    };

    let res = match args.mode.as_str() {
        "sanity" => run_sanity(&args),
        "reduce" => run_reduce(&args),
        "extend" => run_extend(&args),
        "orbit" => run_orbit(&args),
        other => Err(format!("unknown mode '{}'", other)),
    };

    if let Err(e) = res {
        eprintln!("ERROR: {}", e);
        std::process::exit(1);
    }
}
