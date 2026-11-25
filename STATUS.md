# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Branch `exp/phase5a-issue85-t5v2`, abgezweigt von `origin/main` @ `fd40499` [PR #11 gemergt]: Phase-5A-Pilot auf `t=5, v=2` [Issue #85] mit Zero-Dep-Rust-Solver [`solvers/t5_bin_search`](solvers/t5_bin_search/src/main.rs); Gate 0 G0-1 PASS, G0-2 PASS, **G0-3 FAIL → sauberer Abbruch vor Gate 1** nach vollständiger Ursachenanalyse; `results/`, `verifiers/` und `PR #88` unverändert).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), Audit-Paket siehe [`submission/MANIFEST.md`](submission/MANIFEST.md).

## 0. Governance- & Branch-Status

- **Gemergte PRs:** PR #1 (`phase-1-setup`), PR #2 (`chore/sync-main-docs`), PR #3 (`exp/pgl-binary-ccl-v2`), PR #4 (`exp/pgl-binary-ccl-v3`), PR #6 (`exp/pgl-binary-ccl-v5` @ `a27da71`), PR #7 (`chore/ca-tools-submission-prep` @ `162d48f`), PR #8 (`chore/ca-tools-final-polish` @ `734d768`), PR #9 (`chore/ca-tools-pre-submit` @ `e945ed5`), PR #10 (`docs/pr88-accounting` @ `34d1743`), PR #11 (`exp/phase5-recon` @ `fd40499`).
- **Aktiver Branch (`exp/phase5a-issue85-t5v2`, Phase 5A Pilot — Gate-0-Abbruch):**
  - **Regel-7-Sperre aktiv:** Keine neue Suche oder Einreichung zur Bauart `PGL(2,q)+CCL` auf `t=3` bis zum Prüfbericht zu `chrispbsmolen/ca-tools#88`.
  - **Solver [`solvers/t5_bin_search`](solvers/t5_bin_search/src/main.rs) (`std`-only Rust, `--mode comp|free`, `--algo tabu|sa|best-sa|mix-sa|hybrid`, `--fix-const`, `--step-down`):**
    - **G0-1 (`--self-test`):** **PASS** — `10.000` zufällige Bit-Flips je `comp`/`free` auf `k=12` und `k=25` + `160` HD-1-Brute-Force-Prüfungen (`0` Abweichungen); unabhängige `ca_verify`-Prüfung bestätigt exakte Zählung (`592` kanon. = `1.184` volle Lücken).
    - **G0-2 (Anker `CA(126; 5, 28, 2)` @ `083a093`):** **PASS** — `table/arrays/CA_126_5_28_2.txt`, SHA-256 `f919b04aef4bfe288c6a965873d0e5de54c184d02ad22ff1b00b57f215eb4062`, `0` Treffer in `withdrawn_files.csv`, Dual-Verifikation PASS (`ca_verify 0,01 s`, `verify_independent.py 2,30 s`), exakt `63/63` Komplementpaare (`r[i+63] == ~r[i]`, paarweiser Spaltenabstand konstant `32`).
    - **G0-3 (`k=25`, Step-Down `126→124→122`, `<=30 s`):** **FAIL → Gate-0-Abbruch (kein Gate-1-Blindlauf).** Durchsatz auf 2 Threads: `25–28k evals/s` bei `k=25` (`C(24,4)=10.626` 5-Tupel/Flip) bzw. `290–335k evals/s` bei `k=15`. Zwei quantitativ belegte Ursachen: (1) `CA(126; 5, 28, 2)` ist ein starrer Frobenius-invarianter `Z_63`-Kristall (`init_unc=137` nach Drop von 1 Paar/Zeile; Energiebarriere blockiert 1-Bit-Flips in allen Modi `comp`/`free`, Tabu, SA und MixSa); (2) aus Random-Start (`k=25`, auch mit `--fix-const` und Metropolis-Bulk-Zügen `pf=0..0.02`) stagniert 1-Bit-Suche auf 2 vCPUs bei `unc=501` (`N=124`, 10 s) bzw. `unc=569..589` (`N=122`, 12–15 s) — konsistent mit `k=15`-Kalibrierung (`N=96`: `unc=69` nach `1,46M` Zügen; `binsa.c` nutzt `50M`-Zyklen ≈ `30 min`/Zyklus bei `k=25`).
  - **Phase-5-Recon-Archiv (PR #11):** [`docs/CA_TOOLS_WANTED_85_86.md`](docs/CA_TOOLS_WANTED_85_86.md), [`scripts/scan_t4_targets.py`](scripts/scan_t4_targets.py), [`docs/TARGET_SCAN_t4.md`](docs/TARGET_SCAN_t4.md) @ `083a093`.
  - **Archiv Checkliste Meldung nach außen (`RULES.md` Punkt 2, PR #88) — 5/5 PASS (Stand `2026-11-25`):**
    - `2a` (Tabellen-Check @ `083a0933e3561625b2aad9bd19035ad76d783f03`, `2026-11-25T13:32:06Z`): **PASS** — `table/ca_table.csv.gz` 23/23, `table/ca_frame.csv` 23/23, `table/derived.csv` 23/23 strikt kleiner (`submission/CA_TOOLS_FORMAT.md`).
    - `2b` (Offene PRs & Issues `ca-tools`): **PASS** — 0 offene PRs vor Einreichung; 2 offene Wanted-Issues (`#85`, `#86`).
    - `2c` (Literaturprüfung in `docs/`): **PASS** — [`docs/LITERATURE_CHECK_PGL_CCL.md`](docs/LITERATURE_CHECK_PGL_CCL.md) (inkl. Seelman/IRSI, Sitjar v1.4, Canli `quantavane-covering-arrays` @ `0b179b52` mit `0` Konflikten und transparenter Restliste; Neuheitsstatus formal offen; `k=18, 19` als *best known upper bound 18* präzisiert).
    - `2d` (Drittprüfung): **PASS** — [`docs/THIRD_PARTY_VERIFICATION.md`](docs/THIRD_PARTY_VERIFICATION.md) + archiviertes [`submission/third_check.py`](submission/third_check.py) (SHA-256 `2acd4477…`): 1. Prüfung auf `results/` (16/16 gültig, Negativkontrolle 70 Zeilen entfernt), 2. Prüfung auf `main @ 162d48f` (13/13 Staging byte-identisch, 13/13 bit-exakt aus frischem Build, `tools/check_submission.py` 13/13 PASS) & 3. Gegenprüfung PR #88 durch Claude (13/13 Arrays byte-identisch, `tools/check_submission.py` @ `083a093` 13/13 PASS) + eigene Nur-Lese-Nachprüfung von `refs/pull/88/head`.
    - `2e` (Deterministische Reproduktion & SHA-256-Vergleich): **PASS** — 13/13 byte-identische Übereinstimmung aus `data/ccl_binary/` (`submission/REPRODUCE.md`).

## Meldung nach außen

- **Pull Request:** https://github.com/chrispbsmolen/ca-tools/pull/88 (eigenständig eröffnet durch `Justus42`)
- **Datum und Uhrzeit (UTC):** `2026-11-25T14:44:16Z`
- **Einreichungsordner:** `submissions/jeserigk-pgl-ccl-2026-11/` (`15` neue Dateien: `claims.csv`, `HOW.md`, 13 Pareto-Arrays über 23 Zellen; `0` geänderte oder gelöschte Dateien außerhalb)
- **Basis-Commit (`chrispbsmolen/ca-tools`):** `083a0933e3561625b2aad9bd19035ad76d783f03` (`083a093`)
- **Head-Commit (`Justus42:submit/jeserigk-pgl-ccl-2026-11`):** `66a9947c0d422b5ce30d551736a4befe84c474b1` (`66a9947`)
- **Zustand:** **offen, wartet auf Prüfbericht und Maintainer** (`draft: false`, `0` Issue-Kommentare, `0` Reviews; GitHub-Actions-Workflows `Verify submission`, `Consistency` und `Tests` auf `66a9947` stehen auf `action_required` — warten auf Ersteinreicher-Freigabe durch den Maintainer; Bot-Prüfbericht noch nicht vorliegend / nicht gelesen)
- **Nur-Lese-Nachprüfung (2026-11-25):** `13/13` Arrays aus `refs/pull/88/head` SHA-256-identisch zu [`results/SHA256SUMS`](results/SHA256SUMS), `15/15` Dateien byte-identisch zu [`submission/ca_tools_staging/`](submission/ca_tools_staging/), PR-Text gelesen (`8281` Bytes, inkl. `AI tools used: yes` & `Extent of AI use:`). Korrespondenz-Entwürfe bei Maintainer-Rückfragen: [`docs/PR88_KORRESPONDENZ.md`](docs/PR88_KORRESPONDENZ.md).
- **Vermerk nach `RULES.md` Regel 7:** Bis zum Prüfbericht des Ziels (`chrispbsmolen/ca-tools`) **keine weitere Meldung zur Bauart `PGL(2,q)+CCL`**. Kein Push auf `Justus42/ca-tools` (auch nicht auf den PR-Branch `submit/jeserigk-pgl-ccl-2026-11`), solange der PR unverändert im Review steht.

## 1. Pareto-Front der 13 Arrays (kleiner als `ca-tools` @ `083a093` auf 23 Zellen)

Frisch dual-verifiziert am `2026-11-25` durch [`submission/verify_all.sh`](submission/verify_all.sh) (`xargs -P 2`); vollständige Checksummen in [`results/SHA256SUMS`](results/SHA256SUMS) (`32/32 OK`) und [`submission/records.csv`](submission/records.csv).

| Zelle `(3, k, v)` | `ca_table` (`083a093`) | `derived.csv` | Best `M` (`cc`) | Array `N` | Delta vs `ca_table` | Abgedeckte `k` | `ca_verify` / `py_verify` | Datei (`results/`) & SHA-256 (Prefix) |
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
