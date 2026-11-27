"""Small finite fields GF(q), q prime power, own implementation (independent of the repo)."""
import itertools

IRRED = {4: (2, [1, 1, 1]), 8: (2, [1, 1, 0, 1]), 9: (3, [1, 0, 1]), 16: (2, [1, 1, 0, 0, 1]),
         25: (5, [2, 0, 1]), 27: (3, [1, 2, 0, 1])}


def is_prime(n):
    return n > 1 and all(n % i for i in range(2, int(n ** 0.5) + 1))


class GF:
    def __init__(self, q):
        self.q = q
        if is_prime(q):
            self.p, self.n = q, 1
            self.add = [[(a + b) % q for b in range(q)] for a in range(q)]
            self.mul = [[(a * b) % q for b in range(q)] for a in range(q)]
        else:
            p, mod = IRRED[q]
            n = len(mod) - 1
            self.p, self.n = p, n

            def dec(x):
                return [(x // p ** i) % p for i in range(n)]

            def enc(v):
                return sum(c * p ** i for i, c in enumerate(v))

            def mulp(a, b):
                r = [0] * (2 * n - 1)
                for i, x in enumerate(a):
                    for j, y in enumerate(b):
                        r[i + j] = (r[i + j] + x * y) % p
                for d in range(2 * n - 2, n - 1, -1):
                    c = r[d]
                    if c:
                        for j in range(n + 1):
                            r[d - n + j] = (r[d - n + j] - c * mod[j]) % p
                return r[:n]

            self.add = [[enc([(x + y) % p for x, y in zip(dec(a), dec(b))]) for b in range(q)] for a in range(q)]
            self.mul = [[enc(mulp(dec(a), dec(b))) for b in range(q)] for a in range(q)]
        self.neg = [next(b for b in range(q) if self.add[a][b] == 0) for a in range(q)]
        self.inv = [0] + [next(b for b in range(q) if self.mul[a][b] == 1) for a in range(1, q)]
        # sanity: field axioms (cheap spot checks)
        for a in range(1, q):
            assert sorted(self.mul[a]) == list(range(q))
        for a, b, c in itertools.islice(itertools.product(range(q), repeat=3), 0, 4000, 7):
            assert self.mul[a][self.add[b][c]] == self.add[self.mul[a][b]][self.mul[a][c]]

    def sub(self, a, b):
        return self.add[a][self.neg[b]]

    def pw(self, a, e):
        r = 1
        for _ in range(e):
            r = self.mul[r][a]
        return r

    def poly_eval(self, coeffs, x):
        """coeffs[i] is the coefficient of x^i."""
        r = 0
        for c in reversed(coeffs):
            r = self.add[self.mul[r][x]][c]
        return r
