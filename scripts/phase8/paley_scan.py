import sys, json
from paley import count, simple, choose
def isp(n): return n > 2 and all(n % i for i in range(2, int(n ** .5) + 1))
qs = [q for q in range(11, 62) if isp(q)] + [71, 83, 101, 127, 151, 199, 251, 307, 401, 499]
print("q | q%4 | formula | simple: j, m, saved/q^2 | searched: j, n, m, saved/q^2 | m/q^2")
for q in qs:
    F = q * q + q * (q - 1) // 2
    best = min((count(q, j, simple(q, j))[0], j) for j in range(0, q // 6))
    ms, js = best
    bo = None
    if q <= 251:
        for j in sorted({max(js - 1, 0), js, js + 1, js + 2}):
            st, E = choose(q, j, 6 if q < 100 else 12)
            m = count(q, j, E)[0]
            if bo is None or m < bo[0]:
                bo = (m, j, len(E), st)
    mo = bo[0] if bo else ms
    print(f"{q} | {q%4} | {F} | j={js} m={ms} {(F-ms)/q/q:.4f} | " + (f"j={bo[1]} n={bo[2]} m={bo[0]} {(F-bo[0])/q/q:.4f} {bo[3]}" if bo else "-") + f" | {min(mo,ms)/q/q:.4f}", flush=True)
