# Covering Array Submission & Audit Manifest (`submission/MANIFEST.md`)

Stand: **2026-11-25** | Referenz-Datenbasis: `chrispbsmolen/ca-tools` @ Commit `7b08aef06cbedaf1b376dbfa68f6aa171a54df4a` (`2026-11-25T03:31:22Z`).
Maschinenlesbare Tabelle: [`submission/records.csv`](records.csv) | Ein-Befehl-Audit: [`submission/verify_all.sh`](verify_all.sh).

## 1. Überblick & Konstruktionsprinzip

Alle hier aufgeführten `t = 3` Covering Arrays `CA(N; 3, k, v)` ($v = q + 1$, $q \in \{9, 11, 13, 19\}$) wurden deterministisch aus zwei Komponenten über den Zero-Dependency-Rust-Solver [`solvers/pgl_ccl_search`](../solvers/pgl_ccl_search/) erzeugt:
1. **Deterministischer `PGL(2, q)`-Block (`2 * q(q² - 1)` Zeilen):** Zwei balancierte Starterzeilen (`|L| = floor(k/2)`, `|R| = ceil(k/2)`, beide $\le q$) decken unter scharf 3-transitivem `PGL(2, q)` deterministisch 100 % aller 3-distinkten Tupel, alle Konstant-Tupel auf reinen Tripeln (`L³`, `R³`) sowie `aab` auf `L²R` und `baa` auf `LR²` ab.
2. **Allgemeine binäre CCL-Matrix `C` (`M × k`) über `v(v-1)/2` orientierte Paare:** Gerichteter Zyklus `(0,1), ..., (v-1,0)` plus Restpaare `u < w` stellt sicher, dass jedes Symbol mindestens einmal als `0` und `1` auftritt; mit `--cover-const` (`000` oder `111` auf jedem gemischten Tripel) entfallen alle `v` Konstantzeilen (`N = 2q(q²-1) + M·v(v-1)/2`; bei `cc=0`: `+ v`).

## 2. Pareto-Front der 13 Rekord-Arrays (23 verbesserte `(3, k, v)`-Zellen)

Alle Dateien wurden am `2026-11-25` frisch via `./submission/verify_all.sh` (`xargs -P 2`) durch **beide** unveränderte Verifier (`./verifiers/ca_verify` und `python3 verifiers/verify_independent.py`) bestätigt und auf strikte `ca-tools`-Formatkonformität (0-basierte Integer `0..v-1`, genau `N × k`, Einzel-Leerzeichen, kein Header, keine Leerzeilen/Trailing-Spaces, LF) geprüft.

| `t` | `k` | `v` | `N_new` | `N_live` (`ca-tools`) | Delta | Dominierte `k` | Methode | `ca_verify` | `py_verify` | Datei & SHA-256 |
| :-: | :-: | :-: | :---: | :---: | :---: | :---: | --- | :---: | :---: | --- |
| 3 | **15** | **10** | **2070** | `2205` (`VER`) | **−135** | `15` | `PGL(2,9)+CCL(M=14,cc=1)` | `0.009s` | `0.208s` | [`CA_2070_3_15_10.txt`](../results/CA_2070_3_15_10.txt) (`78b0497f2c81b0f7…`) |
| 3 | **16** | **10** | **2115** | `2205` (`VER`) | **−90** | `16` | `PGL(2,9)+CCL(M=15,cc=1)` | `0.007s` | `0.234s` | [`CA_2115_3_16_10.txt`](../results/CA_2115_3_16_10.txt) (`4734fd80ffe90f11…`) |
| 3 | **18** | **10** | **2160** | `2232` (`CIT`) | **−72** | `17..18` | `PGL(2,9)+CCL(M=16,cc=1)` | `0.007s` | `0.311s` | [`CA_2160_3_18_10.txt`](../results/CA_2160_3_18_10.txt) (`410ccbcc821c8db4…`) |
| 3 | **19** | **12** | **3696** | `3806` (`CIT`) | **−110** | `19` | `PGL(2,11)+CCL(M=16,cc=1)` | `0.014s` | `0.600s` | [`CA_3696_3_19_12.txt`](../results/CA_3696_3_19_12.txt) (`2492d0f7e36a993d…`) |
| 3 | **20** | **12** | **3762** | `3806` (`CIT`) | **−44** | `20` | `PGL(2,11)+CCL(M=17,cc=1)` | `0.015s` | `0.715s` | [`CA_3762_3_20_12.txt`](../results/CA_3762_3_20_12.txt) (`6a85d1b1e34aec73…`) |
| 3 | **20** | **14** | **5915** | `6006` (`CIT`) | **−91** | `20` | `PGL(2,13)+CCL(M=17,cc=1)` | `0.027s` | `1.434s` | [`CA_5915_3_20_14.txt`](../results/CA_5915_3_20_14.txt) (`051a4841f551770f…`) |
| 3 | **24** | **14** | **6097** | `6279` (`CIT`) | **−182** | `23..24` | `PGL(2,13)+CCL(M=19,cc=1)` | `0.035s` | `2.484s` | [`CA_6097_3_24_14.txt`](../results/CA_6097_3_24_14.txt) (`3abb40a4dcb501e3…`) |
| 3 | **26** | **14** | **6188** | `6383` (`CIT`) | **−195** | `25..26` | `PGL(2,13)+CCL(M=20,cc=1)` | `0.039s` | `3.064s` | [`CA_6188_3_26_14.txt`](../results/CA_6188_3_26_14.txt) (`2952b2efb82ae208…`) |
| 3 | **29** | **20** | **17670** | `18145` (`CIT`) | **−475** | `27..29` *(k=27,28: −266)* | `PGL(2,19)+CCL(M=21,cc=1)` | `0.403s` | `13.713s` | [`CA_17670_3_29_20.txt`](../results/CA_17670_3_29_20.txt) (`739bf030ad8234a8…`) |
| 3 | **32** | **20** | **17860** | `18145` (`CIT`) | **−285** | `30..32` | `PGL(2,19)+CCL(M=22,cc=1)` | `0.469s` | `18.603s` | [`CA_17860_3_32_20.txt`](../results/CA_17860_3_32_20.txt) (`544735d32928b02d…`) |
| 3 | **34** | **20** | **18050** | `18430` (`CIT`) | **−380** | `33..34` | `PGL(2,19)+CCL(M=23,cc=1)` | `0.387s` | `22.344s` | [`CA_18050_3_34_20.txt`](../results/CA_18050_3_34_20.txt) (`9224fbac04d97afd…`) |
| 3 | **35** | **20** | **18070** | `18677` (`CIT`) | **−607** | `35` | `PGL(2,19)+CCL(M=23,cc=0,+20)` | `0.371s` | `24.567s` | [`CA_18070_3_35_20.txt`](../results/CA_18070_3_35_20.txt) (`8751d063aed3ef33…`) |
| 3 | **38** | **20** | **18240** | `18753` (`CIT`) | **−513** | `36..38` *(k=36: −437)* | `PGL(2,19)+CCL(M=24,cc=1)` | `0.444s` | `32.603s` | [`CA_18240_3_38_20.txt`](../results/CA_18240_3_38_20.txt) (`68678d1c01540b94…`) |

### Explizit mitgeführte Projektions-Begleitdateien in `results/` (ebenfalls dual-verifiziert)
Zusätzlich zur strengen 13er-Pareto-Front liegen drei projizierte Begleitdateien aus v2/v3 in `results/` (alle 16 Dateien zusammen `9,5 MB`, `32/32` SHA-256 OK und alle 16 durch `verify_all.sh` dual-verifiziert):
- `results/CA_2160_3_17_10.txt` (`sha256: 5e199bb6872a68d1…`, `ca 0.010s`, `py 0.272s`) — dominiert von `CA_2160_3_18_10.txt`
- `results/CA_6097_3_23_14.txt` (`sha256: 3927e2d354e405ac…`, `ca 0.035s`, `py 2.267s`) — dominiert von `CA_6097_3_24_14.txt`
- `results/CA_6188_3_25_14.txt` (`sha256: 41befba9ae17253c…`, `ca 0.039s`, `py 2.714s`) — dominiert von `CA_6188_3_26_14.txt`

## 3. Reproduzierbarkeit & Voll-Audit

```bash
./submission/verify_all.sh
```
Prüft in einem Durchlauf:
1. `sha256sum -c verifiers/SHA256SUMS` (3/3 OK) & `git diff main -- verifiers/` (leer)
2. `python3 verifiers/test_verifiers.py` (23/23 PASS)
3. `env -C results sha256sum -c SHA256SUMS` (32/32 OK)
4. Strikter `ca-tools`-Format-Audit aller 16 `results/CA_*.txt`
5. Frische parallele Dual-Verifikation (`xargs -P 2`) aller 16 `results/CA_*.txt` durch `./verifiers/ca_verify` und `python3 verifiers/verify_independent.py`

Kompakte Starter-Matrizen liegen zusätzlich unter `data/ccl_binary/` (`16` Dateien, `68 KB`) und lassen sich per `pgl_ccl_search expand --q <q> --in-bin <file> --out-ca <out>` bit-exakt reproduzieren.
