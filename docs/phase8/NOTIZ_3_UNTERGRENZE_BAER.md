# Notiz 3: Untergrenze im Modell `M(R)` und das Baer-Gitter für Quadratzahlen

- Stand: 2026-11-27, 07:32 MEZ; **Nachtrag 10:20 MEZ** (§2.4 verschärfte Schranke, §8 Gegenlesen und Nachbau; Branch `claude/phase8-doku-reste`). Autor: Claude (Phase-8-Chat, Nachfolger; Erzeugerrolle). Erstfassung auf Branch `claude/phase8-untergrenze-baer` (PR `#44`).
- Vergleichsstand: dieses Repo `main @ 6994817`; `chrispbsmolen/ca-tools @ 697325b` (27.11., 03:08 MEZ; nur `table/` geholt, rein lesend).
- **Rolle:** Argument, Bauart und Rechnung stammen vom selben Chat. Nichts hier ist von einem unbeteiligten Modell oder Menschen gelesen oder nachgebaut. **Kein Neuheitsanspruch; die Literaturprüfung nach `RULES.md` Regel 2c fehlt** (§7).
- **Außenwirkung:** keine. Kein Bridge-Aufruf. Keine Einreichung ohne Freigabe durch Justus.
- Auftrag: Punkt 1 aus `docs/UEBERGABE_PHASE8_CHAT_2026-11-27.md` §4 („Untergrenze im Modell `M(R)`; ist `7/5` das Ende? Andere Skelette“). Schreibweise wie `docs/PHASE8_ARGUMENTE.md` (Rahmen und Notation), `v = q`, wenn nichts anderes dasteht.

## 1. Ergebnis

1. **Untergrenze für jede Liste (Argument, §2):** Für jede Primzahlpotenz `q` und jede Vertreterliste `R`, deren `M(R)` Stärke 2 hat, gilt
   `|R| >= q^2 + q*sqrt(q)*(sqrt(q) - 1)/(sqrt(q) + 1)`, also mindestens `q^2 + q^(3/2) - 2q`. Das Argument braucht nur den Satz von Jamison (Brouwer–Schrijver) über blockierende Mengen der affinen Ebene und Abzählen. Eine kleine Verschärfung von Gemini gibt `|R| >= q^2 + (q^2 - q)/(sqrt(q) + 2)` (§2.4).
2. **Für Quadratzahlen ist `7/5` nicht das Ende (gebaut, §3):** Für `q = n^2` gibt es eine Liste mit
   `|R| = q^2 + 2*q*sqrt(q) - 2q` bei `v = q` und `|R| = q^2 + q*sqrt(q) - 2q + sqrt(q)` bei `v = q - sqrt(q)`; dazwischen kostet jedes weitere Symbol `q` Vertreter. Ohne Löser gebaut und mit zwei Zählern geprüft für `q = 4, 9, 16, 25, 49, 64, 81`.
3. Für Quadratzahlen liegt der Überschuss über `q^2` damit bei beiden Schranken in der Ordnung `q^(3/2)`; zwischen Untergrenze und Liste bleibt bei `v = q` ein Faktor von höchstens `2` im Term `q^(3/2)`.
4. **Listenwerte bei `q = 25`:** `705, 725, 750, 775, 800, 825` für `v = 20..25` (bisher im Repo: `730, 761, 792, 828, 863, 888`). Bei `q = 16`: `292, 304, 320, 336, 352` für `v = 12..16`. Bei `q = 9` bringt die Bauart nichts (`117` gegen `113`).
5. **Für Primzahlen ändert sich nichts Belegtes:** `7/5` bleibt der Boden *des Skeletts aus 1.3 mit den Klassen aus 1.2*. Im Modell insgesamt ist für Primzahlen nur die Untergrenze aus Satz 1 belegt (als Argument); ob mit Blokhuis ein fester Faktor über `1` folgt und ob ein zweiseitiges Skelett unter `7/5` kommt, ist offen (§5).

## 2. Untergrenze

### 2.1 Lemma J (Klassengröße gegen Zahl der getroffenen Waagerechten)

**Aussage.** Sei `q` eine Primzahlpotenz und `A` eine Punktmenge in `F_q^2`, die jede Gerade `c + al*d = u` trifft. Trifft `A` genau `m` der `q` Waagerechten `d = const`, dann ist `|A| >= q + m - 1`.

**Argument.** Auf jede der `q - m` nicht getroffenen Waagerechten einen Punkt dazunehmen. Die neue Menge trifft jede Gerade der affinen Ebene `AG(2, q)` und hat `|A| + q - m` Punkte. Nach Jamison (1977) und Brouwer–Schrijver (1978) hat eine solche Menge mindestens `2q - 1` Punkte.

Das Lemma gilt für jede Symbolklasse `A_s`, `B_s`, auch für solche mit voller Waagerechter. Gleichheit: volle Waagerechte allein (`m = 1`, `q` Punkte); Baer-Klasse (`m = sqrt(q) + 1`, `q + sqrt(q)` Punkte); Klasse `A(e)` aus `docs/PHASE8_ARGUMENTE.md` 1.2 (`m = (q + 3)/2`, `(3q + 1)/2` Punkte).

### 2.2 Satz U

**Aussage.** Sei `q` eine Primzahlpotenz, `v = q`, und `R` eine Vertreterliste, die die drei Bedingungen (Punktabdeckung, Geradentreffer, Symbolpaare) erfüllt. Dann
`|R| >= q^2 + q*sqrt(q)*(sqrt(q) - 1)/(sqrt(q) + 1)`.

**Argument.** Für die Waagerechte `d` sei `M_d` die Zahl der Vertreter auf ihr, `mu_d` die Zahl der `a`-Symbole und `nu_d` die Zahl der `b`-Symbole, die auf ihr vorkommen. Jedes Symbolpaar `(a, b)` wird einer Waagerechten zugeschlagen, auf der ein Vertreter mit diesem Paar liegt; `p_d` sei die Zahl der Paare, die `d` zugeschlagen sind. Dann `sum_d p_d = q^2`, `p_d <= M_d` (verschiedene Paare, verschiedene Vertreter) und `p_d <= mu_d * nu_d`.

- (a) Jeder Punkt braucht einen Vertreter, also `M_d >= q` und `M_d >= p_d`. Mit `E := sum_d max(0, p_d - q)` folgt `|R| = sum_d M_d >= q^2 + E`.
- (b) Jeder Vertreter trägt genau ein `a`-Symbol, also `|R| >= sum_s |A_s|`. Nach Lemma J ist `|A_s| >= q + m_s - 1`, und `sum_s m_s = sum_d mu_d`. Also `|R| >= q^2 - q + sum_d mu_d`, ebenso mit `nu_d`. Mittelwert und `(mu_d + nu_d)/2 >= sqrt(mu_d * nu_d) >= sqrt(p_d)` geben `|R| >= q^2 - q + sum_d sqrt(p_d)`.
- (c) Für jedes `p >= 0` ist `sqrt(p) >= min(p, q)/sqrt(q)`. Also `sum_d sqrt(p_d) >= (q^2 - E)/sqrt(q)`.
- (d) Aus (b), (c): `|R| >= q^2 - q + (q^2 - E)/sqrt(q)`. Diese Ungleichung plus `1/sqrt(q)` mal (a): `|R| * (1 + 1/sqrt(q)) >= q^2 - q + 2*q*sqrt(q)`. Auflösen ergibt die Behauptung.

`L(q)` bezeichne die kleinste ganze Zahl über der Schranke: `L = 5, 11, 19, 30, 58, 75, 95, 141, 196, 295, 709` für `q = 2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 25`.

**Was die Schranke nicht ist.** Sie benutzt für Primzahlen den Satz von Blokhuis nicht und ist dort vermutlich weit weg: bei `q = 23` steht `602` (verschärft `604`) gegen die Liste mit `746`. Für `v < q` gibt dasselbe Argument nichts über `q^2` hinaus.

### 2.3 Belege

| Prüfung | Ergebnis | Belegart |
| --- | --- | --- |
| Lemma J an jeder Symbolklasse aller `34` Listen in `data/phase7/`, `data/phase8/`, `data/phase8_repro/` und der `18` neuen Listen | `0` Verletzungen in `52` Listen; in jeder Liste wird die Schranke von mindestens einer Klasse mit Gleichheit angenommen | gezählt (`scripts/phase8/untergrenze.py listen`) |
| `|R| >= L(q)` an den `25` Listen mit `v = q` | `0` Verletzungen; kleinster Abstand `4` (`q = 5`: `34` gegen `30`) | gezählt |
| Exaktes Minimum des Modells für `q = 2, 3, 4` | `q = 2`: Minimum `5 = L(2)` (`OPTIMAL`), die Schranke ist dort scharf. `q = 3`: `12` gefunden, `L(3) = 11`, nach `300 s` **nicht** entschieden. `q = 4`: `22` gefunden, `L(4) = 19`, nach `300 s` **nicht** entschieden | CP-SAT (`scripts/phase7_solve_cpsat.py Q 300 min`), Positivkontrolle `fixknown` (`5`, `12`, `22`) |
| Satz U allgemein | – | **Argument**, von niemandem gegengelesen |

### 2.4 Verschärfung von Schritt (c) (Gemini, 27.11.2026; vom Erzeuger nachgerechnet)

**Aussage U'.** Unter den Voraussetzungen von Satz U gilt `|R| >= q^2 + (q^2 - q)/(sqrt(q) + 2)`.

**Argument.** Wegen `p_d <= mu_d * nu_d <= q^2` liegt jedes `p_d` in `[0, q^2]`. Die Wurzel ist konkav, liegt also auf `[q, q^2]` über der Sekante durch `(q, sqrt(q))` und `(q^2, q)` mit Steigung `1/(q + sqrt(q))`. Zusammen mit `sqrt(p) >= p/sqrt(q)` auf `[0, q]` heißt das für alle `p` in `[0, q^2]`:
`sqrt(p) >= p/sqrt(q) - max(0, p - q)/(sqrt(q) + 1)`.
Summieren: `sum_d sqrt(p_d) >= q*sqrt(q) - E/(sqrt(q) + 1)`. Mit (b) also `|R| >= q^2 - q + q*sqrt(q) - E/(sqrt(q) + 1)`. Diese Ungleichung plus `1/(sqrt(q) + 1)` mal (a): `|R| * (sqrt(q) + 2) >= q^(5/2) + 3q^2 - q`, und das ist die Behauptung.

Der Gewinn gegenüber Satz U ist `q*(sqrt(q) - 1)/((sqrt(q) + 1)*(sqrt(q) + 2))`, also weniger als `sqrt(q)`; die Größenordnung `q^2 + q^(3/2) - 2q` bleibt. `L'(q)` sei die kleinste ganze Zahl über der neuen Schranke:

| `q` | 2 | 3 | 4 | 5 | 7 | 8 | 9 | 11 | 13 | 16 | 17 | 19 | 23 | 25 | 27 | 49 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `L(q)` (Satz U) | 5 | 11 | 19 | 30 | 58 | 75 | 95 | 141 | 196 | 295 | 332 | 413 | 602 | 709 | 825 | 2659 |
| `L'(q)` (Aussage U') | 5 | 11 | 19 | 30 | 59 | 76 | 96 | 142 | 197 | 296 | 334 | 415 | 604 | 711 | 827 | 2663 |

Belegart: **informelles Argument** (Gemini), vom Erzeuger von Hand nachgerechnet; nach Regel 2d von keinem unbeteiligten Modell gelesen. Gezählt (`scripts/phase8/untergrenze.py listen`, Lauf `P8-U-VERSCHAERFUNG`): `0` Verletzungen in `72` Listen, davon `30` mit `v = q`; kleinster Abstand `4` (`q = 5`: `34` gegen `30`).

## 3. Das Baer-Gitter (`q = n^2`)

### 3.1 Bauart

`F_q = F_n + F_n*om` mit `om` außerhalb von `F_n`. Für `z` in `F_q` heißen `z_1, z_2` die Anteile in `z = z_1 + z_2*om`. Für `d != 0` sei `w = 1/d`.

- **`a`-Klasse `(i, j)`**, `i` in `F_n` ohne `0`, `j` in `F_n` (das sind `q - n` Symbole): auf `d = 0` die Punkte mit `c_2 = i`; auf jeder Waagerechten `d = 1/w` mit `w_2 = i` die Punkte `c`, für die der `om`-Anteil von `(c - i*om)*w` gleich `j` ist.
- **`b`-Klasse `(i, j)`**: auf `d = 0` dieselben Punkte `c_2 = i`; auf jeder Waagerechten mit `w_1 = i` die Punkte `c`, für die der `1`-Anteil von `(c - i*om)*w` gleich `j` ist.
- Jede Klasse hat `n` Punkte auf `d = 0` und je `n` Punkte auf `n` weiteren Waagerechten, zusammen `q + n`.
- Dazu `F` Symbole je Seite (`0 <= F <= n`), die auf `d = 0` an allen `q` Punkten stehen. Alphabet `v = q - n + F`.

Vertreter:

- Waagerechte mit `w_1 != 0` und `w_2 != 0` (`(n-1)^2` Stück): an jedem Punkt genau ein Vertreter, nämlich die eine `a`-Klasse und die eine `b`-Klasse, in denen der Punkt liegt.
- Waagerechte mit `w_2 = 0` (`n - 1` Stück): keine `a`-Klasse; `b` wie oben, `a` ist das Vollgeraden-Symbol mit der Nummer des `om`-Anteils von `c*w` (falls es das nicht gibt, ein Füllsymbol). Mit `w_1 = 0` umgekehrt.
- `d = 0`: an Punkten mit `c_2 = i != 0` die `n` Vertreter (`a`-Klasse `(i, j)`, `b`-Klasse `(i, j)`) und `F` Vertreter (Vollgeraden-Symbol `m` von `a`, Vollgeraden-Symbol `m` von `b`); an den `n` Punkten mit `c_2 = 0` die `F` Vertreter (`m`, `m + x mod F`), wobei `x` die Nummer von `c` ist (für `F = 0` ein Füllvertreter).

**Zählung.** `|R| = q(q - 1) + (q - n)(n + F) + n*max(F, 1)`. Für `F >= 1` ist das `q^2 + q*n - 2q + F*q`.

### 3.2 Warum das die drei Bedingungen erfüllt (Argument, knapp)

1. *Klassen.* Die Punkte `(x : z : z*w_0 + y*eps)` mit `x, y, z` in `F_n` bilden eine Baer-Unterebene von `PG(2, q)` (Bild von `F_n^3` unter einer über `F_q` invertierbaren Abbildung), sofern `w_0` nicht in `F_n*eps` liegt. Sie enthält den Fernpunkt der Waagerechten und trifft die Ferngerade nur dort. Ihr affiner Teil sind `n` Punkte auf `d = 0` und je `n` Punkte auf den `n` Waagerechten `d = 1/(w_0 + y*eps)`. Eine Baer-Unterebene trifft jede Gerade, also trifft der affine Teil jede nicht-waagerechte Gerade. Die Klassen oben sind Bilder solcher Mengen unter `(c, d) -> (k*c + r*d + t, d)` mit `eps = 1` für `a` und `eps = om` für `b`.
2. *Punkte.* Auf einer Waagerechten mit `w_2 = i != 0` liegt jeder Punkt in genau einer `a`-Klasse `(i, j)`, weil `c -> om`-Anteil von `(c - i*om)*w` jeden Wert gleich oft annimmt. Ebenso für `b`.
3. *Paare Klasse mit Klasse.* `a`-Klasse `(i, j)` und `b`-Klasse `(i', j')` liegen gemeinsam auf der einen Waagerechten mit `w = i' + i*om`. Dort ist `c -> (1`-Anteil, `om`-Anteil`)` von `c*w` eine Bijektion, also gibt es genau einen gemeinsamen Punkt.
4. *Paare mit Vollgeraden-Symbolen.* Jede `b`-Klasse `(i', j')` liegt auf genau einer Waagerechten mit `w_2 = 0` (nämlich `w = i'`) und trifft dort jedes Vollgeraden-Symbol von `a` einmal. Umgekehrt für `a`-Klassen. Die Paare zweier Vollgeraden-Symbole stehen an den `n` Punkten `c_2 = 0` von `d = 0`.

Belegart: Argument; dazu für jedes gebaute `q` gezählt (§3.3). Der Schluss von der Liste auf das Array beruht auf Aussage A bzw. A' aus `docs/PHASE7_T2_REDUCTION.md` (Argument) und ist an den geprüften Arrays in §4 bestätigt.

### 3.3 Gebaute Listen

Alle Listen: `python3 scripts/phase8/baer_gitter.py Q F --out DATEI` (std-only, ohne Löser, ohne Zufall). Prüfung je Liste mit dem eigenen Zähler im selben Skript (Punkte / Geradentreffer / Symbolpaare) und mit `scripts/phase7_lift.py --check-m` (für `v < q` mit `--v`).

| `q` | `v = q - n` | … | … | … | … | `v = q` | bisher bei `v = q` | `L'(q)` (§2.4) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 18 | 20 | | | | 24 | 22 (Phase 6A) | 19 |
| 9 | 93 | 99 | 108 | | | 117 | 113 (`data/phase8/`) | 96 |
| 16 | 292 | 304 | 320 | 336 | | 352 | 376 (Phase 6A) | 296 |
| 25 | 705 | 725 | 750 | 775 | 800 | 825 | 888 (`data/phase8_repro/`) | 711 |
| 49 | 2653 | | | | | 2989 | – | 2663 |
| 64 | 4488 | | | | | 4992 | – | – |
| 81 | 7137 | | | | | 7857 | – | – |

`0` Lücken in beiden Zählern für alle `18` Listen zu `q = 4, 9, 16, 25` (abgelegt in `data/phase8_baer/`); für `q = 49, 64, 81` nur der eigene Zähler, nur `F = 0` und `F = n`, nicht abgelegt.

Vergleich bei `q = 25` mit den bisherigen Listen des Repos: `v = 20`: `705` gegen `730` (Bauart §14 aus Phase 7); `v = 21`: `725` gegen `761`; `v = 22`: `750` gegen `792`; `v = 23`: `775` gegen `828`; `v = 24`: `800` gegen `863`; `v = 25`: `825` gegen `888`.

## 4. Arrays und Tabelle

Arrays aus `scripts/phase7_lift.py`, Prüfung mit `scripts/phase8/pruefe_baer.py` (Einzelheiten und SHA-256 in `results/phase8_baer/VERIFICATION_LOG_phase8_baer.md`).

- `t = 3`: alle `18` Arrays mit `verifiers/ca_verify` und `verifiers/verify_independent.py` Exit `0` (dazu der Zähler des Prüfers).
- `t = 4`, `q = 16`: alle `5` Arrays mit beiden Verifiern Exit `0`.
- `t = 4`, `q = 25`: `v = 20..24` mit `ca_verify` und dem Zähler des Prüfers Exit `0`, `verify_independent.py` **nicht gelaufen** (das sind nach `RULES.md` §3 keine gültigen Kandidaten). `v = 25`: ebenso; ein Lauf von `verify_independent.py` wurde nach `48 min` an der Zeitgrenze ohne Ergebnis abgebrochen.
- `t = 5, 6`: nicht erzeugt. Alle Zahlen dafür sind Vorhersage.

Gegen `ca-tools @ 697325b` (`scripts/pruefer/tabelle.py`, kleinster Wert über `k' >= k`):

| Zelle | Tabelle | Baer-Gitter | Stand |
| --- | ---: | ---: | --- |
| `(3, 27, 20)` | 17670 | 17625 | dual-verifiziert, abgelegt |
| `(3, 27, 21)` | 19025 | 18125 | dual-verifiziert, abgelegt |
| `(3, 27, 22)` | 19327 | 18750 | dual-verifiziert, abgelegt |
| `(3, 27, 23)` | 19524 | 19375 | dual-verifiziert, abgelegt |
| `(4, 18, 14)` | 82432 | 81920 | dual-verifiziert, abgelegt |
| `(4, 27, 20)` | 456250 | 440625 | nur `ca_verify` und Zähler des Prüfers |
| `(4, 27, 21)` | 523044 | 453125 | nur `ca_verify` und Zähler des Prüfers |
| `(4, 27, 22)` | 531431 | 468750 | nur `ca_verify` und Zähler des Prüfers |
| `(4, 27, 23)` | 531433 | 484375 | nur `ca_verify` und Zähler des Prüfers |
| `(4, 27, 24)` | 531435 | 500000 | nur `ca_verify` und Zähler des Prüfers |
| `(4, 27, 25)` | 531437 | 515625 | nur `ca_verify` und Zähler des Prüfers |
| `(5, 18, 14)`, `(5, 18, 15)` | 1419851, 1419853 | 1310720, 1376256 | nur Vorhersage |
| `(6, 18, 14)`, `(6, 18, 15)`, `(6, 18, 16)` | 24137563, 24137565, 24137567 | 20971520, 22020096, 23068672 | nur Vorhersage |
| `(5, 27, 20..25)` | 12872657 … 14348903 | 11015625 … 12890625 | nur Vorhersage |
| `(6, 27, 20)`, `(6, 27, 21)`, `(6, 27, 22)`, `(6, 27, 24)`, `(6, 27, 25)` | 296071749 … 387420485 | 275390625 … 322265625 | nur Vorhersage |

Nicht kleiner als die Tabelle: alle Zellen zu `q = 4` und `q = 9`; `(3, 18, 12..16)`, `(4, 18, 12)`, `(4, 18, 13)`, `(4, 18, 15)`, `(4, 18, 16)`, `(5, 18, 12)`, `(5, 18, 13)`, `(5, 18, 16)`, `(6, 18, 12)`, `(6, 18, 13)`; `(3, 27, 24)`, `(3, 27, 25)`, `(6, 27, 23)`. Zusammen `27` von `72` Zellen kleiner, `45` nicht. Drei der Tabellenwerte sind die eigenen aus PR `#91`: `(3, 27, 21)`, `(4, 18, 14)`, `(4, 27, 20)`. Offene Pull Requests und Issues des Ziels sind nicht durchgesehen (Regel 2b).

## 5. Was das für „Ist `7/5` das Ende?“ heißt

- **Quadratzahlen:** nein. Der Überschuss über `q^2` ist von der Ordnung `q^(3/2)`, nicht `q^2`. Offen ist der Faktor (zwischen `1` und `2` bei `v = q`).
- **Primzahlen:** nichts Neues belegt. Die Schranke `7/5` aus `docs/PHASE8_ARGUMENTE.md` 1.4 gilt für ein Skelett mit einer Klassenfamilie. Zwei Dinge sind **Überschlag, weder gebaut noch ausgeschrieben:**
  1. Ein zweiseitiges Skelett (Klassen ohne volle Gerade auf der `a`- **und** der `b`-Seite, je etwa `q/4` Klassen, je `(q-1)/2` reine Geraden) käme rechnerisch auf etwa `11/8 * q^2` statt `7/5 * q^2`. Bei `q <= 43` läge es nach dem Überschlag nicht unter den Löserlisten (`q = 37`: etwa `1946` gegen `1942`), wäre also nur für die Forschungsfrage von Belang, nicht für die Tabelle. Offen ist unter anderem die Belegung der schweren Geraden, wenn beide Seiten Klassen tragen.
  2. Mit dem Satz von Blokhuis (Klasse ohne volle Gerade hat mindestens `(3q+1)/2` Punkte) und der Bilanz aus 1.5 sollte für Primzahlen ein fester Faktor über `1` folgen (Überschlag: etwa `1,2 * q^2`). Die Fallunterscheidung über mehrere schwere Geraden habe ich nicht zu Ende geführt; das ist **keine** Aussage.
- **Andere Primzahlpotenzen (`q = 8, 27, 32`):** Für `q = s^h` gibt es entsprechende Klassen mit `q + q/s` Punkten. Ein Überschlag für `q = 27` (`s = 3`) ergibt bei `v = 24` etwa `1026`, also mehr als die Regel-Liste mit `930`. Nicht gebaut.

## 6. Läufe (Vorab-Festlegung vom 27.11., 06:37 MEZ: Positivkontrolle, Abbruch, Zeitgrenze)

Siehe `docs/RUN_LOG.md`, Läufe `P8-BAER-GITTER`, `P8-BAER-ARRAYS`, `P8-U-LISTEN`, `P8-U-EXAKT`, `P8-GEMINI-BAER`.

Zeit: festgelegt waren `45 min` insgesamt; gebraucht `53 min` (06:38–07:31 MEZ). Die Überschreitung kommt aus dem einen Lauf von `verify_independent.py` für `CA(515625; 4, 27, 25)`, den ich auf `17 min` geschätzt hatte und nach `48 min` abgebrochen habe. Kein Suchlauf wurde verlängert oder wiederholt.

## 7. Offen und Grenzen

1. **Literatur (Regel 2c):** nicht geprüft. Baer-Unterebenen, lineare Mengen und Zerlegungen der affinen Ebene in Baer-Unterebenen sind Standardstoff; ob jemand sie für Covering Arrays mit `k = q + 2` benutzt hat, weiß ich nicht. Zu prüfen sind mindestens Bai (2026) samt Begleitarbeit, CKRS (2010) im Original und die Zenodo-Volltexte.
2. **Fremdprüfung:** Satz U und §3.2 sind Argumente des Erzeugers. Ein Nachbau der Listen aus §3.1 ohne `scripts/phase8/baer_gitter.py` fehlt.
3. **Arrays:** `t = 4` bei `q = 25` für `v = 20..25` nur mit `ca_verify` und dem Zähler des Prüfers; `t = 5, 6` nicht erzeugt.
4. **Nicht versucht:** Löser auf der Geraden `d = 0`; billigere Vollgeraden-Symbole bei `v = q`; Geminis Vorschlag mit sechs Baer-Klassen je Seite im alten Skelett (Lauf `P8-GEMINI-BAER`: seine Einzelklasse stimmt, die Überschläge `853` und `729` sind nicht gerechnet).
5. Bei `q = 4`, `v = 2, 3` schlägt die Negativkontrolle „letzte Zeile entfernt“ nicht an: die Arrays haben dort überzählige Zeilen (`72` und `80` Zeilen gegen `12` und `33` in der Tabelle). Das ist kein Fehler der Verifier.

## 8. Nachtrag 27.11.2026, 10:20 MEZ: Gegenlesen und Nachbau

- **Gegenlesen durch Gemini (Planer, kein unbeteiligtes Modell):** kein Befund zu §2.1, §2.2 und §3; dazu ein direkter Nachweis der Geradentreffer für `a`- und `b`-Klassen ohne projektive Ebene (auch in Charakteristik `2`) und die Verschärfung in §2.4. Der Erzeuger hat beides nachgerechnet. Belegart bleibt „Argument“; die Prüfung nach Regel 2d steht aus (Auftrag vorbereitet in `docs/openrouter/PHASE8_NOTIZ3_AUFTRAG.md`, **nicht abgeschickt**).
- **Blinder Nachbau durch Antigravity (PR `#45`, `scripts/phase8_baer_spec_repro.py`):** `20` Listen aus der Beschreibung in §3.1, die `18` gemeinsamen byte-gleich zu `data/phase8_baer/`; Einzelheiten im Lauf `P8-BAER-ABGLEICH-PR45`. Das belegt Beschreibung und Umsetzung auf einer zweiten Maschine, nicht die Mathematik unabhängig vom Erzeuger.
- **Unverändert offen:** Literaturprüfung nach Regel 2c (§7.1), `verify_independent.py` für `t = 4` bei `q = 25`, `t = 5, 6`.
