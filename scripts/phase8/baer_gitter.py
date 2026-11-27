#!/usr/bin/env python3
"""Phase 8: "Baer-Gitter" -- Vertreterliste fuer Quadratzahlen q = n^2 (std-only, ohne Loeser, ohne Suche).

Aufruf:
  baer_gitter.py Q F [--out DATEI]     F = Zahl der Vollgeraden-Symbole je Seite, 0 <= F <= n
                                       Alphabet v = q - n + F,  |R| = q(q-1) + (q-n)(n+F) + n*max(F,1)
  baer_gitter.py Q --klasse            prueft nur eine einzelne Baer-Klasse (Punktzahl, Geradentreffer)

Bauart (Schreibweise wie docs/PHASE8_ARGUMENTE.md, Vertreter (c, d, a, b)):
  F_q = F_n + F_n*om.  Fuer d != 0 sei w = 1/d = w1 + w2*om.
  a-Klasse (i, j), i in F_n^x, j in F_n:  d = 0: c in F_n + i*om;   d = 1/w mit w2 = i: om-Anteil von (c - i*om)*w gleich j.
  b-Klasse (i, j), i in F_n^x, j in F_n:  d = 0: c in F_n + i*om;   d = 1/w mit w1 = i: 1-Anteil  von (c - i*om)*w gleich j.
  Jede Klasse ist der affine Teil einer Baer-Unterebene durch den Fernpunkt der Waagerechten (q + n Punkte).
  Dazu F Symbole je Seite, die die volle Gerade d = 0 tragen.
Koerper und Elementnummern: GeneralGF aus scripts/gen_general_tqv.py (wie scripts/phase7_lift.py).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gen_general_tqv import GeneralGF  # noqa: E402


class Sq:
    def __init__(self, q):
        n = round(q ** 0.5)
        if n * n != q:
            sys.exit("q muss eine Quadratzahl sein")
        self.q, self.n = q, n
        self.F = F = GeneralGF(q)
        self.add, self.mul = F.add, F.mul
        self.neg = [next(b for b in range(q) if F.add[a][b] == 0) for a in range(q)]
        self.inv = [0] + [next(b for b in range(q) if F.mul[a][b] == 1) for a in range(1, q)]
        self.sub = sorted(x for x in range(q) if self.pw(x, n) == x)      # Teilkoerper F_n
        assert len(self.sub) == n
        self.idx = {x: k for k, x in enumerate(self.sub)}
        self.om = next(x for x in range(q) if x not in self.idx)
        self.comp = {}
        for z1 in self.sub:
            for z2 in self.sub:
                self.comp[self.add[z1][self.mul[z2][self.om]]] = (z1, z2)
        assert len(self.comp) == q

    def pw(self, a, e):
        r = 1
        for _ in range(e):
            r = self.mul[r][a]
        return r

    def minus(self, a, b):
        return self.add[a][self.neg[b]]


def build(q, f):
    S = Sq(q)
    n, add, mul, inv, idx, comp, om = S.n, S.add, S.mul, S.inv, S.idx, S.comp, S.om
    if not 0 <= f <= n:
        sys.exit("0 <= F <= n")
    v = q - n + f

    def cls(i, j):          # i in F_n^x, j in F_n  ->  0 .. q-n-1
        return (idx[i] - 1) * n + idx[j]

    def full(m):
        return q - n + m

    fill = full(0) if f else 0
    reps = []
    for d in range(q):
        if d == 0:
            for c in range(q):
                c1, c2 = comp[c]
                if c2 != 0:
                    for j in S.sub:
                        reps.append((c, 0, cls(c2, j), cls(c2, j)))
                    for m in range(f):
                        reps.append((c, 0, full(m), full(m)))
                elif f == 0:
                    reps.append((c, 0, 0, 0))
                else:
                    x = idx[c1]
                    for m in range(f):
                        reps.append((c, 0, full(m), full((m + x) % f)))
            continue
        w = inv[d]
        w1, w2 = comp[w]
        for c in range(q):
            if w2 != 0:
                z = mul[S.minus(c, mul[w2][om])][w]
                a = cls(w2, comp[z][1])
            else:
                m = idx[comp[mul[c][w]][1]]
                a = full(m) if m < f else fill
            if w1 != 0:
                z = mul[S.minus(c, mul[w1][om])][w]
                b = cls(w1, comp[z][0])
            else:
                m = idx[comp[mul[c][w]][0]]
                b = full(m) if m < f else fill
            reps.append((c, d, a, b))
    assert len(set(reps)) == len(reps)
    assert len(reps) == q * (q - 1) + (q - n) * (n + f) + n * max(f, 1)
    return reps, v


def check_model(q, v, reps, F=None):
    """Eigener Zaehler fuer die drei Bedingungen an R (unabhaengig von phase7_lift.py). Gibt Lueckenzahlen zurueck."""
    F = F or GeneralGF(q)
    add, mul = F.add, F.mul
    pts = {(c, d) for (c, d, a, b) in reps}
    miss_pts = q * q - len(pts)
    miss_pairs = v * v - len({(a, b) for (c, d, a, b) in reps})
    miss_lines = 0
    for side in (2, 3):
        seen = set()
        for r in reps:
            c, d, s = r[0], r[1], r[side]
            for al in range(q):
                seen.add((s, al, add[c][mul[al][d]]))
        miss_lines += v * q * q - len(seen)
    return miss_pts, miss_lines, miss_pairs


def klasse(q):
    """Eine Baer-Klasse (Geminis A_Baer, Richtung 1) einzeln: Punktzahl, Treffer aller Geraden c + al*d = u."""
    S = Sq(q)
    n, add, mul, inv, om = S.n, S.add, S.mul, S.inv, S.om
    A = {(x, 0) for x in S.sub}
    for y in S.sub:
        d = inv[S.minus(y, om)]
        A |= {(mul[x][d], d) for x in S.sub}
    hit = {(al, add[c][mul[al][d]]) for (c, d) in A for al in range(q)}
    shifts_disjoint = all(
        not ({(add[c][t], d) for (c, d) in A if d != 0} & {(c, d) for (c, d) in A if d != 0})
        for t in S.sub if t != 0)
    print(f"q={q} n={n}: |A|={len(A)} (q+n={q + n}), nicht getroffene Geraden={q * q - len(hit)}, "
          f"Verschiebungen um t in F_n\\0 ausserhalb d=0 disjunkt: {shifts_disjoint}")
    return q * q - len(hit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("q", type=int)
    ap.add_argument("f", type=int, nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--klasse", action="store_true")
    args = ap.parse_args()
    if args.klasse:
        sys.exit(1 if klasse(args.q) else 0)
    reps, v = build(args.q, args.f)
    mp, ml, mpair = check_model(args.q, v, reps)
    print(f"q={args.q} v={v} F={args.f} |R|={len(reps)} fehlende Punkte={mp} Geradentreffer={ml} Symbolpaare={mpair}")
    if args.out:
        with open(args.out, "w") as fh:
            for r in reps:
                fh.write(" ".join(map(str, r)) + "\n")
    sys.exit(1 if (mp or ml or mpair) else 0)


if __name__ == "__main__":
    main()
