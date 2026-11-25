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


---
# Dual-Verification Log — Phase 4 v3 (`PGL(2,13)`, `v=14`, `exp/pgl-binary-ccl-v3`)
Timestamp (UTC): 2026-11-25T08:33:15Z

## `CA_5915_3_20_14.txt` (Live-Rekord: `6006`, Delta: `-91`)
- Konstruktion: `PGL(2,13)` (`2*2184`) + Binary-CCL `M=17 x k=20` (`cover_const=1`, `91` orientierte Paare) + Post-Op (`saved=0`)
- Suche: `algo=hybrid`, `threads=2`, `seed=6001`, Suchzeit `0.358s (reused k=20 M=17)`
- Starter-Datei: `results/CA_5915_3_20_14.ccl.bin` (`sha256: 1ac1c31d8b6c76b152a493fd2230e5468947807fe0c4ecc9d481f02496ca7057`)
- Array-Datei: `results/CA_5915_3_20_14.txt` (`270552` Bytes, `sha256: 051a4841f551770fd09e84ffd805edf4d3b7c13b435c9687598c14b939d29a3d`)
- Post-Op: `REDUCED /tmp/pgl_ccl_v14/exp_3_20_14.txt -> /tmp/pgl_ccl_v14/red_3_20_14.txt (k=20 v=14 N: 5915 -> 5915, saved=0, elapsed=0.170s)`
- Verifier 1 (`./verifiers/ca_verify results/CA_5915_3_20_14.txt 3 14`): **rc=0** (`0.023 s`)
  > VERIFIED: CA(N=5915; t=3, k=20, v=14) - all 1140 column sets fully cover all 2744 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_5915_3_20_14.txt 3 14 -n 5915 -k 20`): **rc=0** (`1.450 s`)
  > VERIFIED: CA(N=5915; t=3, k=20, v=14) - all 1140 column sets cover all 2744 tuples (3128160 total interactions) [elapsed: 1.3898s]

## `CA_6097_3_23_14.txt` (Live-Rekord: `6279`, Delta: `-182`)
- Konstruktion: `PGL(2,13)` (`2*2184`) + Binary-CCL `M=19 x k=23` (`cover_const=1`, `91` orientierte Paare) + Post-Op (`saved=0`)
- Suche: `algo=hybrid`, `threads=2`, `seed=9102`, Suchzeit `5.405s (proj k=24)`
- Starter-Datei: `results/CA_6097_3_23_14.ccl.bin` (`sha256: 9efbb7ec5e9ac19686c72f93828ef59abcbc32e197499c1ddcdefffbeac52df9`)
- Array-Datei: `results/CA_6097_3_23_14.txt` (`320547` Bytes, `sha256: 3927e2d354e405acb7c4750bf72bb5fe710b3f7c879f034871773080a0b2afd8`)
- Post-Op: `REDUCED /tmp/pgl_ccl_v14/exp_3_23_14.txt -> /tmp/pgl_ccl_v14/red_3_23_14.txt (k=23 v=14 N: 6097 -> 6097, saved=0, elapsed=0.405s)`
- Verifier 1 (`./verifiers/ca_verify results/CA_6097_3_23_14.txt 3 14`): **rc=0** (`0.030 s`)
  > VERIFIED: CA(N=6097; t=3, k=23, v=14) - all 1771 column sets fully cover all 2744 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_6097_3_23_14.txt 3 14 -n 6097 -k 23`): **rc=0** (`2.176 s`)
  > VERIFIED: CA(N=6097; t=3, k=23, v=14) - all 1771 column sets cover all 2744 tuples (4859624 total interactions) [elapsed: 2.1228s]

## `CA_6097_3_24_14.txt` (Live-Rekord: `6279`, Delta: `-182`)
- Konstruktion: `PGL(2,13)` (`2*2184`) + Binary-CCL `M=19 x k=24` (`cover_const=1`, `91` orientierte Paare) + Post-Op (`saved=0`)
- Suche: `algo=hybrid`, `threads=2`, `seed=9102`, Suchzeit `5.405s`
- Starter-Datei: `results/CA_6097_3_24_14.ccl.bin` (`sha256: dbeb866bee291c0c6ecb0e0681f07b3610a1171fcd4ecf160d1c91fa8cc0d815`)
- Array-Datei: `results/CA_6097_3_24_14.txt` (`334464` Bytes, `sha256: 3abb40a4dcb501e3d34512aab8c11398248f629c72e4e9bba1916919f21ffdbb`)
- Post-Op: `REDUCED /tmp/pgl_ccl_v14/exp_3_24_14.txt -> /tmp/pgl_ccl_v14/red_3_24_14.txt (k=24 v=14 N: 6097 -> 6097, saved=0, elapsed=0.485s)`
- Verifier 1 (`./verifiers/ca_verify results/CA_6097_3_24_14.txt 3 14`): **rc=0** (`0.031 s`)
  > VERIFIED: CA(N=6097; t=3, k=24, v=14) - all 2024 column sets fully cover all 2744 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_6097_3_24_14.txt 3 14 -n 6097 -k 24`): **rc=0** (`2.539 s`)
  > VERIFIED: CA(N=6097; t=3, k=24, v=14) - all 2024 column sets cover all 2744 tuples (5553856 total interactions) [elapsed: 2.4837s]

## `CA_6188_3_25_14.txt` (Live-Rekord: `6383`, Delta: `-195`)
- Konstruktion: `PGL(2,13)` (`2*2184`) + Binary-CCL `M=20 x k=25` (`cover_const=1`, `91` orientierte Paare) + Post-Op (`saved=0`)
- Suche: `algo=hybrid`, `threads=2`, `seed=9107`, Suchzeit `2.020s (proj k=26)`
- Starter-Datei: `results/CA_6188_3_25_14.ccl.bin` (`sha256: 857f3b00f67800023d622920e824f7e2739b6f977a884927701c8c9047a42bcc`)
- Array-Datei: `results/CA_6188_3_25_14.txt` (`353562` Bytes, `sha256: 41befba9ae17253cdcfbf1b5a7b17c0ca766a08819c11135dee47f4cabdd57dc`)
- Post-Op: `REDUCED /tmp/pgl_ccl_v14/exp_3_25_14.txt -> /tmp/pgl_ccl_v14/red_3_25_14.txt (k=25 v=14 N: 6188 -> 6188, saved=0, elapsed=0.596s)`
- Verifier 1 (`./verifiers/ca_verify results/CA_6188_3_25_14.txt 3 14`): **rc=0** (`0.034 s`)
  > VERIFIED: CA(N=6188; t=3, k=25, v=14) - all 2300 column sets fully cover all 2744 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_6188_3_25_14.txt 3 14 -n 6188 -k 25`): **rc=0** (`2.849 s`)
  > VERIFIED: CA(N=6188; t=3, k=25, v=14) - all 2300 column sets cover all 2744 tuples (6311200 total interactions) [elapsed: 2.7873s]

## `CA_6188_3_26_14.txt` (Live-Rekord: `6383`, Delta: `-195`)
- Konstruktion: `PGL(2,13)` (`2*2184`) + Binary-CCL `M=20 x k=26` (`cover_const=1`, `91` orientierte Paare) + Post-Op (`saved=0`)
- Suche: `algo=hybrid`, `threads=2`, `seed=9107`, Suchzeit `2.020s`
- Starter-Datei: `results/CA_6188_3_26_14.ccl.bin` (`sha256: bc8d2d0718e3908a690fca00ecac38eb3610ac0b220ea8e918f024b54968d810`)
- Array-Datei: `results/CA_6188_3_26_14.txt` (`367706` Bytes, `sha256: 2952b2efb82ae2087c6c0d560a80bdf1d64409b6b1a42e1d17418f2978396eaa`)
- Post-Op: `REDUCED /tmp/pgl_ccl_v14/exp_3_26_14.txt -> /tmp/pgl_ccl_v14/red_3_26_14.txt (k=26 v=14 N: 6188 -> 6188, saved=0, elapsed=0.711s)`
- Verifier 1 (`./verifiers/ca_verify results/CA_6188_3_26_14.txt 3 14`): **rc=0** (`0.035 s`)
  > VERIFIED: CA(N=6188; t=3, k=26, v=14) - all 2600 column sets fully cover all 2744 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_6188_3_26_14.txt 3 14 -n 6188 -k 26`): **rc=0** (`3.109 s`)
  > VERIFIED: CA(N=6188; t=3, k=26, v=14) - all 2600 column sets cover all 2744 tuples (7134400 total interactions) [elapsed: 3.0544s]


---
# Dual-Verification Log — Phase 4 v4 (`PGL(2,19)`, `v=20` Pareto-Front, `exp/pgl-binary-ccl-v4`)
Timestamp (UTC): 2026-11-25T08:59:56Z

## `CA_17670_3_29_20.txt` (Live-Rekord: `18145`, Delta: `-475`)
- Dominierte Zellen: k=27..29 (k=27,28 live 17936 -> -266)
- Konstruktion: `PGL(2,19)` (`2*6840`) + Binary-CCL `M=21 x k=29` (`cover_const=1`, `190` orientierte Paare)
- Suche: `threads=2`, `seed=11003`, Suchzeit `1.503s (paws)`
- Starter-Datei: `results/CA_17670_3_29_20.ccl.bin` (`sha256: aa318295b830408e3ef174ce0853ccbde5f038561158150ea8ad417fa8790a04`)
- Array-Datei: `results/CA_17670_3_29_20.txt` (`1280830` Bytes, `sha256: 739bf030ad8234a83c9e3fb057b15798918881afe1a82302be5cfb8cad35e58a`)
- Expand: `EXPANDED results/CA_17670_3_29_20.ccl.bin -> results/CA_17670_3_29_20.txt (N=17670 t=3 k=29 v=20 m=21 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_17670_3_29_20.txt 3 20`): **rc=0** (`0.439 s`)
  > VERIFIED: CA(N=17670; t=3, k=29, v=20) - all 3654 column sets fully cover all 8000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_17670_3_29_20.txt 3 20 -n 17670 -k 29`): **rc=0** (`14.419 s`)
  > VERIFIED: CA(N=17670; t=3, k=29, v=20) - all 3654 column sets cover all 8000 tuples (29232000 total interactions) [elapsed: 14.3138s]

## `CA_17860_3_32_20.txt` (Live-Rekord: `18145`, Delta: `-285`)
- Dominierte Zellen: k=30..32 (live 18145 -> -285)
- Konstruktion: `PGL(2,19)` (`2*6840`) + Binary-CCL `M=22 x k=32` (`cover_const=1`, `190` orientierte Paare)
- Suche: `threads=2`, `seed=10009`, Suchzeit `4.388s (hybrid)`
- Starter-Datei: `results/CA_17860_3_32_20.ccl.bin` (`sha256: eb653e2e1d3c3aace44f713d21e7205354cbac083ae8734c6b85194b26113871`)
- Array-Datei: `results/CA_17860_3_32_20.txt` (`1428800` Bytes, `sha256: 544735d32928b02dc0b423627a10aa57a4eba2c853e542df5c4dc5953098061c`)
- Expand: `EXPANDED results/CA_17860_3_32_20.ccl.bin -> results/CA_17860_3_32_20.txt (N=17860 t=3 k=32 v=20 m=22 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_17860_3_32_20.txt 3 20`): **rc=0** (`0.522 s`)
  > VERIFIED: CA(N=17860; t=3, k=32, v=20) - all 4960 column sets fully cover all 8000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_17860_3_32_20.txt 3 20 -n 17860 -k 32`): **rc=0** (`19.794 s`)
  > VERIFIED: CA(N=17860; t=3, k=32, v=20) - all 4960 column sets cover all 8000 tuples (39680000 total interactions) [elapsed: 19.7319s]

## `CA_18050_3_34_20.txt` (Live-Rekord: `18430`, Delta: `-380`)
- Dominierte Zellen: k=33..34 (live 18430 -> -380)
- Konstruktion: `PGL(2,19)` (`2*6840`) + Binary-CCL `M=23 x k=34` (`cover_const=1`, `190` orientierte Paare)
- Suche: `threads=2`, `seed=10006`, Suchzeit `0.673s (hybrid)`
- Starter-Datei: `results/CA_18050_3_34_20.ccl.bin` (`sha256: 016a7f0305b9ed13c63c1e3f95d8526d70fa26e66e5c83b366be0d0db915e3a3`)
- Array-Datei: `results/CA_18050_3_34_20.txt` (`1534544` Bytes, `sha256: 9224fbac04d97afd78c001da51fe7f92f7f9c4b760317819d9dd7bb68c5ff4d0`)
- Expand: `EXPANDED results/CA_18050_3_34_20.ccl.bin -> results/CA_18050_3_34_20.txt (N=18050 t=3 k=34 v=20 m=23 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_18050_3_34_20.txt 3 20`): **rc=0** (`0.374 s`)
  > VERIFIED: CA(N=18050; t=3, k=34, v=20) - all 5984 column sets fully cover all 8000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_18050_3_34_20.txt 3 20 -n 18050 -k 34`): **rc=0** (`24.601 s`)
  > VERIFIED: CA(N=18050; t=3, k=34, v=20) - all 5984 column sets cover all 8000 tuples (47872000 total interactions) [elapsed: 24.5459s]

## `CA_18070_3_35_20.txt` (Live-Rekord: `18677`, Delta: `-607`)
- Dominierte Zellen: k=35 (live 18677 -> -607)
- Konstruktion: `PGL(2,19)` (`2*6840`) + Binary-CCL `M=23 x k=35` (`cover_const=0`, `190` orientierte Paare + 20 const)
- Suche: `threads=2`, `seed=10020`, Suchzeit `1.882s (hybrid)`
- Starter-Datei: `results/CA_18070_3_35_20.ccl.bin` (`sha256: 09f17abf37881d49c2897901576ba7b03dc2c8fd6331c28d32efce2a95486541`)
- Array-Datei: `results/CA_18070_3_35_20.txt` (`1581468` Bytes, `sha256: 8751d063aed3ef33322c7252dfee57abfa9a705ab4490da2b9d9eb5300b855ad`)
- Expand: `EXPANDED results/CA_18070_3_35_20.ccl.bin -> results/CA_18070_3_35_20.txt (N=18070 t=3 k=35 v=20 m=23 cover_const=0)`
- Verifier 1 (`./verifiers/ca_verify results/CA_18070_3_35_20.txt 3 20`): **rc=0** (`0.405 s`)
  > VERIFIED: CA(N=18070; t=3, k=35, v=20) - all 6545 column sets fully cover all 8000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_18070_3_35_20.txt 3 20 -n 18070 -k 35`): **rc=0** (`27.935 s`)
  > VERIFIED: CA(N=18070; t=3, k=35, v=20) - all 6545 column sets cover all 8000 tuples (52360000 total interactions) [elapsed: 27.8792s]

## `CA_18240_3_38_20.txt` (Live-Rekord: `18753`, Delta: `-513`)
- Dominierte Zellen: k=36..38 (k=36 live 18677 -> -437; k=37,38 live 18753 -> -513)
- Konstruktion: `PGL(2,19)` (`2*6840`) + Binary-CCL `M=24 x k=38` (`cover_const=1`, `190` orientierte Paare)
- Suche: `threads=2`, `seed=10001`, Suchzeit `0.590s (hybrid)`
- Starter-Datei: `results/CA_18240_3_38_20.ccl.bin` (`sha256: 733b432e86db12c51075ae84a7824d236f0bee54d5568be07590a00745a14695`)
- Array-Datei: `results/CA_18240_3_38_20.txt` (`1732800` Bytes, `sha256: 68678d1c01540b943656d81908a86857ee0a1ff445b76863e072d27aef5e80cb`)
- Expand: `EXPANDED results/CA_18240_3_38_20.ccl.bin -> results/CA_18240_3_38_20.txt (N=18240 t=3 k=38 v=20 m=24 cover_const=1)`
- Verifier 1 (`./verifiers/ca_verify results/CA_18240_3_38_20.txt 3 20`): **rc=0** (`0.458 s`)
  > VERIFIED: CA(N=18240; t=3, k=38, v=20) - all 8436 column sets fully cover all 8000 tuples
- Verifier 2 (`python3 verifiers/verify_independent.py results/CA_18240_3_38_20.txt 3 20 -n 18240 -k 38`): **rc=0** (`33.304 s`)
  > VERIFIED: CA(N=18240; t=3, k=38, v=20) - all 8436 column sets cover all 8000 tuples (67488000 total interactions) [elapsed: 33.2486s]

