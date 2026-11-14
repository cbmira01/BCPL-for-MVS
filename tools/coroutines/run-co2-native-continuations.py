#!/usr/bin/env python3
"""CO.2 native repeated-continuation candidate; temporary MVS objects only.

Reuses the accepted CO.2 compiler/IFOX/IEWL/GO driver without editing
installed BOOT_OBJ or allocating any permanent BCPL global numbers.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co2-native-changeco.py')
SOURCE = (ROOT / 'packaging/milestones/coroutines/candidates'
          / 'co2-native-continuations/source.bcpl')
EVIDENCE = ROOT / 'workarea/co2-native-continuations'
BASE_EXPECTED = ('A1', 'B1', 'A2', 'R1', 'B2', 'R2', 'PASS')
EXPECTED = ('X1', 'Y1', 'X2', 'Y2', 'X3', 'R1', 'Y3', 'R2', 'PASS')
FAILURES = ('FALLOC', 'FINIT', 'FVALUE', 'FSECOND', 'FTERM')


class FixtureSelection:
    """Replace only the BCPL fixture, keeping proven /CN settings."""

    def __init__(self, baseline: Path):
        self.baseline = baseline

    def __truediv__(self, name: str) -> Path:
        if name == 'source.bcpl':
            return SOURCE
        return self.baseline / name


def run() -> int:
    spec = importlib.util.spec_from_file_location('co2_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError('CO.2 native baseline driver is unavailable')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    if tuple(driver.EXPECTED) != BASE_EXPECTED:
        raise RuntimeError('CO.2 baseline native output oracle changed')
    driver.FIXTURE = FixtureSelection(driver.FIXTURE)
    driver.WORK = EVIDENCE
    driver.EXPECTED = EXPECTED
    # The baseline parser does not assume a specific worker marker set.
    names = '|'.join(re.escape(x) for x in (*EXPECTED, *FAILURES))
    driver.OUTPUT_RE = re.compile(r'^CO2BCPL\s+(' + names + r')\s*$')
    return driver.execute()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit isolated compiler and native MVS jobs')
    args = parser.parse_args()
    if not args.run:
        parser.error('MVS submission requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
