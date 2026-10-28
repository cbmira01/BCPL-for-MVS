#!/usr/bin/env python3
"""Prepare ONE test-only Q1FDIAG deck from preserved Q16FIN JCL. No JES.

Only the authenticated JOB name, temporary load-member name, and exact
ASMQ source are changed; all other steps and 16 F1024 DDs are retained.
The IFOX WTO list/execute expansion MUST be verified on target MVS.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q1'
BASELINE = HERE / 'bcplqsam.asm'

# Three calls: QSMFIN entry (after reset), loop completion, just before exit.
ENTRY = "         XC    QFCOUNT(4),QFCOUNT\n"
ENTRY_NEW = ENTRY + ("         SR    0,0\n"
                     "         L     15,=A(QFPROBE)\n"
                     "         BALR  14,15\n")
LOOP = "QFRET    L     0,QFCOUNT\n"
LOOP_NEW = ("QFRET    LA    0,1\n"
            "         L     15,=A(QFPROBE)\n"
            "         BALR  14,15\n"
            "         L     0,QFCOUNT\n")
EXIT = "QFEXIT   L     15,QFSTAT\n"
EXIT_NEW = ("QFEXIT   LA    0,2\n"
            "         L     15,=A(QFPROBE)\n"
            "         BALR  14,15\n"
            "         L     15,QFSTAT\n")

# A wholly distinct CSECT avoids perturbing QSMFIN's USING range.
# For the single-line WTO list, the 4-byte header precedes message text.
# This structural assumption is NOT established until an IFOX/IEWL gate.
PROBE = '''***********************************************************************
* Q.1 TEST-ONLY FINISH DIAGNOSTIC. NO API, REGISTRY OR CORE CHANGE.
* PHASE IN R0: 0 ENTRY, 1 LOOP COMPLETION, 2 RETURN.
* WTO LIST FORM MESSAGE BYTES ASSUMED AT LIST+4; VERIFY ON MVS.
***********************************************************************
QFPROBE  CSECT
         USING QFPROBE,12
         STM   14,12,12(13)
         LR    12,15
         LA    2,QFPASAV
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
         ST    0,QFPHASE
         XC    QFPREAS(4),QFPREAS
         LTR   1,1
         BZ    QFPNORE
         MVC   QFPREAS(4),0(1)
QFPNORE  L     6,=A(QFCOUNT)
         MVC   QFPCOUNT(4),0(6)
         L     6,=A(QSLIVE)
         MVC   QFPLIVE(4),0(6)
         L     6,=A(QSDCBS)
         MVC   QFPDCBS(4),0(6)
         L     6,=A(QSSTAGES)
         MVC   QFPSTAG(4),0(6)
         L     6,=A(QFSTAT)
         MVC   QFPSTAT(4),0(6)
         L     0,QFPHASE
         LTR   0,0
         BZ    QFPENT
         C     0,=F'1'
         BE    QFPLP
         C     0,=F'2'
         BE    QFPEX
         B     QFPDONE
* ENTRY: REASON, LIVE, DCB, STAGES (ALL FULLWORDS AS HEX).
QFPENT   LA    4,QFEL+10
         LA    6,QFPREAS
         BAL   14,QFPHEX
         LA    4,QFEL+19
         LA    6,QFPLIVE
         BAL   14,QFPHEX
         LA    4,QFEL+28
         LA    6,QFPDCBS
         BAL   14,QFPHEX
         LA    4,QFEL+37
         LA    6,QFPSTAG
         BAL   14,QFPHEX
         WTO   MF=(E,QFEL)
         B     QFPDONE
* LOOP: SUCCESSES, LIVE, DCB, STAGES, STATUS.
QFPLP    LA    4,QFLL+10
         LA    6,QFPCOUNT
         BAL   14,QFPHEX
         LA    4,QFLL+19
         LA    6,QFPLIVE
         BAL   14,QFPHEX
         LA    4,QFLL+28
         LA    6,QFPDCBS
         BAL   14,QFPHEX
         LA    4,QFLL+37
         LA    6,QFPSTAG
         BAL   14,QFPHEX
         LA    4,QFLL+46
         LA    6,QFPSTAT
         BAL   14,QFPHEX
         WTO   MF=(E,QFLL)
         B     QFPDONE
* EXIT: SAME FIVE VALUES IN THE FINAL RETURN PATH.
QFPEX    LA    4,QFXL+10
         LA    6,QFPCOUNT
         BAL   14,QFPHEX
         LA    4,QFXL+19
         LA    6,QFPLIVE
         BAL   14,QFPHEX
         LA    4,QFXL+28
         LA    6,QFPDCBS
         BAL   14,QFPHEX
         LA    4,QFXL+37
         LA    6,QFPSTAG
         BAL   14,QFPHEX
         LA    4,QFXL+46
         LA    6,QFPSTAT
         BAL   14,QFPHEX
         WTO   MF=(E,QFXL)
QFPDONE  L     13,4(13)
         LM    14,12,12(13)
         BR    14
* BYTE-TO-EBCDIC HEX; FOUR SOURCE BYTES -> EIGHT DIGITS.
* R6 SOURCE, R4 DEST, R14 RETURN. PRIVATE NONREENTRANT SCRATCH.
QFPHEX   ST    14,QFPHRET
         LA    9,4
QFPHXL   SR    0,0
         IC    0,0(6)
         LR    7,0
         SRL   7,4
         LA    2,QFPDIG
         SR    3,3
         IC    3,0(7,2)
         STC   3,0(4)
         LR    7,0
         N     7,=X'0000000F'
         SR    3,3
         IC    3,0(7,2)
         STC   3,1(4)
         LA    6,1(6)
         LA    4,2(4)
         BCT   9,QFPHXL
         L     14,QFPHRET
         BR    14
         LTORG
QFPASAV  DS    18F
QFPHRET DC    F'0'
QFPHASE DC    F'0'
QFPREAS DC    F'0'
QFPCOUNT DC   F'0'
QFPLIVE DC    F'0'
QFPDCBS DC    F'0'
QFPSTAG DC    F'0'
QFPSTAT DC    F'0'
QFPDIG  DC    C'0123456789ABCDEF'
QFEL     WTO  'Q1F:E:00000000:00000000:00000000:00000000',MF=L
QFLL     WTO 'Q1F:L:00000000:00000000:00000000:00000000:00000000',MF=L
QFXL     WTO 'Q1F:X:00000000:00000000:00000000:00000000:00000000',MF=L
'''


def load_campaign():
    p = HERE / 'prepare-q1-campaign.py'
    s = importlib.util.spec_from_file_location('q1_finalizer_campaign', p)
    if s is None or s.loader is None:
        raise ValueError('campaign helper unavailable')
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def replace_once(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise ValueError('missing/duplicate native anchor: ' + before[:30])
    return source.replace(before, after, 1)


def validate_cards(source: str) -> None:
    if not source.endswith('\n'):
        raise ValueError('missing final newline')
    for n, row in enumerate(source.splitlines(), 1):
        if not row.isascii() or '\t' in row or len(row) > 71:
            raise ValueError(f'bad IFOX/JCL card {n}: {row!r}')


def instrument_asm(source: str) -> str:
    validate_cards(source)
    if 'QFPROBE  CSECT' in source or 'Q1F:E:' in source:
        raise ValueError('source already instrumented')
    for old, new in ((ENTRY, ENTRY_NEW), (LOOP, LOOP_NEW),
                     (EXIT, EXIT_NEW)):
        source = replace_once(source, old, new)
    source = replace_once(source, 'QSMCTRL  CSECT\n',
                          PROBE + 'QSMCTRL  CSECT\n')
    validate_cards(source)
    if source.count('         L     15,=A(QFPROBE)') != 3:
        raise ValueError('expected exactly three probe calls')
    for marker in ('QFEL     WTO', 'QFLL     WTO', 'QFXL     WTO'):
        if source.count(marker) != 1:
            raise ValueError('missing probe WTO list: '+marker)
    return source


def instrument_deck(deck: str, baseline: str) -> str:
    m = load_campaign()
    original = deck.splitlines()
    m.verify(original, 'Q16FIN', 'finish')
    left,right=m.source_span(original,'ASMQ')
    if original[left:right] != baseline.splitlines():
        raise ValueError('ASMQ does not match exact source-controlled baseline')
    original[left:right] = instrument_asm(baseline).splitlines()
    original[0] = replace_once(original[0], '//Q16FIN ', '//Q1FDIAG ')
    m.replace_one(original, ' NAME Q16FIN(R)', ' NAME Q1FDIAG(R)')
    m.replace_one(original, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
                  '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1FDIAG),')
    result=m.verify(original, 'Q1FDIAG', 'finish')
    if len(original) != len(deck.splitlines()) + len(instrument_asm(baseline).splitlines()) - len(baseline.splitlines()):
        raise ValueError('unexpected JCL changes')
    return result


def under_workarea(path: Path) -> Path:
    p=path.resolve()
    if WORK.resolve() not in p.parents:
        raise ValueError('JCL must stay inside ignored Q.1 workarea')
    return p


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--input', type=Path)
    p.add_argument('--output', type=Path)
    a=p.parse_args()
    if a.check:
        if a.input or a.output:
            p.error('--check is pathless')
        m=load_campaign()
        sample=m.module('prepare-q1-query.py').time_helper().trailer_helper().sample_generated()
        deck=m.make_deck('finish',sample,
                         ["//Q16FIN JOB (BCPL),'Q1 CHECK',CLASS=A"],
                         'HERC02.BCPL.BOOT.OBJ')
        made=instrument_deck(deck,BASELINE.read_text(encoding='ascii'))
        print('PASS: Q1FDIAG synthetic source/deck: '+str(len(made.splitlines()))+' cards; no JES')
        return
    if a.input is None or a.output is None:
        p.error('--input and --output required')
    src=under_workarea(a.input)
    dst=under_workarea(a.output)
    if src==dst or dst.exists():
        raise ValueError('output must be new and distinct')
    content=instrument_deck(src.read_text(encoding='ascii'),
                            BASELINE.read_text(encoding='ascii'))
    WORK.mkdir(parents=True,exist_ok=True)
    fd=os.open(dst,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='ascii',newline='\n') as out:
        out.write(content)
    print('PREPARED ONLY:',dst,'cards',len(content.splitlines()))
    print('No JES submission, no installed dataset modification')

if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,UnicodeError,AssertionError) as exc:
        raise SystemExit('Q1FDIAG preparation FAILED: '+str(exc))
