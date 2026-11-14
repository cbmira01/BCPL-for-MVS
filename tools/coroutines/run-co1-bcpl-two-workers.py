#!/usr/bin/env python3
"""CO.1 two-worker native BCPL probe with proven candidate IFOX/IEWL/GO.

Only the BCPL fixture and evidence directory change. The separately
assembled switch, private runtime link, source checks and JES oracle are
inherited from the previous CO.1 candidate runner.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co1-bcpl-switch.py')
SOURCE = (ROOT / 'packaging/milestones/coroutines/candidates'
          / 'co1-bcpl-two-workers/source.bcpl')
EVIDENCE = ROOT / 'workarea/co1-bcpl-two-workers'


class FixtureSelection:
    """Select only a new BCPL input; leave the tested assembly intact."""

    def __init__(self, baseline: Path):
        self.baseline = baseline

    def __truediv__(self, name: str) -> Path:
        if name == 'source.bcpl':
            return SOURCE
        return self.baseline / name


def run() -> int:
    spec = importlib.util.spec_from_file_location('co1_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError('CO.1 baseline runner is unavailable')
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
                        help='run two-worker BCPL compiler and native MVS GO')
    args = parser.parse_args()
    if not args.run:
        parser.error('MVS execution requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
