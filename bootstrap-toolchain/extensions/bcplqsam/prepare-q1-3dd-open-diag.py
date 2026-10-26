#!/usr/bin/env python3
"""Isolate Q.1 OPEN errors in temporary ASMQ; never alter baseline code."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q1'
BASELINE = HERE / 'bcplqsam.asm'

PATCHES = (
    ("QSMCORE  CSECT\n         STM   14,12,12(13)", "QSMCORE  CSECT\n         EXTRN IODIAG\n         STM   14,12,12(13)"),
    ("         RDJFCB ((2))\n         C     15,=F'4'\n         BE    QCNOTDD\n         LTR   15,15\n         BNZ   QCNOPEN", "         RDJFCB ((2))\n         C     15,=F'4'\n         BE    QCNOTDD\n         LTR   15,15\n         BNZ   QDNRJ"),
    ("         L     0,48(2)\n         LTR   0,0\n         BZ    QCNOPEN", "         L     0,48(2)\n         LTR   0,0\n         BZ    QDNPT"),
    ("QCHDONE  SR    15,15\n         B     QCRET\nQCNOTDD L   7,=F'-5'", "QCHDONE  SR    15,15\n         B     QCRET\nQDNRJ    L     1,=A(QDMRJ)\n         LA    2,11\n         L     15,=A(IODIAG)\n         BALR  14,15\n         LA    10,4095(12)\n         LA    10,1(10)\n         B     QCNOPEN\nQDNPT    L     1,=A(QDMDP)\n         LA    2,11\n         L     15,=A(IODIAG)\n         BALR  14,15\n         LA    10,4095(12)\n         LA    10,1(10)\n         B     QCNOPEN\nQCNOTDD L   7,=F'-5'"),
    ("QCPREBAD LR    7,15\n         B     QCROLL", "QCPREBAD LR    7,15\n         L     1,=A(QDMPR)\n         LA    2,12\n         L     15,=A(IODIAG)\n         BALR  14,15\n         LA    10,4095(12)\n         LA    10,1(10)\n         B     QCROLL"),
    ("QCPOSTER LR    7,15\n         LTR   7,7\n         BM    QCCLEAN\n         L     7,=F'-6'\n         B     QCCLEAN", "QCPOSTER LR    7,15\n         LTR   7,7\n         BM    QDPST\n         L     7,=F'-6'\nQDPST    L     1,=A(QDMPF)\n         LA    2,13\n         L     15,=A(IODIAG)\n         BALR  14,15\n         LA    10,4095(12)\n         LA    10,1(10)\n         B     QCCLEAN"),
    ("QCERRPRI DC   F'0'\n***********************************************************************", "QCERRPRI DC   F'0'\nQDMRJ    DC    C'Q1O:RDJFCB '\nQDMPR    DC    C'Q1O:PREFORM '\nQDMDP    DC    C'Q1O:DCBPTR '\nQDMPF    DC    C'Q1O:POSTFORM '\n***********************************************************************"),
)

def instrument_asm(source: str) -> str:
    for old, new in PATCHES:
        if source.count(old) != 1:
            raise ValueError('missing or repeated assembler anchor: ' + old[:40])
        source = source.replace(old, new, 1)
    if not source.endswith('\n') or any(
            len(c) > 71 or not c.isascii() or '\t' in c
            for c in source.splitlines()):
        raise ValueError('invalid IFOX card')
    if source.count('L     15,=A(IODIAG)') != 4:
        raise ValueError('expected four diagnostic calls')
    return source


def instrument_deck(deck: str) -> str:
    if not deck.endswith('\n'):
        raise ValueError('truncated deck')
    rows = deck.splitlines()
    if not rows or not rows[0].startswith('//Q13DD '):
        raise ValueError('not a Q13DD job')
    for card, count in (
        ('//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,', 1),
        ('         BCXREQ BCPLQSAM', 1),
        ('//SYSIN    DD  *', 6),
        ('/*', 8),
    ):
        if rows.count(card) != count:
            raise ValueError('unexpected JCL content: ' + card)
    if any('CATLG' in x or 'DISP=MOD' in x or '//EXTLIB' in x
           or ('BOOT_DEVOBJ' in x and x.startswith('//'))
           for x in rows):
        raise ValueError('forbidden installed library operation')
    before = [i for i, x in enumerate(rows)
              if x.startswith('//ASMQ ') and ' EXEC ' in x]
    after = [i for i, x in enumerate(rows)
             if x.startswith('//ASMG ') and ' EXEC ' in x]
    if len(before) != 1 or len(after) != 1 or before[0] >= after[0]:
        raise ValueError('unexpected ASMQ / ASMG sequence')
    start = [i for i in range(before[0], after[0])
             if rows[i] == '//SYSIN    DD  *']
    end = [i for i in range(before[0], after[0]) if rows[i] == '/*']
    if len(start) != 1 or len(end) != 1:
        raise ValueError('ambiguous ASMQ SYSIN boundaries')
    left, right = start[0] + 1, end[0]
    original = BASELINE.read_text(encoding='ascii')
    if rows[left:right] != original.splitlines():
        raise ValueError('original ASMQ source does not match Git baseline')
    rows[left:right] = instrument_asm(original).splitlines()
    if any(len(x) > 71 or not x.isascii() or '\t' in x for x in rows):
        raise ValueError('invalid diagnostic JCL card')
    return '\n'.join(rows) + '\n'


def in_workarea(path: Path) -> Path:
    resolved = path.resolve()
    if WORK.resolve() not in resolved.parents:
        raise ValueError('path must be under ignored workarea')
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.check:
        if args.input or args.output:
            parser.error('--check does not accept files')
        spec = importlib.util.spec_from_file_location(
            'q1_three_gate', HERE / 'prepare-q1-3dd.py')
        if spec is None or spec.loader is None:
            raise ValueError('original generator unavailable')
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        helper = gate.query_helper().time_helper().trailer_helper()
        deck = gate.make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'OPEN DIAG',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')
        updated = instrument_deck(deck)
        if 'Q1O:RDJFCB ' not in updated or updated == deck:
            raise ValueError('ASMQ substitution failed')
        print('PASS: temporary ASMQ-only OPEN-stage deck; GO REGION=256K')
        return
    if args.input is None or args.output is None:
        parser.error('--input and --output required')
    src, dst = in_workarea(args.input), in_workarea(args.output)
    if src == dst:
        raise ValueError('output must differ from input')
    updated = instrument_deck(src.read_text(encoding='ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    fd = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
            fd = -1
            stream.write(updated)
    finally:
        if fd >= 0:
            os.close(fd)
    print(f'PREPARED ONLY: {dst}')
    print('Baseline assembler untouched; GO REGION=256K')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'Q13DD diagnostic preparation FAILED: {exc}')
