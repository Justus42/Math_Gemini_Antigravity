# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-24 (Abschluss Phase 4 Gate 0 & Gate 1 auf Branch `exp/pgl-binary-ccl`: **4 dual-verifizierte Weltrekord-Arrays** unter [`results/`](results/) mit Verbesserungen auf **6 Zielzellen**).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md).

## 0. Governance- & Branch-Status

- **`main`-Sync:** PR [#2](https://github.com/Justus42/Math_Gemini_Antigravity/pull/2) (`chore/sync-main-docs` → `main`) angelegt (noch offen zur Review/Merge).
- **Abgeschlossene Such-Branches:**
  - `exp/ca-3-9-5` (`3ca3058`): **Abgeschlossen (Gate 1 ABORT)** — `G0-K1` PASS (`5,39 s`), Stagnation auf `(3, 9, 5)` (`2D`: 24/60 Orbits, 93 unc).
  - `exp/ca-3-k-6` (`8c210f2`): **Abgeschlossen (Gate 2 ABORT)** — `G0v6-3` PASS (`0,41 s`), `PSL(2,5)`/`PGL(2,5)` auf `(3, 13, 6)` für `N <= 486` ausgereizt.
  - `exp/t3-target-scan` (`4bc62c4`): **Abgeschlossen (Target-Scan PASS)** — [`docs/TARGET_SCAN_t3.md`](docs/TARGET_SCAN_t3.md).
- **Aktive Phase (`exp/pgl-binary-ccl`, abgezweigt von `4bc62c4`):**
  - Neuer Zero-Dep-Rust-Solver [`solvers/pgl_ccl_search`](solvers/pgl_ccl_search/): 2 deterministische `PGL(2,q)`-Orbits + allgemeine binäre CCL-Matrix (`M x k`) über `v*(v-1)/2` orientierte Paare mit `--cover-const` (spart alle `v` Konstantzeilen).
  - **Gate 0 PASS** (alle 3 Gruppen `PGL(2,5)`, `PGL(2,9)`, `PGL(2,11)` E2E dual-verifiziert).
  - **Gate 1 PASS** (7,98 min Gesamtsuchzeit): **4 dual-verifizierte Weltrekord-Arrays** in [`results/`](results/) (unterbieten 6 Live-Rekordzellen in `chrispbsmolen/ca-tools` @ `7b08aef`, `2026-11-25T03:31:22Z`).

## 1. Phase-4-Ergebnisse: Dual-verifizierte Rekorde (`results/`)

Abgleich gegen Live-Tabelle `chrispbsmolen/ca-tools` (`table/ca_table.csv.gz` @ `7b08aef`, `2026-11-25T03:31:22Z`):

| Zelle `(3, k, v)` | Live-Rekord `N_rec` (`tier`) | Best `M` (`cc`) | Neu `N` | `ΔN` | Artefakt (`results/`) & SHA-256 (Array `.txt`) | Dual-Verify |
| :---: | :---: | :---: | :---: | :---: | --- | :---: |
| **`(3, 15, 10)`** | 2205 (`VERIFIED`) | `14` (`true`) | **2070** | **−135** | `CA_2070_3_15_10.txt` (`8e32a9ea67a9c9da8f98459707e0d206afe7b42ce43d939e0184303fe62a163a`) | `C:0.00s` / `Py:0.20s` |
| **`(3, 16, 10)`** | 2205 (`VERIFIED`) | `15` (`true`) | **2115** | **−90** | `CA_2115_3_16_10.txt` (`22629bbbd13cc8460c5dda428e8f45dc252410ee24c25bdbef99aaaa35e45b79`) | `C:0.00s` / `Py:0.19s` |
| **`(3, 17, 10)`** | 2232 (`CITED`) | `16` (`true`, via `k=18`) | **2160** | **−72** | via `CA_2160_3_18_10.txt` (`k=17 M=15` bei `unc=3` offen) | via `k=18` |
| **`(3, 18, 10)`** | 2232 (`CITED`) | `16` (`true`) | **2160** | **−72** | `CA_2160_3_18_10.txt` (`9a73777a7a794134fccfa3f3cd67463058a644b92891dd43c9c709114edcc005`) | `C:0.00s` / `Py:0.27s` |
| **`(3, 19, 12)`** | 3806 (`CITED`) | `17` (`true`, via `k=20`) | **3762** | **−44** | via `CA_3762_3_20_12.txt` (`k=19 M=16` bei **`unc=1`** offen!) | via `k=20` |
| **`(3, 20, 12)`** | 3806 (`CITED`) | `17` (`true`) | **3762** | **−44** | `CA_3762_3_20_12.txt` (`cde99c963702767b9c22e661c6e916fb53932ff3dc4da1b1342a59e207e91de3`) | `C:0.01s` / `Py:0.66s` |
| `(3, 21, 12)` | 3828 (`CITED`) | `17` (`unc=3`) | — | — | Heißer Kandidat (`N=3762`, −66) bei `unc=3` nach 50 s | n/a |
| `(3, 22, 12)` | 3828 (`CITED`) | `17` (`unc=7`) | — | — | `N=3762`/`3774` nach 35 s bei `unc=10`/`7` | n/a |
| `(3, 16..18, 12)` | 3564–3647 (`CITED`) | `M=13..15` | — | — | Wand (`unc=30 / 19 / 11`) — benötigt kleineres `M` als binäre CCL-Schwelle | n/a |

## 2. Ziel-Landkarte & nächste Hebel

| Track / Zelle | Live-Rekord | Status | Kurzfazit / nächster Hebel |
| --- | :---: | --- | --- |
| **`(3, 15..18, 10)` (`PGL(2,9)`)** | **2205 / 2232** | **4× REKORD VERIFIZIERT** | **`2070` (−135), `2115` (−90), `2160` (−72)** dual-verifiziert; nächster Hebel: `k=17 M=15` (`unc=3` → `2115`, −117) oder Post-op Row-Deletion auf `2070/2115/2160` |
| **`(3, 19..22, 12)` (`PGL(2,11)`)** | **3806 / 3828** | **2× REKORD VERIFIZIERT** | **`3762` (−44) für `k=19,20`** dual-verifiziert; heißeste offene Stufen: **`k=19 M=16` (`unc=1` → `3696`, −110)** und **`k=21 M=17` (`unc=3` → `3762`, −66)** |
| `(3, 20..26, 14)` (`PGL(2,13)`) | **6006–6383** | Erweiterter Horizont | Gleiche `PGL(2,13)` + Bin-CCL-Architektur (`2*2184 = 4368`, Schritt `91`): `M=17` (`k=20`) liefert sofort **`5915` (−91)** ohne neue Suche! |
| `(3, 9, 5)` / `(3, 13, 6)` | **185 / 490** | Abgeschlossen | Gate 1 / Gate 2 ABORT auf früheren Branches |

## 3. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Resultat-Integrität:** `sha256sum -c results/SHA256SUMS` 8/8 OK (4 kanonische Arrays + 4 kompakte Binär-CCL-Matrizen + 4 vollständige Dual-Verify-Logs).
- **Gate-Archiv:**
  - `exp/ca-3-9-5`: Gate 0 PASS (`G0-K1` `5,39 s`), Gate 1 ABORT (`2D-1..3`).
  - `exp/ca-3-k-6`: Gate 0 PASS (`G0v6-3` `0,41 s`), Gate 2 ABORT (`3C-1`/`3C-2`).
  - `exp/t3-target-scan`: Target-Scan `P3-SCAN1` PASS (`docs/TARGET_SCAN_t3.md`).
  - `exp/pgl-binary-ccl`: **Gate 0 PASS** (`P4-G0`, `0,001–0,017 s` über `q=5,9,11`), **Gate 1 PASS** (4 dual-verifizierte Rekord-Arrays in `results/`).
