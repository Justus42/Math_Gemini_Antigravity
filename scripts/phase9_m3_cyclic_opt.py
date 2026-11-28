#!/usr/bin/env python3
r"""Phase 9 (Option C, Approach 1): Deterministic Block-Idempotent + 3P-Split M_3(R_3) Constructor.

Pure Python (std-only) + FieldOps / check_m3 from scripts/phase9_m3_lift.py.
Zero randomness, zero metaheuristics.

Key structural improvements over scripts/phase9_m3_construct.py (asymptotic 19/10 = 1.9000 q^3):
  1. k-Block Idempotent-Free Partial Latin Square T (k in {3, 4, 5}):
       Partition F_q into k balanced blocks B_0, ..., B_{k-1} of sizes floor(q/k) or ceil(q/k).
       Let L be an idempotent Latin square of order k (L[i][i] = i; for i != j, L[i][j] not in {i, j}).
       Place a maximal Latin rectangle in B_i x B_j -> B_{L[i][j]} for all i != j.
       The uncovered diagonal blocks B_i x B_i become 1P lines; for k | q this achieves the exact
       closed formula:
           m_raw(q, k) = (2 - 1/k + 2/k^2) * q^3 - (1 - 1/k) * q^2.
       In particular:
           k = 3: (17/9) q^3 - (2/3) q^2  = 1.88889 q^3 - O(q^2)
           k = 4: (15/8) q^3 - (3/4) q^2  = 1.87500 q^3 - O(q^2)   [strictly < 19/10 = 1.90!]
           k = 5: (47/25) q^3 - (4/5) q^2 = 1.88000 q^3 - O(q^2)
       For q % k != 0, an optional deterministic greedy completion adds off-diagonal 3P triples
       that strictly decrease m_raw = (|T| + |1P|) q + |U(T)|.
       We also include the cyclic difference-band PLS T_r from phase9_m3_construct.py as candidate
       k = 0 so the family strictly dominates the previous deterministic baseline for every q.
  2. Heavy-Value-Sorted Light-Plane Matching:
       Sort candidate x-lines by increasing heavy value on z* so high-heavy-value lines (3P_HHH,
       1P_HH) are preserved for the heavy plane z* = q - 1.
  3. Deterministic z* Line/Bijection Re-Optimization:
       After initial greedy placement of remaining 3P, 1P, and U triples on z*, iteratively move
       3P rows, re-match 1P x-bijections, and relocate U triples to eliminate heavy-symbol deficits.
  4. Post-Heavy 3P-Splitting (Preserves 100% suff=0):
       Replace a column x of a 3P(a0, b0, c0) line (keeping >= 1 unsplit column so (a0,b0,c0) stays
       covered) by three heavy-redundant U-triples (a0, b0, cx), (a0, bx, c0), (ax, b0, c0) at the
       same (x, y, z), saving 1 point per split while keeping all three pair x-lines and all light
       plane owners intact.

All generated R_3 sets satisfy suff=0 (and hence check_m3=0 in full-bg3 mode for all 3 <= t <= q).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase9_m3_construct import _max_bijection_gain, optimal_r_theoretical  # noqa: E402
from phase9_m3_lift import FieldOps, check_m3, write_reps  # noqa: E402


def idempotent_ls(k: int) -> list[list[int]]:
    """Return an explicit idempotent Latin square of order k (k >= 3, k = 4 or odd k)."""
    if k == 4:
        return [
            [0, 2, 3, 1],
            [3, 1, 0, 2],
            [1, 3, 2, 0],
            [2, 0, 1, 3],
        ]
    if k % 2 == 1 and k >= 3:
        inv2 = (k + 1) // 2
        return [[(inv2 * (i + j)) % k for j in range(k)] for i in range(k)]
    raise ValueError(f"unsupported idempotent_ls order k={k}")


def build_kblock_pls(
    q: int,
    k: int,
    extra_greedy: bool = True,
) -> tuple[list[tuple[int, int, int]], list[list[bool]], list[list[bool]], list[list[bool]], list[list[int]]]:
    """Build k-block idempotent-free PLS of order q (with deterministic greedy completion if q % k != 0)."""
    L = idempotent_ls(k)
    base, rem = q // k, q % k
    blocks: list[list[int]] = []
    cur = 0
    for i in range(k):
        s = base + (1 if i < rem else 0)
        blocks.append(list(range(cur, cur + s)))
        cur += s

    E_ab = [[False] * q for _ in range(q)]
    E_ac = [[False] * q for _ in range(q)]
    E_bc = [[False] * q for _ in range(q)]
    T: list[tuple[int, int, int]] = []

    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            kk = L[i][j]
            Bi, Bj, Bk = blocks[i], blocks[j], blocks[kk]
            M = max(len(Bi), len(Bj), len(Bk))
            for u, a in enumerate(Bi):
                for v, b in enumerate(Bj):
                    w = (u + v) % M
                    if w < len(Bk):
                        c = Bk[w]
                        E_ab[a][b] = True
                        E_ac[a][c] = True
                        E_bc[b][c] = True
                        T.append((a, b, c))

    if extra_greedy and (q % k != 0):
        ab = [[-1] * q for _ in range(q)]
        ac = [[-1] * q for _ in range(q)]
        bc = [[-1] * q for _ in range(q)]
        for a, b, c in T:
            ab[a][b] = c
            ac[a][c] = b
            bc[b][c] = a
        while True:
            best_dm = 0
            best_tr: tuple[int, int, int] | None = None
            for a in range(q):
                row_ab = ab[a]
                row_ac = ac[a]
                for b in range(q):
                    if row_ab[b] != -1:
                        continue
                    row_bc = bc[b]
                    for c in range(q):
                        if row_ac[c] != -1 or row_bc[c] != -1:
                            continue
                        du = 0
                        for c2 in range(q):
                            if row_ac[c2] != -1 and row_bc[c2] != -1:
                                du += 1
                        for b2 in range(q):
                            if row_ab[b2] != -1 and bc[b2][c] != -1:
                                du += 1
                        for a2 in range(q):
                            if ab[a2][b] != -1 and ac[a2][c] != -1:
                                du += 1
                        dm = -2 * q + du
                        if dm < best_dm:
                            best_dm = dm
                            best_tr = (a, b, c)
            if best_tr is None:
                break
            a, b, c = best_tr
            ab[a][b] = c
            ac[a][c] = b
            bc[b][c] = a
            E_ab[a][b] = True
            E_ac[a][c] = True
            E_bc[b][c] = True
            T.append((a, b, c))

    return T, E_ab, E_ac, E_bc, blocks


def build_diffband_pls(
    q: int,
    r: int,
) -> tuple[list[tuple[int, int, int]], list[list[bool]], list[list[bool]], list[list[bool]]]:
    """Build cyclic difference-band PLS T_r = {(a, b, (-a-b)%q) : (a-b)%q < r}."""
    E_ab = [[False] * q for _ in range(q)]
    E_ac = [[False] * q for _ in range(q)]
    E_bc = [[False] * q for _ in range(q)]
    T: list[tuple[int, int, int]] = []
    for a in range(q):
        for b in range(q):
            if (a - b) % q < r:
                c = (-a - b) % q
                E_ab[a][b] = True
                E_ac[a][c] = True
                E_bc[b][c] = True
                T.append((a, b, c))
    return T, E_ab, E_ac, E_bc


def build_from_pls(
    q: int,
    T: list[tuple[int, int, int]],
    E_ab: list[list[bool]],
    E_ac: list[list[bool]],
    E_bc: list[list[bool]],
    AL: set[int],
    BL: set[int],
    CL: set[int],
    reopt_rounds: int = 4,
    do_split: bool = True,
) -> tuple[list[tuple[int, int, int, int, int, int]], dict[str, int]]:
    """Construct a guaranteed suff=0 R_3 from partial Latin square T and Light sets AL, BL, CL."""
    AH = set(range(q)) - AL
    BH = set(range(q)) - BL
    CH = set(range(q)) - CL
    T_set = set(T)

    lines: list[tuple] = [("3P", a, b, c) for (a, b, c) in T]
    n3p = len(lines)
    for a in range(q):
        for b in range(q):
            if not E_ab[a][b]:
                lines.append(("1P_ab", a, b))
    for a in range(q):
        for c in range(q):
            if not E_ac[a][c]:
                lines.append(("1P_ac", a, c))
    for b in range(q):
        for c in range(q):
            if not E_bc[b][c]:
                lines.append(("1P_bc", b, c))
    n1p = len(lines) - n3p

    unc_t3: list[tuple[int, int, int]] = []
    for a in range(q):
        for b in range(q):
            if not E_ab[a][b]:
                continue
            for c in range(q):
                if E_ac[a][c] and E_bc[b][c] and (a, b, c) not in T_set:
                    unc_t3.append((a, b, c))
    m_raw = (n3p + n1p) * q + len(unc_t3)

    plane_owner = [("a", a) for a in sorted(AL)] + [("b", b) for b in sorted(BL)] + [("c", c) for c in sorted(CL)]
    plane_idx = {owner: idx for idx, owner in enumerate(plane_owner)}

    def light_deg(L: tuple) -> int:
        k = L[0]
        if k == "3P":
            return (L[1] in AL) + (L[2] in BL) + (L[3] in CL)
        if k == "1P_ab":
            return (L[1] in AL) + (L[2] in BL)
        if k == "1P_ac":
            return (L[1] in AL) + (L[2] in CL)
        return (L[1] in BL) + (L[2] in CL)

    def heavy_val(L: tuple) -> int:
        k = L[0]
        if k == "3P":
            return 3 * ((L[1] in AH) + (L[2] in BH) + (L[3] in CH))
        if k == "1P_ab":
            return 3 * ((L[1] in AH) + (L[2] in BH)) + 2
        if k == "1P_ac":
            return 3 * ((L[1] in AH) + (L[2] in CH)) + 2
        return 3 * ((L[1] in BH) + (L[2] in CH)) + 2

    lines.sort(key=lambda L: (heavy_val(L), -light_deg(L), 0 if L[0] == "3P" else 1, L))

    def compat_planes(L: tuple) -> list[int]:
        res: list[int] = []
        k = L[0]
        if k == "3P":
            if L[1] in AL:
                res.append(plane_idx[("a", L[1])])
            if L[2] in BL:
                res.append(plane_idx[("b", L[2])])
            if L[3] in CL:
                res.append(plane_idx[("c", L[3])])
        elif k == "1P_ab":
            if L[1] in AL:
                res.append(plane_idx[("a", L[1])])
            if L[2] in BL:
                res.append(plane_idx[("b", L[2])])
        elif k == "1P_ac":
            if L[1] in AL:
                res.append(plane_idx[("a", L[1])])
            if L[2] in CL:
                res.append(plane_idx[("c", L[2])])
        else:
            if L[1] in BL:
                res.append(plane_idx[("b", L[1])])
            if L[2] in CL:
                res.append(plane_idx[("c", L[2])])
        return res

    plane_lines: list[list[int]] = [[] for _ in range(q - 1)]
    for li, L in enumerate(lines):
        for z in compat_planes(L):
            plane_lines[z].append(li)

    n_slots = (q - 1) * q
    match_line = [-1] * len(lines)
    match_slot = [-1] * n_slots
    for z in range(q - 1):
        sp = 0
        for li in plane_lines[z]:
            if match_line[li] == -1:
                sl = z * q + sp
                match_slot[sl] = li
                match_line[li] = sl
                sp += 1
                if sp == q:
                    break

    def augment(sl: int, vis: list[bool]) -> bool:
        z = sl // q
        for li in plane_lines[z]:
            if vis[li]:
                continue
            vis[li] = True
            if match_line[li] == -1 or augment(match_line[li], vis):
                match_slot[sl] = li
                match_line[li] = sl
                return True
        return False

    for sl in range(n_slots):
        if match_slot[sl] == -1:
            augment(sl, [False] * len(lines))

    light_3p: list[tuple[int, int, int, int, int]] = []
    light_other: list[tuple[int, int, int, int, int, int]] = []
    used_unc = [False] * len(unc_t3)
    unc_order = sorted(
        range(len(unc_t3)),
        key=lambda i: ((unc_t3[i][0] in AH) + (unc_t3[i][1] in BH) + (unc_t3[i][2] in CH), unc_t3[i]),
    )
    unc_by: dict[str, dict[int, list[int]]] = {"a": defaultdict(list), "b": defaultdict(list), "c": defaultdict(list)}
    for idx in unc_order:
        a, b, c = unc_t3[idx]
        unc_by["a"][a].append(idx)
        unc_by["b"][b].append(idx)
        unc_by["c"][c].append(idx)

    pad = 0
    for z in range(q - 1):
        col_ch, sym = plane_owner[z]
        for y in range(q):
            li = match_slot[z * q + y]
            if li != -1:
                L = lines[li]
                kind = L[0]
                if kind == "3P":
                    light_3p.append((z, y, L[1], L[2], L[3]))
                elif kind == "1P_ab":
                    for x in range(q):
                        light_other.append((x, y, z, L[1], L[2], x))
                elif kind == "1P_ac":
                    for x in range(q):
                        light_other.append((x, y, z, L[1], x, L[2]))
                else:
                    for x in range(q):
                        light_other.append((x, y, z, x, L[1], L[2]))
            else:
                picked: list[tuple[int, int, int]] = []
                for idx in unc_by[col_ch][sym]:
                    if not used_unc[idx]:
                        used_unc[idx] = True
                        picked.append(unc_t3[idx])
                        if len(picked) == q:
                            break
                while len(picked) < q:
                    pad += 1
                    if col_ch == "a":
                        picked.append((sym, 0, 0))
                    elif col_ch == "b":
                        picked.append((0, sym, 0))
                    else:
                        picked.append((0, 0, sym))
                for x, (a, b, c) in enumerate(picked):
                    light_other.append((x, y, z, a, b, c))

    # Heavy plane z* = q - 1
    z_star = q - 1
    AH_l, BH_l, CH_l = sorted(AH), sorted(BH), sorted(CH)
    AH_idx = {a: i for i, a in enumerate(AH_l)}
    BH_idx = {b: i for i, b in enumerate(BH_l)}
    CH_idx = {c: i for i, c in enumerate(CH_l)}
    na, nb, nc = len(AH_l), len(BH_l), len(CH_l)
    cnt_a = [[[0] * na for _ in range(q)] for _ in range(q)]
    cnt_b = [[[0] * nb for _ in range(q)] for _ in range(q)]
    cnt_c = [[[0] * nc for _ in range(q)] for _ in range(q)]

    def add_cnt(x: int, y: int, a: int, b: int, c: int, d: int) -> None:
        if a in AH_idx:
            cnt_a[x][y][AH_idx[a]] += d
        if b in BH_idx:
            cnt_b[x][y][BH_idx[b]] += d
        if c in CH_idx:
            cnt_c[x][y][CH_idx[c]] += d

    def is_red(x: int, y: int, a: int, b: int, c: int) -> bool:
        if a in AH_idx and cnt_a[x][y][AH_idx[a]] <= 1:
            return False
        if b in BH_idx and cnt_b[x][y][BH_idx[b]] <= 1:
            return False
        if c in CH_idx and cnt_c[x][y][CH_idx[c]] <= 1:
            return False
        return True

    rem_3p = [lines[li] for li in range(len(lines)) if match_line[li] == -1 and lines[li][0] == "3P"]
    rem_1p = [lines[li] for li in range(len(lines)) if match_line[li] == -1 and lines[li][0] != "3P"]
    rem_u = [unc_t3[i] for i in range(len(unc_t3)) if not used_unc[i]]

    rem_3p.sort(key=lambda L: (-heavy_val(L), L))
    rem_1p.sort(key=lambda L: (-heavy_val(L), L))

    heavy_3p: list[list[int]] = []
    heavy_1p: list[list] = []
    used_cell_triple: set[tuple[int, int, int, int, int]] = set()

    for _, a, b, c in rem_3p:
        best_y, best_g = 0, -1
        ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
        for y in range(q):
            g = 0
            for x in range(q):
                if ai != -1 and cnt_a[x][y][ai] == 0:
                    g += 1
                if bi != -1 and cnt_b[x][y][bi] == 0:
                    g += 1
                if ci != -1 and cnt_c[x][y][ci] == 0:
                    g += 1
            if g > best_g:
                best_g, best_y = g, y
        heavy_3p.append([best_y, a, b, c])
        for x in range(q):
            add_cnt(x, best_y, a, b, c, +1)
            used_cell_triple.add((x, best_y, a, b, c))

    def place_1p_line(L: tuple) -> tuple[int, int, list[int]]:
        kind = L[0]
        best_y, best_g, best_pi = 0, -1, list(range(q))
        for y in range(q):
            gain_adj: list[list[int]] = [[] for _ in range(q)]
            valid_adj: list[list[int]] = [[] for _ in range(q)]
            base_g = 0
            if kind == "1P_ab":
                _, a, b = L
                ai, bi = AH_idx.get(a, -1), BH_idx.get(b, -1)
                for x in range(q):
                    if ai != -1 and cnt_a[x][y][ai] == 0:
                        base_g += 1
                    if bi != -1 and cnt_b[x][y][bi] == 0:
                        base_g += 1
                    for c in range(q):
                        if (x, y, a, b, c) in used_cell_triple:
                            continue
                        valid_adj[x].append(c)
                        ci = CH_idx.get(c, -1)
                        if ci != -1 and cnt_c[x][y][ci] == 0:
                            gain_adj[x].append(c)
            elif kind == "1P_ac":
                _, a, c = L
                ai, ci = AH_idx.get(a, -1), CH_idx.get(c, -1)
                for x in range(q):
                    if ai != -1 and cnt_a[x][y][ai] == 0:
                        base_g += 1
                    if ci != -1 and cnt_c[x][y][ci] == 0:
                        base_g += 1
                    for b in range(q):
                        if (x, y, a, b, c) in used_cell_triple:
                            continue
                        valid_adj[x].append(b)
                        bi = BH_idx.get(b, -1)
                        if bi != -1 and cnt_b[x][y][bi] == 0:
                            gain_adj[x].append(b)
            else:
                _, b, c = L
                bi, ci = BH_idx.get(b, -1), CH_idx.get(c, -1)
                for x in range(q):
                    if bi != -1 and cnt_b[x][y][bi] == 0:
                        base_g += 1
                    if ci != -1 and cnt_c[x][y][ci] == 0:
                        base_g += 1
                    for a in range(q):
                        if (x, y, a, b, c) in used_cell_triple:
                            continue
                        valid_adj[x].append(a)
                        ai = AH_idx.get(a, -1)
                        if ai != -1 and cnt_a[x][y][ai] == 0:
                            gain_adj[x].append(a)
            res = _max_bijection_gain(q, gain_adj, valid_adj)
            if res is None:
                continue
            g = base_g + res[0]
            if g > best_g:
                best_g, best_y, best_pi = g, y, res[1]
        return best_y, best_g, best_pi

    for L in rem_1p:
        y, _, pi = place_1p_line(L)
        heavy_1p.append([y, L, pi])
        kind = L[0]
        for x in range(q):
            v = pi[x]
            if kind == "1P_ab":
                a, b, c = L[1], L[2], v
            elif kind == "1P_ac":
                a, b, c = L[1], v, L[2]
            else:
                a, b, c = v, L[1], L[2]
            add_cnt(x, y, a, b, c, +1)
            used_cell_triple.add((x, y, a, b, c))

    rem_u.sort(key=lambda t: (-((t[0] in AH) + (t[1] in BH) + (t[2] in CH)), t))
    u_pos: list[list] = []
    for a, b, c in rem_u:
        ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
        best_xy = (0, 0)
        best_g = -1
        for x in range(q):
            for y in range(q):
                if (x, y, a, b, c) in used_cell_triple:
                    continue
                g = (
                    (ai != -1 and cnt_a[x][y][ai] == 0)
                    + (bi != -1 and cnt_b[x][y][bi] == 0)
                    + (ci != -1 and cnt_c[x][y][ci] == 0)
                )
                if g > best_g:
                    best_g, best_xy = g, (x, y)
                    if g == 3:
                        break
            if best_g == 3:
                break
        x, y = best_xy
        u_pos.append([x, y, a, b, c, True])
        add_cnt(x, y, a, b, c, +1)
        used_cell_triple.add((x, y, a, b, c))

    # Deterministic re-optimization pass on z*
    for _round in range(reopt_rounds):
        deficits = [
            (x, y)
            for x in range(q)
            for y in range(q)
            if any(v == 0 for v in cnt_a[x][y]) or any(v == 0 for v in cnt_b[x][y]) or any(v == 0 for v in cnt_c[x][y])
        ]
        if not deficits:
            break
        improved = False
        for rec in heavy_3p:
            oy, a, b, c = rec
            ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
            old_g = 0
            for x in range(q):
                add_cnt(x, oy, a, b, c, -1)
                used_cell_triple.remove((x, oy, a, b, c))
                if ai != -1 and cnt_a[x][oy][ai] == 0:
                    old_g += 1
                if bi != -1 and cnt_b[x][oy][bi] == 0:
                    old_g += 1
                if ci != -1 and cnt_c[x][oy][ci] == 0:
                    old_g += 1
            best_y, best_g = oy, old_g
            for y in range(q):
                if y == oy:
                    continue
                ok = True
                g = 0
                for x in range(q):
                    if (x, y, a, b, c) in used_cell_triple:
                        ok = False
                        break
                    if ai != -1 and cnt_a[x][y][ai] == 0:
                        g += 1
                    if bi != -1 and cnt_b[x][y][bi] == 0:
                        g += 1
                    if ci != -1 and cnt_c[x][y][ci] == 0:
                        g += 1
                if ok and g > best_g:
                    best_g, best_y = g, y
            if best_y != oy:
                rec[0] = best_y
                improved = True
            for x in range(q):
                add_cnt(x, rec[0], a, b, c, +1)
                used_cell_triple.add((x, rec[0], a, b, c))

        for rec in heavy_1p:
            oy, L, opi = rec
            kind = L[0]
            old_g = 0
            for x in range(q):
                v = opi[x]
                if kind == "1P_ab":
                    a, b, c = L[1], L[2], v
                elif kind == "1P_ac":
                    a, b, c = L[1], v, L[2]
                else:
                    a, b, c = v, L[1], L[2]
                add_cnt(x, oy, a, b, c, -1)
                used_cell_triple.remove((x, oy, a, b, c))
                if a in AH_idx and cnt_a[x][oy][AH_idx[a]] == 0:
                    old_g += 1
                if b in BH_idx and cnt_b[x][oy][BH_idx[b]] == 0:
                    old_g += 1
                if c in CH_idx and cnt_c[x][oy][CH_idx[c]] == 0:
                    old_g += 1
            ny, ng, npi = place_1p_line(L)
            if ng > old_g:
                rec[0], rec[2] = ny, npi
                improved = True
            else:
                ny, npi = oy, opi
            for x in range(q):
                v = npi[x]
                if kind == "1P_ab":
                    a, b, c = L[1], L[2], v
                elif kind == "1P_ac":
                    a, b, c = L[1], v, L[2]
                else:
                    a, b, c = v, L[1], L[2]
                add_cnt(x, ny, a, b, c, +1)
                used_cell_triple.add((x, ny, a, b, c))

        deficits = [
            (x, y)
            for x in range(q)
            for y in range(q)
            if any(v == 0 for v in cnt_a[x][y]) or any(v == 0 for v in cnt_b[x][y]) or any(v == 0 for v in cnt_c[x][y])
        ]
        if deficits:
            for rec in u_pos:
                x, y, a, b, c, _alive = rec
                ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
                old_g = (
                    (ai != -1 and cnt_a[x][y][ai] == 1)
                    + (bi != -1 and cnt_b[x][y][bi] == 1)
                    + (ci != -1 and cnt_c[x][y][ci] == 1)
                )
                if old_g == 3:
                    continue
                best_xy = None
                best_g = old_g
                for dx, dy in deficits:
                    if (dx, dy, a, b, c) in used_cell_triple:
                        continue
                    g = (
                        (ai != -1 and cnt_a[dx][dy][ai] == 0)
                        + (bi != -1 and cnt_b[dx][dy][bi] == 0)
                        + (ci != -1 and cnt_c[dx][dy][ci] == 0)
                    )
                    if g > best_g:
                        best_g, best_xy = g, (dx, dy)
                        if g == 3:
                            break
                if best_xy is not None:
                    add_cnt(x, y, a, b, c, -1)
                    used_cell_triple.remove((x, y, a, b, c))
                    nx, ny = best_xy
                    rec[0], rec[1] = nx, ny
                    add_cnt(nx, ny, a, b, c, +1)
                    used_cell_triple.add((nx, ny, a, b, c))
                    improved = True
        if not improved:
            break

    exh: list[tuple[int, int, int, int, int, int]] = []
    for x in range(q):
        for y in range(q):
            ma = [AH_l[i] for i in range(na) if cnt_a[x][y][i] == 0]
            mb = [BH_l[i] for i in range(nb) if cnt_b[x][y][i] == 0]
            mc = [CH_l[i] for i in range(nc) if cnt_c[x][y][i] == 0]
            kmax = max(len(ma), len(mb), len(mc))
            for idx in range(kmax):
                a = ma[idx] if idx < len(ma) else 0
                b = mb[idx] if idx < len(mb) else 0
                c = mc[idx] if idx < len(mc) else 0
                while (x, y, a, b, c) in used_cell_triple:
                    c = (c + 1) % q
                exh.append((x, y, z_star, a, b, c))
                add_cnt(x, y, a, b, c, +1)
                used_cell_triple.add((x, y, a, b, c))

    # Post-heavy 3P-splitting (preserves 100% suff=0)
    sp_z, sp_L = 0, 0
    heavy_3p_splits: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    light_3p_splits: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)

    if do_split:
        u_ab: dict[tuple[int, int], list[int]] = defaultdict(list)
        u_ac: dict[tuple[int, int], list[int]] = defaultdict(list)
        u_bc: dict[tuple[int, int], list[int]] = defaultdict(list)
        for i, (_x, _y, a, b, c, _alive) in enumerate(u_pos):
            u_ab[(a, b)].append(i)
            u_ac[(a, c)].append(i)
            u_bc[(b, c)].append(i)

        def try_split_3p(
            a0: int,
            b0: int,
            c0: int,
            on_zstar: bool,
            y_line: int,
            used_x_set: set[int],
        ) -> tuple[int, int, int, int] | None:
            if len(used_x_set) >= q - 1:
                return None
            i1 = next((i for i in u_ab[(a0, b0)] if u_pos[i][5] and is_red(*u_pos[i][:5])), -1)
            if i1 == -1:
                return None
            add_cnt(*u_pos[i1][:5], -1)
            i2 = next((i for i in u_ac[(a0, c0)] if i != i1 and u_pos[i][5] and is_red(*u_pos[i][:5])), -1)
            if i2 == -1:
                add_cnt(*u_pos[i1][:5], +1)
                return None
            add_cnt(*u_pos[i2][:5], -1)
            i3 = next(
                (i for i in u_bc[(b0, c0)] if i != i1 and i != i2 and u_pos[i][5] and is_red(*u_pos[i][:5])),
                -1,
            )
            if i3 == -1:
                add_cnt(*u_pos[i2][:5], +1)
                add_cnt(*u_pos[i1][:5], +1)
                return None
            add_cnt(*u_pos[i3][:5], -1)
            cx, bx, ax = u_pos[i1][4], u_pos[i2][3], u_pos[i3][2]
            chosen_x = -1
            for x in range(q):
                if x in used_x_set:
                    continue
                if on_zstar and (
                    (x, y_line, a0, b0, cx) in used_cell_triple
                    or (x, y_line, a0, bx, c0) in used_cell_triple
                    or (x, y_line, ax, b0, c0) in used_cell_triple
                ):
                    continue
                chosen_x = x
                break
            if chosen_x == -1:
                for idx in (i3, i2, i1):
                    add_cnt(*u_pos[idx][:5], +1)
                return None
            for idx in (i1, i2, i3):
                u_pos[idx][5] = False
                used_cell_triple.remove(tuple(u_pos[idx][:5]))
            used_x_set.add(chosen_x)
            if on_zstar:
                add_cnt(chosen_x, y_line, a0, b0, c0, -1)
                used_cell_triple.remove((chosen_x, y_line, a0, b0, c0))
                for tr in ((a0, b0, cx), (a0, bx, c0), (ax, b0, c0)):
                    add_cnt(chosen_x, y_line, *tr, +1)
                    used_cell_triple.add((chosen_x, y_line, *tr))
            return (chosen_x, cx, bx, ax)

        for idx, (y_line, a0, b0, c0) in enumerate(heavy_3p):
            used_x: set[int] = set()
            while (res := try_split_3p(a0, b0, c0, True, y_line, used_x)) is not None:
                heavy_3p_splits[idx].append(res)
                sp_z += 1
        for idx, (_z_line, y_line, a0, b0, c0) in enumerate(light_3p):
            used_x = set()
            while (res := try_split_3p(a0, b0, c0, False, y_line, used_x)) is not None:
                light_3p_splits[idx].append(res)
                sp_L += 1

    reps: list[tuple[int, int, int, int, int, int]] = list(light_other) + list(exh)
    for y, L, pi in heavy_1p:
        kind = L[0]
        for x in range(q):
            v = pi[x]
            if kind == "1P_ab":
                reps.append((x, y, z_star, L[1], L[2], v))
            elif kind == "1P_ac":
                reps.append((x, y, z_star, L[1], v, L[2]))
            else:
                reps.append((x, y, z_star, v, L[1], L[2]))
    for idx, (z_line, y_line, a0, b0, c0) in enumerate(light_3p):
        sp_map = {x: (cx, bx, ax) for (x, cx, bx, ax) in light_3p_splits[idx]}
        for x in range(q):
            if x in sp_map:
                cx, bx, ax = sp_map[x]
                reps.append((x, y_line, z_line, a0, b0, cx))
                reps.append((x, y_line, z_line, a0, bx, c0))
                reps.append((x, y_line, z_line, ax, b0, c0))
            else:
                reps.append((x, y_line, z_line, a0, b0, c0))
    for idx, (y_line, a0, b0, c0) in enumerate(heavy_3p):
        sp_map = {x: (cx, bx, ax) for (x, cx, bx, ax) in heavy_3p_splits[idx]}
        for x in range(q):
            if x in sp_map:
                cx, bx, ax = sp_map[x]
                reps.append((x, y_line, z_star, a0, b0, cx))
                reps.append((x, y_line, z_star, a0, bx, c0))
                reps.append((x, y_line, z_star, ax, b0, c0))
            else:
                reps.append((x, y_line, z_star, a0, b0, c0))
    for x, y, a, b, c, alive in u_pos:
        if alive:
            reps.append((x, y, z_star, a, b, c))

    uniq = sorted(set(reps))
    stats = {
        "m": len(uniq),
        "m_raw": m_raw,
        "dups": len(reps) - len(uniq),
        "n3p": n3p,
        "n1p": n1p,
        "u": len(unc_t3),
        "exh": len(exh),
        "pad": pad,
        "sp_z": sp_z,
        "sp_L": sp_L,
    }
    return uniq, stats


def verify_suff0(q: int, reps: list[tuple[int, int, int, int, int, int]]) -> dict[str, int]:
    """Direct independent verification of all four sufficient conditions (Typ 0, 1, 2, 3)."""
    # Typ 0: all (x, y, z)
    miss0 = q**3 - len({(r[0], r[1], r[2]) for r in reps})
    # Typ 3: all (a, b, c)
    miss3 = q**3 - len({(r[3], r[4], r[5]) for r in reps})
    # Typ 1: every symbol in A, B, C owns a full horizontal z-plane
    miss1 = 0
    for col in (3, 4, 5):
        by_sz: list[list[set[tuple[int, int]]]] = [[set() for _ in range(q)] for _ in range(q)]
        for r in reps:
            by_sz[r[col]][r[2]].add((r[0], r[1]))
        for s in range(q):
            if not any(len(by_sz[s][z]) == q * q for z in range(q)):
                miss1 += 1
    # Typ 2: every pair in ab, ac, bc owns a full x-line (constant y, z, all q values of x)
    miss2 = 0
    for c1, c2 in ((3, 4), (3, 5), (4, 5)):
        by_pyz: dict[tuple[int, int, int, int], set[int]] = defaultdict(set)
        for r in reps:
            by_pyz[(r[c1], r[c2], r[1], r[2])].add(r[0])
        covered_pairs = {(p1, p2) for (p1, p2, _y, _z), xs in by_pyz.items() if len(xs) == q}
        miss2 += q * q - len(covered_pairs)
    return {
        "miss0": miss0,
        "miss1": miss1,
        "miss2": miss2,
        "miss3": miss3,
        "total": miss0 + miss1 + miss2 + miss3,
    }


def construct_best_opt(
    q: int,
    fast: bool = False,
) -> tuple[list[tuple[int, int, int, int, int, int]], dict]:
    """Deterministically select the smallest suff=0 R_3 across k in {3, 4, 5} and diffband."""
    ka = (q - 1 + 2) // 3
    kb = (q - 1 + 1) // 3
    kc = (q - 1) // 3

    best_reps: list[tuple[int, int, int, int, int, int]] | None = None
    best_meta: dict = {}

    ks = [3, 4, 5] if q <= 17 else [4, 5]
    reopt = 4 if (q <= 17 and not fast) else 2
    greedy_cap = 17 if not fast else 13

    for k in ks:
        T, E_ab, E_ac, E_bc, blocks = build_kblock_pls(q, k, extra_greedy=(q <= greedy_cap))
        b_starts = [0]
        for B in blocks[:-1]:
            b_starts.append(b_starts[-1] + len(B))
        configs = [
            ("same", set(range(ka)), set(range(kb)), set(range(kc))),
            (
                "diff",
                {(b_starts[0] + i) % q for i in range(ka)},
                {(b_starts[1] + i) % q for i in range(kb)},
                {(b_starts[2] + i) % q for i in range(kc)},
            ),
            (
                "stride",
                {(i * 3) % q for i in range(ka)},
                {(i * 3 + 1) % q for i in range(kb)},
                {(i * 3 + 2) % q for i in range(kc)},
            ),
        ]
        for cname, AL, BL, CL in configs:
            reps, st = build_from_pls(q, T, E_ab, E_ac, E_bc, AL, BL, CL, reopt_rounds=reopt, do_split=True)
            if best_reps is None or st["m"] < best_meta["m"]:
                best_reps = reps
                best_meta = dict(st, family=f"k{k}_{cname}", k=k, align=cname)

    # Also evaluate cyclic difference-band PLS (r_opt) with heavy-sort + re-opt + 3P-splitting
    r_opt, _ = optimal_r_theoretical(q)
    r_cands = [r_opt] if fast else sorted({r for r in (r_opt - 1, r_opt, r_opt + 1) if 1 <= r <= q - 1})
    for r in r_cands:
        T, E_ab, E_ac, E_bc = build_diffband_pls(q, r)
        for c_shift in (0, q // 3, (2 * q) // 3):
            AL = set(range(ka))
            BL = set(range(kb))
            CL = {(c_shift + i) % q for i in range(kc)}
            reps, st = build_from_pls(q, T, E_ab, E_ac, E_bc, AL, BL, CL, reopt_rounds=reopt, do_split=True)
            if best_reps is None or st["m"] < best_meta["m"]:
                best_reps = reps
                best_meta = dict(st, family=f"band_r{r}_s{c_shift}", k=0, align=f"r{r}_s{c_shift}")

    assert best_reps is not None
    return best_reps, best_meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 9 Option C Approach 1: Block-Idempotent + 3P-Split M_3 Constructor")
    ap.add_argument("--q", type=int, default=0, help="Single prime power q >= 5")
    ap.add_argument("--all", type=str, default="", help="Comma-separated list of q values (e.g. 7,8,9,11,13,16,17,19,23,25)")
    ap.add_argument("--out", type=str, default="", help="Output R_3 file path (single --q mode)")
    ap.add_argument("--out-dir", type=str, default="", help="Output directory for --all mode")
    ap.add_argument("--check-m3", action="store_true", help="Run exact full-bg3 check_m3 (recommended for q <= 17)")
    ap.add_argument("--fast", action="store_true", help="Faster parameter sweep for large q")
    args = ap.parse_args()

    qs = [int(x) for x in args.all.split(",") if x.strip()] if args.all else ([args.q] if args.q > 0 else [7, 8, 9, 11, 13])

    for q in qs:
        t0 = time.time()
        reps, meta = construct_best_opt(q, fast=args.fast)
        suff = verify_suff0(q, reps)
        dt = time.time() - t0
        if suff["total"] != 0:
            print(f"ERROR q={q}: suff={suff}", file=sys.stderr)
            return 2

        chk_str = ""
        if args.check_m3:
            t1 = time.time()
            ops = FieldOps(q)
            res = check_m3(reps, ops, "full-bg3")
            dt_chk = time.time() - t1
            chk_str = f" | check_m3={res['total']} ({dt_chk:.2f}s)"
            if res["total"] != 0:
                print(f"ERROR q={q}: check_m3={res}", file=sys.stderr)
                return 3

        m = meta["m"]
        out_path = ""
        if args.out and len(qs) == 1:
            out_path = args.out
        elif args.out_dir:
            Path(args.out_dir).mkdir(parents=True, exist_ok=True)
            out_path = str(Path(args.out_dir) / f"R3_q{q}_opt_{meta['family']}_m{m}.txt")
        sha_str = ""
        if out_path:
            sha = write_reps(out_path, reps)
            sha_str = f" | saved={out_path} sha256={sha[:16]}..."

        print(
            f"q={q:2d}: m={m:5d} ({m/q**3:.5f}*q^3) [m_raw={meta['m_raw']:5d}, fam={meta['family']:12s}, "
            f"exh={meta['exh']:3d}, pad={meta['pad']:2d}, sp={meta['sp_z']}+{meta['sp_L']}] | "
            f"49/27={49/27*q**3:7.1f} | suff=0 ({dt:.2f}s){chk_str}{sha_str}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
