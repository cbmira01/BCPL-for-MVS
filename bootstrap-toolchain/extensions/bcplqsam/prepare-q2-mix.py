#!/usr/bin/env python3
"""Q2MIX source-only QSAM + installed read-only BCPLDEMO interoperability.

Reuse native Q2STOP's proven IFOX/IEWL/BGO/VGO structure, but replace
its BCXCAT with a test-only mixed catalog and use an independent verifier.
Never installs any object or macro and never submits JES.
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
BCX = ROOT / 'bootstrap-toolchain/extensions/bcx'
RUN = ROOT / 'workarea/bcplqsam-q2/mix-demo'
STEPS = ('ASMA', 'ASMV', 'ASMN', 'ASMR', 'ASMQ', 'ASMG',
         'LKED', 'LKVR', 'BGO', 'VGO')


def module(filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(
        filename.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('required native generator missing: ' + filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def source_span(rows: list[str], step: str) -> tuple[int, int]:
    starts = [i for i, r in enumerate(rows)
              if r.startswith(f'//{step:<8} EXEC ')]
    if len(starts) != 1:
        raise ValueError('expected one assembler step ' + step)
    start = starts[0]
    following = next((i for i in range(start+1, len(rows))
                      if rows[i] == '//SYSIN    DD  *'), -1)
    end = next((i for i in range(following+1, len(rows))
                if rows[i] == '/*'), -1)
    if following < start or end < following:
        raise ValueError('unbounded SYSIN for ' + step)
    return following+1, end


def once(rows: list[str], old: str, new: str) -> None:
    if rows.count(old) != 1:
        raise ValueError('expected one template card: ' + old)
    rows[rows.index(old)] = new


def make_deck(generated: str, jobcard: list[str],
              boot_obj: str, ext_obj: str) -> str:
    if not jobcard or not re.match(r'^//Q2MIX\s+JOB\b', jobcard[0]):
        raise ValueError('authenticated Q2MIX job card required')
    if not re.fullmatch(
        r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+',
        ext_obj):
        raise ValueError('invalid manifest EXT_OBJ dataset name')
    stop = module('prepare-q2-stop-flush.py')
    query = stop.load_query()
    t0 = query.time_helper()
    helper = t0.trailer_helper()
    rows = stop.make_deck(
        generated, ["//Q2STOP JOB (BCPL),'Q2 MIX TEMPLATE',CLASS=A"],
        boot_obj).splitlines()
    rows[:1] = jobcard
    once(rows, ' NAME Q2STOP(R)', ' NAME Q2MIX(R)')
    once(rows, '//SYSLMOD  DD  DSN=&&Q2SLD(Q2STOP),',
         '//SYSLMOD  DD  DSN=&&Q2MLD(Q2MIX),')
    once(rows,
         '//* Q.2 STOP(8) FINALIZER FB80 FLUSH; NO PERMANENT WRITES',
         '//* Q2MIX: TEMP QSAM + INSTALLED DEMO; NO PDS WRITES')

    # Replace the exact accepted ASMV verifier source, not an arbitrary
    # occurrence of a label elsewhere in an assembler listing.
    lo, hi = source_span(rows, 'ASMV')
    old = t0.read_cards(helper, HERE / 'q2-stop-verify.asm')
    new = t0.read_cards(helper, HERE / 'q2-mix-verify.asm')
    if rows[lo:hi] != old:
        raise ValueError('ASMV deviates from Q2STOP template')
    rows[lo:hi] = new
    once(rows, ' ENTRY Q2STVF', ' ENTRY Q2MVER')
    once(rows, ' NAME Q2STVF(R)', ' NAME Q2MVER(R)')
    once(rows, '//SYSLMOD  DD  DSN=&&Q2VLD(Q2STVF),',
         '//SYSLMOD  DD  DSN=&&Q2VLD(Q2MVER),')

    # IFOX BCXPRE/BCXPOST stay identical; catalog resolves QSMOBJ as
    # temporary and installed EXT_OBJ(BCPLDEMO) as a read-only PDS.
    def cards(path: Path) -> list[str]:
        return t0.read_cards(helper, path)
    orig = (cards(BCX / 'BCXPRE.asm')
            + cards(HERE / 'q1-catalog.asm')
            + cards(HERE / 'q1-selection.asm')
            + cards(BCX / 'BCXPOST.asm'))
    mixed = (cards(BCX / 'BCXPRE.asm')
             + cards(HERE / 'q2-mix-catalog.asm')
             + cards(HERE / 'q2-mix-selection.asm')
             + cards(BCX / 'BCXPOST.asm'))
    lo, hi = source_span(rows, 'ASMG')
    if rows[lo:hi] != orig:
        raise ValueError('ASMG differs from accepted Q.1 BCX source')
    rows[lo:hi] = mixed

    # The installed package is consumed only by the application's IEWL.
    # The independent verifier continues to link without any extension.
    anchor = '//QSMOBJ   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)'
    pos = rows.index(anchor) if rows.count(anchor) == 1 else -1
    if pos < 0:
        raise ValueError('temporary QSMOBJ IEWL DD missing')
    rows[pos:pos] = [f'//EXTLIB   DD  DSN={ext_obj},DISP=SHR']
    return verify(rows, ext_obj)


def verify(rows: list[str], ext_obj: str) -> str:
    if not re.match(r'^//Q2MIX\s+JOB\b', rows[0]):
        raise ValueError('Q2MIX JOB missing')
    for step in STEPS:
        if sum(row.startswith(f'//{step:<8} EXEC ') for row in rows) != 1:
            raise ValueError('step missing/duplicated: ' + step)
    if rows.count('//SYSIN    DD  *') != 6 or rows.count('/*') != 8:
        raise ValueError('IFOX/IEWL stream boundaries invalid')
    for required in (
        '         BCXREQ BCPLQSAM',
        '         BCXREQ BCPLDEMO',
        " NAME Q2MIX(R)",
        " NAME Q2MVER(R)",
        ' ENTRY R0APP',
        ' ENTRY Q2MVER',
        '//QPOST    DD  DSN=&&Q2POST,DISP=(NEW,PASS),',
        '//QPOST    DD  DSN=&&Q2POST,DISP=(OLD,DELETE),',
        '//             TIME=(,2),COND=(8,NE,BGO)',
        f'//EXTLIB   DD  DSN={ext_obj},DISP=SHR',
    ):
        if rows.count(required) != 1:
            raise ValueError('missing/duplicate Q2MIX card: ' + required)
    if sum(row == f'//EXTLIB   DD  DSN={ext_obj},DISP=SHR'
           for row in rows) != 1:
        raise ValueError('installed extension DD repeated')
    if 'Q2STVF' in '\n'.join(rows):
        raise ValueError('old verifier still referenced')
    for n, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise ValueError(f'bad IFOX/JCL card {n}: {row!r}')
        if 'CATLG' in row or 'DISP=MOD' in row:
            raise ValueError('permanent dataset write forbidden')
        if row.startswith('//') and not row.startswith('//*'):
            if 'BOOT_DEVOBJ' in row or 'DISP=SHR' in row and (
                'EXTLIB' not in row and 'SYSLIB' not in row
                and '//OBJ ' not in row):
                # The inherited accepted deck uses BOOT_OBJ and
                # SYS1.MACLIB as the other read-only library inputs.
                raise ValueError('unexpected library DD')
    return '\n'.join(rows) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--generated', type=Path)
    args = ap.parse_args()
    stop = module('prepare-q2-stop-flush.py')
    query = stop.load_query()
    helper = query.time_helper().trailer_helper()
    if args.check:
        if args.generated:
            ap.error('--check needs no generated code')
        deck = make_deck(
            helper.sample_generated(),
            ["//Q2MIX JOB (BCPL),'Q2 MIX CHECK',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ', 'HERC02.BCPL.EXT.OBJ')
        print(f'PASS: Q2MIX synthetic IFOX/IEWL/JCL ({len(deck.splitlines())} cards)')
        print('No JES submission and no permanent MVS writes')
        return
    if args.generated is None:
        ap.error('--generated is required after real MVS compilation')
    path = args.generated.resolve()
    if (ROOT / 'workarea').resolve() not in path.parents or not path.is_file():
        raise ValueError('compiled BCPL assembler must exist under workarea')
    core = helper.load_core()
    cfg = core.load_config()
    for alias, kind in (('BOOT_OBJ', 'object'), ('EXT_OBJ', 'object')):
        obj = cfg['datasets'][alias]
        if not (obj.get('content_type') == kind and
                obj.get('dsorg') == 'PO' and obj.get('recfm') == 'FB'
                and int(obj.get('lrecl', 0)) == 80):
            raise ValueError('invalid manifest library ' + alias)
    boot = core.full_dsn(cfg, cfg['datasets']['BOOT_OBJ'])
    ext = core.full_dsn(cfg, cfg['datasets']['EXT_OBJ'])
    deck = make_deck(
        path.read_bytes().decode('latin-1'),
        core.authenticated_job_card(
            cfg, 'Q2MIX', 'Q2 MIX DEMO', redact_password=False),
        boot, ext)
    RUN.mkdir(parents=True, exist_ok=True)
    target = RUN / 'q2mix.jcl'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as output:
        output.write(deck)
    print(f'PREPARED Q2MIX: {len(deck.splitlines())} cards')
    print('SHA-256: ' + hashlib.sha256(deck.encode('ascii')).hexdigest())
    print('Only EXT_OBJ(BCPLDEMO) read-only; no JES submission')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit('Q2MIX preparation failed: ' + str(exc))
