#!/usr/bin/env python3
"""CO.3 isolated DELETECO/revoke/FREEVEC/registry reuse native candidate.

Reuse the accepted independent-BCPL compiler/IFOX/IEWL/JES coordinator,
without modifying its original first-lifecycle and parent-chain fixtures.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_RUNNER = ROOT/'tools/coroutines/run-co3-first-lifecycle.py'
FIXTURE = ROOT/'packaging/milestones/coroutines/candidates/co3-delete-reuse'
EVIDENCE = ROOT/'workarea/co3-delete-reuse'
EXTENSION = FIXTURE/'co3drop.inc'
EXPECTED = ('MADE', 'FULL', 'A1', 'RA', 'B1', 'RB', 'DELA',
            'C1', 'RC', 'B2', 'RB2', 'DELB', 'C2', 'RC2',
            'DELC', 'D1', 'RD', 'D2', 'RD2', 'DELD', 'PASS')
LIBRARY_EXPORTS = ((289, 'C3INIT'), (290, 'C3CREATE'),
                   (291, 'C3DELETE'), (292, 'C3CALL'),
                   (293, 'C3WAIT'), (294, 'C3RESUME'))


class CandidateError(ValueError):
    pass


def merge_bridge(baseline: str, extension: str) -> str:
    """Inject CO3DROP only into the temporary IFOX candidate assembly.

    Fail if the qualified CO.2 registry layout or interface changed.
    This never writes an assembler file into the owner's checkout.
    """
    entry = '         ENTRY CO2INIT,CHANGECO\n'
    anchor = "         DS    0F\nROOTPTR  DC    F'0'"
    for token in (entry, anchor):
        if baseline.count(token) != 1:
            raise CandidateError('BCPLCO source contract changed')
    if 'CO3DROP' in baseline or 'CO3DROP' not in extension:
        raise CandidateError('unexpected CO3DROP source')
    if 'ROOTPTR' not in baseline or 'REGW1' not in baseline or 'REGW2' not in baseline:
        raise CandidateError('BCPLCO registry labels missing')
    lines = extension.rstrip('\n').splitlines()
    if (not lines or 'CO3DROP  STM   4,10,0(15)' not in lines or
            '         DROP  10' not in lines):
        raise CandidateError('incomplete CO3DROP extension')
    for number, line in enumerate(lines, 1):
        if len(line)>71 or not line.isascii() or '\t' in line:
            raise CandidateError(f'bad IFOX extension card {number}')
    merged = baseline.replace(entry, entry+'         ENTRY CO3DROP\n')
    merged = merged.replace(anchor, extension.rstrip('\n')+'\n'+anchor)
    if merged.count('CO3DROP  STM') != 1 or merged.count('         END   BCPLCO') != 1:
        raise CandidateError('ambiguous candidate BCPLCO assembly')
    return merged


def bind_application_export(rows: list[str], driver) -> list[str]:
    """G!300 only: install CO3DROP IFOX entry through app trailer.

    G!291 is independently compiled DELETECO BCPL; machine G!300 is
    a private global installation. Neither slot is a public allocation.
    """
    rows = list(rows)
    start, last, maximum, pairs = driver.trailer(rows)
    if 1200 in {number for number, _ in pairs}:
        raise CandidateError('generated app already exports G!300')
    # The qualified CO.3 runner generates the five-function EXTRN card
    # literally even when its EXPORTS tuple includes DELETECO.
    baseline = '         EXTRN C3INIT,C3CREATE,C3CALL,C3WAIT,C3RESUME'
    expanded = '         EXTRN C3INIT,C3CREATE,C3DELETE,C3CALL,C3WAIT,C3RESUME'
    if rows.count(baseline) != 1 or expanded in rows:
        raise CandidateError('BCPL library imports changed')
    at = rows.index(baseline)
    rows[at] = expanded
    rows.insert(at+1, '         EXTRN CO3DROP')
    start, last, maximum, pairs = driver.trailer(rows)
    rows[start] = f"         DC F'{max(maximum, 1200)}'"
    rows[last:last] = ["         DC F'1200'", '         DC A(CO3DROP)']
    return driver.co2.checked_cards('\n'.join(rows), 'CO3APP')


def bind_library_export(rows: list[str], driver) -> list[str]:
    """Publish the added independent BCPL DELETECO procedure to IEWL.

    The qualified CO.3 runner also hard-codes the older five-entry IFOX
    ENTRY card, independent of its dynamic EXPORTS procedure trailer.
    """
    rows = list(rows)
    baseline = '         ENTRY C3INIT,C3CREATE,C3CALL,C3WAIT,C3RESUME'
    expanded = '         ENTRY C3INIT,C3CREATE,C3DELETE,C3CALL,C3WAIT,C3RESUME'
    if rows.count(baseline) != 1 or expanded in rows:
        raise CandidateError('BCPL library ENTRY contract changed')
    import re
    if sum(bool(re.fullmatch(r'C3DELETE\s+EQU\s+L\d{1,5}', row))
           for row in rows) != 1:
        raise CandidateError('DELETECO label alias missing or ambiguous')
    rows[rows.index(baseline)] = expanded
    return driver.co2.checked_cards('\n'.join(rows), 'CO3LIB')


def configure(driver) -> None:
    if tuple(driver.EXPORTS) != ((289, 'C3INIT'), (290, 'C3CREATE'),
                                (292, 'C3CALL'), (293, 'C3WAIT'),
                                (294, 'C3RESUME')):
        raise CandidateError('qualified CO.3 library export baseline changed')
    old_application = driver.generated_application
    old_library = driver.generated_library
    old_deck = driver.build_deck
    extension = EXTENSION.read_text('ascii')

    driver.EXPORTS = LIBRARY_EXPORTS
    driver.FIXTURE = FIXTURE
    driver.WORK = EVIDENCE
    driver.EXPECTED = EXPECTED

    def application(source: str) -> list[str]:
        return bind_application_export(old_application(source), driver)

    def library(source: str) -> list[str]:
        return bind_library_export(old_library(source), driver)

    def deck(app: str, library: str, main: str, bridge: str,
             jobcard: list[str], obj_dsn: str) -> str:
        return old_deck(app, library, main,
                        merge_bridge(bridge, extension), jobcard, obj_dsn)

    driver.generated_application = application
    driver.generated_library = library
    driver.build_deck = deck


def run() -> int:
    spec = importlib.util.spec_from_file_location('co3_baseline', BASE_RUNNER)
    if spec is None or spec.loader is None:
        raise CandidateError('CO.3 independent-library driver unavailable')
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    configure(driver)
    return driver.execute('first')


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true',
                        help='submit isolated Cambridge/IFOX/IEWL/GO jobs')
    args=parser.parse_args()
    if not args.run:
        parser.error('native MVS execution requires explicit --run')
    return run()


if __name__ == '__main__':
    raise SystemExit(main())
