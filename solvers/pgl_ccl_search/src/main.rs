mod ccl;
mod pgl;
mod postop;

use std::env;
use std::path::PathBuf;
use std::process;
use std::sync::Arc;
use std::time::Instant;

use ccl::{load_bin_matrix, run_search, save_bin_matrix, self_test_ccl, CclProblem, SearchAlgo};
use pgl::{expand_and_write_ca, expand_ca_rows, oriented_pairs, self_test_pgl2, write_ca_rows};
use postop::{greedy_row_delete, load_ca_rows, repair_and_complete};

fn usage() -> ! {
    eprintln!("Usage:");
    eprintln!("  pgl_ccl_search selftest");
    eprintln!("  pgl_ccl_search search --k <k> --m <M> [--q <5|9|11|13>] [--cover-const]");
    eprintln!("                        --time-limit-secs <f64> [--threads <N>] [--seed <u64>]");
    eprintln!("                        [--algo <hybrid|tabu-cw|paws>] [--out-bin <path>]");
    eprintln!("                        [--out-best-bin <path>] [--out-ca <path>]");
    eprintln!("                        [--checkpoint <path>] [--resume <path>]");
    eprintln!("  pgl_ccl_search expand --q <5|9|11|13> --in-bin <path> [--cover-const] --out-ca <path>");
    eprintln!("  pgl_ccl_search reduce --v <v> --in-ca <path> --out-ca <path>");
    eprintln!("  pgl_ccl_search complete --q <5|9|11|13> --in-bin <path> [--cover-const]");
    eprintln!("                          --max-n <N> --time-limit-secs <f64> --out-ca <path>");
    process::exit(2);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        usage();
    }

    match args[1].as_str() {
        "selftest" => {
            for &q in &[5usize, 9, 11, 13] {
                let perms = self_test_pgl2(q);
                let pairs = oriented_pairs(q + 1);
                println!(
                    "PASS PGL(2,{:2}): |G|={:4}, 2|G|={:4}, v={:2}, pairs={:2}",
                    q,
                    perms.len(),
                    2 * perms.len(),
                    q + 1,
                    pairs.len()
                );
            }
            self_test_ccl();
            println!("PASS CCL incremental vs scratch self-test");
        }
        "search" => {
            let mut k: Option<usize> = None;
            let mut m: Option<usize> = None;
            let mut q: Option<usize> = None;
            let mut cover_const = false;
            let mut time_limit_secs: Option<f64> = None;
            let mut threads: usize = 2;
            let mut seed: u64 = 42;
            let mut algo = SearchAlgo::Hybrid;
            let mut out_bin: Option<PathBuf> = None;
            let mut out_best_bin: Option<PathBuf> = None;
            let mut out_ca: Option<PathBuf> = None;
            let mut checkpoint: Option<PathBuf> = None;
            let mut resume: Option<PathBuf> = None;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--k" => {
                        i += 1;
                        k = Some(args[i].parse().expect("Invalid --k"));
                    }
                    "--m" => {
                        i += 1;
                        m = Some(args[i].parse().expect("Invalid --m"));
                    }
                    "--q" => {
                        i += 1;
                        q = Some(args[i].parse().expect("Invalid --q"));
                    }
                    "--cover-const" => {
                        cover_const = true;
                    }
                    "--time-limit-secs" => {
                        i += 1;
                        time_limit_secs = Some(args[i].parse().expect("Invalid --time-limit-secs"));
                    }
                    "--threads" => {
                        i += 1;
                        threads = args[i].parse().expect("Invalid --threads");
                    }
                    "--seed" => {
                        i += 1;
                        seed = args[i].parse().expect("Invalid --seed");
                    }
                    "--algo" => {
                        i += 1;
                        algo = match args[i].as_str() {
                            "hybrid" => SearchAlgo::Hybrid,
                            "tabu-cw" => SearchAlgo::TabuCw,
                            "paws" => SearchAlgo::Paws,
                            other => panic!("Unknown --algo {}", other),
                        };
                    }
                    "--out-bin" => {
                        i += 1;
                        out_bin = Some(PathBuf::from(&args[i]));
                    }
                    "--out-best-bin" => {
                        i += 1;
                        out_best_bin = Some(PathBuf::from(&args[i]));
                    }
                    "--out-ca" => {
                        i += 1;
                        out_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--checkpoint" => {
                        i += 1;
                        checkpoint = Some(PathBuf::from(&args[i]));
                    }
                    "--resume" => {
                        i += 1;
                        resume = Some(PathBuf::from(&args[i]));
                    }
                    other => {
                        eprintln!("Unknown option: {}", other);
                        usage();
                    }
                }
                i += 1;
            }

            let k = k.expect("--k is required");
            let m = m.expect("--m is required");
            let time_limit_secs = time_limit_secs.expect("--time-limit-secs is required");
            if out_ca.is_some() && q.is_none() {
                panic!("--q is required when --out-ca is specified");
            }
            if let Some(qv) = q {
                let _ = self_test_pgl2(qv);
            }

            let init_resume = resume.map(|p| {
                let (rk, rm, _, mat) = load_bin_matrix(&p).expect("Failed to load --resume");
                assert_eq!((rk, rm), (k, m), "Resume dimensions mismatch");
                mat
            });

            let prob = Arc::new(CclProblem::new(k, m, cover_const));
            let res = run_search(
                Arc::clone(&prob),
                algo,
                threads,
                seed,
                time_limit_secs,
                init_resume,
                checkpoint,
            );

            let mv_s = if res.elapsed_secs > 0.0 {
                (res.total_moves as f64) / res.elapsed_secs
            } else {
                0.0
            };

            let n_str = if let Some(qv) = q {
                let v = qv + 1;
                let n = 2 * qv * (qv * qv - 1) + m * v * (v - 1) / 2 + if cover_const { 0 } else { v };
                format!(" q={} v={} N={}", qv, v, n)
            } else {
                String::new()
            };

            println!(
                "RESULT k={} m={} cover_const={}{} algo={:?} threads={} seed={} best_unc={} req_slots={} elapsed={:.3}s moves={} mv_s={:.0} restarts={}",
                k,
                m,
                cover_const as u8,
                n_str,
                algo,
                threads,
                seed,
                res.best_unc,
                prob.total_req_slots,
                res.elapsed_secs,
                res.total_moves,
                mv_s,
                res.total_restarts
            );

            if let Some(ref p) = out_best_bin {
                save_bin_matrix(p, k, m, cover_const, res.best_unc, &res.best_mat)
                    .expect("Failed to write --out-best-bin");
                println!("WROTE_BEST_BIN {} unc={}", p.display(), res.best_unc);
            }

            if res.best_unc == 0 {
                if let Some(ref p) = out_bin {
                    save_bin_matrix(p, k, m, cover_const, 0, &res.best_mat)
                        .expect("Failed to write --out-bin");
                    println!("WROTE_BIN {}", p.display());
                }
                if let Some(ref p) = out_ca {
                    let qv = q.unwrap();
                    let n = expand_and_write_ca(qv, k, m, &res.best_mat, cover_const, p)
                        .expect("Failed to expand CA");
                    println!("WROTE_CA {} N={} t=3 k={} v={}", p.display(), n, k, qv + 1);
                }
                process::exit(0);
            } else {
                process::exit(1);
            }
        }
        "expand" => {
            let mut q: Option<usize> = None;
            let mut in_bin: Option<PathBuf> = None;
            let mut out_ca: Option<PathBuf> = None;
            let mut cover_const_override: Option<bool> = None;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--q" => {
                        i += 1;
                        q = Some(args[i].parse().expect("Invalid --q"));
                    }
                    "--in-bin" => {
                        i += 1;
                        in_bin = Some(PathBuf::from(&args[i]));
                    }
                    "--out-ca" => {
                        i += 1;
                        out_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--cover-const" => {
                        cover_const_override = Some(true);
                    }
                    "--no-cover-const" => {
                        cover_const_override = Some(false);
                    }
                    other => {
                        eprintln!("Unknown option: {}", other);
                        usage();
                    }
                }
                i += 1;
            }

            let q = q.expect("--q is required");
            let in_bin = in_bin.expect("--in-bin is required");
            let out_ca = out_ca.expect("--out-ca is required");
            let (k, m, header_cc, mat) = load_bin_matrix(&in_bin).expect("Failed to load --in-bin");
            let cover_const = cover_const_override.or(header_cc).unwrap_or(false);
            let prob = CclProblem::new(k, m, cover_const);
            let unc = prob.verify_from_scratch(&mat);
            assert_eq!(
                unc, 0,
                "Binary matrix {} is NOT valid for k={} m={} cover_const={}: unc={}",
                in_bin.display(),
                k,
                m,
                cover_const,
                unc
            );
            let n = expand_and_write_ca(q, k, m, &mat, cover_const, &out_ca)
                .expect("Failed to expand CA");
            println!(
                "EXPANDED {} -> {} (N={} t=3 k={} v={} m={} cover_const={})",
                in_bin.display(),
                out_ca.display(),
                n,
                k,
                q + 1,
                m,
                cover_const as u8
            );
        }
        "reduce" => {
            let mut v: Option<usize> = None;
            let mut in_ca: Option<PathBuf> = None;
            let mut out_ca: Option<PathBuf> = None;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--v" => {
                        i += 1;
                        v = Some(args[i].parse().expect("Invalid --v"));
                    }
                    "--in-ca" => {
                        i += 1;
                        in_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--out-ca" => {
                        i += 1;
                        out_ca = Some(PathBuf::from(&args[i]));
                    }
                    other => {
                        eprintln!("Unknown option: {}", other);
                        usage();
                    }
                }
                i += 1;
            }
            let v = v.expect("--v is required");
            let in_ca = in_ca.expect("--in-ca is required");
            let out_ca = out_ca.expect("--out-ca is required");

            let t0 = Instant::now();
            let rows = load_ca_rows(&in_ca, v).expect("Failed to load --in-ca");
            let orig_n = rows.len();
            let k = rows[0].len();
            let reduced = greedy_row_delete(&rows, v);
            let new_n = reduced.len();
            write_ca_rows(&reduced, &out_ca).expect("Failed to write --out-ca");
            println!(
                "REDUCED {} -> {} (k={} v={} N: {} -> {}, saved={}, elapsed={:.3}s)",
                in_ca.display(),
                out_ca.display(),
                k,
                v,
                orig_n,
                new_n,
                orig_n - new_n,
                t0.elapsed().as_secs_f64()
            );
        }
        "complete" => {
            let mut q: Option<usize> = None;
            let mut in_bin: Option<PathBuf> = None;
            let mut out_ca: Option<PathBuf> = None;
            let mut max_n: Option<usize> = None;
            let mut time_limit_secs: Option<f64> = None;
            let mut cover_const_override: Option<bool> = None;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--q" => {
                        i += 1;
                        q = Some(args[i].parse().expect("Invalid --q"));
                    }
                    "--in-bin" => {
                        i += 1;
                        in_bin = Some(PathBuf::from(&args[i]));
                    }
                    "--out-ca" => {
                        i += 1;
                        out_ca = Some(PathBuf::from(&args[i]));
                    }
                    "--max-n" => {
                        i += 1;
                        max_n = Some(args[i].parse().expect("Invalid --max-n"));
                    }
                    "--time-limit-secs" => {
                        i += 1;
                        time_limit_secs = Some(args[i].parse().expect("Invalid --time-limit-secs"));
                    }
                    "--cover-const" => {
                        cover_const_override = Some(true);
                    }
                    "--no-cover-const" => {
                        cover_const_override = Some(false);
                    }
                    other => {
                        eprintln!("Unknown option: {}", other);
                        usage();
                    }
                }
                i += 1;
            }
            let q = q.expect("--q is required");
            let in_bin = in_bin.expect("--in-bin is required");
            let out_ca = out_ca.expect("--out-ca is required");
            let max_n = max_n.expect("--max-n is required");
            let time_limit_secs = time_limit_secs.expect("--time-limit-secs is required");

            let t0 = Instant::now();
            let (k, m, header_cc, mat) = load_bin_matrix(&in_bin).expect("Failed to load --in-bin");
            let cover_const = cover_const_override.or(header_cc).unwrap_or(true);
            let v = q + 1;
            let rows = expand_ca_rows(q, k, m, &mat, cover_const);
            let base_n = rows.len();
            let (done_rows, init_unc, repairs, final_unc) =
                repair_and_complete(rows, v, max_n, time_limit_secs);
            let final_n = done_rows.len();
            println!(
                "COMPLETE q={} v={} k={} m={} cc={} base_N={} init_unc_tuples={} zero_break_repairs={} final_N={} final_unc={} elapsed={:.3}s",
                q,
                v,
                k,
                m,
                cover_const as u8,
                base_n,
                init_unc,
                repairs,
                final_n,
                final_unc,
                t0.elapsed().as_secs_f64()
            );
            if final_unc == 0 {
                write_ca_rows(&done_rows, &out_ca).expect("Failed to write --out-ca");
                println!("WROTE_CA {} N={} t=3 k={} v={}", out_ca.display(), final_n, k, v);
                process::exit(0);
            } else {
                process::exit(1);
            }
        }
        _ => usage(),
    }
}
