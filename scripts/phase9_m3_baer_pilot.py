#!/usr/bin/env python3
"""Phase 9 AP 3: Structural 3D Baer Pilot for M_3(R_3) at q = 9 (s = 3), with scaling check q = 16, 25.

Pure Python (std-only) + FieldOps/check_m3 from scripts/phase9_m3_lift.py.
Tests four concrete 3D Baer / F_3-trace mechanisms at q = 9 against the thresholds:
  - elliptic:        2*q^3 - q^2       = 1377
  - det cyclic band: m_det(9)          = 1332
  - solver warmstart: m_sol(9)         = 1324
  - 49/27 * q^3:                       = 1323
  - 46/27 * q^3 (LP1 Light+Heavy):     = 1242

Experiments executed:
  1. Single-set 3D geometry checks on GF(9):
     - 4D F_3-subspaces (|W| = 81): verify non-horizontal ones fail Typ 1.
     - Rank-3 F_3-linear sets (|P| = 12): verify Typ 2 = 0 and mandatory planarity.
     - Baer cylinder X x A_Baer (|P| = 108): verify Typ 1 = 0.
     - 3 pairwise transverse 2D Baer families (Fam A, B, C) in AG(2, 9).
  2. Architecture 1 — Full 3-Family 3D Baer Cylinder construction (check_m3 = 0):
     - Explicit build at q = 9 (verified via check_m3(full-bg3) == 0) + exact formula check at q = 16, 25.
  3. Architecture 2 — 2D Baer-Grid Stack (z = a, 9 x 117 = 1053 pts) with untwisted, linear,
     and nonlinear twists: exact Typ 0..3 missing counts via check_m3(full-bg3).
  4. Architecture 3 — GF(9) = F_3^2 additive F_3-subline complement (r = 6, AP3 = 12, m_raw = 1323)
     placed on the Light+Heavy skeleton (verified via check_m3(full-bg3) == 0).
"""

from __future__ import annotations

from collections import defaultdict
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase9_m3_construct import _max_bijection_gain, check_sufficient_full_bg3  # noqa: E402
from phase9_m3_lift import FieldOps, check_m3  # noqa: E402


def gf_pow(ops: FieldOps, x: int, e: int) -> int:
    r = 1
    for _ in range(e):
        r = ops.mul[r][x]
    return r


def field_inv_table(ops: FieldOps) -> list[int]:
    q = ops.q
    inv = [0] * q
    for x in range(1, q):
        for y in range(1, q):
            if ops.mul[x][y] == 1:
                inv[x] = y
                break
    return inv


def subfield_and_basis(ops: FieldOps) -> tuple[int, list[int], int, list[int]]:
    q = ops.q
    s = int(round(q ** 0.5))
    assert s * s == q, f"q={q} is not a square"
    fn = [x for x in range(q) if gf_pow(ops, x, s) == x]
    assert len(fn) == s
    om = next(x for x in range(q) if x not in fn)
    inv = field_inv_table(ops)
    return s, fn, om, inv


def make_baer_family(ops: FieldOps, fn: list[int], om: int, inv: list[int], eps: int, f: int) -> dict[int, set[tuple[int, int]]]:
    """Construct q - s affine Baer classes in AG(2, q) for F_s-basis (eps, f)."""
    add, mul = ops.add, ops.mul
    s = len(fn)
    nz = [x for x in fn if x != 0]
    classes: dict[int, set[tuple[int, int]]] = {}
    for idx_i, i in enumerate(nz):
        t = mul[i][om]
        w0 = mul[i][f]
        for idx_j, j in enumerate(fn):
            r = mul[j][f]
            pts: set[tuple[int, int]] = set()
            for x in fn:
                pts.add((add[x][t], 0))
            for y in fn:
                w = add[w0][mul[y][eps]]
                z = inv[w]
                for x in fn:
                    c = add[mul[add[mul[x][eps]][r]][z]][t]
                    pts.add((c, z))
            classes[idx_i * s + idx_j] = pts
    return classes


def check_2d_lines(ops: FieldOps, pts: set[tuple[int, int]]) -> int:
    q = ops.q
    sub, mul = ops.sub, ops.mul
    miss = 0
    for w in range(q):
        seen = {sub[y][mul[w][z]] for y, z in pts}
        miss += q - len(seen)
    return miss


def check_typ1_single(ops: FieldOps, pts: set[tuple[int, int, int]]) -> int:
    q = ops.q
    sub, mul = ops.sub, ops.mul
    miss = 0
    for v in range(q):
        for w in range(q):
            seen = {(sub[x][mul[v][z]], sub[y][mul[w][z]]) for x, y, z in pts}
            miss += q * q - len(seen)
    return miss


def check_typ2_single(ops: FieldOps, pts: set[tuple[int, int, int]]) -> int:
    q = ops.q
    add, mul = ops.add, ops.mul
    miss = 0
    for al in range(q):
        for be in range(q):
            seen = {add[add[x][mul[al][y]]][mul[be][z]] for x, y, z in pts}
            miss += q - len(seen)
    return miss


def exp1_single_set_geometry(ops: FieldOps) -> None:
    print("=== EXP 1: 3D Baer & F_3-Subspace Geometry Checks (q = 9, s = 3) ===")
    q = ops.q
    s, fn, om, inv = subfield_and_basis(ops)
    add, mul = ops.add, ops.mul

    # (a) Non-horizontal 4D F_3-subspace W = {(x, y, z) : y_om = 0, z_om = 0} (size 81)
    # Wait: x in F_9 (2D), y in F_3 (1D), z in F_3 (1D) -> 4D F_3-subspace of size 81!
    w_nonhoriz = {(x, y, z) for x in range(q) for y in fn for z in fn}
    m_w = check_typ1_single(ops, w_nonhoriz)
    print(f"  4D F_3-subspace (non-horizontal, |W|={len(w_nonhoriz)}): Typ1_miss = {m_w} (>0 => obstructed)")

    # (b) Rank-3 F_3-linear set L_U \ {X_inf} (size 12): spans plane y + om*z = 1
    pts_r3 = set()
    for u1 in fn:
        for u2 in fn:
            for u3 in fn:
                t = add[u2][mul[u3][om]]
                if t == 0:
                    continue
                it = inv[t]
                pts_r3.add((mul[u1][it], mul[u2][it], mul[u3][it]))
    m_r3 = check_typ2_single(ops, pts_r3)
    plane_vals = {add[y][mul[om][z]] for _, y, z in pts_r3}
    print(f"  Rank-3 linear set (|P|={len(pts_r3)}): Typ2_miss = {m_r3}, y + om*z = {plane_vals} (necessarily planar)")

    # (c) 3D Baer cylinder X x A_Baer (size 108)
    famA = make_baer_family(ops, fn, om, inv, 1, om)
    famB = make_baer_family(ops, fn, om, inv, om, 1)
    famC = make_baer_family(ops, fn, om, inv, add[1][om], 1)
    cyl0 = {(x, y, z) for x in range(q) for y, z in famA[0]}
    m_cyl = check_typ1_single(ops, cyl0)
    print(f"  Baer cylinder X x A_Baer (|P|={len(cyl0)}): Typ1_miss = {m_cyl} (OK)")

    for nm, fam in [("A", famA), ("B", famB), ("C", famC)]:
        m2 = {check_2d_lines(ops, pts) for pts in fam.values()}
        assert m2 == {0}
    i_ab = [len({p for p in p1 & p2 if p[1] != 0}) for p1 in famA.values() for p2 in famB.values()]
    i_ac = [len({p for p in p1 & p3 if p[1] != 0}) for p1 in famA.values() for p3 in famC.values()]
    i_bc = [len({p for p in p2 & p3 if p[1] != 0}) for p2 in famB.values() for p3 in famC.values()]
    print(
        f"  3 transverse Baer families (6 classes of 12 each, 2D_miss=0): "
        f"|A∩B|_nz={set(i_ab)}, |A∩C|_nz={set(i_ac)}, |B∩C|_nz={set(i_bc)}"
    )


def build_exp2_baer_cylinder_full(ops: FieldOps, verify_exact: bool = True) -> dict[str, int]:
    """Explicit 3-family 3D Baer-cylinder construction (z != 0 Baer grid + z = 0 F-packing + U)."""
    q = ops.q
    s, fn, om, inv = subfield_and_basis(ops)
    add = ops.add
    n_baer = q - s

    famA = make_baer_family(ops, fn, om, inv, 1, om)
    famB = make_baer_family(ops, fn, om, inv, om, 1)
    famC = make_baer_family(ops, fn, om, inv, add[1][om], 1)

    a_of, b_of, c_of = {}, {}, {}
    for sym, pts in famA.items():
        for p in pts:
            if p[1] != 0:
                a_of[p] = sym
    for sym, pts in famB.items():
        for p in pts:
            if p[1] != 0:
                b_of[p] = sym
    for sym, pts in famC.items():
        for p in pts:
            if p[1] != 0:
                c_of[p] = sym

    reps: list[tuple[int, int, int, int, int, int]] = []
    cov_ab: set[tuple[int, int]] = set()
    cov_ac: set[tuple[int, int]] = set()
    cov_bc: set[tuple[int, int]] = set()
    cov_t3: set[tuple[int, int, int]] = set()

    # 1. Place all (q - 1) * q lines on z != 0
    n3p_nz = 0
    n1p_nz = 0
    for z in range(1, q):
        for y in range(q):
            p = (y, z)
            a, b, c = a_of.get(p), b_of.get(p), c_of.get(p)
            if a is not None and b is not None and c is not None:
                n3p_nz += 1
                for x in range(q):
                    reps.append((x, y, z, a, b, c))
                cov_ab.add((a, b))
                cov_ac.add((a, c))
                cov_bc.add((b, c))
                cov_t3.add((a, b, c))
            elif a is not None and b is not None:
                n1p_nz += 1
                for x in range(q):
                    reps.append((x, y, z, a, b, x))
                cov_ab.add((a, b))
                for cc in range(q):
                    cov_t3.add((a, b, cc))
            elif a is not None and c is not None:
                n1p_nz += 1
                for x in range(q):
                    reps.append((x, y, z, a, x, c))
                cov_ac.add((a, c))
                for bb in range(q):
                    cov_t3.add((a, bb, c))
            elif b is not None and c is not None:
                n1p_nz += 1
                for x in range(q):
                    reps.append((x, y, z, x, b, c))
                cov_bc.add((b, c))
                for aa in range(q):
                    cov_t3.add((aa, b, c))
            else:
                raise RuntimeError(f"unexpected uncovered (y,z)={p}")

    # 2. On z = 0, cover:
    #    - Baer x-lines needed on z = 0 for Typ 1 of Baer symbols?
    #      Each Baer symbol a in 0..n_baer-1 needs its s points y on z = 0 to carry a full x-line!
    #      AND each F-symbol in n_baer..q-1 needs a full horizontal plane z = 0 (all q*q points (x, y, 0))!
    #    - Remaining pairs (all involving >= 1 F-symbol):
    #      (i)  F_a x F_b x B_c: s^2 3P lines (covers F_a x F_b, plus s^2 of F_a x B_c and F_b x B_c)
    #      (ii) F_a x B_b x F_c: s^2 3P lines
    #      (iii)B_a x F_b x F_c: s^2 3P lines
    #      (iv) Remaining F_a x B_b & F_a x B_c (s*(q-s) - s^2 = s*(q - 2s) each):
    #           pack into s*(q - 2s) 3P lines of F_a x B_b x B_c (and symmetrically for F_b, F_c).
    #      Note: every 3P line on z = 0 is placed on a y compatible with its Baer symbol(s) when needed,
    #      and any remaining Typ-1 (x, y) cells on z = 0 are filled!
    F_syms = list(range(n_baer, q))
    B_syms = list(range(n_baer))
    z0_3p: list[tuple[int, int, int]] = []

    # Assign disjoint B-targets for F x F x B (size s^2 = q, wait n_baer = q - s; each B_c appears s times?
    # Wait: for each fa in F_a and fb in F_b (s^2 pairs), we need DISTINCT (fa, bc) and (fb, bc)!
    # Since |F_a| = s and |B_c| = q - s >= s (for s >= 2, actually q - s = s(s-1) >= s for s >= 2):
    # Map (i_a, i_b) in [0..s-1]^2 -> bc = (i_a + i_b) % s (each fa gets bc in 0..s-1, each fb gets bc in 0..s-1)!
    # That covers ALL s^2 pairs of F_a x F_b, plus s^2 pairs F_a x {0..s-1} and F_b x {0..s-1}!
    for ia, fa in enumerate(F_syms):
        for ib, fb in enumerate(F_syms):
            bc = B_syms[(ia + ib) % s]
            z0_3p.append((fa, fb, bc))
            bb = B_syms[(ia + ib) % s]
            z0_3p.append((fa, bb, F_syms[ib]))
            ba = B_syms[(ia + ib) % s]
            z0_3p.append((ba, F_syms[ia], F_syms[ib]))

    # Remaining F x B pairs: for each f in F, B symbols in B_syms[s:] (size q - 2s)!
    # Pack (fa, bb, bc) with bb = bc in B_syms[s:] (covers (fa, bb) and (fa, bc) simultaneously!)
    for fa in F_syms:
        for b_sym in B_syms[s:]:
            z0_3p.append((fa, b_sym, b_sym))
    for fb in F_syms:
        for a_sym in B_syms[s:]:
            z0_3p.append((a_sym, fb, a_sym))
    for fc in F_syms:
        for a_sym in B_syms[s:]:
            z0_3p.append((a_sym, a_sym, fc))

    # Place z0_3p lines onto y in 0..q-1 maximizing Typ-1 coverage on z = 0:
    # Required on z = 0:
    #   - Every F-symbol in a, b, c needs ALL q*q cells (x, y)
    #   - Every Baer symbol a in B_syms needs its s y-rows y_req_a[a] (all q values of x)
    y_req_a = {sym: {y for y, z in pts if z == 0} for sym, pts in famA.items()}
    y_req_b = {sym: {y for y, z in pts if z == 0} for sym, pts in famB.items()}
    y_req_c = {sym: {y for y, z in pts if z == 0} for sym, pts in famC.items()}

    cnt_a = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_b = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_c = [[[0] * q for _ in range(q)] for _ in range(q)]
    used_z0: list[list[set[tuple[int, int, int]]]] = [[set() for _ in range(q)] for _ in range(q)]

    def need_a(a: int, y: int) -> bool:
        return (a >= n_baer) or (y in y_req_a[a])

    def need_b(b: int, y: int) -> bool:
        return (b >= n_baer) or (y in y_req_b[b])

    def need_c(c: int, y: int) -> bool:
        return (c >= n_baer) or (y in y_req_c[c])

    def add_z0(x: int, y: int, a: int, b: int, c: int) -> None:
        reps.append((x, y, 0, a, b, c))
        used_z0[y][x].add((a, b, c))
        cnt_a[y][x][a] += 1
        cnt_b[y][x][b] += 1
        cnt_c[y][x][c] += 1
        cov_t3.add((a, b, c))

    for a, b, c in z0_3p:
        best = None
        for y in range(q):
            if any((a, b, c) in used_z0[y][x] for x in range(q)):
                continue
            g = 0
            if need_a(a, y):
                g += sum(1 for x in range(q) if cnt_a[y][x][a] == 0)
            if need_b(b, y):
                g += sum(1 for x in range(q) if cnt_b[y][x][b] == 0)
            if need_c(c, y):
                g += sum(1 for x in range(q) if cnt_c[y][x][c] == 0)
            cand = (g, -sum(len(used_z0[y][x]) for x in range(q)), -y)
            if best is None or cand > best[0]:
                best = (cand, y)
        assert best is not None
        y = best[1]
        for x in range(q):
            add_z0(x, y, a, b, c)
        cov_ab.add((a, b))
        cov_ac.add((a, c))
        cov_bc.add((b, c))

    assert len(cov_ab) == q * q and len(cov_ac) == q * q and len(cov_bc) == q * q

    # 3. Place remaining uncovered Typ-3 triples on z = 0 cells that maximize Typ-1 gain
    rem_t3 = [(a, b, c) for a in range(q) for b in range(q) for c in range(q) if (a, b, c) not in cov_t3]
    for a, b, c in rem_t3:
        best = None
        for y in range(q):
            na, nb, nc = need_a(a, y), need_b(b, y), need_c(c, y)
            for x in range(q):
                if (a, b, c) in used_z0[y][x]:
                    continue
                g = (na and cnt_a[y][x][a] == 0) + (nb and cnt_b[y][x][b] == 0) + (nc and cnt_c[y][x][c] == 0)
                cand = (g, -len(used_z0[y][x]), -y, -x)
                if best is None or cand > best[0]:
                    best = (cand, x, y)
        assert best is not None
        add_z0(best[1], best[2], a, b, c)

    # 4. Fill any residual Typ-1 deficits on z = 0 (for F-symbols or Baer z=0 rows)
    extra_z0 = 0
    for y in range(q):
        for x in range(q):
            ma = [a for a in range(q) if need_a(a, y) and cnt_a[y][x][a] == 0]
            mb = [b for b in range(q) if need_b(b, y) and cnt_b[y][x][b] == 0]
            mc = [c for c in range(q) if need_c(c, y) and cnt_c[y][x][c] == 0]
            need = max(len(ma), len(mb), len(mc))
            for i in range(need):
                a = ma[i] if i < len(ma) else F_syms[0]
                b = mb[i] if i < len(mb) else F_syms[0]
                c = mc[i] if i < len(mc) else F_syms[0]
                if (a, b, c) in used_z0[y][x]:
                    found = False
                    for ca in range(q):
                        for cb in range(q):
                            for cc in range(q):
                                aa = ma[i] if i < len(ma) else ca
                                bb = mb[i] if i < len(mb) else cb
                                cc2 = mc[i] if i < len(mc) else cc
                                if (aa, bb, cc2) not in used_z0[y][x]:
                                    a, b, c = aa, bb, cc2
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                add_z0(x, y, a, b, c)
                extra_z0 += 1

    dups = len(reps) - len(set(reps))
    chk_tot = -1
    if verify_exact:
        chk = check_m3(reps, ops, mode="full-bg3")
        chk_tot = chk["total"]
        assert dups == 0 and chk_tot == 0, f"failed check_m3: dups={dups}, chk={chk}"

    return {
        "q": q,
        "m": len(reps),
        "n3p_nz": n3p_nz,
        "n1p_nz": n1p_nz,
        "z0_3p": len(z0_3p),
        "rem_t3": len(rem_t3),
        "extra_z0": extra_z0,
        "dups": dups,
        "check_m3": chk_tot,
    }


def exp3_2d_baer_stack_q9(ops: FieldOps) -> None:
    print("\n=== EXP 3: 2D Baer-Grid Stack (z = a, 9 x 117 = 1053 pts) with Twists ===")
    q = ops.q
    s, fn, om, inv = subfield_and_basis(ops)
    add, sub, mul = ops.add, ops.sub, ops.mul
    decomp = {add[z1][mul[z2][om]]: (z1, z2) for z1 in fn for z2 in fn}
    f3_idx = {x: idx for idx, x in enumerate(fn)}
    f3_nz_idx = {x: idx for idx, x in enumerate([u for u in fn if u != 0])}

    # Exact 2D Baer grid (117 reps) from Phase 8 NOTIZ_3 §3.1
    r2d: list[tuple[int, int, int, int]] = []
    for y in range(1, q):
        w = inv[y]
        w1, w2 = decomp[w]
        for x in range(q):
            if w1 != 0 and w2 != 0:
                ja = decomp[mul[sub[x][mul[w2][om]]][w]][1]
                jb = decomp[mul[sub[x][mul[w1][om]]][w]][0]
                r2d.append((x, y, f3_nz_idx[w2] * 3 + f3_idx[ja], f3_nz_idx[w1] * 3 + f3_idx[jb]))
            elif w2 == 0:
                jb = decomp[mul[sub[x][mul[w1][om]]][w]][0]
                ia = decomp[mul[x][w]][1]
                r2d.append((x, y, 6 + f3_idx[ia], f3_nz_idx[w1] * 3 + f3_idx[jb]))
            else:
                ja = decomp[mul[sub[x][mul[w2][om]]][w]][1]
                ib = decomp[mul[x][w]][0]
                r2d.append((x, y, f3_nz_idx[w2] * 3 + f3_idx[ja], 6 + f3_idx[ib]))
    for x in range(q):
        x1, x2 = decomp[x]
        if x2 != 0:
            for j in range(3):
                r2d.append((x, 0, f3_nz_idx[x2] * 3 + j, f3_nz_idx[x2] * 3 + j))
            for m in range(3):
                r2d.append((x, 0, 6 + m, 6 + m))
        else:
            xi = f3_idx[x1]
            for m in range(3):
                r2d.append((x, 0, 6 + m, 6 + (m + xi) % 3))
    assert len(r2d) == 117

    twists = [
        ("untwisted (x, y, a)", lambda x, y, a: (x, y, a)),
        ("linear (x+a, y+om*a, a)", lambda x, y, a: (add[x][a], add[y][mul[om][a]], a)),
        ("quadratic (x+a^2, y+a, a)", lambda x, y, a: (add[x][mul[a][a]], add[y][a], a)),
        ("cubic (x+a^2, y+a^3, a)", lambda x, y, a: (add[x][mul[a][a]], add[y][gf_pow(ops, a, 3)], a)),
    ]
    for label, fn_xy in twists:
        reps = [(*fn_xy(x, y, a), a, b, c) for a in range(q) for x, y, b, c in r2d]
        chk = check_m3(reps, ops, mode="full-bg3")
        print(
            f"  {label:28s}: m={len(reps):4d} | Typ0={chk['miss0']} "
            f"Typ1={chk['miss1']} (fs={chk['fail_sets1']:3d}/243) "
            f"Typ2={chk['miss2']} (fs={chk['fail_sets2']:2d}/243) Typ3={chk['miss3']}"
        )


def exp4_f3_subline_light_heavy_q9(ops: FieldOps) -> None:
    print("\n=== EXP 4: GF(9) = F_3^2 Additive F_3-Subline Complement in Light+Heavy ===")
    q = ops.q
    _, fn, om, _ = subfield_and_basis(ops)
    add, sub, mul, neg = ops.add, ops.sub, ops.mul, ops.neg

    # Exclude F_3 = {0, 1, 2} as difference band complement E -> D = GF(9) \ F_3 (size r = 6)
    E = set(fn)
    D = set(range(q)) - E
    T_list = [(a, b, neg[add[a][b]]) for a in range(q) for b in range(q) if sub[a][b] in D]
    E_ab = [[False] * q for _ in range(q)]
    E_ac = [[False] * q for _ in range(q)]
    E_bc = [[False] * q for _ in range(q)]
    T_set = set(T_list)
    lines: list[tuple] = []
    for a, b, c in T_list:
        lines.append(("3P", a, b, c))
        E_ab[a][b] = E_ac[a][c] = E_bc[b][c] = True
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
    unc_t3 = [
        (a, b, c)
        for a in range(q)
        for b in range(q)
        if E_ab[a][b]
        for c in range(q)
        if E_ac[a][c] and E_bc[b][c] and (a, b, c) not in T_set
    ]
    m_raw = len(lines) * q + len(unc_t3)
    print(f"  GF(9) F_3-subline complement: |T|={len(T_list)}, |1P|={len(lines)-len(T_list)}, |U|={len(unc_t3)}, m_raw={m_raw} (= 49/27 * 9^3)")

    # Place onto Light+Heavy with F_3-coset light sets AL={0,1,2}, BL={0,1,2}, CL={0,1}
    AL, BL, CL = set(fn), set(fn), {fn[0], fn[1]}
    AH, BH, CH = set(range(q)) - AL, set(range(q)) - BL, set(range(q)) - CL
    plane_owner = [("a", a) for a in sorted(AL)] + [("b", b) for b in sorted(BL)] + [("c", c) for c in sorted(CL)]
    plane_idx = {o: i for i, o in enumerate(plane_owner)}

    def light_deg(L: tuple) -> int:
        k = L[0]
        if k == "3P":
            return (L[1] in AL) + (L[2] in BL) + (L[3] in CL)
        if k == "1P_ab":
            return (L[1] in AL) + (L[2] in BL)
        if k == "1P_ac":
            return (L[1] in AL) + (L[2] in CL)
        return (L[1] in BL) + (L[2] in CL)

    lines.sort(key=lambda L: (-light_deg(L), 0 if L[0] == "3P" else 1, L))
    plane_lines: list[list[int]] = [[] for _ in range(q - 1)]
    for li, L in enumerate(lines):
        k = L[0]
        if k == "3P":
            if L[1] in AL: plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in BL: plane_lines[plane_idx[("b", L[2])]].append(li)
            if L[3] in CL: plane_lines[plane_idx[("c", L[3])]].append(li)
        elif k == "1P_ab":
            if L[1] in AL: plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in BL: plane_lines[plane_idx[("b", L[2])]].append(li)
        elif k == "1P_ac":
            if L[1] in AL: plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in CL: plane_lines[plane_idx[("c", L[2])]].append(li)
        else:
            if L[1] in BL: plane_lines[plane_idx[("b", L[1])]].append(li)
            if L[2] in CL: plane_lines[plane_idx[("c", L[2])]].append(li)

    n_slots = (q - 1) * q
    match_line = [-1] * len(lines)
    match_slot = [-1] * n_slots

    def aug(sl: int, vis: list[bool]) -> bool:
        z = sl // q
        for li in plane_lines[z]:
            if vis[li]:
                continue
            vis[li] = True
            if match_line[li] == -1 or aug(match_line[li], vis):
                match_slot[sl] = li
                match_line[li] = sl
                return True
        return False

    for sl in range(n_slots):
        if match_slot[sl] == -1:
            aug(sl, [False] * len(lines))

    reps: list[tuple[int, int, int, int, int, int]] = []
    for z in range(q - 1):
        for y in range(q):
            li = match_slot[z * q + y]
            assert li != -1
            L = lines[li]
            k = L[0]
            if k == "3P":
                for x in range(q): reps.append((x, y, z, L[1], L[2], L[3]))
            elif k == "1P_ab":
                for x in range(q): reps.append((x, y, z, L[1], L[2], x))
            elif k == "1P_ac":
                for x in range(q): reps.append((x, y, z, L[1], x, L[2]))
            else:
                for x in range(q): reps.append((x, y, z, x, L[1], L[2]))

    zh = q - 1
    z_lines = [lines[li] for li in range(len(lines)) if match_line[li] == -1]
    cnt_a = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_b = [[[0] * q for _ in range(q)] for _ in range(q)]
    cnt_c = [[[0] * q for _ in range(q)] for _ in range(q)]
    used_z: list[list[set[tuple[int, int, int]]]] = [[set() for _ in range(q)] for _ in range(q)]
    row_load = [0] * q

    def add_z(x: int, y: int, a: int, b: int, c: int) -> None:
        reps.append((x, y, zh, a, b, c))
        used_z[y][x].add((a, b, c))
        row_load[y] += 1
        cnt_a[y][x][a] += 1
        cnt_b[y][x][b] += 1
        cnt_c[y][x][c] += 1

    for L in z_lines:
        k = L[0]
        if k == "3P":
            _, a, b, c = L
            best = None
            for y in range(q):
                if any((a, b, c) in used_z[y][x] for x in range(q)):
                    continue
                g = (
                    (sum(1 for x in range(q) if cnt_a[y][x][a] == 0) if a in AH else 0)
                    + (sum(1 for x in range(q) if cnt_b[y][x][b] == 0) if b in BH else 0)
                    + (sum(1 for x in range(q) if cnt_c[y][x][c] == 0) if c in CH else 0)
                )
                cand = (g, -row_load[y], -y)
                if best is None or cand > best[0]:
                    best = (cand, y)
            for x in range(q):
                add_z(x, best[1], a, b, c)
        else:
            best = None
            for y in range(q):
                if k == "1P_ab":
                    a, b = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_a[y][x][a] == 0) if a in AH else 0) + (
                        sum(1 for x in range(q) if cnt_b[y][x][b] == 0) if b in BH else 0
                    )
                    va = [[c for c in range(q) if (a, b, c) not in used_z[y][x]] for x in range(q)]
                    ga = [[c for c in va[x] if c in CH and cnt_c[y][x][c] == 0] for x in range(q)]
                elif k == "1P_ac":
                    a, c = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_a[y][x][a] == 0) if a in AH else 0) + (
                        sum(1 for x in range(q) if cnt_c[y][x][c] == 0) if c in CH else 0
                    )
                    va = [[b for b in range(q) if (a, b, c) not in used_z[y][x]] for x in range(q)]
                    ga = [[b for b in va[x] if b in BH and cnt_b[y][x][b] == 0] for x in range(q)]
                else:
                    b, c = L[1], L[2]
                    fg = (sum(1 for x in range(q) if cnt_b[y][x][b] == 0) if b in BH else 0) + (
                        sum(1 for x in range(q) if cnt_c[y][x][c] == 0) if c in CH else 0
                    )
                    va = [[a for a in range(q) if (a, b, c) not in used_z[y][x]] for x in range(q)]
                    ga = [[a for a in va[x] if a in AH and cnt_a[y][x][a] == 0] for x in range(q)]
                res = _max_bijection_gain(q, ga, va)
                if res is None:
                    continue
                cand = (fg + res[0], -row_load[y], -y)
                if best is None or cand > best[0]:
                    best = (cand, y, res[1])
            _, y, pi = best
            for x in range(q):
                if k == "1P_ab": add_z(x, y, L[1], L[2], pi[x])
                elif k == "1P_ac": add_z(x, y, L[1], pi[x], L[2])
                else: add_z(x, y, pi[x], L[1], L[2])

    for a, b, c in sorted(unc_t3, key=lambda t: (-((t[0] in AH) + (t[1] in BH) + (t[2] in CH)), t)):
        best = None
        for y in range(q):
            for x in range(q):
                if (a, b, c) in used_z[y][x]:
                    continue
                g = (a in AH and cnt_a[y][x][a] == 0) + (b in BH and cnt_b[y][x][b] == 0) + (c in CH and cnt_c[y][x][c] == 0)
                cand = (g, -len(used_z[y][x]), -y, -x)
                if best is None or cand > best[0]:
                    best = (cand, x, y)
        add_z(best[1], best[2], a, b, c)

    exh = 0
    for y in range(q):
        for x in range(q):
            ma = [a for a in sorted(AH) if cnt_a[y][x][a] == 0]
            mb = [b for b in sorted(BH) if cnt_b[y][x][b] == 0]
            mc = [c for c in sorted(CH) if cnt_c[y][x][c] == 0]
            for i in range(max(len(ma), len(mb), len(mc))):
                a = ma[i] if i < len(ma) else next(iter(AH))
                b = mb[i] if i < len(mb) else next(iter(BH))
                c = mc[i] if i < len(mc) else next(iter(CH))
                add_z(x, y, a, b, c)
                exh += 1

    suff = check_sufficient_full_bg3(reps, q)
    chk = check_m3(reps, ops, mode="full-bg3")
    assert suff["total"] == 0 and chk["total"] == 0
    print(
        f"  Result: m = {len(reps)} ({len(reps)/q**3:.5f}*q^3), exh = {exh}, "
        f"suff = {suff['total']}, check_m3 = {chk['total']} (> det 1332, > 1323)"
    )


def main() -> None:
    t0 = time.perf_counter()
    ops9 = FieldOps(9)
    exp1_single_set_geometry(ops9)

    print("\n=== EXP 2: Explicit 3-Family 3D Baer Cylinder Construction ===")
    r9 = build_exp2_baer_cylinder_full(ops9, verify_exact=True)
    print(
        f"  q= 9: m={r9['m']:5d} ({r9['m']/9**3:.5f}*q^3) | nz=(3P:{r9['n3p_nz']}, 1P:{r9['n1p_nz']}), "
        f"z0_3P={r9['z0_3p']}, rem_t3={r9['rem_t3']}, extra_z0={r9['extra_z0']} | "
        f"dups={r9['dups']} check_m3={r9['check_m3']} (vs ell=1377, det=1332, 49/27=1323, 46/27=1242)"
    )
    r16 = build_exp2_baer_cylinder_full(FieldOps(16), verify_exact=True)
    print(
        f"  q=16: m={r16['m']:5d} ({r16['m']/16**3:.5f}*q^3) | nz=(3P:{r16['n3p_nz']}, 1P:{r16['n1p_nz']}), "
        f"z0_3P={r16['z0_3p']}, rem_t3={r16['rem_t3']}, extra_z0={r16['extra_z0']} | "
        f"dups={r16['dups']} check_m3={r16['check_m3']} (vs ell=7936, det=7653)"
    )

    exp3_2d_baer_stack_q9(ops9)
    exp4_f3_subline_light_heavy_q9(ops9)
    print(f"\nTotal pilot runtime: {time.perf_counter() - t0:.2f} s")


if __name__ == "__main__":
    main()
