#!/usr/bin/env python3
"""Phase 5B-1: Structure inspection, PG(3,7) geometry & cheap prototypes for t=4 NEAR_BUSH.

Pure Python (std-only). Analyzes verified k = q+2 arrays from chrispbsmolen/ca-tools
(CA_3556_4_9_7, CA_6101_4_10_8, CA_9801_4_11_9), computes PG(3,7) twisted-cubic
dependencies for k = 9 and k = 10, and constructs positive controls + cheap k = q+3
prototypes in an external output directory (never writing into results/).
"""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path
import time


# ---------------------------------------------------------------------------
# Helpers: I/O, exact 4-coverage check, finite-field arithmetic for GF(8)
# ---------------------------------------------------------------------------

def load_array(path: Path) -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                rows.append(tuple(int(x) for x in s.split()))
    return rows


def write_array(path: Path, rows: list[tuple[int, ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(" ".join(str(x) for x in r) + "\n")


def count_missing_t4(
    rows: list[tuple[int, ...]],
    k: int,
    v: int,
    col_tuples: list[tuple[int, int, int, int]] | None = None,
) -> tuple[int, int]:
    """Return (missing_4tuples_total, bad_4sets_count)."""
    if col_tuples is None:
        col_tuples = list(combinations(range(k), 4))
    target = v ** 4
    v2 = v * v
    v3 = v2 * v
    total_missing = 0
    bad_sets = 0
    for c0, c1, c2, c3 in col_tuples:
        seen = {r[c0] * v3 + r[c1] * v2 + r[c2] * v + r[c3] for r in rows}
        miss = target - len(seen)
        if miss:
            total_missing += miss
            bad_sets += 1
    return total_missing, bad_sets


def check_oa_t(rows: list[tuple[int, ...]], cols: list[int], t: int, v: int) -> tuple[int, int]:
    """Check how many t-subsets of `cols` form an exact OA(v^t; t, t, v)."""
    if len(rows) != v ** t:
        return 0, 0
    target = v ** t
    ok = 0
    total = 0
    for comb in combinations(cols, t):
        total += 1
        seen = {tuple(r[c] for c in comb) for r in rows}
        if len(seen) == target:
            ok += 1
    return ok, total


# GF(8) = GF(2)[x] / (x^3 + x + 1), elements 0..7
def gf8_mul(a: int, b: int) -> int:
    res = 0
    for _ in range(3):
        if b & 1:
            res ^= a
        hi = a & 4
        a = (a << 1) & 7
        if hi:
            a ^= 3  # x^3 = x + 1 -> 0b011
        b >>= 1
    return res


GF8_MUL = [[gf8_mul(a, b) for b in range(8)] for a in range(8)]
GF8_INV = [0] + [next(b for b in range(1, 8) if GF8_MUL[a][b] == 1) for a in range(1, 8)]


# ---------------------------------------------------------------------------
# Part A: Structure Inspection of CA_3556, CA_6101, CA_9801
# ---------------------------------------------------------------------------

def inspect_ca_array(name: str, path: Path, q: int) -> None:
    t0 = time.perf_counter()
    rows = load_array(path)
    n = len(rows)
    k = len(rows[0])
    row_set = set(rows)
    const_idxs = [i for i, r in enumerate(rows) if len(set(r)) == 1]

    # Z_q additive shift closure
    zq_closed = sum(1 for r in rows if tuple((x + 1) % q for x in r) in row_set)
    # AGL(1, q) multiplicative closure (for prime q)
    if q == 7:
        agl_closed = sum(1 for r in rows if tuple((3 * x) % 7 for x in r) in row_set)
    else:
        agl_closed = None
    # GF(8) XOR closure for q == 8
    xor_closed = (
        sum(1 for r in rows if tuple(x ^ 1 for x in r) in row_set) if q == 8 else None
    )

    # Column symbol balance
    col_min_max = []
    for c in range(k):
        cnt = Counter(r[c] for r in rows)
        col_min_max.append((min(cnt.values()), max(cnt.values())))

    # Check if prefix q^4 rows on first q+1 columns is an exact OA(q^4; 4, q+1, q)
    oa_ok, oa_tot = check_oa_t(rows[: q ** 4], list(range(q + 1)), 4, q)

    print(f"\n--- Inspecting {name} (N={n}, k={k}, v={q}) ---")
    print(f"  unique_rows={len(row_set)}/{n}, const_rows={len(const_idxs)} (idxs={const_idxs[:5]})")
    print(f"  Z_{q}_shift_closed={zq_closed}/{n}"
          + (f", AGL(1,7)_x3_closed={agl_closed}/{n}" if agl_closed is not None else "")
          + (f", GF(8)_xor1_closed={xor_closed}/{n}" if xor_closed is not None else ""))
    print(f"  col_symbol_counts_minmax(first 3, last 2)={col_min_max[:3]} ... {col_min_max[-2:]}")
    print(f"  prefix_OA(q^4; 4, q+1, q) on rows[0:{q**4}], cols[0:{q+1}]: {oa_ok}/{oa_tot}")

    if q == 7 and k == 9:
        # Check exact decomposition into cosets of all-ones code over Z_7
        canon = {tuple((x - r[0]) % 7 for x in r) for r in rows}
        full_cosets = sum(
            1
            for base in canon
            if all(tuple((x + s) % 7 for x in base) in row_set for s in range(7))
        )
        print(f"  Z_7 all-ones cosets: {full_cosets} complete cosets ({full_cosets * 7}/{n} rows)")

    if q == 9 and k == 11 and oa_ok == oa_tot:
        main_rows = rows[: q ** 4]
        res_rows = rows[q ** 4 :]
        c10_main = Counter(r[10] for r in main_rows)
        c10_res = Counter(r[10] for r in res_rows)
        print(f"  CA_9801 main (6561 rows) col10 counts: {dict(sorted(c10_main.items()))}")
        print(f"  CA_9801 residual ({len(res_rows)} rows) col10 counts: {dict(sorted(c10_res.items()))}")
        # Verify per-symbol OA(729; 3, 9, 9) structure on cols 0..8 for symbols 5..8
        for sym in sorted(c10_res):
            sub = [r for r in res_rows if r[10] == sym]
            if len(sub) == q ** 3:
                ok3, tot3 = check_oa_t(sub, list(range(9)), 3, 9)
                by_c9 = Counter(r[9] for r in sub)
                ok2_slices = sum(
                    1
                    for d_val in range(9)
                    if check_oa_t([r for r in sub if r[9] == d_val], list(range(9)), 2, 9) == (36, 36)
                )
                print(
                    f"    res col10={sym}: N={len(sub)}, OA(729;3,9,9) on cols 0..8 = {ok3}/{tot3}, "
                    f"col9_uniform={set(by_c9.values())}, OA(81;2,9,9)_slices={ok2_slices}/9"
                )
            else:
                # Check if union of OA(81; 2, 9, 9) slices (repair blocks)
                by_c9 = Counter(r[9] for r in sub)
                print(
                    f"    res col10={sym}: N={len(sub)} (= {len(sub)//81}*81 repair block), "
                    f"col9_dist={dict(sorted(by_c9.items()))}"
                )
    print(f"  elapsed={time.perf_counter() - t0:.2f}s")


# ---------------------------------------------------------------------------
# Part B1: PG(3, 7) Twisted-Cubic Geometry & Linear Lower Bound
# ---------------------------------------------------------------------------

def norm_pg3(v: tuple[int, int, int, int], p: int) -> tuple[int, int, int, int]:
    for x in v:
        if x % p != 0:
            inv = pow(x % p, p - 2, p)
            return tuple((y * inv) % p for y in v)
    raise ValueError("zero vector")


def det4_mod(rows4: list[tuple[int, int, int, int]], p: int) -> int:
    m = [list(r) for r in rows4]
    det = 1
    for i in range(4):
        piv = None
        for r in range(i, 4):
            if m[r][i] % p != 0:
                piv = r
                break
        if piv is None:
            return 0
        if piv != i:
            m[i], m[piv] = m[piv], m[i]
            det = (-det) % p
        val = m[i][i] % p
        det = (det * val) % p
        inv = pow(val, p - 2, p)
        for r in range(i + 1, 4):
            f = (m[r][i] * inv) % p
            if f:
                for c in range(i, 4):
                    m[r][c] = (m[r][c] - f * m[i][c]) % p
    return det


def analyze_pg3_7() -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    t0 = time.perf_counter()
    p = 7
    tc = [(1, x, (x * x) % p, (x * x * x) % p) for x in range(p)] + [(0, 0, 0, 1)]
    tc_set = {norm_pg3(v, p) for v in tc}

    all_pts: set[tuple[int, int, int, int]] = set()
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    if a or b or c or d:
                        all_pts.add(norm_pg3((a, b, c, d), p))
    ext = sorted(all_pts - tc_set)
    assert len(tc) == 8 and len(ext) == 392

    # Precompute all C(8,3)=56 planes spanned by 3 points of TC as normal vectors
    tc_triples = list(combinations(range(8), 3))
    dep1_by_pt: dict[tuple[int, int, int, int], int] = {}
    for pt in ext:
        cnt = sum(1 for i, j, l in tc_triples if det4_mod([tc[i], tc[j], tc[l], pt], p) == 0)
        dep1_by_pt[pt] = cnt
    dist1 = Counter(dep1_by_pt.values())

    # All minimum-dependency points (d1 == 5)
    min_pts = [pt for pt, c in dep1_by_pt.items() if c == 5]
    p1 = min_pts[0]  # (0, 0, 1, 0)
    assert p1 == (0, 0, 1, 0)

    # For k=10: fix p1 = (0,0,1,0) (TC + p1 is orbit-representative on 56 min-points)
    # and check all other 391 points p2 (exact over all 56 min-points x 391? Check p1 + all 391
    # AND verify globally over all pairs of min_pts and (5,7) pairs!)
    tc_pairs = list(combinations(range(8), 2))
    best_k10 = (999, None, None, 0, 0, 0)
    # Precompute coplanar pair-planes for p1
    for p2 in ext:
        if p2 == p1:
            continue
        d1 = dep1_by_pt[p1]
        d2 = dep1_by_pt[p2]
        if d1 + d2 >= best_k10[0]:
            continue
        d12 = sum(1 for i, j in tc_pairs if det4_mod([tc[i], tc[j], p1, p2], p) == 0)
        tot = d1 + d2 + d12
        if tot < best_k10[0]:
            best_k10 = (tot, p1, p2, d1, d2, d12)

    # Global verification across all pairs (u, v) in ext with d1 + d2 < 12 (only 5+5=10 can beat 12!)
    global_min = best_k10[0]
    for idx_a, pa in enumerate(min_pts):
        for pb in min_pts[idx_a + 1 :]:
            d12 = sum(1 for i, j in tc_pairs if det4_mod([tc[i], tc[j], pa, pb], p) == 0)
            if 10 + d12 < global_min:
                global_min = 10 + d12

    print("\n--- PG(3, 7) Twisted-Cubic Geometry (k=8 -> k=9, k=10) ---")
    print(f"  |PG(3,7)|={len(all_pts)}, |TC|=8, |ext|={len(ext)}")
    print(f"  k=9 dependent 4-set distribution: {dict(sorted(dist1.items()))}")
    print(f"  k=9 minimum: 5/126 dependent 4-sets -> {5 * 6 * 343} missing 4-tuples (witness p1={p1})")
    print(
        f"  k=10 global minimum (proven over all C(392,2) pairs): {global_min}/210 dependent 4-sets -> "
        f"{global_min * 6 * 343} missing 4-tuples"
    )
    print(
        f"    witness: p1={best_k10[1]} (d1={best_k10[3]}), p2={best_k10[2]} (d2={best_k10[4]}), "
        f"d12={best_k10[5]}, total={best_k10[0]}"
    )
    print("  Linear Augmentation Lower Bound N >= q^4 + (q-1)*q^3 (unchanged linear [k,4]_q base):")
    for q in (7, 8, 9, 11, 13):
        lb = q ** 4 + (q - 1) * (q ** 3)
        print(f"    q={q:2d}: q^4={q**4:5d}, q^4+(q-1)q^3={lb:5d}")
    print(f"  elapsed={time.perf_counter() - t0:.2f}s")
    return best_k10[1], best_k10[2]


# ---------------------------------------------------------------------------
# Part B2: Positive Controls (PC-1, PC-2) & Cheap Prototypes (q=7, q=8)
# ---------------------------------------------------------------------------

def pencil_odd_q(u: int, v: int, q: int) -> int:
    """Partition AG(2, q) (q odd) into (q+1)/2 intersecting line-pairs through (0,0).

    Symbol 0 gets lines y = 0 and x = 0 (2q-1 points, including origin (0,0)).
    Symbol m in 1..(q-1)/2 gets lines y = (2m-1)x and y = 2m*x (2q-2 non-origin points).
    """
    if u == 0 or v == 0:
        return 0
    slope = (v * pow(u, q - 2, q)) % q  # in 1..q-1
    return (slope + 1) // 2  # in 1..(q-1)/2


def build_pc1_poly2_q7() -> list[tuple[int, ...]]:
    """PC-1: CA(3577; 4, 9, 7) via odd-q poly2 with pencil cover of AG(2, 7)."""
    q = 7
    rows: list[tuple[int, ...]] = []

    # 1) Main OA(2401; 4, 8, 7) + pencil col 8 in {0, 1, 2, 3}
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = [(a + b * x + c * x * x + d * x * x * x) % q for x in range(q)]
                    r.append(d)
                    r.append(pencil_odd_q(c, d, q))
                    rows.append(tuple(r))

    # 2) Vertex-overlap repair blocks: 3 * 49 = 147 rows for col 8 in {1, 2, 3}
    # At (c, d) = (0, 0), col 8 took 0 instead of 1, 2, 3 -> add OA(49; 2, 7, 7) with d=0, col8=m.
    for m in (1, 2, 3):
        for a in range(q):
            for b in range(q):
                r = [(a + b * x) % q for x in range(q)] + [0, m]
                rows.append(tuple(r))

    # 3) Missing-symbol blocks: 3 * 343 = 1029 rows for col 8 in {4, 5, 6}
    # Exact OA(343; 3, 8, 7) on cols 0..7: (a + bx + cx^2 for x=0..6, col7 = c).
    for m in (4, 5, 6):
        for a in range(q):
            for b in range(q):
                for c in range(q):
                    r = [(a + b * x + c * x * x) % q for x in range(q)] + [c, m]
                    rows.append(tuple(r))

    assert len(rows) == 3577
    return rows


def build_pc2_pg3_q7(
    p1: tuple[int, int, int, int], p2: tuple[int, int, int, int]
) -> list[tuple[int, ...]]:
    """PC-2: CA(4459; 4, 10, 7) via linear PG(3,7) block + 6 shifted 3D subspaces."""
    q = 7
    tc = [(1, x, (x * x) % q, (x * x * x) % q) for x in range(q)] + [(0, 0, 0, 1)]
    pts = tc + [p1, p2]
    assert len(pts) == 10

    # Find a 1D shift vector u not in the row space of any dependent 4-subset,
    # equivalently find a 3D subspace H (normal w) avoiding all 1D kernels of dependent 4-sets.
    dep_kernels: set[tuple[int, int, int, int]] = set()
    for c0, c1, c2, c3 in combinations(range(10), 4):
        if det4_mod([pts[c0], pts[c1], pts[c2], pts[c3]], q) == 0:
            # Find non-zero kernel vector x with pts[ci] . x == 0 mod 7
            for a in range(q):
                for b in range(q):
                    for c in range(q):
                        for d in range(q):
                            if not (a or b or c or d):
                                continue
                            if all(
                                (pts[ci][0] * a + pts[ci][1] * b + pts[ci][2] * c + pts[ci][3] * d) % q == 0
                                for ci in (c0, c1, c2, c3)
                            ):
                                dep_kernels.add(norm_pg3((a, b, c, d), q))

    # Pick hyperplane H: {v : w . v = 0} such that no dependent kernel lies in H (i.e. w . ker != 0)
    # Wait: shifting H by (0,..,0, s_c) needs a codeword-free direction; simpler & exact:
    # Add 6 shifts of a 3D subspace H (size 343) by a vector e_shift in GF(7)^10 that has
    # non-zero syndrome on EVERY dependent 4-set!
    # First pick H = {d = 0} (or any hyperplane avoiding dep_kernels: w . ker != 0).
    good_w = None
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    if not (a or b or c or d):
                        continue
                    w = (a, b, c, d)
                    if all((w[0] * k[0] + w[1] * k[1] + w[2] * k[2] + w[3] * k[3]) % q != 0 for k in dep_kernels):
                        good_w = w
                        break
                if good_w:
                    break
            if good_w:
                break
        if good_w:
            break
    assert good_w is not None

    # Basis of H = {v in GF(7)^4 : good_w . v = 0}
    h_vecs = [
        (a, b, c, d)
        for a in range(q)
        for b in range(q)
        for c in range(q)
        for d in range(q)
        if (good_w[0] * a + good_w[1] * b + good_w[2] * c + good_w[3] * d) % q == 0
    ]
    assert len(h_vecs) == 343

    # For each dependent 4-set S, find a non-zero parity check vector alpha in GF(7)^4
    # with sum_{j=0..3} alpha_j * pts[S[j]] = 0. We want a shift vector delta in GF(7)^10
    # such that sum alpha_j * delta[S[j]] != 0 mod 7 for ALL 12 dependent 4-sets S.
    dep_checks: list[tuple[tuple[int, int, int, int], tuple[int, int, int, int]]] = []
    for comb in combinations(range(10), 4):
        if det4_mod([pts[ci] for ci in comb], q) == 0:
            # Find non-zero linear relation among the 4 points
            found = None
            for l0 in range(q):
                for l1 in range(q):
                    for l2 in range(q):
                        for l3 in range(q):
                            if not (l0 or l1 or l2 or l3):
                                continue
                            if all(
                                (l0 * pts[comb[0]][j] + l1 * pts[comb[1]][j] + l2 * pts[comb[2]][j] + l3 * pts[comb[3]][j]) % q == 0
                                for j in range(4)
                            ):
                                found = (l0, l1, l2, l3)
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            assert found is not None
            dep_checks.append((comb, found))
    assert len(dep_checks) == 12

    # Find shift vector delta supported on cols 8, 9 (only 49 choices!)
    delta = None
    for d8 in range(q):
        for d9 in range(q):
            vec = [0] * 8 + [d8, d9]
            if all(
                sum(alpha[j] * vec[comb[j]] for j in range(4)) % q != 0
                for comb, alpha in dep_checks
            ):
                delta = vec
                break
        if delta is not None:
            break
    assert delta is not None

    rows: list[tuple[int, ...]] = []
    # Main linear block: all 7^4 = 2401 vectors
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    rows.append(
                        tuple((pt[0] * a + pt[1] * b + pt[2] * c + pt[3] * d) % q for pt in pts)
                    )
    # 6 shifted copies of H
    for s in range(1, q):
        for a, b, c, d in h_vecs:
            rows.append(
                tuple(
                    (pt[0] * a + pt[1] * b + pt[2] * c + pt[3] * d + s * delta[ci]) % q
                    for ci, pt in enumerate(pts)
                )
            )
    assert len(rows) == 4459
    return rows


def test_double_poly2_q7() -> dict[str, int]:
    """Cheap k=10, q=7 Double-poly2 feasibility test (demonstrating odd-q conic obstruction)."""
    q = 7
    rows: list[tuple[int, ...]] = []

    # 1) Main OA(2401; 4, 8, 7) + col8 = pencil(c,d), col9 = pencil(a,b)
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = [(a + b * x + c * x * x + d * x * x * x) % q for x in range(q)]
                    r.extend([d, pencil_odd_q(c, d, q), pencil_odd_q(a, b, q)])
                    rows.append(tuple(r))

    # 2) Vertex repairs for col8 in {1,2,3} (c=d=0, col9 = pencil(a,b)) -> 147 rows
    for m in (1, 2, 3):
        for a in range(q):
            for b in range(q):
                r = [(a + b * x) % q for x in range(q)] + [0, m, pencil_odd_q(a, b, q)]
                rows.append(tuple(r))

    # 3) Vertex repairs for col9 in {1,2,3} (a=b=0, col8 = pencil(c,d)) -> 147 rows
    for m in (1, 2, 3):
        for c in range(q):
            for d in range(q):
                r = [(c * x * x + d * x * x * x) % q for x in range(q)] + [d, pencil_odd_q(c, d, q), m]
                rows.append(tuple(r))

    # 4) 3 blocks of OA(343; 3, 8, 7) for col8 in {4,5,6}, sliced by internal point (1,0,1)
    #    of PG(2,7) into 7 slices s = (a + c) mod 7 (4 secant-pairs -> non-OA, 3 non-secants).
    #    Bijection s -> c9 sends {4,5,6}->{4,5,6} (cyclic shift) and {0,1,2,3}->{0,1,2,3},
    #    so each col9 in {4,5,6} collects all 3 distinct slices s in {4,5,6} across m8 in {4,5,6}.
    for m8 in (4, 5, 6):
        shift = m8 - 4
        for a in range(q):
            for b in range(q):
                for c in range(q):
                    s = (a + c) % q
                    c9 = (4 + (s - 4 + shift) % 3) if s >= 4 else ((s + shift) % 4)
                    r = [(a + b * x + c * x * x) % q for x in range(q)] + [c, m8, c9]
                    rows.append(tuple(r))

    # 5) Remaining 3 * 4 * 49 = 588 slices for col9 in {4,5,6}: slices s in {0,1,2,3}
    #    paired with col8 = s -> together with Step 4, each col9 in {4,5,6} has exact OA(343;3,8,7).
    for m9 in (4, 5, 6):
        for s in (0, 1, 2, 3):
            for b in range(q):
                for c in range(q):
                    a = (s - c) % q
                    r = [(a + b * x + c * x * x) % q for x in range(q)] + [c, s, m9]
                    rows.append(tuple(r))

    # 6) 9 vertex-collision rows (0^8, v8, v9) for v8, v9 in {1,2,3}
    for v8 in (1, 2, 3):
        for v9 in (1, 2, 3):
            rows.append((0,) * 8 + (v8, v9))

    assert len(rows) == 4321

    # Partition 4-sets into 4 classes to localize missing tuples exactly
    c_base = [c for c in combinations(range(10), 4) if 8 not in c and 9 not in c]
    c_o8 = [c for c in combinations(range(10), 4) if 8 in c and 9 not in c]
    c_o9 = [c for c in combinations(range(10), 4) if 9 in c and 8 not in c]
    c_both = [c for c in combinations(range(10), 4) if 8 in c and 9 in c]

    m_base, b_base = count_missing_t4(rows, 10, q, c_base)
    m_o8, b_o8 = count_missing_t4(rows, 10, q, c_o8)
    m_o9, b_o9 = count_missing_t4(rows, 10, q, c_o9)
    m_both, b_both = count_missing_t4(rows, 10, q, c_both)
    return {
        "N": len(rows),
        "miss_0_7": m_base,
        "miss_only_8": m_o8,
        "miss_only_9": m_o9,
        "miss_both_8_9": m_both,
        "bad_both_8_9": b_both,
    }


def pencil_even_q8(u: int, v: int) -> int:
    """Partition AG(2, 8) into 4 intersecting line-pairs through (0, 0).

    Symbol 0: u == 0 or v == 0 (15 points, incl. origin).
    Symbol 1: v/u in {1, 2} (14 points).
    Symbol 2: v/u in {3, 4} (14 points).
    Symbol 3: v/u in {5, 6} (14 points).
    Wait: 7 non-zero slopes {1..7} -> pair (1,2)->1, (3,4)->2, (5,6)->3, and slope 7 -> 0!
    Wait: check blocking property! Every line NOT through (0,0) has 8 points with 7 distinct
    slopes plus u=0 and v=0 -> misses at most 1 slope! Actually a line y = m*x + b (b!=0)
    hits u=0 (at (0,b)), v=0 (at (b/m, 0)), and every slope s != m exactly once!
    So pairing any 2 lines through (0,0) forms a blocking set of ALL affine lines:
      sym 0: {u=0, v=0, v=7u} (3 lines, 22 pts)
      sym 1: {v=1u, v=2u} (2 lines, 14 non-origin pts)
      sym 2: {v=3u, v=4u} (2 lines, 14 non-origin pts)
      sym 3: {v=5u, v=6u} (2 lines, 14 non-origin pts)
    Every affine line misses at most 1 of the 9 lines through (0,0), hence hits EVERY
    pair (size >= 2) at least once!
    """
    if u == 0 or v == 0:
        return 0
    slope = GF8_MUL[v][GF8_INV[u]]
    if slope == 7:
        return 0
    return (slope + 1) // 2  # 1,2->1; 3,4->2; 5,6->3


def build_hyperoval_double_poly2_q8() -> tuple[list[tuple[int, ...]], tuple[int, int]]:
    """Even-q Hyperoval Double-poly2: CA(7561; 4, 11, 8) (-119 below ca-tools @ c5f447d).

    Uses the 10-point hyperoval in PG(2, 8):
      cols 0..7: (1, x, x^2) for x in GF(8)
      col 8:     (0, 0, 1)   (point at infinity of conic)
      col 9:     (0, 1, 0)   (nucleus of conic in char 2!)
    yielding an exact OA(512; 3, 10, 8) that partitions cleanly into 8 OA(64; 2, 9, 8) slices
    by the 10th column b = (0, 1, 0) . (a, b, c)!
    """
    # Verify hyperoval OA(512; 3, 10, 8)
    ho_rows: list[tuple[int, ...]] = []
    for a in range(8):
        for b in range(8):
            for c in range(8):
                r = [
                    a ^ GF8_MUL[b][x] ^ GF8_MUL[c][GF8_MUL[x][x]]
                    for x in range(8)
                ]
                r.append(c)  # col 8 = (0,0,1)
                r.append(b)  # col 9 = (0,1,0) nucleus
                ho_rows.append(tuple(r))
    ho_ok, ho_tot = check_oa_t(ho_rows, list(range(10)), 3, 8)
    assert (ho_ok, ho_tot) == (120, 120)

    # Precompute the 8 disjoint OA(64; 2, 9, 8) slices indexed by nucleus b in 0..7
    # Each slice has cols 0..8: (a + b*x + c*x^2 for x in GF(8), col8 = c)
    slices: list[list[tuple[int, ...]]] = []
    for b in range(8):
        sl = []
        for a in range(8):
            for c in range(8):
                r = [a ^ GF8_MUL[b][x] ^ GF8_MUL[c][GF8_MUL[x][x]] for x in range(8)]
                r.append(c)
                sl.append(tuple(r))
        slices.append(sl)

    rows: list[tuple[int, ...]] = []

    # 1) Main OA(4096; 4, 9, 8) on cols 0..8: f(x) = a + b*x + c*x^2 + d*x^3, col8 = d
    #    col9  = pencil_even_q8(c, d) in {0,1,2,3}
    #    col10 = pencil_even_q8(a, b) in {0,1,2,3}
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    r = []
                    for x in range(8):
                        x2 = GF8_MUL[x][x]
                        x3 = GF8_MUL[x2][x]
                        r.append(a ^ GF8_MUL[b][x] ^ GF8_MUL[c][x2] ^ GF8_MUL[d][x3])
                    r.append(d)
                    r.append(pencil_even_q8(c, d))
                    r.append(pencil_even_q8(a, b))
                    rows.append(tuple(r))

    # 2) Vertex repairs for col9 in {1,2,3} at (c,d) = (0,0) -> 3 * 64 = 192 rows
    for m9 in (1, 2, 3):
        for a in range(8):
            for b in range(8):
                r = [a ^ GF8_MUL[b][x] for x in range(8)] + [0, m9, pencil_even_q8(a, b)]
                rows.append(tuple(r))

    # 3) Vertex repairs for col10 in {1,2,3} at (a,b) = (0,0) -> 3 * 64 = 192 rows
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

    # 4) 4 hyperoval OA(512; 3, 10, 8) blocks for col9 in {4,5,6,7} -> 2048 rows.
    #    Map nucleus b -> col10 = b ^ (m9 - 4) (bijection preserving {0..3} and {4..7}).
    #    Each m9 block is an exact OA(512; 3, 10, 8) on (cols 0..8, col10), and across
    #    m9 in {4..7} each col10 in {4..7} receives the 4 distinct slices b in {4,5,6,7}.
    for m9 in (4, 5, 6, 7):
        shift = m9 - 4
        for b in range(8):
            c10 = b ^ shift
            for base in slices[b]:
                rows.append(base + (m9, c10))

    # 5) Remaining 4 distinct OA(64; 2, 9, 8) slices b in {0,1,2,3} for each col10 in {4,5,6,7}
    #    paired with col9 in {0,1,2,3} -> 4 * 4 * 64 = 1024 rows.
    #    Together with Step 4, each col10 in {4..7} holds all 8 slices = full OA(512; 3, 9, 8).
    for m10 in (4, 5, 6, 7):
        for idx, m9 in enumerate((0, 1, 2, 3)):
            b = idx
            for base in slices[b]:
                rows.append(base + (m9, m10))

    # 6) 9 vertex-collision rows (0^9, v9, v10) for v9, v10 in {1,2,3} -> 9 rows
    for v9 in (1, 2, 3):
        for v10 in (1, 2, 3):
            rows.append((0,) * 9 + (v9, v10))

    assert len(rows) == 7561
    return rows, (ho_ok, ho_tot)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 5B-1 t=4 NEAR_BUSH analysis & prototypes")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory with downloaded ca-tools arrays")
    parser.add_argument("--out-dir", type=Path, required=True, help="Scratch directory for generated test arrays")
    args = parser.parse_args()

    t_start = time.perf_counter()

    print("=== PART A: STRUCTURE INSPECTION OF VERIFIED k = q+2 ARRAYS ===")
    for fname, q in [
        ("CA_3556_4_9_7.txt", 7),
        ("CA_6101_4_10_8.txt", 8),
        ("CA_9801_4_11_9.txt", 9),
    ]:
        p = args.data_dir / fname
        if not p.exists():
            raise FileNotFoundError(f"Missing required input array: {p}")
        inspect_ca_array(fname, p, q)

    print("\n--- Universal odd-q poly2 pencil-cover formula: N = q^4 + ((q^2 - 1)/2) * q^2 ---")
    for q in (7, 9, 11, 13):
        n_p2 = q ** 4 + ((q * q - 1) // 2) * (q * q)
        print(f"  q={q:2d}, k={q+2:2d}: poly2 = {n_p2}")

    print("\n=== PART B: PG(3,7) GEOMETRY, POSITIVE CONTROLS & CHEAP PROTOTYPES ===")
    p1, p2 = analyze_pg3_7()

    # PC-1: CA(3577; 4, 9, 7)
    t0 = time.perf_counter()
    pc1 = build_pc1_poly2_q7()
    m1, b1 = count_missing_t4(pc1, 9, 7)
    pc1_path = args.out_dir / "pc1_poly2_CA_3577_4_9_7.txt"
    write_array(pc1_path, pc1)
    print(f"\n[PC-1] poly2 CA(3577; 4, 9, 7): N={len(pc1)}, uniq={len(set(pc1))}, "
          f"missing={m1} (bad_4sets={b1}), elapsed={time.perf_counter()-t0:.2f}s -> {pc1_path.name}")
    assert m1 == 0

    # PC-2: CA(4459; 4, 10, 7)
    t0 = time.perf_counter()
    pc2 = build_pc2_pg3_q7(p1, p2)
    m2, b2 = count_missing_t4(pc2, 10, 7)
    pc2_path = args.out_dir / "pc2_pg3_CA_4459_4_10_7.txt"
    write_array(pc2_path, pc2)
    print(f"[PC-2] PG(3,7)+6H CA(4459; 4, 10, 7): N={len(pc2)}, uniq={len(set(pc2))}, "
          f"missing={m2} (bad_4sets={b2}), elapsed={time.perf_counter()-t0:.2f}s -> {pc2_path.name}")
    assert m2 == 0

    # Cheap Test 1: Double-poly2 on q=7, k=10
    t0 = time.perf_counter()
    dp7 = test_double_poly2_q7()
    print(f"[TEST-q7] Double-poly2 (q=7, k=10): {dp7}, elapsed={time.perf_counter()-t0:.2f}s")

    # Cheap Test 2: Hyperoval Double-poly2 on q=8, k=11
    t0 = time.perf_counter()
    ho8, (ho_ok, ho_tot) = build_hyperoval_double_poly2_q8()
    m8, b8 = count_missing_t4(ho8, 11, 8)
    ho8_path = args.out_dir / "test_hyperoval_CA_7561_4_11_8.txt"
    write_array(ho8_path, ho8)
    print(
        f"[TEST-q8] Hyperoval Double-poly2 CA(7561; 4, 11, 8): hyperoval_OA(512;3,10,8)={ho_ok}/{ho_tot}, "
        f"N={len(ho8)}, uniq={len(set(ho8))}, missing={m8} (bad_4sets={b8}), "
        f"delta_vs_c5f447d={len(ho8)-7680}, elapsed={time.perf_counter()-t0:.2f}s -> {ho8_path.name}"
    )
    assert m8 == 0 and len(set(ho8)) == 7561

    print(f"\nTotal runtime: {time.perf_counter() - t_start:.2f}s")


if __name__ == "__main__":
    main()
