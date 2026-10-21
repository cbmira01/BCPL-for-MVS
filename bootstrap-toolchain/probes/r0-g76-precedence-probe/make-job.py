#!/usr/bin/env python3
"""Prepare a one-job R.0 test of installed BCPLMAIN G!76 precedence."""
from __future__ import annotations

import argparse
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/runtime-extensions-r0-g76'
TRAIL = HERE.parent / 'r0-export-trailer-probe' / 'make-job.py'
HELPER = ROOT / 'bootstrap-toolchain/regression/prepare-native-global.py'
JOB = 'R0G76'


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    if spec is None or spec.loader is None:
        raise ValueError(f'unable to load {path}')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def application_source(generated: str) -> list[str]:
    base = load(TRAIL, 'r0_g76_trailer')
    helper = load(HELPER, 'r0_g76_native')
    rows = base.application_source(generated)
    position = rows.index('         ENTRY R0APP')
    rows.insert(position + 1, '         EXTRN R0CK76')
    start, maximum, pairs = helper.find_trailer(rows)
    if len(pairs) != 1 or pairs[0][0] != 4:
        raise ValueError('test application must export only START G!1')
    if maximum < 4 or maximum % 4 or maximum > 2796:
        raise ValueError('invalid application maximum global')
    l998 = helper.one_index(rows, helper.L998, 'L998')
    replacement = [f"         DC F'{max(maximum, 604)}'", "         DC F'0'"]
    for offset, value in pairs:
        replacement += [f"         DC F'{offset}'", f'         DC A({value})']
    replacement += ["         DC F'604'", '         DC A(R0CK76)']
    rows[start:l998] = replacement
    return base.checked_asm('\n'.join(rows), 'G76 application with G!151')


def make_deck(jobcard: list[str], generated: str, probe: str,
              obj_dsn: str) -> str:
    trailer = load(TRAIL, 'r0_g76_deck')
    if not jobcard or jobcard[0].split()[:2] != ['//R0G76', 'JOB']:
        raise ValueError('unexpected R0G76 job card')
    cards = [*jobcard, '//* R.0 G76 REAL RUNTIME, INSTALLED BOOT_OBJ; NO PDS WRITES']
    cards += trailer.asm_step('ASMA', 'R0AOBJ', application_source(generated))
    cards += trailer.asm_step('ASMP', 'R0POBJ',
                              trailer.checked_asm(probe, 'G76 test function'))
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMA),(0,NE,ASMP))',
        f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
        '//SYSLIN   DD  DSN=&&R0AOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0POBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' INCLUDE OBJ(BCPLMAIN)',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' INCLUDE OBJ(BLIB)',
        ' ENTRY R0APP',
        ' NAME R0G76(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0G76),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(0,NE,LKED)',
        '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
        '//             BLKSIZE=132)',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for n, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise ValueError(f'bad JCL card {n}: {row!r}')
    if cards.count('/*') != 3:
        raise ValueError('expected two inline IFOX and IEWL sources')
    if any('DISP=SHR' in row and '//OBJ' not in row and
           'SYS1.MACLIB' not in row for row in cards):
        raise ValueError('unexpected permanent DD access')
    return '\n'.join(cards) + '\n'


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--generated', type=Path)
    a = p.parse_args()
    if not a.check and a.generated is None:
        p.error('--generated required unless --check')
    trail = load(TRAIL, 'r0_g76_standalone')
    generated = (a.generated.read_bytes().decode('latin-1')
                 if a.generated else trail.sample_generated())
    probe = (HERE / 'check76.asm').read_text('ascii')
    if a.check:
        jobcard = ['//R0G76   JOB (BCPL),\'G76 PROBE\',CLASS=A,MSGCLASS=A']
        obj_dsn = 'HERC02.BCPL.BOOT.OBJ'
    else:
        core = trail.load_core()
        cfg = core.load_config()
        obj = cfg['datasets']['BOOT_OBJ']
        if (obj.get('content_type') != 'object' or obj.get('dsorg') != 'PO'
                or obj.get('recfm') != 'FB' or int(obj.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ must be an FB80 object PDS')
        jobcard = core.authenticated_job_card(
            cfg, JOB, 'R0 G76 PRECEDENCE', redact_password=False)
        obj_dsn = core.full_dsn(cfg, obj)
    deck = make_deck(jobcard, generated, probe, obj_dsn)
    if a.check:
        print(f'CHECK R.0 G76: {len(deck.splitlines())} JCL cards; '
              'no credentials or JCL written')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / 'r0-g76.jcl'
    out.write_text(deck, encoding='ascii', newline='\n')
    out.chmod(0o600)
    print(f'Generated test-only JCL: {out}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'R.0 G76 generator FAILED: {exc}')
