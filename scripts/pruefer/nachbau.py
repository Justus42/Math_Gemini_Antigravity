#!/usr/bin/env python3
"""Eigener Nachbau (Claude): Lift einer Vertreterliste, eigene Koerperarithmetik, Horner-Schema.
Aufruf: nachbau.py q t LISTE AUSGABE [v]   (v<q: Retraktion z->z fuer z<v, sonst 0, nur Auswertungsspalten)"""
import sys, itertools
def field(q):
    for p in range(2, q + 1):
        if q % p == 0: break
    r, x = 0, q
    while x > 1: x //= p; r += 1
    assert p ** r == q
    if r == 1:
        return (lambda a, b: (a + b) % p), (lambda a, b: (a * b) % p)
    red = {(2, 3): [1, 1, 0], (3, 2): [1, 0]}[(p, r)]      # X^3 = X + 1 ; X^2 = -1  (niedrigster Grad zuerst)
    def dig(a): return [(a // p ** i) % p for i in range(r)]
    def num(d): return sum(c * p ** i for i, c in enumerate(d))
    def add(a, b): return num([(x + y) % p for x, y in zip(dig(a), dig(b))])
    def mul(a, b):
        da, db = dig(a), dig(b)
        prod = [0] * (2 * r - 1)
        for i, x in enumerate(da):
            for j, y in enumerate(db): prod[i + j] = (prod[i + j] + x * y) % p
        for e in range(2 * r - 2, r - 1, -1):
            c = prod[e]; prod[e] = 0
            if c:
                for i in range(r):
                    # X^r = -(f_0 + ... + f_{r-1} X^{r-1}), f = normiertes Minimalpolynom
                    prod[e - r + i] = (prod[e - r + i] - c * FMIN[i]) % p
        return num(prod[:r])
    FMIN = {(2, 3): [1, 1, 0], (3, 2): [1, 0]}[(p, r)]
    A = [[add(a, b) for b in range(q)] for a in range(q)]
    M = [[mul(a, b) for b in range(q)] for a in range(q)]
    return (lambda a, b: A[a][b]), (lambda a, b: M[a][b])
q, t = int(sys.argv[1]), int(sys.argv[2])
v = int(sys.argv[5]) if len(sys.argv) > 5 else q
add, mul = field(q)
reps = [tuple(map(int, l.split('#')[0].split())) for l in open(sys.argv[3]) if l.split('#')[0].strip()]
pi = [z if z < v else 0 for z in range(q)]
with open(sys.argv[4], 'w') as out:
    for (c, d, a, b) in reps:
        for low in itertools.product(range(q), repeat=t - 2):
            co = list(low) + [c, d]
            row = []
            for x in range(q):
                s = 0
                for e in range(t - 1, -1, -1): s = add(mul(s, x), co[e])
                row.append(pi[s])
            out.write(' '.join(map(str, row + [a, b])) + '\n')
