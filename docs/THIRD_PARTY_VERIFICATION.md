# Unabhängige Drittprüfung (`docs/THIRD_PARTY_VERIFICATION.md`)

Stand: **2026-11-25** | Prüfvermerk gemäß [`RULES.md`](../RULES.md) Abschnitt *Meldung nach außen*, Punkt 2d.

## 1. Prüfinstanz, Programm & Umfang

- **Unabhängige Prüfinstanz:** Externes Sprachmodell (Claude / Anthropic), unbeteiligt an Solver-Implementierung und Suchläufen (die mit Gemini / Google Antigravity durchgeführt wurden).
- **Drittes Verifier-Programm:** [`submission/third_check.py`](../submission/third_check.py) (unverändert archiviert, SHA-256 `2acd4477976d78e47869493b4ca4ed1170c79eebd47f49a66e97ee8e18387289`, teilt keinen Code mit `verifiers/ca_verify.c` oder `verifiers/verify_independent.py`; nutzt `numpy`, daher in der separaten Prüf-Umgebung ausgeführt und im Arbeits-Container unverändert auf saubere Syntax geprüft).
- **Prüfdatum:** 2026-11-25 (drei Prüfdurchgänge: Erstprüfung auf `results/`, Zweitprüfung auf `main @ 162d48f`, Nachprüfung auf eingereichtem PR #88 @ `66a9947`).

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

## 4. Nachtrag: Prüfung des eingereichten PR #88 (`chrispbsmolen/ca-tools#88`, 2026-11-25)

### 4a. Gegenprüfung durch Claude (Angabe von Claude, 2026-11-25)

- **Prüfgegenstand:** `https://github.com/chrispbsmolen/ca-tools/pull/88`, Head-Commit `66a9947c0d422b5ce30d551736a4befe84c474b1`, Basis-Commit `083a093`, Ordner `submissions/jeserigk-pgl-ccl-2026-11/` (`15` neue Dateien, sonst keine Änderung).
- **Befund (Angabe von Claude):**
  - `13/13` Arrays im PR sind **bytegleich** zu `submission/ca_tools_staging/`.
  - Lokaler Lauf von `tools/check_submission.py` am Stand `083a093` mit **`13/13` bestanden**.
- **Nicht geprüft / nicht gelesen (Angabe von Claude):** PR-Text und Bot-Bericht wurden von Claude nicht gesehen.

### 4b. Eigene Nur-Lese-Nachprüfung von PR #88 (Agent, 2026-11-25)

- **Methode:** Rein lesender Abruf via `git fetch --no-tags --depth 1 https://github.com/chrispbsmolen/ca-tools.git refs/pull/88/head` nach `/tmp/pr88_ro` sowie `gh api` (kein Schreibzugriff auf `chrispbsmolen/ca-tools` oder `Justus42/ca-tools`).
- **PR-Metadaten:** Eröffnet durch `Justus42` am `2026-11-25T14:44:16Z`, Status `open` (`draft: false`), Basis-Commit `083a0933e3561625b2aad9bd19035ad76d783f03`, Head-Commit `66a9947c0d422b5ce30d551736a4befe84c474b1` (`Justus42:submit/jeserigk-pgl-ccl-2026-11`), exakt `15` hinzugefügte Dateien (`additions: 121927`, `deletions: 0`), alle in `submissions/jeserigk-pgl-ccl-2026-11/`.
- **SHA-256-Abgleich:** Alle **`13/13` Arrays** aus `refs/pull/88/head` sind SHA-256-identisch zu [`results/SHA256SUMS`](../results/SHA256SUMS); alle **`15/15` Dateien** (inkl. `HOW.md` `f90540db0eddb458…` und `claims.csv` `d81bb439c7ccfcf6…`) sind byte-identisch zu `submission/ca_tools_staging/`.
- **PR-Text:** gelesen (`8281` Bytes; enthält `AI tools used: yes`, den Absatz `Extent of AI use:` und `Independent`).
- **Bot-Prüfbericht:** noch nicht vorhanden (`0` Issue-Kommentare, `0` Reviews, `0` Review-Kommentare; die drei GitHub-Actions-Läufe `Verify submission`, `Consistency` und `Tests` auf `66a9947` vom `2026-11-25T14:44:25Z` stehen auf `status: completed`, `conclusion: action_required` — warten auf Ersteinreicher-Freigabe durch den Maintainer; Bot-Prüfbericht daher noch nicht vorliegend / nicht gelesen).

## 5. Zusammenfassung (Punkt 2d)

Die Voraussetzung nach `RULES.md` Abschnitt *Meldung nach außen*, Punkt 2d (Nachrechnung aller Arrays durch ein drittes unabhängiges Programm / unbeteiligtes Modell zusätzlich zu `verifiers/ca_verify` und `verifiers/verify_independent.py`) ist für das eingereichte 13-Array-Paket (`chrispbsmolen/ca-tools#88`) **erfüllt**.

