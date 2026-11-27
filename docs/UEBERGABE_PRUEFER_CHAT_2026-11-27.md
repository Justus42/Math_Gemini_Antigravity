# Übergabe des Prüfer-Chats an den Phase-8-Chat (27.11.2026, 01:25 MEZ)

Geschrieben von Claude (Prüfer-Chat, Sitzung vom 26./27.11.) für den Chat, der die Bauart „Klassen ohne volle Gerade“ (Phase 8) entwickelt hat und jetzt Schreibrechte am Repo bekommt. Angaben mit Belegart. Was ich nicht selbst geprüft habe, steht ausdrücklich so da. Bei Widerspruch gilt das Repo, nicht diese Datei.

## 1. Stand in fünf Sätzen

1. Die zweite Einreichung (`jeserigk-ckrs-coset-2026-11`, 37 Arrays, `k = q + 2`, `t = 3..6`) ist bei `chrispbsmolen/ca-tools` als PR `#91` **gemergt** (27.11., 01:13 MEZ, Merge-Commit `fef4f72`).
2. Die automatische Prüfung dort hat bestanden: `Result: PASS. 37 of 37 claims passed.`, keine Credit-Flags.
3. In die Tabellendateien (`table/ca_frame.csv`, `table/ca_table.csv.gz`) sind die 37 Zeilen um 01:25 MEZ **noch nicht** eingetragen (`main` dort `f682ba3`); bei PR `#88` kam dieser Schritt etwa 45 Minuten nach dem Merge.
4. Nach deinen Angaben sind 13 der 37 Arrays durch deine neuen Listen schon unterboten. Das habe ich nicht geprüft; die Listen liegen nicht im Repo.
5. Dieser Chat endet hier. Offene Punkte stehen in §6, mein Blick auf Phase 8 in §7.

## 2. Was eingereicht und gemergt ist

| Gegenstand | Wert | Belegart |
| --- | --- | --- |
| Pull Request | https://github.com/chrispbsmolen/ca-tools/pull/91, geöffnet von Justus am 26.11. zwischen 22:53 und 23:03 MEZ | Seite gelesen (27.11., 00:43 MEZ) |
| Merge | `fef4f72174691200c58121146683eba4b8618a0b`, 27.11., 01:13 MEZ | `git fetch`, `git log` (rein lesend) |
| Head der Einreichung | `Justus42/ca-tools`, Branch `submit/jeserigk-ckrs-coset-2026-11`, `0acc8244f4506f795cc14e4d3b2f9c2c0228f412`; liegt in `upstream/main` | nachgeprüft |
| Basis | `ca-tools @ 808945f` | nachgeprüft |
| Inhalt | nur `submissions/jeserigk-ckrs-coset-2026-11/`: 37 Arrays, `claims.csv`, `HOW.md`; `199.087.972 B` (`189,8651 MiB`) | byte-gleich zu `staging/jeserigk-ckrs-coset-2026-11/` auf `main` dieses Repos, nachgerechnet |
| Prüfbericht | Kommentar `#issuecomment-7205657566`: `PASS`, `37/37` `verified`, `exceeds_table`, `Credit check: No flags`, `88,8 min` | Seite gelesen, mit lokalem Lauf abgeglichen (`previous best` 37/37 gleich) |
| Commit-Autor | `Justus42` (GitHub-noreply), Committer Claude, mit `Co-Authored-By` | eigener Commit |

Die 37 Zellen: 14 aus Löserlisten bei `v = q` (`q = 5, 7, 8, 9, 11`; Blockzahlen `34, 68, 91, 116, 175`), 17 aus der geschlossenen Liste bei `v < q` (`|R| = q^2 + C(max(0, 2v - q), 2)`), 6 aus derselben Liste bei `v = q` (`q = 13, 17, 19`; das ist Phase 6A). Vollständige Tabelle mit SHA-256: [`docs/STAGING_PHASE7_37.md`](STAGING_PHASE7_37.md) §1.

**Was `HOW.md` nach außen sagt** (für deine nächste Einreichung wichtig, weil sie daran anschließt):

- Verfeinerung einer Bauart von Colbourn, Kéri, Rivas Soriano, Schlage-Puchta (2010), Lemma 3.3 nach Preprint-Nummerierung, „our reading“; kein Neuheitsanspruch.
- Die Bedingung an `M(R)` ist als **hinreichend** bezeichnet, Notwendigkeit wird nicht behauptet.
- Offene Punkte dort: Optimalität der fünf Löser-Blockzahlen offen; die geschlossene Liste ist für `v < q` nicht kleinstmöglich (`(5, 4)`, `(7, 6)`); Argument von einem unbeteiligten Modell gelesen, von keinem Menschen mit Fachausbildung; Literaturprüfung nicht erschöpfend.

Deine neuen Listen widersprechen also keiner Aussage der Einreichung. Sie zeigen aber, dass die Abbruchregel „ein zweiter Lauf gleicher Länge findet nichts“ ein schwacher Beleg war: bei `q = 11` blieb der Löser zweimal 30 Minuten bei 175 stehen, du nennst 170.

## 3. Repo: wo was liegt

- **Regeln:** [`RULES.md`](../RULES.md) (Wortwahl nach außen, Regel 3 dominierte Dateien, Regel 7, Dual-Verifikation, `HANDOVER`-Format §5), [`AGENTS.md`](../AGENTS.md), [`STATUS.md`](../STATUS.md) (Abschnitt „Meldung nach außen“ ist der amtliche Stand zu PR `#88` und `#91`).
- **Phase 7 (Argument):** [`docs/PHASE7_T2_REDUCTION.md`](PHASE7_T2_REDUCTION.md). §2 Konventionen, §3 Aussage A, §11 Modell `v < q` (Aussage A'), §14 geschlossene Bauart, §10 und §13 Löserläufe und Abbruchregel.
- **Literatur:** [`docs/LITERATURE_CHECK_PHASE7_VQ.md`](LITERATURE_CHECK_PHASE7_VQ.md) (§2.6 CKRS, §2.7 Zenodo-Stände, §4 Herkunftsreihenfolge, §5 Restliste).
- **Prüfvermerke:** [`docs/THIRD_PARTY_VERIFICATION_PHASE7.md`](THIRD_PARTY_VERIFICATION_PHASE7.md), [`docs/STAGING_REVIEW_PR34.md`](STAGING_REVIEW_PR34.md), [`docs/THIRD_MODEL_REVIEW_PHASE7.md`](THIRD_MODEL_REVIEW_PHASE7.md) mit Wortlaut in `docs/openrouter/`.
- **Zuschnitt:** [`docs/PHASE7_VQ_SCAN.md`](PHASE7_VQ_SCAN.md) (76 Zellen), [`docs/PHASE7_ZUSCHNITT.md`](PHASE7_ZUSCHNITT.md) (41 Zellen geschätzt bis 50 MiB, 36 darüber). Beide gegen `ca-tools @ e673ab4` gerechnet; mit deinen Listen sind die Blockzahlen dort überholt.
- **Erzeuger:** `scripts/phase7_lift.py` (Lift, `--check-m`, `--v`), `scripts/phase7_reps_vq.py` (geschlossene Liste), `scripts/gen_general_tqv.py` (Körperarithmetik; wird von beiden importiert), `scripts/phase7_solve_cpsat.py` und `scripts/phase7_solve_cpsat_vq.py` (CP-SAT).
- **Eigene Prüfwerkzeuge, unabhängig vom Erzeuger:** `scripts/pruefer/zaehler.c` (zählt Überdeckung; Exit 0 gedeckt, 1 Lücken, 2 Format), `scripts/pruefer/nachbau.py` (eigener Lift mit eigener Körperarithmetik, nur Primzahl-`q` und `q = 8, 9`), `scripts/pruefer/tabelle.py` (Tabellenwert mit Treppenregel).
- **Listen:** `data/phase7/` (`R_q5_m34`, `R_q7_m68`, `R_q8_m91`, `R_q9_m116`, `R_q11_m175` sowie Listen für `v < q`).
- **Arrays:** `results/phase7/`, `results/phase7_vq/`, `results/general_tqv/`, `results/t4_nearbush/`; Kopie der Einreichung in `staging/jeserigk-ckrs-coset-2026-11/`.

**Nicht ändern:** `verifiers/`, `results/`, `submission/ca_tools_staging/`, und ab jetzt auch `staging/jeserigk-ckrs-coset-2026-11/` (Abbild von PR `#91`). Nicht verschieben, umbenennen oder löschen: `docs/LITERATURE_CHECK_PGL_CCL.md`, `docs/THIRD_PARTY_VERIFICATION.md`, `docs/RUN_LOG.md`, `results/VERIFICATION_LOG_pgl_ccl.md` (in PR `#88` verlinkt). `docs/RUN_LOG.md` nur anhängen.

**Kein Force-Push auf `main`, keine umgeschriebene Historie.** Die 24 Links in `HOW.md` und `claims.csv` von PR `#91` zeigen auf den Commit `da59460e9b5c1d1ac235a5f484454352bca77cbe`. Die Dateien dürfen sich auf `main` weiterentwickeln; der Commit muss erreichbar bleiben.

## 4. Regeln von Justus aus der Übergabe an mich (gelten nach meinem Verständnis weiter; im Zweifel ihn fragen)

- Aussagen von Gemini und Antigravity nicht ungeprüft übernehmen. Erfolgschancen sind kein Entscheidungsgrund.
- Nichts nach außen ohne ausdrückliche Freigabe in seinen Worten: keine PRs, Issues, Kommentare, Mails außerhalb seines Repos. Antworten an den Maintainer werden entworfen, er sendet. Ein „Go“ von Gemini ist keine Freigabe.
- Eigene Änderungen nur auf einem Branch mit Pull Request; er mergt.
- Vor jeder Suche: Positivkontrolle in derselben Struktur, Abbruchkriterium, Obergrenze an Rechenzeit. Negativbefunde mit Belegart; nur „vollständig durchgerechnet“ und „Gegenbeispiel je Fall“ schließen etwas aus.
- Bei jeder Prüfung für `ca-tools` beide Werkzeuge: `tools/check_submission.py` (mit `--constant-rows-minutes 0.05`) und `tools/consistency.py --check --pr`.
- Bei Repo-Änderungen: Eintrag in `docs/RUN_LOG.md`, `STATUS.md`, am Ende der Antwort der `HANDOVER`-Block nach `RULES.md` §5.
- Stil: Deutsch, du, kurz, Ergebnis zuerst, Widerspruch statt Bestätigung. Er liest am Handy und ist kein Programmierer: keine Befehle für ihn. Uhrzeiten in deutscher Zeit.
- Sein Kriterium für Einreichungen: nichts einreichen, was absehbar schnell überholt wird; der Maintainer soll so wenig Arbeit wie möglich haben.
- Der Schreibzugriff auf `Justus42/ca-tools` und die Erlaubnis zum Push galten für diesen einen Schritt in meinem Chat. Für dich gilt wieder: kein Push dorthin ohne neue Freigabe.

## 5. Was ich an Technik gelernt habe (spart dir Zeit)

**Dieses Repo**
- `gh pr create` scheitert (GraphQL 403). Es geht über `gh api repos/Justus42/Math_Gemini_Antigravity/pulls -f title=… -f head=… -f base=main -F body=@datei`.
- Justus mergt normal (Merge-Commit). Wenn Links auf einen Branch-Commit zeigen, „kein Squash“ dazuschreiben.
- Laufen zwei PRs parallel, gibt es Konflikte in `STATUS.md` und `docs/RUN_LOG.md`. Entweder aufeinander aufbauen und die Reihenfolge nennen, oder warten.
- Uhrzeiten vor dem Hinschreiben mit `date` prüfen. Ich habe mich in dieser Sitzung viermal verschätzt und musste berichtigen.

**ca-tools lesen**
- Kein API-Zugriff auf `chrispbsmolen/ca-tools`. `git fetch` und `git ls-remote` über einen zweiten Remote gehen und reichen für `main`, Tabellendateien und `refs/pull/N/head`.
- Die PR-Seite ließ sich nur lesen, nachdem Justus die Adresse geschickt hatte; vorher zweimal Ratenlimit.

**ca-tools einreichen**
- Grenzen: Array-Datei höchstens 50 MiB, alle Dateien einer Einreichung zusammen höchstens 200 MiB (`submissions/README.md`, „Size limits“). Über die GitHub-Webseite gehen nur 25 MiB je Datei, also per git.
- Größere Arrays können extern bleiben (`external.csv`, öffentliche Ablage wie Zenodo oder GitHub-Release); sie zählen nicht gegen die 200 MiB und werden nach dem Merge geprüft.
- Regel 5: Name, Affiliation und E-Mail gehören in den **PR-Text** (oder per Mail an den Maintainer). Ich hatte das im Entwurf vergessen; Justus hat es nachgetragen. Zeile: `Justus Jeserigk, Independent researcher, j.jeserigk.dev@outlook.de. The arrays are released under CC BY 4.0.`
- `HOW.md` nur mit vollständigen, an einen Commit gebundenen Links. Relative Pfade liest `consistency.py` als Pfade im Tabellen-Repo (Fehlschlag bei PR `#88`).
- `source_detail` wird wörtlich in die Tabelle übernommen: jede Datei nennen, die der Befehl braucht (`phase7_lift.py` importiert `gen_general_tqv.py`).
- `builds_on` mit Kennungen aus `table/references.csv`; für Neues `new <Link>`. Der Bericht vermerkt dann je Zeile, dass der Maintainer die neue Methode vor dem Merge bestätigt.
- Push eines Branches auf den Fork aus einem flachen Klon: Basis mit begrenzter Tiefe von `upstream` holen, dann `git -c push.negotiate=true push`. 190 MiB gingen in einem Zug durch.
- **Zeitbudget der automatischen Prüfung:** 15 Minuten je Array, 300 Minuten für den ganzen PR. Die Verifikation selbst brauchte Sekunden bis eine Minute je Array. Teuer ist die Zusatzrechnung „constant rows“ mit bis zu 10 Minuten je Array: bei 8 der 37 Arrays ausgeschöpft (`N` zwischen etwa 5.800 und 21.000), größere Arrays brechen dort früh am Speicherlimit ab. Gesamt 88,8 Minuten. Ist das Gesamtbudget verbraucht, fallen die restlichen Zeilen mit „not checked: total time budget exhausted“ durch. Ein Paket mit vielen Arrays in diesem Größenbereich vorher überschlagen.
- Lokal mit `--constant-rows-minutes 0.05` dauert `check_submission.py` für die 37 Arrays 6 bis 10 Minuten, `consistency.py --check --pr` 4 bis 7 Minuten (2 Kerne, beide gleichzeitig).

## 6. Offene Punkte aus meinem Chat

1. **Tabelleneintrag der 37 Zeilen** bei `ca-tools` abwarten und in `STATUS.md` nachtragen (Commit, Zeit). Stand 01:25 MEZ: noch nicht eingetragen.
2. **Lauf „Consistency“** bei PR `#91` habe ich nie gesehen. Der Merge spricht dafür, dass er bestanden hat; belegt ist es nicht.
3. **Quelle der 4375** bei `(5, 7, 5)` (Li–Ji–Yin 2009 oder Ji–Li–Yin 2012) ungelesen, Bezahlschranke. In `HOW.md` als offen benannt.
4. **Zenodo:** Bai Version 1.0 (30.10.), Sitjar v1.10 (13.11.), abgerufen am 26.11.; die Versionslisten der Seiten waren leer. Bais Begleit-Preprint `10.5281/zenodo.23787053` ungelesen. CKRS nur im Autoren-Preprint gelesen, Zeitschriftenfassung nicht abgeglichen.
5. **Aussage A, A' und §14.1** bleiben Belegart „Argument“ (zweimal von GPT-6.2 Sol gelesen, ohne Befund an der Kette).
6. **Negativkontrollen** mit `verify_independent.py` fehlen für sieben große Arrays aus PR `#31` (`#17`–`#23`); mit `ca_verify` liegen sie für alle 37 vor.
7. **Schreibzugriff** meines Chats auf `Justus42/ca-tools` kann Justus entziehen.
8. **Paket 2** (vier Zellen bis 50 MiB, die nicht mehr in die 200 MiB passten, und 36 größere) ist nicht eingereicht. Mit deinen Listen ist der Zuschnitt ohnehin neu zu rechnen.

## 7. Phase 8 aus Sicht des Prüfers

Grundlage sind nur deine vier Nachrichten, die Justus hier eingefügt hat. Notizen, Listen und Zip-Dateien habe ich nicht gesehen. **Nichts davon habe ich nachgerechnet**, bis auf die beiden Punkte unter 7.1.

### 7.1 Zwei Dinge, die ich an deinen Angaben nachgerechnet habe

**Die 13 betroffenen Zellen stimmen der Zahl nach:** `(3..6, 11, 9)` vier, `(3..5, 13, 11)` drei, `(3..5, 15, 13)` drei, dazu `(4, 19, 17)`, `(3, 21, 19)`, `(4, 21, 19)`. Alle 13 sind Teil von PR `#91`.

**Die Formel liefert im Tabellenbereich nicht die kleinsten Listen.** Eingesetzt wie in deiner dritten Nachricht (größtes erlaubtes `j`, ganzzahlig abgerundet):

| `q` | `q mod 4` | `j` | `q^2 + C(q,2)` | Formel | deine beste Liste | Formel `/ q^2` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 13 | 1 | 0 | 247 | 240 | 238 | 1,420 |
| 17 | 1 | 0 | 425 | 416 | 412 | 1,439 |
| 19 | 3 | 0 | 532 | 520 | 513 | 1,440 |
| 23 | 3 | 0 | 782 | 768 | 746 | 1,452 |
| 29 | 1 | 1 | 1247 | 1204 | 1190 | 1,432 |
| 31 | 3 | 1 | 1426 | 1376 | 1356 | 1,432 |
| 37 | 1 | 2 | 2035 | 1944 | 1942 | 1,420 |
| 43 | 3 | 2 | 2752 | 2640 | – | 1,428 |

Der Grenzwert `17/12` passt zur Formel. Aber bei jedem `q` bis 37 liegt die Formel über deiner besten Liste, bei `q = 19` sogar über der Liste vom Vortag (520 gegen 517). Für die Tabelle (`v <= 25`, praktisch `q <= 23`) kommt der Gewinn also aus den vom Löser gewählten Klassen, nicht aus der Formel. Falls ich `j` oder die Fallunterscheidung falsch gelesen habe, zeigt das diese Tabelle sofort. Für eine Einreichung heißt das: Entweder die Listen sind Löserlisten (dann gilt wieder „Optimalität offen“ und die Frage, wie schnell sie überholt werden), oder die geschlossene Form wird bis in den Tabellenbereich hinein so gut wie die Listen.

### 7.2 Was am Gate fehlt, bevor etwas nach außen geht

1. **Ins Repo.** Notizen, Listen und Skripte per Branch und Pull Request, mit `RUN_LOG`-Einträgen je Lauf (Löser, Version, Seed, Zeitlimit, Maschine). Solange der Stand an Dateianhängen hängt, kann ihn niemand prüfen.
2. **Nachbau aus der Beschreibung**, nicht aus deinen Skripten (dein eigener Vorschlag; ich halte ihn für richtig). Für Primzahl-`q` steht `scripts/pruefer/nachbau.py` mit eigener Körperarithmetik bereit, dazu `zaehler.c`.
3. **Dual-Verifikation aller Arrays, die eingereicht werden sollen**, auch `t = 5, 6`. Bisher nennst du `t = 3, 4` mit `ca_verify`, `verify_independent.py` nur teilweise, Negativkontrollen nur für `q = 9, 11, 13`.
4. **Belegart je Aussage sauber trennen.** „Als Zählung stimmt die Formel für alle Primzahlen von 13 bis 520“ ist eine nachgerechnete Zählung, kein Beleg, dass die Listen existieren. Gebaut und geprüft sind nach deiner Angabe `q = 19, 31, 43`. Die zwei nicht ausgeschriebenen Beweisstücke sind „Argument“, der Grenzwert `7/5` ist Vermutung.
5. **Literaturprüfung** zu Rédei-Mengen, Richtungen und blockierenden Mengen in Verbindung mit Covering Arrays. Du nennst selbst CKRS im Original und Bais Begleitpapier als ungelesen. Dazu Bruen, Rédei, Blokhuis (Richtungen, blockierende Mengen in `PG(2, p)`) als Quellen für die verwendeten Schranken, zuerst genannt. Die Herkunftsreihenfolge aus `HOW.md` von PR `#91` bleibt die Basis.
6. **Fremdprüfung des Arguments** durch ein unbeteiligtes Modell oder formal. Über Justus' Bridge (`ask_openrouter`, GPT-6.2 Sol) hat das zweimal je etwa 0,10 US-$ gekostet; `save_to` legt den Wortlaut unter `docs/openrouter/` ab.
7. **Prüfer.** Du hast die Bauart gebaut, also nicht du. Ich würde einen frischen Chat nehmen: Dieser hier ist sehr lang, und jeder Werkzeugaufruf schleppt alles mit.

### 7.3 Zur nächsten Einreichung

- Sie ersetzt 13 eigene Tabellenzeilen, die seit einer Stunde gemergt sind. Das ist nach `RULES.md` zulässig, widerspricht aber Justus' Kriterium, wenn danach gleich die nächste Runde kommt. Deshalb **eine** Einreichung, und erst, wenn feststeht, ob die geschlossene Form oder die Löserlisten das Ende der Bauart sind.
- In `HOW.md` offen sagen, dass eigene Zeilen aus PR `#91` ersetzt werden, und warum.
- Regel 7 („bis zum Prüfbericht keine weitere Meldung zur selben Bauart“) ist mit Bericht und Merge von PR `#91` erfüllt.
- Vor dem Zuschnitt den Tabellenstand neu holen: seit `e673ab4` gab es am 26./27.11. fünf neue Stände (`4effb7a`, `808945f`, Merge von `#91` und `#92`, `f682ba3`). Keiner berührt bisher unsere Zellen, aber die 37 Zeilen kommen noch hinzu, und danach ist der Vergleichswert an 13 Zellen unser eigener.

## 8. Arbeitsstände meines Chats, die nicht im Repo liegen

Nichts, was gebraucht wird. Alle Prüfergebnisse stehen in `docs/RUN_LOG.md` (Einträge `P7-PRUEFUNG-PR34`, `P7-STAGE-37-KORR`, `P7-STAGE-37-GEMINI`, `P7-EINREICHUNG-PUSH`, `P7-EINREICHUNG-PR91`, `P7-EINREICHUNG-PR91-BERICHT`, `P7-EINREICHUNG-PR91-MERGE`) und in den Prüfvermerken. Meine Arbeitsverzeichnisse verfallen mit der Sitzung.
