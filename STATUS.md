# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Abschluss Phase 4 v3 auf Branch `exp/pgl-binary-ccl-v3`: **11 dual-verifizierte Rekord-Arrays** für `t=3`, `v=10 (k=15..18)`, `v=12 (k=19..20)` und `v=14 (k=20, 23..26)` gegen Live-Stand `chrispbsmolen/ca-tools` @ `7b08aef`; PR #3 für `exp/pgl-binary-ccl-v2` offen).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), vollständiges Verifikationslog siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md).

## 0. Governance- & Branch-Status

- **`main`-Sync:** PR #2 (`chore/sync-main-docs` → `main`) gemerged (`028828b`).
- **Offener PR:** PR #3 (`exp/pgl-binary-ccl-v2` @ `03e18aa` → `main`, erste 6 Rekorde `v=10/12`).
- **Abgeschlossene Such-Branches:**
  - `exp/ca-3-9-5` (`3ca3058`): **Abgeschlossen (Gate 1 ABORT)** — `G0-K1` PASS (`5,39 s`).
  - `exp/ca-3-k-6` (`8c210f2`): **Abgeschlossen (Gate 2 ABORT)** — `G0v6-3` PASS (`0,41 s`).
  - `exp/t3-target-scan` (`4bc62c4`): **Abgeschlossen (`P3-SCAN1`)** — `docs/TARGET_SCAN_t3.md`.
- **Aktiver Branch (`exp/pgl-binary-ccl-v3`, Phase 4 v3):** Zero-Dep Rust-Solver [`solvers/pgl_ccl_search`](solvers/pgl_ccl_search/) erweitert um `PGL(2,13)` (`v=14`, `2|G|=4368`, `91` Paare, bis `k=26`) sowie Post-Op-Module `reduce` (det. Greedy-Row-Deletion) und `complete` (Zero-Break-Repair + Greedy-Single-Row-Completion). **Gate 0 PASS (`v=6/10/12/14`)**, **Gate 1 PASS (11 dual-verifizierte Rekorde in `results/`)**.

## 1. Alle 11 dual-verifizierten Rekord-Ergebnisse (`results/`, Live-Stand `ca-tools` @ `7b08aef`)

Alle 11 Kandidaten bestehen `./verifiers/ca_verify` (`rc=0`) **und** `python3 verifiers/verify_independent.py` (`rc=0`); Checksummen siehe [`results/SHA256SUMS`](results/SHA256SUMS) (`22/22 OK`), Detail-Logs siehe [`results/VERIFICATION_LOG_pgl_ccl.md`](results/VERIFICATION_LOG_pgl_ccl.md). Deterministische Greedy-Row-Deletion (`P4-POSTOP`) bestätigte `saved=0` auf allen 11 Arrays (jede Zeile essentiell).

| Zelle `(3, k, v)` | Live-Rekord (`ca_table`) | Best `M` (`cc`) | Neu `N` | Delta | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
| :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **`(3, 15, 10)`** | `2205` (`VER`) | `14` (`1`) | **2070** | **−135** | `rc=0 (0,006s)` / `rc=0 (0,223s)` | `CA_2070_3_15_10.txt` (`78b0497f2c81b0f7…`) |
| **`(3, 16, 10)`** | `2205` (`VER`) | `15` (`1`) | **2115** | **−90** | `rc=0 (0,006s)` / `rc=0 (0,251s)` | `CA_2115_3_16_10.txt` (`4734fd80ffe90f11…`) |
| **`(3, 17, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | `rc=0 (0,006s)` / `rc=0 (0,281s)` | `CA_2160_3_17_10.txt` (`5e199bb6872a68d1…`) |
| **`(3, 18, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | `rc=0 (0,007s)` / `rc=0 (0,325s)` | `CA_2160_3_18_10.txt` (`410ccbcc821c8db4…`) |
| **`(3, 19, 12)`** | `3806` (`CIT`) | `16` (`1`) | **3696** | **−110** | `rc=0 (0,018s)` / `rc=0 (0,598s)` | `CA_3696_3_19_12.txt` (`2492d0f7e36a993d…`) |
| **`(3, 20, 12)`** | `3806` (`CIT`) | `17` (`1`) | **3762** | **−44** | `rc=0 (0,015s)` / `rc=0 (0,731s)` | `CA_3762_3_20_12.txt` (`6a85d1b1e34aec73…`) |
| **`(3, 20, 14)`** | `6006` (`CIT`) | `17` (`1`) | **5915** | **−91** | `rc=0 (0,023s)` / `rc=0 (1,450s)` | `CA_5915_3_20_14.txt` (`051a4841f551770f…`) |
| **`(3, 23, 14)`** | `6279` (`CIT`) | `19` (`1`) | **6097** | **−182** | `rc=0 (0,030s)` / `rc=0 (2,176s)` | `CA_6097_3_23_14.txt` (`3927e2d354e405ac…`) |
| **`(3, 24, 14)`** | `6279` (`CIT`) | `19` (`1`) | **6097** | **−182** | `rc=0 (0,031s)` / `rc=0 (2,539s)` | `CA_6097_3_24_14.txt` (`3abb40a4dcb501e3…`) |
| **`(3, 25, 14)`** | `6383` (`CIT`) | `20` (`1`) | **6188** | **−195** | `rc=0 (0,034s)` / `rc=0 (2,849s)` | `CA_6188_3_25_14.txt` (`41befba9ae17253c…`) |
| **`(3, 26, 14)`** | `6383` (`CIT`) | `20` (`1`) | **6188** | **−195** | `rc=0 (0,035s)` / `rc=0 (3,109s)` | `CA_6188_3_26_14.txt` (`2952b2efb82ae208…`) |

**Bestätigte Walls (`P4-V12-END` 170,5 s, `P4-V14-T1/PUSH` 272,4 s):**
- `v=12, k=21..22` (Live `3828`, `M_max=17`): `k=21 M=17` bleibt bei `unc=2 (cc=0) / 3 (cc=1)` (9,1M Züge), `k=22 M=17` bei `unc=8/10`; `zero_break_repairs=0` und `66` offene Tupel pro 2-sym-Slot erzwingen mind. `+66` Zusatzzeilen (`3762+66=3828`, nicht `< 3828`).
- `v=14, k=19` (Live `5255`) und `k=21..22` (Live `6006`): unterhalb `M_max=9` bzw. `17` unlösbar.
- `v=14, k=23..26`: scharfe binäre CCL-Walls bei `(23,18) unc=3..4`, `(24,18) unc=9..10`, `(25,19) unc=3..5`, `(26,19) unc=9..11`.

## 2. Ziel-Landkarte & Track-Status

| Track / Zelle | Live-Rekord | Status | Kurzfazit |
| --- | :---: | --- | --- |
| `(3, 9, 5)` / `(3, 13, 6)` | `185` / `490` | **Abgeschlossen (ABORT)** | Historische Phasen 2A–3C abgeschlossen |
| **`(3, 15..18, 10)` (`PGL(2,9)+CCL`)** | `2205 / 2232` | **4× REKORD DUAL-VERIFIZIERT** | **`2070 (−135)`, `2115 (−90)`, `2160 (−72)`, `2160 (−72)`** (`saved=0` Post-Op) |
| **`(3, 19..20, 12)` (`PGL(2,11)+CCL`)** | `3806` | **2× REKORD DUAL-VERIFIZIERT** | **`3696 (−110)`, `3762 (−44)`** (`k=16..18, 21..22` am binären CCL-Wall) |
| **`(3, 20, 23..26, 14)` (`PGL(2,13)+CCL`)** | `6006 / 6279 / 6383` | **5× REKORD DUAL-VERIFIZIERT** | **`5915 (−91)`, `6097 (−182)`, `6097 (−182)`, `6188 (−195)`, `6188 (−195)`** |
| **`v=17/18/20` (`PGL(2,16/17/19)+CCL`)** | offen | **Nächster Skalierungs-Track** | Gleiches `PGL(2,q)+CCL`-Prinzip auf höhere Primzahlpotenzen `q=16, 17, 19` oder Delete+Tabu-Repair-Post-Op auf `v=10` (`CA_2070`/`2115`) |
| `(4, 9, 3)` | `135` | Wartend | Benötigt `t=4`-Solver (`AGL(1,3)`-Orbits) |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Gate-Archiv:**
  - `exp/pgl-binary-ccl-v2`: Gate 0 PASS (`v=6/10/12`), Gate 1 PASS (6 Rekorde `v=10/12`), PR #3 offen.
  - `exp/pgl-binary-ccl-v3`: Post-Op `reduce`/`complete` geprüft (`saved=0` auf allen 11 Arrays), `PGL(2,13)` Gate 0 PASS (`v=14`) & Gate 1 PASS (5 weitere Rekorde `v=14`, gesamt **11 dual-verifizierte Rekord-Arrays** in `results/`).
