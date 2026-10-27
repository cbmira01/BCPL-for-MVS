#!/usr/bin/env python3
"""Build test-only Q.1 OBTAIN/CAMLST SEARCH feasibility from identity JCL.

This adds a read-only VTOC inquiry for each eligible allocated, single-volume
DASD DD (Q00/Q01/Q02) using its runtime RDJFCB name/volume. It emits raw
DSCB bytes (not trusted field interpretations), always returns -6 before
QSAM OPEN, and never SCRATCH/RENAME/GET/PUT. No JES submission.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
WORK=ROOT/'workarea/bcplqsam-q1'

INSERT_AFTER='''         LA    1,QIDMTB
         LA    2,24
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QIDBACK
'''
REPLACE_WITH=INSERT_AFTER+'''* TEST ONLY: OBTAIN ALLOCATED SINGLE-VOLUME DASD DSCB.
         BAL   14,QOBREAD
'''
READ_PROBE='''* READ-ONLY VTOC INQUIRY; R12 IS QID BASE.
* DO NOT ACCEPT THESE DSCB OFFSETS AS PRODUCTION DEFINITIONS.
QOBREAD  ST    14,QOBRET
         L     6,QIDPTR
         CLI   117(6),X'01'
         BNE   QOBSKIP
         CLC   118(6),=CL6' '
         BE    QOBSKIP
* SOURCE NAME/VOLUME COME FROM THIS DD'S RUNTIME RDJFCB JFCB.
         MVC   QOBNAME(44),0(6)
         MVC   QOBVOL(6),118(6)
         XC    QOBWORK(140),QOBWORK
         OBTAIN QOBLIST
         ST    15,QOBRC
         L     0,QIDIDX
         A     0,=F'240'
         STC   0,QOBRCB+6
         STC   0,QOBD0B+6
         STC   0,QOBD1B+6
         LA    6,QOBRC
         LA    5,QOBRCB+11
         LA    9,4
         BAL   14,QIDHEX
         LA    1,QOBRCB
         LA    2,19
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QOBRET0
         CLC   QOBRC(4),=F'0'
         BNE   QOBRET0
* FORMAT-1 DSCB IS REPORTED RAW AS TWO 48-BYTE DATA RECORDS.
* THE FIRST 96 WORK BYTES ARE DSCB DATA; DO NOT CLAIM GEOMETRY.
         LA    6,QOBWORK
         LA    5,QOBD0B+12
         LA    9,48
         BAL   14,QIDHEX
         LA    1,QOBD0B
         LA    2,108
         BAL   14,QIDOUT
         CLC   QIDERR(4),=F'0'
         BNE   QOBRET0
         LA    6,QOBWORK+48
         LA    5,QOBD1B+12
         LA    9,48
         BAL   14,QIDHEX
         LA    1,QOBD1B
         LA    2,108
         BAL   14,QIDOUT
         B     QOBRET0
QOBSKIP  L     0,QIDIDX
         A     0,=F'240'
         STC   0,QOBSKB+6
         LA    1,QOBSKB
         LA    2,12
         BAL   14,QIDOUT
QOBRET0  L     14,QOBRET
         BR    14
'''
DATA_PROBE='''QOBRET   DC    F'0'
QOBRC    DC    F'0'
QOBNAME  DC    CL44' '
QOBVOL   DC    CL6' '
         DS    0D
QOBWORK  DS    CL140
QOBRCB   DC    C'Q1O:Q00:RC=',8C'0'
QOBD0B   DC    C'Q1O:Q00:DS0=',96C'0'
QOBD1B   DC    C'Q1O:Q00:DS1=',96C'0'
QOBSKB   DC    C'Q1O:Q00:SKIP'
QOBLIST  CAMLST SEARCH,QOBNAME,QOBVOL,QOBWORK
'''


def identity_module():
    p=HERE/'prepare-q1-3dd-identity.py'
    spec=importlib.util.spec_from_file_location('q1_obtain_identity',p)
    if not spec or not spec.loader:raise ValueError('missing identity helper')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def extension(source: str) -> str:
    if source.count(INSERT_AFTER)!=1:raise ValueError('identity MET anchor changed')
    if source.count('QIDBACK  L     14,QIDRET')!=1:
        raise ValueError('identity return anchor changed')
    if source.count("QIDRCB   DC    C'Q1I:Q00:RC='")!=1:
        raise ValueError('identity private data anchor changed')
    # This variant adds two 108-byte RAW records. The already tested
    # identity-only QIDOUT enforces <=72; enlarge *only its private bound*.
    # IOREPL replaces/flushes each complete record, and 108 < IOBUF 132.
    if source.count("         C     2,=F'72'")!=1:
        raise ValueError('identity output-width guard changed')
    result=source.replace("         C     2,=F'72'",
                          "         C     2,=F'108'",1)
    result=result.replace('MAX LENGTH 72 < BCPLIO PRIMARY 132.',
                          'MAX LENGTH 108 < BCPLIO PRIMARY 132.',1)
    result=result.replace(INSERT_AFTER,REPLACE_WITH,1)
    result=result.replace('QIDBACK  L     14,QIDRET',
                          READ_PROBE+'QIDBACK  L     14,QIDRET',1)
    result=result.replace("QIDRCB   DC    C'Q1I:Q00:RC='",
                          DATA_PROBE+"QIDRCB   DC    C'Q1I:Q00:RC='",1)
    if any(not row.isascii() or len(row)>71 or '\t' in row
           for row in result.splitlines()):
        raise ValueError('invalid IFOX card in OBTAIN probe')
    for forbidden in ('SCRATCH ', 'RENAME ', '         GET   ',
                      '         PUT   ', '         OPEN  '):
        if forbidden in READ_PROBE:
            raise ValueError('unsafe macro in inquiry')
    if result.count('         OBTAIN QOBLIST')!=1:
        raise ValueError('expected one OBTAIN macro in diagnostic source')
    return result


def instrument_deck(deck: str, baseline: str):
    ident=identity_module()
    rows,left,right=ident.validate_deck(deck)
    if rows[left:right]!=baseline.splitlines():
        raise ValueError('ASMQ must match current unmodified source')
    original=ident.PROBE_CSECT
    derived=extension(original)
    src=ident.instrument_asm(baseline)
    if src.count(original)!=1:
        raise ValueError('identity source anchor changed')
    src=src.replace(original,derived,1)
    rows[left:right]=src.splitlines()
    output='\n'.join(rows)+'\n'
    if not ident.cards_are_valid(output):
        raise ValueError('invalid OBTAIN JCL/IFOX cards')
    if output.count('         OBTAIN QOBLIST')!=1:
        raise ValueError('OBTAIN disappeared from JCL')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--input',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    ident=identity_module()
    if a.check:
        if a.input or a.output:p.error('--check takes no paths')
        helper=ident.check()
        e=extension(ident.PROBE_CSECT)
        print('PASS: test-only OBTAIN syntax/cards: '+str(len(e.splitlines())))
        return
    if not a.input or not a.output:p.error('--input and --output required')
    src,dst=ident.under_workarea(a.input),ident.under_workarea(a.output)
    if src==dst or dst.exists():raise ValueError('output must be new and distinct')
    output=instrument_deck(src.read_text(encoding='ascii'),
                           ident.BASELINE.read_text(encoding='ascii'))
    WORK.mkdir(parents=True,exist_ok=True)
    fd=os.open(dst,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='ascii',newline='\n') as f:f.write(output)
    print('PREPARED ONLY:',dst)
    print('Read-only OBTAIN; no QSAM OPEN/GET/PUT, no JES submission')

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,UnicodeError) as e:
        raise SystemExit('Q.1 OBTAIN preparation FAILED: '+str(e))
