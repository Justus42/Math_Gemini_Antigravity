# Unabhängige Drittprüfung (`docs/THIRD_PARTY_VERIFICATION.md`)

Stand: **2026-11-25** | Prüfvermerk gemäß [`RULES.md`](../RULES.md) Abschnitt *Meldung nach außen*, Punkt 2d.

## 1. Prüfinstanz, Programm & Umfang

- **Unabhängige Prüfinstanz:** Externes Sprachmodell (Claude / Anthropic), unbeteiligt an Solver-Implementierung und Suchläufen (die mit Gemini / Google Antigravity durchgeführt wurden).
- **Drittes Verifier-Programm:** [`submission/third_check.py`](../submission/third_check.py) (unverändert archiviert, SHA-256 `2acd4477976d78e47869493b4ca4ed1170c79eebd47f49a66e97ee8e18387289`, teilt keinen Code mit `verifiers/ca_verify.c` oder `verifiers/verify_independent.py`; nutzt `numpy`, daher in der separaten Prüf-Umgebung ausgeführt und im Arbeits-Container unverändert auf saubere Syntax geprüft).
- **Prüfdatum:** 2026-11-25 (zwei Prüfdurchgänge: Erstprüfung auf `results/`, Zweitprüfung auf `main @ 162d48f`).

## 2. Erste Drittprüfung (`results/`, 16 Arrays)

1. **Offizieller C-Verifier (`ca_verify`):** Alle 16 Arrays bestanden mit Exit-Code `0`.
2. **Eigenes drittes Verifier-Programm ([`submission/third_check.py`](../submission/third_check.py)):**
   - Alle 16 Arrays in `results/` als gültige Covering Arrays `CA(N; 3, k, v)` bestätigt (0 ungedeckte 3-Tupel über sämtliche $\binom{k}{3}$ Spaltentripel).
   - **Negativkontrolle:** Eine verkürzte Kopie (**70 Zeilen entfernt** / `70 rows removed`) wurde vom dritten Verifier korrekt zurückgewiesen.
3. **SHA-256-Integrität:** Alle `32/32` Prüfsummen in [`results/SHA256SUMS`](../results/SHA256SUMS) (16 Array-Dateien + 16 `.ccl.bin`-Startmatrizen) bestätigt.
4. **Tabellenvergleich (`chrispbsmolen/ca-tools` @ `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a`):** Alle 23 abgedeckten `(3, k, v)`-Zellen als strikt kleiner als `ca-tools` @ `7b08aef` (einschließlich abgeleiteter Größen in `table/derived.csv`) bestätigt.

## 3. Zweite Drittprüfung (`main @ 162d48f`, Staging-Paket & offizielles Prüfskript)

Am **2026-11-25** wurde das gemergte Repository (`main @ 162d48f`, PR #7) erneut vollständig unabhängig durch die externe Prüfinstanz (Claude / Anthropic) geprüft:

1. **Staging-Integrität:** Alle `13/13` Dateien in `submission/ca_tools_staging/` sind **byte-identisch** zu den entsprechenden Dateien in `results/`.
2. **Doppelte Verifikation inklusive drittem Verifier:** Alle `13/13` Staging-Arrays sind gültig unter `verifiers/ca_verify` und unter [`submission/third_check.py`](../submission/third_check.py).
3. **Bit-exakte Reproduktion aus frischem Build:** Alle `13/13` Arrays wurden aus einem frisch kompilierten `solvers/pgl_ccl_search` und den kompakten Binär-Startern in `data/ccl_binary/` **bit-identisch** (13/13 SHA-256-Treffer) reproduziert.
4. **Lokaler Lauf des offiziellen `ca-tools`-Prüfskripts:** Das Einreichungspaket bestand den lokalen Lauf des offiziellen `ca-tools`-Prüfskripts (`tools/check_submission.py`) mit **13/13 PASS** (alle 23 Zellen kleiner als `ca-tools @ 7b08aef`, 0 offene PRs).

## 4. Zusammenfassung (Punkt 2d)

Die Voraussetzung nach `RULES.md` Abschnitt *Meldung nach außen*, Punkt 2d (Nachrechnung aller Arrays durch ein drittes unabhängiges Programm / unbeteiligtes Modell zusätzlich zu `verifiers/ca_verify` und `verifiers/verify_independent.py`) ist für das vorliegende 13-Array-Einreichungspaket **erfüllt**.

