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
