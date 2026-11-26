Construction: Deterministic polynomial construction over a finite field GF(q) yielding CA(q^t + C(v, 2) * q^(t - 2); t, q + 2, v) for any prime power q >= 2, strength 2 <= t <= q + 2, and alphabet size 2 <= v <= q. No search, no heuristic, and no randomness are used.
- Field, order, and retraction: Identify GF(q) = GF(p)[X]/(f(X)) (using the lexicographically smallest monic irreducible polynomial f(X) of degree r over GF(p)) with {0, 1, ..., q - 1} in base p under the linear order 0 < 1 < ... < q - 1. Define the symbol retraction pi: GF(q) -> {0, ..., v - 1} by pi(z) = z for z < v and pi(z) = 0 for z >= v (identity when v = q).
- Columns: The k = q + 2 columns are indexed by GF(q) U {inf, *}.
- Block 1 (q^t rows): For every degree-(<= t - 1) polynomial P(x) = a_0 + a_1 x + ... + a_{t-3} x^{t-3} + c x^{t-2} + d x^{t-1} over GF(q), emit the row ((pi(P(x)))_{x in GF(q)}, pi(d), pi(min(c, d))). For v = q, the first q + 1 columns form the Bush orthogonal array OA(q^t; t, q + 1, q).
- Block 2 (C(v, 2) * q^(t - 2) rows): For every ordered symbol pair (c, d) with 0 <= c < d < v and every (a_0, ..., a_{t-3}) in GF(q)^{t - 2}, emit the row ((pi(P(x)))_{x in GF(q)}, c, d), where column inf is decoupled from the leading coefficient d of P(x) (col_inf = c, col_* = d).
- Proof and scope: A self-contained covering proof is documented at https://github.com/Justus42/Math_Gemini_Antigravity/blob/main/docs/GENERAL_TQV_PROOF.md. For t = 6, q = v = 9 (not included in this package due to file size), the formula evaluates to 9^6 + C(9, 2) * 9^4 = 767637, reaching the value 767637 by another route (it does not solve Open Problem 2 of Bai 2026 as a line-polychromatic colouring of an affine plane).
- Table comparison and literature status: All 19 arrays in this package are strictly smaller than ca-tools at commit e673ab45758a3959710c662a34837f79f6add689 (2026-11-26T06:17:26Z) across the table, frame, and derived bounds. No novelty claim is made. Colbourn and Lanus (2018, doi:10.26493/2590-9770.1220.3a1) was checked in full text; older literature including Hartman (2005), Ji and Yin (2010), Colbourn (2004, 2015), Hedayat, Sloane and Stufken (1999), Chateauneuf and Kreher (2002), and Colbourn, Lanus and Sarkar (2018) has not been checked in full text and remains open (see https://github.com/Justus42/Math_Gemini_Antigravity/blob/main/docs/LITERATURE_CHECK_T4_NEARBUSH.md).

Built from: nothing (all 19 arrays are constructed from scratch over GF(q); no existing table arrays and no Torres-Jimenez arrays were used as inputs). Conceptually, the construction builds on Bush (1952, `oa-bush1952`), Colbourn, Keri, Rivas Soriano and Schlage-Puchta (2010, Lemma 3.3, `fuse-ckrs2010`), and Bai XunDi (2026, doi:10.5281/zenodo.23787051, `polychrome-bai2026`).

Program: Pure Python (standard library only) generator pinned at https://github.com/Justus42/Math_Gemini_Antigravity/blob/ba4cfb2ff7477f8768fa2ad9f356fecc0aa5a94b/scripts/gen_general_tqv.py (commit `ba4cfb2ff7477f8768fa2ad9f356fecc0aa5a94b` on `main`). No code is included in this submission directory. Every submitted file is reproduced byte-identically by running `python3 gen_general_tqv.py` with the following arguments:
- `--t 3 --q 9 --v 9 --out CA_1053_3_11_9.txt`
- `--t 3 --q 11 --v 11 --out CA_1936_3_13_11.txt`
- `--t 3 --q 13 --v 13 --out CA_3211_3_15_13.txt`
- `--t 3 --q 19 --v 18 --out CA_9766_3_21_18.txt`
- `--t 3 --q 19 --v 19 --out CA_10108_3_21_19.txt`
- `--t 4 --q 7 --v 7 --out CA_3430_4_9_7.txt`
- `--t 4 --q 8 --v 8 --out CA_5888_4_10_8.txt`
- `--t 4 --q 9 --v 9 --out CA_9477_4_11_9.txt`
- `--t 4 --q 11 --v 10 --out CA_20086_4_13_10.txt`
- `--t 4 --q 11 --v 11 --out CA_21296_4_13_11.txt`
- `--t 4 --q 13 --v 12 --out CA_39715_4_15_12.txt`
- `--t 4 --q 13 --v 13 --out CA_41743_4_15_13.txt`
- `--t 5 --q 7 --v 7 --out CA_24010_5_9_7.txt`
- `--t 5 --q 8 --v 8 --out CA_47104_5_10_8.txt`
- `--t 5 --q 9 --v 9 --out CA_85293_5_11_9.txt`
- `--t 5 --q 11 --v 10 --out CA_220946_5_13_10.txt`
- `--t 5 --q 11 --v 11 --out CA_234256_5_13_11.txt`
- `--t 6 --q 7 --v 7 --out CA_168070_6_9_7.txt`
- `--t 6 --q 8 --v 8 --out CA_376832_6_10_8.txt`

AI tools used: yes
Extent of AI use: The construction, the generator script, the covering proof, and the text of this submission were produced by AI systems (Gemini in Google Antigravity), with independent review and re-implementation checks by Claude. The submitter has no formal training in combinatorics. He directed the project, approved each step, and takes responsibility for the submission, but did not derive the construction himself.
Verification: All 19 arrays passed exhaustive dual verification locally (`ca_verify.c` and a standalone Python verifier) as well as independent third-party reproduction and verification on a second machine (see https://github.com/Justus42/Math_Gemini_Antigravity/blob/main/docs/THIRD_PARTY_VERIFICATION_GENERAL_TQV.md and https://github.com/Justus42/Math_Gemini_Antigravity/blob/main/docs/RUN_LOG.md).

Submitter: Justus Jeserigk, Independent (j.jeserigk.dev@outlook.de). Released under CC BY 4.0.
