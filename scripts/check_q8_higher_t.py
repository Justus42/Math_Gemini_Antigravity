#!/usr/bin/env python3
"""Phase 5C: Exhaustive verification of the q = 8 irreducible-quadratic mechanism
for t = 4 (Gate 0 byte-identical positive control), t = 5 ((5, 10, 8)), and
t = 6 ((6, 10, 8)).

Pure Python (std-only), completely deterministic, zero heuristics.

Mathematical framework over GF(8) = GF(2)[x] / (x^3 + x + 1):
  - Main Bush OA(8^t; t, 9, 8) consists of all polynomials f(x) = sum_{i=0}^{t-1} a_i x^i
    evaluated at x in GF(8) (cols 0..7) and leading coefficient a_{t-1} (col 8 = inf).
  - For any monic irreducible quadratic g(x) = x^2 + alpha*x + beta over GF(8)
    (exact count: (8^2 - 8)/2 = 28), the quotient map Q_g(f) = f(x) mod g(x) maps
    GF(8)^t -> AG(2, 8) with (t - 2)-dimensional kernel
        ker(Q_g) = { h(x) * g(x) : deg(h) < t - 2 }  (size 8^{t-2}).
  - Every (t - 1)-column fiber of Bush OA(8^t; t, 9, 8) is an affine line whose
    direction polynomial e_S(x) splits into linear factors over GF(8), so g(x) does
    not divide e_S(x) and Q_g maps every such line onto an affine line of AG(2, 8).
  - Coloring AG(2, 8) with 4 disjoint 15-point minimal blocking sets {0, 1, 2, 3}
    plus 4 singleton free points {4, 5, 6, 7} covers all (t - 1)-tuples paired with
    m in {0, 1, 2, 3} inside the 8^t Bush rows.
  - To complete each free-point fiber f_0 + ker(Q_g) (size 8^{t-2}) for m in {4, 5, 6, 7}
    to an OA(8^{t-1}; t - 1, 9, 8) using 7 additional slices (total N = 8^t + 28 * 8^{t-2}:
    5888 for t=4, 47104 for t=5, 376832 for t=6), there must exist a vector
    w in GF(8)^9 \\ ker(Q_g) at Hamming distance >= 11 - t from ker(Q_g).
  - Because an OA(8^{t-1}; t - 1, 9, 8) has index lambda = 1, even a SINGLE extra row
    w outside ker(Q_g) avoids collisions on all C(9, t - 1) column (t - 1)-subsets
    if and only if G_ext = [G_ker; w] generates a linear [9, t - 1, 11 - t]_8 MDS code.
    Thus exhausting P(GF(8)^9 / ker(Q_g)) for all 28 irreducible quadratics g proves
    existence or non-existence for BOTH linear and nonlinear OA(8^{t-1}; t - 1, 9, 8)
    completions of any fiber Q_g^{-1}(p, q).
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations, product
from pathlib import Path
import time


# ---------------------------------------------------------------------------
# GF(8) = GF(2)[x] / (x^3 + x + 1), elements 0..7
# ---------------------------------------------------------------------------

def _gf8_mul(a: int, b: int) -> int:
    res = 0
    for _ in range(3):
        if b & 1:
            res ^= a
        hi = a & 4
        a = (a << 1) & 7
        if hi:
            a ^= 3  # x^3 = x + 1
        b >>= 1
    return res


GF8_MUL: tuple[tuple[int, ...], ...] = tuple(
    tuple(_gf8_mul(a, b) for b in range(8)) for a in range(8)
)
GF8_INV: tuple[int, ...] = (0,) + tuple(
    next(b for b in range(1, 8) if GF8_MUL[a][b] == 1) for a in range(1, 8)
)

def _gf8_pow(x: int, d: int) -> int:
    res = 1
    for _ in range(d):
        res = GF8_MUL[res][x]
    return res


GF8_POW: tuple[tuple[int, ...], ...] = tuple(
    tuple(_gf8_pow(x, d) for x in range(8)) for d in range(8)
)

# All 72 affine lines of AG(2, 8), points indexed as p = u*8 + v in 0..63
AG2_8_LINES: tuple[tuple[int, ...], ...] = tuple(
    tuple(c * 8 + y for y in range(8)) for c in range(8)
) + tuple(
    tuple(x * 8 + (GF8_MUL[m][x] ^ b) for x in range(8))
    for m in range(8)
    for b in range(8)
)
assert len(AG2_8_LINES) == 72

# 4 disjoint 15-point minimal blocking sets {0..3} + 4 singleton points {4,5,6,7} at (9,39,42,59)
K10_COLORING: tuple[int, ...] = (
    1, 1, 1, 0, 2, 1, 3, 1,
    0, 4, 3, 2, 2, 2, 3, 1,
    0, 3, 3, 0, 2, 0, 0, 1,
    1, 3, 2, 3, 0, 1, 1, 1,
    3, 3, 1, 0, 2, 0, 3, 5,
    1, 2, 6, 0, 3, 0, 3, 3,
    2, 2, 2, 1, 2, 2, 3, 0,
    0, 0, 0, 7, 1, 3, 2, 2,
)
K10_FREE_PTS: tuple[int, ...] = (9, 39, 42, 59)

EXPECTED_GATE0_SHA256 = "7d72bc894b54b7cffb388c030d1485372cde6af12afb016f19622feb8be2a802"


def verify_polychromatic_4(coloring: tuple[int, ...]) -> None:
    assert len(coloring) == 64
    for line in AG2_8_LINES:
        present = {coloring[p] for p in line}
        assert {0, 1, 2, 3}.issubset(present), f"Line {line} misses a color in {{0,1,2,3}}"


def all_monic_irred_quadratics_gf8() -> list[tuple[int, int]]:
    """Return all (alpha, beta) in GF(8)^2 such that g(x) = x^2 + alpha*x + beta has no root in GF(8)."""
    irreds: list[tuple[int, int]] = []
    for alpha in range(8):
        for beta in range(8):
            if all((GF8_POW[2][x] ^ GF8_MUL[alpha][x] ^ beta) != 0 for x in range(8)):
                irreds.append((alpha, beta))
    return irreds


def eval_bush_t(t: int, coeffs: tuple[int, ...]) -> tuple[int, ...]:
    """Evaluate Bush OA(8^t; t, 9, 8) codeword for f(x) = sum_{d=0}^{t-1} coeffs[d] * x^d."""
    r = []
    for x in range(8):
        val = 0
        for d in range(t):
            val ^= GF8_MUL[coeffs[d]][GF8_POW[d][x]]
        r.append(val)
    r.append(coeffs[t - 1])
    return tuple(r)


def poly_mod_quadratic(coeffs: tuple[int, ...], alpha: int, beta: int) -> tuple[int, int]:
    """Compute f(x) mod (x^2 + alpha*x + beta) = r0 + r1*x over GF(8)."""
    rem = list(coeffs)
    for deg in range(len(rem) - 1, 1, -1):
        c = rem[deg]
        if c:
            rem[deg] = 0
            rem[deg - 1] ^= GF8_MUL[c][alpha]
            rem[deg - 2] ^= GF8_MUL[c][beta]
    return (rem[0], rem[1])


def kernel_generator_matrix(t: int, alpha: int, beta: int) -> list[list[int]]:
    """Return the (t - 2) x 9 generator matrix G_ker of ker(Q_g) for g(x) = x^2 + alpha*x + beta.

    Basis rows correspond to h_d(x) = x^d * g(x) for d = 0, ..., t - 3:
      - col x in 0..7 : g(x) * x^d
      - col 8 (inf)   : 1 if d == t - 3 else 0 (leading x^{t-1} coefficient)
    """
    g_vals = [GF8_POW[2][x] ^ GF8_MUL[alpha][x] ^ beta for x in range(8)]
    mat: list[list[int]] = []
    for d in range(t - 2):
        row = [GF8_MUL[g_vals[x]][GF8_POW[d][x]] for x in range(8)]
        row.append(1 if d == t - 3 else 0)
        mat.append(row)
    return mat


def det_gf8(mat: list[list[int]]) -> int:
    """Exact determinant of an n x n matrix over GF(8) (characteristic 2)."""
    n = len(mat)
    m = [row[:] for row in mat]
    det = 1
    for c in range(n):
        piv = -1
        for i in range(c, n):
            if m[i][c]:
                piv = i
                break
        if piv == -1:
            return 0
        if piv != c:
            m[c], m[piv] = m[piv], m[c]
        val = m[c][c]
        det = GF8_MUL[det][val]
        inv = GF8_INV[val]
        row_c = [GF8_MUL[x][inv] for x in m[c]]
        for i in range(c + 1, n):
            f = m[i][c]
            if f:
                for j in range(c + 1, n):
                    m[i][j] ^= GF8_MUL[f][row_c[j]]
    return det


def precompute_minor_forms(
    g_ker: list[list[int]], t: int
) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """For every (t - 1)-subset S of {0..8}, compute the exact cofactor linear form
    L_S(w) = det([G_ker|_S; w|_S]) = sum_{j} coeff_j * w[col_j].

    Because w is normalized to have w[0..t-4] = 0 and w[8] = 0 (unique representative
    in GF(8)^9 / ker(Q_g)), we restrict the linear form to the free coordinates
    c in {t-3, ..., 7}.
    """
    free_start = t - 3
    m = t - 1
    forms: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for subset in combinations(range(9), m):
        # Compute cofactor for each position j in 0..m-1 with subset[j] in {free_start..7}
        cols_used: list[int] = []
        coeffs_used: list[int] = []
        for j, col in enumerate(subset):
            if free_start <= col <= 7:
                sub_cols = [subset[i] for i in range(m) if i != j]
                sub_mat = [[g_ker[r][c] for c in sub_cols] for r in range(m - 1)]
                cof = det_gf8(sub_mat)
                if cof:
                    cols_used.append(col - free_start)
                    coeffs_used.append(cof)
        assert cols_used, f"Degenerate minor form on subset {subset}"
        forms.append((tuple(cols_used), tuple(coeffs_used)))
    return forms


def build_general_t_array(
    t: int,
    alpha: int,
    beta: int,
    ext_w: tuple[int, ...],
) -> list[tuple[int, ...]]:
    """Build the N = 8^t + 28 * 8^{t-2} array for strength t, g(x) = x^2 + alpha*x + beta,
    and kernel extension vector ext_w (length 9).

    For t = 4, alpha = 1, beta = 1, ext_w = (g(x)*x^2 for x in 0..7, 0), this reproduces
    results/t4_nearbush/CA_5888_4_10_8.txt byte-identically.
    """
    verify_polychromatic_4(K10_COLORING)
    for idx, pt in enumerate(K10_FREE_PTS):
        assert K10_COLORING[pt] == 4 + idx

    g_vals = [GF8_POW[2][x] ^ GF8_MUL[alpha][x] ^ beta for x in range(8)]
    assert all(gv != 0 for gv in g_vals)

    rows: list[tuple[int, ...]] = []

    # 1) Main Bush OA(8^t; t, 9, 8) + col 9 = K10_COLORING[Q_g(f)]
    # Coordinate convention matching gen_t4_q8_nearbush.py for g(x) = x^2 + x + 1:
    #   (p, q) = (r0, r0 ^ r1) where f(x) mod g(x) = r0 + r1*x.
    # For general g(x) = x^2 + alpha*x + beta, f_0(x) = q0*x + p0*x^2 has
    #   r0 = beta*p0, r1 = q0 ^ alpha*p0, so p = r0/beta, q = r1 ^ alpha*p.
    inv_beta = GF8_INV[beta]
    for coeffs in product(range(8), repeat=t):
        r0, r1 = poly_mod_quadratic(coeffs, alpha, beta)
        p = GF8_MUL[r0][inv_beta]
        q = r1 ^ GF8_MUL[alpha][p]
        rows.append(eval_bush_t(t, coeffs) + (K10_COLORING[p * 8 + q],))

    # 2) Complete each symbol m in {4, 5, 6, 7} from its existing w = 0 slice with w in 1..7
    for idx, pt in enumerate(K10_FREE_PTS):
        m = 4 + idx
        p0, q0 = pt >> 3, pt & 7
        shift_coeffs = (0, q0, p0) + (0,) * (t - 3)
        shift = eval_bush_t(t, shift_coeffs)
        for w_scalar in range(1, 8):
            w_ext = [GF8_MUL[w_scalar][ext_w[c]] for c in range(9)]
            for h_coeffs in product(range(8), repeat=t - 2):
                r = []
                for x in range(8):
                    hx = 0
                    for d in range(t - 2):
                        hx ^= GF8_MUL[h_coeffs[d]][GF8_POW[d][x]]
                    r.append(shift[x] ^ GF8_MUL[hx][g_vals[x]] ^ w_ext[x])
                r.append(shift[8] ^ h_coeffs[t - 3] ^ w_ext[8])
                rows.append(tuple(r) + (m,))

    expected_n = (8 ** t) + 28 * (8 ** (t - 2))
    assert len(rows) == expected_n
    return rows


def write_array_and_sha256(path: Path, rows: list[tuple[int, ...]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            line = " ".join(str(x) for x in r) + "\n"
            fh.write(line)
            h.update(line.encode("utf-8"))
    return h.hexdigest()


def run_gate0(out_path: Path) -> None:
    """Gate 0: Byte-identical positive control reproducing CA(5888; 4, 10, 8)."""
    t0 = time.perf_counter()
    alpha, beta = 1, 1  # g(x) = x^2 + x + 1
    g_vals = [GF8_POW[2][x] ^ GF8_MUL[alpha][x] ^ beta for x in range(8)]
    ext_w = tuple(GF8_MUL[GF8_POW[2][x]][g_vals[x]] for x in range(8)) + (0,)
    rows = build_general_t_array(4, alpha, beta, ext_w)
    sha = write_array_and_sha256(out_path, rows)
    elapsed = time.perf_counter() - t0
    match = (sha == EXPECTED_GATE0_SHA256)
    print(
        f"[GATE 0] t=4 g(x)=x^2+x+1 N={len(rows)} sha256={sha} "
        f"expected={EXPECTED_GATE0_SHA256} match={match} elapsed={elapsed:.3f}s -> {out_path}"
    )
    if not match:
        raise SystemExit("GATE 0 FAILED: SHA-256 mismatch against results/t4_nearbush/CA_5888_4_10_8.txt")


def verify_witness_deficit_direct(
    t: int, alpha: int, beta: int, ext_w: tuple[int, ...]
) -> tuple[int, int]:
    """Direct brute-force tuple count on a single free-point symbol's 8^{t-1} rows
    (used as an exact cross-check of the cofactor-rank deficit formula).
    Returns (bad_subsets, missing_tuples_single_symbol).
    """
    g_vals = [GF8_POW[2][x] ^ GF8_MUL[alpha][x] ^ beta for x in range(8)]
    sym_rows: list[tuple[int, ...]] = []
    for w_scalar in range(8):
        w_ext = [GF8_MUL[w_scalar][ext_w[c]] for c in range(9)]
        for h_coeffs in product(range(8), repeat=t - 2):
            r = []
            for x in range(8):
                hx = 0
                for d in range(t - 2):
                    hx ^= GF8_MUL[h_coeffs[d]][GF8_POW[d][x]]
                r.append(GF8_MUL[hx][g_vals[x]] ^ w_ext[x])
            r.append(h_coeffs[t - 3] ^ w_ext[8])
            sym_rows.append(tuple(r))
    cols = [tuple(row[c] for row in sym_rows) for c in range(9)]
    req = 8 ** (t - 1)
    bad_subsets = 0
    missing = 0
    for s in combinations(range(9), t - 1):
        cov = len(set(zip(*(cols[c] for c in s))))
        if cov < req:
            bad_subsets += 1
            missing += req - cov
    return bad_subsets, missing


def run_exhaustive(t: int, cross_check_witness: bool = True) -> dict:
    """Exhaustively check ALL 28 monic irreducible quadratics g over GF(8) and ALL
    projective 1-dimensional extensions in P(GF(8)^9 / ker(Q_g)) for strength t.
    """
    t0 = time.perf_counter()
    irreds = all_monic_irred_quadratics_gf8()
    assert len(irreds) == 28, f"Expected 28 monic irreducible quadratics, got {len(irreds)}"

    quot_dim = 11 - t
    total_proj_per_g = (8 ** quot_dim - 1) // 7
    free_len = 8 - (t - 3)  # coordinates x in {t-3 .. 7}
    nonzero_norm_per_g = 7 ** (free_len - 1)  # w_{t-3} = 1, remaining in GF(8)*
    trivial_zero_per_g = total_proj_per_g - nonzero_norm_per_g
    num_minors = len(list(combinations(range(9), t - 1)))
    unc_per_bad_minor = 7 * (8 ** (t - 2))

    mul = GF8_MUL
    total_hits = 0
    global_min_bad = num_minors + 1
    global_best_witness: tuple[int, int, tuple[int, ...]] | None = None
    per_g_summary: list[tuple[int, int, int, int]] = []

    for alpha, beta in irreds:
        g_ker = kernel_generator_matrix(t, alpha, beta)
        # Verify G_ker itself is MDS of rank t - 2 on every (t - 2)-subset
        forms = precompute_minor_forms(g_ker, t)
        assert len(forms) == num_minors

        # Split forms into length-2, length-3, general for tight inner loop
        # Pre-pack into flat tuples for speed in pure Python
        hits_g = 0
        min_bad_g = num_minors + 1
        best_tail_g: tuple[int, ...] | None = None

        for tail in product(range(1, 8), repeat=free_len - 1):
            vec = (1,) + tail
            bad = 0
            limit = min_bad_g
            for cols_u, coeffs_u in forms:
                acc = 0
                for idx in range(len(cols_u)):
                    acc ^= mul[coeffs_u[idx]][vec[cols_u[idx]]]
                if acc == 0:
                    bad += 1
                    if bad > limit:
                        break
            if bad == 0:
                hits_g += 1
            if bad < min_bad_g:
                min_bad_g = bad
                best_tail_g = vec

        total_hits += hits_g
        per_g_summary.append((alpha, beta, hits_g, min_bad_g))
        if min_bad_g < global_min_bad and best_tail_g is not None:
            global_min_bad = min_bad_g
            full_w = (0,) * (t - 3) + best_tail_g + (0,)
            global_best_witness = (alpha, beta, full_w)

    elapsed = time.perf_counter() - t0
    target_n = (8 ** t) + 28 * (8 ** (t - 2))
    min_unc_single = global_min_bad * unc_per_bad_minor
    min_unc_total = 4 * min_unc_single

    print(f"=== EXHAUSTIVE q=8 CHECK: t={t}, k=10, target N={target_n} ===")
    print(f"  monic irreducible quadratics g over GF(8) : {len(irreds)}")
    print(f"  quotient space dim(GF(8)^9 / ker(Q_g))    : {quot_dim}")
    print(f"  projective extensions per g               : {total_proj_per_g}")
    print(f"    - trivial zero-coordinate rejects       : {trivial_zero_per_g}")
    print(f"    - normalized nonzero-tail evaluated     : {nonzero_norm_per_g}")
    print(f"  total projective space (28 * {total_proj_per_g}) : {28 * total_proj_per_g}")
    print(f"  total nonzero-tail evaluated (28 * {nonzero_norm_per_g}) : {28 * nonzero_norm_per_g}")
    print(f"  C(9, {t-1}) minors per candidate           : {num_minors}")
    print(f"  total MDS hits across all 28 g            : {total_hits}")
    print(f"  min singular minors per symbol            : {global_min_bad} / {num_minors}")
    print(f"  min uncovered (t-1)-tuples per symbol     : {min_unc_single} (= {global_min_bad} * {unc_per_bad_minor})")
    print(f"  min uncovered t-tuples in N={target_n} array : {min_unc_total} (= 4 * {min_unc_single})")
    if global_best_witness is not None:
        wa, wb, ww = global_best_witness
        print(f"  witness (alpha={wa}, beta={wb}, w={list(ww)})")
        if cross_check_witness and t <= 6:
            b_sub, b_miss = verify_witness_deficit_direct(t, wa, wb, ww)
            assert b_sub == global_min_bad and b_miss == min_unc_single, (
                f"Cross-check mismatch: direct=({b_sub}, {b_miss}) vs formula=({global_min_bad}, {min_unc_single})"
            )
            print(f"  direct 8^{t-1}-row witness cross-check    : EXACT MATCH ({b_sub} bad subsets, {b_miss} missing tuples)")
    # Verify uniformity across all 28 irreducible quadratics (scaling invariance check)
    hits_set = {x[2] for x in per_g_summary}
    min_bad_set = {x[3] for x in per_g_summary}
    print(f"  uniformity across all 28 g                : hits_per_g={sorted(hits_set)}, min_bad_per_g={sorted(min_bad_set)}")
    print(f"  elapsed                                   : {elapsed:.3f}s")

    return {
        "t": t,
        "irreds": len(irreds),
        "total_proj": 28 * total_proj_per_g,
        "total_eval": 28 * nonzero_norm_per_g,
        "total_hits": total_hits,
        "min_bad": global_min_bad,
        "min_unc_single": min_unc_single,
        "min_unc_total": min_unc_total,
        "witness": global_best_witness,
        "elapsed": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exhaustive q=8 irreducible-quadratic mechanism check for t=4, 5, 6"
    )
    parser.add_argument(
        "--mode",
        choices=["gate0", "exhaustive"],
        required=True,
        help="gate0: byte-identical t=4 positive control; exhaustive: full search over all 28 g",
    )
    parser.add_argument("--t", type=int, choices=[4, 5, 6], default=5, help="Strength t for exhaustive mode")
    parser.add_argument("--out", type=Path, help="Output file path for gate0")
    args = parser.parse_args()

    if args.mode == "gate0":
        if args.out is None:
            raise SystemExit("--out is required for --mode gate0")
        run_gate0(args.out)
    else:
        run_exhaustive(args.t)


if __name__ == "__main__":
    main()
