#!/usr/bin/env python3
"""Require the actual BCPL program's exact QUERY success record."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = 'R0 QUERY TWO DISPATCHERS PASS'


def verify(text: str) -> None:
    # The IFOX listing contains instruction/source constants, but only an
    # exact report record containing the marker is accepted as GO output.
    lines = [line.replace('\f', '').rstrip() for line in text.splitlines()]
    matched = sum(line == MARKER for line in lines)
    if matched != 1:
        raise ValueError(f'expected one exact BCPL GO line, found {matched}')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    a = p.parse_args()
    verify(a.report.read_text(encoding='utf-8'))
    print(f'VERIFIED QUERY GO OUTPUT: {MARKER}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 QUERY verification FAILED: {exc}')
