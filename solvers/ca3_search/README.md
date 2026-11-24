# `ca3_search` — Zero-Dependency Rust Solver for Strength-3 Covering Arrays

Native Rust (`std`-only, zero external crates) incremental local-search solver for covering arrays $\mathrm{CA}(N; 3, k, v)$ with L1-cache-resident flat interaction counts, non-freezing Focused Tabu + fractional fixed-point SWT Clause Weighting (`--algo tabu-cw`, `BASE_W=16..MAX_W=26`, $O(1)$ deduplicated full-scan), geometric Simulated Annealing (`--algo sa`, `--algo hybrid-sa-cw`), orbit quotient spaces (`--group z5 | g10 | agl5`), 2-thread deterministic multi-start (`SplitMix64` + `Xoshiro256**`), and atomic checkpointing/resume.

## Build

```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release --manifest-path solvers/ca3_search/Cargo.toml
```

## Sanity Check

Verifies exact incremental counts & delta evaluation over 10,000 moves against full recomputation (0 discrepancies required) for `CaState`, `OrbitState(Z5)` (5× expansion), `OrbitState(G10)` (10× expansion), and `OrbitState(AGL5)` (20× expansion):

```bash
./solvers/ca3_search/target/release/ca3_search sanity \
  --input baselines/CA_185_3_10_5.txt --k 9 --v 5 --n 180
```

## Modes

- **`orbit`**: Searches starter rows under `--group z5` (orbit size 5), `--group g10` (orbit size 10, 12 non-constant orbits/triple), or `--group agl5` ($\mathrm{AGL}(1,5)$, orbit size 20, 6 non-constant orbits/triple) with `--algo tabu-cw | sa`.
- **`extend`**: Extends a `(k-1)`-column baseline (e.g. `baselines/CA_165_3_8_5.txt`) via greedy column + repair-row initialization, locked Stage 1, and unfrozen Stage 2 (`--stage2-algo`).
- **`reduce`**: Drops minimum-exclusivity row(s) from an existing CA (or `k`-column projection via `--drop-col <idx|all>`) and repairs; supports `--resume <checkpoint_matrix>`.
- **`hybrid`**: Loads an existing matrix (`--input`), appends `--free-rows R` greedy repair rows, runs locked Stage 1 + unfrozen Stage 2.
