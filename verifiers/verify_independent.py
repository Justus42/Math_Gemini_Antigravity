#!/usr/bin/env python3
"""Independent, pure-stdlib exact verifier for Covering Arrays CA(N; t, k, v).

Written strictly from the mathematical definition of a covering array without
reusing any code or algorithmic ideas from ca_verify.c.

Definition:
    An N x k array A over alphabet {0, 1, ..., v-1} is a covering array
    CA(N; t, k, v) iff for every t-subset of columns C = {c_1, ..., c_t}
    (0 <= c_1 < ... < c_t < k) and every tuple u in {0, ..., v-1}^t,
    there exists at least one row r in {0, ..., N-1} such that
    (A[r][c_1], ..., A[r][c_t]) == u.

Exit codes:
    0 : VERIFIED (valid format, dimensions, range, and full t-way coverage)
    1 : FAILED (valid format/range/dimensions, but missing required t-tuples)
    2 : FAILED (invalid CLI arguments, file I/O error, format, dimensions, or range)
"""

from __future__ import annotations

import argparse
import itertools
import math
import re
import sys
import time
from pathlib import Path

UNSIGNED_INT_RE = re.compile(r"^[0-9]+$")
NEGATIVE_INT_RE = re.compile(r"^-[0-9]+$")


def parse_and_validate_array(
    path: Path,
    t: int,
    v: int,
    expected_n: int | None = None,
    expected_k: int | None = None,
) -> tuple[list[list[int]], int, int]:
    """Load array and enforce strict rectangular dimensions and 0 <= a_ij < v."""
    if t < 1:
        raise ValueError(f"Strength t must be >= 1, got {t}")
    if v < 2:
        raise ValueError(f"Alphabet size v must be >= 2, got {v}")
    if expected_n is not None and expected_n < 1:
        raise ValueError(f"--expected-n must be >= 1, got {expected_n}")
    if expected_k is not None and expected_k < t:
        raise ValueError(f"--expected-k must be >= t ({t}), got {expected_k}")

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read file '{path}': {exc}") from exc

    lines = raw_text.splitlines()
    if not lines:
        raise ValueError(f"Array file '{path}' is empty")

    rows: list[list[int]] = []
    width: int | None = None

    for line_no, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            raise ValueError(f"Empty or whitespace-only line at line {line_no}")

        # Split strictly on whitespace; reject comma-only or malformed tokens
        tokens = stripped.split()
        if width is None:
            width = len(tokens)
            if width == 0:
                raise ValueError(f"Row {line_no} has 0 columns")
        elif len(tokens) != width:
            raise ValueError(
                f"Inconsistent column count at line {line_no}: "
                f"expected {width}, got {len(tokens)}"
            )

        parsed_row: list[int] = []
        for col_idx, tok in enumerate(tokens):
            if UNSIGNED_INT_RE.match(tok):
                val = int(tok)
            elif NEGATIVE_INT_RE.match(tok):
                raise ValueError(
                    f"Negative symbol at row {line_no}, col {col_idx + 1}: "
                    f"{tok!r} not in [0, {v - 1}]"
                )
            else:
                raise ValueError(
                    f"Non-integer entry at row {line_no}, col {col_idx + 1}: {tok!r}"
                )
            if val < 0 or val >= v:
                raise ValueError(
                    f"Out-of-range symbol at row {line_no}, col {col_idx + 1}: "
                    f"{val} not in [0, {v - 1}]"
                )
            parsed_row.append(val)
        rows.append(parsed_row)

    actual_n = len(rows)
    actual_k = width if width is not None else 0

    if expected_n is not None and actual_n != expected_n:
        raise ValueError(
            f"Row count mismatch: expected N={expected_n}, got N={actual_n}"
        )
    if expected_k is not None and actual_k != expected_k:
        raise ValueError(
            f"Column count mismatch: expected k={expected_k}, got k={actual_k}"
        )
    if actual_k < t:
        raise ValueError(
            f"Column count k={actual_k} is smaller than strength t={t}"
        )

    return rows, actual_n, actual_k


def verify_coverage(
    rows: list[list[int]],
    t: int,
    k: int,
    v: int,
    max_examples: int = 10,
) -> tuple[int, int, int, list[tuple[tuple[int, ...], tuple[int, ...]]]]:
    """Exhaustively check every C(k, t) column subset covers all v^t tuples.

    Returns:
        (total_col_sets, incomplete_col_sets, total_missing_tuples, example_gaps)
    """
    required_tuples = v ** t
    expected_col_sets = math.comb(k, t)

    # Transpose into column tuples for direct projection via zip()
    cols = [tuple(row[c] for row in rows) for c in range(k)]

    checked_sets = 0
    incomplete_sets = 0
    total_missing = 0
    examples: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

    for col_subset in itertools.combinations(range(k), t):
        checked_sets += 1
        covered = set(zip(*(cols[c] for c in col_subset)))
        missing_here = required_tuples - len(covered)
        if missing_here > 0:
            incomplete_sets += 1
            total_missing += missing_here
            if len(examples) < max_examples:
                for tup in itertools.product(range(v), repeat=t):
                    if tup not in covered:
                        examples.append((col_subset, tup))
                        if len(examples) >= max_examples:
                            break

    if checked_sets != expected_col_sets:
        raise RuntimeError(
            f"Internal check failed: checked {checked_sets} != C({k},{t})={expected_col_sets}"
        )

    return checked_sets, incomplete_sets, total_missing, examples


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Independent pure-stdlib verifier for Covering Arrays CA(N; t, k, v)."
    )
    parser.add_argument("file", type=Path, help="Path to plain-text array file")
    parser.add_argument("t", type=int, help="Covering strength t")
    parser.add_argument("v", type=int, help="Alphabet size v (symbols must be in 0..v-1)")
    parser.add_argument(
        "--expected-n",
        "-n",
        type=int,
        default=None,
        help="Optional strict check on row count N",
    )
    parser.add_argument(
        "--expected-k",
        "-k",
        type=int,
        default=None,
        help="Optional strict check on column count k",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=10,
        help="Maximum missing (column-subset, tuple) examples to print on failure",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    start = time.perf_counter()
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        rows, n, k = parse_and_validate_array(
            path=args.file,
            t=args.t,
            v=args.v,
            expected_n=args.expected_n,
            expected_k=args.expected_k,
        )
    except ValueError as exc:
        elapsed = time.perf_counter() - start
        print(f"FAILED (VALIDATION): {exc} [elapsed: {elapsed:.4f}s]", file=sys.stderr)
        return 2

    checked_sets, incomplete_sets, total_missing, examples = verify_coverage(
        rows=rows,
        t=args.t,
        k=k,
        v=args.v,
        max_examples=args.max_examples,
    )
    elapsed = time.perf_counter() - start
    total_required = checked_sets * (args.v ** args.t)

    if total_missing == 0:
        print(
            f"VERIFIED: CA(N={n}; t={args.t}, k={k}, v={args.v}) - "
            f"all {checked_sets} column sets cover all {args.v ** args.t} tuples "
            f"({total_required} total interactions) [elapsed: {elapsed:.4f}s]"
        )
        return 0

    print(
        f"FAILED (COVERAGE): CA(N={n}; t={args.t}, k={k}, v={args.v}) - "
        f"missing {total_missing}/{total_required} interactions across "
        f"{incomplete_sets}/{checked_sets} column sets [elapsed: {elapsed:.4f}s]",
        file=sys.stderr,
    )
    for col_subset, tup in examples:
        print(f"  gap: cols={col_subset} tuple={tup}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
