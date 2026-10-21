#!/usr/bin/env python3
"""Verify actual QOUT record, not a PASSREC constant in an IFOX listing."""
from __future__ import annotations
import argparse
from pathlib import Path
import importlib.util
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r0_a_make', HERE/'make-jobs.py')
make = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make)


def verify(text: str, profile: str) -> None:
    marker = make.PROFILES[profile][2]
    lines = [line.replace('\f', '').rstrip() for line in text.splitlines()]
    if lines.count(marker) != 1:
        raise ValueError(f'{profile}: exactly one GO/QOUT marker required; found {lines.count(marker)}')
    if any(x.strip() == 'R0 A INTERNAL CHECK FAILED' for x in lines):
        raise ValueError('unexpected failure marker')


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=make.PROFILES)
    p.add_argument('report',type=Path)
    a=p.parse_args()
    verify(a.report.read_text(encoding='utf-8'),a.profile)
    print(f'R.0 A {a.profile}: ACTUAL QOUT MARKER VERIFIED')


if __name__=='__main__':
    try: main()
    except (OSError,ValueError) as ex: raise SystemExit(f'R.0 A report FAILED: {ex}')
