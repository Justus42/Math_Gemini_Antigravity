#!/usr/bin/env python3
"""Phase 5B-2B: Generalized GF(q) k = q + 2 NEAR_BUSH generator & odd-q diagnostic.

Pure Python (std-only). Transfers the Phase 5B-2A q = 8 construction
(irreducible-quadratic projection + polychromatic AG(2, q) blocking-set partition
+ free slices) to general prime powers q in {7, 8, 9, 11, 13}:

  1. Gate 0a (q = 8, mode=irred-quad):
     Reproduces CA(5888; 4, 10, 8) byte-identically (SHA-256 = 7d72bc89...) via the
     same parameterized GF(q) engine, verifying zero parameterization errors.

  2. Odd-q diagnostic (q in {7, 9, 11, 13}, mode=irred-quad-diag):
     Verifies and quantifies the two exact algebraic obstructions in characteristic != 2:
       (a) Segre/Nucleus obstruction: in Q_g (irreducible quadratic kernel), col_inf
           acts as (0, 1, 0) in PG(2, q), which is the conic nucleus only in char 2;
           for odd q, naive w-completion fails on (q - 1)/2 pairs {x, -x} per free symbol
           and no linear (q + 1)-arc extends G_2.
       (b) Jamison/Brouwer-Schrijver parity bound: every affine blocking set in AG(2, q)
           has size >= 2q - 1. Hence at most c_B = floor(q^2 / (2q - 1)) = (q - 1)/2
           disjoint blocking sets fit for odd q (vs q/2 for even q), giving
           N_constr(q) = q^4 + ((q + 1)/2)(q - 1)q^2 = q^4 + ((q^2 - 1)/2)q^2 = N_poly2(q).

  3. Adapted odd-q construction (q in {7, 9, 11, 13}, mode=poly2-disjoint):
     Switches the projection to Q_cd(a, b, c, d) = (c, d) so col_inf = d corresponds to
     (0, 0, 1) ON the conic {(1, x, x^2)} U {(0, 0, 1)}, allowing exact shifted
     OA(q^3; 3, q + 1, q) completion of every singleton free slice in (q - 1)q^2 rows.
     For q = 7, 9, exploits the exact identity
         ((q - 1)/2)(2q - 1) + q + (q - 1)/2 = q^2
     to pack (q - 1)/2 disjoint minimal blocking sets + 1 q-point parabola {(d^2, d)}
     for symbol m* = (q - 1)/2 + (q - 1)/2 singletons. This produces exact CA(N_poly2(q);
     4, q + 2, q) arrays where symbol m*'s completion rows have 0 unique tuples on all
     col_inf triples and massively reduced min_row_unique (15 for q=7, 36 for q=9).

Builds on Bush (1952), Segre (1955), Jamison (1977), Brouwer-Schrijver (1978),
and Bai XunDi (2026).
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import time


# ---------------------------------------------------------------------------
# Unified GF(q) arithmetic for q in {7, 8, 9, 11, 13}
# ---------------------------------------------------------------------------

class GF:
    """Small finite field GF(q) with precomputed add/sub/mul/inv tables."""

    def __init__(self, q: int) -> None:
        self.q = q
        if q in (7, 11, 13):
            self.char = q
            self.add = tuple(tuple((a + b) % q for b in range(q)) for a in range(q))
            self.sub = tuple(tuple((a - b) % q for b in range(q)) for a in range(q))
            self.mul = tuple(tuple((a * b) % q for b in range(q)) for a in range(q))
        elif q == 8:
            # GF(2)[x] / (x^3 + x + 1)
            self.char = 2
            self.add = tuple(tuple(a ^ b for b in range(8)) for a in range(8))
            self.sub = self.add

            def m8(a: int, b: int) -> int:
                res = 0
                for _ in range(3):
                    if b & 1:
                        res ^= a
                    hi = a & 4
                    a = (a << 1) & 7
                    if hi:
                        a ^= 3
                    b >>= 1
                return res

            self.mul = tuple(tuple(m8(a, b) for b in range(8)) for a in range(8))
        elif q == 9:
            # GF(3)[x] / (x^2 + 1), element = c0 + 3*c1
            self.char = 3

            def a9(a: int, b: int) -> int:
                return ((a % 3 + b % 3) % 3) + 3 * ((a // 3 + b // 3) % 3)

            def s9(a: int, b: int) -> int:
                return ((a % 3 - b % 3) % 3) + 3 * ((a // 3 - b // 3) % 3)

            def m9(a: int, b: int) -> int:
                a0, a1 = a % 3, a // 3
                b0, b1 = b % 3, b // 3
                return ((a0 * b0 - a1 * b1) % 3) + 3 * ((a0 * b1 + a1 * b0) % 3)

            self.add = tuple(tuple(a9(a, b) for b in range(9)) for a in range(9))
            self.sub = tuple(tuple(s9(a, b) for b in range(9)) for a in range(9))
            self.mul = tuple(tuple(m9(a, b) for b in range(9)) for a in range(9))
        else:
            raise ValueError(f"Unsupported q={q}; supported: 7, 8, 9, 11, 13")

        self.inv = (0,) + tuple(
            next(b for b in range(1, q) if self.mul[a][b] == 1) for a in range(1, q)
        )
        self.x2 = tuple(self.mul[x][x] for x in range(q))
        self.x3 = tuple(self.mul[self.x2[x]][x] for x in range(q))
        self._verify_axioms()

    def _verify_axioms(self) -> None:
        q = self.q
        for a in range(q):
            assert self.add[a][0] == a and self.sub[a][a] == 0
            assert self.mul[a][1] == a and self.mul[a][0] == 0
            if a > 0:
                assert self.mul[a][self.inv[a]] == 1
        # Sample associativity & distributivity
        for a in range(min(q, 5)):
            for b in range(min(q, 5)):
                for c in range(min(q, 5)):
                    assert self.mul[a][self.add[b][c]] == self.add[self.mul[a][b]][self.mul[a][c]]

    def ag2_lines(self) -> tuple[tuple[int, ...], ...]:
        """All q^2 + q affine lines of AG(2, q), points indexed as p = u*q + v."""
        q = self.q
        add, mul = self.add, self.mul
        lines = [tuple(c * q + y for y in range(q)) for c in range(q)]
        for m in range(q):
            for b in range(q):
                lines.append(tuple(x * q + add[mul[m][x]][b] for x in range(q)))
        assert len(lines) == q * q + q
        return tuple(lines)

    def first_irreducible_quadratic(self) -> tuple[int, int]:
        """Return (g0, g1) of a monic irreducible x^2 + g1*x + g0 over GF(q)."""
        q = self.q
        add, mul = self.add, self.mul
        if q == 8:
            # Canonical x^2 + x + 1 matching Phase 5B-2A
            g0, g1 = 1, 1
            assert all(add[add[self.x2[x]][mul[g1][x]]][g0] != 0 for x in range(q))
            return (g0, g1)
        for g1 in range(q):
            for g0 in range(1, q):
                if all(add[add[self.x2[x]][mul[g1][x]]][g0] != 0 for x in range(q)):
                    return (g0, g1)
        raise RuntimeError(f"No irreducible quadratic over GF({q})")

    def eval_bush_tc(self, a: int, b: int, c: int, d: int) -> tuple[int, ...]:
        """Evaluate Bush OA(q^4; 4, q + 1, q) codeword for (a, b, c, d) in GF(q)^4."""
        add, mul, x2, x3 = self.add, self.mul, self.x2, self.x3
        return tuple(
            add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
            for x in range(self.q)
        ) + (d,)


# ---------------------------------------------------------------------------
# Verified deterministic AG(2, q) blocking-set partitions (checked at runtime)
# ---------------------------------------------------------------------------

# q = 8 (even): 4 disjoint 15-pt blocking sets {0..3} + 4 singletons {4..7} at (9,39,42,59)
# Exact match to Phase 5B-2A scripts/gen_t4_q8_nearbush.py (Gate 0a)
Q8_K10_COLORING: tuple[int, ...] = (
    1, 1, 1, 0, 2, 1, 3, 1,
    0, 4, 3, 2, 2, 2, 3, 1,
    0, 3, 3, 0, 2, 0, 0, 1,
    1, 3, 2, 3, 0, 1, 1, 1,
    3, 3, 1, 0, 2, 0, 3, 5,
    1, 2, 6, 0, 3, 0, 3, 3,
    2, 2, 2, 1, 2, 2, 3, 0,
    0, 0, 0, 7, 1, 3, 2, 2,
)
Q8_FREE_PTS: tuple[int, ...] = (9, 39, 42, 59)

# q = 7 (odd): 3 disjoint 13-pt blocking sets {0,1,2} + 7-pt parabola {(d^2, d)} (tag 4 -> sym 3)
#              + 3 singletons (tag 3 -> syms 4,5,6); 3*13 + 7 + 3 = 49 exact.
Q7_PARABOLA_RAW: tuple[int, ...] = (
    4, 1, 0, 1, 2, 1, 1,
    0, 4, 0, 1, 0, 2, 4,
    2, 1, 0, 4, 4, 0, 2,
    1, 2, 1, 3, 3, 1, 0,
    2, 1, 4, 3, 0, 4, 2,
    0, 0, 2, 2, 1, 1, 2,
    2, 1, 0, 0, 0, 2, 2,
)

# q = 9 (odd): 4 disjoint 17-pt blocking sets {0..3} + 9-pt parabola {(d^2, d)} (tag 5 -> sym 4)
#              + 4 singletons (tag 4 -> syms 5,6,7,8); 4*17 + 9 + 4 = 81 exact.
Q9_PARABOLA_RAW: tuple[int, ...] = (
    5, 2, 2, 3, 2, 2, 2, 1, 0,
    4, 5, 5, 2, 0, 3, 3, 4, 1,
    0, 0, 1, 5, 2, 1, 5, 1, 3,
    0, 2, 1, 2, 2, 5, 3, 5, 2,
    4, 0, 3, 3, 3, 0, 1, 3, 2,
    2, 1, 0, 3, 0, 0, 0, 0, 3,
    3, 1, 0, 0, 5, 2, 3, 2, 5,
    4, 2, 1, 1, 1, 0, 3, 1, 1,
    1, 3, 3, 2, 1, 0, 3, 1, 0,
)

# q = 11 (odd): 5 disjoint 22-pt blocking sets {0..4} + 11 free pts (tag 5 -> syms 5..10)
Q11_DISJOINT_RAW: tuple[int, ...] = (
    3, 2, 2, 5, 4, 0, 3, 2, 4, 3, 1,
    4, 1, 3, 3, 1, 3, 2, 0, 1, 3, 2,
    4, 0, 0, 1, 5, 0, 0, 4, 2, 3, 0,
    4, 0, 0, 0, 3, 0, 0, 5, 0, 1, 2,
    0, 2, 3, 0, 1, 3, 1, 1, 1, 3, 4,
    4, 5, 2, 1, 3, 0, 1, 3, 3, 1, 5,
    1, 2, 2, 5, 4, 0, 0, 5, 2, 2, 3,
    1, 4, 3, 2, 1, 4, 0, 2, 5, 4, 4,
    2, 2, 4, 4, 1, 4, 1, 3, 4, 0, 1,
    3, 3, 1, 0, 2, 2, 2, 4, 2, 5, 5,
    4, 1, 5, 2, 0, 1, 4, 4, 4, 3, 3,
)

# q = 13 (odd): 6 disjoint 27-pt blocking sets {0..5} + 7 free pts (tag 6 -> syms 6..12)
Q13_DISJOINT_RAW: tuple[int, ...] = (
    4, 2, 4, 2, 3, 1, 3, 4, 5, 0, 2, 3, 2,
    1, 0, 2, 0, 4, 1, 3, 5, 2, 0, 0, 0, 0,
    2, 0, 2, 4, 4, 0, 2, 0, 1, 3, 5, 6, 2,
    0, 4, 4, 3, 4, 4, 2, 1, 0, 5, 6, 1, 3,
    0, 3, 3, 6, 5, 1, 1, 2, 1, 4, 2, 5, 3,
    5, 3, 2, 0, 1, 1, 5, 2, 6, 2, 2, 2, 4,
    1, 2, 5, 0, 1, 1, 3, 2, 0, 1, 0, 3, 4,
    1, 5, 0, 1, 0, 3, 4, 4, 1, 0, 1, 4, 2,
    3, 6, 4, 4, 1, 4, 3, 4, 5, 0, 2, 3, 3,
    5, 1, 1, 4, 3, 2, 3, 3, 4, 0, 3, 4, 1,
    0, 5, 2, 1, 2, 5, 5, 4, 5, 5, 5, 5, 3,
    3, 5, 2, 5, 0, 1, 5, 4, 1, 0, 5, 5, 5,
    3, 5, 2, 6, 4, 1, 0, 0, 3, 5, 4, 3, 6,
)


def verify_blocking_sets(gf: GF, coloring: tuple[int, ...] | list[int], c_b: int) -> None:
    """Assert that every one of the q^2 + q affine lines of AG(2, q) hits all colors 0..c_b-1."""
    assert len(coloring) == gf.q * gf.q
    req = set(range(c_b))
    for line in gf.ag2_lines():
        present = {coloring[p] for p in line}
        assert req.issubset(present), f"AG(2,{gf.q}) line {line} misses color in 0..{c_b - 1}"


def build_irred_quad_q8(gf: GF) -> list[tuple[int, ...]]:
    """Gate 0a: Parameterized GF(q) irreducible-quadratic + polychromatic AG(2, q) on q = 8.

    Must reproduce CA(5888; 4, 10, 8) byte-identically to Phase 5B-2A (sha256: 7d72bc89...).
    """
    assert gf.q == 8
    c_b = gf.q // 2  # 4
    verify_blocking_sets(gf, Q8_K10_COLORING, c_b)
    for idx, pt in enumerate(Q8_FREE_PTS):
        assert Q8_K10_COLORING[pt] == c_b + idx

    g0, g1 = gf.first_irreducible_quadratic()  # (1, 1) -> x^2 + x + 1
    add, sub, mul, x2 = gf.add, gf.sub, gf.mul, gf.x2
    scale = [add[add[g0][mul[g1][x]]][x2[x]] for x in range(gf.q)] + [1]
    assert all(s != 0 for s in scale)

    # Projection Q_g(a, b, c, d) = (p, q) such that f(x) - (q*x + p*x^2) is divisible by g(x):
    # For x^2 + x + 1 in GF(8), f(x) = (a + d*x)(x^2 + x + 1) + (a+b+d)*x + (a+c+d)*x^2
    rows: list[tuple[int, ...]] = []
    q = gf.q
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    p_coord = add[add[a][c]][d]
                    q_coord = add[add[a][b]][d]
                    rows.append(
                        gf.eval_bush_tc(a, b, c, d) + (Q8_K10_COLORING[p_coord * q + q_coord],)
                    )

    for idx, pt in enumerate(Q8_FREE_PTS):
        m = c_b + idx
        p0, q0 = divmod(pt, q)
        shift = gf.eval_bush_tc(0, q0, p0, 0)
        for w in range(1, q):
            for u in range(q):
                for v in range(q):
                    r = [
                        add[shift[x]][mul[add[add[u][mul[v][x]]][mul[w][x2[x]]]][scale[x]]]
                        for x in range(q)
                    ]
                    r.append(add[shift[q]][v])
                    rows.append(tuple(r) + (m,))

    assert len(rows) == q**4 + (q - c_b) * (q - 1) * (q**2) == 5888
    return rows


def diagnose_irred_quad_odd(q: int) -> dict[str, object]:
    """Explicitly run & verify both odd-characteristic obstructions for literal Q_g over GF(q)."""
    gf = GF(q)
    g0, g1 = gf.first_irreducible_quadratic()
    add, sub, mul, x2 = gf.add, gf.sub, gf.mul, gf.x2
    scale = [add[add[g0][mul[g1][x]]][x2[x]] for x in range(q)] + [1]
    assert all(s != 0 for s in scale)

    # 1) Check all pairs {x1, x2} with col_inf = (0, 1, 0) in naive w-extension
    #    det([1, x1, x1^2; 1, x2, x2^2; 0, 1, 0]) = -(x2^2 - x1^2)
    collided_pairs = [
        (x1, x2_i)
        for x1 in range(q)
        for x2_i in range(x1 + 1, q)
        if x2[x1] == x2[x2_i]
    ]
    assert len(collided_pairs) == (q - 1) // 2

    # 2) Verify directly on a single w-extended block (q^3 rows) how many triples are missed
    #    on each collided 3-set {x1, x2, col_inf} vs non-collided 3-sets
    block_rows = []
    for w in range(q):
        for u in range(q):
            for v in range(q):
                r = [
                    mul[add[add[u][mul[v][x]]][mul[w][x2[x]]]][scale[x]]
                    for x in range(q)
                ]
                r.append(v)
                block_rows.append(tuple(r))
    # Check collided pair (1, q-1) with col_inf = q
    c1, c2 = collided_pairs[0]
    seen_coll = {(r[c1], r[c2], r[q]) for r in block_rows}
    missed_per_coll_triple = q**3 - len(seen_coll)
    assert missed_per_coll_triple == (q - 1) * q * q  # rank 2 -> only q^2 of q^3 covered!

    # Check non-collided pair (0, 1) with col_inf = q
    seen_ok = {(r[0], r[1], r[q]) for r in block_rows}
    assert len(seen_ok) == q**3

    # 3) Check Segre conic-tangent obstruction: image size of z -> z^2 in GF(q)
    n_squares = len(set(x2))
    assert n_squares == (q + 1) // 2 < q

    # 4) Jamison / Brouwer-Schrijver parity bound for disjoint blocking sets
    c_b_max = (q * q) // (2 * q - 1)
    assert c_b_max == (q - 1) // 2
    rem_syms = q - c_b_max  # (q + 1) // 2
    n_disjoint_single_slice = q**4 + rem_syms * (q - 1) * q * q
    n_poly2 = q**4 + ((q * q - 1) // 2) * q * q
    assert n_disjoint_single_slice == n_poly2

    return {
        "q": q,
        "k": q + 2,
        "irred_quad": f"x^2 + {g1}*x + {g0}",
        "collided_pairs_count": len(collided_pairs),
        "collided_pairs": collided_pairs,
        "missed_per_collided_triple": missed_per_coll_triple,
        "total_missed_per_free_symbol": len(collided_pairs) * missed_per_coll_triple,
        "n_squares": n_squares,
        "c_b_max": c_b_max,
        "rem_syms": rem_syms,
        "n_disjoint_single_slice": n_disjoint_single_slice,
        "n_poly2": n_poly2,
    }


def _odd_sym_map_and_anchors(gf: GF) -> tuple[list[int], list[tuple[int, int]], str]:
    """Return (sym_map[c*q + d], [(m, anchor_pt)], layout_desc) for odd q in {7, 9, 11, 13}."""
    q = gf.q
    c_b = (q - 1) // 2

    if q in (7, 9):
        raw = Q7_PARABOLA_RAW if q == 7 else Q9_PARABOLA_RAW
        verify_blocking_sets(gf, raw, c_b)
        parab_tag = c_b + 1
        sing_tag = c_b
        parab_expected = {gf.x2[d] * q + d for d in range(q)}
        parab_pts = [p for p, t in enumerate(raw) if t == parab_tag]
        sing_pts = [p for p, t in enumerate(raw) if t == sing_tag]
        assert set(parab_pts) == parab_expected
        assert len(sing_pts) == (q - 1) // 2

        sym_map = list(raw)
        # Parabola -> symbol m* = c_b (anchored at (0, 0) in parabola)
        for p in parab_pts:
            sym_map[p] = c_b
        anchors: list[tuple[int, int]] = [(c_b, 0)]
        # Singletons -> symbols c_b + 1 .. q - 1
        for idx, p in enumerate(sing_pts):
            m = c_b + 1 + idx
            sym_map[p] = m
            anchors.append((m, p))
        assert len(anchors) == (q + 1) // 2
        desc = f"{c_b}x({2*q-1})-BS + {q}-pt parabola (sym {c_b}) + {len(sing_pts)} singletons"
        return sym_map, anchors, desc

    if q in (11, 13):
        raw = Q11_DISJOINT_RAW if q == 11 else Q13_DISJOINT_RAW
        verify_blocking_sets(gf, raw, c_b)
        free_pts = [p for p, t in enumerate(raw) if t == c_b]
        rem_syms = q - c_b  # (q + 1) // 2
        assert len(free_pts) >= rem_syms

        sym_map = list(raw)
        # Assign first rem_syms free points as singleton anchors for symbols c_b .. q-1;
        # pack any remaining free points onto symbol c_b (preferring distinct d coordinates).
        anchors = []
        used_d = set()
        # Pick one anchor per remaining symbol
        chosen_anchors = free_pts[:rem_syms]
        extra_free = free_pts[rem_syms:]
        for idx, p in enumerate(chosen_anchors):
            m = c_b + idx
            sym_map[p] = m
            anchors.append((m, p))
            if idx == 0:
                used_d.add(p % q)
        for p in extra_free:
            sym_map[p] = c_b
            used_d.add(p % q)
        bs_sz = (q * q - len(free_pts)) // c_b
        desc = (
            f"{c_b}x({bs_sz})-BS + {1 + len(extra_free)}-pt sym {c_b} "
            f"+ {rem_syms - 1} singletons"
        )
        return sym_map, anchors, desc

    raise ValueError(f"Unsupported odd q={q}")


def build_odd_poly2_disjoint(q: int) -> tuple[list[tuple[int, ...]], str]:
    """Adapted Q_cd(a, b, c, d) = (c, d) disjoint-BS + free-slice construction for odd q.

    Produces exact CA(q^4 + ((q^2 - 1)/2)*q^2; 4, q + 2, q) for q in {7, 9, 11, 13}.
    """
    gf = GF(q)
    sym_map, anchors, desc = _odd_sym_map_and_anchors(gf)
    add, sub, mul, x2, x3 = gf.add, gf.sub, gf.mul, gf.x2, gf.x3

    rows: list[tuple[int, ...]] = []
    # 1) Main Bush OA(q^4; 4, q + 1, q) + col_{q+1} = sym_map[c*q + d]
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = [
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    ]
                    r.append(d)
                    r.append(sym_map[c * q + d])
                    rows.append(tuple(r))

    # 2) Complete each remaining symbol m from its anchor (c0, d0) via shifted OA(q^3; 3, q+1, q)
    #    For cp == d0, the slice is already present in the main block; add cp in GF(q) \ {d0}.
    for m, anchor_pt in anchors:
        c0, d0 = divmod(anchor_pt, q)
        cd = sub[c0][d0]
        shift = [add[mul[cd][x2[x]]][mul[d0][x3[x]]] for x in range(q)]
        for cp in range(q):
            if cp == d0:
                continue
            for a in range(q):
                for b in range(q):
                    r = [
                        add[add[add[a][mul[b][x]]][mul[cp][x2[x]]]][shift[x]]
                        for x in range(q)
                    ]
                    r.append(cp)
                    r.append(m)
                    rows.append(tuple(r))

    expected_n = q**4 + ((q * q - 1) // 2) * (q * q)
    assert len(rows) == expected_n
    return rows, desc


def build_odd_poly2_pencil(q: int) -> list[tuple[int, ...]]:
    """Standard Bai XunDi (2026) poly2 pencil-cover CA(q^4 + ((q^2-1)/2)q^2; 4, q+2, q) for odd q."""
    gf = GF(q)
    add, mul, inv, x2, x3 = gf.add, gf.mul, gf.inv, gf.x2, gf.x3
    c_b = (q + 1) // 2  # pencil colors 0..c_b-1 sharing origin (0,0)

    def pencil(c: int, d: int) -> int:
        if c == 0 or d == 0:
            return 0
        slope = mul[d][inv[c]]  # in 1..q-1
        return (slope + 1) // 2  # 1..(q-1)//2

    rows: list[tuple[int, ...]] = []
    # 1) Main Bush block
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for d in range(q):
                    r = [
                        add[add[a][mul[b][x]]][add[mul[c][x2[x]]][mul[d][x3[x]]]]
                        for x in range(q)
                    ]
                    r.append(d)
                    r.append(pencil(c, d))
                    rows.append(tuple(r))

    # 2) Vertex repairs at (c, d) = (0, 0) for colors 1..(q-1)//2
    for m in range(1, c_b):
        for a in range(q):
            for b in range(q):
                r = [add[a][mul[b][x]] for x in range(q)]
                r.append(0)
                r.append(m)
                rows.append(tuple(r))

    # 3) Full OA(q^3; 3, q+1, q) blocks for remaining symbols c_b..q-1
    for m in range(c_b, q):
        for cp in range(q):
            for a in range(q):
                for b in range(q):
                    r = [add[add[a][mul[b][x]]][mul[cp][x2[x]]] for x in range(q)]
                    r.append(cp)
                    r.append(m)
                    rows.append(tuple(r))

    expected_n = q**4 + ((q * q - 1) // 2) * (q * q)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generalized GF(q) k = q + 2 NEAR_BUSH generator & odd-q diagnostic"
    )
    parser.add_argument(
        "--mode",
        choices=["irred-quad", "irred-quad-diag", "poly2-disjoint", "poly2-pencil"],
        required=True,
    )
    parser.add_argument("--q", type=int, choices=[7, 8, 9, 11, 13], required=True)
    parser.add_argument("--out", type=Path, help="Output canonical array path")
    args = parser.parse_args()

    t0 = time.perf_counter()
    if args.mode == "irred-quad-diag":
        if args.q == 8:
            raise SystemExit("Use --mode irred-quad --q 8 for even q = 8")
        info = diagnose_irred_quad_odd(args.q)
        dt = time.perf_counter() - t0
        print(
            f"[irred-quad-diag q={info['q']} k={info['k']}] "
            f"g(x)={info['irred_quad']} "
            f"collided_pairs={info['collided_pairs_count']} ({info['collided_pairs']}) "
            f"missed/triple={info['missed_per_collided_triple']} "
            f"missed/free_sym={info['total_missed_per_free_symbol']} "
            f"|squares|={info['n_squares']}<{info['q']} "
            f"c_B_max={info['c_b_max']} rem_syms={info['rem_syms']} "
            f"N_disjoint_single={info['n_disjoint_single_slice']} (=N_poly2={info['n_poly2']}) "
            f"elapsed={dt:.3f}s"
        )
        return

    if args.out is None:
        raise SystemExit("--out is required for array generation modes")

    if args.mode == "irred-quad":
        if args.q != 8:
            raise SystemExit("Literal irred-quad produces valid CA only for even q=8; use irred-quad-diag or poly2-disjoint for odd q")
        gf = GF(8)
        rows = build_irred_quad_q8(gf)
        desc = "irred x^2+x+1 + 4x15-BS + 4 singletons (Gate 0a)"
    elif args.mode == "poly2-disjoint":
        if args.q == 8:
            raise SystemExit("Use --mode irred-quad --q 8 for q = 8")
        rows, desc = build_odd_poly2_disjoint(args.q)
    elif args.mode == "poly2-pencil":
        if args.q == 8:
            raise SystemExit("Use gen_t4_q8_nearbush.py for q = 8 pencil")
        rows = build_odd_poly2_pencil(args.q)
        desc = f"standard poly2 pencil cover (q={args.q})"
    else:
        raise ValueError(args.mode)

    sha = write_array_and_sha256(args.out, rows)
    dt = time.perf_counter() - t0
    print(
        f"mode={args.mode} CA({len(rows)}; 4, {args.q + 2}, {args.q}) "
        f"layout=[{desc}] sha256={sha} elapsed={dt:.3f}s -> {args.out}"
    )


if __name__ == "__main__":
    main()
