# Reproduktions- & Verifikationslog `t = 4 NEAR_BUSH` (`--target-n`, `--threads 1`)

Eigenständiges Log der Phase 5B-Audit. Es ergänzt [`VERIFICATION_LOG.md`](VERIFICATION_LOG.md) (unverändert) und deckt die `6` Pareto-Best-Arrays in `results/t4_nearbush/` ab.

- **Datum (UTC):** `2026-11-25` (`22:00`–`22:16Z`)
- **Branch:** `chore/t4-nearbush-audit` (Basis `origin/main` @ `ca637a6`, nach Merge von PR `#17`)
- **Quellstand:** `solvers/t4_postop/src/main.rs`, `scripts/gen_t4_odd_q_nearbush.py` und `scripts/gen_t4_q8_nearbush.py` zuletzt geändert in `98d7a43` (SHA-256 `48847bcb…`, `32afb669…`, `eec6adad…`); in diesem Branch unverändert.
- **Build:** `cargo build --release` in `solvers/t4_postop` (`rustc 1.100.0`, `std`-only), `python3` `3.12.16`; `verifiers/ca_verify` lokal aus `verifiers/ca_verify.c` kompiliert.
- **Hardware:** `Intel(R) Xeon(R) CPU @ 2.30GHz`, 2 vCPUs; alle `t4_postop`-Läufe strikt `--threads 1` und nacheinander (kein paralleler Lauf).
- **Ausgaben:** in einem Scratch-Verzeichnis außerhalb des Repos; Vergleich gegen die abgelegten Dateien per SHA-256 und `cmp -s`. Die abgelegten Dateien in `results/t4_nearbush/` wurden **nicht** überschrieben.
- **Laufzeiten:** Für `t4_postop` ist die Angabe `elapsed` aus der Abschlusszeile des Programms übernommen. Eine zusätzliche Shell-Messung der Wall-Clock fiel aus (`bc` im Container nicht installiert); die Einhaltung der externen `timeout`-Grenzen ist durch Exit-Code `0` aller Läufe belegt.
- **Belegart:** Reproduktion mit dokumentiertem Befehl aus den Startdateien, `12/12` Läufe byte-identisch zu den abgelegten Dateien (Punkt 2e der Checkliste `RULES.md`, nur lokal). Keine neue Suche.

---

## 1. Übersicht

| Array | Startarray (SHA-256, 2× byte-identisch erzeugt) | Befehl (fester Stopp) | Lauf 1 | Lauf 2 | Output-SHA-256 (beide Läufe) | = abgelegte Datei |
| --- | --- | --- | :---: | :---: | --- | :---: |
| `CA(5888; 4, 10, 8)` | — (direkter Generator) | `gen_t4_q8_nearbush.py --mode k10-polychrom` | `0,037 s` | `0,034 s` | `7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802` | ja |
| `CA(3430; 4, 9, 7)` | `CA(3577)` `bd2299130cb8058c366b919f5cf36e7bcf9cc9f75d737a71488327d58c181ae5` | `--target-n 3430` | `2,26 s` | `2,34 s` | `d5860adeeab8a438e8716abadc82c699c4f3192a658edf1e8a5046a2ac57f533` | ja |
| `CA(7056; 4, 11, 8)` | `CA(7203)` `cb222f4828c3d843b167b58959f69c08dbd557f60f4146f57e8fbd6d67d7c68e` | `--target-n 7056` | `97,84 s` | `96,86 s` | `b18c17426dabadd7470245c3f3819e18c52bcd1ec0b060ac7ed8378d117233d7` | ja |
| `CA(9558; 4, 11, 9)` | `CA(9801)` `3fa0850ef5730767e733002ebaeda8af33d2ffe7c7da67a248ddcc8f3b2a39e7` | `--target-n 9558` | `31,17 s` | `32,37 s` | `8ffd689d66b57fde974df670c954b1e29addb66749563d119b8b5da7383f6dd2` | ja |
| `CA(21900; 4, 13, 11)` | `CA(21901)` `0112cdea420a59d47e68021639dbdbd0c07cb99504b52df5de3d01d2460b0dc3` | `--target-n 21900` | `3,09 s` | `3,27 s` | `cb7696e377564594b0f8d047ec1a5efdf4797e1ccba6faa79a6ab26a2222dafc` | ja |
| `CA(42722; 4, 15, 13)` | `CA(42757)` `049978017b5cd523dec751609ed32635c84053dfe2ac502533566c8cd33f60be` | `--target-n 42722` | `202,58 s` | `202,18 s` | `1b5a6d75f4b59345850d6bee9c8aaa4bbcd06b6479e9a410688bb662eed20e73` | ja |

Summe aller `t4_postop`-Reproduktionsläufe: `673,96 s` (`10` Läufe). Generatorläufe zusätzlich `< 0,4 s` je Lauf.

## 2. Befehle im Wortlaut

Platzhalter: `<S>` = Scratch-Verzeichnis, `BIN = ./solvers/t4_postop/target/release/t4_postop`.

### 2.1 Startarrays (je 2×, `cmp -s` PASS)

```bash
timeout --kill-after=10s 30 python3 scripts/gen_t4_q8_nearbush.py   --mode k10-polychrom            --out <S>/CA_5888_r{1,2}.txt   # 0,037 / 0,034 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 7     --out <S>/start_q7_r{1,2}.txt   # 0,017 / 0,021 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_q8_nearbush.py   --mode k11-polychrom            --out <S>/start_q8k11_r{1,2}.txt # 0,096 / 0,093 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 9     --out <S>/start_q9_r{1,2}.txt   # 0,053 / 0,051 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 11    --out <S>/start_q11_r{1,2}.txt  # 0,129 / 0,126 s
timeout --kill-after=10s 30 python3 scripts/gen_t4_odd_q_nearbush.py --mode poly2-disjoint --q 13    --out <S>/start_q13_r{1,2}.txt  # 0,277 / 0,314 s
```

### 2.2 `t4_postop` (je 2×, `--threads 1`, `cmp -s` PASS)

```bash
timeout --kill-after=10s 60  $BIN --input <S>/start_q7_r1.txt    --v 7  --threads 1 --seed 5302 --time-limit-secs 15  --stagnation-secs 10 --target-n 3430  --out <S>/CA_3430_r{1,2}.txt
timeout --kill-after=10s 180 $BIN --input <S>/start_q8k11_r1.txt --v 8  --threads 1 --seed 5211 --time-limit-secs 150 --stagnation-secs 60 --target-n 7056  --out <S>/CA_7056_r{1,2}.txt
timeout --kill-after=10s 180 $BIN --input <S>/start_q9_r1.txt    --v 9  --threads 1 --seed 5321 --time-limit-secs 115 --stagnation-secs 60 --target-n 9558  --out <S>/CA_9558_r{1,2}.txt
timeout --kill-after=10s 90  $BIN --input <S>/start_q11_r1.txt   --v 11 --threads 1 --seed 5461 --time-limit-secs 160 --stagnation-secs 60 --target-n 21900 --out <S>/CA_21900_r{1,2}.txt
timeout --kill-after=10s 240 $BIN --input <S>/start_q13_r1.txt   --v 13 --threads 1 --seed 5471 --time-limit-secs 260 --stagnation-secs 60 --target-n 42722 --out <S>/CA_42722_r{1,2}.txt
```

### 2.3 Abschlusszeilen von `t4_postop` (beide Läufe je Zelle identisch bis auf Zeitangaben)

| Array | `init_N → final_N` | `saved` | `absorbed_tuples` | `steps` | `evals` | `evals/s` (Lauf 1 / 2) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| `CA_3430` | `3577 → 3430` | `147` | `67` | `24.297` | `1.057.430` | `468.454 / 451.483` |
| `CA_7056` | `7203 → 7056` | `147` | `61` | `685.644` | `42.024.831` | `429.540 / 433.883` |
| `CA_9558` | `9801 → 9558` | `243` | `3.898` | `68.487` | `3.835.841` | `123.045 / 118.486` |
| `CA_21900` | `21901 → 21900` | `1` | `0` | `1.665` | `126.354` | `40.850 / 38.686` |
| `CA_42722` | `42757 → 42722` | `35` | `0` | `223` | `13.910` | `69 / 69` |

Gleiche `steps`- und `evals`-Zahlen in beiden Läufen belegen denselben Suchpfad; die Laufzeit hängt mit `--target-n` nicht mehr vom Zeitlimit ab.

### 2.4 Abgleich mit PR `#17` für `CA(42722; 4, 15, 13)`

In PR `#17` (`VERIFICATION_LOG.md` §6) sind zwei `--target-n 42722`-Läufe mit denselben Programmargumenten geloggt, aber mit äußerem `timeout --kill-after=10s 280` (`217,21 s` / `214,93 s`); der dritte Lauf war der initiale Lauf ohne `--target-n`. Die beiden Läufe hier verwenden die Grenze `timeout --kill-after=10s 240` und laufen in `202,58 s` / `202,18 s` durch. Damit liegen für `CA_42722` jetzt `4` byte-identische Läufe mit `--target-n 42722` vor.

## 3. Dual-Verifikation der abgelegten Dateien

| Datei (`results/t4_nearbush/`) | `ca_verify` (Exit, Zeit) | `verify_independent.py` (Exit, Zeit) | Abdeckung |
| --- | :---: | :---: | --- |
| `CA_3430_4_9_7.txt` | `0`, `0,01 s` | `0`, `0,1086 s` | `126` Spaltenmengen × `2401` Tupel |
| `CA_5888_4_10_8.txt` | `0`, `0,02 s` | `0`, `0,3638 s` | `210` × `4096` |
| `CA_7056_4_11_8.txt` | `0`, `0,01 s` | `0`, `0,5822 s` | `330` × `4096` |
| `CA_9558_4_11_9.txt` | `0`, `0,01 s` | `0`, `0,9924 s` | `330` × `6561` |
| `CA_21900_4_13_11.txt` | `0`, `0,04 s` | `0`, `5,0028 s` | `715` × `14641` |
| `CA_42722_4_15_13.txt` | `0`, `0,13 s` | `0`, `22,1229 s` | `1365` × `28561` |

Befehle: `timeout --kill-after=10s 30 ./verifiers/ca_verify <datei> 4 <v>` und `timeout --kill-after=10s 120 python3 verifiers/verify_independent.py <datei> 4 <v> -n <N> -k <k>` (inkl. `q = 13`). Da alle `12` reproduzierten Dateien byte-identisch zu den abgelegten Dateien sind, gilt das Ergebnis auch für sie.

## 4. Pflicht-Checks

- `sha256sum -c verifiers/SHA256SUMS`: `3/3 OK`
- `sha256sum -c SHA256SUMS` in `results/`: `32/32 OK`
- `sha256sum -c SHA256SUMS` in `results/t4_nearbush/`: `10/10 OK`
- `python3 verifiers/test_verifiers.py`: `23/23` PASS
- `git diff origin/main -- verifiers/ submission/ results/VERIFICATION_LOG_pgl_ccl.md docs/LITERATURE_CHECK_PGL_CCL.md docs/THIRD_PARTY_VERIFICATION.md`: leer
