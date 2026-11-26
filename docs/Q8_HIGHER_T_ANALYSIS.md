# Phase 5C: Vollständige Prüfung des `q = 8`-Mechanismus auf `t = 5` (`(5, 10, 8)`) und `t = 6` (`(6, 10, 8)`)

- **Datum:** `2026-11-25`
- **Branch:** `exp/phase5c-q8-t5-t6` (Basis: `origin/main` @ `7a0e743`, PR `#18` gemergt)
- **Werkzeug:** [`scripts/check_q8_higher_t.py`](../scripts/check_q8_higher_t.py) (reines Pure-Python, `std`-only, deterministisch, ohne Heuristik; `solvers/` unverändert)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz` (`2` vCPUs, einzelner Thread)
- **Bezug:** Verallgemeinerung der `CA(5888; 4, 10, 8)`-Konstruktion (Verfeinerung von Bai XunDis Satz 3.5 / 5.1, `polychrome-bai2026`, über irreduzibles Quadrat `g(x)` in Charakteristik `2`) auf Stärke `t = 5` und `t = 6`.

---

## 1. Live-Abgleich `chrispbsmolen/ca-tools` (Schritt 0)

Rein lesender Abgleich via `gh api` am `2026-11-25`:
- **`main`-Commit:** `d7394120eb9703fbd92e5a28cbbda970c298f115` (`2026-11-25T20:25:41Z`, unverändert gegenüber Phase 5B-Audit).
- **Offene Pull Requests:** ausschließlich PR `#88` (`state: open`, `draft: false`, `head: 8d3365c`, `mergeable_state: clean`, `comments: 2`, `review_comments: 0`); `0` offene `t = 5`- oder `t = 6`-PRs.
- **Aktuelle Vergleichswerte (`table/ca_table.csv.gz`, `table/ca_frame.csv`, `table/derived.csv`):**

| Zelle `(t, k, v)` | Tabellenwert `N` (`ca_table` / `ca_frame`) | `derived.csv` | Tier / Quelle / Konstruktion | Zielgröße `q = 8`-Bauart `N = 8^t + 28 * 8^(t-2)` |
| :---: | :---: | :---: | --- | :---: |
| **`(5, 10, 8)`** | **`49.128`** | — | `VERIFIED` (`S7`, `pr-59`, `2026-11-09`, Credit: T. N. Sitjar / `tns-research` v1.8, `doi:10.5281/zenodo.24060956`); Post-Op (`postop-nck2013`) auf Bai XunDis `CA(49136; 5, 10, 8)` (`doi:10.5281/zenodo.23787055`, `pr-13`) | `47.104` (`−2.024`) |
| **`(6, 10, 8)`** | **`393.018`** | — | `VERIFIED` (`S7`, `pr-59`, `2026-11-09`, Credit: T. N. Sitjar / `tns-research` v1.8, `doi:10.5281/zenodo.24060956`); Post-Op (`postop-nck2013`) auf Bai XunDis `CA(393088; 6, 10, 8)` (`doi:10.5281/zenodo.23787055`, `pr-15`) | `376.832` (`−16.186`) |

- **Verifier-Vorabcheck für `t = 5` und `t = 6`:** Beide unveränderten Verifier (`./verifiers/ca_verify` und `verifiers/verify_independent.py`) bestehen kleine Test-Arrays `CA(32; 5, 5, 2)` und `CA(64; 6, 6, 2)` direkt ohne Änderung (`0,00 s` / `0,007 s`).

---

## 2. Verallgemeinerung & Gate 0 (Byte-identische Positivkontrolle bei `t = 4`)

### 2.1 Allgemeiner `q = 8`-Mechanismus für Stärke `t`
Über $\mathrm{GF}(8) = \mathrm{GF}(2)[x] / (x^3 + x + 1)$ besteht das Bush-Orthogonal-Array $\mathrm{OA}(8^t; t, 9, 8)$ aus allen Polynomen $f(x) = \sum_{i=0}^{t-1} a_i x^i$ vom Grad $< t$, ausgewertet an $x \in \mathrm{GF}(8)$ (Spalten `0..7`) sowie dem Leitkoeffizienten $a_{t-1}$ (Spalte `8` $= \infty$).

Für jedes normierte irreduzible quadratische Polynom $g(x) = x^2 + \alpha x + \beta \in \mathrm{GF}(8)[x]$ (exakt $(8^2 - 8)/2 = 28$ Polynome) hat die Quotientenabbildung
$$Q_g : \mathrm{GF}(8)^t \to \mathrm{AG}(2, 8), \qquad f(x) \mapsto f(x) \bmod g(x)$$
den $(t - 2)$-dimensionalen Kern
$$\ker(Q_g) = \{ h(x) g(x) : \deg(h) < t - 2 \} \subset \mathrm{GF}(8)^9 \qquad (|\ker(Q_g)| = 8^{t-2}).$$
Da jedes $(t - 1)$-Spalten-Richtungspolynom $e_S(x)$ vollständig in Linearfaktoren über $\mathrm{GF}(8)$ zerfällt und $g(x)$ keine Nullstelle in $\mathrm{GF}(8)$ besitzt, gilt $g \nmid e_S$. Somit bildet $Q_g$ für **jedes** $t \in \{4, 5, 6\}$ jede $(t - 1)$-Spalten-Faser des Bush-OA auf eine affine Gerade in $\mathrm{AG}(2, 8)$ ab. Mit den vier disjunkten $15$-Punkte-Blocking-Sets $\{0, 1, 2, 3\}$ und vier freien Einzelpunkten $\{4, 5, 6, 7\}$ sind alle $(t - 1)$-Tupel mit Spalte `9` $\in \{0, 1, 2, 3\}$ bereits im $8^t$-Block abgedeckt.

Die Einsparung auf $N = 8^t + 4 \cdot 7 \cdot 8^{t-2} = 8^t + 28 \cdot 8^{t-2}$ Zeilen verlangt, dass jede der vier freien Punkt-Fasern $f_0 + \ker(Q_g)$ (Größe $8^{t-2}$) durch $7$ weitere Scheiben zu einem $\mathrm{OA}(8^{t-1}; t - 1, 9, 8)$ vervollständigt werden kann.

### 2.2 Gate 0: Byte-identische Positivkontrolle (`t = 4`)
Mit `timeout --kill-after=10s 60 python3 scripts/check_q8_higher_t.py --mode gate0 --out <scratch>/gate0_CA_5888_4_10_8.txt`:
- **Ergebnis:** `CA(5888; 4, 10, 8)` in `0,065 s` erzeugt; SHA-256 = `7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` — **exakt byte-identisch** zu `results/t4_nearbush/CA_5888_4_10_8.txt` (`cmp -s` PASS).
- **Dual-Verifikation:** `./verifiers/ca_verify` PASS (`0,02 s`), `verifiers/verify_independent.py` PASS (`0,3438 s`) → **`DUAL_PASS`**.
- **Exhaustive Gegenkontrolle der Such-Engine bei `t = 4`:** Über alle `28` irreduziblen Quadrate `g` und den gesamten projektiven Quotientenraum (`28 × 299.593 = 8.388.604` projektive Punkte, davon `28 × 117.649 = 3.294.172` normierte Nichtnull-Kandidaten) findet dieselbe Engine exakt **`280` gültige MDS-Erweiterungen** (`10` je `g`, `0/84` singuläre Minoren, `0` ungedeckte Tupel, `13,814 s`).

---

## 3. Vollständige Durchrechnung für `t = 5` und `t = 6` (Schritt B)

### 3.1 Exakte Raumkardinalität & vollständige Ergebnisse
Für jedes der `28` irreduziblen Quadrate $g(x)$ hat der Quotientenraum $\mathrm{GF}(8)^9 / \ker(Q_g)$ die Dimension $11 - t$ und damit exakt $(8^{11-t} - 1)/7$ projektive 1-dimensionale Erweiterungen. Durch eindeutige Reduktion modulo $\ker(Q_g)$ lässt sich jeder Vertreter eindeutig auf $w_0 = \dots = w_{t-4} = w_\infty = 0$ bringen. Jede Koordinate $w_x = 0$ ($x \in \{t-3, \dots, 7\}$) macht den Minor $\{0, \dots, t-4, x, \infty\}$ sofort singulär; nach Normierung $w_{t-3} = 1$ verbleiben exakt $7^{10-t}$ nichttriviale Kandidaten je `g`, die sämtlich gegen alle $\binom{9}{t-1}$ Minoren exakt ausgewertet wurden:

| Stärke `t` | Zielzelle / Ziel-`N` | Irred. Quadrate `g` | Projektiver Raum `28 × (8^(11-t)-1)/7` | Normiert ausgewertet `28 × 7^(10-t)` | MDS-Treffer (`unc = 0`) | Min. singuläre Minoren (je Symbol) | Min. ungedeckte `(t-1)`-Tupel (je Symbol) | Min. ungedeckte `t`-Tupel (Gesamt-Array) | Laufzeit (Erstlauf / Repro) | Belegart |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `4` *(Kontrolle)* | `(4, 10, 8)` / `5.888` | `28` | `8.388.604` | `3.294.172` | **`280`** (`10` je `g`) | `0 / 84` | `0` | `0` | `13,814 s` | Positivkontrolle PASS |
| **`5`** | **`(5, 10, 8)` / `47.104`** | **`28`** | **`1.048.572`** (`28 × 37.449`) | **`470.596`** (`28 × 16.807`) | **`0`** (`0` je `g`) | **`7 / 126`** | **`25.088`** (`7 × 3.584`) | **`100.352`** (`4 × 25.088`) | `12,007 s` / `11,955 s` | **vollständig durchgerechnet, für diese Bauart ausgeschlossen** |
| **`6`** | **`(6, 10, 8)` / `376.832`** | **`28`** | **`131.068`** (`28 × 4.681`) | **`67.228`** (`28 × 2.401`) | **`0`** (`0` je `g`) | **`8 / 126`** | **`229.376`** (`8 × 28.672`) | **`917.504`** (`4 × 229.376`) | `2,047 s` / `2,143 s` | **vollständig durchgerechnet, für diese Bauart ausgeschlossen** |

- **Einheitlichkeit über alle `28` irreduziblen Quadrate:** Für `t = 5` liefern alle `28` Polynome `g` exakt `hits = 0` und `min_bad = 7`; für `t = 6` liefern alle `28` Polynome `g` exakt `hits = 0` und `min_bad = 8`.
- **Direkte Zeugen-Gegenprüfung (`8^(t-1)`-Zeilen-Brute-Force):**
  - `t = 5`, Zeuge `(alpha=1, beta=1, w=[0, 0, 1, 1, 6, 7, 1, 6, 0])`: direkte Auszählung über `4.096` Zeilen bestätigt exakt `7` defekte `4`-Spaltenmengen und `25.088` fehlende `4`-Tupel.
  - `t = 6`, Zeuge `(alpha=1, beta=1, w=[0, 0, 0, 1, 1, 3, 4, 7, 0])`: direkte Auszählung über `32.768` Zeilen bestätigt exakt `8` defekte `5`-Spaltenmengen und `229.376` fehlende `5`-Tupel.

---

## 4. Algebraische Ursache (auch für beliebige nichtlineare Erweiterungen)

Die Ursache des Ausschlusses für `t = 5` und `t = 6` ist rein algebraisch und schließt **nicht nur lineare**, sondern **sämtliche (auch nichtlineare)** $\mathrm{OA}(8^{t-1}; t - 1, 9, 8)$-Erweiterungen der Faser $Q_g^{-1}(p, q)$ vollständig aus:

1. **Skalierungsinvarianz über alle `28` irreduziblen Quadrate `g`:** Da $g(x) \neq 0$ für alle $x \in \mathrm{GF}(8)$, reduziert die Substitution $u_x = w_x / g(x)$ (bei $w_\infty = 0$) die MDS-Bedingung für $G_{\mathrm{ext}}(g, w)$ unabhängig von $g$ auf die Matrix $M(u)$ mit Spalten $(1, x, \dots, x^{t-3}, u_x)^T$ für $x \in \mathrm{GF}(8)$ und $(0, \dots, 0, 1, 0)^T$ an Spalte $\infty$. Das erklärt die gemessene exakte Gleichheit der Ergebnisse über alle `28` Polynome `g`.
2. **Hyperoval-Nukleus nur bei `t = 4`:** Bei `t = 4` bildet $M(u)$ mit $u_x = x^2$ neun Punkte des `10`-Punkte-Hyperovals in $\mathrm{PG}(2, 8)$ inkl. Nukleus $(0, 1, 0)^T$. Bei `t = 5` ($\mathrm{PG}(3, 8)$) bzw. `t = 6` ($\mathrm{PG}(4, 8)$) liegt die Spalte $\infty = (0, \dots, 0, 1, 0)^T$ auf der vorletzten Koordinate $x^{t-3}$ (nicht auf der Leitkoordinate). Die Projektion aus $\infty$ verlangt, dass $u_x$ gleichzeitig ohne $x^{t-3}$ und mit $x^{t-3}$ einen $(9)$-Bogen in $\mathrm{PG}(t - 2, 8)$ erzeugt; die vollständige Durchrechnung zeigt, dass kein solcher Vektor $u \in \mathrm{GF}(8)^8$ existiert.
3. **Ausschluss auch nichtlinearer $\mathrm{OA}(8^{t-1}; t - 1, 9, 8)$-Erweiterungen (Index-$\lambda = 1$-Argument):** Ein $\mathrm{OA}(8^{t-1}; t - 1, 9, 8)$ hat Index $\lambda = 1$, also Mindest-Hamming-Abstand $d_H \ge 9 - (t - 2) = 11 - t$. Enthält ein beliebiges (lineares oder nichtlineares) $\mathrm{OA}(8^{t-1}; t - 1, 9, 8)$ die Faser $C = \ker(Q_g)$ (nach Verschiebung um $-f_0$), so muss **jede einzelne** zusätzliche Zeile $w \notin C$ für jede $(t - 1)$-Spaltenmenge $S$ außerhalb von $C|_S$ liegen — äquivalent zu $\mathrm{rank}([G_{\ker}|_S;\, w|_S]) = t - 1$ für alle $S$. Da kein solches $w \in \mathrm{GF}(8)^9$ existiert, besitzt $C = \ker(Q_g)$ für $t \in \{5, 6\}$ Überdeckungsradius $\rho(C) \le 10 - t$: **Nicht einmal eine einzige zusätzliche Zeile** lässt sich kollisionsfrei zu einer Faser $Q_g^{-1}(p, q)$ hinzufügen.

---

## 5. Fazit

Der `q = 8`-Mechanismus mit freien Einzelpunkten als fertigen $8^{t-2}$-Scheiben (`N = 8^t + 28 * 8^(t-2)`) ist auf **`t = 4`** (`CA(5888; 4, 10, 8)`) beschränkt. Für **`(5, 10, 8)`** (`47.104` vs. `49.128`) und **`(6, 10, 8)`** (`376.832` vs. `393.018`) ist er **vollständig durchgerechnet, für diese Bauart ausgeschlossen**. Es wurden keine neuen Arrays erzeugt und kein Verzeichnis `results/q8_higher_t/` angelegt.

---

## 6. Abschlussvermerk Track 2 (mit Live-Abgleich `table/ca_frame.csv` @ `d739412`)

### 6.1 Live-Abgleich `table/ca_frame.csv` (`chrispbsmolen/ca-tools` @ `d7394120eb9703fbd92e5a28cbbda970c298f115`, rein lesend via `gh api`)
- **`(4, 18, 16)`:** `83.519` (`CITED`, `orthogonal array fuse` / OA über `GF(17)` fusioniert nach Colbourn–Kéri–Rivas Soriano–Schlage-Puchta 2010, Lemma 3.1).
- **`(4, 19, 16)`:** `114.489` (`VERIFIED`, Post-Op auf `CA(114495; 4, 19, 16)`).
- **`q = 32, 64`:** `0` Tabellenzellen in `table/ca_frame.csv` vorhanden.

### 6.2 Gesamtbewertung aller Parameterbereiche des freie-Scheiben-Mechanismus
- **`q = 4`:** `(4, 6, 4)` Vorhersage `352 > 340` (Tabelle); `(5, 6, 4)` Vorhersage `1.408 > 1.024` (Tabelle).
- **`q = 8, t = 5, 6`:** vollständig durchgerechnet, für diese Bauart ausgeschlossen (PR `#19`, Abschnitte 3–4).
- **`q = 16, t = 4`:** `(4, 18, 16)` Vorhersage `96.256 > 83.519` (Tabelle); `(4, 19, 16)` Aufbau `16^4 + 8 * 16^3 + 64 * 16^2 = 114.688` plus Reparaturzeilen `> 114.489` (Tabelle).
- **`q = 32, 64`:** keine Tabellenzellen in `ca-tools`.

**Fazit:** Der freie-Scheiben-Mechanismus trägt ausschließlich bei **`q = 8, t = 4`** (`CA(5888; 4, 10, 8)`, kleiner als `ca-tools` am Commit `d739412`). Track 2 ist abgeschlossen.

