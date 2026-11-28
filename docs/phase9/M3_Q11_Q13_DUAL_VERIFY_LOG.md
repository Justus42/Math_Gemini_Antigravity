# Phase 9 — AP 1: Dual-Verifikation `q = 11, 13` (`t = 4`) & Abgleich `ca-tools @ b689967`

- **Datum:** 2026-11-28 UTC (Branch `exp/phase9-biaffine-3d`, PR `#54`, Basis `0d6e9f5`).
- **Hardware:** Intel Xeon CPU @ 2.30 GHz, 2 vCPU / 2 Threads, Python 3.12 (`std`-only), `gcc 13.3.0` (`-O3 -pthread`).
- **Verifier-Integrität:** `sha256sum -c verifiers/SHA256SUMS` `3/3 OK`, `git diff main -- verifiers/` leer, `python3 verifiers/test_verifiers.py` `23/23 PASS`.
- **Speicherhygiene & Governance:** Alle ausgerollten CA-Dateien ausschließlich in `/tmp/phase9_m3/` erzeugt und geprüft (nicht committet); keine Ablage in `results/`, keine Schreibvorgänge auf `ca-tools`, keine Außenwirkung.

---

## 1. Dual-Verifikation `q = 11` und `q = 13` (`t = 4`, in `/tmp/phase9_m3/`)

Beide kompakten `R_3`-Seeds in `data/phase9_m3/` (`SHA256SUMS` `17/17 OK`) wurden zunächst per [`scripts/phase9_m3_construct.py`](../../scripts/phase9_m3_construct.py) byte-identisch gegen die abgelegten Seeds nachgebaut, mit [`scripts/phase9_m3_lift.py`](../../scripts/phase9_m3_lift.py) (`--check-m3 --mode full-bg3`) exakt geprüft, `2×` byte-identisch nach `/tmp/phase9_m3/` geliftet und mit beiden unabhängigen Verifiern (`verifiers/ca_verify` und `verifiers/verify_independent.py`) jeweils positiv (`POS`) und negativ (`NEG`, letzte Zeile `N` entfernt) verifiziert.

| Parameter | `q = 11` (`k = 14`, `t = 4`) | `q = 13` (`k = 16`, `t = 4`) |
| --- | --- | --- |
| **Seed (`data/phase9_m3/`)** | `R3_q11_fullbg3_det_m2454.txt` (`m = 2.454`) | `R3_q13_fullbg3_det_m4088.txt` (`m = 4.088`) |
| **Seed SHA-256** | `f95ed1c305f6cb399f7697c2adedb7e6a2a864e9e7022ef3630240606f956ab5` | `fc2ecb6cbab5699670212d37c0ef968c75697dbf4a558f6c31d8867c091b113b` |
| **Seed-Repro (`construct.py`)** | `match = True` (`0,647 s`) | `match = True` (`1,369 s`) |
| **`check_m3(full-bg3)`** | **`0` Lücken** (`|D1|=121, |N2|=121`, `0,371 s`) | **`0` Lücken** (`|D1|=169, |N2|=169`, `0,871 s`) |
| **CA-Datei (`/tmp/phase9_m3/`)** | `CA_26994_4_14_11.txt` (`790.185 B` = `0,7536 MiB`) | `CA_53144_4_16_13.txt` (`1.896.856 B` = `1,8090 MiB`) |
| **CA SHA-256 (`2×` byte-identisch)** | `ee039374c0112e3febba1ec98367cc6307642da8f7e45a8fd133734489866767` | `548f15db41f34486fc28bea1258691f33ddb717dfeb80d3352935086195acd07` |
| **Lift-Laufzeit (Erst / Repro)** | `0,267 s` / `0,341 s` (`byte_identical = True`) | `0,727 s` / `0,578 s` (`byte_identical = True`) |
| **`verifiers/ca_verify` POS** | **`rc = 0`** (`0,086 s`, `1.001` 4-Sets, `14.641` Tupel) | **`rc = 0`** (`0,410 s`, `1.820` 4-Sets, `28.561` Tupel) |
| **`verifiers/ca_verify` NEG (`N-1`)** | **`rc = 1`** (`0,101 s`) | **`rc = 1`** (`0,334 s`) |
| **`verify_independent.py` POS** | **`rc = 0`** (`7,263 s`, `14.655.641` Interaktionen) | **`rc = 0`** (`38,869 s`, `51.981.020` Interaktionen) |
| **`verify_independent.py` NEG (`N-1`)** | **`rc = 1`** (`7,359 s`, `81/1.001` 4-Sets mit Lücken) | **`rc = 1`** (`35,691 s`, `246/1.820` 4-Sets mit Lücken) |
| **Vergleich `ca-tools @ b689967`** | **`26.994` < `27.544`** (**`-550`**) | **`53.144` < `54.925`** (**`-1.781`**) |
| **Gesamtergebnis** | **`Dual-Verify PASS` (Regel-2d offen)** | **`Dual-Verify PASS` (Regel-2d offen)** |

### Bonus-Check `check_m3(full-bg3) = 0` für `q = 16` und `q = 17` (ohne CA-Rollout)

Da beide `t = 4`-Dual-Verifikationen deutlich unter `2 min` lagen (`~16 s` bzw. `~78 s`), wurde zusätzlich `check_m3(full-bg3)` für `q = 16` und `q = 17` ohne CA-Rollout direkt geprüft:
- **`q = 16` (`k = 19`):** `r = 14`, `c_shift = 10`, `m_det = 7.653` (`1,8684 * q^3`, `-283` vs. `ell = 7.936`, `exh = 37`, Bauzeit `0,68 s`): `suff = 0`, **`check_m3(full-bg3) = 0`** (`|D1| = 256, |N2| = 256`, `1,78 s`).
- **`q = 17` (`k = 20`):** `r = 15`, `c_shift = 11`, `m_det = 9.182` (`1,8689 * q^3`, `-355` vs. `ell = 9.537`, `exh = 19`, Bauzeit `0,90 s`): `suff = 0`, **`check_m3(full-bg3) = 0`** (`|D1| = 289, |N2| = 289`, `2,35 s`).

---

## 2. Read-only Abgleich gegen `chrispbsmolen/ca-tools @ b689967` (`q = 7..19`, `t = 4, 5, 6`)

Geprüft wurden per rein lesendem `gh api`-Abruf am Commit `b68996787557cb79153f2d0ca9640aa821c57e52` (`2026-11-28T02:10:53Z`, `0` offene PRs) alle drei Tabellen-Dateien (`table/ca_frame.csv`, `table/ca_table.csv.gz`, `table/derived.csv`, jeweils kleinster Wert über alle $k' \ge k$).

| `q` | `k` | `t` | `N_det` (`m_det`) | `N_sol` (`m_sol`) | `ca-tools @ b689967` (`k'`) | `Delta_det` | `Delta_sol` | Belegstatus (`M_3` / Verifikation) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| `7` | `10` | `4` | `4.417` (`631`) | **`4.340`** (`620`) | `4.459` (`15`) | `-42` | **`-119`** | `m=620`: **`Dual-Verify PASS`** (`/tmp`); `m=631`: `check_m3=0` |
| `7` | `10` | `5` | `30.919` (`631`) | **`30.380`** (`620`) | `31.213` (`13`) | `-294` | **`-833`** | `m=620`: **`Dual-Verify PASS`** (`/tmp`); `m=631`: `check_m3=0` |
| `7` | `10` | `6` | `216.433` (`631`) | **`212.660`** (`620`) | `218.491` (`13`) | `-2.058` | **`-5.831`** | `m=620`: **`Dual-Verify PASS`** (`/tmp`); `m=631`: `check_m3=0` |
| `8` | `11` | `4` | `7.560` (`945`) | **`7.440`** (`930`) | `7.680` (`15`) | `-120` | **`-240`** | `m=930`: **`Dual-Verify PASS`** (`/tmp`; lokal `CA_7056` kleiner); `m=945`: `check_m3=0` |
| `8` | `11` | `5` | `60.480` (`945`) | **`59.520`** (`930`) | `61.440` (`14`) | `-960` | **`-1.920`** | `m=930`: **`Dual-Verify PASS`** (`/tmp`); `m=945`: `check_m3=0` |
| `8` | `11` | `6` | `483.840` (`945`) | `476.160` (`930`) | `491.520` (`14`) | `-7.680` | `-15.360` | Vorhersage (`check_m3=0` für `m=930, 945`) |
| `9` | `12` | `4` | `11.988` (`1.332`) | **`11.916`** (`1.324`) | `12.393` (`17`) | `-405` | **`-477`** | `m=1324`: **`Dual-Verify PASS`** (`/tmp`); `m=1332`: `check_m3=0` |
| `9` | `12` | `5` | `107.892` (`1.332`) | `107.244` (`1.324`) | `111.537` (`16`) | `-3.645` | `-4.293` | Vorhersage (`check_m3=0` für `m=1324, 1332`) |
| `9` | `12` | `6` | `971.028` (`1.332`) | `965.196` (`1.324`) | `1.003.833` (`16`) | `-32.805` | `-38.637` | Vorhersage (`check_m3=0` für `m=1324, 1332`) |
| **`11`** | **`14`** | **`4`** | **`26.994`** (`2.454`) | `—` | `27.544` (`14`) | **`-550`** | `—` | **`Dual-Verify PASS`** (`/tmp`, **neu in AP 1**; Regel-2d offen) |
| `11` | `14` | `5` | `296.934` (`2.454`) | `—` | `307.461` (`18`) | `-10.527` | `—` | Vorhersage (`check_m3=0`) |
| `11` | `14` | `6` | `3.266.274` (`2.454`) | `—` | `3.528.481` (`15`) | `-262.207` | `—` | Vorhersage (`check_m3=0`) |
| **`13`** | **`16`** | **`4`** | **`53.144`** (`4.088`) | `—` | `54.925` (`21`) | **`-1.781`** | `—` | **`Dual-Verify PASS`** (`/tmp`, **neu in AP 1**; Regel-2d offen) |
| `13` | `16` | `5` | `690.872` (`4.088`) | `—` | `714.025` (`21`) | `-23.153` | `—` | Vorhersage (`check_m3=0`) |
| `13` | `16` | `6` | `8.981.336` (`4.088`) | `—` | `9.651.421` (`16`) | `-670.085` | `—` | Vorhersage (`check_m3=0`) |
| `16` | `19` | `4` | `122.448` (`7.653`) | `—` | `113.866` (`19`) | `+8.582` | `—` | über Tabelle (`check_m3=0`, neu) |
| `16` | `19` | `5` | `1.959.168` (`7.653`) | `—` | `2.031.616` (`25`) | `-72.448` | `—` | Vorhersage (`check_m3=0`, neu) |
| `16` | `19` | `6` | `31.346.688` (`7.653`) | `—` | `33.554.416` (`23`) | `-2.207.728` | `—` | Vorhersage (`check_m3=0`, neu) |
| `17` | `20` | `4` | `156.094` (`9.182`) | `—` | `130.317` (`20`) | `+25.777` | `—` | über Tabelle (`check_m3=0`, neu) |
| `17` | `20` | `5` | `2.653.598` (`9.182`) | `—` | `2.476.095` (`20`) | `+177.503` | `—` | über Tabelle (`check_m3=0`, neu) |
| `17` | `20` | `6` | `45.111.166` (`9.182`) | `—` | `47.045.877` (`20`) | `-1.934.711` | `—` | Vorhersage (`check_m3=0`, neu) |
| `19` | `22` | `4` | `245.632` (`12.928`) | `—` | `253.783` (`28`) | `-8.151` | `—` | Vorhersage (`suff=0`, `check_m3` nicht gelaufen) |
| `19` | `22` | `5` | `4.667.008` (`12.928`) | `—` | `4.945.339` (`22`) | `-278.331` | `—` | Vorhersage (`suff=0`, `check_m3` nicht gelaufen) |
| `19` | `22` | `6` | `88.673.152` (`12.928`) | `—` | `94.091.743` (`30`) | `-5.418.591` | `—` | Vorhersage (`suff=0`, `check_m3` nicht gelaufen) |

**Bilanz gegen `ca-tools @ b689967`:**
- Für `q = 7, 8, 9, 11, 13` sind alle `15/15` Zellen (`t = 4, 5, 6`) kleiner als `ca-tools @ b689967` (`8` davon `Dual-Verify PASS` in `/tmp/phase9_m3/`, `7` Vorhersage mit `check_m3=0`).
- Inkl. `q = 16, 17, 19` liegen **21 Zellen** unter `ca-tools @ b689967` (`8` `Dual-Verify PASS`, `10` Vorhersage `check_m3=0`, `3` Vorhersage `suff=0`).
- **Regel-2d / Regel-2c:** Für alle Phase-9-Zellen stehen Drittprüfung (Regel 2d) und Literaturprüfung (Regel 2c) noch aus; keine Ablage in `results/`, keine Außenwirkung.
