#!/usr/bin/env python3
"""Single-JOB R.0 dependency and finalizer *test-only* MVS evidence batch."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'workarea/runtime-extensions-r0-batch'

# (EBCDIC package identity, major, minor, export global, optional dependency)
# Dependencies are (package identity, required major, minimum minor).
PACKAGES = {
    'A': ('PACKA', 1, 2, 299, None),
    'B': ('PACKB', 1, 0, 300, ('PACKA', 1, 1)),
    'C': ('PACKC', 1, 0, 301, ('PACKB', 1, 0)),
    'BM': ('PACKB', 1, 0, 300, ('PACKA', 2, 0)),
    'BN': ('PACKB', 1, 0, 300, ('PACKA', 1, 9)),
    'ACY': ('PACKA', 1, 2, 299, ('PACKB', 1, 0)),
    'A2': ('PACKA', 1, 1, 302, None),
    'DG': ('PACKZ', 1, 0, 299, None),
    'CORE': ('PACKX', 1, 0, 14, None),
    'RSV': ('PACKZ', 1, 0, 200, None),
}

# One executable GO checks *every* scenario against the explicit status.
# No scenario is counted as PASS merely because the assembly linked.
CASES = (
    ('EMPTY', (), (), 0, 'EMPTY SELECTION'),
    ('ONE', ('A',), ('PACKA',), 0, 'ONE PACKAGE'),
    ('CHAIN', ('A', 'B', 'C'), ('PACKC',), 0, 'THREE PACKAGE CHAIN'),
    ('MISS', ('B',), ('PACKB',), 12, 'MISSING DEPENDENCY'),
    ('MAJOR', ('A', 'BM'), ('PACKB',), 16, 'WRONG API MAJOR'),
    ('MINOR', ('A', 'BN'), ('PACKB',), 16, 'LOW API MINOR'),
    ('ORDER', ('B', 'A'), ('PACKB',), 20, 'REVERSED ORDER'),
    ('CYCLE', ('ACY', 'B'), ('PACKA',), 20, 'CYCLE ORDER REJECT'),
    ('DUPID', ('A', 'A2'), ('PACKA',), 28, 'DUPLICATE PACKAGE ID'),
    ('DUPGN', ('A', 'DG'), ('PACKA',), 32, 'DUPLICATE GLOBAL'),
    ('CORE', ('CORE',), ('PACKX',), 40, 'CORE G14 REJECT'),
    ('RSV', ('RSV',), ('PACKZ',), 40, 'RESERVED G200 REJECT'),
    ('APPREQ', ('A',), ('PACKZ',), 36, 'MISSING APP REQUIREMENT'),
    ('TRANS', ('A', 'C'), ('PACKC',), 12, 'TRANSITIVE MISSING DEP'),
)
FIN_CASES = (
    'R0 F01 EMPTY FINISH RC0 PASS',
    'R0 F02 REVERSE BA ONCE PASS',
    'R0 F03 FINISH ERROR RC8 PASS',
    'R0 F04 STOP4 PRESERVED PASS',
    'R0 F05 STOP8 PRESERVED PASS',
    'R0 F06 STOP0 PRESERVED PASS',
)


def cards_ok(source: str, what: str) -> str:
    for n, card in enumerate(source.splitlines(), 1):
        if (len(card) > 71 or not card.isascii() or '\t' in card
                or card in ('/*',) or card.startswith('//')):
            raise ValueError(f'{what} card {n}: {card!r}')
    return source.rstrip('\n')


def package_source() -> str:
    cards = ['* R.0 TEST ONLY: RELOCATED PER-PACKAGE DESCRIPTORS.']
    for tag, (name, major, minor, global_number, dep) in PACKAGES.items():
        begin, end = 'R0' + tag + 'B', 'R0' + tag + 'E'
        section = 'R0' + tag
        count = 1 if dep else 0
        cards.extend([
            f'{section:<8} CSECT',
            f'         ENTRY {begin},{end}',
            '         EXTRN R0HOOK',
            f"{begin:<8} DC    CL4'BCEX'",
            "         DC    F'1'",
            "         DC    F'48'",
            f"         DC    F'{56 + 16 * count}'",
            f"         DC    CL8'{name:<8}'",
            f"         DC    F'{major}'",
            f"         DC    F'{minor}'",
            "         DC    F'1'",
            "         DC    F'0'",
            f"         DC    F'{count}'",
            "         DC    F'0'",
            f"         DC    F'{global_number}'",
            "         DC    A(R0HOOK)",
        ])
        if dep:
            depid, reqmaj, reqmin = dep
            cards += [f"         DC    CL8'{depid:<8}'",
                      f"         DC    F'{reqmaj}'",
                      f"         DC    F'{reqmin}'"]
        cards += [f'{end:<8} DS    0F']
    cards += ['         END']
    return cards_ok('\n'.join(cards), 'descriptor')


def registry_source() -> str:
    cards = ['* R.0 TEST ONLY: SCENARIO FIXTURES AND LINKED PAIRS.',
             'R0DAT    CSECT',
             '         ENTRY R0TBL',
             '         EXTRN R0HOOK']
    for tag in PACKAGES:
        cards.append(f'         EXTRN R0{tag}B,R0{tag}E')
    for i, (_, selection, requirements, _, _) in enumerate(CASES, 1):
        if selection:
            cards.append(f'SL{i:02d}     DS    0F')
            for tag in selection:
                cards.append(f'         DC    A(R0{tag}B),A(R0{tag}E)')
        if requirements:
            cards.append(f'RQ{i:02d}     DS    0F')
            for r in requirements:
                cards.append(f"         DC    CL8'{r:<8}'")
    cards += ['         DS    0F', 'R0TBL    DC    F\'%s\'' % len(CASES)]
    for i, (ident, selection, requirements, expect, title) in enumerate(CASES, 1):
        sl = f'SL{i:02d}' if selection else '0'
        rq = f'RQ{i:02d}' if requirements else '0'
        cards += [f"         DC    F'{expect}',F'{len(selection)}'",
                  f"         DC    F'{len(requirements)}'",
                  f'         DC    A({sl}),A({rq})',
                  f"         DC    CL80'R0 D{i:02d} {title} PASS'"]
    cards += ['         END']
    return cards_ok('\n'.join(cards), 'registry')


def input_source(name: str) -> str:
    return cards_ok((HERE / name).read_text(encoding='ascii'), name)


def asm_step(name: str, obj: str, src: str) -> list[str]:
    return [f'//{name:<8} EXEC PGM=IFOX00,REGION=256K,',
            "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
            '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
            '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
            '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
            '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
            '//SYSPRINT DD  SYSOUT=*',
            '//SYSPUNCH DD  DUMMY',
            f'//SYSGO    DD  DSN=&&{obj},UNIT=SYSDA,',
            '//             SPACE=(80,(300,100)),DISP=(NEW,PASS),',
            '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSIN    DD  *', *src.splitlines(), '/*']


def make_deck(job_card: list[str]) -> str:
    if not job_card or not job_card[0].startswith('//R0BATCH JOB'):
        raise ValueError('wrong job card')
    inputs = (
        ('ASMM', 'R0MOBJ', input_source('master.asm')),
        ('ASMD', 'R0DOBJ', input_source('dependency.asm')),
        ('ASMF', 'R0FOBJ', input_source('finalizer.asm')),
        ('ASMH', 'R0HOBJ', input_source('hooks.asm')),
        ('ASMP', 'R0POBJ', package_source()),
        ('ASMR', 'R0ROBJ', registry_source()),
    )
    # Descriptors and registry assemble into separate object datasets;
    # IEWL relocates the external begin/end symbols between them.
    cards = [*job_card, '//* R.0 BATCH TEST ONLY; NO ACCEPTED PDS UPDATES']
    for name, obj, src in inputs:
        cards.extend(asm_step(name, obj, src))
    cards += ['//LKED     EXEC PGM=IEWL,REGION=256K,',
              "//             PARM='NCAL,LIST,XREF,MAP',",
              '//             COND=((0,NE,ASMM),(0,NE,ASMD),',
              '//             (0,NE,ASMF),(0,NE,ASMH),',
              '//             (0,NE,ASMP),(0,NE,ASMR))']
    cards += [f'//SYSLIN   DD  DSN=&&{obj},DISP=(OLD,DELETE)'
              if i == 0 else f'//         DD  DSN=&&{obj},DISP=(OLD,DELETE)'
              for i, (_, obj, _) in enumerate(inputs)]
    cards += ['//         DD  *', ' ENTRY R0BM', ' NAME R0BATCH(R)', '/*',
              '//SYSLMOD  DD  DSN=&&R0LOAD(R0BATCH),UNIT=SYSDA,',
              '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
              '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
              '//SYSPRINT DD  SYSOUT=*',
              '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
              '//             TIME=(,2),COND=(0,NE,LKED)',
              '//QOUT     DD  SYSOUT=*,',
              '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
              '//SYSUDUMP DD  SYSOUT=*', '//']
    for n, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'JCL card {n}: {card!r}')
    if cards.count('/*') != 7:
        raise ValueError('expected six independent IFOX inputs + IEWL')
    return '\n'.join(cards) + '\n'


def expected_markers() -> tuple[str, ...]:
    return tuple(f'R0 D{i:02d} {title} PASS' for i, (_, _, _, _, title)
                 in enumerate(CASES, 1)) + FIN_CASES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        jobcard = ["//R0BATCH JOB (BCPL),'R0 BATCH',CLASS=A,MSGCLASS=A"]
    else:
        p = ROOT / 'tools/datasets/dspal-core.py'
        spec = importlib.util.spec_from_file_location('r0batchcore', p)
        if spec is None or spec.loader is None:
            raise RuntimeError('missing authenticated job helper')
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        config = core.load_config()
        jobcard = core.authenticated_job_card(
            config, 'R0BATCH', 'R0 BATCH', redact_password=False)
    deck = make_deck(jobcard)
    if args.check:
        print(f'CHECK R.0 batch: {len(deck.splitlines())} JCL cards; '
              f'{len(CASES)} dependency, {len(FIN_CASES)} finalizer cases; '
              'no credentials or file writes')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'r0-batch.jcl'
    target.write_text(deck, encoding='ascii', newline='\n')
    target.chmod(0o600)
    (OUT / 'expected-markers.txt').write_text(
        '\n'.join(expected_markers()) + '\n', encoding='ascii')
    print(f'R.0 test-only job: {target}')


if __name__ == '__main__':
    main()
