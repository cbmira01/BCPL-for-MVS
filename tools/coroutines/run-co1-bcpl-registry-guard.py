#!/usr/bin/env python3
"""Run the isolated CO.1 known-descriptor registry native MVS probe.

Reuses the proved Cambridge/IFOX/IEWL/GO baseline driver. Only this
probe's BCPL, private switch assembly and evidence directory change.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co1-bcpl-switch.py')
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co1-bcpl-registry-guard')
EVIDENCE = ROOT / 'workarea/co1-bcpl-registry-guard'


class FixtureSelection:
    """Replace only test BCPL and assembly; keep accepted /CN fixture."""

    def __init__(self, baseline: Path):
        self.baseline = baseline

    def __truediv__(self, name: str) -> Path:
        if name in ('source.bcpl', 'co1change.asm'):
            return FIXTURE / name
        return self.baseline / name


def run() -> int:
    spec = importlib.util.spec_from_file_location('co1_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError('CO.1 baseline native runner unavailable')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    if tuple(driver.EXPECTED) != ('A1', 'R1', 'A2', 'R2', 'PASS'):
        raise RuntimeError('CO.1 baseline native output oracle changed')
    driver.FIXTURE = FixtureSelection(driver.FIXTURE)
    driver.WORK = EVIDENCE
    return driver.execute()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit only the isolated registry-guard MVS jobs')
    args = parser.parse_args()
    if not args.run:
        parser.error('MVS execution requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
