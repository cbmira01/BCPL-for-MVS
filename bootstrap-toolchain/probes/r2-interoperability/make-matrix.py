#!/usr/bin/env python3
"""Build four R.2 selection links in ONE job, with ONE BCPLMAIN object.

Selections are zero, A (BCPLDEMO G!203), B (test-only G!299), A+B.
All generated objects and load modules are temporary MVS datasets.
The --check path is credential-free and writes no files.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRAIL = HERE.parent / 'r0-export-trailer-probe/make-job.py'
PATCHER = ROOT / 'tools/checks/r1_prepare_candidate.py'
PROVENANCE = ROOT / 'tools/checks/r1_provenance.py'
DEMO = ROOT / 'bootstrap-toolchain/extensions/bcpldemo'
TESTB = ROOT / 'bootstrap-toolchain/extensions/r2testb'
WORK = ROOT / 'workarea/runtime-extensions-r2'
JOB = 'R2MATRIX'
CORE = ('BCPLIO', 'BCPLMEM', 'BCPLBYTE', 'BCPLAPT', 'BLIB')
PROFILES = ('zero', 'a', 'b', 'both')
APP_OBJ = {'zero': 'R2A0', 'a': 'R2AA', 'b': 'R2AB', 'both': 'R2AAB'}
REG_OBJ = {'zero': 'R2G0', 'a': 'R2GA', 'b': 'R2GB', 'both': 'R2GX'}
LINK = {'zero': 'L0', 'a': 'LA', 'b': 'LB', 'both': 'LX'}
GO = {'zero': 'G0', 'a': 'GA', 'b': 'GB', 'both': 'GX'}
LOAD = {'zero': 'R2ZERO', 'a': 'R2ONLYA', 'b': 'R2ONLYB',
        'both': 'R2BOTH'}
LDDSN = {'zero': 'R2L0', 'a': 'R2LA', 'b': 'R2LB', 'both': 'R2LX'}
SELECT = {'zero': (), 'a': ('a',), 'b': ('b',),
          'both': ('a', 'b')}
PKG = {'a': ('DMOBEG', 'DMOEND', 'BCPLDEMO'),
       'b': ('R2BBEG', 'R2BEND', 'R2TESTB')}
PKG_OBJ = {'a': ('R2AD', 'R2AS'), 'b': ('R2BD', 'R2BS')}


def load(path: Path, label: str):
    spec = importlib.util.spec_from_file_location(label, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing build helper: {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def registry(profile: str) -> str:
    selected = SELECT[profile]
    count = len(selected)
    total = 28 + count * 16
    lines = [
        '* R.2 TEST REGISTRY; ONLY EXPLICITLY SELECTED PACKAGES.',
        'BCPLREG  CSECT',
        '         ENTRY BCRGBEG,BCRGEND',
    ]
    if selected:
        symbols = ','.join(symbol for pkg in selected
                           for symbol in PKG[pkg][:2])
        lines.append(f'         EXTRN {symbols}')
    lines += [
        'BCRGBEG  DS    0F',
        "         DC    CL4'BCRG'",
        f"         DC    F'1',F'28',F'{total}',F'{count}',F'{count}',F'0'",
    ]
    for pkg in selected:
        begin, end, _ = PKG[pkg]
        lines.append(f'         DC    A({begin}),A({end})')
    for pkg in selected:
        lines.append(f"         DC    CL8'{PKG[pkg][2]}'")
    lines += ['BCRGEND  EQU   *', '         END   BCPLREG']
    return '\n'.join(lines) + '\n'


def extension_sources() -> dict[str, tuple[str, str]]:
    return {
        'a': ((DEMO / 'descriptor.asm').read_text('ascii'),
              (DEMO / 'dispatcher.asm').read_text('ascii')),
        'b': ((TESTB / 'descriptor.asm').read_text('ascii'),
              (TESTB / 'dispatcher.asm').read_text('ascii')),
    }


def make_deck(generated: dict[str, str], jobcard: list[str],
              obj_dsn: str) -> str:
    if set(generated) != set(PROFILES):
        raise ValueError('require all four compiler-generated sources')
    if not jobcard or jobcard[0].split()[:2] != [f'//{JOB}', 'JOB']:
        raise ValueError('wrong authenticated JOB card')
    trail = load(TRAIL, 'r2_matrix_trail')
    patch = load(PATCHER, 'r2_matrix_patcher')
    provenance = load(PROVENANCE, 'r2_matrix_provenance')
    extensions = extension_sources()
    for profile, selected in SELECT.items():
        if selected:
            descriptors = '\n'.join(extensions[p][0] for p in selected)
            dispatchers = [extensions[p][1] for p in selected]
            result = provenance.check(registry(profile), descriptors,
                                      dispatchers)
            if result != {'descriptor_spans':len(selected),
                          'finalizers': []}:
                raise ValueError(f'{profile}: unexpected BCEX contract')
    # Once assembled, the same unmodified temporary core and registrar
    # object datasets are passed to all FOUR separate IEWL link-edits.
    source = (ROOT / 'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    native_core = patch.adapt(source)
    registrar = (ROOT / 'bootstrap-toolchain/asm/bcplrgs.asm').read_text('ascii')
    inputs = []
    for profile, step in [('zero','AS0'), ('a','ASA'),
                          ('b','ASB'), ('both','ASAB')]:
        inputs.append((step, APP_OBJ[profile],
                       trail.application_source(generated[profile])))
    inputs += [
        ('ASMN', 'R2NOBJ', trail.checked_asm(native_core, 'BCPLMAIN')),
        ('ASMR', 'R2ROBJ', trail.checked_asm(registrar, 'RGINIT')),
    ]
    for profile, step in [('zero','ASG0'), ('a','ASGA'),
                          ('b','ASGB'), ('both','ASGX')]:
        inputs.append((step, REG_OBJ[profile],
                       trail.checked_asm(registry(profile), 'BCPLREG')))
    for pkg, desc_step, disp_step in [('a','ASDA','ASSA'),
                                      ('b','ASDB','ASSB')]:
        desc, disp = extensions[pkg]
        d_obj, s_obj = PKG_OBJ[pkg]
        inputs += [(desc_step, d_obj, trail.checked_asm(desc, 'BCEX')),
                   (disp_step, s_obj, trail.checked_asm(disp, 'dispatcher'))]
    cards = [*jobcard,
             '//* R.2 SELECTIVE INTEROPERABILITY FOUR-LINK CANDIDATE',
             '//* BCPLMAIN ASSEMBLED ONCE; ALL OBJECTS TEMPORARY',
             '//* BOOT_OBJ READ ONLY; G299 TEST-LOCAL ONLY']
    for step, obj, source_lines in inputs:
        cards += trail.asm_step(step, obj, source_lines)
    for profile in PROFILES:
        lstep = LINK[profile]
        objects = [APP_OBJ[profile], 'R2NOBJ', 'R2ROBJ',
                   REG_OBJ[profile]]
        for pkg in SELECT[profile]:
            objects.extend(PKG_OBJ[pkg])
        cards += [
            f'//{lstep:<8} EXEC PGM=IEWL,REGION=256K,',
            "//             PARM='NCAL,LIST,XREF,MAP',",
            '//             COND=(0,NE)',
            f'//OBJ      DD  DSN={obj_dsn},DISP=SHR',
        ]
        for i, obj in enumerate(objects):
            dd = '//SYSLIN   DD ' if i == 0 else '//         DD '
            cards.append(f'{dd} DSN=&&{obj},DISP=(OLD,PASS)')
        cards += [
            '//         DD  *',
            *(f' INCLUDE OBJ({name})' for name in CORE),
            ' ENTRY R0APP',
            f' NAME {LOAD[profile]}(R)',
            '/*',
            f'//SYSLMOD  DD  DSN=&&{LDDSN[profile]}'
            f'({LOAD[profile]}),UNIT=SYSDA,',
            '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
            '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
            '//SYSPRINT DD  SYSOUT=*',
            f'//{GO[profile]:<8} EXEC PGM=*.{lstep}.SYSLMOD,REGION=256K,',
            f'//             TIME=(,2),COND=(0,NE,{lstep})',
            '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
            '//             BLKSIZE=132)',
            '//SYSUDUMP DD  SYSOUT=*',
        ]
    cards.append('//')
    for line_no, line in enumerate(cards, 1):
        if (not line.isascii() or len(line) > 71 or '\t' in line):
            raise ValueError(f'invalid JCL card {line_no}: {line!r}')
    expected = len(inputs) + len(PROFILES)
    if cards.count('/*') != expected:
        raise ValueError(f'expected {expected} exact instream terminators')
    if sum(line.startswith('//ASMN') for line in cards) != 1:
        raise ValueError('core assembly must occur exactly once')
    if any('DISP=MOD' in line or 'BOOT.DEVOBJ' in line for line in cards):
        raise ValueError('unexpected persistent output target')
    return '\n'.join(cards) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='synthetic check only, no files or credentials')
    parser.add_argument('--generated-dir', type=Path,
                        help='directory with zero/a/b/both.s370.asm')
    args = parser.parse_args()
    if not args.check and args.generated_dir is None:
        parser.error('--generated-dir required outside --check')
    trail = load(TRAIL, 'r2_matrix_trail_fixture')
    if args.generated_dir:
        generated = {p:(args.generated_dir / f'{p}.s370.asm')
                         .read_bytes().decode('latin-1') for p in PROFILES}
    else:
        generated = {p:trail.sample_generated() for p in PROFILES}
    if args.check:
        jobcard = ["//R2MATRIX JOB (BCPL),'R2 MATRIX',CLASS=A,MSGCLASS=A"]
        obj_dsn = 'HERC02.BCPL.BOOT.OBJ'
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or
            spec.get('dsorg') != 'PO' or spec.get('recfm') != 'FB' or
            int(spec.get('lrecl',0)) != 80):
            raise ValueError('BOOT_OBJ must be an FB80 object PDS')
        obj_dsn = core.full_dsn(cfg, spec)
        jobcard = core.authenticated_job_card(
            cfg, JOB, 'R2 SELECTIVE MATRIX', redact_password=False)
    jcl = make_deck(generated, jobcard, obj_dsn)
    if args.check:
        print(f'CHECK {JOB}: {len(jcl.splitlines())} JCL cards; '
              '4 links / 4 runs / 1 BCPLMAIN assembly; no files written')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    output = WORK / 'r2-matrix.jcl'
    output.write_text(jcl, encoding='ascii', newline='\n')
    output.chmod(0o600)
    print(f'Candidate JCL: {output}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'R.2 matrix generation FAILED: {exc}')
