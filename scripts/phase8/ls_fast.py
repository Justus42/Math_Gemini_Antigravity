"""Fast candidate enumeration: one base class, then its orbit under (c,d)->(k*c+r*d+t, d)."""
import itertools


def candidates_fast(q):
    chi = lambda x: 0 if x == 0 else (1 if pow(x, (q - 1) // 2, q) == 1 else q - 1)
    U = [(x, x * chi(x) % q) for x in range(q)]
    D = {(y1 - y2) * pow(x1 - x2, -1, q) % q for (x1, y1), (x2, y2) in itertools.combinations(U, 2)}
    assert len(D) == (q + 3) // 2
    m = min(D - {1, q - 1})
    BU = {(y - m * x) % q for x, y in U}
    binf = min(b for b in range(q) if b not in BU)
    X0 = []
    for x, y in U:
        w = pow((y - m * x - binf) % q, -1, q)
        X0.append((x * w % q, w))
    D0 = [pow((mu - m) % q, -1, q) for mu in D - {m}]
    out = {}
    for k in range(1, q):
        for r in range(q):
            for t in range(q):
                X = frozenset(((k * c + r * d + t) % q, d) for c, d in X0)
                out[X] = frozenset((k * c + t) % q for c in D0)
    return sorted({d for c, d in X0}), out
