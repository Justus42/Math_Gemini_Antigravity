# `ca3_search` — Zero-Dependency Rust Solver for Strength-3 Covering Arrays

Native Rust (`std`-only, zero external crates) incremental local-search solver for covering arrays $\mathrm{CA}(N; 3, k, v)$ with L1-cache-resident flat interaction counts, time-based geometric Simulated Annealing + Endgame Exact Full-Focused-Neighborhood Tabu (`unc <= 25`), cyclic $\mathbb{Z}_v$ and order-$2v$ ($G_{10}$) orbit quotient spaces, 2-thread deterministic multi-start (`SplitMix64` + `Xoshiro256**`), and atomic checkpointing/resume.

## Build

```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release --manifest-path solvers/ca3_search/Cargo.toml
```

## Sanity Check

Verifies exact incremental counts & delta evaluation over 10,000 moves against full recomputation (0 discrepancies required) for `CaState`, `OrbitState(Z5)` (5× expansion invariant), and `OrbitState(G10)` (10× expansion invariant):

```bash
./solvers/ca3_search/target/release/ca3_search sanity \
  --input baselines/CA_185_3_10_5.txt --k 9 --v 5 --n 180
```

## Modes

- **`orbit`**: Searches starter rows under `--group z5` ($x \mapsto x + b \pmod 5$, orbit size 5) or `--group g10` ($x \mapsto s x + b \pmod 5, s \in \{1,4\}$, orbit size 10, 12 non-constant orbits/triple) with optional `--const-rows 0|v`, time-based geometric SA (`--t-start`, `--t-end`), endgame full-focused Tabu (`--endgame`), and optional `--free-rows R` hybrid polishing.
- **`hybrid`**: Loads an expanded orbit or baseline checkpoint (`--input`), appends `--free-rows R` greedy-initialized repair rows focused on uncovered triples, optimizes the `R` free rows in Stage 1 (`--stage1-secs`), then unfreezes the full array in Stage 2 (auto-reducing toward `--min-n` if `unc == 0`).
- **`reduce`**: Drops minimum-exclusivity row(s) from an existing CA (or `k`-column projection via `--drop-col <idx|all>`) and repairs; supports `--resume <checkpoint_matrix>`.
- **`extend`**: Extends a `(k-1)`-column baseline (e.g. `baselines/CA_165_3_8_5.txt`) via greedy column + repair-row initialization, locked Stage 1, and unfrozen Stage 2.
