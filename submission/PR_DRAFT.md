# Pull Request Draft for `chrispbsmolen/ca-tools`

> **BEFORE OPENING THE PR:**
> 1. Replace all `[REAL_NAME_TBD]`, `[AFFILIATION_TBD]`, `[EMAIL_TBD]`, `[FINAL_MAIN_COMMIT_TBD]`, and `[LITERATURE_ATTRIBUTION_TBD]` placeholders in `HOW.md`, `claims.csv`, and this PR text.
> 2. Copy `submission/ca_tools_staging/` as `submissions/<slug>/` into your own fork of `chrispbsmolen/ca-tools` (touching **no** files outside `submissions/<slug>/`, per Rule 7).
> 3. Run `python3 tools/check_submission.py submissions/<slug>` locally in your `ca-tools` clone before pushing.

---

## Suggested PR Title

`Submission <slug>: 13 strength-3 covering arrays smaller than ca-tools @ 7b08aef (v=10, 12, 14, 20; 23 entries)`

## Suggested PR Body

Adds `submissions/<slug>/` containing **13 Pareto-front strength-3 covering arrays**, `claims.csv`, and `HOW.md`. Under stair-step semantics, these 13 arrays are strictly smaller than `chrispbsmolen/ca-tools` at commit `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a` (checked across `table/ca_table.csv.gz`, `table/ca_frame.csv`, and `table/derived.csv`) on **23 entries** across four alphabet sizes (`v = 10, 12, 14, 20`), reducing `N` by **44 to 607 rows** relative to that snapshot.

### Prior Work & Construction

Building on group-action constructions for strength-3 covering arrays (Chateauneuf–Colbourn–Kreher 1999; Chateauneuf–Kreher 2002; Meagher–Stevens 2005), binary pair-expansion / augmented-annealing constructions (Cohen–Colbourn–Ling 2008), and tabu/clause-weighting local search (Nurmela 2004), all 13 arrays are generated from **one uniform, from-scratch construction** parameterized by a prime power `q` (`v = q + 1`, `k <= 2q`):

`[LITERATURE_ATTRIBUTION_TBD]`
*(Pending written literature review in `docs/` prior to release: verify exact prior-art attribution and `builds_on` IDs against Cohen–Colbourn–Ling 2008 [`sa-ccl2008`], Chateauneuf–Kreher 2002 [`ck-ck2002`], Chateauneuf–Colbourn–Kreher 1999 [`ck-cck1999`], Meagher–Stevens 2005 [`group-ms2005`], and Nurmela 2004 [`tabu-n2004`].)*

1. **Deterministic `PGL(2, q)` block (`2 * q(q² - 1)` rows):**
   Partition the `k` columns into balanced halves `L` (`|L| = floor(k/2)`) and `R` (`|R| = ceil(k/2)`), both `<= q`. Expand two explicit starter rows under the sharply 3-transitive action of `PGL(2, q)` on `P¹(GF(q))`:
   - `r1`: `0` on `L`, pairwise distinct nonzero symbols `1..|R|` on `R`.
   - `r2`: pairwise distinct symbols `0..|L|-1` on `L`, `q` (`∞`) on `R`.
   This deterministically covers all 3-distinct tuples on all `C(k, 3)` column triples, all constant tuples on pure triples (`L³`, `R³`), all `aab` tuples on `(L, L, R)` triples, and all `baa` tuples on `(L, R, R)` triples.

2. **General (non-self-complementary) binary CCL matrix `C` (`M × k`) over `v(v - 1)/2` oriented pairs:**
   Search a binary `M × k` matrix `C` covering the remaining 6 non-constant patterns on `L³`/`R³` and the remaining 4 non-constant patterns on mixed triples (`L²R`, `LR²`). Orient all `v(v - 1)/2` unordered pairs `{u, w}` using a directed cycle `(0,1), (1,2), ..., (v-1,0)` plus the remaining pairs `u < w` so every symbol appears at least once in both the `0`-slot and the `1`-slot. Requiring `000` or `111` on every mixed triple (`--cover-const`, used in 12 of the 13 arrays) covers all constant tuples on mixed triples and eliminates all `v` constant rows (`N = 2q(q² - 1) + M · v(v - 1)/2`; for `CA(18070; 3, 35, 20)` without `--cover-const`, `+20` constant rows are appended).
   Because `C(M, k)` is independent of `q`, the same `17 × 20` binary starter yields both `CA(3762; 3, 20, 12)` and `CA(5915; 3, 20, 14)`.

### Summary of the 13 Pareto-Front Arrays (23 Entries Smaller Than Table @ `7b08aef`)

| `t` | `k` | `v` | `N_submitted` | `ca_table` (`7b08aef`) | `derived.csv` | Delta vs `ca_table` | Covered `k` range | SHA-256 |
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

- Every array passed exhaustive verification with both `ca_verify.c` (exit code 0, `0.006–0.451 s`) and an independent standard-library Python verifier (`verify_independent.py`, exit code 0, `0.208–33.373 s`), plus `[THIRD_PARTY_VERIFICATION_TBD]`.
- All 13 arrays were deterministically regenerated from the stored `data/ccl_binary/` starter matrices and verified byte-for-byte against the SHA-256 hashes above (13/13 exact matches; exact commands in `submission/REPRODUCE.md`).
- All 13 arrays are built completely from scratch (`Built from: nothing`); no existing table arrays and no Torres-Jimenez arrays were used (Rule 6).
- Full source code (`solvers/pgl_ccl_search`, zero-dependency Rust `std`-only) and compact `M × k` binary starter matrices (`data/ccl_binary/`, 68 KB) are published at https://github.com/Justus42/Math_Gemini_Antigravity.

### AI Tools Disclosure (Rule 1 & `CHANGES.md`)

- `AI tools used: yes` (included explicitly in `HOW.md`).
- Tools used: Gemini and Google Antigravity for solver implementation and local-search sweeps; independent review/cross-checking by Claude. All verification checks are deterministic and exhaustive.

### Submitter & Licence (Rules 4 & 5)

- **Responsible person:** `[REAL_NAME_TBD]`, `[AFFILIATION_TBD]` (e.g., Independent researcher).
- **Contact:** `[EMAIL_TBD]` *(or sent separately to `chrispbsmolen@gmail.com`)*; ORCID: `[ORCID_OPTIONAL]`.
- **Licence:** All submitted arrays are released under **CC BY 4.0**.
