#!/usr/bin/env python3
"""Test-only FINISH CLOSE probe for regression 084."""
from __future__ import annotations
import argparse
from pathlib import Path

ANCHOR = """FINRETN  BAL   14,RELMEM"""
REPLACEMENT = """FINRETN  CLOSE (BCPOUT)
         BAL   14,RELMEM"""

def instrument(text: str) -> str:
    if text.count(ANCHOR) != 1:
        raise ValueError("expected exactly one FINRETN teardown anchor")
    if text.count("BCPOUT   DCB") != 1:
        raise ValueError("expected exactly one BCPOUT DCB")
    result = text.replace(ANCHOR, REPLACEMENT, 1)
    for lineno, line in enumerate(result.splitlines(), 1):
        if len(line) > 71 or "\t" in line or line.rstrip() != line:
            raise ValueError(f"line {lineno}: assembler column/hygiene error")
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    original = args.source.read_text(encoding="ascii")
    args.source.write_text(instrument(original), encoding="ascii", newline="\n")
    print("084 CLOSE probe: OK (test-only FINISH CLOSE insertion)")

if __name__ == "__main__":
    main()
