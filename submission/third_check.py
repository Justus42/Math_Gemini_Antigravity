#!/usr/bin/env python3
"""Dritte, unabhaengige Pruefung von Covering Arrays der Staerke 3.

Geschrieben von Claude (Anthropic) am 25.11.2026 als Gegenpruefung zu
verifiers/ca_verify.c und verifiers/verify_independent.py. Teilt mit beiden
keinen Code. Braucht numpy.

Aufruf:  python3 third_check.py CA_<N>_3_<k>_<v>.txt [weitere Dateien]
N, k und v werden aus dem Dateinamen gelesen. Exit-Code 0 nur, wenn alle
Dateien gueltig sind.

Verfahren: Fuer jedes Spaltentripel werden die Zeilen als Zahl
a*v*v + b*v + c kodiert; das Tripel ist gedeckt, wenn genau v^3
verschiedene Werte vorkommen.
"""
import re
import sys
import time

import numpy as np


def check(path):
    m = re.search(r"CA_(\d+)_(\d+)_(\d+)_(\d+)\.txt$", path)
    if not m:
        raise SystemExit(f"Dateiname passt nicht zum Muster: {path}")
    N, t, k, v = map(int, m.groups())
    if t != 3:
        raise SystemExit("Nur Staerke 3 wird geprueft.")
    A = np.loadtxt(path, dtype=np.int64)
    if A.shape != (N, k):
        raise SystemExit(f"Form {A.shape} statt {(N, k)}: {path}")
    if A.min() < 0 or A.max() >= v:
        raise SystemExit(f"Symbol ausserhalb 0..{v - 1}: {path}")
    need = v ** 3
    bad = 0
    for a in range(k):
        for b in range(a + 1, k):
            ab = A[:, a] * v + A[:, b]
            rest = ab[:, None] * v + A[:, b + 1:]
            for j in range(rest.shape[1]):
                if np.unique(rest[:, j]).size != need:
                    bad += 1
    return N, k, v, bad


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    failed = 0
    for p in sys.argv[1:]:
        t0 = time.time()
        N, k, v, bad = check(p)
        status = "OK" if bad == 0 else f"FEHLER ({bad} Spaltentripel unvollstaendig)"
        print(f"CA({N};3,{k},{v}): {status}  {time.time() - t0:.1f}s", flush=True)
        failed += bad != 0
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
