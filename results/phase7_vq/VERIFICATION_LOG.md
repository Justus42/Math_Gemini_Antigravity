# Verifikations-Log: Phase 7 Abschluss — Option B (`23` Arrays, `results/phase7_vq/` + Ergänzungen)

- **Datum (UTC):** `2026-11-26`
- **Branch:** `chore/verify-phase7-23` (Basis `origin/main` @ `e3100f6`, enthält PR `#29` @ `2268ff4`/`8b918d4` und PR `#30` @ `e3100f6`/`119098d`)
- **Ablage (ohne Änderung bestehender Dateien außer Erweiterung der `SHA256SUMS`):**
  - `17` Arrays Bauart §14 (`v < q`): `results/phase7_vq/` (`SHA256SUMS` `17/17 OK`, `125.593.124 B` / `119,7749 MiB`)
  - `3` Arrays Löserliste (`q = 11, v = 11`): `results/phase7/` (`CA_1925`, `CA_21175`, `CA_232925`; `SHA256SUMS` `11 -> 14`, `6.955.102 B` / `6,6329 MiB`)
  - `3` Arrays Phase 6A (`v = q`, Erstlauf): `results/general_tqv/` (`CA_122825`, `CA_192052`, `CA_542659`; `SHA256SUMS` `14 -> 17`, `33.644.446 B` / `32,0858 MiB`)
- **Deterministische Generatoren (`std`-only, ohne Suche, ohne OR-Tools):** [`scripts/phase7_reps_vq.py`](../../scripts/phase7_reps_vq.py), [`scripts/phase7_lift.py`](../../scripts/phase7_lift.py), [`scripts/gen_general_tqv.py`](../../scripts/gen_general_tqv.py); Zertifikat [`data/phase7/R_q11_m175.txt`](../../data/phase7/R_q11_m175.txt); Basis [`docs/PHASE7_ZUSCHNITT.md`](../../docs/PHASE7_ZUSCHNITT.md)
- **Tabellen-Referenz (`chrispbsmolen/ca-tools`, Live-Abgleich via `gh api`):** Commit `e673ab45758a3959710c662a34837f79f6add689` (`e673ab4`, `2026-11-26T06:17:26Z`); geprüft gegen `table/ca_frame.csv`, `table/ca_table.csv.gz` und `table/derived.csv` (einziger offener PR: `#89` `add-ca165-3-8-5`, `CA(165; 3, 8, 5)`, ohne Überschneidung).
- **Hardware (Zweitmaschine):** `Intel(R) Xeon(R) CPU @ 2.30GHz` (`2` vCPUs, AVX2, `7,8 GiB` RAM), `Python 3.12.16`, `gcc 13.3.0`. `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert (`verifiers/SHA256SUMS` `3/3 OK`, `verifiers/test_verifiers.py` `23/23 PASS`).
- **Selbsttest `scripts/pruefer/zaehler.c` (kompiliert nach `/tmp/zaehler`, `gcc -O3`, nicht committet):**
  - Positivkontrolle `results/phase7/CA_1044_3_11_9.txt` (`3 9 1044 11`): `N=1044 k=11 t=3 v=9 Spaltenmengen=165 davon_lueckenhaft=0 fehlende_Tupel=0 PASS` (`rc=0`).
  - Negativkontrolle Scratch-Kopie (`1043` Zeilen, letzte Zeile entfernt): `N=1043 k=11 t=3 v=9 Spaltenmengen=165 davon_lueckenhaft=108 fehlende_Tupel=108 FAIL` (`rc=1`).
- **SHA-256-Abgleich & Belegart (Regel 4 & 8):**
  - `20/20` Arrays mit Soll-SHA-256 (Claude `3267d87`, `#1–#14, #16, #17, #19, #21–#23`): lokal `2×` deterministisch byte-identisch (`cmp -s` `20/20 PASS`) und **`20/20` byte-identisch gegen `3267d87`** (rechnerunabhängig bestätigt mit demselben Skript auf zweiter Maschine).
  - `3/3` Phase-6A-Erstläufe (`#15 CA_122825`, `#18 CA_192052`, `#20 CA_542659`): lokal `2×` deterministisch byte-identisch (`cmp -s` `3/3 PASS`); Zweitmaschinen-Abgleich folgt.
  - Alle Tabellenvergleiche gelten als **„kleiner als `ca-tools` am Commit `e673ab4`“**. Kein Push nach `Justus42/ca-tools`, keine externe Einreichung.

---

## 1. Live-Abgleich gegen `chrispbsmolen/ca-tools @ e673ab4` (`23/23`)

| # | Zelle `(t, k, v)` | `q` | Herkunft | `N` | `ca_frame` (`k >=`) | `ca_table` (`k >=`) | `derived` (`k >=`) | Tier | Delta vs. `e673ab4` |
| :---: | :---: | :---: | --- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `(3, 13, 10)` | `11` | Bauart §14 | `1.727` | `1.760` (`k=13`) | `1.760` (`k=13`) | `5.289` (`k=629`) | `VERIFIED` | **`−33`** |
| 2 | `(3, 13, 11)` | `11` | Löserliste | `1.925` | `1.991` (`k=13`) | `1.991` (`k=13`) | `10.461` (`k=20726`) | `VERIFIED` | **`−66`** |
| 3 | `(3, 15, 12)` | `13` | Bauart §14 | `2.912` | `2.955` (`k=15`) | `2.955` (`k=15`) | `8.747` (`k=912`) | `VERIFIED` | **`−43`** |
| 4 | `(3, 21, 17)` | `19` | Bauart §14 | `8.854` | `9.376` (`k=21`) | `9.376` (`k=21`) | `34.017` (`k=26602`) | `VERIFIED` | **`−522`** |
| 5 | `(3, 21, 18)` | `19` | Bauart §14 | `9.443` | `9.830` (`k=21`) | `9.830` (`k=21`) | `20.537` (`k=446`) | `VERIFIED` | **`−387`** |
| 6 | `(4, 13, 10)` | `11` | Bauart §14 | `18.997` | `20.383` (`k=13`) | `20.383` (`k=13`) | `58.529` (`k=114`) | `VERIFIED` | **`−1.386`** |
| 7 | `(4, 13, 11)` | `11` | Löserliste | `21.175` | `21.901` (`k=13`) | `21.901` (`k=13`) | `379.080` (`k=11000`) | `VERIFIED` | **`−726`** |
| 8 | `(4, 15, 12)` | `13` | Bauart §14 | `37.856` | `40.476` (`k=15`) | `40.476` (`k=15`) | `114.203` (`k=145`) | `VERIFIED` | **`−2.620`** |
| 9 | `(3, 27, 21)` | `25` | Bauart §14 | `19.025` | `19.052` (`k=27`) | `19.052` (`k=27`) | `48.595` (`k=3137`) | `CITED` | **`−27`** |
| 10 | `(4, 18, 14)` | `16` | Bauart §14 | `82.432` | `82.993` (`k=18`) | `82.993` (`k=18`) | `126.929` (`k=25`) | `CITED` | **`−561`** |
| 11 | `(4, 19, 14)` | `17` | Bauart §14 | `99.416` | `106.023` (`k=19`) | `106.023` (`k=19`) | `126.929` (`k=25`) | `VERIFIED` | **`−6.607`** |
| 12 | `(4, 19, 15)` | `17` | Bauart §14 | `106.063` | `110.273` (`k=19`) | `110.273` (`k=19`) | `250.557` (`k=145`) | `VERIFIED` | **`−4.210`** |
| 13 | `(4, 19, 16)` | `17` | Bauart §14 | `113.866` | `114.489` (`k=19`) | `114.489` (`k=19`) | `250.559` (`k=145`) | `VERIFIED` | **`−623`** |
| 14 | `(5, 13, 10)` | `11` | Bauart §14 | `208.967` | `224.844` (`k=13`) | `224.844` (`k=13`) | `1.288.329` (`k=463`) | `VERIFIED` | **`−15.877`** |
| 15 | `(4, 19, 17)` | `17` | Phase 6A | `122.825` | `125.137` (`k=19`) | `125.137` (`k=19`) | `1.753.920` (`k=15000`) | `VERIFIED` | **`−2.312`** |
| 16 | `(5, 13, 11)` | `11` | Löserliste | `232.925` | `240.911` (`k=13`) | `240.911` (`k=13`) | `6.736.170` (`k=11000`) | `VERIFIED` | **`−7.986`** |
| 17 | `(4, 21, 18)` | `19` | Bauart §14 | `179.417` | `188.412` (`k=21`) | `188.412` (`k=21`) | `390.959` (`k=181`) | `VERIFIED` | **`−8.995`** |
| 18 | `(4, 21, 19)` | `19` | Phase 6A | `192.052` | `195.301` (`k=21`) | `195.301` (`k=21`) | `2.476.080` (`k=100000`) | `VERIFIED` | **`−3.249`** |
| 19 | `(5, 15, 12)` | `13` | Bauart §14 | `492.128` | `527.205` (`k=15`) | `527.205` (`k=15`) | `2.227.751` (`k=192`) | `VERIFIED` | **`−35.077`** |
| 20 | `(5, 15, 13)` | `13` | Phase 6A | `542.659` | `555.841` (`k=15`) | `555.841` (`k=15`) | `5.272.345` (`k=1008`) | `VERIFIED` | **`−13.182`** |
| 21 | `(4, 25, 20)` | `23` | Bauart §14 | `351.785` | `382.933` (`k=25`) | `382.933` (`k=25`) | `839.515` (`k=265`) | `VERIFIED` | **`−31.148`** |
| 22 | `(4, 25, 21)` | `23` | Bauart §14 | `370.300` | `390.612` (`k=25`) | `390.612` (`k=25`) | `839.517` (`k=265`) | `CITED` | **`−20.312`** |
| 23 | `(4, 27, 20)` | `25` | Bauart §14 | `456.250` | `507.412` (`k=27`) | `507.412` (`k=27`) | `839.515` (`k=265`) | `VERIFIED` | **`−51.162`** |

Ergebnis: **`23/23` kleiner als `ca-tools` am Commit `e673ab4`** in allen drei Tabellen (`ca_frame.csv`, `ca_table.csv.gz`, `derived.csv`).

---

## 2. Laufzeit- & Budget-Übersicht (`23` Arrays, getrennt nach Erstlauf / Repro / Verifikation)

Alle Befehle liefen unter externem `timeout --kill-after=10s <SECS>`.

- **Erstlauf-Summe Generierung (`23` Arrays):** `50,380 s` (Gruppe 1: `14,814 s`, Gruppe 2: `35,566 s`)
- **Reproduktions-Summe Generierung (2. Lauf, `cmp -s` `23/23 PASS`):** `51,620 s` (Gruppe 1: `14,674 s`, Gruppe 2: `36,946 s`)
- **Gruppe 1 (`#1–#16`, Dual-Verifikation `verifiers/ca_verify` + `verifiers/verify_independent.py`):**
  - `verifiers/ca_verify` (`timeout 60`): Positiv `14,968 s` (`16/16 PASS`, `rc=0`), Negativkontrolle `14,099 s` (`16/16 FAIL`, `rc=1`)
  - `verifiers/verify_independent.py` (`timeout 120` für `#1–#9`, `timeout 450` für `#10–#16`; `#10–#16` Positiv/Negativ paarweise parallel auf 2 Kernen): Positiv CPU-Summe `1034,991 s` (`16/16 PASS`, `rc=0`), Negativkontrolle CPU-Summe `1041,207 s` (`16/16 FAIL`, `rc=1`)
  - Aktive Wall-Clock Gruppe 1: `1153,923 s`
- **Gruppe 2 (`#17–#23`, zwei unabhängige C-Verifier: `verifiers/ca_verify` [2 Threads] + `/tmp/zaehler`):**
  - `verifiers/ca_verify` (`timeout 300`, 2 Threads): Positiv `156,039 s` (`7/7 PASS`, `rc=0`), Negativkontrolle `151,775 s` (`7/7 FAIL`, `rc=1`)
  - `/tmp/zaehler` (`timeout 300`): Positiv `198,376 s` (`7/7 PASS`, `rc=0`), Negativkontrolle `199,328 s` (`7/7 FAIL`, `rc=1`)
  - `verifiers/verify_independent.py`: **`nicht gelaufen (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap)`** (`7/7` nicht gestartet)
  - Aktive Wall-Clock Gruppe 2: `780,594 s`
- **Aktive Pipeline-Wall-Clock gesamt (`#1–#23`):** `1934,517 s`

---

## 3. Einzelergebnisse Gruppe 1 (`#1–#16`, volle Dual-Verifikation)

| # | Datei (Pfad) | Zelle `(t, k, v)` | Erstlauf / Repro (`cmp -s`, Soll-SHA `3267d87`) | Größe (Bytes / MiB) | `ca_verify` (`60s`) | `verify_independent.py` (`120s`/`450s`) | Negativkontrolle (`N - 1` Zeilen, `ca` / `py`) | SHA-256 |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| 1 | `results/phase7_vq/CA_1727_3_13_10.txt` | `(3, 13, 10)` | `0,158 s` / `0,144 s` (`PASS`, exakt) | `44.902 B` (`0,0428 MiB`) | `PASS` (`rc=0`, `0,008 s`) | `PASS` (`rc=0`, `0,152 s`) | `ca FAIL` (`rc=1`, `0,007 s`), `py FAIL` (`rc=1`, `0,154 s`; 116 of 286 column sets have gaps (116 missing tuples total)) | `98e5906a59dc0e0f4aef4a32c2841ce71e0b0c56b2f8aac6728f6a08851f36ec` |
| 2 | `results/phase7/CA_1925_3_13_11.txt` | `(3, 13, 11)` | `0,088 s` / `0,087 s` (`PASS`, exakt) | `52.294 B` (`0,0499 MiB`) | `PASS` (`rc=0`, `0,008 s`) | `PASS` (`rc=0`, `0,162 s`) | `ca FAIL` (`rc=1`, `0,008 s`), `py FAIL` (`rc=1`, `0,171 s`; 221 of 286 column sets have gaps (221 missing tuples total)) | `94bfc0a39c0fd523ef5474125487cdb7577148bce1097bf064b2a1b405cff764` |
| 3 | `results/phase7_vq/CA_2912_3_15_12.txt` | `(3, 15, 12)` | `0,175 s` / `0,165 s` (`PASS`, exakt) | `93.912 B` (`0,0896 MiB`) | `PASS` (`rc=0`, `0,011 s`) | `PASS` (`rc=0`, `0,301 s`) | `ca FAIL` (`rc=1`, `0,012 s`), `py FAIL` (`rc=1`, `0,303 s`; 116 of 455 column sets have gaps (116 missing tuples total)) | `9f41ef45a18fe5b773cd309a5b253632dd09d1b548a50d37a3408e1fcb67fb84` |
| 4 | `results/phase7_vq/CA_8854_3_21_17.txt` | `(3, 21, 17)` | `0,280 s` / `0,293 s` (`PASS`, exakt) | `439.812 B` (`0,4194 MiB`) | `PASS` (`rc=0`, `0,049 s`) | `PASS` (`rc=0`, `2,585 s`) | `ca FAIL` (`rc=1`, `0,050 s`), `py FAIL` (`rc=1`, `2,508 s`; 355 of 1330 column sets have gaps (355 missing tuples total)) | `8df731279c7495d533b1a729ef7eded790824de82d224a8c874ffc623208bb28` |
| 5 | `results/phase7_vq/CA_9443_3_21_18.txt` | `(3, 21, 18)` | `0,285 s` / `0,289 s` (`PASS`, exakt) | `479.028 B` (`0,4568 MiB`) | `PASS` (`rc=0`, `0,058 s`) | `PASS` (`rc=0`, `3,215 s`) | `ca FAIL` (`rc=1`, `0,057 s`), `py FAIL` (`rc=1`, `3,210 s`; 553 of 1330 column sets have gaps (553 missing tuples total)) | `e3cd323a0881232338651f910687a81fda8c5401a2dc03863f7c1dff428416ec` |
| 6 | `results/phase7_vq/CA_18997_4_13_10.txt` | `(4, 13, 10)` | `0,335 s` / `0,343 s` (`PASS`, exakt) | `493.922 B` (`0,4710 MiB`) | `PASS` (`rc=0`, `0,044 s`) | `PASS` (`rc=0`, `3,892 s`) | `ca FAIL` (`rc=1`, `0,042 s`), `py FAIL` (`rc=1`, `3,873 s`; 203 of 715 column sets have gaps (203 missing tuples total)) | `2bd4886415f8f1c4871ebb7aeaa3ed4e9fcba272cfc8407bd0fa789cbe4bc3a8` |
| 7 | `results/phase7/CA_21175_4_13_11.txt` | `(4, 13, 11)` | `0,282 s` / `0,284 s` (`PASS`, exakt) | `575.234 B` (`0,5486 MiB`) | `PASS` (`rc=0`, `0,049 s`) | `PASS` (`rc=0`, `4,593 s`) | `ca FAIL` (`rc=1`, `0,050 s`), `py FAIL` (`rc=1`, `4,429 s`; 520 of 715 column sets have gaps (520 missing tuples total)) | `ca50246466727ad7c7980fc344c3a237da6b4f3ac465d6e736af61c09ac526a1` |
| 8 | `results/phase7_vq/CA_37856_4_15_12.txt` | `(4, 15, 12)` | `0,592 s` / `0,590 s` (`PASS`, exakt) | `1.220.856 B` (`1,1643 MiB`) | `PASS` (`rc=0`, `0,135 s`) | `PASS` (`rc=0`, `16,896 s`) | `ca FAIL` (`rc=1`, `0,134 s`), `py FAIL` (`rc=1`, `16,889 s`; 67 of 1365 column sets have gaps (67 missing tuples total)) | `b5d916c34d0bd89988578fca51179ad6e9b6439e1db67b1611eae2ce3138abf0` |
| 9 | `results/phase7_vq/CA_19025_3_27_21.txt` | `(3, 27, 21)` | `0,535 s` / `0,567 s` (`PASS`, exakt) | `1.253.625 B` (`1,1955 MiB`) | `PASS` (`rc=0`, `0,228 s`) | `PASS` (`rc=0`, `12,969 s`) | `ca FAIL` (`rc=1`, `0,222 s`), `py FAIL` (`rc=1`, `13,126 s`; 790 of 2925 column sets have gaps (790 missing tuples total)) | `77f289f1638481979bb10b3b4e96f73c745ab73be00fb7364a3c4e59380d2d78` |
| 10 | `results/phase7_vq/CA_82432_4_18_14.txt` | `(4, 18, 14)` | `1,279 s` / `1,262 s` (`PASS`, exakt) | `3.334.656 B` (`3,1802 MiB`) | `PASS` (`rc=0`, `0,596 s`) | `PASS` (`rc=0`, `83,994 s`) | `ca FAIL` (`rc=1`, `0,620 s`), `py FAIL` (`rc=1`, `84,185 s`; 686 of 3060 column sets have gaps (686 missing tuples total)) | `dcf37e8dabdadfefb8237cddd7b1e2f80df715b54e054f2e94fa5d721ad8ba53` |
| 11 | `results/phase7_vq/CA_99416_4_19_14.txt` | `(4, 19, 14)` | `1,619 s` / `1,594 s` (`PASS`, exakt) | `4.221.712 B` (`4,0261 MiB`) | `PASS` (`rc=0`, `0,958 s`) | `PASS` (`rc=0`, `119,267 s`) | `ca FAIL` (`rc=1`, `0,995 s`), `py FAIL` (`rc=1`, `118,842 s`; 466 of 3876 column sets have gaps (466 missing tuples total)) | `881f8187a6f2c4dbd2022cff25a1742a1a39b62bd6672ad89ef4965ef63acbfb` |
| 12 | `results/phase7_vq/CA_106063_4_19_15.txt` | `(4, 19, 15)` | `1,712 s` / `1,727 s` (`PASS`, exakt) | `4.617.353 B` (`4,4035 MiB`) | `PASS` (`rc=0`, `1,159 s`) | `PASS` (`rc=0`, `136,599 s`) | `ca FAIL` (`rc=1`, `1,134 s`), `py FAIL` (`rc=1`, `131,427 s`; 690 of 3876 column sets have gaps (690 missing tuples total)) | `6db6dbf97f4b0b644ed2e5907432c2f852e5c96bcb68aaa7b891ae8f604ac776` |
| 13 | `results/phase7_vq/CA_113866_4_19_16.txt` | `(4, 19, 16)` | `1,887 s` / `1,847 s` (`PASS`, exakt) | `5.078.308 B` (`4,8431 MiB`) | `PASS` (`rc=0`, `1,401 s`) | `PASS` (`rc=0`, `150,101 s`) | `ca FAIL` (`rc=1`, `1,343 s`), `py FAIL` (`rc=1`, `151,216 s`; 985 of 3876 column sets have gaps (985 missing tuples total)) | `53b0db39d2a010f7642c3e873a65e5d9ad6d1c10aec8a2dcaebbdfa8e97d688c` |
| 14 | `results/phase7_vq/CA_208967_5_13_10.txt` | `(5, 13, 10)` | `2,389 s` / `2,367 s` (`PASS`, exakt) | `5.433.142 B` (`5,1814 MiB`) | `PASS` (`rc=0`, `3,376 s`) | `PASS` (`rc=0`, `121,483 s`) | `ca FAIL` (`rc=1`, `3,272 s`), `py FAIL` (`rc=1`, `118,620 s`; 6 of 1287 column sets have gaps (6 missing tuples total)) | `591fedf245e1a8fd2c982010ce2af7595df04b180b05258a951dd2b09912881c` |
| 15 | `results/general_tqv/CA_122825_4_19_17.txt` | `(4, 19, 17)` | `0,449 s` / `0,481 s` (`PASS`, Erstlauf (ohne Soll)) | `5.608.045 B` (`5,3482 MiB`) | `PASS` (`rc=0`, `1,731 s`) | `PASS` (`rc=0`, `223,857 s`) | `ca FAIL` (`rc=1`, `1,652 s`), `py FAIL` (`rc=1`, `229,975 s`; 816 of 3876 column sets have gaps (816 missing tuples total)) | `cbf2db9954edd1ecdcd6c7bd3541aaf6aa2ad900b53c04dd7cb071f143bba6fb` |
| 16 | `results/phase7/CA_232925_5_13_11.txt` | `(5, 13, 11)` | `2,747 s` / `2,633 s` (`PASS`, exakt) | `6.327.574 B` (`6,0344 MiB`) | `PASS` (`rc=0`, `5,159 s`) | `PASS` (`rc=0`, `154,925 s`) | `ca FAIL` (`rc=1`, `4,501 s`), `py FAIL` (`rc=1`, `162,280 s`; 897 of 1287 column sets have gaps (897 missing tuples total)) | `5377d6557520b44d651499f47cb31dff443aecacb6b2906cf0be4076d3b94cea` |

---

## 4. Einzelergebnisse Gruppe 2 (`#17–#23`, `ca_verify` + `/tmp/zaehler`; `verify_independent.py` nicht gelaufen)

| # | Datei (Pfad) | Zelle `(t, k, v)` | Erstlauf / Repro (`cmp -s`, Soll-SHA `3267d87`) | Größe (Bytes / MiB) | `ca_verify` (`300s`, 2T) | `/tmp/zaehler` (`300s`) | `verify_independent.py` | Negativkontrolle (`N - 1` Zeilen, `ca` / `zaehler`) | SHA-256 |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | --- | --- | --- |
| 17 | `results/phase7_vq/CA_179417_4_21_18.txt` | `(4, 21, 18)` | `3,202 s` / `4,543 s` (`PASS`, exakt) | `9.101.532 B` (`8,6799 MiB`) | `PASS` (`rc=0`, `4,348 s`) | `PASS` (`rc=0`, `7,473 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `4,184 s`), `zaehler FAIL` (`rc=1`, `7,495 s`; 1797/5985 Sets, 1797 fehlende Tupel) | `36d945d874fb6c3b87be4c3f24931256dd9d2d0f026ac0684414ab85e55833b3` |
| 18 | `results/general_tqv/CA_192052_4_21_19.txt` | `(4, 21, 19)` | `0,735 s` / `0,710 s` (`PASS`, Erstlauf (ohne Soll)) | `9.944.106 B` (`9,4834 MiB`) | `PASS` (`rc=0`, `4,457 s`) | `PASS` (`rc=0`, `5,763 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `4,526 s`), `zaehler FAIL` (`rc=1`, `5,744 s`; 1140/5985 Sets, 1140 fehlende Tupel) | `7da2d494c677f7dfc7b5c122c1799101440bb0aabb87fdc07d9b571521896cc3` |
| 19 | `results/phase7_vq/CA_492128_5_15_12.txt` | `(5, 15, 12)` | `6,254 s` / `6,296 s` (`PASS`, exakt) | `15.871.128 B` (`15,1359 MiB`) | `PASS` (`rc=0`, `30,331 s`) | `PASS` (`rc=0`, `15,230 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `29,818 s`), `zaehler FAIL` (`rc=1`, `14,056 s`; 243/3003 Sets, 243 fehlende Tupel) | `240b6c938f6b87088ccebaa50515ebc7e8b8468f07cb03db08259cc731c05028` |
| 20 | `results/general_tqv/CA_542659_5_15_13.txt` | `(5, 15, 13)` | `1,599 s` / `1,578 s` (`PASS`, Erstlauf (ohne Soll)) | `18.092.295 B` (`17,2542 MiB`) | `PASS` (`rc=0`, `40,173 s`) | `PASS` (`rc=0`, `10,147 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `37,828 s`), `zaehler FAIL` (`rc=1`, `11,344 s`; 1001/3003 Sets, 1001 fehlende Tupel) | `1a78674e85083dcc37b8c27db839e6254c9eed2ca1b46f00f382219b991b0508` |
| 21 | `results/phase7_vq/CA_351785_4_25_20.txt` | `(4, 25, 20)` | `6,974 s` / `6,996 s` (`PASS`, exakt) | `21.404.398 B` (`20,4128 MiB`) | `PASS` (`rc=0`, `19,904 s`) | `PASS` (`rc=0`, `41,051 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `19,770 s`), `zaehler FAIL` (`rc=1`, `40,943 s`; 5836/12650 Sets, 5836 fehlende Tupel) | `43a09235850184dbf7e568339fa9edba0db7d060721a2654f380524b39217f3c` |
| 22 | `results/phase7_vq/CA_370300_4_25_21.txt` | `(4, 25, 21)` | `7,273 s` / `7,175 s` (`PASS`, exakt) | `22.917.338 B` (`21,8557 MiB`) | `PASS` (`rc=0`, `21,678 s`) | `PASS` (`rc=0`, `41,349 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `20,980 s`), `zaehler FAIL` (`rc=1`, `40,017 s`; 7200/12650 Sets, 7200 fehlende Tupel) | `edd06b3b669e7fb1994f69d6d225f16556aaed0b37cdbd188157c50063154d83` |
| 23 | `results/phase7_vq/CA_456250_4_27_20.txt` | `(4, 27, 20)` | `9,529 s` / `9,646 s` (`PASS`, exakt) | `29.587.500 B` (`28,2168 MiB`) | `PASS` (`rc=0`, `35,147 s`) | `PASS` (`rc=0`, `77,363 s`) | `nicht gelaufen` (geschätzte Laufzeit > 350 s / 10-Min.-Shell-Cap) | `ca FAIL` (`rc=1`, `34,670 s`), `zaehler FAIL` (`rc=1`, `79,730 s`; 2926/17550 Sets, 2926 fehlende Tupel) | `d70e6fdae82ca64c92d0d19a26af8c8e48bee392af1a64131ad70007215971ff` |

---

## 5. Gemessene Paketgröße (`37` Einreichungskandidaten)

Exakte unkomprimierte Dateigrößen aller `37` Einreichungskandidaten aus [`docs/PHASE7_ZUSCHNITT.md`](../../docs/PHASE7_ZUSCHNITT.md) (`14` bestehende Dateien in `results/phase7/`, `results/general_tqv/`, `results/t4_nearbush/` + `23` neue Dateien):

- **Summe `14` bestehende Dateien:** `32.837.076 Bytes` (`31,3159 MiB`)
- **Summe `23` neue Dateien:** `166.192.672 Bytes` (`158,4937 MiB`)
- **Gesamtsumme aller `37` Dateien:** **`199.029.748 Bytes`** (**`189,8096 MiB`**) — **unter `200 MiB`** (`209.715.200 Bytes`; verbleibender Spielraum: `10.685.452 Bytes` = `10,1904 MiB`)
- **Größte Einzeldatei:** `results/phase7_vq/CA_456250_4_27_20.txt` (`(4, 27, 20)`) mit **`29.587.500 Bytes`** (**`28,2168 MiB`**) — **unter `50 MiB`** (`52.428.800 Bytes`)
- **Prüfung auf `(4, 27, 21)` (`q = 25, m = 761, N = 475.625, k = 27`, nicht erzeugt):**
  - Selbst die absolute Untergrenze bei ausschließlich einstelligen Einträgen (`2 Bytes/Eintrag`: `475.625 * 27 * 2 = 25.683.750 Bytes` = `24,4939 MiB`) übersteigt den verbleibenden Spielraum (`10.685.452 Bytes` = `10,1904 MiB`) um mehr als `14,3 MiB`.
  - Schätzung bei Gleichverteilung (`2,5238 Bytes/Eintrag`): `32.410.446 Bytes` (`30,9090 MiB`); skaliert mit realer Byte-Dichte von `(4, 25, 21)` (`2,4755 Bytes/Eintrag`): `31.790.612 Bytes` (`30,3179 MiB`).
  - **Befund:** `(4, 27, 21)` passt **nicht** mehr zusätzlich unter `200 MiB` (`37` Dateien bilden das exakte Maximum innerhalb `200 MiB`).

| Rang | Zelle `(t, k, v)` | Herkunft | Status | Datei | Größe (Bytes) | Größe (MiB) |
| :---: | :---: | --- | --- | --- | :---: | :---: |
| 1 | `(3, 11, 9)` | Löserliste | bestehend | `results/phase7/CA_1044_3_11_9.txt` | `22.968` | `0,0219 MiB` |
| 2 | `(3, 13, 10)` | Bauart §14 | neu #1 | `results/phase7_vq/CA_1727_3_13_10.txt` | `44.902` | `0,0428 MiB` |
| 3 | `(3, 13, 11)` | Löserliste | neu #2 | `results/phase7/CA_1925_3_13_11.txt` | `52.294` | `0,0499 MiB` |
| 4 | `(5, 7, 5)` | Löserliste | bestehend | `results/phase7/CA_4250_5_7_5.txt` | `59.500` | `0,0567 MiB` |
| 5 | `(4, 9, 7)` | Löserliste | bestehend | `results/phase7/CA_3332_4_9_7.txt` | `59.976` | `0,0572 MiB` |
| 6 | `(3, 15, 12)` | Bauart §14 | neu #3 | `results/phase7_vq/CA_2912_3_15_12.txt` | `93.912` | `0,0896 MiB` |
| 7 | `(3, 15, 13)` | Phase 6A | bestehend | `results/general_tqv/CA_3211_3_15_13.txt` | `107.055` | `0,1021 MiB` |
| 8 | `(4, 10, 8)` | Löserliste | bestehend | `results/phase7/CA_5824_4_10_8.txt` | `116.480` | `0,1111 MiB` |
| 9 | `(4, 11, 9)` | Löserliste | bestehend | `results/phase7/CA_9396_4_11_9.txt` | `206.712` | `0,1971 MiB` |
| 10 | `(5, 9, 7)` | Löserliste | bestehend | `results/phase7/CA_23324_5_9_7.txt` | `419.832` | `0,4004 MiB` |
| 11 | `(3, 21, 17)` | Bauart §14 | neu #4 | `results/phase7_vq/CA_8854_3_21_17.txt` | `439.812` | `0,4194 MiB` |
| 12 | `(3, 21, 18)` | Bauart §14 | neu #5 | `results/phase7_vq/CA_9443_3_21_18.txt` | `479.028` | `0,4568 MiB` |
| 13 | `(4, 13, 10)` | Bauart §14 | neu #6 | `results/phase7_vq/CA_18997_4_13_10.txt` | `493.922` | `0,4710 MiB` |
| 14 | `(3, 21, 19)` | Phase 6A | bestehend | `results/general_tqv/CA_10108_3_21_19.txt` | `523.374` | `0,4991 MiB` |
| 15 | `(4, 13, 11)` | Löserliste | neu #7 | `results/phase7/CA_21175_4_13_11.txt` | `575.234` | `0,5486 MiB` |
| 16 | `(5, 10, 8)` | Löserliste | bestehend | `results/phase7/CA_46592_5_10_8.txt` | `931.840` | `0,8887 MiB` |
| 17 | `(4, 15, 12)` | Bauart §14 | neu #8 | `results/phase7_vq/CA_37856_4_15_12.txt` | `1.220.856` | `1,1643 MiB` |
| 18 | `(3, 27, 21)` | Bauart §14 | neu #9 | `results/phase7_vq/CA_19025_3_27_21.txt` | `1.253.625` | `1,1955 MiB` |
| 19 | `(4, 15, 13)` | Phase 6A | bestehend | `results/t4_nearbush/CA_41743_4_15_13.txt` | `1.391.715` | `1,3272 MiB` |
| 20 | `(5, 11, 9)` | Löserliste | bestehend | `results/phase7/CA_84564_5_11_9.txt` | `1.860.408` | `1,7742 MiB` |
| 21 | `(6, 9, 7)` | Löserliste | bestehend | `results/phase7/CA_163268_6_9_7.txt` | `2.938.824` | `2,8027 MiB` |
| 22 | `(4, 18, 14)` | Bauart §14 | neu #10 | `results/phase7_vq/CA_82432_4_18_14.txt` | `3.334.656` | `3,1802 MiB` |
| 23 | `(4, 19, 14)` | Bauart §14 | neu #11 | `results/phase7_vq/CA_99416_4_19_14.txt` | `4.221.712` | `4,0261 MiB` |
| 24 | `(4, 19, 15)` | Bauart §14 | neu #12 | `results/phase7_vq/CA_106063_4_19_15.txt` | `4.617.353` | `4,4035 MiB` |
| 25 | `(4, 19, 16)` | Bauart §14 | neu #13 | `results/phase7_vq/CA_113866_4_19_16.txt` | `5.078.308` | `4,8431 MiB` |
| 26 | `(5, 13, 10)` | Bauart §14 | neu #14 | `results/phase7_vq/CA_208967_5_13_10.txt` | `5.433.142` | `5,1814 MiB` |
| 27 | `(4, 19, 17)` | Phase 6A | neu #15 | `results/general_tqv/CA_122825_4_19_17.txt` | `5.608.045` | `5,3482 MiB` |
| 28 | `(5, 13, 11)` | Löserliste | neu #16 | `results/phase7/CA_232925_5_13_11.txt` | `6.327.574` | `6,0344 MiB` |
| 29 | `(6, 10, 8)` | Löserliste | bestehend | `results/phase7/CA_372736_6_10_8.txt` | `7.454.720` | `7,1094 MiB` |
| 30 | `(4, 21, 18)` | Bauart §14 | neu #17 | `results/phase7_vq/CA_179417_4_21_18.txt` | `9.101.532` | `8,6799 MiB` |
| 31 | `(4, 21, 19)` | Phase 6A | neu #18 | `results/general_tqv/CA_192052_4_21_19.txt` | `9.944.106` | `9,4834 MiB` |
| 32 | `(5, 15, 12)` | Bauart §14 | neu #19 | `results/phase7_vq/CA_492128_5_15_12.txt` | `15.871.128` | `15,1359 MiB` |
| 33 | `(6, 11, 9)` | Löserliste | bestehend | `results/phase7/CA_761076_6_11_9.txt` | `16.743.672` | `15,9680 MiB` |
| 34 | `(5, 15, 13)` | Phase 6A | neu #20 | `results/general_tqv/CA_542659_5_15_13.txt` | `18.092.295` | `17,2542 MiB` |
| 35 | `(4, 25, 20)` | Bauart §14 | neu #21 | `results/phase7_vq/CA_351785_4_25_20.txt` | `21.404.398` | `20,4128 MiB` |
| 36 | `(4, 25, 21)` | Bauart §14 | neu #22 | `results/phase7_vq/CA_370300_4_25_21.txt` | `22.917.338` | `21,8557 MiB` |
| 37 | `(4, 27, 20)` | Bauart §14 | neu #23 | `results/phase7_vq/CA_456250_4_27_20.txt` | `29.587.500` | `28,2168 MiB` |

---

## 6. Reproduktions- und Prüfkommandos

```bash
# Gruppe 1 (#1-#16) + Gruppe 2 (#17-#23): Erzeugung
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 11 10 /tmp/R_q11_v10.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --v 10 --reps /tmp/R_q11_v10.txt --check-m --t 3 --out results/phase7_vq/CA_1727_3_13_10.txt
timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --reps data/phase7/R_q11_m175.txt --check-m --t 3 --out results/phase7/CA_1925_3_13_11.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 13 12 /tmp/R_q13_v12.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 13 --v 12 --reps /tmp/R_q13_v12.txt --check-m --t 3 --out results/phase7_vq/CA_2912_3_15_12.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 19 17 /tmp/R_q19_v17.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 19 --v 17 --reps /tmp/R_q19_v17.txt --check-m --t 3 --out results/phase7_vq/CA_8854_3_21_17.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 19 18 /tmp/R_q19_v18.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 19 --v 18 --reps /tmp/R_q19_v18.txt --check-m --t 3 --out results/phase7_vq/CA_9443_3_21_18.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 11 10 /tmp/R_q11_v10.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --v 10 --reps /tmp/R_q11_v10.txt --check-m --t 4 --out results/phase7_vq/CA_18997_4_13_10.txt
timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --reps data/phase7/R_q11_m175.txt --check-m --t 4 --out results/phase7/CA_21175_4_13_11.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 13 12 /tmp/R_q13_v12.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 13 --v 12 --reps /tmp/R_q13_v12.txt --check-m --t 4 --out results/phase7_vq/CA_37856_4_15_12.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 25 21 /tmp/R_q25_v21.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 25 --v 21 --reps /tmp/R_q25_v21.txt --check-m --t 3 --out results/phase7_vq/CA_19025_3_27_21.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 16 14 /tmp/R_q16_v14.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 16 --v 14 --reps /tmp/R_q16_v14.txt --check-m --t 4 --out results/phase7_vq/CA_82432_4_18_14.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 17 14 /tmp/R_q17_v14.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 17 --v 14 --reps /tmp/R_q17_v14.txt --check-m --t 4 --out results/phase7_vq/CA_99416_4_19_14.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 17 15 /tmp/R_q17_v15.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 17 --v 15 --reps /tmp/R_q17_v15.txt --check-m --t 4 --out results/phase7_vq/CA_106063_4_19_15.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 17 16 /tmp/R_q17_v16.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 17 --v 16 --reps /tmp/R_q17_v16.txt --check-m --t 4 --out results/phase7_vq/CA_113866_4_19_16.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 11 10 /tmp/R_q11_v10.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --v 10 --reps /tmp/R_q11_v10.txt --check-m --t 5 --out results/phase7_vq/CA_208967_5_13_10.txt
timeout --kill-after=10s 120 python3 scripts/gen_general_tqv.py --t 4 --q 17 --v 17 --out results/general_tqv/CA_122825_4_19_17.txt
timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 11 --reps data/phase7/R_q11_m175.txt --check-m --t 5 --out results/phase7/CA_232925_5_13_11.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 19 18 /tmp/R_q19_v18.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 19 --v 18 --reps /tmp/R_q19_v18.txt --check-m --t 4 --out results/phase7_vq/CA_179417_4_21_18.txt
timeout --kill-after=10s 120 python3 scripts/gen_general_tqv.py --t 4 --q 19 --v 19 --out results/general_tqv/CA_192052_4_21_19.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 13 12 /tmp/R_q13_v12.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 13 --v 12 --reps /tmp/R_q13_v12.txt --check-m --t 5 --out results/phase7_vq/CA_492128_5_15_12.txt
timeout --kill-after=10s 120 python3 scripts/gen_general_tqv.py --t 5 --q 13 --v 13 --out results/general_tqv/CA_542659_5_15_13.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 23 20 /tmp/R_q23_v20.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 23 --v 20 --reps /tmp/R_q23_v20.txt --check-m --t 4 --out results/phase7_vq/CA_351785_4_25_20.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 23 21 /tmp/R_q23_v21.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 23 --v 21 --reps /tmp/R_q23_v21.txt --check-m --t 4 --out results/phase7_vq/CA_370300_4_25_21.txt
timeout --kill-after=10s 30 python3 scripts/phase7_reps_vq.py 25 20 /tmp/R_q25_v20.txt && timeout --kill-after=10s 120 python3 scripts/phase7_lift.py --q 25 --v 20 --reps /tmp/R_q25_v20.txt --check-m --t 4 --out results/phase7_vq/CA_456250_4_27_20.txt

# Verifikation Gruppe 1 (#1-#16): ca_verify + verify_independent.py
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_1727_3_13_10.txt 3 10 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_1727_3_13_10.txt 3 10 -n 1727 -k 13
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_1925_3_13_11.txt 3 11 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7/CA_1925_3_13_11.txt 3 11 -n 1925 -k 13
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_2912_3_15_12.txt 3 12 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_2912_3_15_12.txt 3 12 -n 2912 -k 15
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_8854_3_21_17.txt 3 17 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_8854_3_21_17.txt 3 17 -n 8854 -k 21
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_9443_3_21_18.txt 3 18 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_9443_3_21_18.txt 3 18 -n 9443 -k 21
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_18997_4_13_10.txt 4 10 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_18997_4_13_10.txt 4 10 -n 18997 -k 13
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_21175_4_13_11.txt 4 11 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7/CA_21175_4_13_11.txt 4 11 -n 21175 -k 13
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_37856_4_15_12.txt 4 12 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_37856_4_15_12.txt 4 12 -n 37856 -k 15
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_19025_3_27_21.txt 3 21 && timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/phase7_vq/CA_19025_3_27_21.txt 3 21 -n 19025 -k 27
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_82432_4_18_14.txt 4 14 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7_vq/CA_82432_4_18_14.txt 4 14 -n 82432 -k 18
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_99416_4_19_14.txt 4 14 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7_vq/CA_99416_4_19_14.txt 4 14 -n 99416 -k 19
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_106063_4_19_15.txt 4 15 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7_vq/CA_106063_4_19_15.txt 4 15 -n 106063 -k 19
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_113866_4_19_16.txt 4 16 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7_vq/CA_113866_4_19_16.txt 4 16 -n 113866 -k 19
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7_vq/CA_208967_5_13_10.txt 5 10 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7_vq/CA_208967_5_13_10.txt 5 10 -n 208967 -k 13
timeout --kill-after=10s 60 ./verifiers/ca_verify results/general_tqv/CA_122825_4_19_17.txt 4 17 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/general_tqv/CA_122825_4_19_17.txt 4 17 -n 122825 -k 19
timeout --kill-after=10s 60 ./verifiers/ca_verify results/phase7/CA_232925_5_13_11.txt 5 11 && timeout --kill-after=10s 450 python3 verifiers/verify_independent.py results/phase7/CA_232925_5_13_11.txt 5 11 -n 232925 -k 13

# Verifikation Gruppe 2 (#17-#23): ca_verify + /tmp/zaehler (verify_independent.py nicht gelaufen)
timeout --kill-after=10s 30 gcc -O3 -o /tmp/zaehler scripts/pruefer/zaehler.c
timeout --kill-after=10s 300 ./verifiers/ca_verify results/phase7_vq/CA_179417_4_21_18.txt 4 18 2 && timeout --kill-after=10s 300 /tmp/zaehler results/phase7_vq/CA_179417_4_21_18.txt 4 18 179417 21
timeout --kill-after=10s 300 ./verifiers/ca_verify results/general_tqv/CA_192052_4_21_19.txt 4 19 2 && timeout --kill-after=10s 300 /tmp/zaehler results/general_tqv/CA_192052_4_21_19.txt 4 19 192052 21
timeout --kill-after=10s 300 ./verifiers/ca_verify results/phase7_vq/CA_492128_5_15_12.txt 5 12 2 && timeout --kill-after=10s 300 /tmp/zaehler results/phase7_vq/CA_492128_5_15_12.txt 5 12 492128 15
timeout --kill-after=10s 300 ./verifiers/ca_verify results/general_tqv/CA_542659_5_15_13.txt 5 13 2 && timeout --kill-after=10s 300 /tmp/zaehler results/general_tqv/CA_542659_5_15_13.txt 5 13 542659 15
timeout --kill-after=10s 300 ./verifiers/ca_verify results/phase7_vq/CA_351785_4_25_20.txt 4 20 2 && timeout --kill-after=10s 300 /tmp/zaehler results/phase7_vq/CA_351785_4_25_20.txt 4 20 351785 25
timeout --kill-after=10s 300 ./verifiers/ca_verify results/phase7_vq/CA_370300_4_25_21.txt 4 21 2 && timeout --kill-after=10s 300 /tmp/zaehler results/phase7_vq/CA_370300_4_25_21.txt 4 21 370300 25
timeout --kill-after=10s 300 ./verifiers/ca_verify results/phase7_vq/CA_456250_4_27_20.txt 4 20 2 && timeout --kill-after=10s 300 /tmp/zaehler results/phase7_vq/CA_456250_4_27_20.txt 4 20 456250 27
```
