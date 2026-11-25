#!/usr/bin/env python3
"""Search-free structural analysis of t = 4 NEAR_BUSH arrays against Bai (2026) bounds.

Pure Python (std-only). Performs three deterministic checks without any search:
  1. CA(5888; 4, 10, 8) vs. Bai (2026) Prop. 5.4 model bound 6144 (block/slice breakdown).
  2. Raw CA(7203; 4, 11, 8) vs. Bai (2026) Thm. 6.2 bound 8192 (shared hyperoval slices + repairs).
  3. Bai (2026) Thm. 3.7 / Open Problem 2 check on CA(3430; 4, 9, 7) and CA(5888; 4, 10, 8):
     checks Bush OA(q^4; 4, q+1, q) survival on cols 0..q, single-valuedness of col_{q+1},
     color counts per (t-1)-tuple fiber, and number of universal (all-fiber) colors vs. floor(q/2).
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gen_t4_odd_q_nearbush import GF  # noqa: E402
from gen_t4_q8_nearbush import (  # noqa: E402
    GF8_MUL,
    K10_COLORING,
    K10_FREE_PTS,
    build_k11_polychrom,
    eval_bush_tc,
)


def load_rows(path: Path) -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                rows.append(tuple(int(x) for x in s.split()))
    return rows


def bush_oa_set(q: int) -> set[tuple[int, ...]]:
    """Return exact set of q^4 rows of Bush OA(q^4; 4, q+1, q)."""
    if q == 8:
        return {
            eval_bush_tc(a, b, c, d)
            for a in range(8)
            for b in range(8)
            for c in range(8)
            for d in range(8)
        }
    gf = GF(q)
    add, mul, x2, x3 = gf.add, gf.mul, gf.x2, gf.x3
    out: set[tuple[int, ...]] = set()
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = tuple(
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    ) + (d,)
                    out.add(r)
    return out


def analyze_5888_vs_6144(rows_5888: list[tuple[int, ...]]) -> None:
    print("=== 1. CA(5888; 4, 10, 8) vs. Bai (2026) Prop. 5.4 (6144) ===")
    bush = bush_oa_set(8)
    in_bush = [r for r in rows_5888 if r[:9] in bush]
    out_bush = [r for r in rows_5888 if r[:9] not in bush]
    in_cnt = Counter(r[9] for r in in_bush)
    out_cnt = Counter(r[9] for r in out_bush)
    tot_cnt = Counter(r[9] for r in rows_5888)
    print(f"  Total rows: {len(rows_5888)} (Bai Prop. 5.4 model bound: 4096 + 32*64 = 6144, delta = {len(rows_5888) - 6144})")
    print(f"  Rows with cols 0..8 in Bush OA(4096): {len(in_bush)} (distinct prefixes: {len({r[:9] for r in in_bush})})")
    print(f"  Rows outside Bush OA(4096):           {len(out_bush)} = {len(out_bush)//64} slices of 64 (vs. 32*64 = 2048 -> -{(2048 - len(out_bush))//64} slices = -{2048 - len(out_bush)} rows)")
    print(f"  Symbol counts in Bush OA (col 9):     {dict(sorted(in_cnt.items()))}")
    print(f"  Symbol counts outside Bush OA (col9): {dict(sorted(out_cnt.items()))}")
    print(f"  Total symbol counts (col 9):          {dict(sorted(tot_cnt.items()))}")
    # Verify each symbol 4..7 in Bush OA is an exact OA(64; 2, 9, 8) (t=2 on all C(9,2)=36 pairs)
    for m in (4, 5, 6, 7):
        sub_in = [r[:9] for r in in_bush if r[9] == m]
        sub_all = [r[:9] for r in rows_5888 if r[9] == m]
        oa2_ok = all(len({(r[i], r[j]) for r in sub_in}) == 64 for i, j in combinations(range(9), 2))
        oa3_ok = all(len({(r[i], r[j], r[l]) for r in sub_all}) == 512 for i, j, l in combinations(range(9), 3))
        print(f"  Symbol m={m}: {len(sub_in)} rows in Bush OA (OA(64;2,9,8)={oa2_ok}) + {len(sub_all)-len(sub_in)} extra = {len(sub_all)} (OA(512;3,9,8)={oa3_ok})")
    print(f"  AG(2, 8) point budget: 4 * 15 (disjoint minimal BS) + 4 * 1 (free pts {K10_FREE_PTS}) = 64")
    print(f"  Savings mechanism: each free point supplies 1 OA(64;2,9,8) slice inside Bush OA -> 7*64=448 extra rows/symbol instead of 8*64=512 (-64/symbol, -256 total).")


def analyze_7203_vs_8192() -> None:
    print("\n=== 2. Raw CA(7203; 4, 11, 8) vs. Bai (2026) Thm. 6.2 (8192) ===")
    rows = build_k11_polychrom()
    assert len(rows) == 7203
    blk_main = rows[:4096]
    blk_col9 = rows[4096 : 4096 + 2048]
    blk_col10 = rows[4096 + 2048 : 4096 + 2048 + 1024]
    blk_rep = rows[4096 + 2048 + 1024 :]
    assert len(blk_rep) == 35

    # Breakdown of (col9 in {0..3} vs {4..7}, col10 in {0..3} vs {4..7})
    quad = Counter((r[9] >= 4, r[10] >= 4) for r in rows)
    quad_col9 = Counter((r[9] >= 4, r[10] >= 4) for r in blk_col9)
    quad_col10 = Counter((r[9] >= 4, r[10] >= 4) for r in blk_col10)
    print(f"  Total rows: {len(rows)} (Bai Thm. 6.2 bound: 4096 + 4*512 + 4*512 = 8192, delta = {len(rows) - 8192})")
    print(f"  Block breakdown: main Bush OA = {len(blk_main)}, col9-hyperoval = {len(blk_col9)}, col10-hyperoval = {len(blk_col10)}, greedy pair-repair = {len(blk_rep)}")
    print(f"  Quadrant counts (col9>=4, col10>=4) total:      {dict(sorted(quad.items()))}")
    print(f"  Quadrant counts in col9-hyperoval (2048 rows):  {dict(sorted(quad_col9.items()))}")
    print(f"  Quadrant counts in col10-hyperoval (1024 rows): {dict(sorted(quad_col10.items()))}")
    # Verify that in blk_col9 + blk_col10, each m9 in 4..7 has 512 rows (OA(512;3,9,8)) and each m10 in 4..7 has 512 rows (256 shared from blk_col9 + 256 from blk_col10)
    for m10 in (4, 5, 6, 7):
        from_c9 = sum(1 for r in blk_col9 if r[10] == m10)
        from_c10 = sum(1 for r in blk_col10 if r[10] == m10)
        sub_m10 = [r[:9] for r in blk_col9 + blk_col10 if r[10] == m10]
        oa3_ok = all(len({(r[i], r[j], r[l]) for r in sub_m10}) == 512 for i, j, l in combinations(range(9), 3))
        print(f"  col10={m10}: {from_c9} shared rows from col9-blocks + {from_c10} dedicated rows = {len(sub_m10)} (OA(512;3,9,8)={oa3_ok})")
    print("  Net delta vs. 8192: -1024 (16 shared OA(64) slices in (col9,col10) in {4..7}^2) + 35 (repair of 68 missed {0..3}^2 pairs) = -989.")


def check_thm37(label: str, path: Path, q: int) -> None:
    print(f"\n=== 3. Bai Thm. 3.7 / Open Problem 2 Check: {label} (q={q}, k={q+2}) ===")
    rows = load_rows(path)
    k = len(rows[0])
    assert k == q + 2
    bush = bush_oa_set(q)

    # Check cols 0..q against standard Bush OA(q^4; 4, q+1, q)
    prefix_to_vals: dict[tuple[int, ...], list[int]] = defaultdict(list)
    non_bush_rows = 0
    for r in rows:
        pref = r[: q + 1]
        if pref in bush:
            prefix_to_vals[pref].append(r[q + 1])
        else:
            non_bush_rows += 1

    bush_covered = len(prefix_to_vals)
    bush_missing = len(bush) - bush_covered
    multi_valued = sum(1 for vs in prefix_to_vals.values() if len(set(vs)) > 1)
    dup_same_val = sum(1 for vs in prefix_to_vals.values() if len(vs) > 1 and len(set(vs)) == 1)
    total_rows_in_bush_prefix = sum(len(vs) for vs in prefix_to_vals.values())

    print(f"  Array size: N={len(rows)}, q^4={q**4}, floor(q/2)={q // 2}")
    print(f"  Standard Bush OA(q^4;4,{q+1},{q}) on cols 0..{q}:")
    print(f"    Present prefixes: {bush_covered}/{q**4} (missing: {bush_missing})")
    print(f"    Total rows with Bush prefix: {total_rows_in_bush_prefix} (multi-valued col_{q+1}: {multi_valued}, dup same val: {dup_same_val})")
    print(f"    Rows outside Bush OA prefix: {non_bush_rows}")

    # Check ALL k subsets of (q+1) columns for distinct projections and exact OA(q^4) completeness
    # Note: for a (q+1)-subset S, a necessary condition for containing OA(q^4) is >= q^4 distinct (q+1)-tuples.
    oa_candidates = []
    for drop_col in range(k):
        cols = [c for c in range(k) if c != drop_col]
        proj = {tuple(r[c] for c in cols) for r in rows}
        # For cols 0..q, check if exactly q^4 rows from bush exist; for any subset check distinct count
        if len(proj) >= q**4:
            oa_candidates.append((drop_col, len(proj)))
    print(f"  (q+1)-column subsets with >= q^4 distinct projections: {oa_candidates}")

    # Analyze (t-1)=3-tuple fibers on cols 0..q restricted to the Bush-OA rows
    # (exact setting of Bai Thm. 3.7 if bush_covered == q^4 and multi_valued == 0)
    if bush_covered == q**4 and multi_valued == 0:
        base_rows = [pref + (vals[0],) for pref, vals in prefix_to_vals.items()]
        print(f"  -> Pure function f: OA({q**4}) -> GF({q}) exists on cols 0..{q} (0 missing, 0 multi-valued).")
    else:
        base_rows = [r for r in rows if r[: q + 1] in bush]
        print(f"  -> Bush OA(q^4) on cols 0..{q} is NOT intact as a single-valued base (missing={bush_missing}, multi_valued={multi_valued}).")

    # Compute per-fiber color counts across all C(q+1, 3) 3-column subsets of cols 0..q
    # Both on base_rows (Bush OA rows) and on the full array
    for scope_name, scope_rows in (("Bush-OA rows only", base_rows), ("Full array", rows)):
        min_colors = q + 1
        max_colors = 0
        universal_colors = set(range(q))
        color_min_cov: dict[int, int] = {m: 10**9 for m in range(q)}
        total_fibers = 0
        for c0, c1, c2 in combinations(range(q + 1), 3):
            fib: dict[tuple[int, int, int], set[int]] = defaultdict(set)
            for r in scope_rows:
                fib[(r[c0], r[c1], r[c2])].add(r[q + 1])
            # Count missing fibers (if base_rows incomplete)
            if len(fib) < q**3:
                min_colors = 0
                universal_colors.clear()
                for m in range(q):
                    color_min_cov[m] = 0
            for s in fib.values():
                ls = len(s)
                if ls < min_colors:
                    min_colors = ls
                if ls > max_colors:
                    max_colors = ls
                universal_colors &= s
            for m in range(q):
                cnt_m = sum(1 for s in fib.values() if m in s)
                if cnt_m < color_min_cov[m]:
                    color_min_cov[m] = cnt_m
            total_fibers += q**3
        print(
            f"  [{scope_name}] across {total_fibers} 3-tuple fibers on cols 0..{q}: "
            f"colors/fiber min={min_colors}, max={max_colors}; "
            f"universal colors (hit every 3-tuple fiber) = {sorted(universal_colors)} "
            f"(count={len(universal_colors)} vs. floor(q/2)={q // 2})"
        )
        if scope_name == "Bush-OA rows only":
            print(f"    min fibers hit per symbol (out of {q**3}): {color_min_cov}")

    # Also check how many rows of CA_3430 match the original Bush OA on cols 0..q-1 (degree-3 poly)
    # and how many Bush-OA rows changed col_{q+1} compared to the start array CA(3577)
    if q == 7:
        from gen_t4_odd_q_nearbush import _odd_sym_map_and_anchors
        gf = GF(7)
        sym_map, _, _ = _odd_sym_map_and_anchors(gf)
        add, mul, x2, x3 = gf.add, gf.mul, gf.x2, gf.x3
        poly_to_d: dict[tuple[int, ...], int] = {}
        bush_start_col8: dict[tuple[int, ...], int] = {}
        for a in range(7):
            for b in range(7):
                for c in range(7):
                    for d in range(7):
                        p = tuple(
                            add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                            for x in range(7)
                        )
                        poly_to_d[p] = d
                        bush_start_col8[p + (d,)] = sym_map[c * 7 + d]
        non_poly = sum(1 for r in rows if r[:7] not in poly_to_d)
        col_inf_match = sum(1 for r in rows if r[:7] in poly_to_d and r[7] == poly_to_d[r[:7]])
        col_inf_diff = sum(1 for r in rows if r[:7] in poly_to_d and r[7] != poly_to_d[r[:7]])
        mod_bush = sum(
            1 for pref, vals in prefix_to_vals.items() if vals[0] != bush_start_col8[pref]
        )
        print(
            f"  Poly-code check on cols 0..6: non_poly={non_poly}, col_inf==d (Bush OA rows)={col_inf_match}, "
            f"col_inf!=d (completion slices)={col_inf_diff}, modified Bush-OA col_8 vs. CA(3577)={mod_bush}/{q**4} ({mod_bush // (q*q)} slices of {q*q})"
        )


def main() -> None:
    t0 = time.perf_counter()
    p5888 = REPO_ROOT / "results" / "t4_nearbush" / "CA_5888_4_10_8.txt"
    p3430 = REPO_ROOT / "results" / "t4_nearbush" / "CA_3430_4_9_7.txt"

    rows_5888 = load_rows(p5888)
    analyze_5888_vs_6144(rows_5888)
    analyze_7203_vs_8192()
    check_thm37("CA(5888; 4, 10, 8)", p5888, 8)
    check_thm37("CA(3430; 4, 9, 7)", p3430, 7)
    print(f"\nElapsed: {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    main()
