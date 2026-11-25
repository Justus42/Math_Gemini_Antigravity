# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Branch `chore/ca-tools-submission-prep`: `RULES.md` um Abschnitt *Meldung nach außen* ergänzt; alle 23 Zellen gegen `table/ca_table.csv.gz`, `table/ca_frame.csv` und `table/derived.csv` @ `7b08aef` geprüft [23/23 strikt kleiner, 0 offene PRs]; 13/13 deterministische SHA-256-Reproduktion in [`submission/REPRODUCE.md`](submission/REPRODUCE.md) bestätigt; Regel-4/8-Sprachaudit durchgeführt).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), Audit-Paket siehe [`submission/MANIFEST.md`](submission/MANIFEST.md).

## 0. Governance- & Branch-Status

- **Gemergte PRs:** PR #1 (`phase-1-setup`), PR #2 (`chore/sync-main-docs`), PR #3 (`exp/pgl-binary-ccl-v2`), PR #4 (`exp/pgl-binary-ccl-v3`).
- **Offene PRs:** PR #5 (`exp/pgl-binary-ccl-v4`) und PR #6 (`exp/pgl-binary-ccl-v5` @ `1e1c60c`, enthält & ersetzt PR #5).
- **Aktiver Branch (`chore/ca-tools-submission-prep` — noch kein PR bis Abschluss Deep Research):**
  - `RULES.md` um `## Meldung nach außen` (Punkte 1–8) erweitert; keinerlei Schreibzugriff auf Fremd-Repos.
  - **Checkliste Meldung nach außen (`RULES.md` Punkt 2):**
    - `2a` (Tabellen-Check @ `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a`): **PASS** — `table/ca_table.csv.gz` 23/23, `table/ca_frame.csv` 23/23, `table/derived.csv` 23/23 strikt kleiner (`submission/CA_TOOLS_FORMAT.md`).
    - `2b` (Offene PRs & Issues `ca-tools`): **PASS** — 0 offene PRs.
    - `2c` (Literaturprüfung in `docs/`): **OFFEN** (`[LITERATURE_ATTRIBUTION_TBD]`).
    - `2d` (Drittprüfung durch unabhängiges Programm/Modell): **OFFEN** (`[THIRD_PARTY_VERIFICATION_TBD]`).
    - `2e` (Deterministische Reproduktion & SHA-256-Vergleich): **PASS** — 13/13 byte-identische Übereinstimmung aus `data/ccl_binary/` nach `/tmp/repro_check/` (`submission/REPRODUCE.md`).
  - Lokales Staging [`submission/ca_tools_staging/`](submission/ca_tools_staging/) (`8,7 MB`, 13 Pareto-Arrays, `claims.csv` gegen 82 `references.csv`-IDs geprüft, `HOW.md` mit `AI tools used: yes`) + [`submission/PR_DRAFT.md`](submission/PR_DRAFT.md) (Regel-4-geprüft, Platzhalter `[REAL_NAME_TBD]`/`[LITERATURE_ATTRIBUTION_TBD]` markiert).

## 1. Pareto-Front der 13 Arrays (kleiner als `ca-tools` @ `7b08aef` auf 23 Zellen)

Frisch dual-verifiziert am `2026-11-25` durch [`submission/verify_all.sh`](submission/verify_all.sh) (`xargs -P 2`); vollständige Checksummen in [`results/SHA256SUMS`](results/SHA256SUMS) (`32/32 OK`) und [`submission/records.csv`](submission/records.csv).

| Zelle `(3, k, v)` | `ca_table` (`7b08aef`) | `derived.csv` | Best `M` (`cc`) | Array `N` | Delta vs `ca_table` | Abgedeckte `k` | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **`(3, 15, 10)`** | `2205` (`VER`) | `2178` | `14` (`1`) | **2070** | −135 | `15` | `0,008s` / `0,208s` | `CA_2070_3_15_10.txt` (`78b0497f…`) |
| **`(3, 16, 10)`** | `2205` (`VER`) | `2178` | `15` (`1`) | **2115** | −90 | `16` | `0,006s` / `0,238s` | `CA_2115_3_16_10.txt` (`4734fd80…`) |
| **`(3, 18, 10)`** | `2232` (`CIT`) | — | `16` (`1`) | **2160** | −72 | `17..18` | `0,008s` / `0,320s` | `CA_2160_3_18_10.txt` (`410ccbcc…`) |
| **`(3, 19, 12)`** | `3806` (`CIT`) | — | `16` (`1`) | **3696** | −110 | `19` | `0,017s` / `0,610s` | `CA_3696_3_19_12.txt` (`2492d0f7…`) |
| **`(3, 20, 12)`** | `3806` (`CIT`) | — | `17` (`1`) | **3762** | −44 | `20` | `0,018s` / `0,763s` | `CA_3762_3_20_12.txt` (`6a85d1b1…`) |
| **`(3, 20, 14)`** | `6006` (`CIT`) | `6193` | `17` (`1`) | **5915** | −91 | `20` | `0,028s` / `1,400s` | `CA_5915_3_20_14.txt` (`051a4841…`) |
| **`(3, 24, 14)`** | `6279` (`CIT`) | `6193` | `19` (`1`) | **6097** | −182 | `23..24` | `0,036s` / `2,424s` | `CA_6097_3_24_14.txt` (`3abb40a4…`) |
| **`(3, 26, 14)`** | `6383` (`CIT`) | — | `20` (`1`) | **6188** | −195 | `25..26` | `0,042s` / `3,266s` | `CA_6188_3_26_14.txt` (`2952b2ef…`) |
| **`(3, 29, 20)`** | `18145` (`CIT`) | `18487` | `21` (`1`) | **17670** | −475 | `27..29` *(k=27,28: −266)* | `0,394s` / `14,072s` | `CA_17670_3_29_20.txt` (`739bf030…`) |
| **`(3, 32, 20)`** | `18145` (`CIT`) | `18487` | `22` (`1`) | **17860** | −285 | `30..32` | `0,448s` / `19,324s` | `CA_17860_3_32_20.txt` (`544735d3…`) |
| **`(3, 34, 20)`** | `18430` (`CIT`) | `18487` | `23` (`1`) | **18050** | −380 | `33..34` | `0,352s` / `23,294s` | `CA_18050_3_34_20.txt` (`9224fbac…`) |
| **`(3, 35, 20)`** | `18677` (`CIT`) | `18487` | `23` (`0`) | **18070** | −607 | `35` | `0,427s` / `25,272s` | `CA_18070_3_35_20.txt` (`8751d063…`) |
| **`(3, 38, 20)`** | `18753` (`CIT`) | `18563` | `24` (`1`) | **18240** | −513 | `36..38` *(k=36: −437)* | `0,451s` / `33,373s` | `CA_18240_3_38_20.txt` (`68678d1c…`) |

*(Zusätzlich 3 projizierte Begleitdateien aus v2/v3 in `results/` — `CA_2160_3_17_10.txt`, `CA_6097_3_23_14.txt`, `CA_6188_3_25_14.txt` — werden gemäß Regel 3 nicht eingereicht; Gesamtgröße `results/`: `9,5 MB`.)*

## 2. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Gate-Archiv:**
  - `exp/pgl-binary-ccl-v2`..`v4`: Gate 0 PASS (7/7 `PGL(2,q)`), Gate 1 PASS (13 dual-verifizierte Pareto-Front-Arrays kleiner als `ca-tools` @ `7b08aef` auf 23 Zellen, 16 `C(M,k)`-Startmatrizen in `data/ccl_binary/`).
  - `exp/pgl-binary-ccl-v5`: `cc=0`-Snipe abgeschlossen (`hits=[]`), `tabu_reduce` 10k-Sanity PASS & Pilot abgeschlossen (`saved=0`), vollständiger Audit (`verify_all.sh` 16/16 PASS).
  - `chore/ca-tools-submission-prep`: `RULES.md` erweitert, Punkt 2a (3 Tabellen-Dateien 23/23) & Punkt 2e (13/13 SHA-256-Reproduktion) PASS, Regel-4/8-Sprachaudit abgeschlossen.
