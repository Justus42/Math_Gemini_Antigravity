# Phase 9 — AP 3: Struktureller 3D-Baer-Pilot (`M_3(R_3)`, `q = 9` & Skalierung `q = 16`)

Datum: 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, Basis `0d6e9f5`).
Skript: [`scripts/phase9_m3_baer_pilot.py`](../../scripts/phase9_m3_baer_pilot.py) (`std`-only + `FieldOps`/`check_m3`, deterministisch, Laufzeit `2,97 s <= 180 s`).
**Belegdisziplin:** Keine Außenwirkung, keine Ablage in `results/`, strikte Trennung zwischen `Argument`, `suff=0`, `check_m3=0` und `Dual-Verify`.

---

## 1. Fragestellung & Vergleichsschwellen

Lässt sich für Quadratordnungen $q = s^2$ (Pilotfall $q = 9, s = 3$; Referenz `m_det(9) = 1332`, Solver `m_sol(9) = 1324`) durch 3D-Baer-Unterstrukturen bzw. $\mathbb{F}_s$-Spurgitter in $\mathbb{F}_q^3$ die führende Konstante im Modell $M_3(R_3)$ (`full-bg3`, $k = q + 3$) unter:
- die Schranke $49/27 \cdot q^3$ ($q = 9: 1323$), oder
- die LP-Schranke $46/27 \cdot q^3$ ($q = 9: 1242$)

drücken — analog zum 2D-Baer-Gitter in Phase 8 (`M(R)`: $|R| = q^2 + O(q^{3/2})$ statt $\frac{7}{5} q^2$)?

**Ergebnis (Stoppkriterium erreicht):** **Nein.** Alle vier getesteten 3D-Baer-/$\mathbb{F}_3$-Architekturen scheitern an strukturellen 3D-Obstruktionen und liefern bei $q = 9$ Werte **oberhalb** von `1332` (`1410`, `1485`, `>= 1539`), mit asymptotischer Skalierung $2 q^3 + \Theta(q^{5/2})$ bei der direkten 3-Familien-Baer-Zylinder-Bauart (schlechter als die elliptische Schranke $2 q^3 - q^2$).

---

## 2. Vier strukturelle Obstruktionen (Theorie + exakte Rechnung auf `GF(9)`)

### 2.1 Experiment 1 — Geometrie einzelner 3D-Baer-/$\mathbb{F}_3$-Unterstrukturen (`q = 9`)

| Objekt in $\mathrm{AG}(3, 9) \cong \mathbb{F}_3^6$ | Punktzahl | Geprüfte Bedingung | Exakter Befund (`check_m3`-Baustein) | Belegart |
| --- | :---: | --- | --- | --- |
| 3D-Baer-Unterraum $\mathrm{AG}(3, 3)$ | $27 = q^{3/2}$ | Typ 1 ($\ge q^2 = 81$) | Trivial zu klein ($27 < 81$) | Argument |
| Nicht-horizontale 4D-$\mathbb{F}_3$-Unterebene $W = \mathbb{F}_9 \times \mathbb{F}_3 \times \mathbb{F}_3$ | $81 = q^2$ | Typ 1 (`D_1 = F_9^2`) | **`Typ1_miss = 1458`** (`> 0`, blockiert) | Exakt gerechnet + Argument |
| 5D-$\mathbb{F}_3$-Spurhyperebene $\mathrm{Tr}(\alpha x + \beta y + \gamma z) = t$ | $243 = q^{5/2}$ | Typ 1 ($\sum_s |U_s|$) | $\sum_s |U_s| = q^{7/2} = 2187 \gg 2 q^3$ | Argument |
| 3D-Baer-Zylinder $X \times A_{\mathrm{Baer}}$ | $108 = q^2 + q^{3/2}$ | Typ 1 (`D_1 = F_9^2`) | **`Typ1_miss = 0`** (gültiger Typ-1-Blocker) | Exakt gerechnet + Argument |
| Rang-3-$\mathbb{F}_3$-Linearset $L_U \setminus \{X_\infty\}$ | $12 = q + \sqrt{q}$ | Typ 2 (`N_2 = F_9^2`) | **`Typ2_miss = 0`**, aber $y + \omega z \equiv 1$ (**zwangsläufig eben**) | Exakt gerechnet + Argument |
| 3 transversale 2D-Baer-Familien `Fam A, B, C` in $\mathrm{AG}(2, 9)$ | je `6` Klassen à `12` | 2D-Geraden & paarweise Schnitte | `2D_miss = 0` (`18/18`); $|A \cap B|_{z\neq 0} = |A \cap C|_{z\neq 0} = |B \cap C|_{z\neq 0} = \{1\}$ | Exakt gerechnet |

**Algebraische Begründung der beiden Dimensions-Obstruktionen (Argument, Regel-2d offen):**
1. **Keine nicht-horizontale 4D-$\mathbb{F}_s$-Unterebene erfüllt Typ 1:** Enthält ein 4D-$\mathbb{F}_s$-Unterraum $W \subset \mathbb{F}_q^3$ ($|W| = s^4 = q^2$) einen Vektor $(x_1, y_1, z_1)$ mit $z_1 \neq 0$, so schneidet die nicht-horizontale $\mathbb{F}_q$-Gerade durch $0$ in Richtung $(v, w, 1) = (x_1/z_1, y_1/z_1, 1)$ den Raum $W$ mindestens in $\mathbb{F}_s \cdot (x_1, y_1, z_1)$ (Größe $\ge s$). Damit hat die Projektion $(x, y, z) \mapsto (x - v z, y - w z)$ auf $W$ Bildgröße $\le q^2 / s < q^2$ und verletzt Typ 1.
2. **Keine nicht-ebene Rang-3-Baer-Menge für Typ 2:** Jede 3-dimensionale $\mathbb{F}_s$-lineare Menge $L_U \subset \mathrm{PG}(3, s^2)$ wird von 3 Vektoren aus $\mathbb{F}_{s^2}^4$ aufgespannt und liegt daher stets in einer einzigen 2D-Ebene $\Pi \subset \mathrm{PG}(3, s^2)$. Nach Bose–Burton/Bruen sind die einzigen Typ-2-Blocker der Größe $q$ volle $x$-Geraden; jeder Nicht-Geraden-Typ-2-Blocker hat Größe $\ge q + \sqrt{q}$ (`12` bei $q = 9$).

---

### 2.2 Experiment 2 — Vollständige 3-Familien-3D-Baer-Zylinder-Bauart (`check_m3 = 0`)

Auf $z \neq 0$ werden die drei paarweise transversalen 2D-Baer-Familien `Fam A, B, C` (`q - s` Klassen je Seite) direkt zu $x$-Geraden geliftet:
- Innenbereich (`(s - 1)(s - 2) q` Punkte): alle 3 Baer-Klassen aktiv $\to$ `3P`-$x$-Geraden.
- 3 Sonder-Horizontalscharen (`3(s - 1) q` Punkte): genau 2 Baer-Klassen aktiv, 3. Koordinate frei $\to$ `1P`-$x$-Geraden.
- Auf $z = 0$ decken `F = s` Voll-Ebenen-Symbole je Seite alle restlichen Paare über `3 s^2` `3P`-Geraden in $F \times F \times B$ plus `3 s(q - 2s)` `3P`-Geraden in $F \times B \times B$ (insgesamt $3 q^{3/2} - 3 q$ Geraden); danach werden alle verbleibenden Typ-3-Tripel platziert (`extra_z0 = 0`!).

| $q = s^2$ | `nz` (`3P` / `1P`) | `z0_3P` | `rem_t3` | `extra_z0` | **`m_Baer_cyl`** | `m / q^3` | `ell = 2q^3 - q^2` | `m_det` | `check_m3(full-bg3)` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`9`** ($s=3$) | `18` / `54` | `54` | `351` | `0` | **`1.485`** | `2,03704` | `1.377` (`+108`) | `1.332` (`+153`) | **`0 (OK)`** (`dups = 0`) |
| **`16`** ($s=4$) | `96` / `144` | `144` | `2.032` | `0` | **`8.176`** | `1,99609` | `7.936` (`+240`) | `7.653` (`+523`) | **`0 (OK)`** (`dups = 0`) |

**Kernursache der Obstruktion (Typ-2-vs.-Typ-3-Konflikt):**
Im Gegensatz zu 2D (`M(R)`), wo paarweise Schnitte $|A_a \cap B_b| = 1$ das Problem in $q^2 + O(q^{3/2})$ bereits abschließen, fordert 3D zusätzlich die kubische Typ-3-Bedingung (alle $q^3$ Tripel $(a, b, c)$). Bei der 3-Familien-Baer-Zylinder-Bauart strebt der Anteil der `3P`-Geraden auf $z \neq 0$ gegen $\frac{(s-1)(s-2)}{s^2} = 1 - \frac{3}{\sqrt{q}} + \frac{2}{q} \to 1$. Dadurch decken die nur $3(s - 1) q$ `1P`-Geraden lediglich $O(q^{5/2})$ Tripel ab; es verbleiben $q^3 - O(q^{5/2})$ ungedeckte Typ-3-Tripel (`rem_t3`). Die Gesamtgröße schnappt deshalb auf
$$|R_3|_{\text{Baer-cyl}} = (q^3 - q^2) + (3 q^{5/2} - 3 q^2) + (q^3 - O(q^{5/2})) = 2 q^3 + \Theta(q^{5/2})$$
zurück — **strikt schlechter als die elliptische Schranke $2 q^3 - q^2$** und weit über `m_det`.

---

### 2.3 Experiment 3 — Gestapeltes 2D-Baer-Gitter (`z = a`, $9 \times 117 = 1053$ Punkte) mit Twists

Stapelt man auf jeder horizontalen Ebene $z = a \in \mathbb{F}_9$ ein 2D-Baer-Gitter aus Phase 8 (`117` Punkte auf $(x, y)$ für die Symbole $(b, c)$), so sind `Typ 0`, `Typ 1(a)`, `Typ 2(ab)`, `Typ 2(ac)` und `Typ 3` bereits mit $1053 = q^3 + O(q^{5/2})$ Punkten (mit Baer-v3 `108`: `972`) komplett erfüllt.

| Twist $(x, y, z)$ | `m` | `Typ 0` | `Typ 1` (`fail_sets / 243`) | `Typ 2` (`fail_sets / 243`) | `Typ 3` |
| --- | :---: | :---: | :---: | :---: | :---: |
| Ungetwistet `(x, y, a)` | `1.053` | `0` | `8.136` (`18/243`) | `5.526` (`9/243`) | `0` |
| Linear `(x + a, y + om*a, a)` | `1.053` | `0` | `8.136` (`18/243`) | `5.526` (`9/243`) | `0` |
| Quadratisch `(x + a^2, y + a, a)` | `1.053` | `0` | `23.328` (`162/243`) | `23.328` (`81/243`) | `0` |
| Kubisch `(x + a^2, y + a^3, a)` | `1.053` | `0` | `25.164` (`162/243`) | `18.144` (`81/243`) | `0` |

**Kernursache der Obstruktion:**
- Bei ungetwistetem/linearem Stapel bildet jede `{b, c}`-Paarfaser $P_{(b, c)}$ eine vertikale (bzw. schräge) Gerade der Größe $q = 9$. Diese verfehlt exakt die $q = 9$ Normalen $(1, \alpha, \beta)$ mit $\beta = -(c_1 + \alpha c_2)$ (`9/81` Normalen auf `{b, c}`, `5.526` Lücken), und $b, c$ verfehlen je $q = 9$ Richtungen in Typ 1 (`18/243` `fail_sets`).
- Nicht-lineare Twists zerstören die Geradenprojektion und brechen alle `81/81` Normalen auf `{b, c}` (`Typ 2`: `18.144–23.328`).
- Eine Reparatur der fehlenden `{b, c}`-Normalen und Typ-1-Defizite (z. B. volle Ebenen für $b, c$ oder `81` $x$-Geraden auf einer Zusatzebene) kostet mindestens $+567\dots 729$ Punkte und hebt die Gesamtzahl auf $\ge 1539\dots 1701 \gg 1323$.

---

### 2.4 Experiment 4 — Additiver $\mathbb{F}_3$-Untergeraden-Komplement-Hybrid in `GF(9) = F_3^2`

Ersetzt man in `scripts/phase9_m3_construct.py` das zyklische Differenzband $\mathbb{Z}_9$ durch das $\mathbb{F}_3$-Untergeraden-Komplement $D = \mathbb{F}_9 \setminus \mathbb{F}_3$ ($r = 6$, `|T| = 54`, `|1P| = 81`, `|U| = 108`, exakte Rohsumme $m_{\mathrm{raw}} = 1323 = \frac{49}{27} \cdot 9^3$) mit $\mathbb{F}_3$-Nebenklassen-Light-Mengen, so erhält man:
- **`m = 1.410`** (`1,93416 * q^3`, `exh = 87`, `suff = 0`, `check_m3(full-bg3) = 0`) — schlechter als das zyklische Band (`m_det = 1332`, `exh = 9`), da das kleinere `|U| = 108` zu wenig Ausgleichsmasse auf der schweren Ebene $z^*$ bereitstellt.

---

## 3. Fazit & Stoppentscheidung

Der 3D-Baer-Pilot erreicht bei $q = 9$ das definierte Stoppkriterium:
- **Kein Treffer `< 1323` (`49/27`) oder `< 1242` (`46/27`)**; beste gültige 3D-Baer-Hybridliste im Pilot ist `1.410` (bzw. `1.485` für reine 3D-Baer-Zylinder, `8.176` bei $q = 16$), jeweils oberhalb von `m_det(9) = 1.332` und `m_sol(9) = 1.324`.
- **Strukturelle Erklärung:** Anders als in 2D (`M(R)`) koppelt `M_3(R_3)` drei Ebenen (`Typ 1`: 1-Blocker $\ge q^2$, `Typ 2`: 2-Blocker $\ge q$ bzw. $\ge q + \sqrt{q}$, `Typ 3`: $q^3$-Würfel). 3D-Baer-Zylinder beseitigen zwar den Heavy-Plane-Overhead (`extra_z0 = 0`), erzwingen aber `3P`-Dichte $\to 1$ und damit $|U| \to q^3$, was den Gesamtbedarf wieder auf $2 q^3 + \Theta(q^{5/2})$ drückt. Ein Durchbruch unter `46/27` würde eine wesentlich andere nicht-zylindrische 3-Weg-Überdeckung erfordern, deren Existenz im Modell `M_3(R_3)` offen bleibt.
