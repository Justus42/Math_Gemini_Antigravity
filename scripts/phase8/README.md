# Skripte zu Phase 8 (Claude, Phase-8-Chat, 2026-11-26/27)

Arbeitsstand, nicht aufgeräumt. Beschreibung der Bauart: `docs/phase8/NOTIZ_2_FORMEL.md` §2; Übersicht und Belegart: `docs/PHASE8_UEBERSICHT.md`. Alle Skripte im selben Verzeichnis starten (flache Importe). Braucht `ortools`.

- Listen bauen: `python3 paley.py Q J build` (Paare `±σ`), `python3 apex.py Q J LIMIT AUSGABE` (beliebige Steigungspaare durch einen Punkt), `python3 ls_pack2.py Q J LIMIT AUSGABE` (ohne gemeinsamen Punkt), `python3 skeleton.py 9 240 int AUSGABE` (`q = 9`).
- Zählen ohne Bauen: `python3 paley_scan.py`; `python3 paley_v.py Q V` (`v < q`).
- Prüfen: `python3 scripts/phase8/pruefe_listen.py ZAEHLER ARBEITSVERZEICHNIS` (aus dem Wurzelverzeichnis).

Die Läufe haben Zeitlimits und sind nicht bytegenau wiederholbar; maßgeblich sind die Listen in `data/phase8/`.

## Nachtrag 27.11.2026: Untergrenze und Baer-Gitter (`docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md`)

- `baer_gitter.py Q F [--out DATEI]`: Liste für Quadratzahl `Q`, `F` Vollgeraden-Symbole je Seite; std-only, ohne Löser, bytegenau wiederholbar. `baer_gitter.py Q --klasse` prüft eine einzelne Baer-Klasse.
- `untergrenze.py schranke Q ...` und `untergrenze.py listen DATEI ...`: Schranken `L(q)` (Satz U) und `L'(q)` (verschärft, Notiz 3 §2.4) und Lemma J an Listen; `listen` vergleicht seit dem 27.11., 10:20 MEZ mit `L'(q)`.
- `pruefe_baer.py ARBEITSVERZEICHNIS ZAEHLER Q:F:T[:py] ...` (aus dem Wurzelverzeichnis): Liste, Lift, Verifier, Negativkontrolle als Markdown-Zeile.
