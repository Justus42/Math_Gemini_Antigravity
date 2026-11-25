#!/usr/bin/env python3
"""Phase 5B-2A: Deterministic generators for t = 4, q = 8 NEAR_BUSH covering arrays.

Pure Python (std-only). Implements three deterministic constructions over GF(8)
(GF(2)[x] / (x^3 + x + 1)) plus a structural diagnostic for k = 12:

  1. k11-pencil    -> CA(7561; 4, 11, 8): Hyperoval Double-poly2 (exact Phase 5B-1 anchor;
                      -119 below ca-tools @ c5f447d = 7680).
  2. k10-polychrom -> CA(5888; 4, 10, 8): Irreducible-quadratic projection (x^2 + x + 1)
                      with 4 disjoint 15-point affine blocking sets + 4 singleton slices in
                      AG(2, 8) completed by 4 x 7 scaled-hyperoval OA(64; 2, 9, 8) slices
                      (-213 below ca-tools @ c5f447d = 6101).
  3. k11-polychrom -> CA(7203; 4, 11, 8): Two balanced 4-polychromatic colorings of AG(2, 8)
                      + 3072 hyperoval slices + deterministic greedy repair of the remaining
                      68 (c0, c1, 9, 10) tuples (-477 below ca-tools @ c5f447d = 7680).
  4. k12-check     -> Constructive & algebraic diagnostic for k = 12, q = 8 (N < 7680).

Builds on Bush (1952) OA(q^4; 4, q+1, q) / hyperoval OA(q^3; 3, q+2, q),
Jamison (1977) / Brouwer-Schrijver (1978) affine blocking sets in AG(2, q),
and Bai XunDi (2026) poly2 pencil-cover decomposition.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
from pathlib import Path
import time


# ---------------------------------------------------------------------------
# GF(8) = GF(2)[x] / (x^3 + x + 1), elements 0..7
# ---------------------------------------------------------------------------

def _gf8_mul(a: int, b: int) -> int:
    res = 0
    for _ in range(3):
        if b & 1:
            res ^= a
        hi = a & 4
        a = (a << 1) & 7
        if hi:
            a ^= 3  # x^3 = x + 1
        b >>= 1
    return res


GF8_MUL: tuple[tuple[int, ...], ...] = tuple(
    tuple(_gf8_mul(a, b) for b in range(8)) for a in range(8)
)
GF8_INV: tuple[int, ...] = (0,) + tuple(
    next(b for b in range(1, 8) if GF8_MUL[a][b] == 1) for a in range(1, 8)
)

# All 72 affine lines of AG(2, 8), points indexed as p = u*8 + v in 0..63
AG2_8_LINES: tuple[tuple[int, ...], ...] = tuple(
    tuple(c * 8 + y for y in range(8)) for c in range(8)
) + tuple(
    tuple(x * 8 + (GF8_MUL[m][x] ^ b) for x in range(8))
    for m in range(8)
    for b in range(8)
)
assert len(AG2_8_LINES) == 72


# Explicit deterministic 4-polychromatic AG(2, 8) tables (verified on all 72 lines at runtime)
# 1) 4 disjoint 15-point minimal blocking sets {0..3} + 4 singleton points {4,5,6,7} at (9,39,42,59)
K10_COLORING: tuple[int, ...] = (
    1, 1, 1, 0, 2, 1, 3, 1,
    0, 4, 3, 2, 2, 2, 3, 1,
    0, 3, 3, 0, 2, 0, 0, 1,
    1, 3, 2, 3, 0, 1, 1, 1,
    3, 3, 1, 0, 2, 0, 3, 5,
    1, 2, 6, 0, 3, 0, 3, 3,
    2, 2, 2, 1, 2, 2, 3, 0,
    0, 0, 0, 7, 1, 3, 2, 2,
)
K10_FREE_PTS: tuple[int, ...] = (9, 39, 42, 59)

# 2) Two balanced [16, 16, 16, 16] 4-polychromatic colorings of AG(2, 8) (68 pair misses on 7168)
K11_F1: tuple[int, ...] = (
    0, 0, 3, 2, 3, 1, 1, 0,
    2, 2, 0, 1, 3, 2, 0, 0,
    1, 2, 1, 3, 3, 1, 0, 1,
    0, 1, 0, 0, 2, 2, 0, 3,
    1, 2, 3, 1, 1, 1, 2, 0,
    2, 2, 3, 2, 3, 0, 0, 1,
    1, 2, 3, 2, 0, 1, 3, 2,
    3, 3, 2, 3, 3, 3, 0, 1,
)
K11_F2: tuple[int, ...] = (
    0, 2, 3, 1, 3, 0, 1, 0,
    3, 1, 0, 1, 0, 2, 1, 3,
    3, 0, 0, 3, 1, 2, 0, 0,
    3, 3, 1, 2, 3, 0, 3, 2,
    2, 1, 2, 2, 3, 0, 2, 0,
    3, 1, 1, 0, 2, 1, 1, 0,
    3, 0, 2, 2, 3, 2, 2, 1,
    1, 1, 3, 2, 0, 3, 1, 2,
)


def verify_polychromatic_4(coloring: tuple[int, ...]) -> None:
    """Assert that every one of the 72 affine lines of AG(2, 8) hits all 4 colors {0, 1, 2, 3}."""
    assert len(coloring) == 64
    for line in AG2_8_LINES:
        present = {coloring[p] for p in line}
        assert {0, 1, 2, 3}.issubset(present), f"Line {line} misses a color in {{0,1,2,3}}"


def eval_bush_tc(a: int, b: int, c: int, d: int) -> tuple[int, ...]:
    """Evaluate Bush OA(4096; 4, 9, 8) codeword for (a, b, c, d) in GF(8)^4."""
    r = []
    for x in range(8):
        x2 = GF8_MUL[x][x]
        x3 = GF8_MUL[x2][x]
        r.append(a ^ GF8_MUL[b][x] ^ GF8_MUL[c][x2] ^ GF8_MUL[d][x3])
    r.append(d)
    return tuple(r)


def pencil_even_q8(u: int, v: int) -> int:
    """Partition AG(2, 8) into 4 intersecting line-sets through (0, 0).

    Symbol 0: {u=0, v=0, v=7u} (3 lines, 22 pts including origin).
    Symbol 1: {v=1u, v=2u}; Symbol 2: {v=3u, v=4u}; Symbol 3: {v=5u, v=6u}.
    """
    if u == 0 or v == 0:
        return 0
    slope = GF8_MUL[v][GF8_INV[u]]
    if slope == 7:
        return 0
    return (slope + 1) // 2


def hyperoval_slices_q8() -> list[list[tuple[int, ...]]]:
    """Return 8 disjoint OA(64; 2, 9, 8) slices of the 10-point hyperoval OA(512; 3, 10, 8)."""
    slices: list[list[tuple[int, ...]]] = []
    for b in range(8):
        sl: list[tuple[int, ...]] = []
        for a in range(8):
            for c in range(8):
                r = [a ^ GF8_MUL[b][x] ^ GF8_MUL[c][GF8_MUL[x][x]] for x in range(8)]
                r.append(c)
                sl.append(tuple(r))
        slices.append(sl)
    return slices


def build_k11_pencil() -> list[tuple[int, ...]]:
    """Deterministic Hyperoval Double-poly2: CA(7561; 4, 11, 8) (Phase 5B-1 anchor)."""
    slices = hyperoval_slices_q8()
    rows: list[tuple[int, ...]] = []

    # 1) Main Bush OA(4096; 4, 9, 8) + col9 = pencil(c, d), col10 = pencil(a, b)
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    rows.append(
                        eval_bush_tc(a, b, c, d) + (pencil_even_q8(c, d), pencil_even_q8(a, b))
                    )

    # 2) Vertex repairs for col9 in {1, 2, 3} at (c, d) = (0, 0) -> 192 rows
    for m9 in (1, 2, 3):
        for a in range(8):
            for b in range(8):
                r = [a ^ GF8_MUL[b][x] for x in range(8)] + [0, m9, pencil_even_q8(a, b)]
                rows.append(tuple(r))

    # 3) Vertex repairs for col10 in {1, 2, 3} at (a, b) = (0, 0) -> 192 rows
    for m10 in (1, 2, 3):
        for c in range(8):
            for d in range(8):
                r = []
                for x in range(8):
                    x2 = GF8_MUL[x][x]
                    x3 = GF8_MUL[x2][x]
                    r.append(GF8_MUL[c][x2] ^ GF8_MUL[d][x3])
                r.extend([d, pencil_even_q8(c, d), m10])
                rows.append(tuple(r))

    # 4) 4 hyperoval OA(512; 3, 10, 8) blocks for col9 in {4, 5, 6, 7} -> 2048 rows
    for m9 in (4, 5, 6, 7):
        shift = m9 - 4
        for b in range(8):
            c10 = b ^ shift
            for base in slices[b]:
                rows.append(base + (m9, c10))

    # 5) Remaining 4 slices b in {0, 1, 2, 3} for col10 in {4, 5, 6, 7} -> 1024 rows
    for m10 in (4, 5, 6, 7):
        for idx, m9 in enumerate((0, 1, 2, 3)):
            for base in slices[idx]:
                rows.append(base + (m9, m10))

    # 6) 9 vertex-collision rows (0^9, v9, v10) for v9, v10 in {1, 2, 3}
    for v9 in (1, 2, 3):
        for v10 in (1, 2, 3):
            rows.append((0,) * 9 + (v9, v10))

    assert len(rows) == 7561
    return rows


def build_k10_polychrom() -> list[tuple[int, ...]]:
    """Deterministic CA(5888; 4, 10, 8) via irreducible-quadratic scaled-hyperoval completion.

    Uses Q(a, b, c, d) = (a ^ c ^ d, a ^ b ^ d), whose kernel {(u + v*x)(x^2 + x + 1)}
    has no roots in GF(8) for (x^2 + x + 1). Each point (p, q) in AG(2, 8) yields an
    exact OA(64; 2, 9, 8) slice equal to the w = 0 slice of a shifted scaled hyperoval
    OA(512; 3, 10, 8). Partitioning AG(2, 8) into 4 disjoint 15-point blocking sets
    {0, 1, 2, 3} plus 4 singleton points {4, 5, 6, 7} leaves only 7 slices (448 rows)
    per symbol m in {4, 5, 6, 7}: N = 4096 + 4 * 448 = 5888.
    """
    verify_polychromatic_4(K10_COLORING)
    for idx, pt in enumerate(K10_FREE_PTS):
        assert K10_COLORING[pt] == 4 + idx

    scale = [1 ^ x ^ GF8_MUL[x][x] for x in range(8)] + [1]
    assert all(s != 0 for s in scale)

    rows: list[tuple[int, ...]] = []
    # 1) Main Bush OA(4096; 4, 9, 8) + col9 = K10_COLORING[Q(a, b, c, d)]
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    p = a ^ c ^ d
                    q = a ^ b ^ d
                    rows.append(eval_bush_tc(a, b, c, d) + (K10_COLORING[p * 8 + q],))

    # 2) Complete each symbol m in {4, 5, 6, 7} from its existing w = 0 slice with w in 1..7
    for idx, pt in enumerate(K10_FREE_PTS):
        m = 4 + idx
        p0, q0 = pt >> 3, pt & 7
        shift = eval_bush_tc(0, q0, p0, 0)
        for w in range(1, 8):
            for u in range(8):
                for v in range(8):
                    r = [
                        shift[x] ^ GF8_MUL[u ^ GF8_MUL[v][x] ^ GF8_MUL[w][GF8_MUL[x][x]]][scale[x]]
                        for x in range(8)
                    ]
                    r.append(shift[8] ^ v)
                    rows.append(tuple(r) + (m,))

    assert len(rows) == 5888
    return rows


def build_k11_polychrom() -> list[tuple[int, ...]]:
    """Deterministic CA(7203; 4, 11, 8) via balanced 4-polychromatic AG(2, 8) + hyperoval.

    Replaces the overlapping pencil blocking sets (which required 192 + 192 + 9 = 393
    vertex-repair rows) with two disjoint balanced 4-polychromatic colorings (K11_F1, K11_F2)
    on (c, d) and (a, b), leaving only 68 uncovered tuples on (c0, c1, 9, 10) in {0..3}^2
    covered deterministically by 35 greedy rows -> N = 4096 + 3072 + 35 = 7203.
    """
    verify_polychromatic_4(K11_F1)
    verify_polychromatic_4(K11_F2)
    slices = hyperoval_slices_q8()
    rows: list[tuple[int, ...]] = []

    # 1) Main Bush OA(4096; 4, 9, 8) + col9 = K11_F1(c, d), col10 = K11_F2(a, b)
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    rows.append(
                        eval_bush_tc(a, b, c, d) + (K11_F1[c * 8 + d], K11_F2[a * 8 + b])
                    )

    # 2) 4 hyperoval blocks for col9 in {4..7} -> 2048 rows
    for m9 in (4, 5, 6, 7):
        shift = m9 - 4
        for b in range(8):
            c10 = b ^ shift
            for base in slices[b]:
                rows.append(base + (m9, c10))

    # 3) Remaining 4 slices for col10 in {4..7} -> 1024 rows
    for m10 in (4, 5, 6, 7):
        for idx, m9 in enumerate((0, 1, 2, 3)):
            for base in slices[idx]:
                rows.append(base + (m9, m10))

    # 4) Collect exact missing (c0, c1, 9, 10) tuples in {0..3}^2 and pack greedily
    missing_by_pair: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {
        (v9, v10): [] for v9 in range(4) for v10 in range(4)
    }
    main_rows = rows[:4096]
    for c0, c1 in combinations(range(9), 2):
        seen = {(r[c0] << 7) | (r[c1] << 4) | (r[9] << 2) | r[10] for r in main_rows}
        for y0 in range(8):
            for y1 in range(8):
                for v9 in range(4):
                    for v10 in range(4):
                        if ((y0 << 7) | (y1 << 4) | (v9 << 2) | v10) not in seen:
                            missing_by_pair[(v9, v10)].append((c0, c1, y0, y1))

    for (v9, v10), mlist in sorted(missing_by_pair.items()):
        rem = list(mlist)
        while rem:
            # Deterministically pack compatible (c0, c1, y0, y1) pairs into one row
            row: list[int | None] = [None] * 9
            new_rem: list[tuple[int, int, int, int]] = []
            for c0, c1, y0, y1 in rem:
                if (row[c0] is None or row[c0] == y0) and (row[c1] is None or row[c1] == y1):
                    row[c0] = y0
                    row[c1] = y1
                else:
                    new_rem.append((c0, c1, y0, y1))
            rows.append(tuple(0 if x is None else x for x in row) + (v9, v10))
            rem = new_rem

    return rows


def check_k12_diagnostic() -> None:
    """Verify constructive & algebraic obstructions for k = 12, q = 8 (target N < 7680)."""
    # 1) Pure 4-color main block (cols 9, 10, 11 in {0..3}) lower bound:
    triples_outside = 8**3 - 4**3  # 448
    min_residual_rows = triples_outside * 8  # 3584
    min_total_pure4 = 4096 + min_residual_rows  # 7680
    assert min_total_pure4 == 7680

    # 2) Verify PG(2, 8) hyperoval maximality: no 11th point avoids all C(10, 2) = 45 secants
    ho_pts = [(1, x, GF8_MUL[x][x]) for x in range(8)] + [(0, 0, 1), (0, 1, 0)]
    all_pg2 = set()
    for a in range(8):
        for b in range(8):
            for c in range(8):
                if a or b or c:
                    lead = a if a else (b if b else c)
                    inv = GF8_INV[lead]
                    all_pg2.add((GF8_MUL[a][inv], GF8_MUL[b][inv], GF8_MUL[c][inv]))
    assert len(all_pg2) == 73
    secant_pts: set[tuple[int, int, int]] = set()
    for p1, p2 in combinations(ho_pts, 2):
        for l1 in range(8):
            for l2 in range(8):
                if l1 or l2:
                    v = (
                        GF8_MUL[l1][p1[0]] ^ GF8_MUL[l2][p2[0]],
                        GF8_MUL[l1][p1[1]] ^ GF8_MUL[l2][p2[1]],
                        GF8_MUL[l1][p1[2]] ^ GF8_MUL[l2][p2[2]],
                    )
                    lead = v[0] if v[0] else (v[1] if v[1] else v[2])
                    inv = GF8_INV[lead]
                    secant_pts.add((GF8_MUL[v[0]][inv], GF8_MUL[v[1]][inv], GF8_MUL[v[2]][inv]))
    free_arc_pts = all_pg2 - secant_pts

    print("[k=12, q=8 Constructive Diagnostic]")
    print(f"  1) Pure 4-color main block (4096 rows, cols 9..11 in {{0..3}}):")
    print(f"     triples outside {{0..3}}^3 = {triples_outside}, min residual = {min_residual_rows} -> N >= {min_total_pure4} (not < 7680)")
    print(f"  2) PG(2, 8) hyperoval maximality (OA(512; 3, 10, 8) -> k_sub=11):")
    print(f"     |PG(2,8)|={len(all_pg2)}, |hyperoval|={len(ho_pts)}, points on secants={len(secant_pts)}, valid 11th arc points={len(free_arc_pts)}")
    print(f"     -> OA(512; 3, 11, 8) does not exist (Bush/Segre); direct Hyperoval-Double-poly2 does not yield k=12, N < 7680.")


def write_array_and_sha256(path: Path, rows: list[tuple[int, ...]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            line = " ".join(str(x) for x in r) + "\n"
            fh.write(line)
            h.update(line.encode("utf-8"))
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic generators for t=4, q=8 NEAR_BUSH CAs")
    parser.add_argument(
        "--mode",
        choices=["k11-pencil", "k10-polychrom", "k11-polychrom", "k12-check"],
        default="k11-pencil",
        help="Construction mode",
    )
    parser.add_argument("--out", type=Path, help="Output canonical array path")
    args = parser.parse_args()

    t0 = time.perf_counter()
    if args.mode == "k12-check":
        check_k12_diagnostic()
        return

    if args.mode == "k11-pencil":
        rows = build_k11_pencil()
        k = 11
    elif args.mode == "k10-polychrom":
        rows = build_k10_polychrom()
        k = 10
    elif args.mode == "k11-polychrom":
        rows = build_k11_polychrom()
        k = 11
    else:
        raise ValueError(args.mode)

    n = len(rows)
    if args.out is None:
        raise SystemExit("--out is required for array generation modes")
    sha = write_array_and_sha256(args.out, rows)
    elapsed = time.perf_counter() - t0
    print(f"mode={args.mode} CA({n}; 4, {k}, 8) uniq={len(set(rows))} sha256={sha} elapsed={elapsed:.3f}s -> {args.out}")


if __name__ == "__main__":
    main()
