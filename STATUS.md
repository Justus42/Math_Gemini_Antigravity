# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Abschluss Phase 4 v4 auf Branch `exp/pgl-binary-ccl-v4`: **16 dual-verifizierte Pareto-Front-Rekord-Arrays** in `results/` — dominieren **23 Rekordzellen** auf `t=3` für `v=10 (k=15..18)`, `v=12 (k=19..20)`, `v=14 (k=20, 23..26)` und `v=20 (k=27..38)` gegen Live-Stand `chrispbsmolen/ca-tools` @ `7b08aef`; PR #4 für `v3` offen).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), vollständiges Verifikationslog siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md).

## 0. Governance- & Branch-Status

- **`main`-Sync:** PR #2 (`chore/sync-main-docs` → `main`) gemerged (`028828b`).
- **Offene PRs:** PR #3 (`exp/pgl-binary-ccl-v2`, 6 Rekorde) und PR #4 (`exp/pgl-binary-ccl-v3`, 11 Rekorde, ersetzt PR #3).
- **Aktiver Branch (`exp/pgl-binary-ccl-v4`, Phase 4 v4):** Zero-Dep Rust-Solver [`solvers/pgl_ccl_search`](solvers/pgl_ccl_search/) unterstützt alle 7 Gruppen `PGL(2,q)` für `q in {5, 9, 11, 13, 16, 17, 19}` (`GF(16) = GF(2)[x]/(x⁴+x+1)`), wiederverwendbaren Binär-CCL-Cache [`data/ccl_binary/`](data/ccl_binary/) (`16` verifizierte `C(M,k)`-Matrizen) und Post-Op (`reduce`/`complete`). **Gate 0 PASS (7/7 Gruppen)**, **Gate 1 PASS (16 dual-verifizierte Rekord-Arrays in `results/`, `9,6 MB`)**.

## 1. Alle 16 dual-verifizierten Rekord-Arrays (`results/`, Live-Stand `ca-tools` @ `7b08aef`)

Alle 16 Dateien bestehen `./verifiers/ca_verify` (`rc=0`) **und** `python3 verifiers/verify_independent.py` (`rc=0`); Checksummen siehe [`results/SHA256SUMS`](results/SHA256SUMS) (`32/32 OK`), Detail-Logs siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md).

| Zelle `(3, k, v)` | Live-Rekord (`ca_table`) | Best `M` (`cc`) | Neu `N` | Delta | Dominierte `k` (im Log) | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
| :---: | :---: | :---: | :---: | :---: | --- | :---: | --- |
| **`(3, 15, 10)`** | `2205` (`VER`) | `14` (`1`) | **2070** | **−135** | — | `0,006s` / `0,223s` | `CA_2070_3_15_10.txt` (`78b0497f…`) |
| **`(3, 16, 10)`** | `2205` (`VER`) | `15` (`1`) | **2115** | **−90** | — | `0,006s` / `0,251s` | `CA_2115_3_16_10.txt` (`4734fd80…`) |
| **`(3, 17, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | — | `0,006s` / `0,281s` | `CA_2160_3_17_10.txt` (`5e199bb6…`) |
| **`(3, 18, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | — | `0,007s` / `0,325s` | `CA_2160_3_18_10.txt` (`410ccbcc…`) |
| **`(3, 19, 12)`** | `3806` (`CIT`) | `16` (`1`) | **3696** | **−110** | — | `0,018s` / `0,598s` | `CA_3696_3_19_12.txt` (`2492d0f7…`) |
| **`(3, 20, 12)`** | `3806` (`CIT`) | `17` (`1`) | **3762** | **−44** | — | `0,015s` / `0,731s` | `CA_3762_3_20_12.txt` (`6a85d1b1…`) |
| **`(3, 20, 14)`** | `6006` (`CIT`) | `17` (`1`) | **5915** | **−91** | — | `0,023s` / `1,450s` | `CA_5915_3_20_14.txt` (`051a4841…`) |
| **`(3, 23, 14)`** | `6279` (`CIT`) | `19` (`1`) | **6097** | **−182** | — | `0,030s` / `2,176s` | `CA_6097_3_23_14.txt` (`3927e2d3…`) |
| **`(3, 24, 14)`** | `6279` (`CIT`) | `19` (`1`) | **6097** | **−182** | — | `0,031s` / `2,539s` | `CA_6097_3_24_14.txt` (`3abb40a4…`) |
| **`(3, 25, 14)`** | `6383` (`CIT`) | `20` (`1`) | **6188** | **−195** | — | `0,034s` / `2,849s` | `CA_6188_3_25_14.txt` (`41befba9…`) |
| **`(3, 26, 14)`** | `6383` (`CIT`) | `20` (`1`) | **6188** | **−195** | — | `0,035s` / `3,109s` | `CA_6188_3_26_14.txt` (`2952b2ef…`) |
| **`(3, 29, 20)`** | `18145` (`CIT`) | `21` (`1`) | **17670** | **−475** | `k=27,28` (`−266` vs `17936`) | `0,439s` / `14,419s` | `CA_17670_3_29_20.txt` (`739bf030…`) |
| **`(3, 32, 20)`** | `18145` (`CIT`) | `22` (`1`) | **17860** | **−285** | `k=30,31` (`−285` vs `18145`) | `0,522s` / `19,794s` | `CA_17860_3_32_20.txt` (`544735d3…`) |
| **`(3, 34, 20)`** | `18430` (`CIT`) | `23` (`1`) | **18050** | **−380** | `k=33` (`−380` vs `18430`) | `0,374s` / `24,601s` | `CA_18050_3_34_20.txt` (`9224fbac…`) |
| **`(3, 35, 20)`** | `18677` (`CIT`) | `23` (`0`) | **18070** | **−607** | — | `0,405s` / `27,935s` | `CA_18070_3_35_20.txt` (`8751d063…`) |
| **`(3, 38, 20)`** | `18753` (`CIT`) | `24` (`1`) | **18240** | **−513** | `k=36` (`−437`), `k=37` (`−513`) | `0,458s` / `33,304s` | `CA_18240_3_38_20.txt` (`68678d1c…`) |

## 2. Ziel-Landkarte & Scan-Befunde (`v=17, 18, 20, 24`)

| Track / `v` | Gruppe | Status | Kurzfazit |
| --- | --- | --- | --- |
| **`v=10` (`k=15..18`)** | `PGL(2,9)` | **4× REKORD DUAL-VERIFIZIERT** | `2070 (−135)`, `2115 (−90)`, `2160 (−72)`, `2160 (−72)` (`saved=0` Post-Op) |
| **`v=12` (`k=19..20`)** | `PGL(2,11)` | **2× REKORD DUAL-VERIFIZIERT** | `3696 (−110)`, `3762 (−44)` (`k=21..22` Wall `M=17`, `unc=2/8`) |
| **`v=14` (`k=20, 23..26`)** | `PGL(2,13)` | **5× REKORD DUAL-VERIFIZIERT** | `5915 (−91)`, `6097 (−182)`×2, `6188 (−195)`×2 |
| `v=17` (`k=19..32`) | `PGL(2,16)` | **Gate 0 PASS / Skip Gate 1** | `v=17` ist Primzahl (`OA(17³)`+CK ergibt `9537` bis `k=36`, `M_max=10` unlösbar) |
| `v=18` (`k=25..34`) | `PGL(2,17)` | **Gate 0 PASS / Wall `M=20`** | Live `12866..12908` erfordert `M <= 20`; `k=27 M=20` extrem nahe (`unc=1` in 40 s), `k=28 M=20` `unc=4/6` |
| **`v=20` (`k=27..38`)** | `PGL(2,19)` | **5× PARETO-REKORD (12 ZELLEN)** | **`17670..18240` (`−266` bis `−607`)**; Near-Misses `unc=1` bei `(27,20)` und `(33,22 cc=0)` |
| `v=24` (`k=31..46`) | `PGL(2,23)` | **In `ca-tools` vorhanden (eng)** | `M_max=17` (`k=31..32`) bzw. `M_max=20` (`k=33..46`, Live `29883..29929`) — `M=20` bereits bei `k=27` am Wall |
| `v=15, 21, 22` / `t=4` | — | **Nächste Optionen** | Nicht-Primzahlpotenzen `v=q+1` mit `q=25 (v=26)`, `q=27 (v=28)`, oder Delete+Tabu-Repair-Post-Op auf `v=10` (`CA_2070/2115`), oder Submission-Paket für `ca-tools` |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Gate-Archiv:**
  - `exp/pgl-binary-ccl-v2`: 6 Rekorde (`v=10, 12`), PR #3.
  - `exp/pgl-binary-ccl-v3`: 11 Rekorde (`v=10, 12, 14`), PR #4.
  - `exp/pgl-binary-ccl-v4`: Gate 0 PASS (`q=16, 17, 19`), Gate 1 PASS (`338,3 s <= 360 s`, 5 neue `v=20`-Pareto-Front-Rekorde → gesamt **16 dual-verifizierte Rekord-Arrays**, **23 verbesserte Zellen**).
