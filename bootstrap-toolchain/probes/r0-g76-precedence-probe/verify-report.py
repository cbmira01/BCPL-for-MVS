#!/usr/bin/env python3
"""Require one GO program output marker (never count source listings)."""
from pathlib import Path
import argparse
import re

MARKER = 'R0 G76 INSTALLED BLIB PASS'

def verify(text: str) -> None:
    lines = text.replace('\f', '').splitlines()
    actual = [x.rstrip() for x in lines if x.rstrip() == MARKER]
    if len(actual) != 1:
        raise ValueError(f'expected one exact GO marker, found {len(actual)}')
    if not any(re.fullmatch(r'R0 G76 INSTALLED BLIB PASS\s*', x)
               for x in lines):
        raise ValueError('missing full GO output marker')

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    a = p.parse_args()
    verify(a.report.read_text('utf-8'))
    print(f'VERIFIED ACTUAL GO OUTPUT: {MARKER}')

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 G76 report verification FAILED: {exc}')
