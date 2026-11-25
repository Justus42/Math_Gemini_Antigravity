# Drittprüfungs-Vermerk `t = 4 NEAR_BUSH` (`docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`)

- **Stand:** `2026-11-25`
- **Geprüfter Stand:** Commit `98d7a43` (Head von PR `#17`, `exp/phase5b2c-q11-q13-nearbush`; gemergt in `main` als `ca637a6`).
- **Prüfer:** unabhängiges Prüfmodell „Claude/Fable“, ausgeführt auf der Maschine des Drittprüfers (nicht in diesem Container).
- **Bezug:** Punkt 2d der Checkliste `RULES.md` („Meldung nach außen“). Dieser Vermerk betrifft ausschließlich `t = 4`; der Drittprüfungs-Vermerk zu PR `#88` (`docs/THIRD_PARTY_VERIFICATION.md`) bleibt unverändert und unberührt.
- **Hinweis:** Alle Befunde in Abschnitt 1 und 2 sind **Angaben des Drittprüfers**. Sie wurden hier nicht erneut durch den Drittprüfer erzeugt, sondern als Mitteilung übernommen. Die eigene Reproduktion in diesem Repo steht getrennt in [`results/t4_nearbush/VERIFICATION_LOG_t4_nearbush.md`](../results/t4_nearbush/VERIFICATION_LOG_t4_nearbush.md).

---

## 1. Gültigkeit der Arrays (Angabe des Drittprüfers)

Alle `10` lokalen `t = 4`-Arrays in `results/t4_nearbush/` @ `98d7a43` wurden vom Drittprüfer mit `4` unabhängigen Verifikationsprogrammen geprüft und als gültige Covering Arrays bestätigt:

| Gruppe | Dateien |
| --- | --- |
| `5` ältere Zwischenstände (Phase 5B-2A/2B) | `CA_3479_4_9_7.txt`, `CA_5888_4_10_8.txt`, `CA_7070_4_11_8.txt`, `CA_7561_4_11_8.txt`, `CA_9639_4_11_9.txt` |
| `5` neue Arrays aus PR `#17` (Phase 5B-2C) | `CA_3430_4_9_7.txt`, `CA_7056_4_11_8.txt`, `CA_9558_4_11_9.txt`, `CA_21900_4_13_11.txt`, `CA_42722_4_15_13.txt` |

## 2. Fremd-Reproduktion auf der Maschine des Drittprüfers (Angabe des Drittprüfers)

| Array | Fremd-Reproduktion byte-identisch | Methode |
| --- | :---: | --- |
| `CA(3430; 4, 9, 7)` | **bestätigt** | `t4_postop --threads 1 --target-n 3430` |
| `CA(9558; 4, 11, 9)` | **bestätigt** | `t4_postop --threads 1 --target-n 9558` |
| `CA(21900; 4, 13, 11)` | **bestätigt** | `t4_postop --threads 1 --target-n 21900` |
| `CA(7056; 4, 11, 8)` | **offen** | — |
| `CA(42722; 4, 15, 13)` | **offen** | — |
| `CA(5888; 4, 10, 8)` | nicht gesondert gemeldet | rein deterministischer Generator, keine Suche |

## 3. Offene Punkte

1. **Fremd-Reproduktion** von `CA(7056; 4, 11, 8)` und `CA(42722; 4, 15, 13)` auf einer anderen Maschine (Befehle mit festem `--target-n` siehe [`VERIFICATION_LOG_t4_nearbush.md`](../results/t4_nearbush/VERIFICATION_LOG_t4_nearbush.md)).
2. **Nachvollzug der Schranken-Argumente** in [`docs/T4_ODD_Q_NEAR_BUSH.md`](T4_ODD_Q_NEAR_BUSH.md) §8.2 (Anzahl entfernbarer `q^2`-Slices, Einzel-Symbol-Schranke, Parabel-Restklassen).
3. **Externe Literaturprüfung** außerhalb des Containers (arXiv / Colbourn / Zenodo), siehe [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) Abschnitt 6.

Solange diese Punkte offen sind, gilt Punkt 2d der Checkliste für `t = 4` als **nicht abgeschlossen**. Eine Meldung nach außen ist ohnehin gesperrt, bis PR `#88` vom Maintainer entschieden ist (Regel 7).
