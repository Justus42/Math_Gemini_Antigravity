# Projektstatus & Governance-Gates (`STATUS.md`)

Letzte Aktualisierung: 2026-11-25 (Branch `exp/phase5b2a-q8-nearbush`, abgezweigt von `origin/main` @ `56a3413` [PR #14 gemergt]: Phase-5B-2A abgeschlossen — deterministischer Generator [`scripts/gen_t4_q8_nearbush.py`](scripts/gen_t4_q8_nearbush.py) & Zero-Dep-Rust Post-Op-Reduzierer [`solvers/t4_postop`](solvers/t4_postop/src/main.rs); Live-Abgleich `ca-tools` @ `c5f447d` unverändert [0 `t=4`-Änderungen, nur PR #88 offen]; Gate 0 PASS [G0-1..G0-3]; Gate 1 PASS & Ablage dual-verifizierter Arrays in [`results/t4_nearbush/`](results/t4_nearbush/VERIFICATION_LOG.md): **`CA(5888; 4, 10, 8)`** [`-213` vs. `6101`], **`CA(7070; 4, 11, 8)`** [`-610` vs. `7680`], Anker `CA(7561; 4, 11, 8)` [`-119` vs. `7680`]; `verifiers/`, `submission/`, alle bestehenden `results/`-Dateien und PR #88 vollständig unverändert).
Verbindliche Projektregeln siehe [`RULES.md`](RULES.md), vollständiges Laufprotokoll siehe [`docs/RUN_LOG.md`](docs/RUN_LOG.md), Audit-Paket siehe [`submission/MANIFEST.md`](submission/MANIFEST.md).

## 0. Governance- & Branch-Status

- **Gemergte PRs:** PR #1 (`phase-1-setup`), PR #2 (`chore/sync-main-docs`), PR #3 (`exp/pgl-binary-ccl-v2`), PR #4 (`exp/pgl-binary-ccl-v3`), PR #6 (`exp/pgl-binary-ccl-v5` @ `a27da71`), PR #7 (`chore/ca-tools-submission-prep` @ `162d48f`), PR #8 (`chore/ca-tools-final-polish` @ `734d768`), PR #9 (`chore/ca-tools-pre-submit` @ `e945ed5`), PR #10 (`docs/pr88-accounting` @ `34d1743`), PR #11 (`exp/phase5-recon` @ `fd40499`), PR #12 (`docs/pr88-consistency-fix` @ `4a650ea`), PR #13 (`exp/phase5a-issue85-t5v2` @ `8f33f7d`), PR #14 (`exp/phase5b-t4-nearbush-recon` @ `56a3413`).
- **Aktiver Branch (`exp/phase5b2a-q8-nearbush`, Phase 5B-2A — `t=4, q=8 NEAR_BUSH`):**
  - **Regel-7-Sperre & PR-#88-Schutz aktiv:** Keine neue Suche oder Einreichung zur Bauart `PGL(2,q)+CCL` auf `t=3`, kein Schreibzugriff auf `Justus42/ca-tools` oder `chrispbsmolen/ca-tools` bis zum Prüfbericht zu PR `#88`; `verifiers/`, `submission/`, alle bestehenden Phase-4-Dateien in `results/` sowie die 4 PR-#88-verlinkten Dokumente (`docs/LITERATURE_CHECK_PGL_CCL.md`, `docs/THIRD_PARTY_VERIFICATION.md`, `results/VERIFICATION_LOG_pgl_ccl.md`; `docs/RUN_LOG.md` nur unten angehängt) sind vollständig unverändert.
  - **Frischer Live-Abgleich `chrispbsmolen/ca-tools` @ `c5f447da7f3efcc1b39cdea6340463ec7e90e006` (`2026-11-25T17:49:34Z`, rein lesend via `gh api`):** Unverändert gegenüber Phase 5B-1 (`0` neue Commits, `0` geänderte `t=4`-Zellen in `ca_table.csv.gz` / `ca_frame.csv` / `derived.csv`: `(4, 10, 8) = 6101 [VER]`, `(4, 11..15, 8) = 7680 [CIT]`; einziger offener PR ist `#88`).
  - **Ergebnisse Phase 5B-2A (Schritt A + Schritt B, Dual-Verifikation in [`results/t4_nearbush/VERIFICATION_LOG.md`](results/t4_nearbush/VERIFICATION_LOG.md)):**
    - **Schritt A ([`scripts/gen_t4_q8_nearbush.py`](scripts/gen_t4_q8_nearbush.py), Pure Python `std`-only, 2× byte-identisch):**
      - `k11-pencil` → **`results/t4_nearbush/CA_7561_4_11_8.txt`** (`sha256: 821c23ea…`, byte-identisch zu Phase 5B-1, `0,042 s`, Dual-Verify PASS `0,01 s / 0,621 s`, `-119` unter `7680` @ `c5f447d`; Anker, dominiert von `7070`).
      - `k10-polychrom` → **`results/t4_nearbush/CA_5888_4_10_8.txt`** (`sha256: 7d72bc89…`, `0,038 s`, Dual-Verify PASS `0,03 s / 0,379 s`, **`-213` kleiner als `ca-tools` @ `c5f447d` = `6101`**): Projektion entlang irreduziblem `x^2 + x + 1` über `GF(8)` + 4 disjunkte 15-Punkte-Blocking-Sets + 4 Einzelpunkte `{4..7}` in `AG(2, 8)` + `4 × 7` skalierte Hyperoval-Slices (`4096 + 4 · 448 = 5888`).
      - `k11-polychrom` → `CA(7203; 4, 11, 8)` (`sha256: cb222f48…`, `0,099 s`, Dual-Verify PASS `0,01 s / 0,709 s`, `-477` unter `7680` @ `c5f447d`): zwei balancierte 4-polychromatische `AG(2, 8)`-Färbungen + `3072` Hyperoval-Slices + `35` deterministische Reparaturzeilen (Startarray für Gate 1).
      - `k12-check` (Negativbefund, algebraisch belegt): Reiner 4-Farben-Kern auf `k = 12` erzwingt `N >= 4096 + (512 - 64) · 8 = 7680`; zudem hat das 10-Punkte-Hyperoval in `PG(2, 8)` `0` freie Punkte außerhalb seiner 45 Sekanten (`OA(512; 3, 11, 8)` existiert nicht nach Bush/Segre).
    - **Schritt B — Gate 0 PASS ([`solvers/t4_postop`](solvers/t4_postop/src/main.rs), Zero-Dep Rust `std`-only, LTO + `target-cpu=native`, 2 Threads, Gesamtzeit `30,7 s <= 120 s`):**
      - **G0-1 PASS:** `CA(7561; 4, 11, 8)` byte-identisch reproduziert + Dual-Verify PASS.
      - **G0-2 PASS:** `--self-test --self-test-steps 12000` (`12.000` inkrementelle Zell-Deltas + `10` Row-Deletions vs. Brute-Force, **`0` Abweichungen**, `0,353 s`).
      - **G0-3 PASS:** (a) `+3`-aufgeblähte `CA(7564; 4, 11, 8)` in `0,32 s` auf `7561` reduziert (`ca_verify` PASS); (b) `CA(7561; 4, 11, 8)` in `30,03 s` (2 Threads, `560.043 evals/s`) auf **`CA(7450; 4, 11, 8)`** reduziert (`saved = 111`, `absorbed = 503`, Dual-Verify PASS `0,01 s / 0,657 s`).
    - **Schritt B — Gate 1 PASS (Gesamtzeit `320,29 s <= 600 s`, alle Einzelläufe `<= 180 s`, 2 Threads):**
      - `G1-A` (`180,05 s`, `seed=5211`, `695k evals/s`): `CA(7203; 4, 11, 8) → CA(7072; 4, 11, 8)` (`saved = 131`, `absorbed = 214`, Dual-Verify PASS `0,01 s / 0,638 s`).
      - `G1-B` (`45,02 s`, `seed=5221`, `877k evals/s`): `CA(5888; 4, 10, 8)` → `saved = 0` (`min_row_unique = 75`, `absorbed = 0`), **sauberer Stagnationsabbruch** (`Heuristische Suche erfolglos, 45 s Stagnation`).
      - `G1-C` (`95,22 s`, `--resume CA(7072)`, `seed=5212`, `739k evals/s`): `CA(7072; 4, 11, 8)` → **`results/t4_nearbush/CA_7070_4_11_8.txt`** (`saved = 2`, `absorbed = 52`, danach sauberer `60 s`-Stagnationsabbruch; `sha256: ae72c96e…`, Dual-Verify PASS `0,01 s / 0,778 s`, **`-610` kleiner als `ca-tools` @ `c5f447d` = `7680`**, `-491` unter `7561`).
    - **Ergebnis- & Außenmeldungs-Sperre:** Alle drei Arrays liegen mit `SHA256SUMS` und `VERIFICATION_LOG.md` ausschließlich lokal unter `results/t4_nearbush/`. **Keine** Einreichung bei `chrispbsmolen/ca-tools` vor Prüfbericht zu PR `#88` und vollständiger Checkliste `RULES.md` Punkt 2 (insbesondere Literatur- und Drittprüfung).
  - **Archiv Phase 5B-1 (PR #14 @ `56a3413`):** [`docs/T4_NEAR_BUSH_ANALYSIS.md`](docs/T4_NEAR_BUSH_ANALYSIS.md), [`scripts/analyze_t4_nearbush.py`](scripts/analyze_t4_nearbush.py) (`CA_3556`/`CA_6101`/`CA_9801`-Inspektion, `PG(3,7)`-Geometrie, Positivkontrollen PC-1/PC-2, Scratch-Prototyp `CA(7561;4,11,8)`).
  - **Nächste offene Optionen (nach Freigabe):**
    - **Option A (`q = 7, 9, 11, 13` / ungerade `q`, Übertragung der 4-polychromatischen + irreduzibel-quadratischen `AG(2, q)`-Zerlegung & `5B-2B`):** Prüfung, ob die `k = q + 2`-Bauart von `CA(5888; 4, 10, 8)` (disjunkte minimale Blocking-Sets + Einzelpunkt-Slices in `AG(2, q)`) direkt auf `q = 7, 9, 11, 13` (`(4, 9, 7)`, `(4, 11, 9)`, `(4, 13, 11)`, `(4, 15, 13)`) übertragbar ist, oder `Z_7`-Coset-Suche (`5B-2B`) auf `(4, 10, 7) < 4459`.
    - **Option B (Weitere `q = 2^m`-Instanzen / `k = 12..15`):** Prüfung von `q = 16` (`(4, 18, 16) < 83519`, `(4, 19, 16) < 114489`) oder nicht-konstruktiver Erweiterung von `CA(7070; 4, 11, 8)` Richtung `k = 12` (`< 7680`).
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
