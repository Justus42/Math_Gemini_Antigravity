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
- **Fremde Vorarbeit:** Bush (1952) für das orthogonale Array `OA(q^4; 4, q + 1, q)` und das `(q + 2)`-Hyperoval `OA(q^3; 3, q + 2, q)` über `GF(2^m)`; Jamison (1977) und Brouwer–Schrijver (1978) für affine Blocking-Sets der Mindestgröße `2q - 1` in `AG(2, q)`; Nurmela (2004) für Tabu-Search-Reparatur; Nayeri–Colbourn–Konjevod (2013) für Post-Optimierung; **X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“ (30.10.2026, `doi:10.5281/zenodo.23787051`, `polychrome-bai2026`; Daten `doi:10.5281/zenodo.23787055`)** für den gesamten Färbungsrahmen über `AG(2, q)` (Satz 3.5), die Jamison-Obergrenze `c <= floor(q/2)` (Prop. 4.1), die `poly2`-Geradenbüschel-Zerlegung (Satz 5.1 / Prop. 5.2 / Kor. 5.3), Zwei-Zusatzspalten-Bauarten (Satz 6.2) sowie Row-Deletion + Tabu-Post-Optimierung.
- **Eigener Beitrag (auf Basis von Bai `polychrome-bai2026`):**
  - `CA_7561_4_11_8.txt`: Deterministische Hyperoval-Double-`poly2`-Implementierung (`scripts/gen_t4_q8_nearbush.py --mode k11-pencil`).
  - `CA_5888_4_10_8.txt`: Konkrete Wahl der Projektion `Q(a, b, c, d) = (a ^ c ^ d, a ^ b ^ d)` entlang `x^2 + x + 1` über `GF(8)` (jede Faser ist ein exaktes `OA(64; 2, 9, 8)`), sodass die `4` freien Punkte neben `4` disjunkten 15-Punkte-Blocking-Sets direkt `4` Hyperoval-Slices im Bush-OA liefern (`4096 + 4 · 448 = 5888`, `−256` unter Bais Modellgrenze `6144` aus Prop. 5.4).
  - `CA_7070_4_11_8.txt`: Zwei balancierte 4-polychromatische `AG(2, 8)`-Färbungen mit geteilten Hyperoval-Slices (`16` geteilte `OA(64)`-Slices) + `35` Reparaturzeilen (`CA(7203; 4, 11, 8)`, `−989` unter Bais Satz-6.2-Wert `8192`), gefolgt von Post-Optimierung mit eigenem Reduzierer `solvers/t4_postop` (`7203 → 7072 → 7070`).

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
- **Fremde Vorarbeit:** Bush (1952) für `OA(q^4; 4, q + 1, q)` und `OA(q^3; 3, q + 1, q)`; Segre (1955) für `(q + 1)`-Bögen in `PG(2, q)`; Jamison (1977) und Brouwer–Schrijver (1978) für affine Blocking-Sets der Größe `>= 2q - 1` in `AG(2, q)`; Nurmela (2004) für Tabu-Reparatur; Nayeri–Colbourn–Konjevod (2013) für Post-Optimierung; **X. Bai, „Covering arrays from line-polychromatic colourings of affine planes“ (30.10.2026, `doi:10.5281/zenodo.23787051`, `polychrome-bai2026`; Daten `doi:10.5281/zenodo.23787055`)** für den Färbungsrahmen (Satz 3.5), die Obergrenze `c <= floor(q/2)` (Prop. 4.1), die Formel `N = q^4 + ((q^2 - 1)/2) q^2` (Satz 5.1 / Prop. 5.2 / Kor. 5.3) sowie Row-Deletion + Tabu-Post-Optimierung; Sitjar (2026) für `CA(3556; 4, 9, 7)`.
- **Eigener Beitrag (auf Basis von Bai `polychrome-bai2026`):** Parabel-Packung (`q^2 = q` [Parabel] `+ ((q - 1)/2)*(2q - 1)` [disjunkte minimale Blocking-Sets] `+ (q - 1)/2` [Einzelpunkte]) unter Projektion `Q_cd(a, b, c, d) = (c, d)` (`scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint`), gefolgt von Post-Optimierung mit eigenem Reduzierer `solvers/t4_postop` (0-Break-Don't-Care-Absorption + Row-Deletion + Focused-HD1-Tabu + PAWS).

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

---

# Anhang — Phase 5B-Audit: Lokal deterministische `--target-n`-Reproduktion (`--threads 1`, 2× byte-identisch)

Konsolidierter Audit-Abschnitt der Phase 5B-Audit für alle `6` Pareto-Best-Arrays in `results/t4_nearbush/`.

- **Datum (UTC):** `2026-11-25` (`22:00`–`22:16Z`)
- **Branch:** `chore/t4-nearbush-audit` (Basis `origin/main` @ `ca637a6`, nach Merge von PR `#17`)
- **Quellstand:** `solvers/t4_postop/src/main.rs`, `scripts/gen_t4_odd_q_nearbush.py` und `scripts/gen_t4_q8_nearbush.py` zuletzt geändert in `98d7a43` (SHA-256 `48847bcb…`, `32afb669…`, `eec6adad…`); in diesem Branch unverändert.
- **Build:** `cargo build --release` in `solvers/t4_postop` (`rustc 1.100.0`, `std`-only), `python3` `3.12.16`; `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert.
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, 2 vCPUs; alle `t4_postop`-Läufe strikt `--threads 1` und nacheinander (kein paralleler Lauf).
- **Ausgaben:** in einem Scratch-Verzeichnis außerhalb des Repos; Vergleich gegen die abgelegten Dateien per SHA-256 und `cmp -s`. Die abgelegten Dateien in `results/t4_nearbush/` wurden **nicht** überschrieben.
- **Laufzeiten & FAIL-Regel:** Für `t4_postop` ist `elapsed` aus der Abschlusszeile des Programms übernommen (`bc` im Container nicht installiert; Einhaltung der externen `timeout`-Grenzen durch Exit-Code `0` aller Läufe belegt). **Verbindliche Regel (`RULES.md` §4):** Wird `--target-n` innerhalb des gesetzten Zeitlimits nicht erreicht, gilt der Reproduktionslauf als **`FAIL`**.
- **Belegart:** **lokal deterministisch (2× byte-identisch mit `--target-n`, `--threads 1`)** auf derselben Maschine (`12/12` Läufe byte-identisch zu den abgelegten Dateien, Punkt 2e der Checkliste `RULES.md`, nur lokal; keine neue Suche). Rechnerunabhängige Bestätigung auf einer zweiten Maschine siehe getrennt [`docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md`](../../docs/THIRD_PARTY_VERIFICATION_T4_NEARBUSH.md) (`5` Arrays bestätigt, `7056` und `42722` noch offen).

## 7. Übersicht der lokal deterministischen `--target-n`-Reproduktionen

| Array | Startarray (SHA-256, 2× byte-identisch erzeugt) | Befehl (fester Stopp) | Lauf 1 | Lauf 2 | Output-SHA-256 (beide Läufe) | = abgelegte Datei |
| --- | --- | --- | :---: | :---: | --- | :---: |
| `CA(5888; 4, 10, 8)` | — (direkter Generator) | `gen_t4_q8_nearbush.py --mode k10-polychrom` | `0,037 s` | `0,034 s` | `7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` | ja |
| `CA(3430; 4, 9, 7)` | `CA(3577)` `bd2299130cb8058c366b919f5cf36e7bcf9cc9f75d737a71488327d58c181ae5` | `--target-n 3430` | `2,26 s` | `2,34 s` | `d5860adeeab8a438e8716abadc82c699c4f3192a658edf1e8a5046a2ac57f533` | ja |
| `CA(7056; 4, 11, 8)` | `CA(7203)` `cb222f4828c3d843b167b58959f69c08dbd557f60f4146f57e8fbd6d67d7c68e` | `--target-n 7056` | `97,84 s` | `96,86 s` | `b18c17426dabadd7470245c3f3819e18c52bcd1ec0b060ac7ed8378d117233d7` | ja |
| `CA(9558; 4, 11, 9)` | `CA(9801)` `3fa0850ef5730767e733002ebaeda8af33d2ffe7c7da67a248ddcc8f3b2a39e7` | `--target-n 9558` | `31,17 s` | `32,37 s` | `8ffd689d66b57fde974df670c954b1e29addb66749563d119b8b5da7383f6dd2` | ja |
| `CA(21900; 4, 13, 11)` | `CA(21901)` `0112cdea420a59d47e68021639dbdbd0c07cb99504b52df5de3d01d2460b0dc3` | `--target-n 21900` | `3,09 s` | `3,27 s` | `cb7696e377564594b0f8d047ec1a5efdf4797e1ccba6faa79a6ab26a2222dafc` | ja |
| `CA(42722; 4, 15, 13)` | `CA(42757)` `049978017b5cd523dec751609ed32635c84053dfe2ac502533566c8cd33f60be` | `--target-n 42722` | `202,58 s` | `202,18 s` | `1b5a6d75f4b59345850d6bee9c8aaa4bbcd06b6479e9a410688bb662eed20e73` | ja |

Summe aller `t4_postop`-Reproduktionsläufe: `673,96 s` (`10` Läufe). Generatorläufe zusätzlich `< 0,4 s` je Lauf.

### 7.1 Befehle im Wortlaut (`<S>` = Scratch-Verzeichnis, `BIN = ./solvers/t4_postop/target/release/t4_postop`)

```bash
# Startarrays (je 2x, cmp -s PASS)
timeout --kill-after=10s 30 python3 scripts/gen_t4_q8_nearbush.py    --mode k10-polychrom            --out <S>/CA_5888_r{1,2}.txt    # 0,037 / 0,034 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 7     --out <S>/start_q7_r{1,2}.txt   # 0,017 / 0,021 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_q8_nearbush.py    --mode k11-polychrom            --out <S>/start_q8k11_r{1,2}.txt # 0,096 / 0,093 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 9     --out <S>/start_q9_r{1,2}.txt   # 0,053 / 0,051 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 11    --out <S>/start_q11_r{1,2}.txt  # 0,129 / 0,126 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 13    --out <S>/start_q13_r{1,2}.txt  # 0,277 / 0,314 s

# t4_postop (je 2x, --threads 1, cmp -s PASS; Nicht-Erreichen von --target-n = FAIL)
timeout --kill-after=10s 60  $BIN --input <S>/start_q7_r1.txt    --v 7  --threads 1 --seed 5302 --time-limit-secs 15  --stagnation-secs 10 --target-n 3430  --out <S>/CA_3430_r{1,2}.txt
timeout --kill-after=10s 180 $BIN --input <S>/start_q8k11_r1.txt --v 8  --threads 1 --seed 5211 --time-limit-secs 150 --stagnation-secs 60 --target-n 7056  --out <S>/CA_7056_r{1,2}.txt
timeout --kill-after=10s 180 $BIN --input <S>/start_q9_r1.txt    --v 9  --threads 1 --seed 5321 --time-limit-secs 115 --stagnation-secs 60 --target-n 9558  --out <S>/CA_9558_r{1,2}.txt
timeout --kill-after=10s 90  $BIN --input <S>/start_q11_r1.txt   --v 11 --threads 1 --seed 5461 --time-limit-secs 160 --stagnation-secs 60 --target-n 21900 --out <S>/CA_21900_r{1,2}.txt
timeout --kill-after=10s 240 $BIN --input <S>/start_q13_r1.txt   --v 13 --threads 1 --seed 5471 --time-limit-secs 260 --stagnation-secs 60 --target-n 42722 --out <S>/CA_42722_r{1,2}.txt
```

### 7.2 Abschlusszeilen (`t4_postop`) & Dual-Verifikation (Audit-Durchlauf)

| Array | `init_N → final_N` | `saved` | `absorbed` | `steps` | `evals` | `evals/s` (L1 / L2) | `ca_verify` (`timeout 30`) | `verify_independent.py` (`timeout 120`) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `CA_5888` | — (Gen.) | — | — | — | — | — | `0`, `0,02 s` | `0`, `0,3638 s` (`210 × 4096`) |
| `CA_3430` | `3577 → 3430` | `147` | `67` | `24.297` | `1.057.430` | `468.454 / 451.483` | `0`, `0,01 s` | `0`, `0,1086 s` (`126 × 2401`) |
| `CA_7056` | `7203 → 7056` | `147` | `61` | `685.644` | `42.024.831` | `429.540 / 433.883` | `0`, `0,01 s` | `0`, `0,5822 s` (`330 × 4096`) |
| `CA_9558` | `9801 → 9558` | `243` | `3.898` | `68.487` | `3.835.841` | `123.045 / 118.486` | `0`, `0,01 s` | `0`, `0,9924 s` (`330 × 6561`) |
| `CA_21900` | `21901 → 21900` | `1` | `0` | `1.665` | `126.354` | `40.850 / 38.686` | `0`, `0,04 s` | `0`, `5,0028 s` (`715 × 14641`) |
| `CA_42722` | `42757 → 42722` | `35` | `0` | `223` | `13.910` | `69 / 69` | `0`, `0,13 s` | `0`, `22,1229 s` (`1365 × 28561`) |

*(Für `CA_42722` lagen aus PR `#17` §6 bereits 2 `--target-n 42722`-Läufe mit `timeout 280` vor [`217,21 / 214,93 s`]; mit den beiden Läufen hier [`timeout 240`, `202,58 / 202,18 s`] liegen `4` byte-identische `--target-n 42722`-Läufe vor.)*



---

# Anhang — Phase 5E: Deterministische Bauart `N(q) = q^4 + (q(q - 1)/2) q^2` (`CA_9477`, `CA_21296`, `CA_41743`)

- **Datum (UTC):** `2026-11-26`
- **Branch:** `exp/phase5e-minus3q2-structure` (Basis `origin/main` @ `431328b`, nach Merge von PR `#20`)
- **Generator:** [`scripts/gen_t4_minus3q2.py`](../../scripts/gen_t4_minus3q2.py) (Pure Python `std`-only, suchfrei, kein Solver, `--variant transitive`)
- **Live-Abgleich `chrispbsmolen/ca-tools`:** Commit `0b79e3fb71af992bc1d5638ade0c1f972a43a12d` (`0b79e3f`, `2026-11-26T05:32:10Z`)
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`; `python3` `3.12.16`; `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert.
- **Bestehende Dateien:** Alle `10` bestehenden Array-Dateien in `results/t4_nearbush/` blieben vollständig unverändert (`CA_9558`, `CA_21900`, `CA_42722` verbleiben als historische Referenzen).

## 8. Dual-Verifikation, 2×-Determinismus & Negativkontrollen (Phase 5E)

| Datei (`results/t4_nearbush/`) | Zelle `(4, k, v)` | `ca-tools @ 0b79e3f` | Delta | Erstlauf / Repro (`cmp -s`) | SHA-256 | `ca_verify` (direkt auf Datei) | `verify_independent.py` (direkt auf Datei) | Negativkontrolle (`N - 1` Zeilen, Scratch) |
| --- | :---: | :---: | :---: | :---: | --- | :---: | :---: | --- |
| `CA_9477_4_11_9.txt` | `(4, 11, 9)` | `9801` (`VER`) | **`−324`** | `0,048 s` / `0,048 s` (`PASS`) | `eeea94544ed885cf2110733f4cd74b998c87d944dae8af535718bc267d431b30` | `rc=0`, `0,01 s` (`330 × 6561`) | `rc=0`, `0,9140 s` (`2.165.130` Interakt.) | `ca rc=1`, `py rc=1` (`120` fehlende Tupel in `120/330` 4-Mengen) |
| `CA_21296_4_13_11.txt` | `(4, 13, 11)` | `21901` (`VER`) | **`−605`** | `0,123 s` / `0,115 s` (`PASS`) | `cb9a4c5e431f1eb1652f70b0626bd981eaaa0c529f1267fad346847f703401a3` | `rc=0`, `0,03 s` (`715 × 14641`) | `rc=0`, `4,2043 s` (`10.468.315` Interakt.) | `ca rc=1`, `py rc=1` (`220` fehlende Tupel in `220/715` 4-Mengen) |
| `CA_41743_4_15_13.txt` | `(4, 15, 13)` | `42757` (`VER`) | **`−1014`** | `0,247 s` / `0,250 s` (`PASS`) | `e8435eb665b9c627982239675bc93f21334ac40d4e8d781cb3592e768233d9a5` | `rc=0`, `0,10 s` (`1365 × 28561`) | `rc=0`, `17,9351 s` (`38.985.765` Interakt.) | `ca rc=1`, `py rc=1` (`364` fehlende Tupel in `364/1365` 4-Mengen) |

*(Zusätzliche Gate-0-Positivkontrollen im Scratch-Verzeichnis mit demselben Generator: `q = 7` → `CA(3430; 4, 9, 7)` [`d29b5155…`, `0,014/0,015 s`, `DUAL_PASS`, Negativkontrolle `56` Lücken]; `q = 8` → `CA(5888; 4, 10, 8)` [`2e4bf66b…`, `0,033/0,031 s`, `DUAL_PASS`].)*

### 8.1 Reproduktions- und Prüfkommandos

```bash
timeout --kill-after=10s 60  python3 scripts/gen_t4_minus3q2.py --q 9  --variant transitive --out results/t4_nearbush/CA_9477_4_11_9.txt
timeout --kill-after=10s 120 python3 scripts/gen_t4_minus3q2.py --q 11 --variant transitive --out results/t4_nearbush/CA_21296_4_13_11.txt
timeout --kill-after=10s 120 python3 scripts/gen_t4_minus3q2.py --q 13 --variant transitive --out results/t4_nearbush/CA_41743_4_15_13.txt

timeout --kill-after=10s 30  ./verifiers/ca_verify results/t4_nearbush/CA_9477_4_11_9.txt 4 9
timeout --kill-after=10s 60  python3 verifiers/verify_independent.py results/t4_nearbush/CA_9477_4_11_9.txt 4 9 -n 9477 -k 11
timeout --kill-after=10s 30  ./verifiers/ca_verify results/t4_nearbush/CA_21296_4_13_11.txt 4 11
timeout --kill-after=10s 90  python3 verifiers/verify_independent.py results/t4_nearbush/CA_21296_4_13_11.txt 4 11 -n 21296 -k 13
timeout --kill-after=10s 45  ./verifiers/ca_verify results/t4_nearbush/CA_41743_4_15_13.txt 4 13
timeout --kill-after=10s 180 python3 verifiers/verify_independent.py results/t4_nearbush/CA_41743_4_15_13.txt 4 13 -n 41743 -k 15
```
