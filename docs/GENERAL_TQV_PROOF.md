# Vollständiger mathematischer Beweis: `CAN(t, q + 2, v) <= q^t + C(v, 2) * q^(t - 2)`

- **Datum (UTC):** `2026-11-26`
- **Branch:** `exp/phase6a-general-tqv` (Basis `origin/main` @ `68c8402`)
- **Zugehörige Skripte:** [`scripts/gen_general_tqv.py`](../scripts/gen_general_tqv.py) (deterministischer Generator, Pure Python `std`-only), [`scripts/scan_general_tqv.py`](../scripts/scan_general_tqv.py) (Tabellen-Scan).
- **Neuheitsvorbehalt & Einreichungs-Sperre (Regel 4):** Die externe Literaturprüfung für die allgemeine Formel `q^t + C(v, 2) * q^(t - 2)` (einschließlich beliebiger Stärken `t` und Alphabet-Einschränkungen `v < q`) ist **noch nicht abgeschlossen**. Dieses Dokument erhebt ausdrücklich **keine** Neuheits- oder Rekordbehauptung; Tabellenvergleiche erfolgen ausschließlich sachlich als *„kleiner als `ca-tools` am Commit `<SHA>`“*.

---

## 1. Voraussetzungen und Hauptsatz

### Notation
- Sei $q = p^r$ eine Primzahlpotenz ($p$ prim, $r \ge 1$) und $\mathbb{F}_q$ der endliche Körper der Ordnung $q$.
- Fixiere eine beliebige Bijektion $\iota: \{0, 1, \dots, q - 1\} \xrightarrow{\sim} \mathbb{F}_q$; im Folgenden identifizieren wir die Elemente von $\mathbb{F}_q$ mit $\{0, 1, \dots, q - 1\}$ samt der natürlichen totalen Ordnung $0 < 1 < \dots < q - 1$ (die Körperoperationen $+, -, \cdot$ bleiben die von $\mathbb{F}_q$, die Ordnung $<$ ist rein kombinatorisch).
- Für eine ganze Zahl $v$ mit $2 \le v \le q$ sei $\pi: \mathbb{F}_q \to \{0, 1, \dots, v - 1\}$ eine beliebige Retraktion auf $\{0, 1, \dots, v - 1\}$, das heißt
  $$\pi(z) = z \quad \text{für alle } z \in \{0, 1, \dots, v - 1\}$$
  (kanonische Wahl in `scripts/gen_general_tqv.py`: $\pi(z) = z$ für $0 \le z < v$ und $\pi(z) = 0$ für $v \le z < q$).
- Für $t \ge 2$ bezeichne $\mathcal{P}_{t-1}(\mathbb{F}_q)$ den Raum aller Polynome über $\mathbb{F}_q$ vom Grad höchstens $t - 1$:
  $$P(x) = a_0 + a_1 x + \dots + a_{t-3} x^{t-3} + c x^{t-2} + d x^{t-1}, \qquad (a_0, \dots, a_{t-3}, c, d) \in \mathbb{F}_q^t.$$
  *(Für $t = 2$ ist die Liste der unteren Koeffizienten $(a_0, \dots, a_{t-3})$ leer und $P(x) = c + d x$.)*

### Hauptsatz
Für jede Primzahlpotenz $q \ge 2$, jede Stärke $t \in \mathbb{Z}$ mit
$$2 \le t \le q + 2$$
und jede Alphabetgröße $v \in \mathbb{Z}$ mit $2 \le v \le q$ existiert ein explizit und deterministisch konstruierbares Covering Array
$$\mathrm{CA}\!\left(q^t + \binom{v}{2} q^{t - 2};\; t,\; q + 2,\; v\right).$$
Insbesondere gilt für jede Spaltenzahl $k$ mit $t \le k \le q + 2$:
$$\mathrm{CAN}(t, k, v) \le \mathrm{CAN}(t, q + 2, v) \le q^t + \binom{v}{2} q^{t - 2}.$$

*(Hinweis zu den Parametergrenzen: Die Bedingung $t \ge 2$ stellt sicher, dass die beiden führenden Koeffizienten $c = a_{t-2}$ und $d = a_{t-1}$ wohlbestimmt sind. Die Bedingung $t \le q + 2$ ist die notwendige Voraussetzung $k = q + 2 \ge t$ für ein Covering Array der Stärke $t$. Der nichttriviale Bereich mit $k > t$ ist $2 \le t \le q + 1$; der reguläre Bush-Bereich ist $2 \le t \le q$. Der Beweis in Abschnitt 2 deckt ohne Falllücken alle drei Bereiche $q \ge t$, $q = t - 1$ und $q = t - 2$ ab, einschließlich $t = 2$.)*

---

## 2. Konstruktion und vollständiger Deckungsbeweis

### 2.1 Explizite Definition des Arrays $A$

Die $k = q + 2$ Spalten von $A$ werden indiziert durch die disjunkte Vereinigung
$$\mathcal{C} = \mathbb{F}_q \cup \{\infty, *\}.$$
Das Array $A$ besteht aus zwei Blöcken über dem Alphabet $\{0, 1, \dots, v - 1\}$:

1. **Basisblock (Block 1, exakt $q^t$ Zeilen):**
   Für jedes Tupel $(a_0, \dots, a_{t-3}, c, d) \in \mathbb{F}_q^t$ mit zugehörigem Polynom $P(x) = \sum_{j=0}^{t-3} a_j x^j + c x^{t-2} + d x^{t-1}$ enthält Block 1 die Zeile
   $$\mathrm{row}(a_0, \dots, a_{t-3}, c, d) = \Big(\big(\pi(P(x))\big)_{x \in \mathbb{F}_q},\;\; \pi(d),\;\; \pi(\min(c, d))\Big).$$
   Dabei ist $\min(c, d)$ das Minimum bezüglich der festen linearen Ordnung $0 < 1 < \dots < q - 1$ auf $\mathbb{F}_q$. Für $v = q$ ist $\pi = \mathrm{id}$, sodass die ersten $q + 1$ Spalten von Block 1 exakt das orthogonale Array von Bush (1952), $\mathrm{OA}(q^t; t, q + 1, q)$, bilden und die Zusatzspalte $*$ den Wert $\min(c, d)$ trägt.

2. **Zusatzblöcke (Block 2, exakt $\binom{v}{2} q^{t - 2}$ Zeilen):**
   Für jedes geordnete Symbolpaar $(c, d)$ mit
   $$0 \le c < d < v$$
   und für jedes $(a_0, \dots, a_{t-3}) \in \mathbb{F}_q^{t-2}$ mit $P(x) = \sum_{j=0}^{t-3} a_j x^j + c x^{t-2} + d x^{t-1}$ enthält Block 2 die Zeile
   $$\mathrm{row}'(a_0, \dots, a_{t-3}, c, d) = \Big(\big(\pi(P(x))\big)_{x \in \mathbb{F}_q},\;\; c,\;\; d\Big).$$
   *(Für $t = 2$ gibt es $q^0 = 1$ Zeile pro Paar $(c, d)$, nämlich $\big((\pi(c + d x))_{x \in \mathbb{F}_q},\, c,\, d\big)$.)*
   Da $0 \le c < d < v$ gilt, liegen $c$ und $d$ bereits in $\{0, 1, \dots, v - 1\}$. In Block 2 ist die Spalte $\infty$ bewusst vom Leitkoeffizienten $d$ des Polynoms **entkoppelt** ($\mathrm{col}_\infty = c$ statt $d$).

**Zeilenanzahl und Alphabet:**
Block 1 besitzt genau $q^t$ Zeilen, Block 2 genau $\binom{v}{2} q^{t - 2}$ Zeilen, zusammen exakt
$$N(t, q, v) = q^t + \binom{v}{2} q^{t - 2}.$$
Alle Einträge in Block 1 und Block 2 liegen nach Konstruktion von $\pi$ und der Einschränkung $0 \le c < d < v$ in $\{0, 1, \dots, v - 1\}$.

---

### 2.2 Vollständige Fallunterscheidung über alle $t$-Spaltenteilmengen

Sei $T \subset \mathcal{C} = \mathbb{F}_q \cup \{\infty, *\}$ eine beliebige $t$-elementige Spaltenteilmenge und $\mathbf{y} = (y_u)_{u \in T} \in \{0, 1, \dots, v - 1\}^t$ ein beliebiges Ziel-$t$-Tupel auf $T$. Wir zeigen, dass eine Zeile von $A$ existiert, deren Projektion auf $T$ gleich $\mathbf{y}$ ist.

#### Fall 1: $* \notin T$
Dann ist $T \subset \mathbb{F}_q \cup \{\infty\}$ (dieser Fall tritt nur auf, wenn $q + 1 \ge t$, also $q \ge t - 1$).

- **Unterfall 1a: $\infty \notin T$.**
  Dann besteht $T = \{x_1, \dots, x_t\} \subset \mathbb{F}_q$ aus $t$ paarweise verschiedenen Körperelementen (erfordert $q \ge t$). Nach dem Satz über Lagrange-Interpolation über dem Körper $\mathbb{F}_q$ existiert genau ein Polynom $P \in \mathcal{P}_{t-1}(\mathbb{F}_q)$ mit $P(x_i) = y_{x_i}$ für alle $i = 1, \dots, t$. Da $y_{x_i} \in \{0, \dots, v - 1\}$ und $\pi|_{\{0, \dots, v - 1\}} = \mathrm{id}$, folgt $\pi(P(x_i)) = \pi(y_{x_i}) = y_{x_i}$ für alle $i$. Die zugehörige Zeile in **Block 1** überdeckt $\mathbf{y}$ auf $T$.

- **Unterfall 1b: $\infty \in T$.**
  Dann ist $T = \{x_1, \dots, x_{t-1}, \infty\}$ mit $t - 1$ paarweise verschiedenen Punkten $x_1, \dots, x_{t-1} \in \mathbb{F}_q$ (erfordert $q \ge t - 1$). Setze $d = y_\infty \in \{0, \dots, v - 1\}$. Nach Lagrange-Interpolation existiert genau ein Polynom $Q(x) = \sum_{j=0}^{t-2} a_j x^j$ vom Grad $\le t - 2$ mit
  $$Q(x_i) = y_{x_i} - d x_i^{t-1} \qquad (i = 1, \dots, t - 1).$$
  Dann besitzt $P(x) = Q(x) + d x^{t-1} \in \mathcal{P}_{t-1}(\mathbb{F}_q)$ den Leitkoeffizienten $d = y_\infty$ und erfüllt $P(x_i) = y_{x_i}$ für alle $i = 1, \dots, t - 1$. Nach Anwendung von $\pi$ liefert die zugehörige Zeile in **Block 1** die Einträge $\pi(P(x_i)) = y_{x_i}$ und $\pi(d) = y_\infty$, überdeckt also $\mathbf{y}$ auf $T$.

#### Fall 2: $* \in T$ und $\infty \in T$
Dann ist $T = \{x_1, \dots, x_{t-2}, \infty, *\}$ mit $t - 2$ paarweise verschiedenen Punkten $x_1, \dots, x_{t-2} \in \mathbb{F}_q$ (für $t = 2$ ist diese Menge leer; für $t \ge 3$ genügt $q \ge t - 2$). Seien $y_\infty, m \in \{0, \dots, v - 1\}$ die Zielwerte in den Spalten $\infty$ und $*$.

- **Unterfall 2a: $y_\infty \ge m$** (bezüglich der Ordnung $0 < 1 < \dots < q - 1$).
  Wähle $(c, d) = (m, y_\infty)$ in **Block 1**. Dann gilt $\pi(d) = \pi(y_\infty) = y_\infty$ und $\pi(\min(c, d)) = \pi(\min(m, y_\infty)) = \pi(m) = m$.
  - Für $t = 2$ gibt es keine endlichen Spalten in $T$, sodass die Zeile $\mathrm{row}(m, y_\infty)$ in Block 1 das Paar $(y_\infty, m)$ direkt überdeckt.
  - Für $t \ge 3$ existiert nach Lagrange-Interpolation auf den $t - 2$ paarweise verschiedenen Punkten $x_1, \dots, x_{t-2} \in \mathbb{F}_q$ genau ein Polynom $R(x) = \sum_{j=0}^{t-3} a_j x^j$ vom Grad $\le t - 3$ mit
    $$R(x_i) = y_{x_i} - c x_i^{t-2} - d x_i^{t-1} \qquad (i = 1, \dots, t - 2).$$
    Dann erfüllt $P(x) = R(x) + c x^{t-2} + d x^{t-1}$ die Gleichungen $P(x_i) = y_{x_i}$ für alle $i$, und nach Anwendung von $\pi$ überdeckt $\mathrm{row}(a_0, \dots, a_{t-3}, m, y_\infty)$ in **Block 1** das gesamte Tupel $\mathbf{y}$ auf $T$.

- **Unterfall 2b: $y_\infty < m$.**
  Da $y_\infty, m \in \{0, 1, \dots, v - 1\}$, gilt $0 \le y_\infty < m < v$. Somit gehört das Paar $(c, d) = (y_\infty, m)$ exakt zur Indexmenge von **Block 2**, mit $\mathrm{col}_\infty = c = y_\infty$ und $\mathrm{col}_* = d = m$.
  - Für $t = 2$ überdeckt $\mathrm{row}'(y_\infty, m)$ in Block 2 direkt $(y_\infty, m)$.
  - Für $t \ge 3$ liefert Lagrange-Interpolation wie in Unterfall 2a genau ein $R(x) = \sum_{j=0}^{t-3} a_j x^j$ mit $P(x_i) = y_{x_i}$ für $i = 1, \dots, t - 2$. Weil Block 2 für das Paar $(y_\infty, m)$ sämtliche $(a_0, \dots, a_{t-3}) \in \mathbb{F}_q^{t-2}$ durchläuft, überdeckt die Zeile $\mathrm{row}'(a_0, \dots, a_{t-3}, y_\infty, m)$ in **Block 2** das Tupel $\mathbf{y}$ auf $T$.

#### Fall 3: $* \in T$ und $\infty \notin T$
Dann ist $T = \{x_1, \dots, x_{t-1}, *\}$ mit $t - 1$ paarweise verschiedenen Punkten $x_1, \dots, x_{t-1} \in \mathbb{F}_q$ (tritt nur für $q \ge t - 1$ auf). Seien $y_{x_1}, \dots, y_{x_{t-1}}, m \in \{0, \dots, v - 1\}$ die Zielwerte auf $T$.

Nach Lagrange-Interpolation existiert genau ein Polynom
$$Q(x) = \sum_{j=0}^{t-2} q_j x^j \in \mathcal{P}_{t-2}(\mathbb{F}_q)$$
mit $Q(x_i) = y_{x_i}$ für alle $i = 1, \dots, t - 1$. Definiere nun das Polynom vom Grad $\le t - 1$:
$$P(x) = Q(x) + m \prod_{i=1}^{t-1} (x - x_i) \in \mathcal{P}_{t-1}(\mathbb{F}_q).$$
Es besitzt folgende Eigenschaften:
1. **Werte auf den endlichen Spalten:** Für jedes $i \in \{1, \dots, t - 1\}$ verschwindet $\prod_{j=1}^{t-1} (x_i - x_j) = 0$, also $P(x_i) = Q(x_i) = y_{x_i}$ und wegen $y_{x_i} \in \{0, \dots, v - 1\}$ auch $\pi(P(x_i)) = y_{x_i}$.
2. **Führende Koeffizienten $(c, d)$:** Nach dem Satz von Vieta gilt in $\mathbb{F}_q[x]$ (unabhängig von der Charakteristik von $\mathbb{F}_q$):
   $$\prod_{i=1}^{t-1} (x - x_i) = x^{t-1} - S x^{t-2} + (\text{Terme vom Grad } \le t - 3), \qquad S = \sum_{i=1}^{t-1} x_i \in \mathbb{F}_q.$$
   Daher sind die beiden obersten Koeffizienten von $P(x)$ exakt:
   $$d = [x^{t-1}] P(x) = m, \qquad c = [x^{t-2}] P(x) = q_{t-2} - S \cdot m \in \mathbb{F}_q.$$
3. **Überdeckung in Block 1 oder Block 2:** Vergleiche $c \in \{0, \dots, q - 1\}$ und $m \in \{0, \dots, v - 1\}$ in der totalen Ordnung $0 < 1 < \dots < q - 1$:
   - **Unterfall 3a: $c \ge m$.**
     (Dies schließt ausdrücklich den Fall $c \ge v$ ein!) Dann gilt $\min(c, d) = \min(c, m) = m < v$, und daher $\pi(\min(c, d)) = \pi(m) = m$. Da Block 1 alle Polynome in $\mathcal{P}_{t-1}(\mathbb{F}_q)$ enthält, überdeckt die Zeile von $P$ in **Block 1** das Tupel $\mathbf{y}$ auf $T$.
   - **Unterfall 3b: $c < m$.**
     Da $m \in \{0, \dots, v - 1\}$, erzwingt die Ungleichung $c < m$ automatisch
     $$0 \le c < m < v.$$
     Folglich liegt das Paar $(c, d) = (c, m)$ in der Indexmenge von **Block 2**, und da Block 2 für $(c, m)$ alle Koeffiziententupel $(a_0, \dots, a_{t-3}) \in \mathbb{F}_q^{t-2}$ durchläuft, tritt das Polynom $P$ in **Block 2** mit $\mathrm{col}_* = d = m$ auf und überdeckt $\mathbf{y}$ auf $T$.

Damit ist jedes $t$-Tupel $\mathbf{y} \in \{0, \dots, v - 1\}^t$ auf jeder $t$-Spaltenteilmenge $T \subset \mathcal{C}$ abgedeckt. $\square$

---

### 2.3 Warum genügen für $v < q$ genau $\binom{v}{2}$ statt $\binom{q}{2}$ Zusatzblöcke?

Die Einsparung von $\binom{q}{2} - \binom{v}{2}$ Zusatzblöcken à $q^{t - 2}$ Zeilen bei $v < q$ beruht auf der exakten Ausrichtung der Symbolteilmenge $\{0, 1, \dots, v - 1\}$ an das untere Anfangsstück der linearen Ordnung $0 < 1 < \dots < q - 1$ auf $\mathbb{F}_q$:

1. **Basisblock (Block 1) und $\pi$-Retraktion:** Auf allen endlichen Spalten $x \in \mathbb{F}_q$ sowie auf $\mathrm{col}_\infty$ wird jedes Körperelement $z \in \{0, \dots, v - 1\}$ identisch beibehalten ($\pi(z) = z$), während Werte $z \in \{v, \dots, q - 1\}$ auf $\{0, \dots, v - 1\}$ zurückprojiziert werden. Da alle Zielkoordinaten $y_u$ in $\{0, \dots, v - 1\}$ liegen, bleiben sämtliche Interpolationszeilen mit $P(x_i) = y_{x_i}$ nach Anwendung von $\pi$ erhalten.
2. **Spalte $*$ im Basisblock:** Für jedes Zielsymbol $m \in \{0, \dots, v - 1\}$ bilden die Punkte
   $$L_m = \{(c, m) : m \le c < q\} \cup \{(m, d) : m \le d < q\} \subset \mathbb{F}_q^2$$
   einen verschachtelten L-Haken, auf dem $\min(c, d) = m < v$ gilt, sodass $\pi(\min(c, d)) = m$ unverändert bleibt — insbesondere auch für alle Punkte $(c, m)$ mit $c \in \{v, \dots, q - 1\}$!
   - Der horizontale Strahl $\{(c, m) : m \le c < q\}$ deckt in Fall 3 sämtliche $c \ge m$ ab (einschließlich $c \ge v$); nur die $m$ Werte $0 \le c < m$ fehlen auf der horizontalen Geraden $d = m$.
   - Der vertikale Strahl $\{(m, d) : m \le d < v\}$ deckt in Fall 2 sämtliche $y_\infty \in \{m, \dots, v - 1\}$ ab; nur die $m$ Werte $0 \le y_\infty < m$ fehlen.
3. **Exakte Paarung im Block 2:** Weil $m < v$ ist, liegen sämtliche fehlenden Indizes in beiden Fällen strikt unter $v$ ($0 \le c < m < v$ bzw. $0 \le y_\infty < m < v$). Jedes Paar $(c, m)$ mit $0 \le c < m < v$ schließt in Block 2 gleichzeitig den fehlenden Punkt $(c, m)$ auf der Geraden $d = m$ (Fall 3b) **und** den fehlenden $\mathrm{col}_\infty$-Wert $c$ (Fall 2b). Paare $(c, d)$ mit $d \ge v$ (also $c < d$ und $d \in \{v, \dots, q - 1\}$) werden für kein Zielsymbol $m < v$ je benötigt.
4. **Freiheitsgrad im Block $\{v, \dots, q - 1\}^2$:** Im Quadranten $c \ge v, d \ge v$ von Block 1 gilt $\min(c, d) \ge v$; diese Zeilen werden weder in Fall 2 noch in Fall 3 für $\mathrm{col}_*$ benötigt, sodass $\pi(\min(c, d))$ beliebig in $\{0, \dots, v - 1\}$ gewählt werden darf (z. B. $0$), ohne die Deckung zu beeinträchtigen.

*(Bemerkung zur Turnier-Verallgemeinerung: Für $v = q$ und ungerades $q$ funktioniert ebenso jedes reguläre Turnier auf $\mathbb{F}_q$, z. B. das zyklische Turnier aus `scripts/gen_t4_minus3q2.py --variant cyclic`, mit gleicher Zeilenanzahl. Für allgemeines $2 \le v \le q$ ist jedoch die transitive Ordnung $0 < 1 < \dots < q - 1$ mit $\mathrm{col}_*(c, d) = \pi(\min(c, d))$ kanonisch, da sie für jedes $v \le q$ automatisch ohne Umindizierung die exakte Teilmenge $0 \le c < d < v$ abtrennt.)*

---

## 3. Explizite Prüfung aller Randfälle

| Randfall | Parameterbereich | Gültigkeit des Beweises | Strukturelle Einordnung / Besonderheit |
| --- | --- | :---: | --- |
| **Gerades $q = 2^r$ vs. ungerades $q = p^r$** | alle Primzahlpotenzen $q \ge 2$ | **vollständig gültig** | Der Beweis ist vollständig charakteristikunabhängig (in $\mathrm{char}\, 2$ gilt $-S = +S$, die Vieta-Identität $c = q_{t-2} - S m$ bleibt wörtlich gültig). **Ausnahme zur Schärfe bei $t = 3, q = 2^r$:** Dort existiert bereits das Bush-Hyperoval $\mathrm{OA}(q^3; 3, q + 2, q)$ mit nur $q^3$ Zeilen auf $k = q + 2$ Spalten; unsere Formel $q^3 + \binom{v}{2} q$ ist zwar gültig, wird aber vom Hyperoval strikt dominiert. |
| **$t = 2$** | $q \ge 2$, $2 \le v \le q$, $k = q + 2$ | **vollständig gültig** | $q^{t-2} = q^0 = 1$, $N = q^2 + \binom{v}{2}$. Keine unteren Koeffizienten ($R \equiv 0$). Beispiel $q = 2, v = 2$: $\mathrm{CA}(5; 2, 4, 2)$ (exakt optimal, $\mathrm{CAN}(2, 4, 2) = 5$). |
| **$t = 3, 4, 5, 6$** (und allgemeines $t \ge 3$) | $q \ge \max(2, t - 2)$, $2 \le v \le q$ | **vollständig gültig** | Für $t = 4, v = q$ stimmt die Konstruktion mit der transitiven Phase-5E-Bauart (`scripts/gen_t4_minus3q2.py`) zeilen- und byte-identisch überein. |
| **Grenzfall $q = t - 1$** ($k = q + 2 = t + 1$) | z. B. $(3, 4, 2)$, $(4, 5, 3)$, $(5, 6, 4)$, $(6, 7, 5)$ | **vollständig gültig** | Unterfall 1a tritt nicht auf (nur $q = t - 1$ endliche Spalten). In Fall 1b und Fall 3 ist $\{x_1, \dots, x_{t-1}\} = \mathbb{F}_q$ die gesamte Körpermenge; $\prod_{x \in \mathbb{F}_q}(x - x_i) = x^q - x$ hat Koeffizient $-S = -1$ bei $q = 2$ bzw. $0$ bei $q > 2$, sodass $c = q_{t-2} - S m$ exakt bleibt. |
| **Grenzfall $q = t - 2$** ($k = q + 2 = t$) | z. B. $(4, 4, 2)$, $(5, 5, 3)$ | **vollständig gültig** | Einzige $t$-Teilmenge ist $T = \mathcal{C}$ (nur Fall 2). Trivial dominiert durch das vollständige Produkt $v^t \le q^t < N$. |
| **$v = 2$** | beliebiges $q \ge \max(2, t - 2)$ | **vollständig gültig** | $\binom{2}{2} = 1$, genau ein Zusatzblock $(c, d) = (0, 1)$, also $N = q^t + q^{t - 2}$. Für große $q$ gegenüber binären CAs nicht konkurrenzfähig, für $t = 2, q = 2$ exakt ($N = 5$). |
| **$v = q - 1$** | beliebiges $q \ge \max(3, t - 2)$ | **vollständig gültig** | $\binom{q - 1}{2} = \frac{(q - 1)(q - 2)}{2}$, spart $(q - 1) q^{t - 2}$ Zeilen gegenüber $v = q$ bei unveränderter Spaltenzahl $k = q + 2$ (erfasst u. a. Nicht-Primzahlpotenzen wie $v = 6$ via $q = 7$, $v = 10$ via $q = 11$, $v = 12$ via $q = 13$, $v = 14, 15$ via $q = 16$). |

---

## 4. Sachliche Abgrenzung gegen bekannte Konstruktionsformeln

Alle Vergleiche beziehen sich auf die Spaltenzahl $k = q + 2$ (bzw. $k = q + 1$ für Bush) bei einer Primzahlpotenz $q \ge t - 1$; fremde Vorarbeit wird gemäß `RULES.md` Regel 4 zuerst genannt.

| Konstruktion / Quelle | Spaltenzahl $k$ | Zeilenanzahl $N$ | Differenz zu $N(t, q, v) = q^t + \binom{v}{2} q^{t - 2}$ | Einordnung |
| --- | :---: | :---: | :---: | --- |
| **Bush (1952)** (`oa-bush1952`) | $q + 1$ *(bzw. $q + 2$ für $t = 3, q = 2^r$)* | $q^t$ | $+\binom{v}{2} q^{t - 2}$ Zusatzzeilen für Spalte $q + 2$ | Grundlage von Block 1; bei $t = 3, q = 2^r$ liefert das Bush-Hyperoval bereits $k = q + 2$ in $q^t$ Zeilen |
| **CKRS (2010), Lemma 3.3** *(Colbourn–Kéri–Rivas Soriano–Schlage-Puchta)* | $q + 2$ *(für $v = q$)* | $q^t + (q - 1) q^{t - 1} - q^{t - 2} = q^t + (q^2 - q - 1) q^{t - 2}$ | Ersparnis bei $v = q$: $\frac{(q - 2)(q + 1)}{2} q^{t - 2}$ *(strikt $> 0$ für alle $q \ge 3$; gleich bei $q = 2$)* | Reduziert den quadratischen Zusatzterm $(q^2 - q - 1) q^{t - 2}$ auf $\frac{q^2 - q}{2} q^{t - 2}$ (ungefähr halbiert) |
| **Bai (2026), Kor. 5.3** *(ungerades $q$, `polychrome-bai2026`, Pencil-Cover in $\mathrm{AG}(2, q)$)* | $q + 2$ *(für $v = q$)* | $q^t + \frac{q^2 - 1}{2} q^{t - 2}$ | Ersparnis bei $v = q$: $\frac{q - 1}{2} q^{t - 2} = \lfloor q/2 \rfloor q^{t - 2}$ *(strikt $> 0$ für alle ungeraden $q \ge 3$)* | Durch Entkopplung von $\mathrm{col}_\infty$ in Block 2 entfallen alle $(q - 1)/2$ überschüssigen Slices des Pencil-Covers |
| **Bai (2026), Prop. 5.4** *(gerades $q$, `polychrome-bai2026`, Modellgrenze im Ebenenfärbungs-/Kostenmodell)* | $q + 2$ *(für $v = q$)* | $q^t + \frac{q^2}{2} q^{t - 2}$ | Ersparnis bei $v = q$: $\frac{q}{2} q^{t - 2} = \lfloor q/2 \rfloor q^{t - 2}$ *(strikt $> 0$ für alle geraden $q \ge 2$)* | Prop. 5.4 gilt ausschließlich innerhalb von Bais Ebenenfärbungs-/Kostenmodell (keine allgemeine CA-Untergrenze) |
| **Allgemeines $v < q$** *(diese Konstruktion)* | $q + 2$ | $q^t + \binom{v}{2} q^{t - 2}$ | Zusätzliche Ersparnis gegenüber $v = q$: $\left(\binom{q}{2} - \binom{v}{2}\right) q^{t - 2}$ | Nutzt $\pi$-Retraktion und die Anfangssegment-Eigenschaft von $\{0, \dots, v - 1\}$ in der Ordnung $0 < \dots < q - 1$ |

**Abgrenzung der Schranken (Modell vs. allgemeine Covering Arrays):**
- Im eingeschränkten Modell *intaktes Bush-$\mathrm{OA}(q^t)$ auf Spalten $\mathbb{F}_q \cup \{\infty\}$ plus polynomielle $q^{t - 2}$-Zusatz-Slices* erzwingt der Jamison-/Brouwer–Schrijver-Satz ($|B| \ge 2q - 1$ in $\mathrm{AG}(2, q)$) für $v = q$ exakt die modellinterne Untergrenze $E \ge \binom{q}{2}$ Slices (siehe [`docs/T4_MINUS3Q2_ANALYSIS.md`](T4_MINUS3Q2_ANALYSIS.md) §2.2).
- Dies ist jedoch ausdrücklich **keine** allgemeine Untergrenze für $\mathrm{CAN}(t, q + 2, v)$: Andere Konstruktionen (wie OA-Fusion, CPHF, Zyklische/Coset-Konstruktionen oder Post-Optimierung) liefern für zahlreiche kleine oder große Parameterwerte streng kleinere Covering Arrays (z. B. $\mathrm{CAN}(4, 6, 4) \le 340 < 352$, $\mathrm{CAN}(4, 7, 5) \le 825 < 875$, $\mathrm{CAN}(4, 18, 16) \le 83.519 < 96.256$). Maßstab für konkrete Parameterzellen ist stets der systematische Abgleich gegen den aktuellen Tabellenstand (`table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv`) in [`docs/GENERAL_TQV_SCAN.md`](GENERAL_TQV_SCAN.md).
