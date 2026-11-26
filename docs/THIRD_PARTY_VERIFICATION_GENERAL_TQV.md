# Drittprüfungs-Vermerk `general_tqv` (`docs/THIRD_PARTY_VERIFICATION_GENERAL_TQV.md`)

- **Stand:** `2026-11-26` (Prüfbericht vom `2026-11-26, 07:48 CET`)
- **Geprüfter Stand:** PR `#22` (Branch `exp/phase6a-general-tqv`, Commit **`fff093c`**, gemergt in `main` als `9062018`)
- **Tabellen-Referenz:** `chrispbsmolen/ca-tools @ e673ab45758a3959710c662a34837f79f6add689` (`e673ab4`)
- **Prüfer:** unabhängiges Prüfmodell „Claude“, ausgeführt auf der Maschine des Drittprüfers (nicht in diesem Container).
- **Bezug:** Punkt 2d der Checkliste [`RULES.md`](../RULES.md) („Meldung nach außen“). Die bestehenden Drittprüfungs-Vermerke [`docs/THIRD_PARTY_VERIFICATION.md`](THIRD_PARTY_VERIFICATION.md) (PR `#88`) und [`docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`](THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md) (`t = 4 NEAR_BUSH`) bleiben unverändert.
- **Hinweis:** Alle nachfolgenden Prüfbefunde sind **Angaben des Drittprüfers (Claude)** und wurden hier als Mitteilung übernommen. Die eigene lokale Dual-Verifikation und 2×-Reproduktion stehen getrennt in [`results/general_tqv/VERIFICATION_LOG.md`](../results/general_tqv/VERIFICATION_LOG.md).

---

## 1. Prüfbefunde zu PR `#22` (`fff093c`, Angabe von Claude, `2026-11-26, 07:48 CET`)

| Prüfpunkt | Ergebnis (Angabe Drittprüfer) | Detail |
| --- | :---: | --- |
| **Fremd-Reproduktion `results/general_tqv/`** | **`12/12` byte-identisch** | Alle `12` Phase-6A-Arrays auf zweiter Maschine mit `scripts/gen_general_tqv.py` byte-identisch erzeugt (rechnerunabhängig bestätigt). |
| **Gültigkeit nach Verifiern** | **`12/12` gültig (3 Programme)**; **`10/12` `verify_independent.py`** | Alle `12/12` Arrays gültig nach `verifiers/ca_verify`, `ca-tools ca_verify` und eigenem Prüfprogramm des Drittprüfers; `verifiers/verify_independent.py` lief auf `10/12` Arrays (die zwei `t = 6`-Arrays `CA_168070_6_9_7.txt` und `CA_376832_6_10_8.txt` wurden dort nicht gelaufen). |
| **Negativkontrolle** | **`12/12 FAIL`** | Nach Zeilenentnahme melden die Prüfprogramme für alle `12/12` Arrays `FAIL`. |
| **Unabhängiger Nachbau (Primzahl-`q`)** | **`8/8` byte-identisch** | Alle `8` Primzahl-`q`-Arrays aus `results/general_tqv/` sind byte-identisch zum unabhängigen Nachbau des Drittprüfers. |
| **Randfall-Prüfung** | **`14/14` gültig** | `14` geprüfte Randfälle einschließlich `t = q + 1` und `t = q + 2` als gültige Covering Arrays bestätigt. |
| **Tabellen- und Scan-Abgleich (`@ e673ab4`)** | **`17/17` kleiner als Tabelle**; **Scan `56/56` bestätigt** | Alle `17/17` abgelegten Arrays (`12` aus `results/general_tqv/` + `5` aus `results/t4_nearbush/`) liegen strikt unter der Tabelle `ca-tools @ e673ab4`; der vollständige Scan mit `56` Treffern in [`docs/GENERAL_TQV_SCAN.md`](GENERAL_TQV_SCAN.md) wurde `56/56` bestätigt. |

---

## 2. Abgrenzung & offene Punkte

1. **Geprüfte Dateien (`results/general_tqv/`, Phase 6A):** Die `12` Dateien aus PR `#22` (`fff093c`) gelten auf Grundlage der Fremd-Reproduktion auf zweiter Maschine als **rechnerunabhängig bestätigt** (`12/12` byte-identisch, `12/12` gültig nach drei Programmen inkl. eigenem Programm des Prüfers; `verify_independent.py` wurde lokal auf `12/12` und beim Drittprüfer auf `10/12` ausgeführt).
2. **Neuere Dateien (Phase 6B-1 ff.):** Arrays, die nach PR `#22` in `results/general_tqv/` ergänzt werden, sind von diesem Prüfvermerk **nicht** abgedeckt und stehen bis zu einer eigenen Fremd-Reproduktion weiterhin als lokal deterministisch 2× byte-identisch aus.
3. **Externe Literaturprüfung & Einreichungs-Sperre:** Die externe Literaturprüfung zur allgemeinen Formel `q^t + C(v, 2) * q^(t - 2)` (siehe [`docs/LITERATURE_CHECK_T4_NEARBUSH.md`](LITERATURE_CHECK_T4_NEARBUSH.md) §8.2) ist noch nicht abgeschlossen. Die externe Einreichungs-Sperre für das gesamte `q^t + C(v, 2) * q^(t - 2)`-Paket bleibt aktiv.
