# Dual-Verification Log — Phase 4 (`exp/pgl-binary-ccl`)
Timestamp (UTC): 2026-11-25T07:24:06Z
Solver: `solvers/pgl_ccl_search` (Zero-Dep Rust `std`-only, `--release -C target-cpu=native`)

## `CA_2070_3_15_10.txt` (Live-Rekord: `2205`, Delta: `-135`)
- Konstruktion: `PGL(2,9)` (`2*720`) + Binary-CCL `M=14 x k=15` (`cover_const=1`, `45` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=5008`, Suchzeit `0.863s`
- Starter-Datei: `results/CA_2070_3_15_10.ccl.bin` (`sha256: e89b647b82cf07a8e869f0a8272047b1157f008e9f6b22e9c58fb4a6cf1d638c`)
- Array-Datei: `results/CA_2070_3_15_10.txt` (`62100` Bytes, `sha256: 78b0497f2c81b0f72b9a454c7fbf42a3d66f1e31851be5f568c95d7f584c1865`)
- Expand: `EXPANDED results/CA_2070_3_15_10.ccl.bin -> results/CA_2070_3_15_10.txt (N=2070 t=3 k=15 v=10 m=14 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_2070_3_15_10.txt 3 10`): **rc=0** (`0.006 s`)
  > VERIFIED: CA(N=2070; t=3, k=15, v=10) - all 455 column sets fully cover all 1000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_2070_3_15_10.txt 3 10 -n 2070 -k 15`): **rc=0** (`0.223 s`)
  > VERIFIED: CA(N=2070; t=3, k=15, v=10) - all 455 column sets cover all 1000 tuples (455000 total interactions) [elapsed: 0.1648s]

## `CA_2115_3_16_10.txt` (Live-Rekord: `2205`, Delta: `-90`)
- Konstruktion: `PGL(2,9)` (`2*720`) + Binary-CCL `M=15 x k=16` (`cover_const=1`, `45` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=5002`, Suchzeit `0.027s`
- Starter-Datei: `results/CA_2115_3_16_10.ccl.bin` (`sha256: 382bfecbbebf3b8c665d1c644f3ca33be4efa814b44802e0cca9a702269a8ba0`)
- Array-Datei: `results/CA_2115_3_16_10.txt` (`67680` Bytes, `sha256: 4734fd80ffe90f11664912e113b045ba599cbeb4a0bc749729764b7f700b86b4`)
- Expand: `EXPANDED results/CA_2115_3_16_10.ccl.bin -> results/CA_2115_3_16_10.txt (N=2115 t=3 k=16 v=10 m=15 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_2115_3_16_10.txt 3 10`): **rc=0** (`0.006 s`)
  > VERIFIED: CA(N=2115; t=3, k=16, v=10) - all 560 column sets fully cover all 1000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_2115_3_16_10.txt 3 10 -n 2115 -k 16`): **rc=0** (`0.251 s`)
  > VERIFIED: CA(N=2115; t=3, k=16, v=10) - all 560 column sets cover all 1000 tuples (560000 total interactions) [elapsed: 0.1964s]

## `CA_2160_3_17_10.txt` (Live-Rekord: `2232`, Delta: `-72`)
- Konstruktion: `PGL(2,9)` (`2*720`) + Binary-CCL `M=16 x k=17` (`cover_const=1`, `45` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=5005`, Suchzeit `0.019s (proj k=18)`
- Starter-Datei: `results/CA_2160_3_17_10.ccl.bin` (`sha256: 872267a9ee735feba1569950640b2baf68d9ff75af1d7d0fdbcd9734787a6885`)
- Array-Datei: `results/CA_2160_3_17_10.txt` (`73440` Bytes, `sha256: 5e199bb6872a68d1c45a9436911112e3f7ba6c77a4e5f25b7f6a7630c56cd751`)
- Expand: `EXPANDED results/CA_2160_3_17_10.ccl.bin -> results/CA_2160_3_17_10.txt (N=2160 t=3 k=17 v=10 m=16 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_2160_3_17_10.txt 3 10`): **rc=0** (`0.006 s`)
  > VERIFIED: CA(N=2160; t=3, k=17, v=10) - all 680 column sets fully cover all 1000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_2160_3_17_10.txt 3 10 -n 2160 -k 17`): **rc=0** (`0.281 s`)
  > VERIFIED: CA(N=2160; t=3, k=17, v=10) - all 680 column sets cover all 1000 tuples (680000 total interactions) [elapsed: 0.2298s]

## `CA_2160_3_18_10.txt` (Live-Rekord: `2232`, Delta: `-72`)
- Konstruktion: `PGL(2,9)` (`2*720`) + Binary-CCL `M=16 x k=18` (`cover_const=1`, `45` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=5005`, Suchzeit `0.019s`
- Starter-Datei: `results/CA_2160_3_18_10.ccl.bin` (`sha256: fd4088607ac4b71f05fe064328471bf8ad9b521c39f72350df931e95c79744d3`)
- Array-Datei: `results/CA_2160_3_18_10.txt` (`77760` Bytes, `sha256: 410ccbcc821c8db43a9274344ddb37c1c82f401b7c7a2ddb245cdbb9e567686a`)
- Expand: `EXPANDED results/CA_2160_3_18_10.ccl.bin -> results/CA_2160_3_18_10.txt (N=2160 t=3 k=18 v=10 m=16 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_2160_3_18_10.txt 3 10`): **rc=0** (`0.007 s`)
  > VERIFIED: CA(N=2160; t=3, k=18, v=10) - all 816 column sets fully cover all 1000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_2160_3_18_10.txt 3 10 -n 2160 -k 18`): **rc=0** (`0.325 s`)
  > VERIFIED: CA(N=2160; t=3, k=18, v=10) - all 816 column sets cover all 1000 tuples (816000 total interactions) [elapsed: 0.2733s]

## `CA_3696_3_19_12.txt` (Live-Rekord: `3806`, Delta: `-110`)
- Konstruktion: `PGL(2,11)` (`2*1320`) + Binary-CCL `M=16 x k=19` (`cover_const=1`, `66` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=6006`, Suchzeit `4.290s`
- Starter-Datei: `results/CA_3696_3_19_12.ccl.bin` (`sha256: 59f224748781fce1f9bdd3e946fdf838f024bb7ae50dc8941b7270441141bd6a`)
- Array-Datei: `results/CA_3696_3_19_12.txt` (`152152` Bytes, `sha256: 2492d0f7e36a993defeb9cef1ecbc58284d900f8842809c6019b01cbec4f2514`)
- Expand: `EXPANDED results/CA_3696_3_19_12.ccl.bin -> results/CA_3696_3_19_12.txt (N=3696 t=3 k=19 v=12 m=16 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_3696_3_19_12.txt 3 12`): **rc=0** (`0.018 s`)
  > VERIFIED: CA(N=3696; t=3, k=19, v=12) - all 969 column sets fully cover all 1728 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_3696_3_19_12.txt 3 12 -n 3696 -k 19`): **rc=0** (`0.598 s`)
  > VERIFIED: CA(N=3696; t=3, k=19, v=12) - all 969 column sets cover all 1728 tuples (1674432 total interactions) [elapsed: 0.5411s]

## `CA_3762_3_20_12.txt` (Live-Rekord: `3806`, Delta: `-44`)
- Konstruktion: `PGL(2,11)` (`2*1320`) + Binary-CCL `M=17 x k=20` (`cover_const=1`, `66` orientierte Paare)
- Suche: `algo=hybrid`, `threads=2`, `seed=6001`, Suchzeit `0.358s`
- Starter-Datei: `results/CA_3762_3_20_12.ccl.bin` (`sha256: 1ac1c31d8b6c76b152a493fd2230e5468947807fe0c4ecc9d481f02496ca7057`)
- Array-Datei: `results/CA_3762_3_20_12.txt` (`163092` Bytes, `sha256: 6a85d1b1e34aec7305d588775ab14005a29bea18f2d0931b56f9e58fb61572d4`)
- Expand: `EXPANDED results/CA_3762_3_20_12.ccl.bin -> results/CA_3762_3_20_12.txt (N=3762 t=3 k=20 v=12 m=17 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_3762_3_20_12.txt 3 12`): **rc=0** (`0.015 s`)
  > VERIFIED: CA(N=3762; t=3, k=20, v=12) - all 1140 column sets fully cover all 1728 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_3762_3_20_12.txt 3 12 -n 3762 -k 20`): **rc=0** (`0.731 s`)
  > VERIFIED: CA(N=3762; t=3, k=20, v=12) - all 1140 column sets cover all 1728 tuples (1969920 total interactions) [elapsed: 0.6802s]

