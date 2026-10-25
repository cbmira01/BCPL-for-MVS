#!/usr/bin/env python3
"""Prepare the Q.1 native BCPL QUERY-only BCX integration job.

Based on the accepted BCPLTIME T.0 temporary IFOX/IEWL/GO build pattern.
The caller performs QUERY and unsupported-opcode checks; it NEVER OPENs
a QSAM DD. --check uses synthetic CG370, no credentials or JES.
--generated writes local 0600 JCL under workarea/; never submits itself.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea' / 'bcplqsam-q1'
BCX = ROOT / 'bootstrap-toolchain/extensions/bcx'
JOB = 'Q1QUERY'


def time_helper():
    path = ROOT / 'tools/checks/prepare-bcpltime-t0.py'
    spec = importlib.util.spec_from_file_location('q1_t0_jcl', path)
    if spec is None or spec.loader is None:
        raise ValueError('accepted T.0 job generator unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r'^//Q1QUERY\s+JOB\b', jobcard[0]):
        raise ValueError('expected authenticated Q1QUERY JOB card')
    if not re.fullmatch(
        r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+',
        obj_dsn,
    ):
        raise ValueError('invalid manifest BOOT_OBJ dataset name')
    t0 = time_helper()
    helper = t0.trailer_helper()
    app = helper.application_source(generated)
    bcplmain = t0.read_cards(
        helper, ROOT / 'bootstrap-toolchain/asm/bcplmain.asm')
    bcplrgs = t0.read_cards(
        helper, ROOT / 'bootstrap-toolchain/asm/bcplrgs.asm')
    qsam = t0.read_cards(helper, HERE / 'bcplqsam.asm')
    macros: list[str] = []
    for path in (BCX / 'BCXPRE.asm', HERE / 'q1-catalog.asm',
                 HERE / 'q1-selection.asm', BCX / 'BCXPOST.asm'):
        macros.extend(t0.read_cards(helper, path))

    cards = [
        *jobcard,
        '//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES',
        *helper.asm_step('ASMA', 'Q1APOBJ', app),
        *helper.asm_step('ASMN', 'Q1NMOBJ', bcplmain),
        *helper.asm_step('ASMR', 'Q1RGOBJ', bcplrgs),
        *helper.asm_step('ASMQ', 'Q1QSOBJ', qsam),
        '//ASMG     EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,DECK,LIST,XREF(FULL),ESD,RLD',",
        '//             COND=(0,NE)',
        '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSPUNCH DD  DSN=&&Q1REGD,UNIT=SYSDA,',
        '//             SPACE=(80,(100,20)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSGO    DD  DUMMY',
        '//SYSIN    DD  *', *macros, '/*',
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=(0,NE)',
        f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
        '//QSMOBJ   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)',
        '//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)',
        '//         DD  DSN=&&Q1NMOBJ,DISP=(OLD,PASS)',
        '//         DD  DSN=&&Q1RGOBJ,DISP=(OLD,PASS)',
        '//         DD  DSN=&&Q1REGD,DISP=(OLD,PASS)',
        '//         DD  *',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' INCLUDE OBJ(BLIB)',
        ' ENTRY R0APP',
        ' NAME Q1QUERY(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
        '//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),',
        '//             DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(0,NE,LKED)',
        '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
        '//             BLKSIZE=132)',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for no, row in enumerate(cards, 1):
        if len(row) > 71 or not row.isascii() or '\t' in row:
            raise ValueError(f'invalid JCL/IFOX card {no}: {row!r}')
    if cards.count('/*') != 6 or cards.count(' ENTRY R0APP') != 1:
        raise ValueError('unexpected in-stream source/IEWL boundaries')
    if any('DISP=MOD' in row or 'CATLG' in row or '//EXTLIB' in row or
           'DSN=&&Q1QSOBJ,DISP=(NEW,' in row for row in cards):
        raise ValueError('unapproved MVS dataset or output')
    if cards.count(' INCLUDE OBJ(BCPLIO)') != 1:
        raise ValueError('accepted BCPLIO import missing')
    # IFOX assembler operations occupy columns 10 onward; preserve the
    # actual fixed-column card instead of matching an unindented token.
    if cards.count('         BCXREQ BCPLQSAM') != 1:
        raise ValueError('expected one temporary BCPLQSAM requirement')
    if not any(row.startswith('//QSMOBJ   DD  DSN=&&Q1QSOBJ')
               for row in cards):
        raise ValueError('no temporary QSMOBJ object import')
    if any(row.startswith('//Q00 ') or row.startswith('//Q01 ')
           for row in cards):
        raise ValueError('QUERY-only test cannot allocate QSAM DDs')
    return '\n'.join(cards) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='synthetic cards only, no files or MVS')
    parser.add_argument('--generated', type=Path,
                        help='real CG370 output of test-q1-query.bcpl')
    args = parser.parse_args()
    t0 = time_helper()
    helper = t0.trailer_helper()
    if args.check:
        if args.generated is not None:
            parser.error('--check cannot use --generated')
        deck = make_deck(helper.sample_generated(),
                         ["//Q1QUERY JOB (BCPL),'Q1 CHECK',CLASS=A"],
                         'HERC02.BCPL.BOOT.OBJ')
        print(f'PASS: Q.1 QUERY synthetic temporary JCL '
              f'({len(deck.splitlines())} cards); no MVS execution')
        return
    if args.generated is None:
        parser.error('--generated required for authenticated JCL')
    generated = args.generated.resolve()
    if (ROOT / 'workarea').resolve() not in generated.parents:
        raise ValueError('CG370 source must be under workarea/')
    t0 = time_helper()
    core = t0.trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or
        spec.get('dsorg') != 'PO' or
        spec.get('recfm') != 'FB' or
        int(spec.get('lrecl', 0)) != 80):
        raise ValueError('manifest BOOT_OBJ is not an FB80 object PDS')
    obj_dsn = core.full_dsn(config, spec)
    jobcard = core.authenticated_job_card(
        config, JOB, 'Q1 QUERY', redact_password=False)
    raw = generated.read_bytes().decode('latin-1')
    deck = make_deck(raw, jobcard, obj_dsn)
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / 'q1query.jcl'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
            fd = -1
            stream.write(deck)
    finally:
        if fd != -1:
            os.close(fd)
    print(f'PREPARED ONLY: {target}')
    print('Query-only native GO at REGION=256K; no QSAM DD allocations.')
    print('Operator must submit explicitly; no permanent PDS writes.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'Q.1 native QUERY preparation FAILED: {exc}')
