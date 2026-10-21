#!/usr/bin/env python3
"""R.0 test-only two-dispatcher shared QUERY native BCPL link-and-run."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'workarea/runtime-extensions-r0-query'
TRAIL = HERE.parent / 'r0-export-trailer-probe' / 'make-job.py'
HELPER = ROOT / 'bootstrap-toolchain/regression/prepare-native-global.py'
JOB = 'R0QUERY'
# Test-local only. Neither number is a global registry allocation.
BINDINGS = ((298, 'R0QAA'), (299, 'R0QBB'))


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing module {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def application_source(generated: str) -> list[str]:
    base = load(TRAIL, 'r0_query_trailer')
    helper = load(HELPER, 'r0_query_globals')
    rows = base.application_source(generated)
    entry = rows.index('         ENTRY R0APP')
    for n, (_, symbol) in enumerate(BINDINGS, 1):
        rows.insert(entry + n, f'         EXTRN {symbol}')
    start, maximum, pairs = helper.find_trailer(rows)
    if len(pairs) != 1 or pairs[0][0] != 4:
        raise ValueError('expected only application START G!1 export')
    if maximum < 4 or maximum > 2796 or maximum % 4:
        raise ValueError('invalid generated global-vector maximum')
    offsets = {offset for offset, _ in pairs}
    if any(4 * g in offsets for g, _ in BINDINGS):
        raise ValueError('test-only global already exported')
    end = helper.one_index(rows, helper.L998, 'L998')
    replacement = [f"         DC F'{max(maximum, 4 * BINDINGS[-1][0])}'",
                   "         DC F'0'"]
    for offset, symbol in pairs:
        replacement += [f"         DC F'{offset}'", f'         DC A({symbol})']
    for g, symbol in BINDINGS:
        replacement += [f"         DC F'{4 * g}'", f'         DC A({symbol})']
    rows[start:end] = replacement
    verified = base.checked_asm('\n'.join(rows), 'R.0 QUERY BCPL')
    for g, symbol in BINDINGS:
        if verified.count(f"         DC F'{4 * g}'") != 1:
            raise ValueError(f'no unique G!{g} export')
        if verified.count(f'         DC A({symbol})') != 1:
            raise ValueError(f'no unique {symbol} address')
    return verified


def make_deck(jobcard: list[str], generated: str, obj_dsn: str) -> str:
    base = load(TRAIL, 'r0_query_deck')
    if not jobcard or jobcard[0].split()[:2] != ['//R0QUERY', 'JOB']:
        raise ValueError('bad R0QUERY JOB card')
    if not obj_dsn or not obj_dsn.isascii():
        raise ValueError('invalid BOOT_OBJ dataset')
    rows = [*jobcard, '//* R.0 QUERY: TWO SEPARATE DISPATCHERS, TEST ONLY',
            '//* BOOT_OBJ READ ONLY; LINK TO TEMPORARY LOAD MODULE']
    inputs = (
        ('ASMA', 'R0AOBJ', application_source(generated)),
        ('ASMB', 'R0BOBJ', base.checked_asm(
            (HERE / 'dispatcher-a.asm').read_text('ascii'), 'dispatcher A')),
        ('ASMC', 'R0COBJ', base.checked_asm(
            (HERE / 'dispatcher-b.asm').read_text('ascii'), 'dispatcher B')),
    )
    for step, obj, source in inputs:
        rows += base.asm_step(step, obj, source)
    rows += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=((0,NE,ASMA),(0,NE,ASMB),(0,NE,ASMC))',
        f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
        '//SYSLIN   DD  DSN=&&R0AOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0BOBJ,DISP=(OLD,DELETE)',
        '//         DD  DSN=&&R0COBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' INCLUDE OBJ(BCPLMAIN)',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' INCLUDE OBJ(BLIB)',
        ' ENTRY R0APP',
        ' NAME R0QUERY(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&R0LOAD(R0QUERY),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(0,NE,LKED)',
        '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
        '//             BLKSIZE=132)',
        '//SYSUDUMP DD  SYSOUT=*', '//',
    ]
    for n, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise ValueError(f'invalid JCL card {n}: {row!r}')
    if rows.count('/*') != 4 or sum(x == '//SYSIN    DD  *' for x in rows) != 3:
        raise ValueError('expected three IFOX sources and one IEWL input')
    if any('DISP=SHR' in x and not (x.startswith('//OBJ ') or
        'SYS1.MACLIB' in x) for x in rows):
        raise ValueError('unexpected read-only dataset')
    return '\n'.join(rows) + '\n'


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generated', type=Path)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if args.generated is None and not args.check:
        p.error('--generated required except in --check')
    base = load(TRAIL, 'r0_query_base')
    generated = (args.generated.read_bytes().decode('latin-1')
                 if args.generated is not None else base.sample_generated())
    if args.check:
        card = ["//R0QUERY JOB (BCPL),'R0 QUERY',CLASS=A,MSGCLASS=A"]
        obj = 'HERC02.BCPL.BOOT.OBJ'  # synthetic check only
    else:
        core = base.load_core()
        config = core.load_config()
        spec = config['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
                or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ must be FB80 object PDS')
        obj = core.full_dsn(config, spec)
        card = core.authenticated_job_card(
            config, JOB, 'R0 QUERY ABI', redact_password=False)
    deck = make_deck(card, generated, obj)
    if args.check:
        print(f'CHECK R.0 QUERY: {len(deck.splitlines())} JCL cards; '
              'three independent IFOX objects; no credentials/JCL written')
        return
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / 'r0-query.jcl'
    output.write_text(deck, encoding='ascii', newline='\n')
    output.chmod(0o600)
    print(f'Generated test-only QUERY job: {output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.0 QUERY generation FAILED: {exc}')
