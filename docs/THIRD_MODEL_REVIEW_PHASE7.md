# Prüfung des Arguments durch ein unbeteiligtes Modell (`docs/THIRD_MODEL_REVIEW_PHASE7.md`)

- **Stand:** 2026-11-26, ca. 20:45 MEZ. **Verfasser dieses Vermerks:** Claude (Prüfer-Chat). Zwei Durchgänge: Der erste ist hier nur **zusammengefasst** (Wortlaut nicht archiviert). Der zweite liegt im Wortlaut vor: [`docs/openrouter/PHASE7_ARGUMENT_REVIEW_gpt-6.2-sol.md`](openrouter/PHASE7_ARGUMENT_REVIEW_gpt-6.2-sol.md) (von der Bridge unverändert abgelegt, Commit `dffec8d`).
- **Modell:** `openai/gpt-6.2-sol` über OpenRouter (Betreiber laut OpenRouter: OpenAI), Denkstufe `high`, Aufruf über Justus' Bridge am 26.11.2026 um 20:13 MEZ auf seine Anweisung.
- **Verbrauch:** Eingabe `20395` Tokens, Ausgabe `5095` (davon Denken `2965`); Kosten laut OpenRouter `0,10 US-$`.
- **Gelesen (Stand `main @ 666f767`):** `docs/PHASE7_T2_REDUCTION.md`, `scripts/phase7_reps_vq.py`, `scripts/phase7_lift.py`, `scripts/gen_general_tqv.py`.
- **Auftrag:** Fehler suchen in §2/§3 (Aussage A, Aussage B), §11.1 (Aussage A'), §14.1–§14.3 und in der Übereinstimmung von Text und Code; kleine Fälle von Hand; kein Urteil über Neuheit. Das Modell hat kein Programm ausgeführt.
- **Einordnung:** unbeteiligtes Modell (hat an Planung, Rechnung und Dokument nicht mitgewirkt). Es hat dasselbe Dokument gelesen wie die anderen; ein formaler Beweis ist das nicht.

## Erster Durchgang (20:13 MEZ): Urteile des Modells

| Glied | Urteil | Kern der Begründung |
| --- | --- | --- |
| (1) §2, §3 Aussage A mit Präzisierungen | korrekt | Zwei Auswertungsspalten legen `(c, d)` fest; bei `j = t-1` ist der nächste Koeffizient des Produkts `-sigma`, daher `c + sigma*d = u`; Fall `S = GF(q)` und `q = 2` von Hand nachvollzogen; `j = t-2` und die leeren Fälle bei `t = q+1`, `q+2` stimmen. |
| (2) §3 Aussage B | korrekt | Für Primzahl `q` durchlaufen die Summen der Translate einer `(t-1)`-Menge alle Werte; die Primzahlannahme ist nötig (in `GF(4)` hat keine Zweiermenge Summe null). |
| (3) §11.1 Aussage A' | korrekt | `pi` lässt die Zielsymbole fest; es werden genau die drei Bedingungen gebraucht. Hinweis zur Formulierung bei `u` (eingepflegt). |
| (4) §14.1–§14.3 | Bauformel und Nachweis korrekt; **ein Nebenfehler** | In §14.1 stand `C(2v - q, 2) < C(v, 2)` ohne `max`; für `2v < q` ist das nicht definiert bzw. falsch. Kein Gegenbeispiel zu einem Array. Fallunterscheidung für alle Paare `(s, m)` vollständig; auf jeder doppelt belegten Geraden bleiben `q - d >= 1` Punkte mit Grundbeschriftung; Handproben `(q, v) = (3,2), (4,2), (5,2), (4,3)`. |
| (5) Text und Code | Liste, Lift, Körperarithmetik stimmen; **ein Randfall** | `uncovered_pairs` brach bei leerer Vertreterliste mit `IndexError` ab; Bereichsprüfungen in `read_reps` waren `assert`s (unter `python -O` wirkungslos). |

## Vom Modell genannte stillschweigende Voraussetzungen

- Zeilen werden mit Vielfachheit gezählt; für `t > q` können gleiche Zeilen entstehen (Beispiel `q = v = 2`, `t = 4`).
- Vergleiche wie `c < d` und `min` betreffen nur die Nummern `0..q-1`, nicht eine Ordnung des Körpers.
- Der Paarzähler setzt gültige Beschriftungen voraus.

## Vom Modell nicht geprüft

Laufzeitverhalten der Skripte, Datei-Hashes, externe Listen und Verifier.

## Nachprüfung und Folgen (Prüfer)

- Beide Nebenfehler bestätigt und behoben: §14.1 jetzt mit `max(0, 2v - q)`; `scripts/phase7_lift.py` meldet leere Listen und ungültige Vertreter mit einer Fehlermeldung statt mit `IndexError` oder `assert`. Die Ausgabe für gültige Eingaben ist unverändert (SHA-256 für `(5, 7, 5)`, `(4, 11, 9)`, `(3, 13, 10)` geprüft).
- Die Voraussetzungen stehen jetzt in §14.1.
- Kein Befund betrifft ein Array, eine Blockzahl oder einen Tabellenvergleich.

## Zweiter Durchgang (20:22 MEZ, Wortlaut archiviert)

- Gelesen: der Stand **nach** den beiden Korrekturen (Branch `claude/phase7-drittmodell @ ac40205`), zusätzlich `docs/LITERATURE_CHECK_PHASE7_VQ.md`. Verbrauch: Eingabe `25722`, Ausgabe `6455` Tokens (davon Denken `3609`); Kosten laut OpenRouter `0,13 US-$`.
- Urteile: Glieder (1) bis (5) alle „korrekt“. Neu geprüft Glied (6), Einordnung gegen CKRS (2010) Lemma 3.3, auf Grundlage der Beschreibung in `docs/LITERATURE_CHECK_PHASE7_VQ.md` §2.6 (das Modell konnte die Originalarbeit nicht lesen): „korrekt“.
  - (6a) Die Liste `{(c, d, d, d) : (c, d) != (0, 0)} ∪ {(0, 0, x, y) : x != y}` erfüllt die Bedingungen und hat `q^2 + q(q-1) - 1` Vertreter, auch für `q = 2`.
  - (6b) Sie entspricht der beschriebenen Bauart von Lemma 3.3.
  - (6c) „Verfeinerung“ ist als Bezeichnung des gemeinsamen Bauprinzips sachgerecht. Irreführend wäre „Ausdünnung“ im Sinn einer Teilmenge des CKRS-Arrays. Bei `q = 2` gibt es keine echte Ersparnis (`5 = 5`).
- Weitere Hinweise: Die Vielfachheit von Zeilen gilt schon ab §2; die Nummern `0` und `1` müssen die Körpernull und -eins sein; `--check-m` prüft die Voraussetzung, nicht den Lift selbst; fehlende Kommandozeilen-Argumente wurden nicht abgefangen (behoben).
- Vom Modell nicht geprüft: CKRS im Original, Skriptläufe, Hashes, Verifier, Löserprotokolle, Tabellenvergleiche.

Gesamtkosten beider Durchgänge: `0,23 US-$`.
