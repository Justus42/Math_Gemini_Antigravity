# Phase 9 (AP 3): 3D-Baer-Pilot für Quadratordnungen `q = s^2` (`q = 9`, `q = 16`)

- **Datum:** 2026-11-28 UTC
- **Branch / Basis:** `exp/phase9-biaffine-3d` (Basis `0d6e9f5`, PR `#54`)
- **Prototyp:** [`scripts/phase9_m3_baer_pilot.py`](../../scripts/phase9_m3_baer_pilot.py) (`std`-only + `FieldOps` / `check_m3`, Laufzeit gesamt `~7 s <= 3 min`)
- **Fragestellung:** Lässt sich für Quadratordnungen $q = s^2$ (Testfall $q = 9, s = 3$; `det m = 1332`, C-Solver `m = 1324`, `49/27 * 9^3 = 1323`, LP `46/27 * 9^3 = 1242`) durch 3D-Baer-Unterräume, 2D-Baer-Zylinder oder ein 2D-Baer-Ebenen-Hybrid die Konstante unter `49/27` bzw. unter `46/27` drücken?

---

## 1. Kurzergebnis (Stoppkriterium erfüllt)

1. **Bei $q = 9$ (und $q = 16$) KEIN Treffer unter `1323` (`49/27`) oder `1242` (`46/27`):**
   - **Reine 3D-Baer-Unterräume & 2D-Baer-Zylinder (Ausbruch unter $\frac{5}{3}q^3$ / $\frac{46}{27}q^3$)** scheitern an drei exakten, rechnerisch verifizierten strukturellen Obstruktionen (Abschnitt 2).
   - **3-Wege-2D-Baer-Ebenen-Hybrid + schwere Ebene $z^*$** besteht zwar exakt `check_m3(full-bg3) = 0` auf $q = 9$ und $q = 16$, erreicht aber bei $q = 9$ minimal **`m = 1498`** (`2,0549 q^3`, deutlich über `det = 1332`, `solver = 1324` und `49/27 * 9^3 = 1323`) und bei $q = 16$ minimal **`m = 8161`** (`1,9924 q^3`, über `det = 7653`). Ursache ist der $O(q^{5/2})$-Baer-Overhead auf den $q - 1$ leichten Ebenen.
2. **Asymptotischer Nebenbefund für große Quadratordnungen $q = s^2$:**
   - Der 3-Wege-2D-Baer-Ebenen-Hybrid (`B1_full`, `check_m3 = 0` geprüft auf $q = 9, 16$) skaliert asymptotisch wie
     $$m_{\mathrm{B1}}(q) = \mathbf{\frac{47}{27}\,q^3 + 2\,q^{5/2} + O(q^2)} \approx 1{,}74074\,q^3 + 2\,q^{5/2}$$
     und unterbietet damit asymptotisch sowohl die deterministische zyklische `x`-Geraden-Konstruktion ($\frac{19}{10} = 1{,}90$, Übergang ab $q \ge 13^2 = 169$) als auch die `1P_LH`-freie LP-Schranke ($\frac{49}{27} \approx 1{,}81481$, Übergang ab $q \ge 29^2 = 841$), bleibt aber um $\frac{1}{27}$ **oberhalb** der allgemeinen Light+Heavy-LP-Schranke $\frac{46}{27} \approx 1{,}70370$.
3. **Abbruch gemäß Stoppkriterium:** Da bei $q = 9$ kein Treffer $m < 1323$ erreicht wird und die Obstruktionen sowohl theoretisch als auch rechnerisch exakt geklärt sind, wird die 3D-Baer-Linie für kleine $q$ hier sauber beendet.

---

## 2. Experiment A: Drei strukturelle Obstruktionen reiner 3D-Baer-Ansätze (`q = 9`, `s = 3`)

Um das horizontale-Ebenen-Skelett ($m \ge \frac{5}{3}q^3 = \frac{45}{27}q^3$) und damit die `46/27`-LP-Schranke zu brechen, müssten `Typ 1`-Fasern ohne horizontale $z$-Ebenen auskommen. Direkte Prüfung mit `scripts/phase9_m3_baer_pilot.py` auf $q = 9$ ($\mathbb{F}_9 = \mathbb{F}_3 + \mathbb{F}_3 \omega$):

| Obstruktion | Objekt auf $q = 9$ ($s = 3$) | Rechnerischer Befund | Mathematische Ursache |
| :--- | :--- | :--- | :--- |
| **(O1) Kardinalität `Typ 1`** | 3D-Baer-Unterraum $\mathrm{AG}(3, 3) = \mathbb{F}_3^3$ (`27` Punkte; $\mathrm{PG}(3, 3)$ hat `40`) | `Typ 1`: **`4536 / 6561`** fehlende Geraden; `Typ 2`: **`9 / 81`** fehlerhafte Normalen (`54` fehlende Ebenen) | Für festes $(v, w)$ partitionieren die $q^2$ parallelen Geraden der Richtung $(v, w, 1)$ den Raum $\mathbb{F}_q^3$, daher gilt zwingend $\|U_s\| \ge q^2$ ($81 > 40$). Ein 3D-Baer-Unterraum blockiert (bis auf $\mathrm{PG}(2, s)$) Ebenen, **nicht** Geraden. |
| **(O2) Steigungs-Obstruktion `Typ 2`** | Schnitt zweier orthogonaler 2D-Baer-Zylinder $B_a(x, z) \cap B_b(y, z)$ auf $z = 1/w$ (`3 × 3`-Gitter $X \times Y$, `9` Punkte) | `Typ 2`: exakt **`27 / 81`** ($= s q$) fehlerhafte Normalen $(\alpha, \beta)$, **`162`** ($= s(q-s)q$) fehlende Ebenen pro Paar | Auf $z = 1/w$ ist $X \times Y$ affin isomorph zu $(1/w)(\mathbb{F}_s \times \omega \mathbb{F}_s)$. Für alle $s$ Steigungen $\alpha \in \mathbb{F}_s \omega^{-1}$ kollabiert $x + \alpha y$ auf nur $s$ statt $q$ Werte (kein 2D-Baer-Blocking-Set der Größe $q + s$, keine $x$-Gerade). |
| **(O3) Tripel-Disjunktheit `Typ 3`** | 3-Wege-2D-Baer-Zylinder ($w_2 = i_a$, $w_1 = i_b$, $w_1 + w_2 = i_c$) auf $z \neq 0$ | Nur **`2 / 8` (`25 %`)** der Klassen-Index-Tripel $(i_a, i_b, i_c)$ treffen sich jemals auf $z \neq 0$ (`75 %` Verlust) | Über $\mathbb{F}_s$ ist $\mathbb{F}_q$ nur $2$-dimensional: $i_a = w_2$ und $i_b = w_1$ erzwingen bereits $i_c = i_a + i_b$. Selbst ein $x$-Zylinder-Lift eines 3-Spalten-2D-Baer-Gitters in $(y, z)$ deckt in $q^3 + O(q^{5/2})$ Punkten nur $O(q^2)$ Tripel ab und benötigt danach weitere $\sim q^3$ `0P`-Punkte (Gesamtsumme $\sim 2 q^3$). |

**Zusatz-Lemma (Eindeutigkeit von `x`-Geraden der Größe $q$ für `Typ 2`):** *Jede Menge $P \subseteq \mathbb{F}_q^3$ der Größe $|P| = q$, die alle Ebenen $x + \alpha y + \beta z = u$ trifft, ist eine volle $x$-Gerade $\{(x, y_0, z_0) : x \in \mathbb{F}_q\}$.* (Beweis: Aus $\alpha = \beta = 0$ folgt $P = \{(x, y(x), z(x)) : x \in \mathbb{F}_q\}$. Gilt $y(x_1) \neq y(x_2)$ für $x_1 \neq x_2$, so erzeugt $\beta = 0, \alpha = -(x_2 - x_1)/(y(x_2) - y(x_1))$ eine Kollision; analog für $z$. $\square$)

---

## 3. Experiment B: 3-Wege-2D-Baer-Ebenen-Hybrid (`check_m3 = 0` auf `q = 9, 16`)

Da 2D-Baer-Gitter $R_{2D} \subset \mathbb{F}_q^4$ aus Phase 8 in einer horizontalen Ebene $z = z_0$ für jedes Symbolpaar $(a_0, b)$ bzw. $(a_0, c)$ ein 2D-Baer-Blocking-Set der Größe $q + s$ liefern, erfüllen sie auf Ebene $z_0$ unmittelbar `Typ 2` für alle $(a_0, \cdot)$ und gleichzeitig `Typ 3` für alle $(a_0, b, c)$.

### Bauart
- **Variante `B1_full`:** Die $q - 1$ leichten Ebenen $z \in Z_a \sqcup Z_b \sqcup Z_c$ ($|A_L| = k_a$, $|B_L| = k_b$, $|C_L| = k_c$, $k_a + k_b + k_c = q - 1$) tragen je ein vollständiges $v = q$ 2D-Baer-Gitter (auf $Z_a$ mit festem $a \in A_L$ und $(b, c)$ aus $R_{2D}$; analog $Z_b, Z_c$). Damit sind **alle** Paare außerhalb von $A_H \times B_H, A_H \times C_H, B_H \times C_H$ und **alle** Tripel außerhalb von $A_H \times B_H \times C_H$ gedeckt. Die schwere Ebene $z^* = q - 1$ deckt nur noch den schweren Teilwürfel $A_H \times B_H \times C_H$ (Größe $h \approx \frac{2}{3}q$) über `3P`/`1P`-`x`-Geraden ($h^2 q \approx \frac{4}{9}q^3$) plus Resttripel ($h^3 - h^2 \approx \frac{8}{27}q^3$).
- **Variante `B2_trimmed`:** Auf jeder leichten Ebene wird nur ein getrimmtes 2D-Baer-Gitter für die schweren Symbole ($v \approx \frac{2}{3}q$) gelegt und die $s - 1$ freien horizontalen Geraden ($w_1 = 0$ bzw. $w_2 = 0$) werden für `LL`-Paare recycelt; fehlende `LLH`/`LLL`-Tripel werden als `0P`-Punkte auf $z^*$ nachgezogen.

### Rechnerische Ergebnisse (`python3 scripts/phase9_m3_baer_pilot.py`)

| Instanz / Variante | `m` | `m / q^3` | Aufschlüsselung (`light / 3P / 1P / remU / exh`) | `check_m3(full-bg3)` | Referenz (`det` / `49/27` / `46/27`) | Laufzeit |
| :--- | :---: | :---: | --- | :---: | :---: | :---: |
| `q = 9`, `B1_full` (Baer-v1 `m2d=117`) | `1.590` | `2,1811` | `936 / 36 / 12 / 180 / 42` | **`0 (OK)`** | `1332 / 1323 / 1242` | `0,14 s` |
| `q = 9`, `B1_full` (Phase-8 `m2d=113`) | `1.558` | `2,1372` | `904 / 36 / 12 / 180 / 42` | **`0 (OK)`** | `1332 / 1323 / 1242` | `0,14 s` |
| `q = 9`, `B2_trimmed` (Baer-v1 getrimmt) | **`1.498`** | `2,0549` | `780 / 36 / 16 / 248 / 2` | **`0 (OK)`** | `1332 / 1323 / 1242` | `0,14 s` |
| `q = 16`, `B1_full` (Baer-v1 `m2d=352`) | `8.538` | `2,0845` | `5280 / 121 / 0 / 1210 / 112` | **`0 (OK)`** | `7653 / 7434 / 6978` | `2,16 s` |
| `q = 16`, `B2_trimmed` (Baer-v1 getrimmt) | **`8.161`** | `1,9924` | `4380 / 121 / 0 / 1845 / 0` | **`0 (OK)`** | `7653 / 7434 / 6978` | `2,05 s` |

### Quantitative Begründung des Klein-`q`-Scheiterns vs. Asymptotik (`47/27`)
1. **Warum $q = 9$ strukturell nicht unter `1323` kommt:**
   - Selbst mit einer hypothetischen 2D-Liste auf der bewiesenen Phase-8-Untergrenze $L'(9) = 96$ (Notiz 3 §2.4) hätte `B1_full` mindestens $8 \cdot 96 + (36 \cdot 9 + 12 \cdot 9 + 180) = 768 + 612 = 1380 > 1332 > 1323$.
   - Selbst bei `B2_trimmed` mit dem physikalischen `Typ 0`-Minimum $8 \cdot 81 = 648$ auf den leichten Ebenen erzwingen die ungedeckten `LLH`/`HHH`-Tripel und schweren Paare auf $z^*$ ($324 + 144 + 248 = 716$) zusammen mindestens $648 + 716 = 1364 > 1332 > 1323$.
2. **Asymptotischer Übergang von `B1_full` (Argument, für $q = 9, 16$ exakt gerechnet):**
   Mit $m_{2D}(q) = q^2 + 2q^{3/2} - 2q$ (Baer-v1) ergibt sich für $q = s^2$:
   $$m_{\mathrm{B1}}(q) = (q - 1)(q^2 + 2q^{3/2} - 2q) + \frac{4}{9}q^3 + \frac{8}{27}q^3 + O(q^2) = \frac{47}{27}q^3 + 2q^{5/2} + O(q^2).$$
   - Unterschreitet $\frac{19}{10}q^3$ (`scripts/phase9_m3_construct.py`) ab $s \ge 13$ ($q \ge 169$: $1{,}8786\,q^3$).
   - Unterschreitet $\frac{49}{27}q^3$ (`1P_LH`-freie LP-Schranke) ab $s \ge 29$ ($q \ge 841$: $1{,}8066\,q^3$).
   - Bleibt stets oberhalb von $\frac{46}{27}q^3$ ($\frac{47}{27} - \frac{46}{27} = \frac{1}{27}$).
   *(Hinweis: `exh` auf $z^*$ in `B1_full` ist für $q > 16$ noch nicht analytisch beschränkt — analog zu `[OFFEN / PRUEFPUNKT] P1`.)*
