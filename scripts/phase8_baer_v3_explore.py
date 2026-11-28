#!/usr/bin/env python3
"""Phase 8 (Baustelle 1): Baer-v3 construction & exploration.

Features (pure Python, std-only, uses GeneralGF from scripts/gen_general_tqv.py):
  1. Cross-Group K-Promotion + Redundant-Slot Recycling (Baer-v3):
     Promotes k_promo K-classes K(i_src, j) onto spare free lines L_dst in {w2=0} (a-side)
     and L'_dst in {w1=0} (b-side), deleting their n reps from d = 0 and recycling:
       - their n redundant a-slots on w = i_dst + i_src*om (covering (V_src, K(i_dst, *)) free),
       - their n redundant b-slots on w = i_src + i_dst*om (covering (K(i_dst, *), V_src) free),
       - their (n - 1) redundant b-slots on L_src and a-slots on L'_src (covering (V_src, *) and (*, V_src) free).
     Strictly beats Baer-v2 on EVERY target cell of q = 9, 16, 25:
       q =  9: v = 6: 87 (< 93), v = 9: 108 (< 111)
       q = 16: v = 12: 280 (< 292), v = 13: 284 (< 292), v = 14: 298 (< 300),
               v = 15: 316 (< 318), v = 16: 334 (< 336)
       q = 25: v = 20: 685 (< 705), v = 21: 690 (< 705), v = 22: 708 (< 715),
               v = 23: 733 (< 739), v = 24: 762 (< 767), v = 25: 791 (< 795)
  2. Complete AG(2, 9) Baer-subplane + full-line catalog analysis (657 sets).
  3. Exhaustive 3rd/4th Baer direction & shifted anchor d* != 0 obstruction analysis on q = 9, 16, 25.
  4. F = 0 K-class shift-to-(c2 = 0) obstruction check on q = 9, 16, 25.

Usage:
  python3 scripts/phase8_baer_v3_explore.py --mode all --out-dir data/phase8_baer_v3
  python3 scripts/phase8_baer_v3_explore.py --mode baer3-construct --out-dir data/phase8_baer_v3
  python3 scripts/phase8_baer_v3_explore.py --mode q9-catalog
  python3 scripts/phase8_baer_v3_explore.py --mode baer3-16-25
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF, factor_prime_power  # noqa: E402


# Baer-v2 / Baer-v1 (F=0) reference targets from task specification (must be strictly beaten)
BAER_V2_TARGETS: dict[tuple[int, int], int] = {
    (9, 6): 93,
    (9, 9): 111,
    (16, 12): 292,
    (16, 14): 300,
    (16, 15): 318,
    (16, 16): 336,
    (25, 20): 705,
    (25, 21): 705,
    (25, 22): 715,
    (25, 23): 739,
    (25, 24): 767,
    (25, 25): 795,
}


@dataclass(frozen=True)
class BaerField:
    q: int
    n: int
    gf: GeneralGF
    add: tuple[tuple[int, ...], ...]
    sub: tuple[tuple[int, ...], ...]
    mul: tuple[tuple[int, ...], ...]
    neg: tuple[int, ...]
    inv: tuple[int, ...]
    fn: tuple[int, ...]
    num: dict[int, int]
    om: int
    p1: tuple[int, ...]
    p2: tuple[int, ...]


def gf_pow(mul, x: int, e: int) -> int:
    if e == 0:
        return 1
    if x == 0:
        return 0
    r = 1
    b = x
    while e > 0:
        if e & 1:
            r = mul[r][b]
        b = mul[b][b]
        e >>= 1
    return r


def build_field(q: int) -> BaerField:
    n = math.isqrt(q)
    assert n * n == q and n >= 2
    factor_prime_power(n)
    gf = GeneralGF(q)
    add = tuple(tuple(row) for row in gf.add)
    mul = tuple(tuple(row) for row in gf.mul)
    neg = tuple(next(y for y in range(q) if add[x][y] == 0) for x in range(q))
    sub = tuple(tuple(add[x][neg[y]] for y in range(q)) for x in range(q))
    inv = (-1,) + tuple(next(y for y in range(1, q) if mul[x][y] == 1) for x in range(1, q))
    fn = tuple(x for x in range(q) if gf_pow(mul, x, n) == x)
    assert len(fn) == n
    num = {x: i for i, x in enumerate(fn)}
    om = next(x for x in range(q) if x not in num)
    p1 = [-1] * q
    p2 = [-1] * q
    for z1 in fn:
        for z2 in fn:
            z = add[z1][mul[z2][om]]
            p1[z] = z1
            p2[z] = z2
    assert all(x != -1 for x in p1)
    return BaerField(q, n, gf, add, sub, mul, neg, inv, fn, num, om, tuple(p1), tuple(p2))


def check_mr(bf: BaerField, v: int, reps: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    """Independent M(R) checker: returns (miss_pts, miss_lines, miss_pairs, dup_reps)."""
    q = bf.q
    add, mul = bf.add, bf.mul
    dup = len(reps) - len(set(reps))
    pts = {(c, d) for (c, d, a, b) in reps}
    miss_pts = q * q - len(pts)
    pairs = {(a, b) for (c, d, a, b) in reps}
    miss_pairs = v * v - len(pairs)
    miss_lines = 0
    for side in (2, 3):
        seen = set()
        for r in reps:
            c, d, s = r[0], r[1], r[side]
            for al in range(q):
                seen.add((s, al, add[c][mul[al][d]]))
        miss_lines += v * q * q - len(seen)
    return miss_pts, miss_lines, miss_pairs, dup


def write_reps_file(reps: list[tuple[int, int, int, int]], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    sreps = sorted(reps, key=lambda r: (r[1], r[0], r[2], r[3]))
    data = "".join(f"{c} {d} {a} {b}\n" for (c, d, a, b) in sreps).encode("utf-8")
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


# =============================================================================
# Part 1: Baer-v3 Cross-Group K-Promotion + Redundant-Slot Recycling
# =============================================================================

def build_k_skeleton(bf: BaerField):
    q, n = bf.q, bf.n
    mul, sub, inv, fn, num, om, p1, p2 = (
        bf.mul, bf.sub, bf.inv, bf.fn, bf.num, bf.om, bf.p1, bf.p2
    )

    def sym_K(i: int, j: int) -> int:
        return (num[i] - 1) * n + num[j]

    a_fixed: dict[tuple[int, int], int] = {}
    b_fixed: dict[tuple[int, int], int] = {}
    lines_w2_0: dict[int, int] = {}
    lines_w1_0: dict[int, int] = {}

    for d in range(1, q):
        w = inv[d]
        w1, w2 = p1[w], p2[w]
        if w2 == 0:
            lines_w2_0[w1] = d
        if w1 == 0:
            lines_w1_0[w2] = d
        w2_om = mul[w2][om]
        w1_om = mul[w1][om]
        for c in range(q):
            a_fixed[(c, d)] = sym_K(w2, p2[mul[sub[c][w2_om]][w]]) if w2 != 0 else -1
            b_fixed[(c, d)] = sym_K(w1, p1[mul[sub[c][w1_om]][w]]) if w1 != 0 else -1

    return sym_K, a_fixed, b_fixed, lines_w2_0, lines_w1_0


def build_baer_v3_cross_kpromo(
    bf: BaerField, F: int, r: int, promo_sources: tuple[int, ...]
) -> list[tuple[int, int, int, int]]:
    """Construct Baer-v3 representative list with Cross-Group K-Promotion + Redundant-Slot Recycling.

    Parameters:
      F             : 0 .. n  (v = q - n + F)
      r             : 0 .. min(F, n - 1), number of dedicated full lines V_0..V_{r-1} on fn_nz[0..r-1]
      promo_sources : tuple of length k_promo <= (n - 1 - r); entry p gives src_idx in 0..n-2 whose
                      next unpromoted K-class K(fn_nz[src_idx], fn[j]) is promoted to a full horizontal
                      line on spare line dst_idx = r + p (i_dst = fn_nz[r + p]).
                      Must leave at least 1 unpromoted K-class in every group src_idx (count <= n - 1).
    """
    q, n = bf.q, bf.n
    v = q - n + F
    k_promo = len(promo_sources)
    assert 0 <= F <= n
    assert 0 <= r <= min(F, n - 1)
    assert 0 <= k_promo <= (n - 1 - r)

    add, mul, inv, fn, num, om, p1, p2 = (
        bf.add, bf.mul, bf.inv, bf.fn, bf.num, bf.om, bf.p1, bf.p2
    )
    sym_K, a_fixed, b_fixed, lines_w2_0, lines_w1_0 = build_k_skeleton(bf)
    fn_nz = list(fn[1:])  # length n - 1

    def sym_V(m: int) -> int:
        return q - n + m

    v_full_i = fn_nz[:r]
    # Assign promoted K-classes to spare lines dst_idx = r .. r + k_promo - 1
    used_j_per_src = [0] * (n - 1)
    promo_by_dst_i: dict[int, tuple[int, int, int]] = {}  # i_dst -> (K_sym, i_src, src_idx)
    promoted_k_syms: set[int] = set()
    # Map (d, K_sym) -> V_u for redundant-slot recycling on w = i_dst + i_src*om (a) and w = i_src + i_dst*om (b)
    recycle_a_line: dict[tuple[int, int], int] = {}
    recycle_b_line: dict[tuple[int, int], int] = {}
    # Map u (in 0..r-1) -> list of promoted K_syms belonging to group i_src = fn_nz[u]
    promo_in_vgroup: dict[int, list[int]] = {u: [] for u in range(r)}

    for p_idx, src_idx in enumerate(promo_sources):
        assert 0 <= src_idx < n - 1
        j_pos = used_j_per_src[src_idx]
        assert j_pos < n - 1, "Must keep at least 1 unpromoted K-class per group for d = 0"
        used_j_per_src[src_idx] += 1
        i_src = fn_nz[src_idx]
        i_dst = fn_nz[r + p_idx]
        k_sym = sym_K(i_src, fn[j_pos])
        promo_by_dst_i[i_dst] = (k_sym, i_src, src_idx)
        promoted_k_syms.add(k_sym)

        if src_idx < r:
            vu = sym_V(src_idx)
            promo_in_vgroup[src_idx].append(k_sym)
            # Line w = i_dst + i_src*om: a = k_sym is 100% redundant (b = K(i_dst, *) already hit on L_dst)!
            d_a = inv[add[i_dst][mul[i_src][om]]]
            recycle_a_line[(d_a, k_sym)] = vu
            # Line w = i_src + i_dst*om: b = k_sym is 100% redundant (a = K(i_dst, *) already hit on L'_dst)!
            d_b = inv[add[i_src][mul[i_dst][om]]]
            recycle_b_line[(d_b, k_sym)] = vu

    # 1. Build initial d != 0 grid (recording freeable slots on L_u and L'_u for recycling!)
    # grid_d_nz[(c, d)] = [a, b]
    grid_a: dict[tuple[int, int], int] = {}
    grid_b: dict[tuple[int, int], int] = {}
    freed_b_slots: dict[int, list[tuple[int, int]]] = {u: [] for u in range(r)}  # a = V_u fixed, b free!
    freed_a_slots: dict[int, list[tuple[int, int]]] = {u: [] for u in range(r)}  # b = V_u fixed, a free!

    for d in range(1, q):
        w = inv[d]
        w1, w2 = p1[w], p2[w]
        for c in range(q):
            a = a_fixed[(c, d)]
            b = b_fixed[(c, d)]
            if a == -1:
                if w1 in v_full_i:
                    a = sym_V(v_full_i.index(w1))
                elif w1 in promo_by_dst_i:
                    a = promo_by_dst_i[w1][0]
                else:
                    m_a = num[p2[mul[c][w]]]
                    a = sym_V(m_a) if m_a < F else (sym_V(0) if F >= 1 else 0)
            else:
                if (d, a) in recycle_a_line:
                    a = recycle_a_line[(d, a)]

            if b == -1:
                if w2 in v_full_i:
                    b = sym_V(v_full_i.index(w2))
                elif w2 in promo_by_dst_i:
                    b = promo_by_dst_i[w2][0]
                else:
                    m_b = num[p1[mul[c][w]]]
                    b = sym_V(m_b) if m_b < F else (sym_V(0) if F >= 1 else 0)
            else:
                if (d, b) in recycle_b_line:
                    b = recycle_b_line[(d, b)]

            grid_a[(c, d)] = a
            grid_b[(c, d)] = b

    # Collect (n - 1) freeable slots per promoted K_sym in group u on L_u (b-side) and L'_u (a-side)!
    for u in range(r):
        i_u = v_full_i[u]
        d_Lu = lines_w2_0[i_u]
        d_Lpu = lines_w1_0[i_u]
        for k_sym in promo_in_vgroup[u]:
            pts_b = [c for c in range(q) if grid_b[(c, d_Lu)] == k_sym]
            assert len(pts_b) == n
            # Keep pts_b[0] for (V_u, k_sym); free the remaining n - 1 points!
            for c in pts_b[1:]:
                freed_b_slots[u].append((c, d_Lu))
            pts_a = [c for c in range(q) if grid_a[(c, d_Lpu)] == k_sym]
            assert len(pts_a) == n
            # Keep pts_a[0] for (k_sym, V_u); free the remaining n - 1 points!
            for c in pts_a[1:]:
                freed_a_slots[u].append((c, d_Lpu))

    # Compute pairs already covered by non-freed d != 0 entries
    freed_b_set = {pt for pts in freed_b_slots.values() for pt in pts}
    freed_a_set = {pt for pts in freed_a_slots.values() for pt in pts}
    # Note: freed_b_set lies on {w2 == 0}, freed_a_set lies on {w1 == 0}, so they are DISJOINT!
    assert freed_b_set.isdisjoint(freed_a_set)

    covered_pairs: set[tuple[int, int]] = set()
    for pt in grid_a:
        if pt not in freed_b_set and pt not in freed_a_set:
            covered_pairs.add((grid_a[pt], grid_b[pt]))

    r_syms = [sym_V(m) for m in range(r)]
    s_syms = [sym_V(m) for m in range(r, F)]
    s = len(s_syms)
    leftover = {(a, b) for a in range(v) for b in range(v) if (a, b) not in covered_pairs}

    # Balanced symmetric slot-filling across freed_b_slots[u] (a=V_u fixed) and freed_a_slots[u] (b=V_u fixed):
    # Step A: Place diagonal (V_u, V_u) on L_u (1 slot) and off-diagonal (V_u, V_w) (u != w) on L'_w (1 slot),
    #         so every u uses 1 slot on L_u (diagonal) and (r - 1) slots on L'_u (off-diagonals), keeping
    #         remaining capacity on L_u and L'_u balanced!
    # Step B: Cover symmetric pairs (V_u, K_promo) & (K_promo, V_u) (saves 2 full reps when both fit!).
    # Step C: Cover symmetric pairs (V_u, V_s) & (V_s, V_u) TOGETHER (1 slot on L_u + 1 slot on L'_u),
    #         so any uncovered V_s stays symmetric and costs only +1 split instead of +2 asymmetric reps!
    # Step D: Fill any remaining single slots with remaining missing pairs (V_u, *) or (*, V_u).
    b_ptr = [0] * r
    a_ptr = [0] * r

    def put_b(u: int, tgt: int) -> bool:
        if b_ptr[u] < len(freed_b_slots[u]) and (sym_V(u), tgt) in leftover:
            grid_b[freed_b_slots[u][b_ptr[u]]] = tgt
            leftover.discard((sym_V(u), tgt))
            b_ptr[u] += 1
            return True
        return False

    def put_a(u: int, tgt: int) -> bool:
        if a_ptr[u] < len(freed_a_slots[u]) and (tgt, sym_V(u)) in leftover:
            grid_a[freed_a_slots[u][a_ptr[u]]] = tgt
            leftover.discard((tgt, sym_V(u)))
            a_ptr[u] += 1
            return True
        return False

    # Step A: {V_0..V_{r-1}}^2 balanced across L_u (diag) and L'_w (off-diag)
    for u in range(r):
        if not put_b(u, sym_V(u)):
            put_a(u, sym_V(u))
    for u in range(r):
        for w in range(r):
            if u != w:
                # Prefer L'_w (a-slot) so L_u and L'_u stay balanced; fallback to L_u (b-slot)
                if not put_a(w, sym_V(u)):
                    put_b(u, sym_V(w))

    # Step B: (V_u, K_promo) & (K_promo, V_u)
    for u in range(r):
        for kp_sym in sorted(promoted_k_syms):
            put_b(u, kp_sym)
            put_a(u, kp_sym)

    # Step C: Symmetric pairs (V_u, V_s) & (V_s, V_u) matched together
    for u in range(r):
        for Vs in s_syms:
            if (sym_V(u), Vs) in leftover and (Vs, sym_V(u)) in leftover:
                if b_ptr[u] < len(freed_b_slots[u]) and a_ptr[u] < len(freed_a_slots[u]):
                    put_b(u, Vs)
                    put_a(u, Vs)

    # Step D: Any remaining freed slots (single-sided or remaining non-promoted K)
    nonpromo_k = [k for k in range(q - n) if k not in promoted_k_syms]
    for u in range(r):
        for tgt in s_syms + nonpromo_k:
            if (sym_V(u), tgt) in leftover and (tgt, sym_V(u)) in leftover:
                if b_ptr[u] < len(freed_b_slots[u]) and a_ptr[u] < len(freed_a_slots[u]):
                    put_b(u, tgt)
                    put_a(u, tgt)
        for tgt in r_syms + sorted(promoted_k_syms) + s_syms + nonpromo_k:
            put_b(u, tgt)
            put_a(u, tgt)

    reps: list[tuple[int, int, int, int]] = [
        (c, d, grid_a[(c, d)], grid_b[(c, d)]) for d in range(1, q) for c in range(q)
    ]

    # 2. Build d = 0 with exact zero-cost swaps + symmetric +1 splits + c2 = 0
    c_by_i: dict[int, list[int]] = {i: [c for c in range(q) if p2[c] == i] for i in fn}
    unswapped_vs_pts: dict[int, list[int]] = {Vs: [] for Vs in s_syms}

    for i in fn_nz:
        pts_i = c_by_i[i]
        active_k = [sym_K(i, j) for j in fn if sym_K(i, j) not in promoted_k_syms]

        need_swap_vs = [
            Vs for Vs in s_syms
            if any((Vs, K) in leftover and (K, Vs) in leftover for K in active_k)
        ]
        need_split_vr = [
            Vr for Vr in r_syms
            if any((Vr, K) in leftover and (K, Vr) in leftover for K in active_k)
        ]
        ns_sw = len(need_swap_vs)
        nr_sp = len(need_split_vr)
        assert ns_sw + nr_sp <= n

        for x, c in enumerate(pts_i):
            swapped_vs_here: set[int] = set()
            for k_idx, K in enumerate(active_k):
                slot = (k_idx + x) % n
                if slot < ns_sw:
                    Vs = need_swap_vs[slot]
                    reps.append((c, 0, Vs, K))
                    reps.append((c, 0, K, Vs))
                    leftover.discard((Vs, K))
                    leftover.discard((K, Vs))
                    swapped_vs_here.add(Vs)
                elif slot < ns_sw + nr_sp:
                    Vr = need_split_vr[slot - ns_sw]
                    if (Vr, K) in leftover or (K, Vr) in leftover:
                        reps.append((c, 0, Vr, K))
                        reps.append((c, 0, K, Vr))
                        leftover.discard((Vr, K))
                        leftover.discard((K, Vr))
                    else:
                        reps.append((c, 0, K, K))
                        leftover.discard((K, K))
                else:
                    reps.append((c, 0, K, K))
                    leftover.discard((K, K))

            for Vs in s_syms:
                if Vs not in swapped_vs_here:
                    unswapped_vs_pts[Vs].append(c)

    # c2 = 0 (n points):
    # - First min(n, s) points x = 0..s-1: s x s cyclic Latin square covering all s^2 pairs of s_syms^2
    #   and covering every Vs on both sides at those s points.
    # - Remaining (n - s) points x = s..n-1: diagonal (c_x, 0, Vs, Vs) reps are 100% redundant as pairs,
    #   so add them to unswapped_vs_pts[Vs] where they can be split at +1 for symmetric (Vs, U) & (U, Vs)!
    pts_0 = c_by_i[0]
    if s >= 1:
        for x in range(s):
            c = pts_0[x]
            for m in range(s):
                sa = s_syms[m]
                sb = s_syms[(m + x) % s]
                reps.append((c, 0, sa, sb))
                leftover.discard((sa, sb))
        for x in range(s, n):
            c = pts_0[x]
            for Vs in s_syms:
                unswapped_vs_pts[Vs].append(c)

    # Place unswapped (c, 0, Vs, Vs) reps (on c2 != 0 and x = s..n-1 of c2 = 0), splitting for
    # any remaining symmetric missing pairs (Vs, U) & (U, Vs) where U not in s_syms!
    for Vs in s_syms:
        partners = [
            U for U in range(v)
            if U not in s_syms and (Vs, U) in leftover and (U, Vs) in leftover
        ]
        avail_c = unswapped_vs_pts[Vs]
        for idx_c, c in enumerate(avail_c):
            if idx_c < len(partners):
                U = partners[idx_c]
                reps.append((c, 0, Vs, U))
                reps.append((c, 0, U, Vs))
                leftover.discard((Vs, U))
                leftover.discard((U, Vs))
            else:
                reps.append((c, 0, Vs, Vs))
                leftover.discard((Vs, Vs))

    rem_list = sorted(leftover)
    used_pts_0 = set(pts_0) if s >= 1 else set()
    reps_set = set(reps)
    for idx_p, (a, b) in enumerate(rem_list):
        placed = False
        for off in range(n):
            c = pts_0[(idx_p + off) % n]
            if (c, 0, a, b) not in reps_set:
                reps.append((c, 0, a, b))
                reps_set.add((c, 0, a, b))
                used_pts_0.add(c)
                placed = True
                break
        if not placed:
            for c in range(q):
                if (c, 0, a, b) not in reps_set:
                    reps.append((c, 0, a, b))
                    reps_set.add((c, 0, a, b))
                    break

    for c in pts_0:
        if c not in used_pts_0:
            fill = sym_V(0) if F >= 1 else 0
            reps.append((c, 0, fill, fill))

    return reps


def enumerate_promo_configs(n: int, r: int) -> list[tuple[int, ...]]:
    """Generate representative (up to symmetry) promo_sources tuples for a given (n, r)."""
    max_kp = n - 1 - r
    configs: list[tuple[int, ...]] = [()]
    for kp in range(1, max_kp + 1):
        # Allow sources from 0..r-1 (V-groups, cross-group recycling!) and self-group (dst_idx = r + p)
        # To keep search tiny and clean: choose sources from {0..r-1} U {-1 (meaning self dst_idx)}
        # Wait: since r <= 4 and kp <= 4, total non-decreasing tuples from {0..r-1} plus self is tiny!
        if r == 0:
            # Self-group promotion: src_idx = p for p = 0..kp-1
            configs.append(tuple(range(kp)))
        else:
            # All combinations with replacement of length kp from 0..r-1 (cross-group from V-groups)
            for comb in itertools.combinations_with_replacement(range(r), kp):
                if all(comb.count(u) <= n - 1 for u in range(r)):
                    configs.append(comb)
            # Also allow mixing k_cross from 0..r-1 and k_self self-promoted spare lines
            for k_self in range(1, kp + 1):
                k_cross = kp - k_self
                for comb in itertools.combinations_with_replacement(range(r), k_cross):
                    if all(comb.count(u) <= n - 1 for u in range(r)):
                        cfg = comb + tuple(r + k_cross + j for j in range(k_self))
                        configs.append(cfg)
    return configs


def analyze_f0_k_shift_obstruction(q: int) -> dict:
    bf = build_field(q)
    n, add, sub, mul, inv, fn, om, p2 = (
        bf.n, bf.add, bf.sub, bf.mul, bf.inv, bf.fn, bf.om, bf.p2
    )
    sym_K, a_fixed, _, _, _ = build_k_skeleton(bf)
    min_coll_pts = 10**9
    for i in fn[1:]:
        for j in fn[1:]:
            target_sym = sym_K(i, j)
            for r in range(q):
                coll = 0
                for w1 in fn:
                    w = add[w1][mul[i][om]]
                    d = inv[w]
                    for c_new in range(q):
                        if p2[sub[mul[c_new][w]][r]] == j:
                            orig_a = a_fixed[(c_new, d)]
                            if orig_a != target_sym:
                                if not (orig_a == sym_K(i, 0) and w1 in (0, i)):
                                    coll += 1
                if coll < min_coll_pts:
                    min_coll_pts = coll
    return {"q": q, "n": n, "fuell_saved_if_shifted": n, "min_a_side_collision_pts": min_coll_pts}


def run_baer3_construct(out_dir: Path | None) -> list[dict]:
    t0 = time.perf_counter()
    results = []
    print("=== Baer-v3 Cross-Group K-Promotion + Redundant-Slot Recycling (q = 9, 16, 25) ===")
    for q in (9, 16, 25):
        bf = build_field(q)
        n = bf.n
        for F in range(n + 1):
            v = q - n + F
            best_m = 10**9
            best_reps = None
            best_cfg = None
            for r in range(min(F, n - 1) + 1):
                for promo in enumerate_promo_configs(n, r):
                    reps = build_baer_v3_cross_kpromo(bf, F, r, promo)
                    m = len(reps)
                    if m < best_m:
                        mp, ml, mpair, dup = check_mr(bf, v, reps)
                        assert (mp, ml, mpair, dup) == (0, 0, 0, 0), (
                            f"Invalid Baer-v3 for q={q} v={v} r={r} promo={promo}: {(mp, ml, mpair, dup)}"
                        )
                        best_m = m
                        best_reps = reps
                        best_cfg = (r, promo)

            target = BAER_V2_TARGETS.get((q, v))
            v1_m = q * (q - 1) + (q - n) * (n + F) + n * max(F, 1)
            p7_d = max(0, 2 * v - q)
            p7_m = q * q + p7_d * (p7_d - 1) // 2
            beat_str = ""
            saved_path = None
            sha = None
            # Save every list strictly beating its Baer-v2/v1 target (plus q=16 v=13 beating v1=304 & v2=292!)
            save_it = (target is not None and best_m < target) or (q == 16 and v == 13 and best_m < 292)
            if target is not None and best_m < target:
                beat_str = f" *** BEATS {target} (delta={best_m - target:+d}) ***"
            elif q == 16 and v == 13 and best_m < 292:
                beat_str = f" *** BEATS v1=304/v2=292 (delta={best_m - 292:+d}) ***"
            elif target is not None:
                beat_str = f" (vs target {target})"

            if save_it and out_dir is not None:
                fname = f"R_q{q}_v{v}_baer3_m{best_m}.txt"
                saved_path = out_dir / fname
                sha = write_reps_file(best_reps, saved_path)

            print(
                f"  q={q:2d} F={F} v={v:2d}: v1={v1_m:3d}, p7={p7_m:3d}, baer3={best_m:3d} "
                f"(r={best_cfg[0]}, promo={best_cfg[1]}){beat_str}"
            )
            results.append({
                "q": q,
                "F": F,
                "v": v,
                "v1": v1_m,
                "p7": p7_m,
                "target": target,
                "best_m": best_m,
                "cfg": best_cfg,
                "saved_path": str(saved_path) if saved_path else None,
                "sha256": sha,
            })

    if out_dir is not None:
        # Remove any stale files in out_dir before writing fresh SHA256SUMS
        saved_names = {os.path.basename(r["saved_path"]) for r in results if r["saved_path"]}
        for existing in out_dir.glob("R_q*.txt"):
            if existing.name not in saved_names:
                existing.unlink()
        saved = [r for r in results if r["saved_path"]]
        sha_lines = [
            f"{r['sha256']}  {os.path.basename(r['saved_path'])}\n"
            for r in sorted(saved, key=lambda x: (x["q"], x["v"]))
        ]
        (out_dir / "SHA256SUMS").write_text("".join(sha_lines), encoding="utf-8")
        print(f"\nWrote {len(saved)} strictly improved lists + {out_dir / 'SHA256SUMS'} in {time.perf_counter() - t0:.2f}s")

    print("\n=== F = 0 K-Class Shift-to-(c2=0) Obstruction Check ===")
    for q in (9, 16, 25):
        obs = analyze_f0_k_shift_obstruction(q)
        print(
            f"  q={q:2d} (n={obs['n']}): Fuell reps on c2=0 = {obs['fuell_saved_if_shifted']}, "
            f"min d!=0 collision points on a-side alone = {obs['min_a_side_collision_pts']} "
            f"(=> net >= {obs['min_a_side_collision_pts'] - obs['fuell_saved_if_shifted']:+d})"
        )
    return results


# =============================================================================
# Part 2: Complete AG(2, 9) Baer-subplane catalog & 3rd/4th direction analysis
# =============================================================================

def enumerate_baer_subplanes_through_pinfty(bf: BaerField) -> list[tuple[frozenset[tuple[int, int]], dict]]:
    q, n = bf.q, bf.n
    add, mul, inv, fn, om = bf.add, bf.mul, bf.inv, bf.fn, bf.om
    directions = [1, om] + [add[1][mul[lam][om]] for lam in fn[1:]]

    fn_mults = {}
    coset_reps = {}
    for eps in directions:
        span = frozenset(mul[y][eps] for y in fn)
        fn_mults[eps] = span
        seen = set()
        reps_e = []
        for z in range(q):
            if z not in seen:
                reps_e.append(z)
                for u in span:
                    seen.add(add[z][u])
        coset_reps[eps] = reps_e

    sublines: dict[frozenset[int], tuple[int, int, int]] = {}
    for d_star in range(q):
        for eps in directions:
            for w0 in coset_reps[eps]:
                if w0 in fn_mults[eps]:
                    continue
                ds = frozenset([d_star] + [add[d_star][inv[add[w0][mul[y][eps]]]] for y in fn])
                if ds not in sublines:
                    sublines[ds] = (d_star, eps, w0)

    catalog_map: dict[frozenset[tuple[int, int]], dict] = {}
    for d_set, (d_star, eps, w0) in sublines.items():
        deltas = [inv[add[w0][mul[y][eps]]] for y in fn]
        d_lines = [add[d_star][dl] for dl in deltas]
        for kp in directions:
            kp_eps = mul[kp][eps]
            kp_eps_span = frozenset(mul[u][kp_eps] for u in fn)
            seen_r = set()
            r_reps = []
            for z in range(q):
                if z not in seen_r:
                    r_reps.append(z)
                    for u in kp_eps_span:
                        seen_r.add(add[z][u])
            kp_x_list = [mul[kp][x] for x in fn]
            kp_eps_x_list = [mul[kp_eps][x] for x in fn]
            for t in coset_reps[kp]:
                pts_anchor = [(add[t][kx], d_star) for kx in kp_x_list]
                for r in r_reps:
                    pts = list(pts_anchor)
                    for dl, d_line in zip(deltas, d_lines):
                        for kex in kp_eps_x_list:
                            pts.append((add[t][mul[add[kex][r]][dl]], d_line))
                    fpts = frozenset(pts)
                    assert len(fpts) == q + n
                    if fpts not in catalog_map:
                        catalog_map[fpts] = {
                            "type": "baer",
                            "d_star": d_star,
                            "eps": eps,
                            "w0": w0,
                            "d_lines": d_set,
                            "has_d0": (0 in d_set),
                        }
    if q <= 9:
        for fpts in catalog_map:
            hit = {(al, add[c][mul[al][d]]) for (c, d) in fpts for al in range(q)}
            assert len(hit) == q * q
    return list(catalog_map.items())


def analyze_baer3_direction_obstruction() -> None:
    """Exact Baer-subline intersection & pair-split obstruction for replacing d = 0 symbols
    by 3rd/4th-direction or shifted-anchor Baer subplanes on top of fixed K-classes."""
    print("\n=== Task A2: 3rd/4th Baer Direction & Shifted Anchor d* != 0 Obstruction (q = 9, 16, 25) ===")
    for q in (9, 16, 25):
        bf = build_field(q)
        n, add, mul, inv, fn, om, p1, p2 = bf.n, bf.add, bf.mul, bf.inv, bf.fn, bf.om, bf.p1, bf.p2
        dirs = [1, om] + [add[1][mul[lam][om]] for lam in fn[1:]]
        sublines = set()
        for d_star in range(q):
            for eps in dirs:
                span = {mul[y][eps] for y in fn}
                for w0 in range(q):
                    if w0 in span:
                        continue
                    sublines.add(frozenset([d_star] + [add[d_star][inv[add[w0][mul[y][eps]]]] for y in fn]))
        sublines = list(sublines)
        fn_nz = list(fn[1:])
        w2_0_by_i = {i: inv[i] for i in fn_nz}
        w1_0_by_i = {i: inv[mul[i][om]] for i in fn_nz}
        w2_all = set(w2_0_by_i.values())
        max_ha = max(len(ds & w2_all) for ds in sublines)
        max_ha_d0 = max(len(ds & (w2_all | {0})) for ds in sublines)
        assert max_ha_d0 == 2
        b0 = q * (q - 1) + (q - n) * n + n
        print(f"  q={q:2d} (n={n}): sublines={len(sublines)}, max|D&w2=0|={max_ha}, max|D&({{0}}Uw2=0)|={max_ha_d0}")
        for r in range(n):
            s = n - r
            free_a = {w2_0_by_i[i] for i in fn_nz[r:]}
            free_b = {w1_0_by_i[i] for i in fn_nz[r:]}
            min_sa = min(len(ds - free_a) for ds in sublines)
            min_union = min(len((ds1 - free_a) | (ds2 - free_b)) for ds1 in sublines for ds2 in sublines)
            lb_with_vk = b0 + r * max(0, r - 1) * n + s * (min_sa + r) * n
            print(
                f"    r={r}, s={s} Baer: min|S_a|={min_sa} ({min_sa*n:2d} pts), "
                f"min|S_a U S_b|={min_union} ({min_union*n:2d} pts), "
                f"LB_with_VK_splits={lb_with_vk} (Baer-v2 v={q}: {BAER_V2_TARGETS[(q, q)]})"
            )


def analyze_q9_catalog() -> None:
    print("\n=== Task A1: AG(2, 9) Complete Baer-Subplane + Full-Line Catalog ===")
    bf = build_field(9)
    baer_cat = enumerate_baer_subplanes_through_pinfty(bf)
    print(
        f"  Catalog AG(2,9) through P_infty: {len(baer_cat)} affine Baer subplanes (size 12, all 4 dirs & "
        f"all 9 anchors, {len({m['d_lines'] for _, m in baer_cat})} Baer sublines) + 9 full horizontal lines (size 9) "
        f"= {len(baer_cat) + 9} total."
    )
    print(
        "  Fixed 6 K-classes cannot beat 111 using pure Baer replacements (see Task A2 LB >= 111); "
        "unfreezing 1 K-class via Cross-Group K-Promotion achieves 108 (< 111) deterministically above."
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 8 Baer-v3 construction & exploration (q = 9, 16, 25).")
    ap.add_argument(
        "--mode",
        choices=("all", "baer3-construct", "q9-catalog", "baer3-16-25"),
        default="all",
    )
    ap.add_argument("--out-dir", type=Path, default=Path("data/phase8_baer_v3"))
    args = ap.parse_args()

    if args.mode in ("all", "baer3-construct"):
        run_baer3_construct(args.out_dir)
    if args.mode in ("all", "q9-catalog"):
        analyze_q9_catalog()
    if args.mode in ("all", "baer3-16-25"):
        analyze_baer3_direction_obstruction()


if __name__ == "__main__":
    main()
