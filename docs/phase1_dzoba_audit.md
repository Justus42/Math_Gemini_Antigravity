# Phase-1-Audit: Gegenprüfung `dzoba/covering-arrays-2026` vs. `ca_table.csv`

- **Prüfdatum:** 2026-11-24
- **Quelle 1 (`ca_table.csv`):** `chrispbsmolen/ca-tools` (`table/ca_table.csv`), Commit `47596cf` (2026-11-24T13:57:37Z)
- **Quelle 2 (`dzoba`):** `dzoba/covering-arrays-2026` (`README.md`, `arrays/`), Commit `040a622` (2026-10-21T20:08:08Z)

## Vergleich der 5 angefragten Zellen

| Zelle `(t, k, v)` | Live-Wert `ca_table.csv` | Wert in `dzoba/covering-arrays-2026` | Neuerer ungemergter Wert? | Anmerkung |
| --- | :---: | :---: | :---: | --- |
| `(4, 9, 3)` | **135** (`VERIFIED` 2026-11-16 & `CITED` S1) | nicht verbessert (`k=9` bleibt 135) | **Nein** | In `dzoba` explizit unter *Not improved* gelistet |
| `(3, 9, 5)` | **185** (`VERIFIED` 2026-11-12 via `k=10` & `CITED` S1) | nicht verbessert (`k=9,10` bleibt 185) | **Nein** | In `dzoba` explizit unter *Not improved* gelistet |
| `(3, 9, 6)` | **361** (`VERIFIED` 2026-11-12 & `CITED` S1) | kein Eintrag | **Nein** | `dzoba` enthält keine `v=6`-Arrays |
| `(4, 12, 3)` | **189** (`CITED` S1, Torres-Jimenez) | kein Eintrag | **Nein** | `dzoba` enthält für `t=4, v=3` nur `k=8` |
| `(3, 11, 5)` | **225** (`VERIFIED` 2026-11-12 via `k=12` & `CITED` S1) | **218** (`arrays/CA_218_3_11_5.txt`) | **Ja (−7 Zeilen)** | Extension Lemma aus AGL(1,5)-`CA(185;3,10,5)` + 33-Zeilen-Block; noch nicht in `ca_table.csv` gemergt |

## Relevante ungemergte Nachbarzellen in `dzoba/covering-arrays-2026`

Obwohl unsere drei Pilot-Zielzellen `(4,9,3)`, `(3,9,5)` und `(3,9,6)` selbst nicht verbessert sind, liegen in `dzoba/covering-arrays-2026` zwei sehr relevante **ungemergte Bestwerte für direkte Nachbarn (`k = 8`)**:

| Nachbarzelle `(t, k, v)` | Live-Wert `ca_table.csv` | Ungemergter Wert in `dzoba` | Datei & Methode |
| --- | :---: | :---: | --- |
| `(4, 8, 3)` | 135 (via `k=9`) | **129** (−6 Zeilen) | `arrays/CA_129_4_8_3.txt` — AGL(1,3)-Entwicklung aus 21 Starter-Zeilen + 3 konstante Zeilen |
| `(3, 8, 5)` | 185 (via `k=10`; `k=7` ist 165 von Bai XunDi) | **165** (−20 Zeilen) | `arrays/CA_165_3_8_5.txt` — AGL(1,5)-Entwicklung aus 8 Starter-Zeilen + 5 konstante Zeilen |

Weitere Arrays in `dzoba/covering-arrays-2026` (nicht im Zielzellen-Fokus): `CA_165_3_7_5.txt`, `CA_476_3_10_7.txt`, `CA_556_3_11_7.txt`, `CA_633_3_12_7.txt`.
