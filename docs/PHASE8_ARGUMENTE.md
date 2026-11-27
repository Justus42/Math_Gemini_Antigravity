# Phase 8: Mathematische Argumente zur Konstruktion ohne Vollgeraden

- **Status / Belegart (`RULES.md`, Abschnitt „Meldung nach außen“: Regel 2d, Wortwahl nach Regel 4):** Informelles Argument. Ausgearbeitet von Gemini (Planerrolle) und gegengelesen vom Phase-8-Erzeugerchat (Claude). Eine Prüfung durch ein unbeteiligtes Drittmodell nach Regel 2d steht aus.
- **Kein Neuheitsanspruch:** Die Aussagen ordnen ausschließlich die Blockzahl $m = |R|$ im Nebenklassen-Modell $K_t$ (Tabelle $M(R)$ gemischter Stärke 2) ein; eine Literaturprüfung nach Regel 2c steht gesondert aus.

---

## Rahmen und Notation

Sei $q$ eine Primzahlpotenz, $2 \le v \le q$ und $V = \{0, \dots, v-1\}$. Eine Vertreterliste $R$ ist eine endliche Multimenge von Tupeln $(c, d, a, b) \in \mathbb{F}_q^2 \times V^2$. Die Tabelle $M(R)$ hat $|R|$ Zeilen und $q+2$ Spalten mit Einträgen
$$
\bigl((c + \alpha d)_{\alpha \in \mathbb{F}_q},\; a,\; b\bigr).
$$
Nach Aussage A / A' (Phase 7, `docs/PHASE7_T2_REDUCTION.md`) erzeugt der Nebenklassen-Lift $L_t^\pi(R)$ ein $\mathrm{CA}(|R|\,q^{t-2};\, t, q+2, v)$ für alle $2 \le t \le q+2$, sobald $M(R)$ gemischte Stärke 2 besitzt (Alphabet $\mathbb{F}_q$ in den $q$ Auswertungsspalten, Alphabet $V$ in den Spalten $a, b$).

Die Stärke-2-Bedingung an $M(R)$ zerfällt in drei Bedingungen an $R$:
1. **Punktabdeckung:** Jedes Paar $(c, d) \in \mathbb{F}_q^2$ kommt mindestens einmal als Projektion in $R$ vor (äquivalent zur Abdeckung aller Paare zwischen zwei beliebigen Auswertungsspalten $\alpha_1 \neq \alpha_2$).
2. **Geradentreffer (Inzidenz):** Für jedes $s \in V$ bezeichne $A_s = \{(c, d) \in \mathbb{F}_q^2 : \exists\, b \text{ mit } (c, d, s, b) \in R\}$ und $B_s = \{(c, d) \in \mathbb{F}_q^2 : \exists\, a \text{ mit } (c, d, a, s) \in R\}$. Jede nicht-waagerechte affine Gerade
   $$
   L_{\alpha, u} = \{(c, d) \in \mathbb{F}_q^2 : c + \alpha d = u\} \qquad (\alpha, u \in \mathbb{F}_q)
   $$
   muss jede Menge $A_s$ und jede Menge $B_s$ mindestens einmal treffen.
3. **Symbolpaare:** Jedes Paar $(a, b) \in V^2$ kommt mindestens einmal in $R$ vor.

Im Folgenden bezeichnet $\square_0 = \{x^2 : x \in \mathbb{F}_q\}$ die Menge der Quadrate samt $0$ und $\square^\times = \square_0 \setminus \{0\}$.

---

## 1.1 Dichotomie über blockierende Mengen in $\mathrm{PG}(2, q)$

**Aussage 1.1.** *Sei $q$ eine Primzahlpotenz und $A \subseteq \mathbb{F}_q^2$ eine Punktmenge, die jede Gerade $L_{\alpha, u}$ ($\alpha, u \in \mathbb{F}_q$) trifft. Dann gilt eine der beiden Möglichkeiten:*
1. *$A$ enthält eine vollständige waagerechte Gerade $H_{d^*} = \{(c, d^*) : c \in \mathbb{F}_q\}$ für ein $d^* \in \mathbb{F}_q$;*
2. *oder $|A| \ge q + \sqrt{q}$ (Bruen), und falls $q$ eine Primzahl ist, sogar $|A| \ge \frac{3q+1}{2}$ (Blokhuis).*

**Argument.** Bette $\mathrm{AG}(2, q) = \mathbb{F}_q^2$ in die projektive Ebene $\mathrm{PG}(2, q)$ mit Ferngerade $L_\infty$ ein. Die Parallelschar der waagerechten Geraden $H_d$ ($d \in \mathbb{F}_q$) schneidet $L_\infty$ in einem gemeinsamen Fernpunkt $P_\infty$. Setze $B := A \cup \{P_\infty\}$.

- Jede nicht-waagerechte affine Gerade $L_{\alpha, u}$ trifft $A$, also trifft ihr projektiver Abschluss $B$.
- Jede waagerechte projektive Gerade $\overline{H_d}$ sowie $L_\infty$ enthält $P_\infty \in B$.

Damit ist $B$ eine blockierende Menge in $\mathrm{PG}(2, q)$. Da $B \cap L_\infty = \{P_\infty\}$, kann $B$ weder $L_\infty$ noch den projektiven Abschluss einer nicht-waagerechten Geraden enthalten (deren Fernpunkt liegt in $L_\infty \setminus \{P_\infty\}$). Enthält $B$ eine projektive Gerade, muss es sich also um eine waagerechte Gerade $\overline{H_{d^*}}$ handeln, d. h. $H_{d^*} \subseteq A$ (Fall 1).

Enthält $A$ keine volle waagerechte Gerade, ist $B$ eine nicht-triviale blockierende Menge in $\mathrm{PG}(2, q)$. Nach dem Satz von Bruen (1970) gilt $|B| \ge q + \sqrt{q} + 1$, also $|A| \ge q + \sqrt{q}$. Ist $q$ eine Primzahl, liefert der Satz von Blokhuis (1994) $|B| \ge \frac{3(q+1)}{2}$, also $|A| \ge \frac{3q+1}{2}$. $\square$

---

## 1.2 Allgemeine Klassen-Regel für ungerade Primzahlpotenzen $q$

Sei $q$ eine ungerade Primzahlpotenz und $n_0 \in \mathbb{F}_q^\times \setminus \square_0$ ein festes Nichtquadrat. Definiere
$$
\Delta := \left\{\frac{1}{s - n_0} : s \in \square_0\right\} \subseteq \mathbb{F}_q^\times, \qquad d_0 := -\frac{1}{n_0} \in \Delta, \qquad O := (0, d_0).
$$
Da $s \mapsto (s - n_0)^{-1}$ injektiv auf $\square_0$ ist (wegen $n_0 \notin \square_0$), gilt $|\Delta| = |\square_0| = \frac{q+1}{2}$ und $0 \notin \Delta$. Ferner gilt für jedes $d \in \Delta$:
$$
\frac{1}{d} + n_0 = s \in \square_0 \qquad \text{sowie} \qquad n_0(d - d_0) = n_0 d + 1 = s d.
$$

Für jedes $e \in \mathbb{F}_q^\times$ (die Menge hängt nur von $\{e, -e\}$ ab, es gibt also $\frac{q-1}{2}$ Klassen) definiere $A(e) := A_\Delta(e) \cup A_0(e) \subseteq \mathbb{F}_q^2$ durch
$$
A_\Delta(e) := \bigl\{(\epsilon\, e\, n_0(d - d_0),\; d) : d \in \Delta,\; \epsilon \in \{+1, -1\}\bigr\},
$$
$$
A_0(e) := \bigl\{(p, 0) : p \in \mathbb{F}_q,\; p^2 - e^2 \in \square_0\bigr\}.
$$

**Aussage 1.2.** *Für jede ungerade Primzahlpotenz $q$ und jedes $e \in \mathbb{F}_q^\times$ gilt:*
1. *$|A_0(e)| = \frac{q+1}{2}$, $|A_\Delta(e)| = q$ und $|A(e)| = \frac{3q+1}{2}$.*
2. *$A(e)$ trifft jede Gerade $L_{\alpha, u}$ ($\alpha, u \in \mathbb{F}_q$).*
3. *Für $e_1, e_2 \in \mathbb{F}_q^\times$ mit $e_1 \neq \pm e_2$ gilt $A_\Delta(e_1) \cap A_\Delta(e_2) = \{O\}$.*

**Argument.**

*Zu (1):* Für $p \in \mathbb{F}_q$ gilt $p^2 - e^2 = y^2 \iff (p - y)(p + y) = e^2$. Mit $t := p - y \in \mathbb{F}_q^\times$ folgt $p + y = e^2/t$, also $p = \frac{1}{2}(t + e^2/t)$ (char $\mathbb{F}_q \neq 2$). Umgekehrt liefert jedes $t \in \mathbb{F}_q^\times$ eine Lösung $(p, y) = \bigl(\frac{t + e^2/t}{2}, \frac{e^2/t - t}{2}\bigr)$, und $t_1 + e^2/t_1 = t_2 + e^2/t_2 \iff (t_1 - t_2)(t_1 t_2 - e^2) = 0 \iff t_2 \in \{t_1, e^2/t_1\}$. Die Involution $t \mapsto e^2/t$ auf $\mathbb{F}_q^\times$ besitzt genau zwei Fixpunkte ($t = \pm e$) und $\frac{q-3}{2}$ Zweierbahnen; daher ist $|A_0(e)| = 2 + \frac{q-3}{2} = \frac{q+1}{2}$.

Auf $\Delta$: Für $d = d_0$ gilt $n_0(d_0 - d_0) = 0$, also genau ein Punkt $O = (0, d_0)$. Für jedes der $\frac{q-1}{2}$ Elemente $d \in \Delta \setminus \{d_0\}$ ist $e n_0(d - d_0) \neq 0$, also entstehen wegen char $\mathbb{F}_q \neq 2$ genau zwei Punkte $(\pm e n_0(d - d_0), d)$. Somit ist $|A_\Delta(e)| = 1 + 2\cdot\frac{q-1}{2} = q$. Da $0 \notin \Delta$, sind $A_\Delta(e)$ und $A_0(e)$ disjunkt, also $|A(e)| = \frac{3q+1}{2}$.

*Zu (2):* Betrachte eine beliebige Gerade $L_{\alpha, u}: c + \alpha d = u$.
- **Fall A ($u^2 - e^2 \in \square_0$):** Dann liegt $(u, 0) \in A_0(e)$ auf $L_{\alpha, u}$.
- **Fall B ($u^2 - e^2 \notin \square_0$, insbesondere $u \neq \pm e$):**
  - Ist $\alpha + n_0 u = 0$, gilt $0 + \alpha d_0 = -\alpha/n_0 = u$, also liegt $O = (0, d_0) \in A_\Delta(e)$ auf $L_{\alpha, u}$.
  - Sei nun $\alpha + n_0 u \neq 0$. Ein Punkt $(\epsilon e (n_0 d + 1), d)$ mit $\epsilon \in \{\pm 1\}$ liegt genau dann auf $L_{\alpha, u}$, wenn
    $$
    (\alpha + \epsilon e n_0)\, d = u - \epsilon e.
    $$
    Da $u - \epsilon e \neq 0$, liefert jedes $\epsilon \in \{\pm 1\}$ mit $\alpha + \epsilon e n_0 \neq 0$ eine eindeutige Lösung $d_\epsilon = \frac{u - \epsilon e}{\alpha + \epsilon e n_0} \neq 0$. Es gilt $d_\epsilon \in \Delta$ genau dann, wenn
    $$
    s_\epsilon := \frac{1}{d_\epsilon} + n_0 = \frac{\alpha + \epsilon e n_0}{u - \epsilon e} + n_0 = \frac{\alpha + n_0 u}{u - \epsilon e} \in \square_0.
    $$
    - *Unterfall B1:* Ein Koeffizient verschwindet, etwa $\alpha + \epsilon e n_0 = 0$ für ein $\epsilon \in \{\pm 1\}$. Da $2 e n_0 \neq 0$, verschwindet der andere Koeffizient nicht; zudem ist $\alpha + n_0 u = n_0(u - \epsilon e)$, also
      $$
      s_{-\epsilon} = \frac{n_0(u - \epsilon e)}{u + \epsilon e} = \frac{n_0(u - \epsilon e)^2}{u^2 - e^2}.
      $$
      Als Quotient zweier Nichtquadrate ($n_0 \notin \square_0$ und $u^2 - e^2 \notin \square_0$) multipliziert mit einem von $0$ verschiedenen Quadrat ist $s_{-\epsilon} \in \square^\times$, also $d_{-\epsilon} \in \Delta$.
    - *Unterfall B2:* Beide Koeffizienten $\alpha \pm e n_0$ sind ungleich $0$. Dann sind $s_+$ und $s_-$ beide ungleich $0$ und erfüllen
      $$
      s_+ s_- = \frac{(\alpha + n_0 u)^2}{u^2 - e^2} \notin \square_0.
      $$
      Folglich ist genau eines der beiden Elemente $s_+, s_-$ ein Quadrat in $\mathbb{F}_q^\times$, sodass genau eines der beiden $d_+, d_-$ in $\Delta$ liegt.

In jedem Fall trifft $L_{\alpha, u}$ die Menge $A(e)$.

*Zu (3):* Für $d \in \Delta \setminus \{d_0\}$ ist $n_0(d - d_0) \neq 0$. Aus $\epsilon_1 e_1 n_0(d - d_0) = \epsilon_2 e_2 n_0(d - d_0)$ folgt $e_1 = \pm e_2$. Also sind die Klassen auf jeder Geraden $d \in \Delta \setminus \{d_0\}$ paarweise disjunkt und teilen sich auf $\Delta$ nur den Punkt $O = (0, d_0)$. $\square$

---

## 1.3 Skelett, Packungsbedingung und Belegbarkeit der schweren Geraden ($v \le q$)

Sei $q$ eine ungerade Primzahlpotenz, $2 \le v \le q$ und $j \ge 0$ eine ganze Zahl mit
$$
x_b := \frac{q+1}{2} + j \le \min(v - 1, q - 1), \qquad x_a := q - 1 - x_b = \frac{q-3}{2} - j.
$$
Setze $h_a := v - x_a$ (schwere $a$-Symbole $H_a$) und $h_b := v - x_b$ (schwere $b$-Symbole $H_b$). Für $v = q$ gilt $h_a = x_b + 1 = \frac{q+3}{2} + j$ und $h_b = q - x_b = \frac{q-1}{2} - j$, also $h_a - h_b = 2 + 2j$. Allgemein für $v \le q$ gilt
$$
h_a - h_b = x_b - x_a = 2 + 2j, \qquad h_b = v - \frac{q+1}{2} - j \le \frac{q-1}{2} - j \lt \frac{q+1}{2}.
$$
Die Bedingung $x_b \le v - 1$ bedeutet $h_b \ge 1$. Sie wird unten zweimal gebraucht: für die Kantenfärbung mit $h_b$ Farben und dafür, dass an jedem Punkt von $d = 0$ mindestens ein Vertreter liegt ($m(p) \ge h_b \ge 1$). Aus $x_b \le q - 1$ folgt $x_a \ge 0$; aus $h_a = h_b + 2 + 2j \ge 3$ folgt $x_a = v - h_a \lt v$.

Wähle eine Menge $S \subseteq \mathbb{F}_q^\times / \{\pm 1\}$ mit $n := |S|$ unter der Packungsbedingung
$$
1 \le n \le \min\bigl(q - h_a,\; h_a,\; \tfrac{q-1}{2}\bigr)
$$
(für $v = q$ ist $q - h_a = x_a = \frac{q-3}{2} - j$; für $v \lt q$ lockert sich $q - h_a = x_a + (q - v)$).

**Konstruktion von $R$:**
1. **Reine $a$-Geraden ($x_a$ Geraden $d \notin \Delta \cup \{0\}$):** Je ein reines $a$-Symbol $a_d \in V \setminus H_a$; Vertreter $(c, d, a_d, \pi(c))$ für alle $c \in \mathbb{F}_q$ (wobei $\pi: \mathbb{F}_q \to V$ surjektiv ist). Dies deckt alle Paare $(a_d, b)$ für $b \in V$, die volle Gerade $H_d$ für $a_d$ und alle Punkte der Geraden.
2. **Reine $b$-Geraden ($x_b$ Geraden: $\Delta$ plus $j$ weitere Geraden $d \neq 0$):** Je ein reines $b$-Symbol $b_d \in V \setminus H_b$.
   - Auf $d = d_0$: am Punkt $O = (0, d_0)$ stehen die $n$ Vertreter $(0, d_0, a_e, b_{d_0})$ für $e \in S$; die übrigen $h_a - n$ schweren $a$-Symbole werden auf die $q - 1 \ge h_a - n$ Punkte $(c, d_0)$ ($c \neq 0$) verteilt (Rest beliebig mit Symbolen aus $H_a$).
   - Auf jedem $d \in \Delta \setminus \{d_0\}$: die $2n$ disjunkten Klassenpunkte $(\pm e n_0(d - d_0), d)$ erhalten $(c, d, a_e, b_d)$; die übrigen $h_a - n$ schweren $a$-Symbole passen ohne Mehrfachbelegung auf die verbleibenden $q - 2n$ Punkte, weil $h_a - n \le q - 2n \iff n \le q - h_a$.
   - Auf den $j$ übrigen reinen $b$-Geraden: alle $h_a \le q$ schweren $a$-Symbole kommen mindestens einmal vor.
   Damit sind alle Paare $(a, b_d)$ für $a \in H_a$, alle vollen Geraden für die reinen $b$-Symbole, alle Punkte außerhalb $d = 0$ sowie die $\Delta$-Anteile aller Klassen $A(e)$ ($e \in S$) abgedeckt.
3. **Schwere Gerade $d = 0$:** Auf $d = 0$ müssen abgedeckt werden:
   - jedes schwere $a$-Symbol aus $H_a \setminus S$ an allen $q$ Punkten (volle Gerade $H_0$);
   - jedes Klassen-Symbol $a_e$ ($e \in S$) an allen Punkten $(p, 0) \in A_0(e)$;
   - jedes schwere $b$-Symbol $b \in H_b$ an allen $q$ Punkten (volle Gerade $H_0$);
   - jedes Paar $(a, b) \in H_a \times H_b$ mindestens einmal.

Definiere für jedes $p \in \mathbb{F}_q$ die Anzahl der entfallenden Klassen-Symbole
$$
\mathrm{adel}(p) := \bigl|\{e \in S : p^2 - e^2 \notin \square_0\}\bigr|
$$
und die geforderte Symbolmenge $A_{\mathrm{req}}(p) := (H_a \setminus S) \cup \{a_e : e \in S,\; p^2 - e^2 \in \square_0\}$ der Größe $h_a - \mathrm{adel}(p)$.

**Aussage 1.3 (Belegbarkeit von $d = 0$).** *Für alle Parameter wie oben lässt sich die Gerade $d = 0$ mit exakt*
$$
M_0 = \sum_{p \in \mathbb{F}_q} \max\bigl(h_a - \mathrm{adel}(p),\; h_b\bigr) = q h_a - \sum_{p \in \mathbb{F}_q} \min\bigl(\mathrm{adel}(p),\; 2 + 2j\bigr)
$$
*Vertretern so belegen, dass alle Bedingungen an $d = 0$ erfüllt sind. Insgesamt gilt*
$$
|R| = q(v + x_b) - \sum_{p \in \mathbb{F}_q} \min\bigl(\mathrm{adel}(p),\; 2 + 2j\bigr) + (n - 1).
$$

**Argument.** Setze $m(p) := \max(|A_{\mathrm{req}}(p)|, h_b)$. Da stets $h_b \lt h_a$, lässt sich $A_{\mathrm{req}}(p)$ im Fall $|A_{\mathrm{req}}(p)| \lt h_b$ beliebig zu einer Teilmenge $A^*(p) \subseteq H_a$ der Größe $h_b$ erweitern; sonst setze $A^*(p) := A_{\mathrm{req}}(p)$. Dann ist $|A^*(p)| = m(p) \ge h_b \ge 1$ für alle $p \in \mathbb{F}_q$.

Betrachte den bipartiten Graphen $G = (H_a, \mathbb{F}_q; E)$ mit Kante $(a, p) \in E \iff a \in A^*(p)$ und $|E| = \sum_{p \in \mathbb{F}_q} m(p) = M_0$. Seine Knotengrade erfüllen:
- $\deg_G(p) = m(p) \ge h_b$ für alle $p \in \mathbb{F}_q$;
- $\deg_G(a) = q \ge h_b$ für alle $a \in H_a \setminus S$;
- $\deg_G(a_e) \ge |A_0(e)| = \frac{q+1}{2} \gt \frac{q-1}{2} - j \ge h_b$ für alle $e \in S$.

Also hat $G$ Minimalgrad $\delta(G) \ge h_b$. Spalte jeden Knoten $x \in H_a \cup \mathbb{F}_q$ in einen Hauptknoten $x_0$ vom Grad exakt $h_b$ und weitere Restknoten vom Grad $\le h_b$ auf (die inzidenten Kanten von $x$ werden beliebig partitioniert). Der entstehende bipartite Graph $G'$ hat Maximalgrad $\Delta(G') = h_b$. Nach dem Kantenfärbungssatz von König (1916) besitzt $G'$ eine zulässige Kantenfärbung $c: E(G') \to H_b$ mit $h_b$ Farben (equivalenterweise folgt dies direkt aus dem Satz von Gupta 1967 zur Kantenüberdeckungszahl bipartiter Graphen).

Lege auf $d = 0$ für jede Kante $(a, p) \in E(G)$ den Vertreter $(p, 0, a, c(a, p))$ ab.
- Da jeder Hauptknoten $p_0$ Grad $h_b$ hat und alle $h_b$ inzidenten Kanten verschiedene Farben tragen, kommt am Punkt $(p, 0)$ jedes $b \in H_b$ mindestens einmal vor.
- Da jeder Hauptknoten $a_0$ Grad $h_b$ hat und alle $h_b$ inzidenten Kanten verschiedene Farben tragen, kommt für jedes $a \in H_a$ jedes Paar $(a, b) \in H_a \times H_b$ mindestens einmal vor.
- Nach Konstruktion von $A^*(p) \supseteq A_{\mathrm{req}}(p)$ sind alle geforderten $a$-Symbole an jedem Punkt $(p, 0)$ vorhanden.

Gesamtzählung: $x_a q$ Vertreter auf reinen $a$-Geraden, $x_b q + (n - 1)$ auf reinen $b$-Geraden (Mehrfachbelegung nur bei $O$ mit $n \ge 1$ Vertretern) und $M_0 = q h_a - \sum_p \min(\mathrm{adel}(p), h_a - h_b)$ auf $d = 0$. Mit $x_a + h_a = v$ ergibt dies $(v + x_b)q - \sum_p \min(\mathrm{adel}(p), 2 + 2j) + (n - 1)$ (für $v = q$: $q^2 + q x_b - \sum_p \min(\mathrm{adel}(p), 2+2j) + (n-1)$). $\square$

*(Anmerkung zum Randfall $n = 0$: Bei $n = 0$ entfällt die Mehrfachbelegung bei $O$, der Term $(n - 1)$ wird durch $0$ ersetzt.)*

---

## 1.4 Charakter-Summe, geschlossene Formel (a) und Asymptotik $7/5$ im Ein-$\Delta$-Skelett mit symmetrischen Klassen $A(e)$ um einen gemeinsamen Punkt $O$ ($v = q$)

Sei $q$ eine ungerade Primzahlpotenz, $v = q$, $\chi: \mathbb{F}_q \to \{-1, 0, 1\}$ der quadratische Charakter ($\chi(0) = 0$) und $N_0 := \frac{q-1}{2}$.

**Hilfssatz (Volle Streichungszahl).** *Für $S_{\mathrm{all}} = \mathbb{F}_q^\times / \{\pm 1\}$ gilt:*
- *Für $p = 0$: $\mathrm{adel}_{\mathrm{all}}(0) = N_0$ falls $q \equiv 3 \pmod 4$, und $\mathrm{adel}_{\mathrm{all}}(0) = 0$ falls $q \equiv 1 \pmod 4$.*
- *Für jedes $p \in \mathbb{F}_q^\times$: $\mathrm{adel}_{\mathrm{all}}(p) = \frac{q - 2 + \chi(-1)}{4}$ (d. h. $\frac{q-3}{4}$ bei $q \equiv 3 \pmod 4$ und $\frac{q-1}{4}$ bei $q \equiv 1 \pmod 4$).*

**Argument.** Für $p = 0$ ist $0^2 - e^2 = -e^2$, also $\chi(-e^2) = \chi(-1)$. Für $p \neq 0$ ergibt die Substitution $e = px$:
$$
\sum_{e \in \mathbb{F}_q} \chi(p^2 - e^2) = \sum_{x \in \mathbb{F}_q} \chi(1 - x^2).
$$
Für $x \neq 1$ setze $t = \frac{1 + x}{1 - x} \in \mathbb{F}_q \setminus \{-1\}$; dann ist $1 - x^2 = (1 - x)^2 t$, also $\chi(1 - x^2) = \chi(t)$. Summieren über $t \in \mathbb{F}_q \setminus \{-1\}$ ergibt $\sum_{t \in \mathbb{F}_q} \chi(t) - \chi(-1) = -\chi(-1)$.
Da $e = 0$ den Beitrag $\chi(p^2) = 1$ liefert und $e = \pm p$ den Beitrag $0$, folgt
$$
\sum_{e \in \mathbb{F}_q^\times \setminus \{\pm p\}} \chi(p^2 - e^2) = -\chi(-1) - 1.
$$
Unter den $q - 3$ Werten $e \in \mathbb{F}_q^\times \setminus \{\pm p\}$ sei $Q_+$ die Anzahl mit $\chi(p^2 - e^2) = 1$ und $Q_-$ die Anzahl mit $\chi(p^2 - e^2) = -1$. Aus $Q_+ + Q_- = q - 3$ und $Q_+ - Q_- = -1 - \chi(-1)$ folgt $Q_- = \frac{q - 2 + \chi(-1)}{2}$. Wegen Symmetrie $e \leftrightarrow -e$ ist $\mathrm{adel}_{\mathrm{all}}(p) = \frac{Q_-}{2} = \frac{q - 2 + \chi(-1)}{4}$. $\square$

### Geschlossene Formel (a)
Wählt man eine beliebige Teilmenge $S$ der Größe $n = \frac{q-3}{2} - j$, werden genau $N_0 - n = j + 1$ Paare weggelassen. Daher sinkt $\mathrm{adel}(p)$ gegenüber $\mathrm{adel}_{\mathrm{all}}(p)$ um höchstens $j + 1$:
$$
\mathrm{adel}(p) \ge \mathrm{adel}_{\mathrm{all}}(p) - (j + 1) \qquad (p \neq 0).
$$
Die Kappung $2 + 2j$ ist an allen $p \neq 0$ automatisch erreicht, sobald $\mathrm{adel}_{\mathrm{all}}(p) - (j + 1) \ge 2 + 2j \iff 3j + 3 \le \mathrm{adel}_{\mathrm{all}}(p)$, also:
- **$q \equiv 3 \pmod 4$:** $3j + 3 \le \frac{q-3}{4} \iff 0 \le j \le \frac{q-15}{12}$. Da zudem $\mathrm{adel}(0) = n \ge 2 + 2j$ für dieses $j$ (für $q \ge 15$ gilt $n = \frac{q-3}{2} - j \ge 2 + 2j \iff j \le \frac{q-7}{6}$), erreicht jedes $p \in \mathbb{F}_q$ die Kappung $2 + 2j$. Einsetzen in Aussage 1.3 liefert
  $$
  |R| = q^2 + q\left(\frac{q+1}{2} + j\right) - q(2 + 2j) + \left(\frac{q-5}{2} - j\right) = q^2 + \binom{q}{2} - q(1 + j) + \frac{q-5}{2} - j.
  $$
- **$q \equiv 1 \pmod 4$:** $3j + 3 \le \frac{q-1}{4} \iff 0 \le j \le \frac{q-13}{12}$. Hier gilt $\mathrm{adel}(0) = 0$, sodass die Streichungssumme $(q - 1)(2 + 2j)$ statt $q(2 + 2j)$ beträgt — also exakt $+(2 + 2j)$ mehr als im Fall $q \equiv 3 \pmod 4$.

### Scharfe Asymptotik $\frac{7}{5} q^2$ innerhalb des Ein-$\Delta$-Skeletts mit symmetrischen Klassen $A(e)$ um einen gemeinsamen Punkt $O$
**Aussage 1.4.** *Für jede ungerade Primzahlpotenz $q \ge 11$ existiert im Skelett aus 1.3 (mit $v = q$ und den Klassen $A(e)$ aus 1.2 um den gemeinsamen Punkt $O$) ein Parameter $j$ und eine Wahl $S$ mit*
$$
|R| \le \frac{7}{5} q^2 + \frac{1}{4\sqrt{2}}\, q^{3/2} + 2q.
$$
*Umgekehrt erfüllt jede Wahl von $j \ge 0$ und $S$ ($|S| = n \le \frac{q-3}{2} - j$) in diesem Skelett mit diesen Klassen*
$$
|R| \ge \frac{7}{5} q^2 - \frac{3}{2} q.
$$

*Abgrenzung.* Beide Schranken gelten nur für diese Bauart. Verschobene Klassen, unsymmetrische Steigungspaare und Klassen aus Baer-Unterebenen sind nicht erfasst; die Untergrenze ist also kein Boden für das Modell $M(R)$ insgesamt.

**Argument.**
*Obergrenze (probabilistische Methode):* Setze $j := \lfloor (q - 11)/10 \rfloor \ge 0$, $n := \frac{q-3}{2} - j$, $C := 2 + 2j$, und wähle $S \subseteq \mathbb{F}_q^\times / \{\pm 1\}$ mit $|S| = n$ gleichverteilt zufällig. Für jedes feste $p \in \mathbb{F}_q^\times$ ist $X_p := \mathrm{adel}(p)$ hypergeometrisch verteilt mit Parametern $(N_0, K, n)$, wobei $K = \mathrm{adel}_{\mathrm{all}}(p) = \frac{q - 2 + \chi(-1)}{4}$.
- Erwartungswert: $\mu = \frac{n K}{N_0} \in \bigl[\frac{n}{2} - \frac{1}{2},\; \frac{n}{2}\bigr]$. Da $10j \le q - 11$, gilt $\frac{n}{2} = \frac{q - 3 - 2j}{4} \ge 2 + 2j = C$, also $\min(\mu, C) \ge C - \frac{1}{2}$.
- Varianz: $\mathrm{Var}(X_p) = n \frac{K}{N_0}\bigl(1 - \frac{K}{N_0}\bigr)\frac{N_0 - n}{N_0 - 1} \le \frac{n}{4} \lt \frac{q}{8}$, also $\sigma_p := \sqrt{\mathrm{Var}(X_p)} \lt \sqrt{q/8}$.

Aus $\min(X_p, C) = \frac{X_p + C - |X_p - C|}{2}$, der Dreiecksungleichung $|X_p - C| \le |X_p - \mu| + |\mu - C|$ und Cauchy-Schwarz $\mathbb{E}[|X_p - \mu|] \le \sigma_p$ folgt für jedes $p \neq 0$:
$$
\mathbb{E}[\min(X_p, C)] \ge \frac{\mu + C - |\mu - C| - \sigma_p}{2} = \min(\mu, C) - \frac{\sigma_p}{2} \ge C - \frac{1}{2} - \frac{\sqrt{q/8}}{2}.
$$
Summieren über alle $q - 1$ Punkte $p \neq 0$ (mit $\min(\mathrm{adel}(0), C) \ge 0$) garantiert die Existenz mindestens einer Auswahl $S$ mit
$$
G = \sum_{p \in \mathbb{F}_q} \min(\mathrm{adel}(p), C) \ge (q - 1)\left(2j + \frac{3}{2} - \frac{\sqrt{q}}{4\sqrt{2}}\right).
$$
Einsetzen in Aussage 1.3 und Verwenden von $j \ge \frac{q - 20}{10}$ (also $-qj \le -\frac{q^2}{10} + 2q$) sowie $2j + n = \frac{q-3}{2} + j \le \frac{3}{5} q - \frac{13}{5}$ liefert:
$$
|R| \le \frac{3}{2} q^2 - qj + \frac{q}{2} - \frac{3}{2} q + \frac{3}{2} + 2j + n - 1 + \frac{q - 1}{4\sqrt{2}}\sqrt{q} \le \frac{7}{5} q^2 + \frac{1}{4\sqrt{2}}\, q^{3/2} + 2q.
$$

*Untergrenze im selben Skelett:* Jede Klasse $e \in S$ streicht genau $\frac{q-1}{2}$ Punkte auf $d = 0$; zugleich greift an jedem der $q$ Punkte die Kappung $2 + 2j$. Also ist
$$
G \le \min\left(q(2 + 2j),\; n\cdot\frac{q-1}{2}\right) \le \min\left(2q + 2qj,\; \left(\frac{q-3}{2} - j\right)\frac{q-1}{2}\right).
$$
Damit gilt $|R| \ge \frac{3}{2} q^2 + \frac{q}{2} + qj - \min\bigl(2q + 2qj,\; (\frac{q-3}{2} - j)\frac{q-1}{2}\bigr)$. Der Ausdruck fällt linear in $j$ links vom Schnittpunkt und steigt linear in $j$ rechts davon; das Minimum über $j \in \mathbb{R}$ liegt im Schnittpunkt $j^* = \frac{q^2 - 12q + 3}{2(5q - 1)} \lt \frac{q}{10}$. Einsetzen liefert $|R| \ge \frac{3}{2} q^2 - \frac{3}{2} q - q j^* \ge \frac{7}{5} q^2 - \frac{3}{2} q$. $\square$

---

## 1.5 Vollgeraden-Untergrenze ($v = q$)

**Aussage 1.5.** *Sei $q \ge 2$ eine ganze Zahl und $R$ eine endliche Multimenge von Tupeln $(c, d, a, b) \in \{0, \dots, q-1\}^4$ mit folgenden Eigenschaften:*
1. *Jeder Punkt $(c, d)$ kommt mindestens einmal in $R$ vor.*
2. *Jedes Paar $(a, b)$ kommt mindestens einmal in $R$ vor.*
3. *Jede $a$-Klasse $A_s$ enthält mindestens eine volle waagerechte Gerade $H_{d(s)}$, und jede $b$-Klasse $B_s$ enthält mindestens eine volle waagerechte Gerade $H_{d'(s)}$.*

*Dann gilt $|R| \ge q^2 + \binom{q}{2}$.*

*(Hinweis: Die Voraussetzung an beide Seiten ist wesentlich; die Phase-8-Konstruktion erfüllt (3) nur auf der $b$-Seite und unterschreitet $q^2 + \binom{q}{2}$.)*

**Argument.** Wähle für jedes $a \in \{0, \dots, q-1\}$ eine volle Gerade $d(a)$ und für jedes $b$ eine volle Gerade $d'(b)$. Definiere für jedes $d \in \{0, \dots, q-1\}$ die Mengen $C_d := \{a : d(a) = d\}$ ($c_d := |C_d|$) und $R_d := \{b : d'(b) = d\}$ ($r_d := |R_d|$); es gilt $\sum_d c_d = \sum_d r_d = q$. Bezeichne $M_d$ die Anzahl der Vertreter in $R$ auf der Geraden $d$, sodass $|R| = \sum_d M_d$.

Zerlege $\{0, \dots, q-1\}$ in vier disjunkte Mengen:
$$
D_0 = \{d : c_d = 0, r_d = 0\}, \quad D_a = \{d : c_d \ge 1, r_d = 0\}, \quad D_b = \{d : c_d = 0, r_d \ge 1\}, \quad D_+ = \{d : c_d \ge 1, r_d \ge 1\}.
$$
Setze $\alpha := \sum_{d \in D_a} c_d$, $\beta := \sum_{d \in D_b} r_d$ und $k := |D_+|$. Dann gilt $\sum_{d \in D_+} c_d = q - \alpha$ und $\sum_{d \in D_+} r_d = q - \beta$.

Definiere den nicht-negativen Überschuss $E_d \ge 0$ auf $D_0 \cup D_a \cup D_b$:
- Für $d \in D_0$: $E_d := M_d - q \ge 0$ (nach (1)).
- Für $d \in D_a$: jedes $a \in C_d$ erscheint an allen $q$ Punkten von $H_d$, also $M_d \ge q c_d$ und $E_d := M_d - q c_d \ge 0$.
- Für $d \in D_b$: symmetrisch $E_d := M_d - q r_d \ge 0$.

Setze $E^* := \sum_{d \in D_0 \cup D_a \cup D_b} E_d \ge 0$. Damit ist
$$
|R| = q|D_0| + q\alpha + q\beta + E^* + \sum_{d \in D_+} M_d \implies \sum_{d \in D_+} 2 M_d = 2|R| - 2q|D_0| - 2q\alpha - 2q\beta - 2E^*.
$$

Betrachte nun die Zielmenge der Paare
$$
T := \Bigl(\{0, \dots, q-1\} \setminus \bigcup_{d \in D_a} C_d\Bigr) \times \Bigl(\{0, \dots, q-1\} \setminus \bigcup_{d \in D_b} R_d\Bigr), \qquad |T| = (q - \alpha)(q - \beta).
$$
Wie viele verschiedene Paare aus $T$ deckt jede Gerade $d$ höchstens ab?
- **$d \in D_0$:** höchstens $M_d = q + E_d$ Paare.
- **$d \in D_a$:** die mindestens $q c_d$ Vertreter mit $a \in C_d$ liefern keine Paare in $T$; es bleiben höchstens $M_d - q c_d = E_d$ Paare in $T$.
- **$d \in D_b$:** symmetrisch höchstens $E_d$ Paare in $T$.
- **$d \in D_+$:** zerlege die $M_d$ Vertreter auf $H_d$ nach $a \in C_d$ und $b \in R_d$ in Anzahlen $U_{11}, U_{10}, U_{01}, U_{00}$ mit Summe $M_d$. Die Vertreter in $U_{11}$ decken höchstens $c_d r_d$ verschiedene Paare in $C_d \times R_d$ ab, die übrigen höchstens $M_d - U_{11}$ Paare. Aus $U_{11} + U_{10} \ge q c_d$ und $U_{11} + U_{01} \ge q r_d$ folgt
  $$
  U_{11} + (U_{11} + U_{10} + U_{01}) \ge q(c_d + r_d) \implies U_{11} \ge q(c_d + r_d) - M_d,
  $$
  also deckt $H_d$ höchstens $c_d r_d + (M_d - U_{11}) \le 2 M_d - q(c_d + r_d) + c_d r_d$ verschiedene Paare in $T$ ab.

Nach (2) müssen alle $|T|$ Paare überdeckt werden. Aufsummieren über alle Geraden ergibt:
$$
(q - \alpha)(q - \beta) \le q|D_0| + E^* + \sum_{d \in D_+} 2 M_d - q(2q - \alpha - \beta) + \sum_{d \in D_+} c_d r_d.
$$
Einsetzen von $\sum_{d \in D_+} 2 M_d = 2|R| - 2q|D_0| - 2q\alpha - 2q\beta - 2E^*$ und Kürzen von $-q\alpha - q\beta$ auf beiden Seiten ergibt die Grundungleichung
$$
2|R| \ge 3q^2 + \alpha\beta + q|D_0| + E^* - \sum_{d \in D_+} c_d r_d.
$$

Es bleibt zu zeigen, dass $\Delta_{\mathrm{quad}} := \sum_{d \in D_+} c_d r_d - \alpha\beta - q|D_0| \le q$:
- **Fall $k = 0$ ($D_+ = \emptyset$):** Dann ist $\alpha = \beta = q$ und $\sum_{D_+} c_d r_d = 0$, also $\Delta_{\mathrm{quad}} = -q^2 - q|D_0| \le 0 \le q$ (sogar $|R| \ge 2q^2$).
- **Fall $k \ge 1$:** Wegen $c_d - 1 \ge 0$ und $r_d - 1 \ge 0$ für alle $d \in D_+$ gilt
  $$
  \sum_{d \in D_+} (c_d - 1)(r_d - 1) \le \left(\sum_{d \in D_+} (c_d - 1)\right)\left(\sum_{d \in D_+} (r_d - 1)\right) = (q - \alpha - k)(q - \beta - k).
  $$
  Ausmultiplizieren und Auflösen nach $\sum_{D_+} c_d r_d - \alpha\beta$ mit $s := \alpha + \beta + k$ ergibt
  $$
  \sum_{d \in D_+} c_d r_d - \alpha\beta \le q^2 - q(s - k) - (k - 1)(2q - s).
  $$
  Zudem ist $|D_a| \le \alpha$ und $|D_b| \le \beta$, also $|D_0| = q - |D_a| - |D_b| - k \ge \max(0,\, q - s)$.
  - *Unterfall $s \le q$:* Mit $|D_0| \ge q - s$ folgt
    $$
    \Delta_{\mathrm{quad}} \le q^2 - qs + qk - (k - 1)(2q - s) - q(q - s) = q - (k - 1)(q - s) \le q.
    $$
  - *Unterfall $s \gt q$:* Mit $|D_0| \ge 0$ und $k \le q$ (also $q - k + 1 \ge 1$) folgt
    $$
    \Delta_{\mathrm{quad}} \le q^2 + 2q - qk - (q - k + 1)s = q - (q - k + 1)(s - q) \lt q.
    $$

In allen Fällen gilt $\Delta_{\mathrm{quad}} \le q$ und $E^* \ge 0$, somit
$$
2|R| \ge 3q^2 - q = 2\left(q^2 + \binom{q}{2}\right) \implies |R| \ge q^2 + \binom{q}{2}. \qquad \square
$$

---

## Lesevermerk des Phase-8-Erzeugerchats (Claude), 2026-11-27, 02:16 MEZ

**Einordnung.** Der Text oben stammt von Gemini und ist hier aus zwei eingefügten Teilen zusammengesetzt (Überlappung im Argument zu 1.4 zeilenweise gleich, einmal entfernt; sonst unverändert bis auf die unten vermerkte Nachbesserung an drei Stellen). Der Phase-8-Chat hat die Bauart entwickelt; seine Lesung ist **keine** Prüfung nach Regel 2d (`RULES.md`, Abschnitt „Meldung nach außen“). Belegart aller Aussagen 1.1–1.5 bleibt „Argument“.

**Gelesen und von Hand nachgerechnet, ohne Fehler gefunden:**

- 1.1: Schluss über $B = A \cup \{P_\infty\}$.
- 1.2: Größen; in Fall B die Formel $s_\epsilon = \frac{\alpha + n_0 u}{u - \epsilon e}$, Unterfälle B1 und B2; Teil (3).
- 1.3: Zählung $|R| = q(v + x_b) - G + (n-1)$; Gradbedingungen; Aufspaltung und König.
- 1.4: Hilfssatz mit der Substitution $t = \frac{1+x}{1-x}$; Formel (a) in beiden Restklassen; in der Obergrenze die Schritte $\mu \in [\frac n2 - \frac12, \frac n2]$, $\mathbb{E}[\min(X_p, C)] \ge \min(\mu, C) - \frac{\sigma_p}{2}$ und die Schlussabschätzung ($\frac75 q^2 + 1{,}6\,q - 2{,}1 + \frac{q^{3/2}}{4\sqrt2}$); in der Untergrenze $j^*$ und $j^* < \frac{q}{10}$.
- 1.5: Grundungleichung $2|R| \ge 3q^2 + \alpha\beta + q|D_0| + E^* - \sum_{D_+} c_d r_d$ unabhängig hergeleitet; beide Unterfälle für $\Delta_{\mathrm{quad}} \le q$ nachgerechnet.

**Anmerkungen** (1 bis 3 beziehen sich auf den Stand im Commit `f0d009e` und sind inzwischen eingearbeitet, siehe „Nachbesserung“):

1. **1.3 braucht $h_b \ge 1$**, also $x_b \le v - 1$. Der Text lässt $x_b \le \min(v, q-1)$ zu. Bei $h_b = 0$ gibt es keine Farben, und die Punkte von $d = 0$ sind nicht mehr sicher belegt.
2. **Die Untergrenze in 1.4 betrifft nur die Klassen $A(e)$ aus 1.2 mit gemeinsamem Punkt $O$.** Verschobene Klassen, unsymmetrische Steigungspaare (Listen `R_q11_m170.txt`, `R_q19_m513.txt`) und Klassen anderer Art bei Primzahlpotenzen (Baer-Unterebenen, Liste `R_q9_m113.txt`) sind nicht erfasst. „Boden des Skeletts“ ist in diesem Sinn zu lesen.
3. In der Kopfzeile ist „RULES.md §4 & §2d“ ungenau; gemeint ist Regel 2d im Abschnitt „Meldung nach außen“.
4. 1.5 benutzt keine nicht-waagerechte Gerade und gilt deshalb für jede ganze Zahl $q \ge 2$, wie im Text angegeben.

**Nachbesserung, 2026-11-27, 05:59 MEZ.** Auf Angabe von Gemini (Verfasser) hat der Phase-8-Chat drei Stellen im Text oben geändert: Kopfzeile (Verweis auf `RULES.md`, Anmerkung 3); 1.3 (Bedingung $x_b \le \min(v - 1, q - 1)$ mit Begründung, dazu $m(p) \ge h_b \ge 1$ im Argument, Anmerkung 1); 1.4 (Überschriften, Wortlaut der Aussage und der Absatz „Abgrenzung“, Anmerkung 2). Sonst ist der Text unverändert. Die Änderungen sind selbst ungeprüft.

**Abgleich mit Rechnungen (kein Ersatz für die Prüfung):**

- 1.2 (2): für alle Klassen bei den Primzahlen $q = 11, 13, 17, 19, 23, 29, 31, 37, 41, 43$ nachgerechnet (Lauf im Chat am 27.11., ca. 01:50 MEZ, mit der Beschreibung $\Delta$, $O = (0, -1/n_0)$, Punkte $(\pm e n_0 (d - d_0), d)$; nicht im Laufprotokoll). Für Primzahlpotenzen **nicht** gerechnet.
- Zählformel aus 1.3 gegen gebaute Listen: `746` ($q = 23$, $j = 1$), `1190`, `1356`, `1942` ($q = 29, 31, 37$, $j = 2$), `722` ($(q, v) = (23, 22)$, $j = 1$) stimmen mit `data/phase8/` überein (dort $n = 9, 11, 12, 13, 10$ und $G = 90, 154, 174, 216, 92$, am 06:05 MEZ aus den Listen abgelesen; bei $q = 37$ ist $n = 13$ kleiner als das größte zulässige $n = 15$, mit dem Formel (a) `1944` ergibt); Formel (a) als Zählung für alle Primzahlen $13 \le q < 520$ (Lauf `P8-FORMEL-ZAEHLUNG`).
- Vorhersagen aus dem Text, nicht gebaut: `116` für $q = 9$ ($j = 0$, $n = 3$) und `828` für $(q, v) = (25, 23)$ ($j = 2$, $n = 11$); beide Teil des laufenden Nachbau-Auftrags an Antigravity.

## Prüfung durch ein unbeteiligtes Modell, 2026-11-27, 06:03 MEZ

**Was vorlag.** `openai/gpt-6.2-sol` über OpenRouter, Denkstufe `high`, Auftrag `docs/openrouter/PHASE8_ARGUMENTE_AUFTRAG.md`, dazu dieses Dokument im Stand des Commits `b71b035` und `docs/PHASE7_T2_REDUCTION.md`. Antwort im Wortlaut: `docs/openrouter/PHASE8_ARGUMENTE_REVIEW_gpt-6.2-sol.md` (Commit `7b7f631`). Das Modell hat kein Programm ausgeführt und weder Listen noch Skripte noch die Originalquellen der zitierten Sätze gesehen. Der Text oberhalb des Lesevermerks ist seit `b71b035` nicht mehr geändert.

**Urteile.** 1.1, 1.2, 1.4 (Hilfssatz, Formel (a), Obergrenze, Untergrenze) und 1.5: korrekt. 1.3: korrekt mit kleiner Lücke. Kein Fehler gemeldet. Von Hand gerechnet laut Antwort: 1.2 und der Hilfssatz für $q = 3, 5, 7$; 1.5 für $q = 2, 3$; ein Gegenbeispiel zur alten Bedingung in 1.3 ($q = 7$, $v = 4$, $j = 0$, $n = 2$: $m(0) = 0$).

**Vom Phase-8-Chat nachgerechnet (06:05 MEZ):** die Punktmengen der Handrechnung für $q = 7$, $n_0 = 3$ ($\Delta = \{1, 2, 3, 6\}$, $d_0 = 2$, $A_0(1) = \{\pm 1, \pm 3\}$) und das Gegenbeispiel ($x_b = 4 = v$, also $h_b = 0$, $h_a = 2$; bei $p = 0$ ist $-e^2$ kein Quadrat, beide Klassen entfallen). Beides stimmt. Die übrigen Handrechnungen der Antwort sind nicht nachgerechnet.

**Offene Präzisierungen aus der Antwort (nicht eingearbeitet, damit der geprüfte Stand erhalten bleibt):**

1. 1.1: Die zwei Fälle schließen sich nur aus, wenn Fall 2 ausdrücklich „keine volle Waagerechte“ verlangt.
2. 1.3: die Zuordnung $e \mapsto a_e$ als Injektion nach $H_a$ ausdrücklich wählen; die $x_a + j$ Geraden außerhalb von $\Delta \cup \{0\}$ ausdrücklich aufteilen; die danach freien Punkte der reinen $b$-Geraden brauchen je einen Vertreter; für $n = 0$ lautet der Zusatzterm einheitlich $\max(0, n - 1)$.
3. 1.4, Formel (a): Das „$+(2 + 2j)$“ betrifft $|R|$; die Streichungssumme ist im Fall $q \equiv 1 \pmod 4$ um $2 + 2j$ kleiner.
4. Rahmen: $\pi$ aus Phase 7 sollte im Dokument selbst definiert sein.
5. Lesevermerk: Beim Eintrag `1942` fehlte $n$; oben nachgetragen ($n = 13$).

**Einordnung.** Das ist die Lesung eines unbeteiligten Sprachmodells, kein formaler Beweis und keine Rechnung. Regel 2d in `RULES.md` betrifft Arrays und bleibt für jede Meldung gesondert zu erfüllen. Belegart der Aussagen 1.1 bis 1.5: „Argument, von einem unbeteiligten Modell gelesen, kein Fehler gefunden“.
