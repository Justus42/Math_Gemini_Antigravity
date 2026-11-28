# Beweisnotiz: Deterministische Light+Heavy-3D-Konstruktion im biaffinen Modell `M_3(R_3)` (`k = q + 3`, `3 <= t <= q`)

- **Datum:** 2026-11-28 UTC
- **Branch / Basis:** `exp/phase9-biaffine-3d` (Basis `0d6e9f5`, PR `#54`)
- **Referenzimplementierung:** [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py) (`std`-only + `GeneralGF`), [`scripts/phase9_m3_lift.py`](../../scripts/phase9_m3_lift.py)
- **Zweck:** Prüfbare mathematische Ausarbeitung für Gegenprüfung und Drittmodell-Prüfung nach [`RULES.md`](../../RULES.md) Regel 2d.
- **Belegart-Disziplin:** Algebraische Beweisschritte sind streng von numerisch geprüften Fällen (`suff=0`, `check_m3=0`, `Dual-Verify PASS`) und offenen Punkten (`[OFFEN / PRUEFPUNKT]`) getrennt. **Drittprüfung nach Regel 2d steht aus.**

---

## 1. Definitionen und Übersetzungssatz (`M_3(R_3)` → `CA(N; t, q + 3, q)`)

Sei $q = p^e \ge 3$ eine Primzahlpotenz, $\mathbb{F}_q$ der endliche Körper der Ordnung $q$ (mit gewählter Nummerierung $\mathbb{F}_q = \{0, 1, \dots, q-1\}$), und $3 \le t \le q$.

### 1.1 Kern und Nebenklassen-Lift
Wir definieren den linearen Kern der Dimension $t - 3$ über $\mathbb{F}_q$:
$$K_t^{(3)} := \Big\{ \big( (g(x))_{x \in \mathbb{F}_q},\, 0,\, 0,\, 0 \big) \in \mathbb{F}_q^{q+3} \;:\; g \in \mathbb{F}_q[X],\; \deg g \le t - 4 \Big\}$$
(für $t = 3$ ist $K_3^{(3)} = \{0\}$). Eine **Vertreterliste** ist eine endliche Menge $R_3 \subseteq \mathbb{F}_q^6$ von $6$-Tupeln $(c_0, c_1, c_2, a, b, c)$. Der zugehörige **Lift** $M_3(R_3, t)$ hat $N = |R_3|\, q^{t-3}$ Zeilen und $k = q + 3$ Spalten (indiziert durch $x \in \mathbb{F}_q$ sowie drei Zusatzspalten $\infty_a, \infty_b, \infty_c$):
$$\mathrm{row}(g;\, c_0, c_1, c_2, a, b, c) := \Big( \big(f(x)\big)_{x \in \mathbb{F}_q},\; a,\; b,\; c \Big), \qquad f(X) = g(X) + c_0 X^{t-3} + c_1 X^{t-2} + c_2 X^{t-1}$$
über alle $(c_0, c_1, c_2, a, b, c) \in R_3$ und alle $g \in \mathbb{F}_q[X]$ mit $\deg g \le t - 4$.

### 1.2 Exakte Bedingungen (`check_m3=0`) und stärkeunabhängige Bedingung (`full-bg3`)
Sei $U \subseteq \mathbb{F}_q$ eine Menge von $r$ Körper-Spalten ($0 \le r \le t$). Für $S \subseteq \mathbb{F}_q$ bezeichnen $e_1(S) = \sum_{x \in S} x$ und $e_2(S) = \sum_{\{x, y\} \subset S} xy$ die ersten beiden elementarsymmetrischen Polynome.

**Satz 1 (Übersetzungssatz `M_3` → `CA`).** *Für festes $3 \le t \le q$ ist $M_3(R_3, t)$ genau dann ein Covering Array $\mathrm{CA}(|R_3|\,q^{t-3};\, t,\, q+3,\, q)$, wenn $R_3$ die vier Bedingungen (Typ 0–3) erfüllt:*
- **(Typ 0, $0$ Zusatzspalten):** Jedes $(c_0, c_1, c_2) \in \mathbb{F}_q^3$ tritt mindestens einmal in $R_3$ auf.
- **(Typ 1, $1$ Zusatzspalte):** Für jedes $u \in \{a, b, c\}$, jedes $s \in \mathbb{F}_q$ und jede Richtung $(v, w, 1) \in D_1(t)$ gilt
  $$\big|\big\{ (c_0 - v c_2,\; c_1 - w c_2) \;:\; (c_0, c_1, c_2, a, b, c) \in R_3,\; u = s \big\}\big| = q^2,$$
  wobei $D_1(t) = \{ (e_2(S), -e_1(S), 1) : S \in \binom{\mathbb{F}_q}{t-1} \}$.
- **(Typ 2, $2$ Zusatzspalten):** Für jedes Spaltenpaar $\{u_1, u_2\} \in \{\{a,b\}, \{a,c\}, \{b,c\}\}$, jedes $(s_1, s_2) \in \mathbb{F}_q^2$ und jede Normale $(1, \alpha, \beta) \in N_2(t)$ gilt
  $$\big|\big\{ c_0 + \alpha c_1 + \beta c_2 \;:\; (c_0, c_1, c_2, a, b, c) \in R_3,\; (u_1, u_2) = (s_1, s_2) \big\}\big| = q,$$
  wobei $N_2(t) = \{ (1,\, e_1(U),\, e_1(U)^2 - e_2(U)) : U \in \binom{\mathbb{F}_q}{t-2} \}$.
- **(Typ 3, $3$ Zusatzspalten):** Jedes $(a, b, c) \in \mathbb{F}_q^3$ tritt mindestens einmal in $R_3$ auf.

*Beweisskizze (Polynomdivision / Lagrange-Interpolation):*
1. **Typ 0 ($t$ Körper-Spalten $S$, $|S|=t$):** Zu gegebenen Zielwerten $(y_x)_{x \in S}$ gibt es genau ein Polynom $f$ mit $\deg f \le t - 1$ und $f(x) = y_x$ für alle $x \in S$. Dieses legt $(c_0, c_1, c_2)$ und $g$ ($\deg g \le t-4$) eindeutig fest.
2. **Typ 1 ($t - 1$ Körper-Spalten $S$ + $1$ Zusatzspalte $u = s$):** Sei $P_S(X) = \prod_{x \in S} (X - x) = X^{t-1} - e_1(S) X^{t-2} + e_2(S) X^{t-3} + \tilde{P}(X)$ mit $\deg \tilde{P} \le t - 4$. Zwei Polynome $f, f'$ vom Grad $\le t - 1$ stimmen auf $S$ genau dann überein, wenn $f - f' = \lambda P_S(X)$ für ein $\lambda \in \mathbb{F}_q$, d. h. wenn sich ihre drei obersten Koeffizienten $(c_0, c_1, c_2)$ genau um ein Vielfaches von $(e_2(S), -e_1(S), 1)$ unterscheiden. Da $g$ frei über alle Polynome vom Grad $\le t - 4$ läuft, wird ein Tupel auf $S$ bei $u = s$ genau dann erreicht, wenn die Projektion $(c_0 - e_2(S)c_2,\; c_1 + e_1(S)c_2)$ den entsprechenden Restklassen-Vektor in $\mathbb{F}_q^2$ trifft.
3. **Typ 2 ($t - 2$ Körper-Spalten $U$ + $2$ Zusatzspalten $(u_1, u_2) = (s_1, s_2)$):** Sei $Q_U(X) = \prod_{x \in U}(X - x) = X^{t-2} - e_1(U)X^{t-3} + e_2(U)X^{t-4} + \dots$. Die Nebenklassen von $f \bmod Q_U(X)$ im Quotienten $\mathbb{F}_q[X]_{< t} / (K_t^{(3)} + Q_U \cdot \mathbb{F}_q[X]_{< 2})$ sind eindimensional und werden durch die Linearform $\ell_U(c_0, c_1, c_2) = c_0 + e_1(U)\,c_1 + (e_1(U)^2 - e_2(U))\,c_2$ getrennt (Division von $c_0 X^{t-3} + c_1 X^{t-2} + c_2 X^{t-1}$ durch $Q_U(X)$ liefert als $X^{t-3}$-Koeffizient des Rests exakt $c_0 + e_1 c_1 + (e_1^2 - e_2) c_2$, da $X^{t-2} \equiv e_1 X^{t-3} - e_2 X^{t-4}$ und $X^{t-1} \equiv (e_1^2 - e_2) X^{t-3} + \text{deg}\le t-4 \pmod{Q_U}$).
4. **Typ 3 ($t - 3$ Körper-Spalten $W$ + alle $3$ Zusatzspalten $(a,b,c)$):** Für festes $(c_0, c_1, c_2, a, b, c) \in R_3$ läuft $g(X)$ über alle Polynome vom Grad $\le t - 4$ und nimmt damit auf den $t - 3$ Stellen $W$ jedes $(t - 3)$-Tupel genau einmal an. Somit ist Surjektivität genau dann erfüllt, wenn $(a, b, c)$ vorkommt. $\square$

*(Prüfvermerk: Satz 1 ist numerisch gegen Exhaustivzählung auf $q = 3, 4, 5$ in Gate 0 `scripts/phase9_m3_lift.py --gate0` mit $0$ Abweichungen und durch Dual-Verifikation gelifteter Arrays für $q \in \{3, 4, 5, 7, 8, 9, 11, 13\}$ bestätigt; Regel-2d-Prüfung des Texts steht aus.)*

**Korollar 1 (`full-bg3`).** *Ersetzt man $D_1(t)$ und $N_2(t)$ durch alle $q^2$ Richtungen $D_1^{\mathrm{full}} = \{(v, w, 1) : v, w \in \mathbb{F}_q\}$ und alle $q^2$ Normalen $N_2^{\mathrm{full}} = \{(1, \alpha, \beta) : \alpha, \beta \in \mathbb{F}_q\}$, so hebt jedes $R_3$ mit `check_m3(full-bg3) = 0` simultan für **alle** Stärken $3 \le t \le q$ auf ein gültiges $\mathrm{CA}(|R_3|\,q^{t-3};\, t,\, q+3,\, q)$.*

### 1.3 Hinreichende geometrische Bedingung (`suff=0`)
Im affinen Raum $\mathrm{AG}(3, q) = \mathbb{F}_q^3$ mit Koordinaten $(x, y, z) := (c_0, c_1, c_2)$ gilt:
- Eine **horizontale $z$-Ebene** $H_{z_0} = \{(x, y, z_0) : x, y \in \mathbb{F}_q\}$ trifft jede nicht-horizontale Gerade $\{(x_0 + vt, y_0 + wt, t) : t \in \mathbb{F}_q\}$ genau bei $t = z_0$. Enthält die Faser $\{u = s\}$ eine vollständige horizontale Ebene $H_{z_0}$, so ist Typ 1 für $(u, s)$ über ganz $D_1^{\mathrm{full}}$ erfüllt.
- Eine **volle $x$-Gerade** $L_{y_0, z_0} = \{(x, y_0, z_0) : x \in \mathbb{F}_q\}$ trifft jede Ebene $x + \alpha y + \beta z = \mu$ genau bei $x = \mu - \alpha y_0 - \beta z_0$. Enthält die Paar-Faser $\{(u_1, u_2) = (s_1, s_2)\}$ eine volle $x$-Gerade $L_{y_0, z_0}$, so ist Typ 2 für dieses Paar über ganz $N_2^{\mathrm{full}}$ erfüllt.

**Lemma 1 (`suff=0` $\Rightarrow$ `check_m3(full-bg3)=0`).** *Besitzt $R_3 \subseteq \mathbb{F}_q^6$ keine Duplikate, deckt alle $q^3$ Punkte $(x, y, z)$ (Typ 0) und alle $q^3$ Tripel $(a, b, c)$ (Typ 3), besitzt jedes Einzelsymbol $s \in \mathbb{F}_q$ in jeder Spalte $u \in \{a, b, c\}$ mindestens eine vollständige horizontale $z$-Ebene, und besitzt jedes Symbolpaar $(s_1, s_2) \in \mathbb{F}_q^2$ in jedem Paar $\{a,b\}, \{a,c\}, \{b,c\}$ mindestens eine volle $x$-Gerade, dann gilt `check_m3(full-bg3) = 0`.* $\square$

*(Implementiert als `check_sufficient_full_bg3` in [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py#L578-L615).)*

---

## 2. Explizite deterministische Konstruktion & exakte Zählformel

Im Folgenden bezeichnen wir die $q$ Elemente des Symbolalphabets als $\mathbb{Z}_q = \{0, 1, \dots, q-1\}$ (die Symbol-Arithmetik in Step 1 nutzt ausschließlich die zyklische Gruppe $\mathbb{Z}_q$, unabhängig davon, ob $q$ prim oder eine echte Primzahlpotenz ist; die Körperstruktur $\mathbb{F}_q$ wird erst beim Lift in Satz 1 benötigt).

### 2.1 Parameterwahl und Light+Heavy-Zerlegung
Für jede Primzahlpotenz $q \ge 5$, Bandbreite $r \in \{1, \dots, q-1\}$ (mit Komplement $e := q - r$) und Verschiebung $c_{\mathrm{shift}} \in \mathbb{Z}_q$:
1. **Balancierte Partition der $q - 1$ leichten $z$-Ebenen:**
   $$k_a = \left\lfloor \frac{q + 1}{3} \right\rfloor, \qquad k_b = \left\lfloor \frac{q}{3} \right\rfloor, \qquad k_c = \left\lfloor \frac{q - 1}{3} \right\rfloor \qquad (k_a + k_b + k_c = q - 1).$$
   Setze $A_L = \{0, \dots, k_a - 1\}$, $B_L = \{0, \dots, k_b - 1\}$, $C_L = \{(c_{\mathrm{shift}} + i) \bmod q : 0 \le i < k_c\}$ sowie die schweren Mengen $A_H = \mathbb{Z}_q \setminus A_L$, $B_H = \mathbb{Z}_q \setminus B_L$, $C_H = \mathbb{Z}_q \setminus C_L$. Die $q - 1$ leichten horizontalen Ebenen $z \in \{0, \dots, q-2\}$ werden bijektiv den Symbolen aus $A_L \sqcup B_L \sqcup C_L$ zugeordnet; $z^* := q - 1$ ist die einzige schwere Ebene.
2. **Zyklisches Differenzband `3P` + komplementäre `1P`-`x`-Geraden + Resttripel $U$:**
   Setze $D := \{0, 1, \dots, r-1\} \subset \mathbb{Z}_q$ und $E := \mathbb{Z}_q \setminus D = \{r, \dots, q-1\}$ ($|E| = e = q - r$).
   - **Typ-`3P`-`x`-Geraden** (partielles lateinisches Quadrat $T$ der Größe $|T| = r q$):
     $$T := \big\{ (a, b, c) \in \mathbb{Z}_q^3 \;:\; a + b + c \equiv 0 \pmod q,\; (a - b) \bmod q \in D \big\}.$$
     Jedes $(a, b, c) \in T$ definiert eine volle $x$-Gerade mit konstanten Symbolen $(a, b, c)$ (`q` Punkte), die die drei Paare $(a, b), (a, c), (b, c)$ sowie das Tripel $(a, b, c)$ abdeckt.
     Da $a + b + c \equiv 0 \pmod q$ jede dritte Koordinate eindeutig festlegt, sind die drei Paarprojektionen exakt charakterisiert durch:
     $$\begin{aligned}
     E_{ab} &:= \mathrm{proj}_{ab}(T) = \{(a, b) : (a - b) \bmod q \in D\}, && |E_{ab}| = rq, \\
     E_{ac} &:= \mathrm{proj}_{ac}(T) = \{(a, c) : (2a + c) \bmod q \in D\}, && |E_{ac}| = rq, \\
     E_{bc} &:= \mathrm{proj}_{bc}(T) = \{(b, c) : (-2b - c) \bmod q \in D\}, && |E_{bc}| = rq.
     \end{aligned}$$
   - **Typ-`1P`-`x`-Geraden** ($3(q - r)q = 3 e q$ Geraden):
     Für jedes fehlende Paar $(a, b) \notin E_{ab}$ wird eine Gerade `1P_ab(a, b)` erzeugt (mit konstanten $a, b$ und einer Bijektion $\pi: \mathbb{F}_q \to \mathbb{F}_q$ in der dritten Koordinate $c$), analog `1P_ac(a, c)` für $(a, c) \notin E_{ac}$ und `1P_bc(b, c)` für $(b, c) \notin E_{bc}$.
   - **Resttripel $U$ (Typ-3-Defekt von $T$ und `1P`):**
     $$U := \big\{ (a, b, c) \in \mathbb{Z}_q^3 \setminus T \;:\; (a, b) \in E_{ab},\; (a, c) \in E_{ac},\; (b, c) \in E_{bc} \big\}.$$
3. **Deterministisches Light-Plane-Matching (Ebenen $z = 0, \dots, q-2$):**
   Die $q(q-1)$ $x$-Geraden-Slots $(z, y)$ werden durch ein maximales bipartites Matching kompatiblen `3P`-/`1P`-Geraden zugeordnet (eine Gerade ist zu Ebene $z$ mit Besitzer $(\mathrm{col}, s)$ kompatibel, wenn ihre feste Koordinate $\mathrm{col}$ gleich $s$ ist). Jeder ungematchte Light-Slot $(z, y)$ wird mit $q$ noch unbenutzten Tripeln aus $U$ mit $\mathrm{col} = s$ (oder bei Erschöpfung mit Füllpunkten mit $\mathrm{col} = s$) aufgefüllt.
4. **Deterministische Heavy-Plane-Platzierung (Ebene $z^* = q - 1$):**
   - Übrige `3P`-Geraden werden nacheinander auf die Zeile $y \in \{0, \dots, q-1\}$ mit maximalem neuem Heavy-Deckungsgewinn (in $A_H, B_H, C_H$) gelegt.
   - Übrige `1P`-Geraden erhalten für jedes $y$ per bipartitem Matching (`_max_bijection_gain`) eine duplikatfreie $x$-Bijektion $\pi$ mit maximalem Heavy-Deckungsgewinn und wählen das beste $y$.
   - Übrige Tripel aus $U$ werden punktweise auf schwere Defizitzellen $(x, y)$ von $z^*$ verteilt, gefolgt von bis zu $5$ deterministischen $1$-Punkt-Relokationspässen.
   - Verbleibende Heavy-Defizite (`exh` Punkte) werden zellweise auf $z^*$ aufgefüllt.

### 2.2 Exakte geschlossene Zählformel für $|U|$ und $m_{\mathrm{raw}}(q, r)$ (und Korrektur gegen `49/27`)

**Satz 2 (Exakte Zählformel für das zyklische Differenzband).** *Für jedes $q \ge 3$ und jedes $r \in [\lceil q/2 \rceil, q - 1]$ (d. h. $e = q - r \le \lfloor q/2 \rfloor$) gilt exakt:*
$$|U| = q \cdot \mathrm{AP}_3(q, r), \qquad \mathrm{AP}_3(q, r) := \#\big\{(d, s) \in D^2 \;:\; s \neq d,\; (2d - s) \bmod q \in D\big\},$$
*mit der geschlossenen Formel*
$$\mathrm{AP}_3(q, r) = q^2 - (3e + 1)q + \frac{5}{2}e^2 + e + (-1)^q \frac{1}{2}\,\mathbf{1}_{e\text{ ungerade}}.$$
*Die Roh-Punktzahl aus `3P`, `1P` und $U$ beträgt damit exakt:*
$$m_{\mathrm{raw}}(q, r) := (3q - 2r)q^2 + q \cdot \mathrm{AP}_3(q, r) = 2q^3 - (e + 1)q^2 + \frac{5}{2}e^2 q + eq + (-1)^q \frac{q}{2}\,\mathbf{1}_{e\text{ ungerade}}.$$

*Beweis:*
1. **Reduktion auf $\mathrm{AP}_3(q, r)$:** Zu $(a, b, c) \in \mathbb{Z}_q^3$ setze $d := (a - b) \bmod q$, $s := (2a + c) \bmod q$ und $w := (-2b - c) \bmod q$. Dann gilt identisch $s + w \equiv 2(a - b) = 2d \pmod q$, also $w = (2d - s) \bmod q$. Weiter ist $(a, b, c) \in T \iff a + b + c \equiv 0 \iff 2a + c \equiv a - b \iff s = d$. Umgekehrt legt jedes Tripel $(a, d, s) \in \mathbb{Z}_q \times D^2$ mit $s \neq d$ und $(2d - s) \bmod q \in D$ genau ein $(a, b, c) \in U$ fest via $b = (a - d) \bmod q$ und $c = (s - 2a) \bmod q$. Also $|U| = q \cdot \mathrm{AP}_3(q, r)$.
2. **Inklusion-Exklusion über $E = \{r, \dots, q-1\}$ ($|E| = e \le q/2$):**
   Betrachte alle $q(q - 1)$ geordneten Paare $(d, s) \in \mathbb{Z}_q^2$ mit $d \neq s$ und setze $w = (2d - s) \bmod q$ (stets $w \neq d$).
   - **1 Element in $E$:** Jede der drei Bedingungen $d \in E$, $s \in E$, $w \in E$ trifft genau $e(q - 1)$ Paare (Summe $3e(q - 1)$).
   - **2 Elemente in $E$:**
     - $(d, s) \in E^2, s \neq d$: genau $e(e - 1)$ Paare.
     - $(d, w) \in E^2, w \neq d$: genau $e(e - 1)$ Paare.
     - $(s, w) \in E^2$ mit $2d \equiv s + w \pmod q$ und $d \neq s$:
       - Ist $q$ **ungerade**, so ist $2$ invertierbar in $\mathbb{Z}_q$; jedes $(s, w) \in E^2$ mit $s \neq w$ liefert eindeutig $d = (s + w)/2 \neq s$, also genau $e(e - 1)$ Paare.
       - Ist $q$ **gerade**, so erfordert $2d \equiv s + w \pmod q$ genau $s \equiv w \pmod 2$. Für $s \neq w$ gibt es zwei Lösungen $d_1 = (s+w)/2 \in E$ und $d_2 = d_1 + q/2 \notin E$ (beide $\neq s$, da $|w - s| < e \le q/2$), zusammen $2 \cdot \mathrm{AP}_3^{\mathbb{Z}}(E)$; für $s = w \in E$ liefert $d = s + q/2 \neq s$ weitere $e$ Lösungen.
   - **3 Elemente in $E$ ($\mathrm{AP}_3(E)$):** Da $E = [q - e, q - 1]$ und $2e \le q$, gilt für $d, s \in E$: $2d - s \in [q - 2e + 1, q + e - 2]$, was weder $\le -1$ noch $\ge 2q - e$ erreichen kann. Es tritt **kein zyklischer Wrap-Around** auf, sodass $(d, s, 2d - s) \in E^3$ mit $d \neq s$ bijektiv den geordneten Paaren $(s, w) \in [0, e)^2$ mit $s \neq w$ und $s \equiv w \pmod 2$ entspricht:
     $$\mathrm{AP}_3^{\mathbb{Z}}(E) = \begin{cases} \frac{1}{2} e^2 - e & (e \text{ gerade}), \\ \frac{1}{2}(e - 1)^2 & (e \text{ ungerade}). \end{cases}$$
   - Zusammenfassen nach Inklusion-Exklusion $\mathrm{AP}_3(q, r) = q(q-1) - 3e(q-1) + 2e(e-1) + N_{sw} - \mathrm{AP}_3^{\mathbb{Z}}(E)$ liefert in allen vier Paritätsfällen $(q \bmod 2, e \bmod 2)$ exakt die behauptete Formel. Addition von $(3q - 2r)q^2 = (q + 2e)q^2$ ergibt $m_{\mathrm{raw}}(q, r)$. $\square$

*(Rechnerische Gegenprüfung: Formel für alle $3 \le q < 40$ und alle $\lceil q/2 \rceil \le r \le q - 1$ gegen Exhaustivzählung mit $0$ Abweichungen bestätigt.)*

**Korollar 2 (Asymptotik von `scripts/phase9_m3_construct.py` — explizite Korrektur gegen `(49/27) q^3`).**
*Minimierung von $m_{\mathrm{raw}}(q, q - e)$ über $e \in \mathbb{Z}_{\ge 1}$ liefert das kontinuierliche Minimum bei $e^* = (q - 1)/5$, also $r^* = \mathrm{round}((4q + 1)/5)$. Mit $e = (q - 1)/5 + \delta$ ($|\delta| \le 1/2$) folgt:*
$$m_{\mathrm{raw}}(q, r^*) = \mathbf{\frac{19}{10}\,q^3} - \frac{4}{5}\,q^2 + \left(\frac{5}{2}\delta^2 - \frac{1}{10} + \frac{(-1)^q}{2}\mathbf{1}_{e\text{ odd}}\right)q.$$
*Die tatsächliche Größe der deterministischen Liste beträgt:*
$$|R_3| = m_{\mathrm{det}}(q) = m_{\mathrm{raw}}(q, r) + \mathrm{exh}(q, r, c_{\mathrm{shift}}) + \mathrm{dummy}(q, r, c_{\mathrm{shift}}).$$

> **Wichtige Klarstellung zur führenden Konstante (`19/10` vs. `49/27`):**
> Die führende Konstante der deterministischen zyklischen Differenzband-Bauart in [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py) ist **$\frac{19}{10} = 1{,}90$**, **nicht** $\frac{49}{27} \approx 1{,}8148$. Dass $m_{\mathrm{det}}(q)/q^3$ für $q \in [7, 13]$ im Bereich $1{,}827\dots 1{,}861$ liegt (und bei $q = 9, r = 7$ zufällig exakt $m_{\mathrm{raw}}(9, 7) = 1323 = \frac{49}{27} \cdot 9^3$ annimmt), beruht allein auf dem negativen $q^2$-Restterm $-\frac{4}{5}q^2$ (bei $q = 9$: $1{,}90 - 0{,}80/9 = 1{,}8111$). Für wachsendes $q$ steigt $m_{\mathrm{raw}}/q^3$ monoton gegen $1{,}90$ ($q = 25$: $1{,}8672$; $q = 31$: $1{,}8741$; $q = 97$: $1{,}8917$). Die Konstante $\frac{49}{27}$ gehört stattdessen als **LP-Untergrenze** zur `1P_LH`-freien Familie (Abschnitt 4).

---

## 3. Beweis der Vollabdeckung (`suff=0` für alle Primzahlpotenzen $q \ge 5$) & offene Prüfpunkte

**Satz 3 (Deterministische Korrektheit — `suff=0` ohne Ausnahmen für alle $q \ge 2, 1 \le r < q$).**
*Für jede Primzahlpotenz $q \ge 2$, jedes $r \in \{1, \dots, q-1\}$ und jedes $c_{\mathrm{shift}} \in \mathbb{Z}_q$ terminiert `build_m3_for_params(q, r, c_shift)` ohne Fehler und liefert eine duplikatfreie Liste $R_3 \subseteq \mathbb{F}_q^6$ mit `check_sufficient_full_bg3(R_3, q) = 0` (also nach Lemma 1 und Korollar 1 `check_m3(full-bg3) = 0` und gültige $\mathrm{CA}(|R_3| q^{t-3}; t, q+3, q)$ für alle $3 \le t \le q$).*

*Algebraischer Fallunterscheidungsbeweis (Schritt für Schritt):*
1. **Keine Duplikate und keine Abbrüche auf den leichten Ebenen $z \in \{0, \dots, q-2\}$:**
   In Step 2 wird für jedes Paar $(z, y) \in \{0, \dots, q-2\} \times \{0, \dots, q-1\}$ und jedes $x \in \{0, \dots, q-1\}$ genau ein Punkt $(x, y, z, a, b, c)$ erzeugt (entweder durch die zu $(z, y)$ gematchte Gerade oder durch $q$ Füllpunkte). Daher liegt auf jedem Gitterpunkt $(x, y, z)$ mit $z \le q - 2$ exakt ein Vertreter: **0 Duplikate** auf $z \le q - 2$ und **alle $(q-1)q^2$ Punkte** mit $z \le q - 2$ sind gedeckt. Ferner gilt nach Kompatibilitätsdefinition für jeden Punkt auf Ebene $z$ mit Besitzer $(\mathrm{col}, s)$, dass seine Koordinate $\mathrm{col}$ gleich $s$ ist; damit besitzt jedes Symbol in $A_L \sqcup B_L \sqcup C_L$ seine vollständige horizontale Ebene $z$.
2. **Kollisionsfreie `3P`-Platzierung auf $z^* = q - 1$:**
   Alle `3P`-Geraden tragen paarweise verschiedene Tripel $(a, b, c) \in T$ und werden auf $z^*$ vor allen `1P`-Geraden und $U$-Punkten platziert. Für jede `3P`-Gerade ist daher jedes $y \in \{0, \dots, q-1\}$ frei von $(a, b, c)$ (`best_3p` ist stets definiert, **0 Duplikate**).
3. **Existenz einer kollisionsfreien `1P`-Bijektion auf $z^*$ (Schubfachprinzip + Hall-Heiratssatz):**
   Sei `1P_ab(a, b)` auf $z^*$ zu platzieren (analog für `1P_ac`, `1P_bc`). Da $(a, b) \notin E_{ab}$, kann kein zuvor platzierter `3P`-Punkt und keine andere `1P_ab`-Gerade das Paar $(a, b)$ tragen. Ein Konflikt $(a, b, c) \in \mathrm{used}[y][x]$ entsteht daher ausschließlich durch zuvor auf derselben Zeile $y$ platzierte Geraden `1P_ac(a, c)` (mit $\pi(x) = b$) oder `1P_bc(b, c)` (mit $\pi(x) = a$).
   - Es gibt höchstens $q - r$ Geraden `1P_ac(a, \cdot)` und höchstens $q - r$ Geraden `1P_bc(b, \cdot)`, und jede legt höchstens eine verbotene Kante $(x, c)$ auf genau einer Zeile $y$ fest.
   - Über alle $q$ Zeilen $y \in \{0, \dots, q-1\}$ summiert gibt es höchstens $2(q - r)$ verbotene Kanten $(x, c)$.
   - Da $r \ge 1$, ist $2(q - r) \le 2q - 2 < 2q$; nach dem **Schubfachprinzip** existiert mindestens eine Zeile $y$ mit höchstens $\lfloor (2q - 2)/q \rfloor = 1$ verbotener Kante (für $r > q/2$ sogar mit **$0$ verbotenen Kanten**, d. h. vollständigem $K_{q, q}$!).
   - Ein vollständiger bipartiter Graph $K_{q, q}$ minus höchstens eine Kante besitzt für jedes $q \ge 2$ ein perfektes Matching (Hall-Bedingung trivial erfüllt). Folglich findet `_max_bijection_gain` auf dieser Zeile $y$ garantiert eine duplikatfreie Bijektion $\pi: \mathbb{F}_q \to \mathbb{F}_q$ (`best_1p` ist stets definiert, **0 Duplikate**).
4. **Kollisionsfreie Platzierung und Relokation von $U_{\mathrm{rem}}$ auf $z^*$:**
   Jedes $(a, b, c) \in U$ liegt weder in $T$ noch im Bild einer `1P`-Geraden (denn $(a, b) \in E_{ab}$, $(a, c) \in E_{ac}$, $(b, c) \in E_{bc}$), und alle Elemente von $U$ sind paarweise verschieden. Somit ist $(a, b, c) \notin \mathrm{used}[y][x]$ für **alle** $q^2$ Zellen $(x, y)$ von $z^*$ (sowohl bei der Erstplatzierung als auch bei allen Relokationen: **0 Duplikate**).
5. **Kollisionsfreie `extra_heavy`-Auffüllung und Vollständigkeit auf $z^*$:**
   Für jede Zelle $(x, y)$ auf $z^*$ werden die fehlenden schweren Symbole $m_a, m_b, m_c$ in $\mathrm{need} = \max(|m_a|, |m_b|, |m_c|)$ Schritten aufgefüllt. In Schritt $i < \mathrm{need}$ gilt mindestens eine der Bedingungen $i < |m_a|$, $i < |m_b|$ oder $i < |m_c|$. Ohne Einschränkung sei $i < |m_a|$; dann kommt $a = m_a[i]$ in $\mathrm{used}[y][x]$ bisher **gar nicht** vor (`cnt_a[y][x][a] == 0`), sodass $(a, b, c) \notin \mathrm{used}[y][x]$ für beliebige $b, c$ automatisch erfüllt ist (**0 Duplikate**). Danach enthält jede Zelle $(x, y)$ von $z^*$ jedes $a \in A_H$, $b \in B_H$, $c \in C_H$ (und wegen $A_H \neq \emptyset$ insbesondere mindestens einen Punkt $\Rightarrow$ **Typ 0 auf $z^*$ erfüllt** und **Typ 1 für alle schweren Symbole erfüllt**).
6. **Vollabdeckung Typ 2 und Typ 3:**
   - **Typ 2:** Jedes Paar $(a, b) \in \mathbb{Z}_q^2$ liegt entweder in $E_{ab}$ (dann existiert eine `3P`-Gerade mit $(a, b)$ auf einer leichten Ebene oder auf $z^*$) oder in $\mathbb{Z}_q^2 \setminus E_{ab}$ (dann existiert eine `1P_ab`-Gerade mit $(a, b)$ auf einer leichten Ebene oder auf $z^*$). Analog für $\{a, c\}$ und $\{b, c\}$. Jedes Paar besitzt also eine volle $x$-Gerade.
   - **Typ 3:** Jedes Tripel $(a, b, c) \in \mathbb{Z}_q^3$ liegt entweder in $T$ (gedeckt durch seine `3P`-Gerade), hat mindestens eine Projektion außerhalb von $E_{ab}/E_{ac}/E_{bc}$ (gedeckt durch die zugehörige `1P`-Gerade, da $\pi$ surjektiv auf $\mathbb{F}_q$ ist), oder liegt in $U$ (gedeckt auf einem ungematchten Light-Slot oder auf $z^*$). $\square$

### 3.1 Ehrliche Markierung aller `[OFFEN / PRUEFPUNKT]`-Stellen (für Regel 2d)

| Nr. | Status | Gegenstand & konkreter Handlungsbedarf |
| :---: | :---: | --- |
| **P1** | **`[OFFEN / PRUEFPUNKT]`** | **Analytische Oberschranke für `exh(q)` und `dummy(q)` (Beweis von $m_{\mathrm{det}}(q) < 2q^3 - q^2$ für alle $q \ge 7$):** Satz 3 beweist `suff=0` für *alle* $q \ge 2$, und Satz 2 beweist $m_{\mathrm{raw}}(q, r^*) = \frac{19}{10}q^3 - \frac{4}{5}q^2 + O(q) < 2q^3 - q^2$ für alle $q \ge 5$. Um $m_{\mathrm{det}}(q) < 2q^3 - q^2$ *für alle Primzahlpotenzen $q \ge 7$* rein analytisch (ohne Rechenprüfung) zu beweisen, fehlt noch eine geschlossene obere Schranke $\mathrm{exh}(q) + \mathrm{dummy}(q) < \frac{1}{10}q^3 - \frac{1}{5}q^2$. **Numerisch geprüft** für alle $14$ Primzahlpotenzen $5 \le q \le 31$: stets `dummy = 0` und $\mathrm{exh}(q) \le 0{,}77\,q^2$, sodass $m_{\mathrm{det}}(q) < 2q^3 - q^2$ für alle getesteten $q \in \{7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31\}$ gilt (nur bei $q = 5$ ist $m_{\mathrm{det}}(5) = 227 > 225$). |
| **P2** | **`[OFFEN / PRUEFPUNKT]`** | **Grenzfall $q \bmod 3$ und `dummy = 0` bei ungematchten Light-Slots:** Im Light-Plane-Matching (Step 2) entstehen bei großem $q$ ungematchte Light-Slots (`unm = 5..104` für $q = 7..31$). Bisher ist nur empirisch bis $q = 31$ belegt, dass für jeden ungematchten Slot $(z, y)$ noch mindestens $q$ unverbrauchte Tripel in $U$ mit dem festen Symbol der Ebene $z$ vorliegen (`dummy = 0`). Eine explizite untere Schranke auf die Fasergröße $|U \cap \{u = s\}| = \mathrm{AP}_3(q, r) \approx 0{,}5 q^2$ gegenüber höchstens $q$ ungematchten Slots je Symbol ($q \cdot q = q^2$) ist für den Fall hoher Unmatched-Raten noch zu prüfen bzw. durch ein explizites Matching-Lemma abzusichern. |
| **P3** | **`[OFFEN / PRUEFPUNKT]`** | **Fremdprüfung von Satz 1, 2, 3 (Regel 2d) & Literaturprüfung (Regel 2c):** Die gesamte Kette (Übersetzungssatz 1 → Zählformel 2 → Korrektheit 3 → LP-Schranken 4) wurde vom Erzeuger erstellt und rechnerisch geprüft; eine unabhängige Prüfung durch ein unbeteiligtes Modell (Regel 2d) und eine Literaturprüfung zu 3D-biaffinen `k = q + 3`-Bauten (Regel 2c) stehen aus. |

---

## 4. Abgrenzung gegen die LP-Schranken `46/27` und `49/27` (Einstieg für AP 3)

Welche Bautypen werden durch die Konstanten **`46/27`** ($\approx 1{,}70370$, bei $q = 9$: $1242$) und **`49/27`** ($\approx 1{,}81481$, bei $q = 9$: $1323$) tatsächlich beschränkt — und wie lassen sie sich prinzipiell unterbieten?

### 4.1 Das asymptotische Light+Heavy-`x`-Geraden-LP
Betrachte eine beliebige (nicht notwendig zyklische!) Konstruktion in der **Light+Heavy-`x`-Geraden-Familie**:
- Symmetrische Zerlegung in leichte Symbole ($|A_L|/q = |B_L|/q = |C_L|/q = \ell = \frac{1}{3}$, auf $q - 1$ leichten $z$-Ebenen) und schwere Symbole ($h = 1 - \ell = \frac{2}{3}$, gemeinsam auf einer schweren Ebene $z^*$).
- Alle $3q^2$ Paare (`LL`: $\frac{1}{3}q^2$, `LH`: $\frac{4}{3}q^2$, `HH`: $\frac{4}{3}q^2$) werden durch volle `x`-Geraden vom Typ `3P` (je $3$ Paare, $0$ asymptotisches Tripel-Volumen) oder Typ `1P` (je $1$ Paar und $q$ Tripel, anteilig $\ell$ bzw. $h$ in der freien Koordinate) abgedeckt; übrige Tripel werden durch Einzelpunkte `0P` gedeckt (Union-Bound auf den $4$ Oktantenklassen `LLL`: $\frac{1}{27}$, `LLH`: $\frac{6}{27}$, `LHH`: $\frac{12}{27}$, `HHH`: $\frac{8}{27}$).
- Auf den leichten Ebenen liegen insgesamt $\ge q^3$ Punkte (`light_pts >= 1`); auf $z^*$ decken die Punkte über alle drei Koordinaten gemittelt $\ge 3h = 2$ schwere Symbol-Vorkommen je Zelle (`heavy_sym >= 2`).

**Satz 4 (Exakte Dual-Zertifikate für `46/27` und `49/27`).** *In diesem LP gilt:*
1. **Allgemeine `3P + 1P + 0P`-Familie (inkl. `1P_LH`):** Das exakte Minimum über alle nichtnegativen Dichten $(L_{3*}, L_{1*}, L_{0*}, H_{3*}, H_{1*}, H_{0*})$ ist **$\frac{46}{27} \approx 1{,}703704$**.
   *Exaktes Dual-Zertifikat* (alle $19$ Variablen erfüllen $(A^\top y)_j \le 1$, Zielfunktionswert $b^\top y = \frac{184}{108} = \frac{46}{27}$):
   $$y = \Big(\underbrace{\tfrac{1}{12}}_{\text{pair}_{LL}},\; \underbrace{\tfrac{5}{24}}_{\text{pair}_{LH}},\; \underbrace{\tfrac{1}{12}}_{\text{pair}_{HH}},\; \underbrace{\tfrac{1}{2}}_{\text{light\_pts}},\; \underbrace{\tfrac{1}{4}}_{\text{heavy\_sym}},\; \underbrace{\tfrac{1}{2}}_{\text{trip}_{LLL}},\; \underbrace{\tfrac{3}{8}}_{\text{trip}_{LLH}},\; \underbrace{\tfrac{1}{4}}_{\text{trip}_{LHH}},\; \underbrace{\tfrac{1}{4}}_{\text{trip}_{HHH}}\Big).$$
2. **`1P_LH`-freie Unterfamilie (ohne gemischte `1P_LH`-Geraden):** Schließt man `1P_LH`-Geraden aus (`L_1LH = H_1LH = 0`), steigt das exakte Minimum auf **$\frac{49}{27} \approx 1{,}814815$**.
   *Exaktes Dual-Zertifikat* (benötigt nicht einmal `light_pts` oder `heavy_sym`; alle $17$ erlaubten Variablen erfüllen $(A^\top y)_j \le 1$, $b^\top y = \frac{3+12+12+6+12+4}{27} = \frac{49}{27}$):
   $$y = \Big(\underbrace{\tfrac{1}{3}}_{\text{pair}_{LL}},\; \underbrace{\tfrac{1}{3}}_{\text{pair}_{LH}},\; \underbrace{\tfrac{1}{3}}_{\text{pair}_{HH}},\; \underbrace{0}_{\text{light}},\; \underbrace{0}_{\text{heavy}},\; \underbrace{0}_{\text{trip}_{LLL}},\; \underbrace{1}_{\text{trip}_{LLH}},\; \underbrace{1}_{\text{trip}_{LHH}},\; \underbrace{\tfrac{1}{2}}_{\text{trip}_{HHH}}\Big).$$
3. **Abhängigkeit von $\ell$:** Für jede symmetrische Light+Heavy-Zerlegung mit $3\ell \le 1$ (höchstens $q - 1$ leichte Ebenen) erzwingen bereits `Typ 0` auf den nicht-schweren Ebenen und `Typ 1` auf $z^*$ die triviale Skelett-Schranke $m / q^3 \ge 1 + (1 - \ell) = 2 - \ell \ge \frac{5}{3} = \frac{45}{27}$ (für $\ell < \frac{8}{27}$ bereits $> \frac{46}{27}$).

### 4.2 Reichweite der Schranken & Ausbruchswege (Übergang zu AP 3)
Die Schranken `46/27` und `49/27` gelten **nicht** für allgemeine Vertreterlisten $R_3 \subseteq \mathbb{F}_q^6$, sondern **ausschließlich** unter zwei starken strukturellen Annahmen:
1. **Horizontale-Ebenen-Skelett für `Typ 1`:** Jedes Symbol besitzt eine horizontale $z$-Ebene (erzwingt bereits $m \ge \frac{5}{3}q^3 = \frac{45}{27}q^3$). Um unter $\frac{45}{27}$ bzw. $\frac{46}{27}$ zu gelangen, müssten `Typ 1`-Fasern echte nicht-horizontale 3D-Linien-Blocking-Sets sein (z. B. 2D-Baer-Zylinder der Größe $q^2 + q^{3/2}$).
2. **`x`-Geraden-Skelett für `Typ 2`:** Jedes Symbolpaar wird über eine volle $x$-Gerade abgedeckt. Ersetzt man auf den $q - 1$ leichten Ebenen die `x`-Geraden durch **2D-Baer-Gitter** (sodass ein Paar $(a, b)$ auf Ebene $z_a$ über eine 2D-Baer-Unterebene der Größe $q + \sqrt{q}$ statt einer $x$-Geraden abgedeckt wird), ist das `x`-Geraden-LP (`49/27` und die zyklische `19/10`-Konstruktion) **ausgehebelt** — genau dies untersucht AP 3 in [`M3_BAER_PILOT_REPORT.md`](M3_BAER_PILOT_REPORT.md).
