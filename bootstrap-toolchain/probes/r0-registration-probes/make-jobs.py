#!/usr/bin/env python3
"""Make test-only R.0 IFOX/IEWL descriptor/linkage validation decks."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
# Observed validator results, not the GO step condition codes.
PROFILES = {
    'valid': ('R0VALID', 0, 'R0 VALID LINK BOUNDS PASS'),
    'badlen': ('R0LENG', 4, 'R0 BADLEN REJECTED PASS'),
    'badversion': ('R0VERS', 8, 'R0 BADVERSION REJECTED PASS'),
    'duplicate': ('R0DUP', 12, 'R0 DUPLICATE EXPORT REJECTED PASS'),
    'corecollision': ('R0CORE', 16, 'R0 CORE G14 COLLISION REJECTED PASS'),
    'missingreq': ('R0REQ', 24, 'R0 MISSING REQUIREMENT REJECTED PASS'),
}


def base_harness():
    spec = importlib.util.spec_from_file_location('r0_dasd_harness', BASE)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing existing IFOX harness: {BASE}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_source(text: str, name: str) -> str:
    for n, card in enumerate(text.splitlines(), 1):
        if (not card.isascii() or len(card) > 71 or card == '/*'
                or card.startswith('//') or '\t' in card):
            raise ValueError(f'{name}:{n} invalid IFOX source card: {card!r}')
    return text.rstrip('\n')


def driver_source(profile: str) -> str:
    _, expect, marker = PROFILES[profile]
    s = (HERE / 'validator.asm').read_text(encoding='ascii')
    for a, b in (("DC    F'EXPCODE'", f"DC    F'{expect}'"),
                 ("DC    CL80'PASSMARKER'", f"DC    CL80'{marker}'")):
        if s.count(a) != 1:
            raise ValueError(f'cannot replace single R.0 source token {a}')
        s = s.replace(a, b)
    return checked_source(s, f'validator:{profile}')


def registry_source(profile: str) -> str:
    length = 40 if profile == 'badlen' else 44
    version = 2 if profile == 'badversion' else 1
    required = 'PACKB   ' if profile == 'missingreq' else 'PACKA   '
    cards = [
        '* R.0 TEST ONLY: INDEPENDENT LINKED REGISTRY DATA EXTENT.',
        'R0REG    CSECT',
        '         ENTRY R0RB,R0RE',
        '         EXTRN R0PB,R0PE',
        "R0RB     DC    CL4'BCRG'",
        f"         DC    F'{version}'",
        "         DC    F'28'",
        f"         DC    F'{length}'",
        "         DC    F'1'",
        "         DC    F'1'",
        "         DC    F'0'",
        '         DC    A(R0PB)',
        '         DC    A(R0PE)',
        f"         DC    CL8'{required}'",
        'R0RE     DS    0F',
        '         END   R0REG',
    ]
    return checked_source('\n'.join(cards), 'registry')


def package_source(profile: str) -> str:
    duplicate = profile == 'duplicate'
    count = 2 if duplicate else 1
    export = 14 if profile == 'corecollision' else 299
    cards = [
        '* R.0 TEST ONLY: RELOCATED PACKAGE DESCRIPTOR DATA.',
        'R0PKG    CSECT',
        '         ENTRY R0PB,R0PE',
        '         EXTRN R0FUNC',
        "R0PB     DC    CL4'BCEX'",
        "         DC    F'1'",
        "         DC    F'48'",
        f"         DC    F'{48 + 8 * count}'",
        "         DC    CL8'PACKA   '",
        "         DC    F'1'",
        "         DC    F'0'",
        f"         DC    F'{count}'",
        '         DC    A(R0FUNC)',
        "         DC    F'0'",
        "         DC    F'0'",
        f"         DC    F'{export}'",
        '         DC    A(R0FUNC)',
    ]
    if duplicate:
        cards += ["         DC    F'299'", '         DC    A(R0FUNC)']
    cards += ['R0PE     DS    0F', '         END   R0PKG']
    return checked_source('\n'.join(cards), 'package')


def func_source() -> str:
    return checked_source((HERE / 'function.asm').read_text('ascii'),
                          'function')


def make_deck(profile: str, jobcard: list[str]) -> str:
    if profile not in PROFILES:
        raise ValueError(f'unknown R.0 profile {profile!r}')
    job, _, marker = PROFILES[profile]
    if (not jobcard or len(jobcard[0]) < 15
            or jobcard[0][2:10].rstrip() != job
            or not jobcard[0][10:].startswith(' JOB ')):
        raise ValueError('unexpected padded R.0 JOB card')
    base = base_harness()
    cards = [
        *jobcard,
        '//* R.0 TEST ONLY: FOUR INDEPENDENT OBJECTS, LINK-RESOLVED',
        '//* NO BCPLMAIN MODIFICATION OR PERMANENT MVS DATA SETS',
        *base.asm_step('ASMD', 'R0DOBJ', driver_source(profile)),
        *base.asm_step('ASMR', 'R0ROBJ', registry_source(profile)),
        *base.asm_step('ASMP', 'R0POBJ', package_source(profile)),
        *base.asm_step('ASMF', 'R0FOBJ', func_source()),
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMD),(0,NE,ASMR),',
        '//             (0,NE,ASMP),(0,NE,ASMF))',
        '//SYSLIN   DD  DSN=&&R0DOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0ROBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0POBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0FOBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' ENTRY R0CHK',
        ' NAME R0PROBE(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0PROBE),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,1),COND=(0,NE,LKED)',
        '//QOUT     DD  SYSOUT=*,',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for n, card in enumerate(cards, 1):
        if len(card) > 71 or not card.isascii() or '\t' in card:
            raise ValueError(f'R.0 JCL card {n} invalid: {card!r}')
    deck = '\n'.join(cards) + '\n'
    if cards.count('/*') != 5 or deck.count('//SYSIN    DD  *') != 4:
        raise ValueError('expected four assembler streams and IEWL deck')
    for obj in ('R0DOBJ', 'R0ROBJ', 'R0POBJ', 'R0FOBJ'):
        if sum(f'DSN=&&{obj},DISP=(OLD,DELETE)' in c for c in cards) != 1:
            raise ValueError(f'missing link DD: {obj}')
    if marker not in deck:
        raise ValueError('missing exact executable QOUT marker')
    return deck


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=PROFILES)
    p.add_argument('--check', action='store_true',
                   help='validate without local credentials or writing JCL')
    args = p.parse_args()
    job = PROFILES[args.profile][0]
    if args.check:
        jobcard = [f"//{job:<8} JOB (BCPL),'R0 PROBE',CLASS=A,MSGCLASS=A"]
    else:
        core = base_harness().config_module()
        config = core.load_config()
        jobcard = core.authenticated_job_card(
            config, job, 'R0 PROBE', redact_password=False)
    deck = make_deck(args.profile, jobcard)
    if args.check:
        print(f'CHECK R.0 {args.profile}: {len(deck.splitlines())} cards; '
              'no credentials or JCL written')
        return
    out = ROOT / 'workarea/runtime-extensions-r0' / f'r0-{args.profile}.jcl'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(deck, encoding='ascii', newline='\n')
    out.chmod(0o600)
    print(f'R.0 test-only JCL: {out}')


if __name__ == '__main__':
    main()