#!/usr/bin/env python3
"""Prepare a test-only Q.1 RDJFCB allocation-identity diagnostic deck.

Replaces only ASMQ's temporary source in an existing omitted-DCB Q13DD
JCL deck. On the first OPEN request the diagnostic issues RDJFCB for
Q00/Q01/Q02, emits bounded raw-hex identity/geometry records through
BCPLIO IOREPL + IOWRCH, then returns QS_ERR_OPEN=-6 without QSAM OPEN.
No OBTAIN, no JES submission, no changes to bcplqsam.asm.
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
GO = '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'
WGO = '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,'
SOURCE_BEGIN = '//SYSIN    DD  *'
SOURCE_END = '/*'

CORE_OLD = '''         ST    8,QCREQ
         ST    9,QCRES
         C     7,=F'1'
         BE    QCOPEN'''
CORE_NEW = '''         ST    8,QCREQ
         ST    9,QCRES
* TEST ONLY: INSPECT ALL THREE DDs; NEVER EXECUTE QSAM OPEN.
         C     7,=F'1'
         BNE   QIDSKIP
         L     15,=A(QIDRUN)
         BALR  14,15
         L     15,=F'-6'
         B     QCRET
QIDSKIP  C     7,=F'1'
         BE    QCOPEN'''

# A distinct CSECT keeps QSMCORE's existing base-register/addressability
# interval unchanged. The candidate offset constants are intentionally
# *raw-byte* observations, not accepted MVS 3.8J field definitions.
PROBE_CSECT = '''***********************************************************************
* TEST ONLY: PRE-OPEN ALLOCATION IDENTITY; NO OBTAIN AND NO QSAM OPEN.
* R15 -> ENTRY FROM QSMCORE, R13 -> CALLER STANDARD SAVE AREA.
* EARLIER-MANUAL JFCB OFFSET CANDIDATES: DSNM 0, NVOL 117,
* VOLS 118. RECORD RAW BYTES; DO NOT INFER ALLOCATION IDENTITY.
***********************************************************************
QIDPROB  CSECT
         EXTRN IOREPL,IOWRCH,IOSTAT
         USING QIDPROB,12
QIDRUN   STM   14,12,12(13)
         LR    12,15
         LA    2,QIDSAVE
         ST    13,4(2)
         ST    2,8(13)
         LR    13,2
* R5 AT ENTRY IS QSMDISP'S BCPL WORKSPACE; HEX ENCODER CLOBBERS IT.
         ST    5,QIDWORK
         XC    QIDERR(4),QIDERR
* THREE INDEPENDENT QSAM DCBs AND THEIR 176-BYTE JFCB AREAS.
         L     2,=A(QI00)
         L     7,=A(QJ00)
         LA    6,0
         BAL   14,QIDREAD
         CLC   QIDERR(4),=F'0'
         BNE   QIDEXIT
         L     2,=A(QI01)
         L     7,=A(QJ01)
         LA    6,1
         BAL   14,QIDREAD
         CLC   QIDERR(4),=F'0'
         BNE   QIDEXIT
         L     2,=A(QI02)
         L     7,=A(QJ02)
         LA    6,2
         BAL   14,QIDREAD
QIDEXIT  L     13,4(13)
         LM    14,12,12(13)
         BR    14
* INPUTS: R2 DCB, R7 JFCB, R6 DD NUMBER 0..2.
QIDREAD  ST    14,QIDRET
         ST    7,QIDPTR
         ST    6,QIDIDX
         XC    0(176,7),0(7)
         RDJFCB ((2))
         ST    15,QIDRC
* LABEL CHAR IS EBCDIC '0' + INDEX; THE REST IS STATIC.
         L     0,QIDIDX
         A     0,=F'240'
         STC   0,QIDRCB+6
         STC   0,QIDN0B+6
         STC   0,QIDN1B+6
         STC   0,QIDVLB+6
         STC   0,QIDMTB+6
* ALWAYS PRINT RDJFCB R15, EVEN IF NO JFCB IS AVAILABLE.
         LA    6,QIDRC
         LA    5,QIDRCB+11
         LA    9,4
         BAL   14,QIDHEX
         LA    1,QIDRCB
         LA    2,19
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
         CLC   QIDRC(4),=F'0'
         BNE   QIDBACK
* NAME=44 BYTES, TWO 22-BYTE HEX RECORDS.
         L     6,QIDPTR
         LA    5,QIDN0B+12
         LA    9,22
         BAL   14,QIDHEX
         LA    1,QIDN0B
         LA    2,56
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
         L     6,QIDPTR
         LA    6,22(6)
         LA    5,QIDN1B+12
         LA    9,22
         BAL   14,QIDHEX
         LA    1,QIDN1B
         LA    2,56
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
* VOLS=30 BYTES. NVOL+RECFM+BLKSIZE+LRECL=6 BYTES.
         L     6,QIDPTR
         LA    6,118(6)
         LA    5,QIDVLB+12
         LA    9,30
         BAL   14,QIDHEX
         LA    1,QIDVLB
         LA    2,72
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
         L     6,QIDPTR
         MVC   QIDMET(1),117(6)
         MVC   QIDMET+1(1),100(6)
         MVC   QIDMET+2(2),102(6)
         MVC   QIDMET+4(2),104(6)
         LA    6,QIDMET
         LA    5,QIDMTB+12
         LA    9,6
         BAL   14,QIDHEX
         LA    1,QIDMTB
         LA    2,24
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
QIDBACK  L     14,QIDRET
         BR    14
* INPUTS: R6 SOURCE, R5 DESTINATION, R9 BYTE COUNT.
* DIGITS ARE EBCDIC (THE SAME ENCODING AS BCPLIO TEXT).
QIDHEX   ST    14,QIDHRET
QIDHXLP  SR    0,0
         IC    0,0(6)
         LR    4,0
         SRL   4,4
         LA    1,QIDDIG
         SR    3,3
         IC    3,0(4,1)
         STC   3,0(5)
         LR    4,0
         N     4,=X'0000000F'
         SR    3,3
         IC    3,0(4,1)
         STC   3,1(5)
         LA    5,2(5)
         LA    6,1(6)
         BCT   9,QIDHXLP
         L     14,QIDHRET
         BR    14
* ONE RECORD PER FIELD; MAX LENGTH 72 < BCPLIO PRIMARY 132.
* IOREPL REPLACES THE PENDING PRIMARY RECORD (NO APPEND).
* IOWRCH WITH R7=10 FLUSHES IT; R6 IS ITS RETURN REGISTER.
* IOSTAT CHECKS ANY PERSISTENT OUTPUT ERROR. FAIL CLOSED.
QIDOUT   STM   0,15,QIDKEEP
         LTR   2,2
         BM    QIDBAD
         C     2,=F'72'
         BH    QIDBAD
         L     15,=A(IOREPL)
         BALR  14,15
         LTR   15,15
         BNZ   QIDBAD
         L     5,QIDWORK
         LA    7,10
         L     15,=A(IOWRCH)
         BALR  6,15
         L     15,=A(IOSTAT)
         BALR  14,15
         LTR   15,15
         BZ    QIDOK
QIDBAD   LA    0,1
         ST    0,QIDERR
         WTO   'Q1I OUTPUT ERROR'
QIDOK    LM    0,15,QIDKEEP
         BR    14
         LTORG
QIDSAVE  DS    18F
QIDRET   DC    F'0'
QIDHRET  DC    F'0'
QIDPTR   DC    F'0'
QIDIDX   DC    F'0'
QIDRC    DC    F'0'
QIDERR   DC    F'0'
QIDWORK  DC    F'0'
QIDMET   DC    CL6' '
         DS    0F
QIDKEEP  DS    16F
QIDDIG   DC    C'0123456789ABCDEF'
QIDRCB   DC    C'Q1I:Q00:RC=',8C'0'
QIDN0B   DC    C'Q1I:Q00:NM0=',44C'0'
QIDN1B   DC    C'Q1I:Q00:NM1=',44C'0'
QIDVLB   DC    C'Q1I:Q00:VOL=',60C'0'
QIDMTB   DC    C'Q1I:Q00:MET=',12C'0'
'''


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError('missing or duplicate source anchor: ' + old[:55])
    return source.replace(old, new, 1)


def cards_are_valid(source: str) -> bool:
    return (source.endswith('\n') and all(
        row.isascii() and '\t' not in row and len(row) <= 71
        for row in source.splitlines()))


def instrument_asm(source: str) -> str:
    if not cards_are_valid(source):
        raise ValueError('invalid baseline assembler card')
    if 'QIDPROB  CSECT' in source or 'Q1I:Q00:' in source:
        raise ValueError('source already contains identity probe')
    source = replace_once(source, CORE_OLD, CORE_NEW)
    source = replace_once(
        source,
        'QSMCTRL  CSECT\n',
        PROBE_CSECT + 'QSMCTRL  CSECT\n')
    if not cards_are_valid(source):
        raise ValueError('invalid IFOX card in probe')
    for token, count in (
        ('         RDJFCB ((2))', 2),
        ('         OPEN  ((2),(OUTPUT))', 1),
        ('QCOPENIN OPEN  ((2),(INPUT))', 1),
        ('         BAL   14,QIDREAD', 3),
        ('         BAL   14,QIDOUT', 5),
        ('         BALR  6,15', 1),
        ('         EXTRN IOREPL,IOWRCH,IOSTAT', 1),
        ("         BNE   QIDBACK", 6),
        ("         BNE   QIDEXIT", 2),
    ):
        if source.count(token) != count:
            raise ValueError(f'unexpected count for {token!r}')
    return source


def validate_deck(deck: str) -> tuple[list[str], int, int]:
    if not cards_are_valid(deck):
        raise ValueError('truncated/invalid JCL card')
    rows = deck.splitlines()
    if not rows[0].startswith('//Q13DD '):
        raise ValueError('expected Q13DD job')
    for marker, count in ((GO, 1), (WGO, 1),
                          (SOURCE_BEGIN, 6), (SOURCE_END, 8),
                          ('         BCXREQ BCPLQSAM', 1)):
        if rows.count(marker) != count:
            raise ValueError(f'wrong JCL structure for {marker!r}')
    if rows.index(WGO) >= rows.index(GO):
        raise ValueError('WGO must precede GO')
    for num in range(3):
        writer = (f'//Q{num:02d}      DD  DSN=&&Q1H{num:02d},'
                  'DISP=(NEW,PASS),')
        reader = (f'//Q{num:02d}      DD  DSN=&&Q1H{num:02d},'
                  'DISP=(OLD,DELETE)')
        if (rows.count(writer) != 1 or rows.count(reader) != 1 or
                not rows.index(WGO) < rows.index(writer) < rows.index(GO) or
                not rows.index(GO) < rows.index(reader)):
            raise ValueError('DD configuration not canonical: Q' + str(num))
        at = rows.index(reader)
        if (at+1 < len(rows) and
                rows[at+1].startswith('//             DCB=')):
            raise ValueError('GO reader DCB must be omitted')
    if any(('CATLG' in row or 'DISP=MOD' in row or
            '//EXTLIB' in row or
            (row.startswith('//') and 'BOOT_DEVOBJ' in row))
           for row in rows):
        raise ValueError('permanent dataset/JCL operation forbidden')
    asm_step = [i for i, r in enumerate(rows)
                if r.startswith('//ASMQ ') and ' EXEC ' in r]
    next_step = [i for i, r in enumerate(rows)
                 if r.startswith('//ASMG ') and ' EXEC ' in r]
    if len(asm_step) != 1 or len(next_step) != 1 or asm_step[0] >= next_step[0]:
        raise ValueError('ambiguous ASMQ/ASMG steps')
    start = [i for i in range(asm_step[0], next_step[0])
             if rows[i] == SOURCE_BEGIN]
    end = [i for i in range(asm_step[0], next_step[0])
           if rows[i] == SOURCE_END]
    if len(start) != 1 or len(end) != 1 or start[0] >= end[0]:
        raise ValueError('ambiguous ASMQ source stream')
    return rows, start[0]+1, end[0]


def instrument_deck(deck: str, baseline: str) -> str:
    rows, left, right = validate_deck(deck)
    if rows[left:right] != baseline.splitlines():
        raise ValueError('ASMQ must exactly match source-controlled bcplqsam')
    rows[left:right] = instrument_asm(baseline).splitlines()
    result = '\n'.join(rows) + '\n'
    if not cards_are_valid(result):
        raise ValueError('invalid instrumented JCL/IFOX cards')
    return result


def under_workarea(path: Path) -> Path:
    resolved = path.resolve()
    if WORK.resolve() not in resolved.parents:
        raise ValueError('both paths must be under ignored Q.1 workarea')
    return resolved


def check() -> None:
    spec = importlib.util.spec_from_file_location('q1_identity_base',
                                                  HERE / 'prepare-q1-3dd.py')
    if spec is None or spec.loader is None:
        raise ValueError('Q.1 generator unavailable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    helper = mod.query_helper().time_helper().trailer_helper()
    deck = mod.make_deck(
        helper.sample_generated(),
        ["//Q13DD JOB (BCPL),'ID ONLY',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    result = instrument_deck(deck, BASELINE.read_text(encoding='ascii'))
    assert result.count('Q1I:Q00:RC=') == 1
    assert result.count('QIDPROB  CSECT') == 1
    assert GO in result and WGO in result
    assert result.count('         BCXREQ BCPLQSAM') == 1
    print(f'PASS: identity-only omitted-DCB Q13DD synthetic JCL '
          f'({len(result.splitlines())} cards), no JES')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--input', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    if args.check:
        if args.input or args.output:
            p.error('--check does not accept --input or --output')
        check()
        return
    if args.input is None or args.output is None:
        p.error('--input and --output are required')
    src = under_workarea(args.input)
    dst = under_workarea(args.output)
    if src == dst:
        raise ValueError('input and output must differ')
    result = instrument_deck(src.read_text(encoding='ascii'),
                             BASELINE.read_text(encoding='ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
            fd = -1
            out.write(result)
    finally:
        if fd >= 0:
            os.close(fd)
    print('PREPARED ONLY:', dst)
    print('RDJFCB Q00/Q01/Q02; forced -6 before QSAM OPEN; no JES')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError, AssertionError) as e:
        raise SystemExit('Q.1 identity diagnostic FAILED: ' + str(e))
