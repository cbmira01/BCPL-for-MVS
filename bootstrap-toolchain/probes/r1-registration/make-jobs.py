#!/usr/bin/env python3
"""Generate candidate R.1 empty/selected BCPLREG IFOX/IEWL/GO JCL.

Use --check for syntax/deck preparation without secrets or disk writes.
Normal operation requires --generated path produced by compile-mvs.
All objects and load modules are temporary. BOOT_OBJ is read-only.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / 'r0-export-trailer-probe/make-job.py'
PATCHER = ROOT / 'tools/checks/r1_prepare_candidate.py'
WORK = ROOT / 'workarea/runtime-extensions-r1'
CORE = ('BCPLIO','BCPLMEM','BCPLBYTE','BCPLAPT','BLIB')


def load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'cannot find helper: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def asm(source: str, desc: str, trail):
    return trail.checked_asm(source, desc)


def make_deck(profile: str, jobcard: list[str], generated: str,
              source: str, obj_dsn: str, *, jobname_override=None,
              registry_override=None, descriptor_override=None,
              extra_asm=(), core_override=None) -> str:
    trail = load(BASE, 'r1_jcl_base')
    patcher = load(PATCHER, 'r1_jcl_patcher')
    selected = profile == 'selected'
    jobname = jobname_override or ('R1SELECT' if selected else 'R1EMPTY')
    if not jobcard or jobcard[0].split()[:2] != [f'//{jobname}', 'JOB']:
        raise ValueError('wrong authenticated job-card identity')
    inputs = [
        ('ASMA', 'R1AOBJ', trail.application_source(generated)),
        ('ASMN', 'R1NOBJ', asm(core_override or patcher.adapt(source), 'BCPLMAIN', trail)),
        ('ASMR', 'R1ROBJ', asm((ROOT / 'bootstrap-toolchain/asm/bcplrgs.asm').read_text('ascii'), 'registrar', trail)),
        ('ASMG', 'R1GOBJ', asm(registry_override or (HERE / ('selected-registry.asm' if selected else '../../asm/bcplreg-empty.asm')).resolve().read_text('ascii'), 'BCPLREG', trail)),
    ]
    if selected:
        for step, obj, name in [('ASMD','R1DOBJ','descriptor.asm'),
                                ('ASMS','R1SOBJ','dispatcher.asm')]:
            inputs.append((step,obj,asm(
                descriptor_override if name == 'descriptor.asm'
                and descriptor_override is not None else
                (HERE / name).read_text('ascii'), name, trail)))
    for step, obj, source_asm in extra_asm:
        inputs.append((step, obj, asm(source_asm, step, trail)))
    cards = [*jobcard, f'//* R.1 {profile.upper()} BCPLREG CANDIDATE',
             '//* ALL TEST OBJECTS TEMPORARY; BOOT_OBJ READ ONLY']
    for step, obj, rows in inputs:
        cards += trail.asm_step(step, obj, rows)
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',",
        '//             COND=(0,NE)',
        f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
    ]
    for i, (_, obj, _) in enumerate(inputs):
        cards += [f'//SYSLIN   DD  DSN=&&{obj},DISP=(OLD,DELETE)'
                  if i == 0 else
                  f'//         DD  DSN=&&{obj},DISP=(OLD,DELETE)']
    cards += [
        '//         DD  *',
        *(f' INCLUDE OBJ({name})' for name in CORE),
        ' ENTRY R0APP',
        f' NAME {jobname}(R)',
        '/*',
        f'//SYSLMOD  DD  DSN=&&R1LOAD({jobname}),UNIT=SYSDA,',
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
            raise ValueError(f'invalid JCL card {n}: {row!r}')
    if cards.count('/*') != len(inputs) + 1:
        raise ValueError('wrong count of assembler + IEWL streams')
    for row in cards:
        if row.startswith('//SYSLMOD') or row.startswith('//SYSGO'):
            if 'BOOT.OBJ' in row or 'BOOT.DEVOBJ' in row:
                raise ValueError('unexpected persistent dataset target')
    return '\n'.join(cards) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=('empty','selected'))
    p.add_argument('--generated', type=Path)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if not args.check and args.generated is None:
        p.error('--generated required outside --check')
    trail = load(BASE, 'r1_trailer')
    source = (ROOT / 'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    generated = (args.generated.read_bytes().decode('latin-1') if args.generated
                 else trail.sample_generated())
    job = 'R1SELECT' if args.profile == 'selected' else 'R1EMPTY'
    if args.check:
        # Avoid requiring authenticated machine-local configuration.
        jobcard = [f'//{job} JOB (BCPL),\'R1 VERIFY\',CLASS=A,MSGCLASS=A']
        dsn = 'HERC02.BCPL.BOOT.OBJ'
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or
            spec.get('dsorg') != 'PO' or spec.get('recfm') != 'FB' or
            int(spec.get('lrecl',0)) != 80):
            raise ValueError('BOOT_OBJ is not an FB80 object PDS')
        dsn = core.full_dsn(cfg,spec)
        jobcard = core.authenticated_job_card(cfg,job,'R1 BCPLREG',
                                            redact_password=False)
    deck = make_deck(args.profile,jobcard,generated,source,dsn)
    if args.check:
        print(f'CHECK {job}: {len(deck.splitlines())} JCL cards, '
              'no credentials or JCL written')
        return
    WORK.mkdir(parents=True,exist_ok=True)
    output = WORK / f'r1-{args.profile}.jcl'
    output.write_text(deck,'ascii',newline='\n')
    output.chmod(0o600)
    print(f'Candidate JCL: {output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError,OSError,UnicodeError) as exc:
        raise SystemExit(f'R.1 JCL generation FAILED: {exc}')
