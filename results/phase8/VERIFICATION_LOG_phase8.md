# Verifikations-Log: Phase 8 (`results/phase8/`)

- **Datum:** 2026-11-27, 01:35–01:36 MEZ (`73 s` für alle Läufe). Lauf-ID `P8-PRUEFUNG-LISTEN`.
- **Branch:** `claude/phase8-klassen-ohne-gerade` (Basis `origin/main @ d04a97b`).
- **Befehl:** `python3 scripts/phase8/pruefe_listen.py <zaehler> <arbeitsverzeichnis>` aus dem Wurzelverzeichnis; `zaehler` mit `gcc -O2 -o zaehler scripts/pruefer/zaehler.c`, `verifiers/ca_verify` mit `gcc -O3 -march=native -pthread -o verifiers/ca_verify verifiers/ca_verify.c -lm`.
- **Vorab:** `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`; `git diff origin/main -- verifiers/` leer; `python3 verifiers/test_verifiers.py` `23/23`.
- **Hardware:** `Intel(R) Xeon(R) Processor @ 2.10GHz`, `2` vCPU; Python `3.13.18`. Eine Maschine, keine Fremd-Reproduktion.
- **Listen:** `data/phase8/` (SHA-256 in `data/phase8/SHA256SUMS`). Lift: `scripts/phase7_lift.py --q Q [--v V] --reps LISTE --check-m --t T --out DATEI`.
- **Spalten:** `ca_verify` und `verify_independent` mit Exit-Code und Laufzeit; „Nachbau byte-gleich“ vergleicht das Array aus `scripts/pruefer/nachbau.py` mit dem aus `scripts/phase7_lift.py`; Negativkontrolle = Array ohne letzte Zeile, Exit-Codes von `ca_verify` / `verify_independent`.
- **Abgelegt** sind nur die sieben mit „(abgelegt)“ markierten Arrays; die übrigen sind mit dem Befehl oben aus den Listen erzeugbar (SHA-256 in der Tabelle).
- **Wortwahl (Regel 4):** Vergleiche gelten als „kleiner als `ca-tools` am Commit `f682ba3`“; siehe [`docs/PHASE8_UEBERSICHT.md`](../../docs/PHASE8_UEBERSICHT.md) §4. Keine Einreichung ohne Freigabe.

| Liste | `t` | Array | SHA-256 (Array) | `M(R)` Lücken | `ca_verify` | `verify_independent` | Nachbau byte-gleich | `zaehler` | Negativkontrolle |
| --- | :---: | --- | --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `R_q9_m113.txt` | 3 | `CA(1017; 3, 11, 9)` (abgelegt) | `a6fd20dc6b747b53fe132197aebff23772fdd666fd21b094df33ed4fcfb7e742` | 0 | Exit 0 (0.0 s) | Exit 0 (0.0 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q9_m113.txt` | 4 | `CA(9153; 4, 11, 9)` (abgelegt) | `9204e3235d9343824da94c957243051fa68a3687a45144626351cfb417c3faf0` | 0 | Exit 0 (0.0 s) | Exit 0 (0.5 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q11_m170.txt` | 3 | `CA(1870; 3, 13, 11)` (abgelegt) | `30c5db61f054af9747c17b7b5bd900e3a280fb05515a0def0aacd9448bbed4cc` | 0 | Exit 0 (0.0 s) | Exit 0 (0.1 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q11_m170.txt` | 4 | `CA(20570; 4, 13, 11)` (abgelegt) | `413633790af6ada219240e7171868e64f4781fc82b4e160641227b94baf64085` | 0 | Exit 0 (0.0 s) | Exit 0 (2.5 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q13_m238.txt` | 3 | `CA(3094; 3, 15, 13)` (abgelegt) | `c51facaa443d428b0c9b50ea82c7ea23985e5e8adbd9506fc767ee760ee28240` | 0 | Exit 0 (0.0 s) | Exit 0 (0.1 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q13_m238.txt` | 4 | `CA(40222; 4, 15, 13)` (abgelegt) | `e3cec78d335b18eada5dfae1d8499046ee7579574264d3f1b18d92ebde30e570` | 0 | Exit 0 (0.1 s) | Exit 0 (14.1 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q17_m412.txt` | 3 | `CA(7004; 3, 19, 17)` | `3fc6f3968c564de8a6a3e79978f13487cfb5480f55016bb7fcd2b7c4f988f492` | 0 | Exit 0 (0.0 s) | Exit 0 (0.7 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q19_m513.txt` | 3 | `CA(9747; 3, 21, 19)` (abgelegt) | `cd08a80045c0967784dffa4d4604e1e6d541017d5c740001f2ff5a538a3b0274` | 0 | Exit 0 (0.0 s) | Exit 0 (1.6 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q23_m746.txt` | 3 | `CA(17158; 3, 25, 23)` | `5a6088e6495edc3ad51642c2b4688f8c049dcb9ec2c95a4361689e4a76c90d77` | 0 | Exit 0 (0.0 s) | Exit 0 (5.5 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q23_v22_m722.txt` | 3 | `CA(16606; 3, 25, 22)` | `9b9c7fffe7be7b39875a63fdb070645360a0b58d2989cc29ee2c3ccc84e38d66` | 0 | Exit 0 (0.2 s) | Exit 0 (4.6 s) | ja | Exit 0 | Exit 1 / 1 |
| `R_q29_m1190.txt` | 3 | `CA(34510; 3, 31, 29)` | `486af973530834e642d860f1579eae18682209f8ba5202ec3fda4a30a451f977` | 0 | Exit 0 (0.1 s) | nicht gelaufen | ja | Exit 0 | Exit 1 / – |
| `R_q31_m1356.txt` | 3 | `CA(42036; 3, 33, 31)` | `822af65deb79bb584a5dd5c0f9566e44a9f8e0dfa963e656a6f39a2662d3d429` | 0 | Exit 0 (0.2 s) | nicht gelaufen | ja | Exit 0 | Exit 1 / – |
| `R_q37_m1942.txt` | 3 | `CA(71854; 3, 39, 37)` | `284930670f89634976eff498f6f83397846fe3199fe1a70a1d08569577d995d9` | 0 | Exit 0 (0.5 s) | nicht gelaufen | ja | Exit 0 | Exit 1 / – |
