# Verifikations-Log: Phase 6A (`results/general_tqv/`)

- **Datum (UTC):** `2026-11-26`
- **Branch:** `exp/phase6a-general-tqv` (Basis `origin/main` @ `68c8402`, nach Merge von PR `#21`)
- **Generator:** [`scripts/gen_general_tqv.py`](../../scripts/gen_general_tqv.py) (Pure Python `std`-only, suchfrei, kein Solver, keine Heuristik)
- **Beweis & Scan:** [`docs/GENERAL_TQV_PROOF.md`](../../docs/GENERAL_TQV_PROOF.md), [`docs/GENERAL_TQV_SCAN.md`](../../docs/GENERAL_TQV_SCAN.md)
- **Tabellen-Referenz (`chrispbsmolen/ca-tools`):** Commit `e673ab45758a3959710c662a34837f79f6add689` (`e673ab4`, `2026-11-26T06:17:26Z`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz` (2 vCPUs), `python3` `3.12.16`, `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert (`verifiers/SHA256SUMS` 3/3 OK, `test_verifiers.py` 23/23 PASS).
- **Externe Einreichungs-Sperre & Wortwahl (Regel 4):** Alle Vergleiche gelten streng als **„kleiner als `ca-tools` am Commit `e673ab4`“**. Die externe Literaturprüfung für `q^t + C(v, 2) * q^(t - 2)` ist noch nicht abgeschlossen; Drittprüfung auf zweiter Maschine steht für diese `12` neuen Dateien noch aus (daher hier ausschließlich **lokal deterministisch 2× byte-identisch**, nicht „rechnerunabhängig bestätigt“).

---

## 1. Gate 0 — Harte Positivkontrolle (`t = 4, v = q`, `q in {7, 8, 9, 11, 13}`)

Vor Schritt 4 wurde [`scripts/gen_general_tqv.py`](../../scripts/gen_general_tqv.py) mit `timeout --kill-after=10s 60` gegen alle `5` Phase-5E-Arrays aus `scripts/gen_t4_minus3q2.py` (sowie direkt gegen die `3` abgelegten Phase-5E-Dateien in `results/t4_nearbush/SHA256SUMS`) geprüft:

| `q` | Zelle `(4, q+2, q)` | `N` | Laufzeit `gen_general_tqv.py` | SHA-256 | Abgleich (`cmp -s`) |
| :---: | :---: | :---: | :---: | --- | --- |
| `7` | `(4, 9, 7)` | `3.430` | `0,009 s` | `d29b51556a7150ac1c5b060d504b08d3987b1f1d9b018bd77b19f624c4a9d642` | **byte-identisch** zu `gen_t4_minus3q2.py --q 7` *(Hinweis: `results/t4_nearbush/CA_3430_4_9_7.txt` `d5860ade…` ist die unveränderte PR-#17-`t4_postop`-Datei)* |
| `8` | `(4, 10, 8)` | `5.888` | `0,015 s` | `2e4bf66ba6bdaff78e31460d766843f9858485493f93aa6ab0c69e01d2883fe1` | **byte-identisch** zu `gen_t4_minus3q2.py --q 8` *(Hinweis: `results/t4_nearbush/CA_5888_4_10_8.txt` `7d72bc89…` ist die unveränderte PR-#15-`gen_t4_q8_nearbush.py`-Datei)* |
| `9` | `(4, 11, 9)` | `9.477` | `0,021 s` | `eeea94544ed885cf2110733f4cd74b998c87d944dae8af535718bc267d431b30` | **byte-identisch** zu `results/t4_nearbush/CA_9477_4_11_9.txt` |
| `11` | `(4, 13, 11)` | `21.296` | `0,049 s` | `cb9a4c5e431f1eb1652f70b0626bd981eaaa0c529f1267fad346847f703401a3` | **byte-identisch** zu `results/t4_nearbush/CA_21296_4_13_11.txt` |
| `13` | `(4, 15, 13)` | `41.743` | `0,112 s` | `e8435eb665b9c627982239675bc93f21334ac40d4e8d781cb3592e768233d9a5` | **byte-identisch** zu `results/t4_nearbush/CA_41743_4_15_13.txt` |

**Gate-0-Ergebnis:** `5/5` byte-identisch **PASS** (Gesamtlaufzeit `0,206 s`; zusätzlich `28/28` Randfall-Checks über `t in 2..6`, `v <= q`, `q in {2..27}` mit `ca_verify` PASS).

---

## 2. Schritt 4 — Dual-Verifikation, 2×-Determinismus & Negativkontrollen (`12/12 phase6a_small`)

Alle `12` neuen `phase6a_small`-Zellen aus [`docs/GENERAL_TQV_SCAN.md`](../../docs/GENERAL_TQV_SCAN.md) wurden streng aufsteigend nach `C(k, t) * N_pred` innerhalb des harten Wall-Clock-Gesamtbudgets von `600 s` erzeugt und geprüft (jeder Einzelschritt mit externem `timeout --kill-after=10s <SECS>`):

- **Erstlauf-Summe Generierung (`12` Arrays):** `2,613 s`
- **Reproduktions-Summe Generierung (2. Lauf, `cmp -s` `12/12` PASS):** `2,594 s`
- **Summe Dual-Verifikation:** `ca_verify` `14,313 s` (`12/12` `rc=0`), `verify_independent.py` `102,047 s` (`12/12` `rc=0`)
- **Summe Negativkontrollen (`N - 1` Zeilen in Scratch):** `ca_verify` `12,735 s` (`12/12` `rc=1`), `verify_independent.py` `109,395 s` (`12/12` `rc=1`)
- **Gesamt-Wall-Clock Schritt 4 (inkl. 2× Gen., Dual-Verify & Negativkontrollen):** `244,065 s` (Budget `600 s` eingehalten)
- **Gesamtgröße (`12` Dateien):** `16,04 MB` (jede Datei `<= 7,19 MB <= 10 MB`)

| # | Datei (`results/general_tqv/`) | Zelle `(t, k, v)` | `q` | `ca-tools @ e673ab4` | Delta | Erstlauf / Repro (`cmp -s`) | Größe | `ca_verify` (`t=30s`) | `verify_independent.py` (`t=90s`) | Negativkontrolle (`N - 1` Zeilen) | SHA-256 |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- | --- |
| 1 | `CA_1053_3_11_9.txt` | `(3, 11, 9)` | `9` | `1.089` (`VERIFIED`) | **`−36`** | `0,067 s` / `0,064 s` (`PASS`) | `0,02 MB` | `rc=0`, `0,006 s` | `rc=0`, `0,087 s` | `ca rc=1`, `py rc=1` (`missing 45/120285 interactions across 45/165 column sets`) | `4bd2469875295c1b44134f0c77443460793a22ddcfaefb031aaf204352e180d1` |
| 2 | `CA_1936_3_13_11.txt` | `(3, 13, 11)` | `11` | `1.991` (`VERIFIED`) | **`−55`** | `0,067 s` / `0,069 s` (`PASS`) | `0,05 MB` | `rc=0`, `0,007 s` | `rc=0`, `0,158 s` | `ca rc=1`, `py rc=1` (`missing 66/380666 interactions across 66/286 column sets`) | `0220988fa28d5be959b70da80c3d9632f94af4539e9561ae53fb85f543103c2d` |
| 3 | `CA_3211_3_15_13.txt` | `(3, 15, 13)` | `13` | `3.289` (`VERIFIED`) | **`−78`** | `0,074 s` / `0,074 s` (`PASS`) | `0,10 MB` | `rc=0`, `0,012 s` | `rc=0`, `0,297 s` | `ca rc=1`, `py rc=1` (`missing 91/999635 interactions across 91/455 column sets`) | `05984611eca09f5833c9d2311a61cfde19986e750a5a8484210ad952962c9ec8` |
| 4 | `CA_24010_5_9_7.txt` | `(5, 9, 7)` | `7` | `25.039` (`VERIFIED`) | **`−1.029`** | `0,111 s` / `0,115 s` (`PASS`) | `0,41 MB` | `rc=0`, `0,035 s` | `rc=0`, `1,134 s` | `ca rc=1`, `py rc=1` (`missing 70/2117682 interactions across 70/126 column sets`) | `13f1c8da1aaa37d1c4235285d581d05cc6d6d667884e7a7c13d099feddb79ce6` |
| 5 | `CA_47104_5_10_8.txt` | `(5, 10, 8)` | `8` | `49.128` (`VERIFIED`) | **`−2.024`** | `0,166 s` / `0,190 s` (`PASS`) | `0,90 MB` | `rc=0`, `0,122 s` | `rc=0`, `4,573 s` | `ca rc=1`, `py rc=1` (`missing 126/8257536 interactions across 126/252 column sets`) | `8550074fda93e3b7e6dca9090f68e185777f77200d6e75fae946960fe509901e` |
| 6 | `CA_9766_3_21_18.txt` | `(3, 21, 18)` | `19` | `9.830` (`VERIFIED`) | **`−64`** | `0,092 s` / `0,091 s` (`PASS`) | `0,47 MB` | `rc=0`, `0,055 s` | `rc=0`, `3,254 s` | `ca rc=1`, `py rc=1` (`missing 113/7756560 interactions across 113/1330 column sets`) | `9cbdafb7f73fd4e0706c3ba7609412566952aa1cdf8a618bb57cefd688bcedf3` |
| 7 | `CA_10108_3_21_19.txt` | `(3, 21, 19)` | `19` | `10.279` (`VERIFIED`) | **`−171`** | `0,098 s` / `0,096 s` (`PASS`) | `0,50 MB` | `rc=0`, `0,063 s` | `rc=0`, `3,469 s` | `ca rc=1`, `py rc=1` (`missing 190/9122470 interactions across 190/1330 column sets`) | `8ff69cf373caa31ff5f0a88fd8e50540dcc10a53375c039926b35cfd64eead5c` |
| 8 | `CA_168070_6_9_7.txt` | `(6, 9, 7)` | `7` | `175.273` (`VERIFIED`) | **`−7.203`** | `0,433 s` / `0,432 s` (`PASS`) | `2,89 MB` | `rc=0`, `2,380 s` | `rc=0`, `7,344 s` | `ca rc=1`, `py rc=1` (`missing 56/9882516 interactions across 56/84 column sets`) | `c7de1a5387a2153bb5d61f43eb4ae702778b8daf75a4fe95ccb2a58ae640dd16` |
| 9 | `CA_20086_4_13_10.txt` | `(4, 13, 10)` | `11` | `20.383` (`VERIFIED`) | **`−297`** | `0,113 s` / `0,109 s` (`PASS`) | `0,50 MB` | `rc=0`, `0,040 s` | `rc=0`, `3,928 s` | `ca rc=1`, `py rc=1` (`missing 80/7150000 interactions across 80/715 column sets`) | `d150abae2d774a49f0d9d2a1dec000b4c189706c3eb18f9f3cbca9d27305f537` |
| 10 | `CA_85293_5_11_9.txt` | `(5, 11, 9)` | `9` | `88.209` (`VERIFIED`) | **`−2.916`** | `0,270 s` / `0,262 s` (`PASS`) | `1,79 MB` | `rc=0`, `0,425 s` | `rc=0`, `14,089 s` | `ca rc=1`, `py rc=1` (`missing 210/27280638 interactions across 210/462 column sets`) | `b369ba93389c4493c3a7541e1ab7637924acb126235ed19084bea55dce8bf0cc` |
| 11 | `CA_39715_4_15_12.txt` | `(4, 15, 12)` | `13` | `40.476` (`VERIFIED`) | **`−761`** | `0,176 s` / `0,169 s` (`PASS`) | `1,22 MB` | `rc=0`, `0,144 s` | `rc=0`, `17,863 s` | `ca rc=1`, `py rc=1` (`missing 157/28304640 interactions across 157/1365 column sets`) | `4e651a190870981ebeadd45e6afcf0434a361fe127536d62bfe9690a40c7cae6` |
| 12 | `CA_376832_6_10_8.txt` | `(6, 10, 8)` | `8` | `393.018` (`VERIFIED`) | **`−16.186`** | `0,945 s` / `0,922 s` (`PASS`) | `7,19 MB` | `rc=0`, `11,023 s` | `rc=0`, `45,851 s` | `ca rc=1`, `py rc=1` (`missing 126/55050240 interactions across 126/210 column sets`) | `2d433053ac2a24c44f74e54429460f5ea76aa248b3c43f9a6f7af2e084ba4c92` |

---

## 3. Reproduktions- und Prüfkommandos

```bash
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 3 --q 9 --v 9 --out results/general_tqv/CA_1053_3_11_9.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 3 --q 11 --v 11 --out results/general_tqv/CA_1936_3_13_11.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 3 --q 13 --v 13 --out results/general_tqv/CA_3211_3_15_13.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 5 --q 7 --v 7 --out results/general_tqv/CA_24010_5_9_7.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 5 --q 8 --v 8 --out results/general_tqv/CA_47104_5_10_8.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 3 --q 19 --v 18 --out results/general_tqv/CA_9766_3_21_18.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 3 --q 19 --v 19 --out results/general_tqv/CA_10108_3_21_19.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 6 --q 7 --v 7 --out results/general_tqv/CA_168070_6_9_7.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 4 --q 11 --v 10 --out results/general_tqv/CA_20086_4_13_10.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 5 --q 9 --v 9 --out results/general_tqv/CA_85293_5_11_9.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 4 --q 13 --v 12 --out results/general_tqv/CA_39715_4_15_12.txt
timeout --kill-after=10s 60 python3 scripts/gen_general_tqv.py --t 6 --q 8 --v 8 --out results/general_tqv/CA_376832_6_10_8.txt

timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_1053_3_11_9.txt 3 9 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_1053_3_11_9.txt 3 9 -n 1053 -k 11
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_1936_3_13_11.txt 3 11 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_1936_3_13_11.txt 3 11 -n 1936 -k 13
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_3211_3_15_13.txt 3 13 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_3211_3_15_13.txt 3 13 -n 3211 -k 15
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_24010_5_9_7.txt 5 7 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_24010_5_9_7.txt 5 7 -n 24010 -k 9
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_47104_5_10_8.txt 5 8 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_47104_5_10_8.txt 5 8 -n 47104 -k 10
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_9766_3_21_18.txt 3 18 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_9766_3_21_18.txt 3 18 -n 9766 -k 21
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_10108_3_21_19.txt 3 19 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_10108_3_21_19.txt 3 19 -n 10108 -k 21
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_168070_6_9_7.txt 6 7 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_168070_6_9_7.txt 6 7 -n 168070 -k 9
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_20086_4_13_10.txt 4 10 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_20086_4_13_10.txt 4 10 -n 20086 -k 13
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_85293_5_11_9.txt 5 9 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_85293_5_11_9.txt 5 9 -n 85293 -k 11
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_39715_4_15_12.txt 4 12 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_39715_4_15_12.txt 4 12 -n 39715 -k 15
timeout --kill-after=10s 30 ./verifiers/ca_verify results/general_tqv/CA_376832_6_10_8.txt 6 8 && timeout --kill-after=10s 90 python3 verifiers/verify_independent.py results/general_tqv/CA_376832_6_10_8.txt 6 8 -n 376832 -k 10
```
