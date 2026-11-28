# Phase 9: Strukturanalyse `M_3(R_3)` & Kurzpilot `q = 7` (`exp/phase9-biaffine-3d`)

Datum: 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, Basis `main @ 0bcbe2b`).
Analyse-Skript: [`scripts/phase9_m3_analyze.py`](../../scripts/phase9_m3_analyze.py) (`std`-only + `FieldOps`).
C-Solver: [`scripts/phase9_m3_search.c`](../../scripts/phase9_m3_search.c) (erweitert um `--init heavy`, Min-Unique-Deletion bei `--init-file`, `cands[2048]`, `q = 7` im `--self-test` `6/6 PASS`).
Tabellenabgleich nur lesend gegen `chrispbsmolen/ca-tools @ ff6cf963fca4f347177d0617390312c3913c48b6` (keine Außenwirkung, kein Merge nach `main`, kein GitHub-Actions-Lauf).

## 1. Kernbefund der Strukturanalyse (Light-Layer + Heavy-Layer-Geometrie)

Beide ohne Vorstruktur aus `--init rand` gefundenen `full-bg3`-Lösungen (`R3_q3_fullbg3_m43.txt` und `R3_q5_fullbg3_m215.txt`) zeigen dieselbe 3D-Struktur:

1. **Konzentration des Überschusses auf genau eine schwere horizontale `z = c2`-Ebene (`z*`):**
   - `q = 3, m = 43`: `z`-Schichten `[9, 11, 23]` (`z* = 2` trägt `14` der `16` Zusatzvertreter; alle `9` Punkte auf `z = 2` haben `m >= 2`).
   - `q = 5, m = 215`: `z`-Schichten `[26, 26, 26, 112, 25]` (`z* = 3` trägt `87` der `90` Zusatzvertreter; alle `25` Punkte auf `z = 3` haben `m >= 4`; bei `m = 214`: `[25, 25, 26, 113, 25]`).
   - Dagegen sind die Profile entlang `y = c1` und `x = c0` nahezu flach (`q = 3`: `[13, 14, 16]`; `q = 5`: `[45, 41, 41, 45, 43]` bzw. `[46, 41, 42, 45, 41]`).
2. **Zyklische Aufteilung der `q - 1` leichten `z`-Ebenen auf `a, b, c` (`k_a + k_b + k_c = q - 1`):**
   - Bei `q = 5, m = 215` hat **jedes** der `15` Symbole (`h_a = 5, h_b = 5, h_c = 5`) genau eine volle horizontale `z`-Ebene:
     - `4` leichte Ebenen: `a = 0` (`z = 0`), `a = 2` (`z = 1`), `b = 3` (`z = 2`), `c = 4` (`z = 4`) (`k_a = 2, k_b = 1, k_c = 1`).
     - Alle übrigen `3 + 4 + 4 = 11` Symbole (`a in {1,3,4}`, `b in {0,1,2,4}`, `c in {0,1,2,3}`) teilen sich die schwere Ebene `z* = 3`.
   - Bei `q = 3, m = 43`: `h_a = 2, h_b = 3, h_c = 3` (beliebige Ebenen: `4, 4, 3`). Die `2` leichten Ebenen gehören `b = 1` (`z = 0`) und `c = 1` (`z = 1`); das einzige Symbol ohne horizontale `z`-Ebene (`a = 1`, `|U_1| = 16`, `z_pts = [6, 6, 4]`, `proj_(c1,c2) = 6/9`, `x_cyl = False`) enthält stattdessen zwei gekippte volle Ebenen `(0, 1, 1)` und `(0, 1, 2)` mit `5` vollen `x`-Geraden.
   - Skelett-Größe bei ausgewogener Partition `k_a + k_b + k_c = q - 1` (`L = q - floor((q-1)/3)`):
     `m_skel = (q - 1) * q^2 + L * q^2 ≈ (5/3) q^3 << 2 q^3 - q^2`.
3. **Paar-Fasern (`Typ 2`) fast vollständig über volle `x`-Geraden `{(x, y0, z0) : x in F_q}`:**
   - `q = 3, m = 43`: `27/27` (`9/9` je Spaltenpaar) enthalten mindestens eine volle `x`-Gerade.
   - `q = 5, m = 215`: `71/75` (`{a,b}: 24/25`, `{a,c}: 23/25`, `{b,c}: 24/25`) enthalten mindestens eine volle `x`-Gerade. Die `4` Nicht-`x`-Geraden-Paare haben Größen `11` (`z`-Schichten `2`), `10` (`1`), `12` (`2`), `11` (`2`) — keines enthält eine andere volle Gerade; sie wirken als ebene/2-schichtige 2D/3D-Hyperplan-Treffmengen (`|P| >= 2q`) überwiegend auf `z* = 3`.
4. **Kontrast zu `tspec t = 4` (`q = 4, m = 105`, nur `|D1| = 4, |N2| = 6`):**
   - Schwächer konzentriert (`z`-Schichten `[26, 42, 19, 18]`), kaum volle Ebenen (`h_a = 1, h_b = 1, h_c = 0`), alle Symbole ohne volle `z`-Ebene sind echt 3D (`x_cyl = False`, Verhältnis `|U_s| / |proj| = 1,62..2,78`), und nur `10/48` Paare (`2/16, 2/16, 6/16`) nutzen eine volle `x`-Gerade (`18/48` irgendeine volle Gerade, minimale Nicht-`x`-Geraden-Paargröße `4` über `y`-Geraden auf `1` Schicht).

## 2. Exakte Kennzahlen je Liste

### 2.1 `R3_q3_fullbg3_m43.txt` (`q = 3`, `full-bg3`, `m = 43`, `2q^3 - q^2 = 45`)
- **Multiplizitäten `(c0,c1,c2)`:** `27/27` Punkte (`m=1: 16`, `m=2: 7`, `m=3: 3`, `m>=4: 1`, max `4`). `(a,b,c)`: `27/27` (`m=1: 17`, `m=2: 4`, `m=3: 6`, max `3`).
- **Schichtzahlen:** `z=c2`: `[9, 11, 23]` (`z=0: 9/0/0/0`; `z=1: 7/2/0/0`; `z=2: 0/5/3/1`); `y=c1`: `[13, 14, 16]`; `x=c0`: `[13, 14, 16]`.
- **Einzel-Fasern `|U_s|` / `N_s`:**
  - `a`: `|U_s| = [12, 13, 16]` (`N_s = [13, 14, 16]`), `h_a = 2` (`a=0: z=2`, `a=2: z=2`; `a=1` ohne `z`-Ebene: `z_hit=3`, `z_pts=[6,6,4]`, `proj_(c1,c2)=6/9`, `x_cyl=False`, `full_x_lines=5/9`, `any_planes=2 [(0,1,1),(0,1,2)]`).
  - `b`: `|U_s| = [12, 13, 16]` (`N_s = [13, 14, 16]`), `h_b = 3` (`b=0: z=2`, `b=1: z=0`, `b=2: z=2`; `b=1` auch `(0,1,0)`).
  - `c`: `|U_s| = [13, 13, 14]` (`N_s = [14, 14, 15]`), `h_c = 3` (`c=0: z=2`, `c=1: z=1`, `c=2: z=2`).
- **Paar-Fasern `|P_(s1,s2)|`:**
  - `{a,b}`: min `3`, med `5,0`, max `7`, `hist={3:2, 4:2, 5:2, 6:2, 7:1}`, volle `x`-Geraden `9/9`.
  - `{a,c}`: min `4`, med `5,0`, max `6`, `hist={4:3, 5:5, 6:1}`, volle `x`-Geraden `9/9`.
  - `{b,c}`: min `4`, med `5,0`, max `6`, `hist={4:3, 5:5, 6:1}`, volle `x`-Geraden `9/9`.
- **Affine Korrelation (Zufall `14,3 = 0,333`):** `a`: max `24/43 (0,558)` bei `(0,1,2,1)` (`eq_c2=18/43`); `b`: max `23/43 (0,535)` bei `(0,2,0,0)`/`(0,0,2,1)` (`eq_c2=13/43`); `c`: max `22/43 (0,512)` bei `c=c2` (`(0,0,1,0)`).

### 2.2 `R3_q4_t4_tspec_m105.txt` (`q = 4`, `tspec t = 4`, `m = 105`, `2q^3 - q^2 = 112`)
- **Multiplizitäten `(c0,c1,c2)`:** `64/64` (`m=1: 37`, `m=2: 14`, `m=3: 12`, `m>=4: 1`, max `4`). `(a,b,c)`: `64/64` (`37/16/8/3`).
- **Schichtzahlen:** `z=c2`: `[26, 42, 19, 18]`; `y=c1`: `[26, 24, 27, 28]`; `x=c0`: `[25, 26, 27, 27]`.
- **Einzel-Fasern:** `a`: `|U_s|=[23,26,28,28]`, `h_a=1` (`a=1: z=1`); `b`: `|U_s|=[16,26,28,28]`, `h_b=1` (`b=3: z=3`); `c`: `|U_s|=[24,25,25,26]`, `h_c=0`. Nicht-`z`-Symbole: `z_hit=3..4`, `proj=9..16/16`, `x_cyl=False`, `full_x_lines=0..4/16`.
- **Paar-Fasern:** `{a,b}` min `4`/med `7,0`/max `9` (`2/16` `x`-Ger., `6/16` bel. Ger., Nicht-`x` min `4`, `z`-Sch. `{1:4,2:1,3:7,4:2}`); `{a,c}` min `5`/med `6,5`/max `8` (`2/16` `x`-Ger., `5/16` bel. Ger., Nicht-`x` min `5`, `z`-Sch. `{2:2,3:10,4:2}`); `{b,c}` min `4`/med `7,0`/max `9` (`6/16` `x`-Ger., `7/16` bel. Ger., Nicht-`x` min `6`, `z`-Sch. `{1:2,2:3,3:4,4:1}`).
- **Affine Korrelation (Zufall `26,2 = 0,250`):** `a` max `42/105 (0,400)`; `b` max `51/105 (0,486)` bei `(0,0,3,1)`; `c` max `54/105 (0,514)` bei `(0,0,2,2)`.

### 2.3 `R3_q5_fullbg3_m215.txt` (`q = 5`, `full-bg3`, `m = 215`, `2q^3 - q^2 = 225`)
- **Multiplizitäten `(c0,c1,c2)`:** `125/125` (`m=1: 97`, `m=2: 3`, `m=3: 0`, `m>=4: 25`, max `8`). `(a,b,c)`: `125/125` (`93/10/1/21`, max `5`).
- **Schichtzahlen:** `z=c2`: `[26, 26, 26, 112, 25]` (`z=0,1,2: 24/1/0/0`; `z=3: 0/0/0/25`; `z=4: 25/0/0/0`); `y=c1`: `[45, 41, 41, 45, 43]`; `x=c0`: `[46, 41, 42, 45, 41]`.
- **Einzel-Fasern `|U_s|` / `N_s`:**
  - `a`: `|U_s| = [35, 37, 41, 41, 43]` (`N_s = [42, 42, 42, 43, 46]`), `h_a = 5` (`a=0: z=0`, `a=2: z=1`, `a=1,3,4: z=3`; `full_x_lines = 6..7/25`).
  - `b`: `|U_s| = [40, 40, 41, 42, 42]` (`N_s = [42, 42, 43, 44, 44]`), `h_b = 5` (`b=3: z=2`, `b=0,1,2,4: z=3`; `full_x_lines = 7/25`).
  - `c`: `|U_s| = [38, 39, 43, 43, 43]` (`N_s = [42, 43, 43, 43, 44]`), `h_c = 5` (`c=4: z=4`, `c=0,1,2,3: z=3`; `full_x_lines = 6..8/25`).
- **Paar-Fasern `|P_(s1,s2)|`:**
  - `{a,b}`: min `5`, med `9,0`, max `11`, `hist={5:1, 6:2, 8:7, 9:11, 10:3, 11:1}`, volle `x`-Geraden `24/25`, Nicht-`x` (`1/25`): `(3,1)`, Größe `11`, `z`-Schichten `2`, keine andere volle Gerade.
  - `{a,c}`: min `5`, med `9,0`, max `12`, `hist={5:2, 6:2, 7:1, 8:3, 9:11, 10:5, 12:1}`, volle `x`-Geraden `23/25`, Nicht-`x` (`2/25`): min Größe `10` (`(1,3)`, `z`-Schichten `1`, rein auf `z = 3`), max `12` (`z`-Schichten `2`).
  - `{b,c}`: min `5`, med `9,0`, max `11`, `hist={5:2, 6:2, 7:2, 8:3, 9:10, 10:3, 11:3}`, volle `x`-Geraden `24/25`, Nicht-`x` (`1/25`): `(2,1)`, Größe `11`, `z`-Schichten `2`, keine andere volle Gerade.
- **Affine Korrelation (Zufall `43,0 = 0,200`):** `a` max `94/215 (0,437)` bei `(0,0,2,0)`; `b` max `74/215 (0,344)` bei `(0,0,3,2)`; `c` max `75/215 (0,349)` bei `(0,0,4,3)` (alle reinen `c2`-Funktionen, da `z = 3` schwer besetzt ist).

### 2.4 Nachbesserung Teil 1.4 (`q = 3` & `q = 5`, `full-bg3`)
- `q = 3`, Warmstart (Min-Unique-Deletion ab `R3_q3_fullbg3_m43.txt`, je `15 s`, PAWS `w03=4, ten=8, sm=80`):
  - `m = 42` (`init_unc = 4`): `TIMEOUT (best_unc=2)`, `by_type=(0,0,0,2)` (`15,012 s`, `296k mv/s`).
  - `m = 41` (`init_unc = 10`): `TIMEOUT (best_unc=4)`, `by_type=(0,0,0,4)` (`15,004 s`, `292k mv/s`).
- `q = 5`, Step-down ab `R3_q5_fullbg3_m215.txt` (`58,1 s <= 60 s` gesamt):
  - `m = 214` (`init_unc = 1`, `(0,0,0,1)`): mit `w03=3` (`18,0 s`) `TIMEOUT (best_unc=1)`; mit `w03=8, ten=10, sm=100` (`seed=9914`) **`SOLVED` in `0,003 s` (`86` Schritte)** → `data/phase9_m3/R3_q5_fullbg3_m214.txt` (`z`-Schichten `[25, 25, 26, 113, 25]`, hebt auf `CA(214; 3, 8, 5)`, `CA(1070; 4, 8, 5)`, `CA(5350; 5, 8, 5)`).
  - `m = 213` ab `m = 214` (`init_unc = 1`, `(0,0,0,1)`): `TIMEOUT (best_unc=1)` (`40,056 s`, `66k mv/s`).

## 3. Kurzpilot Option A (`q = 7, k = 10, full-bg3`, Budget `<= 120 s`)

Die aus Teil 1 abgeleitete Light+Heavy-Initialisierung (`--init heavy`, `k_a = k_b = k_c = 2` leichte `z`-Ebenen `z = 0..5` + schwere Ebene `z = 6` mit `L = 5` Basis-Kopien + Zusatzvertretern) startet bei `q = 7, m = 636` mit `Typ0 = 0, Typ1 = 0, Typ3 = 0` und `Typ2 = 2055..2250` (aus `101.528` Interaktionen). Durchsatz: `23,1k–23,7k mv/s` (`1,20M–1,29M ev/s`, 2 Threads). Gesamtzeit Teil 2: `86,46 s <= 120 s`.

| Lauf | Ziel `(q=7, full-bg3)` | Start & Seed | Dauer / Limit | Durchsatz (`mv/s`, `ev/s`) | Ergebnis |
| --- | --- | --- | :---: | :---: | --- |
| `P9-Q7-dry` | `m = 636` | `--init heavy`, `seed=9700` | `1,035 s` / `1 s` | `23.749` / `1.294.835` | `TIMEOUT (best_unc=12)` (`init_unc=2090`) |
| `P9-Q7-636` | `m = 636` (`< 637`) | `--init heavy`, `seed=9701` | **`9,128 s`** / `60 s` | `23.565` / `1.278.286` | **`SOLVED` (`unc=0`, `rst=0`, `tid=0`)** |
| `P9-Q7-630` | `m = 630` (`-7`) | `--init heavy`, `seed=10330` | **`4,028 s`** / `25 s` | `23.532` / `1.264.218` | **`SOLVED` (`unc=0`, `rst=0`, `tid=1`)** |
| `P9-Q7-620` | `m = 620` (`-17`) | `--init heavy`, `seed=10320` | **`17,016 s`** / `25 s` | `23.244` / `1.221.578` | **`SOLVED` (`unc=0`, `rst=0`, `tid=0`)** |
| `P9-Q7-610` | `m = 610` (`-27`) | `--init heavy`, `seed=10310` | `25,129 s` / `25 s` | `23.227` / `1.199.059` | `TIMEOUT (best_unc=47)`, `by_type=(0,0,43,4)` |
| `P9-Q7-615` | `m = 615` (`-22`) | `--init heavy`, `seed=11015` | `30,091 s` / `30 s` | `23.141` / `1.205.270` | `TIMEOUT (best_unc=8)`, `by_type=(0,0,7,1)` |

Struktur von `R3_q7_fullbg3_m620.txt`: `z`-Schichten `[54, 57, 53, 57, 53, 50, 296]`, `h_a = h_b = h_c = 7`, `|U_s|`: `a:[79..87]`, `b:[78..87]`, `c:[77..87]`; volle `x`-Geraden in Paaren `{a,b}: 48/49`, `{a,c}: 45/49`, `{b,c}: 48/49` (`141/147`; Nicht-`x` min Größen `19, 13, 17`).

## 4. Dual-Verifikation & Tabellenvergleich (`8/8 PASS`)

Alle `4` neuen Listen liegen in `data/phase9_m3/` (`SHA256SUMS` `10/10 OK`, `--check-m3 --mode full-bg3` `0` Lücken); alle `8` gelifteten Arrays in `/tmp/phase9_m3/` bestehen `verifiers/ca_verify` (`rc = 0`), `verifiers/verify_independent.py` (`rc = 0`) sowie die Negativkontrolle (letzte Zeile entfernt → beide `rc = 1`):

| Liste (`data/phase9_m3/`) | SHA-256 (Liste) | Geliftetes Array (`/tmp/phase9_m3/`) | SHA-256 (Array) | `ca_verify` POS / NEG | `py_verify` POS / NEG | `ca-tools @ ff6cf96` (`Delta`) |
| --- | --- | --- | --- | :---: | :---: | :---: |
| `R3_q5_fullbg3_m214.txt` | `0c46844d…` | `CA(214; 3, 8, 5)` | `21a9f09bde8721a0a9fd3eedaaf598d8297dd3fb7a1008d647a8ff7057444496` | `0 (6 ms)` / `1 (4 ms)` | `0 (62 ms)` / `1 (63 ms)` | `165` (`+49`) |
| `R3_q5_fullbg3_m214.txt` | `0c46844d…` | `CA(1070; 4, 8, 5)` | `8dd80786d11a7aadb0e5755866edf98b0d1e08c795ca6c757d6eb3e04e1af71c` | `0 (4 ms)` / `1 (4 ms)` | `0 (80 ms)` / `1 (80 ms)` | `1006` (`+64`) |
| `R3_q5_fullbg3_m214.txt` | `0c46844d…` | `CA(5350; 5, 8, 5)` | `2915cb681ed15ecbc5474881375f347445fa62ec6f5a791a851b387aa07dda1e` | `0 (7 ms)` / `1 (7 ms)` | `0 (170 ms)` / `1 (177 ms)` | `5000` (`+350`) |
| `R3_q7_fullbg3_m636.txt` | `6c497964…` | `CA(4452; 4, 10, 7)` | `c6d0eb638a6a8dc1a07ac6d918833332046a555ce294ee2f1027fe2b01874083` | `0 (14 ms)` / `1 (17 ms)` | `0 (252 ms)` / `1 (255 ms)` | `4459` (**`-7`**) |
| `R3_q7_fullbg3_m630.txt` | `44162cf0…` | `CA(4410; 4, 10, 7)` | `575e0517fe40322ddc2aab0398983b3bd4208116763fc16da2939dded2884ada` | `0 (17 ms)` / `1 (18 ms)` | `0 (247 ms)` / `1 (248 ms)` | `4459` (**`-49`**) |
| `R3_q7_fullbg3_m620.txt` | `afc517b7…` | `CA(620; 3, 10, 7)` | `d399cd7418547d474ff7eda9855f3d308db2c06aeff4b7db4950d3fe953feec9` | `0 (3 ms)` / `1 (4 ms)` | `0 (76 ms)` / `1 (88 ms)` | `479` (`+141`) |
| `R3_q7_fullbg3_m620.txt` | `afc517b7…` | **`CA(4340; 4, 10, 7)`** | `cf31647b456b6dffa11a9bf8b422e2517f71769592918e2e5bc2379bda64ad72` | `0 (16 ms)` / `1 (15 ms)` | `0 (237 ms)` / `1 (254 ms)` | `4459` (**`-119`**) |
| `R3_q7_fullbg3_m620.txt` | `afc517b7…` | **`CA(30380; 5, 10, 7)`** | `9ebfd33211ec22cac73814cabc087612b1e01c4a6ad14a999740fe6ce761e6c7` | `0 (78 ms)` / `1 (80 ms)` | `0 (2,709 s)` / `1 (2,718 s)` | `31213` (**`-833`**) |

*(Vorhersage für `t = 6`, nicht geliftet/verifiziert: `CA(212660; 6, 10, 7)` vs. `ca-tools @ ff6cf96` = `218491`, `-5831`.)*
*(Hinweis: Arrays liegen in `/tmp/phase9_m3/`, nicht in `results/`; Drittprüfung, Literaturprüfung und Freigabe stehen aus — keine Außenwirkung.)*
