# Deterministische Reproduktion & SHA-256-Prüfung (`submission/REPRODUCE.md`)

Gemäß `RULES.md` Abschnitt *Meldung nach außen*, Punkt 2e: Alle 13 Pareto-Front-Arrays in [`submission/ca_tools_staging/`](ca_tools_staging/) und [`results/`](../results/) werden bit-identisch aus den gespeicherten binären Startmatrizen unter [`data/ccl_binary/`](../data/ccl_binary/) erzeugt.

Zuletzt vollständig nachgeprüft nach `/tmp/repro_check/`: **2026-11-25** (**13/13 byte-identische SHA-256-Übereinstimmung** mit `submission/ca_tools_staging/` und `results/`).

## 1. Zero-Dependency-Solver bauen & Gruppen-Selbsttest ausführen

```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release --manifest-path solvers/pgl_ccl_search/Cargo.toml
solvers/pgl_ccl_search/target/release/pgl_ccl_search selftest
```

`selftest` prüft Körperaxiome, Gruppenordnung $|PGL(2,q)| = q(q^2 - 1)$, Bijektivität, paarweise Verschiedenheit und scharfe 3-Transitivität für $q \in \{5, 9, 11, 13, 16, 17, 19\}$ sowie die orientierte Paar-Expansion.

## 2. Alle 13 Pareto-Front-Arrays nach `/tmp/repro_check/` reproduzieren

```bash
BIN=solvers/pgl_ccl_search/target/release/pgl_ccl_search
OUT=/tmp/repro_check
rm -rf "$OUT" && mkdir -p "$OUT"

$BIN expand --q  9 --in-bin data/ccl_binary/ccl_k15_m14_cc1.bin --cover-const    --out-ca "$OUT/CA_2070_3_15_10.txt"
$BIN expand --q  9 --in-bin data/ccl_binary/ccl_k16_m15_cc1.bin --cover-const    --out-ca "$OUT/CA_2115_3_16_10.txt"
$BIN expand --q  9 --in-bin data/ccl_binary/ccl_k18_m16_cc1.bin --cover-const    --out-ca "$OUT/CA_2160_3_18_10.txt"
$BIN expand --q 11 --in-bin data/ccl_binary/ccl_k19_m16_cc1.bin --cover-const    --out-ca "$OUT/CA_3696_3_19_12.txt"
$BIN expand --q 11 --in-bin data/ccl_binary/ccl_k20_m17_cc1.bin --cover-const    --out-ca "$OUT/CA_3762_3_20_12.txt"
$BIN expand --q 13 --in-bin data/ccl_binary/ccl_k20_m17_cc1.bin --cover-const    --out-ca "$OUT/CA_5915_3_20_14.txt"
$BIN expand --q 13 --in-bin data/ccl_binary/ccl_k24_m19_cc1.bin --cover-const    --out-ca "$OUT/CA_6097_3_24_14.txt"
$BIN expand --q 13 --in-bin data/ccl_binary/ccl_k26_m20_cc1.bin --cover-const    --out-ca "$OUT/CA_6188_3_26_14.txt"
$BIN expand --q 19 --in-bin data/ccl_binary/ccl_k29_m21_cc1.bin --cover-const    --out-ca "$OUT/CA_17670_3_29_20.txt"
$BIN expand --q 19 --in-bin data/ccl_binary/ccl_k32_m22_cc1.bin --cover-const    --out-ca "$OUT/CA_17860_3_32_20.txt"
$BIN expand --q 19 --in-bin data/ccl_binary/ccl_k34_m23_cc1.bin --cover-const    --out-ca "$OUT/CA_18050_3_34_20.txt"
$BIN expand --q 19 --in-bin data/ccl_binary/ccl_k35_m23_cc0.bin --no-cover-const --out-ca "$OUT/CA_18070_3_35_20.txt"
$BIN expand --q 19 --in-bin data/ccl_binary/ccl_k38_m24_cc1.bin --cover-const    --out-ca "$OUT/CA_18240_3_38_20.txt"
```

## 3. SHA-256-Abgleich gegen `submission/ca_tools_staging/` und `results/`

```bash
for f in "$OUT"/CA_*.txt; do
    base="$(basename "$f")"
    cmp -s "$f" "submission/ca_tools_staging/$base" || { echo "DIFF staging: $base"; exit 1; }
    cmp -s "$f" "results/$base" || { echo "DIFF results: $base"; exit 1; }
done
sha256sum "$OUT"/CA_*.txt
```

## 4. Erwartete SHA-256-Hashes (13/13 verifiziert am 2026-11-25)

| Datei | Startdatei (`data/ccl_binary/`) | `q` | `cc` | SHA-256 |
| --- | --- | :-: | :-: | --- |
| `CA_2070_3_15_10.txt` | `ccl_k15_m14_cc1.bin` | 9 | 1 | `78b0497f2c81b0f72b9a454c7fbf42a3d66f1e31851be5f568c95d7f584c1865` |
| `CA_2115_3_16_10.txt` | `ccl_k16_m15_cc1.bin` | 9 | 1 | `4734fd80ffe90f11664912e113b045ba599cbeb4a0bc749729764b7f700b86b4` |
| `CA_2160_3_18_10.txt` | `ccl_k18_m16_cc1.bin` | 9 | 1 | `410ccbcc821c8db43a9274344ddb37c1c82f401b7c7a2ddb245cdbb9e567686a` |
| `CA_3696_3_19_12.txt` | `ccl_k19_m16_cc1.bin` | 11 | 1 | `2492d0f7e36a993defeb9cef1ecbc58284d900f8842809c6019b01cbec4f2514` |
| `CA_3762_3_20_12.txt` | `ccl_k20_m17_cc1.bin` | 11 | 1 | `6a85d1b1e34aec7305d588775ab14005a29bea18f2d0931b56f9e58fb61572d4` |
| `CA_5915_3_20_14.txt` | `ccl_k20_m17_cc1.bin` | 13 | 1 | `051a4841f551770fd09e84ffd805edf4d3b7c13b435c9687598c14b939d29a3d` |
| `CA_6097_3_24_14.txt` | `ccl_k24_m19_cc1.bin` | 13 | 1 | `3abb40a4dcb501e3d34512aab8c11398248f629c72e4e9bba1916919f21ffdbb` |
| `CA_6188_3_26_14.txt` | `ccl_k26_m20_cc1.bin` | 13 | 1 | `2952b2efb82ae2087c6c0d560a80bdf1d64409b6b1a42e1d17418f2978396eaa` |
| `CA_17670_3_29_20.txt` | `ccl_k29_m21_cc1.bin` | 19 | 1 | `739bf030ad8234a83c9e3fb057b15798918881afe1a82302be5cfb8cad35e58a` |
| `CA_17860_3_32_20.txt` | `ccl_k32_m22_cc1.bin` | 19 | 1 | `544735d32928b02dc0b423627a10aa57a4eba2c853e542df5c4dc5953098061c` |
| `CA_18050_3_34_20.txt` | `ccl_k34_m23_cc1.bin` | 19 | 1 | `9224fbac04d97afd78c001da51fe7f92f7f9c4b760317819d9dd7bb68c5ff4d0` |
| `CA_18070_3_35_20.txt` | `ccl_k35_m23_cc0.bin` | 19 | 0 | `8751d063aed3ef33322c7252dfee57abfa9a705ab4490da2b9d9eb5300b855ad` |
| `CA_18240_3_38_20.txt` | `ccl_k38_m24_cc1.bin` | 19 | 1 | `68678d1c01540b943656d81908a86857ee0a1ff445b76863e072d27aef5e80cb` |
