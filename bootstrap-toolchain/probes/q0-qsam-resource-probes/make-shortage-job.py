#!/usr/bin/env python3
"""Generate a guarded Q.0 one-shot conditional GETMAIN-refusal experiment."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
JOB = 'QS0NOMEM'
SOURCE = 'conditional-shortage.asm'
REQUEST_BYTES = 1048576
GO_REGION_K = 256


def harness():
    spec = importlib.util.spec_from_file_location('q0_dasd_base', PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'MVS DASD harness unavailable: {PARENT}')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    return base


def assembler_source():
    s = (HERE / SOURCE).read_text(encoding='ascii')
    for n, card in enumerate(s.splitlines(), 1):
        if len(card) > 71 or not card.isascii() or card.startswith('//') or card == '/*':
            raise ValueError(f'invalid IFOX card {SOURCE}:{n}: {card!r}')
    mandatory = (
        'GETMAIN RC,LV=1048576',
        "C     15,=F'4'",
        'BZ    BIGOK',
        'FREEMAIN R,LV=(2),A=(1)',
        'GETMAIN RC,LV=80',
        'GETMAIN RC,LV=96',
        'ROLLBACK L',
        "Q0 REAL GETMAIN RC4 ROLLBACK 3 ALLOC 3 FREE PASS",
    )
    for needle in mandatory:
        if needle not in s:
            raise ValueError(f'missing safety/test element: {needle}')
    if s.count('GETMAIN RC,LV=1048576') != 1:
        raise ValueError('only one large allocation request is allowed')
    if 'GETMAIN RU' in s or 'GETMAIN R,LV=' in s:
        raise ValueError('unconditional allocation is prohibited')
    return s.rstrip('\n')


def make_deck(jobcard):
    if not jobcard or not jobcard[0].startswith('//'+JOB):
        raise ValueError('wrong JOB card')
    base = harness()
    cards = [
        *jobcard,
        '//* Q.0 OPT-IN, ONE 1MB GETMAIN RC AT GO REGION=256K',
        '//* NO REQUEST LOOP; UNEXPECTED SUCCESS FREE IMMEDIATELY',
        *base.asm_step('ASM', 'NOMOBJ', assembler_source()),
        *base.link_step('LKED', 'NOMOBJ', 'NOMMOD', 'Q0NOMMOD',
                        'Q0NOMEM', 'ASM'),
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,1),COND=((0,NE,ASM),(0,NE,LKED))',
        '//QOUT     DD  SYSOUT=*,',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for n, card in enumerate(cards, 1):
        if not card.isascii() or len(card)>71:
            raise ValueError(f'invalid JCL card {n}: {card!r}')
    deck='\n'.join(cards)+'\n'
    if deck.count('//SYSIN    DD  *') != 1 or cards.count('/*') != 2:
        raise ValueError('unexpected assembler/linker in-stream input')
    if deck.count('REGION=256K') < 2:
        raise ValueError('missing bounded GO region')
    if deck.count('GETMAIN RC,LV=1048576') != 1:
        raise ValueError('unexpected repeated oversized request')
    if 'DSN=HERC' in deck or 'DISP=OLD' in deck:
        raise ValueError('unexpected permanent user-dataset reference')
    return deck


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true',
                   help='safe static check; no jobcard/config or generated files')
    p.add_argument('--allow-large-getmain', action='store_true',
                   help='opt in to generating JCL with one real 1MB GETMAIN RC')
    args = p.parse_args()
    if args.check:
        jobcard=[f"//{JOB} JOB (BCPL),'Q0 COND GET',CLASS=A,MSGCLASS=A"]
    else:
        if not args.allow_large_getmain:
            p.error('generation requires --allow-large-getmain; see README')
        base=harness()
        core=base.config_module()
        cfg=core.load_config()
        jobcard=core.authenticated_job_card(
            cfg,JOB,'Q0 COND GET',redact_password=False)
    deck=make_deck(jobcard)
    if args.check:
        print(f'CHECK SHORTAGE: {len(deck.splitlines())} cards;'
              ' one 1MB GETMAIN RC; GO REGION=256K; no JCL written')
        return
    out=ROOT/'workarea/qsam-q0-resource/q0-shortage.jcl'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(deck,encoding='ascii',newline='\n')
    out.chmod(0o600)
    print(f'Q.0 guarded GETMAIN-refusal JCL: {out}')


if __name__=='__main__':
    main()
