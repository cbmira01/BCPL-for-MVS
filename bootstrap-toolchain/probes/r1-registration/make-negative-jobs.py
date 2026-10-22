#!/usr/bin/env python3
"""Generate integrated R.1 negative BCPLREG MVS jobs (unaccepted fixtures).

Each 1001..1014 job must end GO RC=0012 with the matching BCPLREG
WTO and no START message. A test-only BCPLMAIN rejection-path witness
checks that G!298 and G!299 remain unset; a leak returns RC=0016.
2001 must show the finalizer WTO and GO RC=0008 after START executes.

This does not change accepted BOOT_OBJ or canonical BCPLMAIN.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE / 'make-jobs.py'
PATCHER = ROOT / 'tools/checks/r1_prepare_candidate.py'
WORK = Path(os.environ['R1_CAMPAIGN_STAGE']) if os.environ.get(
    'R1_CAMPAIGN_STAGE') else ROOT / 'workarea/runtime-extensions-r1'
CASES = tuple(range(1001, 1015)) + (2001,)


def load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing helper {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def once(src: str, old: str, new: str) -> str:
    if src.count(old) != 1:
        raise ValueError(f'fixture anchor count not 1: {old!r}')
    return src.replace(old, new)


# Source-trusted second package, with an independent dispatcher entry.
# This allows late validation failure after a valid first package.
BASE_PKG = """***********************************************************************
* R.1 NEGATIVE: EXTRA VALID SELECTED PACKAGE (TEST ONLY).
***********************************************************************
R1BASE   CSECT
         ENTRY R1BABEG,R1BAEND,R1BENT
R1BABEG  DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'R1BASE'
         DC    F'1',F'0',F'1',F'0',F'0',F'0'
         DC    F'299',A(R1BENT)
R1BAEND  EQU   *
R1BENT   LA    7,0
         BR    14
         END   R1BASE
"""
FINALIZER = """***********************************************************************
* R.1 NEGATIVE 2001: F ABI TEST (RETURN NONZERO, PRESERVE R2-R13).
***********************************************************************
R1FINAL  CSECT
         ENTRY R1FIN
R1FIN    LA    15,8
         BR    14
         END   R1FINAL
"""


def fixture(case: int) -> tuple[str, str, tuple]:
    """Return (registry, descriptor, extra assembler inputs)."""
    if case not in CASES:
        raise ValueError(f'unknown diagnostic {case}')
    reg = (HERE / 'selected-registry.asm').read_text('ascii')
    desc = (HERE / 'descriptor.asm').read_text('ascii')
    extra = ()
    if case == 1001:
        reg = once(reg, 'BCRGEND  EQU   *',
                   "         DC    X'00'\nBCRGEND  EQU   *")
    elif case == 1002:
        reg = once(reg, "CL4'BCRG'", "CL4'BAD!'")
    elif case == 1003:
        reg = once(reg, "F'44',F'1',F'1'", "F'44',F'2',F'1'")
    elif case == 1004:
        desc = once(desc, 'R1EXEND  EQU   *',
                    "         DC    X'00'\nR1EXEND  EQU   *")
    elif case == 1005:
        desc = once(desc, "CL4'BCEX'", "CL4'BAD!'")
    elif case == 1006:
        desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                    "F'1',F'0',F'2',F'0',F'0',F'0'")
    elif case == 1007:
        desc = once(desc, "CL8'R1TEST'", "CL8' '")
    elif case == 1008:
        desc = once(desc, "F'298',A(R1DISP)", "F'0',A(R1DISP)")
    elif case == 1009:
        desc = once(desc, "F'298',A(R1DISP)", "F'1',A(R1DISP)")
    elif case == 1010:
        reg = once(reg, "F'28',F'44',F'1',F'1'",
                   "F'28',F'52',F'1',F'2'")
        reg = once(reg, 'BCRGEND  EQU   *',
                   "         DC    CL8'MISSING'\nBCRGEND  EQU   *")
    elif case in (1011, 1012):
        reg = once(reg, "F'28',F'44',F'1',F'1'",
                   "F'28',F'52',F'2',F'1'")
        pair = "         DC    A(R1EXBEG),A(R1EXEND)\n"
        base_pair = "         DC    A(R1BABEG),A(R1BAEND)\n"
        reg = once(reg, '         EXTRN R1EXBEG,R1EXEND\n',
                   '         EXTRN R1EXBEG,R1EXEND\n'
                   '         EXTRN R1BABEG,R1BAEND\n')
        reg = once(reg, pair,
                   base_pair + pair if case == 1011 else pair + base_pair)
        desc = once(desc, "F'1',F'48',F'56'", "F'1',F'48',F'72'")
        desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                    "F'1',F'0',F'1',F'0',F'1',F'0'")
        desc = once(desc, 'R1EXEND  EQU   *',
                    "         DC    CL8'R1BASE',F'2',F'0'\n"
                    'R1EXEND  EQU   *' if case == 1011 else
                    "         DC    CL8'R1BASE',F'1',F'0'\n"
                    'R1EXEND  EQU   *')
        extra = (('ASMB', 'R1BOBJ', BASE_PKG),)
    elif case == 1013:
        desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                    "F'1',F'0',F'1',F'1',F'0',F'0'")
    elif case == 1014:
        desc = once(desc, "F'1',F'48',F'56'", "F'1',F'48',F'72'")
        desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                    "F'1',F'0',F'1',F'0',F'1',F'0'")
        desc = once(desc, 'R1EXEND  EQU   *',
                    "         DC    CL8'R1TEST',F'1',F'0'\nR1EXEND  EQU   *")
    elif case == 2001:
        desc = once(desc, '         EXTRN R1DISP\n',
                    '         EXTRN R1DISP,R1FIN\n')
        desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                    "F'1',F'0',F'1',A(R1FIN),F'0',F'0'")
        extra = (('ASMF', 'R1FOBJ', FINALIZER),)
    for name, source in [('registry', reg), ('descriptor', desc),
                         *[(step, source) for step, _, source in extra]]:
        for index, line in enumerate(source.splitlines(), 1):
            if not line.isascii() or len(line) > 71 or '\t' in line:
                raise ValueError(f'{case} invalid {name} card {index}')
    return reg, desc, extra


def rejection_witness(adapted: str) -> str:
    """Add test-only no-partial-publish checks at the R1BAD path."""
    old = 'R1BAD    LR    9,10\n         L     15,=A(IOFIN)\n'
    # Address offsets 4*298 and 4*299. Compare original sentinels.
    # LEAK returns RC=16, not the required registration-reject RC=12.
    insertion = (
        'R1BAD    LR    9,10\n'
        '         L     1,1192(12)\n'
        "         C     1,=X'C7D3F4A8'\n"
        '         BNE   R1LEAK\n'
        '         L     1,1196(12)\n'
        "         C     1,=X'C7D3F4AC'\n"
        '         BNE   R1LEAK\n'
        '         B     R1CLEAN\n'
        "R1LEAK   WTO   'R1 NEGATIVE PARTIAL GLOBAL PUBLICATION'\n"
        '         L     15,=A(IOFIN)\n'
        '         BALR  14,15\n'
        '         LR    10,9\n'
        '         BAL   14,RELMEM\n'
        '         L     13,4(13)\n'
        '         LM    14,12,12(13)\n'
        '         LA    15,16\n'
        '         BR    14\n'
        'R1CLEAN  L     15,=A(IOFIN)\n'
    )
    result = once(adapted, old, insertion)
    if max(map(len, result.splitlines())) > 71:
        raise ValueError('test witness source too wide')
    return result


def make_case(case: int, generated: str, baseline: str, jobcard: list[str],
              obj_dsn: str) -> str:
    builder = load(BASE, 'r1_negative_builder')
    patcher = load(PATCHER, 'r1_negative_patcher')
    reg, desc, extra = fixture(case)
    job = f'R1N{case}'
    core = patcher.adapt(baseline)
    if case != 2001:
        core = rejection_witness(core)
    return builder.make_deck('selected', jobcard, generated, baseline,
                             obj_dsn, jobname_override=job,
                             registry_override=reg,
                             descriptor_override=desc,
                             extra_asm=extra, core_override=core,
                             allow_untrusted_fixture=(case==1013))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('case', help='1001..1014, 2001, or all')
    p.add_argument('--generated', type=Path)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if args.case == 'all':
        cases = CASES
    else:
        try:
            case = int(args.case)
        except ValueError:
            p.error('case must be 1001..1014, 2001, or all')
        if case not in CASES:
            p.error('case must be 1001..1014, 2001, or all')
        cases = (case,)
    if not args.check and args.generated is None:
        p.error('--generated required outside --check')
    builder = load(BASE, 'r1_negative_main')
    trail = builder.load(builder.BASE, 'r1_negative_trailer')
    source = (ROOT / 'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    generated = (args.generated.read_bytes().decode('latin-1') if args.generated
                 else trail.sample_generated())
    if args.check:
        cfg = None
    else:
        core = trail.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or
            spec.get('dsorg') != 'PO' or spec.get('recfm') != 'FB' or
            int(spec.get('lrecl', 0)) != 80):
            raise ValueError('BOOT_OBJ is not an FB80 object PDS')
        dsn = core.full_dsn(cfg, spec)
    for case in cases:
        job = f'R1N{case}'
        if args.check:
            jobcard = [f"//{job} JOB (BCPL),'R1 NEGATIVE',CLASS=A,MSGCLASS=A"]
            dsn = 'HERC02.BCPL.BOOT.OBJ'
        else:
            jobcard = core.authenticated_job_card(
                cfg, job, 'R1 BCPLREG NEGATIVE', redact_password=False)
        deck = make_case(case, generated, source, jobcard, dsn)
        if args.check:
            print(f'CHECK {job}: {len(deck.splitlines())} cards; '
                  f'expect {case}, GO RC={8 if case == 2001 else 12:04d}')
            continue
        WORK.mkdir(parents=True, exist_ok=True)
        output = WORK / f'r1-neg-{case}.jcl'
        output.write_text(deck, 'ascii', newline='\n')
        output.chmod(0o600)
        print(f'Candidate JCL: {output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, UnicodeError) as exc:
        raise SystemExit(f'R.1 negative generation FAILED: {exc}')
