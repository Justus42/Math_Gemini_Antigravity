mod io;
mod orbit;
mod proj_orbit;
mod rng;
mod search;
mod state;

use io::{
    delete_row, project_drop_col, read_matrix, write_matrix_atomic, write_meta_atomic,
    CheckpointMeta,
};
use orbit::{orbit_sanity_test, search_orbit, OrbitGroup, OrbitSearchConfig, OrbitState, SearchAlgo};
use proj_orbit::{
    proj_sanity_test, search_proj_tabu_cw, ProjGroup, ProjOrbitState, ProjSearchConfig,
};
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
    algo: SearchAlgo,
    stage2_algo: Option<SearchAlgo>,
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
    t_start: f64,
    t_end: f64,
    full_scan_thresh: Option<usize>,
    log_interval: f64,
    drop_col: Option<String>,
    probe_secs: f64,
    stage1_frac: f64,
    stage1_secs: Option<f64>,
    group: OrbitGroup,
    proj_group: Option<ProjGroup>,
    gen_starters: Option<usize>,
    bin_starters: Option<usize>,
    restart_stag: u64,
    const_rows: Option<usize>,
    free_rows: usize,
    orbit_secs: Option<f64>,
    free_stage1_secs: Option<f64>,
    unfreeze_frac: f64,
}

fn parse_algo(s: &str) -> Result<SearchAlgo, String> {
    match s.to_lowercase().as_str() {
        "tabu-cw" | "tabu_cw" | "tabucw" => Ok(SearchAlgo::TabuCw),
        "sa" => Ok(SearchAlgo::Sa),
        "hybrid-sa-cw" | "hybrid_sa_cw" => Ok(SearchAlgo::HybridSaCw),
        other => Err(format!(
            "unknown algo '{}', expected tabu-cw, sa, or hybrid-sa-cw",
            other
        )),
    }
}

fn parse_args() -> Result<Args, String> {
    let raw: Vec<String> = env::args().collect();
    if raw.len() < 2 || raw[1] == "-h" || raw[1] == "--help" {
        return Err(
            "Usage: ca3_search <sanity|reduce|extend|orbit|hybrid> [options]\n\
             Common: --algo <tabu-cw|sa|hybrid-sa-cw> --stage2-algo <algo> \
             --v <5> --k <9> --n <N> --min-n <N> --threads <2> --seed <42> \
             --time-limit-secs <60> --checkpoint-dir <dir> --prefix <name> \
             --no-weights --noise <0.002> --t-start <0.55> --t-end <0.16> \
             --full-scan-thresh <N> --log-interval <30>\n\
             reduce: --input <file> [--drop-col <idx|all>] [--probe-secs <1.5>] [--resume <file>]\n\
             extend: --input <file> --n <target_n> [--stage1-secs <90>] [--min-n <N>]\n\
             orbit:  --group <z5|g10|agl5|pgl25|psl25> --n <orbit_n> --k <k> --v <v> [--const-rows <0|v>] \
                     [--gen-starters <A>] [--bin-starters <B>] [--restart-stag <1000000>] \
                     [--orbit-secs <f64>] [--free-rows <0>] [--free-stage1-secs <f64>]\n\
             hybrid: --input <file> --v <5> --free-rows <R> [--stage1-secs <60>] [--min-n <N>]"
                .to_string(),
        );
    }

    let mut args = Args {
        mode: raw[1].clone(),
        algo: SearchAlgo::TabuCw,
        stage2_algo: None,
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
        noise: 0.002,
        t_start: 0.55,
        t_end: 0.16,
        full_scan_thresh: None,
        log_interval: 30.0,
        drop_col: None,
        probe_secs: 1.5,
        stage1_frac: 0.25,
        stage1_secs: None,
        group: OrbitGroup::Zv,
        proj_group: None,
        gen_starters: None,
        bin_starters: None,
        restart_stag: 1_000_000,
        const_rows: None,
        free_rows: 0,
        orbit_secs: None,
        free_stage1_secs: None,
        unfreeze_frac: 0.0,
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
            "--algo" => args.algo = parse_algo(&next_val(&mut i)?)?,
            "--stage2-algo" => args.stage2_algo = Some(parse_algo(&next_val(&mut i)?)?),
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
            "--t-start" => {
                args.t_start = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--t-start: {}", e))?
            }
            "--t-end" => {
                args.t_end = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--t-end: {}", e))?
            }
            "--full-scan-thresh" | "--endgame" => {
                args.full_scan_thresh = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--full-scan-thresh: {}", e))?,
                )
            }
            "--log-interval" => {
                args.log_interval = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--log-interval: {}", e))?
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
            "--stage1-secs" => {
                args.stage1_secs = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--stage1-secs: {}", e))?,
                )
            }
            "--group" => {
                let g = next_val(&mut i)?.to_lowercase();
                match g.as_str() {
                    "z5" | "zv" => {
                        args.group = OrbitGroup::Zv;
                        args.proj_group = None;
                    }
                    "g10" | "g2v" => {
                        args.group = OrbitGroup::G2v;
                        args.proj_group = None;
                    }
                    "agl5" | "agl" => {
                        args.group = OrbitGroup::Agl;
                        args.proj_group = None;
                    }
                    "pgl25" | "pgl" => {
                        args.proj_group = Some(ProjGroup::Pgl25);
                        args.v = 6;
                    }
                    "psl25" | "psl" => {
                        args.proj_group = Some(ProjGroup::Psl25);
                        args.v = 6;
                    }
                    other => {
                        return Err(format!(
                            "unknown --group '{}', expected z5, g10, agl5, pgl25, or psl25",
                            other
                        ))
                    }
                }
            }
            "--gen-starters" => {
                args.gen_starters = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--gen-starters: {}", e))?,
                )
            }
            "--bin-starters" => {
                args.bin_starters = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--bin-starters: {}", e))?,
                )
            }
            "--restart-stag" => {
                args.restart_stag = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--restart-stag: {}", e))?
            }
            "--const-rows" => {
                args.const_rows = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--const-rows: {}", e))?,
                )
            }
            "--free-rows" => {
                args.free_rows = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--free-rows: {}", e))?
            }
            "--orbit-secs" => {
                args.orbit_secs = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--orbit-secs: {}", e))?,
                )
            }
            "--free-stage1-secs" => {
                args.free_stage1_secs = Some(
                    next_val(&mut i)?
                        .parse()
                        .map_err(|e| format!("--free-stage1-secs: {}", e))?,
                )
            }
            "--unfreeze-frac" => {
                args.unfreeze_frac = next_val(&mut i)?
                    .parse()
                    .map_err(|e| format!("--unfreeze-frac: {}", e))?
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

fn thread_tenure_range(tid: usize) -> (u32, u32) {
    if tid % 2 == 0 {
        (7, 10)
    } else {
        (12, 16)
    }
}

fn thread_algo(algo: SearchAlgo, tid: usize) -> SearchAlgo {
    match algo {
        SearchAlgo::HybridSaCw => {
            if tid % 2 == 0 {
                SearchAlgo::TabuCw
            } else {
                SearchAlgo::Sa
            }
        }
        other => other,
    }
}

fn pick_min_excl_row(state: &CaState, rng: &mut Rng) -> (usize, usize) {
    let excl = state.row_exclusivities();
    let mut order: Vec<(usize, usize)> = excl.into_iter().enumerate().collect();
    order.sort_by_key(|&(_, e)| e);
    let min_e = order[0].1;
    let tied_count = order.iter().take_while(|&&(_, e)| e == min_e).count();
    order[rng.gen_usize(tied_count)]
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
    println!("=== SANITY CHECK (t=3, k={}, v={}, algo=tabu-cw) ===", args.k, args.v);
    let (mat, n, k, v) = if let Some(ref path) = args.input {
        let lm = read_matrix(path)?;
        let (m, k_use) = if lm.k == args.k + 1 {
            (project_drop_col(&lm.mat, lm.n, lm.k, 1), args.k)
        } else {
            (lm.mat, lm.k)
        };
        let st = CaState::from_matrix(m.clone(), lm.n, k_use, args.v);
        let mut rng = Rng::from_seed(args.seed);
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
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
        "[PASS] CaState(tabu-cw) 10,000-move incremental check: 0 discrepancies | throughput = {:.0} moves/sec | unc: {} -> {}",
        ca_mps, start_unc, end_unc
    );

    let (z5_mps, z5_unc, z5_n) = orbit_sanity_test(OrbitGroup::Zv, k, v, 35, true)?;
    println!(
        "[PASS] OrbitState(Z5/tabu-cw, 35+5 -> N={}) 10,000-move incremental + 5x expansion check: 0 discrepancies | throughput = {:.0} moves/sec | best_unc_orbits = {}",
        z5_n, z5_mps, z5_unc
    );

    if v % 2 == 1 && v >= 3 {
        let (g10_mps, g10_unc, g10_n) = orbit_sanity_test(OrbitGroup::G2v, k, v, 17, true)?;
        println!(
            "[PASS] OrbitState(G10/tabu-cw, 17+5 -> N={}) 10,000-move incremental + 10x expansion check: 0 discrepancies | throughput = {:.0} moves/sec | best_unc_orbits = {}",
            g10_n, g10_mps, g10_unc
        );
    }
    if v == 5 {
        let (agl_mps, agl_unc, agl_n) = orbit_sanity_test(OrbitGroup::Agl, 8, v, 8, true)?;
        println!(
            "[PASS] OrbitState(AGL5/tabu-cw, k=8, 8+5 -> N={}) 10,000-move incremental + 20x expansion check: 0 discrepancies | throughput = {:.0} moves/sec | best_unc_orbits = {}",
            agl_n, agl_mps, agl_unc
        );
    }

    let (pgl_mps, pgl_unc, pgl_exp, pgl_n) = proj_sanity_test(ProjGroup::Pgl25, 2, 3, 9, true)?;
    println!(
        "[PASS] ProjOrbit(PGL25/tabu-cw, k=9, A=2 B=3 +6 -> N={}) 10,000-move incremental + weighted expansion (120*D+30*2sym) check: 0 discrepancies | throughput = {:.0} moves/sec | best_orb={} (exp={})",
        pgl_n, pgl_mps, pgl_unc, pgl_exp
    );

    let (psl_mps, psl_unc, psl_exp, psl_n) = proj_sanity_test(ProjGroup::Psl25, 4, 3, 9, true)?;
    println!(
        "[PASS] ProjOrbit(PSL25/tabu-cw, k=9, A=4 B=3 +6 -> N={}) 10,000-move incremental + weighted expansion (60*(D1+D2)+30*2sym) check: 0 discrepancies | throughput = {:.0} moves/sec | best_orb={} (exp={})",
        psl_n, psl_mps, psl_unc, psl_exp
    );
    Ok(())
}

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
    let full_thresh = args.full_scan_thresh.unwrap_or(80);

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

            for tid in 0..args.threads {
                let mat_clone = cur_mat.clone();
                let solved_c = Arc::clone(&solved_flag);
                let gb_c = Arc::clone(&gb);
                let tm_c = Arc::clone(&total_moves_all);
                let ckpt_dir = args.checkpoint_dir.clone();
                let pfx = prefix.to_string();
                let ext = extra_label.to_string();
                let seed_t = thread_seed(args.seed ^ (cur_n as u64 * 1009), tid);
                let base_seed = args.seed;
                let (tmin, tmax) = thread_tenure_range(tid);
                let algo_t = thread_algo(args.algo, tid);

                let cfg = SearchConfig {
                    algo: algo_t,
                    tenure_min: tmin,
                    tenure_max: tmax,
                    noise_prob: args.noise,
                    use_weights: args.use_weights,
                    t_start: args.t_start,
                    t_end: args.t_end,
                    full_scan_thresh: full_thresh,
                    lock_rows: 0,
                    lock_cols: 0,
                    log_interval_secs: args.log_interval,
                    label: format!("reduce-N{}:t={}", cur_n, tid),
                };

                handles.push(thread::spawn(move || {
                    let mut rng = Rng::from_seed(seed_t);
                    let mut state = CaState::from_matrix(mat_clone, cur_n, k, v);
                    if tid > 0 && state.uncovered() > 0 {
                        for _ in 0..2 {
                            let r = rng.gen_usize(cur_n);
                            let c = rng.gen_usize(k);
                            let nv = rng.gen_usize(v) as u8;
                            state.apply_move(r, c, nv);
                        }
                    }
                    let mut last_reported = 0u64;
                    let res = search_ca(
                        &mut state,
                        &mut rng,
                        &cfg,
                        deadline,
                        &solved_c,
                        None,
                        |new_unc, best_m, cur_m| {
                            let dm = cur_m - last_reported;
                            last_reported = cur_m;
                            tm_c.fetch_add(dm, Ordering::Relaxed);

                            let mut guard = gb_c.lock().unwrap();
                            if new_unc < guard.uncovered {
                                guard.uncovered = new_unc;
                                guard.mat.copy_from_slice(best_m);
                                guard.best_thread = tid;
                                guard.best_seed = seed_t;
                                let elapsed = t_start.elapsed().as_secs_f64();
                                if new_unc == 0 {
                                    solved_c.store(true, Ordering::Relaxed);
                                }
                                if new_unc == 0
                                    || guard.last_write.elapsed() >= Duration::from_secs(2)
                                {
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
                    tm_c.fetch_add(res.moves - last_reported, Ordering::Relaxed);
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
            let st = CaState::from_matrix(solved_mat.clone(), cur_n, k, v);
            let mut rng = Rng::from_seed(args.seed ^ (cur_n as u64 * 31337));
            let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
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
        let min_n = args.min_n.unwrap_or(lm.n.saturating_sub(4));
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
        let full_thresh = args.full_scan_thresh.unwrap_or(80);
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
            let (tmin, tmax) = thread_tenure_range(tid);
            let cfg = SearchConfig {
                algo: SearchAlgo::TabuCw,
                tenure_min: tmin,
                tenure_max: tmax,
                noise_prob: args.noise,
                use_weights: args.use_weights,
                t_start: args.t_start,
                t_end: args.t_end,
                full_scan_thresh: full_thresh,
                lock_rows: 0,
                lock_cols: 0,
                log_interval_secs: 0.0,
                label: "probe".to_string(),
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
                        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
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
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
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
    let stage1_secs = args
        .stage1_secs
        .unwrap_or(args.time_limit_secs * args.stage1_frac.clamp(0.0, 0.9));
    let stage1_deadline = (t_start + Duration::from_secs_f64(stage1_secs)).min(deadline);
    let full_thresh = args.full_scan_thresh.unwrap_or(80);
    let stage2_algo = args.stage2_algo.unwrap_or(args.algo);

    println!(
        "[extend] Base {} ({}x{}, v={}) -> target CA({}; 3, {}, {}) (+{} repair rows) | s1={:.1}s ({:?}), s2={:.1}s ({:?}, full_scan<={}), T_sa: {:.2}->{:.2}, threads={}",
        input_path.display(),
        n_base,
        k_base,
        v,
        target_n,
        k,
        v,
        repair_rows,
        stage1_secs,
        args.algo,
        (args.time_limit_secs - stage1_secs).max(0.0),
        stage2_algo,
        full_thresh,
        args.t_start,
        args.t_end,
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
    }));

    let base_mat = Arc::new(lm.mat);

    // Phase 1: Stage 1 (locked base n_base x k_base; optimize col k-1 of base rows + all cols of repair rows)
    let mut s1_handles = Vec::with_capacity(args.threads);
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
        let (tmin, tmax) = thread_tenure_range(tid);
        let noise = args.noise;
        let algo1 = thread_algo(args.algo, tid);
        let t_s = args.t_start;
        let t_e = args.t_end;
        let log_int = args.log_interval;

        s1_handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut state =
                CaState::build_extended_greedy(&bm_c, n_base, k_base, target_n, v, &mut rng);
            let init_unc = state.uncovered();
            println!(
                "  [extend-s1:t={}] Greedy init uncovered={} (seed={}, tenure={}..{})",
                tid, init_unc, seed_t, tmin, tmax
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

            if !solved_c.load(Ordering::Relaxed) && Instant::now() < stage1_deadline {
                let cfg1 = SearchConfig {
                    algo: algo1,
                    tenure_min: tmin,
                    tenure_max: tmax,
                    noise_prob: noise,
                    use_weights,
                    t_start: t_s,
                    t_end: t_e,
                    full_scan_thresh: full_thresh,
                    lock_rows: n_base,
                    lock_cols: k_base,
                    log_interval_secs: log_int,
                    label: format!("extend-s1:t={}", tid),
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
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2)
                            {
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
                    "  [extend-s1:t={}] Done: best_unc={} (60s={}, last@{:.1}s), moves={}, smoothings={}",
                    tid,
                    res1.best_uncovered,
                    res1.best_at_60s,
                    res1.last_improve_sec,
                    res1.moves,
                    res1.reheats
                );
            }
        }));
    }
    for h in s1_handles {
        let _ = h.join();
    }

    let (s1_best_unc, s1_best_mat) = {
        let guard = gb.lock().unwrap();
        (guard.uncovered, guard.mat.clone())
    };
    println!(
        "[extend] Stage 1 SUMMARY: best_unc={} at {:.1}s -> unfreezing full {}x{} array!",
        s1_best_unc,
        t_start.elapsed().as_secs_f64(),
        target_n,
        k
    );

    // Phase 2: Stage 2 (unfreeze entire target_n x k array, starting from best Stage 1 matrix!)
    if !solved_flag.load(Ordering::Relaxed) && Instant::now() < deadline {
        let s1_arc = Arc::new(s1_best_mat);
        let mut s2_handles = Vec::with_capacity(args.threads);

        for tid in 0..args.threads {
            let s1_c = Arc::clone(&s1_arc);
            let solved_c = Arc::clone(&solved_flag);
            let gb_c = Arc::clone(&gb);
            let tm_c = Arc::clone(&total_moves);
            let ckpt_dir = args.checkpoint_dir.clone();
            let pfx = prefix.to_string();
            let seed_t = thread_seed(args.seed ^ 0x5A5A_1234, tid);
            let base_seed = args.seed;
            let use_weights = args.use_weights;
            let (tmin, tmax) = thread_tenure_range(tid);
            let noise = args.noise;
            let algo2 = thread_algo(stage2_algo, tid);
            let t_s = args.t_start;
            let t_e = args.t_end;
            let log_int = args.log_interval;

            s2_handles.push(thread::spawn(move || {
                let mut rng = Rng::from_seed(seed_t);
                let mut state = CaState::from_matrix((*s1_c).clone(), target_n, k, v);
                let algo_tag = match algo2 {
                    SearchAlgo::TabuCw => "tabu-cw",
                    SearchAlgo::Sa | SearchAlgo::HybridSaCw => "sa->tabu-cw",
                };
                println!(
                    "  [extend-s2:t={}] Starting unfrozen {}x{} (algo={}, tenure={}..{}, start_unc={})",
                    tid,
                    target_n,
                    k,
                    algo_tag,
                    tmin,
                    tmax,
                    state.uncovered()
                );

                let cfg2 = SearchConfig {
                    algo: algo2,
                    tenure_min: tmin,
                    tenure_max: tmax,
                    noise_prob: noise,
                    use_weights,
                    t_start: t_s,
                    t_end: t_e,
                    full_scan_thresh: full_thresh,
                    lock_rows: 0,
                    lock_cols: 0,
                    log_interval_secs: log_int,
                    label: format!("extend-s2({}):t={}", algo_tag, tid),
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
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2)
                            {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    "extend",
                                    &guard,
                                    tm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    &format!("stage=2_free_algo={}", algo_tag),
                                );
                            }
                        }
                    },
                );
                tm_c.fetch_add(res2.moves - last_m, Ordering::Relaxed);
                println!(
                    "  [extend-s2({}):t={}] Done: best_unc={} (s2@60s={}, s2@120s={}, last@{:.1}s), moves={}, smoothings={}",
                    algo_tag,
                    tid,
                    res2.best_uncovered,
                    res2.best_at_60s,
                    res2.best_at_120s,
                    res2.last_improve_sec,
                    res2.moves,
                    res2.reheats
                );
            }));
        }
        for h in s2_handles {
            let _ = h.join();
        }
    }

    let (final_unc, final_mat) = {
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
            &format!("base={}_r={}_s1unc={}", n_base, repair_rows, s1_best_unc),
        );
        println!(
            "[extend] SUMMARY N={}: best_uncovered={} (after s1={}), total_moves={} ({:.0} moves/sec), elapsed={:.2}s",
            target_n,
            guard.uncovered,
            s1_best_unc,
            tot,
            tot as f64 / elapsed.max(1e-9),
            elapsed
        );
        (guard.uncovered, guard.mat.clone())
    };

    // If solved and min_n < target_n and time remains, automatically reduce toward min_n!
    let min_n = args.min_n.unwrap_or(target_n);
    if final_unc == 0 && target_n > min_n && Instant::now() < deadline {
        let st = CaState::from_matrix(final_mat.clone(), target_n, k, v);
        let mut rng = Rng::from_seed(args.seed ^ 0xBEEF_9999);
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
        println!(
            "[extend] SOLVED N={}! Deleting row {} (min_excl={}) and reducing toward min_n={}...",
            target_n, del_r, min_e, min_n
        );
        let next_mat = delete_row(&final_mat, target_n, k, del_r);
        let next_prefix = format!("{}_reduced", prefix);
        run_reduce_multithread(
            next_mat,
            target_n - 1,
            k,
            v,
            min_n,
            args,
            t_start,
            deadline,
            &next_prefix,
            &format!("from_extend_N{}", target_n),
        )?;
    }
    Ok(())
}

fn run_hybrid_from_matrix(
    base_mat: Vec<u8>,
    n_base: usize,
    k: usize,
    v: usize,
    free_rows: usize,
    stage1_secs: f64,
    args: &Args,
    t_start: Instant,
    deadline: Instant,
    prefix: &str,
    mode_tag: &str,
    extra_base: &str,
    prior_moves: u64,
) -> Result<(usize, u64), String> {
    let target_n = n_base + free_rows;
    let now = Instant::now();
    let stage1_deadline = (now + Duration::from_secs_f64(stage1_secs.max(0.0))).min(deadline);
    let base_check = CaState::from_matrix(base_mat.clone(), n_base, k, v);
    let base_unc = base_check.uncovered();
    let full_thresh = args.full_scan_thresh.unwrap_or(80);

    println!(
        "[{}] Starting Hybrid {}x{} (unc={}) + {} greedy free rows -> N={} | stage1={:.1}s, remaining={:.1}s, threads={}",
        mode_tag,
        n_base,
        k,
        base_unc,
        free_rows,
        target_n,
        stage1_secs,
        deadline.saturating_duration_since(now).as_secs_f64(),
        args.threads
    );

    let solved_flag = Arc::new(AtomicBool::new(false));
    let hybrid_moves = Arc::new(AtomicU64::new(0));
    let gb = Arc::new(Mutex::new(GlobalBest {
        n: target_n,
        k,
        v,
        uncovered: usize::MAX,
        mat: vec![0u8; target_n * k],
        best_thread: 0,
        best_seed: args.seed,
        last_write: Instant::now() - Duration::from_secs(60),
    }));

    let bm_arc = Arc::new(base_mat);
    let mut handles = Vec::with_capacity(args.threads);

    for tid in 0..args.threads {
        let bm_c = Arc::clone(&bm_arc);
        let solved_c = Arc::clone(&solved_flag);
        let gb_c = Arc::clone(&gb);
        let hm_c = Arc::clone(&hybrid_moves);
        let ckpt_dir = args.checkpoint_dir.clone();
        let pfx = prefix.to_string();
        let mtag = mode_tag.to_string();
        let ext = extra_base.to_string();
        let seed_t = thread_seed(args.seed ^ 0x517C_C1B7, tid);
        let base_seed = args.seed;
        let use_weights = args.use_weights;
        let (tmin, tmax) = thread_tenure_range(tid);
        let algo_t = thread_algo(args.algo, tid);
        let noise = args.noise;
        let t_s = args.t_start;
        let t_e = args.t_end;
        let log_int = args.log_interval;

        handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut state = CaState::append_greedy_rows(&bm_c, n_base, k, v, free_rows, &mut rng);
            let init_unc = state.uncovered();
            println!(
                "  [{}:t={}] After appending {} greedy free rows: unc={} -> {}",
                mtag, tid, free_rows, base_unc, init_unc
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
                            &mtag,
                            &guard,
                            prior_moves + hm_c.load(Ordering::Relaxed),
                            t_start.elapsed().as_secs_f64(),
                            base_seed,
                            &format!("{}_stage=greedy_init", ext),
                        );
                    }
                }
            }

            if free_rows > 0 && !solved_c.load(Ordering::Relaxed) && Instant::now() < stage1_deadline
            {
                let cfg1 = SearchConfig {
                    algo: algo_t,
                    tenure_min: tmin,
                    tenure_max: tmax,
                    noise_prob: noise,
                    use_weights,
                    t_start: t_s,
                    t_end: t_e,
                    full_scan_thresh: full_thresh,
                    lock_rows: n_base,
                    lock_cols: k,
                    log_interval_secs: log_int,
                    label: format!("{}-s1:t={}", mtag, tid),
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
                        hm_c.fetch_add(dm, Ordering::Relaxed);
                        let mut guard = gb_c.lock().unwrap();
                        if new_unc < guard.uncovered {
                            guard.uncovered = new_unc;
                            guard.mat.copy_from_slice(best_m);
                            guard.best_thread = tid;
                            guard.best_seed = seed_t;
                            if new_unc == 0 {
                                solved_c.store(true, Ordering::Relaxed);
                            }
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2)
                            {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    &mtag,
                                    &guard,
                                    prior_moves + hm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    &format!("{}_stage=1_free_only", ext),
                                );
                            }
                        }
                    },
                );
                hm_c.fetch_add(res1.moves - last_m, Ordering::Relaxed);
            }

            if !solved_c.load(Ordering::Relaxed) && Instant::now() < deadline {
                {
                    let guard = gb_c.lock().unwrap();
                    if guard.uncovered < state.uncovered() {
                        state.mat.copy_from_slice(&guard.mat);
                        state.recompute_counts();
                    }
                }
                state.reset_weights();
                let cfg2 = SearchConfig {
                    algo: algo_t,
                    tenure_min: tmin,
                    tenure_max: tmax,
                    noise_prob: noise,
                    use_weights,
                    t_start: t_s,
                    t_end: t_e,
                    full_scan_thresh: full_thresh,
                    lock_rows: 0,
                    lock_cols: 0,
                    log_interval_secs: log_int,
                    label: format!("{}-s2:t={}", mtag, tid),
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
                        hm_c.fetch_add(dm, Ordering::Relaxed);
                        let mut guard = gb_c.lock().unwrap();
                        if new_unc < guard.uncovered {
                            guard.uncovered = new_unc;
                            guard.mat.copy_from_slice(best_m);
                            guard.best_thread = tid;
                            guard.best_seed = seed_t;
                            if new_unc == 0 {
                                solved_c.store(true, Ordering::Relaxed);
                            }
                            if new_unc == 0 || guard.last_write.elapsed() >= Duration::from_secs(2)
                            {
                                guard.last_write = Instant::now();
                                save_checkpoint(
                                    &ckpt_dir,
                                    &pfx,
                                    &mtag,
                                    &guard,
                                    prior_moves + hm_c.load(Ordering::Relaxed),
                                    t_start.elapsed().as_secs_f64(),
                                    base_seed,
                                    &format!("{}_stage=2_unfreeze", ext),
                                );
                            }
                        }
                    },
                );
                hm_c.fetch_add(res2.moves - last_m, Ordering::Relaxed);
            }
        }));
    }

    for h in handles {
        let _ = h.join();
    }

    let (best_unc, best_mat) = {
        let guard = gb.lock().unwrap();
        let elapsed = t_start.elapsed().as_secs_f64();
        let hm = hybrid_moves.load(Ordering::Relaxed);
        save_checkpoint(
            &args.checkpoint_dir,
            prefix,
            mode_tag,
            &guard,
            prior_moves + hm,
            elapsed,
            args.seed,
            &format!("{}_free={}_base_unc={}", extra_base, free_rows, base_unc),
        );
        (guard.uncovered, guard.mat.clone())
    };
    let hm = hybrid_moves.load(Ordering::Relaxed);

    let min_n = args.min_n.unwrap_or(target_n);
    if best_unc == 0 && target_n > min_n && Instant::now() < deadline {
        let st = CaState::from_matrix(best_mat.clone(), target_n, k, v);
        let mut rng = Rng::from_seed(args.seed ^ 0xBEEF_9999);
        let (del_r, min_e) = pick_min_excl_row(&st, &mut rng);
        println!(
            "[{}] SOLVED N={}! Deleting row {} (min_excl={}) -> reducing toward min_n={}...",
            mode_tag, target_n, del_r, min_e, min_n
        );
        let next_mat = delete_row(&best_mat, target_n, k, del_r);
        let next_prefix = format!("{}_reduced", prefix);
        run_reduce_multithread(
            next_mat,
            target_n - 1,
            k,
            v,
            min_n,
            args,
            t_start,
            deadline,
            &next_prefix,
            &format!("from_{}_N{}", mode_tag, target_n),
        )?;
    }

    Ok((best_unc, hm))
}

fn run_hybrid(args: &Args) -> Result<(), String> {
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or("hybrid");
    let input_path = args
        .input
        .as_ref()
        .ok_or_else(|| "hybrid mode requires --input <matrix_file>".to_string())?;
    let lm = read_matrix(input_path)?;
    let stage1_secs = args
        .stage1_secs
        .unwrap_or(args.time_limit_secs * args.stage1_frac.clamp(0.0, 0.8));

    let (best_unc, hm) = run_hybrid_from_matrix(
        lm.mat,
        lm.n,
        lm.k,
        args.v,
        args.free_rows,
        stage1_secs,
        args,
        t_start,
        deadline,
        prefix,
        "hybrid",
        &format!("input={}", input_path.display()),
        0,
    )?;
    let elapsed = t_start.elapsed().as_secs_f64();
    println!(
        "[hybrid] FINAL SUMMARY N={}: best_uncovered={}, moves={} ({:.0} moves/sec), elapsed={:.2}s",
        lm.n + args.free_rows,
        best_unc,
        hm,
        hm as f64 / elapsed.max(1e-9),
        elapsed
    );
    Ok(())
}

fn run_proj_orbit(args: &Args, group: ProjGroup) -> Result<(), String> {
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or(group.name());
    let k = args.k;
    let const_rows = args.const_rows.unwrap_or(6);
    if const_rows != 0 && const_rows != 6 {
        return Err(format!("--const-rows must be 0 or 6 for {}", group.name()));
    }
    let has_const = const_rows == 6;
    let num_gen = args.gen_starters.unwrap_or(match group {
        ProjGroup::Pgl25 => 2,
        ProjGroup::Psl25 => 4,
    });
    let num_bin = args.bin_starters.unwrap_or(3);
    let target_n = num_gen * group.order() + num_bin * 30 + const_rows;
    if let Some(req_n) = args.n {
        if req_n != target_n {
            return Err(format!(
                "mismatch: --n {} != |{}|*A({}) + 30*B({}) + const({}) = {}",
                req_n,
                group.name(),
                num_gen,
                num_bin,
                const_rows,
                target_n
            ));
        }
    }
    let full_thresh = args.full_scan_thresh.unwrap_or(500);
    let num_vars = (num_gen + num_bin) * k;

    println!(
        "[proj:{}] Target CA({}; 3, {}, 6): A={} gen (|G|={}) + B={} bin (30) + {} const ({} vars) | algo=TabuCw(BASE_W=16..26), full_scan<={}, restart_stag={}, time={:.1}s, threads={}",
        group.name(),
        target_n,
        k,
        num_gen,
        group.order(),
        num_bin,
        const_rows,
        num_vars,
        full_thresh,
        args.restart_stag,
        args.time_limit_secs,
        args.threads
    );

    let solved_flag = Arc::new(AtomicBool::new(false));
    let total_moves = Arc::new(AtomicU64::new(0));
    let num_s = num_gen + num_bin;

    let best_proj: Arc<Mutex<(usize, usize, Vec<u8>, usize, u64, usize, usize, f64)>> = Arc::new(
        Mutex::new((
            usize::MAX,
            usize::MAX,
            vec![0u8; num_s * k],
            0,
            args.seed,
            usize::MAX,
            usize::MAX,
            0.0,
        )),
    );

    let mut handles = Vec::with_capacity(args.threads);
    for tid in 0..args.threads {
        let solved_c = Arc::clone(&solved_flag);
        let bp_c = Arc::clone(&best_proj);
        let tm_c = Arc::clone(&total_moves);
        let seed_t = thread_seed(args.seed, tid);
        let (tmin, tmax) = thread_tenure_range(tid);
        let cfg = ProjSearchConfig {
            tenure_min: tmin,
            tenure_max: tmax,
            noise_prob: args.noise,
            full_scan_thresh: full_thresh,
            restart_stagnation: args.restart_stag,
            base_seed: seed_t,
            log_interval_secs: args.log_interval,
            thread_id: tid,
        };

        handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut st = ProjOrbitState::new_random(group, num_gen, num_bin, k, has_const, &mut rng);
            let res = search_proj_tabu_cw(&mut st, &mut rng, &cfg, deadline, &solved_c, None);
            tm_c.fetch_add(res.moves, Ordering::Relaxed);
            println!(
                "  [proj-{}:t={}] Done (tenure={}..{}): best_orb={} (60s={}, 120s={}, last@{:.1}s, exp_unc={}), moves={}, smoothings={}, restarts={}",
                group.name(),
                tid,
                tmin,
                tmax,
                res.best_uncovered_orbits,
                res.best_at_60s,
                res.best_at_120s,
                res.last_improve_sec,
                res.best_expanded_uncovered,
                res.moves,
                res.smoothings,
                res.restarts
            );
            let mut guard = bp_c.lock().unwrap();
            if res.best_at_60s < guard.5 {
                guard.5 = res.best_at_60s;
            }
            if res.best_at_120s < guard.6 {
                guard.6 = res.best_at_120s;
            }
            if res.best_uncovered_orbits < guard.0
                || (res.best_uncovered_orbits == guard.0
                    && res.best_expanded_uncovered < guard.1)
            {
                guard.0 = res.best_uncovered_orbits;
                guard.1 = res.best_expanded_uncovered;
                guard.2 = res.best_starters;
                guard.3 = tid;
                guard.4 = seed_t;
                guard.7 = res.last_improve_sec;
                if res.best_uncovered_orbits == 0 {
                    solved_c.store(true, Ordering::Relaxed);
                }
            }
        }));
    }
    for h in handles {
        let _ = h.join();
    }

    let (best_orb, best_exp_pred, best_starters, best_tid, best_seed_t, best_60, best_120, last_imp) =
        best_proj.lock().unwrap().clone();
    let elapsed = t_start.elapsed().as_secs_f64();
    let tot_moves = total_moves.load(Ordering::Relaxed);

    let final_st = ProjOrbitState::from_starters(group, best_starters, num_gen, num_bin, k, has_const);
    let expanded_ca = final_st.expand_exact_to_ca();
    let exp_unc = expanded_ca.uncovered();
    debug_assert_eq!(exp_unc, best_exp_pred);

    println!(
        "[proj:{}] SUMMARY CA({}; 3, {}, 6) [A={} B={} +{}]: best_orb={} (60s={}, 120s={}, last@{:.1}s, exp_unc={}), moves={} ({:.0} moves/sec), elapsed={:.2}s",
        group.name(),
        target_n,
        k,
        num_gen,
        num_bin,
        const_rows,
        best_orb,
        best_60,
        best_120,
        last_imp,
        exp_unc,
        tot_moves,
        tot_moves as f64 / elapsed.max(1e-9),
        elapsed
    );

    let gb = GlobalBest {
        n: target_n,
        k,
        v: 6,
        uncovered: exp_unc,
        mat: expanded_ca.mat,
        best_thread: best_tid,
        best_seed: best_seed_t,
        last_write: Instant::now(),
    };
    save_checkpoint(
        &args.checkpoint_dir,
        prefix,
        &format!("proj_{}", group.name()),
        &gb,
        tot_moves,
        elapsed,
        args.seed,
        &format!(
            "group={}_A={}_B={}_const={}_orb={}_60s={}_120s={}_last={:.1}s",
            group.name(),
            num_gen,
            num_bin,
            const_rows,
            best_orb,
            best_60,
            best_120,
            last_imp
        ),
    );
    Ok(())
}

fn run_orbit(args: &Args) -> Result<(), String> {
    if let Some(pg) = args.proj_group {
        return run_proj_orbit(args, pg);
    }
    let t_start = Instant::now();
    let deadline = t_start + Duration::from_secs_f64(args.time_limit_secs);
    let prefix = args.prefix.as_deref().unwrap_or("orbit");
    let k = args.k;
    let v = args.v;
    let group = args.group;
    let orb_sz = group.orbit_size(v);
    let const_rows = args.const_rows.unwrap_or(v);
    if const_rows != 0 && const_rows != v {
        return Err(format!("--const-rows must be 0 or v={}", v));
    }
    let has_const = const_rows == v;
    let orbit_n = args.n.unwrap_or(match group {
        OrbitGroup::Agl => 165,
        OrbitGroup::G2v => 175,
        OrbitGroup::Zv => 180,
    });
    if orbit_n < const_rows || (orbit_n - const_rows) % orb_sz != 0 {
        return Err(format!(
            "orbit_n={} must equal num_starters * {} + const_rows({}) for group {}",
            orbit_n,
            orb_sz,
            const_rows,
            group.name()
        ));
    }
    let num_starters = (orbit_n - const_rows) / orb_sz;
    let full_thresh = args.full_scan_thresh.unwrap_or(match group {
        OrbitGroup::Agl | OrbitGroup::G2v => 35,
        OrbitGroup::Zv => 45,
    });

    let orbit_secs = if let Some(os) = args.orbit_secs {
        os.min(args.time_limit_secs)
    } else if args.free_rows > 0 || args.unfreeze_frac > 0.0 {
        let u_frac = if args.unfreeze_frac > 0.0 {
            args.unfreeze_frac
        } else {
            0.30
        };
        args.time_limit_secs * (1.0 - u_frac.clamp(0.0, 0.9))
    } else {
        args.time_limit_secs
    };
    let orbit_deadline = (t_start + Duration::from_secs_f64(orbit_secs)).min(deadline);

    println!(
        "[orbit:{}] Target CA({}; 3, {}, {}): {} starters (orb_sz={}) + {} const rows | algo={:?}, full_scan<={}, restart_stag={}, orbit={:.1}s, threads={}",
        group.name(),
        orbit_n,
        k,
        v,
        num_starters,
        orb_sz,
        const_rows,
        args.algo,
        full_thresh,
        args.restart_stag,
        orbit_secs,
        args.threads
    );

    let solved_flag = Arc::new(AtomicBool::new(false));
    let total_orbit_moves = Arc::new(AtomicU64::new(0));

    let best_orbit: Arc<Mutex<(usize, Vec<u8>, usize, u64, usize, usize, f64)>> = Arc::new(
        Mutex::new((
            usize::MAX,
            vec![0u8; num_starters * k],
            0,
            args.seed,
            usize::MAX,
            usize::MAX,
            0.0,
        )),
    );

    let mut handles = Vec::with_capacity(args.threads);
    for tid in 0..args.threads {
        let solved_c = Arc::clone(&solved_flag);
        let bo_c = Arc::clone(&best_orbit);
        let om_c = Arc::clone(&total_orbit_moves);
        let seed_t = thread_seed(args.seed, tid);
        let (tmin, tmax) = thread_tenure_range(tid);
        let algo_t = thread_algo(args.algo, tid);

        let cfg = OrbitSearchConfig {
            algo: algo_t,
            tenure_min: tmin,
            tenure_max: tmax,
            noise_prob: args.noise,
            use_weights: args.use_weights,
            t_start: args.t_start,
            t_end: args.t_end,
            full_scan_thresh: full_thresh,
            restart_stagnation: args.restart_stag,
            base_seed: seed_t,
            log_interval_secs: args.log_interval,
            thread_id: tid,
        };

        handles.push(thread::spawn(move || {
            let mut rng = Rng::from_seed(seed_t);
            let mut st = OrbitState::new_random(group, num_starters, k, v, has_const, &mut rng);
            let res = search_orbit(&mut st, &mut rng, &cfg, orbit_deadline, &solved_c, None);
            om_c.fetch_add(res.moves, Ordering::Relaxed);
            println!(
                "  [orbit-{}:t={}] Done (tenure={}..{}): best_orb={} (60s={}, 120s={}, last@{:.1}s, exp_unc={}), moves={}, smoothings={}",
                group.name(),
                tid,
                tmin,
                tmax,
                res.best_uncovered_orbits,
                res.best_at_60s,
                res.best_at_120s,
                res.last_improve_sec,
                res.best_uncovered_orbits * orb_sz,
                res.moves,
                res.reheats
            );
            let mut guard = bo_c.lock().unwrap();
            if res.best_at_60s < guard.4 {
                guard.4 = res.best_at_60s;
            }
            if res.best_at_120s < guard.5 {
                guard.5 = res.best_at_120s;
            }
            if res.best_uncovered_orbits < guard.0 {
                guard.0 = res.best_uncovered_orbits;
                guard.1 = res.best_starters;
                guard.2 = tid;
                guard.3 = seed_t;
                guard.6 = res.last_improve_sec;
                if res.best_uncovered_orbits == 0 {
                    solved_c.store(true, Ordering::Relaxed);
                }
            }
        }));
    }
    for h in handles {
        let _ = h.join();
    }

    let (best_orb_unc, best_starters, best_tid, best_seed_orb, best_60, best_120, last_imp) =
        best_orbit.lock().unwrap().clone();
    let orb_elapsed = t_start.elapsed().as_secs_f64();
    let orb_moves = total_orbit_moves.load(Ordering::Relaxed);

    let orb_state = OrbitState::from_starters(group, best_starters, num_starters, k, v, has_const);
    let expanded_ca = orb_state.expand_exact_to_ca();
    let exp_unc = expanded_ca.uncovered();

    println!(
        "[orbit:{}] ORBIT SUMMARY N={}: best_orb={} (60s={}, 120s={}, last@{:.1}s, exp_unc={}), moves={} ({:.0} moves/sec), elapsed={:.2}s",
        group.name(),
        orbit_n,
        best_orb_unc,
        best_60,
        best_120,
        last_imp,
        exp_unc,
        orb_moves,
        orb_moves as f64 / orb_elapsed.max(1e-9),
        orb_elapsed
    );

    let gb_orb = GlobalBest {
        n: orbit_n,
        k,
        v,
        uncovered: exp_unc,
        mat: expanded_ca.mat.clone(),
        best_thread: best_tid,
        best_seed: best_seed_orb,
        last_write: Instant::now(),
    };
    save_checkpoint(
        &args.checkpoint_dir,
        prefix,
        &format!("orbit_{}", group.name()),
        &gb_orb,
        orb_moves,
        orb_elapsed,
        args.seed,
        &format!(
            "group={}_algo={:?}_starters={}_const={}_orb_unc={}_60s={}_120s={}_last={:.1}s",
            group.name(),
            args.algo,
            num_starters,
            const_rows,
            best_orb_unc,
            best_60,
            best_120,
            last_imp
        ),
    );

    if exp_unc == 0 {
        return Ok(());
    }

    let rem_secs = deadline
        .saturating_duration_since(Instant::now())
        .as_secs_f64();
    if rem_secs > 1.0 && (args.free_rows > 0 || args.unfreeze_frac > 0.0) {
        let f_s1 = args
            .free_stage1_secs
            .unwrap_or(if args.free_rows > 0 { rem_secs * 0.25 } else { 0.0 });
        let hyb_prefix = if args.free_rows > 0 {
            format!("{}_hybrid_N{}", prefix, orbit_n + args.free_rows)
        } else {
            format!("{}_unfreeze", prefix)
        };
        let (final_unc, hyb_moves) = run_hybrid_from_matrix(
            expanded_ca.mat,
            orbit_n,
            k,
            v,
            args.free_rows,
            f_s1,
            args,
            t_start,
            deadline,
            &hyb_prefix,
            &format!("orbit_{}_hybrid", group.name()),
            &format!("group={}_orb_unc={}", group.name(), best_orb_unc),
            orb_moves,
        )?;
        let tot_elapsed = t_start.elapsed().as_secs_f64();
        let tot_moves = orb_moves + hyb_moves;
        println!(
            "[orbit:{}] FINAL HYBRID SUMMARY N={}: orbit_unc={} -> final_unc={}, total_moves={} ({:.0} moves/sec), elapsed={:.2}s",
            group.name(),
            orbit_n + args.free_rows,
            exp_unc,
            final_unc,
            tot_moves,
            tot_moves as f64 / tot_elapsed.max(1e-9),
            tot_elapsed
        );
    }
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
        "hybrid" => run_hybrid(&args),
        other => Err(format!("unknown mode '{}'", other)),
    };

    if let Err(e) = res {
        eprintln!("ERROR: {}", e);
        std::process::exit(1);
    }
}
