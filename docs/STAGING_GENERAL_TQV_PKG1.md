# Lokales Staging Paket 1: `q^t + C(v, 2) * q^(t - 2)` (`docs/STAGING_GENERAL_TQV_PKG1.md`)

- **Datum (UTC):** `2026-11-26`
- **Branch:** `chore/stage-general-tqv-pkg1` (Basis `origin/main` @ `ba4cfb2ff7477f8768fa2ad9f356fecc0aa5a94b`, nach Merge von PR `#23`)
- **Staging-Ordner (isoliert):** [`staging/jeserigk-bush-pair-2026-11/`](../staging/jeserigk-bush-pair-2026-11/) (`21` Dateien: `19` Array-Dateien, `claims.csv`, `HOW.md`; **`0`** Code-Dateien im Ordner)
- **Tabellen-Referenz (rein lesend):** `chrispbsmolen/ca-tools @ e673ab45758a3959710c662a34837f79f6add689` (`2026-11-26T06:17:26Z`)
- **Außenwirkung:** **keine** (strikt lokales Staging; kein Push nach `Justus42/ca-tools`, kein PR, kein Issue, kein Kommentar nach außen; externe Einreichung weiter vorbehaltlich ausdrücklicher Nutzerfreigabe).
- **Wortwahl (Regel 4):** durchgehend *„kleiner als `ca-tools` am Commit `e673ab4`“* — **kein Neuheitsanspruch**.

---

## 1. Live-Abgleich `chrispbsmolen/ca-tools` (`2026-11-26`)

| Prüfpunkt | Ergebnis |
| --- | --- |
| `main`-Commit-SHA | `e673ab45758a3959710c662a34837f79f6add689` (`2026-11-26T06:17:26Z`) |
| Offene PRs | `1` offener PR: `#89` (`Add CA(165; 3, 8, 5) — column extension of Bai XunDi's CA(165; 3, 7, 5)`, `jaredhaxton-cmd`) — **0 Konflikte** mit den `19` Paket-1-Zellen |
| `table/ca_table.csv.gz` | **`19/19`** strikt kleiner (`exceeds_table`) |
| `table/ca_frame.csv` | **`19/19`** strikt kleiner |
| `table/derived.csv` | **`19/19`** strikt kleiner |
| `table/withdrawn_files.csv` | **`0`** Treffer |
| `table/references.csv` | `oa-bush1952`, `fuse-ckrs2010`, `polychrome-bai2026` alle vorhanden und im Format `oa-bush1952;fuse-ckrs2010;polychrome-bai2026` verwendet |

---

## 2. Zuschnitt & SHA-256-Tabelle der 19 einheitlichen `gen_general_tqv.py`-Arrays

Alle `19` Array-Dateien werden ohne Ausnahme durch [`scripts/gen_general_tqv.py`](../scripts/gen_general_tqv.py) (Commit `ba4cfb2ff7477f8768fa2ad9f356fecc0aa5a94b`) byte-identisch erzeugt (`19/19` Byte-Vergleich in `5,09 s` PASS).
- Für `(4, 9, 7)` und `(4, 10, 8)` wurden ausdrücklich **nicht** die älteren Varianten aus `results/t4_nearbush/` (`d5860ade…` Post-Op bzw. `7d72bc89…` `Q_g`) verwendet, sondern die reinen Generator-Ausgaben (`d29b5155…` bzw. `2e4bf66b…`), lokal zusätzlich dual-verifiziert (`CA_3430`: `ca 0,01 s`, `py 0,1166 s`; `CA_5888`: `ca 0,02 s`, `py 0,3533 s`).
- `CA_7056_4_11_8.txt` (`k = q + 3` + `t4_postop`) ist ausdrücklich **nicht** enthalten.
- **Paketgröße (Array-Dateien):** `31.272.740` Bytes = **`29,82 MiB`** (`<= 200 MiB` Einreichungslimit); größte Einzeldatei `CA_376832_6_10_8.txt` = **`7,19 MiB`** (`<= 50 MiB` Einzeldateilimit, alle unkomprimierter Klartext nach `ca-tools/submissions/README.md`).

| # | Datei | `(t, k, v)` | `q` | `N` | Live `e673ab4` | Delta | Größe (Bytes / MiB) | `check_submission` | SHA-256 |
| :---: | --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| 1 | `CA_1053_3_11_9.txt` | `(3, 11, 9)` | `9` | `1053` | `1089` (`VER`) | `−36` | `23.166` (`0,02`) | `PASS (0,1 s)` | `4bd2469875295c1b44134f0c77443460793a22ddcfaefb031aaf204352e180d1` |
| 2 | `CA_1936_3_13_11.txt` | `(3, 13, 11)` | `11` | `1936` | `1991` (`VER`) | `−55` | `52.514` (`0,05`) | `PASS (0,1 s)` | `0220988fa28d5be959b70da80c3d9632f94af4539e9561ae53fb85f543103c2d` |
| 3 | `CA_3211_3_15_13.txt` | `(3, 15, 13)` | `13` | `3211` | `3289` (`VER`) | `−78` | `107.055` (`0,10`) | `PASS (3,1 s)` | `05984611eca09f5833c9d2311a61cfde19986e750a5a8484210ad952962c9ec8` |
| 4 | `CA_9766_3_21_18.txt` | `(3, 21, 18)` | `19` | `9766` | `9830` (`VER`) | `−64` | `495.292` (`0,47`) | `PASS (3,6 s)` | `9cbdafb7f73fd4e0706c3ba7609412566952aa1cdf8a618bb57cefd688bcedf3` |
| 5 | `CA_10108_3_21_19.txt` | `(3, 21, 19)` | `19` | `10108` | `10279` (`VER`) | `−171` | `523.374` (`0,50`) | `PASS (3,6 s)` | `8ff69cf373caa31ff5f0a88fd8e50540dcc10a53375c039926b35cfd64eead5c` |
| 6 | `CA_3430_4_9_7.txt` | `(4, 9, 7)` | `7` | `3430` | `3556` (`VER`) | `−126` | `61.740` (`0,06`) | `PASS (0,2 s)` | `d29b51556a7150ac1c5b060d504b08d3987b1f1d9b018bd77b19f624c4a9d642` |
| 7 | `CA_5888_4_10_8.txt` | `(4, 10, 8)` | `8` | `5888` | `6101` (`VER`) | `−213` | `117.760` (`0,11`) | `PASS (0,6 s)` | `2e4bf66ba6bdaff78e31460d766843f9858485493f93aa6ab0c69e01d2883fe1` |
| 8 | `CA_9477_4_11_9.txt` | `(4, 11, 9)` | `9` | `9477` | `9801` (`VER`) | `−324` | `208.494` (`0,20`) | `PASS (2,6 s)` | `eeea94544ed885cf2110733f4cd74b998c87d944dae8af535718bc267d431b30` |
| 9 | `CA_20086_4_13_10.txt` | `(4, 13, 10)` | `11` | `20086` | `20383` (`VER`) | `−297` | `522.236` (`0,50`) | `PASS (3,6 s)` | `d150abae2d774a49f0d9d2a1dec000b4c189706c3eb18f9f3cbca9d27305f537` |
| 10 | `CA_21296_4_13_11.txt` | `(4, 13, 11)` | `11` | `21296` | `21901` (`VER`) | `−605` | `577.654` (`0,55`) | `PASS (3,7 s)` | `cb9a4c5e431f1eb1652f70b0626bd981eaaa0c529f1267fad346847f703401a3` |
| 11 | `CA_39715_4_15_12.txt` | `(4, 15, 12)` | `13` | `39715` | `40476` (`VER`) | `−761` | `1.280.344` (`1,22`) | `PASS (4,5 s)` | `4e651a190870981ebeadd45e6afcf0434a361fe127536d62bfe9690a40c7cae6` |
| 12 | `CA_41743_4_15_13.txt` | `(4, 15, 13)` | `13` | `41743` | `42757` (`VER`) | `−1014` | `1.391.715` (`1,33`) | `PASS (4,6 s)` | `e8435eb665b9c627982239675bc93f21334ac40d4e8d781cb3592e768233d9a5` |
| 13 | `CA_24010_5_9_7.txt` | `(5, 9, 7)` | `7` | `24010` | `25039` (`VER`) | `−1029` | `432.180` (`0,41`) | `PASS (3,5 s)` | `13f1c8da1aaa37d1c4235285d581d05cc6d6d667884e7a7c13d099feddb79ce6` |
| 14 | `CA_47104_5_10_8.txt` | `(5, 10, 8)` | `8` | `47104` | `49128` (`VER`) | `−2024` | `942.080` (`0,90`) | `PASS (4,2 s)` | `8550074fda93e3b7e6dca9090f68e185777f77200d6e75fae946960fe509901e` |
| 15 | `CA_85293_5_11_9.txt` | `(5, 11, 9)` | `9` | `85293` | `88209` (`VER`) | `−2916` | `1.876.446` (`1,79`) | `PASS (5,6 s)` | `b369ba93389c4493c3a7541e1ab7637924acb126235ed19084bea55dce8bf0cc` |
| 16 | `CA_220946_5_13_10.txt` | `(5, 13, 10)` | `11` | `220946` | `224844` (`VER`) | `−3898` | `5.744.596` (`5,48`) | `PASS (14,2 s)` | `882f13369eb1bab475c8c812e031657144cde700880b38a1d8d0c5b0a3075fd0` |
| 17 | `CA_234256_5_13_11.txt` | `(5, 13, 11)` | `11` | `234256` | `240911` (`VER`) | `−6655` | `6.354.194` (`6,06`) | `PASS (16,3 s)` | `c525abfa2835d7f483eb0cc575e82723190c883e2b60936fb599cfa99e222c71` |
| 18 | `CA_168070_6_9_7.txt` | `(6, 9, 7)` | `7` | `168070` | `175273` (`VER`) | `−7203` | `3.025.260` (`2,89`) | `PASS (7,7 s)` | `c7de1a5387a2153bb5d61f43eb4ae702778b8daf75a4fe95ccb2a58ae640dd16` |
| 19 | `CA_376832_6_10_8.txt` | `(6, 10, 8)` | `8` | `376832` | `393018` (`VER`) | `−16186` | `7.536.640` (`7,19`) | `PASS (20,3 s)` | `2d433053ac2a24c44f74e54429460f5ea76aa248b3c43f9a6f7af2e084ba4c92` |

---

## 3. Lokale Volltests gegen `chrispbsmolen/ca-tools @ e673ab4` (im temporären Scratch)

### 3.1 `tools/check_submission.py`
- **Befehl:** `timeout --kill-after=10s 900 python3 tools/check_submission.py submissions/jeserigk-bush-pair-2026-11 --constant-rows-minutes 0.05 --out "$SCRATCH/check_out"`
- **Exit-Code:** **`0`**
- **Laufzeit:** `102,4 s` intern (`132,59 s` Wall-Clock)
- **Ergebnis:** **`Result: PASS. 19 of 19 claims passed.`** (`19/19 verified`, `19/19 exceeds_table`, `Credit check: No flags`, `0` Warnungen, `0` Fehler).

### 3.2 `tools/consistency.py`
- **Befehl (Komplettlauf):** `timeout --kill-after=10s 900 python3 -u tools/consistency.py --check --pr --base HEAD` (nach `git add submissions/jeserigk-bush-pair-2026-11` im temporären Scratch-Clone `@ e673ab4`)
- **Befund:** Der Komplettlauf wurde bei `591 s` vom 10-Minuten-Limit der Tool-Shell (nicht von `timeout 900`) innerhalb von `check_constructions` (Neuberechnung der `180` bestehenden `ca-tools`-Zertifikate in `table/constructions/CONSTRUCTIONS.csv`, unverändert durch unseren PR) abgebrochen.
- **Einzelprüfung aller `21/22` übrigen Prüffunktionen von `tools/consistency.py --check --pr --base HEAD` (inkl. `check_links`, `check_append_only`, `check_arrays`, `check_frame`, `check_derived`, `check_builds_on`, `check_certificates`):**
  - **Exit-Code:** **`0`**, **`0` Probleme** in **`65,9 s`** (`load` `0,13 s`, `counts` `0,59 s`, `check_structure` `0,16 s`, `check_arrays` `0,01 s`, `check_external` `0,01 s`, `check_constant_rows` `0,01 s`, `priority` `0,00 s`, `check_derived` `0,14 s`, `check_frame(pr=True)` `0,22 s`, `check_guarantee` `0,17 s`, `check_frame_veto` `0,13 s`, `check_above_rule` `0,85 s`, `check_certificates` `61,96 s`, `check_builds_on` `0,06 s`, `check_lower_bounds` `0,42 s`, `check_disputed` `0,02 s`, `check_retracted` `0,01 s`, `check_upgrades` `0,16 s`, `correct_credit` `0,11 s`, `check_sizes` `0,01 s`, **`check_links` `0,07 s` mit `submissions/jeserigk-bush-pair-2026-11/HOW.md in tracked_markdown() == True`**, `check_append_only("HEAD")` `0,53 s`).
  - Einziger unvollendeter Teil auf dieser 2-vCPU-VM: `check_constructions` auf den `180` unveränderten Bestandszertifikaten von `ca-tools` (kein Bestandteil unserer Einreichung; wird im `ca-tools`-CI-Runner ohne 10-Minuten-Shell-Cap vollständig ausgeführt).

---

## 4. Integritäts- & Pflicht-Checks

- `sha256sum -c verifiers/SHA256SUMS`: `3/3 OK`
- `sha256sum -c results/SHA256SUMS`: `32/32 OK`
- `sha256sum -c results/t4_nearbush/SHA256SUMS`: `13/13 OK`
- `sha256sum -c results/general_tqv/SHA256SUMS`: `14/14 OK`
- `python3 verifiers/test_verifiers.py`: `23/23 PASS`
- Code-Dateien in `staging/jeserigk-bush-pair-2026-11/`: `0` (nur `19` `CA_*.txt` + `claims.csv` + `HOW.md`)
- `git diff origin/main -- verifiers/ submission/ solvers/ results/ docs/LITERATURE_CHECK_PGL_CCL.md docs/THIRD_PARTY_VERIFICATION.md docs/GENERAL_TQV_PROOF.md`: leer (`0` Zeilen)
