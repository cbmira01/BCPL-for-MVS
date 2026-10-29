#!/usr/bin/env python3
"""Prepare Q2STOP: BCPL STOP(8), independent assembler FB80 verification.

Uses the proven Q.1 BCX/IFOX/IEWL native application template.
All writable MVS datasets are temporary; this script never submits JES.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / 'workarea/bcplqsam-q2/stop-flush'
GO = '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'


def load_query():
    path = HERE / 'prepare-q1-query.py'
    spec = importlib.util.spec_from_file_location('q2stop_query', path)
    if spec is None or spec.loader is None:
        raise ValueError('Q.1 native template missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_one(rows, before, after):
    if rows.count(before) != 1:
        raise ValueError('expected exactly one JCL card: ' + before)
    rows[rows.index(before)] = after


def make_deck(generated, jobcard, obj_dsn):
    if not jobcard or not re.match(r'^//Q2STOP\s+JOB\b', jobcard[0]):
        raise ValueError('authenticated Q2STOP JOB card required')
    q = load_query()
    rows = q.make_deck(
        generated,
        ["//Q1QUERY JOB (BCPL),'Q2 STOP TEMPLATE',CLASS=A"],
        obj_dsn,
    ).splitlines()
    rows[:1] = jobcard
    replace_one(
        rows,
        '//* Q.1 QUERY-ONLY: NO QSAM OPEN/CLOSE; NO PDS WRITES',
        '//* Q.2 STOP(8) FINALIZER FB80 FLUSH; NO PERMANENT WRITES')
    replace_one(rows, ' NAME Q1QUERY(R)', ' NAME Q2STOP(R)')
    replace_one(rows, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
                '//SYSLMOD  DD  DSN=&&Q2SLD(Q2STOP),')

    t0 = q.time_helper()
    helper = t0.trailer_helper()
    vf = t0.read_cards(helper, HERE / 'q2-stop-verify.asm')
    insertion = next(
        i for i, r in enumerate(rows)
        if r.startswith('//ASMN     EXEC '))
    rows[insertion:insertion] = helper.asm_step('ASMV', 'Q2SVOBJ', vf)

    go = rows.index(GO)
    rows[go:go] = [
        '//LKVR     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=(0,NE)',
        '//SYSLIN   DD  DSN=&&Q2SVOBJ,DISP=(OLD,PASS)',
        '//         DD  *',
        ' ENTRY Q2STVF',
        ' NAME Q2STVF(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&Q2VLD(Q2STVF),',
        '//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),',
        '//             DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
    ]
    replace_one(rows, GO,
                '//BGO      EXEC PGM=*.LKED.SYSLMOD,REGION=256K,')
    replace_one(rows, '//             TIME=(,2),COND=(0,NE,LKED)',
                '//             TIME=(,2),COND=(0,NE)')

    bgo = next(
        i for i, row in enumerate(rows)
        if row.startswith('//BGO      EXEC '))
    sysp = next(
        i for i in range(bgo + 1, len(rows))
        if rows[i].startswith('//SYSPRINT DD '))
    fb = '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)'
    rows[sysp:sysp] = [
        '//QPOST    DD  DSN=&&Q2POST,DISP=(NEW,PASS),',
        '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',
        fb,
    ]
    if rows[-1] != '//':
        raise ValueError('template terminator absent')
    rows.pop()
    rows += [
        '//VGO      EXEC PGM=*.LKVR.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(8,NE,BGO)',
        '//QPOST    DD  DSN=&&Q2POST,DISP=(OLD,DELETE),',
        fb,
        '//QOUT     DD  SYSOUT=*,',
        fb,
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]

    for n, card in enumerate(rows, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'invalid IFOX/JCL card {n}: {card!r}')
        if ('CATLG' in card or 'DISP=MOD' in card or
            (card.startswith('//') and 'BOOT_DEVOBJ' in card)):
            raise ValueError('permanent dataset operation prohibited')

    steps = ('ASMA', 'ASMV', 'ASMN', 'ASMR', 'ASMQ', 'ASMG',
             'LKED', 'LKVR', 'BGO', 'VGO')
    for step in steps:
        if sum(row.startswith(f'//{step:<8} EXEC ')
               for row in rows) != 1:
            raise ValueError('missing/duplicate step: ' + step)
    if rows.count('//SYSIN    DD  *') != 6 or rows.count('/*') != 8:
        raise ValueError('unexpected assembler/linker in-stream boundaries')
    if rows.count(' ENTRY R0APP') != 1 or rows.count(' ENTRY Q2STVF') != 1:
        raise ValueError('wrong entry symbols')
    if rows.count('         BCXREQ BCPLQSAM') != 1:
        raise ValueError('QSM package not selected exactly once')
    if rows.count('//             TIME=(,2),COND=(8,NE,BGO)') != 1:
        raise ValueError('verifier requires actual STOP RC=8')
    if rows.count('//QPOST    DD  DSN=&&Q2POST,DISP=(NEW,PASS),') != 1:
        raise ValueError('BCPL temporary FB80 output absent')
    if rows.count('//QPOST    DD  DSN=&&Q2POST,DISP=(OLD,DELETE),') != 1:
        raise ValueError('independent assembler input absent')
    return '\n'.join(rows) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generated', type=Path, required=True)
    args = ap.parse_args()
    path = args.generated.resolve()
    if (ROOT / 'workarea').resolve() not in path.parents or not path.is_file():
        raise ValueError('compiled BCPL assembler must exist in workarea')
    q = load_query()
    core = q.time_helper().trailer_helper().load_core()
    cfg = core.load_config()
    obj = cfg['datasets']['BOOT_OBJ']
    if not (obj.get('content_type') == 'object' and
            obj.get('dsorg') == 'PO' and obj.get('recfm') == 'FB' and
            int(obj.get('lrecl', 0)) == 80):
        raise ValueError('BOOT_OBJ manifest mismatch')
    deck = make_deck(
        path.read_bytes().decode('latin-1'),
        core.authenticated_job_card(
            cfg, 'Q2STOP', 'Q2 STOP FLUSH', redact_password=False),
        core.full_dsn(cfg, obj),
    )
    RUN.mkdir(parents=True, exist_ok=True)
    target = RUN / 'q2stop.jcl'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(deck)
    print(f'PREPARED Q2STOP: {len(deck.splitlines())} cards')
    print('SHA-256: ' + hashlib.sha256(deck.encode('ascii')).hexdigest())
    print('NO JES SUBMISSION; no permanent MVS datasets or object writes')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit('Q2STOP JCL preparation failed: ' + str(exc))
