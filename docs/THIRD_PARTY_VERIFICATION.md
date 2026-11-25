# Unabhängige Drittprüfung (`docs/THIRD_PARTY_VERIFICATION.md`)

Stand: **2026-11-25** | Prüfvermerk gemäß [`RULES.md`](../RULES.md) Abschnitt *Meldung nach außen*, Punkt 2d.

## 1. Prüfinstanz & Umfang

- **Unabhängige Prüfinstanz:** Externes Sprachmodell (Claude / „Fable“), unbeteiligt an Solver-Implementierung und Suchläufen (die mit Gemini / Google Antigravity durchgeführt wurden).
- **Prüfdatum:** 2026-11-25.
- **Prüfumfang:** Alle **16 Array-Dateien** in `results/` (darunter sämtliche **13 Pareto-Front-Arrays** in `submission/ca_tools_staging/` sowie die 3 projizierten Begleitdateien) samt [`results/SHA256SUMS`](../results/SHA256SUMS).

## 2. Durchgeführte Prüfungen & Befunde

1. **Offizieller C-Verifier (`ca_verify`):** Alle 16 Arrays bestanden mit Exit-Code `0`.
2. **Eigenes drittes Verifier-Programm (unabhängig neu implementiert):**
   - Alle 16 Arrays in `results/` als gültige Covering Arrays `CA(N; 3, k, v)` bestätigt (0 ungedeckte 3-Tupel über sämtliche $\binom{k}{3}$ Spaltentripel).
   - **Negativkontrolle:** Eine verkürzte Kopie (Zeile entfernt) wurde vom dritten Verifier korrekt zurückgewiesen.
3. **SHA-256-Integrität:** Alle `32/32` Prüfsummen in `results/SHA256SUMS` (16 Array-Dateien + 16 `.ccl.bin`-Startmatrizen) bestätigt.
4. **Tabellenvergleich (`chrispbsmolen/ca-tools` @ `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a`):** Alle 23 abgedeckten `(3, k, v)`-Zellen als strikt kleiner als `ca-tools` @ `7b08aef` (einschließlich abgeleiteter Größen in `table/derived.csv`) bestätigt.

## 3. Zusammenfassung (Punkt 2d)

Die Voraussetzung nach `RULES.md` Abschnitt *Meldung nach außen*, Punkt 2d (Nachrechnung aller Arrays durch ein drittes unabhängiges Programm / unbeteiligtes Modell zusätzlich zu `verifiers/ca_verify` und `verifiers/verify_independent.py`) ist für das vorliegende 13-Array-Einreichungspaket **erfüllt**.
