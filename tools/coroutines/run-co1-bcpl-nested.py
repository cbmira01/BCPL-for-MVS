#!/usr/bin/env python3
"""Run the CO.1 nested-frame native BCPL probe using the proven driver.

Reuses the candidate's IFOX/IEWL/GO job, accepted positive-record oracle,
and tracked switch source; selects only a different BCPL source and an
independent evidence directory. No installed MVS datasets are changed.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co1-bcpl-switch.py')
SOURCE = (ROOT / 'packaging/milestones/coroutines/candidates'
          / 'co1-bcpl-nested/source.bcpl')


class FixtureSelection:
    """Map only the BCPL source; retain the proven assembler/parm fixture."""

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
    # Reject accidental changes to the baseline's output oracle.
    if tuple(driver.EXPECTED) != ('A1', 'R1', 'A2', 'R2', 'PASS'):
        raise RuntimeError('CO.1 baseline native output oracle changed')
    driver.FIXTURE = FixtureSelection(driver.FIXTURE)
    driver.WORK = ROOT / 'workarea/co1-bcpl-nested'
    return driver.execute()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit one nested BCPL compiler/native MVS run')
    options = parser.parse_args()
    if not options.run:
        parser.error('MVS execution requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
