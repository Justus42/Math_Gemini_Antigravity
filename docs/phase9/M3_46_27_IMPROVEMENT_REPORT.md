# Phase 9 / PR #54 (Option C): Strukturelle Lücken-Diagnose (`19/10 -> 49/27 -> 47/27 -> 46/27`) und Konstruktive Verbesserung von `M_3(R_3)`

- **Datum:** 2026-11-28
- **Branch:** `exp/phase9-biaffine-3d` (Basis `00c3653`)
- **Zielmodell:** 3D-biaffines Modell `M_3(R_3)` im Modus `full-bg3` (`k = q + 3`, `3 <= t <= q`, `|D_1| = |N_2| = q^2`)
- **Governance:** `verifiers/`, `submission/`, `staging/`, `results/phase7*`, `data/phase8_baer/`, `results/phase8_baer/` strikt unverändert; alle ausgerollten CAs ausschließlich unter `/tmp/phase9_m3/`; `ca-tools@b689967` strikt read-only.
- **Belegstatus:** Streng getrennt nach `LP-Vorhersage` / `Argument` / `suff=0` / `check_m3=0` / `Dual-Verify PASS` / `Regel-2d offen`.

---

## 1. AP 1: Strukturelle Lücken-Diagnose (`19/10 -> 49/27 -> 47/27 -> 46/27`)

### 1.1 Was trennt `46/27` (`1.70370 q^3`) von `49/27` (`1.81481 q^3`)?

Im symmetrischen Light+Heavy-`x`-Geraden-LP (`l = 1/3`, `h = 2/3`; Variablen in Einheiten von `q^3`; optimistische Bonferroni-1.-Ordnung für Tripel-Abdeckung durch `1P`-Geraden ohne Mehrfachüberlappungs-Abzug) ergeben sich exakte rationale Optima (`fractions.Fraction`, Two-Phase-Simplex):

| LP-Variante | Nebenbedingung | Exaktes Optimum | Dezimalwert | Belegart |
|---|---|---:|---:|---|
| **`LP1` (frei, `3P+1P+0P`)** | Alle `3P`/`1P`/`0P`-Typen frei | **`46/27`** | `1.703704` | `LP-Vorhersage` |
| **`LP_49a`** | Verbot von `3P` in `LLL`/`LLH` (`L_3LLL = L_3LLH = H_3LLL = H_3LLH = 0`) | **`49/27`** | `1.814815` | `LP-Vorhersage` |
| **`LP_49b`** | Verbot gemischter `1P_LH`-Geraden (`L_1LH = H_1LH = 0`) | **`49/27`** | `1.814815` | `LP-Vorhersage` |
| **`LP_2P` (mit `H_2P_L_HH`)** | Zusätzlicher `2P`-Sharing-Block auf `z*` (`a_0 in A_L`, `B_H, C_H` zyklisch gekoppelt auf selber Zeile `y`) | **`1885/1107`** | `1.702800` | `LP-Vorhersage` |
| **`LP_2P_no3PLL`** | Wie `LP_49a` (kein `3P` in `LLL/LLH`), aber mit `H_2P_L_HH` auf `z*` | **`143/81`** | `1.765432` | `LP-Vorhersage` |

**Primal-optimale Gewichte der `46/27`-LP (`LP1`):**
- **Light-Ebenen (`Summe = 1 = 27/27`):** `L_3LLH = 7/27`, `L_3LHH = 11/81`, `L_1LL = 2/27`, `L_1LH = 14/27`, `L_0LLL = 1/81`.
- **Heavy-Ebene `z*` (`Summe = 19/27`, Heavy-Abdeckung `= 2 = 54/27`):** `H_3LHH = 1/81`, `H_3HHH = 8/27`, `H_1HH = 8/27`, `H_0HHH = 8/81`.

**Primal-optimale Gewichte der `49/27`-LP (`LP_49a`, kein `3P` in `LLL`/`LLH`):**
- **Light-Ebenen (`Summe = 27/27`):** `L_3LHH = 10/27`, `L_1LL = 1/3` (`9/27`), `L_0LHH = 8/27`.
- **Heavy-Ebene `z*` (`Summe = 22/27`):** `H_3LHH = 8/27`, `H_3HHH = 2/27`, `H_1HH = 4/9` (`12/27`).

**Strukturelle Diagnose (zwei getrennte Barrieren):**
1. **Lineare Nebenbedingungs-Lücke (`46/27 -> 49/27`):** Sowohl das Verbot von `3P`-Geraden in `LLL`/`LLH` (`LP_49a`, vgl. `M3_DETERMINISTIC_CONSTRUCTION_PROOF.md` §4.1) als auch das Verbot gemischter `1P_LH`-Geraden (`LP_49b`) heben das LP-Optimum exakt um `+3/27 = +1/9` von `46/27` auf `49/27`.
2. **Realisierbarkeits-Lücke (Bonferroni-Überzählung & Ruzsa–Szemerédi-Obstruktion):** Selbst `LP_49a` unterstellt, dass `H_1HH = 12/27` die `HHH`-Tripel (`8/27`) *ohne Mehrfachüberdeckung* überdeckt. Für drei reale komplementäre `1P`-Zylinder `E_ab^c x F_q`, `E_ac^c x F_q`, `E_bc^c x F_q` mit Dichte `s` pro Paar-Typ gilt jedoch die exakte Inklusion-Exklusion:
   $$m_{\mathrm{raw}}(T) / q^3 = 3 - 2(1-s) + |U(T)|/q^3 = 2 - s + I_2 - I_3,$$
   wobei `I_2` die paarweisen Zylinder-Überlappungen und `I_3` die 3-fach-Überlappungen sind. Eine vollständige Disjunktivität (`I_2 = I_3 = 0`) bei `s = 1/4` würde `7/4 = 1.75` liefern, ist aber mit einer realen partiellen lateinischen Struktur `T` unvereinbar (Ruzsa–Szemerédi / Dreieckspackungs-Obstruktion).
3. **Ausweg über Punkt-Sharing (`3P`-Splitting & `2P`-Sharing):** Beide LP-Modelle (`46/27` und `49/27`) nehmen implizit an, dass `3P`- und `1P`-Geraden *punktfremd* platziert werden. Zwei konstruktive Mechanismen brechen diese Annahme direkt auf:
   - **`3P`-Splitting (erhält 100% `suff=0`!):** Ersetzt in einer Spalte `x` einer `3P(a_0, b_0, c_0)`-Geraden (bei mindestens 1 ungespaltener Spalte `x'`) den einzelnen Punkt durch drei `U`-Tripel `(a_0, b_0, c_x), (a_0, b_x, c_0), (a_x, b_0, c_0)` auf derselben Zeile `(y, z)`. Alle drei Paar-`x`-Geraden und alle Light-Ebenen-Owner bleiben 100% erhalten, und es wird exakt `1` Punkt pro Split eingespart. Auf `z*` beträgt der Verlust an distinkter Heavy-Abdeckung `2 * (1_{a_0 in A_H} + 1_{b_0 in B_H} + 1_{c_0 in C_H})` (für `3P_LLL` exakt `0`).
   - **`H_2P_L_HH`-Sharing auf `z*`:** Koppelt für fixes `a_0 in A_L` alle `b_u in B_H` und `c_{(u+x) mod h} in C_H` auf derselben Zeile `(y, z*)`. Da `a_0` leicht ist, entsteht kein Multiplizitätsverlust bei Heavy-Symbolen (`2` distinkte Heavy-Inzidenzen pro Punkt, `2` `LH`-Paare pro Punkt), was das Dual von `LP1` (`46/27`) strikt verletzt (`13/12 > 1`) und `LP_49a` auf `143/81 = 1.7654` senkt.

### 1.2 Wie bricht `B1_full` (`47/27`) die `49/27`-Grenze — und ist das auf Nicht-Quadrate übertragbar?

- **Mechanismus von `B1_full` (`q = s^2`, vgl. `M3_BAER_PILOT_REPORT.md`):** Auf jeder der `q - 1` Light-Ebenen wird statt `x`-Geraden eine vollständige 2D-Baer-Struktur `R_2D(q)` der Dichte `c_2(q) = 1 + 2/sqrt(q)` platziert. Dadurch werden *alle* `L`-beteiligten Paare über 2D-Baer-Unterebenen (`q + sqrt(q)` Punkte statt reine `x`-Geraden) und *alle* `L`-beteiligten Tripel in `q^3 + 2 q^{5/2}` Punkten abgedeckt. Auf `z*` verbleibt nur `A_H x B_H x C_H` (`(4/9 + 8/27) q^3 = (20/27) q^3`), gesamt `(47/27) q^3 + 2 q^{5/2}`.
- **Übertragbarkeit auf allgemeine Primzahlpotenzen `q` (Negativbefund, `Argument`):** Ersetzt man `R_2D(q)` durch eine beliebige 2D-`M(R)`-Liste der Dichte `c_2 * q^2`, ergibt die identische Bauart
  $$|R_3| = \left(c_2 + \frac{20}{27}\right) q^3 + O(q^2).$$
  Um `49/27` zu schlagen, wäre `c_2 < 29/27 ≈ 1.074` erforderlich (um `2` zu schlagen: `c_2 < 34/27 ≈ 1.259`). Für ungerade Primzahlen `q` erreichen die Phase-8-Konstruktionen `c_2 ≈ 7/5 = 1.40` (`-> 2.141 q^3`), und bereits die Phase-8-Untergrenze (Satz C.1: `c_2 >= 91/68 ≈ 1.338`) erzwingt `(91/68 + 20/27) q^3 ≈ 2.079 q^3 > 2 q^3`. Der `B1_full`-Mechanismus ist daher **nicht** ohne Quadrat-/Unterkörper-Spurstruktur (`c_2 < 29/27`) auf Primzahlen `q` übertragbar.

### 1.3 Wo verliert `m_det` (`19/10 = 1.90 q^3`) gegenüber `49/27` und `46/27`?

In `scripts/phase9_m3_construct.py` definiert `T_r = {(a, b, (-a-b) mod q) : (a - b) mod q < r}` ein einzelnes zyklisches Intervall der Dichte `p = r/q = 1 - s`. Per exakter Inklusion-Exklusion über das Komplement-Intervall `[r, q)` (Länge `s <= 1/2`, 3-AP-Dichte `s^2/2`) folgt exakt:
$$\frac{m_{\mathrm{raw}}(T_r)}{q^3} = 3 - 2(1-s) + \left(1 - 3s + 3s^2 - \frac{s^2}{2}\right) = 2 - s + \frac{5}{2} s^2.$$
Das Minimum liegt bei `s = 1/5` (`p = 4/5`) mit Wert `2 - 1/5 + 1/10 = 19/10 = 1.90000`. Exhaustive Prüfung aller `2^q` Differenzmengen `D subset Z_q` (`q <= 13`) bestätigt zudem, dass das Intervall `D = [0, r)` unter allen zyklischen Differenzmengen bereits optimal ist.

Quantitative Aufschlüsselung des Überschusses von `m_det` (`scripts/phase9_m3_construct.py`) für `q = 7, 8, 9, 11, 13`:

| `q` | `m_det` (`m/q^3`) | `3P` | `1P` | `U` | `exh` | `pad` | `m_det - 49/27 q^3` | `m_det - 46/27 q^3` | Hauptverlust |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `7` | `631` (`1.8397`) | `294` | `147` | `168` | `22` | `0` | `+8.5` | `+46.6` | `exh = 22` (`m_raw = 609 < 49/27`) |
| `8` | `945` (`1.8457`) | `448` | `192` | `288` | `15` | `2` | `+15.8` | `+72.7` | `exh+pad = 17` (`m_raw = 928 < 49/27`) |
| `9` | `1332` (`1.8272`) | `648` | `243` | `432` | `9` | `0` | `+9.0` | `+90.0` | `exh = 9` (`m_raw = 1323 = 49/27`) |
| `11` | `2454` (`1.8437`) | `1210` | `363` | `880` | `1` | `0` | `+38.5` | `+186.4` | Band-Modell (`m_raw = 2453`, `exh = 1`) |
| `13` | `4088` (`1.8607`) | `1859` | `1014` | `1170` | `45` | `0` | `+100.9` | `+345.0` | Band-Modell (`m_raw = 4043`) + `exh = 45` |

**Ergebnis der Diagnose:** Für `q = 7, 8, 9` steckt nahezu der gesamte Verlust gegenüber `49/27` in `exh` (`9..22` Punkte) und fehlendem Punkt-Sharing (`3P`-Splitting); ab `q >= 11` dominiert zusätzlich der asymptotische Verlust des zyklischen Intervall-Bands (`19/10 = 1.90` gegenüber realisierbaren Block-PLS-Konstruktionen).

---

## 2. AP 2: Konstruktive Verbesserungen (Ansatz 1 & Ansatz 2)

### 2.1 Ansatz 1 — Deterministische Block-Idempotent-PLS + `z*`-Re-Opt + `3P`-Splitting (`scripts/phase9_m3_cyclic_opt.py`)

Rein deterministische, `std`-only Konstruktion (0 Zufall, 100% `suff=0`, skalierbar auf beliebige `q`):
1. **`k`-Block-idempotent-freie partielle lateinische Quadrate (`k in {3, 4, 5}`):** Partitioniere `F_q` in `k` Blöcke `B_0, ..., B_{k-1}` und wähle ein idempotentes lateinisches Quadrat `L` der Ordnung `k` (`L[i][i] = i`; für `i != j` ist `L[i][j] not in {i, j}`; explizit `GF(4)` für `k = 4` und `((k+1)/2)*(i+j) mod k` für ungerades `k`). Alle off-diagonalen Blöcke `(B_i, B_j, B_{L[i][j]})` bilden `3P`-Geraden, die `k` Diagonalblöcke `B_i x B_i` bilden `1P`-Geraden. Für `k | q` gilt die **exakte geschlossene Formel**:
   $$m_{\mathrm{raw}}(q, k) = \left(2 - \frac{1}{k} + \frac{2}{k^2}\right) q^3 - \left(1 - \frac{1}{k}\right) q^2.$$
   - `k = 3`: `(17/9) q^3 - (2/3) q^2 = 1.88889 q^3 - O(q^2)` (`q = 9`: `m_raw = 1323 = 49/27 * 9^3`).
   - **`k = 4`**: **`(15/8) q^3 - (3/4) q^2 = 1.87500 q^3 - O(q^2)`** (strikt unter `19/10 = 1.90`! `q = 8`: `m_raw = 912 = 1.78125 q^3`; `q = 16`: `m_raw = 7488 = 1.82812 q^3`).
   - `k = 5`: `(47/25) q^3 - (4/5) q^2 = 1.88000 q^3 - O(q^2)` (`q = 25`: `m_raw = 28875 = 1.84800 q^3`).
   Für `q mod k != 0` ergänzt eine deterministische Greedy-Vervollständigung off-diagonale `3P`-Tripel mit `dm_raw < 0`; zusätzlich wird das Differenzband (`k = 0`) als Kandidat mitgeführt.
2. **Heavy-Value-sortiertes Light-Matching + `z*`-Re-Optimierung:** Zeilen werden nach aufsteigendem Heavy-Wert auf die Light-Ebenen gematcht, sodass `3P_HHH` und `1P_HH` für `z*` erhalten bleiben; anschließend minimieren deterministische `z*`-Runden (Zeilenwechsel von `3P`/`1P`, Bijektions-Re-Matching, `U`-Relokation) die Defizite `exh`.
3. **Post-Heavy `3P`-Splitting (erhält 100% `suff=0`):** Zieht heavy-redundante `U`-Tripel von `z*` in `3P`-Splits auf `z*` und Light-Ebenen (`-1` Punkt pro Split).

**Skalierungstabelle Ansatz 1 (`q = 7..25`, 100% deterministisch, `suff = 0`):**

| `q` | Alt `m_det` (`m/q^3`) | **Ansatz 1 `m_opt` (`m/q^3`)** | Gewinn vs `m_det` | `m_raw` | Familie | `exh` | `3P`-Splits | `49/27 q^3` | Belegart |
|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| `7` | `631` (`1.8397`) | **`613`** (`1.7872`) | **`-18`** | `615` | `k4_same` | `0` | `0+2` | `622.5` | `suff=0` & `check_m3=0` |
| `8` | `945` (`1.8457`) | **`932`** (`1.8203`) | **`-13`** | `928` | `band_r7_s5` | `6` | `1+1` | `929.2` | `suff=0` & `check_m3=0` |
| `9` | `1332` (`1.8272`) | **`1326`** (`1.8189`) | **`-6`** | `1323` | `band_r8_s6` | `3` | `0+0` | `1323.0` | `suff=0` & `check_m3=0` |
| `11` | `2454` (`1.8437`) | **`2425`** (`1.8219`) | **`-29`** | `2436` | `k5_same` | `2` | `0+13` | `2415.5` | `suff=0` & `check_m3=0` |
| `13` | `4088` (`1.8607`) | **`4035`** (`1.8366`) | **`-53`** | `4038` | `k4_same` | `5` | `0+8` | `3987.1` | `suff=0` & `check_m3=0` |
| `16` | `7653` (`1.8684`) | **`7595`** (`1.8543`) | **`-58`** | `7616` | `band_r14_s5` | `10` | `4+27` | `7433.5` | `suff=0` & `check_m3=0` |
| `17` | `9182` (`1.8689`) | **`9114`** (`1.8551`) | **`-68`** | `9095` | `band_r14_s5` | `45` | `1+25` | `8916.2` | `suff=0` & `check_m3=0` |
| `19` | `12899` (`1.8806`) | **`12848`** (`1.8732`) | **`-51`** | `12737` | `k5_diff` | `155` | `0+44` | `12447.8` | `suff=0` |
| `23` | `23036` (`1.8933`) | **`22849`** (`1.8780`) | **`-187`** | `22701` | `band_r18_s7` | `199` | `0+53` | `22080.9` | `suff=0` |
| `25` | `29705` (`1.9011`) | **`29108`** (`1.8629`) | **`-597`** | `28875` | `k5_stride` | `341` | `1+107` | `28356.5` | `suff=0` |

**Asymptotisches Fazit zu Ansatz 1:** Die reale Führungskonstante sinkt deterministisch von `19/10 = 1.9000` auf `<= 15/8 = 1.8750` (bei `q = 25` bereits `1.8629 q^3`, `-597` Punkte gegenüber `m_det`, durch `k = 5` `47/25 = 1.8800` minus `O(q^2)` + `108` `3P`-Splits). Bereits rein deterministisch schlägt Ansatz 1 für `q = 7` (`613` vs `620`), `q = 11` (`2425` vs `2454`) und `q = 13` (`4035` vs `4088`) die bisherigen Gesamtbestwerte auf dem Branch.

### 2.2 Ansatz 2 — C-Kernel-Warmstart (`scripts/phase9_m3_search.c`, erweitert auf `q <= 13`)

`scripts/phase9_m3_search.c` wurde minimal um `MAX_Q = 13`, `MAX_M = 4200` sowie die Primkörper `q in {11, 13}` erweitert (`gcc -O3 -march=native -pthread -Wall -Wextra`, 0 Warnungen, `8/8 --self-test PASS` inkl. `q = 11` mit `968,968` und `q = 13` mit `2,232,152` Interaktionen bei 0 Differenzen).

Durch schrittweise Min-Unique-Deletion + fokussiertes Tabu/PAWS mit aktiven ILS-Restarts (`--w03 2`, `--restart 1500..6000`, `--threads 2`) ausgehend von den Ansatz-1-Seeds (für `q = 8` vom `k=4`-Seed mit `m_raw = 912`) wurden **alle fünf Benchmark-Ordnungen `q = 7, 8, 9, 11, 13` strikt verbessert** — und **alle drei kleinen Ordnungen `q = 7, 8, 9` strikt unter `49/27 * q^3` gedrückt**:

| `q` | Alt Best (`m_alt`) | Ansatz 1 (Det) | **Ansatz 2 (Neu Best)** | `m / q^3` | `49/27 q^3` | Delta vs `m_alt` | Delta vs `49/27` | Anatomie (`z_light`, `z*`, `pure_3P`, `non_x`, `z_owners`) | Stopp-Wall (`best_unc=1`) |
|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `7` | `620` | `613` | **`607`** | `1.76968` | `622.5` | **`-13`** | **`-15.5`** | `49..51`, `307`, `34`, `3/147`, `21/21` | `m=606`: `by_type=(0,0,0,1)` |
| `8` | `930` | `932` (`k4:938`) | **`914`** | `1.78516` | `929.2` | **`-16`** | **`-15.2`** | `64..66`, `463`, `43`, `9/192`, `24/24` | `m=913`: `by_type=(0,0,0,1)` |
| `9` | `1324` | `1326` | **`1319`** | `1.80933` | `1323.0` | **`-5`** | **`-4.0`** | `81..84`, `662`, `68`, **`0/243`**, `27/27` | `m=1318`: `by_type=(0,0,0,1)` |
| `11` | `2454` | `2425` | **`2417`** | `1.81593` | `2415.5` | **`-37`** | `+1.5` | `121..135`, `1179`, `87`, `1/363`, `33/33` | `m=2416`: `by_type=(0,0,0,1)` |
| `13` | `4088` | `4035` | **`4026`** | `1.83250` | `3987.1` | **`-62`** | `+38.9` | `169..177`, `1981`, `125`, **`0/507`**, `39/39` | `m=4025`: `by_type=(0,0,0,1)` |

**Wichtige strukturelle Beobachtungen aus Ansatz 2:**
1. **`49/27` ist auch innerhalb von reinem `suff=0` durchbrochen!** Die neue `q = 9`-Lösung (`m = 1319 < 1323 = 49/27 * 9^3`) besitzt `non_x_pairs = 0/243` und `z_owners = 27/27` (100% reine `x`-Geraden und volle `z`-Ebenen!). Die Einsparung gegenüber `49/27` entsteht ausschließlich durch **`3P`-Splitting / Zeilen-Sharing** auf den Light-Ebenen (`z_light = 81..84`) und `z*`.
2. **Einheitliche Stopp-Signatur `by_type = (0, 0, 0, 1)`:** Bei allen fünf Ordnungen tritt die lokale Barriere (`606, 913, 1318, 2416, 4025`) exakt an einer einzelnen ungedeckten Typ-3-Kombination (`0` Typ-0/1/2-Lücken) auf, nachdem das Min-Unique-Deletion-Pruning alle überzähligen `U`-Punkte abgebaut hat. Um deutlich näher an `46/27` (`584.4, 872.3, 1242.0, 2267.6, 3743.0`) zu kommen, wären großskalige Mehrzeilen-Umbauten (z. B. globales `2P`-Sharing auf `z*` oder nicht-`x`-Geraden-Paare in `Typ 2`) statt lokaler 1-Eintrag-Züge erforderlich.

---

## 3. AP 3: Vollständige Dual-Verifikation (`t = 4`, in `/tmp/phase9_m3/`) & `ca-tools@b689967`-Abgleich

Alle fünf verbesserten `R_3`-Seeds wurden kanonisiert unter `data/phase9_m3/` gespeichert (`data/phase9_m3/SHA256SUMS`: `22/22 OK`), mit `scripts/phase9_m3_lift.py --check-m3 --mode full-bg3` exakt geprüft (`0` Lücken), 2x byte-identisch nach `/tmp/phase9_m3/` ausgerollt (`t = 4`) und vollständig gegen **beide unveränderte Verifizierer** (`./verifiers/ca_verify` und `python3 verifiers/verify_independent.py`) inklusive Negativkontrolle (`N - 1` Zeilen -> `FAIL`, `rc = 1`) dual-verifiziert.

### 3.1 Dual-Verify-Protokoll (`t = 4`)

| `q` | Array `CA(N; 4, k, v)` | Seed (`data/phase9_m3/`) | Seed SHA-256 (Prefix) | Ausgerollte CA SHA-256 (2x identisch) | `ca_verify` POS / NEG | `verify_independent.py` POS / NEG | Belegstatus |
|---:|---|---|---|---|:---:|:---:|---|
| `7` | `CA(4249; 4, 10, 7)` | `R3_q7_fullbg3_opt_paws_m607.txt` | `662191d6347614de` | `5a1243a2bb01f3f590e66b3cbbe31fbefe80db26460e777946c5830d007f797d` | `PASS (0.01s)` / `FAIL (rc=1)` | `PASS (0.24s)` / `FAIL (rc=1)` | **Dual-Verify PASS** |
| `8` | `CA(7312; 4, 11, 8)` | `R3_q8_fullbg3_opt_paws_m914.txt` | `7b777bb8998834f5` | `5fc8b4a2c45e2b4cdebe7553ce1a907e8799abd33c8ad839f05668b345adf1ee` | `PASS (0.01s)` / `FAIL (rc=1)` | `PASS (0.67s)` / `FAIL (rc=1)` | **Dual-Verify PASS** |
| `9` | `CA(11871; 4, 12, 9)` | `R3_q9_fullbg3_opt_paws_m1319.txt` | `19ab9ff1b20eec11` | `774bff33af29ecfb721cbff2ac4f8b122ec4ec7b016ee8746e5c0ba8f7af16df` | `PASS (0.02s)` / `FAIL (rc=1)` | `PASS (1.60s)` / `FAIL (rc=1)` | **Dual-Verify PASS** |
| `11` | `CA(26587; 4, 14, 11)` | `R3_q11_fullbg3_opt_paws_m2417.txt` | `cb3ceece0b67e84e` | `7ff2e3c747d8d63756b66e2469e925291ee1163e7e5efd23f1e6325c9b947dad` | `PASS (0.07s)` / `FAIL (rc=1)` | `PASS (7.11s)` / `FAIL (rc=1)` | **Dual-Verify PASS** |
| `13` | `CA(52338; 4, 16, 13)` | `R3_q13_fullbg3_opt_paws_m4026.txt` | `26f2d265008b19b2` | `8db4c6c94cf87174b1b05a2f1dd302e894ac2dcbf2c2f7b0210a402ae224c727` | `PASS (0.23s)` / `FAIL (rc=1)` | `PASS (27.99s)` / `FAIL (rc=1)` | **Dual-Verify PASS** |

*(Vollständige 64-Zeichen-SHA-256-Summen der Seeds stehen in `data/phase9_m3/SHA256SUMS`.)*

### 3.2 Read-only-Abgleich gegen `chrispbsmolen/ca-tools @ b689967` (`t = 4, 5, 6`)

Verglichen gegen das kleinste `N` mit `k' >= k = q + 3` aus `ca_table.csv.gz` / `derived.csv` / `ca_frame.csv` (Snapshot `b689967`, read-only):

| `q` | `k` | `t` | **Neu `M_3` (`N`)** | Alt `M_3` (`N`) | Gewinn vs Alt `M_3` | `ca-tools@b689967` (`k'`) | Delta vs `ca-tools` | Belegstatus |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `7` | `10` | `4` | **`4249`** | `4340` | `-91` | `4459` (`k'=14`) | **`-210`** | **Dual-Verify PASS** |
| `7` | `10` | `5` | `29743` | `30380` | `-637` | `31213` (`k'=12`) | `-1470` | `check_m3=0` (nicht ausgerollt) |
| `7` | `10` | `6` | `208201` | `212660` | `-4459` | `218491` (`k'=11`) | `-10290` | `check_m3=0` (nicht ausgerollt) |
| `8` | `11` | `4` | **`7312`** | `7440` | `-128` | `7680` (`k'=15`) | **`-368`** | **Dual-Verify PASS** |
| `8` | `11` | `5` | `58496` | `59520` | `-1024` | `61440` (`k'=13`) | `-2944` | `check_m3=0` (nicht ausgerollt) |
| `8` | `11` | `6` | `467968` | `476160` | `-8192` | `491520` (`k'=12`) | `-23552` | `check_m3=0` (nicht ausgerollt) |
| `9` | `12` | `4` | **`11871`** | `11916` | `-45` | `12393` (`k'=17`) | **`-522`** | **Dual-Verify PASS** |
| `9` | `12` | `5` | `106839` | `107244` | `-405` | `111537` (`k'=14`) | `-4698` | `check_m3=0` (nicht ausgerollt) |
| `9` | `12` | `6` | `961551` | `965196` | `-3645` | `1003833` (`k'=12`) | `-42282` | `check_m3=0` (nicht ausgerollt) |
| `11` | `14` | `4` | **`26587`** | `26994` | `-407` | `27544` (`k'=14`) | **`-957`** | **Dual-Verify PASS** |
| `11` | `14` | `5` | `292457` | `296934` | `-4477` | `307461` (`k'=15`) | `-15004` | `check_m3=0` (nicht ausgerollt) |
| `11` | `14` | `6` | `3217027` | `3266274` | `-49247` | `3528481` (`k'=15`) | `-311454` | `check_m3=0` (nicht ausgerollt) |
| `13` | `16` | `4` | **`52338`** | `53144` | `-806` | `54925` (`k'=21`) | **`-2587`** | **Dual-Verify PASS** |
| `13` | `16` | `5` | `680394` | `690872` | `-10478` | `714025` (`k'=16`) | `-33631` | `check_m3=0` (nicht ausgerollt) |
| `13` | `16` | `6` | `8845122` | `8981336` | `-136214` | `9651421` (`k'=16`) | `-806299` | `check_m3=0` (nicht ausgerollt) |

---

## 4. Reproduzierbarkeit

```bash
# Ansatz 1 (deterministisch, suff=0 & check_m3=0 fuer q<=17):
python3 scripts/phase9_m3_cyclic_opt.py --all 7,8,9,11,13 --check-m3
python3 scripts/phase9_m3_cyclic_opt.py --all 16,17 --check-m3
python3 scripts/phase9_m3_cyclic_opt.py --all 19,23,25 --fast

# Ansatz 2 C-Kernel (Self-Test inkl. q=11, 13):
gcc -O3 -march=native -pthread -Wall -Wextra scripts/phase9_m3_search.c -o /tmp/phase9_m3_search -lm
/tmp/phase9_m3_search --self-test

# Seed-Integritaet & Dual-Verify (Beispiel q=13):
(cd data/phase9_m3 && sha256sum -c SHA256SUMS)
python3 scripts/phase9_m3_lift.py --q 13 --t 4 --mode full-bg3 --in data/phase9_m3/R3_q13_fullbg3_opt_paws_m4026.txt --check-m3 --out /tmp/CA_q13_t4_m4026.txt
./verifiers/ca_verify /tmp/CA_q13_t4_m4026.txt 4 13 2
python3 verifiers/verify_independent.py /tmp/CA_q13_t4_m4026.txt 4 13 --expected-n 52338 --expected-k 16
```
