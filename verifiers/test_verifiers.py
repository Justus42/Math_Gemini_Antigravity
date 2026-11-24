#!/usr/bin/env python3
"""Automated test suite for the Dual-Verifier pipeline.

Verifies that BOTH independent verifiers:
  1. verifiers/ca_verify            (C verifier from chrispbsmolen/ca-tools)
  2. verifiers/verify_independent.py (independent pure-Python stdlib verifier)

consistently:
  - ACCEPT valid baseline covering arrays (exit code 0), and
  - REJECT all four intentional defect classes (exit code != 0):
      (a) deleted row causing missing t-tuples,
      (b) single flipped entry within [0, v-1] breaking at least one t-tuple,
      (c) invalid out-of-range symbol >= v (plus negative & non-integer checks),
      (d) wrong column count (ragged row, and expected-k / <t column checks).
"""

from __future__ import annotations

import itertools
import subprocess
import sys
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CA_VERIFY_BIN = REPO_ROOT / "verifiers" / "ca_verify"
PY_VERIFY_SCRIPT = REPO_ROOT / "verifiers" / "verify_independent.py"
BASELINES_DIR = REPO_ROOT / "baselines"


@dataclass(frozen=True)
class BaselineSpec:
    name: str
    path: Path
    n: int
    t: int
    k: int
    v: int


BASELINES: list[BaselineSpec] = [
    BaselineSpec("CA(27;3,4,3)", BASELINES_DIR / "CA_27_3_4_3.txt", 27, 3, 4, 3),
    BaselineSpec("CA(135;4,9,3)", BASELINES_DIR / "CA_135_4_9_3.txt", 135, 4, 9, 3),
    BaselineSpec("CA(185;3,10,5)", BASELINES_DIR / "CA_185_3_10_5.txt", 185, 3, 10, 5),
    BaselineSpec("CA(361;3,9,6)", BASELINES_DIR / "CA_361_3_9_6.txt", 361, 3, 9, 6),
]


def load_rows(path: Path) -> list[list[str]]:
    return [line.strip().split() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_rows(path: Path, rows: list[list[str]]) -> None:
    path.write_text("\n".join(" ".join(r) for r in rows) + "\n", encoding="utf-8")


def find_critical_row_and_col(rows: list[list[str]], t: int) -> tuple[int, int]:
    """Deterministically find a (row, col) participating in a uniquely covered t-tuple.

    Deleting that row OR flipping (row, col) to any other value in [0, v-1]
    is guaranteed to break coverage of at least one t-tuple.
    """
    k = len(rows[0])
    for col_subset in itertools.combinations(range(k), t):
        counts: Counter[tuple[str, ...]] = Counter()
        first_row: dict[tuple[str, ...], int] = {}
        for r_idx, row in enumerate(rows):
            tup = tuple(row[c] for c in col_subset)
            counts[tup] += 1
            if tup not in first_row:
                first_row[tup] = r_idx
        for tup, cnt in counts.items():
            if cnt == 1:
                return first_row[tup], col_subset[0]
    raise RuntimeError("No uniquely covered t-tuple found in baseline array")


def run_cmd(cmd: list[str]) -> tuple[int, float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    output = (proc.stdout + proc.stderr).strip().splitlines()
    summary = output[-1] if output else "(no output)"
    return proc.returncode, elapsed_ms, summary


def run_both(
    array_path: Path,
    t: int,
    v: int,
    expected_n: int | None = None,
    expected_k: int | None = None,
) -> tuple[tuple[int, float, str], tuple[int, float, str]]:
    c_cmd = [str(CA_VERIFY_BIN), str(array_path), str(t), str(v)]
    py_cmd = [sys.executable, str(PY_VERIFY_SCRIPT), str(array_path), str(t), str(v)]
    if expected_n is not None:
        py_cmd.extend(["-n", str(expected_n)])
    if expected_k is not None:
        py_cmd.extend(["-k", str(expected_k)])
    return run_cmd(c_cmd), run_cmd(py_cmd)


def main() -> int:
    if not CA_VERIFY_BIN.is_file():
        print(f"ERROR: Missing compiled verifier: {CA_VERIFY_BIN}", file=sys.stderr)
        return 2
    if not PY_VERIFY_SCRIPT.is_file():
        print(f"ERROR: Missing independent verifier: {PY_VERIFY_SCRIPT}", file=sys.stderr)
        return 2

    failures: list[str] = []
    results_table: list[tuple[str, str, str, int, float, int, float, str]] = []

    def record(
        baseline_name: str,
        case_name: str,
        expect_accept: bool,
        c_res: tuple[int, float, str] | None,
        py_res: tuple[int, float, str],
    ) -> None:
        py_rc, py_ms, _ = py_res
        py_ok = (py_rc == 0) if expect_accept else (py_rc != 0)
        if c_res is not None:
            c_rc, c_ms, _ = c_res
            c_ok = (c_rc == 0) if expect_accept else (c_rc != 0)
        else:
            c_rc, c_ms, c_ok = -1, 0.0, True

        status = "PASS" if (c_ok and py_ok) else "FAIL"
        if status == "FAIL":
            failures.append(
                f"{baseline_name} / {case_name}: expected={'ACCEPT' if expect_accept else 'REJECT'}, "
                f"ca_verify={c_rc}, verify_independent={py_rc}"
            )
        results_table.append(
            (
                baseline_name,
                case_name,
                "ACCEPT" if expect_accept else "REJECT",
                c_rc,
                c_ms,
                py_rc,
                py_ms,
                status,
            )
        )

    with tempfile.TemporaryDirectory(prefix="ca_verifier_tests_") as tmpdir:
        tmp = Path(tmpdir)

        for spec in BASELINES:
            rows = load_rows(spec.path)
            assert len(rows) == spec.n, f"{spec.path}: expected {spec.n} rows, got {len(rows)}"
            assert all(len(r) == spec.k for r in rows), f"{spec.path}: non-rectangular baseline"

            crit_row, crit_col = find_critical_row_and_col(rows, spec.t)

            # 0. Valid baseline (both MUST accept)
            c_res, py_res = run_both(spec.path, spec.t, spec.v, expected_n=spec.n, expected_k=spec.k)
            record(spec.name, "valid_baseline", True, c_res, py_res)

            # (a) Deleted row causing missing tuples (both MUST reject without -n/-k override)
            del_path = tmp / f"{spec.path.stem}_a_deleted_row.txt"
            write_rows(del_path, rows[:crit_row] + rows[crit_row + 1 :])
            c_res, py_res = run_both(del_path, spec.t, spec.v)
            record(spec.name, "(a)_deleted_row", False, c_res, py_res)

            # (b) Flipped entry within [0, v-1] breaking >= 1 tuple (both MUST reject)
            flip_path = tmp / f"{spec.path.stem}_b_flipped_entry.txt"
            flipped = [list(r) for r in rows]
            old_val = int(flipped[crit_row][crit_col])
            flipped[crit_row][crit_col] = str((old_val + 1) % spec.v)
            write_rows(flip_path, flipped)
            c_res, py_res = run_both(flip_path, spec.t, spec.v, expected_n=spec.n, expected_k=spec.k)
            record(spec.name, "(b)_flipped_entry", False, c_res, py_res)

            # (c) Invalid symbol >= v (both MUST reject)
            oor_path = tmp / f"{spec.path.stem}_c_symbol_ge_v.txt"
            oor = [list(r) for r in rows]
            # Pick a cell whose replacement with v still leaves at least one 0 in the array
            oor[crit_row][crit_col] = str(spec.v)
            write_rows(oor_path, oor)
            c_res, py_res = run_both(oor_path, spec.t, spec.v, expected_n=spec.n, expected_k=spec.k)
            record(spec.name, "(c)_symbol_ge_v", False, c_res, py_res)

            # (d) Wrong column count: ragged row (row 0 missing last column) -> both MUST reject
            ragged_path = tmp / f"{spec.path.stem}_d_wrong_cols_ragged.txt"
            ragged = [list(r) for r in rows]
            ragged[0] = ragged[0][:-1]
            write_rows(ragged_path, ragged)
            c_res, py_res = run_both(ragged_path, spec.t, spec.v)
            record(spec.name, "(d)_wrong_cols_ragged", False, c_res, py_res)

        # Extra strict-validation checks on CA(27; 3, 4, 3) for verify_independent.py
        oa_spec = BASELINES[0]
        oa_rows = load_rows(oa_spec.path)

        # (c2) Negative symbol (-1) -> both reject
        neg_path = tmp / "oa_c2_negative_symbol.txt"
        neg = [list(r) for r in oa_rows]
        neg[0][0] = "-1"
        write_rows(neg_path, neg)
        c_res, py_res = run_both(neg_path, oa_spec.t, oa_spec.v)
        record(oa_spec.name, "(c2)_negative_symbol", False, c_res, py_res)

        # (c3) Non-integer token (1.5) -> both reject
        flt_path = tmp / "oa_c3_non_integer.txt"
        flt = [list(r) for r in oa_rows]
        flt[0][0] = "1.5"
        write_rows(flt_path, flt)
        c_res, py_res = run_both(flt_path, oa_spec.t, oa_spec.v)
        record(oa_spec.name, "(c3)_non_integer_entry", False, c_res, py_res)

        # (d2) Uniform wrong column count (all rows k-1) checked via --expected-k on verify_independent.py
        unif_col_path = tmp / "oa_d2_uniform_wrong_k.txt"
        write_rows(unif_col_path, [r[:-1] for r in oa_rows])
        py_res = run_cmd(
            [
                sys.executable,
                str(PY_VERIFY_SCRIPT),
                str(unif_col_path),
                str(oa_spec.t),
                str(oa_spec.v),
                "-k",
                str(oa_spec.k),
            ]
        )
        record(oa_spec.name, "(d2)_uniform_wrong_k", False, None, py_res)

    # Print formatted results table
    header = (
        f"{'Baseline':<15} | {'Test Case':<23} | {'Expect':<6} | "
        f"{'ca_verify rc/ms':<16} | {'py_verify rc/ms':<16} | {'Status'}"
    )
    print(header)
    print("-" * len(header))
    for base, case, exp, c_rc, c_ms, py_rc, py_ms, status in results_table:
        c_str = "n/a" if c_rc == -1 else f"rc={c_rc:<2} {c_ms:6.2f} ms"
        py_str = f"rc={py_rc:<2} {py_ms:6.2f} ms"
        print(f"{base:<15} | {case:<23} | {exp:<6} | {c_str:<16} | {py_str:<16} | {status}")

    print("-" * len(header))
    total = len(results_table)
    passed = total - len(failures)
    print(f"Summary: {passed}/{total} test cases passed.")

    if failures:
        print("\nFAILURES:", file=sys.stderr)
        for msg in failures:
            print(f"  - {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
