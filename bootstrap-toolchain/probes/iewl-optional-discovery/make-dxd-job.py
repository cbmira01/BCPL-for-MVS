#!/usr/bin/env python3
"""R.4 candidate: test cumulative DXD length under IFOX/IEWL on MVS.

Four links explicitly select zero, A, B, or both optional packages.
Each combined package keeps its BCEX v1 descriptor and dispatcher and
adds a *unique*, 4-byte external dummy section (DXD) with a Q offset.
One generic observer uses CXD but knows no per-package symbol names.

This DOES NOT register extensions. The CXD word contains a storage
length, not an initialized BCEX descriptor table. The probe establishes
only whether that length reflects explicitly included packages.

Generated objects and load modules use MVS && temporary datasets only.
--check is credential-free and writes nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/runtime-extensions-r4'
JOB = 'R4DXDCXD'
PROFILE = ('zero', 'a', 'b', 'both')
SELECT = {'zero': (), 'a': ('a',), 'b': ('b',),
          'both': ('a', 'b')}
XD = {'a': ('R4DXDA', 'R4XAQ'), 'b': ('R4DXDB', 'R4XBQ')}
EXT_OBJ = {'a': 'R4DAX', 'b': 'R4DBX'}
OBS_OBJ = 'R4OBS'
LOAD = {'zero': 'R4DX0', 'a': 'R4DXA',
        'b': 'R4DXB', 'both': 'R4DXAB'}
LINK = {'zero': 'L0', 'a': 'LA', 'b': 'LB', 'both': 'LX'}
GO = {'zero': 'G0', 'a': 'GA', 'b': 'GB', 'both': 'GX'}


def baseline():
    """Reuse the current R.4 combined package and JCL assembly builder."""
    path = HERE / 'make-job.py'
    spec = importlib.util.spec_from_file_location('r4_iewl_baseline', path)
    if spec is None or spec.loader is None:
        raise ValueError(f'cannot load R.4 baseline: {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extension_source(pkg: str, base=None) -> str:
    """Append unique DXD/Q metadata without modifying a byte of BCEX."""
    if pkg not in XD:
        raise ValueError(f'unknown package {pkg}')
    if base is None:
        base = baseline()
    rows = base.combined_source(pkg).rstrip('\n').splitlines()
    end = {'a': '         END   DMODISP',
           'b': '         END   R2BDISP'}[pkg]
    if rows[-1] != end:
        raise ValueError(f'{pkg}: source END contract changed')
    name, qsect = XD[pkg]
    # DXD supplies storage LENGTH ONLY; Q stores the link-assigned OFFSET.
    # The Q constant also ensures the assembler emits the XD ESD entry.
    rows[-1:] = [
        f'{name:<8} DXD   F',
        f'{qsect:<8} CSECT',
        f'         DC    Q({name})',
        end,
    ]
    result = '\n'.join(rows) + '\n'
    base.checked_cards(result, pkg)
    if result.count('         END   ') != 1:
        raise ValueError('expected one END')
    return result


def observer_source(base=None) -> str:
    """Common code for all four links; no package symbols or WXTRN."""
    if base is None:
        base = baseline()
    rows = [
        '* R.4: DXD/CXD CUMULATIVE LENGTH; NO DESCRIPTOR ENUMERATION.',
        '* ONE UNMODIFIED OBSERVER USED IN ALL FOUR LINK EDITS.',
        'R4CXDOBS CSECT',
        '         LR    1,15',
        '         USING R4CXDOBS,1',
        '         L     0,DXDLEN',
        '         LR    15,0',
        '         BCR   15,14',
        'DXDLEN   CXD',
        '         END   R4CXDOBS',
    ]
    result = '\n'.join(rows) + '\n'
    base.checked_cards(result, 'R4CXDOBS')
    return result


def make_deck(jobcard: list[str], base=None) -> str:
    if base is None:
        base = baseline()
    if not jobcard or jobcard[0].split()[:2] != [f'//{JOB}', 'JOB']:
        raise ValueError('authenticated R4DXDCXD JOB card required')
    cards = [*jobcard,
             '//* R.4 DXD/CXD COUNT STUDY: NO PRODUCTION CODE WRITES.',
             '//* ONE GENERIC OBSERVER OBJECT REUSED ACROSS FOUR LINKS.',
             '//* R2TESTB / G!299 IS TEST-ONLY. ALL OUTPUTS TEMPORARY.']
    for pkg, step in [('a', 'ASPA'), ('b', 'ASPB')]:
        cards += base.asm_step(step, EXT_OBJ[pkg],
                               extension_source(pkg, base))
    cards += base.asm_step('ASOB', OBS_OBJ, observer_source(base))
    for profile in PROFILE:
        link, go = LINK[profile], GO[profile]
        # Capture the generic observer's returned CXD length as its return
        # code: zero, four, four, eight for the four inclusion profiles.
        # The GO code is the **measured length**, not a success/failure RC.
        cards += [
            f'//{link:<8} EXEC PGM=IEWL,REGION=256K,',
            "//             PARM='NCAL,LIST,XREF,MAP',",
            '//             COND=((0,NE,ASPA),(0,NE,ASPB),',
            '//             (0,NE,ASOB))',
            '//PKGA     DD  DSN=&&R4DAX,DISP=(OLD,PASS)',
            '//PKGB     DD  DSN=&&R4DBX,DISP=(OLD,PASS)',
            f'//SYSLIN   DD  DSN=&&{OBS_OBJ},DISP=(OLD,PASS)',
            '//         DD  *',
            *(f' INCLUDE {"PKGA" if pkg == "a" else "PKGB"}'
              for pkg in SELECT[profile]),
            ' ENTRY R4CXDOBS',
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
    for i, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'JCL card {i}: {card!r}')
    if cards.count('/*') != 7:
        raise ValueError('expected three source and four IEWL decks')
    if sum(x.startswith('//SYSLMOD') for x in cards) != 4:
        raise ValueError('expected four load modules')
    if any(x.startswith('//SYSLMOD') and 'HERC' in x for x in cards):
        raise ValueError('persistent output disallowed')
    return '\n'.join(cards) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='credential-free structural test; no file output')
    args = parser.parse_args()
    if args.check:
        card = ["//R4DXDCXD JOB (BCPL),'R4 DXD',CLASS=A,MSGCLASS=A"]
    else:
        base = baseline()
        core = base.load_core()
        cfg = core.load_config()
        card = core.authenticated_job_card(cfg, JOB,
                   'R4 DXD CXD PROBE', redact_password=False)
    deck = make_deck(card)
    if args.check:
        print(f'CHECK {JOB}: {len(deck.splitlines())} JCL cards; '
              '3 ASM, 4 IEWL, 4 GO, all temporary')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / 'r4-dxd-cxd.jcl'
    out.write_text(deck, encoding='ascii', newline='\n')
    out.chmod(0o600)
    print(f'Candidate JCL: {out}')
    print('Expected GO RCs: G0=0000, GA=0004, GB=0004, GX=0008')
    print('Nonzero GO RCs are measurements, not step failures.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.4 DXD/CXD generation FAILED: {exc}')
