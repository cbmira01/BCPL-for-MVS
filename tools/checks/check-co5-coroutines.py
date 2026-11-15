#!/usr/bin/env python3
"""Offline CO.5 native suite source/oracle verification (never submits JES)."""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'tests/coroutines'
RUNNER = ROOT / 'tools/checks/run-coroutine-regression.py'


def main() -> int:
    if not RUNNER.is_file() or not CASES.is_dir():
        print('CO.5 offline check FAIL: missing adapter or suite directory', file=sys.stderr)
        return 1
    for number in range(177, 190):
        matches = list(CASES.glob(f'{number:03d}-*'))
        if len(matches) != 1 or not matches[0].is_dir():
            print(f'CO.5 {number:03d} FAIL: missing/ambiguous fixture', file=sys.stderr)
            return 1
        command = [sys.executable, '-B', str(RUNNER), str(number), str(matches[0]), '--check']
        proc = subprocess.run(command, cwd=ROOT, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              check=False)
        print(proc.stdout, end='')
        if proc.returncode:
            print(f'CO.5 offline check STOP: case {number:03d} RC={proc.returncode}', file=sys.stderr)
            return 1
    print('CO.5 OFFLINE SOURCE/ORACLE CHECK PASS: 13/13')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
