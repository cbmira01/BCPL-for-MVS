#!/usr/bin/env python3
"""Verify that CG370D differs from CG370 only by diagnostic comments."""

from __future__ import annotations

import argparse
from pathlib import Path
import difflib
import sys

MARKER = "* CG370-DIAG:"


def read(path: Path) -> list[str]:
    return path.read_text(encoding="latin-1").splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check-cg370-diagnostic",
        description=(
            "Strip CG370D diagnostic comment lines and compare the remaining "
            "assembler with ordinary CG370 output."
        ),
    )
    parser.add_argument("baseline")
    parser.add_argument("diagnostic")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    diagnostic_path = Path(args.diagnostic)

    for path in (baseline_path, diagnostic_path):
        if not path.is_file():
            print(f"{path}: file not found", file=sys.stderr)
            return 1

    baseline = read(baseline_path)
    diagnostic = read(diagnostic_path)
    comments = [line for line in diagnostic if line.startswith(MARKER)]
    stripped = [line for line in diagnostic if not line.startswith(MARKER)]

    if not comments:
        print(
            f"{diagnostic_path}: no {MARKER!r} lines found",
            file=sys.stderr,
        )
        return 1

    if baseline != stripped:
        print(
            "CG370D semantic-equivalence check FAILED: non-comment output differs",
            file=sys.stderr,
        )
        diff = difflib.unified_diff(
            baseline,
            stripped,
            fromfile=str(baseline_path),
            tofile=f"{diagnostic_path} (diagnostics stripped)",
            lineterm="",
        )
        for line in diff:
            print(line, file=sys.stderr)
        return 1

    print("CG370D semantic-equivalence check: PASS")
    print(f"diagnostic comments: {len(comments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
