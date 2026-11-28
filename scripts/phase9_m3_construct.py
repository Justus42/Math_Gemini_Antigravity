#!/usr/bin/env python3
r"""Phase 9: Deterministic Light+Heavy 3D constructor for M_3(R_3) (full-bg3, k = q + 3, 3 <= t <= q).

Pure Python (std-only) + GeneralGF from scripts/gen_general_tqv.py.
Zero randomness, zero metaheuristics, zero local search.

Construction (Cyclic Difference-Band 3P + Complementary 1P on Light+Heavy Skeleton):
  1. Partition symbols into Light and Heavy sets:
       |A_L| = ka = (q + 1) // 3,  |B_L| = kb = q // 3,  |C_L| = kc = (q - 1) // 3
       (ka + kb + kc = q - 1; A_L = {0..ka-1}, B_L = {0..kb-1}, C_L = {(c_shift+i)%q : i < kc}).
       Heavy sets: A_H = F_q \ A_L, B_H = F_q \ B_L, C_H = F_q \ C_L.
     Horizontal planes z = 0..q-2 are assigned 1-to-1 to A_L, B_L, C_L; z* = q - 1 is the heavy plane.
  2. Choose difference-band width r in [1, q - 1] (minimizing m_raw = (3q^2 - 2rq)q + q*AP3(r)):
       - Type 3P x-lines: T = {(a, b, (-a - b) mod q) : (a - b) mod q < r} (size r*q, partial Latin square).
       - Type 1P x-lines: complementary pairs not covered by T:
           1P_ab(a, b) for (a, b) not in proj_ab(T)   (size (q - r)*q),
           1P_ac(a, c) for (a, c) not in proj_ac(T)   (size (q - r)*q),
           1P_bc(b, c) for (b, c) not in proj_bc(T)   (size (q - r)*q).
       - Remaining Typ-3 triples not covered by T or 1P:
           U = {(a, b, c) not in T : (a,b) in proj_ab(T), (a,c) in proj_ac(T), (b,c) in proj_bc(T)}.
  3. Deterministic Light-Plane Matching:
       Match light-plane x-line slots (z in 0..q-2, y in 0..q-1) to compatible x-lines via
       maximum bipartite matching (prioritizing high light-degree lines and 3P lines); fill any
       unmatched light slot with q triples from U matching that plane's fixed symbol.
  4. Deterministic Heavy-Plane Placement (z* = q - 1):
       - Place remaining 3P lines on rows y maximizing new heavy coverage (A_H, B_H, C_H).
       - Place remaining 1P lines on rows y with an optimal x-bijection (bipartite matching)
         maximizing new heavy coverage.
       - Place remaining triples of U on deficient (x, y) cells of z*, followed by a deterministic
         relocation pass over U to eliminate heavy-symbol deficits; fill any residual deficit.

Guarantees (verified directly):
  - Typ 0: all q^3 points (c0, c1, c2) covered.
  - Typ 1: every symbol in A, B, C owns a full horizontal z-plane -> 0 missing across all q^2 directions D_1.
  - Typ 2: every pair in {ab, ac, bc} owns a full x-line -> 0 missing across all q^2 normals N_2.
  - Typ 3: all q^3 triples (a, b, c) covered.
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
from gen_general_tqv import GeneralGF  # noqa: E402
from phase9_m3_lift import FieldOps, check_m3, write_reps  # noqa: E402


def optimal_r_theoretical(q: int) -> tuple[int, int]:
    """Return (best_r, m_raw) minimizing (3q^2 - 2rq)*q + q*AP3(r) over 1 <= r <= q - 1."""
    best_r = max(1, q - 1)
    best_m = 10 ** 18
    for r in range(1, q):
        cnt_ds = 0
        for d in range(r):
            d2 = 2 * d
            for s in range(r):
                if s != d and ((d2 - s) % q) < r:
                    cnt_ds += 1
        m_raw = (3 * q * q - 2 * r * q) * q + q * cnt_ds
        if m_raw < best_m:
            best_m = m_raw
            best_r = r
    return best_r, best_m


def _max_bijection_gain(q: int, gain_adj: list[list[int]], valid_adj: list[list[int]]) -> tuple[int, list[int]] | None:
    """Find bijection pi: 0..q-1 -> 0..q-1 using valid_adj maximizing edges in gain_adj."""
    match_v = [-1] * q
    match_x = [-1] * q
    for x in range(q):
        for v in gain_adj[x]:
            if match_v[v] == -1:
                match_x[x] = v
                match_v[v] = x
                break

    def aug_gain(x: int, vis: list[bool]) -> bool:
        for v in gain_adj[x]:
            if vis[v]:
                continue
            vis[v] = True
            if match_v[v] == -1 or aug_gain(match_v[v], vis):
                match_x[x] = v
                match_v[v] = x
                return True
        return False

    for x in range(q):
        if match_x[x] == -1:
            aug_gain(x, [False] * q)

    def aug_all(x: int, vis: list[bool]) -> bool:
        for v in valid_adj[x]:
            if vis[v]:
                continue
            vis[v] = True
            if match_v[v] == -1 or aug_all(match_v[v], vis):
                match_x[x] = v
                match_v[v] = x
                return True
        return False

    for x in range(q):
        if match_x[x] == -1:
            if not aug_all(x, [False] * q):
                return None

    gain_sets = [set(g) for g in gain_adj]
    gain = sum(1 for x in range(q) if match_x[x] in gain_sets[x])
    return gain, match_x


def build_m3_for_params(q: int, r: int, c_shift: int) -> tuple[list[tuple[int, int, int, int, int, int]], dict[str, int]]:
    """Deterministic construction for fixed (q, r, c_shift)."""
    ka = (q - 1 + 2) // 3
    kb = (q - 1 + 1) // 3
    kc = (q - 1) // 3
    AL = set(range(0, ka))
    BL = set(range(0, kb))
    CL = {(c_shift + i) % q for i in range(kc)}
    AH = set(range(q)) - AL
    BH = set(range(q)) - BL
    CH = set(range(q)) - CL

    # Step 1: Build 3P and complementary 1P x-lines + remaining Typ-3 triples U
    lines: list[tuple] = []
    E_ab = [[False] * q for _ in range(q)]
    E_ac = [[False] * q for _ in range(q)]
    E_bc = [[False] * q for _ in range(q)]
    T_set: set[tuple[int, int, int]] = set()

    for a in range(q):
        for b in range(q):
            if (a - b) % q < r:
                c = (-a - b) % q
                lines.append(("3P", a, b, c))
                T_set.add((a, b, c))
                E_ab[a][b] = True
                E_ac[a][c] = True
                E_bc[b][c] = True

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

    # Step 2: Match x-lines to the q - 1 light planes (q slots per plane)
    plane_owner = [("a", a) for a in sorted(AL)] + [("b", b) for b in sorted(BL)] + [("c", c) for c in sorted(CL)]
    plane_idx = {owner: idx for idx, owner in enumerate(plane_owner)}

    def light_deg(L: tuple) -> int:
        kind = L[0]
        if kind == "3P":
            return (L[1] in AL) + (L[2] in BL) + (L[3] in CL)
        if kind == "1P_ab":
            return (L[1] in AL) + (L[2] in BL)
        if kind == "1P_ac":
            return (L[1] in AL) + (L[2] in CL)
        return (L[1] in BL) + (L[2] in CL)

    lines.sort(key=lambda L: (-light_deg(L), 0 if L[0] == "3P" else 1, L))

    def compat_planes(L: tuple) -> list[int]:
        res: list[int] = []
        kind = L[0]
        if kind == "3P":
            if L[1] in AL:
                res.append(plane_idx[("a", L[1])])
            if L[2] in BL:
                res.append(plane_idx[("b", L[2])])
            if L[3] in CL:
                res.append(plane_idx[("c", L[3])])
        elif kind == "1P_ab":
            if L[1] in AL:
                res.append(plane_idx[("a", L[1])])
            if L[2] in BL:
                res.append(plane_idx[("b", L[2])])
        elif kind == "1P_ac":
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

    # Capacitated matching: each light plane z in 0..q-2 has capacity q.
    # Model as bipartite matching from n_slots = (q-1)*q to lines (fast: <= 600 slots at q=25).
    plane_lines: list[list[int]] = [[] for _ in range(q - 1)]
    for li, L in enumerate(lines):
        for z in compat_planes(L):
            plane_lines[z].append(li)

    n_slots = (q - 1) * q
    match_line = [-1] * len(lines)
    match_slot = [-1] * n_slots

    for z in range(q - 1):
        slot_ptr = 0
        for li in plane_lines[z]:
            if match_line[li] == -1:
                sl = z * q + slot_ptr
                match_slot[sl] = li
                match_line[li] = sl
                slot_ptr += 1
                if slot_ptr == q:
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

    # Emit light-plane reps
    reps: list[tuple[int, int, int, int, int, int]] = []
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

    unmatched_slots = 0
    for z in range(q - 1):
        col_ch, sym = plane_owner[z]
        for y in range(q):
            li = match_slot[z * q + y]
            if li != -1:
                L = lines[li]
                kind = L[0]
                if kind == "3P":
                    _, a, b, c = L
                    for x in range(q):
                        reps.append((x, y, z, a, b, c))
                elif kind == "1P_ab":
                    _, a, b = L
                    for x in range(q):
                        reps.append((x, y, z, a, b, x))
                elif kind == "1P_ac":
                    _, a, c = L
                    for x in range(q):
                        reps.append((x, y, z, a, x, c))
                else:
                    _, b, c = L
                    for x in range(q):
                        reps.append((x, y, z, x, b, c))
            else:
                unmatched_slots += 1
                filled = 0
                for idx in unc_by[col_ch][sym]:
                    if not used_unc[idx]:
                        used_unc[idx] = True
                        a, b, c = unc_t3[idx]
                        reps.append((filled, y, z, a, b, c))
                        filled += 1
                        if filled == q:
                            break
                while filled < q:
                    a = sym if col_ch == "a" else 0
                    b = sym if col_ch == "b" else 0
                    c = sym if col_ch == "c" else 0
                    reps.append((filled, y, z, a, b, c))
                    filled += 1

    # Step 3: Heavy plane z* = q - 1
    zh = q - 1
    z_lines = [lines[li] for li in range(len(lines)) if match_line[li] == -1]
    z_lines.sort(key=lambda L: (0 if L[0] == "3P" else 1, L))

    cnt_a = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_b = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_c = [[[0] * q for _ in range(q)] for _ in range(q)]
    used_pts_z: list[list[set[tuple[int, int, int]]]] = [[set() for _ in range(q)] for _ in range(q)]
    row_load = [0] * q

    # Deficient cell sets for O(1)-amortized placement of unc_t3
    def_a: dict[int, set[tuple[int, int]]] = {a: {(x, y) for y in range(q) for x in range(q)} for a in AH}
    def_b: dict[int, set[tuple[int, int]]] = {b: {(x, y) for y in range(q) for x in range(q)} for b in BH}
    def_c: dict[int, set[tuple[int, int]]] = {c: {(x, y) for y in range(q) for x in range(q)} for c in CH}

    def add_z_pt(x: int, y: int, a: int, b: int, c: int, append_rep: bool = True) -> None:
        if append_rep:
            reps.append((x, y, zh, a, b, c))
        used_pts_z[y][x].add((a, b, c))
        row_load[y] += 1
        if cnt_a[y][x][a] == 0 and a in AH:
            def_a[a].discard((x, y))
        cnt_a[y][x][a] += 1
        if cnt_b[y][x][b] == 0 and b in BH:
            def_b[b].discard((x, y))
        cnt_b[y][x][b] += 1
        if cnt_c[y][x][c] == 0 and c in CH:
            def_c[c].discard((x, y))
        cnt_c[y][x][c] += 1

    def rem_z_pt(x: int, y: int, a: int, b: int, c: int) -> None:
        used_pts_z[y][x].remove((a, b, c))
        row_load[y] -= 1
        cnt_a[y][x][a] -= 1
        if cnt_a[y][x][a] == 0 and a in AH:
            def_a[a].add((x, y))
        cnt_b[y][x][b] -= 1
        if cnt_b[y][x][b] == 0 and b in BH:
            def_b[b].add((x, y))
        cnt_c[y][x][c] -= 1
        if cnt_c[y][x][c] == 0 and c in CH:
            def_c[c].add((x, y))

    for L in z_lines:
        kind = L[0]
        if kind == "3P":
            _, a, b, c = L
            best_3p = None
            for y in range(q):
                if any((a, b, c) in used_pts_z[y][x] for x in range(q)):
                    continue
                g = 0
                if a in AH:
                    g += sum(1 for x in range(q) if cnt_a[y][x][a] == 0)
                if b in BH:
                    g += sum(1 for x in range(q) if cnt_b[y][x][b] == 0)
                if c in CH:
                    g += sum(1 for x in range(q) if cnt_c[y][x][c] == 0)
                cand = (g, -row_load[y], -y)
                if best_3p is None or cand > best_3p[0]:
                    best_3p = (cand, y)
            _, y = best_3p
            for x in range(q):
                add_z_pt(x, y, a, b, c)
        else:
            best_1p = None
            for y in range(q):
                if kind == "1P_ab":
                    a, b = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_a[y][x][a] == 0) if a in AH else 0) + (
                        sum(1 for x in range(q) if cnt_b[y][x][b] == 0) if b in BH else 0
                    )
                    valid_adj = [[c for c in range(q) if (a, b, c) not in used_pts_z[y][x]] for x in range(q)]
                    gain_adj = [[c for c in valid_adj[x] if c in CH and cnt_c[y][x][c] == 0] for x in range(q)]
                elif kind == "1P_ac":
                    a, c = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_a[y][x][a] == 0) if a in AH else 0) + (
                        sum(1 for x in range(q) if cnt_c[y][x][c] == 0) if c in CH else 0
                    )
                    valid_adj = [[b for b in range(q) if (a, b, c) not in used_pts_z[y][x]] for x in range(q)]
                    gain_adj = [[b for b in valid_adj[x] if b in BH and cnt_b[y][x][b] == 0] for x in range(q)]
                else:
                    b, c = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_b[y][x][b] == 0) if b in BH else 0) + (
                        sum(1 for x in range(q) if cnt_c[y][x][c] == 0) if c in CH else 0
                    )
                    valid_adj = [[a for a in range(q) if (a, b, c) not in used_pts_z[y][x]] for x in range(q)]
                    gain_adj = [[a for a in valid_adj[x] if a in AH and cnt_a[y][x][a] == 0] for x in range(q)]
                res = _max_bijection_gain(q, gain_adj, valid_adj)
                if res is None:
                    continue
                vg, pi = res
                cand = (fg + vg, -row_load[y], -y)
                if best_1p is None or cand > best_1p[0]:
                    best_1p = (cand, y, pi)
            _, y, pi = best_1p
            for x in range(q):
                if kind == "1P_ab":
                    add_z_pt(x, y, L[1], L[2], pi[x])
                elif kind == "1P_ac":
                    add_z_pt(x, y, L[1], pi[x], L[2])
                else:
                    add_z_pt(x, y, pi[x], L[1], L[2])

    # Place remaining unc_t3 points onto z* using deficient cell sets (fast even for q = 25!)
    rem_unc = [unc_t3[i] for i in range(len(unc_t3)) if not used_unc[i]]
    rem_unc.sort(key=lambda t: (-((t[0] in AH) + (t[1] in BH) + (t[2] in CH)), t))
    unc_pos: list[list[int]] = []
    rr_cell = 0
    q2 = q * q

    for a, b, c in rem_unc:
        cands: set[tuple[int, int]] = set()
        if a in AH:
            cands |= def_a[a]
        if b in BH:
            cands |= def_b[b]
        if c in CH:
            cands |= def_c[c]

        chosen_xy = None
        if cands:
            best_c = None
            for x, y in cands:
                if (a, b, c) in used_pts_z[y][x]:
                    continue
                g = (
                    (a in AH and cnt_a[y][x][a] == 0)
                    + (b in BH and cnt_b[y][x][b] == 0)
                    + (c in CH and cnt_c[y][x][c] == 0)
                )
                cand = (g, -len(used_pts_z[y][x]), -y, -x)
                if best_c is None or cand > best_c[0]:
                    best_c = (cand, x, y)
            if best_c is not None:
                chosen_xy = (best_c[1], best_c[2])

        if chosen_xy is None:
            # Round-robin cell on z* without duplicate 6-tuple
            for _ in range(q2):
                x = rr_cell % q
                y = (rr_cell // q) % q
                rr_cell = (rr_cell + 1) % q2
                if (a, b, c) not in used_pts_z[y][x]:
                    chosen_xy = (x, y)
                    break

        x, y = chosen_xy
        add_z_pt(x, y, a, b, c, append_rep=False)
        unc_pos.append([x, y, a, b, c])

    # Deterministic relocation pass over unc_pos (only inspects deficient cells!)
    for _pass in range(5):
        tot_def = sum(len(s) for s in def_a.values()) + sum(len(s) for s in def_b.values()) + sum(len(s) for s in def_c.values())
        if tot_def == 0:
            break
        moved = False
        for item in unc_pos:
            x, y, a, b, c = item
            loss = (
                (a in AH and cnt_a[y][x][a] == 1)
                + (b in BH and cnt_b[y][x][b] == 1)
                + (c in CH and cnt_c[y][x][c] == 1)
            )
            if loss == 3:
                continue
            cands = set()
            if a in AH:
                cands |= def_a[a]
            if b in BH:
                cands |= def_b[b]
            if c in CH:
                cands |= def_c[c]
            if not cands:
                continue
            best_m = None
            for x2, y2 in cands:
                if (x2 == x and y2 == y) or (a, b, c) in used_pts_z[y2][x2]:
                    continue
                gain = (
                    (a in AH and cnt_a[y2][x2][a] == 0)
                    + (b in BH and cnt_b[y2][x2][b] == 0)
                    + (c in CH and cnt_c[y2][x2][c] == 0)
                )
                if gain > loss:
                    cand = (gain - loss, -len(used_pts_z[y2][x2]), -y2, -x2)
                    if best_m is None or cand > best_m[0]:
                        best_m = (cand, x2, y2)
            if best_m is not None:
                _, x2, y2 = best_m
                rem_z_pt(x, y, a, b, c)
                add_z_pt(x2, y2, a, b, c, append_rep=False)
                item[0], item[1] = x2, y2
                moved = True
        if not moved:
            break

    for x, y, a, b, c in unc_pos:
        reps.append((x, y, zh, a, b, c))

    # Fill any residual heavy-symbol deficits on z*
    extra_heavy = 0
    for y in range(q):
        for x in range(q):
            ma = [a for a in sorted(AH) if cnt_a[y][x][a] == 0]
            mb = [b for b in sorted(BH) if cnt_b[y][x][b] == 0]
            mc = [c for c in sorted(CH) if cnt_c[y][x][c] == 0]
            need = max(len(ma), len(mb), len(mc))
            for i in range(need):
                a = ma[i] if i < len(ma) else next(iter(AH))
                b = mb[i] if i < len(mb) else next(iter(BH))
                c = mc[i] if i < len(mc) else next(iter(CH))
                if (a, b, c) in used_pts_z[y][x]:
                    found = False
                    for ca in range(q):
                        for cb in range(q):
                            for cc in range(q):
                                aa = ma[i] if i < len(ma) else ca
                                bb = mb[i] if i < len(mb) else cb
                                cc2 = mc[i] if i < len(mc) else cc
                                if (aa, bb, cc2) not in used_pts_z[y][x]:
                                    a, b, c = aa, bb, cc2
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                add_z_pt(x, y, a, b, c, append_rep=True)
                extra_heavy += 1

    meta = {
        "q": q,
        "r": r,
        "c_shift": c_shift,
        "m": len(reps),
        "n3p": n3p,
        "n1p": n1p,
        "unc_t3": len(unc_t3),
        "unmatched_slots": unmatched_slots,
        "extra_heavy": extra_heavy,
    }
    return reps, meta


def construct_best(q: int) -> tuple[list[tuple[int, int, int, int, int, int]], dict[str, int]]:
    """Deterministically select best (r, c_shift) around theoretical optimum."""
    GeneralGF(q)  # verify q is a prime power
    r_opt, _ = optimal_r_theoretical(q)
    if q <= 13:
        r_cands = sorted({rc for rc in (r_opt - 1, r_opt, r_opt + 1) if 1 <= rc < q})
        shift_cands = sorted({0, q // 3, (2 * q) // 3})
    else:
        r_cands = sorted({rc for rc in (r_opt, r_opt + 1) if 1 <= rc < q})
        shift_cands = [(2 * q) // 3]

    best_reps = None
    best_meta = None
    for r in r_cands:
        for csh in shift_cands:
            reps, meta = build_m3_for_params(q, r, csh)
            if best_reps is None or len(reps) < len(best_reps):
                best_reps = reps
                best_meta = meta
    assert best_reps is not None and best_meta is not None
    return best_reps, best_meta


def check_sufficient_full_bg3(reps: list[tuple[int, int, int, int, int, int]], q: int) -> dict[str, int]:
    """Fast O(m) check of sufficient conditions for full-bg3:
       0 duplicates, Typ 0 = 0, every symbol in a/b/c owns a full z-plane (=> Typ 1 = 0),
       every pair in {ab, ac, bc} owns a full x-line (=> Typ 2 = 0), Typ 3 = 0."""
    q2, q3 = q * q, q * q * q
    dups = len(reps) - len(set(reps))
    pts0 = {(r[0], r[1], r[2]) for r in reps}
    pts3 = {(r[3], r[4], r[5]) for r in reps}
    miss0 = q3 - len(pts0)
    miss3 = q3 - len(pts3)

    # Full horizontal z-planes per symbol
    miss_zplanes = 0
    for col_idx in (3, 4, 5):
        by_sz: list[list[set[tuple[int, int]]]] = [[set() for _ in range(q)] for _ in range(q)]
        for r in reps:
            by_sz[r[col_idx]][r[2]].add((r[0], r[1]))
        for s in range(q):
            if not any(len(by_sz[s][z]) == q2 for z in range(q)):
                miss_zplanes += 1

    # Full x-lines per symbol pair
    miss_xlines = 0
    for i1, i2 in ((3, 4), (3, 5), (4, 5)):
        by_pyz: dict[tuple[int, int, int, int], set[int]] = defaultdict(set)
        for r in reps:
            by_pyz[(r[i1], r[i2], r[1], r[2])].add(r[0])
        covered_pairs = {(p1, p2) for (p1, p2, y, z), xs in by_pyz.items() if len(xs) == q}
        miss_xlines += q2 - len(covered_pairs)

    return {
        "dups": dups,
        "miss0": miss0,
        "miss_zplanes": miss_zplanes,
        "miss_xlines": miss_xlines,
        "miss3": miss3,
        "total": dups + miss0 + miss_zplanes + miss_xlines + miss3,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Deterministic Light+Heavy M_3(R_3) full-bg3 constructor")
    ap.add_argument("--q", type=int, help="single prime power q >= 5")
    ap.add_argument("--out", help="output path for single --q")
    ap.add_argument("--sweep", action="store_true", help="run full sweep q in [5,7,8,9,11,13,16,19,23,25]")
    ap.add_argument("--save-dir", help="directory to save lists with m_det < 2q^3-q^2 for q in [7,8,9,11,13]")
    ap.add_argument("--check-exact", action="store_true", help="also run exact check_m3(full-bg3)")
    args = ap.parse_args()

    if args.sweep:
        qs = [5, 7, 8, 9, 11, 13, 16, 19, 23, 25]
        save_qs = {7, 8, 9, 11, 13}
        print(f"{'q':>3} | {'r':>2} | {'m_det':>6} | {'m/q^3':>7} | {'ell':>6} | {'gain':>6} | {'N(t=4)':>8} | {'suff':>4} | {'m3_exact':>8} | {'exh':>3} | {'time':>6}")
        print("-" * 92)
        for q in qs:
            t0 = time.perf_counter()
            reps, meta = construct_best(q)
            dt = time.perf_counter() - t0
            suff = check_sufficient_full_bg3(reps, q)
            assert suff["total"] == 0, f"sufficient check failed for q={q}: {suff}"
            m3_str = "skipped"
            if q <= 13:
                chk = check_m3(reps, FieldOps(q), mode="full-bg3")
                assert chk["total"] == 0, f"check_m3 failed for q={q}: {chk}"
                m3_str = "0 (OK)"
            m = len(reps)
            ell = 2 * q**3 - q**2
            gain = ell - m
            nt4 = m * q
            print(
                f"{q:3d} | {meta['r']:2d} | {m:6d} | {m/q**3:7.4f} | {ell:6d} | {gain:+6d} | "
                f"{nt4:8d} | {suff['total']:4d} | {m3_str:>8} | {meta['extra_heavy']:3d} | {dt:5.2f}s"
            )
            if args.save_dir and q in save_qs and m < ell:
                out_p = Path(args.save_dir) / f"R3_q{q}_fullbg3_det_m{m}.txt"
                sha = write_reps(out_p, reps)
                print(f"    -> saved {out_p} sha256={sha}")
        return

    if args.q is None:
        sys.exit("need --q Q or --sweep")
    reps, meta = construct_best(args.q)
    suff = check_sufficient_full_bg3(reps, args.q)
    assert suff["total"] == 0, f"sufficient check failed: {suff}"
    if args.check_exact:
        chk = check_m3(reps, FieldOps(args.q), mode="full-bg3")
        assert chk["total"] == 0, f"check_m3 failed: {chk}"
    ell = 2 * args.q**3 - args.q**2
    print(f"q={args.q} r={meta['r']} csh={meta['c_shift']} m_det={len(reps)} ({len(reps)/args.q**3:.4f}*q^3) ell={ell} gain={ell-len(reps):+d} suff=0")
    if args.out:
        sha = write_reps(args.out, reps)
        print(f"wrote {args.out} sha256={sha}")


if __name__ == "__main__":
    main()
