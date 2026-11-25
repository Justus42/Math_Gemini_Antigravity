#!/usr/bin/env python3
"""Phase 5B-2C Step A.2: Empirical & structural q^2-slice analysis for q = 7 and q = 9.

Pure Python (std-only). Compares poly2-disjoint start arrays against reduced t4_postop
arrays without assuming any closed-form savings formula:
  - Symbol counts in col_{q+1} and joint (col_inf, col_{q+1}) counts (exact multiples of q^2?)
  - Bush degree-3 polynomial code preservation on cols 0..q-1 and Bush OA(q^4) fiber colors
  - Exact slice survival (intact / deleted / partial) against the start array
  - Structural lower bounds (per-symbol CA(3, q+1, q) >= q^3 and fixed-parabola 2nd divided-
    difference coverage).
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

from gen_t4_odd_q_nearbush import GF, _odd_sym_map_and_anchors  # noqa: E402


def load_rows(path: Path) -> list[tuple[int, ...]]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                rows.append(tuple(int(x) for x in s.split()))
    return rows


def build_reference_maps(q: int):
    gf = GF(q)
    sym_map, anchors, _ = _odd_sym_map_and_anchors(gf)
    add, sub, mul, x2, x3 = gf.add, gf.sub, gf.mul, gf.x2, gf.x3
    c_b = (q - 1) // 2

    bush_prefix_to_cd: dict[tuple[int, ...], tuple[int, int]] = {}
    poly_prefix_to_cd: dict[tuple[int, ...], tuple[int, int]] = {}
    row_to_slice: dict[tuple[int, ...], str] = {}
    slice_rows: dict[str, list[tuple[int, ...]]] = defaultdict(list)

    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    p_fin = tuple(
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    )
                    bush_prefix_to_cd[p_fin + (d,)] = (c, d)
                    poly_prefix_to_cd[p_fin] = (c, d)
                    m = sym_map[c * q + d]
                    r = p_fin + (d, m)
                    kind = "parab" if (m == c_b and c == x2[d]) else ("bs" if m < c_b else "sing")
                    sname = f"main_{kind}_m{m}_c{c}_d{d}"
                    row_to_slice[r] = sname
                    slice_rows[sname].append(r)

    for m, anchor_pt in anchors:
        c0, d0 = divmod(anchor_pt, q)
        cd = sub[c0][d0]
        shift = [add[mul[cd][x2[x]]][mul[d0][x3[x]]] for x in range(q)]
        for cp in range(q):
            if cp == d0:
                continue
            sname = f"comp_m{m}_cp{cp}"
            for a in range(q):
                for b in range(q):
                    r = tuple(
                        add[add[add[a][mul[b][x]]][mul[cp][x2[x]]]][shift[x]]
                        for x in range(q)
                    ) + (cp, m)
                    row_to_slice[r] = sname
                    slice_rows[sname].append(r)

    return gf, bush_prefix_to_cd, poly_prefix_to_cd, row_to_slice, slice_rows


def analyze_structural_bounds(gf: GF) -> None:
    q = gf.q
    add, mul, x2 = gf.add, gf.mul, gf.x2
    sums_present = sorted({add[add[x0][x1]][x2_i] for x0, x1, x2_i in combinations(range(q), 3)})
    uncovered_by_parab = {
        S: set(range(q)) - {add[x2[d]][mul[d][S]] for d in range(q)} for S in sums_present
    }
    need_count = {cp: sum(1 for unc in uncovered_by_parab.values() if cp in unc) for cp in range(q)}
    print(f"\n--- Structural bounds for q={q} (k={q+2}) ---")
    print(f"  3-col sums S present: {len(sums_present)}/{q}; parabola misses {sorted({len(u) for u in uncovered_by_parab.values()})} div-diff classes per S")
    print(f"  Sums S requiring completion value cp (0..{q-1}): {need_count}")
    print(
        f"  Hard CA(3,q+1,q) floor per symbol: N_m >= {q**3} ({q} slices of q^2={q*q}). "
        f"Start slack above q^4: {(q*q-1)//2} slices total ({q-1} on m*, {q-1} per BS, 0 per singleton)."
    )


def analyze_array(
    gf: GF,
    label: str,
    path: Path,
    bush_map: dict[tuple[int, ...], tuple[int, int]],
    poly_map: dict[tuple[int, ...], tuple[int, int]],
    row_to_slice: dict[tuple[int, ...], str],
    slice_rows: dict[str, list[tuple[int, ...]]],
) -> None:
    q = gf.q
    q2 = q * q
    k = q + 2
    rows = load_rows(path)
    n = len(rows)
    start_n = q**4 + ((q2 - 1) // 2) * q2
    saved = start_n - n

    sym_cnt = Counter(r[k - 1] for r in rows)
    joint = Counter((r[q], r[k - 1]) for r in rows)
    non_mult = sum(1 for c in joint.values() if c % q2 != 0)

    row_set = Counter(rows)
    intact = deleted = partial = 0
    deleted_names = []
    for sname, srows in sorted(slice_rows.items()):
        kept = sum(1 for r in srows if row_set[r] > 0)
        if kept == q2:
            intact += 1
        elif kept == 0:
            deleted += 1
            deleted_names.append(sname)
        else:
            partial += 1

    bush_rows = [r for r in rows if r[: q + 1] in bush_map]
    extra_rows = [r for r in rows if r[: q + 1] not in bush_map]
    non_poly = sum(1 for r in rows if r[:q] not in poly_map)

    fiber_cols: dict[tuple[int, int], Counter[int]] = defaultdict(Counter)
    for r in bush_rows:
        fiber_cols[bush_map[r[: q + 1]]][r[k - 1]] += 1
    pure_fibers = sum(1 for v in fiber_cols.values() if len(v) == 1 and next(iter(v.values())) == q2)

    print(f"\n=== {label}: {path} (N={n}, saved={saved} = {saved / q2:.2f}*q^2) ===")
    print("  col_{q+1} counts (in q^2):", {m: f"{sym_cnt[m]} ({sym_cnt[m]/q2:.2f}q^2)" for m in range(q)})
    print(f"  (col_inf, col_{{q+1}}) non-multiples of q^2: {non_mult}")
    print(f"  Start-slice survival: intact={intact}/{len(slice_rows)}, deleted={deleted}, partial={partial}")
    print(f"  Bush OA(q^4) rows={len(bush_rows)}/{q**4} (pure {q2}-fibers={pure_fibers}/{q2}), extra={len(extra_rows)}, non-poly rows={non_poly}")
    print(f"  Deleted start slices ({len(deleted_names)}): {deleted_names}")


def main() -> None:
    t0 = time.perf_counter()
    targets = {
        7: [
            ("CA_3479 (5B-2B, 2T)", Path("results/t4_nearbush/CA_3479_4_9_7.txt")),
            ("CA_3430 (5B-2C, 1T)", Path("results/t4_nearbush/CA_3430_4_9_7.txt")),
        ],
        9: [
            ("CA_9639 (5B-2B, 2T)", Path("results/t4_nearbush/CA_9639_4_11_9.txt")),
            ("CA_9558 (5B-2C, 1T)", Path("results/t4_nearbush/CA_9558_4_11_9.txt")),
        ],
    }
    for q, items in targets.items():
        gf, bush_map, poly_map, r2s, srows = build_reference_maps(q)
        analyze_structural_bounds(gf)
        for label, path in items:
            if path.exists():
                analyze_array(gf, label, path, bush_map, poly_map, r2s, srows)
    print(f"\nDone in {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    main()
