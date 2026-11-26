#!/usr/bin/env python3
"""Phase 5E: Deterministic Pure-Python generator for CA(q^4 + (q(q-1)/2)q^2; 4, q + 2, q).

Pure Python (std-only). No solver, no search, no randomness, no precomputed colorings.

Mathematical construction (prime powers q in {7, 8, 9, 11, 13}):
  Builds on Bush (1952) OA(q^4; 4, q + 1, q), Jamison (1977) / Brouwer-Schrijver (1978)
  affine blocking-set lower bound |B| >= 2q - 1 in AG(2, q), and Bai XunDi (2026)
  poly2 / line-polychromatic framework (polychrome-bai2026).

  For any prime power q and any tournament orientation T on GF(q) (default: transitive
  order 0 < 1 < ... < q - 1):
    - Block 1 (Bush OA(q^4; 4, q + 1, q) on cols 0..q, plus col_{q+1}):
        For all (a, b, c, d) in GF(q)^4:
          row(a, b, c, d) = ((a + b*x + c*x^2 + d*x^3)_{x in GF(q)}, d, min(c, d))
    - Block 2 ((q(q - 1)/2) * q^2 extra OA(q^2) polynomial slices with decoupled col_inf):
        For all 0 <= c < d < q and all (a, b) in GF(q)^2:
          row'(a, b, c, d) = ((a + b*x + c*x^2 + d*x^3)_{x in GF(q)}, c, d)

  Every symbol m in GF(q) covers:
    1) All q values of col_inf: {m, ..., q-1} via Bush fibers (m, d) with d >= m,
       plus {0, ..., m-1} via extra slices (c, m, col_inf=c) with c < m.
    2) All q^2 non-horizontal affine lines c + S*d = r in AG(2, q): the union of
       Bush fibers {(c, m) : c >= m} and extra slices {(c, m) : c < m} is the entire
       horizontal line d = m of AG(2, q).

  Total rows:
    N(q) = q^4 + (q(q - 1)/2) * q^2 = q^3 * (3q - 1) / 2.
  This achieves the exact Jamison/Brouwer-Schrijver lower bound b_m + 2*e_m >= 2q - 1
  for every symbol m in GF(q) (zero waste; savings of floor(q/2)*q^2 rows vs. Bai Kor. 5.3 /
  Prop. 5.4).

  An optional balanced cyclic-tournament variant (--variant cyclic) is also provided for
  odd q, achieving the exact same N(q) with equal symbol multiplicity (3q - 1)/2 * q^2.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gen_t4_odd_q_nearbush import GF, write_array_and_sha256  # noqa: E402


def build_decoupled_tournament(q: int, variant: str = "transitive") -> list[tuple[int, ...]]:
    """Build CA(q^4 + (q(q - 1)/2)q^2; 4, q + 2, q) deterministically over GF(q)."""
    gf = GF(q)
    add, mul, x2, x3 = gf.add, gf.mul, gf.x2, gf.x3

    sym_map = [0] * (q * q)
    extras: list[tuple[int, int, int, int]] = []  # (c, d, col_inf, col_{q+1})

    if variant == "transitive":
        # col_{q+1}(c, d) = min(c, d); extras = {(c, d, c, d) : 0 <= c < d < q}
        for d in range(q):
            for c in range(d):
                sym_map[c * q + d] = c
                extras.append((c, d, c, d))
            for c in range(d, q):
                sym_map[c * q + d] = d
    elif variant == "cyclic":
        if q % 2 == 0:
            raise ValueError("Cyclic tournament variant requires odd q")
        half = (q - 1) // 2
        for d in range(q):
            for c in range(half + 1):
                sym_map[c * q + d] = d
            for j in range(1, half + 1):
                c = half + j
                sym_map[c * q + d] = (d + j) % q
        for m in range(q):
            for j in range(1, half + 1):
                c = half + j
                extras.append((c, m, (m + j) % q, m))
    else:
        raise ValueError(f"Unknown variant: {variant}")

    # Verify per-symbol coverage invariants before emitting rows
    for m in range(q):
        bush_pts = {(c, d) for c in range(q) for d in range(q) if sym_map[c * q + d] == m}
        ext_m = [(c, d, ci) for (c, d, ci, mm) in extras if mm == m]
        # 1) col_inf coverage
        ci_cov = {d for (_, d) in bush_pts} | {ci for (_, _, ci) in ext_m}
        assert len(ci_cov) == q, f"sym {m} misses col_inf"
        # 2) horizontal line d = m coverage
        line_c = {c for (c, d) in bush_pts if d == m} | {c for (c, d, _) in ext_m if d == m}
        assert len(line_c) == q, f"sym {m} misses point on horizontal line d={m}"
        # 3) exact Jamison budget b_m + 2*e_m == 2q - 1
        assert len(bush_pts) + 2 * len(ext_m) == 2 * q - 1

    rows: list[tuple[int, ...]] = []
    # Block 1: full Bush OA(q^4; 4, q + 1, q) + col_{q+1}
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = [
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    ]
                    r.append(d)
                    r.append(sym_map[c * q + d])
                    rows.append(tuple(r))

    # Block 2: (q(q - 1)/2) decoupled OA(q^2) slices
    for c, d, ci, m in extras:
        for a in range(q):
            for b in range(q):
                r = [
                    add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                    for x in range(q)
                ]
                r.append(ci)
                r.append(m)
                rows.append(tuple(r))

    expected_n = q**4 + (q * (q - 1) // 2) * (q * q)
    assert len(rows) == expected_n
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic generator for CA(q^4 + (q(q-1)/2)q^2; 4, q + 2, q)"
    )
    parser.add_argument("--q", type=int, choices=[7, 8, 9, 11, 13], required=True)
    parser.add_argument(
        "--variant",
        choices=["transitive", "cyclic"],
        default="transitive",
        help="Tournament orientation: transitive (all q, col_{q+1}=min(c,d)) or cyclic (odd q, balanced)",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output canonical array path")
    args = parser.parse_args()

    t0 = time.perf_counter()
    rows = build_decoupled_tournament(args.q, variant=args.variant)
    sha = write_array_and_sha256(args.out, rows)
    dt = time.perf_counter() - t0
    print(
        f"variant={args.variant} CA({len(rows)}; 4, {args.q + 2}, {args.q}) "
        f"sha256={sha} elapsed={dt:.3f}s -> {args.out}"
    )


if __name__ == "__main__":
    main()
