#!/usr/bin/env python3
"""Phase 5E Step A: Deterministic dissection of CA(3430; 4, 9, 7) and CA(9558; 4, 11, 9).

Pure Python (std-only). No search or heuristic.
Compares the reduced arrays CA_3430_4_9_7.txt (-3*7^2) and CA_9558_4_11_9.txt (-3*9^2)
against their exact poly2-disjoint start arrays CA(3577; 4, 9, 7) and CA(9801; 4, 11, 9):
  1. Exact row/cell diff (by Bush polynomial (a, b, c, d), col_inf, col_{q+1})
  2. Complete slice-level inventory (Bush OA(q^4) fibers + extra slices + partial slices)
  3. Per-symbol AG(2, q) line-coverage & 2nd divided-difference coverage analysis
  4. Uniformity check across q = 7 and q = 9 and compatibility with Bai's pencil cover.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gen_t4_odd_q_nearbush import (  # noqa: E402
    GF,
    _odd_sym_map_and_anchors,
    build_odd_poly2_disjoint,
)


def load_rows(path: Path) -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                rows.append(tuple(int(x) for x in s.split()))
    return rows


def build_poly_decoder(gf: GF) -> dict[tuple[int, ...], tuple[int, int, int, int]]:
    """Map every finite-column codeword r[:q] to its unique degree-3 coeffs (a, b, c, d)."""
    q = gf.q
    add, mul, x2, x3 = gf.add, gf.mul, gf.x2, gf.x3
    dec: dict[tuple[int, ...], tuple[int, int, int, int]] = {}
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    p = tuple(
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    )
                    dec[p] = (a, b, c, d)
    assert len(dec) == q**4
    return dec


def check_ag2_missed_lines(gf: GF, pts: set[tuple[int, int]]) -> list[tuple[str, int, int]]:
    """Return all affine lines in AG(2, q) (coordinates (c, d)) missed by pts.

    Line encoding:
      - ('d_const', d0, 0): horizontal line d = d0  (corresponds to 3-set with col_inf!)
      - ('slope', S, r):    line c + S * d = r      (corresponds to 3-set of finite cols with sum S!)
    """
    q = gf.q
    add, mul = gf.add, gf.mul
    missed: list[tuple[str, int, int]] = []
    for d0 in range(q):
        if not any(d == d0 for (_, d) in pts):
            missed.append(("d_const", d0, 0))
    for S in range(q):
        for r in range(q):
            if not any(add[c][mul[S][d]] == r for (c, d) in pts):
                missed.append(("slope", S, r))
    return missed


def slice_covers_line(gf: GF, c: int, d: int, col_inf: int, line: tuple[str, int, int]) -> bool:
    """Does an OA(q^2) polynomial slice (c, d, col_inf) cover the missing 3-tuple class `line`?

    For finite 3-set {x0, x1, x2} with S = x0 + x1 + x2:
      2nd divided difference is c + S * d (independent of col_inf).
    For 3-set {x0, x1, col_inf}:
      value of col_inf is `col_inf` (independent of c, d; covers all (y0, y1, col_inf) because (a,b) spans GF(q)^2).
    """
    kind, p1, p2 = line
    if kind == "d_const":
        return col_inf == p1
    # kind == "slope": c + S * d == r
    return gf.add[c][gf.mul[p1][d]] == p2


def dissect_q(q: int, reduced_path: Path) -> None:
    gf = GF(q)
    q2 = q * q
    k = q + 2
    c_b = (q - 1) // 2
    dec = build_poly_decoder(gf)
    sym_map, anchors, desc = _odd_sym_map_and_anchors(gf)
    start_rows, _ = build_odd_poly2_disjoint(q)
    red_rows = load_rows(reduced_path)

    print("=" * 88)
    print(f"DISSECTION q = {q}, k = {k}: start N = {len(start_rows)} -> reduced N = {len(red_rows)} "
          f"(delta = {len(red_rows) - len(start_rows)} = {(len(red_rows) - len(start_rows)) / q2:.2f} * q^2)")
    print(f"Start layout: {desc}")
    print("=" * 88)

    # 1. Exact multiset diff & polynomial-code check
    non_poly = [r for r in red_rows if r[:q] not in dec]
    print(f"\n[1] Row- & Cell-Diff (start vs reduced):")
    print(f"  non-polynomial rows in reduced: {len(non_poly)}")
    assert len(non_poly) == 0

    start_cnt = Counter(start_rows)
    red_cnt = Counter(red_rows)
    unchanged_exact = sum((start_cnt & red_cnt).values())
    removed_exact = sum((start_cnt - red_cnt).values())
    added_exact = sum((red_cnt - start_cnt).values())
    print(f"  Exact identical rows: {unchanged_exact}/{len(start_rows)}")
    print(f"  Start rows not present verbatim in reduced: {removed_exact}")
    print(f"  Reduced rows not present verbatim in start: {added_exact} "
          f"(net deleted = {removed_exact - added_exact})")

    # Classify start rows vs reduced rows by finite polynomial p = (a, b, c, d)
    start_by_poly: dict[tuple[int, int, int, int], list[tuple[int, int]]] = defaultdict(list)
    for r in start_rows:
        start_by_poly[dec[r[:q]]].append((r[q], r[q + 1]))

    red_by_poly: dict[tuple[int, int, int, int], list[tuple[int, int]]] = defaultdict(list)
    for r in red_rows:
        red_by_poly[dec[r[:q]]].append((r[q], r[q + 1]))

    # Check Bush OA(q^4) preservation (col_inf == d)
    bush_start = {dec[r[:q]]: r[q + 1] for r in start_rows[: q**4]}
    bush_red_map: dict[tuple[int, int, int, int], list[int]] = defaultdict(list)
    extra_red: list[tuple[int, int, int, int, int, int]] = []
    for r in red_rows:
        a, b, c, d = dec[r[:q]]
        ci, m = r[q], r[q + 1]
        if ci == d:
            bush_red_map[(a, b, c, d)].append(m)
        else:
            extra_red.append((a, b, c, d, ci, m))

    bush_missing = [abcd for abcd in bush_start if abcd not in bush_red_map]
    bush_dup = [abcd for abcd, ms in bush_red_map.items() if len(ms) > 1]
    bush_same_col = sum(
        1 for abcd, m0 in bush_start.items()
        if abcd in bush_red_map and m0 in bush_red_map[abcd]
    )
    bush_recolored = sum(
        1 for abcd, m0 in bush_start.items()
        if abcd in bush_red_map and m0 not in bush_red_map[abcd]
    )
    print(f"\n  Bush OA(q^4) block (r[col_inf] == d):")
    print(f"    present codewords: {len(bush_red_map)}/{q**4} (missing={len(bush_missing)}, duplicate={len(bush_dup)})")
    print(f"    unchanged col_{{q+1}}: {bush_same_col}/{q**4}")
    print(f"    recolored col_{{q+1}}: {bush_recolored}/{q**4} (= {bush_recolored / q2:.4f} * q^2)")

    # Match row-by-row within same finite polynomial (a,b,c,d) to count cell edits vs pure deletions
    cell_edits_1 = 0
    cell_edits_2 = 0
    pure_del = 0
    pure_add = 0
    for abcd in set(start_by_poly.keys()) | set(red_by_poly.keys()):
        s_list = list(start_by_poly.get(abcd, []))
        r_list = list(red_by_poly.get(abcd, []))
        # Remove exact matches first
        s_rem = []
        for x in s_list:
            if x in r_list:
                r_list.remove(x)
            else:
                s_rem.append(x)
        # Pair remaining greedily by Hamming distance (1 vs 2)
        used_r = [False] * len(r_list)
        unmatched_s = []
        for x in s_rem:
            found = -1
            for j, y in enumerate(r_list):
                if not used_r[j] and (x[0] == y[0] or x[1] == y[1]):
                    found = j
                    break
            if found >= 0:
                used_r[found] = True
                cell_edits_1 += 1
            else:
                unmatched_s.append(x)
        rem_r = [y for j, y in enumerate(r_list) if not used_r[j]]
        k2 = min(len(unmatched_s), len(rem_r))
        cell_edits_2 += k2
        pure_del += len(unmatched_s) - k2
        pure_add += len(rem_r) - k2

    print(f"\n  Minimum cell-edit pairing on identical finite polynomials r[:q]:")
    print(f"    1-cell edits (only col_inf or only col_{{q+1}} changed): {cell_edits_1}")
    print(f"    2-cell edits (both col_inf and col_{{q+1}} changed):     {cell_edits_2}")
    print(f"    unmatched deleted rows (no partner on same poly):      {pure_del}")
    print(f"    unmatched added rows (no partner on same poly):        {pure_add}")
    print(f"    net row delta = {pure_add - pure_del}")

    # 2. Complete slice-level inventory (c, d, col_inf, m)
    print(f"\n[2] Complete (c, d, col_inf, m) slice inventory:")
    start_slices: Counter[tuple[int, int, int, int]] = Counter()
    for r in start_rows:
        _, _, c, d = dec[r[:q]]
        start_slices[(c, d, r[q], r[q + 1])] += 1

    red_slices: Counter[tuple[int, int, int, int]] = Counter()
    for r in red_rows:
        _, _, c, d = dec[r[:q]]
        red_slices[(c, d, r[q], r[q + 1])] += 1

    full_red = {k_s for k_s, cnt in red_slices.items() if cnt == q2}
    partial_red = {k_s: cnt for k_s, cnt in red_slices.items() if cnt != q2}
    print(f"  Start slices: {len(start_slices)} (all size {q2})")
    print(f"  Reduced full {q2}-slices: {len(full_red)}, partial slices: {len(partial_red)}")
    if partial_red:
        print(f"  Partial slice details (c, d, col_inf, m): count:")
        for k_s, cnt in sorted(partial_red.items()):
            tag = "BUSH" if k_s[1] == k_s[2] else "EXTRA"
            print(f"    {tag} (c={k_s[0]}, d={k_s[1]}, ci={k_s[2]}, m={k_s[3]}): {cnt}/{q2}")

    # Bush fiber recoloring table (c, d): m_start -> Counter(m_red)
    print(f"\n  Bush fiber (c, d) changes (start m -> reduced m):")
    bush_fiber_red: dict[tuple[int, int], Counter[int]] = defaultdict(Counter)
    for r in red_rows:
        _, _, c, d = dec[r[:q]]
        if r[q] == d:
            bush_fiber_red[(c, d)][r[q + 1]] += 1

    recolored_fibers = []
    for c in range(q):
        for d in range(q):
            m0 = sym_map[c * q + d]
            cnts = bush_fiber_red[(c, d)]
            if cnts != Counter({m0: q2}):
                kind0 = "parab" if (m0 == c_b and c == gf.x2[d]) else ("bs" if m0 < c_b else "sing")
                recolored_fibers.append((c, d, m0, kind0, dict(cnts)))
    print(f"    Changed Bush fibers: {len(recolored_fibers)}/{q2}")
    for c, d, m0, kind0, cnts in recolored_fibers:
        print(f"      (c={c}, d={d}) [start m={m0} ({kind0})] -> {cnts}")

    # Extra slices diff (col_inf != d)
    start_extra_slices = {k_s for k_s in start_slices if k_s[1] != k_s[2]}
    red_extra_slices_all = {k_s: cnt for k_s, cnt in red_slices.items() if k_s[1] != k_s[2]}
    print(f"\n  Extra slices (col_inf != d): start={len(start_extra_slices)}, "
          f"reduced full={sum(1 for cnt in red_extra_slices_all.values() if cnt == q2)}, "
          f"reduced partial={sum(1 for cnt in red_extra_slices_all.values() if cnt != q2)}")

    deleted_extra = sorted(start_extra_slices - set(red_extra_slices_all.keys()))
    added_extra = sorted(set(red_extra_slices_all.keys()) - start_extra_slices)
    print(f"    Deleted extra slices ({len(deleted_extra)}):")
    for c, d, ci, m in deleted_extra:
        print(f"      DEL (c={c}, d={d}, ci={ci}, m={m})")
    print(f"    New / modified extra slices ({len(added_extra)}):")
    for c, d, ci, m in added_extra:
        cnt = red_extra_slices_all[(c, d, ci, m)]
        # Also check if (c, d, ci) existed under another m in start
        prev_m = [k_s[3] for k_s in start_extra_slices if k_s[:3] == (c, d, ci)]
        # Check if (c, d) with ci==d existed in start
        bush_m = sym_map[c * q + d]
        print(f"      NEW (c={c}, d={d}, ci={ci}, m={m}) cnt={cnt}/{q2} "
              f"[same (c,d,ci) in start? m={prev_m}; bush(c,d) start m={bush_m}]")

    # 3. Per-symbol algebraic decomposition
    print(f"\n[3] Per-symbol algebraic structure in reduced array:")
    for m in range(q):
        start_bush_m = {(c, d) for c in range(q) for d in range(q) if sym_map[c * q + d] == m}
        start_ext_m = sorted([(c, d, ci) for (c, d, ci, mm) in start_extra_slices if mm == m])

        red_bush_full_m = {(c, d) for (c, d) in bush_fiber_red if bush_fiber_red[(c, d)].get(m, 0) == q2}
        red_bush_part_m = {
            (c, d): bush_fiber_red[(c, d)][m]
            for (c, d) in bush_fiber_red
            if 0 < bush_fiber_red[(c, d)].get(m, 0) < q2
        }
        red_ext_full_m = sorted([
            (c, d, ci) for (c, d, ci, mm), cnt in red_extra_slices_all.items()
            if mm == m and cnt == q2
        ])
        red_ext_part_m = sorted([
            (c, d, ci, cnt) for (c, d, ci, mm), cnt in red_extra_slices_all.items()
            if mm == m and cnt != q2
        ])

        start_tot = len(start_bush_m) + len(start_ext_m)
        red_rows_m = sum(1 for r in red_rows if r[q + 1] == m)
        delta_slices = (red_rows_m - start_tot * q2) / q2

        role = "BS" if m < c_b else ("PARAB" if m == c_b else "SING")
        print(f"\n  Symbol m={m} [{role}]: start={start_tot} slices ({len(start_bush_m)} bush + {len(start_ext_m)} ext) "
              f"-> reduced={red_rows_m/q2:.2f} slices ({len(red_bush_full_m)} bush + {len(red_ext_full_m)} ext"
              f"{f' + part_bush={red_bush_part_m}' if red_bush_part_m else ''}"
              f"{f' + part_ext={red_ext_part_m}' if red_ext_part_m else ''}), delta={delta_slices:+.2f}*q^2")

        # Missed AG(2,q) lines by reduced FULL bush points
        missed_by_bush = check_ag2_missed_lines(gf, red_bush_full_m)
        missed_by_all_slices = [
            ln for ln in missed_by_bush
            if not any(slice_covers_line(gf, c, d, ci, ln) for (c, d, ci) in red_ext_full_m)
        ]
        # Check algebraic relation of all slices of symbol m!
        all_pts_m = sorted(red_bush_full_m)
        # Check if (c, d) of bush + extra slices satisfy a simple relation (e.g. col_inf vs c, d)
        print(f"    Bush points gained vs start: {sorted(red_bush_full_m - start_bush_m)}")
        print(f"    Bush points lost vs start:   {sorted(start_bush_m - red_bush_full_m)}")
        print(f"    Extra slices (c, d, ci):     {red_ext_full_m}")
        print(f"    AG(2,{q}) lines missed by full Bush pts: {len(missed_by_bush)} "
              f"(d_const: {sum(1 for x in missed_by_bush if x[0]=='d_const')}, "
              f"slope: {sum(1 for x in missed_by_bush if x[0]=='slope')})")
        print(f"    Still missed after full extra slices:    {len(missed_by_all_slices)}")
        if len(missed_by_bush) <= 25 and missed_by_bush:
            print(f"    Missed lines by Bush: {missed_by_bush}")
        if missed_by_all_slices:
            print(f"    Uncovered by full slices (repaired by partials): {missed_by_all_slices[:10]}")

        # Check: in reduced slices of symbol m, are the extra slices on a shifted line/parabola?
        # Specifically: for every full slice (c, d, ci) of symbol m, compute (c, d, ci, c - ci*d?, c - d^2?)
        if m >= c_b or delta_slices != 0:
            # Check how many distinct col_inf values are covered by Bush vs Extra
            bush_d = sorted({d for (_, d) in red_bush_full_m})
            ext_ci = sorted([ci for (_, _, ci) in red_ext_full_m])
            print(f"    Distinct d in Bush: {bush_d}; ci in Extra: {ext_ci}")
            # Check if the combined (c, d) points of Bush + Extra form a shifted OA(q^3) or line!
            # Remember: a shifted OA(q^3; 3, q+1, q) is {(c0 + (cp - d0), d0, cp) : cp in GF(q)}
            # i.e., FIXED d = d0, and c - cp = const = c0 - d0!
            d_groups = defaultdict(list)
            for (c, d) in red_bush_full_m:
                d_groups[d].append((c, d, gf.sub[c][d], "B"))
            for (c, d, ci) in red_ext_full_m:
                d_groups[d].append((c, ci, gf.sub[c][ci], "E"))
            # Check constant (c - ci) groups with fixed d (which form OA(q^3) lines!)
            oa3_groups = defaultdict(list)
            for (c, d) in red_bush_full_m:
                oa3_groups[(d, gf.sub[c][d])].append((c, d, d, "B"))
            for (c, d, ci) in red_ext_full_m:
                oa3_groups[(d, gf.sub[c][ci])].append((c, d, ci, "E"))
            big_oa3 = {k_g: v for k_g, v in oa3_groups.items() if len(v) >= 2}
            if big_oa3:
                print(f"    Shifted-OA3 lines (fixed d, fixed c-ci) of size >= 2:")
                for (d_val, c_minus_ci), items in sorted(big_oa3.items(), key=lambda kv: -len(kv[1])):
                    cis = sorted(x[2] for x in items)
                    tags = "".join(x[3] for x in sorted(items, key=lambda x: x[2]))
                    print(f"      (d={d_val}, c-ci={c_minus_ci}): len={len(items)}/{q}, cis={cis} [{tags}]")

            # Also check for each slope S in GF(q), which values of c + S*d are covered by Bush vs Extra
            # (crucial for understanding why m* saves 3 or 6 slices!)
            if m == c_b:
                print(f"    Detailed slope coverage for parabola symbol m*={m}:")
                all_full_cd = [(c, d, d, "B") for (c, d) in red_bush_full_m] + [
                    (c, d, ci, "E") for (c, d, ci) in red_ext_full_m
                ]
                print(f"      Total full slices for m*={m}: {len(all_full_cd)} (Bush={len(red_bush_full_m)}, Extra={len(red_ext_full_m)})")
                for S in range(q):
                    vals_b = sorted({gf.add[c][gf.mul[S][d]] for (c, d) in red_bush_full_m})
                    vals_e = sorted({gf.add[c][gf.mul[S][d]] for (c, d, _) in red_ext_full_m})
                    vals_all = sorted(set(vals_b) | set(vals_e))
                    miss = sorted(set(range(q)) - set(vals_all))
                    print(f"      S={S}: bush={vals_b} ({len(vals_b)}), extra={vals_e}, union={len(vals_all)}/{q}, miss={miss}")

    # 4. Global structural check on ALL reduced slices of symbols m >= c_b (and m < c_b that changed)
    print(f"\n[4] Check of partial-slice rows (if any) in reduced array:")
    if not partial_red:
        print("  ZERO partial slices! Every single row belongs to a complete q^2-slice.")
    else:
        # Group partial rows by (c, d)
        by_cd: dict[tuple[int, int], list[tuple[int, int, int, int]]] = defaultdict(list)
        for r in red_rows:
            a, b, c, d = dec[r[:q]]
            if (c, d, r[q], r[q + 1]) in partial_red:
                by_cd[(c, d)].append((a, b, r[q], r[q + 1]))
        for (c, d), items in sorted(by_cd.items()):
            print(f"  Partial rows at (c={c}, d={d}): total={len(items)}")
            by_ab = Counter((a, b) for a, b, _, _ in items)
            by_cim = Counter((ci, m) for _, _, ci, m in items)
            print(f"    (ci, m) counts: {dict(by_cim)}")
            print(f"    distinct (a, b) covered: {len(by_ab)}/{q2}, mults={Counter(by_ab.values())}")
            # Check if (ci, m) is a function of a, b (e.g. linear in a, b?)
            for (ci, m), cnt in sorted(by_cim.items()):
                abs_here = [(a, b) for a, b, ci2, m2 in items if (ci2, m2) == (ci, m)]
                a_cnt = Counter(a for a, _ in abs_here)
                b_cnt = Counter(b for _, b in abs_here)
                print(f"      (ci={ci}, m={m}) cnt={cnt}: a_dist={dict(sorted(a_cnt.items()))}, b_dist={dict(sorted(b_cnt.items()))}")

    # 5. Jamison / Brouwer-Schrijver per-symbol budget: b_m + 2*e_m >= 2q - 1
    print(f"\n[5] Jamison / Brouwer-Schrijver budget (b_m + 2*e_m >= 2q - 1 = {2 * q - 1}):")
    floor_e = q * (q - 1) // 2
    bai_e = (q * q - 1) // 2
    print(f"  Global lower bound for Bush OA(q^4) + q^2-slices: E >= q(q-1)/2 = {floor_e} "
          f"(N >= {q**4 + floor_e * q2}); Bai Kor. 5.3 has E = (q^2-1)/2 = {bai_e} "
          f"(excess = {(q - 1) // 2} slices = waste {q - 1}).")
    tot_b = 0
    tot_e = 0.0
    tot_waste = 0.0
    for m in range(q):
        b_m = sum(1 for (c, d) in bush_fiber_red if bush_fiber_red[(c, d)].get(m, 0) == q2)
        rows_m = sum(1 for r in red_rows if r[q + 1] == m)
        e_m = (rows_m - b_m * q2) / q2
        budget = b_m + 2.0 * e_m
        waste = budget - (2 * q - 1)
        tot_b += b_m
        tot_e += e_m
        tot_waste += waste
        print(f"    m={m}: b_m={b_m:2d}, e_m={e_m:5.2f}, b_m + 2*e_m = {budget:5.2f} (waste={waste:+.2f})")
    print(f"  TOTAL: sum b_m={tot_b} (=q^2={q2}), sum e_m={tot_e:.2f} (floor={floor_e}), total waste={tot_waste:+.2f}")


def main() -> None:
    t0 = time.perf_counter()
    dissect_q(7, Path("results/t4_nearbush/CA_3430_4_9_7.txt"))
    print()
    dissect_q(9, Path("results/t4_nearbush/CA_9558_4_11_9.txt"))
    print(f"\nTotal dissection time: {time.perf_counter() - t0:.3f}s")


if __name__ == "__main__":
    main()
