# Notiz 4: Verschärfte Untergrenzen im Modell `M(R)` — Satz C.1 (Primzahlen, `91/68`) und Satz C.2 (Quadratzahlen, `-(9/8)q`)

- **Stand:** 2026-11-27 (Branch `exp/phase8-bounds-q16hybrid`).
- **Belegart (verbindlich):** Informelles Argument aus Vorwärts-Recherche, rechnerisch gegen Listen geprüft, Regel-2d-Prüfung am Sonntag offen.
- **Keine Außenwirkung:** Kein PR/Issue gegen `chrispbsmolen/ca-tools`, kein Neuheitsanspruch, kein formaler Beweis.
- **Skript:** [`scripts/phase8_bounds_c1_c2.py`](../../scripts/phase8_bounds_c1_c2.py) (`std`-only, Laufzeit `< 2 s`).

---

## 1. Rahmen und Vorarbeit

Wie in [`docs/PHASE8_ARGUMENTE.md`](../PHASE8_ARGUMENTE.md) und [`docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md`](NOTIZ_3_UNTERGRENZE_BAER.md) bezeichne `R \subset \mathbb{F}_q^4` eine Vertreterliste für das Stärke-2-Modell `M(R)` mit `v = q`:
1. **Punktabdeckung:** Jeder affine Punkt `(c, d) \in \mathbb{F}_q^2` trägt mindestens einen Vertreter `(c, d, a, b) \in R` (insbesondere hat jede Waagerechte `L_d = \{(c, d) : c \in \mathbb{F}_q\}` mindestens `M_d \ge q` Vertreter).
2. **Geradentreffer:** Für jedes Symbol `s \in \{0, \dots, q-1\}` treffen die Träger `A_s = \{(c, d) : \exists b\,(c, d, s, b) \in R\}` und `B_s = \{(c, d) : \exists a\,(c, d, a, s) \in R\}` jede nicht-waagerechte Gerade `c + \alpha d = u` in `\mathrm{AG}(2, q)`.
3. **Symbolpaare:** Jedes geordnete Paar `(a, b) \in \{0, \dots, q-1\}^2` tritt bei mindestens einem Vertreter in `R` auf.

**Zitierte Geometrie-Bausteine (Literatur):**
- **Jamison (1977) / Brouwer–Schrijver (1978):** Jede blockierende Menge von `\mathrm{AG}(2, q)` hat mindestens `2q - 1` Punkte.
- **Blokhuis–Brouwer (1986), *Bull. London Math. Soc.* 18, 132–134** & **Bartoli–Héger–Kiss–Takáts (2017), arXiv:1706.06583, Result 3.11** (dort zitiert nach Blokhuis–Brouwer; Lemma 3.12 ist die Umformulierung mit `k`-Erweiterern für `k = 1`; Präzisierung nach `docs/LITERATURE_CHECK_PHASE8.md` §5; vgl. auch Lemma J in Notiz 3 §2.1): Ist `A \subset \mathrm{AG}(2, q)` eine Punktmenge, die jede nicht-waagerechte Gerade trifft und genau `m` der `q` Waagerechten schneidet, so ist `B = A \cup \{P_\infty\}` eine blockierende Menge in `\mathrm{PG}(2, q)` mit `q - m + 1` Tangenten durch den wesentlichen Punkt `P_\infty`; daraus folgt `q - m + 1 \ge 2q + 1 - |B| = 2q - |A|`, also
  $$|A| \ge q + m - 1.$$
- **Bruen (1970, *Bull. AMS* 76; 1971, *SIAM J. Appl. Math.* 21):** Jede nichttriviale blockierende Menge von `\mathrm{PG}(2, q)` hat mindestens `q + \sqrt{q} + 1` Punkte. Enthält `A_s` keine volle Waagerechte, so gilt entweder `|A_s| \ge 2q - 1` (falls `A_s` eine volle nicht-waagerechte Gerade enthält und deren `q - 1` Parallelen treffen muss) oder `A_s \cup \{P_\infty\}` ist eine nichttriviale blockierende Menge von `\mathrm{PG}(2, q)`, also in beiden Fällen `|A_s| \ge q + \sqrt{q}` (`q \ge 4`).
- **Blokhuis (1994, *Combinatorica* 14, 111–114):** Für eine Primzahl `p` hat jede nichttriviale blockierende Menge von `\mathrm{PG}(2, p)` mindestens `3(p + 1)/2` Punkte. Enthält `A_s` keine volle Waagerechte, so folgt analog `|A_s| \ge \mathrm{bl}(p) := (3p + 1)/2` (für ungerade Primzahlen `p \ge 3`, da `2p - 1 \ge (3p + 1)/2`).

---

## 2. Satz C.1 (Ungerade Primzahlen `p`, `v = p`)

### 2.1 Aussage (Exakte ganzzahlige Schranke)

Sei `p \ge 3` eine ungerade Primzahl, `\mathrm{bl} = (3p + 1)/2`, und `R` eine gültige Vertreterliste für `M(R)` mit `v = p`. Dann gilt
$$|R| \ge \min_{(h_a, h_b, U, V, t_{11})} \max(e_1, e_2, e_{3a}, e_{3b}, e_4, e_{5a}, e_{5b}, e_6),$$
wobei das Minimum über alle ganzzahligen Parameter mit `0 \le h_a \le h_b \le p`, `0 \le U \le h_a` (`u_A := h_a - U = 0` genau dann, wenn `h_a = 0`), `0 \le V \le h_b` (`u_B := h_b - V = 0` genau dann, wenn `h_b = 0`) sowie `\max(0, u_A + u_B - p) \le t_{11} \le \min(u_A, u_B)` läuft, mit
$$F = U + V + t_{11}, \qquad S = \begin{cases} 0, & t_{11} = 0, \\ \min(h_a h_b,\, U V + F), & t_{11} \ge 1, \end{cases}$$
und
$$\begin{aligned}
e_1    &= p h_a + (p - h_a)\mathrm{bl}, &
e_2    &= p h_b + (p - h_b)\mathrm{bl}, \\
e_{3a} &= \left\lceil \frac{p^2 + p F + p h_a - S + (p - h_a)\mathrm{bl}}{2} \right\rceil, &
e_{3b} &= \left\lceil \frac{p^2 + p F + p h_b - S + (p - h_b)\mathrm{bl}}{2} \right\rceil, \\
e_4    &= \left\lceil \frac{p(h_a + h_b) + (2p - h_a - h_b)\mathrm{bl} + h_a h_b - S}{2} \right\rceil, &
e_6    &= p^2 + p \max(U, V), \\
e_{5a} &= \left\lceil \frac{p(h_a + h_b) + (p - h_b)\mathrm{bl} + h_a h_b - S + (p - h_a)(p + u_B - 1)}{2} \right\rceil, \\
e_{5b} &= \left\lceil \frac{p(h_a + h_b) + (p - h_a)\mathrm{bl} + h_a h_b - S + (p - h_b)(p + u_A - 1)}{2} \right\rceil.
\end{aligned}$$

### 2.2 Beweisdarstellung (Informelles Argument)

Bezeichne `H_A` (Größe `h_a`) die Menge der `a`-Symbole, deren Träger `A_s` mindestens eine volle Waagerechte enthält, und analog `H_B` (Größe `h_b`) für `b`-Symbole. Durch Vertauschen von `a` und `b` sei o. B. d. A. `0 \le h_a \le h_b \le p`.

Jedem `a \in H_A` ordnen wir **eine** volle Waagerechte `d(a)` zu; sei `D_A = \{d(a) : a \in H_A\}` mit `u_A = |D_A|` und `U = h_a - u_A`. Analog seien `d(b)`, `D_B`, `u_B = |D_B|`, `V = h_b - u_B` definiert. Für jede Waagerechte `d` seien `A(d) = \{a \in H_A : d(a) = d\}` (`\alpha_d = |A(d)|`) und `B(d) = \{b \in H_B : d(b) = d\}` (`\beta_d = |B(d)|`). Dann gilt `\sum_{d \in D_A} (\alpha_d - 1) = U`, `\sum_{d \in D_B} (\beta_d - 1) = V` und `t_{11} := |D_A \cap D_B|` erfüllt `\max(0, u_A + u_B - p) \le t_{11} \le \min(u_A, u_B)`.

Für jedes `a \in H_A` fixieren wir auf `d(a)` je einen Basisvertreter pro Punkt `(c, d(a))` (`p` Stück); die Zahl aller übrigen Vertreter mit `a`-Symbol `a` sei `\delta_a = |R_a| - p \ge 0`, und `\Delta_A := \sum_{a \in H_A} \delta_a`. Analog sei `\Delta_B := \sum_{b \in H_B} \delta'_b` mit `\delta'_b = |R_b| - p \ge 0`.

1. **Schranken `e_1, e_2` (Blokhuis):** Jedes `a \in H_A` hat `|R_a| = p + \delta_a`, jedes `a \notin H_A` hat nach Blokhuis (1994) `|R_a| \ge |A_a| \ge \mathrm{bl}`. Summieren über alle `p` Symbole liefert
   $$|R| \ge p h_a + (p - h_a)\mathrm{bl} + \Delta_A \ge e_1, \qquad |R| \ge p h_b + (p - h_b)\mathrm{bl} + \Delta_B \ge e_2. \tag{1}$$

2. **Schranke `e_6` (Vielfachheitsüberhang):** Auf jeder Waagerechten `d \in D_A` trägt jeder Punkt mindestens `\alpha_d` Vertreter, also `M_d \ge p \alpha_d = p + p(\alpha_d - 1)`. Summieren über alle `p` Waagerechten gibt `|R| = \sum_d M_d \ge p^2 + p U`, symmetrisch `|R| \ge p^2 + p V`, also `|R| \ge e_6`.

3. **Abschätzung der ko-linearen Paare `S`:** Die Anzahl der Paare `(a, b) \in H_A \times H_B` mit `d(a) = d(b)` ist
   $$S_{\mathrm{akt}} = \sum_{d \in D_A \cap D_B} \alpha_d \beta_d.$$
   Für `t_{11} = 0` ist `S_{\mathrm{akt}} = 0`. Für `t_{11} \ge 1` schreiben wir `\alpha_d = 1 + x_d`, `\beta_d = 1 + y_d` (`x_d, y_d \ge 0`) auf `D_A \cap D_B` und erhalten
   $$S_{\mathrm{akt}} = t_{11} + \sum x_d + \sum y_d + \sum x_d y_d \le t_{11} + U + V + U V = F + U V,$$
   und trivial `S_{\mathrm{akt}} \le h_a h_b`, also stets `S_{\mathrm{akt}} \le S`.

4. **Schranke `e_4` (Paare zwischen `H_A` und `H_B`):** Jedes der `h_a h_b - S_{\mathrm{akt}}` Paare `(a, b) \in H_A \times H_B` mit `d(a) \neq d(b)` muss auf einer Waagerechten `d` auftreten; wegen `d(a) \neq d(b)` gilt entweder `d \neq d(a)` (zählt in `\Delta_A`) oder `d \neq d(b)` (zählt in `\Delta_B`). Verschiedene Paare liefern verschiedene Vertreter, also
   $$\Delta_A + \Delta_B \ge h_a h_b - S_{\mathrm{akt}} \ge h_a h_b - S. \tag{2}$$
   Addition der beiden Ungleichungen in `(1)` und Einsetzen von `(2)` ergibt `2|R| \ge p(h_a + h_b) + (2p - h_a - h_b)\mathrm{bl} + h_a h_b - S`, also `|R| \ge e_4`.

5. **Schranken `e_{3a}, e_{3b}` (Inklusion-Exklusion auf `D_A \cap D_B`):** Sei `X_d` die Zahl der Vertreter auf `d` mit `a \in A(d)` und `b \in B(d)`. Auf `d \in D_A \cap D_B` gilt per Inklusion-Exklusion `M_d \ge p \alpha_d + p \beta_d - X_d = p + p(\alpha_d - 1) + p(\beta_d - 1) + p - X_d`. Summieren über alle `p` Waagerechten liefert
   $$|R| = \sum_d M_d \ge p^2 + p(U + V + t_{11}) - \sum_{d \in D_A \cap D_B} X_d = p^2 + p F - \sum_{d \in D_A \cap D_B} X_d.$$
   Für jedes `a \in A(d)` decken seine `x_a` Vertreter in `X_d` höchstens `\beta_d` verschiedene `b`-Symbole ab (nämlich `B(d)`). Da `a` insgesamt alle `p` Werte von `b` mit `p + \delta_a` Vertretern abdecken muss, folgt `(p + \delta_a - x_a) + \beta_d \ge p`, also `x_a - \beta_d \le \delta_a`. Summieren über `a \in A(d)` und `d \in D_A \cap D_B` liefert `\sum X_d \le S_{\mathrm{akt}} + \Delta_A \le S + \Delta_A`, somit
   $$|R| + \Delta_A \ge p^2 + p F - S.$$
   Addition mit `|R| - \Delta_A \ge p h_a + (p - h_a)\mathrm{bl}` aus `(1)` eliminiert `\Delta_A` und liefert `|R| \ge e_{3a}`; symmetrisch mit `\Delta_B` folgt `|R| \ge e_{3b}`.

6. **Schranken `e_{5a}, e_{5b}` (Kopplung über Blokhuis–Brouwer / Bartoli–Héger–Kiss–Takáts Lemma 3.12):** Zerlege `\Delta_B = \Delta_B^{(H)} + \Delta_B^{(N)}` nach `a \in H_A` bzw. `a \notin H_A`; in `(2)` werden nur Vertreter mit `a \in H_A` benötigt, also `\Delta_A + \Delta_B^{(H)} \ge h_a h_b - S`.
   Für jedes `a \notin H_A` sei `k_a` die Zahl der Waagerechten `d \in D_B`, die `A_a` meidet. Dann trifft `A_a` mindestens `u_B - k_a` Waagerechte, also gilt nach Blokhuis–Brouwer (1986) / Lemma J
   $$|R_a| \ge |A_a| \ge p + (u_B - k_a) - 1 = p + u_B - 1 - k_a.$$
   (Auch im Randfall `u_B = k_a = 0` gilt `|A_a| \ge p > p - 1`.) Auf jeder gemiedenen Waagerechten `d \in D_B` wähle ein `b_d \in B(d)`; das Paar `(a, b_d)` muss außerhalb von `d = d(b_d)` liegen und zählt in `\Delta_B^{(N)}`. Folglich `\Delta_B^{(N)} \ge \sum_{a \notin H_A} k_a`, und damit
   $$|R| \ge p h_a + \Delta_A + (p - h_a)(p + u_B - 1) - \Delta_B^{(N)}.$$
   Addition mit `|R| \ge p h_b + \Delta_B^{(H)} + \Delta_B^{(N)} + (p - h_b)\mathrm{bl}` kürzt `\Delta_B^{(N)}` heraus und liefert mit `\Delta_A + \Delta_B^{(H)} \ge h_a h_b - S` genau `|R| \ge e_{5a}`; symmetrisch folgt `|R| \ge e_{5b}`. `\square`

### 2.3 Asymptotik `91/68`

Skaliere `\alpha = h_a/p`, `\beta = h_b/p`, `u = U/p`, `v = V/p` (`0 \le u \le \alpha \le \beta \le 1`, `0 \le v \le \beta \le 1`) und lasse `p \to \infty`. Für jedes zulässige Tupel gilt `S \le U V + F` mit `F = U + V + t_{11} \le 3p` (für `t_{11} = 0` ist `S = 0`). Ein wörtlicher Ersatz von `S/p^2` durch `u v` wäre nicht zulässig: Für endliches `p` kann `S > U V` sein, und dann würde der Ersatz die Ausdrücke mit `-S` erhöhen. Ersetzt man dagegen `-S` durch `-(U V + F)`, sinkt jeder der Ausdrücke `e_{3a}, e_4, e_{5a}` um höchstens `\lceil F/2 \rceil = O(p)`; in `e_{3a}` wird zusätzlich der nichtnegative Beitrag `p\,t_{11}` aus `p F` weggelassen. Damit sind die folgenden `f`-Ausdrücke Unterabschätzungen von `e_{3a}/p^2, e_4/p^2, e_{5a}/p^2` bis auf `O(1/p)`, ohne `t_{11}/p \to 0` vorauszusetzen. Es genügt zu zeigen:
$$\max\big(f_1,\, f_{3a},\, f_4,\, f_{5a}\big) \ge \frac{91}{68},$$
mit `2 f_1 = 3 - \alpha`, `2 f_{3a} = \frac{5}{2} - \frac{\alpha}{2} + v + (1 - v)u`, `2 f_4 = 3 - \frac{\alpha + \beta}{2} + \alpha\beta - u v`, `2 f_{5a} = \frac{5}{2} + \frac{\beta}{2} - v + \alpha v - u v`.

- **Fall `\alpha \le 11/34`:** `f_1 = \frac{3}{2} - \frac{\alpha}{2} \ge \frac{3}{2} - \frac{11}{68} = \frac{91}{68}`.
- **Fall `\alpha > 11/34`:** Bilde die Konvexkombination `h(\alpha, \beta, v) := v(2 f_{3a}) + (1 - v)\max(2 f_4, 2 f_{5a})`, in der `u` identisch wegfällt! Wegen `2 f_4 - 2 f_{5a} = (1 - \alpha)(\frac{1}{2} - \beta + v)` gilt `\max(2 f_4, 2 f_{5a}) = 2 f_4` für `\beta \le v + \frac{1}{2}` und `= 2 f_{5a}` für `\beta \ge v + \frac{1}{2}`.
  1. Für `\frac{11}{34} < \alpha \le \frac{1}{2}` fällt `2 f_4` in `\beta`, während `2 f_{5a}` in `\beta` wächst. Ist `v \le \frac{1}{2}`, liegt das Minimum über `\beta` bei `\beta = v + \frac{1}{2}`, was
     $$h(\alpha, v + \tfrac{1}{2}, v) = \tfrac{11}{4} - \tfrac{3}{4}v + \tfrac{3}{2}v^2 + \alpha v(\tfrac{1}{2} - v) \ge \tfrac{11}{4} - \tfrac{40}{68}v + \tfrac{40}{34}v^2 = \tfrac{182}{68} + \tfrac{20}{17}(v - \tfrac{1}{4})^2 \ge \tfrac{182}{68} = 2 \cdot \tfrac{91}{68}$$
     ergibt (Gleichheit bei `\alpha = \frac{11}{34}, \beta = \frac{3}{4}, v = \frac{1}{4}, u = \frac{2}{17}`). Ist `v > \frac{1}{2}`, liegt das Minimum bei `\beta = 1` und `\alpha = \frac{1}{2}`: `h(\frac{1}{2}, 1, v) = \frac{11}{4} + v^2 - \frac{v}{2} \ge \frac{11}{4} > \frac{182}{68}`.
  2. Für `\alpha > \frac{1}{2}`: Die Werte `\beta = v + \frac{1}{2}` bzw. `\beta = \alpha` sind hier nicht stets zulässig; sie sind Minima über einen erweiterten Bereich und liefern wegen der Monotonie in `\beta` weiterhin **untere** Vergleichswerte. Bei `\beta \ge v + \frac{1}{2}` (also `v \le \frac{1}{2}`) liefert wie oben `\beta = v + \frac{1}{2}` den unteren Vergleichswert und `h \ge \frac{182}{68}` wegen `\alpha > \frac{11}{34}`. Bei `\beta \le v + \frac{1}{2}` wächst `2 f_4` in `\beta`, also ist `\beta = \alpha` minimal; mit `x = \alpha - \frac{1}{2} \in (0, \frac{1}{2}]` ergibt Minimieren über `v`:
     $$h(\alpha, \alpha, v) \ge \tfrac{11}{4} + x^2 - \tfrac{1}{4}(\tfrac{1}{2} + \tfrac{x}{2} + x^2)^2 \ge \tfrac{43}{16} - \tfrac{x}{8} + \tfrac{1}{2}x^2 = \tfrac{343}{128} + \tfrac{1}{2}(x - \tfrac{1}{8})^2 > \tfrac{182}{68}.$$

Damit gilt asymptotisch `|R| \ge \frac{91}{68} p^2 - O(p) \approx 1{,}338235\,p^2`. `\square`

*Nachrechnung (Prüferchat, 28.11.2026; Auswertung der endlichen Formel aus §2.1 mit `scripts/phase8_bounds_c1_c2.py`, `bound_c1_exact` gleich `bound_c1_bruteforce` für `p \le 13`):* Für alle ungeraden Primzahlen `p \le 101` liegt das Formelminimum zwischen `\frac{91}{68}p^2 - 0{,}015\,p` (`p = 3`) und `\frac{91}{68}p^2 + 0{,}16\,p`. Die Reparatur folgt dem Review `docs/openrouter/PHASE8_NOTIZ4_REVIEW_gpt-6.2-sol.md` (Abschnitt Asymptotik, C.1).

---

## 3. Satz C.2 (Quadrat-Primzahlpotenzen `q = n^2`, `v = q`)

### 3.1 Aussage (Exakte ganzzahlige Schranke)

Sei `q = n^2` eine Quadrat-Primzahlpotenz (`n \ge 2`) und `R` eine gültige Vertreterliste für `M(R)` mit `v = q`. Dann gilt `|R| \ge q^2 + \min_{(k_A, k_B, h_A, h_B)} E`, wobei `0 \le k_A \le k_B \le q`, `h_A \in (\{0\}\text{ falls }k_A = 0\text{ sonst }\{1, \dots, k_A\})`, `h_B \in (\{0\}\text{ falls }k_B = 0\text{ sonst }\{1, \dots, k_B\})` und
$$\begin{aligned}
c_{1X} &= (q - k_A)n, & c_{2X} &= \max\big((q - k_B)n + (h_A - 1)k_B,\; (h_A - 1)q\big), & e_X &= \max\!\left(c_{1X},\, \left\lceil\frac{c_{1X} + c_{2X}}{2}\right\rceil\right), \\
c_{1Y} &= (q - k_B)n, & c_{2Y} &= \max\big((q - k_A)n + (h_B - 1)k_A,\; (h_B - 1)q\big), & e_Y &= \max\!\left(c_{1Y},\, \left\lceil\frac{c_{1Y} + c_{2Y}}{2}\right\rceil\right), \\
E &= \max\big(e_X,\; e_Y,\; (k_A - h_A)q,\; (k_B - h_B)q\big).
\end{aligned}$$

### 3.2 Beweisdarstellung (Informelles Argument)

Sei `E_{\mathrm{akt}} := |R| - q^2` der Überschuss über `q^2`. Wie in Satz C.1 seien `H_A` (Größe `k_A`) bzw. `H_B` (Größe `k_B`) die Symbole mit voller Waagerechter (o. B. d. A. `0 \le k_A \le k_B \le q`), `D_A` (Größe `h_A`) bzw. `D_B` (Größe `h_B`) die Mengen ihrer zugeordneten vollen Waagerechten.

1. **Vielfachheitsüberhang:** Wie in Satz C.1 (`e_6`) liefern die `k_A - h_A` überschüssigen vollen `a`-Geraden und `k_B - h_B` überschüssigen vollen `b`-Geraden sofort `E_{\mathrm{akt}} \ge (k_A - h_A)q` und `E_{\mathrm{akt}} \ge (k_B - h_B)q`.
2. **Bruen-Überschuss `c_{1X}, c_{1Y}`:** Jedes der `q - k_A` Symbole `a \notin H_A` hat nach Bruen (1970/1971) `|R_a| \ge q + n`, also Überschuss `\ge n`. Mit `\Delta_A = \sum_{a \in H_A} (|R_a| - q)` gilt daher
   $$E_{\mathrm{akt}} = \sum_{a=0}^{q-1} (|R_a| - q) \ge (q - k_A)n + \Delta_A = c_{1X} + \Delta_A. \tag{3}$$
   Insbesondere `E_{\mathrm{akt}} \ge c_{1X}` und symmetrisch `E_{\mathrm{akt}} \ge c_{1Y}`.
3. **Kopplung über `h_A` disjunkte volle Waagerechte (`c_{2X}`):** Wähle aus jeder Waagerechten `d \in D_A` ein festes Symbol `a_d \in H_A` mit `d(a_d) = d` (insgesamt `h_A` Symbole). Für jedes `b`-Symbol `b \in \{0, \dots, q-1\}` sei `r_b` die Anzahl der Waagerechten `d \in D_A`, die `B_b` meidet.
   - Einerseits muss jedes Paar `(a_d, b)` mit gemiedenem `d` außerhalb von `d = d(a_d)` auftreten und liefert einen Extravertreter von `a_d`; verschiedene `(a_d, b)` liefern verschiedene Vertreter, also `\sum_{b=0}^{q-1} r_b \le \Delta_A`.
   - Andererseits trifft `B_b` mindestens `h_A - r_b` Waagerechte. Nach Blokhuis–Brouwer (1986) / Bartoli–Héger–Kiss–Takáts (2017) Lemma 3.12 (Lemma J) folgt `(|R_b| - q) + r_b \ge h_A - 1` (gilt auch für `h_A = 0` trivial wegen `|R_b| \ge q > q - 1`).
   - Summieren über **alle** `q` Symbole `b` liefert `E_{\mathrm{akt}} + \Delta_A \ge (h_A - 1)q`.
   - Summieren von `|R_b| - q \ge n` (Bruen) für `b \notin H_B` und `(|R_b| - q) + r_b \ge h_A - 1` für `b \in H_B` liefert `E_{\mathrm{akt}} + \Delta_A \ge (q - k_B)n + (h_A - 1)k_B`.
   - Zusammen also `E_{\mathrm{akt}} + \Delta_A \ge c_{2X}`. Addition mit `(3)` (`E_{\mathrm{akt}} - \Delta_A \ge c_{1X}`) kürzt `\Delta_A` heraus und gibt `2 E_{\mathrm{akt}} \ge c_{1X} + c_{2X}`, also `E_{\mathrm{akt}} \ge e_X`. Symmetrisch folgt `E_{\mathrm{akt}} \ge e_Y`. `\square`

### 3.3 Asymptotik `q^2 + q^{3/2} - \frac{9}{8} q`

**Untergrenze ohne Fehlerterm.** Für jede Quadrat-Primzahlpotenz `q = n^2` gilt
$$|R| \ge q^2 + q^{3/2} - \tfrac{9}{8}\,q .$$
Argument (nach dem Review `docs/openrouter/PHASE8_NOTIZ4_REVIEW_gpt-6.2-sol.md`, Abschnitt Asymptotik, C.2): **O. B. d. A. sei `k_A \le k_B`** (Vertauschen von `a` und `b` vertauscht `X` und `Y`; `E` ist unter dieser Vertauschung symmetrisch). Sei `E` das Maximum der Formel aus §3.1 für ein zulässiges Tupel `(k_A, k_B, h_A, h_B)`.
1. Ist `k_A \le n`, so gilt `E \ge c_{1X} = (q - k_A)n \ge q n - q`.
2. Ist `E \ge q n`, ist nichts zu zeigen. Andernfalls gilt `(k_B - h_B)q \le E < q n`, also `k_B - h_B \le n - 1`, d. h. `h_B - 1 \ge k_B - n`.
3. Sei also `k_A > n` und `E < q n`. Aus `e_Y \ge (c_{1Y} + c_{2Y})/2` und `c_{2Y} \ge (q - k_A)n + (h_B - 1)k_A` folgt mit 2.
$$2E \ge (q - k_B)n + (q - k_A)n + (k_B - n)k_A = 2qn + (k_A - n)k_B - 2nk_A \ge 2qn + k_A^2 - 3nk_A \ge 2qn - \tfrac{9}{4}n^2 .$$
   Der zweite Schritt benutzt `k_A - n > 0` **und `k_B \ge k_A`** (hier geht die Annahme `k_A \le k_B` ein), der dritte das Minimum von `k_A^2 - 3nk_A` bei `k_A = 3n/2`.

In allen Fällen ist `E \ge q n - \frac{9}{8} q` (Fall 1: `q n - q \ge q n - \frac{9}{8}q`), also `|R| \ge q^2 + q^{3/2} - \frac{9}{8} q`. Das ist eine Verschärfung gegenüber `q^2 + q^{3/2} - 2q` aus Notiz 3 (Satz U / Aussage U').

**Koeffizient für das Formelminimum.** Der symmetrische Parameterzeuge `k_A = k_B` nahe `3n/2`, `h_A = h_B = k_A - n + 2` ergibt `E = q n - \frac{9}{8} q + O(n)`. Der Koeffizient `-\frac{9}{8}` stimmt damit für das Minimum der Formel, nicht notwendig für das Listenoptimum.

*Nachrechnung (Prüferchat, 28.11.2026; Auswertung mit `scripts/phase8_bounds_c1_c2.py`, `bound_c2_exact` gleich `bound_c2_bruteforce` für `q \le 49`):* Für `q \in \{4, 9, 16, 25, 49, 64, 81\}` gilt Formelminimum `\ge q^2 + q^{3/2} - \frac{9}{8}q` (`7/7`; `20 \ge 19{,}5`, `99 \ge 97{,}875`, `304 \ge 302`, `725 \ge 721{,}875`, `2694 \ge 2688{,}875`, `4542 \ge 4536`, `7206 \ge 7198{,}875`).

---

## 4. Exakte Zahlenwerte und Listenprüfung (`scripts/phase8_bounds_c1_c2.py`)

### 4.1 Satz C.1 (ungerade Primzahlen `p`, `v = p`)

| `p` | `L'(p)` (Notiz 3) | **Satz C.1** | `LB_{C.1} / p^2` | Zeuge `(h_a, h_b, U, V, t_{11})` | Beste Liste im Repo | Abstand |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 3 | 11 | **12** | 1.3333 | `(3, 3, 0, 0, 3)` | 12 (CP-SAT, Notiz 3) | 0 |
| 5 | 30 | **34** | 1.3600 | `(4, 4, 1, 1, 1)` | 34 (`data/phase7/R_q5_m34.txt`) | **0 (scharf)** |
| 7 | 59 | **66** | 1.3469 | `(5, 5, 2, 2, 1)` | 68 (`data/phase7/R_q7_m68.txt`) | +2 |
| 11 | 142 | **163** | 1.3471 | `(8, 8, 3, 3, 1)` | 170 (`data/phase8/R_q11_m170.txt`) | +7 |
| 13 | 197 | **228** | 1.3491 | `(10, 10, 4, 4, 1)` | 238 (`data/phase8/R_q13_m238.txt`) | +10 |
| 17 | 334 | **388** | 1.3426 | `(12, 12, 5, 5, 1)` | 412 (`data/phase8/R_q17_m412.txt`) | +24 |
| 19 | 415 | **485** | 1.3435 | `(14, 14, 6, 6, 1)` | 513 (`data/phase8/R_q19_m513.txt`) | +28 |
| 23 | 604 | **710** | 1.3422 | `(15, 15, 6, 7, 1)` | 746 (`data/phase8/R_q23_m746.txt`) | +36 |
| 29 | – | **1128** | 1.3413 | `(10, 23, 3, 7, 1)` | 1190 (`data/phase8/R_q29_m1190.txt`) | +62 |
| 31 | – | **1289** | 1.3413 | `(11, 24, 4, 7, 1)` | 1356 (`data/phase8/R_q31_m1356.txt`) | +67 |
| 37 | – | **1837** | 1.3419 | `(14, 29, 5, 9, 1)` | 1942 (`data/phase8/R_q37_m1942.txt`) | +105 |
| 41 | – | **2256** | 1.3421 | `(27, 27, 12, 12, 1)` | – | – |
| 43 | – | **2481** | 1.3418 | `(27, 27, 12, 12, 1)` | – | – |
| 47 | – | **2961** | 1.3404 | `(16, 35, 7, 10, 1)` | – | – |
| 53 | – | **3764** | 1.3400 | `(18, 41, 6, 13, 1)` | – | – |

*(Bemerkung: Für `p = 5` schließt Satz C.1 die Lücke vollständig auf `34 = 34`, unter Vorbehalt der ausstehenden Regel-2d-Prüfung des Arguments.)*

### 4.2 Satz C.2 (Quadrat-Primzahlpotenzen `q = n^2`, `v = q`)

| `q` | `n` | `L'(q)` (Notiz 3) | **Satz C.2** | `E = LB - q^2` | `(E - qn)/q` | Zeuge `(k_A, k_B, h_A, h_B)` | Vergleichswerte (Repo / Baer-v3 / Hybrid) |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4 | 2 | 19 | **20** | 4 | `-1.0000` | `(2, 2, 1, 1)` | 24 (Baer), 22 (Phase 6A) |
| 9 | 3 | 96 | **99** | 18 | `-1.0000` | `(3, 3, 1, 1)` | 113 (`data/phase8/`), 108 (Baer-v3 Ref) |
| 16 | 4 | 296 | **304** | 48 | `-1.0000` | `(4, 4, 1, 1)` | 352 (Baer), 334 (Baer-v3 Ref), **332** (Spur-Baer-Hybrid) |
| 25 | 5 | 711 | **725** | 100 | `-1.0000` | `(5, 5, 1, 1)` | 825 (Baer), 791 (Baer-v3 Ref) |
| 49 | 7 | 2663 | **2694** | 293 | `-1.0204` | `(10, 10, 5, 5)` | 2989 (`data/phase8_baer_repro/`) |
| 64 | 8 | – | **4542** | 446 | `-1.0312` | `(11, 11, 5, 5)` | 4992 (Notiz 3 §3.3) |
| 81 | 9 | – | **7206** | 645 | `-1.0370` | `(12, 12, 5, 5)` | 7857 (Notiz 3 §3.3) |

### 4.3 Ergebnis der Listenprüfung

`python3 scripts/phase8_bounds_c1_c2.py` prüft alle `v = q` Listen in `data/phase7/`, `data/phase8/`, `data/phase8_repro/`, `data/phase8_baer/`, `data/phase8_baer_repro/` und `data/phase8_q16_hybrid/` sowie die drei Baer-v3-Referenzwerte (`q = 9: 108`, `q = 16: 334`, `q = 25: 791`): **`0` Verletzungen**. Alle geforderten Sollwerte (`p = 3..29` und `q = 4..49`) wurden exakt reproduziert und zusätzlich für kleine `p \le 17` bzw. `q \le 25` per Voll-Enumeration quergeprüft.

---

## 5. Referenzen

1. A. A. Bruen (1970): *Baer subplanes and blocking sets*, Bull. Amer. Math. Soc. 76, 342–344; A. A. Bruen (1971): *Blocking sets in finite projective planes*, SIAM J. Appl. Math. 21, 380–392.
2. R. E. Jamison (1977): *Covering finite fields with cosets of subspaces*, J. Combin. Theory Ser. A 22, 253–266; A. E. Brouwer, A. Schrijver (1978): *The blocking number of an affine space*, J. Combin. Theory Ser. A 24, 251–253.
3. A. Blokhuis, A. E. Brouwer (1986): *Blocking sets in Desarguesian projective planes*, Bull. London Math. Soc. 18(2), 132–134.
4. A. Blokhuis (1994): *On the size of a blocking set in `PG(2, p)`*, Combinatorica 14(1), 111–114.
5. D. Bartoli, T. Héger, G. Kiss, M. Takáts (2017): *On the metric dimension of affine planes, biaffine planes and generalized quadrangles*, arXiv:1706.06583, Lemma 3.12 (erschienen in *Australas. J. Combin.* 72 (2018), 226–248).
