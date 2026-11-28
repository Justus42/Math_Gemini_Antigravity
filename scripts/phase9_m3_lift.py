#!/usr/bin/env python3
"""Phase 9: Biaffine 3D model M_3(R_3) checker and coset lift for k = q + 3, 3 <= t <= q.

Pure Python (std-only) + GeneralGF from scripts/gen_general_tqv.py.

Mathematical specification:
  Kernel:
    K_t^(3) = { ((g(x))_{x in F_q}, 0, 0, 0) : deg g <= t - 4 }  (dim t - 3; {0} for t = 3).
  Representative list:
    R_3 subset F_q^6 of tuples (c0, c1, c2, a, b, c).
  Lift to strength t (3 <= t <= q):
    For each (c0, c1, c2, a, b, c) in R_3 and each g(X) with deg g <= t - 4:
      f(X) = g(X) + c0 * X^(t-3) + c1 * X^(t-2) + c2 * X^(t-1)
      row = ( (f(x))_{x in F_q}, a, b, c )  ->  N = |R_3| * q^(t-3), k = q + 3.

  Exact M_3 conditions (mode 'tspec' for fixed t, or 'full-bg3' for all 3 <= t <= q):
    (0) Typ 0: every (c0, c1, c2) in F_q^3 occurs >= 1 time in R_3.
    (1) Typ 1: for each u in {a, b, c}, s in F_q, (v, w, 1) in D_1:
               {(c0 - v*c2, c1 - w*c2) : u = s} has size q^2.
               tspec:    D_1 = {(e2(S), -e1(S), 1) : S in C(F_q, t-1)}
               full-bg3: D_1 = {(v, w, 1) : (v, w) in F_q^2}
    (2) Typ 2: for each {u1, u2} in {{a,b}, {a,c}, {b,c}}, (s1, s2) in F_q^2,
               (1, al, be) in N_2:
               {c0 + al*c1 + be*c2 : (u1, u2) = (s1, s2)} has size q.
               tspec:    N_2 = {(1, e1(U), e1(U)^2 - e2(U)) : U in C(F_q, t-2)}
               full-bg3: N_2 = {(1, al, be) : (al, be) in F_q^2}
    (3) Typ 3: every (a, b, c) in F_q^3 occurs >= 1 time in R_3.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF  # noqa: E402


class FieldOps:
    """Precomputed arithmetic tables for GF(q) backed by GeneralGF."""

    def __init__(self, q: int) -> None:
        self.gf = GeneralGF(q)
        self.q = q
        self.add = self.gf.add
        self.mul = self.gf.mul
        neg = [0] * q
        for x in range(q):
            for y in range(q):
                if self.add[x][y] == 0:
                    neg[x] = y
                    break
        self.neg = tuple(neg)
        self.sub = tuple(tuple(self.add[x][neg[y]] for y in range(q)) for x in range(q))


def read_reps(path: str | Path, q: int, allow_dups: bool = False) -> list[tuple[int, int, int, int, int, int]]:
    reps: list[tuple[int, int, int, int, int, int]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 6:
                sys.exit(f"{path}:{line_no}: expected 6 integers, got {len(parts)}")
            vals = tuple(int(x) for x in parts)
            if not all(0 <= z < q for z in vals):
                sys.exit(f"{path}:{line_no}: value out of range 0..{q - 1}: {vals}")
            reps.append(vals)  # type: ignore[arg-type]
    if not reps:
        sys.exit(f"{path}: empty representative list")
    if not allow_dups and len(set(reps)) != len(reps):
        sys.exit(f"{path}: duplicate representatives found ({len(reps) - len(set(reps))} duplicates)")
    return reps


def write_reps(path: str | Path, reps: list[tuple[int, int, int, int, int, int]]) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with open(p, "w", encoding="utf-8") as fh:
        for r in reps:
            line = " ".join(str(x) for x in r) + "\n"
            fh.write(line)
            h.update(line.encode("utf-8"))
    return h.hexdigest()


def make_r_base_q5() -> list[tuple[int, int, int, int, int, int]]:
    """Linear base R_base for q = 5: (c0, c1, c2, c2, c0, (c0 + c1 + 2*c2) mod 5)."""
    q = 5
    reps = []
    for c0 in range(q):
        for c1 in range(q):
            for c2 in range(q):
                a = c2
                b = c0
                c = (c0 + c1 + 2 * c2) % q
                reps.append((c0, c1, c2, a, b, c))
    return reps


def directions_and_normals(
    ops: FieldOps, mode: str, t: int | None
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return sorted unique D_1 = [(v, w), ...] and N_2 = [(al, be), ...]."""
    q = ops.q
    add, sub, neg, mul = ops.add, ops.sub, ops.neg, ops.mul
    if mode == "full-bg3":
        d1 = [(v, w) for v in range(q) for w in range(q)]
        n2 = [(al, be) for al in range(q) for be in range(q)]
        return d1, n2
    if mode == "tspec":
        if t is None or not (3 <= t <= q):
            raise ValueError(f"--mode tspec requires 3 <= t <= q (got t={t}, q={q})")
        d1_set: set[tuple[int, int]] = set()
        for subset in itertools.combinations(range(q), t - 1):
            e1 = 0
            for x in subset:
                e1 = add[e1][x]
            e2 = 0
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    e2 = add[e2][mul[subset[i]][subset[j]]]
            d1_set.add((e2, neg[e1]))

        n2_set: set[tuple[int, int]] = set()
        for subset in itertools.combinations(range(q), t - 2):
            e1 = 0
            for x in subset:
                e1 = add[e1][x]
            e2 = 0
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    e2 = add[e2][mul[subset[i]][subset[j]]]
            al = e1
            be = sub[mul[e1][e1]][e2]
            n2_set.add((al, be))

        return sorted(d1_set), sorted(n2_set)
    raise ValueError(f"unknown mode: {mode}")


def check_m3(
    reps: list[tuple[int, int, int, int, int, int]],
    ops: FieldOps,
    mode: str,
    t: int | None = None,
) -> dict[str, int]:
    """Check all four M_3 conditions (0)-(3) exactly and return detailed missing counts."""
    q = ops.q
    add, sub, mul = ops.add, ops.sub, ops.mul
    d1, n2 = directions_and_normals(ops, mode, t)

    # Typ 0: (c0, c1, c2) in F_q^3
    pts0 = {(r[0], r[1], r[2]) for r in reps}
    miss0 = q * q * q - len(pts0)

    # Typ 1: u in {a, b, c}, s in F_q, (v, w, 1) in D_1
    miss1 = 0
    fail_sets1 = 0
    for u_idx in (3, 4, 5):
        buckets: list[list[tuple[int, int, int]]] = [[] for _ in range(q)]
        for r in reps:
            buckets[r[u_idx]].append((r[0], r[1], r[2]))
        for v, w in d1:
            set_miss = 0
            for s in range(q):
                seen = {(sub[c0][mul[v][c2]], sub[c1][mul[w][c2]]) for c0, c1, c2 in buckets[s]}
                set_miss += q * q - len(seen)
            miss1 += set_miss
            if set_miss > 0:
                fail_sets1 += 1

    # Typ 2: {u1, u2} in {{a,b}, {a,c}, {b,c}}, (s1, s2) in F_q^2, (1, al, be) in N_2
    miss2 = 0
    fail_sets2 = 0
    for u1_idx, u2_idx in ((3, 4), (3, 5), (4, 5)):
        pbuckets: list[list[tuple[int, int, int]]] = [[] for _ in range(q * q)]
        for r in reps:
            pbuckets[r[u1_idx] * q + r[u2_idx]].append((r[0], r[1], r[2]))
        for al, be in n2:
            set_miss = 0
            for sp in range(q * q):
                seen = {add[add[c0][mul[al][c1]]][mul[be][c2]] for c0, c1, c2 in pbuckets[sp]}
                set_miss += q - len(seen)
            miss2 += set_miss
            if set_miss > 0:
                fail_sets2 += 1

    # Typ 3: (a, b, c) in F_q^3
    pts3 = {(r[3], r[4], r[5]) for r in reps}
    miss3 = q * q * q - len(pts3)

    return {
        "miss0": miss0,
        "miss1": miss1,
        "miss2": miss2,
        "miss3": miss3,
        "total": miss0 + miss1 + miss2 + miss3,
        "num_d1": len(d1),
        "num_n2": len(n2),
        "fail_sets1": fail_sets1,
        "fail_sets2": fail_sets2,
    }


def lift_rows(
    reps: list[tuple[int, int, int, int, int, int]],
    ops: FieldOps,
    t: int,
) -> list[tuple[int, ...]]:
    """Generate the lifted CA(N; t, q+3, q) rows in memory."""
    q = ops.q
    if not (3 <= t <= q):
        raise ValueError(f"need 3 <= t <= q (got t={t}, q={q})")
    add, mul = ops.add, ops.mul
    pw = [[1] * q]
    for _ in range(1, t):
        pw.append([mul[pw[-1][x]][x] for x in range(q)])

    # Precompute all kernel polynomial evaluations g(x) for deg g <= t - 4
    kdim = t - 3
    g_evals: list[tuple[int, ...]] = []
    if kdim == 0:
        g_evals.append(tuple([0] * q))
    else:
        for g_coeffs in itertools.product(range(q), repeat=kdim):
            ev = []
            for x in range(q):
                s = 0
                for e in range(kdim):
                    s = add[s][mul[g_coeffs[e]][pw[e][x]]]
                ev.append(s)
            g_evals.append(tuple(ev))

    pw0, pw1, pw2 = pw[t - 3], pw[t - 2], pw[t - 1]
    rows: list[tuple[int, ...]] = []
    for c0, c1, c2, a, b, c in reps:
        top = [
            add[add[mul[c0][pw0[x]]][mul[c1][pw1[x]]]][mul[c2][pw2[x]]]
            for x in range(q)
        ]
        tail = (a, b, c)
        for ge in g_evals:
            rows.append(tuple(add[ge[x]][top[x]] for x in range(q)) + tail)
    return rows


def write_lifted_ca(
    reps: list[tuple[int, int, int, int, int, int]],
    ops: FieldOps,
    t: int,
    out_path: str | Path,
) -> tuple[int, int, str]:
    rows = lift_rows(reps, ops, t)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with open(p, "w", encoding="utf-8") as fh:
        for row in rows:
            line = " ".join(str(x) for x in row) + "\n"
            fh.write(line)
            h.update(line.encode("utf-8"))
    return len(rows), ops.q + 3, h.hexdigest()


def exhaustive_ca_missing_by_type(
    rows: list[tuple[int, ...]], q: int, t: int
) -> dict[str, int]:
    """Independent exhaustive count of uncovered t-tuples across all C(q+3, t) column t-sets."""
    k = q + 3
    full = q ** t
    by_type = {0: 0, 1: 0, 2: 0, 3: 0}
    for cols in itertools.combinations(range(k), t):
        n_ext = sum(1 for c in cols if c >= q)
        seen = {tuple(r[c] for c in cols) for r in rows}
        by_type[n_ext] += full - len(seen)
    return {
        "miss0": by_type[0],
        "miss1": by_type[1],
        "miss2": by_type[2],
        "miss3": by_type[3],
        "total": sum(by_type.values()),
    }


def run_gate0() -> int:
    """Execute mandatory Gate-0 sanity checks before any search."""
    print("=== GATE-0 SANITY CHECK 1: q=5, t=4 linear base R_base (125 reps) ===")
    ops5 = FieldOps(5)
    r_base = make_r_base_q5()
    assert len(r_base) == 125
    res5 = check_m3(r_base, ops5, mode="tspec", t=4)
    print(
        f"  q=5 t=4 tspec: |R|={len(r_base)} |D1|={res5['num_d1']} |N2|={res5['num_n2']} "
        f"Typ0={res5['miss0']} Typ1={res5['miss1']} Typ2={res5['miss2']} "
        f"(fail_sets2={res5['fail_sets2']}) Typ3={res5['miss3']} total={res5['total']}"
    )
    ok1 = (
        res5["miss0"] == 0
        and res5["miss1"] == 0
        and res5["miss3"] == 0
        and res5["miss2"] == 600
        and res5["fail_sets2"] == 6
    )
    if not ok1:
        print("  FAIL: expected Typ0=0, Typ1=0, Typ3=0, Typ2=600 (6 failing 4-sets x 100)")
        return 1
    # Also cross-check lifted q=5, t=4 R_base array exhaustively!
    rows5 = lift_rows(r_base, ops5, t=4)
    ex5 = exhaustive_ca_missing_by_type(rows5, q=5, t=4)
    # For q=5, t=4: each missing M_3 interaction scales by q^(t-3) = 5 in lifted array
    print(
        f"  Exhaustive lifted CA({len(rows5)}; 4, 8, 5): "
        f"Typ0={ex5['miss0']} Typ1={ex5['miss1']} Typ2={ex5['miss2']} Typ3={ex5['miss3']} "
        f"(expected Typ2 = 600 * 5 = 3000)"
    )
    if not (ex5["miss0"] == 0 and ex5["miss1"] == 0 and ex5["miss3"] == 0 and ex5["miss2"] == 3000):
        print("  FAIL: lifted R_base exhaustive count mismatch!")
        return 1
    print("  CHECK 1 PASS")

    print("\n=== GATE-0 SANITY CHECK 2: q=3, t=3 (5 random small lists + 1 full-covered reference) ===")
    ops3 = FieldOps(3)
    rng = random.Random(20260901)
    all_pts6 = list(itertools.product(range(3), repeat=6))
    mismatches = 0

    for idx, m_size in enumerate([10, 18, 27, 36, 45], 1):
        sample_reps = rng.sample(all_pts6, m_size)
        m3 = check_m3(sample_reps, ops3, mode="tspec", t=3)
        lifted = lift_rows(sample_reps, ops3, t=3)
        ex = exhaustive_ca_missing_by_type(lifted, q=3, t=3)
        match = (
            m3["miss0"] == ex["miss0"]
            and m3["miss1"] == ex["miss1"]
            and m3["miss2"] == ex["miss2"]
            and m3["miss3"] == ex["miss3"]
            and m3["total"] == ex["total"]
        )
        status = "OK" if match else "MISMATCH"
        print(
            f"  Random #{idx} (m={m_size}): "
            f"M3=({m3['miss0']},{m3['miss1']},{m3['miss2']},{m3['miss3']}; tot={m3['total']}) "
            f"EX=({ex['miss0']},{ex['miss1']},{ex['miss2']},{ex['miss3']}; tot={ex['total']}) -> {status}"
        )
        if not match:
            mismatches += 1

    # Fully covered reference list for q=3, t=3: e.g., union of 3 affine/elliptic-style blocks or
    # guaranteed full cover built deterministically by greedy/structured blocks
    # Construct a deterministic fully covered list for q=3, t=3 (start from two orthogonal linear bases + greedy cover)
    ref_reps: list[tuple[int, int, int, int, int, int]] = []
    # 1) Linear base 1: (c0, c1, c2, c0, c1, c2) -> 27 reps
    for c0 in range(3):
        for c1 in range(3):
            for c2 in range(3):
                ref_reps.append((c0, c1, c2, c0, c1, c2))
    # 2) Linear base 2: (c0, c1, c2, (c0+c1)%3, (c1+c2)%3, (c0+2*c2)%3) -> 27 reps (deduplicated)
    seen_ref = set(ref_reps)
    for c0 in range(3):
        for c1 in range(3):
            for c2 in range(3):
                cand = (c0, c1, c2, (c0 + c1) % 3, (c1 + c2) % 3, (c0 + 2 * c2) % 3)
                if cand not in seen_ref:
                    seen_ref.add(cand)
                    ref_reps.append(cand)
    # 3) Add random remaining tuples deterministically until unc == 0 (full-bg3 and tspec t=3)
    while check_m3(ref_reps, ops3, mode="full-bg3")["total"] > 0:
        cand = rng.choice(all_pts6)
        if cand not in seen_ref:
            seen_ref.add(cand)
            ref_reps.append(cand)

    m3_ref_tspec = check_m3(ref_reps, ops3, mode="tspec", t=3)
    m3_ref_bg3 = check_m3(ref_reps, ops3, mode="full-bg3")
    lifted_ref = lift_rows(ref_reps, ops3, t=3)
    ex_ref = exhaustive_ca_missing_by_type(lifted_ref, q=3, t=3)
    match_ref = (
        m3_ref_tspec["total"] == 0
        and m3_ref_bg3["total"] == 0
        and ex_ref["total"] == 0
    )
    print(
        f"  Full-covered ref (m={len(ref_reps)}): "
        f"M3_tspec=({m3_ref_tspec['miss0']},{m3_ref_tspec['miss1']},{m3_ref_tspec['miss2']},{m3_ref_tspec['miss3']}) "
        f"M3_bg3=({m3_ref_bg3['miss0']},{m3_ref_bg3['miss1']},{m3_ref_bg3['miss2']},{m3_ref_bg3['miss3']}) "
        f"EX=({ex_ref['miss0']},{ex_ref['miss1']},{ex_ref['miss2']},{ex_ref['miss3']}) -> {'OK' if match_ref else 'MISMATCH'}"
    )
    if not match_ref:
        mismatches += 1

    # Bonus check: q=4, t=4 random small list (char 2 finite field!)
    ops4 = FieldOps(4)
    rng4 = random.Random(20260904)
    reps4 = [tuple(rng4.randrange(4) for _ in range(6)) for _ in range(60)]
    reps4 = list(dict.fromkeys(reps4))
    m3_4 = check_m3(reps4, ops4, mode="tspec", t=4)
    lifted4 = lift_rows(reps4, ops4, t=4)
    ex4 = exhaustive_ca_missing_by_type(lifted4, q=4, t=4)
    # Scaling factors for q=4, t=4:
    # Typ0: C(4,4)*4 = 4, Typ1: 1*4 = 4 (4 distinct D1), Typ2: 1*4 = 4 (6 distinct N2), Typ3: C(4,1)*4 = 16
    match4 = (
        ex4["miss0"] == m3_4["miss0"] * 4
        and ex4["miss1"] == m3_4["miss1"] * 4
        and ex4["miss2"] == m3_4["miss2"] * 4
        and ex4["miss3"] == m3_4["miss3"] * 16
    )
    print(
        f"  Bonus GF(4) t=4 (m={len(reps4)}): "
        f"M3=({m3_4['miss0']},{m3_4['miss1']},{m3_4['miss2']},{m3_4['miss3']}) "
        f"EX=({ex4['miss0']},{ex4['miss1']},{ex4['miss2']},{ex4['miss3']}) -> {'OK' if match4 else 'MISMATCH'}"
    )
    if not match4:
        mismatches += 1

    print(f"\nGATE-0 SUMMARY: {mismatches} mismatches -> {'PASS' if mismatches == 0 else 'FAIL'}")
    return 0 if mismatches == 0 else 1


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase 9 M_3(R_3) checker and coset lift (k = q + 3)")
    ap.add_argument("--q", type=int, help="prime power q >= 3")
    ap.add_argument("--reps", help="path to representative list (6 integers per line: c0 c1 c2 a b c)")
    ap.add_argument("--allow-dups", action="store_true", help="allow duplicate representatives")
    ap.add_argument("--check-m3", action="store_true", help="check M_3 conditions (0)-(3)")
    ap.add_argument("--mode", choices=["tspec", "full-bg3"], default="tspec", help="M_3 check mode")
    ap.add_argument("--t", type=int, help="strength t (3 <= t <= q)")
    ap.add_argument("--lift", action="store_true", help="lift R_3 to CA(N; t, q+3, q)")
    ap.add_argument("--out", help="output file path for --lift or --write-rbase-q5")
    ap.add_argument("--write-rbase-q5", action="store_true", help="write linear base R_base for q=5 to --out")
    ap.add_argument("--gate0", action="store_true", help="run mandatory Gate-0 sanity checks")
    args = ap.parse_args()

    if args.gate0:
        sys.exit(run_gate0())

    if args.write_rbase_q5:
        if not args.out:
            sys.exit("--write-rbase-q5 requires --out")
        reps = make_r_base_q5()
        sha = write_reps(args.out, reps)
        print(f"wrote R_base (q=5, m={len(reps)}) -> {args.out} sha256={sha}")
        return

    if args.q is None or args.reps is None:
        sys.exit("need --q and --reps (or --gate0 / --write-rbase-q5)")

    ops = FieldOps(args.q)
    reps = read_reps(args.reps, args.q, allow_dups=args.allow_dups)

    exit_code = 0
    if args.check_m3:
        res = check_m3(reps, ops, mode=args.mode, t=args.t)
        t_str = f" t={args.t}" if args.mode == "tspec" else ""
        print(
            f"M_3({args.mode}{t_str}) q={args.q} m={len(reps)} "
            f"|D1|={res['num_d1']} |N2|={res['num_n2']} | "
            f"Typ0={res['miss0']} Typ1={res['miss1']} (fail_sets={res['fail_sets1']}) "
            f"Typ2={res['miss2']} (fail_sets={res['fail_sets2']}) "
            f"Typ3={res['miss3']} | total_missing={res['total']}"
        )
        if res["total"] != 0:
            exit_code = 1

    if args.lift:
        if args.t is None or args.out is None:
            sys.exit("--lift requires --t and --out")
        n, k, sha = write_lifted_ca(reps, ops, args.t, args.out)
        print(f"lifted CA({n}; {args.t}, {k}, {args.q}) -> {args.out} sha256={sha}")

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
