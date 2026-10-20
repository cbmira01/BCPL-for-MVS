#!/usr/bin/env python3
"""Generate two isolated Q.0 pre-OPEN and empty-EOF MVS probe jobs."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
JOBS = {'geometry': 'QS0GEOM', 'empty': 'QS0EMPTY'}


def harness():
    spec = importlib.util.spec_from_file_location('q0_base_jcl', PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError('QSAM DASD job generator is unavailable')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def source(filename):
    raw = (HERE / filename).read_text(encoding='ascii')
    for n, line in enumerate(raw.splitlines(), 1):
        if len(line) > 71 or not line.isascii() or line.startswith('//') or line == '/*':
            raise ValueError(f'Invalid IFOX card {filename}:{n}: {line!r}')
    return raw.rstrip('\n')


def make_deck(profile, jobcard):
    base = harness()
    if not jobcard[0].startswith('//'+JOBS[profile]):
        raise ValueError('wrong JOB name')
    if profile == 'geometry':
        cards = [
            *jobcard,
            '//* Q.0 GEOMETRY: RDJFCB ONLY ON GOOD AND BAD DCB',
            '//* NO OPEN ON EITHER INPUT DCB; NO PDS WRITES',
            *base.asm_step('ASM', 'GEOMOBJ', source('geometry-check.asm')),
            *base.link_step('LKED','GEOMOBJ','GEOMMOD','Q0GEOMMD',
                            'Q0GEOM','ASM'),
            '//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),',
            '//             COND=((0,NE,ASM),(0,NE,LKED))',
            '//QGOOD    DD  DSN=&&Q0GOOD,DISP=(NEW,DELETE),',
            '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//QBAD     DD  DSN=&&Q0BAD,DISP=(NEW,DELETE),',
            '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)',
            '//QOUT     DD  SYSOUT=*,',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSPRINT DD  SYSOUT=*',
            '//SYSUDUMP DD  SYSOUT=*',
            '//',
        ]
    else:
        cards = [
            *jobcard,
            '//* Q.0 EMPTY FB80: OUTPUT OPEN/CLOSE; THEN EOF TWICE',
            '//* EODAD MUST BE TAKEN ONCE; SECOND READ MUST SKIP GET',
            *base.asm_step('ASMWR', 'EMWOBJ', source('empty-write.asm')),
            *base.asm_step('ASMRD', 'EMROBJ', source('empty-read.asm')),
            *base.link_step('LKWR', 'EMWOBJ', 'EMWMOD', 'Q0EMWMOD',
                            'Q0EMW', 'ASMWR'),
            *base.link_step('LKRD', 'EMROBJ', 'EMRMOD', 'Q0EMRMOD',
                            'Q0EMR', 'ASMRD'),
            '//WGO      EXEC PGM=*.LKWR.SYSLMOD,TIME=(,1),',
            '//             COND=((0,NE,ASMWR),(0,NE,LKWR))',
            '//QDISK    DD  DSN=&&Q0EMPTY,DISP=(NEW,PASS),',
            '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSPRINT DD  SYSOUT=*',
            '//SYSUDUMP DD  SYSOUT=*',
            '//RGO      EXEC PGM=*.LKRD.SYSLMOD,TIME=(,1),',
            '//             COND=((0,NE,WGO),(0,NE,LKRD))',
            '//QDISK    DD  DSN=&&Q0EMPTY,DISP=(OLD,DELETE)',
            '//QOUT     DD  SYSOUT=*,',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSPRINT DD  SYSOUT=*',
            '//SYSUDUMP DD  SYSOUT=*',
            '//',
        ]
    for n, c in enumerate(cards, 1):
        if len(c) > 71 or not c.isascii():
            raise ValueError(f'Invalid JCL card {n}: {c!r}')
    result = '\n'.join(cards)+'\n'
    if profile == 'geometry':
        assert 'OPEN  (GDCB' not in result and 'OPEN  (BADDCB' not in result
        assert result.count('RDJFCB ((2))') == 2
        assert 'GJFCB+102' in result and 'BJFCB+102' in result
        assert 'BLKSIZE=801' in result
        assert 'Q0 JFCB FB80/800 OK FB80/801 REJECT PASS' in result
    else:
        assert result.count('GET   QDCB,AREA') == 1
        assert 'EODAD=ATEND' in result
        assert 'Q0 EMPTY FB EOF2 EODAD1 PASS' in result
        assert '//QDISK    DD  DSN=&&Q0EMPTY,DISP=(OLD,DELETE)' in result
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', choices=JOBS)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        card = [f"//{JOBS[args.profile]} JOB (BCPL),'Q0 EXP',CLASS=A,MSGCLASS=A"]
    else:
        base = harness()
        core = base.config_module()
        conf = core.load_config()
        card = core.authenticated_job_card(
            conf, JOBS[args.profile], 'Q0 QSAM PROBE',
            redact_password=False)
    deck = make_deck(args.profile, card)
    if args.check:
        print(f'CHECK {args.profile.upper()}: {len(deck.splitlines())} cards; no JCL written')
        return
    path = ROOT / 'workarea/qsam-q0-followups' / f'q0-{args.profile}.jcl'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(deck, encoding='ascii', newline='\n')
    path.chmod(0o600)
    print(f'Q.0 {args.profile.upper()} JCL: {path}')


if __name__ == '__main__':
    main()
