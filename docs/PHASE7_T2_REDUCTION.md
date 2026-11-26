# Phase 7: Rückführung auf Stärke 2, die Fälle `q = 5, 7, 8, 9` (`docs/PHASE7_T2_REDUCTION.md`)

Stand: 2026-11-26, ca. 20:30 MEZ (§8 zu `q = 7`, §9 zu `q = 8, 9, 11`, §10 zu den längeren Läufen `q = 11, 13`, §11 zu `v < q`, §12 Korrektur, §13 zweite Läufe, §14 geschlossene Bauart für `v < q` nachgetragen). Autor: Claude (Prüfer-Chat), auf Wunsch von Justus als eigene Rechnung
(Schritte 1 und 2 aus Geminis Phase-7-Plan). Vergleichsstand: `chrispbsmolen/ca-tools @ e673ab4`.

**Rollenhinweis:** Diese Rechnung stammt vom Prüfer. Sie ist damit *nicht* fremdgeprüft. Antigravity soll
sie nachbauen und nach den Repo-Regeln dual verifizieren, bevor etwas nach `results/` geht.

## 1. Ergebnis in drei Sätzen

1. Ein Array aus Nebenklassen des Kerns `K_t` ist durch eine Liste `R` von Vertretern `(c, d, a, b)` festgelegt.
   Es hat Stärke `t`, sobald eine kleine Tabelle `M(R)` mit `|R|` Zeilen und `q + 2` Spalten Stärke 2 hat.
2. Für `q = 5` gibt es eine solche Liste mit **34** statt 35 Vertretern (`data/phase7/R_q5_m34.txt`).
3. Daraus entsteht `CA(4250; 5, 7, 5)`. Die Tabelle führt für `(5, 7, 5)` den Wert `4375` (`CITED`, Ji-Li-Yin).
   Bei `t = 3` und `t = 4` bleibt die Tabelle besser (`170 > 165`, `850 > 825`).

## 2. Definitionen

- `q` Primzahlpotenz, `2 <= t <= q + 2`. Vertreter `(c, d, a, b)` aus `GF(q)^4`. Körper und Elementnummern
  wie in `scripts/gen_general_tqv.py` (`GeneralGF`).
- `M(R)`: je Vertreter eine Zeile mit den Spalten `c + al*d` für `al = 0, ..., q-1`, dann `a`, dann `b`.
- `L_t(R)`: je Vertreter und je `(a_0, ..., a_{t-3})` die Zeile `(P(0), ..., P(q-1), a, b)` mit
  `P(x) = a_0 + ... + a_{t-3} x^(t-3) + c x^(t-2) + d x^(t-1)`. Das sind `|R| * q^(t-2)` Zeilen.
- Konventionen: Die Nummern `0` und `1` stehen für die Körpernull und -eins (so in `GeneralGF`). Zeilen werden mit
  Vielfachheit gezählt; ein Vertreter ist eine Koeffizientenvorgabe, verschiedene Vertreter können für `t > q`
  dieselbe Zeile liefern.
- Die Bauart aus Phase 6A ist `R = {(c, d, d, min(c,d))} ∪ {(c, d, c, d): c < d}` mit `|R| = q^2 + C(q,2)`.
  Gegenprobe: `phase7_lift.py --q 5 --known --t 5` liefert dieselbe Zeilenmenge wie
  `gen_general_tqv.py --t 5 --q 5 --v 5` (sortiert `sha256:49b6c01b…`).

## 3. Aussage und Belegart

**Aussage A (hinreichend).** Ist `M(R)` ein `CA(m; 2, q+2, q)`, dann ist `L_t(R)` ein
`CA(m * q^(t-2); t, q+2, q)` für alle `2 <= t <= q + 2`.

Argument, nach Anzahl `j` der gewählten Auswertungsspalten:
- `j = t`: jedes Polynom vom Grad `<= t-1` muss vorkommen, also jedes `(c, d)`. Zwei Spalten
  `c + al*d`, `c + be*d` legen `(c, d)` fest; ihre Paarüberdeckung in `M(R)` liefert das.
- `j = t - 1` plus `a` (oder `b`): Polynome mit festen Werten auf `S` sind `f_0 + la * prod(x - s)`.
  Dabei läuft `(c, d)` über die Gerade `c + sigma*d = const` mit `sigma = Summe von S`. Nötig ist: auf dieser
  Geraden kommt jedes Symbol in `a` vor. Das ist die Paarüberdeckung der Spalten `al = sigma` und `a` in `M(R)`.
- `j = t - 2` plus `a` und `b`: zu jedem `(c, d)` und jeder Wertevorgabe auf `S` gibt es genau ein
  `(a_0, ..., a_{t-3})`. Nötig ist nur, dass jedes Paar in `(a, b)` vorkommt.

Präzisierungen (nach Gegenlesen durch Gemini, 26.11.2026; am Argument ändert sich nichts):
- Leere Fälle: `j = t` kommt nur für `t <= q` vor, `j = t - 1` nur für `t <= q + 1`; für `t = q + 2` bleibt allein
  `j = t - 2` (alle `q` Auswertungsspalten plus `a` und `b`).
- `P(x) = f_0(x) + la * prod_{s in S}(x - s)` ist als formales Polynom in `GF(q)[x]` gemeint, nicht reduziert modulo
  `x^q - x`. Für `t = q + 1` ist `S = GF(q)` und das Produkt gleich `x^q - x`; es hat Grad `t - 1` und verschwindet
  auf ganz `GF(q)`.
- Richtung bei `j = t - 1`: Sei `f_0` der Interpolant vom Grad `<= t - 2` der Zielwerte auf `S`, `u` sein
  Koeffizient bei `x^(t-2)`. Nach Voraussetzung gibt es einen Vertreter `(c, d, a, b)` mit `c + sigma*d = u` und dem
  gewünschten `a` (bzw. `b`). Dann hat `f_0 + d * prod(x - s)` die obersten Koeffizienten `c` und `d`, und seine
  unteren Koeffizienten legen die Zeile fest.
- Bei `j = t - 2` ist `(a_0, ..., a_{t-3})` eindeutig: es interpoliert `y_x - c x^(t-2) - d x^(t-1)` auf den `t - 2`
  Punkten von `S` (für `t = 2` das leere Tupel).

**Aussage B (notwendig).** Für Primzahl `q` und `2 <= t <= q` gilt auch die Umkehrung, weil dann jedes
`sigma` als Summe einer `(t-1)`-Menge auftritt.

| Aussage | Belegart |
| --- | --- |
| A für `q = 5`, `t = 3, 4, 5`, beide Listen (35 und 34) | **nachgezählt** (vier Programme, siehe §5) |
| A für `q = 7`, `t = 3, 4`, Phase-6A-Liste und zyklische Liste | **nachgezählt** (eigenes Programm); Phase-6A-Liste bei `t = 5, 6` über die Arrays aus PR `#22` |
| A allgemein | **Argument**, nicht formal geprüft |
| B | **Argument**; gestützt durch Gegenproben (eine Zeile weniger: `M` und Lifts fallen gemeinsam durch) |
| A für `q = 8, 9`, `t = 3..6`, Phase-6A-Liste (`t = 4`) und neue Listen | **nachgezählt** (§9) |

## 4. Schritt 1: Die beiden 33er-Arrays der Tabelle sitzen nicht auf `K_t`

Translationsstabilisator direkt aus den Tabellen-Dateien bestimmt (Belegart: **nachgerechnet**):
- `CA(165; 3, 7, 5)` (Bai): 33 Nebenklassen des Codes `<(1,1,1,1,1,1,1)>`, zusätzlich skalierungsinvariant.
- `CA(825; 4, 7, 5)` (Sitjar): 33 Nebenklassen eines 2-dimensionalen Codes mit genau einer Nullspalte.
- `K_t` hat zwei Nullspalten. Beide Arrays liegen also auf einem anderen Code; ihre 33 ist nicht übertragbar.

## 5. Schritt 2: Exaktes Modell für `q = 5`

Modell: 625 0/1-Variablen, 525 Paarbedingungen (300 verschiedene), `m` minimieren. Löser: OR-Tools CP-SAT
`9.15`, 2 Worker, `scripts/phase7_solve_cpsat.py`. Gates vorab festgelegt: Positivkontrolle, 5 Minuten je
Lauf. Gemacht wurden zwei Suchläufe.

| Lauf | Aufruf | Dauer | Ergebnis |
| --- | --- | --- | --- |
| Positivkontrolle | `5 30 fixknown` | `< 1 s` | Phase-6A-Liste (35) erfüllt das Modell |
| Minimierung | `5 300 min` | `300 s` (Limit) | **`m = 34` gefunden**, Optimalität nicht bewiesen |
| Entscheidung | `5 300 atmost 33` | `300 s` (Limit) | `UNKNOWN` |

**Belegart: bestes gefundenes `m = 34`; ob `33` möglich ist, ist offen (weder Lösung noch Ausschluss).**
Der Löserlauf ist wegen Zeitlimit und zwei Workern nicht bytegenau wiederholbar. Das Ergebnis ist die
Vertreterliste; alles Weitere ist deterministisch.

Prüfung der drei Arrays (alle deterministisch aus `data/phase7/R_q5_m34.txt`):

| Array | SHA-256 | `verifiers/ca_verify.c` | `verify_independent.py` | `ca-tools` `ca_verify` | eigenes Zählprogramm |
| --- | --- | --- | --- | --- | --- |
| `CA(170; 3, 7, 5)` | `a2b849e9…4f78e3` | PASS | PASS | PASS | PASS |
| `CA(850; 4, 7, 5)` | `4a607117…d1a1c2` | PASS | PASS | PASS | PASS |
| `CA(4250; 5, 7, 5)` | `0fb696c8…4505ec` | PASS | PASS | PASS | PASS |

Negativkontrolle: `CA_4250` ohne die letzte Zeile → `FAIL`; Liste ohne den letzten Vertreter → `t = 3`: 110 Lücken.

Die Arrays liegen bewusst **nicht** in `results/`. Erzeugen:

```
python3 scripts/phase7_lift.py --q 5 --reps data/phase7/R_q5_m34.txt --check-m --t 5 --out CA_4250_5_7_5.txt
sha256sum CA_4250_5_7_5.txt   # 0fb696c821d25467be4d6625b37f81d0cb7956afb47350ed9f035ca9104505ec
```

## 6. Einordnung gegen `ca-tools @ e673ab4`

| Zelle | Tabelle | 35 Blöcke | 34 Blöcke | Schwelle |
| --- | --- | --- | --- | --- |
| `(3, 7, 5)` | `165` (`VERIFIED`, Bai) | `175` | `170` | `<= 32` Blöcke |
| `(4, 7, 5)` | `825` (`VERIFIED`, Sitjar) | `875` | `850` | `<= 32` Blöcke |
| `(5, 7, 5)` | `4375` (`CITED`, Ji-Li-Yin) | `4375` | **`4250`** | erreicht |
| `(6, 7, 5)` | `15625` (`CITED`, OA) | `21875` | `21250` | nicht erreichbar |

Folgerung: Die Konstante `C(q,2)` in `q^t + C(q,2) * q^(t-2)` ist für `q = 5` nicht bestmöglich.
Für `q = 7` siehe §8.

## 7. Offen

1. `q = 5`: Ist `33` möglich? (Exakter Lauf mit Symmetriebrechung oder längerem Budget.)
2. `q = 7`: Ist `67` möglich? (`67` würde `(3,9,7) = 472` schlagen.) `q = 8, 9, 11`: siehe §9. `q = 13, 19`: nicht gerechnet.
3. Struktur: In beiden Listen trägt eine Gerade `d = const` die Zusatzlast (`q = 5`: 12 von 34 Zeilen;
   `q = 7`: 25 von 68), auf den meisten übrigen ist `a` oder `b` konstant. Keine Bauregel abgeleitet.
4. Literatur zu `(5, 7, 5)`: Quelle Ji-Li-Yin (`4375`) nicht gelesen; `4250` nur gegen die Tabelle verglichen.

## 8. Nachtrag `q = 7` (2026-11-26, 10:34–10:45 MEZ)

Modell: 2401 Variablen, 1764 Paarbedingungen (784 verschiedene). Gates wie in §5: Positivkontrolle, 5 Minuten
je Lauf, zwei Suchläufe.

| Lauf | Aufruf | Dauer | Ergebnis |
| --- | --- | --- | --- |
| Positivkontrolle | `7 60 fixknown` | `< 1 s` | Phase-6A-Liste (70) erfüllt das Modell |
| Minimierung, Start bei 70 | `7 300 hint` | `300 s` (Limit) | **`m = 68` gefunden** |
| Minimierung, Start bei 68 | `7 300 hintfile R_q7_m68.txt` | `300 s` (Limit) | keine Verbesserung (`68`) |

**Belegart: bestes gefundenes `m = 68`; ob `67` möglich ist, ist offen.**

| Zelle | `ca-tools @ e673ab4` | Phase 6A (70 Blöcke) | 68 Blöcke | SHA-256 |
| --- | --- | --- | --- | --- |
| `(3, 9, 7)` | `472` | `490` | `476` (nicht kleiner) | — |
| `(4, 9, 7)` | `3556` | `3430` | **`3332`** | `a221268a…ede972` |
| `(5, 9, 7)` | `25039` | `24010` | **`23324`** | `f84786fd…2c9cf` |
| `(6, 9, 7)` | `175273` | `168070` | **`163268`** | `3b6030f0…5f1c12e` |

Prüfung: alle vier Arrays (`t = 3..6`) `PASS` mit `verifiers/ca_verify.c`, `ca-tools`-`ca_verify` und eigenem
Zählprogramm; `verify_independent.py` für `t = 3, 4` (`t = 5, 6` dort nicht gelaufen). Negativkontrolle
(`t = 4`, eine Zeile weniger): `FAIL`.

```
python3 scripts/phase7_lift.py --q 7 --reps data/phase7/R_q7_m68.txt --check-m --t 4 --out CA_3332_4_9_7.txt
sha256sum CA_3332_4_9_7.txt   # a221268ab90ce2c3d8901842966e44fb03ee4f1bdc919cfa7e31845ea6ede972
```

**Folge für Paket 1 (PR `#24`):** Die drei `q = 7`-Arrays im Staging (`3430`, `24010`, `168070`) sind weiter
kleiner als die Tabelle, aber nicht mehr das Beste aus dieser Bauart. Für `q = 8, 9, 11, 13, 19` ist dieselbe
Frage offen (`q = 8, 9` brauchen Körperarithmetik; ab `q = 11` sind es `>= 14641` Variablen).

## 9. Nachtrag `q = 8, 9, 11` (2026-11-26, 11:03–11:32 MEZ)

Skripte auf Primzahlpotenzen erweitert (Körper `GeneralGF` aus `scripts/gen_general_tqv.py`). Gegenproben:
SHA-256 für `q = 5` (`0fb696c8…`) und `q = 7` (`a221268a…`) unverändert; `--known` liefert für `q = 7, 8, 9`,
`t = 4` dieselbe Zeilenmenge wie `gen_general_tqv.py`.

Gates: Positivkontrolle je `q`, 5 Minuten je Lauf, `q = 8, 9` je zwei Läufe, `q = 11` ein Lauf.

| `q` | Phase 6A | Lauf 1 (`hint`, 300 s) | Lauf 2 (`hintfile`, 300 s) | Belegart |
| --- | --- | --- | --- | --- |
| `8` | `92` | **`91`** | `91` (andere Liste, gleiche Größe) | bestes gefundenes `m`, Optimalität offen |
| `9` | `117` | **`116`** | `116` | bestes gefundenes `m`, Optimalität offen |
| `11` | `176` | `176` | nicht gelaufen | **Suche erfolglos im Zeitlimit (300 s); nichts ausgeschlossen** |

| Zelle | `ca-tools @ e673ab4` | Phase 6A | neu | SHA-256 |
| --- | --- | --- | --- | --- |
| `(4, 10, 8)` | `6101` | `5888` | **`5824`** | `58de207c…0316bbe` |
| `(5, 10, 8)` | `49128` | `47104` | **`46592`** | `927c206a…dafb370` |
| `(6, 10, 8)` | `393018` | `376832` | **`372736`** | `7e051655…f99a6e6` |
| `(3, 11, 9)` | `1089` | `1053` | **`1044`** | `91b86580…a46f0fa` |
| `(4, 11, 9)` | `9801` | `9477` | **`9396`** | `3c84f9ab…ff28096` |
| `(5, 11, 9)` | `88209` | `85293` | **`84564`** | `adc1b180…3c137bd` |
| `(6, 11, 9)` | `793881` | `767637` | **`761076`** | `aaee4a1d…03b8f74` |

`(3, 10, 8)`: `728` ist nicht kleiner als die Tabelle (`512`).

Prüfung: alle acht Arrays (`q = 8`, `t = 3..6`; `q = 9`, `t = 3..6`) `PASS` mit `ca-tools`-`ca_verify`;
`q = 8` zusätzlich alle vier mit `verifiers/ca_verify.c`; `q = 9` mit `verifiers/ca_verify.c` für `t = 3, 4`;
eigenes Zählprogramm für `q = 8` (`t = 3, 4, 5`) und `q = 9` (`t = 3, 4`); `verify_independent.py` nur
`(4, 10, 8)`. Negativkontrollen (`t = 4`, eine Zeile weniger) für `q = 8` und `q = 9`: `FAIL`.

```
python3 scripts/phase7_lift.py --q 8 --reps data/phase7/R_q8_m91.txt --check-m --t 4 --out CA_5824_4_10_8.txt
python3 scripts/phase7_lift.py --q 9 --reps data/phase7/R_q9_m116.txt --check-m --t 4 --out CA_9396_4_11_9.txt
```

**Überblick gesparte Blöcke:** `q = 5`: 1, `q = 7`: 2, `q = 8`: 1, `q = 9`: 1, `q = 11`: 0 (ein Lauf). Alle Werte
stammen aus zeitbegrenzten Läufen; ob die Ersparnis mit `q` wächst oder der Löser bei größerem `q` nur weniger
findet, ist **offen**.

**Beobachtung zur Struktur (`q = 5, 7`; nicht bewiesen, nur an den zwei Listen abgelesen):** Die Geraden
`d = const` zerfallen in `(q-1)/2` Geraden mit konstantem `a`, `(q-1)/2` Geraden mit konstantem `b` und eine
schwere Gerade mit `(q+1)/2` Schichten. Ohne weitere Kniffe ergibt das wieder `q^2 + C(q,2)`. Die Ersparnis
entsteht, weil an einigen Punkten der schweren Geraden eine Schicht fehlt und die betroffenen Symbole auf den
anderen Geraden mitgedeckt werden.

## 10. Nachtrag: längere Läufe `q = 11, 13` (2026-11-26, 12:00–13:01 MEZ, neuer Prüfer-Chat)

Auftrag (b) aus der Übergabe. Vorab festgelegt: Positivkontrolle `fixknown`, je `q` **ein** Lauf `hint` mit
Limit `1800 s`, Abbruch am Zeitlimit. Skript unverändert (`scripts/phase7_solve_cpsat.py`, OR-Tools `9.15.6755`,
2 Worker, `seed = 1`), Maschine mit 2 Kernen.

| `q` | Positivkontrolle | Lauf (`hint`, `1800 s`) | Belegart |
| --- | --- | --- | --- |
| `11` | `176` erfüllt das Modell (`0,1 s`) | **`m = 175`** (`data/phase7/R_q11_m175.txt`) | bestes gefundenes `m`, Optimalität offen |
| `13` | `247` erfüllt das Modell (`0,2 s`) | `247` (keine Verbesserung) | **Suche erfolglos im Zeitlimit (`1800 s`); nichts ausgeschlossen** |

Der `q = 13`-Lauf teilte sich in den ersten etwa 15 Minuten die zwei Kerne mit Prüfläufen niedriger Priorität
(`nice 19`); das Budget ist deshalb etwas kleiner als nominell.

| Zelle | `ca-tools @ e673ab4` | Phase 6A (176 Blöcke) | 175 Blöcke | SHA-256 |
| --- | --- | --- | --- | --- |
| `(3, 13, 11)` | `1991` | `1936` | **`1925`** | `94bfc0a39c0fd523ef5474125487cdb7577148bce1097bf064b2a1b405cff764` |
| `(4, 13, 11)` | `21901` | `21296` | **`21175`** | `ca50246466727ad7c7980fc344c3a237da6b4f3ac465d6e736af61c09ac526a1` |
| `(5, 13, 11)` | `240911` | `234256` | **`232925`** | `5377d6557520b44d651499f47cb31dff443aecacb6b2906cf0be4076d3b94cea` |
| `(6, 13, 11)` | `2650021` | `2576816` | **`2562175`** | `aef0efb9869c21c2c883dd63222a93719cad5a3c6a179178e294d5696b6aefc1` |

Prüfung (alle vier Arrays): neuer eigener Zähler `PASS`; `verifiers/ca_verify.c` `PASS`; `t = 3, 4, 5` zusätzlich
`verify_independent.py` `PASS` und byte-gleich in einem eigenen Nachbau (eigene Körperarithmetik, Horner-Schema);
`t = 6` nur mit dem Repo-Skript erzeugt. Negativkontrollen: Liste ohne letzten Vertreter → `M(R)` 65 Lücken,
`t = 3` 2431 fehlende Tupel; Arrays `t = 3, 4, 5` ohne letzte Zeile → `FAIL` (221 / 520 / 897).
`CA_2562175_6_13_11.txt` hat `66,4 MiB` (über der `50 MiB`-Grenze von `ca-tools` für Dateien im PR).

```
python3 scripts/phase7_lift.py --q 11 --reps data/phase7/R_q11_m175.txt --check-m --t 4 --out CA_21175_4_13_11.txt
```

**Folge für Paket 1 (PR `#24`):** Auch die `q = 11`-Arrays im Staging (`1936`, `21296`, `234256`) sind nicht mehr
das Beste aus dieser Bauart. Überblick gesparte Blöcke bei `v = q`: `q = 5`: 1, `7`: 2, `8`: 1, `9`: 1, `11`: 1
(`1800 s`; `300 s` fand nichts), `13`: 0 (`1800 s`). Die Laufzeit bestimmt das Ergebnis mit; ein Trend in `q` ist
daraus nicht ablesbar.

## 11. Verkleinerte Alphabete `v < q` (2026-11-26, 13:01–13:48 MEZ)

Auftrag (c) aus der Übergabe.

### 11.1 Modell

Vertreter `(c, d, a, b)` mit `c, d` in `GF(q)` und `a, b` in `{0, ..., v-1}`. `M(R)` wie in §2, jetzt gemischt:
`q` Symbole in den Spalten `c + al*d`, `v` Symbole in `a` und `b`. `L_t^pi(R)`: Lift wie in §2, danach `pi` auf den
Auswertungsspalten (`pi(z) = z` für `z < v`, sonst `0`); `a`, `b` unverändert.

**Aussage A' (hinreichend).** `L_t^pi(R)` ist ein `CA(|R| * q^(t-2); t, q+2, v)` für `2 <= t <= q + 2`, wenn gilt:
1. jeder Punkt `(c, d)` kommt in `R` vor (`q^2` Bedingungen);
2. auf jeder Geraden `c + al*d = u` kommt jedes der `v` Symbole in `a` vor, ebenso in `b` (je `q * q * v`);
3. jedes Paar `(a, b)` kommt vor (`v^2`).

In Bedingung 2 läuft `u` über **alle** `q` Körperelemente, auch wenn die Zielwerte nur in `{0..v-1}` liegen: der
Koeffizient `u` des Interpolanten liegt im Körper und ist nicht auf `{0..v-1}` beschränkt. (Verlangt wird das für alle `u`; ob jedes `u`
bei gegebenem `t` und `v` wirklich gebraucht wird, gehört zur ungeprüften Notwendigkeit.)

Das ist Stärke 2 von `M(R)` mit gemischten Alphabeten. Argument wie in §3: die Zielwerte liegen in `{0..v-1}`,
dort ist `pi` die Identität; bei `t` Auswertungsspalten braucht man das Polynom selbst (1.), bei `t - 1` plus `a`
oder `b` eine ganze Gerade von `(c, d)` (2.), bei `t - 2` plus `a` und `b` nur das Paar (3.). Für `v = q` ist es
das Modell aus §5. Untere Schranke im Modell: `|R| >= q^2` wegen 1.

Belegart: **Argument**; **nachgezählt** für alle Listen in der Tabelle unten (`t` wie angegeben). Ob die
Bedingungen auch notwendig sind, ist nicht geprüft.

Skripte: `scripts/phase7_solve_cpsat_vq.py` (neu), `scripts/phase7_lift.py --v V` (erweitert; die Hashes für
`v = q` sind unverändert, geprüft an `0fb696c8…` und `3c84f9ab…`).

### 11.2 Läufe

Vorab festgelegt: Positivkontrolle = Phase-6A-Liste mit `q^2 + C(v,2)` Vertretern; je `(q, v)` ein Lauf `hint`;
Limits `120 / 180 / 300 / 300 / 300 / 600 s`, zusammen `30` Minuten; Abbruch am Zeitlimit.

| `q` | `v` | Phase 6A `q^2 + C(v,2)` | Positivkontrolle | Limit | gefunden | Ersparnis | nachgezählt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `5` | `3` | `28` | erfüllt | `120 s` | **`25`** (`= q^2`, im Modell bestmöglich) | `3` | `t = 3, 4, 5` |
| `5` | `4` | `31` | erfüllt | `180 s` | **`27`** | `4` | `t = 3, 4, 5` |
| `7` | `6` | `64` | erfüllt | `300 s` | **`58`** | `6` | `t = 3, 4, 5` |
| `8` | `7` | `85` | erfüllt | `300 s` | **`79`** | `6` | `t = 3, 4` |
| `9` | `8` | `109` | erfüllt | `300 s` | **`104`** | `5` | `t = 3, 4` |
| `11` | `10` | `166` | erfüllt | `600 s` | **`158`** | `8` | `t = 3, 4, 5, 6` |

Belegart überall: bestes gefundenes `m`, Optimalität offen (Ausnahme `(5, 3)`: `25 = q^2` ist die untere Schranke
des Modells). Der Löser lieferte keine brauchbare eigene Schranke. Nachgezählt heißt: eigener Zähler und
`verifiers/ca_verify.c` `PASS`; Negativkontrolle (Liste ohne letzten Vertreter, `t = 3`) je `FAIL`.
Listen: `data/phase7/R_q<q>_v<v>_m<m>.txt`.

Die Arrays zu `q <= 9` sind nicht kleiner als die Tabelle (es fehlen je nach Zelle `5` bis `29` weitere Blöcke).

### 11.3 `q = 11`, `v = 10`: vier Zellen

| Zelle | `ca-tools @ e673ab4` | Phase 6A (166 Blöcke) | 158 Blöcke | SHA-256 |
| --- | --- | --- | --- | --- |
| `(3, 13, 10)` | `1760` | `1826` (nicht kleiner) | **`1738`** | `33c9a4987fa7d080452d81cd129423bbd66355a7325fc14f743a0c79352567c7` |
| `(4, 13, 10)` | `20383` | `20086` | **`19118`** | `1a961a744d45a19c9c1a1ee0c0401a9baaf05ab96c395c4643eb8e5816cd6cc0` |
| `(5, 13, 10)` | `224844` | `220946` | **`210298`** | `89a8ec851c49d3a3804eb37ed3e1dea8d8300102c3f17e8d2f421fc5d9c4d793` |
| `(6, 13, 10)` | `2483623` | `2430406` | **`2313278`** | `c21c9f71e1c28597d083a08bc37ca21ac0f44cf663b439414cb6173129a9d59b` |

`(3, 13, 10)` ist eine Zelle, die Phase 6A nicht erreicht hatte. Prüfung (alle vier): eigener Zähler `PASS`,
`verifiers/ca_verify.c` `PASS`, byte-gleich im eigenen Nachbau; `t = 3, 4, 5` zusätzlich `verify_independent.py`
`PASS`. Negativkontrollen: Arrays ohne letzte Zeile → `FAIL` (116 / 203 / 6 / 1 fehlende Tupel); Liste ohne
letzten Vertreter → `M(R)` 65 Lücken. `CA_2313278_6_13_10.txt` hat `57,4 MiB` (über `50 MiB`).

```
python3 scripts/phase7_lift.py --q 11 --v 10 --reps data/phase7/R_q11_v10_m158.txt --check-m --t 3 --out CA_1738_3_13_10.txt
sha256sum CA_1738_3_13_10.txt   # 33c9a4987fa7d080452d81cd129423bbd66355a7325fc14f743a0c79352567c7
```

### 11.4 Einordnung

- Für `v < q` ist die Konstante `C(v,2)` aus Phase 6A deutlich weiter vom Besten entfernt als für `v = q`
  (Ersparnis `3` bis `8` Blöcke gegen `0` bis `2`).
- Einfacher Grund, als **Argument** (ein Fall nachgezählt: `q = 7, v = 4`, `m = 49`, `t = 3, 4`): Auf den Geraden
  `d = s`, `s < v`, setze `(a, b) = (s, s)`; dann sind 1. und 2. erfüllt, und die `q - v` übrigen Geraden `d >= v`
  sind frei beschriftbar. Sie können die `v(v-1)` gemischten Paare tragen. Also `|R| = q^2`, sobald
  `q(q - v) >= v(v - 1)`. Für `v` nahe `q` reicht das nicht; die Löserlisten nutzen dort mehr als diesen Kniff.
  Keine Bauregel für `v = q - 1` abgeleitet.
- Weitere `(q, v)` mit Phase-6A-Treffern laut `docs/GENERAL_TQV_SCAN.md`: `(13, 12)`, `(16, 14)`, `(16, 15)`,
  `(17, 14..16)`, `(19, 18)`, `(23, 20..22)`, `(25, 20)`, `(25, 21)`, `(25, 24)`. **Nicht gerechnet.** Modellgröße
  `q^2 v^2`: `24336` Variablen bei `(13, 12)`, ab `q = 16` über `50000`.
- Literatur zu `v < q` in dieser Bauart: **nicht geprüft**.

## 12. Korrektur zur Zahl der Prüfprogramme

`verifiers/ca_verify.c` und `ca_verify.c` aus `ca-tools @ e673ab4` sind dieselbe Datei
(SHA-256 `689441c99288ef94ec6b2209cd61d88e00f567dd7290f8b260a562d056ab54d1`). Wo oben beide getrennt genannt
sind (§3 „vier Programme“, §5, §8, §9), zählen sie als **ein** Programm. Unabhängig sind: dieses C-Programm,
`verify_independent.py`, der jeweilige eigene Zähler.

Nachprüfung der elf Arrays aus §5, §8, §9 im neuen Chat (neuer Zähler, neuer Nachbau): alle elf SHA-256 byte-gleich
aus Repo-Skript und Nachbau; alle elf `PASS` (Zähler, `ca_verify.c`); Negativkontrollen (letzte bzw. mittlere
Zeile entfernt) alle `FAIL`; alle elf kleiner als `ca-tools @ e673ab4`. Das ist weiter eine Prüfung durch den
Prüfer selbst, **keine Fremdprüfung**.

## 13. Zweite Läufe nach Abbruchregel (2026-11-26, 14:11–15:45 MEZ)

Regel (vorab mit Justus festgelegt): Eine Liste gilt als einreichungsreif, wenn ein weiterer Lauf gleicher Länge
von ihr aus nichts findet. Je Lauf Limit `1800 s`, Start von der besten Liste (`hintfile`), Skripte und
Einstellungen wie in §10 und §11, Maschine mit 2 Kernen, Läufe nacheinander.

| Liste | Start | Lauf (`1800 s`) | Regel erfüllt? |
| --- | --- | --- | --- |
| `q = 11`, `v = 10` | `158` (§11.3) | **`157`** (`data/phase7/R_q11_v10_m157.txt`) | nein (Verbesserung gefunden) |
| `q = 13`, `v = 12` | `224` (Bauart §14) | `224` | ja (ein Lauf) |
| `q = 11`, `v = 11` | `175` (§10) | `175` | ja (ein Lauf) |

Abweichung: Der Lauf zu `(13, 12)` war zuerst von der Phase-6A-Liste (`235`) gestartet und wurde nach 2 Minuten
abgebrochen, als die Bauart aus §14 mit `224` vorlag; gewertet ist nur der Lauf ab `224`.
Einschränkung: Bei dieser Modellgröße (`24336` Variablen) fand derselbe Löser auch für `q = 13`, `v = 13` in
`1800 s` nichts (§10). „Regel erfüllt“ heißt: dieser Löser fand in dieser Zeit nichts. Ausgeschlossen ist nichts.

Die `157` des Lösers ist dieselbe Blockzahl wie die der Bauart aus §14 für `(11, 10)`. Die Arrays in §14.4
stammen aus der Bauart; die Löserliste bleibt als Beleg des Laufs im Repo. Die Arrays aus §11.3 (`158` Blöcke)
sind damit überholt.

## 14. Geschlossene Bauart für `v <= q` ohne Löser (2026-11-26, ab 14:44 MEZ)

### 14.1 Aussage

Für jede Primzahlpotenz `q`, jedes `2 <= v <= q` und `2 <= t <= q + 2` gibt es ein
`CA((q^2 + C(w, 2)) * q^(t-2); t, q+2, v)` mit `w = max(0, 2v - q)`.
Für `v = q` ist das die Zahl aus Phase 6A (`w = q`). Für `v < q` ist `C(max(0, 2v - q), 2) < C(v, 2)`.
Zeilen werden mit Vielfachheit gezählt: für `t > q` können verschiedene Vertreter und Koeffizienten dieselbe Zeile
liefern (Beispiel `q = v = 2`, `t = 4`); die angegebene Zeilenzahl ist dann eine obere Schranke für die Zahl
verschiedener Zeilen. Vergleiche wie `c < d` betreffen nur die Nummern `0..q-1`, nicht die Körperstruktur.

### 14.2 Liste

`f = q - v`, `w = max(0, q - 2f)`, `n = v - w`. Geraden `d = const` in der Ebene der Punkte `(c, d)`:

- `d < w` („doppelt belegt“): Grundbeschriftung `(a, b) = (d, d)`. An den Punkten `c < d` stehen statt eines
  Vertreters zwei: `(a, b) = (d, c)` und `(c, d)`. Das sind `C(w, 2)` zusätzliche Vertreter.
- `w <= d < w + n` („nur `a`“): `a = w + (d - w)` auf der ganzen Geraden, `b = c` für `c < v`, sonst `0`.
- `w + n <= d < w + 2n` („nur `b`“): `b = w + (d - w - n)` auf der ganzen Geraden, `a = c` für `c < v`, sonst `0`.
- `d >= w + 2n` (nur für `v < q/2`): `(0, 0)`.

Die Geraden passen: für `2v >= q` ist `w = 2v - q`, `n = q - v`, also `w + 2n = q`; für `2v < q` ist `w = 0`,
`n = v`, also `w + 2n = 2v < q`. Alle Beschriftungen liegen in `{0..v-1}`. Zwei Vertreter am selben Punkt
entstehen nur für `c < d < w`; sie sind verschieden, weil `c != d`.

Erzeugen: `python3 scripts/phase7_reps_vq.py Q V AUSGABE` (reines Python, keine Suche; bricht ab, wenn `Q` keine
Primzahlpotenz ist).
Für `v = q` ist die Liste als **Menge** gleich der Phase-6A-Liste (geprüft für `q = 7`), aber anders sortiert.
Die daraus gebauten Arrays haben deshalb dieselben Zeilen in anderer Reihenfolge und **einen anderen SHA-256**
als die Dateien aus `scripts/gen_general_tqv.py`. Für `v = q` bleiben `gen_general_tqv.py` bzw. die Löserlisten
maßgeblich; `phase7_reps_vq.py` ist für `v < q` gedacht.

### 14.3 Argument (Bedingungen 1–3 aus §11.1)

1. Jeder Punkt trägt mindestens einen Vertreter.
2. Jedes Symbol `s` von `a` hat eine ganze Gerade `d = const`, auf der jeder Punkt einen Vertreter mit `a = s`
   trägt: für `s < w` die Gerade `d = s` (am Punkt `c < s` der Vertreter `(s, c)`), für `s >= w` eine
   „nur `a`“-Gerade. Jede Gerade `c + al*d = u` trifft jede Gerade `d = const` in genau einem Punkt. Ebenso für
   `b` (für `m < w` am Punkt `c < m` der Vertreter `(c, m)`).
3. Paare `(s, m)`: `s >= w` → auf der „nur `a`“-Geraden von `s` laufen alle `b` durch; `m >= w` → entsprechend;
   `s = m < w` → Punkt `c >= s` der Geraden `d = s`; `s > m`, beide `< w` → Vertreter `(s, m)` am Punkt
   `(m, s)`; `s < m`, beide `< w` → Vertreter `(s, m)` am Punkt `(s, m)`.

Die Zusatzvertreter entstehen nur zwischen den `w` doppelt belegten Geraden. Jede Gerade, die nur ein Symbol
tragen muss, liefert alle Paare mit diesem Symbol ohne Zusatz.

### 14.4 Belegart

- Aussage 14.1 allgemein: **Argument** (14.3 zusammen mit Aussage A' aus §11.1, die selbst Argument ist).
  Gegengelesen von Gemini am 26.11.2026 (§2, §3, §11.1, §14 und die drei Skripte; Urteil: Kette vollständig, Text
  und Code stimmen überein, fünf Präzisierungen, alle eingepflegt). Gemini hat das Projekt mitgeplant; das ist
  **kein unbeteiligtes Modell** im Sinn von `RULES.md` 2d.
  Geprüft von einem unbeteiligten Modell (GPT-6.2 Sol über OpenRouter, 26.11.2026, 20:13 MEZ; gelesen: dieses
  Dokument und die drei Skripte): Glieder §2/§3 Aussage A, Aussage B, §11.1 Aussage A' ohne Befund; §14.2 und
  §14.3 ohne Befund; zwei Nebenfehler, beide behoben (Ungleichung in §14.1 ohne `max`; `phase7_lift.py` brach
  bei leerer Liste mit `IndexError` ab). Vermerk: [`docs/THIRD_MODEL_REVIEW_PHASE7.md`](THIRD_MODEL_REVIEW_PHASE7.md).
  Ein zweiter Durchgang desselben Modells am korrigierten Stand (Wortlaut:
  [`docs/openrouter/PHASE7_ARGUMENT_REVIEW_gpt-6.2-sol.md`](openrouter/PHASE7_ARGUMENT_REVIEW_gpt-6.2-sol.md)) urteilt für
  alle Glieder „korrekt“ und hält die Beschreibung als Verfeinerung von CKRS (2010) Lemma 3.3 für sachgerecht.
  Belegart bleibt **Argument**, jetzt von zwei Modellen gelesen; kein formaler Beweis.
- Randfälle **nachgezählt** (eigener Zähler): alle `q = 2..5`, alle `v`, alle `t = 2..q+2` (`50` Arrays) sowie
  `(q, v, t) = (7,6,8), (7,6,9), (7,5,8)`.
- Bedingungen 1–3 **nachgezählt** (`phase7_lift.py --check-m`): alle `99` Paare `(q, v)` mit
  `q in {4, 5, 7, 8, 9, 11, 13, 16, 17, 19}`, `2 <= v <= q`.
- Arrays **nachgezählt**: die 20 Zellen der Tabelle unten und `(6, 13, 10)`, außerdem `(t, 7, 4)` für
  `t = 3, 4, 5`. Jeweils eigener Zähler `PASS`; die 20 auch `verifiers/ca_verify.c` `PASS` und
  Negativkontrolle (letzte Zeile entfernt) `FAIL`; 10 davon (Primzahl-`q`, `N <= 250000`) byte-gleich im eigenen
  Nachbau; 7 davon (`t = 3` alle fünf, `(4, 13, 10)`, `(4, 15, 12)`) `verify_independent.py` `PASS`.
- Alle übrigen Zellen in `docs/PHASE7_VQ_SCAN.md`: **Vorhersage aus der Formel**, kein Array erzeugt.
- Nicht fremdgeprüft. Nichts in `results/`.

| Zelle `(t, k, v)` | `q` | Blöcke | `N` | `ca-tools @ e673ab4` | Differenz | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| `(3, 13, 10)` | `11` | `157` | `1727` | `1760` | `-33` | `98e5906a59dc0e0f4aef4a32c2841ce71e0b0c56b2f8aac6728f6a08851f36ec` |
| `(4, 13, 10)` | `11` | `157` | `18997` | `20383` | `-1386` | `2bd4886415f8f1c4871ebb7aeaa3ed4e9fcba272cfc8407bd0fa789cbe4bc3a8` |
| `(5, 13, 10)` | `11` | `157` | `208967` | `224844` | `-15877` | `591fedf245e1a8fd2c982010ce2af7595df04b180b05258a951dd2b09912881c` |
| `(3, 15, 12)` | `13` | `224` | `2912` | `2955` | `-43` | `9f41ef45a18fe5b773cd309a5b253632dd09d1b548a50d37a3408e1fcb67fb84` |
| `(4, 15, 12)` | `13` | `224` | `37856` | `40476` | `-2620` | `b5d916c34d0bd89988578fca51179ad6e9b6439e1db67b1611eae2ce3138abf0` |
| `(5, 15, 12)` | `13` | `224` | `492128` | `527205` | `-35077` | `240b6c938f6b87088ccebaa50515ebc7e8b8468f07cb03db08259cc731c05028` |
| `(4, 18, 14)` | `16` | `322` | `82432` | `82993` | `-561` | `dcf37e8dabdadfefb8237cddd7b1e2f80df715b54e054f2e94fa5d721ad8ba53` |
| `(4, 19, 14)` | `17` | `344` | `99416` | `106023` | `-6607` | `881f8187a6f2c4dbd2022cff25a1742a1a39b62bd6672ad89ef4965ef63acbfb` |
| `(4, 19, 15)` | `17` | `367` | `106063` | `110273` | `-4210` | `6db6dbf97f4b0b644ed2e5907432c2f852e5c96bcb68aaa7b891ae8f604ac776` |
| `(4, 19, 16)` | `17` | `394` | `113866` | `114489` | `-623` | `53b0db39d2a010f7642c3e873a65e5d9ad6d1c10aec8a2dcaebbdfa8e97d688c` |
| `(3, 21, 17)` | `19` | `466` | `8854` | `9376` | `-522` | `8df731279c7495d533b1a729ef7eded790824de82d224a8c874ffc623208bb28` |
| `(3, 21, 18)` | `19` | `497` | `9443` | `9830` | `-387` | `e3cd323a0881232338651f910687a81fda8c5401a2dc03863f7c1dff428416ec` |
| `(4, 21, 18)` | `19` | `497` | `179417` | `188412` | `-8995` | `36d945d874fb6c3b87be4c3f24931256dd9d2d0f026ac0684414ab85e55833b3` |
| `(4, 25, 20)` | `23` | `665` | `351785` | `382933` | `-31148` | `43a09235850184dbf7e568339fa9edba0db7d060721a2654f380524b39217f3c` |
| `(4, 25, 21)` | `23` | `700` | `370300` | `390612` | `-20312` | `edd06b3b669e7fb1994f69d6d225f16556aaed0b37cdbd188157c50063154d83` |
| `(4, 27, 20)` | `25` | `730` | `456250` | `507412` | `-51162` | `d70e6fdae82ca64c92d0d19a26af8c8e48bee392af1a64131ad70007215971ff` |
| `(3, 27, 21)` | `25` | `761` | `19025` | `19052` | `-27` | `77f289f1638481979bb10b3b4e96f73c745ab73be00fb7364a3c4e59380d2d78` |
| `(4, 27, 21)` | `25` | `761` | `475625` | `523044` | `-47419` | `e26bf9386702049101ba9afb4889d68e1a09df15e4174c2ec92b8210bf2e0adb` |
| `(4, 27, 22)` | `25` | `796` | `497500` | `531431` | `-33931` | `46d3d41574a66f858d52f6d83f34a0bbcba97a364fa24bd09fdabb35ee7dd826` |
| `(4, 27, 23)` | `25` | `835` | `521875` | `531433` | `-9558` | `26ca374a133c4974a990e6e0abcb01f0004606560e26e1942f8512647e691def` |

`(6, 13, 10)`: `N = 2298637`, SHA-256 `a126c2daad42ae90517d74cc960bda09c7df91396b5d1d3a92f648713675bb8f`,
eigener Zähler `PASS` (nur dieser), Tabelle `2483623`.

```
python3 scripts/phase7_reps_vq.py 11 10 R_q11_v10.txt
python3 scripts/phase7_lift.py --q 11 --v 10 --reps R_q11_v10.txt --check-m --t 3 --out CA_1727_3_13_10.txt
sha256sum CA_1727_3_13_10.txt   # 98e5906a59dc0e0f4aef4a32c2841ce71e0b0c56b2f8aac6728f6a08851f36ec
```

### 14.5 Verhältnis zu den Löserläufen

| `(q, v)` | Phase 6A | Bauart | Löser (bestes gefundenes `m`) |
| --- | --- | --- | --- |
| `(5, 3)` | `28` | `25` | `25` |
| `(5, 4)` | `31` | `28` | `27` |
| `(7, 6)` | `64` | `59` | `58` |
| `(8, 7)` | `85` | `79` | `79` |
| `(9, 8)` | `109` | `102` | `104` |
| `(11, 10)` | `166` | `157` | `157` |
| `(13, 12)` | `235` | `224` | `224` (Start bei `224`, `1800 s`, nichts gefunden) |

Die Bauart ist nicht bestmöglich: bei `(5, 4)` und `(7, 6)` fand der Löser je einen Block weniger. Ob das für
größere `q` auch gilt, ist **offen**.

### 14.6 Tabellenvergleich und Folgen

- Scan: [`docs/PHASE7_VQ_SCAN.md`](PHASE7_VQ_SCAN.md). `76` Zellen kleiner als `ca-tools @ e673ab4` (Phase 6A: `56`),
  davon `48` mit `v < q`. `20` Zellen hatte Phase 6A nicht erreicht.
- Jede `v < q`-Zelle aus Phase 6A wird durch die Bauart unterboten. Betroffen in `results/general_tqv/` und im
  Staging von PR `#24`: `CA_9766_3_21_18`, `CA_20086_4_13_10`, `CA_39715_4_15_12`, `CA_220946_5_13_10`.
- Literatur: [`docs/LITERATURE_CHECK_PHASE7_VQ.md`](LITERATURE_CHECK_PHASE7_VQ.md). Formel in den gelesenen Quellen nicht
  gefunden, Prüfung nicht vollständig. Direkte Vorarbeit ist CKRS (2010), Lemma 3.3: in der Schreibweise von §2 die
  Liste `{(c, d, d, d) : (c, d) != (0, 0)} ∪ {(0, 0, x, y) : x != y}` mit `q^2 + q(q-1) - 1` Vertretern
  (nachgezählt für `q = 3..11`).
