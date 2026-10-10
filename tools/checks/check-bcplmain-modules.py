#!/usr/bin/env python3
"""Reconstruct BCPLMAIN-WIP byte-for-byte from staged source fragments.

By default check the fragments against the existing monolithic assembler
source. --output writes their concatenation to a separate file. This is
an offline staging tool; the regression build still uses the original.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PARTS = (
    "00-contract.asmfrag",
    "10-bootstrap-and-system.asmfrag",
    "20-streams-and-services.asmfrag",
    "30-control-data-and-end.asmfrag",
)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path,
                    help="write a generated assembler file (never overwrite baseline)")
    args = ap.parse_args()
    source = ROOT / "asm" / "bcplmain-wip.asm"
    folder = ROOT / "asm" / "bcplmain-wip"
    try:
        combined = b"".join((folder / name).read_bytes() for name in PARTS)
        baseline = source.read_bytes()
        if combined != baseline:
            from itertools import zip_longest
            first = next(i for i, (a, b) in enumerate(
                zip_longest(combined, baseline)) if a != b)
            raise ValueError(
                f"source mismatch at byte {first}: modular={len(combined)}, baseline={len(baseline)}")
        print(f"PASS BCPLMAIN staging: {len(PARTS)} fragments, {len(combined)} bytes identical")
        if args.output:
            if args.output.resolve() == source.resolve() or args.output.resolve() in {
                (folder / name).resolve() for name in PARTS
            }:
                raise ValueError("refusing to overwrite source or a fragment")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(combined)
            print(f"Wrote: {args.output}")
    except (OSError, ValueError) as exc:
        ap.exit(1, f"bcplmain-modules: FAIL: {exc}\n")

if __name__ == "__main__":
    main()
