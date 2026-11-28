#!/usr/bin/env python3
"""Phase 8 (Baer-v2): Baer-Gitter mit r ausgelagerten Vollgeraden.

Pure Python (std-only). Uses GeneralGF / factor_prime_power from scripts/gen_general_tqv.py.
No solver, no search, no randomness.

Exact implementation of docs/phase8/BAER_V2_SPEZIFIKATION.md:
  Given q = n^2 (n >= 2 prime power), F in {0..n}, v = q - n + F, r in {0..min(F, n-1)}:
  - Field F_q via GeneralGF(q), subfield F_n = {x : x^n = x} in ascending label order,
    om = min(F_q \\ F_n), z = p1(z) + p2(z) * om.
  - Symbols 0..v-1:
      K(i, j) = (num(i) - 1) * n + num(j)  for i in F_n \\ {0}, j in F_n
      V_m     = q - n + m                   for m in {0..F-1}
      Fuell   = V_0 (= q - n) if F >= 1 else 0
  - Deterministic ordering: d = 0..q-1, therein c = 0..q-1.
  - Counting formula:
      |R(n, F, r)| = q*(q - 1) + (q - n)*(n + F) - n*r*(n - r)
                     + max(n, F^2 + (n - F)*(F - r)).
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


# All 21 (q, F, r*, expected_|R|) target tuples from docs/phase8/BAER_V2_SPEZIFIKATION.md §3
SPEC_TARGETS: tuple[tuple[int, int, int, int], ...] = (
    # q = 4 (n = 2, F = 0..2)
    (4, 0, 0, 18),
    (4, 1, 1, 18),
    (4, 2, 1, 22),
    # q = 9 (n = 3, F = 0..3)
    (9, 0, 0, 93),
    (9, 1, 1, 93),
    (9, 2, 2, 100),
    (9, 3, 1, 111),
    # q = 16 (n = 4, F = 0..4)
    (16, 0, 0, 292),
    (16, 1, 1, 292),
    (16, 2, 2, 300),
    (16, 3, 2, 318),
    (16, 4, 2, 336),
    # q = 25 (n = 5, F = 0..5)
    (25, 0, 0, 705),
    (25, 1, 1, 705),
    (25, 2, 2, 715),
    (25, 3, 3, 739),
    (25, 4, 3, 767),
    (25, 5, 2, 795),
    # q = 49 (n = 7, F = 0, 3, 7)
    (49, 0, 0, 2653),
    (49, 3, 3, 2697),
    (49, 7, 3, 2905),
)


@dataclass(frozen=True)
class BaerField:
    q: int
    n: int
    gf: GeneralGF
    sub: tuple[tuple[int, ...], ...]
    inv: tuple[int, ...]  # inv[0] = -1, inv[d] = 1/d for d in 1..q-1
    fn_elems: tuple[int, ...]  # Fn[0] < ... < Fn[n-1], Fn[0] == 0
    num: dict[int, int]
    om: int
    p1: tuple[int, ...]
    p2: tuple[int, ...]


def isqrt_prime_power(q: int) -> int:
    """Return n if q = n^2 with n >= 2 a prime power, else raise ValueError."""
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

    neg = [-1] * q
    for x in range(q):
        for y in range(q):
            if add[x][y] == 0:
                neg[x] = y
                break
        assert neg[x] != -1
    sub = tuple(tuple(add[x][neg[y]] for y in range(q)) for x in range(q))

    inv = [-1] * q
    for x in range(1, q):
        for y in range(1, q):
            if mul[x][y] == 1:
                inv[x] = y
                break
        assert inv[x] != -1

    fn_elems = tuple(x for x in range(q) if gf_pow(gf, x, n) == x)
    if len(fn_elems) != n:
        raise RuntimeError(f"Expected |F_n|={n}, got {len(fn_elems)}")
    assert fn_elems[0] == 0 and 1 in fn_elems
    fn_set = set(fn_elems)
    for x in fn_elems:
        for y in fn_elems:
            assert add[x][y] in fn_set and mul[x][y] in fn_set

    num = {x: idx for idx, x in enumerate(fn_elems)}
    om = next(x for x in range(q) if x not in fn_set)

    p1 = [-1] * q
    p2 = [-1] * q
    for z1 in fn_elems:
        for z2 in fn_elems:
            z = add[z1][mul[z2][om]]
            assert p1[z] == -1, f"Non-unique decomposition for z={z}"
            p1[z] = z1
            p2[z] = z2
    assert all(val != -1 for val in p1)

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


def expected_size(q: int, F: int, r: int) -> int:
    n = isqrt_prime_power(q)
    if not (0 <= F <= n):
        raise ValueError(f"F={F} out of range 0..{n}")
    r_max = min(F, n - 1)
    if not (0 <= r <= r_max):
        raise ValueError(f"r={r} out of range 0..{r_max}")
    return (
        q * (q - 1)
        + (q - n) * (n + F)
        - n * r * (n - r)
        + max(n, F * F + (n - F) * (F - r))
    )


def optimal_r(q: int, F: int) -> int:
    """Return smallest r in {0..min(F, n-1)} minimizing |R(n, F, r)|."""
    n = isqrt_prime_power(q)
    r_max = min(F, n - 1)
    return min(range(r_max + 1), key=lambda r: (expected_size(q, F, r), r))


def generate_baer_v2_reps(
    bf: BaerField, F: int, r: int
) -> list[tuple[int, int, int, int]]:
    """Generate deterministic Baer-v2 representatives (c, d, a, b) per BAER_V2_SPEZIFIKATION.md."""
    q, n = bf.q, bf.n
    if not (0 <= F <= n):
        raise ValueError(f"F={F} out of range 0..{n}")
    r_max = min(F, n - 1)
    if not (0 <= r <= r_max):
        raise ValueError(f"r={r} out of range 0..{r_max}")

    s = F - r
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

    fuell = sym_V(0) if F >= 1 else 0

    # Precompute bucket assignment for d = 0, c2 == 0, F >= 1, s == 0 (r == F)
    s0_buckets: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    if F >= 1 and s == 0:
        for m_a in range(F):
            for m_b in range(F):
                idx = m_a * F + m_b
                s0_buckets[idx % n].append((sym_V(m_a), sym_V(m_b)))

    reps: list[tuple[int, int, int, int]] = []

    # Deterministic order: d = 0..q-1, therein c = 0..q-1
    for d in range(q):
        if d == 0:
            for c in range(q):
                c1 = p1[c]
                c2 = p2[c]
                t = num[c1]
                if c2 != 0:
                    iota = num[c2] - 1
                    if iota < r:
                        L = [sym_V(m) for m in range(F) if m != iota]
                    else:
                        L = [sym_V(m) for m in range(r, F)]
                    s_loc = len(L)
                    assert s_loc <= n
                    for l_idx in range(s_loc):
                        k_l = sym_K(c2, fn_elems[(t + l_idx) % n])
                        reps.append((c, 0, L[l_idx], k_l))
                        reps.append((c, 0, k_l, L[l_idx]))
                    for l_idx in range(s_loc, n):
                        k_l = sym_K(c2, fn_elems[(t + l_idx) % n])
                        reps.append((c, 0, k_l, k_l))
                else:
                    if F == 0:
                        reps.append((c, 0, fuell, fuell))
                    elif s == 0:
                        bucket = s0_buckets[t]
                        if bucket:
                            for va, vb in bucket:
                                reps.append((c, 0, va, vb))
                        else:
                            reps.append((c, 0, fuell, fuell))
                    else:
                        if t < F:
                            for m in range(F):
                                reps.append((c, 0, sym_V(m), sym_V((m + t) % F)))
                        else:
                            for m in range(r, F):
                                vm = sym_V(m)
                                reps.append((c, 0, vm, vm))
        else:
            w = inv[d]
            w1 = p1[w]
            w2 = p2[w]
            w2_om = mul[w2][om]
            w1_om = mul[w1][om]
            for c in range(q):
                # a-column
                if w2 != 0:
                    a = sym_K(w2, p2[mul[sub[c][w2_om]][w]])
                else:
                    iota1 = num[w1] - 1
                    if iota1 < r:
                        a = sym_V(iota1)
                    else:
                        m_a = num[p2[mul[c][w]]]
                        a = sym_V(m_a) if m_a < r else fuell

                # b-column
                if w1 != 0:
                    b = sym_K(w1, p1[mul[sub[c][w1_om]][w]])
                else:
                    iota2 = num[w2] - 1
                    if iota2 < r:
                        b = sym_V(iota2)
                    else:
                        m_b = num[p1[mul[c][w]]]
                        b = sym_V(m_b) if m_b < r else fuell

                reps.append((c, d, a, b))

    exp_len = expected_size(q, F, r)
    if len(reps) != exp_len:
        raise AssertionError(
            f"Size mismatch for q={q}, F={F}, r={r}: {len(reps)} != {exp_len}"
        )
    if len(set(reps)) != len(reps):
        raise AssertionError(f"Duplicate representative found for q={q}, F={F}, r={r}")
    for c, d, a, b in reps:
        assert 0 <= c < q and 0 <= d < q
        assert 0 <= a < v and 0 <= b < v

    return reps


def write_reps(reps: list[tuple[int, int, int, int]], out_path: Path) -> str:
    """Write representatives in canonical 'c d a b\\n' format and return SHA-256 hex digest."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{c} {d} {a} {b}\n" for (c, d, a, b) in reps).encode("utf-8")
    out_path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def run_single(q: int, F: int, r: int | None, out_path: Path) -> str:
    t0 = time.perf_counter()
    bf = build_baer_field(q)
    r_use = optimal_r(q, F) if r is None else r
    v = q - bf.n + F
    reps = generate_baer_v2_reps(bf, F, r_use)
    sha = write_reps(reps, out_path)
    dt = time.perf_counter() - t0
    print(
        f"q={q} n={bf.n} F={F} v={v} r={r_use} m={len(reps)} om={bf.om} "
        f"sha256={sha} elapsed={dt:.4f}s -> {out_path}"
    )
    return sha


def run_all(out_dir: Path) -> None:
    t_start = time.perf_counter()
    out_dir.mkdir(parents=True, exist_ok=True)
    field_cache: dict[int, BaerField] = {}
    sha_lines: list[str] = []

    for q, F, r_star, exp_m in SPEC_TARGETS:
        if q not in field_cache:
            field_cache[q] = build_baer_field(q)
        bf = field_cache[q]
        r_opt = optimal_r(q, F)
        assert expected_size(q, F, r_star) == expected_size(q, F, r_opt), (
            f"r*={r_star} not optimal for q={q}, F={F} (opt={r_opt})"
        )
        v = q - bf.n + F
        reps = generate_baer_v2_reps(bf, F, r_star)
        assert len(reps) == exp_m, (
            f"Target mismatch for (q={q}, F={F}, r={r_star}): {len(reps)} != {exp_m}"
        )
        fname = f"R_q{q}_v{v}_r{r_star}_m{len(reps)}.txt"
        out_path = out_dir / fname
        sha = write_reps(reps, out_path)
        sha_lines.append(f"{sha}  {fname}\n")
        print(
            f"q={q:2d} n={bf.n} F={F} v={v:2d} r={r_star} m={len(reps):4d} "
            f"(soll={exp_m:4d}) om={bf.om:2d} sha256={sha} -> {out_path}"
        )

    sha_file = out_dir / "SHA256SUMS"
    sha_file.write_text("".join(sha_lines), encoding="utf-8")
    dt = time.perf_counter() - t_start
    print(f"Generated {len(SPEC_TARGETS)}/21 lists + {sha_file} in {dt:.4f}s")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Phase 8 Baer-v2 representative generator (docs/phase8/BAER_V2_SPEZIFIKATION.md)."
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Generate all 21 specification target lists for optimal r*",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/phase8_baer_v2"),
        help="Output directory for --all (default: data/phase8_baer_v2)",
    )
    ap.add_argument("--q", type=int, help="Prime power square q = n^2")
    ap.add_argument("--F", type=int, help="Parameter F in 0..n")
    ap.add_argument(
        "--r",
        type=int,
        default=None,
        help="Parameter r in 0..min(F, n-1) (default: optimal r*)",
    )
    ap.add_argument("--out", type=Path, help="Output file path for single generation")
    args = ap.parse_args()

    if args.all:
        run_all(args.out_dir)
    else:
        if args.q is None or args.F is None or args.out is None:
            ap.error("Specify either --all or all of --q, --F, --out")
        run_single(args.q, args.F, args.r, args.out)


if __name__ == "__main__":
    main()
