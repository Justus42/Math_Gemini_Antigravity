# `ca3_search` — Zero-Dependency Rust Solver for Strength-3 Covering Arrays

Native Rust (`std`-only, zero external crates) incremental local-search solver for covering arrays $\mathrm{CA}(N; 3, k, v)$ with L1-cache-resident flat interaction counts, focused WalkSAT/Tabu + adaptive-thermostat Metropolis hybrid, 2-thread deterministic multi-start (`SplitMix64` + `Xoshiro256**`), and atomic checkpointing/resume.

## Build

```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release --manifest-path solvers/ca3_search/Cargo.toml
```

## Sanity Check

Verifies exact incremental counts & delta evaluation over 10,000 moves against full recomputation (0 discrepancies required) for both `CaState` and `OrbitState`:

```bash
./solvers/ca3_search/target/release/ca3_search sanity \
  --input baselines/CA_185_3_10_5.txt --k 9 --v 5 --n 180
```

## Modes

- **`reduce`**: Drops minimum-exclusivity row(s) from an existing CA (or `k`-column projection via `--drop-col <idx|all>`) and repairs; supports `--resume <checkpoint_matrix>`.
- **`extend`**: Extends a `(k-1)`-column baseline (e.g. `baselines/CA_165_3_8_5.txt`) via greedy column + repair-row initialization, locked Stage 1 optimization, and unfrozen Stage 2 search.
- **`orbit`**: Searches cyclic $\mathbb{Z}_v$-developed starter rows in the $v^2$-quotient orbit space (with optional `--const-rows 0|v`), followed by optional unfrozen cell-level polishing (`--unfreeze-frac`).
