Construction: Refinement of the coset-lift framework of Colbourn, Keri, Rivas Soriano, and Schlage-Puchta (2010, Lemma 3.3, `fuse-ckrs2010`, which uses `q^2 + q(q - 1) - 1` cosets of size `q^(t - 2)` by doubling column `infty` of the Bush orthogonal array and placing all `q(q - 1)` auxiliary blocks at `(0, 0)`). Here, for any prime power `q`, strength `2 <= t <= q + 2`, column count `k = q + 2`, and alphabet size `2 <= v <= q`, we take `m` cosets of the kernel code `K_t` of degree `<= t - 3` polynomials over `GF(q)` (identified with `{0, ..., q - 1}` in base `p` via the lexicographically smallest monic irreducible polynomial over `GF(p)`). Each coset representative `(c, d, a, b)` with `c, d in GF(q)` and `a, b in {0, ..., v - 1}` generates `q^(t - 2)` rows `(pi(P(0)), ..., pi(P(q - 1)), a, b)`, where `P(x) = a_0 + ... + a_{t - 3} x^(t - 3) + c x^(t - 2) + d x^(t - 1)` runs over `(a_0, ..., a_{t - 3}) in GF(q)^(t - 2)` and `pi(z) = z` for `z < v`, `pi(z) = 0` for `z >= v` (identity when `v = q`). Letting both extra columns `a` and `b` vary freely over the affine plane of `(c, d)` reduces the strength-`t` coverage condition to a mixed-level strength-2 condition on the `m x (q + 2)` representative table `M(R)` with columns `(c + alpha * d)_{alpha in GF(q)}, a, b` (see the proof document at https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/PHASE7_T2_REDUCTION.md and the `v = q` proof at https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/GENERAL_TQV_PROOF.md).

This submission consists of 37 arrays (total size below 200 MiB, every file below 50 MiB), all strictly smaller than `chrispbsmolen/ca-tools` at commit `e673ab45758a3959710c662a34837f79f6add689` (`2026-11-26T06:17:26Z`, checked against `ca_table.csv.gz`, `ca_frame.csv`, `derived.csv`, `withdrawn_files.csv`, and open PRs `#89` and `#90`). No novelty claim is made. The 37 arrays fall into two classes:

1. Closed-form representative lists (23 arrays, deterministic, no search):
   For `k = q + 2`, `2 <= v <= q`, and `2 <= t <= q + 2`, setting `w = max(0, 2v - q)` and `n = v - w` gives a closed-form representative list of size `m = q^2 + C(w, 2)` and array size `N = (q^2 + C(max(0, 2v - q), 2)) * q^(t - 2)`. Partitioning the horizontal lines `d = const` of `GF(q)^2`:
   - `d < w`: base label `(a, b) = (d, d)`, replaced at points `c < d` by the two representatives `(d, c)` and `(c, d)` (`C(w, 2)` extra rows).
   - `w <= d < w + n`: `a = d`, `b = pi(c)`.
   - `w + n <= d < w + 2n`: `b = d - n`, `a = pi(c)`.
   - `d >= w + 2n` (only when `v < q / 2`): `(a, b) = (0, 0)`.
   This produces:
   - 17 arrays with `v < q` (`q in {11, 13, 16, 17, 19, 23, 25}`) generated deterministically via `phase7_reps_vq.py` and lifted via `phase7_lift.py --v`.
   - 6 arrays with `v = q`, `q in {13, 17, 19}` (where `w = q` and `m = q^2 + C(q, 2)`) generated deterministically via `gen_general_tqv.py`.

2. CP-SAT representative lists (14 arrays for `v = q`, `q in {5, 7, 8, 9, 11}`):
   Using the exact strength-2 integer formulation on `M(R)` (`q^4` Boolean variables), Google OR-Tools CP-SAT `9.15` (`phase7_solve_cpsat.py`, `num_search_workers = 2`, `random_seed = 1`, wall-clock limit `300 s` for `q in {5, 7, 8, 9}` and `1800 s` for `q = 11`, non-deterministic search because of multi-worker wall-clock termination) found representative lists strictly smaller than `q^2 + C(q, 2)`:
   - `q = 5`: `m = 34` (vs. 35) -> 1 array (`t = 5`).
   - `q = 7`: `m = 68` (vs. 70) -> 3 arrays (`t = 4, 5, 6`).
   - `q = 8`: `m = 91` (vs. 92) -> 3 arrays (`t = 4, 5, 6`).
   - `q = 9`: `m = 116` (vs. 117) -> 4 arrays (`t = 3, 4, 5, 6`).
   - `q = 11`: `m = 175` (vs. 176) -> 3 arrays (`t = 3, 4, 5`).
   Optimality of `m` is open in all five cases. Starting from the five archived fixed representative lists, lifting to all 14 submitted arrays via `phase7_lift.py` is 100% deterministic and byte-reproducible.

Built from: nothing as starting arrays or ingredients (all 37 arrays are built from scratch over `GF(q)`; no existing table arrays and no Torres-Jimenez arrays were used as starts or ingredients). Conceptual and published foundations:
- Bush (1952, `oa-bush1952`): orthogonal arrays `OA(q^t; t, q + 1, q)` via polynomial evaluation over `GF(q)`.
- Colbourn, Keri, Rivas Soriano, and Schlage-Puchta (2010, `fuse-ckrs2010`): Theorem 3.2 and Lemma 3.3 (direct predecessor for the coset-lift framework with `q^2 + q(q - 1) - 1` blocks).
- Bai (2026, `polychrome-bai2026`, `doi:10.5281/zenodo.23787051`, and data deposit `doi:10.5281/zenodo.23787055`): line-polychromatic colourings of `AG(2, q)` and reduced-alphabet bounds in this family.
- Sitjar (2026, `pgl-s2026`, `doi:10.5281/zenodo.23842218`): coset-union framework of Lemma 1 and `CA(825; 4, 7, 5)` as the starting point of the coset analysis that motivated the strength-2 reduction (`CA(825; 4, 7, 5)` lies on a different linear code and was not used as a starting array).

Program: Repository https://github.com/Justus42/Math_Gemini_Antigravity pinned at commit `666f76729372908a8b981878a164e414210eca84` (pure Python 3 standard library only for all deterministic generators and lifters; Google OR-Tools `9.15` was used only to discover the five fixed CP-SAT representative lists). No code files are included in this submission folder. All scripts and fixed representative lists are linked below at the pinned commit:
- Closed-form `v = q` generator (`gen_general_tqv.py`): https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/scripts/gen_general_tqv.py
- Closed-form `v <= q` representative list generator (`phase7_reps_vq.py`): https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/scripts/phase7_reps_vq.py
- Deterministic strength-`t` coset lifter (`phase7_lift.py`): https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/scripts/phase7_lift.py
- CP-SAT strength-2 search script (`phase7_solve_cpsat.py`, OR-Tools `9.15`): https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/scripts/phase7_solve_cpsat.py
- Fixed CP-SAT representative lists:
  * `R_q5_m34.txt`: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/data/phase7/R_q5_m34.txt
  * `R_q7_m68.txt`: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/data/phase7/R_q7_m68.txt
  * `R_q8_m91.txt`: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/data/phase7/R_q8_m91.txt
  * `R_q9_m116.txt`: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/data/phase7/R_q9_m116.txt
  * `R_q11_m175.txt`: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/data/phase7/R_q11_m175.txt

Exact deterministic regeneration commands (with the linked Python scripts and representative lists placed in the working directory):
- For the 17 closed-form `v < q` arrays:
  `python3 phase7_reps_vq.py <q> <v> R_q<q>_v<v>.txt && python3 phase7_lift.py --q <q> --v <v> --reps R_q<q>_v<v>.txt --check-m --t <t> --out CA_<N>_<t>_<k>_<v>.txt`
- For the 6 closed-form `v = q` (`q >= 13`) arrays:
  `python3 gen_general_tqv.py --t <t> --q <q> --v <v> --out CA_<N>_<t>_<k>_<v>.txt`
- For the 14 CP-SAT representative-list arrays:
  `python3 phase7_lift.py --q <q> --reps R_q<q>_m<m>.txt --check-m --t <t> --out CA_<N>_<t>_<k>_<v>.txt`

Documentation, verification logs, and run logs at the pinned commit:
- Reduction and closed-form proof note: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/PHASE7_T2_REDUCTION.md
- `v = q` proof note: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/GENERAL_TQV_PROOF.md
- Literature review note: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/LITERATURE_CHECK_PHASE7_VQ.md
- Complete run log: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/docs/RUN_LOG.md
- Verification logs: https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/results/phase7/VERIFICATION_LOG.md , https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/results/phase7_vq/VERIFICATION_LOG.md , https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/results/general_tqv/VERIFICATION_LOG.md , https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/results/t4_nearbush/VERIFICATION_LOG.md

AI tools used: yes
Extent of AI use: The mathematical analysis, the Python scripts, the CP-SAT runs, the verification runs, and the text of this submission were produced by AI systems (Gemini, Claude, and Antigravity). The submitter has no formal training in combinatorics. He directed the project, approved each step, and takes responsibility for the submission.

Verification: All 37 arrays underwent independent second-machine reproduction (byte-identical SHA-256 across two separate machines) and exhaustive dual verification using both `ca_verify` (https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/verifiers/ca_verify.c) and the standalone Python verifier `verify_independent.py` (https://github.com/Justus42/Math_Gemini_Antigravity/blob/666f76729372908a8b981878a164e414210eca84/verifiers/verify_independent.py), with negative controls (deleting one row) failing on every array.

Open items:
- The general proof argument in `PHASE7_T2_REDUCTION.md` has not yet been reviewed by an uninvolved external model; each of the 37 submitted arrays is verified exhaustively as an individual covering array.
- The literature check is not exhaustive: older covering-array literature, newer Zenodo revisions of Bai and Sitjar, and the primary source for `(5, 7, 5) = 4375` (Li-Ji-Yin 2009 / Ji-Li-Yin 2012) were not checked in full text.
- Optimality of the CP-SAT representative counts `m in {34, 68, 91, 116, 175}` is open.

Submitter: Justus Jeserigk, Independent (j.jeserigk.dev@outlook.de). Released under CC BY 4.0.
