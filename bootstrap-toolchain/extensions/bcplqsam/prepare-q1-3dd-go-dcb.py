#!/usr/bin/env python3
"""Prepare one explicit-GO-DCB Q13DD diagnostic from an existing deck.

This opt-in, temporary-only Q.0 comparison adds DCB attributes to the
GO reader DDs. It does not change the normal Q.1 JCL generator,
baseline BCPLQSAM, or whether ordinary API callers need JCL DCBs.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'workarea/bcplqsam-q1'
GO_EXEC = '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'
WGO_EXEC = '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,'
GEOMETRY = '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)'


def explicit_go_dcb(deck: str) -> str:
    """Only the three GO input DD statements may be changed."""
    if not deck.endswith('\n'):
        raise ValueError('truncated Q13DD JCL')
    cards = deck.splitlines()
    if not cards or not cards[0].startswith('//Q13DD '):
        raise ValueError('expected authenticated Q13DD deck')
    for card in (GO_EXEC, WGO_EXEC, '         BCXREQ BCPLQSAM'):
        if cards.count(card) != 1:
            raise ValueError(f'expected one card: {card}')
    if cards.count('//SYSIN    DD  *') != 6 or cards.count('/*') != 8:
        raise ValueError('unexpected source/IEWL boundaries')
    if sum('Q1O:GEOM R3=' in row for row in cards) != 1:
        raise ValueError('require preserved OPEN geometry diagnostic')
    if any('CATLG' in row or 'DISP=MOD' in row or
           '//EXTLIB' in row or
           (row.startswith('//') and 'BOOT_DEVOBJ' in row)
           for row in cards):
        raise ValueError('permanent MVS object/dataset operation')
    wgo, go = cards.index(WGO_EXEC), cards.index(GO_EXEC)
    if wgo >= go:
        raise ValueError('WGO must precede GO')
    for i in range(3):
        name = f'Q{i:02d}'
        writer = f'//{name}      DD  DSN=&&Q1H{i:02d},DISP=(NEW,PASS),'
        reader = f'//{name}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE)'
        if cards.count(writer) != 1 or cards.count(reader) != 1:
            raise ValueError(f'{name}: expected one writer and reader DD')
        if not wgo < cards.index(writer) < go:
            raise ValueError(f'{name}: writer outside WGO')
        if not go < cards.index(reader):
            raise ValueError(f'{name}: reader outside GO')
        at = cards.index(reader)
        cards[at:at+1] = [reader + ',', GEOMETRY]
    if cards.count(GEOMETRY) != 6:
        raise ValueError('expected three writer and three reader DCBs')
    if any(not row.isascii() or len(row) > 71 or '\t' in row
           for row in cards):
        raise ValueError('invalid JCL/IFOX card')
    return '\n'.join(cards) + '\n'


def workarea_path(path: Path) -> Path:
    resolved = path.resolve()
    if WORK.resolve() not in resolved.parents:
        raise ValueError('path must be within ignored Q.1 workarea')
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='no file access, no authenticated JCL, no JES')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.check:
        if args.input or args.output:
            parser.error('--check cannot use file arguments')
        def load(name: str, filename: str):
            spec = importlib.util.spec_from_file_location(
                name, Path(__file__).resolve().parent / filename)
            if spec is None or spec.loader is None:
                raise ValueError(f'cannot load diagnostic helper: {filename}')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        three = load('q1_check_three', 'prepare-q1-3dd.py')
        diag = load('q1_check_open', 'prepare-q1-3dd-open-diag.py')
        helper = three.query_helper().time_helper().trailer_helper()
        deck = three.make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'Q0 DCB CHECK',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')
        updated = explicit_go_dcb(diag.instrument_deck(deck))
        if updated.count(GEOMETRY) != 6:
            raise ValueError('synthetic Q.0 comparison missing DCBs')
        print(f'PASS: explicit GO F1024 DCBs on 3 temporary DDs '
              f'({len(updated.splitlines())} cards); no JES')
        return
    if args.input is None or args.output is None:
        parser.error('both --input and --output required')
    src, dst = workarea_path(args.input), workarea_path(args.output)
    if src == dst:
        raise ValueError('input and output must differ')
    result = explicit_go_dcb(src.read_text(encoding='ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as f:
            fd = -1
            f.write(result)
    finally:
        if fd >= 0:
            os.close(fd)
    print(f'PREPARED ONLY: {dst}')
    print('GO Q00/Q01/Q02 have explicit F1024 DCB; no JES submission')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'Q.1 Q.0-DCB comparison FAILED: {exc}')
