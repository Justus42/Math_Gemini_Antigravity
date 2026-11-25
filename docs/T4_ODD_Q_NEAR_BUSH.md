# Phase 5B-2B: Übertragung der `k = q + 2`-Bauart auf ungerade `q = 7, 9, 11, 13` (`t = 4 NEAR_BUSH`)

- **Datum (UTC):** `2026-11-25`
- **Branch:** `exp/phase5b2b-odd-q-nearbush` (Basis: `origin/main` @ `6aa37ba`, nach Merge von PR `#15`)
- **Live-Abgleich `chrispbsmolen/ca-tools`:** Commit `7381fdbb258cc24775b0a137dc12eaf20f89c15a` (`7381fdb`, `2026-11-25T19:41:08Z`, rein lesend via `gh api`)
- **Generator & Diagnose:** [`scripts/gen_t4_odd_q_nearbush.py`](../scripts/gen_t4_odd_q_nearbush.py) (Pure Python `std`-only, deterministisch)
- **Post-Op-Reduzierer:** [`solvers/t4_postop`](../solvers/t4_postop/src/main.rs) (bestehender Zero-Dep-Rust-Solver aus Phase 5B-2A, unverändert, 2 Threads auf `Intel(R) Xeon(R) CPU @ 2.30GHz`)
- **Governance & PR-#88-Schutz:** `verifiers/`, `submission/`, alle bestehenden Phase-4-Dateien in `results/` sowie die PR-#88-Dokumente (`docs/LITERATURE_CHECK_PGL_CCL.md`, `docs/THIRD_PARTY_VERIFICATION.md`, `results/VERIFICATION_LOG_pgl_ccl.md`) sind vollständig unverändert; keine Aktionen zu `t = 3 PGL(2,q)+CCL` (Regel 7); keine Meldung nach außen.

---

## 1. Frischer Live-Abgleich (`chrispbsmolen/ca-tools @ 7381fdb`)

Gegenüber dem Phase-5B-2A-Stand (`c5f447d`) liegt `chrispbsmolen/ca-tools/main` genau **2 Commits voraus** (`30d1864`, `7381fdb`; ausschließlich Web-/Dokumentationsdateien, **`0` Änderungen unter `table/`**). Einziger offener PR ist `#88` (`Justus42`, Head `8d3365c`, `1` Kommentar, `0` Reviews, `3` Actions-Läufe im Zustand `action_required`).

| `q` | Zielzelle `k = q + 2` | `ca-tools` @ `7381fdb` (`k = q + 2`) | Quelle / Bauart (`k = q + 2`) | Referenz `k = q + 3` (`ca-tools` @ `7381fdb`) |
| :---: | :---: | :---: | --- | --- |
| `7` | `(4, 9, 7)` | `3556` (`VERIFIED`) | Sitjar v1.5 (`508` Cosets des All-Ones-Codes über `Z_7`) | `4459` (`CITED`, `k = 15` `CPHF(2; 15, 7, 4)`) |
| `8` *(Ref.)* | `(4, 10, 8)` | `6101` (`VERIFIED`) | Bai XunDi 2026 (Row-Deletion + Tabu-Postop von `6125`) | `7680` (`CITED`, `k = 15` `3-Restricted SCPHF RE`) |
| `9` | `(4, 11, 9)` | `9801` (`VERIFIED`) | Bai XunDi 2026 (`poly2` + Block/Pencil-Cover) | `12393` (`CITED`, `k = 17` `3-Restricted SCPHF RE`) |
| `11` | `(4, 13, 11)` | `21901` (`VERIFIED`) | Bai XunDi 2026 (`poly2` + Pencil-Cover auf `AG(2, 11)`) | `27544` (`CITED`, `k = 14` NCK) |
| `13` | `(4, 15, 13)` | `42757` (`VERIFIED`) | Bai XunDi 2026 (`poly2` + Pencil-Cover auf `AG(2, 13)`) | `54925` (`CITED`, `k = 21` `3-Restricted SCPHF RE`) |

*(Geprüft gegen `table/ca_table.csv.gz`, `table/ca_frame.csv` und `table/derived.csv` am Commit `7381fdb`; keine abweichenden Werte in `derived.csv`.)*

---

## 2. Herkunft & Vorarbeit (Regel 4)

- **Fremde Vorarbeit:** Bush (1952) für das orthogonale Array `OA(q^4; 4, q + 1, q)` und das `(q + 2)`-Hyperoval `OA(q^3; 3, q + 2, q)` über `GF(2^m)`; Segre (1955) für die Klassifikation der `(q + 1)`-Bögen in `PG(2, q)` für ungerades `q`; Jamison (1977) und Brouwer–Schrijver (1978) für die untere Schranke `|B| >= 2q - 1` affiner Blocking-Sets in `AG(2, q)`; Nurmela (2004) für Tabu-Search-Reparatur; Bai XunDi (2026) für `poly2` mit Geradenbüschel-Zerlegung (`N_poly2(q) = q^4 + ((q^2 - 1)/2) q^2`) sowie Row-Deletion + Tabu-Post-Optimierung; Sitjar (2026) für die `Z_7`-Coset-Lösung `CA(3556; 4, 9, 7)`.
- **Eigene Zusammensetzung in Phase 5B-2B:**
  1. Verallgemeinerung der `GF(q)`-Implementierung auf `q in {7, 8, 9, 11, 13}` und exakter Nachweis der beiden ungeraden Obstruktionen für die wörtliche `Q_g`-Bauart (Abschnitt 3).
  2. Adaption auf die Projektion `Q_cd(a, b, c, d) = (c, d)` mit disjunkten affinen Blocking-Sets und **Parabel-Packung** der überschüssigen freien Punkte in `AG(2, q)` (Abschnitt 4).
  3. Post-Optimierung der parabel-gepackten Startarrays mittels bestehendem `solvers/t4_postop` auf `q = 7` und `q = 9` (Abschnitt 5).

---

## 3. Schritt A — Gate 0a & exakte algebraische Ursachen für ungerades `q`

### 3.1 Gate 0a (Positivkontrolle auf `q = 8`, Pflicht)

Die verallgemeinerte `GF(q)`-Implementierung in [`scripts/gen_t4_odd_q_nearbush.py`](../scripts/gen_t4_odd_q_nearbush.py) (`--mode irred-quad --q 8`) reproduziert das Phase-5B-2A-Array `CA(5888; 4, 10, 8)` in `0,039 s` **byte-identisch** (`cmp -s` PASS, `sha256 = 7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802`):
- `./verifiers/ca_verify`: `0,02 s` PASS (`210/210` 4-Mengen).
- `python3 verifiers/verify_independent.py`: `0,3590 s` PASS (`860.160` Interaktionen).

### 3.2 Zwei algebraische Obstruktionen der wörtlichen `q = 8`-Bauart bei ungeradem `q`

Die wörtliche Übertragung der `q = 8`-Bauart (*irreduzibles Quadrat `g(x)` + disjunkte Blocking-Sets + skalierte `w`-Slices*) trifft für jedes ungerade `q = p^m` auf **zwei getrennte algebraische Obstruktionen**, die durch `--mode irred-quad-diag` explizit über `GF(7)`, `GF(9)`, `GF(11)` und `GF(13)` nachgerechnet wurden:

1. **Segre-/Nukleus-Obstruktion (`char(GF(q)) != 2`) für die Projektion `Q_g`:**
   Im Kern `K_g = {(u + v x) g(x) : u, v in GF(q)}` ist jede Faser `s + K_g` ein exaktes `OA(q^2; 2, q + 1, q)` mit Erzeugermatrix (nach Spaltenskalierung durch `g(x) != 0`):
   $$G_2 = \begin{pmatrix} 1 & 1 & \cdots & 1 & 0 \\ x_0 & x_1 & \cdots & x_{q-1} & 1 \end{pmatrix}.$$
   Spalte `∞` trägt also den projektiven Punkt `(0, 1, 0) in PG(2, q)`. Bei der `w`-Erweiterung `(u + v x + w x^2) g(x)` (mit `col_∞ = v`) gilt für zwei endliche Spalten `x_1 != x_2` und `col_∞`:
   $$\det \begin{pmatrix} 1 & x_1 & x_1^2 \\ 1 & x_2 & x_2^2 \\ 0 & 1 & 0 \end{pmatrix} = -(x_2 - x_1)(x_2 + x_1).$$
   - In **Charakteristik `2`** (`q = 8`) ist `(0, 1, 0)` der **Nukleus** des Kegelschnitts; `x_2 + x_1 = x_2 - x_1 != 0` liefert ein exaktes Hyperoval-`OA(q^3; 3, q + 1, q)`.
   - In **ungerader Charakteristik** verschwindet die Determinante exakt auf den `(q - 1)/2` Paaren `{x, -x}` (`x != 0`), sodass pro freiem Symbol exakt `((q - 1)/2) · (q - 1) q^2` Tripel ungedeckt bleiben (`q = 7: 882`, `q = 9: 2592`, `q = 11: 6050`, `q = 13: 12.168`).
   - **Allgemeiner Ausschluss (Satz von Segre, 1955):** Nach Zeilenumformung muss jede lineare MDS-Erweiterung `G_3` von `G_2` zu einem `OA(q^3; 3, q + 1, q)` einen `(q + 1)`-Bogen `{(1, x, h(x)) : x in GF(q)} U {(0, 1, 0)}` in `PG(2, q)` bilden. Für ungerades `q` ist jeder `(q + 1)`-Bogen ein Kegelschnitt mit Tangente `X = 0` in `(0, 1, 0)`, also von der Form `Y = alpha Z^2 + beta Z + delta`. Da `z -> z^2` in `GF(q)` für ungerades `q` nur `(q + 1)/2 < q` Werte annimmt (`4 < 7`, `5 < 9`, `6 < 11`, `7 < 13`), existiert **kein** solches `h: GF(q) -> GF(q)`. Die wörtliche `Q_g`-Bauart ist für alle ungeraden Primzahlpotenzen **konstruktiv ausgeschlossen**.

2. **Jamison-/Brouwer–Schrijver-Paritätsschranke für disjunkte Blocking-Sets in `AG(2, q)`:**
   Jedes affine Blocking-Set in `AG(2, q)` hat Größe `|B| >= 2q - 1`. Die Maximalzahl paarweise disjunkter Blocking-Sets beträgt daher:
   $$c_B^{\max}(q) = \left\lfloor \frac{q^2}{2q - 1} \right\rfloor = \begin{cases} q/2 & \text{für gerades } q, \\ (q - 1)/2 & \text{für ungerades } q. \end{cases}$$
   - Bei **geradem `q = 8`** passen `4` disjunkte 15-Punkte-Blocking-Sets (`60` Punkte) + `4` Einzelpunkte (`4` Restsymbole) exakt in `64` Punkte → `N = q^4 + (q/2)(q - 1) q^2 = 5888` (`-213` unter `6101`).
   - Bei **ungeradem `q`** gilt `((q + 1)/2)(2q - 1) = q^2 + (q - 1)/2 > q^2`; es passen höchstens `c_B = (q - 1)/2` disjunkte Blocking-Sets, sodass `(q + 1)/2` Restsymbole verbleiben. Mit einfacher Einzelpunkt-Komplettierung (`q - 1` Slices je Restsymbol) ergibt sich die geschlossene Identität:
     $$N_{\text{disjoint}}(q) = q^4 + \frac{q + 1}{2}(q - 1) q^2 = q^4 + \frac{q^2 - 1}{2} q^2 = N_{\text{poly2}}(q).$$
   Damit erreicht reine Einzelpunkt-Komplettierung über disjunkte Blocking-Sets bei ungeradem `q` **exakt** Bai XunDis `poly2`-Formel (`3577`, `9801`, `21901`, `42757`) — ohne sie deterministisch zu unterbieten.

---

## 4. Adaptierte `Q_cd`-Bauart mit Parabel-Packung (`poly2-disjoint`, Schritt A2)

Wechselt man die Projektion von `Q_g` auf **`Q_cd(a, b, c, d) = (c, d)`**, so ist `col_∞ = d` auf jeder Faser konstant und spielt die Rolle des Kegelschnittpunkts `(0, 0, 1)` statt des Nukleus `(0, 1, 0)`. Jeder freie Ankerpunkt `(c_0, d_0) in AG(2, q)` lässt sich dann für **jede** Primzahlpotenz `q` über den Spaltenversatz `T(x) = (c_0 - d_0) x^2 + d_0 x^3` (`T(∞) = 0`) durch `(q - 1)` Slices `c' in GF(q) \ {d_0}` zu einem exakten verschobenen `OA(q^3; 3, q + 1, q)` vervollständigen.

Zugleich bleiben nach Packung von `(q - 1)/2` minimalen Blocking-Sets der Größe `2q - 1` genau `(3q - 1)/2` freie Punkte in `AG(2, q)` übrig. Für jedes ungerade `q` gilt die exakte Punkt-Identität:
$$\frac{q - 1}{2}(2q - 1) + q + \frac{q - 1}{2} \cdot 1 = q^2.$$
Ordnet man einem ausgezeichneten Restsymbol `m_* = (q - 1)/2` die **`q`-Punkte-Parabel** `P = {(d^2, d) : d in GF(q)}` zu (und den übrigen `(q - 1)/2` Restsymbolen je `1` Einzelpunkt), so bleiben die Zeilenanzahlen unverändert bei `N_constr(q) = N_poly2(q)`, aber im Hauptblock sind für Symbol `m_*` bereits:
- **100 % aller Tripel mit `col_∞`** (`d` durchläuft ganz `GF(q)`) und
- **`(q + 1)/2` von `q` Restklassen** der zweiten dividierten Differenz auf `{0..q - 1}`
abgedeckt. Dadurch fällt die Mindestanzahl einzigartig überdeckter 4-Tupel (`min_row_unique`) in den `(q - 1) q^2` Zusatzzeilen von Symbol `m_*` genau auf die Hälfte gegenüber dem Standard-`poly2`-Pencil-Cover (`q = 7`: `30 -> 15`; `q = 9`: `72 -> 36`).

### Deterministischer Sweep Schritt A (`scripts/gen_t4_odd_q_nearbush.py`)

| `q` | `k = q + 2` | Bauart / Modus | `N_constr(q)` | `ca-tools` @ `7381fdb` | Lücke `N_constr - N_table` | Verifikation | `min_row_unique` (Pencil → Parabel) | Belegart (Schritt A) |
| :---: | :---: | --- | :---: | :---: | :---: | --- | :---: | --- |
| `8` *(G0a)* | `10` | `irred-quad` (`x^2+x+1`) | **`5888`** | `6101` | `−213` | `DUAL_PASS` (`0,02 s / 0,359 s`), `cmp -s` PASS | `75` | **Positivkontrolle Gate 0a PASS** (byte-identisch `7d72bc89…`) |
| `7` | `9` | `irred-quad-diag` (`x^2+1`) | — *(ungültig)* | `3556` | — | `882` fehlende Tupel/Symbol (`3` Kollisionspaare) | — | **Konstruktiv ausgeschlossen für wörtliche `Q_g`-Bauart** (Segre) |
| `7` | `9` | `poly2-disjoint` (`Q_cd` + Parabel) | `3577` | `3556` | `+21` | `DUAL_PASS` (`0,01 s / 0,108 s`, `sha256: bd229913…`) | `30 → 15` | **Deterministisch `DUAL_PASS` (`N_constr = N_poly2`, Spielraum für Gate 1)** |
| `9` | `11` | `irred-quad-diag` (`x^2+4`) | — *(ungültig)* | `9801` | — | `2592` fehlende Tupel/Symbol (`4` Kollisionspaare) | — | **Konstruktiv ausgeschlossen für wörtliche `Q_g`-Bauart** (Segre) |
| `9` | `11` | `poly2-disjoint` (`Q_cd` + Parabel) | `9801` | `9801` | `0` | `DUAL_PASS` (`0,01 s / 1,057 s`, `sha256: 3fa0850e…`) | `72 → 36` | **Deterministisch `DUAL_PASS` (`N_constr = N_poly2`, Spielraum für Gate 1)** |
| `11` | `13` | `poly2-disjoint` (`Q_cd`, `5×22-BS`) | `21901` | `21901` | `0` | `DUAL_PASS` (`0,03 s / 5,023 s`, `sha256: 0112cdea…`) | n/a | **Deterministisch `DUAL_PASS` (`N_constr = N_poly2`; kein Gate-1-Lauf in 5B-2B)** |
| `13` | `15` | `poly2-disjoint` (`Q_cd`, `6×27-BS`) | `42757` | `42757` | `0` | `ca_verify` PASS (`0,16 s`, `sha256: 04997801…`) | n/a | **Deterministisch `ca_verify` PASS (`N_constr = N_poly2`; kein Gate-1-Lauf in 5B-2B)** |

---

## 5. Schritt B — Gate 0b & Gate 1 (`solvers/t4_postop`, Budget `<= 360 s`)

Alle Läufe wurden mit dem unveränderten Zero-Dep-Rust-Reduzierer [`solvers/t4_postop`](../solvers/t4_postop/src/main.rs) (Release + LTO + `target-cpu=native`, `2` Threads) unter verbindlichem externem `timeout --kill-after=10s <SECS>` ausgeführt. Ein vorheriger `--self-test --self-test-steps 12000 --seed 5250` bestand mit `0` Abweichungen (`0,276 s`).

### 5.1 Gate 0b (Positivkontrolle auf ungeradem `q = 7`, Budget `<= 30 s`)

- **Startarray:** parabel-gepacktes `CA(3577; 4, 9, 7)` (`sha256: bd229913…`, `min_row_unique = 15` gegenüber `30` im Standard-`poly2`-Pencil-Cover).
- **Lauf (`timeout --kill-after=10s 30`, `--time-limit-secs 15 --stagnation-secs 10 --seed 5302`, `2` Threads):**
  - Reduktion in `6,20 s` auf **`CA(3479; 4, 9, 7)`** (`saved = 98 = 2 · 7^2`, `absorbed = 1287`, Gesamtlaufzeit `15,01 s`, `1.642.506 evals/s`).
  - Dual-Verifikation der abgelegten Datei [`results/t4_nearbush/CA_3479_4_9_7.txt`](../results/t4_nearbush/CA_3479_4_9_7.txt) (`sha256: dd835c93…`): `ca_verify 0,01 s` PASS, `verify_independent.py 0,2239 s` PASS.
  - **Abstand zur Tabelle (`ca-tools` @ `7381fdb` = `3556`):** **`−77` Zeilen kleiner als die Tabelle am Commit `7381fdb`**.
  - **Belegart:** **Gate 0b PASS & Dual-verifizierter Treffer (`kleiner als ca-tools @ 7381fdb`)**.

### 5.2 Gate 1 (`q = 7` und `q = 9`, Gesamtlaufzeit `266,43 s <= 360 s`)

| Lauf-ID | Zelle `(4, k, v)` | Startarray | Parameter (`2` Threads, externer `timeout`) | Dauer | Durchsatz (`evals/s`) | Ergebnis (`saved`) | Abbruchgrund & Belegart |
| --- | :---: | --- | --- | :---: | :---: | :---: | --- |
| `G1-Q9-A` | `(4, 11, 9)` | `CA(9801)` Parabel (`min_u = 36`) | `seed=5321`, `limit=115 s`, `stag=60 s`, `timeout 120` | `79,02 s` | `428.077` | **`9639`** (`saved = 162 = 2 · 9^2`, `abs = 2466`) | **Dual-verifizierter Treffer (`−162` kleiner als `ca-tools` @ `7381fdb` = `9801`)** + sauberer `60 s`-Stagnationsabbruch (`min_u = 27`) |
| `G1-Q7-A` | `(4, 9, 7)` | `CA(3577)` Parabel (`min_u = 15`) | `seed=5311`, `limit=115 s`, `stag=60 s`, `timeout 120` | `67,38 s` | `1.700.503` | `3480` (`saved = 97`, `abs = 229`) | Sauberer `60 s`-Stagnationsabbruch (`3480` dominiert von `3479` aus Gate 0b) |
| `G1-Q7-B` | `(4, 9, 7)` | `--resume CA(3479)` (`min_u = 5`) | `seed=5312`, `tenure=8`, `rw=5%`, `limit=95 s`, `stag=60 s`, `timeout 100` | `60,01 s` | `1.668.378` | `3479` (`saved = 0`) | **Post-Op-Suche erfolglos im Zeitbudget (`60,01 s` Stagnationsabbruch, `min_u = 5`)** |
| `G1-Q9-B` | `(4, 11, 9)` | `--resume CA(9639)` (`min_u = 27`) | `seed=5322`, `tenure=8`, `rw=5%`, `limit=115 s`, `stag=60 s`, `timeout 120` | `60,02 s` | `480.035` | `9639` (`saved = 0`, `abs = 5`) | **Post-Op-Suche erfolglos im Zeitbudget (`60,02 s` Stagnationsabbruch, `min_u = 27`)** |

**Strukturelle Beobachtung zur Einsparung `2 · q^2`:**
In beiden erfolgreichen Reduktionen (`q = 7`: `3577 -> 3479`, `-98 = -2 · 7^2`; `q = 9`: `9801 -> 9639`, `-162 = -2 · 9^2`) bleiben alle Symbolhäufigkeiten in der letzten Spalte exakte Vielfache von `q^2`:
- `CA_3479_4_9_7.txt`: `{0: 637, 1: 637, 2: 637, 3: 539, 4: 343, 5: 343, 6: 343}` (`13, 13, 13, 11, 7, 7, 7 × 49`)
- `CA_9639_4_11_9.txt`: `{0: 1377, 1: 1458, 2: 1377, 3: 1377, 4: 972, 5: 729, 6: 891, 7: 729, 8: 729}` (`17, 18, 17, 17, 12, 9, 11, 9, 9 × 81`)

Der Reduzierer eliminiert demnach exakt **zwei vollständige `OA(q^2)`-Slices** der Parabel-Komplettierung (bei `q = 9` kombiniert mit einer Umverteilung einzelner `81`-Zeilen-Slices über Don't-Care-Zellen von `col_∞`).

---

## 6. Gesamtbefund & Belegarten pro `q in {7, 9, 11, 13}`

| `q` | Zielzelle | `ca-tools` @ `7381fdb` | Bestes lokales Ergebnis | Delta vs. `7381fdb` | Ablageort & SHA-256 | Exakte Belegart |
| :---: | :---: | :---: | :---: | :---: | --- | --- |
| `7` | `(4, 9, 7)` | `3556` (`VER`) | **`CA(3479; 4, 9, 7)`** | **`−77`** | `results/t4_nearbush/CA_3479_4_9_7.txt` (`dd835c93…`) | **Dual-verifizierter Treffer (`kleiner als ca-tools @ 7381fdb`)**; wörtliche `Q_g`-Bauart konstruktiv ausgeschlossen (Segre); weitere Reduktion ab `3479` erfolglos im Zeitbudget (`60,01 s`, `min_u = 5`) |
| `9` | `(4, 11, 9)` | `9801` (`VER`) | **`CA(9639; 4, 11, 9)`** | **`−162`** | `results/t4_nearbush/CA_9639_4_11_9.txt` (`741f78da…`) | **Dual-verifizierter Treffer (`kleiner als ca-tools @ 7381fdb`)**; wörtliche `Q_g`-Bauart konstruktiv ausgeschlossen (Segre); weitere Reduktion ab `9639` erfolglos im Zeitbudget (`60,02 s`, `min_u = 27`) |
| `11` | `(4, 13, 11)` | `21901` (`VER`) | `CA(21901; 4, 13, 11)` *(Scratch)* | `0` | Nur Scratch (`0112cdea…`) | **Deterministisch `DUAL_PASS` (`N_constr = N_poly2`); wörtliche `Q_g`-Bauart konstruktiv ausgeschlossen (Segre); kein Post-Op-Lauf in Phase 5B-2B** |
| `13` | `(4, 15, 13)` | `42757` (`VER`) | `CA(42757; 4, 15, 13)` *(Scratch)* | `0` | Nur Scratch (`04997801…`) | **Deterministisch `ca_verify` PASS (`N_constr = N_poly2`); wörtliche `Q_g`-Bauart konstruktiv ausgeschlossen (Segre); kein Post-Op-Lauf in Phase 5B-2B** |

### Offene Anschlussoptionen (ohne Außenmeldung vor Prüfbericht zu PR `#88`)
1. **Übertragung der Parabel-Packung + Post-Op auf `q = 11` (`(4, 13, 11) < 21901`) und `q = 13` (`(4, 15, 13) < 42757`):** Analoge `((q - 1)/2) × (2q - 1) + q + (q - 1)/2 = q^2`-Parabel-Partition über `GF(11)` und `GF(13)` (Hinweis: in `solvers/t4_postop` gilt `v^4 <= u16::MAX`, sodass `v = 11` [`14.641 <= 65.535`] und `v = 13` [`28.561 <= 65.535`] direkt ohne Codeänderung unterstützt sind, sofern ein kurzer Lauf im Budget geprüft wird).
2. **Konstruktive Analyse der `2 · q^2`-Einsparung (oder `k = q + 3` auf `q = 7, 9`):** Prüfen, ob sich die von `t4_postop` gefundenen `2 · q^2`-Slice-Reduktionen auf der Parabel-Restmenge algebraisch beschreiben lassen oder ob die `t = 4`-Sammlung in `results/t4_nearbush/` (`CA_5888_4_10_8`, `CA_7070_4_11_8`, `CA_3479_4_9_7`, `CA_9639_4_11_9`) zunächst für Literatur- und Drittprüfung (`RULES.md` Punkt 2) vorbereitet wird.

