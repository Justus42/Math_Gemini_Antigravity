# Verifikations-Log: Phase 8, Baer-Gitter (`results/phase8_baer/`)

- **Datum:** 2026-11-27, 06:41–07:31 MEZ. Lauf-ID `P8-BAER-ARRAYS`. Branch `claude/phase8-untergrenze-baer` (Basis `origin/main @ 6994817`).
- **Rolle:** Rechnung des Erzeugers der Bauart. Keine Fremd-Reproduktion, eine Maschine (`2` vCPU, Python `3.13.18`).
- **Befehl:** `python3 scripts/phase8/pruefe_baer.py ARBEITSVERZEICHNIS ZAEHLER Q:F:T[:py] ...` aus dem Wurzelverzeichnis; `ZAEHLER` mit `gcc -O3 -march=native -o zaehler scripts/pruefer/zaehler.c`, `verifiers/ca_verify` mit `gcc -O3 -march=native -pthread -o verifiers/ca_verify verifiers/ca_verify.c -lm`.
- **Vorab:** `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`; `git diff main -- verifiers/` leer; `python3 verifiers/test_verifiers.py` `23/23`.
- **Listen:** `data/phase8_baer/` (SHA-256 in `data/phase8_baer/SHA256SUMS`), erzeugt mit `python3 scripts/phase8/baer_gitter.py Q F --out DATEI` (std-only, ohne Löser). Lift: `scripts/phase7_lift.py --q Q [--v V] --reps LISTE --check-m --t T --out DATEI`.
- **Spalten:** „Lücken eigener Zähler“ = fehlende Punkte / Geradentreffer / Symbolpaare nach `baer_gitter.check_model`; `zaehler` = `scripts/pruefer/zaehler.c`; Negativkontrolle = Array ohne letzte Zeile, Exit-Code von `ca_verify` (erwartet `1`).
- **Abgelegt** sind fünf Arrays (`SHA256SUMS` in diesem Ordner): `CA_17625_3_27_20.txt`, `CA_18125_3_27_21.txt`, `CA_18750_3_27_22.txt`, `CA_19375_3_27_23.txt`, `CA_81920_4_18_14.txt`. Sie sind dual-verifiziert und kleiner als `ca-tools` am Commit `697325b`. Alle anderen sind mit dem Befehl oben erzeugbar.
- **Gültig nach `RULES.md` §3** sind nur Zeilen, in denen `ca_verify` **und** `verify_independent.py` Exit `0` haben. Die Zeilen mit „nicht gelaufen“ sind es nicht.
- **Negativkontrolle bei `q = 4`, `v = 2, 3`:** Exit `0`, weil die letzte Zeile dort überzählig ist (Arrays mit `72` und `80` Zeilen; die Tabelle führt `12` und `33`). Kein Befund gegen die Verifier.
- **Wortwahl (Regel 4):** „kleiner als `ca-tools` am Commit `697325b`“. Kein Neuheitsanspruch. Keine Einreichung ohne Freigabe.

## `t = 3` (06:41–06:42 MEZ, `37 s`)

| q | v | F | `|R|` | Lücken eigener Zähler | `phase7_lift --check-m` | t | N | `ca_verify` | `zaehler` | `verify_independent.py` | Negativkontrolle | SHA-256 Liste | SHA-256 Array |
| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| 4 | 2 | 0 | 18 | 0/0/0 | Exit 0 | 3 | 72 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 0 | `92b8cc50135319cb…` | `624e8f7a1ec24073…` |
| 4 | 3 | 1 | 20 | 0/0/0 | Exit 0 | 3 | 80 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 0 | `3de2951fe999db76…` | `e677f34839cadc3e…` |
| 4 | 4 | 2 | 24 | 0/0/0 | Exit 0 | 3 | 96 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `8f54b30079759d91…` | `025763d28cb6bdb5…` |
| 9 | 6 | 0 | 93 | 0/0/0 | Exit 0 | 3 | 837 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `34dd5767d8d1ab1b…` | `0322773304cd5a92…` |
| 9 | 7 | 1 | 99 | 0/0/0 | Exit 0 | 3 | 891 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `8a9b96fead6b8eb3…` | `22a9507428faa693…` |
| 9 | 8 | 2 | 108 | 0/0/0 | Exit 0 | 3 | 972 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `9fee35f68e70cb5d…` | `42bb7cd8030c26e7…` |
| 9 | 9 | 3 | 117 | 0/0/0 | Exit 0 | 3 | 1053 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `1853ea2f8770313e…` | `f0b257167069cb49…` |
| 16 | 12 | 0 | 292 | 0/0/0 | Exit 0 | 3 | 4672 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `3181e26eae34a91d…` | `dab1ba7c3cf1c637…` |
| 16 | 13 | 1 | 304 | 0/0/0 | Exit 0 | 3 | 4864 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `6f1b6aa5444ddbd9…` | `2c82562d4cbdefe6…` |
| 16 | 14 | 2 | 320 | 0/0/0 | Exit 0 | 3 | 5120 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `e7f60c85b9a6da8a…` | `ee94f73915647cab…` |
| 16 | 15 | 3 | 336 | 0/0/0 | Exit 0 | 3 | 5376 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `c49cfca582f10aa0…` | `c37df6a1b253104b…` |
| 16 | 16 | 4 | 352 | 0/0/0 | Exit 0 | 3 | 5632 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | Exit 0 (0 s) | Exit 1 | `243450beb23113f5…` | `8bf8ae8341190220…` |
| 25 | 20 | 0 | 705 | 0/0/0 | Exit 0 | 3 | 17625 | Exit 0 (0.1 s) | Exit 0 (0.2 s) | Exit 0 (4 s) | Exit 1 | `ce2d264c896a89d1…` | `4a61b91d0c9ac710…` |
| 25 | 21 | 1 | 725 | 0/0/0 | Exit 0 | 3 | 18125 | Exit 0 (0.1 s) | Exit 0 (0.2 s) | Exit 0 (5 s) | Exit 1 | `a535d40417e047d7…` | `e889ea91cb873b0c…` |
| 25 | 22 | 2 | 750 | 0/0/0 | Exit 0 | 3 | 18750 | Exit 0 (0.1 s) | Exit 0 (0.2 s) | Exit 0 (5 s) | Exit 1 | `681c5978f70ac153…` | `ef4040897237a8f1…` |
| 25 | 23 | 3 | 775 | 0/0/0 | Exit 0 | 3 | 19375 | Exit 0 (0.0 s) | Exit 0 (0.2 s) | Exit 0 (6 s) | Exit 1 | `b98f63eeaccb86f8…` | `a09a3519ddbc64a9…` |
| 25 | 24 | 4 | 800 | 0/0/0 | Exit 0 | 3 | 20000 | Exit 0 (0.0 s) | Exit 0 (0.2 s) | Exit 0 (6 s) | Exit 1 | `4a080948059837be…` | `3c445fd77ee1b7d4…` |
| 25 | 25 | 5 | 825 | 0/0/0 | Exit 0 | 3 | 20625 | Exit 0 (0.0 s) | Exit 0 (0.1 s) | Exit 0 (6 s) | Exit 1 | `e2481696f2760147…` | `72a7cf64dffc7c55…` |

## `t = 4` (06:42–06:58 MEZ, `954 s`)

| q | v | F | `|R|` | Lücken eigener Zähler | `phase7_lift --check-m` | t | N | `ca_verify` | `zaehler` | `verify_independent.py` | Negativkontrolle | SHA-256 Liste | SHA-256 Array |
| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| 16 | 12 | 0 | 292 | 0/0/0 | Exit 0 | 4 | 74752 | Exit 0 (0.4 s) | Exit 0 (1.2 s) | Exit 0 (28 s) | Exit 1 | `3181e26eae34a91d…` | `4c67e2c1310da628…` |
| 16 | 13 | 1 | 304 | 0/0/0 | Exit 0 | 4 | 77824 | Exit 0 (0.8 s) | Exit 0 (1.3 s) | Exit 0 (39 s) | Exit 1 | `6f1b6aa5444ddbd9…` | `d3709ac916c2e7f9…` |
| 16 | 14 | 2 | 320 | 0/0/0 | Exit 0 | 4 | 81920 | Exit 0 (0.7 s) | Exit 0 (1.3 s) | Exit 0 (48 s) | Exit 1 | `e7f60c85b9a6da8a…` | `0674f3cd9c1cf069…` |
| 16 | 15 | 3 | 336 | 0/0/0 | Exit 0 | 4 | 86016 | Exit 0 (1.1 s) | Exit 0 (1.0 s) | Exit 0 (58 s) | Exit 1 | `c49cfca582f10aa0…` | `740b29124da2cadb…` |
| 16 | 16 | 4 | 352 | 0/0/0 | Exit 0 | 4 | 90112 | Exit 0 (0.6 s) | Exit 0 (0.5 s) | Exit 0 (60 s) | Exit 1 | `243450beb23113f5…` | `8e93fc85ecf00c78…` |
| 25 | 20 | 0 | 705 | 0/0/0 | Exit 0 | 4 | 440625 | Exit 0 (37.0 s) | Exit 0 (44.2 s) | nicht gelaufen | Exit 1 | `ce2d264c896a89d1…` | `86d020e57784278c…` |
| 25 | 21 | 1 | 725 | 0/0/0 | Exit 0 | 4 | 453125 | Exit 0 (35.7 s) | Exit 0 (53.5 s) | nicht gelaufen | Exit 1 | `a535d40417e047d7…` | `e9593c2923aeeb7f…` |
| 25 | 22 | 2 | 750 | 0/0/0 | Exit 0 | 4 | 468750 | Exit 0 (42.6 s) | Exit 0 (53.8 s) | nicht gelaufen | Exit 1 | `681c5978f70ac153…` | `088281e511c4cbc1…` |
| 25 | 23 | 3 | 775 | 0/0/0 | Exit 0 | 4 | 484375 | Exit 0 (52.9 s) | Exit 0 (47.6 s) | nicht gelaufen | Exit 1 | `b98f63eeaccb86f8…` | `ee99e18dd047de1d…` |
| 25 | 24 | 4 | 800 | 0/0/0 | Exit 0 | 4 | 500000 | Exit 0 (52.9 s) | Exit 0 (37.8 s) | nicht gelaufen | Exit 1 | `4a080948059837be…` | `a63b91b093d33a53…` |
| 25 | 25 | 5 | 825 | 0/0/0 | Exit 0 | 4 | 515625 | Exit 0 (24.1 s) | Exit 0 (23.0 s) | nicht gelaufen | Exit 1 | `e2481696f2760147…` | `7c3208372873a106…` |

Zur letzten Zeile (`v = 25`, 07:30–07:31 MEZ, `77 s`): Ein Lauf von `verify_independent.py` für `CA(515625; 4, 27, 25)` lief von 06:42 bis 07:30 MEZ und wurde an der Zeitgrenze ohne Ergebnis abgebrochen. Das Array ist damit **nicht** dual-verifiziert.
