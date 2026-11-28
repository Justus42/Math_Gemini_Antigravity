#!/usr/bin/env python3
"""Phase 9: Structural analyzer for M_3(R_3) representative lists (k = q + 3).

Pure Python (std-only) + FieldOps/read_reps from scripts/phase9_m3_lift.py.
Analyzes:
  1. Layer profiles along z=c2, y=c1, x=c0 and 3D point multiplicities m(c0,c1,c2), m(a,b,c).
  2. Single-column fibers U_s subset AG(3, q) for u in {a, b, c}:
     sizes |U_s|, tuple counts N_s, full horizontal z-planes (h_a, h_b, h_c),
     all full affine planes, (c1,c2)-projection & x-cylinder test, full x-lines.
  3. Pair fibers P_{s1,s2} = {(c0,c1,c2) : (u1,u2)=(s1,s2)} for {a,b}, {a,c}, {b,c}:
     size distribution (min/median/max/hist), count with >=1 full x-line (and any full line),
     non-x-line pair z-layer counts, minimum size, and concrete minimal examples.
  4. Affine/linear correlation scan over all q^4 affine functions in GF(q) for a, b, c.
"""

from __future__ import annotations

import argparse
from collections import Counter
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase9_m3_lift import FieldOps, check_m3, read_reps  # noqa: E402


def all_projective_directions(q: int) -> list[tuple[int, int, int]]:
    """Canonical nonzero directions in PG(2, q) (first nonzero coord == 1)."""
    dirs: list[tuple[int, int, int]] = []
    # (1, b, c)
    for b in range(q):
        for c in range(q):
            dirs.append((1, b, c))
    # (0, 1, c)
    for c in range(q):
        dirs.append((0, 1, c))
    # (0, 0, 1)
    dirs.append((0, 0, 1))
    return dirs


def count_full_planes(pts: set[tuple[int, int, int]], ops: FieldOps) -> tuple[list[int], list[tuple[tuple[int, int, int], int]]]:
    """Return (full_z_planes, all_full_affine_planes) contained in pts."""
    q = ops.q
    q2 = q * q
    add, mul = ops.add, ops.mul
    full_z = [z for z in range(q) if sum(1 for (x, y, zz) in pts if zz == z) == q2]

    all_full: list[tuple[tuple[int, int, int], int]] = []
    for n0, n1, n2 in all_projective_directions(q):
        counts = [0] * q
        for x, y, z in pts:
            val = add[add[mul[n0][x]][mul[n1][y]]][mul[n2][z]]
            counts[val] += 1
        for d in range(q):
            if counts[d] == q2:
                all_full.append(((n0, n1, n2), d))
    return full_z, all_full


def count_full_xlines(pts: set[tuple[int, int, int]], q: int) -> int:
    cnt = 0
    for y in range(q):
        for z in range(q):
            if all((x, y, z) in pts for x in range(q)):
                cnt += 1
    return cnt


def has_any_full_line(pts: set[tuple[int, int, int]], ops: FieldOps) -> tuple[bool, int]:
    """Check if pts contains any affine line of AG(3, q); return (exists, count)."""
    q = ops.q
    if len(pts) < q:
        return False, 0
    add, mul = ops.add, ops.mul
    dirs = all_projective_directions(q)
    line_count = 0
    # A line with canonical direction (d0, d1, d2) has a unique basepoint with 0 in the pivot coord.
    for d0, d1, d2 in dirs:
        if d0 == 1:
            for y0 in range(q):
                for z0 in range(q):
                    ok = True
                    for t in range(q):
                        pt = (t, add[y0][mul[t][d1]], add[z0][mul[t][d2]])
                        if pt not in pts:
                            ok = False
                            break
                    if ok:
                        line_count += 1
        elif d1 == 1:
            for x0 in range(q):
                for z0 in range(q):
                    ok = True
                    for t in range(q):
                        pt = (x0, t, add[z0][mul[t][d2]])
                        if pt not in pts:
                            ok = False
                            break
                    if ok:
                        line_count += 1
        else:
            for x0 in range(q):
                for y0 in range(q):
                    ok = True
                    for t in range(q):
                        if (x0, y0, t) not in pts:
                            ok = False
                            break
                    if ok:
                        line_count += 1
    return line_count > 0, line_count


def mult_hist_dict(counts_iter) -> dict[str, int]:
    c = Counter(counts_iter)
    return {
        "m1": c.get(1, 0),
        "m2": c.get(2, 0),
        "m3": c.get(3, 0),
        "m4+": sum(v for k, v in c.items() if k >= 4),
    }


def analyze_list(path: str, q: int, mode: str, t: int | None) -> None:
    ops = FieldOps(q)
    reps = read_reps(path, q)
    m = len(reps)
    q2, q3 = q * q, q * q * q

    chk = check_m3(reps, ops, mode=mode, t=t)
    print("=" * 80)
    print(f"FILE: {path}")
    print(
        f"q={q}, m={m} (q^3={q3}, excess={m - q3}, ell=2q^3-q^2={2*q3 - q2}, delta_ell={m - (2*q3 - q2)}) | "
        f"check_m3({mode}{'' if t is None else f' t={t}'}): total_missing={chk['total']} "
        f"({chk['miss0']},{chk['miss1']},{chk['miss2']},{chk['miss3']})"
    )
    print("=" * 80)

    # 1. Layer profiles along z=c2, y=c1, x=c0
    pt_mult = Counter((r[0], r[1], r[2]) for r in reps)
    abc_mult = Counter((r[3], r[4], r[5]) for r in reps)
    print("\n[1] SCHICHT-PROFILE & PUNKTMULTIPLIZITAETEN")
    tot_h = mult_hist_dict(pt_mult.values())
    abc_h = mult_hist_dict(abc_mult.values())
    print(f"  Gesamt (c0,c1,c2): distinct={len(pt_mult)}/{q3} | mult: 1:{tot_h['m1']}, 2:{tot_h['m2']}, 3:{tot_h['m3']}, >=4:{tot_h['m4+']} (max={max(pt_mult.values())})")
    print(f"  Gesamt (a, b, c ): distinct={len(abc_mult)}/{q3} | mult: 1:{abc_h['m1']}, 2:{abc_h['m2']}, 3:{abc_h['m3']}, >=4:{abc_h['m4+']} (max={max(abc_mult.values())})")

    for axis_name, axis_idx in [("z = c2", 2), ("y = c1", 1), ("x = c0", 0)]:
        layer_counts = []
        print(f"  Achse {axis_name}:")
        for v in range(q):
            lreps = [r for r in reps if r[axis_idx] == v]
            layer_counts.append(len(lreps))
            lpts = Counter((r[0], r[1], r[2]) for r in lreps)
            lh = mult_hist_dict(lpts.values())
            print(
                f"    {axis_name}={v}: reps={len(lreps):3d} (distinct={len(lpts):2d}/{q2}) | "
                f"m=1:{lh['m1']:2d}, m=2:{lh['m2']:2d}, m=3:{lh['m3']:2d}, m>=4:{lh['m4+']:2d}"
            )
        print(f"    -> Schichtzahlen {axis_name}: {layer_counts} (sum={sum(layer_counts)}, min={min(layer_counts)}, max={max(layer_counts)})")

    # 2. Single-column fiber structure for a, b, c
    print("\n[2] FASERSTRUKTUR DER SPALTEN a, b, c (U_s subset AG(3, q))")
    col_names = [(3, "a"), (4, "b"), (5, "c")]
    h_vals = {}
    h_any_vals = {}
    for col_idx, cname in col_names:
        pt_sizes = []
        tup_sizes = []
        full_z_total = 0
        full_any_total = 0
        print(f"  Spalte {cname}:")
        for s in range(q):
            sreps = [r for r in reps if r[col_idx] == s]
            pts = {(r[0], r[1], r[2]) for r in sreps}
            pt_sizes.append(len(pts))
            tup_sizes.append(len(sreps))
            full_z, full_any = count_full_planes(pts, ops)
            full_z_total += len(full_z)
            full_any_total += len(full_any)
            z_dist = [sum(1 for (x, y, z) in pts if z == zv) for zv in range(q)]
            z_hit = sum(1 for c in z_dist if c > 0)
            proj_yz = {(y, z) for (x, y, z) in pts}
            xlines = count_full_xlines(pts, q)
            is_xcyl = (len(pts) == q * len(proj_yz))
            non_z_note = ""
            if not full_z:
                non_z_note = (
                    f" | z_hit={z_hit}/{q} z_pts={z_dist} | "
                    f"proj_(c1,c2)={len(proj_yz)}/{q2} x_cyl={is_xcyl} (ratio={len(pts)/len(proj_yz):.2f}) | "
                    f"full_x_lines={xlines}/{q2}"
                )
            else:
                non_z_note = (
                    f" | FULL_Z={full_z} z_pts={z_dist} | "
                    f"proj_(c1,c2)={len(proj_yz)}/{q2} full_x_lines={xlines}/{q2}"
                )
            any_note = f" | any_full_planes={len(full_any)}" + (
                f" {[p[0] for p in full_any]}" if full_any else ""
            )
            print(f"    {cname}={s}: |U_s|={len(pts):2d}, N_s={len(sreps):2d}{non_z_note}{any_note}")
        h_vals[cname] = full_z_total
        h_any_vals[cname] = full_any_total
        print(
            f"    -> {cname} summary: |U_s| min={min(pt_sizes)} sorted={sorted(pt_sizes)} max={max(pt_sizes)} | "
            f"N_s sorted={sorted(tup_sizes)} | h_{cname}(z-planes)={full_z_total}, any_planes={full_any_total}"
        )
    print(f"  -> h_a={h_vals['a']}, h_b={h_vals['b']}, h_c={h_vals['c']} (any-plane: {h_any_vals})")

    # 3. Pair fiber structure for {a,b}, {a,c}, {b,c}
    print("\n[3] PAAR-FASERSTRUKTUR FUER {a,b}, {a,c}, {b,c}")
    for (i1, n1), (i2, n2) in [((3, "a"), (4, "b")), ((3, "a"), (5, "c")), ((4, "b"), (5, "c"))]:
        pair_sizes = []
        cap_sizes = []
        with_xline = 0
        with_anyline = 0
        non_xline_pairs = []
        # Also precompute single fibers for U1 cap U2 comparison
        u1_fib = [{(r[0], r[1], r[2]) for r in reps if r[i1] == s} for s in range(q)]
        u2_fib = [{(r[0], r[1], r[2]) for r in reps if r[i2] == s} for s in range(q)]

        for s1 in range(q):
            for s2 in range(q):
                pts = {(r[0], r[1], r[2]) for r in reps if r[i1] == s1 and r[i2] == s2}
                cap = u1_fib[s1] & u2_fib[s2]
                pair_sizes.append(len(pts))
                cap_sizes.append(len(cap))
                xl = count_full_xlines(pts, q)
                has_al, al_cnt = has_any_full_line(pts, ops)
                if xl > 0:
                    with_xline += 1
                else:
                    z_layers = len({z for (x, y, z) in pts})
                    non_xline_pairs.append((len(pts), z_layers, has_al, al_cnt, (s1, s2), sorted(pts)))
                if has_al:
                    with_anyline += 1

        hist = dict(sorted(Counter(pair_sizes).items()))
        cap_hist = dict(sorted(Counter(cap_sizes).items()))
        print(
            f"  Paar {{{n1},{n2}}}: |P_(s1,s2)| min={min(pair_sizes)} med={statistics.median(pair_sizes):.1f} "
            f"max={max(pair_sizes)} hist={hist}"
        )
        if cap_hist != hist:
            print(
                f"    (|U1 cap U2| min={min(cap_sizes)} med={statistics.median(cap_sizes):.1f} "
                f"max={max(cap_sizes)} hist={cap_hist})"
            )
        print(f"    Paare mit >=1 voller x-Gerade: {with_xline}/{q2} | mit >=1 beliebiger voller Gerade: {with_anyline}/{q2}")
        if non_xline_pairs:
            non_xline_pairs.sort(key=lambda x: (x[0], x[1]))
            z_cnts = [x[1] for x in non_xline_pairs]
            al_in_nonx = sum(1 for x in non_xline_pairs if x[2])
            min_sz = non_xline_pairs[0][0]
            min_ex = non_xline_pairs[0]
            print(
                f"    Paare OHNE volle x-Gerade ({len(non_xline_pairs)}/{q2}): "
                f"min_size={min_sz}, max_size={max(x[0] for x in non_xline_pairs)}, "
                f"z-Schichten hist={dict(sorted(Counter(z_cnts).items()))}, "
                f"davon mit anderer voller Gerade: {al_in_nonx}/{len(non_xline_pairs)}"
            )
            print(f"    Kleinstes Nicht-x-Geraden-Paar ({n1},{n2})={min_ex[4]} (size={min_ex[0]}, z_layers={min_ex[1]}, any_line={min_ex[2]}): {min_ex[5]}")
        else:
            print(f"    Alle {q2}/{q2} Paare enthalten eine volle x-Gerade.")

    # 4. Affine / linear correlation check over all q^4 affine functions in GF(q)
    print("\n[4] SYMMETRIE- / AFFINE-KORRELATIONS-CHECK (alle q^4 affinen Funktionen in GF(q))")
    add, mul = ops.add, ops.mul
    for col_idx, cname in col_names:
        scores = []
        exact_c2 = sum(1 for r in reps if r[col_idx] == r[2])
        exact_c1 = sum(1 for r in reps if r[col_idx] == r[1])
        exact_c0 = sum(1 for r in reps if r[col_idx] == r[0])
        for k0 in range(q):
            for k1 in range(q):
                for k2 in range(q):
                    for k3 in range(q):
                        hit = 0
                        for r in reps:
                            val = add[add[add[mul[k0][r[0]]][mul[k1][r[1]]]][mul[k2][r[2]]]][k3]
                            if val == r[col_idx]:
                                hit += 1
                        scores.append((hit, (k0, k1, k2, k3)))
        scores.sort(reverse=True)
        top3 = [(h, f"{h/m:.3f}", coef) for h, coef in scores[:3]]
        print(
            f"  {cname}: eq_c0={exact_c0}/{m} ({exact_c0/m:.3f}), eq_c1={exact_c1}/{m} ({exact_c1/m:.3f}), "
            f"eq_c2={exact_c2}/{m} ({exact_c2/m:.3f}) | random_exp={m/q:.1f} ({1/q:.3f}) | "
            f"top3 affine (k0,k1,k2,k3)={top3}"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Structural analyzer for Phase 9 M_3(R_3) lists")
    ap.add_argument("--all", action="store_true", help="analyze the three main lists in data/phase9_m3/")
    ap.add_argument("--q", type=int)
    ap.add_argument("--reps")
    ap.add_argument("--mode", choices=["tspec", "full-bg3"], default="full-bg3")
    ap.add_argument("--t", type=int)
    args = ap.parse_args()

    if args.all:
        analyze_list("data/phase9_m3/R3_q3_fullbg3_m43.txt", 3, "full-bg3", None)
        analyze_list("data/phase9_m3/R3_q4_t4_tspec_m105.txt", 4, "tspec", 4)
        analyze_list("data/phase9_m3/R3_q5_fullbg3_m215.txt", 5, "full-bg3", None)
        return

    if args.q is None or args.reps is None:
        sys.exit("need --all or (--q and --reps)")
    analyze_list(args.reps, args.q, args.mode, args.t)


if __name__ == "__main__":
    main()
