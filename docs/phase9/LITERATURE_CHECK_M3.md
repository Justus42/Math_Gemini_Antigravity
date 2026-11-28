# Literaturprüfung (Regel 2c) — Phase 9 `M_3(R_3)` (`k = q + 3`, `3 <= t <= q`)

- **Stand:** 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, synchronisiert mit `origin/main @ 9558681`).
- **Gegenstand:** 3D-biaffines Nebenklassen-Modell `M_3(R_3)` (`k = q + 3`, `3 <= t <= q`, `|K_t^(3)| = q^(t-3)`), die deterministische `k`-Block-Familie (`scripts/phase9_m3_cyclic_opt.py`, `15/8 q^3`) sowie die **13 konkreten `<= 50 MiB`-PAWS-Zellen** (`q in {7, 8, 9, 11, 13}`, `t in {4, 5, 6}`, Seeds in `data/phase9_m3/R3_q*_fullbg3_opt_paws_m*.txt`).
- **Status & Rolle:** Kompakter Prüfvermerk nach [`RULES.md`](../../RULES.md) Regel 2c, aufbereitet für die unabhängige Prüfung durch Claude. **Kein Neuheitsanspruch, keine Außenwirkung, keine Ablage in `results/`.**
- **Belegdisziplin:** Jede Quelle ist ausdrücklich gekennzeichnet als `gelesene Primärquelle`, `Sekundärangabe (Bericht / Tabellenstand)` oder `ungeprüft / offen`; jede Zelle als `Dual-Verify PASS (in /tmp)` (`10` Zellen) oder `check_m3=0, CI ausstehend` (`3` Zellen).

---

## 1. Abgrenzung gegen bekannte `k = q + 3`-Konstruktionen

| Quelle | Einordnung / Inhalt für `k = q + 3` | Abgrenzung gegen `M_3(R_3)` | Belegart der Quelle |
|---|---|---|---|
| **Bush (1952)** | `OA(q^t; t, q + 1, q)` aus Polynomauswertung (`deg < t`) | Basis-Spalten `F_q` von `M_3(R_3)` | Standardvorarbeit (`ca-tools`) |
| **CKRS (2010), Lemma 3.3** | Nebenklassen-Lift über Bush-Code für `k = q + 2` (2 Zusatzspalten) | Direkte 2D-Vorarbeit; `M_3(R_3)` erweitert auf 3 Zusatzspalten `(a, b, c)` über `K_t^(3)` (`deg <= t - 4`, 3D-Inzidenz in `AG(3, q)`) | `gelesene Primärquelle` (Autoren-Preprint, vgl. [`LITERATURE_CHECK_PHASE7_VQ.md`](../LITERATURE_CHECK_PHASE7_VQ.md) §2.6) |
| **Bai (2026c)** — *Covering arrays from line-polychromatic colourings of affine planes*, `doi:10.5281/zenodo.23787051`, **`Theorem 6.2` & `Corollary 6.3`** | Fügt **2** freie Spalten (`k = q + 3`) über zwei gemeinsam surjektive 2D-linien-polychromatische Färbungen auf `AG(2, q)` plus Hilfs-Array `E = CA(N_E; t-1, q+2, v)` hinzu. Für `v = q` mit `c_1, c_2 <= floor(q/2)` ergibt sich führende Ordnung **`(9/4) q^t = 2,25 q^t`**; Tabellenrekord dort nur bei reduziertem Alphabet `CA(31587750; 6, 19, 14)` (`q = 16`, `v = 14`). | Keine 3D-biaffine Konstruktion in `AG(3, q)`; bei `v = q` liegt `(9/4) q^t` oberhalb von `2 q^t - q^(t-1)` und oberhalb der `13` PAWS-Zellen (`1,77–1,83 q^t`). Als direkte Vorarbeit für `k = q + 3` nennen. | `gelesene Primärquelle` (Volltext `Bai_covering_arrays_line_polychromatic.pdf` geprüft; vgl. auch [`LITERATURE_CHECK_PHASE8.md`](../LITERATURE_CHECK_PHASE8.md) §1, §2.2) |
| **Bai (2026c), `Theorem 7.2`** | Hyperoval-Bauart für `k = q + 2` / `q + 3` ausschließlich für **gerades `q`** und **`t = 3`** (`CAN(3, q+2, q) = q^3`) | Nicht anwendbar auf `t >= 4`; keine der `13` `M_3`-Zellen hat `t = 3`. | `gelesene Primärquelle` (wie oben) |
| **Bai (2026d), `Theorem 3.1` / `Cor. 3.3` & `Theorem 5.2`** (`doi:10.5281/zenodo.23787055`) | Elliptische Zweiblock-Arrays `CAN(t, #E(F_q), q) <= 2q^t - q^(t-1)` sowie Genus-2-Zweiblock-Arrays (`2q^t - q^(t-2)`) | Hält in `ca-tools @ b689967` **8 von 13** Vergleichszellen (`t = 5, 6` für `q = 7..13`, größere Spaltenzahl `k' = #E(F_q) >= q + 3`). Unsere `M_3`-Zellen liefern kleinere `N` bei `k = q + 3`, decken aber weniger Spalten als `#E(F_q)`. | **`Sekundärangabe (Bericht / Tabellenstand)`** (`ca-tools @ b689967` `table/ca_table.csv.gz` & `ca_frame.csv` geprüft; **Voll-PDF von Bai (2026d) nicht vollständig gelesen**) |
| **Torres-Jimenez & Izquierdo-Marquez (2024)** (*Mathematics* 12(12) 1908, Table 5) & **3-Restricted SCPHF RE (CL)** | `CPHF(2; 15, 7, 4)` (`N = 4459`) bzw. `3-Restricted SCPHF` (`2q^4 - q^3` für `q = 8, 9, 13`) | Hält in `ca-tools @ b689967` **4 von 13** Vergleichszellen (`t = 4`, `q = 7, 8, 9, 13`, größere Spaltenzahl `k' = 15..21`). | **`Sekundärangabe (Tabellenstand)`** (`ca-tools @ b689967`) |
| **OA-Fusion (`orthogonal array fuse fuse postop NCK`)** | Tabellenwert `N = 27544` an `(4, 14, 11)` | Hält **1 von 13** Vergleichszellen (`(4, 14, 11)`). | **`Sekundärangabe (Tabellenstand)`** (`ca-tools @ b689967`) |
| **Sitjar (2026, v1.4)** | Vereinigung von Nebenklassen eines linearen Codes (Lemma 1) | Allgemeiner Rahmen für die PAWS-Löserlisten; keine 3D-Light+Heavy-Bauart für `k = q + 3`. | `gelesene Primärquelle` (vgl. [`LITERATURE_CHECK_PHASE8.md`](../LITERATURE_CHECK_PHASE8.md) §1, §2.3) |

### Verbindliche Wortwahl-Grenze
- **Keine pauschale Asymptotik-Behauptung** über `CAN(t, q + 3, q) < 2q^t - q^(t-1)` für allgemeines `q`, solange die offenen Punkte `P1`–`P4` aus [`M3_REGEL2D_BRIEF.md`](M3_REGEL2D_BRIEF.md) (insbesondere `exh(q) = o(q^3)` für alle `q >= 7`) nicht analytisch bewiesen und nach Regel 2d geprüft sind.
- **Strenge Trennung:**
  1. **Deterministische `k`-Block-Familie** (`scripts/phase9_m3_cyclic_opt.py`): Rohformel `m_raw(q, 4) = (15/8) q^3 - (3/4) q^2`; numerisch `suff = 0` bis `q = 25` und `check_m3 = 0` bis `q = 17` (`Regel-2d offen`).
  2. **13 konkrete `<= 50 MiB`-PAWS-Zellen** (`q = 7..13`, `t = 4, 5, 6`): reine endliche Konstruktionsbelege (`kleiner als ca-tools @ b689967`), kein pauschaler Neuheits- oder Rekordanspruch.

---

## 2. Vollständiger Tabellenabgleich aller 13 `<= 50 MiB`-Zellen (`ca-tools @ b689967`)

Lokaler read-only Abgleich gegen **`chrispbsmolen/ca-tools @ b68996787557cb79153f2d0ca9640aa821c57e52`** (`2026-11-28T02:10:53Z`; `table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv`; kleinstes `N` über alle `k' >= k = q + 3`):

| `#` | Zelle `(t, k, v)` | Seed (`m`) | **`N_wir`** | `N_table` | `k_table` | **`Delta`** | Bauart in `ca-tools @ b689967` | Größe (MiB, `<= 50`) | Belegstatus |
|---:|---|---|---:|---:|---:|---:|---|---:|---|
| 1 | `(4, 10, 7)` | `m607` | **`4.249`** | `4.459` | `15` | **`-210`** | `CPHF(2; 15, 7, 4)` (Torres-Jimenez & Izquierdo-Marquez 2024) | `0,0810` | **`Dual-Verify PASS (in /tmp)`** |
| 2 | `(5, 10, 7)` | `m607` | **`29.743`** | `31.213` | `13` | **`-1.470`** | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `0,5673` | **`Dual-Verify PASS (in /tmp)`** |
| 3 | `(6, 10, 7)` | `m607` | **`208.201`** | `218.491` | `13` | **`-10.290`** | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `3,9711` | **`Dual-Verify PASS (in /tmp)`** |
| 4 | `(4, 11, 8)`\* | `m914` | **`7.312`** | `7.680` | `15` | **`-368`**\* | `3-Restricted SCPHF RE (CL)` | `0,1534` | **`Dual-Verify PASS (in /tmp)`**\* |
| 5 | `(5, 11, 8)` | `m914` | **`58.496`** | `61.440` | `14` | **`-2.944`** | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `1,2273` | **`Dual-Verify PASS (in /tmp)`** |
| 6 | `(6, 11, 8)` | `m914` | `467.968` | `491.520` | `14` | `-23.552` | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `~9,82` | `check_m3=0, CI ausstehend` |
| 7 | `(4, 12, 9)` | `m1319` | **`11.871`** | `12.393` | `17` | **`-522`** | `3-Restricted SCPHF RE (CL)` | `0,2717` | **`Dual-Verify PASS (in /tmp)`** |
| 8 | `(5, 12, 9)` | `m1319` | **`106.839`** | `111.537` | `16` | **`-4.698`** | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `2,4454` | **`Dual-Verify PASS (in /tmp)`** |
| 9 | `(6, 12, 9)` | `m1319` | `961.551` | `1.003.833` | `16` | `-42.282` | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `~22,01` | `check_m3=0, CI ausstehend` |
| 10 | `(4, 14, 11)` | `m2417` | **`26.587`** | `27.544` | `14` | **`-957`** | `orthogonal array fuse fuse postop NCK` | `0,7422` | **`Dual-Verify PASS (in /tmp)`** |
| 11 | `(5, 14, 11)` | `m2417` | **`292.457`** | `307.461` | `18` | **`-15.004`** | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `8,1646` | **`Dual-Verify PASS (in /tmp)`** |
| 12 | `(4, 16, 13)` | `m4026` | **`52.338`** | `54.925` | `21` | **`-2.587`** | `3-Restricted SCPHF RE (CL)` | `1,7814` | **`Dual-Verify PASS (in /tmp)`** |
| 13 | `(5, 16, 13)` | `m4026` | `680.394` | `714.025` | `21` | `-33.631` | `elliptic two-block array` (Bai 2026, `zenodo.23787055`) | `~23,16` | `check_m3=0, CI ausstehend` |

*\*Dominanzhinweis (Regel 3): Für `(4, 11, 8)` liegt lokal bereits `results/t4_nearbush/CA_7056_4_11_8.txt` (`7056 < 7312`) vor; diese Zelle ist kein Einreichungskandidat aus `M_3`.*
*(`q = 11, t = 6` [~94 MiB] und `q = 13, t = 6` [~301 MiB] überschreiten das `50 MiB`-Limit und sind ausgeschlossen.)*

---

## 3. Offene Restliste (`ungeprüft / offen`)

1. **`Bai (2026d)` Voll-PDF (`doi:10.5281/zenodo.23787055`):** Bisher nur über Tabellenmetadaten in `ca-tools @ b689967` und Sekundärangaben geprüft; Volltextprüfung steht aus (insbesondere mögliche Zusatzbemerkungen zu `k = q + 3` oder Genus-2-Varianten).
2. **`aadwyer/CA_Database` & Colbourn-/NIST-Vollabgleich:** Vollständiger Abgleich außerhalb von `ca-tools @ b689967` noch nicht durchgeführt.
3. **Erneuter Live-Regel-2a/2b-Abgleich vor jeder späteren Einreichung:** Vor Freigabe eines Einreichungspakets müssen `ca-tools` `main`, offene PRs und Issues tagesaktuell neu geprüft werden (`b689967` ist Stand `2026-11-28T02:10:53Z`).
4. **Regel-2d-Drittprüfung & CI-Lauf:** Unabhängige Prüfung von [`M3_REGEL2D_BRIEF.md`](M3_REGEL2D_BRIEF.md) (Satz 1–4, `k`-Block `15/8`, `H_2P`-Obstruktionen, `P1`–`P4`) sowie Ausführung von [`.github/workflows/verify-phase9-m3.yml`](../../.github/workflows/verify-phase9-m3.yml) für die `3` offenen `<= 50 MiB`-Zellen (`#6, #9, #13`) stehen aus.
