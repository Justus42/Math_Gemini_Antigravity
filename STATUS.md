# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Abschluss `chore/ca-tools-submission-prep`: Read-Only-Format-Audit von `chrispbsmolen/ca-tools` @ `7b08aef` [0 offene PRs, **23/23 Zellen frei**], Staging-Verzeichnis [`submission/ca_tools_staging/`](submission/ca_tools_staging/) [`8,7 MB`, 13 Pareto-Arrays], [`submission/CA_TOOLS_FORMAT.md`](submission/CA_TOOLS_FORMAT.md) und [`submission/PR_DRAFT.md`](submission/PR_DRAFT.md); PR #6 für `v5` offen).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), Audit-Paket siehe [`submission/MANIFEST.md`](submission/MANIFEST.md).

## 0. Governance- & Branch-Status

- **Gemergte PRs:** PR #1 (`phase-1-setup`), PR #2 (`chore/sync-main-docs`), PR #3 (`exp/pgl-binary-ccl-v2`), PR #4 (`exp/pgl-binary-ccl-v3`).
- **Offene PRs:** PR #5 (`exp/pgl-binary-ccl-v4`) und PR #6 (`exp/pgl-binary-ccl-v5` @ `1e1c60c`, enthält & ersetzt PR #5).
- **Aktiver Branch (`chore/ca-tools-submission-prep`):**
  - Read-Only-Analyse `chrispbsmolen/ca-tools` @ `7b08aef` (keinerlei Schreibzugriff auf Fremd-Repos): **alle 23/23 Zellen weiterhin frei**, 0 offene PRs, exakte `claims.csv`-/`HOW.md`-/`ai_tools`-Regeln dokumentiert in [`submission/CA_TOOLS_FORMAT.md`](submission/CA_TOOLS_FORMAT.md).
  - Lokales Staging-Paket [`submission/ca_tools_staging/`](submission/ca_tools_staging/) (`claims.csv` gegen 82 `references.csv`-IDs geprüft, `HOW.md` inkl. `AI tools used: yes`, 13 byte-identische Pareto-Arrays = `8,7 MB`) + PR-Entwurf [`submission/PR_DRAFT.md`](submission/PR_DRAFT.md) (mit `[LITERATURE_ATTRIBUTION_TBD]` & `[REAL_NAME_TBD]`).
  - Frischer Komplett-Audit [`submission/verify_all.sh`](submission/verify_all.sh): **16/16 `FORMAT_OK` & `DUAL_PASS`**, `verifiers/SHA256SUMS` 3/3 OK, `test_verifiers.py` 23/23 PASS.

## 1. Pareto-Front der 13 Rekord-Arrays (23 verbesserte Zellen, `ca-tools` @ `7b08aef`)

Frisch dual-verifiziert am `2026-11-25` durch [`submission/verify_all.sh`](submission/verify_all.sh) (`xargs -P 2`); vollständige Checksummen in [`results/SHA256SUMS`](results/SHA256SUMS) (`32/32 OK`) und [`submission/records.csv`](submission/records.csv).

| Zelle `(3, k, v)` | Live-Rekord (`ca_table`) | Best `M` (`cc`) | Neu `N` | Delta | Dominierte `k` | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **`(3, 15, 10)`** | `2205` (`VER`) | `14` (`1`) | **2070** | **−135** | `15` | `0,009s` / `0,208s` | `CA_2070_3_15_10.txt` (`78b0497f…`) |
| **`(3, 16, 10)`** | `2205` (`VER`) | `15` (`1`) | **2115** | **−90** | `16` | `0,007s` / `0,234s` | `CA_2115_3_16_10.txt` (`4734fd80…`) |
| **`(3, 18, 10)`** | `2232` (`CIT`) | `16` (`1`) | **2160** | **−72** | `17..18` | `0,007s` / `0,311s` | `CA_2160_3_18_10.txt` (`410ccbcc…`) |
| **`(3, 19, 12)`** | `3806` (`CIT`) | `16` (`1`) | **3696** | **−110** | `19` | `0,014s` / `0,600s` | `CA_3696_3_19_12.txt` (`2492d0f7…`) |
| **`(3, 20, 12)`** | `3806` (`CIT`) | `17` (`1`) | **3762** | **−44** | `20` | `0,015s` / `0,715s` | `CA_3762_3_20_12.txt` (`6a85d1b1…`) |
| **`(3, 20, 14)`** | `6006` (`CIT`) | `17` (`1`) | **5915** | **−91** | `20` | `0,027s` / `1,434s` | `CA_5915_3_20_14.txt` (`051a4841…`) |
| **`(3, 24, 14)`** | `6279` (`CIT`) | `19` (`1`) | **6097** | **−182** | `23..24` | `0,035s` / `2,484s` | `CA_6097_3_24_14.txt` (`3abb40a4…`) |
| **`(3, 26, 14)`** | `6383` (`CIT`) | `20` (`1`) | **6188** | **−195** | `25..26` | `0,039s` / `3,064s` | `CA_6188_3_26_14.txt` (`2952b2ef…`) |
| **`(3, 29, 20)`** | `18145` (`CIT`) | `21` (`1`) | **17670** | **−475** | `27..29` *(k=27,28: −266)* | `0,403s` / `13,713s` | `CA_17670_3_29_20.txt` (`739bf030…`) |
| **`(3, 32, 20)`** | `18145` (`CIT`) | `22` (`1`) | **17860** | **−285** | `30..32` | `0,469s` / `18,603s` | `CA_17860_3_32_20.txt` (`544735d3…`) |
| **`(3, 34, 20)`** | `18430` (`CIT`) | `23` (`1`) | **18050** | **−380** | `33..34` | `0,387s` / `22,344s` | `CA_18050_3_34_20.txt` (`9224fbac…`) |
| **`(3, 35, 20)`** | `18677` (`CIT`) | `23` (`0`) | **18070** | **−607** | `35` | `0,371s` / `24,567s` | `CA_18070_3_35_20.txt` (`8751d063…`) |
| **`(3, 38, 20)`** | `18753` (`CIT`) | `24` (`1`) | **18240** | **−513** | `36..38` *(k=36: −437)* | `0,444s` / `32,603s` | `CA_18240_3_38_20.txt` (`68678d1c…`) |

*(Zusätzlich 3 projizierte Begleitdateien aus v2/v3 in `results/` — `CA_2160_3_17_10.txt`, `CA_6097_3_23_14.txt`, `CA_6188_3_25_14.txt` — ebenfalls `FORMAT_OK` & `DUAL_PASS`; Gesamtgröße `results/`: `9,5 MB`.)*

## 2. Verifier-Integrität & Gate-Archiv

- **Verifier-Integrität:** `verifiers/` strikt READ-ONLY (`sha256sum -c verifiers/SHA256SUMS` 3/3 OK, `python3 verifiers/test_verifiers.py` 23/23 PASS, `git diff main -- verifiers/` leer).
- **Gate-Archiv:**
  - `exp/pgl-binary-ccl-v2`..`v4`: Gate 0 PASS (7/7 `PGL(2,q)`), Gate 1 PASS (**13 Pareto-Front-Rekorde / 23 Zellen** in `results/`, 16 wiederverwendbare `C(M,k)` in `data/ccl_binary/`).
  - `exp/pgl-binary-ccl-v5`: `cc=0`-Snipe abgeschlossen (`hits=[]`), `tabu_reduce` 10k-Sanity PASS & Pilot abgeschlossen (`saved=0`), vollständiges Submission- & Audit-Paket `submission/` (`verify_all.sh` **16/16 PASS**).
