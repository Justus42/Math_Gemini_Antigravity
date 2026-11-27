# Notiz: Prüfung der vier Optionen und ein weiterer Ansatz (Klassen ohne volle Gerade)

- Stand: 2026-11-26, 20:42 MEZ (Zeit der Datei; im Chat stand „ca. 21:00“). Autor: Claude (eigener Chat, damals nur Lesezugriff auf das Repo).
- Im Repo abgelegt am 27.11.2026, sonst unverändert. Einstieg und Berichtigungen: [`docs/PHASE8_UEBERSICHT.md`](../PHASE8_UEBERSICHT.md). Die Liste `R_q19_m517.txt` ist durch `R_q19_m513.txt` ersetzt und nicht abgelegt; „Paket“ meint die Dateien in `data/phase8/` und `scripts/phase8/`.
- Vergleichsstand: `Math_Gemini_Antigravity @ e3100f6` (`main`), `chrispbsmolen/ca-tools @ e673ab4` (unverändert).
- **Rollenhinweis:** Alles hier ist Rechnung eines Prüfers und damit nicht fremdgeprüft. Nichts liegt im Repo.
  Kein Neuheitsanspruch; eine Literaturprüfung nach `RULES.md` 2c zu Abschnitt 3 fehlt.
- Schreibweise wie in `docs/PHASE7_T2_REDUCTION.md` §2: Vertreter `(c, d, a, b)`, Tabelle `M(R)`.

## 1. Ergebnis in vier Sätzen

1. Jede Symbolklasse von `a` oder `b` enthält entweder eine volle Gerade `d = const` oder hat mindestens
   `q + sqrt(q)` Punkte (für Primzahl `q`: mindestens `(3q+1)/2`). In allen sieben Löserlisten des Repos sitzt
   die Ersparnis genau in den Klassen ohne volle Gerade.
2. Baut man solche Klassen gezielt aus Rédei-Mengen (Graph von `x -> x^((q+1)/2)`), entstehen Listen mit
   weniger Vertretern als im Repo: `q = 9`: 113 (Repo 116), `q = 11`: 170 (175), `q = 13`: 238 (247),
   `q = 17`: 412 (425), `q = 19`: 517 (532).
3. Damit sind 13 der 37 Arrays des laufenden Pakets (alle mit `v = q` und `q = 9, 11, 13, 17, 19`) unterboten.
4. Von Geminis Optionen trägt A (in dieser geschärften Form); B ist im Test durchgefallen; C steht zu großen
   Teilen schon bei Bai (2026) oder scheitert an einer Rangbedingung; D ist reine Logistik.

## 2. Geminis Optionen

### A. Lücke im Modell verstehen — trägt

- Die Aussage „eine `q`-Menge, die alle Geraden der `q` Richtungen trifft, ist eine Gerade `d = const`“ stimmt.
- Schärfer (Abschnitt 3.1): Nimmt man den gemeinsamen Fernpunkt `P` der Geraden `d = const` hinzu, wird jede
  Symbolklasse eine blockierende Menge der projektiven Ebene. Dafür gelten die Schranken von Bruen und Blokhuis.
- Die Frage „Ersparnis konstant oder wachsend“ ist für die neue Bauart beantwortet, soweit gerechnet:
  6, 9, 13, 15 Blöcke unter `q^2 + C(q, 2)` bei `q = 11, 13, 17, 19`.

### B. Kern mit nur einer Nullspalte — im Test negativ

Getestet: gleiche Polynom-Vertreter `(c x^(t-2) + d x^(t-1), e, b)`, drei Kerne, `t = 3`, CP-SAT mit Zeitlimit.

| Kern | `q = 5` | `q = 7` |
| --- | --- | --- |
| `Z2`: zwei Nullspalten (Repo, `K_t`) | 34 (120 s) | 68 (Repo) |
| `Z1`: eine Nullspalte | 40 (240 s) | 91 (150 s) |
| `Z0`: keine Nullspalte | 42 (150 s) | 91 (150 s) |

Belegart: bestes gefundenes `m` je Lauf, nichts ausgeschlossen. Positivkontrolle: `Z2`, `q = 5` liefert 34 und
300 verschiedene Bedingungen wie im Repo.

Einordnung: Die beiden 33er-Arrays der Tabelle haben **frei gesuchte** Vertreter (Sitjar: lokale Suche über
fehlende Nebenklassen, danach Zeilen gestrichen; Bai/Tabelle: Starterzeilen mit Tabu/SAT). Der Unterschied zu
34 kommt also nicht belegbar vom Kern. Für freie Vertreter gibt es keine Formel, die Rechnung hängt an `t`,
und bei `q = 7` liegt die Tabelle (`3556 = 508 * 7`, Einsen-Kern) schon über den `3332` des Repos.

### C. Mehr Spalten und Hyperovale — größtenteils schon vorhanden oder nicht möglich

- Hyperoval-Basis: Ein Array vom Index eins mit `q + 2` Spalten gibt es für gerades `q` nur bei `t = 3` und
  `t = q - 1` (Bai 2026, §1 und Prop. 4.1(c)). Für `t = 4, 5, 6` gibt es die „stärkere Basis“ nicht.
- Für `t = 3` ist der Weg gegangen: Bai, Satz 7.2 und Kor. 7.3, `CAN(3, q+3, q) <= q^3 + (q - c) CAN(2, q+2, q)`;
  die Tabelle führt `(3, 11, 8) = 812` und `(3, 19, 16) = 6376` mit diesem Etikett.
- Zwei neue Spalten (`k = q + 3`) für ungerades `q`: Bai, Satz 6.2.
- „Derselbe Kern `K_t` mit drei freien Spalten“: Auf `t - 3` Auswertungsspalten plus drei freien Spalten hat
  `K_t` nur Rang `t - 3`. Dann muss jedes Tripel `(a_1, a_2, a_3)` als Vertreter vorkommen, also `|R| >= v^3`
  und `N >= v^3 q^(t-2)`. Für `v` nahe `q` ist das wertlos. Nötig wäre ein Kern der Dimension `t - 3` und ein
  kleines Modell der Stärke 3. Belegart: Argument, nicht gerechnet. (`docs/T4_ODD_Q_NEAR_BUSH.md` §11 hatte
  `k = q + 3` schon mit „3/4 Untergrenzen über Tabelle“ abgeschlossen.)

### D. Die übrigen Zellen über `EXTERNAL.csv` — möglich, keine Mathematik

`table/EXTERNAL.csv` existiert und wird benutzt (Bais Zenodo-Ablage). Die Zahlen 4 + 36 stimmen mit
`docs/PHASE7_ZUSCHNITT.md` überein. Vor einer Ablage sollte Abschnitt 3 entschieden sein, sonst liegen dort
gleich wieder überholte Dateien.

## 3. Klassen ohne volle Gerade

### 3.1 Aussage (Argument)

Sei `A_s` die Menge der Punkte `(c, d)`, an denen ein Vertreter mit `a = s` steht (ebenso für `b`). Bedingung 2
des Modells sagt: `A_s` trifft jede Gerade `c + al*d = u`. Sei `P` der Fernpunkt der Geraden `d = const`.
Dann trifft `A_s ∪ {P}` jede Gerade von `PG(2, q)`. Eine Gerade, die ganz in `A_s ∪ {P}` liegt, geht durch `P`
und ist nicht die Ferngerade, ist also eine Gerade `d = const`. Folglich:

- `A_s` enthält eine volle Gerade `d = const`, **oder**
- `|A_s| >= q + sqrt(q)` (Bruen), für Primzahl `q` sogar `|A_s| >= (3q + 1)/2` (Blokhuis).

Abgelesen an den Listen in `data/phase7/` (`scripts`: `dissect.py` im Paket):

| Liste | Klassen ohne volle Gerade (Größe) | Schranke |
| --- | --- | --- |
| `q = 5`, `m = 34` | `a`: 1 (8) | 8 |
| `q = 7`, `m = 68` | `a`: 1 (12), `b`: 1 (13) | 11 |
| `q = 8`, `m = 91` | `a`: 1 (15), `b`: 1 (16) | 11 |
| `q = 9`, `m = 116` | `a`: 1 (19), `b`: 2 (16, 18) | 12 |
| `q = 11`, `m = 175` | `b`: 2 (22, 23) | 17 |
| `q = 5, v = 4`, `m = 27` | `b`: 1 (8) | 8 |
| `q = 7, v = 6`, `m = 58` | `a`: 1 (12), `b`: 1 (11) | 11 |

Alle anderen Klassen enthalten genau eine volle Gerade. Die Zahl der gesparten Blöcke ist nie größer als die
Zahl dieser Klassen.

Vermutung (Bilanz über Geradentypen gerechnet, **nicht** ausgeschrieben): Enthält jede Klasse eine volle Gerade,
dann `|R| >= q^2 + C(q, 2)`. Das würde erklären, warum Phase 6A und die „schwere Gerade“ aus §9 dieselbe Zahl
liefern.

### 3.2 Bauart für Primzahl `q` (Rédei-Klassen)

Skelett: schwere Gerade `d = 0`; `(q+1)/2` reine `b`-Geraden `DB`; `(q-3)/2` reine `a`-Geraden `DA`. Die
schwere Gerade trägt `h_a = (q+3)/2` Symbole von `a` und `h_b = (q-1)/2` Symbole von `b`. Ohne weiteres sind
das `q^2 + C(q, 2) + q` Vertreter, also `q` mehr als Phase 6A.

Auf jeder reinen `b`-Geraden ist `a` an `(q-3)/2` Punkten frei (die Paare „reines `a`, reines `b`“ deckt schon
die reine `a`-Gerade). In diese freien Plätze kommen für `n` der schweren `a`-Symbole Mengen `X` mit `q` Punkten:
das Bild des Graphen von `x -> x^((q+1)/2)` (Lovász–Schrijver, `(q+3)/2` Richtungen), so gelegt, dass eine
seiner Richtungen `P` ist und die Fernrichtungen auf die schwere Gerade fallen. Dann ist `X` zusammen mit
`(q+1)/2` Punkten `K` der schweren Geraden eine blockierende Menge, und das Symbol kann an den übrigen
`(q-1)/2` Punkten der schweren Geraden **wegfallen**. Je Punkt zählen bis zu zwei Streichungen.

`|R| = q^2 + C(q, 2) + q - G`, mit `G <= 2q` in diesem Skelett. Stoßen zwei Mengen `X` an einem Punkt
zusammen, kostet das einen Vertreter; das ist in `G` abgezogen.

`DB = { 1/(s - n0) : s Quadrat oder 0 }` mit dem kleinsten Nichtquadrat `n0`. Die Kandidaten `(X, K)` sind die
Bilder unter `(c, d) -> (k*c + r*d + t, d)`; ein CP-SAT-Modell wählt die Packung, ein zweites belegt die
schwere Gerade (`ls_pack.py`).

Für `q = 9` hat ein Löser im symmetrischen Skelett (vier reine `a`-, vier reine `b`-Geraden, schwere Gerade
mit 5 + 5 Symbolen, 873 statt 6561 Variablen) in 240 s `113` gefunden. Eine Überschlagsrechnung mit
Baer-Unterebenen (je ein Symbol von `a` und `b`, vier gemeinsame Streichungen) hatte vorher 113 ergeben; die
gefundene Liste benutzt aber größere Klassen (17 und 16 Punkte statt 12). Mit der anderen Aufteilung der
Geraden (Quadrate / Nichtquadrate) fand derselbe Lauf nur 116.

### 3.3 Listen und Prüfung

| `q` | Phase 6A | Repo | neu | `G` | Datei | SHA-256 (Anfang) |
| --- | --- | --- | --- | --- | --- | --- |
| 9 | 117 | 116 | **113** | — | `R_q9_m113.txt` | `dc679d6b…` |
| 11 | 176 | 175 | **170** | 17 | `R_q11_m170.txt` | `ee57c9fa…` |
| 13 | 247 | 247 | **238** | 22 | `R_q13_m238.txt` | `8008fff1…` |
| 17 | 425 | 425 | **412** | 30 | `R_q17_m412.txt` | `d9bfdfba…` |
| 19 | 532 | 532 | **517** | 34 | `R_q19_m517.txt` | `a8a99c81…` |

Belegart: bestes gefundenes `m`; die Packungen für `q = 13, 17, 19` endeten am Zeitlimit (150 s), mehr ist
nicht ausgeschlossen. Prüfung je Liste:

- `M(R)` ohne Lücke: eigener Zähler und `scripts/phase7_lift.py --check-m` (Repo), fünf von fünf.
- Arrays `t = 3` und `t = 4` aus `phase7_lift.py`: `verifiers/ca_verify.c` `PASS`, zehn von zehn.
- `t = 3`: `verifiers/verify_independent.py` `PASS`, fünf von fünf; `t = 4` dort nur `q = 9, 11`.
- Eigener Zähler auf eigenem Lift: `q = 9` (`t = 3, 4`), `q = 11` (`t = 3`).
- Negativkontrolle (letzte Zeile entfernt, `t = 3`): `FAIL` für `q = 9, 11, 13`.
- `t = 5, 6` nicht erzeugt (folgt aus Aussage A des Phase-7-Dokuments, die selbst Argument ist).
- Die Körpertabellen von `gfmod.py` und `GeneralGF` sind für `q = 8, 9, 16, 25, 27` gleich (verglichen).

```
python3 scripts/phase7_lift.py --q 11 --reps R_q11_m170.txt --check-m --t 3 --out CA_1870_3_13_11.txt
sha256sum CA_1870_3_13_11.txt   # 30c5db61f054af9747c17b7b5bd900e3a280fb05515a0def0aacd9448bbed4cc
```

### 3.4 Zellen gegen `ca-tools @ e673ab4`

| Zelle | Tabelle | Repo | neu | Stand |
| --- | --- | --- | --- | --- |
| `(3, 11, 9)` | 1089 | 1044 | **1017** | erzeugt und geprüft |
| `(4, 11, 9)` | 9801 | 9396 | **9153** | erzeugt und geprüft |
| `(5, 11, 9)` | 88209 | 84564 | 82377 | nur Vorhersage |
| `(6, 11, 9)` | 793881 | 761076 | 741393 | nur Vorhersage |
| `(3, 13, 11)` | 1991 | 1925 | **1870** | erzeugt und geprüft |
| `(4, 13, 11)` | 21901 | 21175 | **20570** | erzeugt und geprüft |
| `(5, 13, 11)` | 240911 | 232925 | 226270 | nur Vorhersage |
| `(6, 13, 11)` | 2650021 | 2562175 | 2488970 | nur Vorhersage |
| `(3, 15, 13)` | 3289 | 3211 | **3094** | erzeugt und geprüft |
| `(4, 15, 13)` | 42757 | 41743 | **40222** | erzeugt und geprüft |
| `(5, 15, 13)` | 555841 | 542659 | 522886 | nur Vorhersage |
| `(4, 19, 17)` | 125137 | 122825 | **119068** | erzeugt und geprüft |
| `(5, 19, 17)` | 2127329 | 2088025 | 2024156 | nur Vorhersage |
| `(3, 21, 19)` | 10279 | 10108 | **9823** | erzeugt und geprüft |
| `(4, 21, 19)` | 195301 | 192052 | **186637** | erzeugt und geprüft |
| `(5, 21, 19)` | 3710719 | 3648988 | 3546103 | nur Vorhersage |

`(3, 19, 17)`: `7004` ist nicht kleiner als die Tabelle (`6778`). Die `t = 6`-Zellen zu `q = 13, 17, 19`
verschieben sich entsprechend (nur Vorhersage, über 50 MiB).

Im 37er-Paket betroffen (13 Dateien): `(3..6, 11, 9)`, `(3..5, 13, 11)`, `(3..5, 15, 13)`, `(4, 19, 17)`,
`(3, 21, 19)`, `(4, 21, 19)`. Nicht betroffen: alle Zellen mit `v < q` und `q = 5, 7, 8`.

### 3.5 Was offen ist

1. Fremdprüfung und Nachbau durch Antigravity; Literaturprüfung (Bai 2026 arbeitet mit **einer** neuen Spalte
   und Überdeckungen durch blockierende Mengen, Prop. 5.2 und 5.4; die Verbindung zu Rédei-Mengen steht in den
   gelesenen Teilen nicht, die Prüfung ist nicht vollständig).
2. Bessere Packung: Die Grenze `G = 2q` ist bei keinem `q` erreicht (17 von 22, 22 von 26, 30 von 34, 34 von 38).
3. Mehr reine `b`-Geraden (`(q+1)/2 + j`): Start `q(1 + j)` schlechter, Grenze `G <= (2 + 2j) q`. Nicht gerechnet.
4. `q = 7, 8` (Repo: 68, 91) und `q = 5` (34): mit diesen Skeletten nichts Besseres gefunden bzw. nicht gerechnet
   (`q = 8` braucht eine Bauart für gerades `q`, etwa additive Funktionen mit `q/2 + 1` Richtungen).
5. Quadratzahlen `q`: Baer-Unterebenen sind billiger (`q + sqrt(q)` statt `(3q+1)/2`); nur `q = 9` gerechnet.
6. `v < q`: nicht untersucht. Eine Überschlagsrechnung für `v = q - 1` ergibt höchstens 3 Blöcke unter §14.
7. Untere Schranke im Modell mit Klassen ohne volle Gerade: offen.

## 4. Weitere Ansätze aus der Literatur

- **Bai (2026), offene Fragen 2 und 3:** Gefragt ist `lim sup CAN(t, q+2, q) / q^t` für festes `t >= 4`; bekannt
  ist `<= 3/2`. Phase 6A/7 und Abschnitt 3 liegen knapp darunter, aber mit Ersparnis der Ordnung `q` gegen
  `q^2`; ob Abschnitt 3 mit wachsendem `j` einen festen Anteil spart, ist offen und wäre die eigentliche
  Forschungsfrage.
- **Richtungen und Rédei-Mengen:** Rédei (1970); Lovász–Schrijver (1981); Blokhuis–Ball–Brouwer–Storme–Szőnyi
  (1999) und Ball (2003) klassifizieren Funktionen mit weniger als `(q+3)/2` Richtungen (linear über einem
  Teilkörper). Das sagt, welche Klassen es für `q = p^h` gibt: Baer (`q` Quadrat), `q/p^e + 1` Richtungen sonst.
- **Bruen (1970/71), Blokhuis (1994):** Größe nichttrivialer blockierender Mengen (Abschnitt 3.1).
- **Nachoptimierung (Nayeri–Colbourn–Konjevod 2013; Sitjar 2026, §2.4):** Sitjar hat Bais Arrays an denselben
  Zellen um `0,01 %` bis etwa `5 %` gekürzt. Für unsere Arrays nicht getestet. Argument: An Punkten mit nur einem
  Vertreter ist jede Zeile die einzige für ihre Tupel auf Auswertungsspalten; Spielraum bleibt nur an
  mehrfach belegten Punkten.
- **CKRS (2010), Satz 8.1:** untere Schranke `CAN(3, q+2, q) >= q^3 + 12` für ungerades `q >= 11` (so lese ich
  Bai, §12; der Textauszug war lückenhaft, im Original nicht nachgelesen). Zwischen `q^3` und etwa `1,4 q^3`
  ist also fast nichts bekannt.

## 5. Dateien im Paket

`R_q9_m113.txt`, `R_q11_m170.txt`, `R_q13_m238.txt`, `R_q17_m412.txt`, `R_q19_m517.txt` (Vertreterlisten, Format
wie `data/phase7/`, ohne Kopfzeile); `gfmod.py` (Körper), `skeleton.py`, `skeleton2.py` (Modell im Skelett),
`ls_pack.py` (Rédei-Klassen packen, Liste bauen), `coset_model.py` (Kernvergleich aus 2B), `count_ca.py`
(eigener Zähler), `dissect.py` (Tabelle in 3.1). Die Läufe mit Zeitlimit sind nicht bytegenau wiederholbar;
maßgeblich sind die Listen.
