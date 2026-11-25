# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Phase 4 Gate 0 & Gate 1 auf Branch `exp/pgl-binary-ccl`: **6 dual-verifizierte Rekord-Arrays** für `t=3, v=10 (k=15..18)` und `t=3, v=12 (k=19..20)` gegen Live-Stand `chrispbsmolen/ca-tools` @ `7b08aef`).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), vollständiges Verifikationslog siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md).

## 0. Governance- & Branch-Status

- **`main`-Sync:** PR #2 (`chore/sync-main-docs` → `main`) bereits gemerged (`028828b`).
- **Abgeschlossene Such-Branches:**
  - `exp/ca-3-9-5` (`3ca3058`): **Abgeschlossen (Gate 1 ABORT)** — `G0-K1` PASS (`5,39 s`), Stagnation auf `(3, 9, 5)` (`2D`: 24/60 Orbits, 93 unc).
  - `exp/ca-3-k-6` (`8c210f2`): **Abgeschlossen (Gate 2 ABORT)** — `G0v6-3` PASS (`0,41 s`), `PSL(2,5)`/`PGL(2,5)` auf `(3, 13, 6)` für `N <= 486` ausgereizt.
  - `exp/t3-target-scan` (`4bc62c4`): **Abgeschlossen (`P3-SCAN1`)** — systematischer `t=3` Target-Scan (`docs/TARGET_SCAN_t3.md`).
- **Aktiver Branch (`exp/pgl-binary-ccl`, Phase 4):** Zero-Dep Rust-Solver [`solvers/pgl_ccl_search`](solvers/pgl_ccl_search/) (2 deterministische `PGL(2,q)`-Orbits + allgemeine binäre CCL-Matrix über `v(v-1)/2` orientierte Paare mit `--cover-const`). **Gate 0 PASS**, **Gate 1 PASS (6 neue dual-verifizierte Rekorde in `results/`)**.

## 1. Dual-verifizierte Rekord-Ergebnisse Phase 4 (`results/`, Live-Stand `ca-tools` @ `7b08aef`)

Alle 6 Kandidaten bestehen `./verifiers/ca_verify` (`rc=0`) **und** `python3 verifiers/verify_independent.py` (`rc=0`); Checksummen siehe [`results/SHA256SUMS`](results/SHA256SUMS), Detail-Logs siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md).

| Zelle `(3, k, v)` | Live-Rekord (`ca_table`) | Best `M` (`cc`) | Neu `N` | Delta | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
| :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **`(3, 15, 10)`** | `2205` (`VER`) | `14` (`1`) | **2070** | **−135** | `rc=0 (0,006s)` / `rc=0 (0,223s)` | `CA_2070_3_15_10.txt` (`78b0497f2c81b0f7…`) |
| **`(3, 16, 10)`** | `2205` (`VER`) | `15` (`1`) | **2115** | **−90** | `rc=0 (0,006s)` / `rc=0 (0,251s)` | `CA_2115_3_16_10.txt` (`4734fd80ffe90f11…`) |
| **`(3, 17, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | `rc=0 (0,006s)` / `rc=0 (0,281s)` | `CA_2160_3_17_10.txt` (`5e199bb6872a68d1…`) |
| **`(3, 18, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | `rc=0 (0,007s)` / `rc=0 (0,325s)` | `CA_2160_3_18_10.txt` (`410ccbcc821c8db4…`) |
| **`(3, 19, 12)`** | `3806` (`CIT`) | `16` (`1`) | **3696** | **−110** | `rc=0 (0,018s)` / `rc=0 (0,598s)` | `CA_3696_3_19_12.txt` (`2492d0f7e36a993d…`) |
| **`(3, 20, 12)`** | `3806` (`CIT`) | `17` (`1`) | **3762** | **−44** | `rc=0 (0,015s)` / `rc=0 (0,731s)` | `CA_3762_3_20_12.txt` (`6a85d1b1e34aec73…`) |

**Offene Walls aus Gate 1 (`P4-T1`, `P4-T2`, `P4-PUSH`, Gesamtbudget `460,5 s <= 480 s`):**
- `v=12, k=16..18` (Live `3564 / 3615 / 3647`): erfordern `M <= 13 / 14 / 15`; binäre CCL-Walls liegen bei `(16,14) unc=6`, `(17,15) unc=3`, `(18,15) unc=12`.
- `v=12, k=21..22` (Live `3828`): erfordern `M <= 17`; extrem nahe Near-Misses bei `(21,17) unc=2 (cc=0) / 3 (cc=1)` und `(22,17) unc=6`, sowie `(20,16) unc=2 (cc=0)` und `(17,15) unc=3 (cc=1)` — potenziell mit SAT/ILP oder längerem Spezial-Push (bzw. Row-Deletion-Post-Op auf den neuen Rekord-Arrays!) weiter drückbar.

## 2. Ziel-Landkarte & Track-Status

| Track / Zelle | Live-Rekord | Status | Kurzfazit |
| --- | :---: | --- | --- |
| `(3, 9, 5)` (`exp/ca-3-9-5`) | **185** | **Abgeschlossen (Gate 1 ABORT)** | Einzelzell-Tabu/SA beendet (`G0-K1` PASS `5,39 s`) |
| `(3, 13, 6)` (`exp/ca-3-k-6`) | **490** | **Abgeschlossen (Gate 2 ABORT)** | `PSL(2,5)`/`PGL(2,5)` für `N <= 486` ausgereizt (`G0v6-3` PASS `0,41 s`) |
| **`(3, 15..18, 10)` (`PGL(2,9)+CCL`)** | **2205 / 2232** | **4× REKORD DUAL-VERIFIZIERT** | **`2070 (−135)`, `2115 (−90)`, `2160 (−72)`, `2160 (−72)`** in `results/` abgelegt |
| **`(3, 19..20, 12)` (`PGL(2,11)+CCL`)** | **3806** | **2× REKORD DUAL-VERIFIZIERT** | **`3696 (−110)`, `3762 (−44)`** in `results/` abgelegt; `k=16..18` & `21..22` am binären CCL-Wall (`unc=2..6`) |
| **`(3, 20..26, 14)` (`PGL(2,13)+CCL`)** | **6006–6383** | **Nächster Hochpotenzial-Track** | `2*|PGL(2,13)| = 4368`, Schritt `91`: bereits `M=16..17` aus Phase 4 liefert sofort `5824/5915` für `k=19..20` (`−182/−91` unter `6006`), `k=23..26` mit `M=18..19` bis `−360`! |
| `(4, 9, 3)` | **135** | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Gate-Archiv:**
  - `exp/ca-3-9-5`: Gate 0 PASS (`G0-K1` `CA(165; 3, 8, 5)` in `5,39 s`), Gate 1 ABORT (`2D-1..3`).
  - `exp/ca-3-k-6`: Gate 0 PASS (`G0v6-3` `CA(396; 3, 10, 6)` in `0,41 s`), Gate 2 ABORT (`3C-1`/`3C-2`).
  - `exp/t3-target-scan`: Target-Scan `P3-SCAN1` PASS (`docs/TARGET_SCAN_t3.md`).
  - `exp/pgl-binary-ccl`: Gate 0 PASS (`P4-G0`, `v=6/10/12` E2E), Gate 1 PASS (`P4-T1/T2/PUSH`, 6 dual-verifizierte Rekord-Arrays in `results/`).
