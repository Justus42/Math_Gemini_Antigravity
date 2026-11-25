mod pgl;
mod search;

use std::env;
use std::path::PathBuf;
use std::process;

fn print_usage() {
    eprintln!(
        "pgl_ccl_search — Zero-dep PGL(2,q) + General Binary CCL Covering Array Solver (t=3)\n\
         \n\
         Subcommands:\n\
           selftest\n\
             Verify GF(5), GF(9), GF(11), PGL(2,q) sharp 3-transitivity, and oriented pairs.\n\
         \n\
           search --v <6|10|12> --k <K> --m <M> --time-limit-secs <SEC> [options]\n\
             --cover-const            Require 000 or 111 on mixed triples (saves v const rows)\n\
             --threads <N>            Worker threads (default: 2)\n\
             --seed <U64>             Base RNG seed (default: 42)\n\
             --restart-steps <U64>    Stale steps before restart (default: 200000)\n\
             --out-matrix <PATH>      Save best/solved M x k binary matrix\n\
             --out-array <PATH>       If solved (unc==0), expand full CA to canonical .txt\n\
             --checkpoint <PATH>      Checkpoint file for best binary matrix\n\
             --resume <PATH>          Warm-start from a saved binary matrix (auto-trims if rows > M)\n\
             --quiet                  Suppress progress lines on stderr\n\
         \n\
           expand --v <6|10|12> --k <K> --in-matrix <PATH> --out-array <PATH> [--cover-const]\n\
             Verify a saved M x k binary CCL matrix and expand it to a canonical CA .txt file."
    );
}

fn next_arg(args: &[String], i: &mut usize, flag: &str) -> String {
    *i += 1;
    if *i >= args.len() {
        eprintln!("Missing value for {flag}");
        process::exit(2);
    }
    args[*i].clone()
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_usage();
        process::exit(2);
    }

    // Always run PGL(2,q) and oriented-pair unit tests at startup (< 5 ms)
    pgl::run_pgl_selftests();

    match args[1].as_str() {
        "selftest" => {
            println!("SELFTEST PASS: GF(5)/PGL(2,5) [120], GF(9)/PGL(2,9) [720], GF(11)/PGL(2,11) [1320], oriented pairs OK.");
        }
        "search" => {
            let mut v: Option<usize> = None;
            let mut k: Option<usize> = None;
            let mut m: Option<usize> = None;
            let mut time_limit_secs: Option<f64> = None;
            let mut cover_const = false;
            let mut threads: usize = 2;
            let mut seed: u64 = 42;
            let mut restart_stale_steps: u64 = 200_000;
            let mut out_matrix: Option<PathBuf> = None;
            let mut out_array: Option<PathBuf> = None;
            let mut checkpoint_path: Option<PathBuf> = None;
            let mut resume_path: Option<PathBuf> = None;
            let mut verbose = true;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--v" => v = Some(next_arg(&args, &mut i, "--v").parse().expect("invalid --v")),
                    "--k" => k = Some(next_arg(&args, &mut i, "--k").parse().expect("invalid --k")),
                    "--m" => m = Some(next_arg(&args, &mut i, "--m").parse().expect("invalid --m")),
                    "--time-limit-secs" => {
                        time_limit_secs = Some(
                            next_arg(&args, &mut i, "--time-limit-secs")
                                .parse()
                                .expect("invalid --time-limit-secs"),
                        )
                    }
                    "--cover-const" => cover_const = true,
                    "--threads" => {
                        threads = next_arg(&args, &mut i, "--threads")
                            .parse()
                            .expect("invalid --threads")
                    }
                    "--seed" => {
                        seed = next_arg(&args, &mut i, "--seed")
                            .parse()
                            .expect("invalid --seed")
                    }
                    "--restart-steps" => {
                        restart_stale_steps = next_arg(&args, &mut i, "--restart-steps")
                            .parse()
                            .expect("invalid --restart-steps")
                    }
                    "--out-matrix" => out_matrix = Some(PathBuf::from(next_arg(&args, &mut i, "--out-matrix"))),
                    "--out-array" => out_array = Some(PathBuf::from(next_arg(&args, &mut i, "--out-array"))),
                    "--checkpoint" => checkpoint_path = Some(PathBuf::from(next_arg(&args, &mut i, "--checkpoint"))),
                    "--resume" => resume_path = Some(PathBuf::from(next_arg(&args, &mut i, "--resume"))),
                    "--quiet" => verbose = false,
                    other => {
                        eprintln!("Unknown argument: {other}");
                        process::exit(2);
                    }
                }
                i += 1;
            }

            let v = v.expect("Missing required --v (6, 10, or 12)");
            let k = k.expect("Missing required --k");
            let m = m.expect("Missing required --m");
            let time_limit_secs = time_limit_secs.expect("Missing required --time-limit-secs");
            assert!(
                matches!(v, 6 | 10 | 12),
                "Unsupported v={v}; supported: 6, 10, 12"
            );
            let q = v - 1;
            assert!(k <= 2 * q, "k={k} exceeds 2*q={} for v={v}", 2 * q);

            let resume_rows = resume_path.as_ref().map(|p| {
                search::load_matrix_file(p, k).unwrap_or_else(|e| {
                    eprintln!("Failed to load --resume {:?}: {}", p, e);
                    process::exit(2);
                })
            });

            let target_n = pgl::total_rows(v, m, cover_const);
            let cfg = search::SearchConfig {
                k,
                m,
                cover_const,
                time_limit_secs,
                threads,
                seed,
                restart_stale_steps,
                checkpoint_path,
                resume_rows,
                verbose,
            };

            let res = search::run_search(&cfg);
            let mv_s = if res.elapsed_secs > 0.0 {
                (res.total_moves as f64) / res.elapsed_secs
            } else {
                0.0
            };

            if let Some(ref mp) = out_matrix {
                search::save_matrix_file(mp, k, m, cover_const, res.best_unc, &res.best_rows)
                    .expect("Failed to write --out-matrix");
            }

            if res.solved {
                if let Some(ref ap) = out_array {
                    let written = pgl::expand_to_file(v, k, &res.best_rows, cover_const, ap)
                        .expect("Failed to expand CA to --out-array");
                    assert_eq!(written, target_n);
                }
            }

            println!(
                "RESULT status={} v={} k={} M={} cover_const={} N={} best_unc={} elapsed={:.3}s moves={} mv_s={:.0} restarts={} seed={}",
                if res.solved { "SOLVED" } else { "UNSOLVED" },
                v,
                k,
                m,
                cover_const,
                target_n,
                res.best_unc,
                res.elapsed_secs,
                res.total_moves,
                mv_s,
                res.total_restarts,
                seed
            );

            if !res.solved {
                process::exit(1);
            }
        }
        "expand" => {
            let mut v: Option<usize> = None;
            let mut k: Option<usize> = None;
            let mut cover_const = false;
            let mut in_matrix: Option<PathBuf> = None;
            let mut out_array: Option<PathBuf> = None;

            let mut i = 2;
            while i < args.len() {
                match args[i].as_str() {
                    "--v" => v = Some(next_arg(&args, &mut i, "--v").parse().expect("invalid --v")),
                    "--k" => k = Some(next_arg(&args, &mut i, "--k").parse().expect("invalid --k")),
                    "--cover-const" => cover_const = true,
                    "--in-matrix" => in_matrix = Some(PathBuf::from(next_arg(&args, &mut i, "--in-matrix"))),
                    "--out-array" => out_array = Some(PathBuf::from(next_arg(&args, &mut i, "--out-array"))),
                    other => {
                        eprintln!("Unknown argument: {other}");
                        process::exit(2);
                    }
                }
                i += 1;
            }

            let v = v.expect("Missing --v");
            let k = k.expect("Missing --k");
            let in_matrix = in_matrix.expect("Missing --in-matrix");
            let out_array = out_array.expect("Missing --out-array");

            let rows = search::load_matrix_file(&in_matrix, k).expect("Failed to read --in-matrix");
            let m = rows.len();
            let prob = search::Problem::new(k, m, cover_const);
            let unc = search::verify_binary_ccl(&prob, &rows);
            if unc != 0 {
                eprintln!("Matrix {:?} is NOT a valid binary CCL solution (unc={})", in_matrix, unc);
                process::exit(1);
            }
            let written = pgl::expand_to_file(v, k, &rows, cover_const, &out_array)
                .expect("Failed to expand CA");
            println!(
                "EXPANDED v={} k={} M={} cover_const={} N={} -> {}",
                v,
                k,
                m,
                cover_const,
                written,
                out_array.display()
            );
        }
        _ => {
            print_usage();
            process::exit(2);
        }
    }
}
