#!/usr/bin/env python3
"""Phase 8 (Baustelle 2): Prime lower bound L_prim(p) via Blokhuis (1994) + generalized Prop. 1.5.

Pure Python (std-only). Computes exact integer lower bounds L_prim(p) for odd primes p,
compares against L'(p) and all prime (v = p) representative lists in data/phase7/,
data/phase8/, and data/phase8_repro/, and optionally decides p = 3, m = 11 exhaustively.

Usage:
  python3 scripts/phase8_prime_bound.py
  python3 scripts/phase8_prime_bound.py --check-p3
"""
from __future__ import annotations

import argparse
import glob
import itertools
import math
import os
import re
import sys
import time

PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
LIST_DIRS = ("data/phase7", "data/phase8", "data/phase8_repro")


def is_odd_prime(n: int) -> bool:
    if n < 3 or n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def l_prime_u(q: int) -> int:
    """Exact L'(q) = ceil(q^2 + (q^2 - q) / (sqrt(q) + 2)) using integer arithmetic."""
    def ok(E: int) -> bool:
        rhs = q * q - q - 2 * E
        return rhs <= 0 or q * E * E >= rhs * rhs

    E = max(0, int((q * q - q) / (math.sqrt(q) + 2)) - 2)
    while not ok(E):
        E += 1
    return q * q + E


def blokhuis_bound(p: int, f: int) -> int:
    """B(p, f) = f*p + (p - f)*(3*p + 1)//2 (Blokhuis 1994, odd prime p)."""
    return f * p + (p - f) * ((3 * p + 1) // 2)


def line_bound(p: int, f_a: int, f_b: int) -> tuple[int, tuple[int, int, int]]:
    """Exact LineBound(p, f_a, f_b) and minimizing (alpha, beta, k)."""
    best_val: int | None = None
    best_params = (0, 0, 0)
    p2 = p * p
    base = p2 + p * f_a + p * f_b

    for alpha in range(f_a + 1):
        rem_a = f_a - alpha
        for beta in range(f_b + 1):
            rem_b = f_b - beta
            if rem_a == 0 and rem_b == 0:
                rem_lines = p - alpha - beta
                if rem_lines < 0:
                    rem_lines = 0
                num = base + alpha * beta + p * rem_lines
                val = (num + 1) // 2
                if best_val is None or val < best_val:
                    best_val = val
                    best_params = (alpha, beta, 0)
                continue
            if rem_a == 0 or rem_b == 0:
                # k = 0 only allowed when alpha = f_a and beta = f_b; k >= 1 requires rem_a, rem_b >= 1
                continue

            ab = alpha * beta
            rem_prod = rem_a * rem_b
            rem_sum = rem_a + rem_b
            k_max = rem_a if rem_a < rem_b else rem_b
            # f(k) = p * max(0, p - alpha - beta - k) - (rem_prod - (k - 1)*(rem_sum - k))
            #      = p * max(0, C - k) - rem_prod + (k - 1)*(rem_sum - k)
            # Notice g(k) = (k - 1)*(rem_sum - k) = -k^2 + (rem_sum + 1)*k - rem_sum is CONCAVE in k!
            # On [1, min(k_max, C)], f(k) = p*C - p*k + g(k) is CONCAVE -> min is at endpoints {1, min(k_max, C)}!
            # On [max(1, C), k_max], f(k) = g(k) is CONCAVE -> min is at endpoints {max(1, C), k_max}!
            # Therefore the global minimum over k in 1..k_max is ALWAYS attained at one of at most 3 points:
            #   k = 1, k = k_max, and (if 1 < C < k_max) k = C = p - alpha - beta!
            c_break = p - alpha - beta
            cand_ks = (1, k_max, c_break) if 1 < c_break < k_max else (1, k_max)
            for k in cand_ks:
                s_max = rem_prod - (k - 1) * (rem_sum - k)
                rem_lines = c_break - k
                if rem_lines < 0:
                    rem_lines = 0
                num = base + ab + p * rem_lines - s_max
                val = (num + 1) // 2
                if best_val is None or val < best_val:
                    best_val = val
                    best_params = (alpha, beta, k)

    assert best_val is not None
    return best_val, best_params


def l_prim(p: int) -> tuple[int, tuple[int, int, int, int, int, int, int, int]]:
    """Compute exact L_prim(p) = min_{0 <= f_a <= f_b <= p} max(B(p, f_a), B(p, f_b), LineBound(p, f_a, f_b)).

    Returns (L_prim, (f_a, f_b, B_fa, B_fb, LB, alpha, beta, k)).
    """
    best_val: int | None = None
    best_info = (0, 0, 0, 0, 0, 0, 0, 0)
    b_vals = [blokhuis_bound(p, f) for f in range(p + 1)]

    # Scan f_a from p down to 0 so best_val tightens quickly and prunes high B(p, f_a)
    for f_a in range(p, -1, -1):
        ba = b_vals[f_a]
        if best_val is not None and ba >= best_val:
            break  # B(p, f_a) is strictly decreasing in f_a, so smaller f_a have even larger ba
        for f_b in range(f_a, p + 1):
            bb = b_vals[f_b]
            lb, (alpha, beta, k) = line_bound(p, f_a, f_b)
            val = ba if ba >= bb else bb
            if lb > val:
                val = lb
            if best_val is None or val < best_val:
                best_val = val
                best_info = (f_a, f_b, ba, bb, lb, alpha, beta, k)

    assert best_val is not None
    return best_val, best_info


def scan_prime_lists(repo_root: str) -> list[tuple[int, int, str]]:
    """Return list of (p, |R|, rel_path) for all prime v=p representative lists in LIST_DIRS."""
    found: list[tuple[int, int, str]] = []
    for d in LIST_DIRS:
        pattern = os.path.join(repo_root, d, "R_q*.txt")
        for path in sorted(glob.glob(pattern)):
            name = os.path.basename(path)
            m = re.match(r"R_q(\d+)(?:_v(\d+))?", name)
            if not m:
                continue
            q = int(m.group(1))
            v = int(m.group(2)) if m.group(2) else q
            if not is_odd_prime(q) or v != q:
                continue
            count = 0
            with open(path, encoding="utf-8") as fh:
                for ln in fh:
                    if ln.split("#")[0].strip():
                        count += 1
            rel = os.path.relpath(path, repo_root)
            found.append((q, count, rel))
    return found


def check_p3_m11_exhaustive(timeout_s: float = 60.0) -> tuple[str, int, float, dict[str, int]]:
    """100% exhaustive, symmetry-free-over-points exact check of whether M(R) with |R| = 11 exists for p = 3.

    Every valid R of size 11 must cover all 9 points of F_3^2 at least once, so the point
    multiset is one of:
      - 9 multisets with one point of multiplicity 3 and eight of multiplicity 1;
      - 36 multisets with two points of multiplicity 2 and seven of multiplicity 1.
    For each fixed point multiset of size 11, permuting the 3 symbols in column a independently
    of column b is a symmetry of M(R); thus WLOG the first symbol of a (resp. b) is 0 and the
    first symbol != 0 is 1. Every canonical valid a-vector and b-vector is enumerated completely.
    """
    t0 = time.perf_counter()
    pts = [(c, d) for d in range(3) for c in range(3)]  # 9 points

    # Precompute for each point index i in 0..8 the 3 line indices (al, (c + al*d) % 3)
    # Encoded as bitmask of 9 bits (al*3 + u)
    pt_line_mask = []
    for c, d in pts:
        mask = 0
        for al in range(3):
            u = (c + al * d) % 3
            mask |= 1 << (al * 3 + u)
        pt_line_mask.append(mask)

    # All 45 point multisets of size 11 covering all 9 points
    multisets: list[tuple[int, ...]] = []
    for i in range(9):
        multisets.append(tuple(range(9)) + (i, i))
    for i, j in itertools.combinations(range(9), 2):
        multisets.append(tuple(range(9)) + (i, j))
    assert len(multisets) == 45

    # Generate all canonical length-11 ternary vectors (first elem = 0, first non-zero = 1, all 3 symbols used)
    # Total count: (3^10 - 2^10 + 1) / 2? Let's generate recursively:
    canon_vecs: list[tuple[int, ...]] = []
    buf = [0] * 11

    def gen_canon(pos: int, max_used: int) -> None:
        if pos == 11:
            if max_used == 2:
                canon_vecs.append(tuple(buf))
            return
        # Prune if not enough positions left to reach max_used == 2
        if 2 - max_used > 11 - pos:
            return
        limit = min(2, max_used + 1)
        for val in range(limit + 1):
            buf[pos] = val
            gen_canon(pos + 1, max_used if val <= max_used else val)

    buf[0] = 0
    gen_canon(1, 0)
    # Sanity check count: Stirling S(11, 3) = (3^11 - 3*2^11 + 3)/6 = (177147 - 6144 + 3)/6 = 28501
    assert len(canon_vecs) == 28501, f"Unexpected canon count: {len(canon_vecs)}"

    full_9 = (1 << 9) - 1
    total_valid_sides = 0
    total_pair_checks = 0
    found_sols = 0

    for ms_idx, ms in enumerate(multisets):
        if time.perf_counter() - t0 > timeout_s:
            return "TIMEOUT", found_sols, time.perf_counter() - t0, {
                "multisets_done": ms_idx,
                "total_valid_sides": total_valid_sides,
                "total_pair_checks": total_pair_checks,
            }
        masks = [pt_line_mask[p] for p in ms]
        m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10 = masks

        valid_sides: list[tuple[int, ...]] = []
        for vec in canon_vecs:
            c0 = c1 = c2 = 0
            # Unrolled for speed
            v = vec[0]
            if v == 0: c0 |= m0
            elif v == 1: c1 |= m0
            else: c2 |= m0
            v = vec[1]
            if v == 0: c0 |= m1
            elif v == 1: c1 |= m1
            else: c2 |= m1
            v = vec[2]
            if v == 0: c0 |= m2
            elif v == 1: c1 |= m2
            else: c2 |= m2
            v = vec[3]
            if v == 0: c0 |= m3
            elif v == 1: c1 |= m3
            else: c2 |= m3
            v = vec[4]
            if v == 0: c0 |= m4
            elif v == 1: c1 |= m4
            else: c2 |= m4
            v = vec[5]
            if v == 0: c0 |= m5
            elif v == 1: c1 |= m5
            else: c2 |= m5
            v = vec[6]
            if v == 0: c0 |= m6
            elif v == 1: c1 |= m6
            else: c2 |= m6
            v = vec[7]
            if v == 0: c0 |= m7
            elif v == 1: c1 |= m7
            else: c2 |= m7
            v = vec[8]
            if v == 0: c0 |= m8
            elif v == 1: c1 |= m8
            else: c2 |= m8
            v = vec[9]
            if v == 0: c0 |= m9
            elif v == 1: c1 |= m9
            else: c2 |= m9
            v = vec[10]
            if v == 0: c0 |= m10
            elif v == 1: c1 |= m10
            else: c2 |= m10

            if c0 == full_9 and c1 == full_9 and c2 == full_9:
                valid_sides.append(vec)

        total_valid_sides += len(valid_sides)

        # Check all pairs (a_vec, b_vec) from valid_sides
        # Note: if a_vec is valid and b_vec is valid, we need all 9 pairs (a_vec[i], b_vec[i])
        # Since a and b can be independently permuted, checking canonical a_vec against canonical b_vec
        # covers ALL pairs (a, b) because (sigma(a), tau(b)) covers all 9 pairs iff (a, b) covers all 9 pairs!
        # Wait: we must also check if a duplicate point has identical (a, b) — which only reduces covered pairs,
        # never increases them, so checking 9 distinct (a, b) pairs is necessary and sufficient (and a valid
        # solution cannot have duplicate (c,d,a,b) if we verify len(set(reps)) == 11; actually with 11 rows
        # and 9 distinct (a,b) pairs, even if duplicate (c,d,a,b) existed, removing it would give m=10!).
        n_vs = len(valid_sides)
        for ia in range(n_vs):
            va = valid_sides[ia]
            for ib in range(ia, n_vs):
                vb = valid_sides[ib]
                total_pair_checks += 1
                pmask = 0
                for idx in range(11):
                    pmask |= 1 << (va[idx] * 3 + vb[idx])
                if pmask == full_9:
                    found_sols += 1

    dt = time.perf_counter() - t0
    status = "UNSAT_EXACT" if found_sols == 0 else "SAT_EXACT"
    return status, found_sols, dt, {
        "multisets_done": len(multisets),
        "total_valid_sides": total_valid_sides,
        "total_pair_checks": total_pair_checks,
    }


def check_p3_m12_positive_control() -> tuple[bool, int, int]:
    """Positive control: verify known Phase-6A solution for p=3 has m=12, 0 uncovered pairs,
    AND verify the exact canonical-vector engine finds solutions on that m=12 point multiset."""
    reps = [(c, d, d, min(c, d)) for c in range(3) for d in range(3)] + [
        (c, d, c, d) for d in range(3) for c in range(d)
    ]
    rows = [[(c + al * d) % 3 for al in range(3)] + [a, b] for (c, d, a, b) in reps]
    miss = 0
    for i, j in itertools.combinations(range(5), 2):
        miss += 9 - len({(r[i], r[j]) for r in rows})
    if len(reps) != 12 or miss != 0:
        return False, len(reps), 0

    # Same-engine positive control on the m=12 point multiset of reps
    pts = [(c, d) for d in range(3) for c in range(3)]
    pt_to_idx = {p: i for i, p in enumerate(pts)}
    pt_line_mask = []
    for c, d in pts:
        mask = 0
        for al in range(3):
            mask |= 1 << (al * 3 + (c + al * d) % 3)
        pt_line_mask.append(mask)
    ms12 = [pt_to_idx[(c, d)] for (c, d, _, _) in reps]
    masks = [pt_line_mask[p] for p in ms12]
    full_9 = (1 << 9) - 1

    buf = [0] * 12
    valid_sides: list[tuple[int, ...]] = []

    def gen_check(pos: int, max_used: int, c0: int, c1: int, c2: int) -> None:
        if pos == 12:
            if max_used == 2 and c0 == full_9 and c1 == full_9 and c2 == full_9:
                valid_sides.append(tuple(buf))
            return
        if 2 - max_used > 12 - pos:
            return
        m = masks[pos]
        limit = min(2, max_used + 1)
        for val in range(limit + 1):
            buf[pos] = val
            nm = max_used if val <= max_used else val
            if val == 0:
                gen_check(pos + 1, nm, c0 | m, c1, c2)
            elif val == 1:
                gen_check(pos + 1, nm, c0, c1 | m, c2)
            else:
                gen_check(pos + 1, nm, c0, c1, c2 | m)

    buf[0] = 0
    gen_check(1, 0, masks[0], 0, 0)
    sols12 = 0
    for ia, va in enumerate(valid_sides):
        for ib in range(ia, len(valid_sides)):
            vb = valid_sides[ib]
            pmask = 0
            for idx in range(12):
                pmask |= 1 << (va[idx] * 3 + vb[idx])
            if pmask == full_9:
                sols12 += 1
    return (sols12 > 0), len(reps), sols12


def main() -> None:
    ap = argparse.ArgumentParser(description="Prime lower bound L_prim(p) (Blokhuis + gen. Prop. 1.5).")
    ap.add_argument("--check-p3", action="store_true", help="Exhaustively decide p = 3, m = 11 (std-only).")
    ap.add_argument("--p3-timeout", type=float, default=60.0, help="Hard timeout in seconds for p = 3 check.")
    args = ap.parse_args()

    t_start = time.perf_counter()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prime_lists = scan_prime_lists(repo_root)

    # Best list per prime in repo
    best_by_p: dict[int, tuple[int, str]] = {}
    for p, m, rel in prime_lists:
        if p not in best_by_p or m < best_by_p[p][0]:
            best_by_p[p] = (m, rel)

    # Compute L_prim(p) for all requested primes (plus any prime in repo lists if outside PRIMES)
    all_primes = sorted(set(PRIMES) | {p for p, _, _ in prime_lists})
    results: dict[int, tuple[int, int, tuple[int, int, int, int, int, int, int, int]]] = {}
    for p in all_primes:
        lp_u = l_prime_u(p)
        lp_p, info = l_prim(p)
        results[p] = (lp_u, lp_p, info)

    # Check violations across ALL prime lists (v = p)
    violations = 0
    for p, m, rel in prime_lists:
        _, lp_p, _ = results[p]
        if m < lp_p:
            violations += 1
            print(f"VIOLATION: {rel} has |R|={m} < L_prim({p})={lp_p}", file=sys.stderr)

    dt_bound = time.perf_counter() - t_start

    print("| p | L'(p) | L_prim(p) | L_prim(p)/p^2 | opt (f_a, f_b; alpha, beta, k) | beste Liste im Repo | Abstand |")
    print("| ---: | ---: | ---: | ---: | --- | --- | ---: |")
    for p in PRIMES:
        lp_u, lp_p, info = results[p]
        f_a, f_b, ba, bb, lb, alpha, beta, k = info
        ratio = lp_p / (p * p)
        if p in best_by_p:
            bm, brel = best_by_p[p]
            best_str = f"`{os.path.basename(brel)}` ({bm})"
            gap_str = str(bm - lp_p)
        else:
            best_str = "–"
            gap_str = "–"
        print(
            f"| {p} | {lp_u} | {lp_p} | {ratio:.4f} | "
            f"({f_a}, {f_b}; {alpha}, {beta}, {k}) [B={ba}/{bb}, LB={lb}] | {best_str} | {gap_str} |"
        )

    print(
        f"\nGepruefte Primzahl-Listen (v = p) in {', '.join(LIST_DIRS)}: {len(prime_lists)}; "
        f"Verletzungen: {violations}; Rechenzeit L_prim: {dt_bound:.4f}s"
    )
    for p, m, rel in prime_lists:
        _, lp_p, _ = results[p]
        print(f"  - {rel}: p={p}, |R|={m}, L_prim({p})={lp_p}, Abstand={m - lp_p}")

    if violations > 0:
        sys.exit(1)

    if args.check_p3:
        pc_ok, pc_m, sols12 = check_p3_m12_positive_control()
        print(
            f"\nPositivkontrolle p=3 m={pc_m} (bekannte Liste + gleiche kanon. Engine): "
            f"{'PASS' if pc_ok else 'FAIL'} (kanon. Loesungspaare auf Phase-6A-Multimenge: {sols12})"
        )
        assert pc_ok
        status, sols, dt_p3, stats = check_p3_m11_exhaustive(timeout_s=args.p3_timeout)
        print(
            f"Exakte Entscheidung p=3, m=11 (std-only, alle 45 Punkt-Multimengen x 28501 kanon. Vektoren): "
            f"status={status}, solutions={sols}, time={dt_p3:.3f}s, "
            f"multisets={stats['multisets_done']}/45, valid_single_sides={stats['total_valid_sides']}, "
            f"pair_checks={stats['total_pair_checks']}"
        )


if __name__ == "__main__":
    main()
