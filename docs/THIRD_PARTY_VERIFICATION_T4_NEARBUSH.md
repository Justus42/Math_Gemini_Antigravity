# Drittprüfungs-Vermerk `t = 4 NEAR_BUSH` (`docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`)

- **Stand:** `2026-11-25`
- **Geprüfte Stände:**
  - `5` ältere Zwischenstände (Phase 5B-2A/2B): Commit **`6fc9b58`** (PR `#16`, gemergt als `104bf43`).
  - `5` neue Arrays aus Phase 5B-2C: Commit **`98d7a43`** (PR `#17`, gemergt als `ca637a6`).
- **Prüfer:** unabhängiges Prüfmodell „Claude/Fable“, ausgeführt auf der Maschine des Drittprüfers (nicht in diesem Container).
- **Bezug:** Punkt 2d der Checkliste `RULES.md` („Meldung nach außen“). Dieser Vermerk betrifft ausschließlich `t = 4`; der Drittprüfungs-Vermerk zu PR `#88` (`docs/THIRD_PARTY_VERIFICATION.md`) bleibt unverändert und unberührt.
- **Hinweis:** Alle Befunde in Abschnitt 1 und 2 sind **Angaben des Drittprüfers**. Sie wurden hier nicht erneut durch den Drittprüfer erzeugt, sondern als Mitteilung übernommen. Die eigene lokal deterministische Reproduktion (2× byte-identisch mit `--target-n`, `--threads 1`) steht getrennt in [`results/t4_nearbush/VERIFICATION_LOG.md`](../results/t4_nearbush/VERIFICATION_LOG.md) §7.

---

## 1. Gültigkeit der Arrays (Angabe des Drittprüfers)

Alle `10` lokalen `t = 4`-Arrays in `results/t4_nearbush/` wurden vom Drittprüfer mit **zwei Repo-Verifiern** (`ca_verify`, `verify_independent.py`) plus **zwei unabhängigen Programmen** (eigenes Prüfprogramm des Drittprüfers Claude/Fable + Verifier aus `ca-tools`) geprüft und als gültige Covering Arrays bestätigt:

| Gruppe | Geprüfter Commit | Dateien |
| --- | :---: | --- |
| `5` ältere Zwischenstände (Phase 5B-2A/2B) | `6fc9b58` | `CA_3479_4_9_7.txt`, `CA_5888_4_10_8.txt`, `CA_7070_4_11_8.txt`, `CA_7561_4_11_8.txt`, `CA_9639_4_11_9.txt` |
| `5` neue Arrays aus PR `#17` (Phase 5B-2C) | `98d7a43` | `CA_3430_4_9_7.txt`, `CA_7056_4_11_8.txt`, `CA_9558_4_11_9.txt`, `CA_21900_4_13_11.txt`, `CA_42722_4_15_13.txt` |

## 2. Fremd-Reproduktion auf der Maschine des Drittprüfers (Angabe des Drittprüfers)

Auf einer zweiten Maschine **rechnerunabhängig bestätigt** sind bisher **`5`** Arrays (`3` mit `t4_postop --threads 1 --target-n`, `2` rein deterministische Generatoren); **`2`** Pareto-Best-Arrays sind noch offen:

| Array | Status auf zweiter Maschine | Methode |
| --- | :---: | --- |
| `CA(3430; 4, 9, 7)` | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 3430` |
| `CA(5888; 4, 10, 8)` | **rechnerunabhängig bestätigt** (byte-identisch) | `gen_t4_q8_nearbush.py --mode k10-polychrom` |
| `CA(7561; 4, 11, 8)` *(historischer Anker, dominiert)* | **rechnerunabhängig bestätigt** (byte-identisch) | `gen_t4_q8_nearbush.py --mode k11-pencil` |
| `CA(9558; 4, 11, 9)` | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 9558` |
| `CA(21900; 4, 13, 11)` | **rechnerunabhängig bestätigt** (byte-identisch) | `t4_postop --threads 1 --target-n 21900` |
| `CA(7056; 4, 11, 8)` | **offen** | — |
| `CA(42722; 4, 15, 13)` | **offen** | — |

## 3. Offene Punkte

1. **Fremd-Reproduktion** von `CA(7056; 4, 11, 8)` und `CA(42722; 4, 15, 13)` auf einer zweiten Maschine (Befehle mit festem `--target-n` siehe [`VERIFICATION_LOG.md`](../results/t4_nearbush/VERIFICATION_LOG.md) §7).
2. **Nachvollzug der Schranken-Argumente** in [`docs/T4_ODD_Q_NEAR_BUSH.md`](T4_ODD_Q_NEAR_BUSH.md) §8.2 (Anzahl entfernbarer `q^2`-Slices, Einzel-Symbol-Schranke, Parabel-Restklassen).
3. **Offene Restliste der externen Literaturprüfung** (neuere Zenodo-Versionen, systematische arXiv-Suche 2023–2026, Primärliteratur-Volltexte), siehe [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) Abschnitt 6.

Solange diese Punkte offen sind, gilt Punkt 2d der Checkliste für `t = 4` als **nicht abgeschlossen**. Eine Meldung nach außen ist ohnehin gesperrt, bis PR `#88` vom Maintainer entschieden ist (Regel 7).
