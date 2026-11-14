#!/usr/bin/env python3
"""Run candidate-only CO.1 worker revocation / release under MVS 3.8J.

Reuse the verified Cambridge/IFOX/IEWL/GO baseline and its strict
five-record oracle. Add one test-local assembler global G!296.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = Path(__file__).with_name('run-co1-bcpl-switch.py')
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co1-bcpl-revocation')
EVIDENCE = ROOT / 'workarea/co1-bcpl-revocation'


class FixtureSelection:
    """Select only the isolated BCPL and assembler source."""

    def __init__(self, baseline: Path):
        self.baseline = baseline

    def __truediv__(self, name: str) -> Path:
        if name in ('source.bcpl', 'co1change.asm'):
            return FIXTURE / name
        return self.baseline / name


def add_drop_export(rows: list[str], error_type: type[Exception],
                    checked_cards) -> list[str]:
    """Bind fixture-only G!296 to CO1DROP after baseline G!298/299 binding.

    Reject unexpected CG370 structure rather than guessing addresses or
    changing the authoritative compiled-application adapter.
    """
    rows = list(rows)
    csect = 'CO1APP   CSECT'
    import_line = '         EXTRN CO1DROP'
    if rows.count(csect) != 1 or import_line in rows:
        raise error_type('unexpected candidate CSECT or CO1DROP import')
    if rows.count('         EXTRN CO1INIT,CO1SW') != 1:
        raise error_type('baseline export/import contract changed')
    start = rows.index(csect)
    rows.insert(start + 1, import_line)
    marker = 'L998 EQU *'
    markers = [i for i, line in enumerate(rows)
               if line.split() == ['L998', 'EQU', '*']]
    if len(markers) != 1:
        raise error_type('compiler global trailer marker is ambiguous')
    end = markers[0]
    a = "         DC F'1192'"
    b = '         DC A(CO1INIT)'
    c = "         DC F'1196'"
    d = '         DC A(CO1SW)'
    pair = [i for i in range(1, end - 2)
            if rows[i - 1:i + 3] == [a, b, c, d]]
    if len(pair) != 1 or "         DC F'1184'" in rows[:end]:
        raise error_type('CO1INIT/CO1SW trailer changed or G!296 taken')
    pos = pair[0] - 1
    rows[pos:pos] = ["         DC F'1184'", '         DC A(CO1DROP)']
    return checked_cards('\n'.join(rows), 'CO1APP')


def run() -> int:
    spec = importlib.util.spec_from_file_location('co1_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError('CO.1 baseline runner unavailable')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    if tuple(driver.EXPECTED) != ('A1', 'R1', 'A2', 'R2', 'PASS'):
        raise RuntimeError('CO.1 native output oracle changed')
    original = driver.compiled_application

    def compiled(generated: str) -> list[str]:
        return add_drop_export(original(generated), driver.CandidateError,
                               driver.checked_cards)

    driver.compiled_application = compiled
    driver.FIXTURE = FixtureSelection(driver.FIXTURE)
    driver.WORK = EVIDENCE
    return driver.execute()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit isolated BCPL revocation compiler/MVS jobs')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run is required for MVS execution')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
