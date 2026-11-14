#!/usr/bin/env python3
"""CO.1 isolated generation-handle native BCPL/IFOX/IEWL/GO probe.

Uses the proven baseline and adds test-local G!295 CO1RES and G!296
CO1DROP exports without modifying the common compiler driver.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co1-bcpl-switch.py')
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co1-bcpl-generation')
EVIDENCE = ROOT / 'workarea/co1-bcpl-generation'


class FixtureSelection:
    def __init__(self, baseline: Path):
        self.baseline = baseline

    def __truediv__(self, name: str) -> Path:
        if name in ('source.bcpl', 'co1change.asm'):
            return FIXTURE / name
        return self.baseline / name


def add_exports(rows: list[str], error_type: type[Exception],
                checked_cards) -> list[str]:
    """Fail closed if the proven G!298/299 trailer changes.

    Add G!295 and G!296 before the existing ordered export pairs.
    """
    rows = list(rows)
    csect = 'CO1APP   CSECT'
    if rows.count(csect) != 1:
        raise error_type('unexpected candidate CSECT')
    if rows.count('         EXTRN CO1INIT,CO1SW') != 1:
        raise error_type('baseline CO1INIT/CO1SW import changed')
    for slot in (1180, 1184):
        if f"         DC F'{slot}'" in rows:
            raise error_type(f'test-local G!{slot//4} already exported')
    if '         EXTRN CO1RES,CO1DROP' in rows:
        raise error_type('candidate already augmented')
    indices = [i for i, line in enumerate(rows)
               if line.split() == ['L998', 'EQU', '*']]
    if len(indices) != 1:
        raise error_type('ambiguous generated global trailer')
    trailer_end = indices[0]
    a = ["         DC F'1192'", '         DC A(CO1INIT)',
         "         DC F'1196'", '         DC A(CO1SW)']
    at = [i for i in range(trailer_end - 3)
          if rows[i:i+4] == a]
    if len(at) != 1:
        raise error_type('baseline global export pairs changed')
    trailer_at = at[0]
    rows.insert(rows.index(csect) + 1,
                '         EXTRN CO1RES,CO1DROP')
    # The inserted import precedes the global trailer.
    at = trailer_at + 1
    rows[at:at] = ["         DC F'1180'", '         DC A(CO1RES)',
                   "         DC F'1184'", '         DC A(CO1DROP)']
    return checked_cards('\n'.join(rows), 'CO1APP')


def run() -> int:
    spec = importlib.util.spec_from_file_location('co1_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError('CO.1 baseline runner is unavailable')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    if tuple(driver.EXPECTED) != ('A1', 'R1', 'A2', 'R2', 'PASS'):
        raise RuntimeError('CO.1 baseline native output oracle changed')
    old = driver.compiled_application

    def compiled(source: str) -> list[str]:
        return add_exports(old(source), driver.CandidateError,
                           driver.checked_cards)

    driver.compiled_application = compiled
    driver.FIXTURE = FixtureSelection(driver.FIXTURE)
    driver.WORK = EVIDENCE
    return driver.execute()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit isolated generation-handle MVS probe')
    args = parser.parse_args()
    if not args.run:
        parser.error('native MVS execution requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
