#!/usr/bin/env python3
"""Independent implementation of the Phase 8 rule construction from specification.

Pure Python (std-only). Uses only GeneralGF finite-field arithmetic from
scripts/gen_general_tqv.py. No solver, no search, no randomness, no imports
from scripts/phase8/.

Construction parameters:
  - odd prime power q = p^r >= 3
  - alphabet size v with 2 <= v <= q
  - extra pure b-lines j >= 0 with:
      x_b = (q + 1) // 2 + j
      x_a = q - 1 - x_b = (q - 3) // 2 - j >= 0
      h_a = v - x_a
      h_b = v - x_b >= 1
  - class count n with 1 <= n <= min(q - h_a, (q - 1) // 2) and n <= h_a.

Produces a representative list R of tuples (c, d, a, b) with c, d in F_q and
a, b in {0, ..., v - 1} such that M(R) has 0 uncovered pairs.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402


DEFAULT_TARGETS: tuple[tuple[int, int, int, int, int], ...] = (
    # (q, v, j, n, expected_m)
    (9, 9, 0, 3, 116),
    (11, 11, 0, 4, 172),
    (19, 19, 0, 8, 520),
    (19, 19, 1, 7, 516),
    (23, 23, 0, 10, 768),
    (23, 23, 1, 9, 746),
    (25, 23, 2, 11, 828),
)


def konig_edge_coloring(
    edges: list[tuple[int, int]],
    num_left: int,
    num_right: int,
    num_colors: int,
) -> list[int]:
    """Exact proper edge coloring of a bipartite graph with max degree <= num_colors.

    Implements Konig's alternating-path (Kempe chain) algorithm deterministically.
    Returns a list of color indices in 0..num_colors-1 aligned with `edges`.
    """
    if num_colors < 1:
        raise ValueError(f"num_colors must be >= 1, got {num_colors}")

    # color_u[u][c] = (w, edge_idx) or None
    # color_w[w][c] = (u, edge_idx) or None
    color_u: list[list[tuple[int, int] | None]] = [
        [None] * num_colors for _ in range(num_left)
    ]
    color_w: list[list[tuple[int, int] | None]] = [
        [None] * num_colors for _ in range(num_right)
    ]
    edge_colors = [-1] * len(edges)

    def assign(e_idx: int, u: int, w: int, c: int) -> None:
        assert color_u[u][c] is None and color_w[w][c] is None
        color_u[u][c] = (w, e_idx)
        color_w[w][c] = (u, e_idx)
        edge_colors[e_idx] = c

    for e_idx, (u, w) in enumerate(edges):
        free_u = [c for c in range(num_colors) if color_u[u][c] is None]
        free_w = [c for c in range(num_colors) if color_w[w][c] is None]
        if not free_u or not free_w:
            raise RuntimeError(
                f"Vertex degree exceeds num_colors={num_colors} at edge ({u}, {w})"
            )

        common = [c for c in free_u if color_w[w][c] is None]
        if common:
            assign(e_idx, u, w, common[0])
            continue

        c1 = free_u[0]  # free at u, used at w
        c2 = free_w[0]  # free at w, used at u
        assert c1 != c2

        # Trace maximal (c1, c2) alternating path starting at w with color c1.
        # Because the graph is bipartite and c1 is free at u, this path cannot reach u.
        path: list[tuple[int, int, int, int]] = []  # (u_e, w_e, edge_idx, old_col)
        cur = w
        side = "W"
        col = c1
        while True:
            if side == "W":
                step = color_w[cur][col]
                if step is None:
                    break
                nxt_u, p_eidx = step
                path.append((nxt_u, cur, p_eidx, col))
                cur = nxt_u
                side = "U"
            else:
                step = color_u[cur][col]
                if step is None:
                    break
                nxt_w, p_eidx = step
                path.append((cur, nxt_w, p_eidx, col))
                cur = nxt_w
                side = "W"
            col = c2 if col == c1 else c1

        # Clear old slots along the path, then re-insert with swapped colors.
        for u_e, w_e, _p_eidx, old_col in path:
            color_u[u_e][old_col] = None
            color_w[w_e][old_col] = None
        for u_e, w_e, p_eidx, old_col in path:
            new_col = c2 if old_col == c1 else c1
            assign(p_eidx, u_e, w_e, new_col)

        # Now c1 is free at both u and w.
        assign(e_idx, u, w, c1)

    # Verify proper coloring
    for e_idx, (u, w) in enumerate(edges):
        c = edge_colors[e_idx]
        assert 0 <= c < num_colors
        assert color_u[u][c] == (w, e_idx)
        assert color_w[w][c] == (u, e_idx)
    return edge_colors


def build_phase8_reps(
    q: int, v: int, j: int, n: int
) -> tuple[list[tuple[int, int, int, int]], dict[str, object]]:
    """Construct representative list R according to the Phase 8 specification.

    Returns (sorted_reps, metadata).
    """
    if q < 3 or q % 2 == 0:
        raise ValueError(f"q={q} must be an odd prime power >= 3")
    gf = GeneralGF(q)
    add, mul = gf.add, gf.mul

    if not (2 <= v <= q):
        raise ValueError(f"v={v} must satisfy 2 <= v <= q={q}")
    if j < 0:
        raise ValueError(f"j={j} must be >= 0")

    x_b = (q + 1) // 2 + j
    x_a = q - 1 - x_b
    h_a = v - x_a
    h_b = v - x_b

    if x_a < 0:
        raise ValueError(f"x_a={x_a} < 0 for q={q}, j={j}")
    if h_b < 1:
        raise ValueError(f"h_b={h_b} < 1 for q={q}, v={v}, j={j}")
    max_n = min(q - h_a, (q - 1) // 2)
    if not (1 <= n <= max_n):
        raise ValueError(f"n={n} must satisfy 1 <= n <= {max_n} (q={q}, v={v}, j={j})")
    if n > h_a:
        raise ValueError(f"n={n} exceeds h_a={h_a}")

    # Step 1: Field negation, subtraction, inversion, squares, and fixed non-square n0.
    neg = [next(b for b in range(q) if add[a][b] == 0) for a in range(q)]
    sub = [[add[a][neg[b]] for b in range(q)] for a in range(q)]
    inv = [0] + [next(b for b in range(1, q) if mul[a][b] == 1) for a in range(1, q)]
    sq_set = {mul[x][x] for x in range(q)}
    assert len(sq_set) == (q + 1) // 2
    n0 = next(z for z in range(1, q) if z not in sq_set)

    # Step 2: Delta = {1 / (s - n0) : s in sq_set}, d0 = -1 / n0.
    delta_set = {inv[sub[s][n0]] for s in sq_set}
    d0 = inv[sub[0][n0]]
    assert len(delta_set) == (q + 1) // 2
    assert d0 in delta_set
    assert 0 not in delta_set

    # Step 3: Partition horizontal lines d in F_q.
    outside_delta = [d for d in range(1, q) if d not in delta_set]
    assert len(outside_delta) == (q - 3) // 2
    extra_b_lines = outside_delta[:j]
    pure_b_lines = sorted(delta_set) + extra_b_lines
    pure_a_lines = outside_delta[j:]
    assert len(pure_b_lines) == x_b
    assert len(pure_a_lines) == x_a

    # Step 4: Symbols from {0..v-1} and class subset S of F_q* / {+1, -1}.
    a_line_sym = {d: idx for idx, d in enumerate(pure_a_lines)}
    h_a_syms = list(range(x_a, v))
    assert len(h_a_syms) == h_a

    # Partition F_q* into (q-1)/2 pairs {e, -e}, order by min(e, -e), take n largest.
    pair_reps = sorted({min(e, neg[e]) for e in range(1, q)})
    assert len(pair_reps) == (q - 1) // 2
    s_reps = pair_reps[-n:]
    if gf.r == 1:
        assert s_reps == list(range((q - 1) // 2 - n + 1, (q - 1) // 2 + 1))

    class_sym = {e: h_a_syms[idx] for idx, e in enumerate(s_reps)}
    h_a_free = h_a_syms[n:]
    assert len(h_a_free) == h_a - n

    b_line_sym = {d: idx for idx, d in enumerate(pure_b_lines)}
    h_b_syms = list(range(x_b, v))
    assert len(h_b_syms) == h_b

    reps: list[tuple[int, int, int, int]] = []

    # Step 4 (pure a-lines): (c, d, a_d, pi(c)) for all c in F_q.
    for d in pure_a_lines:
        a_d = a_line_sym[d]
        for c in range(q):
            reps.append((c, d, a_d, c if c < v else 0))

    # Step 5 (pure b-lines):
    # 5a. d = d0: point O = (0, d0) gets all n class representatives; c != 0 gets
    #     remaining h_a - n heavy a-symbols at least once, rest filled with h_a_syms[0].
    b_d0 = b_line_sym[d0]
    for e in s_reps:
        reps.append((0, d0, class_sym[e], b_d0))
    rem_d0_c = list(range(1, q))
    assert len(rem_d0_c) >= len(h_a_free)
    for idx, c in enumerate(rem_d0_c):
        a_val = h_a_free[idx] if idx < len(h_a_free) else h_a_syms[0]
        reps.append((c, d0, a_val, b_d0))

    # 5b. d in Delta \ {d0}: 2n class points (+-e*n0*(d - d0), d) receive a_e;
    #     remaining q - 2n points cover h_a_free at least once, rest h_a_syms[0].
    for d in sorted(delta_set):
        if d == d0:
            continue
        b_d = b_line_sym[d]
        factor = mul[n0][sub[d][d0]]
        assert factor != 0
        assigned: dict[int, int] = {}
        for e in s_reps:
            c_pos = mul[e][factor]
            c_neg = neg[c_pos]
            assert c_pos != c_neg
            assert c_pos not in assigned and c_neg not in assigned
            assigned[c_pos] = class_sym[e]
            assigned[c_neg] = class_sym[e]
        rem_c = [c for c in range(q) if c not in assigned]
        assert len(rem_c) == q - 2 * n
        assert len(rem_c) >= len(h_a_free)
        for idx, c in enumerate(rem_c):
            assigned[c] = h_a_free[idx] if idx < len(h_a_free) else h_a_syms[0]
        for c in range(q):
            reps.append((c, d, assigned[c], b_d))

    # 5c. j extra pure b-lines: cover all h_a heavy a-symbols at least once.
    for d in extra_b_lines:
        b_d = b_line_sym[d]
        assert q >= len(h_a_syms)
        for c in range(q):
            a_val = h_a_syms[c] if c < len(h_a_syms) else h_a_syms[0]
            reps.append((c, d, a_val, b_d))

    # Step 6: Heavy line d = 0 (exact Konig h_b-edge-coloring).
    a_star_by_p: dict[int, list[int]] = {}
    for p in range(q):
        p2 = mul[p][p]
        req = set(h_a_free)
        for e in s_reps:
            if sub[p2][mul[e][e]] in sq_set:
                req.add(class_sym[e])
        if len(req) < h_b:
            for a_cand in h_a_syms:
                if a_cand not in req:
                    req.add(a_cand)
                    if len(req) == h_b:
                        break
        assert len(req) >= h_b
        a_star_by_p[p] = sorted(req)

    # Collect incident lists for left (H_a) and right (F_q) vertices in G.
    inc_a: dict[int, list[int]] = {a: [] for a in h_a_syms}
    inc_p: dict[int, list[int]] = {p: list(a_star_by_p[p]) for p in range(q)}
    for p in range(q):
        for a in a_star_by_p[p]:
            inc_a[a].append(p)

    for a in h_a_syms:
        if len(inc_a[a]) < h_b:
            raise RuntimeError(f"deg_G(a={a})={len(inc_a[a])} < h_b={h_b}")
    for p in range(q):
        assert len(inc_p[p]) >= h_b

    # Split every vertex x into x_0 of degree exactly h_b and remainder vertices of degree <= h_b.
    left_node_id: dict[tuple[int, int], int] = {}
    edge_left_chunk: dict[tuple[int, int], int] = {}
    for a in h_a_syms:
        neighbors = inc_a[a]
        for idx, p in enumerate(neighbors):
            chunk = idx // h_b
            key = (a, chunk)
            if key not in left_node_id:
                left_node_id[key] = len(left_node_id)
            edge_left_chunk[(a, p)] = left_node_id[key]

    right_node_id: dict[tuple[int, int], int] = {}
    edge_right_chunk: dict[tuple[int, int], int] = {}
    for p in range(q):
        neighbors = inc_p[p]
        for idx, a in enumerate(neighbors):
            chunk = idx // h_b
            key = (p, chunk)
            if key not in right_node_id:
                right_node_id[key] = len(right_node_id)
            edge_right_chunk[(a, p)] = right_node_id[key]

    orig_edges: list[tuple[int, int]] = []
    split_edges: list[tuple[int, int]] = []
    for p in range(q):
        for a in a_star_by_p[p]:
            orig_edges.append((a, p))
            split_edges.append((edge_left_chunk[(a, p)], edge_right_chunk[(a, p)]))

    edge_colors = konig_edge_coloring(
        split_edges,
        num_left=len(left_node_id),
        num_right=len(right_node_id),
        num_colors=h_b,
    )

    # Verify full color coverage on every a_0 and p_0.
    seen_a: dict[int, set[int]] = {a: set() for a in h_a_syms}
    seen_p: dict[int, set[int]] = {p: set() for p in range(q)}
    for (a, p), col_idx in zip(orig_edges, edge_colors):
        b_sym = h_b_syms[col_idx]
        seen_a[a].add(b_sym)
        seen_p[p].add(b_sym)
        reps.append((p, 0, a, b_sym))

    for a in h_a_syms:
        assert len(seen_a[a]) == h_b, f"Heavy a={a} missing b-colors"
    for p in range(q):
        assert len(seen_p[p]) == h_b, f"Point p={p} missing b-colors"

    reps.sort()
    assert len(set(reps)) == len(reps), "Duplicate representative produced"

    meta: dict[str, object] = {
        "q": q,
        "v": v,
        "j": j,
        "n": n,
        "m": len(reps),
        "x_a": x_a,
        "x_b": x_b,
        "h_a": h_a,
        "h_b": h_b,
        "n0": n0,
        "d0": d0,
        "S": s_reps,
        "heavy_edges": len(orig_edges),
    }
    return reps, meta


def write_reps_file(
    out_path: Path,
    reps: list[tuple[int, int, int, int]],
    meta: dict[str, object],
) -> str:
    """Write representatives in canonical phase7_lift.py format and return SHA-256."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Phase 8 spec reproduction: q={meta['q']} v={meta['v']} j={meta['j']} "
        f"n={meta['n']} m={meta['m']} n0={meta['n0']} d0={meta['d0']} "
        f"S={meta['S']}\n"
    )
    body = "".join(f"{c} {d} {a} {b}\n" for (c, d, a, b) in reps)
    data = (header + body).encode("utf-8")
    out_path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def default_filename(q: int, v: int, j: int, n: int, m: int) -> str:
    return f"R_q{q}_v{v}_j{j}_n{n}_m{m}.txt"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Independent Phase 8 rule construction from specification."
    )
    ap.add_argument("--all", action="store_true", help="Generate all 7 specification targets.")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/phase8_repro"),
        help="Output directory for --all (default: data/phase8_repro).",
    )
    ap.add_argument("--q", type=int, help="Odd prime power q.")
    ap.add_argument("--v", type=int, help="Alphabet size v (2 <= v <= q).")
    ap.add_argument("--j", type=int, default=0, help="Extra pure b-lines j >= 0.")
    ap.add_argument("--n", type=int, help="Number of classes n.")
    ap.add_argument("--out", type=Path, help="Output file path for single target.")
    args = ap.parse_args()

    if args.all:
        for q, v, j, n, exp_m in DEFAULT_TARGETS:
            reps, meta = build_phase8_reps(q, v, j, n)
            m = len(reps)
            if m != exp_m:
                raise SystemExit(
                    f"Target mismatch for (q={q}, v={v}, j={j}, n={n}): got m={m}, expected {exp_m}"
                )
            out_path = args.out_dir / default_filename(q, v, j, n, m)
            sha = write_reps_file(out_path, reps, meta)
            print(
                f"OK q={q:2d} v={v:2d} j={j} n={n:2d} m={m:3d} "
                f"n0={meta['n0']} d0={meta['d0']} heavy={meta['heavy_edges']:3d} "
                f"sha256={sha} -> {out_path}"
            )
        return

    if args.q is None or args.v is None or args.n is None or args.out is None:
        ap.error("Provide either --all or all of --q, --v, --n, --out")

    reps, meta = build_phase8_reps(args.q, args.v, args.j, args.n)
    sha = write_reps_file(args.out, reps, meta)
    print(
        f"OK q={args.q} v={args.v} j={args.j} n={args.n} m={len(reps)} "
        f"n0={meta['n0']} d0={meta['d0']} heavy={meta['heavy_edges']} "
        f"sha256={sha} -> {args.out}"
    )


if __name__ == "__main__":
    main()
