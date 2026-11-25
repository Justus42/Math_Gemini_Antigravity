# Projektregeln & Governance (`RULES.md`)

Diese Regeln gelten verbindlich ab Abschluss von Phase 1 für alle weiteren Phasen, Skripte und Such-Agenten.

## 1. Integrität der Verifier (`verifiers/` ist READ-ONLY)

- Nach dem Phase-1-Commit auf `main` ist das Verzeichnis [`verifiers/`](verifiers/) **strikt READ-ONLY** für alle Such-Agenten.
- Änderungen an `verifiers/ca_verify.c`, `verifiers/verify_independent.py`, `verifiers/test_verifiers.py` oder `verifiers/SHA256SUMS` sind in Such-Branches verboten (das Binary `verifiers/ca_verify` wird lokal aus `verifiers/ca_verify.c` kompiliert und ist nicht versioniert).
- **Pflicht-Check vor jedem Audit / jeder Ergebnisabnahme:**
  ```bash
  sha256sum -c verifiers/SHA256SUMS
  ```
  Zusätzlich sind `git diff main -- verifiers/` (muss leer sein) und `python3 verifiers/test_verifiers.py` nachzuweisen.

## 2. Kanonisches Array-Format

Jede Kandidaten- und Baseline-Datei muss folgendes Format exakt einhalten:
- UTF-8-Klartext, genau `N` Zeilen (keine Leerzeilen, keine Kommentarzeilen).
- Jede Zeile enthält genau `k` Leerzeichen-getrennte ganze Zahlen in Basis 10 aus `{0, 1, ..., v - 1}`.
- Keine negativen Zahlen, keine Fließkommazahlen, keine `1..v`-Verschiebung, keine Wildcards (`-`, `*`, `NA`, `x`).

## 3. Dual-Verification & Dokumentationspflicht

Ein Kandidat gilt **nur dann** als gültiges Covering Array `CA(N; t, k, v)`, wenn:
1. **Verifier 1 (offizieller C-Verifier):**
   `./verifiers/ca_verify <array_file> <t> <v>` mit **Exit-Code 0** abschließt.
2. **Verifier 2 (unabhängiger Python-Verifier):**
   `python3 verifiers/verify_independent.py <array_file> <t> <v> -n <N> -k <k>` mit **Exit-Code 0** abschließt.
3. **Dokumentation unter `results/`:**
   Jeder verifizierte Kandidat wird zusammen mit folgenden Artefakten abgelegt:
   - die kanonische Array-Datei (`CA_<N>_<t>_<k>_<v>.txt`),
   - der SHA-256-Hash (`sha256sum`),
   - das vollständige Verifikations-Log beider Verifier (Befehle, Exit-Codes, Zeitstempel, Laufzeiten),
   - Reproduktionsmetadaten (Git-Commit des Solvers, Parameter, Seed, Laufzeit/Checkpoints).

Kandidaten, die nur einen Verifier bestehen oder ohne SHA-256-Hash und Verifikations-Log vorliegen, gelten als **ungültig**.

## 4. Solver- & Branch-Workflow

- **Feature-Branches:** Jegliche Solver-Entwicklung und alle Suchläufe müssen auf einem dedizierten Feature-Branch stattfinden (z. B. `feat/<solver>-<cell>` oder `exp/<cell>-<run>`). Direkte Such-Commits auf `main` sind unzulässig.
- **Checkpointing (Pflicht):** Jeder Solver muss deterministisches/konsistentes Checkpointing für **5–20-Minuten-Läufe** unterstützen:
  - regelmäßiges Schreiben von Checkpoints (z. B. alle 60–120 s sowie bei jeder Verbesserung der Kostenfunktion / Zeilenanzahl),
  - sauberes Wiederaufsetzen (`--resume <checkpoint>`) ohne Verlust des besten bisher gefundenen Zustands.
- **Merge-Gate:** Ein Merge nach `main` erfolgt erst nach bestandener Dual-Verifikation, bestandener `verifiers/test_verifiers.py` und Freigabe.

## Meldung nach außen

1. Kein Agent öffnet Pull Requests, Issues, Mails oder Posts außerhalb dieses Repos. Jede Meldung braucht Justus' ausdrückliche Freigabe für genau dieses Paket.
2. Vor der Freigabe, je Meldung neu:
   a) Live-Tabelle am aktuellen Commit holen, jede Zelle gegen die relevanten Tabellen-Dateien (`table/ca_table.csv` / `table/ca_table.csv.gz`, `table/ca_frame.csv`, `table/derived.csv`) prüfen, Commit notieren.
   b) Offene Pull Requests und Issues des Ziels durchsehen.
   c) Literaturprüfung mit schriftlichem Prüfvermerk in `docs/`.
   d) Jedes Array von einem dritten Programm oder einem unbeteiligten Modell nachrechnen lassen, zusätzlich zu den beiden Verifiern.
   e) Arrays mit dokumentiertem Befehl aus den Startdateien neu erzeugen, SHA-256 vergleichen.
3. Nur Arrays einreichen, die keine andere eigene Datei dominiert (gleiches oder kleineres N bei mehr Spalten).
4. Wortwahl: "kleiner als die Tabelle am Commit X". "Rekord" und "neu" nur mit Beleg. Die Bauart mit ihrer Herkunft nennen, fremde Vorarbeit zuerst.
5. KI-Einsatz offenlegen: in `HOW.md` die Zeile `AI tools used: yes`, dazu die Werkzeuge (Gemini, Antigravity, Gegenprüfung durch Claude).
6. Form bei `ca-tools`: ein Ordner `submissions/<slug>/` mit `claims.csv` (Kopf: `t,v,k,N,file,source_detail,construction,builds_on,credit,notes`), den Array-Dateien und `HOW.md`. Sonst ändert der Pull Request nichts.
7. Nach der Meldung: Link, Datum und Commit in `STATUS.md`. Bis zum Prüfbericht des Ziels keine weiteren Meldungen zur selben Bauart. Fehler sofort selbst korrigieren.
8. Im Laufprotokoll zählt nur die Belegart. Wörter wie "heiß" oder "Near-Miss" sind kein Befund.

