# Lokales Staging: 37-Array-Paket (`staging/jeserigk-ckrs-coset-2026-11/`)

- **Stand:** 2026-11-26 (Branch `chore/stage-phase7-37` ab `origin/main` @ `666f76729372908a8b981878a164e414210eca84`).
- **Vergleichsstand (`chrispbsmolen/ca-tools`):** `main` @ `e673ab45758a3959710c662a34837f79f6add689` (`2026-11-26T06:17:26Z`).
- **Offene PRs auf `chrispbsmolen/ca-tools` (rein lesend via `gh api`):**
  - PR `#89` (`jaredhaxton-cmd`): `CA(165; 3, 8, 5)` — keine Überschneidung.
  - PR `#90` (`MimoAlexer`): `CA(73; 3, 28, 3)` — keine Überschneidung.
- **Einreichungsstatus:** **strikt lokales Staging**. Kein Push nach `Justus42/ca-tools`, kein PR, kein Issue, kein Kommentar nach außen (`RULES.md` „Meldung nach außen“ bleibt aktiv). Kein Neuheitsanspruch; Wortwahl durchgehend „kleiner als `ca-tools` am Commit `e673ab4`“.
- **Prüf-Klon:** rein lesender Abruf von `chrispbsmolen/ca-tools @ e673ab4` nach `/tmp/ca-tools-check` (nicht committet).

## 1. Zusammensetzung, Grenzen & Gegenproben

- **Staging-Ordner:** `staging/jeserigk-ckrs-coset-2026-11/` (`submission/` unberührt).
- **Dateianzahl:** exakt **`39` Dateien** (`37` unkomprimierte `.txt`-Arrays + `claims.csv` + `HOW.md`), **`0` Code-Dateien**, **`0` `.gz`-Dateien**.
  - `14` Arrays aus CP-SAT-Vertreterlisten (`v = q`, `q in {5, 7, 8, 9, 11}`) aus `results/phase7/`
  - `17` Arrays aus geschlossener Bauart §14 (`v < q`) aus `results/phase7_vq/`
  - `6` Arrays aus geschlossener Bauart Phase 6A (`v = q`, `q >= 13`): `5` aus `results/general_tqv/`, `1` (`CA_41743_4_15_13.txt`) aus `results/t4_nearbush/`
- **Ausgeschlossene `<= 50 MiB`-Zellen (über `200 MiB`-Summengrenze):** `(4, 27, 21)`, `(4, 27, 22)`, `(4, 27, 23)`, `(4, 29, 24)`. Keine überholte Datei gestaged.
- **Gemessene Größen (`ca-tools`-Grenzen: Einzeldatei `<= 50 MiB = 52.428.800 B`, Summe `<= 200 MiB = 209.715.200 B`):**
  - `37` `.txt`-Arrays: **`199.029.748 B`** (`189,8096 MiB`)
  - `claims.csv`: `39.751 B` (SHA-256 `76cca2c12f5beb1eebc8d0d42edcd8770755b969765499cf9dddf491cf940130`)
  - `HOW.md`: `10.425 B` (SHA-256 `930fc55098e1231c844c49ba1c2151a3f88284723c14a55553eca4c924b53984`)
  - Gesamtordner (`39` Dateien): **`199.079.924 B`** (**`189,8574 MiB <= 200 MiB`**, Restspielraum `10.635.276 B` = `10,1426 MiB`)
  - Größte Einzeldatei: `CA_456250_4_27_20.txt` mit **`29.587.500 B`** (**`28,2168 MiB <= 50 MiB`**)
- **Pflicht-Gegenprobe `CA_41743_4_15_13.txt`:**
  - Befehl: `timeout --kill-after=10s 120 python3 scripts/gen_general_tqv.py --t 4 --q 13 --v 13 --out /tmp/check_41743.txt` (`0,105 s`, `rc = 0`)
  - `cmp -s /tmp/check_41743.txt results/t4_nearbush/CA_41743_4_15_13.txt`: **`PASS` (byte-identisch)**, SHA-256 `e8435eb665b9c627982239675bc93f21334ac40d4e8d781cb3592e768233d9a5`.
- **Live-Tabellenabgleich (`chrispbsmolen/ca-tools @ e673ab4`):**
  - `37/37` strikt kleiner als `table/ca_table.csv.gz` (gezählte Zeilen), `table/ca_frame.csv` und `table/derived.csv`.
  - `0/37` Treffer in `table/withdrawn_files.csv`.
  - `37/37` SHA-256-Übereinstimmung zwischen `staging/jeserigk-ckrs-coset-2026-11/` und den jeweiligen `results/.../SHA256SUMS`.

## 2. Lokale Prüfungen gegen `chrispbsmolen/ca-tools @ e673ab4`

Hardware: 2 vCPUs (`Intel Xeon`), Linux x86_64, `ca_verify` kompiliert aus `/tmp/ca-tools-check/ca_verify.c` (`cc -O3 -pthread`). Die Kopie `submissions/jeserigk-ckrs-coset-2026-11/` wurde im lokalen Scratch-Klon `/tmp/ca-tools-check` mit `git add` vorgemerkt, damit `consistency.py` (`git ls-files "*.md"`) auch `HOW.md` prüft.

| Prüfung | Befehl (in `/tmp/ca-tools-check`) | Exit / Dauer | Ergebnis |
| --- | --- | --- | --- |
| `check_submission.py` | `timeout --kill-after=10s 900 python3 tools/check_submission.py submissions/jeserigk-ckrs-coset-2026-11 --constant-rows-minutes 0.05 --out /tmp/check-jeserigk-ckrs-coset-2026-11` | Shell-Wrapper-Detach nach ~`591 s` (`rc = -1`) während des abschließenden gzip-Schreibens nach `/tmp/.../arrays/`; Prozess beendete sich ~`65 s` danach selbstständig und schrieb `report.md`, `summary.json`, `37` kanonische Arrays (`elapsed_seconds = 492,19 s` / `8,2 min` reine Prüfzeit) | **`37/37 PASS` (`37 verified`, `37 exceeds_table`, `0` Probleme, `Credit check: No flags`, `similarity: no match` bei `37/37`)** — Hinweis: wegen Shell-Cap beim gzip-Export als unter `deviations` vermerkt (Prüfphase selbst `492,19 s` vollständig abgeschlossen) |
| `consistency.py --check --pr` (Komplettlauf) | `timeout --kill-after=10s 900 python3 tools/consistency.py --check --pr --base e673ab45758a3959710c662a34837f79f6add689` | **`nicht vollendet (Shell-Cap)`** nach ~`591 s` (`rc = -1`) in `check_constructions` auf den ~180 Bestandszertifikaten von `ca-tools` | Abgebrochen im Shell-Cap; Komplettlauf inkl. `check_constructions` im Review nachzuziehen |
| `consistency.py` (übrige `21/22` Prüffunktionen einzeln) | Python-Einzelaufruf aller 21 Funktionen außer `check_constructions` (`check_structure`, `check_arrays`, `check_external`, `check_constant_rows`, `priority.check_file`, `check_derived`, `check_frame(--pr)`, `check_guarantee`, `check_frame_veto`, `check_above_rule`, `check_certificates`, `check_builds_on`, `check_lower_bounds`, `check_disputed`, `check_retracted`, `check_upgrades`, `correct_credit.check_log`, `check_sizes`, `check_links`, `check_append_only`, `counts_worse`) | `rc = 0`, `63,856 s` (`64,214 s` Wall-Clock); davon `check_links` `0,072 s` über `148` Markdown-Dateien inkl. `submissions/jeserigk-ckrs-coset-2026-11/HOW.md` | **`0 problems`** (`21/21 PASS`; 1 bestehende `::warning::` zu `t2-v11-k34100-2` aus `ca-tools` selbst, kein Fehler) |
| `test_build_frame.py` | `timeout --kill-after=10s 120 python3 tools/tests_frame/test_build_frame.py` | `rc = 0` | **`115 passed, 0 failed`** |

## 3. Vollständige 37-Array-Übersicht (`staging/jeserigk-ckrs-coset-2026-11/`)

Alle `37` SHA-256 stimmen überein zwischen Datei auf Platte, kanonischem Hash aus `check_submission.py` und dem jeweiligen `results/.../SHA256SUMS`.

| # | Datei | Zelle `(t, k, v)` | `N` | `ca-tools @ e673ab4` | Delta | Quelle | Bytes | MiB | `ca_verify` (`check_submission`) | SHA-256 |
| ---: | --- | :---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 1 | `CA_1044_3_11_9.txt` | `(3, 11, 9)` | `1044` | `1089` | `-45` | CP-SAT-Liste (`results/phase7/`) | `22,968` | `0.0219` | `0.00 s` | `91b865806d5212a1fc99a688743c6ada1ea0285e482d43297bef5a583a46f0fa` |
| 2 | `CA_1727_3_13_10.txt` | `(3, 13, 10)` | `1727` | `1760` | `-33` | Bauart §14 (`results/phase7_vq/`) | `44,902` | `0.0428` | `0.00 s` | `98e5906a59dc0e0f4aef4a32c2841ce71e0b0c56b2f8aac6728f6a08851f36ec` |
| 3 | `CA_1925_3_13_11.txt` | `(3, 13, 11)` | `1925` | `1991` | `-66` | CP-SAT-Liste (`results/phase7/`) | `52,294` | `0.0499` | `0.01 s` | `94bfc0a39c0fd523ef5474125487cdb7577148bce1097bf064b2a1b405cff764` |
| 4 | `CA_2912_3_15_12.txt` | `(3, 15, 12)` | `2912` | `2955` | `-43` | Bauart §14 (`results/phase7_vq/`) | `93,912` | `0.0896` | `0.01 s` | `9f41ef45a18fe5b773cd309a5b253632dd09d1b548a50d37a3408e1fcb67fb84` |
| 5 | `CA_3211_3_15_13.txt` | `(3, 15, 13)` | `3211` | `3289` | `-78` | Phase 6A (`results/general_tqv/`) | `107,055` | `0.1021` | `0.01 s` | `05984611eca09f5833c9d2311a61cfde19986e750a5a8484210ad952962c9ec8` |
| 6 | `CA_8854_3_21_17.txt` | `(3, 21, 17)` | `8854` | `9376` | `-522` | Bauart §14 (`results/phase7_vq/`) | `439,812` | `0.4194` | `0.05 s` | `8df731279c7495d533b1a729ef7eded790824de82d224a8c874ffc623208bb28` |
| 7 | `CA_9443_3_21_18.txt` | `(3, 21, 18)` | `9443` | `9830` | `-387` | Bauart §14 (`results/phase7_vq/`) | `479,028` | `0.4568` | `0.05 s` | `e3cd323a0881232338651f910687a81fda8c5401a2dc03863f7c1dff428416ec` |
| 8 | `CA_10108_3_21_19.txt` | `(3, 21, 19)` | `10108` | `10279` | `-171` | Phase 6A (`results/general_tqv/`) | `523,374` | `0.4991` | `0.06 s` | `8ff69cf373caa31ff5f0a88fd8e50540dcc10a53375c039926b35cfd64eead5c` |
| 9 | `CA_19025_3_27_21.txt` | `(3, 27, 21)` | `19025` | `19052` | `-27` | Bauart §14 (`results/phase7_vq/`) | `1,253,625` | `1.1955` | `0.21 s` | `77f289f1638481979bb10b3b4e96f73c745ab73be00fb7364a3c4e59380d2d78` |
| 10 | `CA_3332_4_9_7.txt` | `(4, 9, 7)` | `3332` | `3556` | `-224` | CP-SAT-Liste (`results/phase7/`) | `59,976` | `0.0572` | `0.01 s` | `a221268ab90ce2c3d8901842966e44fb03ee4f1bdc919cfa7e31845ea6ede972` |
| 11 | `CA_5824_4_10_8.txt` | `(4, 10, 8)` | `5824` | `6101` | `-277` | CP-SAT-Liste (`results/phase7/`) | `116,480` | `0.1111` | `0.02 s` | `58de207c9a3e1b1870c4703a20bb872bdda899dcbe9573f20c7605cfe0316bbe` |
| 12 | `CA_9396_4_11_9.txt` | `(4, 11, 9)` | `9396` | `9801` | `-405` | CP-SAT-Liste (`results/phase7/`) | `206,712` | `0.1971` | `0.01 s` | `3c84f9ab804618d38dbfc8121cca169567849c4f6c986fb392ff29be6ff28096` |
| 13 | `CA_18997_4_13_10.txt` | `(4, 13, 10)` | `18997` | `20383` | `-1386` | Bauart §14 (`results/phase7_vq/`) | `493,922` | `0.4710` | `0.04 s` | `2bd4886415f8f1c4871ebb7aeaa3ed4e9fcba272cfc8407bd0fa789cbe4bc3a8` |
| 14 | `CA_21175_4_13_11.txt` | `(4, 13, 11)` | `21175` | `21901` | `-726` | CP-SAT-Liste (`results/phase7/`) | `575,234` | `0.5486` | `0.04 s` | `ca50246466727ad7c7980fc344c3a237da6b4f3ac465d6e736af61c09ac526a1` |
| 15 | `CA_37856_4_15_12.txt` | `(4, 15, 12)` | `37856` | `40476` | `-2620` | Bauart §14 (`results/phase7_vq/`) | `1,220,856` | `1.1643` | `0.12 s` | `b5d916c34d0bd89988578fca51179ad6e9b6439e1db67b1611eae2ce3138abf0` |
| 16 | `CA_41743_4_15_13.txt` | `(4, 15, 13)` | `41743` | `42757` | `-1014` | Phase 6A / 5E (`results/t4_nearbush/`) | `1,391,715` | `1.3272` | `0.13 s` | `e8435eb665b9c627982239675bc93f21334ac40d4e8d781cb3592e768233d9a5` |
| 17 | `CA_82432_4_18_14.txt` | `(4, 18, 14)` | `82432` | `82993` | `-561` | Bauart §14 (`results/phase7_vq/`) | `3,334,656` | `3.1802` | `0.52 s` | `dcf37e8dabdadfefb8237cddd7b1e2f80df715b54e054f2e94fa5d721ad8ba53` |
| 18 | `CA_99416_4_19_14.txt` | `(4, 19, 14)` | `99416` | `106023` | `-6607` | Bauart §14 (`results/phase7_vq/`) | `4,221,712` | `4.0261` | `0.83 s` | `881f8187a6f2c4dbd2022cff25a1742a1a39b62bd6672ad89ef4965ef63acbfb` |
| 19 | `CA_106063_4_19_15.txt` | `(4, 19, 15)` | `106063` | `110273` | `-4210` | Bauart §14 (`results/phase7_vq/`) | `4,617,353` | `4.4035` | `1.02 s` | `6db6dbf97f4b0b644ed2e5907432c2f852e5c96bcb68aaa7b891ae8f604ac776` |
| 20 | `CA_113866_4_19_16.txt` | `(4, 19, 16)` | `113866` | `114489` | `-623` | Bauart §14 (`results/phase7_vq/`) | `5,078,308` | `4.8431` | `1.14 s` | `53b0db39d2a010f7642c3e873a65e5d9ad6d1c10aec8a2dcaebbdfa8e97d688c` |
| 21 | `CA_122825_4_19_17.txt` | `(4, 19, 17)` | `122825` | `125137` | `-2312` | Phase 6A (`results/general_tqv/`) | `5,608,045` | `5.3482` | `1.43 s` | `cbf2db9954edd1ecdcd6c7bd3541aaf6aa2ad900b53c04dd7cb071f143bba6fb` |
| 22 | `CA_179417_4_21_18.txt` | `(4, 21, 18)` | `179417` | `188412` | `-8995` | Bauart §14 (`results/phase7_vq/`) | `9,101,532` | `8.6799` | `3.50 s` | `36d945d874fb6c3b87be4c3f24931256dd9d2d0f026ac0684414ab85e55833b3` |
| 23 | `CA_192052_4_21_19.txt` | `(4, 21, 19)` | `192052` | `195301` | `-3249` | Phase 6A (`results/general_tqv/`) | `9,944,106` | `9.4834` | `3.84 s` | `7da2d494c677f7dfc7b5c122c1799101440bb0aabb87fdc07d9b571521896cc3` |
| 24 | `CA_351785_4_25_20.txt` | `(4, 25, 20)` | `351785` | `382933` | `-31148` | Bauart §14 (`results/phase7_vq/`) | `21,404,398` | `20.4128` | `17.22 s` | `43a09235850184dbf7e568339fa9edba0db7d060721a2654f380524b39217f3c` |
| 25 | `CA_456250_4_27_20.txt` | `(4, 27, 20)` | `456250` | `507412` | `-51162` | Bauart §14 (`results/phase7_vq/`) | `29,587,500` | `28.2168` | `29.75 s` | `d70e6fdae82ca64c92d0d19a26af8c8e48bee392af1a64131ad70007215971ff` |
| 26 | `CA_370300_4_25_21.txt` | `(4, 25, 21)` | `370300` | `390612` | `-20312` | Bauart §14 (`results/phase7_vq/`) | `22,917,338` | `21.8557` | `18.89 s` | `edd06b3b669e7fb1994f69d6d225f16556aaed0b37cdbd188157c50063154d83` |
| 27 | `CA_4250_5_7_5.txt` | `(5, 7, 5)` | `4250` | `4375` | `-125` | CP-SAT-Liste (`results/phase7/`) | `59,500` | `0.0567` | `0.00 s` | `0fb696c821d25467be4d6625b37f81d0cb7956afb47350ed9f035ca9104505ec` |
| 28 | `CA_23324_5_9_7.txt` | `(5, 9, 7)` | `23324` | `25039` | `-1715` | CP-SAT-Liste (`results/phase7/`) | `419,832` | `0.4004` | `0.03 s` | `f84786fd02bd88e9a95d2efd27b060089de7c9fbdd83c0d4807c431a6b52c9cf` |
| 29 | `CA_46592_5_10_8.txt` | `(5, 10, 8)` | `46592` | `49128` | `-2536` | CP-SAT-Liste (`results/phase7/`) | `931,840` | `0.8887` | `0.09 s` | `927c206a4b71db106e422b61decdac8667e70a5f3fe753a6d80aca00cdafb370` |
| 30 | `CA_84564_5_11_9.txt` | `(5, 11, 9)` | `84564` | `88209` | `-3645` | CP-SAT-Liste (`results/phase7/`) | `1,860,408` | `1.7742` | `0.36 s` | `adc1b18082687cca9fefa54a867f6b28ab3866f016d6d95e24ba0af7d3c137bd` |
| 31 | `CA_208967_5_13_10.txt` | `(5, 13, 10)` | `208967` | `224844` | `-15877` | Bauart §14 (`results/phase7_vq/`) | `5,433,142` | `5.1814` | `2.87 s` | `591fedf245e1a8fd2c982010ce2af7595df04b180b05258a951dd2b09912881c` |
| 32 | `CA_232925_5_13_11.txt` | `(5, 13, 11)` | `232925` | `240911` | `-7986` | CP-SAT-Liste (`results/phase7/`) | `6,327,574` | `6.0344` | `3.99 s` | `5377d6557520b44d651499f47cb31dff443aecacb6b2906cf0be4076d3b94cea` |
| 33 | `CA_492128_5_15_12.txt` | `(5, 15, 12)` | `492128` | `527205` | `-35077` | Bauart §14 (`results/phase7_vq/`) | `15,871,128` | `15.1359` | `24.95 s` | `240b6c938f6b87088ccebaa50515ebc7e8b8468f07cb03db08259cc731c05028` |
| 34 | `CA_542659_5_15_13.txt` | `(5, 15, 13)` | `542659` | `555841` | `-13182` | Phase 6A (`results/general_tqv/`) | `18,092,295` | `17.2542` | `33.92 s` | `1a78674e85083dcc37b8c27db839e6254c9eed2ca1b46f00f382219b991b0508` |
| 35 | `CA_163268_6_9_7.txt` | `(6, 9, 7)` | `163268` | `175273` | `-12005` | CP-SAT-Liste (`results/phase7/`) | `2,938,824` | `2.8027` | `0.85 s` | `3b6030f0ce6afe9c80a2fd86fa8f55e4de923610daafb579e904e65715f1c12e` |
| 36 | `CA_372736_6_10_8.txt` | `(6, 10, 8)` | `372736` | `393018` | `-20282` | CP-SAT-Liste (`results/phase7/`) | `7,454,720` | `7.1094` | `6.48 s` | `7e051655edab7e11a69d8a16ac0865e8a56543b2d2071161e9cb1ce3cf99a6e6` |
| 37 | `CA_761076_6_11_9.txt` | `(6, 11, 9)` | `761076` | `793881` | `-32805` | CP-SAT-Liste (`results/phase7/`) | `16,743,672` | `15.9680` | `39.92 s` | `aaee4a1dfde48c45b7e7b4e99d574e2d3eda28982fd72accf16e2529a03b8f74` |

## 4. Offene Punkte & Nachlauf für Review

1. `tools/consistency.py --check --pr` lief im Komplettlauf bei `check_constructions` (ca. 180 Bestandszertifikate von `ca-tools`) ins ~10-Min.-Shell-Cap (`nicht vollendet (Shell-Cap)`); die übrigen `21/22` Prüffunktionen inkl. `check_links` (mit `HOW.md` im Index) bestanden einzeln mit `0 problems`. Im Review auf einer Maschine ohne 10-Min.-Shell-Cap nachzuziehen.
2. Allgemeines Beweisargument in `docs/PHASE7_T2_REDUCTION.md` ist noch nicht von einem unbeteiligten Drittmodell geprüft (`RULES.md` 2d; alle `37` Einzelarrays sind erschöpfend dual-verifiziert).
3. Literaturprüfung ist nicht vollständig (`docs/LITERATURE_CHECK_PHASE7_VQ.md` §5; u. a. ältere Literatur, neuere Zenodo-Fassungen von Bai/Sitjar, Primärquelle für `(5, 7, 5) = 4375`).
4. Keine Außenwirkung ausgelöst; externe Einreichung erfordert ausdrückliche Freigabe durch Justus.

## 5. Nachtrag 2026-11-26, ab 21:20 MEZ: Korrektur nach Prüfung (Claude, Prüfer-Chat, Branch `claude/stage-phase7-37-korrektur`)

Anlass: [`docs/STAGING_REVIEW_PR34.md`](STAGING_REVIEW_PR34.md) §3 (acht Befunde am Text). Die `37` Array-Dateien sind unverändert (kein Diff gegen `aca3fc6`). Geändert sind nur `HOW.md` und `claims.csv`:

- Alle Blob-Links und die Angabe „pinned at commit“ zeigen jetzt auf `da59460e9b5c1d1ac235a5f484454352bca77cbe` (enthält `main @ 5afa407` und den Prüfvermerk); `23` verschiedene Links, alle an diesem Commit vorhanden.
- `claims.csv`: in `31` Zeilen nennt `source_detail` zusätzlich `scripts/gen_general_tqv.py` (wird von `phase7_lift.py` und `phase7_reps_vq.py` importiert). Alle anderen Felder bis auf den Commit in den Links unverändert (feldweise verglichen).
- `HOW.md`: CKRS-Zitat mit Vorbehalt (Nummerierung des Preprints, Lesart dieses Repos, „Verfeinerung“ erklärt); Löser-Modus je Liste und die Läufe ohne Verbesserung; beide Ausgangs-Arrays der Analyse; Verifikation mit genauer Angabe der Negativkontrollen und Links auf die Nachträge; „Open items“ auf dem Stand nach PR `#33`; neuer offener Punkt, dass die geschlossene Liste nicht überall kleinstmöglich ist (`(5, 4)`, `(7, 6)`).

Damit sind die offenen Punkte 1 und 2 aus §4 erledigt (Komplettlauf von `consistency.py`: siehe Prüfvermerk; Drittmodell: [`docs/THIRD_MODEL_REVIEW_PHASE7.md`](THIRD_MODEL_REVIEW_PHASE7.md)). Die Größen- und Hash-Angaben zu `HOW.md`, `claims.csv` und zum Gesamtordner in §1 gelten für den Stand `aca3fc6`; neu:

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| `HOW.md` | `12797` | `ca5e79b778d8d677002a74afcf0adf90e8b77803d836f2764f9215e562fcc1f2` |
| `claims.csv` | `44587` | `91aac891a1001ce247c8590334cb0934556689039166103ae9f66199fe06c9b1` |
| Ordner (`39` Dateien) | `199087132` | `189,8643 MiB <= 200 MiB` |

Einschränkung: Die Korrekturen hat der Prüfer selbst geschrieben. Der geänderte Text ist danach von niemandem sonst gelesen worden; die Werkzeugläufe prüfen Form, Größen und Arrays, nicht den Inhalt des Textes.
