#!/usr/bin/env python3
"""Generate one isolated R.0 real-runtime G!76 no-export-BLIB test job."""
from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/runtime-extensions-r0-g76-noexport'
TRAIL = HERE.parent / 'r0-export-trailer-probe/make-job.py'
HELPER = ROOT / 'bootstrap-toolchain/regression/prepare-native-global.py'
JOB = 'R0G76F'
MAXG = 2796


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'cannot import {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fixture_source(text: str) -> list[str]:
    """Require a *single* short linked BLIB and exactly one empty trailer."""
    src = text.splitlines()
    executable = [x for x in src if x and not x.startswith('*')]
    expected = [
        'BLIB     CSECT',
        '         ENTRY BLIB',
        '         EXTRN BCPLMAIN',
        '         STM   14,12,12(13)',
        '         L     4,12(15)',
        '         BCR   15,4',
        '         DC    AL2(BLEND-BLIB)',
        '         DC    A(BCPLMAIN)',
        "         DC    F'2796'",
        "         DC    F'0'",
        'BLEND    EQU   *',
        '         END   BLIB',
    ]
    if executable != expected:
        raise ValueError('temporary BLIB must match exact no-export prefix/trailer')
    if any(len(row) > 71 or not row.isascii() or '\t' in row for row in src):
        raise ValueError('invalid IFOX fixture card')
    return src


def application_source(generated: str) -> list[str]:
    trail = load(TRAIL, 'r0g76f_trailer')
    helper = load(HELPER, 'r0g76f_trailer_helper')
    rows = trail.application_source(generated)
    start, maximum, pairs = helper.find_trailer(rows)
    if len(pairs) != 1 or pairs[0][0] != 4:
        raise ValueError('test application must export START only; no G!76')
    if maximum < 4 or maximum > MAXG or maximum % 4:
        raise ValueError('invalid application maximum global')
    if not any(re.fullmatch(r'\s*EXTRN\s+BCPLMAIN\s*', x) for x in rows):
        raise ValueError('application lost runtime external')
    return rows


def make_deck(jobcard: list[str], generated: str, stub: str, obj: str) -> str:
    trail = load(TRAIL, 'r0g76f_job')
    if not jobcard or jobcard[0].split()[:2] != ['//R0G76F', 'JOB']:
        raise ValueError('unexpected JOB card')
    if not re.fullmatch(r'[A-Z0-9@#$]+(?:\.[A-Z0-9@#$]+)+', obj):
        raise ValueError('invalid installed object DSN')
    if not obj.endswith('.BOOT.OBJ'):
        raise ValueError('unexpected installed object dataset')
    fixture_source(stub)
    cards = [*jobcard,
             '//* R.0 G76 NO-EXPORT BLIB: TEMP FIXTURE, INSTALLED OBJ READ ONLY',
             '//* NEVER INCLUDE INSTALLED BOOT_OBJ(BLIB); R.1 NOT STARTED']
    cards += trail.asm_step('ASMA', 'R0AOBJ', application_source(generated))
    cards += trail.asm_step('ASMB', 'R0BOBJ', fixture_source(stub))
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMA),(0,NE,ASMB))',
        f'//OBJ      DD  DSN={obj},DISP=SHR',
        '//SYSLIN   DD  DSN=&&R0AOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0BOBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' INCLUDE OBJ(BCPLMAIN)',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' ENTRY R0APP',
        ' NAME R0G76F(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0G76F),UNIT=SYSDA,',
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
    for i, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise ValueError(f'invalid JCL card {i}: {row!r}')
    if cards.count('/*') != 3:
        raise ValueError('require two IFOX inputs and IEWL control deck')
    if ' INCLUDE OBJ(BLIB)' in cards:
        raise ValueError('installed BLIB inclusion forbidden')
    if not any(x == f'//OBJ      DD  DSN={obj},DISP=SHR' for x in cards):
        raise ValueError('accepted object input not read-only')
    permanent = [x for x in cards if 'DSN=' in x and not '&&' in x and not 'SYS1.MACLIB' in x]
    if permanent != [f'//OBJ      DD  DSN={obj},DISP=SHR']:
        raise ValueError(f'unapproved permanent DD: {permanent!r}')
    return '\n'.join(cards) + '\n'


def run() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--generated', type=Path)
    args = p.parse_args()
    if not args.check and args.generated is None:
        p.error('--generated required outside --check')
    trail = load(TRAIL, 'r0g76f_cli')
    generated = (args.generated.read_bytes().decode('latin-1')
                 if args.generated else trail.sample_generated())
    fixture = (HERE / 'blib-empty.asm').read_text('ascii')
    if args.check:
        jobcard = ["//R0G76F  JOB (BCPL),'G76 NOEXP',CLASS=A,MSGCLASS=A"]
        obj = 'HERC02.BCPL.BOOT.OBJ'
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
                or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ must be an FB80 object PDS')
        obj = core.full_dsn(cfg, spec)
        jobcard = core.authenticated_job_card(
            cfg, JOB, 'R0 G76 NO EXPORT', redact_password=False)
    deck = make_deck(jobcard, generated, fixture, obj)
    if args.check:
        print(f'CHECK R.0 G76 no-export: {len(deck.splitlines())} '
              'cards; no credentials, write DD or MVS submission')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / 'r0-g76-noexport.jcl'
    path.write_text(deck, encoding='ascii', newline='\n')
    path.chmod(0o600)
    print(f'Generated test-only JCL: {path}')


if __name__ == '__main__':
    try:
        run()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'R.0 G76 no-export generator FAILED: {exc}')
