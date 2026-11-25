# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Branch `exp/phase5b-t4-nearbush-recon`, abgezweigt von `origin/main` @ `8f33f7d` [PR #12 & #13 gemergt]: Phase-5B-1 Struktur-Inspektion, `PG(3,7)`-Geometrie, Positivkontrollen und Billig-Tests für `t=4 NEAR_BUSH` in [`scripts/analyze_t4_nearbush.py`](scripts/analyze_t4_nearbush.py) & [`docs/T4_NEAR_BUSH_ANALYSIS.md`](docs/T4_NEAR_BUSH_ANALYSIS.md); Live-Abgleich `ca-tools` @ `c5f447d` [0 `t=4`-Änderungen]; Scratch-Prototyp `CA(7561; 4, 11, 8)` via Hyperoval-Double-`poly2` dual-verifiziert [`-119` unter `7680` @ `c5f447d`]; `verifiers/`, `submission/`, `results/` und PR #88 vollständig unverändert).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), Audit-Paket siehe [`submission/MANIFEST.md`](submission/MANIFEST.md).

## 0. Governance- & Branch-Status

- **Gemergte PRs:** PR #1 (`phase-1-setup`), PR #2 (`chore/sync-main-docs`), PR #3 (`exp/pgl-binary-ccl-v2`), PR #4 (`exp/pgl-binary-ccl-v3`), PR #6 (`exp/pgl-binary-ccl-v5` @ `a27da71`), PR #7 (`chore/ca-tools-submission-prep` @ `162d48f`), PR #8 (`chore/ca-tools-final-polish` @ `734d768`), PR #9 (`chore/ca-tools-pre-submit` @ `e945ed5`), PR #10 (`docs/pr88-accounting` @ `34d1743`), PR #11 (`exp/phase5-recon` @ `fd40499`), PR #12 (`docs/pr88-consistency-fix` @ `4a650ea`), PR #13 (`exp/phase5a-issue85-t5v2` @ `8f33f7d`).
- **Aktiver Branch (`exp/phase5b-t4-nearbush-recon`, Phase 5B-1 Recon — Pure Python, kein Rust-Solver):**
  - **Regel-7-Sperre & PR-#88-Schutz aktiv:** Keine neue Suche oder Einreichung zur Bauart `PGL(2,q)+CCL` auf `t=3`, kein Schreibzugriff auf `Justus42/ca-tools` oder `chrispbsmolen/ca-tools` bis zum Prüfbericht zu PR `#88`; `verifiers/`, `submission/`, `results/` sowie die 4 PR-#88-verlinkten Dateien bleiben in diesem Branch unverändert (`docs/RUN_LOG.md` nur unten angehängt).
  - **Live-Abgleich `chrispbsmolen/ca-tools` @ `c5f447da7f3efcc1b39cdea6340463ec7e90e006` (`2026-11-25T17:49:34Z`, 9 Commits seit `083a093`):** Nur 3 `t=3/5, v=2`-Dateien neu (`smolen-2026-11-formula-arrays-2`), **0 geänderte `t=4`-Zellen**, einzige offene PR ist `#88` (`0` Überschneidungen mit `t=4 NEAR_BUSH`).
  - **Ergebnisse Phase 5B-1 ([`docs/T4_NEAR_BUSH_ANALYSIS.md`](docs/T4_NEAR_BUSH_ANALYSIS.md), [`scripts/analyze_t4_nearbush.py`](scripts/analyze_t4_nearbush.py), `5,06 s`):**
    - Struktur-Inspektion `k=q+2`: `CA(3556;4,9,7)` = exakt `508` All-Ones-Cosets über `Z_7` (Sitjar v1.5); `CA(6101;4,10,8)` = Row-Deletion + Nurmela-Tabu-Postop von NCK `6125` (Bai XunDi); `CA(9801;4,11,9)` = exaktes Bush-`OA(6561;4,10,9)` + `AG(2,9)`-Pencil-Cover + `4` `OA(729;3,9,9)` + `4×81` Reparaturblöcke (`N = q^4 + ((q^2-1)/2)q^2`, Bai XunDi).
    - `PG(3,7)`-Geometrie & untere Schranke: min. `5/126` (`k=9`) bzw. `12/210` (`k=10`) abhängige 4-Mengen; jede Erweiterung eines unveränderten linearen `[k,4]_q`-Grundblocks erfordert `N >= q^4 + (q-1)q^3` (`4459, 7680, 12393, 27951, 54925`).
    - Dual-verifizierte Positivkontrollen (nur im Scratch): `PC-1 CA(3577;4,9,7)` (`poly2`, `0,01s / 0,115s` PASS) und `PC-2 CA(4459;4,10,7)` (`PG(3,7)+6H`, `0,01s / 0,193s` PASS).
    - Billig-Tests `k=q+3`: Bei ungeradem `q=7` scheitert naives `Double-poly2` (`N=4321`) exakt an `4` Kegelschnitt-Sekantenpaaren (`miss_both_8_9 = 5544`, Nichtexistenz von `OA(343;3,9,7)`). Bei geradem `q=8` liefert das `(q+2)`-Hyperoval `OA(512;3,10,8)` (`120/120` Tripel) deterministisch den **dual-verifizierten Scratch-Prototyp `CA(7561; 4, 11, 8)`** (**119 Zeilen kleiner als `7680` am Commit `c5f447d`**, `0,01s / 0,627s` PASS; in 5B-1 bewusst nicht in `results/` abgelegt).
  - **Verbindlicher Bau- und Gate-Vertrag für Phase 5B-2 (Pflicht vor jedem Rust-Solver):**
    - **Primär-Track `5B-2A` (`t=4, q=8, k=11..12`, Hyperoval-Double-`poly2` + lokale Row-Deletion/Tabu-Post-Op):**
      - *Zielstruktur & Zellen:* Deterministischer `Hyperoval Double-poly2`-Generator (für `CA(7561; 4, 11, 8)`, `-119` vs. `c5f447d`) + Zero-Dep-Rust-Post-Op-Reduzierer (`std`-only, 2 Threads, `--time-limit-secs` Pflicht) auf `(4, 11, 8)` (Ziel `< 7561`, Abbau der `9` Kollisionszeilen & redundanter Zeilen) sowie Strukturprüfung `k = 12` (`< 7680`).
      - *Positivkontrolle (exakt selbe Struktur):* (G0-1) Reproduktion `CA(7561; 4, 11, 8)` + Dual-Verify PASS; (G0-2) Solver-`--self-test` (`>= 10.000` inkrementelle Zell-Deltas vs. Vollprüfung, `0` Abweichungen); (G0-3) Post-Op-Reduzierer muss eine um `+3` redundante Zeilen aufgeblähte Instanz bzw. eine Zeile von `CA(7561; 4, 11, 8)` (oder NCK `CA(6125; 4, 10, 8)`) innerhalb `<= 30 s` auf `unc = 0` reduzieren.
      - *Gate-0-Abbruchkriterium:* Bei Fehlschlag von G0-1..G0-3 (insb. `saved = 0` auf G0-3 nach `3 × 30 s`) sofortiger Abbruch der Post-Op-Suche mit Belegart **`Suche erfolglos (3 × 30 s, Gate-0-Abbruch)`**; der deterministische Anker `CA(7561; 4, 11, 8)` bleibt unabhängig davon als verifizierbares Ergebnis erhalten.
      - *Zeitkappen (`--time-limit-secs`):* Gate 0 max. `30 s`/Lauf (`<= 120 s` gesamt); Gate 1 max. `180 s`/Lauf (`<= 600 s` gesamt); kein `/goal`.
    - **Sekundär-Track `5B-2B` (optional, nur bei separater Freigabe: `t=4, q=7, k=10`, `Z_7`-Coset-Suche `< 637` Cosets):**
      - *Positivkontrolle (exakt selbe Struktur):* Derselbe `Z_7`-Coset-Solver muss auf `k = 9, q = 7` mindestens `M = 511` (`N = 3577`, Sitjar-Struktur) innerhalb `<= 30 s` lösen; sonst Abbruch vor Gate 1 mit Belegart **`Suche erfolglos (3 × 30 s, Gate-0-Abbruch)`**.
    - **Ergebnis- & Außenmeldungs-Sperre:** Ablage dual-verifizierter Arrays in `results/` erst nach bestandener Phase-5B-2-Prüfung; **keine** Einreichung bei `chrispbsmolen/ca-tools` vor Prüfbericht zu PR `#88` und vollständiger Checkliste `RULES.md` Punkt 2.
  - **Archiv Phase 5A (`exp/phase5a-issue85-t5v2`, gemergt in PR #13 @ `8f33f7d`):**
    - Solver [`solvers/t5_bin_search`](solvers/t5_bin_search/src/main.rs) (`std`-only Rust): **G0-1 PASS** (`10.000` Flips × 4, `0` Abw.), **G0-2 PASS** (`CA(126;5,28,2)` @ `083a093`, `63/63` Komplementpaare, Dual-Verify PASS), **G0-3 FAIL → Belegart: `Suche erfolglos (3 × 30 s, Gate-0-Abbruch)`** (kein Gate-1-Blindlauf; Ursachen: starrer `Z_63`-Kristall `init_unc=137` + 1-Bit-Durchsatz `25–28k evals/s` auf 2 vCPUs ergibt Glas-Plateau `unc=501..589` bei `k=25`).
  - **Phase-5-Recon-Archiv (PR #11 @ `fd40499`):** [`docs/CA_TOOLS_WANTED_85_86.md`](docs/CA_TOOLS_WANTED_85_86.md), [`scripts/scan_t4_targets.py`](scripts/scan_t4_targets.py), [`docs/TARGET_SCAN_t4.md`](docs/TARGET_SCAN_t4.md) @ `083a093`.
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
- **Head-Commit (`Justus42:submit/jeserigk-pgl-ccl-2026-11`):** `8d3365c618918106322e119a23b983fdb9520b04` (`8d3365c`, seit `2026-11-25T17:05:37Z`); eingereicht mit `66a9947c0d422b5ce30d551736a4befe84c474b1` (`66a9947`)
- **Zustand:** **offen, wartet auf Prüfbericht und Maintainer** (`draft: false`, `0` Issue-Kommentare, `0` Reviews; GitHub-Actions-Workflows `Verify submission`, `Consistency` und `Tests` auf `66a9947` stehen auf `action_required` — warten auf Ersteinreicher-Freigabe durch den Maintainer; Bot-Prüfbericht noch nicht vorliegend / nicht gelesen)
- **Nur-Lese-Nachprüfung (2026-11-25):** `13/13` Arrays aus `refs/pull/88/head` SHA-256-identisch zu [`results/SHA256SUMS`](results/SHA256SUMS), `15/15` Dateien byte-identisch zu [`submission/ca_tools_staging/`](submission/ca_tools_staging/), PR-Text gelesen (`8281` Bytes, inkl. `AI tools used: yes` & `Extent of AI use:`). Korrespondenz-Entwürfe bei Maintainer-Rückfragen: [`docs/PR88_KORRESPONDENZ.md`](docs/PR88_KORRESPONDENZ.md).
- **Nachtrag `2026-11-25` (Korrektur an `HOW.md`, Angabe von Claude):** Der Lauf `Consistency #128` auf `66a9947` schlug fehl (Bildschirmfoto von Justus, 17:40 MEZ). Lokal nachgestellt am Merge-Stand `5327245`: `tools/consistency.py --check --pr` meldet `5 problems`, alle in `HOW.md`: fünf Verweise auf Dateien dieses Repos (`docs/…`, `results/…`), die das Skript als Pfade im Tabellen-Repo liest. Die Arrays und `claims.csv` sind nicht betroffen. Korrektur: die fünf Verweise als volle Links auf dieses Repo, sonst keine Änderung (3 Zeilen). Justus hat sie selbst committet (`8d3365c`, Web-Editor, mit ausdrücklicher Entscheidung). Nachprüfung am neuen Merge-Stand `a8c203b` (Basis `ca-tools` @ `4be5a88`): `consistency.py` `0 problems`, Selbsttest und Frame-Tests bestanden, `check_submission.py` `13/13` PASS; PR weiter genau `15` Dateien. Ergebnis der Läufe auf GitHub selbst: nicht gesehen. [`submission/ca_tools_staging/HOW.md`](submission/ca_tools_staging/HOW.md) ist nachgezogen (SHA-256 `f9bd1f86…`, vorher `f90540db…`).
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
