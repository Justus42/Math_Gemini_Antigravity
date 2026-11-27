# Notiz 2: Von den Rédei-Klassen zu einer Formel (Schritt 1)

- Stand: 2026-11-27, 00:05 MEZ (Zeit der Datei; im Chat stand irrtümlich „ca. 01:00“). Autor: Claude (eigener Chat). Fortsetzung von [`NOTIZ_1_KLASSEN_OHNE_GERADE.md`](NOTIZ_1_KLASSEN_OHNE_GERADE.md).
- Im Repo abgelegt am 27.11.2026, sonst unverändert. Einstieg und Berichtigungen: [`docs/PHASE8_UEBERSICHT.md`](../PHASE8_UEBERSICHT.md); dort steht auch, dass die geschlossene Formel im Tabellenbereich **nicht** die kleinsten Listen liefert.
- Vergleichsstand: `Math_Gemini_Antigravity @ e3100f6`, `chrispbsmolen/ca-tools @ 808945f` (seit `e673ab4` zwei
  geänderte Zellen, `(3, 28, 3)` und `(3, 8, 5)`; keine mit `k = q + 2`).
- **Rollenhinweis:** Rechnung und Argumente eines Prüfers, nicht fremdgeprüft, nichts im Repo. Kein
  Neuheitsanspruch. Nur Primzahlen `q`.

## 1. Ergebnis

Die Ersparnis wächst wie `q^2`, nicht wie `q`. Für Primzahl `q` und `v = q`:

| Aussage | Wert | Belegart |
| --- | --- | --- |
| Formel ohne Suche | `\|R\| = q^2 + C(q,2) - q(1+j) + (q-5)/2 - j`, für `q ≡ 3 (mod 4)` und `0 <= j <= (q-15)/12` | Argument (Abschnitt 3); als Zählung für alle Primzahlen `13 <= q < 520` nachgerechnet; als Liste gebaut und `M(R)` geprüft für `q = 19, 31, 43` |
| dasselbe für `q ≡ 1 (mod 4)` | zusätzlich `+ (2 + 2j)`, `j <= (q-13)/12` | wie oben (Zählung) |
| Leitkonstante daraus | `17/12 ≈ 1,417` statt `3/2` | folgt aus der Formel mit `j = floor((q-15)/12)` |
| mit Auswahl der Klassen per Löser | `\|R\| / q^2`: 1,410 (`q = 23`), 1,407 (`q = 61`), 1,404 (`q = 101`), 1,403 (`q = 251`) | Zählung; Listen gebaut und geprüft für `q = 23, 29, 31, 37` |
| Vermutung | Grenzwert `7/5` | Zahlen oben und Überschlag in Abschnitt 4; kein Beweis |

`N = |R| * q^(t-2)` nach Aussage A aus `docs/PHASE7_T2_REDUCTION.md`.

## 2. Die Bauart in drei Sätzen

1. Skelett wie in Notiz 1: schwere Gerade `d = 0`, `(q+1)/2 + j` reine `b`-Geraden, `(q-3)/2 - j` reine
   `a`-Geraden. Start: `q^2 + C(q,2) + q(1+j)` Vertreter.
2. Jede Klasse ohne volle Gerade ist ein **Geradenpaar durch einen festen Punkt `O`** auf einer reinen
   `b`-Geraden, mit Steigungen `+σ` und `-σ`, eingeschränkt auf `(q+1)/2` der reinen `b`-Geraden (die Menge `Δ`
   aus Notiz 1). Alle Klassen benutzen denselben Punkt `O`; Geraden durch `O` treffen sich sonst nirgends, also
   kostet das Zusammentreffen nur `n - 1` Vertreter bei `O`.
3. Treffen die beiden Geraden die schwere Gerade in `+e` und `-e`, dann darf das Symbol auf der schweren
   Geraden genau an den Punkten `p` wegfallen, für die `p^2 - e^2` **kein Quadrat** ist.

Damit hängt alles nur noch an der Menge `S` der benutzten Quadrate `s = e^2`:

```
adel(p) = #{ s in S : p^2 - s ist kein Quadrat },   n = |S| <= (q-3)/2 - j
\|R\| = q^2 + q*((q+1)/2 + j) - Summe_p min(adel(p), 2+2j) + (n - 1)
```

Satz 3 ist für alle Klassen bei `q = 11 … 43` nachgerechnet (jede Klasse trifft jede Gerade `c + al*d = u`;
stichprobenweise: kein behaltener Punkt ist entbehrlich). Geometrisch ist die Klasse ein „projektives Dreieck“
mit einer Seite auf der schweren Geraden; ausgeschrieben ist der Beweis nicht.

## 3. Warum die Formel ohne Suche gilt (Argument)

Nimmt man **alle** `(q-1)/2` Quadrate, so ist für `p != 0`
`adel(p) = (q-3)/4` (`q ≡ 3 mod 4`) bzw. `(q-1)/4` (`q ≡ 1 mod 4`), unabhängig von `p`. Das ist die bekannte
Summe `Summe_e chi(a - e^2) = -chi(-1)` für `a != 0`. Erlaubt sind aber nur `(q-3)/2 - j` Klassen (Platz auf
den reinen `b`-Geraden). Lässt man `j + 1` Quadrate weg, sinkt `adel(p)` um höchstens `j + 1`. Solange
`(q-3)/4 - (j+1) >= 2 + 2j`, zählt an jedem Punkt die volle Zahl `2 + 2j`, und die Formel folgt durch
Einsetzen. Für `q ≡ 1 (mod 4)` fällt der Punkt `p = 0` aus (dort ist `adel = 0`), das kostet `2 + 2j`.

Offene Stücke des Arguments: (a) Satz 3 allgemein; (b) dass sich die schwere Gerade immer belegen lässt
(Kantenfärbung eines bipartiten Graphen; in allen gebauten Fällen hat ein Löser die Belegung gefunden);
(c) Aussage A selbst ist im Repo als Argument geführt.

## 4. Warum mehr als `17/12` zu erwarten ist

Das Weglassen kostet im Mittel nur `(j+1)/2` je Punkt, nicht `j + 1`. Rechnet man mit dem Mittel, wird die
Bedingung `q/4 - j/2 >= 2j`, also `j ≈ q/10` statt `q/12`, und die Ersparnis `≈ q^2/10`: Leitkonstante `7/5`.
Die Zahlen passen dazu (`1,4028` bei `q = 499` schon ohne Suche). Ein Beweis bräuchte eine Schranke für
unvollständige Charaktersummen (Weil, Pólya–Vinogradov) für eine konkret gewählte Menge weggelassener Quadrate.
Nicht ausgeführt.

Ob `7/5` die Grenze der Idee ist, ist offen. Sie ist die Grenze **dieses** Skeletts: Die Zahl der Klassen ist
durch den Platz auf den reinen `b`-Geraden auf etwa `q/2 - j` begrenzt.

## 5. Listen und Prüfung

| `q` (`v`) | Phase 6A / §14 | Notiz 1 | jetzt | Datei | SHA-256 (Anfang) |
| --- | --- | --- | --- | --- | --- |
| 19 | 532 | 517 | **513** | `R_q19_m513.txt` | `f6484a3d…` |
| 23 | 782 | — | **746** | `R_q23_m746.txt` | `4e376200…` |
| 23 (`v = 22`) | 739 | — | **722** | `R_q23_v22_m722.txt` | `cdf4c4f4…` |
| 29 | 1247 | — | **1190** | `R_q29_m1190.txt` | `0b80d88c…` |
| 31 | 1426 | — | **1356** | `R_q31_m1356.txt` | `75938b61…` |
| 37 | 2035 | — | **1942** | `R_q37_m1942.txt` | `6551934e…` |

Für `q = 11, 13, 17` bleiben die Listen aus Notiz 1 die kleinsten (170, 238, 412); die symmetrische Bauart
(`±σ`) liefert dort 172, 239, 413.

Prüfung: `M(R)` ohne Lücke mit eigenem Zähler und mit `scripts/phase7_lift.py --check-m` (alle sechs);
Arrays `t = 3` aus `phase7_lift.py` mit `verifiers/ca_verify.c` `PASS` (alle sechs, darunter
`CA(71854; 3, 39, 37)` und `CA(16606; 3, 25, 22)`); `t = 4` für `q = 23` (`CA(394634; 4, 25, 23)`) `PASS`;
`verify_independent.py` und Negativkontrolle nur für `q = 23`, `t = 3`. Die Listen zur Formel ohne Suche
(`q = 19, 31, 43`: 520, 1376, 2640) sind nur mit dem eigenen Zähler geprüft und nicht im Paket.

Für `v < q` (Abschnitt 6) ist nur `(q, v) = (23, 22)` gebaut.

## 6. Was das für die Tabelle heißt

Die Tabelle endet bei `v = 25`. Praktisch wirkt die Formel also nur für `q <= 23` (und für `q = 25, 27`, sobald
die Bauart auf Primzahlpotenzen übertragen ist).

| Zelle | Tabelle `808945f` | Repo | neu |
| --- | --- | --- | --- |
| `(3, 21, 19)` | 10279 | 10108 | 9747 (erzeugt und geprüft) |
| `(4, 21, 19)` | 195301 | 192052 | 185193 (nur Vorhersage) |
| `(5, 25, 23)` | 9765621 | 9514594 | 9076582 (nur Vorhersage) |
| `(6, 25, 23)` | 244140621 | 218835662 | 208761386 (nur Vorhersage) |
| `(4, 25, 22)` | 390619 | 390931 (kein Treffer) | 381938 (nur Vorhersage; neuer Treffer) |
| `(5, 25, 22)` | 9765619 | 8991413 | 8784574 (nur Vorhersage) |

`(3, 25, 23)` und `(4, 25, 23)` bleiben über der Tabelle (17158 gegen 15612; 394634 gegen 390621).

`v < q` bei `q = 23`: besser als §14 nur für `v = 22` (722 statt 739) und `v = 21` (699 statt 700, nicht
gebaut); ab `v = 20` ist §14 kleiner.

## 7. Literatur und Tabellenstand (Subagent, Sonnet; plus eigener Blick)

- Kein Fund, der Covering Arrays mit Rédei-Mengen, Richtungszahlen oder Baer-Unterebenen verbindet. Gelesen:
  Bai (Farbungen; elliptische Kurven), Sitjar (zwei Preprints). Nicht gelesen: CKRS 2010 im Original, Bais
  Begleitpapier (Zenodo 23787053 / 24054350), Zenodo-Volltexte. Die Suche ist nicht erschöpfend.
- Die Geometrie-Sätze aus Notiz 1 sind mit Quellen bestätigt (Bruen; Blokhuis 1994; Lovász–Schrijver; Ball 2003).
  Neu: Csajbók (Okt. 2026) zeigt Lovász–Schrijver auch für `q = p^n`, `p > 2`. Bei Gács (2003) nennen zwei
  Quellen leicht verschiedene Formeln; das Original ist nicht gelesen.
- Untere Schranke: `CAN(3, q+2, q) >= q^3 + 12` für ungerades `q >= 11` (CKRS, Satz 8.1; nur über Bai und eine
  Vorabfassung gelesen). Für `t >= 4` nichts gefunden.
- Pull Requests bei `ca-tools` (per `git fetch` gelesen): 89 (`CA(165; 3, 8, 5)`), 90 (`(3, 28, 3)`, 73 Zeilen),
  91 (die eigene Einreichung). Keiner berührt die Zellen hier. Der Subagent selbst kam nicht an GitHub heran.

## 8. Nächste Schritte

1. Nachbau durch Antigravity aus Abschnitt 2 (nicht aus den Skripten); Fremdprüfung der Argumente in 3.
2. Übertragung auf Primzahlpotenzen (`q = 9, 25, 27`); `x^((q+1)/2)` gibt es für jedes ungerade `q`.
3. Beweis von Satz 3 und der Belegung der schweren Geraden ausschreiben; dann ist `17/12` ein Satz.
4. `7/5` über Charaktersummen; und die Frage, ob ein anderes Skelett unter `7/5` kommt.
5. Gerades `q`, und `v < q` systematisch.

## 9. Dateien im Paket 2

Listen aus Abschnitt 5; `apex.py` (gemeinsamer Punkt, beliebige Steigungspaare), `paley.py` (Bauart aus
Abschnitt 2, Zählung und Listenbau), `paley_scan.py` (Tabelle über viele `q`), `paley_v.py` (`v < q`),
`ls_fast.py`, `ls_pack.py`, `ls_pack2.py`, `skeleton.py`, `gfmod.py`.
