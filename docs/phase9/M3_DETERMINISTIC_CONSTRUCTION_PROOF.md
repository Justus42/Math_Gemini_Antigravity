# Phase 9 — Beweisnotiz: Deterministische Light+Heavy-3D-Konstruktion im Modell `M_3(R_3)` (`k = q + 3`, `3 <= t <= q`)

- **Datum:** 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, Basis `0d6e9f5`).
- **Bezugscode:** [`scripts/phase9_m3_lift.py`](../../scripts/phase9_m3_lift.py) (`FieldOps`, `check_m3`, `lift_rows`), [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py) (`build_m3_for_params`, `construct_best`, `check_sufficient_full_bg3`).
- **Status & Rolle:** Erzeugernotiz (**Belegart: Argument + rechnerische Verifikation für endliche $q$**), aufbereitet für die unabhängige Prüfung durch Claude und ein unbeteiligtes Drittmodell nach `RULES.md` Regel 2d. **Kein formaler Beweis, keine Außenwirkung, Literaturprüfung nach Regel 2c steht aus.**
- **Ehrlichkeitshinweis zu `[OFFEN / PRUEFPUNKT]`:** Jeder Beweisschritt, der über endliche Zählung hinaus noch eine analytische Schranke oder Randfallverschärfung benötigt, ist im Text explizit als `[OFFEN / PRUEFPUNKT]` gekennzeichnet. Insbesondere wird die **tatsächliche** asymptotische Konstante dieser Bauart ($\frac{19}{10} q^3$, nicht $\frac{49}{27} q^3$) sauber gegen die LP-Schranken $\frac{46}{27} q^3$ und $\frac{49}{27} q^3$ abgegrenzt (§2.4, §4).

---

## 1. Definitionen & Übersetzungssatz (`M_3(R_3)` $\implies$ `CA(N; t, q + 3, q)`)

### 1.1 Modell `M_3(R_3)` und Nebenklassen-Lift

Sei $q$ eine Primzahlpotenz, $\mathbb{F}_q$ der endliche Körper der Ordnung $q$ und $t \in \mathbb{Z}$ mit $3 \le t \le q$. Wir indizieren die $k = q + 3$ Spalten durch $\mathbb{F}_q \sqcup \{a, b, c\}$.

- **Kern:**
  $$K_t^{(3)} := \Big\{\big((g(x))_{x \in \mathbb{F}_q},\, 0,\, 0,\, 0\big) : g \in \mathbb{F}_q[X],\; \deg g \le t - 4\Big\} \subset \mathbb{F}_q^{q+3}$$
  (mit $K_3^{(3)} = \{0\}$ für $t = 3$; stets $|K_t^{(3)}| = q^{t-3}$).
- **Vertreterliste:** Eine endliche Menge $R_3 \subset \mathbb{F}_q^6$ paarweise verschiedener 6-Tupel $(c_0, c_1, c_2, a, b, c)$ (geometrisch: Punkt $(x, y, z) = (c_0, c_1, c_2) \in \mathrm{AG}(3, q)$ versehen mit Symboltripel $(a, b, c) \in \mathbb{F}_q^3$).
- **Lift $M_3^{(t)}(R_3)$:** Für jedes $(c_0, c_1, c_2, a, b, c) \in R_3$ und jedes $g \in \mathbb{F}_q[X]$ mit $\deg g \le t - 4$ bilde das Polynom
  $$f(X) := g(X) + c_0 X^{t-3} + c_1 X^{t-2} + c_2 X^{t-1}$$
  und die Zeile $((f(x))_{x \in \mathbb{F}_q}, a, b, c) \in \mathbb{F}_q^{q+3}$. Das resultierende Array hat
  $$N = |R_3| \cdot q^{t-3} \text{ Zeilen}, \qquad k = q + 3 \text{ Spalten}, \qquad v = q \text{ Symbole}.$$

### 1.2 Exakte Charakterisierung (`check_m3 = 0`)

Für jede nichtleere Teilmenge $S \subset \mathbb{F}_q$ bezeichne $e_1(S) = \sum_{x \in S} x$ und $e_2(S) = \sum_{\{x, y\} \subset S} x y$ die erste bzw. zweite elementarsymmetrische Funktion (mit $e_1(\emptyset) = e_2(\emptyset) = 0$). Definiere die Richtungs- und Normalenmengen:
- **Modus `tspec` (festes $t$, $3 \le t \le q$):**
  $$D_1^{(t)} := \Big\{(e_2(S),\, -e_1(S)) : S \in \binom{\mathbb{F}_q}{t - 1}\Big\}, \qquad N_2^{(t)} := \Big\{(e_1(U),\, e_1(U)^2 - e_2(U)) : U \in \binom{\mathbb{F}_q}{t - 2}\Big\}.$$
- **Modus `full-bg3` ($t$-unabhängig für alle $3 \le t \le q$):**
  $$D_1^{\mathrm{full}} := \mathbb{F}_q^2, \qquad N_2^{\mathrm{full}} := \mathbb{F}_q^2.$$

**Satz 1 (Übersetzungssatz — Argument, geprüft in Gate 0 und an Dual-Verify-Arrays; `[OFFEN / PRUEFPUNKT 4]` für Regel-2d-Prüfung).**
*Das geliftete Array $M_3^{(t)}(R_3)$ ist genau dann ein $\mathrm{CA}(|R_3| q^{t-3}; t, q + 3, q)$, wenn $R_3$ die folgenden vier Bedingungen erfüllt (`check_m3(tspec, t) = 0`):*
1. **(Typ 0)** $\{(c_0, c_1, c_2) : (c_0, c_1, c_2, a, b, c) \in R_3\} = \mathbb{F}_q^3$.
2. **(Typ 1)** Für jedes $u \in \{a, b, c\}$, jedes $s \in \mathbb{F}_q$ und jedes $(v, w) \in D_1^{(t)}$ gilt:
   $$\big|\{(c_0 - v c_2,\, c_1 - w c_2) : (c_0, c_1, c_2, a, b, c) \in R_3,\; u = s\}\big| = q^2.$$
3. **(Typ 2)** Für jedes Paar $\{u_1, u_2\} \in \{\{a,b\}, \{a,c\}, \{b,c\}\}$, jedes $(s_1, s_2) \in \mathbb{F}_q^2$ und jedes $(\alpha, \beta) \in N_2^{(t)}$ gilt:
   $$\big|\{c_0 + \alpha c_1 + \beta c_2 : (c_0, c_1, c_2, a, b, c) \in R_3,\; (u_1, u_2) = (s_1, s_2)\}\big| = q.$$
4. **(Typ 3)** $\{(a, b, c) : (c_0, c_1, c_2, a, b, c) \in R_3\} = \mathbb{F}_q^3$.

*Insbesondere impliziert `check_m3(full-bg3) = 0` (mit $D_1^{\mathrm{full}} = N_2^{\mathrm{full}} = \mathbb{F}_q^2$), dass $M_3^{(t)}(R_3)$ für **alle** Stärken $3 \le t \le q$ zugleich ein gültiges $\mathrm{CA}(|R_3| q^{t-3}; t, q+3, q)$ ist.*

**Beweis (Polynomreduktion modulo Knotenpolynom):**
Sei $C \subset \mathbb{F}_q \sqcup \{a, b, c\}$ eine beliebige $t$-elementige Spaltenmenge und $j := |C \cap \{a, b, c\}| \in \{0, 1, 2, 3\}$. Setze $S := C \cap \mathbb{F}_q$ ($|S| = t - j$). Für jede feste Nebenklasse $(c_0, c_1, c_2, a, b, c) \in R_3$ variiert $g$ frei über alle $q^{t-3}$ Polynome vom Grad $\le t - 4$.
- **$j = 0$ ($|S| = t$):** Die Auswertungsabbildung $\mathbb{F}_q[X]_{< t} \to \mathbb{F}_q^S$, $f \mapsto (f(x))_{x \in S}$, ist per Lagrange-Interpolation bijektiv. Da $g$ den Unterraum $\mathbb{F}_q[X]_{< t-3}$ durchläuft, ist die Auswertung surjektiv genau dann, wenn $(c_0, c_1, c_2)$ alle $q^3$ Tupel in $\mathbb{F}_q^3$ durchläuft (Typ 0).
- **$j = 1$ ($|S| = t - 1$, $C = S \cup \{u\}$):** Das normierte Knotenpolynom lautet
  $$p_S(X) := \prod_{x \in S} (X - x) = X^{t-1} - e_1(S) X^{t-2} + e_2(S) X^{t-3} - \dots \in \mathbb{F}_q[X].$$
  Modulo $p_S(X)$ gilt $X^{t-1} \equiv e_1(S) X^{t-2} - e_2(S) X^{t-3} + r_S(X)$ mit $\deg r_S \le t - 4$. Damit reduziert sich $f(X)$ modulo $p_S(X)$ zu
  $$f(X) \equiv \big(g(X) + c_2 r_S(X)\big) + \big(c_0 - e_2(S) c_2\big) X^{t-3} + \big(c_1 + e_1(S) c_2\big) X^{t-2} \pmod{p_S(X)}.$$
  Da $\tilde{g} := g + c_2 r_S$ für festes $c_2$ bijektiv alle Polynome vom Grad $\le t - 4$ durchläuft und die Auswertung auf $S$ ein Isomorphismus $\mathbb{F}_q[X]/(p_S) \xrightarrow{\sim} \mathbb{F}_q^S$ ist, wird bei festem $u = s$ ganz $\mathbb{F}_q^S$ genau dann getroffen, wenn $(c_0 - v c_2, c_1 - w c_2)$ mit $(v, w) = (e_2(S), -e_1(S))$ ganz $\mathbb{F}_q^2$ durchläuft (Typ 1). *(Hinweis zu $t = 3$: Hier ist $|S| = 2$, $p_S(X) = X^2 - e_1(S) X + e_2(S)$, $g \equiv 0$, $r_S \equiv 0$, und die Formel gilt exakt ohne Grad-Anomalie.)*
- **$j = 2$ ($|S| = t - 2$, $C = U \cup \{u_1, u_2\}$):** Sei $p_U(X) := \prod_{x \in U} (X - x) = X^{t-2} - e_1(U) X^{t-3} + e_2(U) X^{t-4} - \dots$ (für $t = 3$ ist $|U| = 1$, $p_U(X) = X - x_0$, $e_1(U) = x_0$, $e_2(U) = 0$). Modulo $p_U(X)$ gilt:
  $$X^{t-2} \equiv e_1(U) X^{t-3} - e_2(U) X^{t-4} + \dots \equiv e_1(U) X^{t-3} + \tilde{r}_1(X),$$
  $$X^{t-1} = X \cdot X^{t-2} \equiv e_1(U) X^{t-2} - e_2(U) X^{t-3} + \tilde{r}_2(X) \equiv \big(e_1(U)^2 - e_2(U)\big) X^{t-3} + \tilde{r}_3(X),$$
  mit $\deg \tilde{r}_i \le t - 4$. Setze $\alpha := e_1(U)$ und $\beta := e_1(U)^2 - e_2(U)$. Dann ist
  $$f(X) \equiv \tilde{g}(X) + (c_0 + \alpha c_1 + \beta c_2) X^{t-3} \pmod{p_U(X)},$$
  wobei $\tilde{g}$ ganz $\mathbb{F}_q[X]_{< t-3}$ durchläuft. Per Lagrange-Interpolation auf $U$ deckt die Faser $(u_1, u_2) = (s_1, s_2)$ ganz $\mathbb{F}_q^U$ genau dann, wenn $c_0 + \alpha c_1 + \beta c_2$ alle $q$ Werte in $\mathbb{F}_q$ annimmt (Typ 2).
- **$j = 3$ ($|S| = t - 3$, $C = W \cup \{a, b, c\}$):** Für festes $(c_0, c_1, c_2, a, b, c) \in R_3$ läuft $g|_W$ bijektiv über ganz $\mathbb{F}_q^W$ (für $t = 3$ ist $W = \emptyset$ trivial). Also deckt $C$ ganz $\mathbb{F}_q^t$ genau dann, wenn jedes $(a, b, c) \in \mathbb{F}_q^3$ in $R_3$ vorkommt (Typ 3). $\square$

### 1.3 Körperunabhängige hinreichende Bedingung (`suff = 0`)

**Lemma 1 (`suff = 0` $\implies$ `check_m3(full-bg3) = 0`).**
*Erfüllt $R_3 \subset \mathbb{F}_q^6$ (`0` Duplikate):*
- *(S0) Alle $q^3$ Punkte $(c_0, c_1, c_2) \in \mathbb{F}_q^3$ treten auf;*
- *(S1) Jedes Symbol $s \in \mathbb{F}_q$ in jeder Koordinate $u \in \{a, b, c\}$ besitzt eine volle horizontale Ebene $\{(x, y, z_0) : x, y \in \mathbb{F}_q\}$ für mindestens ein $z_0 \in \mathbb{F}_q$;*
- *(S2) Jedes Symbolpaar $(s_1, s_2) \in \mathbb{F}_q^2$ in jedem Paar $\{a,b\}, \{a,c\}, \{b,c\}$ besitzt eine volle $x$-Gerade $\{(x, y_0, z_0) : x \in \mathbb{F}_q\}$ für mindestens ein $(y_0, z_0) \in \mathbb{F}_q^2$;*
- *(S3) Alle $q^3$ Symboltripel $(a, b, c) \in \mathbb{F}_q^3$ treten auf;*

*so gilt `check_m3(full-bg3) = 0` (für **jeden** Körper $\mathbb{F}_q$ der Ordnung $q$, unabhängig von seiner Multiplikationstafel).*

**Beweis:** (S0) und (S3) sind identisch zu Typ 0 und Typ 3. Für (S1) und beliebiges $(v, w) \in \mathbb{F}_q^2$ bildet $(x, y) \mapsto (x - v z_0, y - w z_0)$ bei festem $z_0$ die Menge $\mathbb{F}_q^2$ durch reine Translation bijektiv auf $\mathbb{F}_q^2$ ab $\implies$ Typ 1 erfüllt. Für (S2) und beliebiges $(\alpha, \beta) \in \mathbb{F}_q^2$ bildet $x \mapsto x + \alpha y_0 + \beta z_0$ bei festem $(y_0, z_0)$ die Menge $\mathbb{F}_q$ bijektiv auf $\mathbb{F}_q$ ab $\implies$ Typ 2 erfüllt. $\square$

---

## 2. Explizite deterministische Light+Heavy-Konstruktion (`scripts/phase9_m3_construct.py`)

Identifiziere die Symbolmenge $\mathbb{F}_q$ mit $\{0, 1, \dots, q - 1\}$ (für die kombinatorische Symbolzuweisung wird ausschließlich $\mathbb{Z}_q$-Arithmetik verwendet; nach Lemma 1 ist die Konstruktion für jede Primzahlpotenz $q \ge 5$ gültig).

### 2.1 Schritt 0: Balancierte Light/Heavy-Ebenenpartition

Wähle die balancierten Light-Größen
$$k_a = \left\lfloor \frac{q + 1}{3} \right\rfloor, \qquad k_b = \left\lfloor \frac{q}{3} \right\rfloor, \qquad k_c = \left\lfloor \frac{q - 1}{3} \right\rfloor \qquad (k_a + k_b + k_c = q - 1),$$
und einen zyklischen Versatz $c_{\mathrm{shift}} \in \{0, \lfloor q/3 \rfloor, \lfloor 2q/3 \rfloor\}$:
$$A_L = \{0, \dots, k_a - 1\}, \quad B_L = \{0, \dots, k_b - 1\}, \quad C_L = \{(c_{\mathrm{shift}} + i) \bmod q : 0 \le i < k_c\},$$
sowie die komplementären Heavy-Mengen $A_H = \mathbb{Z}_q \setminus A_L$, $B_H = \mathbb{Z}_q \setminus B_L$, $C_H = \mathbb{Z}_q \setminus C_L$ (je Größe $\approx \frac{2}{3} q$).
Die $q - 1$ leichten horizontalen Ebenen $z \in \{0, \dots, q - 2\}$ werden bijektiv den Elementen von $A_L \sqcup B_L \sqcup C_L$ zugeordnet; jede leichte Ebene $z$ besitzt $q$ disjunkte $x$-Geraden-Slots $(y, z)$ ($y = 0, \dots, q - 1$). Die einzige verbleibende horizontale Ebene $z^* := q - 1$ ist die **schwere Ebene** für alle Symbole aus $A_H, B_H, C_H$.

### 2.2 Schritt 1: Zyklisches Differenzband `3P` + komplementäre `1P`-Geraden + Resttripel `U`

Wähle eine Bandbreite $r \in \{1, \dots, q - 1\}$ und setze $e := q - r$ (Komplementbreite) sowie $D := \{0, 1, \dots, r - 1\} \subset \mathbb{Z}_q$, $E := \mathbb{Z}_q \setminus D = \{r, \dots, q - 1\}$. Definiere:
1. **`3P`-$x$-Geraden (partielles lateinisches Quadrat $T$):**
   $$T := \big\{(a, b, (-a - b) \bmod q) : a, b \in \mathbb{Z}_q,\; (a - b) \bmod q \in D\big\}, \qquad |T| = r q = (q - e) q.$$
   Jede `3P`-Gerade $(a, b, c) \in T$ liefert bei Platzierung auf $(y, z)$ die $q$ Punkte $\{(x, y, z, a, b, c) : x \in \mathbb{Z}_q\}$.
   Ihre drei Paarprojektionen sind exakt:
   $$\mathrm{proj}_{ab}(T) = \{(a, b) : (a - b) \bmod q \in D\}, \quad \mathrm{proj}_{ac}(T) = \{(a, c) : (2a + c) \bmod q \in D\},$$
   $$\mathrm{proj}_{bc}(T) = \{(b, c) : (-2b - c) \bmod q \in D\},$$
   jeweils von Größe $r q$ (da zu jedem $(a, c)$ genau ein $b \equiv -a - c \pmod q$ existiert und dann $a - b \equiv 2a + c$; analog $-2b - c$; gültig **auch für gerades $q$**, da nie durch $2$ dividiert wird).
2. **`1P`-$x$-Geraden (komplementäre Paare):**
   Für jedes nicht von $T$ gedeckte Paar $(a, b) \notin \mathrm{proj}_{ab}(T)$ bilde eine Gerade `1P_ab(a, b)` (bei Platzierung auf $(y, z)$ mit einer Bijektion $\pi: \mathbb{Z}_q \to \mathbb{Z}_q$ die $q$ Punkte $\{(x, y, z, a, b, \pi(x)) : x \in \mathbb{Z}_q\}$); analog `1P_ac(a, c)` für $(a, c) \notin \mathrm{proj}_{ac}(T)$ und `1P_bc(b, c)` für $(b, c) \notin \mathrm{proj}_{bc}(T)$. Insgesamt:
   $$n_{\mathrm{1P}} = 3 (q - r) q = 3 e q, \qquad n_{\mathrm{lines}} = n_{\mathrm{3P}} + n_{\mathrm{1P}} = (3 q - 2 r) q = (q + 2 e) q.$$
3. **Verbleibende Typ-3-Tripel $U$:**
   $$U := \big\{(a, b, c) \in \mathbb{Z}_q^3 \setminus T : (a, b) \in \mathrm{proj}_{ab}(T),\; (a, c) \in \mathrm{proj}_{ac}(T),\; (b, c) \in \mathrm{proj}_{bc}(T)\big\}.$$

### 2.3 Schritte 2 & 3: Deterministische Platzierung auf leichten Ebenen und schwerer Ebene $z^*$

- **Schritt 2 (Light-Plane-Matching):** Ein deterministisches maximales bipartites Matching weist den $(q - 1) q$ Slots $(y, z)$ ($z \in \{0, \dots, q - 2\}$) kompatible `3P`/`1P`-Geraden zu (eine Gerade ist kompatibel zu Ebene $z$ mit Besitzer $(u, s)$, falls ihre feste $u$-Koordinate gleich $s$ ist; Priorisierung nach fallendem Light-Grad und `3P` vor `1P`). Bleiben `unm` Slots ungematcht, wird jeder ungematchte Slot $(y, z)$ mit bis zu $q$ noch unbenutzten Tripeln aus $U$ befüllt, deren $u$-Koordinate gleich $s$ ist; nur falls weniger als $q$ solche $U$-Tripel verbleiben, wird bis $q$ mit deterministischen Füllpunkten (`pad_light`) aufgefüllt. Auf den leichten Ebenen erhalten alle `1P`-Geraden die Identität $\pi(x) = x$.
- **Schritt 3 (Heavy-Plane-Platzierung auf $z^* = q - 1$):**
  1. Alle nicht auf leichten Ebenen platzierten `3P`-Geraden werden deterministisch auf Zeilen $y \in \{0, \dots, q - 1\}$ von $z^*$ gelegt, die maximalen neuen Heavy-Gewinn (fehlende $(x, y)$-Zellen für $A_H, B_H, C_H$) liefern.
  2. Alle verbleibenden `1P`-Geraden werden deterministisch auf eine Zeile $y$ mit einer über `_max_bijection_gain` (maximales bipartites Matching auf `valid_adj`/`gain_adj`) gewählten kollisionsfreien Bijektion $\pi: \mathbb{Z}_q \to \mathbb{Z}_q$ gelegt, die den Heavy-Gewinn maximiert.
  3. Alle noch nicht verbrauchten Tripel aus $U$ werden deterministisch auf defizitäre $(x, y)$-Zellen von $z^*$ verteilt (gefolgt von bis zu 5 deterministischen 1-Punkt-Relokationspässen über `unc_pos`).
  4. Jedes danach noch fehlende Heavy-Symbol in Zelle $(x, y)$ von $z^*$ wird punktuell aufgefüllt (`exh = extra_heavy` Zusatzvertreter).

### 2.4 Exakte Zählformel für `|U|`, `m_raw(q, e)` und `|R_3|` (geschlossen + Restterme)

**Satz 2 (Exakte Zählung von $U$ und $m_{\mathrm{raw}}$ — vollständig algebraisch bewiesen, zusätzlich geprüft für alle $q \in [5..49]$ und $1 \le e \le \lfloor (q-1)/2 \rfloor$ ohne Abweichung).**
*Sei $q \ge 3$ eine beliebige ganze Zahl und $1 \le e = q - r \le \lfloor (q - 1)/2 \rfloor$. Dann gilt:*
1. **Bijektion für $U$:** Die Abbildung
   $$\Phi: \mathbb{Z}_q \times \{(d, s) \in D^2 : s \neq d,\; (2d - s) \bmod q \in D\} \longrightarrow U, \qquad (a, d, s) \longmapsto \big(a,\; (a - d) \bmod q,\; (s - 2a) \bmod q\big)$$
   ist eine Bijektion (auch für gerades $q$, ohne Division durch $2$). Somit gilt $|U| = q \cdot \mathrm{AP3}(q, r)$ mit $\mathrm{AP3}(q, r) := \#\{(d, s) \in D^2 : s \neq d,\; (2d - s) \bmod q \in D\}$.
2. **Geschlossene Formel für $\mathrm{AP3}(q, r)$:**
   $$\mathrm{AP3}(q, q - e) = q^2 - 3 q e + \kappa(q, e) - q + e, \qquad \kappa(q, e) := \begin{cases} \left\lfloor \dfrac{5 e^2}{2} \right\rfloor = \dfrac{5 e^2 - (e \bmod 2)}{2} & (q \text{ ungerade}), \\[8pt] \left\lceil \dfrac{5 e^2}{2} \right\rceil = \dfrac{5 e^2 + (e \bmod 2)}{2} & (q \text{ gerade}). \end{cases}$$
3. **Geschlossene Formel für die Rohgröße $m_{\mathrm{raw}}(q, e) := q \cdot n_{\mathrm{lines}} + |U|$:**
   $$m_{\mathrm{raw}}(q, e) = 2 q^3 - q^2 e + \kappa(q, e) \cdot q - q^2 + q e.$$
4. **Exakte Zerlegung der tatsächlichen Listengröße $|R_3| = m_{\mathrm{det}}(q)$:**
   $$|R_3| = m_{\mathrm{raw}}(q, e) + \mathrm{pad}_{\mathrm{light}}(q, r, c_{\mathrm{shift}}) + \mathrm{exh}(q, r, c_{\mathrm{shift}}).$$

**Beweis von Satz 2:**
1. *(Bijektion)* Setze $d_1 := (a - b) \bmod q$, $d_2 := (2a + c) \bmod q$, $d_3 := (-2b - c) \bmod q$. Dann gilt identisch $d_2 + d_3 \equiv 2(a - b) \equiv 2 d_1 \pmod q$, also $d_3 \equiv 2 d_1 - d_2 \pmod q$. Zudem ist $(a, b, c) \in T \iff a + b + c \equiv 0 \iff 2a + c \equiv a - b \iff d_2 = d_1$. Zu gegebenem $(a, d_1, d_2)$ mit $d_1, d_2 \in D$, $d_2 \neq d_1$, $(2 d_1 - d_2) \bmod q \in D$ sind $b \equiv a - d_1$ und $c \equiv d_2 - 2a \pmod q$ eindeutig bestimmt und erfüllen automatisch $-2b - c \equiv 2 d_1 - d_2 \in D$.
2. *(Inklusion-Exklusion)* Setze $N_{\mathrm{all}}(D) := \#\{(d, s) \in D^2 : (2d - s) \bmod q \in D\} = \mathrm{AP3}(q, r) + r$. Mit $1_D = 1 - 1_E$ folgt:
   $$N_{\mathrm{all}}(D) = \sum_{d, s \in \mathbb{Z}_q} (1 - 1_E(d))(1 - 1_E(s))(1 - 1_E(2d - s))$$
   $$= q^2 - 3 q e + \underbrace{\sum 1_E(d) 1_E(s)}_{e^2} + \underbrace{\sum 1_E(d) 1_E(2d - s)}_{e^2} + \underbrace{\sum 1_E(s) 1_E(2d - s)}_{S_{\mathrm{par}}} - N_{\mathrm{all}}(E).$$
   - Für ungerades $q$ ist $d \mapsto (2d - s) \bmod q$ bei festem $s$ eine Bijektion $\mathbb{Z}_q \to \mathbb{Z}_q$, also $S_{\mathrm{par}} = e^2$.
   - Für gerades $q$ gilt $2d - s \equiv s \pmod 2$; jedes Paar $(s, t) \in E^2$ gleicher Parität besitzt genau zwei Urbilder $d \in \mathbb{Z}_q$, also $S_{\mathrm{par}} = 2(e_{\mathrm{even}}^2 + e_{\mathrm{odd}}^2) = e^2 + (e \bmod 2)$ (da $E$ ein zusammenhängendes Intervall der Länge $e$ ist, gilt $|e_{\mathrm{even}} - e_{\mathrm{odd}}| = e \bmod 2$).
   - Wegen $2e \le q - 1$ gilt für alle $d, s \in \{0, \dots, e - 1\}$ die strikte Nicht-Überlauf-Schranke $-(e - 1) > -q + e - 1$ und $2(e - 1) < q$. Daher ist $N_{\mathrm{all}}(E) = \#\{(d, s) \in [0, e-1]^2 : 0 \le 2d - s \le e - 1\}$. Summieren über $d = 0, \dots, e - 1$ liefert für $e = 2h$: $\sum_{d=0}^{h-1}(2d+1) + \sum_{d=h}^{2h-1}(4h-1-2d) = 2h^2 = e^2/2$, und für $e = 2h+1$: $(h+1)^2 + h^2 = (e^2 + 1)/2$; zusammen $N_{\mathrm{all}}(E) = \frac{e^2 + (e \bmod 2)}{2}$.
   - Einsetzen in $\mathrm{AP3}(q, r) = N_{\mathrm{all}}(D) - (q - e)$ ergibt:
     $$\mathrm{AP3}(q, q - e) = q^2 - 3 q e + \left(3 e^2 + \mathbf{1}_{2 \mid q}(e \bmod 2) - \frac{e^2 + (e \bmod 2)}{2}\right) - q + e = q^2 - 3 q e + \kappa(q, e) - q + e.$$
3. *(Rohgröße)* $q \cdot n_{\mathrm{lines}} + q \cdot \mathrm{AP3}(q, q-e) = (q^3 + 2 q^2 e) + q(q^2 - 3 q e + \kappa(q, e) - q + e) = 2 q^3 - q^2 e + \kappa(q, e) q - q^2 + q e$.
4. *(Gesamtzahl $|R_3|$)* Jede der $n_{\mathrm{lines}}$ Geraden wird genau einmal (entweder in Schritt 2 oder Schritt 3) mit $q$ Punkten platziert; jedes Tripel in $U$ wird genau einmal (entweder in einem ungematchten Light-Slot oder auf $z^*$) platziert; zusätzlich werden genau $\mathrm{pad}_{\mathrm{light}}$ Füllpunkte in ungematchten Light-Slots und $\mathrm{exh}$ Zusatzpunkte auf $z^*$ erzeugt. $\square$

**Asymptotik & ehrlicher Abgleich gegen $\frac{19}{10} q^3$, $\frac{49}{27} q^3$ und $2 q^3 - q^2$:**
Minimiere $2 q^3 - q^2 e + \frac{5}{2} q e^2 - q^2 + q e$ über $e \in \mathbb{Z}$. Der reelle Minimierer liegt bei $e = \frac{q - 1}{5}$; mit $e^* = \left\lfloor \frac{q + 1}{5} \right\rfloor = \frac{q}{5} + \delta$ ($|\delta| \le \frac{1}{2}$) gilt:
$$m_{\mathrm{raw}}(q, e^*) = \frac{19}{10} q^3 - \frac{4}{5} q^2 + \left(\frac{5}{2} \delta^2 + \delta \pm \frac{1}{2}\right) q = \mathbf{1{,}90\, q^3 - 0{,}80\, q^2 + O(q)}.$$
**Wichtige Klarstellung (Ehrlichkeitspflicht):**
- Die führende asymptotische Konstante dieser zyklischen Differenzband-Bauart ist **$\frac{19}{10} = 1{,}90$**, **nicht** $\frac{49}{27} \approx 1{,}8148$! Gegen die elliptische Schranke $2 q^3 - q^2$ spart sie asymptotisch exakt $\frac{1}{10} q^3 - \frac{1}{5} q^2 + O(q)$ Vertreter (ca. $-5{,}0\,\%$).
- Gegenüber $\frac{49}{27} q^3$ lautet die Differenz:
  $$m_{\mathrm{raw}}(q, e^*) - \frac{49}{27} q^3 = +\frac{23}{270} q^3 - \frac{4}{5} q^2 + O(q) \approx +0{,}0852\, q^3 - 0{,}80\, q^2.$$
  Nur für kleine $q \le 9$ drückt der quadratische Term $-\frac{4}{5} q^2$ die Rohsumme auf oder unter $\frac{49}{27} q^3$ (insbesondere bei $q = 9, e = 2$: $m_{\mathrm{raw}}(9, 2) = 1323 = \frac{49}{27} \cdot 9^3$ exakt!). Ab $q = 11$ liegt $m_{\mathrm{det}}(q) / q^3$ strikt über $\frac{49}{27}$ und steigt monoton gegen $\frac{19}{10} = 1{,}90$:

| $q$ | $r^*$ | $r_{\mathrm{det}}$ | $c_{\mathrm{shift}}$ | $m_{\mathrm{raw}}(r_{\mathrm{det}})$ | `unm` | `pad_light` | `exh` | **`m_det`** | `m_det / q^3` | `ell = 2q^3 - q^2` | Gewinn (`ell - m_det`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `5` | `4` | `4` | `1` | `215` | `1` | `0` | `12` | `227` | `1,81600` | `225` | `-2` |
| `7` | `6` | `6` | `0` | `609` | `5` | `0` | `22` | **`631`** | `1,83965` | `637` | `+6` |
| `8` | `6` | `7` | `0` | `928` | `8` | `2` | `15` | **`945`** | `1,84570` | `960` | `+15` |
| `9` | `7` | `8` | `6` | `1.323` | `9` | `0` | `9` | **`1.332`** | `1,82716` | `1.377` | `+45` |
| `11` | `9` | `10` | `7` | `2.453` | `16` | `0` | `1` | **`2.454`** | `1,84373` | `2.541` | `+87` |
| `13` | `10` | `11` | `4` | `4.043` | `23` | `0` | `45` | **`4.088`** | `1,86072` | `4.225` | `+137` |
| `16` | `13` | `14` | `10` | `7.616` | `31` | `0` | `37` | **`7.653`** | `1,86841` | `7.936` | `+283` |
| `17` | `14` | `15` | `11` | `9.163` | `37` | `0` | `19` | **`9.182`** | `1,86892` | `9.537` | `+355` |
| `19` | `15` | `16` | `12` | `12.749` | `36` | `0` | `179` | **`12.928`** | `1,88482` | `13.357` | `+429` |
| `23` | `18` | `19` | `15` | `22.701` | `48` | `0` | `277` | **`22.978`** | `1,88855` | `23.805` | `+827` |
| `25` | `20` | `21` | `16` | `29.225` | `65` | `0` | `393` | **`29.618`** | `1,89555` | `30.625` | `+1.007` |

*(Alle `11` Zeilen haben `suff = 0`; zusätzlich wurde `check_m3(full-bg3) = 0` für alle `8` Primzahlpotenzen $q \in \{5, 7, 8, 9, 11, 13, 16, 17\}$ direkt geprüft.)*

---

## 3. Beweis der Vollabdeckung (`suff = 0`) & Markierung aller `[OFFEN / PRUEFPUNKT]`-Stellen

**Satz 3 (Vollabdeckung `suff = 0` für alle Primzahlpotenzen $q \ge 5$ und $1 \le e < (q - 2)/2$).**
*Für jede Primzahlpotenz $q \ge 5$ und jedes $e = q - r \ge 1$ mit $2 e < q - 2$ (insbesondere für $e^* = \lfloor (q + 1)/5 \rfloor$ ab $q \ge 7$ sowie für $e = 1$ ab $q \ge 5$) terminiert `build_m3_for_params(q, q - e, c_shift)` ohne Fehler und liefert eine duplikatfreie Menge $R_3 \subset \mathbb{F}_q^6$ mit `suff = 0` (also nach Lemma 1 `check_m3(full-bg3) = 0` und nach Satz 1 gültige `CA(|R_3| q^{t-3}; t, q + 3, q)` für alle $3 \le t \le q$).*

**Schrittweiser Beweis:**
1. **Keine Kollisionen auf den leichten Ebenen (`z = 0..q - 2`):** Jeder Punkt $(x, y, z)$ mit $z \in \{0, \dots, q - 2\}$ wird in Schritt 2 genau einmal emittiert. Insbesondere entstehen auf $z < q - 1$ keine doppelten 6-Tupel, alle $(q - 1) q^2$ Punkte $(x, y, z)$ sind gedeckt, und jedes Light-Symbol $s \in A_L \sqcup B_L \sqcup C_L$ besitzt seine volle horizontale Ebene $z = \mathrm{plane}(u, s)$.
2. **Kollisionsfreie Platzierung aller restlichen `3P`-Geraden auf $z^*$:** Da Schritt 3 die `3P`-Geraden **zuerst** auf $z^*$ platziert (Zeilen 312, 353–373) und alle `3P`-Geraden paarweise verschiedene Tripel $(a, b, c) \in T$ tragen, ist für jede `3P`-Gerade jede Zeile $y \in \{0, \dots, q - 1\}$ kollisionsfrei (`best_3p is not None`).
3. **Existenz einer kollisionsfreien Bijektion $\pi$ für jede restliche `1P`-Gerade auf $z^*$ (Hall-Bedingung):**
   Betrachte o. B. d. A. eine noch zu platzierende Gerade `1P_ab(a, b)` auf einer beliebigen Zeile $y$ von $z^*$. Da $(a, b) \notin \mathrm{proj}_{ab}(T)$, trägt keine zuvor platzierte `3P`-Gerade das Paar $(a, b)$, und keine zuvor platzierte `1P_ab`-Gerade hat dasselbe $(a, b)$. Ein Tripel $(a, b, c)$ kann in Zelle $(x, y)$ von $z^*$ daher **nur** von einer zuvor auf Zeile $y$ platzierten Gerade `1P_ac(a, c)` (höchstens 1 Zelle $x$ pro $c$) oder `1P_bc(b, c)` (höchstens 1 Zelle $x$ pro $c$) stammen. Im bipartiten Graphen `valid_adj` zwischen $X = \mathbb{Z}_q$ und $C = \mathbb{Z}_q$ gilt daher:
   - Für jedes $c \in C$ fehlen höchstens $2$ Kanten $\implies \deg(c) \ge q - 2$.
   - Da es für festes $a$ genau $e$ Geraden `1P_ac(a, *)` und für festes $b$ genau $e$ Geraden `1P_bc(b, *)` gibt, fehlen für jedes $x \in X$ höchstens $2 e$ Kanten $\implies \deg(x) \ge q - 2 e$.
   Für jede nichtleere Teilmenge $S \subset X$ gilt:
   - Ist $|S| \le q - 2 e$, so ist $|N(S)| \ge q - 2 e \ge |S|$.
   - Ist $|S| > q - 2 e$, so hat für $2 e < q - 2$ jedes $c \in C$ mindestens $\deg(c) \ge q - 2 > 2 e = q - (q - 2 e) \ge |X \setminus S|$ Nachbarn in $X$, also mindestens einen Nachbarn in $S$, womit $N(S) = C$ ($|N(S)| = q \ge |S|$).
   Nach dem Heiratssatz von Hall existiert in **jeder** Zeile $y$ ein perfektes Matching (`_max_bijection_gain` findet stets eine gültige Bijektion $\pi$, `best_1p is not None`).
4. **Kollisionsfreie Platzierung aller restlichen $U$-Punkte auf $z^*$:** Jedes $(a, b, c) \in U$ liegt per Definition nicht in $T$ und hat alle drei Paarprojektionen in $\mathrm{proj}(T)$, wird also von keiner `3P`- und keiner `1P`-Geraden erzeugt. Zudem sind alle Elemente von $U$ paarweise verschieden. Somit ist für jedes $u \in U$ jede Zelle $(x, y)$ von $z^*$ frei von $(a, b, c)$, und die Relokationspässe bewahren die Duplikatfreiheit.
5. **Kollisionsfreie Auffüllung der Heavy-Defizite (`exh`) auf $z^*$:** In Zelle $(x, y)$ wird in jedem Schritt $i < \max(|m_a|, |m_b|, |m_c|)$ mindestens eine Koordinate aus den fehlenden Symbolen gewählt (z. B. $a = m_a[i]$ mit `cnt_a[y][x][a] == 0`). Da dieses Symbol in Zelle $(x, y)$ bisher **überhaupt nicht** vorkommt, kann das erzeugte Tripel $(a, b, c)$ nicht bereits in `used_pts_z[y][x]` enthalten sein. Damit erzeugt Schritt 3.4 weder Duplikate noch scheitert er, und am Ende hat jedes Heavy-Symbol aus $A_H, B_H, C_H$ alle $q^2$ Zellen $(x, y)$ auf $z^*$.
6. **Abdeckung (S0)–(S3):**
   - **(S0) Typ 0:** Auf $z < q - 1$ sind alle $(q - 1) q^2$ Punkte abgedeckt (Schritt 1); auf $z^*$ ist nach Schritt 5 für jedes $(x, y)$ jedes $a \in A_H$ ($|A_H| \ge 1$) mindestens einmal vertreten, also sind alle $q^2$ Punkte auf $z^*$ abgedeckt.
   - **(S1) Typ 1:** Jedes Light-Symbol besitzt eine volle horizontale Ebene $z < q - 1$; jedes Heavy-Symbol besitzt nach Schritt 5 die volle horizontale Ebene $z^*$.
   - **(S2) Typ 2:** Jedes Paar in $\mathrm{proj}(T)$ liegt auf einer `3P`-$x$-Geraden; jedes komplementäre Paar liegt auf einer `1P`-$x$-Geraden; jede dieser Geraden wird genau einmal vollständig platziert (Schritte 2–3).
   - **(S3) Typ 3:** Jedes Tripel $(a, b, c) \in \mathbb{Z}_q^3$ liegt entweder in $T$ (`3P`), hat mindestens eine Paarprojektion außerhalb $\mathrm{proj}(T)$ (und wird dann von der zugehörigen `1P`-Geraden wegen der Bijektivität von $\pi$ exakt gedeckt) oder liegt in $U$ (und wird in Schritt 2 oder Schritt 3.3 platziert). $\square$

### Explizite Liste aller offenen Prüfpunkte (`[OFFEN / PRUEFPUNKT]`)

| ID | Stelle | Was bereits bewiesen / geprüft ist | Was noch offen ist (Ziel für Regel-2d / Verschärfung) |
| :---: | --- | --- | --- |
| **`[OFFEN 1]`** | **Größenschranke `m_det(q) < 2 q^3 - q^2` für alle $q \ge 7$** | `m_raw(q, e^*) = 1,90 q^3 - 0,80 q^2 + O(q) < 2 q^3 - q^2` ist für alle $q \ge 7$ bewiesen; numerisch gilt `m_det(q) < 2 q^3 - q^2` für alle `10` geprüften Primzahlpotenzen $q \in \{7, 8, 9, 11, 13, 16, 17, 19, 23, 25\}$ (mit `exh(q) = 1..393 = O(q^2)`). | **Kein analytischer Beweis für `exh(q) + pad_light(q) < (1/10) q^3 - (1/5) q^2` für alle $q \ge 7$!** Die Greedy-Platzierung + 5-Pass-Relokation auf $z^*$ ist deterministisch, aber ihre Restdefizit-Schranke `exh(q) = o(q^3)` ist bisher nur numerisch bis $q = 25$ belegt. |
| **`[OFFEN 2]`** | **Light-Slot-Füllung (`pad_light = 0`)** | Numerisch ist `pad_light = 0` für $q \in \{5, 7, 9, 11, 13, 16, 17, 19, 23, 25\}$ und `pad_light = 2` nur bei $q = 8$ ($r = 7, e = 1$). | Analytischer Nachweis, dass für $e = e^*$ (oder $e^* - 1$) ab $q \ge 9$ die verbleibenden $U$-Tripel je Light-Symbol stets mindestens `q * (unmatched slots auf Ebene z)` übersteigen (`pad_light = 0`). |
| **`[OFFEN 3]`** | **Klein-$q$- und Rundungs-Randfälle ($q \in \{5, 7, 8\}$)** | Bei $q = 5$: $2e = 2 \not< q - 2 = 3$, aber `construct_best(5)` läuft sauber durch (`suff = 0, check_m3 = 0`), erreicht aber `m_det = 227 > 225 = ell` (wegen `exh = 12`). Bei $q = 7, 8$ erfüllt $e = 1$ bereits $2e = 2 < q - 2$ und `m_det < ell`. | Bei $q = 5$ greift der Hall-Beweis aus Schritt 3 ($2e < q - 2$) formal erst ab $q \ge 5$ mit $e = 1$ **nicht** (`2 < 3` stimmt für $q = 5, e = 1$ tatsächlich! Korrektur: $2 \cdot 1 = 2 < 5 - 2 = 3$ gilt bereits ab $q = 5$ für $e = 1$; erst für $e = 2$ braucht man $q \ge 7$!). Prüfung der genauen $q \bmod 3$- und $q \bmod 5$-Rundungsfälle in `construct_best` (für $q > 13$ testet `construct_best` nur noch `c_shift = (2q)//3` und `r in {r_opt, r_opt + 1}`). |
| **`[OFFEN 4]`** | **Unabhängige Prüfung von Satz 1, Satz 2, Satz 3 & §4 (Regel 2d)** | Gate 0 (`phase9_m3_lift.py --gate0`), `check_m3(full-bg3) = 0` für $q \in \{5, 7, 8, 9, 11, 13, 16, 17\}$ sowie Dual-Verify in `/tmp/` für $q = 7, 8, 9, 11, 13$. | Noch keine unabhängige Lesung durch Claude oder ein unbeteiligtes Drittmodell (Regel 2d) und noch keine Literaturprüfung (Regel 2c). |

---

## 4. Abgrenzung gegen die LP-Schranken `46/27` und `49/27` (und Übergang zu AP 3)

### 4.1 Was die LP-Schranken genau beschränken

Betrachte **jede** asymptotische Konstruktion im Modell `M_3(R_3)` auf dem balancierten Light+Heavy-Skelett mit:
- $|A_L| = |B_L| = |C_L| = \lambda q$, $|A_H| = |B_H| = |C_H| = \mu q$ ($\lambda = \frac{1}{3}, \mu = \frac{2}{3}$, $q - 1$ leichte horizontale Ebenen + $1$ schwere Ebene $z^*$),
- Typ-2-Paarabdeckung **ausschließlich durch volle $x$-Geraden** (`3P` und `1P`), ergänzt um Einzelpunkte (`0P`).

Normiere alle Geraden-Dichten durch $q^2$ und alle Punktdichten durch $q^3$. Nach Mittelung über die $S_3$-Symmetrie von $(A, B, C)$ genügen $19$ nicht-negative Variablen (jeweils mit ihren Symmetriemultiplizitäten):
- Auf den leichten Ebenen: `3P`-Geraden $y_3$ (`LLL`, $\times 1$), $y_2$ (`LLH`, $\times 3$), $y_1$ (`LHH`, $\times 3$); `1P`-Geraden $q_{LL}$ (`LL`, $\times 3$), $q_{LH}$ (`LH/HL`, $\times 6$); `0P`-Punkte $u_{L3}$ ($\times 1$), $u_{L2}$ ($\times 3$), $u_{L1}$ ($\times 3$).
- Auf der schweren Ebene $z^*$: `3P`-Geraden $z_3, z_2, z_1, z_0$ ($\times 1, 3, 3, 1$); `1P`-Geraden $r_{LL}, r_{LH}, r_{HH}$ ($\times 3, 6, 3$); `0P`-Punkte $u_{H3}, u_{H2}, u_{H1}, u_{H0}$ ($\times 1, 3, 3, 1$).

Die notwendigen linearen Bedingungen (selbst unter der **optimistischen Bonferroni-Relaxation 1. Ordnung**, die Überlappungen zwischen `1P_ab`, `1P_ac`, `1P_bc` ignoriert!) lauten:
1. **(LightMass):** $y_3 + 3 y_2 + 3 y_1 + 3 q_{LL} + 6 q_{LH} + u_{L3} + 3 u_{L2} + 3 u_{L1} \ge 1$ (Typ 0 auf den $q - 1$ leichten Ebenen).
2. **(HeavyCov):** $z_2 + 2 z_1 + z_0 + \frac{2}{3} r_{LL} + \frac{10}{3} r_{LH} + \frac{8}{3} r_{HH} + u_{H2} + 2 u_{H1} + u_{H0} \ge \frac{2}{3}$ (jedes Heavy-Symbol in $A_H$ braucht eine volle Ebene auf $z^*$; entscheidend: `3*r_HH` liefert nur $\frac{8}{3} r_{HH}$ für $A_H$, weil `1P_bc(H, H)` ein Drittel seiner $x$-Gerade auf $A_L$ verliert!).
3. **(Paarabdeckung `P_LL`, `P_LH`, `P_HH`):**
   $$(y_3+z_3) + (y_2+z_2) + (q_{LL}+r_{LL}) \ge \tfrac{1}{9}, \quad (y_2+z_2) + (y_1+z_1) + (q_{LH}+r_{LH}) \ge \tfrac{2}{9}, \quad (y_1+z_1) + z_0 + r_{HH} \ge \tfrac{4}{9}.$$
4. **(Tripelabdeckung `T_LLL`, `T_LLH`, `T_LHH`, `T_HHH` — Bonferroni 1. Ordnung):**
   $$(q_{LL}+r_{LL}) + (u_{L3}+u_{H3}) \ge \tfrac{1}{27}, \qquad \tfrac{2}{3}(q_{LL}+r_{LL}) + \tfrac{2}{3}(q_{LH}+r_{LH}) + (u_{L2}+u_{H2}) \ge \tfrac{2}{27},$$
   $$\tfrac{4}{3}(q_{LH}+r_{LH}) + \tfrac{1}{3} r_{HH} + (u_{L1}+u_{H1}) \ge \tfrac{4}{27}, \qquad 2 r_{HH} + u_{H0} \ge \tfrac{8}{27}.$$

**Satz 4 (Exakte LP-Schranken `46/27` und `49/27` mit expliziten rationalen Dualzertifikaten — exakt in `Fraction`-Arithmetik primal + dual verifiziert).**
1. **Allgemeines Light+Heavy-`x`-Geraden-LP (`LP1`):** Das exakte Minimum der Gesamtdichte $|R_3|/q^3$ unter (1)–(4) ist **`46/27 ≈ 1,703704`**.
   *Explizites Dualzertifikat:* Multipliziere die $9$ Ungleichungen `(LightMass, HeavyCov, P_LL, P_LH, P_HH, T_LLL, T_LLH, T_LHH, T_HHH)` mit
   $$y^* = \left(\tfrac{1}{2},\; \tfrac{3}{4},\; \tfrac{1}{4},\; \tfrac{5}{4},\; \tfrac{1}{4},\; \tfrac{1}{2},\; \tfrac{9}{8},\; \tfrac{3}{4},\; \tfrac{1}{4}\right) \ge 0.$$
   Für jede der $19$ Variablen liegt die Dualsumme $\le$ ihrer Multiplizität (exakt nachprüfbar), und der Dualwert beträgt:
   $$\frac{1}{2}\cdot 1 + \frac{3}{4}\cdot\frac{2}{3} + \frac{1}{4}\cdot\frac{1}{9} + \frac{5}{4}\cdot\frac{2}{9} + \frac{1}{4}\cdot\frac{4}{9} + \frac{1}{2}\cdot\frac{1}{27} + \frac{9}{8}\cdot\frac{2}{27} + \frac{3}{4}\cdot\frac{4}{27} + \frac{1}{4}\cdot\frac{8}{27} = \frac{46}{27}.$$
   *(Ohne Heavy-Plane-`1P` (`r_LL = r_LH = r_HH = 0`) steigt das Minimum auf `16/9 = 48/27 ≈ 1,7778`; mit reinem `x`-Geraden-LP ohne `0P`-Punkte auf `139/81 ≈ 1,7160`.)*
2. **Schranke `49/27` (ohne `3P`-Geraden in `LLL`/`LLH`):** Erzwingt man zusätzlich $y_3 = z_3 = y_2 = z_2 = 0$ (keine `3P`-Geraden mit $\ge 2$ Light-Symbolen), so steigt das exakte LP-Minimum auf **`49/27 ≈ 1,814815`**.
   *Explizites 5-Term-Dualzertifikat (sogar unabhängig von `LightMass` und `HeavyCov`!):*
   $$3\cdot P_{LL} + 2\cdot P_{LH} + 1\cdot P_{HH} + 3\cdot T_{LHH} + \tfrac{1}{2}\cdot T_{HHH} \implies 3\cdot\tfrac{1}{9} + 2\cdot\tfrac{2}{9} + 1\cdot\tfrac{4}{9} + 3\cdot\tfrac{4}{27} + \tfrac{1}{2}\cdot\tfrac{8}{27} = \frac{49}{27}.$$
   *(Zusätzlich gilt bei $q = 9$ numerisch $m_{\mathrm{raw}}(9, 2) = 1323 = \frac{49}{27} \cdot 9^3$.)*

### 4.2 Hierarchie der Konstanten & warum die LP-Schranken allgemeines `R_3` nicht ausschließen

| Konstante | Wert | Gültigkeitsbereich / Bedeutung |
| :---: | :---: | --- |
| **`45/27 = 5/3`** | `1,6667` | Reines Light+Heavy-Skelett (nur Typ 0 + Typ 1, ohne Typ 2 / Typ 3) |
| **`46/27`** | `1,7037` | Exaktes `LP1`-Minimum für **alle** balancierten Light+Heavy-`x`-Geraden-Bauarten (unter optimistischer Bonferroni-1.-Ordnung) |
| **`49/27`** | `1,8148` | Exaktes LP-Minimum ohne `3P` in `LLL`/`LLH` (und numerisch `m_raw(9, 2) = 1323` bei $q = 9$) |
| **`19/10`** | `1,9000` | Tatsächliche Asymptotik der deterministischen zyklischen Differenzband-Bauart (`scripts/phase9_m3_construct.py`) |
| **`2`** | `2,0000` | Elliptische Schranke `2 q^3 - q^2` (bisherige Tabellenbasis in `ca-tools` für `q = 7..13, 19`) |

**Abgrenzung gegen allgemeines `R_3` (Brücke zu AP 3):**
1. **Ruzsa–Szemerédi-Barriere innerhalb der `3P + 1P + 0P`-Familie:** `LP1` (`46/27`) unterschätzt den wahren `|U|`-Term massiv, weil Bonferroni-1.-Ordnung zulässt, dass `1P`-Geraden disjunkte Tripelmengen überdecken. Für jedes echte partielle lateinische Quadrat $T$ der Dichte $\rho = |T|/q^2 > 0$ erzwingt jedoch der **(6, 3)-Satz von Ruzsa–Szemerédi (1978)** zwingend $|U(T)| = \Omega_\rho(q^3)$ — selbst ohne jede Typ-1-Bedingung (rechnerischer SA-Check bei $q = 9$: bestes allgemeines partielles lateinisches Quadrat erreicht `m_raw = 1318`, nur `-5` unter `1323`, weit über `1242`).
2. **Was die LP-Schranken *nicht* beschränken:** Weder `46/27` noch `49/27` gilt für allgemeine `R_3 \subset \mathbb{F}_q^6`, die **nicht** auf vollen horizontalen Ebenen (Typ 1) und vollen $x$-Geraden (Typ 2) beruhen. Insbesondere motiviert das den in [`M3_BAER_PILOT_REPORT.md`](M3_BAER_PILOT_REPORT.md) (AP 3) getesteten 3D-Baer-Pilot für Quadratordnungen $q = s^2$, der jedoch für alle vier direkten 3D-Baer-/$\mathbb{F}_s$-Architekturen eigene strukturelle 3D-Obstruktionen (`m = 1485` bei $q = 9$, `8176` bei $q = 16$, asymptotisch $2 q^3 + \Theta(q^{5/2})$) aufzeigt.
