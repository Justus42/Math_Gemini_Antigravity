#!/usr/bin/env python3
r"""Phase 9 / PR #54 (Option C): Discrete Realizability Prototype & Obstruction Diagnosis
for the H_2P_L_HH Construction (Aggregate LP_2P_no3PLL = 143/81 = 1.765432 q^3).

Pure Python (std-only) + FieldOps / check_m3 from scripts/phase9_m3_lift.py.
Zero randomness.

This script performs three exact, reproducible checks:
  1. Exact Rational LP Analysis (Two-Phase Fraction Simplex):
       - Reproduces aggregate LP1 = 46/27, LP_49a = 49/27, LP_2P = 1885/1107, LP_2P_no3PLL = 143/81.
       - Enforces the exact row-level heavy multiplicity constraint on z* (Obstruction 1):
           * Unrestricted row-coupled LP collapses from 1885/1107 back to 46/27 (H_2P = 0).
           * No-3P-in-LLL/LLH row-coupled LP rises from 143/81 (1.7654) to 1879/1053 (1.7844).
           * Half-size s = 1/3 (zero heavy overlap) collapses identically to 49/27 (H_2P = 0).
       - Enforces a conservative HHH 3-cylinder overlap cap (1/2 instead of 2/3, Obstruction 2):
           * Row-coupled no-3P-in-LLL/LLH LP rises straight back to 49/27 (1.8148).
       - Enforces light-plane starvation padding (Obstruction 3: pad >= 1/3 per full-size H_2P sym):
           * Row-coupled no-3P-in-LLL/LLH LP collapses identically to 49/27 (H_2P = 0).
  2. Explicit Discrete Finite-q H_2P_L_HH Constructor (q = 7, 8, 9, 11, 13, ...):
       - Tests r2p = 0 (control), full-size s = 2/3 (single / pair2 / triple3 row packing),
         and disjoint half-size s = 1/3 (triple3).
       - Reports exact pre-closure skeleton size + check_m3 by_type = (Typ0, Typ1, Typ2, Typ3),
         and exact closed check_m3 = 0 size with (2P, pad, u_LHH, u_HHH, exh) breakdown.
  3. Exact Typ-2 Failure Check for Placing Spread H_2P_a on Light Plane z(a_0):
       - Demonstrates that spreading (a_0, b_u, c_{(u+x) mod h}) across distinct rows y = u on
         z(a_0) fails Typ 2 at normal al = 1 (and other linear combinations).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase9_m3_construct import _max_bijection_gain  # noqa: E402
from phase9_m3_lift import FieldOps, check_m3  # noqa: E402


# ---------- Part 1: Exact Rational Simplex ----------


def solve_lp_exact(
    c: list[Fraction],
    A_ge: list[list[Fraction]],
    b_ge: list[Fraction],
    A_eq: list[list[Fraction]] | None = None,
    b_eq: list[Fraction] | None = None,
) -> tuple[Fraction | None, list[Fraction] | None]:
    """Minimize c^T x s.t. A_ge x >= b_ge, A_eq x == b_eq, x >= 0 (exact Fraction two-phase simplex)."""
    n = len(c)
    n_ge = len(A_ge)
    n_eq = len(A_eq) if A_eq else 0
    m = n_ge + n_eq
    total_vars = n + n_ge + m
    T: list[list[Fraction]] = []
    basis: list[int] = []

    for i in range(n_ge):
        row = [Fraction(v) for v in A_ge[i]] + [Fraction(0)] * n_ge + [Fraction(0)] * m + [Fraction(b_ge[i])]
        if row[-1] < 0:
            row = [-v for v in row]
            row[n + i] = Fraction(1)
        else:
            row[n + i] = Fraction(-1)
        row[n + n_ge + i] = Fraction(1)
        T.append(row)
        basis.append(n + n_ge + i)

    if A_eq and b_eq:
        for j in range(n_eq):
            row = [Fraction(v) for v in A_eq[j]] + [Fraction(0)] * n_ge + [Fraction(0)] * m + [Fraction(b_eq[j])]
            if row[-1] < 0:
                row = [-v for v in row]
            row[n + n_ge + n_ge + j] = Fraction(1)
            T.append(row)
            basis.append(n + n_ge + n_ge + j)

    def run_simplex(tab: list[list[Fraction]], bas: list[int], cost_vec: list[Fraction]) -> Fraction | None:
        mm = len(tab)
        nv = len(cost_vec)
        rc = [Fraction(v) for v in cost_vec] + [Fraction(0)]
        for i in range(mm):
            cb = cost_vec[bas[i]]
            if cb != 0:
                for j in range(nv + 1):
                    rc[j] -= cb * tab[i][j]
        while True:
            enter = next((j for j in range(nv) if rc[j] < 0), -1)
            if enter == -1:
                break
            leave = -1
            best_ratio: Fraction | None = None
            for i in range(mm):
                a = tab[i][enter]
                if a > 0:
                    ratio = tab[i][nv] / a
                    if best_ratio is None or ratio < best_ratio or (ratio == best_ratio and bas[i] < bas[leave]):
                        best_ratio = ratio
                        leave = i
            if leave == -1:
                return None
            piv = tab[leave][enter]
            tab[leave] = [v / piv for v in tab[leave]]
            for i in range(mm):
                if i != leave and tab[i][enter] != 0:
                    f = tab[i][enter]
                    tab[i] = [tab[i][j] - f * tab[leave][j] for j in range(nv + 1)]
            if rc[enter] != 0:
                f = rc[enter]
                rc = [rc[j] - f * tab[leave][j] for j in range(nv + 1)]
            bas[leave] = enter
        return -rc[nv]

    if run_simplex(T, basis, [Fraction(0)] * (n + n_ge) + [Fraction(1)] * m) != 0:
        return None, None

    nv_orig = n + n_ge
    for i in range(m):
        if basis[i] >= nv_orig:
            col = next((j for j in range(nv_orig) if T[i][j] != 0), -1)
            if col != -1:
                piv = T[i][col]
                T[i] = [v / piv for v in T[i]]
                for k in range(m):
                    if k != i and T[k][col] != 0:
                        f = T[k][col]
                        T[k] = [T[k][j] - f * T[i][j] for j in range(total_vars + 1)]
                basis[i] = col

    T2: list[list[Fraction]] = []
    basis2: list[int] = []
    for i in range(m):
        if basis[i] < nv_orig:
            T2.append(T[i][:nv_orig] + [T[i][-1]])
            basis2.append(basis[i])

    opt = run_simplex(T2, basis2, [Fraction(v) for v in c] + [Fraction(0)] * n_ge)
    x = [Fraction(0)] * n
    for i, b in enumerate(basis2):
        if b < n:
            x[b] = T2[i][-1]
    return opt, x


def run_lp_suite() -> None:
    """Run exact rational LP comparisons isolating Obstructions 1, 2, and 3."""
    print("=== PART 1: EXACT RATIONAL LP DIAGNOSIS (OBSTRUCTIONS 1, 2, 3) ===")

    def solve_row_coupled(
        label: str,
        allow_3p_ll: bool,
        hhh_cap: Fraction = Fraction(2, 3),
        enforce_light_pad: bool = False,
        only_half: bool = False,
    ) -> None:
        names = [
            "L_3LLL", "L_3LLH", "L_3LHH", "L_1LL", "L_1LH", "L_0LLL", "L_0LLH", "L_0LHH",
            "H_3LLL", "H_3LLH", "H_3LHH", "H_3HHH", "H_1LL", "H_1LH", "H_1HH",
            "H_0LLL", "H_0LLH", "H_0LHH", "H_0HHH",
            "F_3LLH", "F_3LHH", "F_3HHH", "F_1LL", "F_1LH", "F_1HH", "F_0LLH", "F_0LHH", "F_0HHH",
            "f_N", "f_1", "f_2", "f_3", "f_half",
        ]
        idx = {k: i for i, k in enumerate(names)}
        n = len(names)
        # Cost of full-size H_2P rows:
        #   f_1: (2/3) on z* (+ optional (1/3) mandatory dummy padding on light plane z(a_0) -> 1!)
        #   f_2: (4/3) on z* (+ optional (2/3) mandatory dummy padding on light planes -> 2!)
        #   f_3: (2) on z*   (+ optional (1) mandatory dummy padding on light planes -> 3!)
        #   f_half: 1 on z*  (0 mandatory light-plane padding because half of B_H, C_H remain free!)
        pad_add = Fraction(1, 3) if enforce_light_pad else Fraction(0)
        c = [Fraction(1)] * n
        c[idx["f_N"]] = Fraction(0)
        c[idx["f_1"]] = Fraction(2, 3) + pad_add
        c[idx["f_2"]] = Fraction(4, 3) + 2 * pad_add
        c[idx["f_3"]] = Fraction(2) + 3 * pad_add
        c[idx["f_half"]] = Fraction(1)

        A_ge: list[list[Fraction]] = []
        b_ge: list[Fraction] = []
        A_eq: list[list[Fraction]] = []
        b_eq: list[Fraction] = []

        def row(d: dict[str, int | Fraction]) -> list[Fraction]:
            r = [Fraction(0)] * n
            for k, v in d.items():
                r[idx[k]] = Fraction(v)
            return r

        A_eq.append(row({"f_N": 1, "f_1": 1, "f_2": 1, "f_3": 1, "f_half": 1}))
        b_eq.append(Fraction(1))

        # Light plane total >= 1 (note: if enforce_light_pad, dummy padding already sits on z(a_0)
        # taking (1/3)*f_1 + (2/3)*f_2 + 1*f_3 of the 1 unit of light-plane capacity, so non-dummy L_*
        # only needs to fill 1 - pad_slots! Wait: total light-plane cost is STILL >= 1, and non-dummy
        # L_* + pad_slots >= 1, so adding pad_add to c[f_i] AND subtracting pad_add from Light RHS
        # models that exact conservation: L_* + (1/3)*f_1 + (2/3)*f_2 + f_3 >= 1, with pad costing 1 each!)
        if enforce_light_pad:
            A_ge.append(row({k: 1 for k in names if k.startswith("L_")} | {"f_1": Fraction(1, 3), "f_2": Fraction(2, 3), "f_3": 1}))
        else:
            A_ge.append(row({k: 1 for k in names if k.startswith("L_")}))
        b_ge.append(Fraction(1))

        # Normal rows on z*: heavy >= 2*f_N and count >= (2/3)*f_N
        A_ge.append(row({
            "H_3LLH": 1, "H_3LHH": 2, "H_3HHH": 3,
            "H_1LL": Fraction(2, 3), "H_1LH": Fraction(5, 3), "H_1HH": Fraction(8, 3),
            "H_0LLH": 1, "H_0LHH": 2, "H_0HHH": 3, "f_N": -2,
        }))
        b_ge.append(Fraction(0))
        A_ge.append(row({k: 1 for k in names if k.startswith("H_")} | {"f_N": Fraction(-2, 3)}))
        b_ge.append(Fraction(0))

        # 1-block H_2P rows filler: missing coordinate >= (2/3)*f_1
        A_ge.append(row({
            "F_3LLH": 1, "F_3LHH": 1, "F_3HHH": 1, "F_1LL": Fraction(2, 3), "F_1LH": 1, "F_1HH": 1,
            "F_0LLH": 1, "F_0LHH": 1, "F_0HHH": 1, "f_1": Fraction(-2, 3),
        }))
        b_ge.append(Fraction(0))

        # Pairs: LL >= 1/3, LH >= 4/3, HH >= 4/3
        A_ge.append(row({"L_3LLL": 3, "L_3LLH": 1, "L_1LL": 1, "H_3LLL": 3, "H_3LLH": 1, "H_1LL": 1, "F_3LLH": 1, "F_1LL": 1}))
        b_ge.append(Fraction(1, 3))
        A_ge.append(row({
            "L_3LLH": 2, "L_3LHH": 2, "L_1LH": 1, "H_3LLH": 2, "H_3LHH": 2, "H_1LH": 1,
            "F_3LLH": 2, "F_3LHH": 2, "F_1LH": 1,
            "f_1": Fraction(4, 3), "f_2": Fraction(8, 3), "f_3": 4, "f_half": 2,
        }))
        b_ge.append(Fraction(4, 3))
        A_ge.append(row({"L_3LHH": 1, "H_3LHH": 1, "H_3HHH": 3, "H_1HH": 1, "F_3LHH": 1, "F_3HHH": 3, "F_1HH": 1}))
        b_ge.append(Fraction(4, 3))

        # Triples: LLL >= 1/27, LLH >= 2/9, LHH >= 4/9, HHH >= 8/27
        A_ge.append(row({"L_1LL": Fraction(1, 3), "H_1LL": Fraction(1, 3), "F_1LL": Fraction(1, 3), "L_0LLL": 1, "H_0LLL": 1}))
        b_ge.append(Fraction(1, 27))
        A_ge.append(row({
            "L_1LL": Fraction(2, 3), "H_1LL": Fraction(2, 3), "F_1LL": Fraction(2, 3),
            "L_1LH": Fraction(1, 3), "H_1LH": Fraction(1, 3), "F_1LH": Fraction(1, 3),
            "L_0LLH": 1, "H_0LLH": 1, "F_0LLH": 1,
        }))
        b_ge.append(Fraction(2, 9))
        A_ge.append(row({
            "L_1LH": Fraction(2, 3), "H_1LH": Fraction(2, 3), "F_1LH": Fraction(2, 3),
            "H_1HH": Fraction(1, 3), "F_1HH": Fraction(1, 3),
            "L_0LHH": 1, "H_0LHH": 1, "F_0LHH": 1,
            "f_1": Fraction(4, 9), "f_2": Fraction(8, 9), "f_3": Fraction(4, 3), "f_half": Fraction(1, 3),
        }))
        b_ge.append(Fraction(4, 9))
        A_ge.append(row({"H_1HH": hhh_cap, "F_1HH": hhh_cap, "H_0HHH": 1, "F_0HHH": 1}))
        b_ge.append(Fraction(8, 27))

        if not allow_3p_ll:
            for k in ("L_3LLL", "L_3LLH", "H_3LLL", "H_3LLH", "F_3LLH"):
                A_eq.append(row({k: 1}))
                b_eq.append(Fraction(0))
        if only_half:
            for k in ("f_1", "f_2", "f_3"):
                A_eq.append(row({k: 1}))
                b_eq.append(Fraction(0))

        opt, x = solve_lp_exact(c, A_ge, b_ge, A_eq, b_eq)
        assert opt is not None and x is not None
        h2p_vol = Fraction(2, 3) * x[idx["f_1"]] + Fraction(4, 3) * x[idx["f_2"]] + 2 * x[idx["f_3"]] + x[idx["f_half"]]
        print(f"  {label:56s}: OPT = {str(opt):10s} = {float(opt):.6f} | H_2P_vol = {str(h2p_vol):8s}")

    solve_row_coupled("Row-exact unrestricted (refutes 1885/1107 artifact!)", allow_3p_ll=True)
    solve_row_coupled("Row-exact no-3P-LL (Obstruction 1: 143/81 -> 1879/1053)", allow_3p_ll=False)
    solve_row_coupled("Row-exact no-3P-LL, half-size s=1/3 only", allow_3p_ll=False, only_half=True)
    solve_row_coupled("Row-exact no-3P-LL + HHH cap 1/2 (Obstruction 2)", allow_3p_ll=False, hhh_cap=Fraction(1, 2))
    solve_row_coupled("Row-exact no-3P-LL + light-plane pad (Obstruction 3)", allow_3p_ll=False, enforce_light_pad=True)


# ---------- Part 2: Explicit Finite-q H_2P_L_HH Constructor ----------


def build_h2plhh_discrete(
    q: int,
    r2p: int,
    half_size: bool = False,
    pack: str = "pair2",
    f3: float = 0.35,
) -> tuple[list[tuple[int, int, int, int, int, int]], list[tuple[int, int, int, int, int, int]], dict[str, int]]:
    """Deterministic finite-q H_2P_L_HH construction returning (reps_skeleton, reps_closed, stats)."""
    ka = (q - 1 + 2) // 3
    kb = (q - 1 + 1) // 3
    kc = (q - 1) // 3
    AL, BL, CL = list(range(ka)), list(range(kb)), list(range(kc))
    AH, BH, CH = list(range(ka, q)), list(range(kb, q)), list(range(kc, q))
    ha, hb, hc = len(AH), len(BH), len(CH)
    AL_s, BL_s, CL_s = set(AL), set(BL), set(CL)
    AH_s, BH_s, CH_s = set(AH), set(BH), set(CH)

    r2p = min(r2p, ka, kb, kc)
    AL1, BL1, CL1 = AL[:r2p], BL[:r2p], CL[:r2p]

    E_ab = [[False] * q for _ in range(q)]
    E_ac = [[False] * q for _ in range(q)]
    E_bc = [[False] * q for _ in range(q)]
    cov_t = [[[False] * q for _ in range(q)] for _ in range(q)]

    z_star = q - 1
    AH_idx = {a: i for i, a in enumerate(AH)}
    BH_idx = {b: i for i, b in enumerate(BH)}
    CH_idx = {c: i for i, c in enumerate(CH)}
    cnt_a = [[[0] * ha for _ in range(q)] for _ in range(q)]
    cnt_b = [[[0] * hb for _ in range(q)] for _ in range(q)]
    cnt_c = [[[0] * hc for _ in range(q)] for _ in range(q)]
    used_zstar: set[tuple[int, int, int, int, int]] = set()

    def add_zstar(x: int, y: int, a: int, b: int, c: int) -> bool:
        if (x, y, a, b, c) in used_zstar:
            return False
        used_zstar.add((x, y, a, b, c))
        cov_t[a][b][c] = True
        if a in AH_idx:
            cnt_a[x][y][AH_idx[a]] += 1
        if b in BH_idx:
            cnt_b[x][y][BH_idx[b]] += 1
        if c in CH_idx:
            cnt_c[x][y][CH_idx[c]] += 1
        return True

    reps_2p: list[tuple[int, int, int, int, int, int]] = []
    if half_size and r2p > 0:
        AH1, AH2 = AH[: ha // 2], AH[ha // 2 :]
        BH1, BH2 = BH[: hb // 2], BH[hb // 2 :]
        CH1, CH2 = CH[: hc // 2], CH[hc // 2 :]
        for i in range(r2p):
            y = i % q
            for u in range(max(len(BH1), len(CH1))):
                b = BH1[u % len(BH1)]
                for x in range(q):
                    c = CH1[(u + x) % len(CH1)]
                    if add_zstar(x, y, AL1[i], b, c):
                        reps_2p.append((x, y, z_star, AL1[i], b, c))
            for b in BH1:
                E_ab[AL1[i]][b] = True
            for c in CH1:
                E_ac[AL1[i]][c] = True

            for u in range(max(len(AH1), len(CH2))):
                a = AH1[u % len(AH1)]
                for x in range(q):
                    c = CH2[(u + x) % len(CH2)]
                    if add_zstar(x, y, a, BL1[i], c):
                        reps_2p.append((x, y, z_star, a, BL1[i], c))
            for a in AH1:
                E_ab[a][BL1[i]] = True
            for c in CH2:
                E_bc[BL1[i]][c] = True

            for u in range(max(len(AH2), len(BH2))):
                a = AH2[u % len(AH2)]
                for x in range(q):
                    b = BH2[(u + x) % len(BH2)]
                    if add_zstar(x, y, a, b, CL1[i]):
                        reps_2p.append((x, y, z_star, a, b, CL1[i]))
            for a in AH2:
                E_ac[a][CL1[i]] = True
            for b in BH2:
                E_bc[b][CL1[i]] = True
    else:
        blocks_2p: list[tuple[str, int]] = []
        for i in range(r2p):
            blocks_2p.extend([("a", AL1[i]), ("b", BL1[i]), ("c", CL1[i])])
        for bi, (ch, sym) in enumerate(blocks_2p):
            y = bi % q if pack == "single" else ((bi // 2) % q if pack == "pair2" else (bi // 3) % q)
            if ch == "a":
                for u in range(max(hb, hc)):
                    b = BH[u % hb]
                    for x in range(q):
                        c = CH[(u + x) % hc]
                        if add_zstar(x, y, sym, b, c):
                            reps_2p.append((x, y, z_star, sym, b, c))
                for b in BH:
                    E_ab[sym][b] = True
                for c in CH:
                    E_ac[sym][c] = True
            elif ch == "b":
                for u in range(max(ha, hc)):
                    a = AH[u % ha]
                    for x in range(q):
                        c = CH[(u + x) % hc]
                        if add_zstar(x, y, a, sym, c):
                            reps_2p.append((x, y, z_star, a, sym, c))
                for a in AH:
                    E_ab[a][sym] = True
                for c in CH:
                    E_bc[sym][c] = True
            else:
                for u in range(max(ha, hb)):
                    a = AH[u % ha]
                    for x in range(q):
                        b = BH[(u + x) % hb]
                        if add_zstar(x, y, a, b, sym):
                            reps_2p.append((x, y, z_star, a, b, sym))
                for a in AH:
                    E_ac[a][sym] = True
                for b in BH:
                    E_bc[b][sym] = True

    lines: list[tuple] = []
    for a in AL:
        for b in BL:
            lines.append(("1P_ab", a, b))
            E_ab[a][b] = True
            for c in range(q):
                cov_t[a][b][c] = True
    for a in AL:
        for c in CL:
            lines.append(("1P_ac", a, c))
            E_ac[a][c] = True
            for b in range(q):
                cov_t[a][b][c] = True
    for b in BL:
        for c in CL:
            lines.append(("1P_bc", b, c))
            E_bc[b][c] = True
            for a in range(q):
                cov_t[a][b][c] = True

    for ia, a in enumerate(AL):
        for u in range(min(hb, hc)):
            b, c = BH[u], CH[(u + ia) % hc]
            if not E_ab[a][b] and not E_ac[a][c] and not E_bc[b][c]:
                lines.append(("3P", a, b, c))
                E_ab[a][b] = E_ac[a][c] = E_bc[b][c] = True
                cov_t[a][b][c] = True
    for ib, b in enumerate(BL):
        for u in range(min(ha, hc)):
            a, c = AH[u], CH[(u + ib) % hc]
            if not E_ab[a][b] and not E_ac[a][c] and not E_bc[b][c]:
                lines.append(("3P", a, b, c))
                E_ab[a][b] = E_ac[a][c] = E_bc[b][c] = True
                cov_t[a][b][c] = True
    for ic, c in enumerate(CL):
        for u in range(min(ha, hb)):
            a, b = AH[u], BH[(u + ic) % hb]
            if not E_ab[a][b] and not E_ac[a][c] and not E_bc[b][c]:
                lines.append(("3P", a, b, c))
                E_ab[a][b] = E_ac[a][c] = E_bc[b][c] = True
                cov_t[a][b][c] = True

    for a in AL:
        for b in BH:
            if not E_ab[a][b]:
                lines.append(("1P_ab", a, b))
                E_ab[a][b] = True
                for c in range(q):
                    cov_t[a][b][c] = True
        for c in CH:
            if not E_ac[a][c]:
                lines.append(("1P_ac", a, c))
                E_ac[a][c] = True
                for b in range(q):
                    cov_t[a][b][c] = True
    for b in BL:
        for a in AH:
            if not E_ab[a][b]:
                lines.append(("1P_ab", a, b))
                E_ab[a][b] = True
                for c in range(q):
                    cov_t[a][b][c] = True
        for c in CH:
            if not E_bc[b][c]:
                lines.append(("1P_bc", b, c))
                E_bc[b][c] = True
                for a in range(q):
                    cov_t[a][b][c] = True
    for c in CL:
        for a in AH:
            if not E_ac[a][c]:
                lines.append(("1P_ac", a, c))
                E_ac[a][c] = True
                for b in range(q):
                    cov_t[a][b][c] = True
        for b in BH:
            if not E_bc[b][c]:
                lines.append(("1P_bc", b, c))
                E_bc[b][c] = True
                for a in range(q):
                    cov_t[a][b][c] = True

    n3_hhh = 0
    tgt = round(f3 * ha * hb)
    for ia in range(ha):
        for ib in range(hb):
            if n3_hhh >= tgt:
                break
            a, b = AH[ia], BH[ib]
            if E_ab[a][b]:
                continue
            c = CH[(-ia - ib) % hc]
            if not E_ac[a][c] and not E_bc[b][c]:
                lines.append(("3P", a, b, c))
                E_ab[a][b] = E_ac[a][c] = E_bc[b][c] = True
                cov_t[a][b][c] = True
                n3_hhh += 1

    for a in AH:
        for b in BH:
            if not E_ab[a][b]:
                lines.append(("1P_ab", a, b))
                E_ab[a][b] = True
                for c in range(q):
                    cov_t[a][b][c] = True
        for c in CH:
            if not E_ac[a][c]:
                lines.append(("1P_ac", a, c))
                E_ac[a][c] = True
                for b in range(q):
                    cov_t[a][b][c] = True
    for b in BH:
        for c in CH:
            if not E_bc[b][c]:
                lines.append(("1P_bc", b, c))
                E_bc[b][c] = True
                for a in range(q):
                    cov_t[a][b][c] = True

    unc_lhh = [
        (a, b, c)
        for a in range(q)
        for b in range(q)
        for c in range(q)
        if not cov_t[a][b][c] and not (a in AH_s and b in BH_s and c in CH_s)
    ]
    unc_hhh = [(a, b, c) for a in AH for b in BH for c in CH if not cov_t[a][b][c]]
    unc_all = unc_lhh + unc_hhh

    plane_owner = [("a", a) for a in AL] + [("b", b) for b in BL] + [("c", c) for c in CL]
    plane_idx = {o: i for i, o in enumerate(plane_owner)}

    def heavy_val(L: tuple) -> int:
        k = L[0]
        if k == "3P":
            return 3 * ((L[1] in AH_s) + (L[2] in BH_s) + (L[3] in CH_s))
        if k == "1P_ab":
            return 3 * ((L[1] in AH_s) + (L[2] in BH_s)) + 2
        if k == "1P_ac":
            return 3 * ((L[1] in AH_s) + (L[2] in CH_s)) + 2
        return 3 * ((L[1] in BH_s) + (L[2] in CH_s)) + 2

    lines.sort(key=lambda L: (heavy_val(L), L))
    plane_lines: list[list[int]] = [[] for _ in range(q - 1)]
    for li, L in enumerate(lines):
        k = L[0]
        if k == "3P":
            if L[1] in AL_s:
                plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in BL_s:
                plane_lines[plane_idx[("b", L[2])]].append(li)
            if L[3] in CL_s:
                plane_lines[plane_idx[("c", L[3])]].append(li)
        elif k == "1P_ab":
            if L[1] in AL_s:
                plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in BL_s:
                plane_lines[plane_idx[("b", L[2])]].append(li)
        elif k == "1P_ac":
            if L[1] in AL_s:
                plane_lines[plane_idx[("a", L[1])]].append(li)
            if L[2] in CL_s:
                plane_lines[plane_idx[("c", L[2])]].append(li)
        else:
            if L[1] in BL_s:
                plane_lines[plane_idx[("b", L[1])]].append(li)
            if L[2] in CL_s:
                plane_lines[plane_idx[("c", L[2])]].append(li)

    n_slots = (q - 1) * q
    match_line = [-1] * len(lines)
    match_slot = [-1] * n_slots
    for z in range(q - 1):
        sp = 0
        for li in plane_lines[z]:
            if match_line[li] == -1:
                match_slot[z * q + sp] = li
                match_line[li] = z * q + sp
                sp += 1
                if sp == q:
                    break

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

    reps_light: list[tuple[int, int, int, int, int, int]] = []
    used_unc = [False] * len(unc_all)
    unc_by: dict[str, dict[int, list[int]]] = {"a": defaultdict(list), "b": defaultdict(list), "c": defaultdict(list)}
    for i, (a, b, c) in enumerate(unc_all):
        unc_by["a"][a].append(i)
        unc_by["b"][b].append(i)
        unc_by["c"][c].append(i)

    pad = 0
    for z in range(q - 1):
        ch, sym = plane_owner[z]
        for y in range(q):
            li = match_slot[z * q + y]
            if li != -1:
                L = lines[li]
                k = L[0]
                if k == "3P":
                    for x in range(q):
                        reps_light.append((x, y, z, L[1], L[2], L[3]))
                elif k == "1P_ab":
                    for x in range(q):
                        reps_light.append((x, y, z, L[1], L[2], x))
                elif k == "1P_ac":
                    for x in range(q):
                        reps_light.append((x, y, z, L[1], x, L[2]))
                else:
                    for x in range(q):
                        reps_light.append((x, y, z, x, L[1], L[2]))
            else:
                picked: list[tuple[int, int, int]] = []
                for idx in unc_by[ch][sym]:
                    if not used_unc[idx]:
                        used_unc[idx] = True
                        picked.append(unc_all[idx])
                        if len(picked) == q:
                            break
                while len(picked) < q:
                    pad += 1
                    picked.append((sym, 0, 0) if ch == "a" else ((0, sym, 0) if ch == "b" else (0, 0, sym)))
                for x, (a, b, c) in enumerate(picked):
                    reps_light.append((x, y, z, a, b, c))

    rem_lines = [lines[li] for li in range(len(lines)) if match_line[li] == -1]
    reps_hlines: list[tuple[int, int, int, int, int, int]] = []
    for L in rem_lines:
        k = L[0]
        if k == "3P":
            _, a, b, c = L
            ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
            best_y, best_g = 0, -1
            for y in range(q):
                g = sum(
                    (ai != -1 and cnt_a[x][y][ai] == 0)
                    + (bi != -1 and cnt_b[x][y][bi] == 0)
                    + (ci != -1 and cnt_c[x][y][ci] == 0)
                    for x in range(q)
                )
                if g > best_g:
                    best_g, best_y = g, y
            for x in range(q):
                if add_zstar(x, best_y, a, b, c):
                    reps_hlines.append((x, best_y, z_star, a, b, c))
        else:
            best_y, best_g, best_pi = 0, -1, list(range(q))
            for y in range(q):
                gain_adj: list[list[int]] = [[] for _ in range(q)]
                valid_adj: list[list[int]] = [[] for _ in range(q)]
                bg = 0
                if k == "1P_ab":
                    _, a, b = L
                    ai, bi = AH_idx.get(a, -1), BH_idx.get(b, -1)
                    for x in range(q):
                        if ai != -1 and cnt_a[x][y][ai] == 0:
                            bg += 1
                        if bi != -1 and cnt_b[x][y][bi] == 0:
                            bg += 1
                        for c in range(q):
                            if (x, y, a, b, c) in used_zstar:
                                continue
                            valid_adj[x].append(c)
                            ci = CH_idx.get(c, -1)
                            if ci != -1 and cnt_c[x][y][ci] == 0:
                                gain_adj[x].append(c)
                elif k == "1P_ac":
                    _, a, c = L
                    ai, ci = AH_idx.get(a, -1), CH_idx.get(c, -1)
                    for x in range(q):
                        if ai != -1 and cnt_a[x][y][ai] == 0:
                            bg += 1
                        if ci != -1 and cnt_c[x][y][ci] == 0:
                            bg += 1
                        for b in range(q):
                            if (x, y, a, b, c) in used_zstar:
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
                            bg += 1
                        if ci != -1 and cnt_c[x][y][ci] == 0:
                            bg += 1
                        for a in range(q):
                            if (x, y, a, b, c) in used_zstar:
                                continue
                            valid_adj[x].append(a)
                            ai = AH_idx.get(a, -1)
                            if ai != -1 and cnt_a[x][y][ai] == 0:
                                gain_adj[x].append(a)
                res = _max_bijection_gain(q, gain_adj, valid_adj)
                if res is not None and bg + res[0] > best_g:
                    best_g, best_y, best_pi = bg + res[0], y, res[1]
            for x in range(q):
                v = best_pi[x]
                a, b, c = (L[1], L[2], v) if k == "1P_ab" else ((L[1], v, L[2]) if k == "1P_ac" else (v, L[1], L[2]))
                if add_zstar(x, best_y, a, b, c):
                    reps_hlines.append((x, best_y, z_star, a, b, c))

    reps_skel = reps_light + reps_2p + reps_hlines

    rem_u = [unc_all[i] for i in range(len(unc_all)) if not used_unc[i]]
    reps_u: list[tuple[int, int, int, int, int, int]] = []
    for a, b, c in rem_u:
        ai, bi, ci = AH_idx.get(a, -1), BH_idx.get(b, -1), CH_idx.get(c, -1)
        best_xy, best_g = (0, 0), -1
        for x in range(q):
            for y in range(q):
                if (x, y, a, b, c) in used_zstar:
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
        if add_zstar(best_xy[0], best_xy[1], a, b, c):
            reps_u.append((best_xy[0], best_xy[1], z_star, a, b, c))

    reps_exh: list[tuple[int, int, int, int, int, int]] = []
    for x in range(q):
        for y in range(q):
            ma = [AH[i] for i in range(ha) if cnt_a[x][y][i] == 0]
            mb = [BH[i] for i in range(hb) if cnt_b[x][y][i] == 0]
            mc = [CH[i] for i in range(hc) if cnt_c[x][y][i] == 0]
            for idx in range(max(len(ma), len(mb), len(mc))):
                a = ma[idx] if idx < len(ma) else 0
                b = mb[idx] if idx < len(mb) else 0
                c = mc[idx] if idx < len(mc) else 0
                while (x, y, a, b, c) in used_zstar:
                    c = (c + 1) % q
                add_zstar(x, y, a, b, c)
                reps_exh.append((x, y, z_star, a, b, c))

    reps_closed = sorted(set(reps_skel + reps_u + reps_exh))
    return reps_skel, reps_closed, {
        "m_skel": len(reps_skel),
        "m_cl": len(reps_closed),
        "pts_2p": len(reps_2p),
        "pad": pad,
        "u_lhh": len(unc_lhh),
        "u_hhh": len(unc_hhh),
        "exh": len(reps_exh),
    }


def check_spread_light_typ2_obstruction(q: int) -> tuple[int, int]:
    """Verify that spreading H_2P_a(a0; BH, CH) across distinct rows y = u on light plane z(a0)
    breaks Typ-2 coverage for (a0, c_v) pairs across normals (1, al, be)."""
    ops = FieldOps(q)
    add, mul = ops.add, ops.mul
    ka = (q - 1 + 2) // 3
    hb = q - (q - 1 + 1) // 3
    hc = q - (q - 1) // 3
    BH = list(range(q - hb, q))
    CH = list(range(q - hc, q))
    # Spread points on z = 0: for u in 0..max(hb,hc)-1, y = u, x in 0..q-1: (x, u, 0, 0, BH[u%hb], CH[(u+x)%hc])
    pts_by_c: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for u in range(max(hb, hc)):
        for x in range(q):
            c = CH[(u + x) % hc]
            pts_by_c[c].append((x, u, 0))
    miss_normals = 0
    miss_tuples = 0
    for al in range(q):
        n_miss = 0
        for c in CH:
            seen = {add[c0][mul[al][c1]] for c0, c1, _c2 in pts_by_c[c]}
            n_miss += q - len(seen)
        if n_miss > 0:
            miss_normals += 1
            miss_tuples += n_miss
    return miss_normals, miss_tuples


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 9 Option C: H_2P_L_HH Realizability & Obstruction Diagnosis")
    ap.add_argument("--qs", type=str, default="7,8,9,11,13", help="Comma-separated q values to test")
    ap.add_argument("--check-m3-max", type=int, default=13, help="Run full check_m3 for q <= this value")
    args = ap.parse_args()

    t0 = time.time()
    run_lp_suite()

    print("\n=== PART 2: DISCRETE H_2P_L_HH PROTOTYPE (PRE-CLOSURE vs CLOSED check_m3=0) ===")
    qs = [int(x) for x in args.qs.split(",") if x.strip()]
    for q in qs:
        ops = FieldOps(q) if q <= args.check_m3_max else None
        r_lp = max(1, round(2 * q / 27))
        print(f"\n--- q={q} (143/81={143/81*q**3:.1f}, 49/27={49/27*q**3:.1f}, LP-target r2p={r_lp}) ---")
        configs = [
            ("r2p=0 (control)", 0, False, "single"),
            (f"r2p={r_lp} full s=2/3 (pair2)", r_lp, False, "pair2"),
            (f"r2p={r_lp} full s=2/3 (single)", r_lp, False, "single"),
            (f"r2p={r_lp} half s=1/3 (disj)", r_lp, True, "triple3"),
        ]
        if r_lp == 1 and q >= 7:
            configs.append(("r2p=2 full s=2/3 (pair2)", 2, False, "pair2"))
        for label, r2p, hs, pk in configs:
            r_sk, r_cl, st = build_h2plhh_discrete(q, r2p=r2p, half_size=hs, pack=pk, f3=0.35)
            chk_str = ""
            if ops is not None:
                cs = check_m3(r_sk, ops, "full-bg3")
                cc = check_m3(r_cl, ops, "full-bg3")
                assert cc["total"] == 0, f"Closure failed for q={q} {label}: {cc}"
                chk_str = f" | skel_miss=({cs['miss0']},{cs['miss1']},{cs['miss2']},{cs['miss3']:4d}) | cl_chk=0"
            print(
                f"  {label:28s}: skel={st['m_skel']:5d} ({st['m_skel']/q**3:.4f}) -> "
                f"CLOSED={st['m_cl']:5d} ({st['m_cl']/q**3:.4f}) "
                f"[2P={st['pts_2p']:4d}, pad={st['pad']:3d}, uLHH={st['u_lhh']:4d}, uHHH={st['u_hhh']:4d}, exh={st['exh']:3d}]{chk_str}",
                flush=True,
            )

    print("\n=== PART 3: SPREAD H_2P_a ON LIGHT PLANE z(a_0) TYP-2 FAILURE CHECK ===")
    for q in (7, 8, 9, 11, 13):
        mn, mt = check_spread_light_typ2_obstruction(q)
        print(f"  q={q:2d}: spread H_2P_a on z(a_0) fails {mn}/{q} al-normals ({mt} missing (pair, val) tuples)")

    print(f"\nDone in {time.time() - t0:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
