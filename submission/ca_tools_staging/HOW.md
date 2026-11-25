Construction: Building on group-action strength-3 constructions (Chateauneuf-Colbourn-Kreher 1999; Chateauneuf-Kreher 2002; Meagher-Stevens 2005), binary pair-expansion constructions (Cohen-Colbourn-Ling 2008), and tabu search (Nurmela 2004): two deterministic sharply 3-transitive PGL(2, q) orbits (2 * q(q^2 - 1) rows, covering all 3-distinct tuples, pure-block constant tuples, and one 2-symbol pattern per mixed triple) combined with a general (non-self-complementary) binary M x k covering matrix expanded over all v(v - 1)/2 oriented symbol pairs (directed Hamiltonian cycle plus remaining pairs u < w, eliminating all v constant rows whenever 000 or 111 appears on every mixed triple). Binary matrices were found by a zero-dependency Rust hybrid Tabu-CW / PAWS local search. [LITERATURE_ATTRIBUTION_TBD: finalize exact prior-art attribution from written review in docs/.]

Built from: nothing (all 13 arrays are built from scratch over GF(q) and binary local search; no existing table arrays and no Torres-Jimenez arrays were used as starts or ingredients).

Program: https://github.com/Justus42/Math_Gemini_Antigravity (zero-dependency Rust `std`-only solver `solvers/pgl_ccl_search`, commit `[FINAL_MAIN_COMMIT_TBD]`). Exact binary starter matrices C(M, k) are stored in `data/ccl_binary/` (68 KB total) and deterministically expand to bit-identical copies of all 13 submitted arrays (verified 13/13 SHA-256 matches, see `submission/REPRODUCE.md`):
- `cargo build --release --manifest-path solvers/pgl_ccl_search/Cargo.toml`
- `solvers/pgl_ccl_search/target/release/pgl_ccl_search selftest` (verifies field axioms, group order |PGL(2,q)| = q(q^2-1), and sharp 3-transitivity for q in {5, 9, 11, 13, 16, 17, 19})
- `solvers/pgl_ccl_search/target/release/pgl_ccl_search expand --q <q> --in-bin data/ccl_binary/ccl_k<k>_m<M>_cc<0|1>.bin [--cover-const|--no-cover-const] --out-ca CA_<N>_3_<k>_<v>.txt`
Search seeds and exact run parameters for every array are logged in `docs/RUN_LOG.md` and `results/VERIFICATION_LOG_pgl_ccl.md`.

AI tools used: yes
Tools: Gemini and Google Antigravity (solver implementation and binary CCL search sweeps); independent cross-check/review by Claude. All arrays passed exhaustive dual verification (`ca_verify.c` and standalone `verify_independent.py`).

Submitter: [REAL_NAME_TBD], [AFFILIATION_TBD] (contact email sent to chrispbsmolen@gmail.com / [EMAIL_TBD]; ORCID: [ORCID_OPTIONAL]). Released under CC BY 4.0.
