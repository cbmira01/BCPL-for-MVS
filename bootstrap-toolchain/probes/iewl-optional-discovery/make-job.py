#!/usr/bin/env python3
"""R.4 isolated IEWL INCLUDE / WXTRN study; never installs objects.

Reads unchanged R.2 extension sources. Builds one combined object for
BCPLDEMO and one for test-only R2TESTB, then four independent links.
IEWL receives the optional objects *only* through explicit INCLUDE DD
statements, not by concatenating them to primary SYSLIN.

--check uses a synthetic job card and never writes files or credentials.
The generated test deck is an MVS *candidate*, not verified execution.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/runtime-extensions-r4'
JOB = 'R4WXLINK'
PROFILES = ('zero', 'a', 'b', 'both')
SELECTION = {'zero': (), 'a': ('a',),
             'b': ('b',), 'both': ('a', 'b')}
PKGS = {
    'a': ('bcpldemo', 'DMODISP'),
    'b': ('r2testb', 'R2BDISP'),
}
OBJ = {'a': 'R4AOBJ', 'b': 'R4BOBJ'}
OBSERVER = {'zero': 'R4W0', 'a': 'R4WA',
            'b': 'R4WB', 'both': 'R4WX'}
LINK = {'zero': 'L0', 'a': 'LA', 'b': 'LB', 'both': 'LX'}
GO = {'zero': 'G0', 'a': 'GA', 'b': 'GB', 'both': 'GX'}
LOAD = {'zero': 'R4ZERO', 'a': 'R4ONLYA',
        'b': 'R4ONLYB', 'both': 'R4BOTH'}


def checked_cards(source: str, label: str) -> list[str]:
    lines = source.rstrip('\n').splitlines()
    if not lines:
        raise ValueError(f'{label}: empty source')
    for i, line in enumerate(lines, 1):
        if not line.isascii() or len(line) > 71 or '\t' in line:
            raise ValueError(f'{label}:{i}: invalid IFOX card: {line!r}')
        if line == '/*' or line.startswith('//'):
            raise ValueError(f'{label}:{i}: JCL delimiter in assembler')
    return lines


def combined_source(pkg: str) -> str:
    """Combine exact existing descriptor and dispatcher CSECT sources.

    Remove only the no-longer-external dispatcher declaration and
    intermediate END statement. All BCEX bytes remain unchanged.
    """
    dirname, dispatcher = PKGS[pkg]
    base = ROOT / 'bootstrap-toolchain/extensions' / dirname
    desc = checked_cards((base / 'descriptor.asm').read_text('ascii'),
                         pkg + ':descriptor')
    disp = checked_cards((base / 'dispatcher.asm').read_text('ascii'),
                         pkg + ':dispatcher')
    excluded = {f'         EXTRN {dispatcher}',
                f'         END   {"DMODESC" if pkg == "a" else "R2BDSC"}'}
    if sum(line in excluded for line in desc) != 2:
        raise ValueError(f'{pkg}: descriptor layout changed; review')
    if sum('         END   ' in line for line in disp) != 1:
        raise ValueError(f'{pkg}: dispatcher must have exactly one END')
    result = '\n'.join([*(line for line in desc if line not in excluded),
                        *disp]) + '\n'
    if result.count('         END   ') != 1:
        raise ValueError(f'{pkg}: combined object has multiple ENDs')
    if pkg == 'a':
        expected = ("CL8'BCPLDEMO'", "F'203',A(DMODISP)",
                    'DMODESC  CSECT', 'DMODISP  CSECT')
    else:
        expected = ("CL8'R2TESTB'", "F'299',A(R2BDISP)",
                    'R2BDSC   CSECT', 'R2BDISP  CSECT')
    for check in expected:
        if check not in result:
            raise ValueError(f'{pkg}: missing canonical BCEX field {check}')
    checked_cards(result, f'combined:{pkg}')
    return result


def observer(profile: str) -> str:
    """Verify weak entry addresses, complete BCEX and relocation.

    Uses only MVS-volatile registers R0, R1 and R15; R14 is preserved.
    No WTO and no runtime calls. RC=0 passes, RC=12 fails.
    A missing weak reference is expected to be zero under IBM rules;
    the actual TK5 IFOX/IEWL behavior remains to be measured.
    """
    if profile not in PROFILES:
        raise ValueError(f'unknown profile {profile}')
    src = [
        '* R.4 LINK-ONLY PROBE; 0/A/B/A+B; NO BCPLREG.',
        '* WXTRN NEVER REQUESTS AN AUTOMATIC LIBRARY SEARCH.',
        'R4WEAK   CSECT',
        '         WXTRN DMOBEG,DMOEND,DMODISP',
        '         WXTRN R2BBEG,R2BEND,R2BDISP',
        '         LR    1,15',
        '         USING R4WEAK,1',
    ]
    for pkg, names in [('a', ('ABEG', 'AEND', 'ADISP')),
                       ('b', ('BBEG', 'BEND', 'BDISP'))]:
        for name in names:
            src += [f'         L     0,{name}',
                    '         LTR   0,0',
                    ('         BZ    BAD' if pkg in SELECTION[profile]
                     else '         BNZ   BAD')]
        if pkg in SELECTION[profile]:
            begin, end, dis = names
            src += [
                f'         L     0,{end}',
                f'         S     0,{begin}',
                "         C     0,=F'56'",
                '         BNE   BAD',
                f'         L     15,{begin}',
                "         CLC   0(4,15),=CL4'BCEX'",
                '         BNE   BAD',
                '         CLC   4(4,15),=F\'1\'',
                '         BNE   BAD',
                '         CLC   8(4,15),=F\'48\'',
                '         BNE   BAD',
                '         CLC   12(4,15),=F\'56\'',
                '         BNE   BAD',
                f'         L     15,{begin}',
                '         L     0,52(15)',
                f'         C     0,{dis}',
                '         BNE   BAD',
            ]
    src += [
        '         SR    15,15',
        '         BCR   15,14',
        'BAD      LA    15,12',
        '         BCR   15,14',
        'ABEG     DC    A(DMOBEG)',
        'AEND     DC    A(DMOEND)',
        'ADISP    DC    A(DMODISP)',
        'BBEG     DC    A(R2BBEG)',
        'BEND     DC    A(R2BEND)',
        'BDISP    DC    A(R2BDISP)',
        '         LTORG',
        '         END   R4WEAK',
    ]
    result = '\n'.join(src) + '\n'
    checked_cards(result, profile)
    return result


def asm_step(name: str, out: str, source: str) -> list[str]:
    return [
        f'//{name:<8} EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSPUNCH DD  DUMMY',
        f'//SYSGO    DD  DSN=&&{out},UNIT=SYSDA,',
        '//             SPACE=(80,(300,100)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSIN    DD  *',
        *checked_cards(source, name),
        '/*',
    ]


def make_deck(jobcard: list[str]) -> str:
    if not jobcard or jobcard[0].split()[:2] != [f'//{JOB}', 'JOB']:
        raise ValueError('missing authenticated R4WXLINK JOB card')
    cards = [
        *jobcard,
        '//* R.4 IEWL WXTRN STUDY: SIX ASMS, FOUR LINKS/GO.',
        '//* ALL INPUT SOURCES GIT-CONTROLLED; OUTPUTS TEMPORARY.',
        '//* NO BOOT_OBJ, BOOT_DEVOBJ, BCPLMAIN, OR BCPLRGS WRITES.',
        '//* R2TESTB/G299 REMAINS TEST-ONLY.',
    ]
    for pkg, step in [('a', 'ASPA'), ('b', 'ASPB')]:
        cards += asm_step(step, OBJ[pkg], combined_source(pkg))
    for profile, step in [('zero','AS0'), ('a','ASA'),
                          ('b','ASB'), ('both','ASAB')]:
        cards += asm_step(step, OBSERVER[profile], observer(profile))
    for profile in PROFILES:
        link, go = LINK[profile], GO[profile]
        cards += [
            f'//{link:<8} EXEC PGM=IEWL,REGION=256K,',
            "//             PARM='NCAL,LIST,XREF,MAP',",
            '//             COND=(0,NE)',
            '//PKGA     DD  DSN=&&R4AOBJ,DISP=(OLD,PASS)',
            '//PKGB     DD  DSN=&&R4BOBJ,DISP=(OLD,PASS)',
            '//SYSLIN   DD  DSN=&&' + OBSERVER[profile] + ',DISP=(OLD,PASS)',
            '//         DD  *',
            *(f' INCLUDE {"PKGA" if p == "a" else "PKGB"}'
              for p in SELECTION[profile]),
            ' ENTRY R4WEAK',
            f' NAME {LOAD[profile]}(R)',
            '/*',
            f'//SYSLMOD  DD  DSN=&&{LOAD[profile]}({LOAD[profile]}),',
            '//             UNIT=SYSDA,SPACE=(1024,(30,10,1)),',
            '//             DISP=(NEW,PASS)',
            '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(30,10))',
            '//SYSPRINT DD  SYSOUT=*',
            f'//{go:<8} EXEC PGM=*.{link}.SYSLMOD,REGION=256K,',
            f'//             TIME=(,2),COND=(0,NE,{link})',
            '//SYSUDUMP DD  SYSOUT=*',
        ]
    cards.append('//')
    for i, line in enumerate(cards, 1):
        if not line.isascii() or len(line) > 71 or '\t' in line:
            raise ValueError(f'JCL card {i}: invalid: {line!r}')
    if cards.count('/*') != 10:
        raise ValueError('expected six asm and four IEWL streams')
    if sum(line.startswith('//SYSLMOD') for line in cards) != 4:
        raise ValueError('expected four temporary load modules')
    if 'DISP=MOD' in '\n'.join(cards) or '//SYSLMOD  DD  DSN=HERC' in '\n'.join(cards):
        raise ValueError('persistent output disallowed')
    return '\n'.join(cards) + '\n'


def load_core():
    path = ROOT / 'tools/datasets/dspal-core.py'
    spec = importlib.util.spec_from_file_location('r4_dspal', path)
    if spec is None or spec.loader is None:
        raise ValueError('missing dataset helper')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='credential-free in-memory JCL check')
    args = parser.parse_args()
    if args.check:
        card = ["//R4WXLINK JOB (BCPL),'R4 WXTRN',CLASS=A,MSGCLASS=A"]
    else:
        core = load_core()
        cfg = core.load_config()
        card = core.authenticated_job_card(
            cfg, JOB, 'R4 WXTRN LINK PROBE', redact_password=False)
    deck = make_deck(card)
    if args.check:
        print(f'CHECK {JOB}: {len(deck.splitlines())} valid JCL cards; '
              '6 ASM, 4 IEWL, 4 GO, no writes')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / 'r4-iewl-wxtrn.jcl'
    out.write_text(deck, encoding='ascii', newline='\n')
    out.chmod(0o600)
    print(f'Candidate JCL: {out}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.4 candidate generation FAILED: {exc}')
