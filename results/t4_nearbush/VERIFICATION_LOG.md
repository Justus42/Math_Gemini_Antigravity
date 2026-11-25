# Dual-Verification Log — Phase 5B-2A (`t = 4, v = 8` NEAR_BUSH)

- **Datum (UTC):** `2026-11-25`
- **Branch:** `exp/phase5b2a-q8-nearbush` (Basis: `origin/main` @ `56a3413`)
- **Live-Tabellenstand (`chrispbsmolen/ca-tools`):** Commit `c5f447da7f3efcc1b39cdea6340463ec7e90e006` (`2026-11-25T17:49:34Z`; geprüft gegen `table/ca_table.csv.gz`, `table/ca_frame.csv` und `table/derived.csv`, 0 offene PRs auf `t = 4`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, 2 vCPUs (2 Threads)
- **Verifier-Integrität:** `sha256sum -c verifiers/SHA256SUMS` 3/3 OK; `python3 verifiers/test_verifiers.py` 23/23 PASS; `git diff origin/main -- verifiers/` leer.
- **Einreichungsstatus:** Nur lokale Ablage unter `results/t4_nearbush/` (keine Meldung nach außen; PR `#88` und Checkliste `RULES.md` Punkt 2 bleiben vorrangig).

---

## 1. Übersicht der dual-verifizierten Arrays (`results/t4_nearbush/`)

Alle drei Dateien erfüllen das kanonische Array-Format (`RULES.md` §2) und bestehen beide unveränderten Verifier (`Exit-Code 0`).

| Datei (`results/t4_nearbush/`) | Zelle `(t, k, v)` | `N` | `ca-tools` @ `c5f447d` | Delta vs. `c5f447d` | Rolle (Regel 3) | SHA-256 |
| --- | :---: | :---: | :---: | :---: | --- | --- |
| `CA_5888_4_10_8.txt` | `(4, 10, 8)` | **5888** | `6101` (`VER`, Bai XunDi 2026) | **−213** | Pareto-Best (`k = 10`) | `7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` |
| `CA_7070_4_11_8.txt` | `(4, 11, 8)` | **7070** | `7680` (`CIT`, Colbourn–Lanús `k = 15`) | **−610** | Pareto-Best (`k = 11`) | `ae72c96e8a9b2a4cfd746b13614c8920125e9e52613890792176f44ec19c8b95` |
| `CA_7561_4_11_8.txt` | `(4, 11, 8)` | **7561** | `7680` (`CIT`, Colbourn–Lanús `k = 15`) | −119 | Deterministischer Phase-5B-1-Anker *(dominiert von `7070`; nicht einreichen)* | `821c23ea6852f7c77c55bbf5e8858c6c907a195aa2c418d20d231e00ce429fd2` |

### Herkunft & Vorarbeit (Regel 4)
- **Vorarbeit:** Bush (1952) für das orthogonale Array `OA(q^4; 4, q + 1, q)` und das `(q + 2)`-Hyperoval `OA(q^3; 3, q + 2, q)` über `GF(2^m)`; Jamison (1977) und Brouwer–Schrijver (1978) für affine Blocking-Sets der Mindestgröße `2q - 1` in `AG(2, q)`; Nurmela (2004) für Tabu-Search-Reparatur; Bai XunDi (2026) für die `poly2`-Geradenbüschel-Zerlegung sowie Row-Deletion + Tabu-Post-Optimierung.
- **Eigene Zusammensetzung:**
  - `CA_7561_4_11_8.txt`: Deterministische Hyperoval-Double-`poly2`-Konstruktion (`scripts/gen_t4_q8_nearbush.py --mode k11-pencil`).
  - `CA_5888_4_10_8.txt`: Projektion `Q(a, b, c, d) = (a ^ c ^ d, a ^ b ^ d)` entlang des irreduziblen quadratischen Polynoms `x^2 + x + 1` über `GF(8)` (jede Faser ist ein exaktes `OA(64; 2, 9, 8)`), kombiniert mit einer 4-polychromatischen Zerlegung von `AG(2, 8)` in vier disjunkte 15-Punkte-Blocking-Sets `{0..3}` plus vier Einzelpunkte `{4..7}` und Komplettierung durch `4 × 7` skalierte Hyperoval-Slices (`4096 + 4 · 448 = 5888`).
  - `CA_7070_4_11_8.txt`: Zwei balancierte 4-polychromatische `AG(2, 8)`-Färbungen + `3072` Hyperoval-Slices + `35` deterministische Reparaturzeilen (`CA(7203; 4, 11, 8)`), gefolgt von Zero-Dep-Rust Post-Optimierung (`solvers/t4_postop`: 0-Break-Don't-Care-Absorption, Row-Deletion, Focused-HD1-Tabu + PAWS) über zwei Läufe (`7203 → 7072 → 7070`).

---

## 2. Verifikations-Protokoll (Dual-Verification)

Ausgeführt am `2026-11-25` auf den abgelegten Dateien in `results/t4_nearbush/`:

### `results/t4_nearbush/CA_5888_4_10_8.txt`
- **Byte-identische Reproduktion (2 unabhängige Läufe):** `sha256 = 7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` (`0,038 s` / `0,034 s`, `cmp -s` PASS).
- **Befehl:** `python3 scripts/gen_t4_q8_nearbush.py --mode k10-polychrom --out results/t4_nearbush/CA_5888_4_10_8.txt`
- **Verifier 1 (`./verifiers/ca_verify results/t4_nearbush/CA_5888_4_10_8.txt 4 8`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=5888; t=4, k=10, v=8) - all 210 column sets fully cover all 4096 tuples` (`0,03 s`)
- **Verifier 2 (`python3 verifiers/verify_independent.py results/t4_nearbush/CA_5888_4_10_8.txt 4 8 -n 5888 -k 10`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=5888; t=4, k=10, v=8) - all 210 column sets cover all 4096 tuples (860160 total interactions) [elapsed: 0.3789s]`

### `results/t4_nearbush/CA_7070_4_11_8.txt`
- **Reproduktionskette (Multi-Thread-Post-Op):**
  1. Startarray `CA(7203; 4, 11, 8)` (`sha256: cb222f4828c3d843b167b58959f69c08dbd557f60f4146f57e8fbd6d67d7c68e`):
     `python3 scripts/gen_t4_q8_nearbush.py --mode k11-polychrom --out <start.txt>` (`0,099 s`, byte-identisch über 2 Läufe).
  2. Lauf `G1-A` (`7203 → 7072`, `180,05 s`, `695.273 evals/s`, `2` Threads, `seed=5211`):
     `./solvers/t4_postop/target/release/t4_postop --input <start.txt> --v 8 --threads 2 --seed 5211 --time-limit-secs 180 --stagnation-secs 60 --out <mid.txt>`
  3. Lauf `G1-C` (`7072 → 7070`, `95,22 s` inkl. `60 s` Stagnationsabbruch, `739.171 evals/s`, `2` Threads, `seed=5212`):
     `./solvers/t4_postop/target/release/t4_postop --resume <mid.txt> --v 8 --threads 2 --seed 5212 --time-limit-secs 180 --stagnation-secs 60 --out results/t4_nearbush/CA_7070_4_11_8.txt`
  *(Hinweis: Da `t4_postop` 2 Threads mit gemeinsamem `AtomicUsize`-Beststand verwendet, ist der genaue Suchpfad scheduling-abhängig; die abgelegte Datei ist über `results/t4_nearbush/SHA256SUMS` fixiert und direkt dual-verifiziert.)*
- **Verifier 1 (`./verifiers/ca_verify results/t4_nearbush/CA_7070_4_11_8.txt 4 8`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7070; t=4, k=11, v=8) - all 330 column sets fully cover all 4096 tuples` (`0,01 s`)
- **Verifier 2 (`python3 verifiers/verify_independent.py results/t4_nearbush/CA_7070_4_11_8.txt 4 8 -n 7070 -k 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7070; t=4, k=11, v=8) - all 330 column sets cover all 4096 tuples (1351680 total interactions) [elapsed: 0.7777s]`

### `results/t4_nearbush/CA_7561_4_11_8.txt`
- **Byte-identische Reproduktion (2 unabhängige Läufe + Übereinstimmung mit Phase 5B-1):** `sha256 = 821c23ea6852f7c77c55bbf5e8858c6c907a195aa2c418d20d231e00ce429fd2` (`0,042 s` / `0,041 s`, `cmp -s` PASS).
- **Befehl:** `python3 scripts/gen_t4_q8_nearbush.py --mode k11-pencil --out results/t4_nearbush/CA_7561_4_11_8.txt`
- **Verifier 1 (`./verifiers/ca_verify results/t4_nearbush/CA_7561_4_11_8.txt 4 8`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7561; t=4, k=11, v=8) - all 330 column sets fully cover all 4096 tuples` (`0,01 s`)
- **Verifier 2 (`python3 verifiers/verify_independent.py results/t4_nearbush/CA_7561_4_11_8.txt 4 8 -n 7561 -k 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7561; t=4, k=11, v=8) - all 330 column sets cover all 4096 tuples (1351680 total interactions) [elapsed: 0.6205s]`

---

# Dual-Verification Log — Phase 5B-2B (`t = 4, v = 7, 9` ungerade NEAR_BUSH)

- **Datum (UTC):** `2026-11-25`
- **Branch:** `exp/phase5b2b-odd-q-nearbush` (Basis: `origin/main` @ `6aa37ba`, nach Merge von PR `#15`)
- **Live-Tabellenstand (`chrispbsmolen/ca-tools`):** Commit `7381fdbb258cc24775b0a137dc12eaf20f89c15a` (`2026-11-25T19:41:08Z`; geprüft gegen `table/ca_table.csv.gz`, `table/ca_frame.csv` und `table/derived.csv`, `0` Änderungen unter `table/` gegenüber `c5f447d`, `0` offene PRs auf `t = 4`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, 2 vCPUs (2 Threads)
- **Verifier-Integrität:** `sha256sum -c verifiers/SHA256SUMS` 3/3 OK; `python3 verifiers/test_verifiers.py` 23/23 PASS; `git diff origin/main -- verifiers/` leer.
- **Einreichungsstatus:** Ausschließlich lokale Ablage unter `results/t4_nearbush/` (keine Meldung nach außen; PR `#88` und Checkliste `RULES.md` Punkt 2 bleiben vorrangig).

## 3. Übersicht der dual-verifizierten ungeraden `q`-Arrays (`results/t4_nearbush/`)

| Datei (`results/t4_nearbush/`) | Zelle `(t, k, v)` | `N` | `ca-tools` @ `7381fdb` | Delta vs. `7381fdb` | Rolle (Regel 3) | SHA-256 |
| --- | :---: | :---: | :---: | :---: | --- | --- |
| `CA_3479_4_9_7.txt` | `(4, 9, 7)` | **3479** | `3556` (`VER`, Sitjar v1.5) | **−77** | Pareto-Best (`q = 7, k = 9`) | `dd835c93a0095586c710c71f56ddb3a15a15482865af5afca6532807ddf294fd` |
| `CA_9639_4_11_9.txt` | `(4, 11, 9)` | **9639** | `9801` (`VER`, Bai XunDi 2026) | **−162** | Pareto-Best (`q = 9, k = 11`) | `741f78da1eb8f91a9432bc9633e0c62be4948752077909c4fd6ebae67b03daf2` |

### Herkunft & Vorarbeit (Regel 4)
- **Vorarbeit:** Bush (1952) für `OA(q^4; 4, q + 1, q)` und `OA(q^3; 3, q + 1, q)`; Segre (1955) für `(q + 1)`-Bögen in `PG(2, q)`; Jamison (1977) und Brouwer–Schrijver (1978) für affine Blocking-Sets der Größe `>= 2q - 1` in `AG(2, q)`; Nurmela (2004) für Tabu-Reparatur; Bai XunDi (2026) für `poly2` (`N_poly2(q) = q^4 + ((q^2 - 1)/2) q^2`) sowie Row-Deletion + Tabu-Post-Optimierung; Sitjar (2026) für `CA(3556; 4, 9, 7)`.
- **Eigene Zusammensetzung:** Projektion `Q_cd(a, b, c, d) = (c, d)` mit exakter `AG(2, q)`-Partition in `(q - 1)/2` disjunkte `(2q - 1)`-Blocking-Sets + `q`-Punkte-Parabel `{(d^2, d)}` (Symbol `(q - 1)/2`) + `(q - 1)/2` Einzelpunkte (`scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint`), gefolgt von Post-Optimierung mit `solvers/t4_postop` (0-Break-Don't-Care-Absorption + Row-Deletion + Focused-HD1-Tabu + PAWS).

## 4. Verifikations-Protokoll (`CA_3479_4_9_7.txt` & `CA_9639_4_11_9.txt`)

### `results/t4_nearbush/CA_3479_4_9_7.txt`
- **Reproduktionskette:**
  1. Deterministisches Startarray `CA(3577; 4, 9, 7)` (`sha256: bd2299130cb8058c366b919f5cf36e7bcf9cc9f75d737a71488327d58c181ae5`, 2× byte-identisch):
     `python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 7 --out <start_q7.txt>`
  2. Lauf `P5B-2B-G0B` (`3577 → 3479`, `saved = 98 = 2 · 7^2`, `15,01 s`, `1.642.506 evals/s`, `2` Threads, `seed=5302`):
     `timeout --kill-after=10s 30 ./solvers/t4_postop/target/release/t4_postop --input <start_q7.txt> --v 7 --threads 2 --seed 5302 --time-limit-secs 15 --stagnation-secs 10 --out results/t4_nearbush/CA_3479_4_9_7.txt`
- **Verifier 1 (`./verifiers/ca_verify results/t4_nearbush/CA_3479_4_9_7.txt 4 7`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=3479; t=4, k=9, v=7) - all 126 column sets fully cover all 2401 tuples` (`0,01 s`)
- **Verifier 2 (`python3 verifiers/verify_independent.py results/t4_nearbush/CA_3479_4_9_7.txt 4 7 -n 3479 -k 9`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=3479; t=4, k=9, v=7) - all 126 column sets cover all 2401 tuples (302526 total interactions) [elapsed: 0.2239s]`

### `results/t4_nearbush/CA_9639_4_11_9.txt`
- **Reproduktionskette:**
  1. Deterministisches Startarray `CA(9801; 4, 11, 9)` (`sha256: 3fa0850ef5730767e733002ebaeda8af33d2ffe7c7da67a248ddcc8f3b2a39e7`, 2× byte-identisch):
     `python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 9 --out <start_q9.txt>`
  2. Lauf `G1-Q9-A` (`9801 → 9639`, `saved = 162 = 2 · 9^2`, `79,02 s` inkl. `60 s` Stagnationsabbruch, `428.077 evals/s`, `2` Threads, `seed=5321`):
     `timeout --kill-after=10s 120 ./solvers/t4_postop/target/release/t4_postop --input <start_q9.txt> --v 9 --threads 2 --seed 5321 --time-limit-secs 115 --stagnation-secs 60 --out results/t4_nearbush/CA_9639_4_11_9.txt`
- **Verifier 1 (`./verifiers/ca_verify results/t4_nearbush/CA_9639_4_11_9.txt 4 9`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=9639; t=4, k=11, v=9) - all 330 column sets fully cover all 6561 tuples` (`0,01 s`)
- **Verifier 2 (`python3 verifiers/verify_independent.py results/t4_nearbush/CA_9639_4_11_9.txt 4 9 -n 9639 -k 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=9639; t=4, k=11, v=9) - all 330 column sets cover all 6561 tuples (2165130 total interactions) [elapsed: 1.0941s]`

---

# Dual-Verification Log — Phase 5B-2C (`--threads 1` Determinismus-Audit & `q = 11, 13`-Übertragung)

- **Datum (UTC):** `2026-11-25`
- **Branch:** `exp/phase5b2c-q11-q13-nearbush` (Basis: `origin/main` @ `104bf43`, nach Merge von PR `#16`)
- **Live-Tabellenstand (`chrispbsmolen/ca-tools`):** Commit `d7394120eb9703fbd92e5a28cbbda970c298f115` (`2026-11-25T20:25:41Z`; `+1` Commit `tools/build_site.py` gegenüber `7381fdb`, `0` Änderungen unter `table/`, `0` offene PRs auf `t = 4`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, 2 vCPUs (alle `t4_postop`-Läufe strikt **`--threads 1`**, jeweils **2× byte-identisch** verifiziert)
- **Verifier-Integrität:** `sha256sum -c verifiers/SHA256SUMS` 3/3 OK; `python3 verifiers/test_verifiers.py` 23/23 PASS; `git diff origin/main -- verifiers/ submission/` leer.
- **Einreichungsstatus:** Ausschließlich lokale Ablage unter `results/t4_nearbush/` (keine Meldung nach außen; PR `#88` und Checkliste `RULES.md` Punkt 2 bleiben vorrangig).

## 5. Übersicht der 2× byte-identischen `--threads 1`-Best-Arrays (`results/t4_nearbush/`)

*(Die früheren Multi-Thread-Post-Op-Dateien `CA_3479_4_9_7.txt`, `CA_7070_4_11_8.txt` und `CA_9639_4_11_9.txt` sowie der deterministische Anker `CA_7561_4_11_8.txt` verbleiben unverändert als historische Referenzen, werden jedoch alle streng dominiert und gemäß Regel 3 nicht eingereicht.)*

| Datei (`results/t4_nearbush/`) | Zelle `(t, k, v)` | `N` | `ca-tools` @ `d739412` | Delta vs. `d739412` | Determinismus (`--threads 1`) | SHA-256 |
| --- | :---: | :---: | :---: | :---: | --- | --- |
| `CA_3430_4_9_7.txt` | `(4, 9, 7)` | **3430** | `3556` (`VER`, Sitjar v1.5) | **−126** | 2× byte-identisch (`cmp -s` PASS, entspricht externer Referenz-SHA-256) | `d5860adeeab8a438e8716abadc82c699c4f3192a658edf1e8a5046a2ac57f533` |
| `CA_5888_4_10_8.txt` | `(4, 10, 8)` | **5888** | `6101` (`VER`, Bai XunDi 2026) | **−213** | 2× byte-identisch (rein deterministischer Generator) | `7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` |
| `CA_7056_4_11_8.txt` | `(4, 11, 8)` | **7056** | `7680` (`CIT`, Colbourn–Lanús `k = 15`) | **−624** | 2× byte-identisch (`cmp -s` PASS) | `b18c17426dabadd7470245c3f3819e18c52bcd1ec0b060ac7ed8378d117233d7` |
| `CA_9558_4_11_9.txt` | `(4, 11, 9)` | **9558** | `9801` (`VER`, Bai XunDi 2026) | **−243** | 3× byte-identisch (`cmp -s` PASS, inkl. Gate 0.2) | `8ffd689d66b57fde974df670c954b1e29addb66749563d119b8b5da7383f6dd2` |
| `CA_21900_4_13_11.txt` | `(4, 13, 11)` | **21900** | `21901` (`VER`, Bai XunDi 2026) | **−1** | 2× byte-identisch (`cmp -s` PASS) | `cb7696e377564594b0f8d047ec1a5efdf4797e1ccba6faa79a6ab26a2222dafc` |
| `CA_42722_4_15_13.txt` | `(4, 15, 13)` | **42722** | `42757` (`VER`, Bai XunDi 2026) | **−35** | 3× byte-identisch (`cmp -s` PASS mit `--target-n 42722`) | `1b5a6d75f4b59345850d6bee9c8aaa4bbcd06b6479e9a410688bb662eed20e73` |

## 6. Verifikations-Protokoll Phase 5B-2C (`--threads 1`, 2× byte-identisch)

### `results/t4_nearbush/CA_3430_4_9_7.txt`
- **Reproduktionskette (2× byte-identisch, `cmp -s` PASS):**
  1. Eigenes deterministisches Startarray `CA(3577; 4, 9, 7)` (`sha256: bd2299130cb8058c366b919f5cf36e7bcf9cc9f75d737a71488327d58c181ae5`):
     `timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 7 --out <start_q7.txt>`
  2. Zweifacher identischer Lauf (`3577 → 3430`, `saved = 147 = 3 · 7^2`, `absorbed = 67`, Lauf 1: `12,58 s` / `786.006 evals/s` [Treffer `2,57 s`], Lauf 2: `12,42 s` / `755.123 evals/s` [Treffer `2,42 s`]):
     `timeout --kill-after=10s 30 ./solvers/t4_postop/target/release/t4_postop --input <start_q7.txt> --v 7 --threads 1 --seed 5302 --time-limit-secs 15 --stagnation-secs 10 --out results/t4_nearbush/CA_3430_4_9_7.txt`
- **Verifier 1 (`timeout --kill-after=10s 30 ./verifiers/ca_verify results/t4_nearbush/CA_3430_4_9_7.txt 4 7`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=3430; t=4, k=9, v=7) - all 126 column sets fully cover all 2401 tuples` (`0,01 s`)
- **Verifier 2 (`timeout --kill-after=10s 30 python3 verifiers/verify_independent.py results/t4_nearbush/CA_3430_4_9_7.txt 4 7 -n 3430 -k 9`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=3430; t=4, k=9, v=7) - all 126 column sets cover all 2401 tuples (302526 total interactions) [elapsed: 0.1603s]`

### `results/t4_nearbush/CA_7056_4_11_8.txt`
- **Reproduktionskette (2× byte-identisch, `cmp -s` PASS):**
  1. Eigenes deterministisches Startarray `CA(7203; 4, 11, 8)` (`sha256: cb222f4828c3d843b167b58959f69c08dbd557f60f4146f57e8fbd6d67d7c68e`):
     `timeout --kill-after=10s 30 python3 scripts/gen_t4_q8_nearbush.py --mode k11-polychrom --out <start_q8_k11.txt>`
  2. Zweifacher identischer Lauf (`7203 → 7056`, `saved = 147`, `absorbed = 61`, Lauf 1: `150,04 s` / `346.106 evals/s` [Treffer `121,96 s`], Lauf 2: `150,04 s` / `327.744 evals/s` [Treffer `129,12 s`]):
     `timeout --kill-after=10s 180 ./solvers/t4_postop/target/release/t4_postop --input <start_q8_k11.txt> --v 8 --threads 1 --seed 5211 --time-limit-secs 150 --stagnation-secs 60 --out results/t4_nearbush/CA_7056_4_11_8.txt`
- **Verifier 1 (`timeout --kill-after=10s 30 ./verifiers/ca_verify results/t4_nearbush/CA_7056_4_11_8.txt 4 8`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7056; t=4, k=11, v=8) - all 330 column sets fully cover all 4096 tuples` (`0,01 s`)
- **Verifier 2 (`timeout --kill-after=10s 60 python3 verifiers/verify_independent.py results/t4_nearbush/CA_7056_4_11_8.txt 4 8 -n 7056 -k 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=7056; t=4, k=11, v=8) - all 330 column sets cover all 4096 tuples (1351680 total interactions) [elapsed: 0.6531s]`

### `results/t4_nearbush/CA_9558_4_11_9.txt`
- **Reproduktionskette (3× byte-identisch, `cmp -s` PASS):**
  1. Eigenes deterministisches Startarray `CA(9801; 4, 11, 9)` (`sha256: 3fa0850ef5730767e733002ebaeda8af33d2ffe7c7da67a248ddcc8f3b2a39e7`):
     `timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 9 --out <start_q9.txt>`
  2. Zweifacher identischer Lauf (`9801 → 9558`, `saved = 243 = 3 · 9^2`, `absorbed = 3898`, Lauf 1: `96,08 s` / `210.994 evals/s` [Treffer `36,07 s`], Lauf 2: `98,79 s` / `204.245 evals/s` [Treffer `38,77 s`]; zusätzlich als Gate-0.2-Positivkontrolle mit dem finalen Binary bei `--time-limit-secs 65 --stagnation-secs 25` in `63,73 s` 2× byte-identisch bestätigt):
     `timeout --kill-after=10s 180 ./solvers/t4_postop/target/release/t4_postop --input <start_q9.txt> --v 9 --threads 1 --seed 5321 --time-limit-secs 115 --stagnation-secs 60 --out results/t4_nearbush/CA_9558_4_11_9.txt`
- **Verifier 1 (`timeout --kill-after=10s 30 ./verifiers/ca_verify results/t4_nearbush/CA_9558_4_11_9.txt 4 9`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=9558; t=4, k=11, v=9) - all 330 column sets fully cover all 6561 tuples` (`0,01 s`)
- **Verifier 2 (`timeout --kill-after=10s 60 python3 verifiers/verify_independent.py results/t4_nearbush/CA_9558_4_11_9.txt 4 9 -n 9558 -k 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=9558; t=4, k=11, v=9) - all 330 column sets cover all 6561 tuples (2165130 total interactions) [elapsed: 1.1042s]`

### `results/t4_nearbush/CA_21900_4_13_11.txt`
- **Reproduktionskette (2× byte-identisch, `cmp -s` PASS):**
  1. Eigenes deterministisches Startarray `CA(21901; 4, 13, 11)` (`sha256: 0112cdea420a59d47e68021639dbdbd0c07cb99504b52df5de3d01d2460b0dc3`, 2× byte-identisch, `DUAL_PASS`):
     `timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 11 --out <start_q11.txt>`
  2. Zweifacher identischer Lauf (`21901 → 21900`, `saved = 1`, `absorbed = 0`, Lauf 1: `63,56 s` / `86.218 evals/s` [Treffer `3,55 s`], Lauf 2: `63,72 s` / `90.357 evals/s` [Treffer `3,65 s`], jeweils sauberer `60 s`-Stagnationsabbruch):
     `timeout --kill-after=10s 180 ./solvers/t4_postop/target/release/t4_postop --input <start_q11.txt> --v 11 --threads 1 --seed 5461 --time-limit-secs 160 --stagnation-secs 60 --out results/t4_nearbush/CA_21900_4_13_11.txt`
- **Verifier 1 (`timeout --kill-after=10s 30 ./verifiers/ca_verify results/t4_nearbush/CA_21900_4_13_11.txt 4 11`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=21900; t=4, k=13, v=11) - all 715 column sets fully cover all 14641 tuples` (`0,03 s`)
- **Verifier 2 (`timeout --kill-after=10s 60 python3 verifiers/verify_independent.py results/t4_nearbush/CA_21900_4_13_11.txt 4 11 -n 21900 -k 13`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=21900; t=4, k=13, v=11) - all 715 column sets cover all 14641 tuples (10468315 total interactions) [elapsed: 5.1351s]`

### `results/t4_nearbush/CA_42722_4_15_13.txt`
- **Reproduktionskette (3× byte-identisch, `cmp -s` PASS):**
  1. Eigenes deterministisches Startarray `CA(42757; 4, 15, 13)` (`sha256: 049978017b5cd523dec751609ed32635c84053dfe2ac502533566c8cd33f60be`, 2× byte-identisch, `DUAL_PASS` `0,15 s / 25,80 s`):
     `timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 13 --out <start_q13.txt>`
  2. Zweifacher identischer Lauf mit deterministischem Stopp `--target-n 42722` (um Wall-Clock-Jitter an der `210 s`-Grenze auszuschließen; im initialen `210 s`-Paar erreichte Lauf 1 `42723` bei `207,01 s` und Lauf 2 `42722` bei `208,57 s` auf identischem Pfad; die beiden `--target-n 42722`-Bestätigungsläufe erreichten `42722` in `217,21 s` bzw. `214,93 s`, exakt `steps = 223`, `evals = 13.910`, `saved = 35`, alle drei Dateien byte-identisch):
     `timeout --kill-after=10s 280 ./solvers/t4_postop/target/release/t4_postop --input <start_q13.txt> --v 13 --threads 1 --seed 5471 --time-limit-secs 260 --stagnation-secs 60 --target-n 42722 --out results/t4_nearbush/CA_42722_4_15_13.txt`
- **Verifier 1 (`timeout --kill-after=10s 30 ./verifiers/ca_verify results/t4_nearbush/CA_42722_4_15_13.txt 4 13`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=42722; t=4, k=15, v=13) - all 1365 column sets fully cover all 28561 tuples` (`0,16 s`)
- **Verifier 2 (`timeout --kill-after=10s 120 python3 verifiers/verify_independent.py results/t4_nearbush/CA_42722_4_15_13.txt 4 13 -n 42722 -k 15`):**
  - Exit-Code: `0`
  - Ausgabe: `VERIFIED: CA(N=42722; t=4, k=15, v=13) - all 1365 column sets cover all 28561 tuples (38985765 total interactions) [elapsed: 24.7447s]`

