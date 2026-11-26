# Drittprüfungs-Vermerk `t = 4 NEAR_BUSH` (`docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`)

- **Stand:** `2026-11-26`
- **Geprüfte Stände:**
  - `5` ältere Zwischenstände (Phase 5B-2A/2B): Commit **`6fc9b58`** (PR `#16`, gemergt als `104bf43`).
  - `5` neue Arrays aus Phase 5B-2C: Commit **`98d7a43`** (PR `#17`, gemergt als `ca637a6`).
  - `5` deterministische Arrays aus `scripts/gen_t4_minus3q2.py` (Phase 5E, PR `#21`, gemergt als `68c8402`): `3430`, `5888`, `9477`, `21296`, `41743` (davon `9477`, `21296`, `41743` in `results/t4_nearbush/`).
- **Prüfer:** unabhängiges Prüfmodell „Claude/Fable“, ausgeführt auf der Maschine des Drittprüfers (nicht in diesem Container).
- **Bezug:** Punkt 2d der Checkliste `RULES.md` („Meldung nach außen“). Dieser Vermerk betrifft `t = 4` (und dokumentiert die Prüfer-Stichproben zur Verallgemeinerung getrennt als Nicht-Repo-Artefakte); der Drittprüfungs-Vermerk zu PR `#88` (`docs/THIRD_PARTY_VERIFICATION.md`) bleibt unverändert und unberührt.
- **Hinweis:** Alle Befunde in Abschnitt 1, 2 und 3 sind **Angaben des Drittprüfers**. Sie wurden hier nicht erneut durch den Drittprüfer erzeugt, sondern als Mitteilung übernommen. Die eigene lokal deterministische Reproduktion steht getrennt in [`results/t4_nearbush/VERIFICATION_LOG.md`](../results/t4_nearbush/VERIFICATION_LOG.md) §7–§8.

---

## 1. Gültigkeit der Arrays (Angabe des Drittprüfers)

Alle `10` älteren lokalen `t = 4`-Arrays in `results/t4_nearbush/` (Phase 5B) sowie alle **`5/5`** deterministischen Arrays aus `scripts/gen_t4_minus3q2.py` (Phase 5E) wurden vom Drittprüfer mit **zwei Repo-Verifiern** (`ca_verify`, `verify_independent.py`) plus **zwei unabhängigen Programmen** (eigenes Prüfprogramm des Drittprüfers Claude/Fable + Verifier aus `ca-tools`, insgesamt `4` Programme) geprüft und als gültige Covering Arrays bestätigt:

| Gruppe | Geprüfter Commit / Stand | Dateien / Arrays |
| --- | :---: | --- |
| `5` ältere Zwischenstände (Phase 5B-2A/2B) | `6fc9b58` | `CA_3479_4_9_7.txt`, `CA_5888_4_10_8.txt`, `CA_7070_4_11_8.txt`, `CA_7561_4_11_8.txt`, `CA_9639_4_11_9.txt` |
| `5` neue Arrays aus PR `#17` (Phase 5B-2C) | `98d7a43` | `CA_3430_4_9_7.txt`, `CA_7056_4_11_8.txt`, `CA_9558_4_11_9.txt`, `CA_21900_4_13_11.txt`, `CA_42722_4_15_13.txt` |
| **`5/5` Arrays aus `gen_t4_minus3q2.py` (Phase 5E, PR `#21`, geprüft `2026-11-26`)** | `bc9cf65` / `68c8402` | `CA(3430; 4, 9, 7)`, `CA(5888; 4, 10, 8)` *(Scratch-Äquivalente)* sowie `CA_9477_4_11_9.txt`, `CA_21296_4_13_11.txt`, `CA_41743_4_15_13.txt` *(in `results/t4_nearbush/`)* |

## 2. Fremd-Reproduktion auf der Maschine des Drittprüfers (Angabe des Drittprüfers)

### 2.1 Phase-5B-Arrays (Stand `2026-11-25 23:46 CET`)

Auf einer zweiten Maschine **rechnerunabhängig bestätigt** sind alle **`6/6`** früheren Phase-5B-Pareto-Arrays (`5` mit `t4_postop --threads 1 --target-n`, `1` rein deterministischer Generator) sowie zusätzlich der historische Anker `CA(7561; 4, 11, 8)`:

| Array | Status auf zweiter Maschine | Methode / Laufzeit (Angabe Drittprüfer) |
| --- | :---: | --- |
| `CA(3430; 4, 9, 7)` | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 3430` |
| `CA(5888; 4, 10, 8)` | **rechnerunabhängig bestätigt** (byte-identisch) | `gen_t4_q8_nearbush.py --mode k10-polychrom` (zusätzlich mit exakt im Vermerk dokumentiertem Befehl neu erzeugt und bestätigt) |
| `CA(7561; 4, 11, 8)` *(historischer Anker, dominiert)* | **rechnerunabhängig bestätigt** (byte-identisch) | `gen_t4_q8_nearbush.py --mode k11-pencil` (zusätzlich mit exakt im Vermerk dokumentiertem Befehl neu erzeugt und bestätigt) |
| `CA(7056; 4, 11, 8)` | **rechnerunabhängig bestätigt** (byte-identisch, `2026-11-25 23:46 CET`) | `t4_postop --threads 1 --target-n 7056` (`60 s`) |
| `CA(9558; 4, 11, 9)` *(in Phase 5E abgelöst durch `9477`)* | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 9558` |
| `CA(21900; 4, 13, 11)` *(in Phase 5E abgelöst durch `21296`)* | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 21900` |
| `CA(42722; 4, 15, 13)` *(in Phase 5E abgelöst durch `41743`)* | **rechnerunabhängig bestätigt** (byte-identisch, `2026-11-25 23:46 CET`) | `t4_postop --threads 1 --target-n 42722` (`112 s`) |

### 2.2 Phase-5E-Arrays aus `gen_t4_minus3q2.py` (Angabe von Claude, `2026-11-26`)

| Array | Status auf zweiter Maschine | Methode / Befund (Angabe Drittprüfer) |
| --- | :---: | --- |
| `CA(3430; 4, 9, 7)` (`gen_t4_minus3q2.py`) | **gültig (4/4 Programme)**; unabhängiger Primzahl-Nachbau **byte-identisch** | `gen_t4_minus3q2.py --q 7` & unabhängiger Nachbau des Prüfers (Primzahl `q = 7`) |
| `CA(5888; 4, 10, 8)` (`gen_t4_minus3q2.py`) | **gültig (4/4 Programme)** | `gen_t4_minus3q2.py --q 8` |
| **`CA(9477; 4, 11, 9)`** (`results/t4_nearbush/CA_9477_4_11_9.txt`) | **rechnerunabhängig bestätigt** (byte-identisch auf zweiter Maschine, 4/4 Programme) | `gen_t4_minus3q2.py --q 9` |
| **`CA(21296; 4, 13, 11)`** (`results/t4_nearbush/CA_21296_4_13_11.txt`) | **rechnerunabhängig bestätigt** (byte-identisch auf zweiter Maschine, 4/4 Programme); unabhängiger Primzahl-Nachbau **byte-identisch** | `gen_t4_minus3q2.py --q 11` & unabhängiger Nachbau des Prüfers (Primzahl `q = 11`) |
| **`CA(41743; 4, 15, 13)`** (`results/t4_nearbush/CA_41743_4_15_13.txt`) | **rechnerunabhängig bestätigt** (byte-identisch auf zweiter Maschine, 4/4 Programme); unabhängiger Primzahl-Nachbau **byte-identisch** | `gen_t4_minus3q2.py --q 13` & unabhängiger Nachbau des Prüfers (Primzahl `q = 13`) |

## 3. Verallgemeinerungs-Stichproben des Prüfers (Angabe von Claude, `2026-11-26` — **Stichproben des Prüfers, keine Repo-Artefakte**)

> **Abgrenzung:** Die folgenden Stichproben wurden vom Drittprüfer eigenständig im Rahmen der Prüfung durchgeführt und sind **ausdrücklich Stichproben des Prüfers, keine Repo-Artefakte**. Eigene, deterministisch erzeugte und dual-verifizierte Repo-Artefakte für allgemeine `(t, q, v)` werden getrennt in Phase 6A (`docs/GENERAL_TQV_PROOF.md`, `docs/GENERAL_TQV_SCAN.md`, `results/general_tqv/`) aufgebaut.

- **Stärken-Stichproben (Stichproben des Prüfers, keine Repo-Artefakte):**
  - `t = 3` bei `q in {5, 7, 11, 13}`,
  - `t = 5` bei `q in {5, 7}`,
  - `t = 6` bei `q = 5`.
- **Alphabet-Einschränkung `v < q` (Stichproben des Prüfers, keine Repo-Artefakte):** `5` geprüfte Fälle mit `N = q^t + C(v, 2) * q^(t - 2)`.
- **Tabellen-Vorab-Zählung (Stichproben des Prüfers, keine Repo-Artefakte):** `56` Zellen unterhalb von `ca_frame.csv @ 0b79e3f` (eigener systematischer Scan gegen den aktuellen Tabellenstand siehe [`docs/GENERAL_TQV_SCAN.md`](GENERAL_TQV_SCAN.md)).

## 4. Offene Punkte

1. ~~**Fremd-Reproduktion** der Phase-5B-Arrays (`7056`, `42722`) und der Phase-5E-Arrays (`9477`, `21296`, `41743`)~~ — **erledigt** (`2026-11-25` / `2026-11-26`, alle abgelegten `t = 4`-Bestwerte auf zweiter Maschine byte-identisch bestätigt).
2. **Externe Literaturprüfung (Restliste & neue allgemeine Formel):** Offene Punkte aus [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) §8.2 (systematische arXiv-Suche 2023–2026, Primärliteratur-Volltexte, `tns-research` v1.7–v1.9) **sowie** vollständige externe Literaturprüfung speziell für die allgemeine Formel `N(t, q, v) = q^t + C(v, 2) * q^(t - 2)` bei `k = q + 2`.
3. **Drittprüfung neuer Phase-6A-Arrays (`results/general_tqv/`):** nach Abschluss von Phase 6A getrennt zu dokumentieren.

PR `#88` ist seit `2026-11-26T05:32:11Z` gemergt (`ca-tools @ 0b79e3f`, in die Tabelle übernommen am Commit `e673ab4`), womit die Regel-7-Sperre für `t = 3 PGL(2,q)+CCL` beendet ist. Für das gesamte `q^t + C(v, 2) q^(t - 2)`-Paket gilt eine **neue verbindliche externe Einreichungs-Sperre** bis zum Abschluss der externen Literaturprüfung und ausdrücklicher Freigabe durch Justus.

