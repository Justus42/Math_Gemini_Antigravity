#!/usr/bin/env python3
"""Phase 8 (Baer-Gitter): Independent pure-Python implementation from mathematical specification.

Pure Python (std-only). Uses GeneralGF / factor_prime_power from scripts/gen_general_tqv.py.
No solver, no search, no randomness, no imports from scripts/phase8/.

Mathematical specification:
  Given q = n^2 (n prime power), F in {0..n}, v = q - n + F:
  1. Finite field F_q via GeneralGF(q) (element labels 0..q-1).
  2. Subfield F_n = { x in F_q : x^n = x }.
  3. om = smallest element label in F_q \\ F_n. Unique decomposition z = p1(z) + p2(z)*om
     with p1(z), p2(z) in F_n.
  4. num: F_n -> {0..n-1} in ascending order of element labels in F_q.
  5. Symbols (0..v-1, identical for a and b):
       K(i, j) -> (num(i) - 1)*n + num(j)   for i in F_n \\ {0}, j in F_n
       V_m     -> q - n + m                  for m in {0..F-1}
       Fuell   -> q - n (= V_0) if F >= 1 else 0 (= K-symbol 0)
  6. Representatives (c, d, a, b), d ascending (0..q-1), c ascending (0..q-1):
     - d = 0, c2 := p2(c):
       * c2 != 0: n reps (c, 0, K(c2, j), K(c2, j)) for j in F_n (ascending num(j)),
                  then F reps (c, 0, V_m, V_m) for m = 0..F-1.
       * c2 == 0:
         - F == 0: one rep (c, 0, Fuell, Fuell).
         - F >= 1: F reps (c, 0, V_m, V_{(m + num(c)) mod F}) for m = 0..F-1.
     - d != 0, w := 1/d, w1 := p1(w), w2 := p2(w), one rep per c:
       * a = K(w2, p2((c - w2*om)*w)) if w2 != 0
           else (V_m if m < F else Fuell) with m = num(p2(c*w))
       * b = K(w1, p1((c - w1*om)*w)) if w1 != 0
           else (V_m if m < F else Fuell) with m = num(p1(c*w))
  7. Target size: |R| = q*(q - 1) + (q - n)*(n + F) + n*max(F, 1).
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_general_tqv import GeneralGF, factor_prime_power  # noqa: E402


# All 20 (q, F, expected_|R|) target tuples from specification item 7
SPEC_TARGETS: tuple[tuple[int, int, int], ...] = (
    # q = 4 (n = 2, F = 0..2)
    (4, 0, 18),
    (4, 1, 20),
    (4, 2, 24),
    # q = 9 (n = 3, F = 0..3)
    (9, 0, 93),
    (9, 1, 99),
    (9, 2, 108),
    (9, 3, 117),
    # q = 16 (n = 4, F = 0..4)
    (16, 0, 292),
    (16, 1, 304),
    (16, 2, 320),
    (16, 3, 336),
    (16, 4, 352),
    # q = 25 (n = 5, F = 0..5)
    (25, 0, 705),
    (25, 1, 725),
    (25, 2, 750),
    (25, 3, 775),
    (25, 4, 800),
    (25, 5, 825),
    # q = 49 (n = 7, F = 0, 7)
    (49, 0, 2653),
    (49, 7, 2989),
)


@dataclass(frozen=True)
class BaerField:
    q: int
    n: int
    gf: GeneralGF
    sub: tuple[tuple[int, ...], ...]
    inv: tuple[int, ...]  # inv[0] = -1, inv[d] = 1/d for d in 1..q-1
    fn_elems: tuple[int, ...]  # sorted ascending in 0..q-1
    num: dict[int, int]
    om: int
    p1: tuple[int, ...]
    p2: tuple[int, ...]


def isqrt_prime_power(q: int) -> int:
    """Return n if q = n^2 with n a prime power >= 2, else raise ValueError."""
    n = math.isqrt(q)
    if n * n != q or n < 2:
        raise ValueError(f"q={q} is not a square n^2 with n >= 2")
    factor_prime_power(n)
    return n


def gf_pow(gf: GeneralGF, x: int, exp: int) -> int:
    if exp == 0:
        return 1
    if x == 0:
        return 0
    mul = gf.mul
    res = 1
    base = x
    e = exp
    while e > 0:
        if e & 1:
            res = mul[res][base]
        base = mul[base][base]
        e >>= 1
    return res


def build_baer_field(q: int) -> BaerField:
    n = isqrt_prime_power(q)
    gf = GeneralGF(q)
    add, mul = gf.add, gf.mul

    # Additive inverses and subtraction table
    neg = [-1] * q
    for x in range(q):
        for y in range(q):
            if add[x][y] == 0:
                neg[x] = y
                break
        assert neg[x] != -1
    sub = tuple(tuple(add[x][neg[y]] for y in range(q)) for x in range(q))

    # Multiplicative inverses
    inv = [-1] * q
    for x in range(1, q):
        for y in range(1, q):
            if mul[x][y] == 1:
                inv[x] = y
                break
        assert inv[x] != -1

    # Subfield F_n = { x in F_q : x^n == x }
    fn_elems = tuple(x for x in range(q) if gf_pow(gf, x, n) == x)
    if len(fn_elems) != n:
        raise RuntimeError(f"Expected |F_n|={n}, got {len(fn_elems)}")
    assert fn_elems[0] == 0 and 1 in fn_elems
    fn_set = set(fn_elems)
    for x in fn_elems:
        for y in fn_elems:
            assert add[x][y] in fn_set and mul[x][y] in fn_set

    num = {x: idx for idx, x in enumerate(fn_elems)}

    # Smallest element label in F_q \ F_n
    om = next(x for x in range(q) if x not in fn_set)

    # Unique decomposition z = z1 + z2 * om with z1, z2 in F_n
    p1 = [-1] * q
    p2 = [-1] * q
    for z1 in fn_elems:
        for z2 in fn_elems:
            z = add[z1][mul[z2][om]]
            assert p1[z] == -1, f"Non-unique decomposition for z={z}"
            p1[z] = z1
            p2[z] = z2
    assert all(v != -1 for v in p1)

    return BaerField(
        q=q,
        n=n,
        gf=gf,
        sub=sub,
        inv=tuple(inv),
        fn_elems=fn_elems,
        num=num,
        om=om,
        p1=tuple(p1),
        p2=tuple(p2),
    )


def expected_size(q: int, F: int) -> int:
    n = isqrt_prime_power(q)
    if not (0 <= F <= n):
        raise ValueError(f"F={F} out of range 0..{n}")
    return q * (q - 1) + (q - n) * (n + F) + n * max(F, 1)


def generate_baer_reps(
    bf: BaerField, F: int
) -> tuple[list[tuple[int, int, int, int]], list[tuple[bool, bool]]]:
    """Generate deterministic representatives (c, d, a, b) and (a_is_fuell, b_is_fuell) flags."""
    q, n = bf.q, bf.n
    if not (0 <= F <= n):
        raise ValueError(f"F={F} out of range 0..{n}")
    v = q - n + F
    mul = bf.gf.mul
    sub = bf.sub
    inv = bf.inv
    fn_elems = bf.fn_elems
    num = bf.num
    om = bf.om
    p1 = bf.p1
    p2 = bf.p2

    def sym_K(i: int, j: int) -> int:
        assert i != 0
        return (num[i] - 1) * n + num[j]

    def sym_V(m: int) -> int:
        assert 0 <= m < F
        return q - n + m

    fuell = q - n if F >= 1 else 0

    reps: list[tuple[int, int, int, int]] = []
    fuell_flags: list[tuple[bool, bool]] = []

    # d ascending (0..q-1), c ascending (0..q-1)
    for d in range(q):
        if d == 0:
            for c in range(q):
                c2 = p2[c]
                if c2 != 0:
                    # First n reps: (c, 0, K(c2, j), K(c2, j)) for j in F_n in ascending num(j) order
                    for j in fn_elems:
                        s = sym_K(c2, j)
                        reps.append((c, 0, s, s))
                        fuell_flags.append((False, False))
                    # Then F reps: (c, 0, V_m, V_m) for m = 0..F-1
                    for m in range(F):
                        s = sym_V(m)
                        reps.append((c, 0, s, s))
                        fuell_flags.append((False, False))
                else:
                    if F == 0:
                        reps.append((c, 0, fuell, fuell))
                        fuell_flags.append((True, True))
                    else:
                        nc = num[c]
                        for m in range(F):
                            sa = sym_V(m)
                            sb = sym_V((m + nc) % F)
                            reps.append((c, 0, sa, sb))
                            fuell_flags.append((False, False))
        else:
            w = inv[d]
            w1 = p1[w]
            w2 = p2[w]
            w2_om = mul[w2][om]
            w1_om = mul[w1][om]
            for c in range(q):
                if w2 != 0:
                    a = sym_K(w2, p2[mul[sub[c][w2_om]][w]])
                    a_fuell = False
                else:
                    m_a = num[p2[mul[c][w]]]
                    if m_a < F:
                        a = sym_V(m_a)
                        a_fuell = False
                    else:
                        a = fuell
                        a_fuell = True

                if w1 != 0:
                    b = sym_K(w1, p1[mul[sub[c][w1_om]][w]])
                    b_fuell = False
                else:
                    m_b = num[p1[mul[c][w]]]
                    if m_b < F:
                        b = sym_V(m_b)
                        b_fuell = False
                    else:
                        b = fuell
                        b_fuell = True

                reps.append((c, d, a, b))
                fuell_flags.append((a_fuell, b_fuell))

    # Basic range and uniqueness assertions
    exp_len = expected_size(q, F)
    if len(reps) != exp_len:
        raise AssertionError(f"Size mismatch for q={q}, F={F}: {len(reps)} != {exp_len}")
    if len(set(reps)) != len(reps):
        raise AssertionError(f"Duplicate representative found for q={q}, F={F}")
    for c, d, a, b in reps:
        assert 0 <= c < q and 0 <= d < q
        assert 0 <= a < v and 0 <= b < v

    return reps, fuell_flags


def verify_k_geometry(
    bf: BaerField,
    F: int,
    reps: list[tuple[int, int, int, int]],
    fuell_flags: list[tuple[bool, bool]],
) -> None:
    """Verify exact Baer-grid geometry property for every class K(i, j), excluding Fuell-points.

    For every i in F_n \\ {0} and j in F_n, sym = K(i, j):
    - As a-class (excluding a-Fuell points):
        * exactly n points on d = 0, all with p2(c) == i (distinct c)
        * on d != 0: appears on exactly the n horizontal lines with p2(1/d) == i,
          with exactly n points (distinct c) on each such line, and 0 on all other lines.
    - As b-class (excluding b-Fuell points):
        * exactly n points on d = 0, all with p2(c) == i (distinct c)
        * on d != 0: appears on exactly the n horizontal lines with p1(1/d) == i,
          with exactly n points (distinct c) on each such line, and 0 on all other lines.
    """
    q, n = bf.q, bf.n
    num = bf.num
    p1 = bf.p1
    p2 = bf.p2
    inv = bf.inv
    fn_elems = bf.fn_elems
    num_k = q - n

    # Group non-Fuell points by symbol -> d -> list of c
    a_pts: list[dict[int, list[int]]] = [{} for _ in range(num_k)]
    b_pts: list[dict[int, list[int]]] = [{} for _ in range(num_k)]

    for (c, d, a, b), (a_fuell, b_fuell) in zip(reps, fuell_flags):
        if not a_fuell and a < num_k:
            a_pts[a].setdefault(d, []).append(c)
        if not b_fuell and b < num_k:
            b_pts[b].setdefault(d, []).append(c)

    # Precompute expected d != 0 line sets for each i in F_n \ {0}
    c_with_p2 = {i: {c for c in range(q) if p2[c] == i} for i in fn_elems if i != 0}
    d_with_w2 = {i: {d for d in range(1, q) if p2[inv[d]] == i} for i in fn_elems if i != 0}
    d_with_w1 = {i: {d for d in range(1, q) if p1[inv[d]] == i} for i in fn_elems if i != 0}

    for i in fn_elems:
        if i == 0:
            continue
        assert len(c_with_p2[i]) == n
        assert len(d_with_w2[i]) == n
        assert len(d_with_w1[i]) == n
        for j in fn_elems:
            sym = (num[i] - 1) * n + num[j]

            # Check a-class
            amap = a_pts[sym]
            assert 0 in amap, f"K({i},{j}) missing on d=0 as a-class"
            assert len(amap[0]) == n and set(amap[0]) == c_with_p2[i], (
                f"K({i},{j}) d=0 a-class mismatch"
            )
            a_nonzero_ds = set(amap.keys()) - {0}
            assert a_nonzero_ds == d_with_w2[i], (
                f"K({i},{j}) a-class horizontals mismatch: {a_nonzero_ds} != {d_with_w2[i]}"
            )
            for d in a_nonzero_ds:
                assert len(amap[d]) == n and len(set(amap[d])) == n, (
                    f"K({i},{j}) a-class on d={d} has {len(amap[d])} points, expected {n}"
                )

            # Check b-class
            bmap = b_pts[sym]
            assert 0 in bmap, f"K({i},{j}) missing on d=0 as b-class"
            assert len(bmap[0]) == n and set(bmap[0]) == c_with_p2[i], (
                f"K({i},{j}) d=0 b-class mismatch"
            )
            b_nonzero_ds = set(bmap.keys()) - {0}
            assert b_nonzero_ds == d_with_w1[i], (
                f"K({i},{j}) b-class horizontals mismatch: {b_nonzero_ds} != {d_with_w1[i]}"
            )
            for d in b_nonzero_ds:
                assert len(bmap[d]) == n and len(set(bmap[d])) == n, (
                    f"K({i},{j}) b-class on d={d} has {len(bmap[d])} points, expected {n}"
                )


def write_reps(reps: list[tuple[int, int, int, int]], out_path: Path) -> str:
    """Write representatives in canonical 'c d a b\\n' format and return SHA-256 hex digest."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{c} {d} {a} {b}\n" for (c, d, a, b) in reps).encode("utf-8")
    out_path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def run_single(q: int, F: int, out_path: Path) -> str:
    t0 = time.perf_counter()
    bf = build_baer_field(q)
    v = q - bf.n + F
    reps, fuell_flags = generate_baer_reps(bf, F)
    verify_k_geometry(bf, F, reps, fuell_flags)
    sha = write_reps(reps, out_path)
    dt = time.perf_counter() - t0
    print(
        f"q={q} n={bf.n} F={F} v={v} m={len(reps)} om={bf.om} "
        f"geom=OK sha256={sha} elapsed={dt:.4f}s -> {out_path}"
    )
    return sha


def run_all(out_dir: Path) -> None:
    t_start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    field_cache: dict[int, BaerField] = {}
    sha_lines: list[str] = []

    for q, F, exp_m in SPEC_TARGETS:
        if q not in field_cache:
            field_cache[q] = build_baer_field(q)
        bf = field_cache[q]
        v = q - bf.n + F
        reps, fuell_flags = generate_baer_reps(bf, F)
        assert len(reps) == exp_m, f"Target mismatch for (q={q}, F={F}): {len(reps)} != {exp_m}"
        verify_k_geometry(bf, F, reps, fuell_flags)
        fname = f"R_q{q}_v{v}.txt"
        out_path = out_dir / fname
        sha = write_reps(reps, out_path)
        sha_lines.append(f"{sha}  {fname}\n")
        print(
            f"q={q:2d} n={bf.n} F={F} v={v:2d} m={len(reps):4d} (soll={exp_m:4d}) "
            f"om={bf.om:2d} geom=OK sha256={sha} -> {out_path}"
        )

    sha_file = out_dir / "SHA256SUMS"
    sha_file.write_text("".join(sha_lines), encoding="utf-8")
    dt = time.perf_counter() - t_start
    print(f"Generated {len(SPEC_TARGETS)}/20 lists + {sha_file} in {dt:.4f}s")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Independent Phase 8 Baer-grid representative generator from specification."
    )
    ap.add_argument("--all", action="store_true", help="Generate all 20 specification target lists")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/phase8_baer_repro"),
        help="Output directory for --all (default: data/phase8_baer_repro)",
    )
    ap.add_argument("--q", type=int, help="Prime power square q = n^2")
    ap.add_argument("--F", type=int, help="Parameter F in 0..n")
    ap.add_argument("--out", type=Path, help="Output file path for single generation")
    args = ap.parse_args()

    if args.all:
        run_all(args.out_dir)
    else:
        if args.q is None or args.F is None or args.out is None:
            ap.error("Specify either --all or all of --q, --F, --out")
        run_single(args.q, args.F, args.out)


if __name__ == "__main__":
    main()
