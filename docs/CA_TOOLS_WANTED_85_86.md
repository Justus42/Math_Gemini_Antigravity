# Auswertung `chrispbsmolen/ca-tools` Issues #85 & #86 (`docs/CA_TOOLS_WANTED_85_86.md`)

Stand: **2026-11-25** | Branch: `exp/phase5-recon` | Datenbasis: `chrispbsmolen/ca-tools` @ Commit `083a0933e3561625b2aad9bd19035ad76d783f03` (`2026-11-25T13:32:06Z`), rein lesend per `gh api` abgerufen (kein Schreibzugriff auf Fremd-Repos; `PR #88` unverändert).
Hardware-Bezug: Intel Xeon @ 2.30 GHz, **2 vCPUs**, **7,8 GiB RAM** (`7,3 GiB` verfügbar).
Verifier-Kalibrierung (aus realen Dual-Verifikationen in [`STATUS.md`](../STATUS.md)):
- `verifiers/ca_verify` (C, AVX2, 2 Threads): ca. `5,0e8` Plane-Row-Operationen/s (`0,451 s` auf `CA(18240; 3, 38, 20)`).
- `verifiers/verify_independent.py` (Python, 1 Thread, Flaschenhals unter `RULES.md`-Dual-Verifikation): ca. `4,5e6` Row-Tupel/s bei `t=3` (`33,373 s` auf `153,9M` Row-Tupeln), konservativ `3,5e6` bei `t=4` und `2,8e6` bei `t=5`.

---

## 1. Issue #85 — „Wanted: arrays at six published sizes“

- **Quelle:** `https://github.com/chrispbsmolen/ca-tools/issues/85`
- **Status / Metadaten:** `open`, Autor `chrispbsmolen`, erstellt `2026-11-24T00:31:36Z`, aktualisiert `2026-11-24T08:00:43Z`, **0 Kommentare**.
- **Anliegen:** Sechs publizierte binäre `t = 5`-Größen aus den Colbourn-Tabellen (Stand Nov. 2024, `SBSTT (TJ-AG)`, in `lexicon.csv` unter Familie `twoStage`) sind in `ca-tools` aktuell nur als `CITED` hinterlegt. Ein Array mit gleicher Zeilenanzahl `N` wechselt den Status auf `VERIFIED`; ein strikt kleineres `N` verbessert den Tabellenstand.
- **Governance-Hinweis (`submissions/README.md` Regel 6):** Alle sechs Zellen standen früher im R-Paket `CAs` (`TJ2level_CAs`) und wurden in `table/withdrawn_files.csv` zurückgezogen (*„no public source other than the CAs package“*). Zurückgezogene Arrays dürfen **weder** eingereicht **noch** als Start- oder Teil-Array verwendet werden (`check_submission.py` prüft gegen `withdrawn_fingerprints.csv`).

### 1.1 Extrahierte Parameter, aktueller Tabellenstand (`083a093`) & 2-vCPU-Machbarkeit

| `(t, k, v)` | Gesuchtes `N` (`ca_table`/`ca_frame`) | `N / 2^5` | `derived.csv` | Kleinstes verif. Array in `ca-tools` (`wanted.csv`) | Bewiesene Untergrenze (`lower_bounds.csv`) | `C(k,5)·2^5` (Tupel) | `C(k,5)·N` | Geschätzte Dual-Verif. (`ca` / `py`) | Speicherbedarf (Solver / Datei) | Methode vs. Suche & nüchterne Bewertung |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| **`(5, 20, 2)`** | **99** (`CITED`, `S1`) | `3,09×` | — | `126` (`k=28` Z63-Zirkulant) | `72` (`2·CAN(4,19,2)`) | `496.128` | `1,53M` | `<0,01 s` / `~0,6 s` | `<5 MB` / `4 KB` | **Offene Suche (schwer):** +10-Sprung zu `k=21 (109)`, nur +1 Zeile über verif. `k=17 (98)` (`Z_2^4`-Orbit); unstrukturierte SA vermutlich eng, eher zyklische/komplement-symmetrische oder Gruppen-Ansätze nötig |
| **`(5, 21, 2)`** | **109** (`CITED`, `S1`) | `3,41×` | — | `126` | `72` | `651.168` | `2,22M` | `<0,01 s` / `~0,8 s` | `<6 MB` / `5 KB` | **Offene Suche (mittel):** `109` liegt 17 Zeilen unter dem verif. `CA(126; 5, 28, 2)` (erlaubter nicht-zurückgezogener Startpunkt via Spaltenprojektion + Row-Deletion-SA/Tabu) |
| **`(5, 22, 2)`** | **111** (`CITED`, `S1`) | `3,47×` | — | `126` | `72` | `842.688` | `2,92M` | `<0,01 s` / `~1,1 s` | `<8 MB` / `5 KB` | **Offene Suche (mittel):** 15 Zeilen unter `CA(126; 5, 28, 2)`; binäre Deckungstabelle passt vollständig in L2/L3-Cache |
| **`(5, 23, 2)`** | **114** (`CITED`, `S1`) | `3,56×` | — | `126` | `72` | `1.076.768` | `3,84M` | `<0,01 s` / `~1,4 s` | `<10 MB` / `5 KB` | **Offene Suche (gut machbar):** 12 Zeilen unter `CA(126; 5, 28, 2)`; sehr hoher Züge/s-Durchsatz in `std`-only Rust (Bit-Parallelität auf `u64`/`u128`) |
| **`(5, 24, 2)`** | **117** (`CITED`, `S1`) | `3,66×` | — | `126` | `72` | `1.360.128` | `4,97M` | `<0,01 s` / `~1,8 s` | `<12 MB` / `6 KB` | **Offene Suche (gut machbar):** nur 9 Zeilen unter `CA(126; 5, 28, 2)`; realistischer Einstiegskandidat für Row-Deletion + Tabu/PAWS/SA |
| **`(5, 25, 2)`** | **118** (`CITED`, `S1`) | `3,69×` | — | `126` | `72` | `1.700.160` | `6,27M` | `<0,02 s` / `~2,2 s` | `<15 MB` / `6 KB` | **Offene Suche (gut machbar):** nur 8 Zeilen unter `CA(126; 5, 28, 2)`; zudem direkt oberhalb des `k=20..25`-Blocks und vollständig unabhängig von Regel 7 (`PGL(2,q)+CCL`) |

*(Kontext Nachbarzellen in `ca_frame.csv` @ `083a093`: `k=16: N=96` und `k=17: N=98` sind `VERIFIED` über `Z_2^4`-XOR-Orbits [Smolen, 2026-11-08/10]; `k=18..19` besitzen keine eigene Zeile und fallen per Stair-Step auf `k=20: N=99`; `k=26..28: N=126` ist `VERIFIED` als komplement-verdoppelter Frobenius-invarianter `Z_63`-Zirkulant [Smolen, 2026-11-13].)*

### 1.2 Fazit Issue #85
- **Verifier- & RAM-Last:** Auf 2 vCPUs vernachlässigbar (`< 2,5 s` Dual-Verifikation, `< 15 MB` RAM für einen binären `u8`-Zählervektor über alle `C(k,5)·32` Tupel).
- **Methodik & Abgrenzung:** Rein binäres `t = 5`-Problem, vollständig unabhängig von `PGL(2,q)+CCL` auf `t = 3` (keine Berührung mit der Regel-7-Sperre). Ein legitimer, regelkonformer Pilotstart für `k = 25 (118)` und `k = 24 (117)` ist die Projektion des öffentlich in `ca-tools` verifizierten `CA(126; 5, 28, 2)` (nicht in `withdrawn_files.csv`) mit anschließender Row-Deletion-Suche (SA/Tabu/PAWS) oder komplement-symmetrischer Suche. Ein Treffer `<= 118` bei `k = 25` wäre unmittelbar prüf- und einreichungsfähig.

---

## 2. Issue #86 — „Wanted: arrays for the sizes the table can only cite“

- **Quelle:** `https://github.com/chrispbsmolen/ca-tools/issues/86`
- **Status / Metadaten:** `open`, Autor `chrispbsmolen`, erstellt `2026-11-24T00:31:37Z`, aktualisiert `2026-11-24T07:59:11Z`, **0 Kommentare**.
- **Anliegen:** Allgemeine Suchliste für alle `CITED`-Einträge ohne hinterlegtes Array. Jedes Array, das `best_N` erreicht, überführt die Zelle in `VERIFIED`; ein kleineres `N` verbessert den Tabellenstand.
- **Abgleich Issue-Text vs. Live-Stand (`083a093`):**
  - Issue-Text (`2026-11-24`): `15.856` Zeilen gesamt (`2.031` mit Array, `13.825` nur zitiert).
  - Live `table/ca_table.csv.gz` (`083a093`, `2026-11-25`): **`16.052` Zeilen** (`2.045 VERIFIED`, `13.944 CITED`, `57 SCREENED`, `3 DISPUTED`, `3 FAILED_PENDING_RECHECK`).
  - **Wichtige Bereinigung über `table/ca_frame.csv` (`9.734` Pareto-Zellen):** Von den `8.620` als `CITED` geführten Pareto-Zellen besitzen `661` bereits ein abrufbares Artefakt (`499 file`, `99 deposit`, `62 construction`, `1 certificate` — darunter z. B. Bush-OAs und Kleitman-Spencer-Katona `t=2, v=2`). Die tatsächlich offenen Pareto-Zellen ohne Array/Zertifikat sind **`7.959` Zellen (`tier=CITED, get=none`)**.
  - Abgleich `table/wanted.csv` (`14.297` Zellen): `6.964` `no_array`, `4.167` `array_above_best`, `3.166` `beat_best`.

### 2.1 Aufschlüsselung der `7.959` offenen `CITED`-Zellen (`ca_frame.csv`, `get=none`) nach 2-vCPU-Machbarkeit

Klassifikation anhand der kalibrierten Dual-Verifikationszeit auf 2 vCPUs (`est_ca_s + est_py_s`):
- **`dual <= 15 s`** (`C(k,t)·N <= 5e7`) und **`dual 15–60 s`** (`5e7 < C(k,t)·N <= 2e8`): zusammen **`1.433` Zellen** im realistischen 2-vCPU-Budget.
- **`C-only <= 60 s`** (`2e8 < C(k,t)·N <= 2e9`): `ca_verify` schnell, aber `verify_independent.py` dauert `> 60 s` (`224` Zellen).
- **`heavy` / `k > 500`**: `6.302` Zellen (unpraktikabel für direkte Array-Verifikation auf 2 vCPUs; dort dominieren CPHF-/SCPHF-/DP-Zertifikate).

| Stärke `t` | Offene `CITED` (`get=none`) | `dual <= 15 s` | `dual 15–60 s` | Summe `dual <= 60 s` | `C-only` (`py > 60 s`) | `heavy` / `k > 500` | Dominante Familien im `<= 60 s`-Fenster |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `t = 2` | `3.038` | `820` | `92` | **`912`** | `0` | `2.126` | `dpGeneralized`, `dpCA`, `pcaCA`, `annealing`, `CS_LCDST` |
| `t = 3` | `1.060` | `187` | `59` | **`246`** | `55` | `759` | `SCA_Busht` (fuse), `CK_doublingCA`, `projection`, `TJ` |
| `t = 4` | `831` | `98` | `48` | **`146`** | `76` | `609` | `cphfCA`, `scphfCA`, `SCA_Busht` (fuse), `augmentOA` |
| `t = 5` | `1.195` | `47` | `21` | **`68`** | `53` | `1.074` | `twoStage` (u. a. Issue #85), `cphfCA`, `scphfCA`, `transversalDesign` |
| `t = 6` | `1.740` | `19` | `8` | **`27`** | `28` | `1.685` | `cphfCA`, `scphfCA`, `TJ`, `transversalDesign` |
| `t = 7..10` | `95` | `27` | `7` | **`34`** | `12` | `49` | `v = 2` kleine `k` (`CITED` Spezial-/Zyklotomie-Konstruktionen) |
| **Gesamt** | **`7.959`** | **`1.198`** | **`235`** | **`1.433`** | **`224`** | **`6.302`** | — |

### 2.2 Repräsentative `<= 60 s`-Klassen in Issue #86 (bekannte Methode vs. offene Suche)

Alle Einträge strikt außerhalb der Regel-7-Bauart (`PGL(2,q)+CCL` auf `t=3`):

| Kategorie / Typische Zellen `(t, k, v, N)` | `C(k,t)·v^t` | Geschätzte Dual-Verif. | RAM | Bekannte Methode vs. offene Suche | Nüchterne Einschätzung (2 vCPUs) |
| --- | :---: | :---: | :---: | --- | --- |
| **Deterministische / strukturierte Reproduktion (`t=2, v=10`):** z. B. `CA(100;2,4,10)` (`OA`), `CA(102;2,6,10)` (`ITD`) | `600–1.500` | `<0,02 s` | `<1 MB` | **Bekannte Methode** (MOLS / unvollständige Transversaldesigns) | Schnell reproduzierbar für `CITED→VERIFIED`-Tie, aber kein neues Bestmaß (`N` teils optimal) |
| **Kleine `t=2`-Metaheuristik:** `CA(37;2,4,6)`, `CA(39;2,5,6)`, `CA(41;2,6,6)`, `CA(22;2,9,4)`, `CA(35;2,9,5)` | `216–900` | `<0,02 s` | `<1 MB` | **Offene Reproduktion** (Cohen SA / Nurmela Tabu / LCDST) | Verifikation und Suche trivial klein; für `CITED→VERIFIED` gut erreichbar, strikte Unterbietung eher unwahrscheinlich (eng an Untergrenzen) |
| **Kleine `t=3`-Metaheuristik (`v=3,4,6`):** `CA(290;3,7,6)`, `CA(301;3,8,6)`, `CA(45;3,14,3)`, `CA(110;3,11,4)` | `7,6k–14k` | `<0,05 s` | `<2 MB` | **Offene Suche** (Torres-Jimenez / Cover-Starter) | Sehr billig auf 2 vCPUs; `v=6, k=7,8` direkt angreifbar, allerdings sehr enge Schranken (`1,34–1,39× v^3`) |
| **`t=4` CPHF/SCPHF auf Primzahlpotenzen (`v=3,4,5,7,8,9,11,13`):** z. B. `CA(384;4,7,4)`, `CA(159;4,11,3)`, `CA(4459;4,10..15,7)`, `CA(7680;4,11..15,8)`, `CA(12393;4,12..17,9)` | `9k–15,6M` | `0,01–9 s` | `5–80 MB` | **Konstruktionssuche** (CPHF / 3-Restricted SCPHF / lineare Cosets / Polynome) | **Hoch attraktiv:** sowohl `CITED→VERIFIED`-Schließung als auch echte Unterbietung oberhalb der Bush-Breite möglich (Details siehe [`docs/TARGET_SCAN_t4.md`](TARGET_SCAN_t4.md)) |
| **`t=4` Nicht-Primzahlpotenzen (`v=10,12,14`):** z. B. `CA(23889;4,14,10)`, `CA(27233;4,15,10)`, `CA(54923;4,16..18,12)` | `10M–37,7M` | `7–30 s` | `40–250 MB` | **Offene Suche / CPHF-Fuse / Gruppen-Orbits** | Unberührte 2026-Nischen mit großen Sprüngen (`2,39–2,79× v^4`), noch im `<= 60 s`-Dual-Verif.-Fenster |
| **`t=5` & `t=6` kleine Primzahlpotenzen (`v=2,3,4`):** z. B. Issue #85 (`t=5, v=2, k=20..25`), `CA(1408;5,7,4)`, `CA(483;5,12,3)`, `CA(1134;6,8,3)`, `CA(5632;6,8,4)` | `20k–1,7M` | `0,02–2,5 s` | `5–30 MB` | **CPHF-Suche** (`t=5,6, v=3,4`) bzw. **binäre SA/Tabu** (`t=5, v=2`) | Verifikation extrem schnell; `CPHF(n; k, q, t)`-Suche für `t=5,6` auf `q=3,4` hat sehr kleinen Suchraum |

### 2.3 Zusammenfassende Bewertung für Phase 5
1. **Unmittelbarster Einzel-Track aus Issues #85/#86:** **Issue #85 (`t=5, v=2, k=20..25`)** — explizit vom Maintainer priorisiert, `< 2,5 s` Dual-Verifikation, `< 15 MB` RAM, und für `k = 21..25` existiert mit dem verifizierten `CA(126; 5, 28, 2)` ein regelkonformer Startpunkt.
2. **Breitester struktureller Hebel aus Issue #86:** **`t = 4` CPHF/SCPHF & Nicht-Primzahlpotenzen (`v = 4, 5, 7, 8, 9, 10, 11, 12`)** — systematisch quantifiziert in [`docs/TARGET_SCAN_t4.md`](TARGET_SCAN_t4.md).
3. **Hinweis zu `DISPUTED` / `FAILED_PENDING_RECHECK` in `ca_table.csv.gz`:** Bei Commit `083a093` existieren 3 `FAILED_PENDING_RECHECK`-Zeilen (`t=5, v=3, k=7,8,28`, Dimensionsabweichung in `S5`) und 3 `DISPUTED`-Zeilen (`t=3, v=6,20,21`, große `k`). Diese sind beim Tabellenabgleich auszuschließen (wird in [`scripts/scan_t4_targets.py`](../scripts/scan_t4_targets.py) strikt umgesetzt).
