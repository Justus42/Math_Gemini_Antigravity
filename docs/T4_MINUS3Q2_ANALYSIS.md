# Phase 5E: Deterministische Sezierung (`3430` / `9558`) & geschlossene Bauart `N(q) = q^4 + (q(q - 1)/2) q^2`

- **Datum (UTC):** `2026-11-26`
- **Branch:** `exp/phase5e-minus3q2-structure` (Basis: `origin/main` @ `431328b`, nach Merge von PR `#20`)
- **Live-Abgleich `chrispbsmolen/ca-tools` (rein lesend via `gh api`):**
  - `main`: Commit `0b79e3fb71af992bc1d5638ade0c1f972a43a12d` (`0b79e3f`, `2026-11-26T05:32:10Z`: Merge von PR `#88` `submit/jeserigk-pgl-ccl-2026-11`).
  - `table/ca_frame.csv` auf `t = 4`: gegenüber `d739412` unverändert (`(4, 9, 7) = 3556`, `(4, 10, 8) = 6101`, `(4, 11, 8) = 7680`, `(4, 11, 9) = 9801`, `(4, 13, 11) = 21901`, `(4, 15, 13) = 42757`).
  - **PR-#88-Schutz & Regel 7:** Keine Änderungen an `verifiers/`, `submission/`, `solvers/`, bestehenden Dateien in `results/` oder PR-#88-Dokumenten; kein Schreibzugriff auf `Justus42/ca-tools` oder `chrispbsmolen/ca-tools`; keine Aktionen zu `t = 3 PGL(2,q)+CCL`.
- **Skripte (Pure Python `std`-only, suchfrei):**
  - Sezierung: [`scripts/analyze_minus3q2.py`](../scripts/analyze_minus3q2.py) (`0,287 s`)
  - Deterministischer Generator: [`scripts/gen_t4_minus3q2.py`](../scripts/gen_t4_minus3q2.py) (`< 0,25 s` je Array)

---

## 1. Herkunft & fremde Vorarbeit (Regel 4)

- **Fremde Vorarbeit (zuerst genannt):**
  - **K. A. Bush (1952):** Orthogonales Array `OA(q^4; 4, q + 1, q)` über `GF(q)` aus Polynomen vom Grad `<= 3` (`(a + b x + c x^2 + d x^3)_{x in GF(q)}`, `col_∞ = d`).
  - **R. E. Jamison (1977)** und **A. E. Brouwer & A. Schrijver (1978):** Untere Schranke `|B| >= 2q - 1` für affine Blocking-Sets in `AG(2, q)`.
  - **X. Bai (Preprint vom `30.10.2026`, `doi:10.5281/zenodo.23787051`, `polychrome-bai2026`; Daten `doi:10.5281/zenodo.23787055`, `deposit-bai2026`):** `poly2`-Rahmen zur Erweiterung des Bush-`OA(q^4)` um eine Zusatzspalte `col_{q+1}` über `AG(2, q)`-Färbungen mit Pencil-Cover (`Kor. 5.3`: `N = q^4 + ((q^2 - 1)/2) q^2` für ungerades `q`; `Prop. 5.4`: `N = q^4 + (q^2/2) q^2` für gerades `q`).
- **Beitrag in Phase 5E:**
  1. Suchfreie Sezierung der in Phase 5B-2C per `t4_postop` gefundenen Arrays `CA(3430; 4, 9, 7)` und `CA(9558; 4, 11, 9)`.
  2. Extraktion des zugrundeliegenden algebraischen Mechanismus (*Horizontallinien-Vervollständigung `d = const` mit entkoppeltem `col_∞`* in Zusatz-`OA(q^2)`-Slices) sowie Nachweis der zugehörigen Jamison-Budgetschranke `b_m + 2 e_m >= 2q - 1` (globale Untergrenze `E >= q(q - 1)/2` Zusatz-Slices).
  3. Geschlossene, suchfreie Konstruktion `col_{q+1}(c, d) = min(c, d)` + Zusatz-Slices `{(c, d, col_∞ = c, col_{q+1} = d) : 0 <= c < d < q}` mit exakter Zeilenanzahl
     $$N(q) = q^4 + \binom{q}{2} q^2 = q^4 + \frac{q^3(q - 1)}{2} = \frac{q^3(3q - 1)}{2},$$
     die die Jamison-Schranke für jede Primzahlpotenz `q >= 4` mit Gleichheit erreicht und Bais `Kor. 5.3` / `Prop. 5.4` deterministisch um `floor(q/2) * q^2` Zeilen unterbietet (nicht nur `−3 q^2`).
- **Neuheitsvorbehalt (Regel 4):** Da die externe Literatur-Restliste ([`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) §8.2: arXiv 2023–2026, Colbourn–Lanus 2018 Volltext, `tns-research` v1.7–v1.9) nicht vollständig abgeschlossen ist, werden alle Größen streng als **„kleiner als `ca-tools` am Commit `0b79e3f`“** ausgewiesen (keine Neuheits- oder Rekordbehauptung).

---

## 2. Schritt A: Suchfreie Sezierung von `CA(3430; 4, 9, 7)` und `CA(9558; 4, 11, 9)`

Ausführung: `timeout --kill-after=10s 120 python3 scripts/analyze_minus3q2.py` (`0,287 s`).

### 2.1 Zeilen- und Zell-Diff gegen die Startarrays (`CA(3577)` / `CA(9801)`)

| Kenngröße | `q = 7`: `3577 → 3430` (`−147 = −3 · 7^2`) | `q = 9`: `9801 → 9558` (`−243 = −3 · 9^2`) |
| --- | :---: | :---: |
| Nicht-Polynom-Zeilen auf Spalten `0..q - 1` | **`0`** (`100 %` Bush-Grad-3-Code) | **`0`** (`100 %` Bush-Grad-3-Code) |
| Exakt unveränderte Zeilen | `2940 / 3577` | `8668 / 9801` |
| Bush-`OA(q^4)` (`col_∞ == d`) erhalten | **`2401 / 2401`** (`0` fehlend, `0` doppelt) | **`6561 / 6561`** (`0` fehlend, `1` doppelt auf `(c=1, d=0)`) |
| Im Bush-`OA(q^4)` umgefärbte `col_{q+1}`-Zeilen | `392 / 2401` (`8 / 49` reine `q^2`-Fasern) | `729 / 6561` (`9 / 81` reine Fasern `+ 1` Zeile) |
| Paarung auf identischem Polynom `(a,b,c,d)`: 1-Zell- / 2-Zell-Edits | `441` / `0` | `809` / `0` |
| Vollständige vs. partielle `q^2`-Slices im Ergebnis | `70` voll, **`0` partiell** (`49` Bush `+ 21` Extra) | `117` voll, `8` partiell (alle auf `(c=1, d=0)`, `m=4`, `81/81` `(a,b)`-Paare) |
| Netto-Zeilenlöschung | `−147` (`5` Extra-Slices weg, `2` neu) | `−243` (`4` Extra-Slices weg, `1` voll neu `+ 1` gemischt-`ci` auf `(1,0)`) |

**Befund zum `OA(q^4)`-Basisblock:** In beiden Arrays bleibt das gesamte Bush-`OA(q^4; 4, q + 1, q)` auf Spalten `0..q` vollständig erhalten; `t4_postop` tastet keine endliche Spalte `0..q - 1` an, sondern färbt ausschließlich Bush-Fasern in `col_{q+1}` um und ersetzt bzw. löscht Zusatz-`OA(q^2)`-Slices.

### 2.2 Algebraische Ursache der Einsparung & Jamison-Budget `b_m + 2 e_m >= 2q - 1`

Für ein Array aus dem vollen Bush-`OA(q^4)` (Faserfärbung `B_m subset AG(2, q)`, `b_m = |B_m|`) und Zusatz-`OA(q^2)`-Polynom-Slices `E_m` (`(c, d, ci) in GF(q)^3`, `e_m = |E_m|`) zerfallen die Abdeckungsbedingungen für Symbol `m` in `col_{q+1}` in zwei vollständig entkoppelte Bedingungen:
1. **`col_∞`-Bedingung (`{x_0, x_1, col_∞, col_{q+1}}`):** `{d : (c, d) in B_m} U {ci : (c, d, ci) in E_m} = GF(q)`. Insbesondere gilt `q - u_m <= e_m`, wobei `u_m = |{d : (c, d) in B_m}|` die Zahl der von `B_m` getroffenen Horizontallinien ist.
2. **Nicht-horizontale Geraden (`{x_0, x_1, x_2, col_{q+1}}`):** Da die zweite dividierte Differenz auf `{x_0, x_1, x_2}` gleich `c + S d` (`S = x_0 + x_1 + x_2`) ist, muss `P_m = B_m U {(c, d) : (c, d, ci) in E_m}` alle `q^2` nicht-horizontalen Geraden `c + S d = r` von `AG(2, q)` treffen.

**Satz (Jamison-Budget für `OA(q^4) + q^2`-Slices):**
Ergänzt man `P_m` auf jeder der `q - u_m <= e_m` von `B_m` verfehlten Horizontallinien um genau `1` Punkt, so entsteht ein affines Blocking-Set `S_m subset AG(2, q)`. Nach Jamison (1977) / Brouwer–Schrijver (1978) gilt `|S_m| >= 2q - 1`, also
$$b_m + 2 e_m \ge |P_m| + (q - u_m) \ge |S_m| \ge 2q - 1 \quad \forall m \in \mathbb{F}_q.$$
Summation über alle `q` Symbole mit `sum_m b_m = q^2` liefert die scharfe globale Untergrenze:
$$E = \sum_{m=0}^{q-1} e_m \ge \frac{q(2q - 1) - q^2}{2} = \frac{q(q - 1)}{2} \implies N \ge q^4 + \frac{q(q - 1)}{2} q^2.$$

**Sezierung der konkreten Arrays im Jamison-Budget:**
- **Bais Pencil-Cover (`Kor. 5.3`) & Parabel-Startarrays:** Beide starten bei `E = (q^2 - 1)/2` und tragen exakt `waste = sum_m (b_m + 2 e_m - (2q - 1)) = q - 1` (`(q - 1)/2` überschüssige `q^2`-Slices):
  - Im Parabel-Startarray liegt die gesamte Redundanz `q - 1` auf dem Parabel-Symbol `m_*` (`b = q, e = q - 1 -> b + 2e = 3q - 2`).
  - Im Pencil-Cover (`Kor. 5.3`) verteilt sie sich als `+1` auf jede der `(q - 1)/2` Pencil-Paar-Farben (`b = 2q - 2, e = 1 -> 2q`) und `+1` auf jede der `(q - 1)/2` leeren Farben (`b = 0, e = q -> 2q`).
- **`CA(3430; 4, 9, 7)` (`q = 7`, `2q - 1 = 13`):** `t4_postop` löst die Parabel auf `m_* = 3` zugunsten der Horizontallinie `d = 0` auf (`4` Bush-Punkte `c in {0, 4, 5, 6}` + `3` Extra-Slices `(1,0,6), (2,0,2), (3,0,3)` mit entkoppeltem `col_∞ in {2, 3, 6}`) und drückt `m = 2` auf `11` Bush- + `1` Extra-Slice `(1, 4, 3)`. **Jedes der `7` Symbole erreicht exakt `b_m + 2 e_m = 13` (`waste = 0`, `E = 21 = 7·6/2`, globales Jamison-Minimum erreicht).**
- **`CA(9558; 4, 11, 9)` (`q = 9`, `2q - 1 = 17`):** Derselbe Horizontallinien-Mechanismus auf `m_* = 4` (`d = 0`: `2` Bush-Punkte `c in {0, 2}` + `7` Extra-Slices `c in {1, 3..8}` mit entkoppeltem `col_∞`, davon `1` Slice auf `(1,0)` mit `81/81` `(a,b)`-Paaren und gemischtem `col_∞`), jedoch bleibt `t4_postop` mit **`waste = 2`** (`m = 1: b=18, e=0` und `m = 4: b=4, e=7`) hängen — genau **`+1` `q^2`-Slice (`+81` Zeilen)** über dem Jamison-Minimum `E = 36` (`N = 9477`)!

### 2.3 Explizite Beantwortung der beiden Strukturfragen (Schritt A)

1. **Einheitlich über `GF(q)` beschreibbar?** **Ja.** Der extrahierte Mechanismus (*Horizontallinie `d = m` im Verein aus Bush- und Extra-Slices + entkoppeltes `col_∞` bei exaktem Jamison-Budget `b_m + 2 e_m = 2q - 1`*) ist für **jede** Primzahlpotenz `q` durch eine einzige geschlossene Vorschrift ohne Suche beschreibbar und verallgemeinert `−3 q^2` zu `−floor(q/2) q^2`.
2. **Abhängigkeit von Parabel-Packung vs. Pencil-Cover (Kor. 5.3)?** Der Mechanismus benötigt **weder** eine Parabel-Packung **noch** eine Blocking-Set-Suche. In der transitiven Variante `col_{q+1}(c, d) = min(c, d)` bleibt Farbe `0` (`{c = 0} U {d = 0}`, `2q - 1` Punkte, `0` Extra-Slices) **identisch** zu Farbe `0` in Bais Pencil-Cover (`Kor. 5.3`), während die übrigen `q - 1` Farben auf `{1..q - 1}^2` Bais schräge Geradenpaare und leere Farben deterministisch durch verschachtelte L-Formen ersetzen und sämtliche `(q - 1)/2` überschüssigen Slices eliminieren.

---

## 3. Geschlossene Konstruktion (`scripts/gen_t4_minus3q2.py`)

Sei `q >= 4` eine beliebige Primzahlpotenz und `0 < 1 < ... < q - 1` eine feste lineare Ordnung auf `GF(q)`. Das Array `A` mit `k = q + 2` Spalten (`GF(q) U {∞, *}`) und
$$N(q) = q^4 + \frac{q(q - 1)}{2} q^2 = \frac{q^3(3q - 1)}{2}$$
Zeilen besteht aus zwei Blöcken:
1. **Block 1 (`q^4` Zeilen, Bush-`OA(q^4)`):** Für alle `(a, b, c, d) in GF(q)^4`:
   $$\text{row}(a, b, c, d) = \big((a + b x + c x^2 + d x^3)_{x \in \mathbb{F}_q},\; d,\; \min(c, d)\big).$$
2. **Block 2 (`(q(q - 1)/2) q^2` Zeilen, entkoppelte `OA(q^2)`-Slices):** Für alle `0 <= c < d < q` und alle `(a, b) in GF(q)^2`:
   $$\text{row}'(a, b, c, d) = \big((a + b x + c x^2 + d x^3)_{x \in \mathbb{F}_q},\; c,\; d\big).$$

**Beweisskizze (`CA(N(q); 4, q + 2, q)` für alle Primzahlpotenzen `q >= 4`):**
- *4-Mengen ohne Spalte `*`:* vollständig abgedeckt durch das Bush-`OA(q^4; 4, q + 1, q)` in Block 1.
- *4-Mengen `{x_0, x_1, ∞, *}`:* Für beliebiges `m in GF(q)` (Spalte `*`) und `y_∞ in GF(q)` (Spalte `∞`) liegt `(c, d) = (m, y_∞)` bei `y_∞ >= m` in Block 1 (`min(m, y_∞) = m`) und `(c, d) = (y_∞, m)` bei `y_∞ < m` in Block 2 (`col_∞ = y_∞`, `col_* = m`). Da `(a, b)` ganz `GF(q)^2` durchläuft, wird jedes `(y_0, y_1)` genau einmal getroffen.
- *4-Mengen `{x_0, x_1, x_2, *}`:* Sei `S = x_0 + x_1 + x_2` und `r` die eindeutige zweite dividierte Differenz von `(y_0, y_1, y_2)`. Setze `d = m` und `c = r - S m`. Für `c >= m` erscheint `(c, m)` in Block 1 (`min(c, m) = m`), für `c < m` in Block 2 (`col_* = m`); die Variation von `(a, b) in GF(q)^2` deckt `(y_0, y_1, y_2)` eindeutig ab.
- *Jamison-Optimalität:* Für jedes `m in {0..q - 1}` gilt `b_m = 2(q - m) - 1`, `e_m = m`, also `b_m + 2 e_m = 2q - 1` (`waste = 0`). *(Eine vollständig balancierte Variante `--variant cyclic` für ungerades `q` mit `b_m = q`, `e_m = (q - 1)/2` erreicht exakt dieselbe Größe `N(q)`.)*

---

## 4. Gate 0 (Positivkontrolle `q = 7, 8, 9`) & Schritt B (`q = 11, 13`)

Alle Generierungs-, Verifikations- und Negativkontrollläufe wurden rein deterministisch ohne Solver und unter externem `timeout --kill-after=10s <SECS>` auf `Intel(R) Xeon(R) CPU @ 2.30GHz` ausgeführt.

| Phase | `q` | Zielzelle `(4, q+2, q)` | Vorhersage `N(q)` (vs. Bai Kor. 5.3/Prop. 5.4) | `ca-tools @ 0b79e3f` | Delta vs. `0b79e3f` | Erstlauf / Repro (`cmp -s`) | `ca_verify` / `verify_independent.py` | Negativkontrolle (`N - 1` Zeilen) | SHA-256 & Ablage / Belegart |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **G0** | `7` | `(4, 9, 7)` | **`3430`** (`−3 · 7^2`) | `3556` (`VER`) | **`−126`** | `0,014 s` / `0,015 s` (`PASS`) | `0,01 s` / `0,1123 s` (`DUAL_PASS`) | `ca rc=1`, `py rc=1` (`56` Lücken) | `d29b5155…` (Scratch; `CA_3430` unverändert in `results/t4_nearbush/`) — **Positivkontrolle Gate 0 PASS** |
| **G0*** | `8` | `(4, 10, 8)` | **`5888`** (`−4 · 8^2`) | `6101` (`VER`) | **`−213`** | `0,033 s` / `0,031 s` (`PASS`) | `0,02 s` / `0,3217 s` (`DUAL_PASS`) | — *(Zusatzkontrolle)* | `2e4bf66b…` (Scratch; `CA_5888` unverändert in `results/t4_nearbush/`) — **Positivkontrolle gerades `q` PASS** |
| **G0 / Neu** | `9` | `(4, 11, 9)` | **`9477`** (`−4 · 9^2`, **`−81` unter `9558`**) | `9801` (`VER`) | **`−324`** | `0,048 s` / `0,048 s` (`PASS`) | `0,01 s` / `0,9239 s` (`DUAL_PASS`) | `ca rc=1`, `py rc=1` (`120` Lücken) | `eeea9454…` → [`results/t4_nearbush/CA_9477_4_11_9.txt`](../results/t4_nearbush/CA_9477_4_11_9.txt) — **Dual-verifizierter Treffer (`kleiner als ca-tools @ 0b79e3f`)** |
| **Step B** | `11` | `(4, 13, 11)` | **`21296`** (`−5 · 11^2`, **`−242` unter `21538`**) | `21901` (`VER`) | **`−605`** | `0,123 s` / `0,115 s` (`PASS`) | `0,03 s` / `4,1342 s` (`DUAL_PASS`) | `ca rc=1`, `py rc=1` (`220` Lücken) | `cb9a4c5e…` → [`results/t4_nearbush/CA_21296_4_13_11.txt`](../results/t4_nearbush/CA_21296_4_13_11.txt) — **Dual-verifizierter Treffer (`kleiner als ca-tools @ 0b79e3f`)** |
| **Step B** | `13` | `(4, 15, 13)` | **`41743`** (`−6 · 13^2`, **`−507` unter `42250`**) | `42757` (`VER`) | **`−1014`** | `0,247 s` / `0,250 s` (`PASS`) | `0,10 s` / `17,3230 s` (`DUAL_PASS`) | `ca rc=1`, `py rc=1` (`364` Lücken) | `e8435eb6…` → [`results/t4_nearbush/CA_41743_4_15_13.txt`](../results/t4_nearbush/CA_41743_4_15_13.txt) — **Dual-verifizierter Treffer (`kleiner als ca-tools @ 0b79e3f`)** |

*(Zusätzlich bestanden `--variant cyclic` für `q = 7` [`3430`, `87a92100…`] und `q = 9` [`9477`, `996bed73…`] `ca_verify` in `0,01 s`. Summe Erstlauf-Generierung `q = 7, 8, 9, 11, 13`: `0,465 s`; Summe Repro-Generierung: `0,459 s`.)*

---

## 5. Tabellen-Abgleich weiterer Primzahlpotenzen (`ca_frame.csv @ 0b79e3f`, rein rechnerisch)

Gemäß der Tabellen-Vorab-Prüfregel (`RULES.md` §4) zeigt der direkte Vergleich von `N(q) = q^4 + (q(q - 1)/2) q^2` gegen `table/ca_frame.csv @ 0b79e3f`:

| `q` | `k = q + 2` | `N(q)` (Formel) | `N_Bai` (`Kor. 5.3` / `Prop. 5.4`) | `ca_frame @ 0b79e3f` | Delta `N(q) − Tabelle` | Einordnung |
| :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `4` | `6` | `352` | `384` | `340` (`CITED`) | `+12` | über Tabelle |
| `5` | `7` | `875` | `925` | `825` (`VERIFIED`) | `+50` | über Tabelle |
| `7` | `9` | **`3430`** | `3577` | `3556` (`VERIFIED`) | **`−126`** | **dual-verifiziert** (`CA_3430` lokal) |
| `8` | `10` | **`5888`** | `6144` | `6101` (`VERIFIED`) | **`−213`** | **dual-verifiziert** (`CA_5888` lokal) |
| `9` | `11` | **`9477`** | `9801` | `9801` (`VERIFIED`) | **`−324`** | **dual-verifiziert** (`CA_9477` neu in `results/t4_nearbush/`) |
| `11` | `13` | **`21296`** | `21901` | `21901` (`VERIFIED`) | **`−605`** | **dual-verifiziert** (`CA_21296` neu in `results/t4_nearbush/`) |
| `13` | `15` | **`41743`** | `42757` | `42757` (`VERIFIED`) | **`−1014`** | **dual-verifiziert** (`CA_41743` neu in `results/t4_nearbush/`) |
| `16` | `18` | `96256` | `98304` | `83519` (`CITED`) | `+12737` | über Tabelle (`OA fuse`) |
| `17` | `19` | `122825` | `125137` | `125137` (`VERIFIED`) | `−2312` | rein tabellarisch kleiner als `@ 0b79e3f` *(in Phase 5E nicht erzeugt)* |
| `19` | `21` | `192052` | `195301` | `195301` (`VERIFIED`) | `−3249` | rein tabellarisch kleiner als `@ 0b79e3f` *(in Phase 5E nicht erzeugt)* |
| `23` | `25` | `413678` | `419497` | `390621` (`CITED`, `k=26`) | `+23057` | über Tabelle (`OA fuse fuse`) |
| `25` | `27` | `578125` | `585625` | `531437` (`CITED`, `k=28`) | `+46688` | über Tabelle (`OA fuse fuse`) |

---

## 6. Aktueller Pareto-Stand `results/t4_nearbush/` (13 Dateien, `SHA256SUMS` 13/13 OK)

Alle bestehenden `10` Dateien aus Phase 5B bleiben unverändert als Referenz erhalten; die drei neuen deterministischen Pareto-Best-Arrays (`CA_9477`, `CA_21296`, `CA_41743`) lösen `CA_9558`, `CA_21900` und `CA_42722` als Bestwerte ab:

| Zelle `(4, k, v)` | `ca-tools @ 0b79e3f` | Bestes lokales Array | Delta vs. `0b79e3f` | Bauart / Quelle | Datei (`results/t4_nearbush/`) & SHA-256 |
| :---: | :---: | :---: | :---: | --- | --- |
| `(4, 9, 7)` | `3556` (`VER`) | **`CA(3430; 4, 9, 7)`** | **`−126`** | Phase 5B-2C (`t4_postop`) **und** Phase 5E (`gen_t4_minus3q2.py`, `0,014 s`) | `CA_3430_4_9_7.txt` (`d5860ade…`) *(det. Äquiv. `d29b5155…`)* |
| `(4, 10, 8)` | `6101` (`VER`) | **`CA(5888; 4, 10, 8)`** | **`−213`** | Phase 5B-2A (`gen_t4_q8_nearbush.py`) **und** Phase 5E (`gen_t4_minus3q2.py`, `0,033 s`) | `CA_5888_4_10_8.txt` (`7d72bc89…`) *(det. Äquiv. `2e4bf66b…`)* |
| `(4, 11, 8)` | `7680` (`CIT`) | **`CA(7056; 4, 11, 8)`** | **`−624`** | Phase 5B-2C (`k11-polychrom` + `t4_postop` 1T) | `CA_7056_4_11_8.txt` (`b18c1742…`) |
| **`(4, 11, 9)`** | `9801` (`VER`) | **`CA(9477; 4, 11, 9)`** | **`−324`** | **Phase 5E rein deterministisch (`gen_t4_minus3q2.py`, `0,048 s`)** | `CA_9477_4_11_9.txt` (`eeea9454…`) *(löst `CA_9558` ab)* |
| **`(4, 13, 11)`** | `21901` (`VER`) | **`CA(21296; 4, 13, 11)`** | **`−605`** | **Phase 5E rein deterministisch (`gen_t4_minus3q2.py`, `0,123 s`)** | `CA_21296_4_13_11.txt` (`cb9a4c5e…`) *(löst `CA_21900` ab)* |
| **`(4, 15, 13)`** | `42757` (`VER`) | **`CA(41743; 4, 15, 13)`** | **`−1014`** | **Phase 5E rein deterministisch (`gen_t4_minus3q2.py`, `0,247 s`)** | `CA_41743_4_15_13.txt` (`e8435eb6…`) *(löst `CA_42722` ab)* |

*(Damit sind **5 von 6** Pareto-Best-Zellen — `q = 7, 8, 9, 11, 13` für `k = q + 2` — vollständig suchfrei, ohne Solver und ohne Parabel-Packung in jeweils `< 0,3 s` deterministisch erzeugbar.)*
