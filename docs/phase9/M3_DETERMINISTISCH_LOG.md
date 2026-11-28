# Phase 9: Deterministische Light+Heavy-3D-Bauart (`M_3(R_3)`), `q = 7, t = 6` & Pilot `q = 8, 9`

Datum: 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, Basis `main @ 0bcbe2b`).
Werkzeuge: [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py) (`std`-only + `GeneralGF`), [`scripts/phase9_m3_lift.py`](../../scripts/phase9_m3_lift.py), [`scripts/phase9_m3_search.c`](../../scripts/phase9_m3_search.c) (`MAX_M = 1536`, `--self-test` `6/6 PASS`).
Tabellenabgleich nur lesend gegen `chrispbsmolen/ca-tools @ ff6cf963fca4f347177d0617390312c3913c48b6`. Keine Ablage in `results/`, keine Außenwirkung, kein GitHub-Actions-Lauf, kein Merge nach `main`.

## 1. Teil 1 (Option A): Dual-Verifikation `CA(212660; 6, 10, 7)` in `/tmp/phase9_m3/`

- Eingabeliste: `data/phase9_m3/R3_q7_fullbg3_m620.txt` (`sha256: afc517b7e110128d5f280f5a5d64af45d5ebf664d32f9d12a5574732cd760f26`), `--check-m3 --mode full-bg3`: `0` Lücken (`Typ0=Typ1=Typ2=Typ3=0`).
- Lift (`--t 6`, `1,546 s`): `/tmp/phase9_m3/CA_212660_6_10_7.txt`
  - Größe: **`4.253.200 B`** (**`4,0562 MiB`**)
  - SHA-256: **`5bf30f0c949ff4d528d3560a45520930f9dfb11632c7221c2425e43c492a1539`**
- Dual-Verifikation & Negativkontrolle:
  - POS `verifiers/ca_verify`: `rc = 0` (`4,247 s`, alle `210` Spaltenmengen decken `117.649` 6-Tupel).
  - POS `verifiers/verify_independent.py`: `rc = 0` (`23,789 s`, `24.706.290` Interaktionen).
  - NEG (Zeile `212659` entfernt, `N = 212659`): `verifiers/ca_verify` `rc = 1` (`3,478 s`, `67/210` Spaltenmengen mit Lücken), `verifiers/verify_independent.py` `rc = 1` (`23,261 s`).
- Tabellenvergleich (`ca-tools @ ff6cf96`): `212.660` vs. `218.491` (`k' = 13`) → **`-5.831`** kleiner als die Tabelle am Commit `ff6cf96`.

## 2. Teil 2 (Option C): Deterministische Light+Heavy-Bauvorschrift (`scripts/phase9_m3_construct.py`)

Rein deterministische Konstruktion ohne Zufall, ohne Metaheuristik und ohne Suche für jede Primzahlpotenz `q >= 5` (`full-bg3`, hebt auf alle `3 <= t <= q`):

1. **Symbole & Ebenen:** Balancierte Zerlegung `|A_L| = ka = (q + 1)//3`, `|B_L| = kb = q//3`, `|C_L| = kc = (q - 1)//3` (`ka + kb + kc = q - 1`), `A_L = {0..ka-1}`, `B_L = {0..kb-1}`, `C_L = {(c_shift + i) mod q : i < kc}`, Rest `A_H, B_H, C_H`. Den `q - 1` leichten horizontalen Ebenen `z = 0..q-2` wird je ein Symbol aus `A_L, B_L, C_L` fest zugeordnet; `z* = q - 1` ist die schwere Ebene.
2. **Zyklisches Differenzband `3P` + komplementäre `1P`-Pfeiler:**
   - Wähle Bandbreite `r in [1, q - 1]` (nahe `0,8 q`), die `m_raw(q, r) = (3 q^2 - 2 r q) q + q * AP3(q, r)` minimiert, wobei `AP3(q, r) = #{(d, s) in [0, r)^2 : s != d, (2d - s) mod q < r}` (Inklusion-Exklusion: ein zusammenhängendes Intervall minimiert 3-APs im Band `D` durch Maximierung im Komplement `E = Z_q \ D`).
   - **Typ `3P` (`r * q` `x`-Geraden, partielle lateinische Quadrate):** `T = {(a, b, (-a - b) mod q) : (a - b) mod q < r}`.
   - **Typ `1P` (`3 (q - r) q` `x`-Geraden):** alle komplementären Paare `1P_ab(a, b)` für `(a, b) not in proj_ab(T)`, `1P_ac(a, c)` für `(a, c) not in proj_ac(T)` und `1P_bc(b, c)` für `(b, c) not in proj_bc(T)`.
   - **Rest-Tripel `U` (`q * AP3(q, r)` Punkte):** alle `(a, b, c) not in T`, deren drei Paarprojektionen in `T` liegen.
3. **Deterministische Zuweisung auf `Z_a, Z_b, Z_c` und `z*`:**
   - Maximales bipartites Matching ordnet die `q` `x`-Geraden-Slots jeder leichten Ebene `z in 0..q-2` kompatiblen `3P`/`1P`-Geraden zu (hoher Light-Grad und `3P` zuerst); nicht gematchte Light-Slots werden mit je `q` passenden Tripeln aus `U` gefüllt.
   - Auf `z* = q - 1` werden restliche `3P`-Geraden auf Zeilen `y` mit maximalem neuem Heavy-Gewinn gelegt, restliche `1P`-Geraden erhalten je Zeile `y` eine maximale `x`-Bijektion (bipartites Matching auf fehlende Heavy-Symbole), danach werden die restlichen `U`-Punkte auf defizitäre `(x, y)`-Zellen verteilt (inkl. deterministischem 1-Punkt-Relokationspass) und verbleibende Heavy-Defizite (`exh`) punktuell aufgefüllt.
4. **Asymptotik:** `m_raw(q) <= 1,90 q^3 - O(q^2) < 2 q^3 - q^2` für alle `q >= 5`; mit `exh`-Auffüllung unterbietet `m_det(q)` die elliptische Schranke `2 q^3 - q^2` ab `q = 7` durchgängig.

### Ergebnistabelle (`python3 scripts/phase9_m3_construct.py --sweep --save-dir data/phase9_m3`)

| `q` | `r` | `m_det` | `m_det / q^3` | `ell = 2q^3 - q^2` | Gewinn (`ell - m_det`) | `N_det (t = 4)` | `suff` | `--check-m3 (full-bg3)` | `exh` | Laufzeit | Ablage `data/phase9_m3/` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `5` | `4` | `227` | `1,8160` | `225` | `-2` | `1.135` | `0` | `0 (OK)` | `12` | `0,02 s` | nicht gespeichert (`> ell`) |
| `7` | `6` | **`631`** | `1,8397` | `637` | **`+6`** | `4.417` | `0` | `0 (OK)` | `22` | `0,05 s` | `R3_q7_fullbg3_det_m631.txt` (`e1e29c3d…`) |
| `8` | `7` | **`945`** | `1,8457` | `960` | **`+15`** | `7.560` | `0` | `0 (OK)` | `15` | `0,15 s` | `R3_q8_fullbg3_det_m945.txt` (`26b0406b…`) |
| `9` | `8` | **`1.332`** | `1,8272` | `1.377` | **`+45`** | `11.988` | `0` | `0 (OK)` | `9` | `0,24 s` | `R3_q9_fullbg3_det_m1332.txt` (`21d593a1…`) |
| `11` | `10` | **`2.454`** | `1,8437` | `2.541` | **`+87`** | `26.994` | `0` | `0 (OK)` | `1` | `0,53 s` | `R3_q11_fullbg3_det_m2454.txt` (`f95ed1c3…`) |
| `13` | `11` | **`4.088`** | `1,8607` | `4.225` | **`+137`** | `53.144` | `0` | `0 (OK)` | `45` | `1,22 s` | `R3_q13_fullbg3_det_m4088.txt` (`fc2ecb6c…`) |
| `16` | `14` | **`7.653`** | `1,8684` | `7.936` | **`+283`** | `122.448` | `0` | hinr. `0` | `37` | `0,69 s` | nicht gespeichert (Sweep) |
| `19` | `16` | **`12.928`** | `1,8848` | `13.357` | **`+429`** | `245.632` | `0` | hinr. `0` | `179` | `1,73 s` | nicht gespeichert (Sweep) |
| `23` | `19` | **`22.978`** | `1,8886` | `23.805` | **`+827`** | `528.494` | `0` | hinr. `0` | `277` | `4,34 s` | nicht gespeichert (Sweep) |
| `25` | `21` | **`29.618`** | `1,8956` | `30.625` | **`+1.007`** | `740.450` | `0` | hinr. `0` | `393` | `6,60 s` | nicht gespeichert (Sweep) |

## 3. Teil 3 (Option B): Kurzpilot `q = 8` & `q = 9` im C-Solver (`<= 90 s` je `q`)

Warmstart aus den deterministischen Listen (`R3_q8_fullbg3_det_m945.txt`, `R3_q9_fullbg3_det_m1332.txt`) mit Min-Unique-Deletion und fokussiertem Tabu+PAWS (2 Threads, Intel Xeon @ 2.30 GHz):

| Lauf | Ziel `(q, full-bg3, m)` | Start & Parameter | Dauer / Limit | Durchsatz (`mv/s`, `ev/s`) | Ergebnis |
| --- | --- | --- | :---: | :---: | --- |
| `P9-Q8-930` | `q = 8, m = 930` (`-15` vs. `m_det`) | `det_m945`, `w03=3, ten=12, sm=120, seed=9830` | **`0,130 s`** / `45 s` | `17.236` / `770.512` | **`SOLVED`** (`init_unc=15`, `2.233` steps, `R3_q8_fullbg3_m930.txt`, `43c78585…`) |
| `P9-Q8-915` | `q = 8, m = 915` (`-30` vs. `m_det`) | `m930`, `w03=3, ten=12, sm=120, seed=9815` | `45,162 s` / `45 s` | `14.693` / `880.436` | `TIMEOUT (best_unc=15)`, `by_type=(0,0,0,15)` |
| `P9-Q9-1320` | `q = 9, m = 1320` (`-12` vs. `m_det`) | `det_m1332`, `w03=4, ten=12, sm=120, seed=9920` | `45,346 s` / `45 s` | `9.846` / `673.864` | `TIMEOUT (best_unc=4)`, `by_type=(0,0,0,4)` |
| `P9-Q9-1324` | `q = 9, m = 1324` (`-8` vs. `m_det`) | `det_m1332`, `w03=4, ten=12, sm=120, seed=9924` | **`0,090 s`** / `44,6 s` | `4.310` / `215.750` | **`SOLVED`** (`init_unc=8`, `388` steps, `R3_q9_fullbg3_m1324.txt`, `51a0a410…`) |

### Dual-Verifikation (`q = 8` & `q = 9`, `/tmp/phase9_m3/`, `3/3 PASS`)

| Array (`/tmp/phase9_m3/`) | Größe | SHA-256 | `ca_verify` POS / NEG | `py_verify` POS / NEG | `ca-tools @ ff6cf96` (`Delta`) |
| --- | :---: | --- | :---: | :---: | :---: |
| **`CA(7440; 4, 11, 8)`** | `0,1561 MiB` | `e1c5733ae7f1ee7602806b1233bba888cf57471ea847671785a89902440f26da` | `0 (11 ms)` / `1 (10 ms)` | `0 (658 ms)` / `1 (652 ms)` | `7.680` (**`-240`**; lokal `results/t4_nearbush/CA_7056` kleiner) |
| **`CA(59520; 5, 11, 8)`** | `1,2488 MiB` | `309fff17a71e33d0949c08a1694dcf8712cb4b300af9f5578797a7f9fbce055d` | `0 (255 ms)` / `1 (261 ms)` | `0 (10,246 s)` / `1 (10,211 s)` | `61.440` (**`-1.920`**) |
| **`CA(11916; 4, 12, 9)`** | `0,2727 MiB` | `39986a2e9dc3e49cf36689200d8d8c1e489103f75efd23679c2ab5d9420dcffc` | `0 (20 ms)` / `1 (21 ms)` | `0 (1,638 s)` / `1 (1,639 s)` | `12.393` (**`-477`**) |

## 4. Tabellenabgleich der Familie (`q = 7..25`, `t = 4..6`, `ca-tools @ ff6cf96`)

| `q` | `k` | Bestes `m` (`det` / `solver`) | `t = 4` vs. Tabelle | `t = 5` vs. Tabelle | `t = 6` vs. Tabelle | Status |
| :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `7` | `10` | `631` / **`620`** | **`4.340` < `4.459`** (`-119`) | **`30.380` < `31.213`** (`-833`) | **`212.660` < `218.491`** (`-5.831`) | `t=4,5,6` dual-verifiziert in `/tmp` |
| `8` | `11` | `945` / **`930`** | **`7.440` < `7.680`** (`-240`) | **`59.520` < `61.440`** (`-1.920`) | `476.160` < `491.520` (`-15.360`) | `t=4,5` dual-verifiziert; `t=6` Vorhersage |
| `9` | `12` | `1.332` / **`1.324`** | **`11.916` < `12.393`** (`-477`) | `107.244` < `111.537` (`-4.293`) | `965.196` < `1.003.833` (`-38.637`) | `t=4` dual-verifiziert; `t=5,6` Vorhersage |
| `11` | `14` | **`2.454`** (`det`) | `26.994` < `27.544` (`-550`) | `296.934` < `307.461` (`-10.527`) | `3.266.274` < `3.528.481` (`-262.207`) | Liste `check_m3=0`; `t=4..6` Vorhersage |
| `13` | `16` | **`4.088`** (`det`) | `53.144` < `54.925` (`-1.781`) | `690.872` < `714.025` (`-23.153`) | `8.981.336` < `9.651.421` (`-670.085`) | Liste `check_m3=0`; `t=4..6` Vorhersage |
| `16` | `19` | **`7.653`** (`det`) | `122.448` > `113.866` (`+8.582`) | `1.959.168` < `2.031.616` (`-72.448`) | `31.346.688` < `33.554.416` (`-2.207.728`) | `suff=0`; `t=5,6` Vorhersage |
| `19` | `22` | **`12.928`** (`det`) | `245.632` < `253.783` (`-8.151`) | `4.667.008` < `4.945.339` (`-278.331`) | `88.673.152` < `94.091.743` (`-5.418.591`) | `suff=0`; `t=4..6` Vorhersage |
| `23` | `26` | `22.978` (`det`) | `528.494` > `390.621` | `12.155.362` > `9.765.621` | `279.573.326` > `244.140.621` | `< 2q^3-q^2`, über Tabelle (`OA`-Fusion) |
| `25` | `28` | `29.618` (`det`) | `740.450` > `531.437` | `18.511.250` > `14.348.903` | `462.781.250` > `387.420.485` | `< 2q^3-q^2`, über Tabelle (`OA`-Fusion) |

Insgesamt liegen **20 Zellen** (`t = 4..6`, `q = 7, 8, 9, 11, 13, 16, 19`) unter `ca-tools @ ff6cf96` (`6` davon dual-verifiziert in `/tmp/phase9_m3/`, `14` Vorhersage). Keine Außenwirkung; Drittprüfung & Literaturprüfung stehen aus.

## 5. Nachtrag AP 1 (Option A): Dual-Verifikation `q = 11` & `q = 13` (`t = 4`), Bonus `check_m3=0` (`q = 16, 17`) & Abgleich `ca-tools @ b689967`

Datum: 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, Basis `0d6e9f5`, PR `#54`; Detailprotokoll in [`M3_Q11_Q13_DUAL_VERIFY_LOG.md`](M3_Q11_Q13_DUAL_VERIFY_LOG.md)). Verifier unverändert (`sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23 PASS`). Alle ausgerollten Arrays liegen ausschließlich unter `/tmp/phase9_m3/` (nicht committet).

### 5.1 Dual-Verifikation `q = 11` & `q = 13` (`t = 4`, 2× byte-identisch, POS & NEG)

| `q` | `k` | `m` | Seed (`data/phase9_m3/`, 2× byte-gleich) | Ausgerolltes Array (`/tmp/phase9_m3/`, 2× byte-gleich) | Größe | `ca_verify` POS / NEG | `verify_independent.py` POS / NEG | `ca-tools @ b689967` (`Delta`) | Belegart |
| :---: | :---: | :---: | --- | --- | :---: | :---: | :---: | :---: | --- |
| `11` | `14` | `2.454` | `R3_q11_fullbg3_det_m2454.txt` (`f95ed1c305f6cb399f7697c2adedb7e6a2a864e9e7022ef3630240606f956ab5`, `0,647 s`) | `CA(26994; 4, 14, 11)` (`ee039374c0112e3febba1ec98367cc6307642da8f7e45a8fd133734489866767`, Lift `0,267 s` / Repro `0,341 s`) | `790.185 B` (`0,7536 MiB`) | `rc=0 (0,086 s)` / `rc=1 (0,101 s)` | `rc=0 (7,263 s)` / `rc=1 (7,359 s, 81/1001 Lücken)` | `27.544 (k=14)` (**`-550`**) | **`Dual-Verify PASS`** (`Regel-2d offen`) |
| `13` | `16` | `4.088` | `R3_q13_fullbg3_det_m4088.txt` (`fc2ecb6cbab5699670212d37c0ef968c75697dbf4a558f6c31d8867c091b113b`, `1,369 s`) | `CA(53144; 4, 16, 13)` (`548f15db41f34486fc28bea1258691f33ddb717dfeb80d3352935086195acd07`, Lift `0,727 s` / Repro `0,578 s`) | `1.896.856 B` (`1,8090 MiB`) | `rc=0 (0,410 s)` / `rc=1 (0,334 s)` | `rc=0 (38,869 s)` / `rc=1 (35,691 s, 246/1820 Lücken)` | `54.925 (k=21)` (**`-1.781`**) | **`Dual-Verify PASS`** (`Regel-2d offen`) |

*(Negativkontrolle jeweils durch Entfernen der letzten Zeile `N -> N - 1`; beide Verifier liefern `rc = 1`.)*

### 5.2 Bonus `check_m3=0` (`q = 16` und `q = 17`, ohne CA-Rollout)
Da `q = 11` (`~16 s`) und `q = 13` (`~78 s`) deutlich unter `2 min` liefen, wurde zusätzlich `check_m3(full-bg3)` für `q = 16` und `q = 17` exakt geprüft:
- `q = 16`: `r = 14, csh = 10, m = 7.653` (`1,8684 q^3`, `exh = 37`), `suff = 0`, **`check_m3(full-bg3) = 0`** (`construct 0,68 s`, `check_m3 1,78 s`).
- `q = 17`: `r = 15, csh = 11, m = 9.182` (`1,8689 q^3`, `exh = 19`), `suff = 0`, **`check_m3(full-bg3) = 0`** (`construct 0,90 s`, `check_m3 2,35 s`).

### 5.3 Read-only `ca-tools @ b689967`-Abgleich (`q = 7, 8, 9, 11, 13` [+ `16, 17, 19`], `t = 4, 5, 6`)
Abgleich ausschließlich lesend gegen `chrispbsmolen/ca-tools @ b68996787557cb79153f2d0ca9640aa821c57e52` (`2026-11-28T02:10:53Z`; `table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv`, `0` offene PRs, monotone Schranke über alle Zeilen mit `t' >= t, v' >= v, k' >= k`):

| `q` | `k` | `m_det` (`m_solver`) | `t = 4`: `N_det` (`N_solv`) vs. `b689967` (`Delta_det`) | `t = 5`: `N_det` (`N_solv`) vs. `b689967` (`Delta_det`) | `t = 6`: `N_det` (`N_solv`) vs. `b689967` (`Delta_det`) | Belegart je Stärke (`t=4 / t=5 / t=6`) |
| :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `7` | `10` | `631` (`620`) | `4.417` (`4.340`) < `4.459` (`-42` / `-119`) | `30.919` (`30.380`) < `31.213` (`-294` / `-833`) | `216.433` (`212.660`) < `218.491` (`-2.058` / `-5.831`) | `det`: `check_m3=0` / `check_m3=0` / `check_m3=0` (`solv m=620`: `Dual-Verify PASS` `t=4,5,6`) |
| `8` | `11` | `945` (`930`) | `7.560` (`7.440`) < `7.680` (`-120` / `-240`; lokal `CA_7056`) | `60.480` (`59.520`) < `61.440` (`-960` / `-1.920`) | `483.840` (`476.160`) < `491.520` (`-7.680` / `-15.360`) | `det`: `check_m3=0` (`solv m=930`: `Dual-Verify PASS` `t=4,5`, `check_m3=0` `t=6`) |
| `9` | `12` | `1.332` (`1.324`) | `11.988` (`11.916`) < `12.393` (`-405` / `-477`) | `107.892` (`107.244`) < `111.537` (`-3.645` / `-4.293`) | `971.028` (`965.196`) < `1.003.833` (`-32.805` / `-38.637`) | `det`: `check_m3=0` (`solv m=1324`: `Dual-Verify PASS` `t=4`, `check_m3=0` `t=5,6`) |
| `11` | `14` | **`2.454`** | **`26.994` < `27.544`** (**`-550`**) | `296.934` < `307.461` (`-10.527`) | `3.266.274` < `3.528.481` (`-262.207`) | **`Dual-Verify PASS` (`t=4`)** / `check_m3=0` (`t=5,6`) |
| `13` | `16` | **`4.088`** | **`53.144` < `54.925`** (**`-1.781`**) | `690.872` < `714.025` (`-23.153`) | `8.981.336` < `9.651.421` (`-670.085`) | **`Dual-Verify PASS` (`t=4`)** / `check_m3=0` (`t=5,6`) |
| `16` | `19` | `7.653` | `122.448` > `113.866` (`+8.582`) | `1.959.168` < `2.031.616` (`-72.448`) | `31.346.688` < `33.554.416` (`-2.207.728`) | `check_m3=0` (`t=4..6`; `t=5,6` kleiner, Vorhersage) |
| `17` | `20` | `9.182` | `156.094` > `130.317` (`+25.777`) | `2.653.598` > `2.476.095` (`+177.503`) | `45.111.166` < `47.045.877` (`-1.934.711`) | `check_m3=0` (`t=4..6`; `t=6` kleiner, Vorhersage) |
| `19` | `22` | `12.928` | `245.632` < `253.783` (`-8.151`) | `4.667.008` < `4.945.339` (`-278.331`) | `88.673.152` < `94.091.743` (`-5.418.591`) | `suff=0` (`t=4..6`; Vorhersage) |

Alle `15/15` Zielzellen für `q in {7, 8, 9, 11, 13}, t in {4, 5, 6}` (plus `6` weitere Zellen bei `q = 16, 17, 19`, insgesamt **`21` Zellen**) liegen strikt unter `ca-tools @ b689967` (`8` davon in `/tmp/phase9_m3/` vollständig dual-verifiziert: `q=7 t=4,5,6`, `q=8 t=4,5`, `q=9 t=4`, `q=11 t=4`, `q=13 t=4`; `Regel-2d offen`, keine Ablage in `results/`, keine Außenwirkung).

