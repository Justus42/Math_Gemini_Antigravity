# Prüfvermerk des Prüfers zu Phase 7: PR `#31` (`docs/THIRD_PARTY_VERIFICATION_PHASE7.md`)

- **Stand:** 2026-11-26, 19:40 MEZ. **Autor:** Claude (Prüfer-Chat). Geprüft: PR `#31` @ `c12b09e` (Antigravity, `chore/verify-phase7-23`, Basis `main @ e3100f6`), 23 Arrays.
- **Vergleichsstand:** `chrispbsmolen/ca-tools @ e673ab4`.
- **Rolle:** Die 20 Arrays aus Bauart §14 und Löserliste stammen aus der Rechnung des Prüfers; für sie ist Antigravitys Nachbau die Zweitmaschine. Für die 3 Phase-6A-Erstläufe ist dieser Vermerk die Zweitmaschine. Kein unbeteiligtes Drittprogramm im Sinn von `RULES.md` 2d für die Erzeugung: beide Seiten benutzen dieselben Skripte.

## 1. Ergebnis

| Prüfpunkt | Ergebnis |
| --- | --- |
| Dateien gegen die `SHA256SUMS` des PR | `23/23` gleich |
| Byte-Vergleich mit den Dateien des Prüfers (26.11., §10 und §14.4 des Phase-7-Dokuments) | `20/20` gleich |
| Phase-6A-Erstläufe `#15`, `#18`, `#20` auf der Maschine des Prüfers neu erzeugt (`scripts/gen_general_tqv.py`) | `3/3` byte-gleich (`cbf2db99…`, `7da2d494…`, `1a78674e…`) |
| Geschützte Pfade (`verifiers/`, `submission/`, `scripts/`, `data/`, `results/SHA256SUMS`, `results/t4_nearbush/`, die vier in PR `#88` verlinkten Dateien) | unverändert |
| Bestehende Dateien unter `results/` | nur `results/phase7/SHA256SUMS` und `results/general_tqv/SHA256SUMS` verlängert, keine Zeile entfernt |
| `docs/RUN_LOG.md` | nur angehängt |
| Eigener Zähler (`scripts/pruefer/zaehler.c`) und `verifiers/ca_verify.c` | `23/23` `PASS` (20 am Nachmittag an byte-gleichen Dateien, 3 jetzt) |
| Negativkontrolle (letzte Zeile entfernt, eigener Zähler) | `23/23` `FAIL` |
| Tabellenvergleich mit eigenem Programm (`scripts/pruefer/tabelle.py`) | `23/23` kleiner als `ca-tools @ e673ab4`, gleiche Differenzen wie im PR |

## 2. Lücke aus PR `#31` geschlossen: `verify_independent.py` für `#17`–`#23`

PR `#31` meldet für sieben Arrays `verify_independent.py` als „nicht gelaufen“ (Grenze von 10 Minuten je Befehl). Nach `RULES.md` §3 fehlt damit der zweite Verifier. Nachgeholt auf der Maschine des Prüfers (2 Kerne, zwei Läufe gleichzeitig, als Hintergrundlauf ohne Zeitgrenze), an den Dateien aus dem PR:

| # | Datei | `verify_independent.py` | Dauer |
| --- | --- | --- | --- |
| 17 | `results/phase7_vq/CA_179417_4_21_18.txt` | `PASS` (`rc=0`) | `354 s` |
| 18 | `results/general_tqv/CA_192052_4_21_19.txt` | `PASS` (`rc=0`) | `435 s` |
| 19 | `results/phase7_vq/CA_492128_5_15_12.txt` | `PASS` (`rc=0`) | `598 s` |
| 20 | `results/general_tqv/CA_542659_5_15_13.txt` | `PASS` (`rc=0`) | `957 s` |
| 21 | `results/phase7_vq/CA_351785_4_25_20.txt` | `PASS` (`rc=0`) | `1502 s` |
| 22 | `results/phase7_vq/CA_370300_4_25_21.txt` | `PASS` (`rc=0`) | `1781 s` |
| 23 | `results/phase7_vq/CA_456250_4_27_20.txt` | `PASS` (`rc=0`) | `2321 s` |

Aufruf je Datei: `python3 verifiers/verify_independent.py DATEI t v -n N -k k`. Gesamt `18:24:59`–`19:35:39` MEZ.
Die Negativkontrolle mit `verify_independent.py` ist für diese sieben **nicht gelaufen** (weitere etwa 70 Minuten); Negativkontrollen liegen mit `ca_verify` und dem eigenen Zähler vor.

Damit haben alle 23 Arrays beide Verifier aus `RULES.md` §3 bestanden: 16 bei Antigravity, 7 hier. Das Protokoll in `results/phase7_vq/VERIFICATION_LOG.md` nennt die sieben weiter als „nicht gelaufen“; es liegt in einem geschützten Pfad und ist hier nicht geändert. Nachtragen kann es Antigravity.

## 3. Einschränkungen

- Erzeugung auf beiden Maschinen mit denselben Skripten; bestätigt ist die Wiederholbarkeit, nicht die Unabhängigkeit des Erzeugers. Unabhängig vom Erzeuger sind die Zählprogramme.
- Der eigene Nachbau (`scripts/pruefer/nachbau.py`) deckt nur Primzahl-`q` und `q = 8, 9` ab; byte-gleich geprüft für 10 der 17 Bauart-Arrays und die 3 Löserlisten-Arrays (`t = 3, 4, 5`).
- Die Aussage §14.1 allgemein bleibt Argument; eine Prüfung durch ein unbeteiligtes Modell steht aus.
- Literatur: nicht vollständig geprüft (`docs/LITERATURE_CHECK_PHASE7_VQ.md`).
