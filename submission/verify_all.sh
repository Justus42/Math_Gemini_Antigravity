#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== 1. Verifier READ-ONLY Integrity Check ==="
sha256sum -c verifiers/SHA256SUMS
if git rev-parse --verify main >/dev/null 2>&1; then
    DIFF_OUT="$(git diff main -- verifiers/)"
    if [ -n "$DIFF_OUT" ]; then
        echo "ERROR: verifiers/ differs from main!" >&2
        exit 1
    fi
    echo "git diff main -- verifiers/: CLEAN (empty)"
fi

if [ ! -x verifiers/ca_verify ]; then
    echo "Compiling verifiers/ca_verify locally from verifiers/ca_verify.c..."
    gcc -O3 -o verifiers/ca_verify verifiers/ca_verify.c -lm
fi

echo ""
echo "=== 2. Verifier Unit Test Suite (23/23) ==="
python3 verifiers/test_verifiers.py

echo ""
echo "=== 3. Results SHA-256 Checksums ==="
env -C results sha256sum -c SHA256SUMS

echo ""
echo "=== 4. Strict ca-tools Canonical Format Audit ==="
python3 - << 'EOF'
import glob, os, re, sys

files = sorted(glob.glob("results/CA_*.txt"))
assert files, "No results/CA_*.txt files found!"
pat = re.compile(r"^CA_(\d+)_(\d+)_(\d+)_(\d+)\.txt$")
for path in files:
    base = os.path.basename(path)
    m = pat.match(base)
    assert m, f"Unexpected filename format: {base}"
    N, t, k, v = map(int, m.groups())
    raw = open(path, "rb").read()
    assert b"\r" not in raw, f"CR byte found in {path}"
    assert raw.endswith(b"\n"), f"Missing trailing newline in {path}"
    lines = raw.decode("ascii").split("\n")[:-1]
    assert len(lines) == N, f"{path}: expected {N} rows, got {len(lines)}"
    for idx, line in enumerate(lines):
        assert line == line.strip(), f"{path} line {idx+1}: leading/trailing whitespace"
        assert "  " not in line, f"{path} line {idx+1}: double space"
        toks = line.split(" ")
        assert len(toks) == k, f"{path} line {idx+1}: expected {k} cols, got {len(toks)}"
        for tok in toks:
            assert tok.isdigit(), f"{path} line {idx+1}: non-digit token {tok!r}"
            val = int(tok)
            assert 0 <= val < v, f"{path} line {idx+1}: value {val} out of range 0..{v-1}"
            assert tok == str(val), f"{path} line {idx+1}: leading zero in {tok!r}"
    print(f"FORMAT_OK {base}: N={N}, t={t}, k={k}, v={v}, bytes={len(raw)}")
print(f"All {len(files)} results/CA_*.txt files passed strict ca-tools format audit.")
EOF

echo ""
echo "=== 5. Fresh Parallel Dual-Verification (xargs -P 2) ==="
verify_one() {
    local path="$1"
    python3 - "$path" << 'PYEOF'
import os, re, subprocess, sys, time
path = sys.argv[1]
base = os.path.basename(path)
N, t, k, v = map(int, re.match(r"^CA_(\d+)_(\d+)_(\d+)_(\d+)\.txt$", base).groups())

t0 = time.perf_counter()
r1 = subprocess.run(["./verifiers/ca_verify", path, str(t), str(v)], capture_output=True, text=True)
dt1 = time.perf_counter() - t0
if r1.returncode != 0:
    print(f"FAIL ca_verify {base}: {r1.stdout} {r1.stderr}", file=sys.stderr)
    sys.exit(1)

t0 = time.perf_counter()
r2 = subprocess.run(["python3", "verifiers/verify_independent.py", path, str(t), str(v), "-n", str(N), "-k", str(k)], capture_output=True, text=True)
dt2 = time.perf_counter() - t0
if r2.returncode != 0:
    print(f"FAIL py_verify {base}: {r2.stdout} {r2.stderr}", file=sys.stderr)
    sys.exit(1)

print(f"DUAL_PASS {base} N={N} t={t} k={k} v={v} ca_verify_s={dt1:.3f} py_verify_s={dt2:.3f}", flush=True)
PYEOF
}
export -f verify_one

find results -maxdepth 1 -name 'CA_*.txt' | sort | xargs -P 2 -I {} bash -c 'verify_one "$@"' _ {}

echo ""
echo "=== ALL AUDIT & DUAL-VERIFICATION CHECKS PASSED ==="
