# Pull Request Draft for `chrispbsmolen/ca-tools`

## Suggested PR Title

`Submission jeserigk-pgl-ccl-2026-11: 13 strength-3 covering arrays smaller than ca-tools @ 083a093 (v=10, 12, 14, 20; 23 entries)`

## Suggested PR Body

Adds `submissions/jeserigk-pgl-ccl-2026-11/` containing **13 Pareto-front strength-3 covering arrays**, `claims.csv`, and `HOW.md`. Under stair-step semantics, these 13 arrays are strictly smaller than `chrispbsmolen/ca-tools` at commit `083a0933e3561625b2aad9bd19035ad76d783f03` (`2026-11-25T13:32:06Z`, checked across `table/ca_table.csv.gz`, `table/ca_frame.csv`, and `table/derived.csv`, 0 open PRs at check time) on **23 entries** across four alphabet sizes (`v = 10, 12, 14, 20`), reducing `N` by **44 to 607 rows** relative to that snapshot.

### Prior Work & Construction

This construction builds directly on prior strength-3 group-action and pair-expansion work:
- **Chateauneuf, Colbourn and Kreher (1999, `ck-cck1999`)** and **Meagher and Stevens (2005, `group-ms2005`)**: group constructions for covering arrays.
- **Chateauneuf and Kreher (2002, `ck-ck2002`)**: strength-3 constructions and doubling benchmarks.
- **Cohen, Colbourn and Ling (2008, Constructions 1–3, `sa-ccl2008`)**: closest predecessor, combining a single `PGL(2, q)` orbit (`k <= q + 1`) with binary pair expansion (`TOCA`).
- **Nurmela (2004, `tabu-n2004`)**: tabu search for covering arrays.
*(By contrast, Maity et al. 2018 [`pgl-macc2018`] apply `PGL(2, q)` at strength `t = 4`.)*

To our knowledge, the specific combination used here extends the single-orbit CCL (2008) framework (`k <= q + 1`) to **two deterministic `PGL(2, q)` orbits with balanced column halving (`k <= 2q`)** and a **general (non-self-complementary) weakened partition-dependent binary matrix `C`**; all 13 arrays are built from scratch over `q in {9, 11, 13, 19}` (`v = q + 1`):

1. **Deterministic `PGL(2, q)` block (`2 · q(q² − 1)` rows):**
   The alphabet is `F_q ∪ {∞}`, encoded 0-based as `{0, ..., q}` with `q` representing `∞`. Partition the `k` columns into balanced halves `L` (`|L| = ⌊k/2⌋`) and `R` (`|R| = ⌈k/2⌉`), both `<= q`. Expand two starter rows under the sharply 3-transitive action of `PGL(2, q)` on `F_q ∪ {∞}`:
   - `r1`: `0` on `L`, pairwise distinct nonzero symbols `1..|R|` on `R` (so when `|R| = q`, e.g. `k = 2q`, `r1` uses all `q` nonzero elements `(F_q \ {0}) ∪ {∞}`).
   - `r2`: pairwise distinct symbols `0..|L|−1` on `L`, and `q` (`∞`) on `R`.
   This deterministically covers all 3-distinct tuples on every column triple, all constant tuples on pure triples (`L³`, `R³`), all `aab` tuples on `L²R` triples, and all `baa` tuples on `LR²` triples.

2. **Oriented pair expansion of `K_v` and binary matrix `C` (`M × k`):**
   Orient all `v(v − 1)/2` edges `{u, w}` of `K_v` via the directed `v`-cycle `(0,1), (1,2), ..., (v−2,v−1), (v−1,0)` plus all remaining edges with `u < w`, so every symbol `0..v−1` appears at least once in the `0`-slot and at least once in the `1`-slot. Expanding each row of `C` via `0 -> u`, `1 -> w` covers all remaining 2-symbol tuples when `C` contains all 6 non-constant patterns on `L³`/`R³`, `{010, 011, 100, 101}` on `L²R`, and `{001, 010, 101, 110}` on `LR²`. Two variants are used:
   - **`C_const` (`cc = 1`, 12 of 13 arrays):** additionally requires `000` or `111` on every mixed triple; the directed cycle then covers all `v` constant tuples on mixed triples with `0` appended constant rows (`N = 2q(q² − 1) + M · v(v − 1)/2`).
   - **`C_plain` (`cc = 0`, used for `CA(18070; 3, 35, 20)`):** omits the `000`/`111` requirement on mixed triples and appends `+v` constant rows (`N = 2q(q² − 1) + M · v(v − 1)/2 + v`).

   Because mixed triples omit two non-constant patterns, `C` is strictly smaller than regular binary covering arrays (for example `M = 14 < 17 = CAN(3, 15, 2)` [proven exact] at `k = 15`, and `M = 16 < best known upper bound 18` at `k = 18, 19`). Because `C(M, k)` is independent of `q`, the same `17 × 20` starter yields both `CA(3762; 3, 20, 12)` and `CA(5915; 3, 20, 14)`. A written literature check (including Colbourn Nov 2024, `CAs` v0.25, NIST, Seelman/IRSI 2026-10-13, Sitjar v1.4 Table 1, and Canli's `quantavane-covering-arrays` @ `0b179b52`) is archived in `docs/LITERATURE_CHECK_PGL_CCL.md`; novelty status is formally open because Chateauneuf & Kreher (2002) full text, Colbourn–Martirosyan–Trung–Walker (2006), Bai XunDi (2026 Zenodo / 237 arrays), and Sitjar (2026 Zenodo archive / pp. 4–9) were not read in full.

### Summary of the 13 Pareto-Front Arrays (23 Entries Smaller Than `ca-tools` @ `083a093`)

| `t` | `k` | `v` | `N` | `ca_table` (`083a093`) | `derived.csv` | Delta vs `ca_table` | Covered `k` range | SHA-256 |
| :-: | :-: | :-: | :---: | :---: | :---: | :---: | :---: | --- |
| 3 | 15 | 10 | **2070** | 2205 (`VER`) | 2178 | −135 | `15` | `78b0497f2c81b0f72b9a454c7fbf42a3d66f1e31851be5f568c95d7f584c1865` |
| 3 | 16 | 10 | **2115** | 2205 (`VER`) | 2178 | −90 | `16` | `4734fd80ffe90f11664912e113b045ba599cbeb4a0bc749729764b7f700b86b4` |
| 3 | 18 | 10 | **2160** | 2232 (`CIT`) | — | −72 | `17..18` | `410ccbcc821c8db43a9274344ddb37c1c82f401b7c7a2ddb245cdbb9e567686a` |
| 3 | 19 | 12 | **3696** | 3806 (`CIT`) | — | −110 | `19` | `2492d0f7e36a993defeb9cef1ecbc58284d900f8842809c6019b01cbec4f2514` |
| 3 | 20 | 12 | **3762** | 3806 (`CIT`) | — | −44 | `20` | `6a85d1b1e34aec7305d588775ab14005a29bea18f2d0931b56f9e58fb61572d4` |
| 3 | 20 | 14 | **5915** | 6006 (`CIT`) | 6193 | −91 | `20` | `051a4841f551770fd09e84ffd805edf4d3b7c13b435c9687598c14b939d29a3d` |
| 3 | 24 | 14 | **6097** | 6279 (`CIT`) | 6193 | −182 | `23..24` | `3abb40a4dcb501e3d34512aab8c11398248f629c72e4e9bba1916919f21ffdbb` |
| 3 | 26 | 14 | **6188** | 6383 (`CIT`) | — | −195 | `25..26` | `2952b2efb82ae2087c6c0d560a80bdf1d64409b6b1a42e1d17418f2978396eaa` |
| 3 | 29 | 20 | **17670** | 18145 (`CIT`) | 18487 | −475 | `27..29` *(k=27,28: −266 vs 17936)* | `739bf030ad8234a83c9e3fb057b15798918881afe1a82302be5cfb8cad35e58a` |
| 3 | 32 | 20 | **17860** | 18145 (`CIT`) | 18487 | −285 | `30..32` | `544735d32928b02dc0b423627a10aa57a4eba2c853e542df5c4dc5953098061c` |
| 3 | 34 | 20 | **18050** | 18430 (`CIT`) | 18487 | −380 | `33..34` | `9224fbac04d97afd78c001da51fe7f92f7f9c4b760317819d9dd7bb68c5ff4d0` |
| 3 | 35 | 20 | **18070** | 18677 (`CIT`) | 18487 | −607 | `35` | `8751d063aed3ef33322c7252dfee57abfa9a705ab4490da2b9d9eb5300b855ad` |
| 3 | 38 | 20 | **18240** | 18753 (`CIT`) | 18563 | −513 | `36..38` *(k=36: −437 vs 18677)* | `68678d1c01540b943656d81908a86857ee0a1ff445b76863e072d27aef5e80cb` |

### Verification & Reproducibility

- **Triple exhaustive check:** Every array passed `verifiers/ca_verify.c` (exit code 0, `0.006–0.451 s`), an independent standard-library Python verifier (`verifiers/verify_independent.py`, exit code 0, `0.208–33.373 s`), and an independent third-party verifier program (`submission/third_check.py`, including negative test with 70 rows removed; both third-party audit passes — including a local run of `tools/check_submission.py` with 13/13 PASS on `main @ 162d48f` — are documented in `docs/THIRD_PARTY_VERIFICATION.md`).
- **Bit-exact reproduction:** All 13 arrays were deterministically regenerated from `data/ccl_binary/` via `solvers/pgl_ccl_search expand` (both internally and independently from a fresh build during the third-party audit) and matched all 13 SHA-256 hashes above byte-for-byte (`submission/REPRODUCE.md`).
- **From scratch (Rule 6):** `Built from: nothing`; no existing table arrays and no Torres-Jimenez arrays were used.
- **Repository:** https://github.com/Justus42/Math_Gemini_Antigravity (`main` @ `734d768`; zero-dependency Rust `std`-only solver `solvers/pgl_ccl_search` + binary starters `data/ccl_binary/`).

### AI Tools Disclosure (Rule 1 & `CHANGES.md`)

- `AI tools used: yes` (recorded explicitly in `HOW.md`).
- Extent of AI use: The construction, the solver, the searches and the text of this submission were produced almost entirely by AI systems (Gemini in Google Antigravity); Claude acted as independent reviewer. The submitter has no formal training in combinatorics. He directed the project, approved each step and takes responsibility for the submission, but did not derive the construction himself.
- All coverage checks are deterministic and exhaustive.

### Submitter & Licence (Rules 4 & 5)

- **Responsible person:** Justus Jeserigk, Independent (`j.jeserigk.dev@outlook.de`).
- **Licence:** All submitted arrays are released under **CC BY 4.0**.
