# Phase 7: Rückführung auf Stärke 2, die Fälle `q = 5` und `q = 7` (`docs/PHASE7_T2_REDUCTION.md`)

Stand: 2026-11-26, ca. 10:55 MEZ (§8 zu `q = 7` nachgetragen). Autor: Claude (Prüfer-Chat), auf Wunsch von Justus als eigene Rechnung
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

- `q` Primzahl, `2 <= t <= q + 2`. Vertreter `(c, d, a, b)` aus `GF(q)^4`.
- `M(R)`: je Vertreter eine Zeile mit den Spalten `c + al*d` für `al = 0, ..., q-1`, dann `a`, dann `b`.
- `L_t(R)`: je Vertreter und je `(a_0, ..., a_{t-3})` die Zeile `(P(0), ..., P(q-1), a, b)` mit
  `P(x) = a_0 + ... + a_{t-3} x^(t-3) + c x^(t-2) + d x^(t-1)`. Das sind `|R| * q^(t-2)` Zeilen.
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

**Aussage B (notwendig).** Für Primzahl `q` und `2 <= t <= q` gilt auch die Umkehrung, weil dann jedes
`sigma` als Summe einer `(t-1)`-Menge auftritt.

| Aussage | Belegart |
| --- | --- |
| A für `q = 5`, `t = 3, 4, 5`, beide Listen (35 und 34) | **nachgezählt** (vier Programme, siehe §5) |
| A für `q = 7`, `t = 3, 4`, Phase-6A-Liste und zyklische Liste | **nachgezählt** (eigenes Programm); Phase-6A-Liste bei `t = 5, 6` über die Arrays aus PR `#22` |
| A allgemein | **Argument**, nicht formal geprüft |
| B | **Argument**; gestützt durch Gegenproben (eine Zeile weniger: `M` und Lifts fallen gemeinsam durch) |
| Primzahlpotenzen `q = 8, 9` | **nicht gerechnet** (Skript kann nur Primzahlen) |

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
2. `q = 7`: Ist `67` möglich? (`67` würde `(3,9,7) = 472` schlagen.) `q = 8, 9, 11, 13`: nicht gerechnet.
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
