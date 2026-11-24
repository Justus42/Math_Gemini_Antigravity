# Agent & Orchestrator Protocol (`AGENTS.md`)

Verbindliche Arbeitsregeln für alle Agenten und Suchläufe in diesem Repository.

## 1. Pflicht vor jeder Aktion
1. Lies zuerst [`STATUS.md`](STATUS.md) (aktuelle Ziel-Landkarte, aktive Gates, Abbruchkriterien) und [`RULES.md`](RULES.md) (Governance, Dual-Verifikation, Branch-Workflow).
2. `verifiers/` ist **strikt READ-ONLY**. Führe vor jeder Ergebnisabnahme `sha256sum -c verifiers/SHA256SUMS` und `git diff main -- verifiers/` (muss leer sein) aus.
3. Keine direkten Such-Commits auf `main`; arbeite auf einem dedizierten Feature-Branch. Keine externen Crates in `solvers/ca3_search` (`std`-only).

## 2. Pflicht nach jedem Suchlauf
Trage jeden abgeschlossenen Lauf **verbindlich** in [`docs/RUN_LOG.md`](docs/RUN_LOG.md) ein und aktualisiere [`STATUS.md`](STATUS.md) vor dem Commit (Ergebnisse niemals nur in `/tmp` belassen):
- Datum/Phase, Lauf-ID, Zielzelle `CA(N; t, k, v)`, Modus/Algorithmus, zentrale Parameter & Seed, Hardware (CPU/Threads), Zeitbudget/Laufzeit, Durchsatz (`moves/sec`), Bestwert (`unc` / Orbits), und **Belegart** (z. B. Dual-verifizierter Treffer, Positivkontrolle, oder Heuristische Suche erfolglos + konkrete Ursache).
- Verifizierte Kandidaten (`unc == 0`) erst nach bestandener Dual-Verifikation (`./verifiers/ca_verify` + `verify_independent.py`) samt SHA-256 und Log in `results/` ablegen.

## 3. Pflicht am Ende jeder Antwort (`HANDOVER`-Block)
Beende jede Antwort mit einem kompakten `HANDOVER`-Codeblock (**max. 25 Zeilen**), der exakt enthält:
- `branch` und letzter `commit`
- `target` + `live_record`
- die letzten 3 Einträge aus `docs/RUN_LOG.md`
- `gate_status` (Gate 0 / Gate 1 / Verifier-Status)
- genau **1** konkrete `decision_question` für den nächsten Schritt
