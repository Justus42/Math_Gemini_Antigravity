# Phase-9-Pilot: Biaffines 3D-Modell `M_3(R_3)` (`k = q + 3`, `3 <= t <= q`)

Datum: 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, Basis `main @ 0bcbe2b`).
Hardware: Intel Xeon CPU @ 2.30 GHz, 2 vCPU / 2 Threads, `gcc 13.3.0` (`-O3 -march=native -pthread`), Python 3.12 (`std`-only).
Keine Außenwirkung auf `chrispbsmolen/ca-tools` (Tabellenvergleich nur lesend am Commit `ff6cf963fca4f347177d0617390312c3913c48b6`), kein GitHub-Actions-Lauf, kein Merge nach `main`.

## 1. Werkzeuge & Gate-0-Verifikation

- **Prüf- und Lift-Skript:** [`scripts/phase9_m3_lift.py`](../../scripts/phase9_m3_lift.py) (`std`-only + `GeneralGF` aus `scripts/gen_general_tqv.py`).
  - Prüft alle vier `M_3`-Bedingungen (Typ 0..3) in den Modi `--mode tspec --t T` und `--mode full-bg3`.
  - Liftet `R_3 subset F_q^6` mit dem Kern `K_t^(3) = { ((g(x))_{x in F_q}, 0, 0, 0) : deg g <= t - 4 }` auf `CA(|R_3| * q^(t-3); t, q+3, q)`.
- **C-Solver:** [`scripts/phase9_m3_search.c`](../../scripts/phase9_m3_search.c) (O(1)-inkrementelle Zähltabellen für Typ 0..3 mit gecachten Zeilenprojektionen, fokussiertes Tabu+PAWS sowie fokussiertes Simulated Annealing `--algo sa`, `--threads 2`, hartes Timeout-Cap `<= 90 s`).
- **Gate 0 (`python3 scripts/phase9_m3_lift.py --gate0`):**
  1. `q = 5, t = 4`, lineare Basis `R_base` (`125` Vertreter `(c0, c1, c2, c2, c0, (c0+c1+2*c2) mod 5)`, `sha256: 5df5b777704689017de0366b3ed4721b774aaf2c7d98b726ff706911f9075d8b`):
     - `--check-m3 --mode tspec --t 4`: `|D1| = 10`, `|N2| = 10`, exakt `Typ0 = 0`, `Typ1 = 0`, `Typ2 = 600` (`6` fehlende 4-Mengen × `100`), `Typ3 = 0`.
     - Exhaustive Gegenprüfung auf dem gelifteten `CA(625; 4, 8, 5)`: `Typ0 = 0`, `Typ1 = 0`, `Typ2 = 3000` (`600 * 5`), `Typ3 = 0`.
  2. `q = 3, t = 3` (`5` zufällige Listen `m = 10, 18, 27, 36, 45` + `1` voll gedeckte Referenzliste `m = 152`): `0` Abweichungen zwischen `--check-m3` und Exhaustivzählung aller `C(6, 3) = 20` 3-Mengen (`total = 373, 274, 201, 124, 91, 0`).
  3. Bonus `GF(4)`, `t = 4` (`m = 60`): exakte Skalierung `M3 = (26, 297, 458, 26)` vs. `EX = (104, 1188, 1832, 416)` (`4x, 4x, 4x, 16x`), `0` Abweichungen.
- **C-Solver Self-Test (`/tmp/phase9_m3_search --self-test`):** `5/5` Fälle (`q = 3 tspec/full-bg3`, `q = 4 tspec`, `q = 5 tspec/full-bg3`), je `2000` Züge + periodischer Voll-Rebuild + Repair-Move-Prüfung: `0` Abweichungen (`PASS`).

## 2. Suchläufe (Piloten 1–4, alle harten Timeouts `<= 90 s`)

| Lauf | Pilot | Ziel `(q, mode, t, m)` | Algorithmus & Parameter | Budget / Dauer | Durchsatz (`mv/s`, `ev/s`, 2T) | Ergebnis |
| --- | --- | --- | --- | :---: | :---: | --- |
| `P9-1a` | Pilot 1 | `q=5, tspec t=4, m=200` | PAWS, `init=base`, `w03=1`, `ten=6`, `sm=40`, `rst=1.5M`, `seed=9101` | 60 s / 60,033 s | 130.080 / 4.062.740 | `TIMEOUT (best_unc=25)`, `by_type=(3,0,1,21)` |
| `P9-1c` | Pilot 1 | `q=5, tspec t=4, m=210` | PAWS, `init=base`, `w03=6`, `ten=6`, `sm=40`, `rst=500k`, `seed=9103` | 60 s / 60,015 s | 123.258 / 4.141.790 | `TIMEOUT (best_unc=24)`, `by_type=(3,1,15,5)` |
| `P9-1d` | Pilot 1 | `q=5, tspec t=4, m=200` | PAWS, Warmstart ab `m=215`, `w03=4`, `ten=8`, `sm=60`, `rst=2M`, `seed=9104` | 60 s / 60,026 s | 131.288 / 4.098.755 | `TIMEOUT (best_unc=60)`, `by_type=(2,17,31,10)` |
| `P9-1e` | Pilot 1 | `q=5, tspec t=4, m=200` | PAWS, `init=rand`, `w03=2`, `ten=8`, `sm=60`, `rst=3M`, `seed=9105` | 60 s / 60,027 s | 133.061 / 4.147.823 | `TIMEOUT (best_unc=32)`, `by_type=(3,0,13,16)` |
| `P9-1f` | Pilot 1 | `q=5, tspec t=4, m=210` | PAWS, `init=rand`, `w03=2`, `ten=8`, `sm=60`, `rst=3M`, `seed=9106` | 60 s / 60,030 s | 128.276 / 4.330.650 | `TIMEOUT (best_unc=15)`, `by_type=(1,1,5,8)` |
| `P9-1-SA` | Pilot 1 | `q=5, tspec t=4, m=200` | SA (`T: 2.0->0.08`), `init=base`, `seed=9110` | 60 s / 60,004 s | 1.222.432 / 1.222.432 | `TIMEOUT (best_unc=69)`, `by_type=(0,0,49,20)` |
| `P9-1g-SA` | Pilot 1 | `q=5, tspec t=4, m=210` | SA (`T: 2.0->0.08`), `init=rand`, `seed=9116` | 60 s / 60,001 s | 1.793.057 / 1.793.057 | `TIMEOUT (best_unc=29)`, `by_type=(15,0,0,14)` |
| `P9-2-45` | Pilot 2 | `q=3, full-bg3, m=45` | PAWS, `init=rand`, `w03=2`, `seed=9245` | 10 s / 0,002 s | 162.222 / 2.608.516 | **`SOLVED` (`unc=0`, `unique=45`)** |
| `P9-2-44` | Pilot 2 | `q=3, full-bg3, m=44` | PAWS, `init=rand`, `w03=2`, `seed=9244` | 10 s / 0,014 s | 276.656 / 4.504.622 | **`SOLVED` (`unc=0`, `unique=44 < 45`)** |
| `P9-2-43` | Pilot 2 | `q=3, full-bg3, m=43` | PAWS, `init=rand`, `w03=4`, `seed=9243` | 10 s / 1,976 s | 293.931 / 4.648.992 | **`SOLVED` (`unc=0`, `unique=43 < 45`)** |
| `P9-2-42` | Pilot 2 | `q=3, full-bg3, m=42` | PAWS `w03=2`/`w03=8` (`seeds=9242,9252`) & SA (`seed=9302`) | 3×10 s / 30,021 s | 291k–3,59M | `TIMEOUT (best_unc=2)`, `by_type=(0,0,0,2)` (SA: `6`) |
| `P9-2-41` | Pilot 2 | `q=3, full-bg3, m=41` | PAWS `w03=8` (`seed=9251`, 8 s) & SA (`seed=9301`, 10 s) | 18 s / 18,008 s | 289k / 3,63M | `TIMEOUT (best_unc=4)`, `by_type=(0,0,0,4)` (SA: `8`) |
| `P9-2-40` | Pilot 2 | `q=3, full-bg3, m=40` | PAWS `w03=2` (`seed=9240`, 10 s) & SA (`seed=9300`, 10 s) | 20 s / 20,015 s | 305k / 3,66M | `TIMEOUT (best_unc=6)`, `by_type=(0,0,0,6)` (SA: `10`) |
| `P9-2-38` | Pilot 2 | `q=3, full-bg3, m=38` | PAWS `w03=2` (`seed=9238`, 10 s) | 10 s / 10,014 s | 309.436 / 4.123.182 | `TIMEOUT (best_unc=14)`, `by_type=(7,0,0,7)` |
| `P9-3a` | Pilot 3 | `q=5, full-bg3, m=215` | PAWS, `init=rand`, `w03=3`, `ten=8`, `sm=60`, `rst=2M`, `seed=9301` | 90 s / **82,505 s** | 66.577 / 2.238.900 | **`SOLVED` (`unc=0`, `unique=215 < 225`, `rst=0`, `tid=1`)** |
| `P9-3b` | Pilot 3 | `q=5, full-bg3, m=200` | PAWS, Warmstart ab `m=215`, `w03=3`, `ten=8`, `sm=60`, `rst=2M`, `seed=9302` | 90 s / 90,019 s | 66.978 / 2.043.446 | `TIMEOUT (best_unc=34)`, `by_type=(8,0,0,26)` |
| `P9-4-105` | Pilot 4 | `q=4, tspec t=4, m=105` | PAWS `seeds=9505,9415,9425` (65 s: `best_unc=1`); **SA `init=rand`, `seed=9435`** | 15 s / **7,497 s** | 2.102.338 / 2.102.338 | **`SOLVED` (`unc=0`, `unique=105 < 112`, `tid=1`)** |
| `P9-4-106` | Pilot 4 | `q=4, tspec t=4, m=106` | PAWS, `init=rand`, `w03=1`, `ten=6`, `sm=40`, `seed=9436` | 15 s / **13,791 s** | 289.538 / 6.891.205 | **`SOLVED` (`unc=0`, `unique=106 < 112`, `tid=1`)** |
| `P9-4-100` | Pilot 4 | `q=4, tspec t=4, m=100` | PAWS `seed=9500` (15 s: `best_unc=9`) & SA `seed=9550` (15 s) | 30 s / 30,007 s | 291k / 3,46M | `TIMEOUT (best_unc=3)` (SA), `by_type=(1,0,0,2)` |
| `P9-4-96` | Pilot 4 | `q=4, tspec t=4, m=96` | PAWS `seed=9496` (15 s: `best_unc=23`) & SA `seed=9546` (15 s) | 30 s / 30,016 s | 288k / 3,30M | `TIMEOUT (best_unc=12)` (SA), `by_type=(9,0,0,3)` |
| `P9-4-95` | Pilot 4 | `q=4, tspec t=4, m=95` | PAWS `seed=9495` (15 s: `best_unc=11`) & SA `seed=9545` (15 s) | 30 s / 30,010 s | 291k / 3,39M | `TIMEOUT (best_unc=17)` (SA; PAWS `11`) |

## 3. Ablage, Dual-Verifikation & Negativkontrollen (`8/8 PASS`)

Alle `6` gefundenen Vertreterlisten (`unc = 0`) liegen in `data/phase9_m3/` (`sha256sum -c data/phase9_m3/SHA256SUMS`: `6/6 OK`) und bestehen `scripts/phase9_m3_lift.py --check-m3` mit `0` Lücken:

| Liste (`data/phase9_m3/`) | SHA-256 (Liste) | Modus | Geliftetes Array (`/tmp/phase9_m3/`) | SHA-256 (Array) | `ca_verify` POS / NEG | `verify_independent.py` POS / NEG | Elliptisch `2q^3-q^2` | `ca-tools @ ff6cf96` |
| --- | --- | --- | --- | --- | :---: | :---: | :---: | :---: |
| `R3_q3_fullbg3_m43.txt` | `453457d0…` | `full-bg3` | `CA(43; 3, 6, 3)` | `faf07d0975430e6bd728e40511e9f1bf55ed64f207674bbd6a2821757e29866b` | `0 (4 ms)` / `1 (4 ms)` | `0 (57 ms)` / `1 (55 ms)` | `45` (`-2`) | `33` (`+10`) |
| `R3_q3_fullbg3_m44.txt` | `81182c3b…` | `full-bg3` | `CA(44; 3, 6, 3)` | `07060a2628e7b6bc2a634df8737454ac10105f19e4feb7c2dce059edf12766d9` | `0 (3 ms)` / `1 (3 ms)` | `0 (60 ms)` / `1 (56 ms)` | `45` (`-1`) | `33` (`+11`) |
| `R3_q3_fullbg3_m45.txt` | `de48caba…` | `full-bg3` | `CA(45; 3, 6, 3)` | `1e99bd9a306ca30c804e064d579655c95f9779ae38b7c9a6e5c7b486406258f0` | `0 (3 ms)` / `1 (3 ms)` | `0 (59 ms)` / `1 (57 ms)` | `45` (`0`) | `33` (`+12`) |
| `R3_q4_t4_tspec_m105.txt` | `bbdfba28…` | `tspec t=4` | `CA(420; 4, 7, 4)` | `529c117dd93171367020477c6ae80a722308632630a8ad125c06cdf0ea1d2021` | `0 (3 ms)` / `1 (3 ms)` | `0 (61 ms)` / `1 (63 ms)` | `448` (`-28`) | `384` (`+36`) |
| `R3_q4_t4_tspec_m106.txt` | `01101152…` | `tspec t=4` | `CA(424; 4, 7, 4)` | `b40837105c922057c9f82bec4c4e34498f8234206364029ef362c7509cc6dd2c` | `0 (3 ms)` / `1 (3 ms)` | `0 (61 ms)` / `1 (64 ms)` | `448` (`-24`) | `384` (`+40`) |
| `R3_q5_fullbg3_m215.txt` | `b3d1f877…` | `full-bg3` | `CA(215; 3, 8, 5)` | `20c1ea82b2352ee2dc799d885be3b0072e5d5f27a6e77abae0d6c5f72663f3e3` | `0 (3 ms)` / `1 (3 ms)` | `0 (61 ms)` / `1 (60 ms)` | `225` (`-10`) | `165` (`+50`) |
| `R3_q5_fullbg3_m215.txt` | `b3d1f877…` | `full-bg3` | `CA(1075; 4, 8, 5)` | `cf6f45d63995f4767cb1e45af024ba058104058dfecd8a06800749d6bad0e68b` | `0 (4 ms)` / `1 (4 ms)` | `0 (76 ms)` / `1 (78 ms)` | `1125` (`-50`) | `1006` (`+69`) |
| `R3_q5_fullbg3_m215.txt` | `b3d1f877…` | `full-bg3` | `CA(5375; 5, 8, 5)` | `6a35ccaa919f9285cd370471c1d9cad1ab91c6a533fc9a37286867c7981bfece` | `0 (7 ms)` / `1 (7 ms)` | `0 (166 ms)` / `1 (174 ms)` | `5625` (`-250`) | `5000` (`+375`) |

Negativkontrolle: je Array letzte Zeile (`N - 1`) entfernt → beide Verifier `rc = 1` (`8/8 FAIL`).
Verifier-Integrität: `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23 PASS`.

## 4. Einordnung & Tabellenabgleich für größere `q` (`ca-tools @ ff6cf96`)

1. **Pilot 2 geklärt:** Im vollen `t`-unabhängigen `BG(3, q)` existieren Listen strikt unter `2 q^3 - q^2`:
   - `q = 3`: `m = 43 < 45` (`-2`, `-4,4 %`).
   - `q = 5`: `m = 215 < 225` (`-10`, `-4,4 %`), hebt gleichzeitig auf `t = 3, 4, 5` (`215`, `1075`, `5375`).
2. **Pilot 1 & 4:** Alle drei getesteten `q` (`3, 4, 5`) unterbieten die elliptische Schranke `2 q^3 - q^2`, bleiben aber über den bestehenden Klein-`q`-Tabellenwerten in `ca-tools @ ff6cf96` (`33`, `384`, `165`, `1006`, `5000`). In Pilot 1 (`q = 5, t = 4, tspec`) blieb `m = 200` (`N = 1000 < 1006`) im 60-s-Budget ungelöst (`best_unc = 25`), ebenso `m = 210` (`best_unc = 15`).
3. **Bedeutung für `q >= 7` (Vorhersage aus `table/ca_frame.csv @ ff6cf96`, nicht gerechnet):**
   Ab `q = 7` liegt die `ca-tools`-Tabelle bei `k = q + 3` (`t = 4, 5`) exakt auf der elliptischen Schranke `2 q^3 - q^2`:
   - `q = 7, k = 10`: `m_ell = 637` (`t = 4: 4459`, `t = 5: 31213`) → jedes `m <= 636` schlägt die Tabelle.
   - `q = 8, k = 11`: `m_ell = 960` (`t = 4: 7680`, `t = 5: 61440`) → jedes `m <= 959` schlägt die Tabelle.
   - `q = 9, k = 12`: `m_ell = 1377` (`t = 4: 12393`, `t = 5: 111537`) → jedes `m <= 1376` schlägt die Tabelle.
   - `q = 11, k = 14`: `t = 5: 307461` (`m_ell = 2541`, `m <= 2540` schlägt Tabelle; `t = 4`: Tabelle `27544`, bräuchte `m <= 2503`).
   - `q = 13, k = 16`: `m_ell = 4225` (`t = 4: 54925`, `t = 5: 714025`) → jedes `m <= 4224` schlägt die Tabelle.
   *(Hinweis: Bei `q >= 7` steigt `|R_3|` kubisch (`637..4225`), daher ist für `q >= 7` eine konstruktive oder symmetriereduzierte Bauart bzw. ein angepasster Solver nötig; ungetestet.)*
