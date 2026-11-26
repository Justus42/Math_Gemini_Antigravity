# Verifikations-Log: Phase 7 (`results/phase7/`)

- **Datum (UTC):** `2026-11-26`
- **Branch:** `chore/verify-phase7-q5-q9` (Basis `origin/main` @ `6c1c656`, nach Merge von PR `#25` @ `be80225`; PR `#24` bleibt separat offen und unberührt)
- **Zertifikate & Lift-Skript (unverändert aus PR `#25`):** [`data/phase7/R_q5_m34.txt`](../../data/phase7/R_q5_m34.txt), [`data/phase7/R_q7_m68.txt`](../../data/phase7/R_q7_m68.txt), [`data/phase7/R_q8_m91.txt`](../../data/phase7/R_q8_m91.txt), [`data/phase7/R_q9_m116.txt`](../../data/phase7/R_q9_m116.txt); deterministischer Pure-Python-Lifter [`scripts/phase7_lift.py`](../../scripts/phase7_lift.py) (`std`-only, ohne Suche, ohne OR-Tools, nutzt `GeneralGF` aus [`scripts/gen_general_tqv.py`](../../scripts/gen_general_tqv.py))
- **Dokumentation der Ausgangsrechnung:** [`docs/PHASE7_T2_REDUCTION.md`](../../docs/PHASE7_T2_REDUCTION.md)
- **Tabellen-Referenz (`chrispbsmolen/ca-tools`, Live-Abgleich via `gh api`):** Commit `e673ab45758a3959710c662a34837f79f6add689` (`e673ab4`, `2026-11-26T06:17:26Z`); geprüft gegen `table/ca_table.csv.gz`, `table/ca_frame.csv` und `table/derived.csv` (einziger offener PR: `#89` `add-ca165-3-8-5`, `CA(165; 3, 8, 5)`, ohne Überschneidung)
- **Hardware (Zweitmaschine):** `Intel(R) Xeon(R) CPU @ 2.30GHz` (`2` vCPUs, AVX2), `python3` `3.12.16`, `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert (`gcc -O3 -march=native -pthread -o verifiers/ca_verify verifiers/ca_verify.c -lm`; `verifiers/SHA256SUMS` `3/3 OK`, `verifiers/test_verifiers.py` `23/23 PASS`)
- **Zweitmaschinen-Bestätigung:** Alle `11/11` Dateien in `results/phase7/` sind lokal `2×` deterministisch byte-identisch (`cmp -s` `11/11 PASS`) **und** `11/11` byte-identisch zu Claudes SHA-256-Hashes aus PR `#25` (`be80225`). Alle `11` Arrays sind damit **rechnerunabhängig bestätigt** und vollständig dual-verifiziert (`verifiers/ca_verify` `11/11 PASS`, `verifiers/verify_independent.py` `11/11 PASS`, womit die bei Claude offene `verify_independent.py`-Lücke für alle `11` Arrays geschlossen ist).
- **Wortwahl & Einreichungs-Sperre (Regel 4):** Alle Tabellenvergleiche gelten als **„kleiner als `ca-tools` am Commit `e673ab4`“**. `(6, 7, 5)` wurde nicht erzeugt (`ca_frame @ e673ab4`: `15.625` `CITED` OA, `21.250` ist nicht kleiner). Externe Einreichungs-Sperre aktiv (kein Push nach `Justus42/ca-tools`).

---

## 1. Live-Abgleich gegen `chrispbsmolen/ca-tools @ e673ab4`

| # | Zelle `(t, k, v)` | `q` | `m` | `N` (`m * q^(t-2)`) | `ca_frame` (`k >=`) | `ca_table` (`k >=`) | `derived` (`k >=`) | Tier | Delta vs. `e673ab4` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `(3, 11, 9)` | `9` | `116` | `1.044` | `1.089` (`k=11`) | `1.089` (`k=11`) | `5.697` (`k=10001`) | `VERIFIED` | **`−45`** |
| 2 | `(5, 7, 5)` | `5` | `34` | `4.250` | `4.375` (`k=7`) | `4.375` (`k=7`) | `248.724` (`k=11000`) | `CITED` | **`−125`** |
| 3 | `(4, 9, 7)` | `7` | `68` | `3.332` | `3.556` (`k=9`) | `3.556` (`k=9`) | `83.244` (`k=12500`) | `VERIFIED` | **`−224`** |
| 4 | `(4, 10, 8)` | `8` | `91` | `5.824` | `6.101` (`k=10`) | `6.101` (`k=10`) | `139.601` (`k=11000`) | `VERIFIED` | **`−277`** |
| 5 | `(4, 11, 9)` | `9` | `116` | `9.396` | `9.801` (`k=11`) | `9.801` (`k=11`) | `219.296` (`k=12500`) | `VERIFIED` | **`−405`** |
| 6 | `(5, 9, 7)` | `7` | `68` | `23.324` | `25.039` (`k=9`) | `25.039` (`k=9`) | `378.559` (`k=5603`) | `VERIFIED` | **`−1.715`** |
| 7 | `(5, 10, 8)` | `8` | `91` | `46.592` | `49.128` (`k=10`) | `49.128` (`k=10`) | `622.574` (`k=1999`) | `VERIFIED` | **`−2.536`** |
| 8 | `(5, 11, 9)` | `9` | `116` | `84.564` | `88.209` (`k=11`) | `88.209` (`k=11`) | `1.249.249` (`k=7382`) | `VERIFIED` | **`−3.645`** |
| 9 | `(6, 9, 7)` | `7` | `68` | `163.268` | `175.273` (`k=9`) | `175.273` (`k=9`) | `3.805.039` (`k=2801`) | `VERIFIED` | **`−12.005`** |
| 10 | `(6, 10, 8)` | `8` | `91` | `372.736` | `393.018` (`k=10`) | `393.018` (`k=10`) | `4.257.520` (`k=238`) | `VERIFIED` | **`−20.282`** |
| 11 | `(6, 11, 9)` | `9` | `116` | `761.076` | `793.881` (`k=11`) | `793.881` (`k=11`) | `16.349.913` (`k=3951`) | `VERIFIED` | **`−32.805`** |
| — | `(6, 7, 5)` *(nicht erzeugt)* | `5` | `34` | `21.250` | `15.625` (`k=7`) | `15.625` (`k=7`) | `386.485` (`k=782`) | `CITED` | `+5.625` *(ausgeschlossen)* |

---

## 2. Zweitmaschinen-Reproduktion, Dual-Verifikation & Negativkontrollen (`11/11`)

Alle Befehle liefen unter externem `timeout --kill-after=10s <SECS>` in streng aufsteigender Reihenfolge (`#1..#8` für `t <= 5`; `#9`, `#10` und `#11` jeweils in separaten Shell-Aufrufen).

- **Erstlauf-Summe Generierung (`11` Arrays, `scripts/phase7_lift.py --check-m`):** `13,911 s` (`M(R)` `uncovered pairs = 0` für alle `11/11`)
- **Reproduktions-Summe Generierung (2. Lauf, `cmp -s` `11/11 PASS`):** `13,365 s`
- **SHA-256-Abgleich gegen PR `#25` (`be80225`, Claude):** **`11/11` byte-identisch**
- **Summe Dual-Verifikation:** `verifiers/ca_verify` (`timeout 60`): `76,264 s` (**`11/11 PASS`, `rc=0`**); `verifiers/verify_independent.py` (`timeout 180` / `900`): `313,476 s` (**`11/11 PASS`, `rc=0`**)
- **Summe Negativkontrollen (`N - 1` Zeilen, letzte Zeile in Scratch-Kopie gelöscht):**
  - `verifiers/ca_verify` (`timeout 30`): `45,761 s` — **`10/11 FAIL (rc=1)`**; **`#11 CA_761076_6_11_9.txt`: `nicht gelaufen`** (`rc=124`, `30,173 s`, Zeitlimit `30 s` erreicht, da `ca_verify` ohne `--fail-fast` alle `462` Spaltensets in `~58 s` durchläuft).
  - Nachholung `#11` `verifiers/ca_verify` mit `timeout 120`: **`FAIL (rc=1)`** (`58,148 s`, `168` von `462` Spaltensets mit Lücken).
  - `verifiers/verify_independent.py` (`timeout 180` / `900`): `316,319 s` — **`11/11 FAIL (rc=1)`**.
- **Aktive Pipeline-Summe gesamt:** `837,245 s` (Brutto-Wall-Clock über die separaten Shell-Aufrufe `10:44:05Z–10:59:37Z`: `932 s`)
- **Gesamtgröße (`11` unkomprimierte Dateien in `results/phase7/`):** `30.814.932` Bytes (`29,39 MiB` / `30,81 MB`)

| # | Datei (`results/phase7/`) | Zelle `(t, k, v)` | Erstlauf / Repro (`cmp -s`, PR `#25` SHA) | Größe | `ca_verify` (`timeout 60`) | `verify_independent.py` (`180s` / `900s`) | Negativkontrolle `ca_verify` (`timeout 30`) | Negativkontrolle `verify_independent.py` (`180s` / `900s`) | SHA-256 |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | --- | --- | --- |
| 1 | `CA_1044_3_11_9.txt` | `(3, 11, 9)` | `0,088 s` / `0,082 s` (`PASS`, exakt) | `22.968 B` | `PASS` (`rc=0`, `0,008 s`) | `PASS` (`rc=0`, `0,108 s`) | `FAIL` (`rc=1`, `0,007 s`) | `FAIL` (`rc=1`, `0,104 s`, `108/165` Sets) | `91b865806d5212a1fc99a688743c6ada1ea0285e482d43297bef5a583a46f0fa` |
| 2 | `CA_4250_5_7_5.txt` | `(5, 7, 5)` | `0,086 s` / `0,088 s` (`PASS`, exakt) | `59.500 B` | `PASS` (`rc=0`, `0,008 s`) | `PASS` (`rc=0`, `0,124 s`) | `FAIL` (`rc=1`, `0,011 s`) | `FAIL` (`rc=1`, `0,125 s`, `7/21` Sets) | `0fb696c821d25467be4d6625b37f81d0cb7956afb47350ed9f035ca9104505ec` |
| 3 | `CA_3332_4_9_7.txt` | `(4, 9, 7)` | `0,088 s` / `0,093 s` (`PASS`, exakt) | `59.976 B` | `PASS` (`rc=0`, `0,013 s`) | `PASS` (`rc=0`, `0,161 s`) | `FAIL` (`rc=1`, `0,015 s`) | `FAIL` (`rc=1`, `0,183 s`, `81/126` Sets) | `a221268ab90ce2c3d8901842966e44fb03ee4f1bdc919cfa7e31845ea6ede972` |
| 4 | `CA_5824_4_10_8.txt` | `(4, 10, 8)` | `0,131 s` / `0,122 s` (`PASS`, exakt) | `116.480 B` | `PASS` (`rc=0`, `0,028 s`) | `PASS` (`rc=0`, `0,393 s`) | `FAIL` (`rc=1`, `0,011 s`) | `FAIL` (`rc=1`, `0,448 s`, `154/210` Sets) | `58de207c9a3e1b1870c4703a20bb872bdda899dcbe9573f20c7605cfe0316bbe` |
| 5 | `CA_9396_4_11_9.txt` | `(4, 11, 9)` | `0,167 s` / `0,166 s` (`PASS`, exakt) | `206.712 B` | `PASS` (`rc=0`, `0,018 s`) | `PASS` (`rc=0`, `1,069 s`) | `FAIL` (`rc=1`, `0,017 s`) | `FAIL` (`rc=1`, `1,019 s`, `180/330` Sets) | `3c84f9ab804618d38dbfc8121cca169567849c4f6c986fb392ff29be6ff28096` |
| 6 | `CA_23324_5_9_7.txt` | `(5, 9, 7)` | `0,230 s` / `0,242 s` (`PASS`, exakt) | `419.832 B` | `PASS` (`rc=0`, `0,042 s`) | `PASS` (`rc=0`, `1,194 s`) | `FAIL` (`rc=1`, `0,036 s`) | `FAIL` (`rc=1`, `1,187 s`, `81/126` Sets) | `f84786fd02bd88e9a95d2efd27b060089de7c9fbdd83c0d4807c431a6b52c9cf` |
| 7 | `CA_46592_5_10_8.txt` | `(5, 10, 8)` | `0,427 s` / `0,420 s` (`PASS`, exakt) | `931.840 B` | `PASS` (`rc=0`, `0,112 s`) | `PASS` (`rc=0`, `5,067 s`) | `FAIL` (`rc=1`, `0,117 s`) | `FAIL` (`rc=1`, `5,531 s`, `188/252` Sets) | `927c206a4b71db106e422b61decdac8667e70a5f3fe753a6d80aca00cdafb370` |
| 8 | `CA_84564_5_11_9.txt` | `(5, 11, 9)` | `0,862 s` / `0,771 s` (`PASS`, exakt) | `1,77 MiB` | `PASS` (`rc=0`, `0,464 s`) | `PASS` (`rc=0`, `16,201 s`) | `FAIL` (`rc=1`, `0,453 s`) | `FAIL` (`rc=1`, `16,831 s`, `210/462` Sets) | `adc1b18082687cca9fefa54a867f6b28ab3866f016d6d95e24ba0af7d3c137bd` |
| 9 | `CA_163268_6_9_7.txt` | `(6, 9, 7)` | `1,331 s` / `1,332 s` (`PASS`, exakt) | `2,80 MiB` | `PASS` (`rc=0`, `2,379 s`) | `PASS` (`rc=0`, `9,170 s`) | `FAIL` (`rc=1`, `2,151 s`) | `FAIL` (`rc=1`, `9,436 s`, `57/84` Sets) | `3b6030f0ce6afe9c80a2fd86fa8f55e4de923610daafb579e904e65715f1c12e` |
| 10 | `CA_372736_6_10_8.txt` | `(6, 10, 8)` | `3,084 s` / `3,137 s` (`PASS`, exakt) | `7,11 MiB` | `PASS` (`rc=0`, `13,196 s`) | `PASS` (`rc=0`, `48,111 s`) | `FAIL` (`rc=1`, `12,771 s`) | `FAIL` (`rc=1`, `50,334 s`, `154/210` Sets) | `7e051655edab7e11a69d8a16ac0865e8a56543b2d2071161e9cb1ce3cf99a6e6` |
| 11 | `CA_761076_6_11_9.txt` | `(6, 11, 9)` | `7,417 s` / `6,913 s` (`PASS`, exakt) | `15,97 MiB` | `PASS` (`rc=0`, `59,997 s`) | `PASS` (`rc=0`, `231,880 s`) | **`nicht gelaufen`** (`rc=124`, `30,173 s`); Nachholung `timeout 120`: `FAIL` (`rc=1`, `58,148 s`, `168/462` Sets) | `FAIL` (`rc=1`, `231,121 s`, `168/462` Sets) | `aaee4a1dfde48c45b7e7b4e99d574e2d3eda28982fd72accf16e2529a03b8f74` |

---

## 3. Reproduktions- und Prüfkommandos

```bash
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 9 --reps data/phase7/R_q9_m116.txt --check-m --t 3 --out results/phase7/CA_1044_3_11_9.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 5 --reps data/phase7/R_q5_m34.txt  --check-m --t 5 --out results/phase7/CA_4250_5_7_5.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 7 --reps data/phase7/R_q7_m68.txt  --check-m --t 4 --out results/phase7/CA_3332_4_9_7.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 8 --reps data/phase7/R_q8_m91.txt  --check-m --t 4 --out results/phase7/CA_5824_4_10_8.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 9 --reps data/phase7/R_q9_m116.txt --check-m --t 4 --out results/phase7/CA_9396_4_11_9.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 7 --reps data/phase7/R_q7_m68.txt  --check-m --t 5 --out results/phase7/CA_23324_5_9_7.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 8 --reps data/phase7/R_q8_m91.txt  --check-m --t 5 --out results/phase7/CA_46592_5_10_8.txt
timeout --kill-after=10s 60  python3 scripts/phase7_lift.py --q 9 --reps data/phase7/R_q9_m116.txt --check-m --t 5 --out results/phase7/CA_84564_5_11_9.txt
timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 7 --reps data/phase7/R_q7_m68.txt  --check-m --t 6 --out results/phase7/CA_163268_6_9_7.txt
timeout --kill-after=10s 300 python3 scripts/phase7_lift.py --q 8 --reps data/phase7/R_q8_m91.txt  --check-m --t 6 --out results/phase7/CA_372736_6_10_8.txt
timeout --kill-after=10s 300 python3 scripts/phase7_lift.py --q 9 --reps data/phase7/R_q9_m116.txt --check-m --t 6 --out results/phase7/CA_761076_6_11_9.txt

# Dual-Verifikation (je Array)
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_1044_3_11_9.txt 3 9 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_1044_3_11_9.txt 3 9 -n 1044 -k 11
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_4250_5_7_5.txt 5 5 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_4250_5_7_5.txt 5 5 -n 4250 -k 7
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_3332_4_9_7.txt 4 7 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_3332_4_9_7.txt 4 7 -n 3332 -k 9
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_5824_4_10_8.txt 4 8 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_5824_4_10_8.txt 4 8 -n 5824 -k 10
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_9396_4_11_9.txt 4 9 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_9396_4_11_9.txt 4 9 -n 9396 -k 11
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_23324_5_9_7.txt 5 7 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_23324_5_9_7.txt 5 7 -n 23324 -k 9
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_46592_5_10_8.txt 5 8 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_46592_5_10_8.txt 5 8 -n 46592 -k 10
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_84564_5_11_9.txt 5 9 && timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/phase7/CA_84564_5_11_9.txt 5 9 -n 84564 -k 11
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_163268_6_9_7.txt 6 7 && timeout --kill-after=10s 900 python3 verifiers/verify_independent.py results/phase7/CA_163268_6_9_7.txt 6 7 -n 163268 -k 9
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_372736_6_10_8.txt 6 8 && timeout --kill-after=10s 900 python3 verifiers/verify_independent.py results/phase7/CA_372736_6_10_8.txt 6 8 -n 372736 -k 10
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_761076_6_11_9.txt 6 9 && timeout --kill-after=10s 900 python3 verifiers/verify_independent.py results/phase7/CA_761076_6_11_9.txt 6 9 -n 761076 -k 11
```
