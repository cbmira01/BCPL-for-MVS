#!/usr/bin/env python3
"""Assemble/link/run the first R.2 real-registered BCPLDEMO example.

All new object and load modules use temporary MVS datasets. BOOT_OBJ
is read-only. --check runs without operator credentials or JES access.
This is extension A only, not the full R.2 acceptance matrix.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEMO = ROOT / 'bootstrap-toolchain/extensions/bcpldemo'
R1 = HERE.parent / 'r1-registration/make-jobs.py'
TRAIL = HERE.parent / 'r0-export-trailer-probe/make-job.py'
PROVENANCE = ROOT / 'tools/checks/r1_provenance.py'
WORK = ROOT / 'workarea/runtime-extensions-r2'
JOB = 'R2DEMO'


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing helper: {path}')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def sources() -> tuple[str, str, str]:
    reg = (HERE / 'registry-demo.asm').read_text('ascii')
    desc = (DEMO / 'descriptor.asm').read_text('ascii')
    dispatch = (DEMO / 'dispatcher.asm').read_text('ascii')
    # Reuse the accepted R.1 build-time, link-relocation provenance guard.
    result = load(PROVENANCE, 'r2_demo_provenance').check(reg, desc,
                                                         [dispatch])
    if result != {'descriptor_spans': 1, 'finalizers': []}:
        raise ValueError('unexpected BCPLDEMO BCEX/BCRG contract')
    for title, src in [('registry', reg), ('descriptor', desc),
                       ('dispatcher', dispatch)]:
        for number, line in enumerate(src.splitlines(), 1):
            if not line.isascii() or len(line) > 71 or '\t' in line:
                raise ValueError(f'{title}:{number}: invalid IFOX card')
    return reg, desc, dispatch


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    r1 = load(R1, 'r2_demo_r1_builder')
    reg, desc, dispatch = sources()
    core = (ROOT / 'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    # The R.1 builder's empty base excludes its R1TEST descriptor and
    # dispatcher. Replace only BCPLREG, then add the two DEMO objects.
    deck = r1.make_deck('empty', jobcard, generated, core, obj_dsn,
                        jobname_override=JOB, registry_override=reg,
                        extra_asm=(('ASMD', 'R2DOBJ', desc),
                                   ('ASMS', 'R2SOBJ', dispatch)))
    marker = '//* R.1 EMPTY BCPLREG CANDIDATE'
    if deck.count(marker) != 1:
        raise ValueError('R.1 deck marker changed unexpectedly')
    return deck.replace(marker, '//* R.2 BCPLDEMO BCPLREG CANDIDATE')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generated', type=Path,
                   help='assembler produced by tools/bootstrap/compile-mvs')
    p.add_argument('--check', action='store_true',
                   help='generate synthetic job in memory only')
    args = p.parse_args()
    if not args.check and args.generated is None:
        p.error('use --generated outside --check')
    trail = load(TRAIL, 'r2_demo_trailer')
    generated = (args.generated.read_bytes().decode('latin-1')
                 if args.generated else trail.sample_generated())
    if args.check:
        jobcard = ["//R2DEMO JOB (BCPL),'R2 DEMO',CLASS=A,MSGCLASS=A"]
        obj_dsn = 'HERC02.BCPL.BOOT.OBJ'  # synthetic preflight only
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or
            spec.get('dsorg') != 'PO' or spec.get('recfm') != 'FB' or
            int(spec.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ must be an FB80 object PDS')
        obj_dsn = core.full_dsn(cfg, spec)
        jobcard = core.authenticated_job_card(cfg, JOB,
                    'R2 BCPLDEMO', redact_password=False)
    jcl = make_deck(generated, jobcard, obj_dsn)
    if args.check:
        print(f'CHECK {JOB}: {len(jcl.splitlines())} JCL cards; '
              'temporary objects; no credentials or JCL written')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    output = WORK / 'r2-demo.jcl'
    output.write_text(jcl, encoding='ascii', newline='\n')
    output.chmod(0o600)
    print(f'Candidate JCL: {output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.2 BCPLDEMO generation FAILED: {exc}')
