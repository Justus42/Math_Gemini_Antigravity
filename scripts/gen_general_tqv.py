#!/usr/bin/env python3
"""Phase 6A: Deterministic Pure-Python generator for CA(q^t + C(v, 2) * q^(t - 2); t, k, v).

Pure Python (std-only). No solver, no search, no heuristic, no randomness.

Mathematical construction (see docs/GENERAL_TQV_PROOF.md):
  For any prime power q = p^r >= 2, strength t with 2 <= t <= q + 2, alphabet size v
  with 2 <= v <= q, and column count k with t <= k <= q + 2 (default k = q + 2):
    - Fix the canonical finite field GF(q) = GF(p)[X]/(f(X)) using the lexicographically
      smallest monic irreducible polynomial f(X) of degree r over GF(p), with elements
      identified with {0, 1, ..., q - 1} in base p and linear order 0 < 1 < ... < q - 1.
      (For q = 8 this selects X^3 + X + 1; for q = 9 this selects X^2 + 1, matching
      scripts/gen_t4_minus3q2.py byte-identically.)
    - Fix the symbol retraction pi: GF(q) -> {0, ..., v - 1} with pi(z) = z for z < v
      and pi(z) = 0 for z >= v (identity when v = q).
    - Block 1 (q^t rows): for all (a_0, ..., a_{t-3}, c, d) in GF(q)^t,
        row = ((pi(P(x)))_{x in GF(q)}, pi(d), pi(min(c, d)))
      where P(x) = a_0 + a_1*x + ... + a_{t-3}*x^{t-3} + c*x^{t-2} + d*x^{t-1}.
    - Block 2 (C(v, 2) * q^(t - 2) rows): for all 0 <= c < d < v (ordered by d, then c)
      and all (a_0, ..., a_{t-3}) in GF(q)^(t - 2),
        row' = ((pi(P(x)))_{x in GF(q)}, c, d).
    - If k < q + 2, the first k columns are emitted (column projection).

Builds on Bush (1952), Jamison (1977), Brouwer-Schrijver (1978), CKRS (2010), and
Bai XunDi (2026, polychrome-bai2026).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
from pathlib import Path
import time


# ---------------------------------------------------------------------------
# General finite field GF(q) for arbitrary prime powers q = p^r (std-only)
# ---------------------------------------------------------------------------

def factor_prime_power(q: int) -> tuple[int, int]:
    """Return (p, r) if q = p^r is a prime power (p prime, r >= 1), else raise ValueError."""
    if q < 2:
        raise ValueError(f"q={q} is not a prime power (must be >= 2)")
    n = q
    p = 2
    while p * p <= n:
        if n % p == 0:
            break
        p += 1 if p == 2 else 2
    else:
        return (q, 1)

    r = 0
    while n % p == 0:
        n //= p
        r += 1
    if n != 1:
        raise ValueError(f"q={q} is not a prime power")
    return (p, r)


def _poly_trim(a: list[int]) -> list[int]:
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def _poly_mod(a: list[int], b: list[int], p: int) -> list[int]:
    a = _poly_trim(a[:])
    b = _poly_trim(b[:])
    deg_b = len(b) - 1
    inv_lead = pow(b[-1], -1, p)
    while len(a) - 1 >= deg_b and not (len(a) == 1 and a[0] == 0):
        shift = len(a) - 1 - deg_b
        coef = (a[-1] * inv_lead) % p
        for i in range(deg_b + 1):
            a[shift + i] = (a[shift + i] - coef * b[i]) % p
        _poly_trim(a)
    return a


def _poly_mul_mod(a: list[int], b: list[int], mod_poly: list[int], p: int) -> list[int]:
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[i + j] = (res[i + j] + ai * bj) % p
    return _poly_mod(res, mod_poly, p)


def _poly_pow_mod(base: list[int], exp: int, mod_poly: list[int], p: int) -> list[int]:
    res = [1]
    cur = _poly_mod(base, mod_poly, p)
    e = exp
    while e > 0:
        if e & 1:
            res = _poly_mul_mod(res, cur, mod_poly, p)
        cur = _poly_mul_mod(cur, cur, mod_poly, p)
        e >>= 1
    return res


def _poly_gcd(a: list[int], b: list[int], p: int) -> list[int]:
    a = _poly_trim(a[:])
    b = _poly_trim(b[:])
    while not (len(b) == 1 and b[0] == 0):
        a, b = b, _poly_mod(a, b, p)
    if a[-1] != 0:
        inv_lead = pow(a[-1], -1, p)
        a = [(c * inv_lead) % p for c in a]
    return a


def _is_irreducible(f: list[int], p: int) -> bool:
    """Rabin irreducibility test over GF(p) for monic polynomial f of degree r >= 2."""
    r = len(f) - 1
    # Check gcd(f, X^(p^k) - X) == 1 for 1 <= k <= r // 2
    x_poly = [0, 1]
    xp = x_poly[:]
    for k in range(1, r // 2 + 1):
        xp = _poly_pow_mod(xp, p, f, p)
        diff = xp[:]
        if len(diff) < 2:
            diff.extend([0] * (2 - len(diff)))
        diff[1] = (diff[1] - 1) % p
        diff = _poly_trim(diff)
        g = _poly_gcd(f, diff, p)
        if len(g) > 1:
            return False
    # Continue to X^(p^r) mod f == X
    for _ in range(r // 2 + 1, r + 1):
        xp = _poly_pow_mod(xp, p, f, p)
    return xp == x_poly


def canonical_irreducible_poly(p: int, r: int) -> list[int]:
    """Return lexicographically smallest monic irreducible polynomial of degree r over GF(p).

    Coefficients are returned in ascending degree order [c_0, c_1, ..., c_{r-1}, 1],
    ordered lexicographically by (c_{r-1}, ..., c_1, c_0) with c_0 != 0.
    For (2, 3) this selects [1, 1, 0, 1] = X^3 + X + 1.
    For (3, 2) this selects [1, 0, 1] = X^2 + 1.
    """
    assert r >= 2
    for high_to_low in itertools.product(range(p), repeat=r - 1):
        for c0 in range(1, p):
            f = [c0] + list(reversed(high_to_low)) + [1]
            if _is_irreducible(f, p):
                return f
    raise RuntimeError(f"No irreducible polynomial found for GF({p}^{r})")


class GeneralGF:
    """Finite field GF(q) for any prime power q = p^r with precomputed add/mul tables."""

    def __init__(self, q: int) -> None:
        self.q = q
        self.p, self.r = factor_prime_power(q)
        self.mod_poly: list[int] | None = None

        if self.r == 1:
            p = self.p
            self.add = tuple(tuple((a + b) % p for b in range(p)) for a in range(p))
            self.mul = tuple(tuple((a * b) % p for b in range(p)) for a in range(p))
        else:
            p, r = self.p, self.r
            f = canonical_irreducible_poly(p, r)
            self.mod_poly = f
            # Precompute base-p digit vectors
            digits: list[list[int]] = []
            for a in range(q):
                v = []
                tmp = a
                for _ in range(r):
                    v.append(tmp % p)
                    tmp //= p
                digits.append(v)

            def to_int(poly: list[int]) -> int:
                val = 0
                mult = 1
                for c in poly:
                    val += c * mult
                    mult *= p
                return val

            add_tbl: list[tuple[int, ...]] = []
            for a in range(q):
                da = digits[a]
                row = []
                for b in range(q):
                    db = digits[b]
                    row.append(to_int([(da[i] + db[i]) % p for i in range(r)]))
                add_tbl.append(tuple(row))
            self.add = tuple(add_tbl)

            mul_tbl: list[tuple[int, ...]] = []
            for a in range(q):
                da = digits[a]
                row = []
                for b in range(q):
                    db = digits[b]
                    prod = _poly_mul_mod(da, db, f, p)
                    row.append(to_int(prod))
                mul_tbl.append(tuple(row))
            self.mul = tuple(mul_tbl)

        self._verify_axioms()

    def _verify_axioms(self) -> None:
        q = self.q
        for a in range(q):
            assert self.add[a][0] == a
            assert self.mul[a][0] == 0
            assert self.mul[a][1] == a
            if a > 0:
                has_inv = any(self.mul[a][b] == 1 for b in range(1, q))
                assert has_inv, f"Missing multiplicative inverse for {a} in GF({q})"
        # Sample distributivity and associativity
        sample = range(min(q, 5))
        for a in sample:
            for b in sample:
                assert self.add[a][b] == self.add[b][a]
                assert self.mul[a][b] == self.mul[b][a]
                for c in sample:
                    assert self.mul[a][self.add[b][c]] == self.add[self.mul[a][b]][self.mul[a][c]]
                    assert self.mul[self.mul[a][b]][c] == self.mul[a][self.mul[b][c]]


def expected_n(t: int, q: int, v: int) -> int:
    """Exact row count N(t, q, v) = q^t + C(v, 2) * q^(t - 2)."""
    return (q ** t) + (v * (v - 1) // 2) * (q ** (t - 2))


def generate_general_tqv(
    t: int,
    q: int,
    v: int,
    out_path: Path,
    k: int | None = None,
) -> tuple[int, int, str]:
    """Generate CA(q^t + C(v, 2) * q^(t - 2); t, k, v) deterministically and stream to out_path.

    Returns (n_rows, k_cols, sha256_hex).
    """
    if t < 2:
        raise ValueError(f"t={t} must be >= 2")
    if q < 2:
        raise ValueError(f"q={q} must be a prime power >= 2")
    if t > q + 2:
        raise ValueError(f"t={t} exceeds q + 2 = {q + 2}")
    if v < 2 or v > q:
        raise ValueError(f"v={v} must satisfy 2 <= v <= q={q}")
    k_cols = q + 2 if k is None else k
    if k_cols < t or k_cols > q + 2:
        raise ValueError(f"k={k_cols} must satisfy t={t} <= k <= q + 2 = {q + 2}")

    gf = GeneralGF(q)
    add = gf.add
    mul = gf.mul

    # Precompute powers x^deg for deg in 0..t-1, x in 0..q-1
    x_pow: list[list[int]] = [[1] * q]
    for _ in range(1, t):
        prev = x_pow[-1]
        x_pow.append([mul[prev[x]][x] for x in range(q)])

    # Precompute term[deg][coeff] = tuple(coeff * x^deg for x in range(q))
    term: list[list[tuple[int, ...]]] = [
        [tuple(mul[coeff][x_pow[deg][x]] for x in range(q)) for coeff in range(q)]
        for deg in range(t)
    ]

    # Retraction pi: GF(q) -> {0, ..., v - 1}, formatted as strings
    pi_str = tuple(str(z if z < v else 0) for z in range(q))
    # Precompute min(c, d) mapped via pi_str for Block 1
    col_star_str = tuple(
        tuple(pi_str[c if c < d else d] for d in range(q)) for c in range(q)
    )

    n_finite = min(k_cols, q)
    has_inf = k_cols >= q + 1
    has_star = k_cols == q + 2

    term_c = term[t - 2]
    term_d = term[t - 1]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    n_rows = 0
    buf: list[str] = []
    FLUSH_LIMIT = 4096

    def flush(fh) -> None:
        if buf:
            chunk = "".join(buf).encode("utf-8")
            fh.write(chunk)
            hasher.update(chunk)
            buf.clear()

    # Helper to compute base polynomial evaluations for lower coefficients a_0..a_{t-3}
    def eval_lower(low: tuple[int, ...]) -> list[int]:
        if not low:
            return [0] * n_finite
        # Start with a_0 (x^0 = 1)
        a0 = low[0]
        acc = [a0] * n_finite
        for deg in range(1, len(low)):
            coeff = low[deg]
            if coeff:
                td = term[deg][coeff]
                for x in range(n_finite):
                    acc[x] = add[acc[x]][td[x]]
        return acc

    with out_path.open("wb") as fh:
        # Block 1: full Bush OA(q^t) with pi-retraction + col_star = pi(min(c, d))
        # Exact loop order: (a_0, ..., a_{t-3}), then c, then d
        for low in itertools.product(range(q), repeat=t - 2):
            base = eval_lower(low)
            for c in range(q):
                tc = term_c[c]
                base_c = [add[base[x]][tc[x]] for x in range(n_finite)]
                star_c = col_star_str[c]
                for d in range(q):
                    td = term_d[d]
                    parts = [pi_str[add[base_c[x]][td[x]]] for x in range(n_finite)]
                    if has_inf:
                        parts.append(pi_str[d])
                    if has_star:
                        parts.append(star_c[d])
                    buf.append(" ".join(parts) + "\n")
                    n_rows += 1
                    if len(buf) >= FLUSH_LIMIT:
                        flush(fh)

        # Block 2: C(v, 2) decoupled slices {(c, d, col_inf=c, col_star=d) : 0 <= c < d < v}
        # Exact loop order: d in 0..v-1, c in 0..d-1, then (a_0, ..., a_{t-3})
        for d in range(v):
            td = term_d[d]
            d_str = pi_str[d]
            for c in range(d):
                tc = term_c[c]
                c_str = pi_str[c]
                cd_eval = [add[tc[x]][td[x]] for x in range(n_finite)]
                for low in itertools.product(range(q), repeat=t - 2):
                    base = eval_lower(low)
                    parts = [pi_str[add[base[x]][cd_eval[x]]] for x in range(n_finite)]
                    if has_inf:
                        parts.append(c_str)
                    if has_star:
                        parts.append(d_str)
                    buf.append(" ".join(parts) + "\n")
                    n_rows += 1
                    if len(buf) >= FLUSH_LIMIT:
                        flush(fh)

        flush(fh)

    exp_n = expected_n(t, q, v)
    assert n_rows == exp_n, f"Row count mismatch: {n_rows} != {exp_n}"
    return (n_rows, k_cols, hasher.hexdigest())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic generator for CA(q^t + C(v, 2) * q^(t - 2); t, k, v)"
    )
    parser.add_argument("--t", type=int, required=True, help="Strength t (2 <= t <= q + 2)")
    parser.add_argument("--q", type=int, required=True, help="Prime power q = p^r >= 2")
    parser.add_argument("--v", type=int, required=True, help="Alphabet size v (2 <= v <= q)")
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        help="Optional column count k (t <= k <= q + 2; default: q + 2)",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output canonical array path")
    args = parser.parse_args()

    t0 = time.perf_counter()
    n_rows, k_cols, sha = generate_general_tqv(
        t=args.t, q=args.q, v=args.v, out_path=args.out, k=args.k
    )
    dt = time.perf_counter() - t0
    print(
        f"CA({n_rows}; {args.t}, {k_cols}, {args.v}) [q={args.q}] "
        f"sha256={sha} elapsed={dt:.3f}s -> {args.out}"
    )


if __name__ == "__main__":
    main()
