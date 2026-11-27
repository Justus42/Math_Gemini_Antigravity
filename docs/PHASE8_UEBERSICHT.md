# Phase 8: Klassen ohne volle Gerade (`k = q + 2`, `v = q`) — Übersicht

- Stand: 2026-11-27, 01:39 MEZ. Autor: Claude (Phase-8-Chat). Branch `claude/phase8-klassen-ohne-gerade`.
- Vergleichsstand: dieses Repo `main @ d04a97b`; `chrispbsmolen/ca-tools @ f682ba3` (27.11., 01:38 MEZ per `git fetch`; die `37` Zeilen aus PR `#91` stehen dort noch nicht in `table/ca_frame.csv`).
- **Rolle:** Der Phase-8-Chat hat die Bauart entwickelt **und** gerechnet. Er ist damit nicht ihr Prüfer. Nichts hier ist von einem unbeteiligten Modell oder Menschen gelesen. Kein Neuheitsanspruch.
- **Außenwirkung:** keine. Keine Einreichung ohne ausdrückliche Freigabe durch Justus (`RULES.md`, „Meldung nach außen“).

Ausführlich: [`docs/phase8/NOTIZ_1_KLASSEN_OHNE_GERADE.md`](phase8/NOTIZ_1_KLASSEN_OHNE_GERADE.md) (Prüfung von Geminis vier Optionen, Idee, erste Listen) und [`docs/phase8/NOTIZ_2_FORMEL.md`](phase8/NOTIZ_2_FORMEL.md) (Bauart mit gemeinsamem Punkt, Formel, Zählung). Schreibweise wie in [`docs/PHASE7_T2_REDUCTION.md`](PHASE7_T2_REDUCTION.md) §2.

> **Nachtrag 27.11.2026, 02:16 MEZ:** Die Argumente zu den Aussagen 1, 2, 5, 6 und 7 sind inzwischen ausgeschrieben (Gemini), siehe [`docs/PHASE8_ARGUMENTE.md`](PHASE8_ARGUMENTE.md); dort auch die Vermutung aus Notiz 1 §3.1 als Aussage 1.5. Belegart bleibt „Argument“, bis ein unbeteiligtes Modell gelesen hat. Die Tabelle unten ist der Stand von 01:39 MEZ.

> **Nachtrag 27.11.2026, 07:30 MEZ:** Zu Frage 3 und 4 aus §6 (Untergrenze im Modell, anderes Skelett) siehe [`docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md`](phase8/NOTIZ_3_UNTERGRENZE_BAER.md): eine Untergrenze `q^2 + q^(3/2) - 2q` für jede Liste (Argument) und eine Bauart für Quadratzahlen mit `q^2 + 2*q^(3/2) - 2q` Vertretern (gebaut für `q = 4..81`). Die Tabellen unten sind der Stand von 01:39 MEZ.

## 1. Was behauptet wird, je mit Belegart

| # | Aussage | Belegart |
| --- | --- | --- |
| 1 | Jede Symbolklasse von `a` oder `b` enthält eine volle Gerade `d = const` oder hat mindestens `q + sqrt(q)` Punkte (Primzahl `q`: mindestens `(3q+1)/2`). | Argument (Notiz 1 §3.1) aus Bruen und Blokhuis; an den sieben Listen in `data/phase7/` abgelesen (`scripts/phase8/dissect.py`) |
| 2 | Für Primzahl `q` ist das Geradenpaar mit Steigungen `±σ` durch einen Punkt `O` einer reinen `b`-Geraden, eingeschränkt auf die Geradenmenge `Δ`, zusammen mit den Punkten `p` der schweren Geraden mit `p^2 - e^2` Quadrat oder `0`, eine solche Klasse. | Für alle Klassen bei `q = 11, 13, 17, 19, 23, 29, 31, 37, 41, 43` nachgerechnet (jede Gerade `c + al*d = u` wird getroffen); allgemein nur Argument (projektives Dreieck), nicht ausgeschrieben |
| 3 | Zehn Vertreterlisten in `data/phase8/` erfüllen die Bedingung an `M(R)`. | Rechnung: `scripts/phase7_lift.py --check-m`, `0` Lücken, `13` von `13` Läufen (§3) |
| 4 | Sieben Arrays in `results/phase8/` sind Covering Arrays. | Dual-verifiziert nach `RULES.md` §3, dazu Nachbau und Zähler des Prüfers, Negativkontrolle (§3) |
| 5 | Geschlossene Formel: `\|R\| = q^2 + C(q,2) - q(1+j) + (q-5)/2 - j` für `q ≡ 3 (mod 4)`, `0 <= j <= (q-15)/12`; für `q ≡ 1 (mod 4)` zusätzlich `+ (2+2j)`, `j <= (q-13)/12`. | Zählung der Streichungen für alle Primzahlen `13 <= q < 520` nachgerechnet; als Liste gebaut und mit eigenem Zähler geprüft nur `q = 19, 31, 43` (Listen nicht abgelegt); der Schluss von der Zählung auf die Liste beruht auf Aussage 2, auf der Belegbarkeit der schweren Geraden (Argument, nicht ausgeschrieben) und auf Aussage A aus Phase 7 (Argument) |
| 6 | Leitkonstante `17/12` statt `3/2` für Primzahlen `q`. | folgt aus Aussage 5; also Argument |
| 7 | Grenzwert `7/5`. | Vermutung; Zählung bis `q = 499` (`1,4028`), kein Beweis |

## 2. Formel, Regel und Listen sind drei verschiedene Dinge

Hinweis des Prüfer-Chats ([`docs/UEBERGABE_PRUEFER_CHAT_2026-11-27.md`](UEBERGABE_PRUEFER_CHAT_2026-11-27.md) §7.1), nachgerechnet und richtig: Die geschlossene Formel liegt bei jedem `q <= 37` über der kleinsten Liste. Genauer gibt es drei Stufen.

| `q` | Phase 6A | (a) geschlossene Formel, größtes erlaubtes `j` | (b) Regel ohne Suche, `j` durch Auszählen gewählt | (c) kleinste Liste | Herkunft von (c) |
| ---: | ---: | ---: | ---: | ---: | --- |
| 9 | 117 | – | – | **113** | CP-SAT im symmetrischen Skelett |
| 11 | 176 | – | 172 | **170** | Packung von Rédei-Klassen mit CP-SAT |
| 13 | 247 | 240 | 240 | **238** | wie `q = 11` |
| 17 | 425 | 416 | 416 | **412** | wie `q = 11` |
| 19 | 532 | 520 | 516 | **513** | gemeinsamer Punkt, Steigungspaare mit CP-SAT gewählt |
| 23 | 782 | 768 | 746 | **746** | gemeinsamer Punkt, Paare `±σ`, Quadrate mit CP-SAT gewählt |
| 29 | 1247 | 1204 | 1192 | **1190** | wie `q = 23` |
| 31 | 1426 | 1376 | 1358 | **1356** | wie `q = 23` |
| 37 | 2035 | 1944 | 1944 | **1942** | wie `q = 23` |

- (a) ist eine Formel. (b) ist eine feste Regel („alle Quadrate außer den `j + 1` kleinsten `e`“), deren Wert man auszählen muss; als Liste gebaut ist (b) nicht. (c) sind Löserlisten innerhalb einer ausdrücklich beschriebenen Familie; **Optimalität offen**.
- In allen Listen belegt ein CP-SAT-Lauf die schwere Gerade. Die Wahl der Klassen ist bei `q >= 19` ein kleines Modell (höchstens `q(q-1)/2` Variablen), das CP-SAT als `OPTIMAL` abschließt; das ist Optimalität **in dieser Familie bei festem `j`**, nicht im Modell `M(R)`.
- Für die Tabelle (`v <= 25`, also `q <= 23`) kommt der Gewinn aus (c), nicht aus (a). Die Formel wird erst für große `q` gut (`1,4177` bei `q = 499`).

## 3. Prüfung der Listen (27.11.2026, 01:35–01:36 MEZ, `73 s`)

Lauf `P8-PRUEFUNG-LISTEN`: `python3 scripts/phase8/pruefe_listen.py <zaehler> <arbeitsverzeichnis>` auf dem Branch. Vorher: `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff origin/main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23`. Ergebnis je Zeile in [`results/phase8/VERIFICATION_LOG_phase8.md`](../results/phase8/VERIFICATION_LOG_phase8.md):

- `M(R)`: `0` Lücken in `13/13` Läufen (`scripts/phase7_lift.py --check-m`).
- `verifiers/ca_verify`: Exit `0` in `13/13`. `verifiers/verify_independent.py`: Exit `0` in `10/10` (für `q = 29, 31, 37` nicht gelaufen).
- `scripts/pruefer/nachbau.py` (eigene Körperarithmetik des Prüfers): Array byte-gleich zu `scripts/phase7_lift.py` in `13/13`. `scripts/pruefer/zaehler.c`: Exit `0` in `13/13`.
- Negativkontrolle (letzte Zeile entfernt): `ca_verify` Exit `1` in `13/13`, `verify_independent.py` Exit `1` in `10/10`.

Einschränkungen: eine Maschine (2 vCPU), keine Fremd-Reproduktion; die Listen stammen aus Läufen mit Zeitlimit und sind nicht bytegenau neu erzeugbar (maßgeblich ist die abgelegte Liste mit SHA-256 in `data/phase8/SHA256SUMS`); `t = 5, 6` nicht erzeugt.

## 4. Zellen gegen `ca-tools @ f682ba3`

Die `37` Zeilen aus PR `#91` stehen noch nicht in der Tabelle; nach ihrem Eintrag ist der Vergleichswert an den Zellen mit „PR `#91`“ der eigene.

| Zelle | Tabelle `f682ba3` | PR `#91` | Phase 8 | Stand |
| --- | ---: | ---: | ---: | --- |
| `(3, 11, 9)` | 1089 | 1044 | 1017 | dual-verifiziert, abgelegt |
| `(4, 11, 9)` | 9801 | 9396 | 9153 | dual-verifiziert, abgelegt |
| `(5, 11, 9)` | 88209 | 84564 | 82377 | nur Vorhersage |
| `(6, 11, 9)` | 793881 | 761076 | 741393 | nur Vorhersage |
| `(3, 13, 11)` | 1991 | 1925 | 1870 | dual-verifiziert, abgelegt |
| `(4, 13, 11)` | 21901 | 21175 | 20570 | dual-verifiziert, abgelegt |
| `(5, 13, 11)` | 240911 | 232925 | 226270 | nur Vorhersage |
| `(3, 15, 13)` | 3289 | 3211 | 3094 | dual-verifiziert, abgelegt |
| `(4, 15, 13)` | 42757 | 41743 | 40222 | dual-verifiziert, abgelegt |
| `(5, 15, 13)` | 555841 | 542659 | 522886 | nur Vorhersage |
| `(4, 19, 17)` | 125137 | 122825 | 119068 | nur Vorhersage (im Chat erzeugt und mit `ca_verify` geprüft, hier nicht wiederholt) |
| `(3, 21, 19)` | 10279 | 10108 | 9747 | dual-verifiziert, abgelegt |
| `(4, 21, 19)` | 195301 | 192052 | 185193 | nur Vorhersage |
| `(4, 25, 22)` | 390619 | – | 381938 | nur Vorhersage |
| `(5, 25, 22)` | 9765619 | – | 8784574 | nur Vorhersage |
| `(5, 25, 23)` | 9765621 | – | 9076582 | nur Vorhersage |
| `(6, 25, 23)` | 244140621 | – | 208761386 | nur Vorhersage |

Nicht kleiner als die Tabelle: `(3, 19, 17)` (`7004` gegen `6778`), `(3, 25, 23)` (`17158` gegen `15612`), `(4, 25, 23)` (`394634` gegen `390621`), `(3, 25, 22)` (`16606` gegen `15517`). Für `v >= 26` hat die Tabelle keine Zellen. Die Tabellenwerte stammen aus `scripts/pruefer/tabelle.py` (`ca_frame.csv`, `ca_table.csv.gz`, `derived.csv`, Treppenregel) am Commit `f682ba3` (Lauf `P8-TABELLE-F682BA3`, 27.11., 01:39 MEZ): `17` Zellen kleiner, `4` nicht. Offene Pull Requests des Ziels sind dabei nicht durchgesehen; vor jeder Meldung nach Regel 2a und 2b neu.

## 5. Was am Gate fehlt (aus der Übergabe §7.2, Stand je Punkt)

1. Ins Repo: mit diesem Branch erledigt, sobald gemergt.
2. Nachbau aus der Beschreibung (Notiz 2 §2), nicht aus `scripts/phase8/`: offen. Der Lift ist mit `nachbau.py` unabhängig nachgebaut, die **Listen** nicht.
3. Dual-Verifikation für `t = 5, 6` und für alle Arrays einer Einreichung: offen.
4. Belegart je Aussage: §1 und §2 oben.
5. Literaturprüfung mit Prüfvermerk nach Regel 2c: offen. Vorarbeit eines Subagenten (Sonnet) in Notiz 2 §7: kein Fund zu Rédei-Mengen oder Richtungszahlen bei Covering Arrays; CKRS im Original, Bais Begleitpapier und Zenodo-Volltexte ungelesen.
6. Fremdprüfung des Arguments (Aussagen 2, 5, 6): offen.
7. Prüfer: ein frischer Chat, nicht dieser.

## 6. Offene Forschungsfragen

1. Beweis von Aussage 2 und der Belegung der schweren Geraden; dann ist `17/12` ein Satz für Primzahlen.
2. Ungerade Primzahlpotenzen (`q = 9, 25, 27`): `x^((q+1)/2)` gibt es für jedes ungerade `q`; nicht gerechnet.
3. Untere Schranke im Modell `M(R)`, wenn Klassen ohne volle Gerade erlaubt sind.
4. `7/5` über unvollständige Charaktersummen; und ob ein anderes Skelett darunter kommt.
5. Gerades `q`; `v < q` (bei `q = 23` nur `v = 22` und knapp `v = 21` kleiner als §14).

## 7. Dateien

- `data/phase8/`: zehn Listen, `SHA256SUMS`. Format: je Zeile `c d a b`, ohne Kopfzeile.
- `results/phase8/`: sieben Arrays, `SHA256SUMS`, `VERIFICATION_LOG_phase8.md`.
- `scripts/phase8/`: `gfmod.py` (Körper), `skeleton.py`, `skeleton2.py` (Modell im Skelett), `ls_pack.py`, `ls_fast.py`, `ls_pack2.py` (Rédei-Klassen packen), `apex.py` (gemeinsamer Punkt), `paley.py`, `paley_scan.py`, `paley_v.py` (Paare `±σ`, Zählung, `v < q`), `coset_model.py`, `count_ca.py` (Kernvergleich, eigener Zähler), `dissect.py`, `pruefe_listen.py`. Braucht `ortools` (gerechnet mit `9.15.6755`, Python `3.13.18`).
