#!/usr/bin/env python3
"""Require each distinct Decision G boundary marker in actual report."""
from __future__ import annotations
import argparse
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent


def expected_markers():
    spec=importlib.util.spec_from_file_location('r0g_job',HERE/'make-job.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(f'R0 G{i:02d} {row[0]} PASS' for i,row in enumerate(module.CASES,1))


def verify(text:str)->None:
    lines=[x.replace('\f','').rstrip() for x in text.splitlines()]
    for marker in expected_markers():
        if lines.count(marker)!=1:
            raise ValueError(f'expected one actual GO output {marker!r}, saw {lines.count(marker)}')
    if any(line=='R0 G BOUNDARY CASE FAILED' for line in lines):
        raise ValueError('GO emitted failure marker')


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('report',type=Path)
    args=a.parse_args()
    verify(args.report.read_text('utf-8'))
    print(f'R.0 G LIMITS: {len(expected_markers())} GO MARKERS VERIFIED')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as ex:
        raise SystemExit(f'R.0 G report verification FAILED: {ex}')
