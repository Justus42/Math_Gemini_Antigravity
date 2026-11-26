# Prüfvermerk des Prüfers zu PR `#34` (Staging des 37er-Pakets)

- **Geprüft:** PR `#34`, Branch `chore/stage-phase7-37` @ `aca3fc6`, Ordner `staging/jeserigk-ckrs-coset-2026-11/` (`HOW.md` SHA-256 `930fc550…`, `claims.csv` SHA-256 `76cca2c1…`).
- **Zeit:** 2026-11-26, 21:02–21:17 MEZ. Maschine des Prüfers (2 vCPU), nicht die Maschine von Antigravity.
- **Vergleichsstand:** `chrispbsmolen/ca-tools @ e673ab4`; `main` dort um 21:02 MEZ unverändert, höchste PR-Nummer `90` (`git ls-remote`, rein lesend).
- **Nach außen:** nichts. Keine Einreichung, kein Push nach `Justus42/ca-tools`.

## 1. Ergebnis

Die 37 Arrays und beide `ca-tools`-Werkzeuge sind ohne Befund. **Der Text ist noch nicht einreichungsreif** (§3), und der PR ist gegen `main @ 5afa407` nicht konfliktfrei (`STATUS.md`, `docs/RUN_LOG.md`).

| Prüfung | Ergebnis | Belegart |
| --- | --- | --- |
| Geschützte Pfade | `verifiers/`, `results/`, `submission/` ohne Diff; `docs/RUN_LOG.md` nur eine Zeile angehängt | Diff gelesen |
| Staging gegen `results/` auf `main` | `37/37` byte-gleich, jede Datei genau einmal in `results/` | nachgerechnet |
| `claims.csv` | `37` Zeilen, `37` Dateien; Dateiname, `q = k - 2`, `m`, `w = max(0, 2v - q)` und `N = m * q^(t-2)` je Zeile stimmig; `14` Löserliste, `17` Formel `v < q`, `6` Formel `v = q` | nachgerechnet (eigenes Skript) |
| Tabellenwert | `37/37` kleiner als `N_eff` (eigenes `scripts/pruefer/tabelle.py`) | nachgerechnet |
| Nachbau mit den Befehlen aus `claims.csv` | Skripte und Listen vom Commit `666f767`: `37/37` byte-gleich; dieselben Befehle mit den Skripten von `main @ 5afa407`: `37/37` byte-gleich | nachgerechnet, zweite Maschine |
| Formel bei `v = q` | Lift von `phase7_reps_vq.py 13 13`, `t = 3`: dieselbe Zeilenmenge wie `CA_3211_3_15_13.txt` (sortiert verglichen) | nachgerechnet, ein Fall |
| Links in `HOW.md` und `claims.csv` | `19` verschiedene Blob-Links, alle am Commit `666f767` vorhanden | nachgerechnet |
| `tools/check_submission.py … --constant-rows-minutes 0.05` | `PASS`, `37/37` `verified` und `exceeds_table`, `0` Probleme, `Credit check: No flags`, Prüfzeit `389 s` (Wall-Clock `442 s`), `rc = 0` | vollständig durchgelaufen |
| `tools/consistency.py --check --pr --base e673ab4` | **Komplettlauf** einschließlich `check_constructions`: `0 problems`, `rc = 0`, `283 s`; eine `::warning::` zu `t2-v11-k34100-2` (Bestand von `ca-tools`) | vollständig durchgelaufen |

Damit ist der in PR `#34` offene Punkt „`consistency.py`-Komplettlauf“ erledigt. Der Nachbau schließt außerdem die Lücke „zweite Maschine“ für `CA_3211_3_15_13.txt`, `CA_10108_3_21_19.txt` und `CA_41743_4_15_13.txt`; für die übrigen 34 lag der Abgleich schon vor.

## 2. Abweichungen und Grenzen dieser Prüfung

- Beide Werkzeuge liefen gleichzeitig auf 2 Kernen (betrifft Zeiten und, über das Zeitbudget, wie viele „constant rows“ berechnet wurden; nicht `PASS`/`FAIL`). Ein erster Start beider Läufe scheiterte sofort an einem fehlenden Hilfsprogramm (`/usr/bin/time`) und wurde ohne dieses wiederholt.
- Prüfkopie: Git-Worktree von `ca-tools @ e673ab4`, Staging-Ordner nach `submissions/jeserigk-ckrs-coset-2026-11/` kopiert und mit `git add` vorgemerkt (nicht committet).
- Nicht wiederholt: `tools/tests_frame/test_build_frame.py`, Negativkontrollen, `verify_independent.py`.
- Offene PRs bei `ca-tools` konnte ich nicht über die API lesen; `#89` und `#90` sind Angaben von Antigravity.
- Der Nachbau nutzt dieselben Skripte wie der Erstlauf: bestätigt ist die Wiederholbarkeit, nicht die Unabhängigkeit des Erzeugers.

## 3. Befunde am Text (vor einer Einreichung zu beheben)

1. **Falscher Stand verlinkt.** Alle `19` Links zeigen auf `666f767`. Dort enthält `docs/PHASE7_T2_REDUCTION.md` noch die in PR `#33` berichtigte Ungleichung in §14.1 (ohne `max`), und die Prüfung durch das unbeteiligte Modell fehlt. Neu verlinken auf einen Stand ab `5afa407`. Die Hashes ändern sich dadurch nicht (§1).
2. **„Open items“ überholt.** `HOW.md` sagt, das Argument sei von keinem unbeteiligten Modell gelesen. Seit PR `#33` stimmt das nicht mehr: zwei Durchgänge mit GPT-6.2 Sol, ohne Befund an der Kette ([`docs/THIRD_MODEL_REVIEW_PHASE7.md`](THIRD_MODEL_REVIEW_PHASE7.md)). Richtig wäre: von einem unbeteiligten Modell gelesen, von keinem Menschen mit Fachausbildung; Belegart bleibt Argument. Ebenso Zenodo: Seiten abgerufen (Bai `1.0`, Sitjar `v1.10`), neuere Fassungen nicht ausgeschlossen.
3. **`source_detail` unvollständig.** `phase7_lift.py` und `phase7_reps_vq.py` importieren `gen_general_tqv.py`. In `31` der `37` Zeilen fehlt diese Datei in `source_detail`; wer nur den dort genannten Links folgt, bekommt einen Importfehler. Da `source_detail` wörtlich in die Tabelle übernommen wird, gehört die Datei in jede dieser Zeilen.
4. **Aussage zur Verifikation weiter als der verlinkte Beleg.** `HOW.md` nennt für alle 37 den Abgleich auf zweiter Maschine und `verify_independent.py`, verlinkt aber `results/phase7_vq/VERIFICATION_LOG.md`, wo `verify_independent.py` für `#17`–`#23` als „nicht gelaufen“ steht, und `results/general_tqv/VERIFICATION_LOG.md`, wo die zweite Maschine als ausstehend steht. Die Nachträge stehen in [`docs/THIRD_PARTY_VERIFICATION_PHASE7.md`](THIRD_PARTY_VERIFICATION_PHASE7.md) und in diesem Vermerk; beide verlinken.
5. **Negativkontrollen genauer fassen.** Nach den Protokollen mit `ca_verify` auf allen 37 gelaufen, mit `verify_independent.py` nicht auf `#17`–`#23` aus PR `#31` (Protokolle gelesen, nicht wiederholt). Der Satz in `HOW.md` lässt das offen.
6. **CKRS-Zitat.** „Lemma 3.3“ ist die Nummerierung des Autoren-Preprints; die Zeitschriftenfassung ist nicht abgeglichen. Die Übersetzung in eine Vertreterliste ist eine Lesart dieses Repos, keine Aussage der Autoren ([`docs/LITERATURE_CHECK_PHASE7_VQ.md`](LITERATURE_CHECK_PHASE7_VQ.md) §2.6). Beides in einem Halbsatz sagen. Außerdem fehlt der vereinbarte Zusatz: gleiches Bauprinzip, andere Beschriftung und Verteilung der Zusatzblöcke, keine Teilmenge des CKRS-Arrays.
7. **CP-SAT-Angaben.** `ca-tools` verlangt für eine Suche „seeds and settings“. Es fehlen der Modus je Liste (`min` bei `q = 5`, `hint` bei `q = 7, 8, 9, 11`) und der Hinweis, dass bei `q = 11` ein zweiter Lauf von `1800 s` ab `175` nichts fand und bei `q = 13` ein Lauf von `1800 s` nichts unter `247` (§10, §13 des Phase-7-Dokuments).
8. **Kleinigkeit.** Die Analyse, die zur Rückführung auf Stärke 2 führte, ging von zwei Tabellen-Arrays aus: `CA(165; 3, 7, 5)` (Bai) und `CA(825; 4, 7, 5)` (Sitjar). `HOW.md` nennt nur das zweite.

Ohne Befund: Zahlen in `HOW.md` (Klassen `23`/`14`, `q`-Mengen, `m`-Werte, Formel und Fallunterscheidung gegen `scripts/phase7_reps_vq.py`), Körperdarstellung, DOI und Kennungen gegen `table/references.csv`, „AI tools used: yes“, kein Neuheitsanspruch, Wortwahl „smaller than `ca-tools` @ `e673ab4`“.

## 4. Nach der Korrektur zu wiederholen

`claims.csv` ändert sich (Befunde 1 und 3). Danach `tools/check_submission.py` und `tools/consistency.py` erneut laufen lassen und die Links am neuen Commit prüfen. Die Arrays selbst müssen nicht neu geprüft werden, solange sie byte-gleich bleiben.
