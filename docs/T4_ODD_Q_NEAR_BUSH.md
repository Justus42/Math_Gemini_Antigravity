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

- **Fremde Vorarbeit:** Bush (1952) für das orthogonale Array `OA(q^4; 4, q + 1, q)` und das `(q + 2)`-Hyperoval `OA(q^3; 3, q + 2, q)` über `GF(2^m)`; Segre (1955) für die Klassifikation der `(q + 1)`-Bögen in `PG(2, q)` für ungerades `q`; Jamison (1977) und Brouwer–Schrijver (1978) für die untere Schranke `|B| >= 2q - 1` affiner Blocking-Sets in `AG(2, q)`; Nurmela (2004) für Tabu-Search-Reparatur; Nayeri–Colbourn–Konjevod (2013) für Post-Optimierung; **X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“ (Preprint vom 30.10.2026, `doi:10.5281/zenodo.23787051`, `polychrome-bai2026`; Daten `doi:10.5281/zenodo.23787055`)** für das gesamte Konstruktionsprinzip der linien-polychromatischen Färbungen von `AG(2, q)` über Bush/RS-OA (Satz 3.5), die Jamison-/Brouwer–Schrijver-Obergrenze `c <= floor(q/2)` (Prop. 4.1) sowie die Pencil-Cover-Formel `N = q^4 + ((q^2 - 1)/2) q^2` (Satz 5.1 / Prop. 5.2 / Kor. 5.3) samt Row-Deletion + Tabu-Post-Optimierung; Sitjar (2026) für die `Z_7`-Coset-Lösung `CA(3556; 4, 9, 7)`.
- **Eigener Beitrag in Phase 5B-2B (auf Basis von Bai `polychrome-bai2026`):**
  1. Verallgemeinerung der `GF(q)`-Implementierung auf `q in {7, 8, 9, 11, 13}` und explizite Nachrechnung der beiden ungeraden Obstruktionen für die wörtliche `Q_g`-Bauart (Abschnitt 3).
  2. Parabel-Packung der überschüssigen freien Punkte in `AG(2, q)` unter Projektion `Q_cd(a, b, c, d) = (c, d)` zur Halbierung von `min_row_unique` bei unveränderter Startgröße `N = q^4 + ((q^2 - 1)/2) q^2` aus Bais Kor. 5.3 (Abschnitt 4).
  3. Post-Optimierung der parabel-gepackten Startarrays mittels eigenem Reduzierer `solvers/t4_postop` auf `q = 7` und `q = 9` (Abschnitt 5).

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

Zugleich bleiben nach Packung von `(q - 1)/2` minimalen Blocking-Sets der Größe `2q - 1` (Obergrenze aus Bai 2026, Prop. 4.1 via Jamison 1977 / Brouwer–Schrijver 1978) genau `(3q - 1)/2` freie Punkte in `AG(2, q)` übrig. Für jedes ungerade `q` gilt die exakte Punkt-Identität:
$$q^2 = q + \frac{q - 1}{2}(2q - 1) + \frac{q - 1}{2}$$
(`q` Punkte Parabel `+ ((q - 1)/2)*(2q - 1)` disjunkte minimale Blocking-Sets `+ (q - 1)/2` Einzelpunkte).
Ordnet man einem ausgezeichneten Restsymbol `m_* = (q - 1)/2` die **`q`-Punkte-Parabel** `P = {(d^2, d) : d in GF(q)}` zu (und den übrigen `(q - 1)/2` Restsymbolen je `1` Einzelpunkt), so bleiben die Zeilenanzahlen unverändert bei `N_constr(q) = N_poly2(q)` (Bai 2026, Kor. 5.3), aber im Hauptblock sind für Symbol `m_*` bereits:
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
1. **Übertragung der Parabel-Packung + Post-Op auf `q = 11` (`(4, 13, 11) < 21901`) und `q = 13` (`(4, 15, 13) < 42757`):** Analoge Partition `q^2 = q` (Parabel) `+ ((q - 1)/2)*(2q - 1)` (disjunkte minimale Blocking-Sets) `+ (q - 1)/2` (Einzelpunkte) über `GF(11)` und `GF(13)` (Hinweis: in `solvers/t4_postop` gilt `v^4 <= u16::MAX`, sodass `v = 11` [`14.641 <= 65.535`] und `v = 13` [`28.561 <= 65.535`] direkt ohne Codeänderung unterstützt sind, sofern ein kurzer Lauf im Budget geprüft wird).
2. **Konstruktive Analyse der `2 · q^2`-Einsparung (oder `k = q + 3` auf `q = 7, 9`):** Prüfen, ob sich die von `t4_postop` gefundenen `2 · q^2`-Slice-Reduktionen auf der Parabel-Restmenge algebraisch beschreiben lassen oder ob die `t = 4`-Sammlung in `results/t4_nearbush/` (`CA_5888_4_10_8`, `CA_7070_4_11_8`, `CA_3479_4_9_7`, `CA_9639_4_11_9`) zunächst für Literatur- und Drittprüfung (`RULES.md` Punkt 2) vorbereitet wird.

---

# Phase 5B-2C: `CA(3430)`-Reproduktion, Determinismus-Audit (`--threads 1`), `q^2`-Slice-Analyse & Übertragung auf `q = 11, 13`

- **Datum (UTC):** `2026-11-25`
- **Branch:** `exp/phase5b2c-q11-q13-nearbush` (Basis: `origin/main` @ `104bf43`, nach Merge von PR `#16`)
- **Live-Abgleich `chrispbsmolen/ca-tools`:** Commit `d7394120eb9703fbd92e5a28cbbda970c298f115` (`2026-11-25T20:25:41Z`, rein lesend via `gh api`): `+1` Commit gegenüber `7381fdb` (ausschließlich `tools/build_site.py`, **`0` Änderungen unter `table/`**). Live-Zielwerte unverändert: `(4, 9, 7) = 3556 [VER]`, `(4, 10, 8) = 6101 [VER]`, `(4, 11, 8) = 7680 [CIT]`, `(4, 11, 9) = 9801 [VER]`, `(4, 13, 11) = 21901 [VER]`, `(4, 15, 13) = 42757 [VER]`. Einziger offener PR: `#88` (`github-actions[bot]`-Prüfkommentar `2026-11-25T20:47:49Z`: `Result: PASS. 13 of 13 claims passed.`, `0` Reviews, wartet auf Maintainer). `docs/llms.txt` („Rules for agents“) gegengelesen: eigene Arrays, keine zurückgezogenen Arrays, Namens-/KI-Offenlegung, Quellen-/DOI-Pflicht.
- **Reproduzierbarkeits-Regel (Phase 5B-2C):** Jeder `t4_postop`-Lauf strikt mit `--threads 1`, **2×** mit identischem Kommando ausgeführt und per `cmp -s` / `sha256sum` auf byte-identische Übereinstimmung geprüft; jeder Rechen- und Verifikationslauf mit externem `timeout --kill-after=10s`.

---

## 7. Schritt 0 — `CA(3430)`-Fremdreproduktion & Determinismus-Nachholung (`--threads 1`)

Alle drei bisherigen Post-Op-Zellen (`q = 7`, `q = 8 k = 11`, `q = 9`) wurden mit `--threads 1` jeweils **2×** ausgeführt. Ursache für die durchgängige Verbesserung gegenüber den 2-Thread-Läufen aus Phase 5B-2A/2B: Im Worker-Pool (`solvers/t4_postop/src/main.rs`) wählt Worker `0` stets aus den `top_k = 4` Zeilen mit minimalem `unique`-Wert, während Worker `1` aus `top_k = 12` zieht und den gemeinsamen Beststand überschreiben kann. Mit `--threads 1` bleibt der Suchpfad vollständig deterministisch und verfolgt ungestört die engste `top_k = 4`-Reduktionskette.

| Zelle `(4, k, v)` | Startarray (eigener Generator) | Bisher (2T, nicht deterministisch) | Neu (`--threads 1`, 2× byte-identisch) | Parameter & Laufzeit (Lauf 1 / Lauf 2) | Delta vs. `ca-tools @ d739412` | SHA-256 & Dual-Verify |
| :---: | --- | :---: | :---: | --- | :---: | --- |
| `(4, 9, 7)` | `CA(3577)` (`bd229913…`) | `3479` | **`CA(3430; 4, 9, 7)`** (`−147 = −3·7^2`) | `seed=5302`, `limit=15s`, `stag=10s`, `timeout 30` (`12,58s` / `12,42s`; Treffer `2,57s` / `2,42s`) | **`−126`** (`3556`) | `d5860ade…` *(exakter Abgleich zur externen Referenz-SHA-256)*; `ca 0,01s / py 0,160s` |
| `(4, 11, 8)` | `CA(7203)` (`cb222f48…`) | `7070` | **`CA(7056; 4, 11, 8)`** (`−147`) | `seed=5211`, `limit=150s`, `stag=60s`, `timeout 180` (`150,04s` / `150,04s`; Treffer `121,96s` / `129,12s`) | **`−624`** (`7680`) | `b18c1742…`; `ca 0,01s / py 0,653s` |
| `(4, 11, 9)` | `CA(9801)` (`3fa0850e…`) | `9639` | **`CA(9558; 4, 11, 9)`** (`−243 = −3·9^2`) | `seed=5321`, `limit=115s`, `stag=60s`, `timeout 180` (`96,08s` / `98,79s`; Treffer `36,07s` / `38,77s`; + Gate 0.2 3× identisch) | **`−243`** (`9801`) | `8ffd689d…`; `ca 0,01s / py 1,104s` |

*(Alle drei neuen Best-Arrays liegen dual-verifiziert in `results/t4_nearbush/` samt aktualisierter `SHA256SUMS`; die früheren 2T-Dateien bleiben als historische Referenzen erhalten und sind als dominiert gekennzeichnet.)*

---

## 8. Schritt A — Herkunft der Färbungen & offene `q^2`-Slice-Analyse

### 8.1 Herkunft der fest eingetragenen Färbungen / Blocking-Sets (`q = 7, 8, 9, 11, 13`)

Für volle Nachvollziehbarkeit wird die exakte Herkunft sämtlicher fest in den Generatoren abgelegten `AG(2, q)`-Färbungen dokumentiert:

- **`q = 8` (`K10_COLORING`, `K11_F1`, `K11_F2` in [`scripts/gen_t4_q8_nearbush.py`](../scripts/gen_t4_q8_nearbush.py) bzw. `Q8_K10_COLORING` in [`scripts/gen_t4_odd_q_nearbush.py`](../scripts/gen_t4_odd_q_nearbush.py)):** Erzeugt in Phase 5B-2A durch nicht ins Repo committete Ad-hoc-Scratch-Suchläufe (lokale Austauschsuche auf den `72` Geraden von `AG(2, 8)` nach `4` disjunkten `15`-Punkte-Blocking-Sets bzw. zwei balancierten `[16, 16, 16, 16]`-4-polychromatischen Färbungen) und als feste Konstanten eingebettet. Zur Laufzeit prüft `verify_polychromatic_4()` / `verify_blocking_sets()` sämtliche `72` affinen Geraden vollständig.
- **`q = 7` (`Q7_PARABOLA_RAW`) und `q = 9` (`Q9_PARABOLA_RAW` in [`scripts/gen_t4_odd_q_nearbush.py`](../scripts/gen_t4_odd_q_nearbush.py)):** Erzeugt in Phase 5B-2B durch nicht ins Repo committete Ad-hoc-Scratch-Suchläufe auf `AG(2, q) \ P` (mit fester Parabel `P = {(d^2, d) : d in GF(q)}`). Inspektion der Blocking-Sets zeigt für `q = 7` (`3 × 13` Punkte) und `q = 9` (`4 × 17` Punkte) jeweils **`0` enthaltene volle Geraden** (`max_line_hit = 4..5` für `q = 7`, `6` für `q = 9`), also **nichttriviale** minimale affine Blocking-Sets. Die versteckte Suche wurde in Schritt B (Abschnitt 9) durch [`scripts/search_parabola_packing.py`](../scripts/search_parabola_packing.py) explizit und reproduzierbar gemacht (Gate 0-Pack findet gültige Parabel-Packungen für `q = 7` in `0,012 s` und `q = 9` in `3,544 s` ohne Vorwissen neu).
- **`q = 11` (`Q11_DISJOINT_RAW`, `5 × 22`-BS + `11` freie Punkte) und `q = 13` (`Q13_DISJOINT_RAW`, `6 × 27`-BS + `7` freie Punkte):** Erzeugt in Phase 5B-2B durch Ad-hoc-Scratch-Suche ohne Parabel-Nebenbedingung (jeweils zur Laufzeit auf allen `132` bzw. `182` affinen Geraden von `AG(2, q)` geprüft). Bei `q = 11` belegt Symbol `5` damit `6` Bush-Punkte mit `6` paarweise verschiedenen `d`-Koordinaten (`d in {2, 3, 7, 8, 9, 10}`), bei `q = 13` belegt jedes Restsymbol `6..12` nur `1` Bush-Punkt (`q^3`-Untergrenze), während die `6` Blocking-Sets je `+2` Punkte über der Mindestgröße `25 = 2q - 1` liegen.

### 8.2 Offene `q^2`-Slice-Analyse auf `q = 7` (`3577 → 3479 → 3430`) und `q = 9` (`9801 → 9639 → 9558`)

Reproduzierbares Analyseskript: [`scripts/analyze_t4_slices.py`](../scripts/analyze_t4_slices.py) (`0,23 s` Laufzeit). Alle Befunde rein empirisch und strukturell ohne Formel-Prämisse:

1. **Vollständiger Erhalt des Bush-Polynomcodes auf den endlichen Spalten `0..q - 1`:**
   In **allen vier** reduzierten Arrays (`CA_3479`, `CA_3430`, `CA_9639`, `CA_9558`) beträgt die Zahl der Zeilen außerhalb des Grad-3-Polynomcodes `{(a + b x + c x^2 + d x^3)_{x in GF(q)}}` exakt **`0`** (`non-poly rows = 0`). Der Post-Op-Reduzierer verändert ausschließlich Einträge in `col_∞` und `col_{q+1}` (und löscht Zeilen).
2. **Welche `q^2`-Slices wurden entfernt bzw. umverteilt?**
   - **`q = 7` (`3577 → 3479`, `−2 · 49 = −98`):** `63/73` Original-Slices intakt, `8` vollständig gelöscht (`comp_m3_cp{1,3,5,6}`, `main_bs_m0_c5_d0`, `main_bs_m2_c6_d0`, `main_parab_m3_c1_d6`, `main_parab_m3_c4_d2`), `2` partiell erhalten (`11` `(col_∞, col_8)`-Einträge keine Vielfachen von `49`). Netto-Zeilen pro `col_8`-Symbol: `{0:13, 1:13, 2:13, 3:11, 4:7, 5:7, 6:7} × 49` (`m = 3` sinkt um `−2 · 49`).
   - **`q = 7` (`3577 → 3430`, `−3 · 49 = −147`):** **Reine `q^2`-Slice-Struktur ohne eine einzige Teil-Slice (`partial = 0`, `0` nicht durch `49` teilbare `(col_∞, col_8)`-Einträge)!** Alle `49/49` Bush-`OA(2401; 4, 8, 7)`-Fasern bleiben mit reiner Farbe erhalten, ergänzt durch exakt `21` reine Polynom-Zusatz-Slices (`49 + 21 = 70` Slices = `3430` Zeilen). Netto-Zeilen pro `col_8`-Symbol: `{0:13, 1:13, 2:12, 3:10, 4:7, 5:7, 6:8} × 49`. Bemerkenswert: `m = 2` fällt im Bush-Block auf **`11 < 13 = 2q - 1` Fasern** (`3` ungedeckte `AG(2, 7)`-Geraden, repariert durch genau `1` Zusatz-Slice `(m=2, col_∞=3, c=1, d=4)` → netto `−1 · 49`); `m = 3` fällt auf `7` Bush- + `3` Zusatz-Slices (`−3 · 49`); `m = 6` wächst auf `3` Bush- + `5` Zusatz-Slices (`+1 · 49`).
   - **`q = 9` (`9801 → 9639`, `−2 · 81 = −162`):** `105/121` Original-Slices intakt, `11` vollständig gelöscht, `5` partiell (`15` nicht-`81`-Vielfache in `(col_∞, col_{10})`). Netto-Symbole `{0:17, 1:18, 2:17, 3:17, 4:12, 5:9, 6:11, 7:9, 8:9} × 81` (`m = 4: −5`, `m = 1: +1`, `m = 6: +2` Slices).
   - **`q = 9` (`9801 → 9558`, `−3 · 81 = −243`):** `107/121` Original-Slices intakt, `13` vollständig gelöscht (`comp_m4_cp2`, `comp_m6_cp{0,3,5}`, `main_bs_m0_c2_d0`, `main_bs_m1_c{7_d2,8_d7}`, `main_parab_m4` an `6` Punkten), nur `1` partiell (`80/81` reine Bush-Fasern). Netto-Symbole `{0:17, 1:18, 2:17, 3:17, 4:11, 5:9, 6:11, 7:9, 8:9} × 81` (`m = 4: −6`, `m = 1: +1`, `m = 6: +2` Slices → netto **`−3 · 81`**).
3. **Strukturelle Schranken (wie viele `q^2`-Slices sind höchstens entfernbar?):**
   - **Ohne Veränderung verbleibender Zeilen:** `0` Slices. Für jede 3-Spalten-Summe `S = x_0 + x_1 + x_2 in GF(q)` deckt die Parabel `{(d^2, d)}` genau `(q + 1)/2` Klassen der zweiten dividierten Differenz `c + d S` und lässt `(q - 1)/2` Klassen ungedeckt; jeder Komplettierungswert `c' != 0` wird von `3` oder `4` Summen (`q = 7`) bzw. `4` oder `5` Summen (`q = 9`) benötigt.
   - **Bei festgehaltener, unveränderter Parabel:** Auf einer festen 3-Menge mit Summe `S` fehlen `(q - 1)/2` Restklassen → es werden mindestens `(q - 1)/2` zusätzliche Slices benötigt, also höchstens `(q - 1) - (q - 1)/2 = (q - 1)/2` entfernbare Komplettierungs-Slices auf `m_*` allein (`q = 7: <= 3`, `q = 9: <= 4`).
   - **Allgemeine Einzel-Symbol-Schranke (`CA(3, q + 1, q) >= q^3`):** Jedes Symbol `m in GF(q)` in `col_{q+1}` benötigt mindestens `q^3 = q · q^2` Zeilen. Auf `m_*` allein (Start `2q - 1` Slices) sind damit maximal `q - 1` Slices entfernbar (`q = 7: <= 6`, `q = 9: <= 8`). Global über alle Symbole beträgt der Abstand des Startarrays zum unerreichbaren `OA(q^4)`-Boden `(q^2 - 1)/2` Slices (`q = 7: 24`, `q = 9: 40`).
   - **Empirischer Befund zur Barriere:** Da `CA_3430` explizit eine Blocking-Set-Klasse (`m = 2`) unter die Jamison-Grenze `2q - 1 = 13` auf `11` Bush-Fasern `+ 1` Zusatz-Slice drückt und sowohl `q = 7` als auch `q = 9` mit `--threads 1` bereits `−3 · q^2` erreichen, existiert **keine** feste `−2 q^2`-Barriere; wie viele weitere Slices jenseits von `−3 · q^2` durch Faser-Umfärbung entfernbar sind, bleibt empirisch offen.
4. **Abgleich gegen Bai (2026) Satz 3.7 / Offenes Problem 2 ([`scripts/analyze_bai_deltas.py`](../scripts/analyze_bai_deltas.py), Details in [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) §7):**
   In `CA(3430; 4, 9, 7)` bleibt das gesamte Bush-`OA(2401; 4, 8, 7)` auf Spalten `0..7` intakt (`2401/2401`, `0` mehrdeutig, `392/2401 = 8` Slices in `col_8` gegenüber `CA(3577)` geändert); die universelle Farbzahl auf den `19.208` 3-Tupel-Fasern fällt dabei auf `2 < floor(7/2) = 3` (in `CA(5888; 4, 10, 8)`: `4 = floor(8/2)`). Keines der beiden Arrays liefert damit `> floor(q/2)` universelle Farbklassen im Sinne von Bais Satz 3.7 / Offenes Problem 2.

---

## 9. Schritt B — Explizite Parabel-Packungs-Suche (`scripts/search_parabola_packing.py`)

Das neue, reproduzierbare Suchskript [`scripts/search_parabola_packing.py`](../scripts/search_parabola_packing.py) (Pure Python `std`-only, Focused Min-Conflicts Tabu + dynamische `(Gerade, Farbe)`-Gewichte + Restarts, ohne jede hartkodierte Färbung) sucht auf `R = AG(2, q) \ P` nach `c_b = (q - 1)/2` paarweise disjunkten minimalen Blocking-Sets der exakten Größe `2q - 1` plus `(q - 1)/2` Einzelpunkten.

| `q` | Rolle / Budget | Parameter | Dauer | Schritte / Evals (`evals/s`) | Bestwert `unc` | Ergebnis & exakte Belegart |
| :---: | --- | --- | :---: | --- | :---: | --- |
| `7` | **Gate 0-Pack** (`timeout 30`) | `seed=5401`, `limit=25s` | `0,012 s` / `0,010 s` | `51` / `3.908` (`326k–383k`) | **`0`** | **Gate 0-Pack PASS (Positivkontrolle, 2× byte-identisch `3882c034…`)** |
| `9` | **Gate 0-Pack** (`timeout 30`) | `seed=5402`, `limit=25s` | `3,544 s` / `3,765 s` | `7.321` / `949.753` (`252k–268k`) | **`0`** | **Gate 0-Pack PASS (Positivkontrolle, 2× byte-identisch `191d834f…`)** |
| `11` | **Zielsuche** (`timeout 60`) | `seed=5411`, `limit=58s` | `58,240 s` | `53.288` / `10,71M` (`184k`) | `3` (`restarts=2`) | **Suche nach Parabel-Packung erfolglos (60 s), Existenz offen** |
| `13` | **Zielsuche** (`timeout 60`) | `seed=5413`, `limit=58s` | `58,553 s` | `28.672` / `8,22M` (`140k`) | `9` (`restarts=1`) | **Suche nach Parabel-Packung erfolglos (60 s), Existenz offen** |

---

## 10. Schritt C — Post-Op-Übertragung auf `q = 11` (`(4, 13, 11)`) und `q = 13` (`(4, 15, 13)`)

Für den expliziten `--self-test` bei `v = 11` und `v = 13` wurde ausschließlich `run_self_test` in [`solvers/t4_postop/src/main.rs`](../solvers/t4_postop/src/main.rs) um Auswertung von `--v` erweitert (Suchkern `Ca4State` / `Rng` / `worker_loop` vollständig unverändert). Alle Läufe starteten ausschließlich von den **eigenen** deterministischen Startarrays aus `scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint` (`q = 11: 0112cdea…`, `q = 13: 04997801…`, jeweils 2× byte-identisch und `DUAL_PASS`).

### 10.1 Gate 0 (`t4_postop`, Pflicht vor Gate 1) — vollständig PASS
1. **`--self-test --v 11 --self-test-steps 12000 --seed 5451` (`timeout 60`):** `SELF_TEST_PASS [(N=120,k=8,v=3), (N=250,k=13,v=11)]` — `12.000` inkrementelle Zell-Deltas + `10` Zeilenlöschungen gegen Brute-Force, **`0` Abweichungen** (`1,744 s`).
2. **`--self-test --v 13 --self-test-steps 12000 --seed 5453` (`timeout 60`):** `SELF_TEST_PASS [(N=120,k=8,v=3), (N=250,k=15,v=13)]` — `12.000` inkrementelle Zell-Deltas + `10` Zeilenlöschungen gegen Brute-Force, **`0` Abweichungen** (`7,431 s`).
3. **Positivkontrolle auf `q = 9` mit demselben Binary (`--threads 1 --seed 5321 --time-limit-secs 65 --stagnation-secs 25`, `timeout 120`):** Eigenes `CA(9801; 4, 11, 9)` → **`CA(9558; 4, 11, 9)`** (`<= 9639`, `63,73 s`), 2× byte-identisch (und identisch zum Schritt-0-Ergebnis `8ffd689d…`, `DUAL_PASS`).

### 10.2 Gate 1 (`q = 11` und `q = 13`, strikt `--threads 1`, Ziel `< Live-Tabellenstand`)

| Zelle `(4, k, v)` | Eigenes Startarray (`DUAL_PASS`) | Parameter (`--threads 1`, externer `timeout`) | Dauer & Durchsatz | Ergebnis (`saved`) | Determinismus (2×/3× SHA-256) | Dual-Verify & Belegart |
| :---: | --- | --- | --- | :---: | --- | --- |
| **`(4, 13, 11)`** | `CA(21901)` (`0112cdea…`, `min_u = 90`) | `seed=5461`, `limit=160s`, `stag=60s`, `timeout 180` | `63,56 s` / `63,72 s` (`86k–90k evals/s`; Treffer `3,55 s` / `3,65 s`, `60 s`-Stagnationsabbruch) | **`CA(21900; 4, 13, 11)`** (`saved = 1`, `−1` vs. `21901`) | **2× byte-identisch** (`cb7696e3…`, `cmp -s` PASS) | `ca 0,03 s / py 5,135 s` — **Dual-verifizierter Treffer (`kleiner als ca-tools @ d739412`)** |
| **`(4, 15, 13)`** | `CA(42757)` (`04997801…`, `min_u = 154`) | Initial: `seed=5471`, `limit=210s`, `stag=60s`, `timeout 240`; Determinismus-Paar: `+ --target-n 42722 --time-limit-secs 260`, `timeout 280` | Initial: `210,76 s` (`42723`) / `212,29 s` (`42722`); Bestätigung: `217,21 s` / `214,93 s` (`64–66 evals/s`, `223` Schritte, `13.910` Evals) | **`CA(42722; 4, 15, 13)`** (`saved = 35`, `−35` vs. `42757`) | **3× byte-identisch** (`1b5a6d75…`, `cmp -s` PASS mit `--target-n 42722`) | `ca 0,16 s / py 24,745 s` — **Dual-verifizierter Treffer (`kleiner als ca-tools @ d739412`)** |

*(Hinweis zur Zeitgrenze bei `q = 13`: Weil `CA(42757; 4, 15, 13)` pro gelöschter Zeile rund `5,5–6,0 s` für den Zustands-Neuaufbau benötigt und beim `210 s`-Limit noch aktiv reduzierte [Lauf 1: `42723` bei `207,01 s`, Lauf 2: `42722` bei `208,57 s`], wurden zwei identische `--target-n 42722`-Läufe zur wall-clock-unabhängigen byte-identischen Reproduktion gefahren; alle drei `42722`-Dateien stimmen bit-exakt überein.)*

### 10.3 Gesamtstand `results/t4_nearbush/` nach Phase 5B-2C (`ca-tools @ d739412`, alle 6 Pareto-Best-Arrays 2× byte-identisch & `DUAL_PASS`)

| `q` | Zielzelle | `ca-tools @ d739412` | Bestes lokales Ergebnis (`--threads 1` / det.) | Delta vs. `d739412` | Datei (`results/t4_nearbush/`) & SHA-256 | Exakte Belegart |
| :---: | :---: | :---: | :---: | :---: | --- | --- |
| `7` | `(4, 9, 7)` | `3556` (`VER`) | **`CA(3430; 4, 9, 7)`** | **`−126`** | `CA_3430_4_9_7.txt` (`d5860ade…`) | **Dual-verifizierter Treffer, 2× byte-identisch (`kleiner als ca-tools @ d739412`)** |
| `8` | `(4, 10, 8)` | `6101` (`VER`) | **`CA(5888; 4, 10, 8)`** | **`−213`** | `CA_5888_4_10_8.txt` (`7d72bc89…`) | **Dual-verifizierter Treffer, 2× byte-identisch (`kleiner als ca-tools @ d739412`)** |
| `8` | `(4, 11, 8)` | `7680` (`CIT`) | **`CA(7056; 4, 11, 8)`** | **`−624`** | `CA_7056_4_11_8.txt` (`b18c1742…`) | **Dual-verifizierter Treffer, 2× byte-identisch (`kleiner als ca-tools @ d739412`)** |
| `9` | `(4, 11, 9)` | `9801` (`VER`) | **`CA(9558; 4, 11, 9)`** | **`−243`** | `CA_9558_4_11_9.txt` (`8ffd689d…`) | **Dual-verifizierter Treffer, 3× byte-identisch (`kleiner als ca-tools @ d739412`)** |
| `11` | `(4, 13, 11)` | `21901` (`VER`) | **`CA(21900; 4, 13, 11)`** | **`−1`** | `CA_21900_4_13_11.txt` (`cb7696e3…`) | **Dual-verifizierter Treffer, 2× byte-identisch (`kleiner als ca-tools @ d739412`)** |
| `13` | `(4, 15, 13)` | `42757` (`VER`) | **`CA(42722; 4, 15, 13)`** | **`−35`** | `CA_42722_4_15_13.txt` (`1b5a6d75…`) | **Dual-verifizierter Treffer, 3× byte-identisch (`kleiner als ca-tools @ d739412`)** |

*(Außenmeldungs-Sperre bleibt aktiv: keine Einreichung bei `chrispbsmolen/ca-tools` und kein Push nach `Justus42/ca-tools` vor Abschluss der Prüfung zu PR `#88` und vollständiger Checkliste `RULES.md` Punkt 2.)*

---

## 11. Phase 5E (Schritt 0) — Abschluss von Option A (`k = q + 3`, ungerade `q in {7, 9, 11, 13}`)

Gemäß der Tabellen-Vorab-Prüfregel (`RULES.md` §4) wurde vor jedem Bau- oder Suchauftrag die Arithmetik des `CA(7203)`-Aufbaus (zwei `AG(2, q)`-Färbungen mit geteilten `t = 3`-Blöcken `N_E = CAN(3, q + 2, q)`) für ungerade `q in {7, 9, 11, 13}` gegen den Live-Stand `chrispbsmolen/ca-tools/table/ca_frame.csv @ 0b79e3f` (`2026-11-26T05:32:10Z`) gegengeprüft:

- **Disjunkte Blocking-Sets (`c = (q - 1)/2`, `r = (q + 1)/2` Restfarben):**
  $$N_{\text{disj}} \ge q^4 + r N_E + r\left(q^3 - \frac{r N_E}{q}\right).$$
- **Zwei-Pencil-Variante (`c = (q + 1)/2` Farben mit Ursprung `(0, 0)`, `r_p = (q - 1)/2` Restfarben, `(q - 1) q^2` Vertex-Reparaturen):** wegen der Symmetrie `r(q - r) = r_p(q - r_p)` gilt algebraisch exakt
  $$N_{\text{pencil}} \ge q^4 + (q - 1) q^2 + r_p N_E + r_p\left(q^3 - \frac{r_p N_E}{q}\right) = N_{\text{disj}} - q^2.$$

| `q` | Zielzelle `(4, q + 3, q)` | `N_E = CAN(3, q + 2, q)` (`ca_frame @ 0b79e3f`) | `ca_frame @ 0b79e3f` (`k = q + 3`) | Untergrenze Zwei-Pencil (`N_disj − q^2`) | Untergrenze Disjoint (`r = (q+1)/2`) | Delta Zwei-Pencil vs. Tabelle |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `7` | `(4, 10, 7)` | `472` (`CITED`) | `4459` (`CITED`, `k = 15`) | `>= 4533,14` (`4534`) | `>= 4582,14` (`4583`) | **`+74` (`+1,66 %`)** |
| `9` | `(4, 12, 9)` | `1089` (`VERIFIED`) | `12393` (`CITED`, `k = 17`) | `>= 12545` | `>= 12626` | **`+152` (`+1,23 %`)** |
| `11` | `(4, 14, 11)` | `1991` (`VERIFIED`) | `27544` (`CITED`, `k = 14`) | `>= 27936` | `>= 28057` | **`+392` (`+1,42 %`)** |
| `13` | `(4, 16, 13)` | `3289` (`VERIFIED`) | `54925` (`CITED`, `k = 21`) | `>= 54397` | `>= 54566` | `−528` (`−0,96 %`) |

**Befund & Abschluss von Option A (Belegart: rechnerische Vorab-Prüfung gegen `ca_frame.csv @ 0b79e3f`, abgeschlossen):**
- Für `q = 7, 9, 11` liegen bereits beide optimistischen Untergrenzen (`>= 4533/4534`, `>= 12545`, `>= 27936`) strikt **über** `table/ca_frame.csv @ 0b79e3f`.
- Für `q = 13` verbleibt selbst unter vollständig kollisionsfreier Packung und vor jeglichen `(col_{q+1}, col_{q+2})`-Paar-Reparaturzeilen ein Abstand von höchstens **`0,96 %`** (`−528` Zeilen; `−0,65 %` bzw. `−359` Zeilen bei disjunkten Blocking-Sets).
- **Option A (`k = q + 3` auf ungeraden `q`) wird hiermit ohne Bau- oder Such-Sprint abgeschlossen.**
