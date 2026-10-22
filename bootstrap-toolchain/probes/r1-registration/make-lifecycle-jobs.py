#!/usr/bin/env python3
"""Prepare four independent integrated R.1 finalizer lifecycle jobs.

Order of package selection: R1BASE, R1TEST. Observable finalizers:
R1TEST then R1BASE; both receive public two-word FINISH/STOP ABI.
Temporary IFOX objects/IEWL load modules; BOOT_OBJ remains DISP=SHR.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = Path(os.environ['R1_CAMPAIGN_STAGE']) if os.environ.get(
    'R1_CAMPAIGN_STAGE') else ROOT / 'workarea/runtime-extensions-r1'
PROFILES = ('finish', 'stop', 'finish-error', 'stop-error')
JOBS = {'finish':'R1LFIN', 'stop':'R1LSTOP',
        'finish-error':'R1LFERR', 'stop-error':'R1LSERR'}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ValueError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f'fixture anchor mismatch: {old[:60]}')
    return source.replace(old, new)


def finalizer(symbol: str, fail: bool) -> str:
    """A real MVS 8-byte-argument finalizer, with separate WTO traces."""
    unit = symbol[-1]
    assert unit in ('A', 'B')
    return '\n'.join((
        '***********************************************************************',
        f'* R.1 {symbol} FINALIZER - PUBLIC 8-BYTE PARAMETER ABI.',
        '***********************************************************************',
        f'{symbol:<8} CSECT',
        f'         ENTRY {symbol}',
        '         STM   14,12,12(13)',
        '         LR    12,15',
        f'         USING {symbol},12',
        '         LA    2,FSAVE',
        '         ST    13,4(2)',
        '         ST    2,8(13)',
        '         LR    13,2',
        '         L     3,0(1)',
        '         LTR   3,3',
        '         BZ    FINISH',
        "         C     3,=F'1'",
        '         BNE   BADPARM',
        '         L     3,4(1)',
        "         C     3,=F'7'",
        '         BNE   BADPARM',
        f"         WTO   'R1 TRACE FIN{unit} STOP'",
        '         B     DONE',
        f"FINISH   WTO   'R1 TRACE FIN{unit} FINISH'",
        '         B     DONE',
        f"BADPARM  WTO   'R1 TRACE FIN{unit} BAD PARAMETER'",
        '         LA    15,8',
        '         B     EXIT',
        'DONE     LA    15,' + ('8' if fail else '0'),
        'EXIT     ST    15,RCELL',
        '         L     13,4(13)',
        '         LM    14,14,12(13)',
        '         LM    0,12,20(13)',
        '         L     15,RCELL',
        '         BR    14',
        '         DS    0F',
        'FSAVE    DS    18F',
        "RCELL    DC    F'0'",
        '         LTORG',
        f'         END   {symbol}',
    )) + '\n'


def sources(profile: str) -> tuple[str, str, tuple]:
    if profile not in PROFILES:
        raise ValueError('unknown profile')
    reg = (HERE/'selected-registry.asm').read_text('ascii')
    desc = (HERE/'descriptor.asm').read_text('ascii')
    negative = load(HERE/'make-negative-jobs.py', 'r1_lifecycle_negative')
    base = negative.BASE_PKG
    reg = once(reg, '         EXTRN R1EXBEG,R1EXEND\n',
               '         EXTRN R1EXBEG,R1EXEND\n'
               '         EXTRN R1BABEG,R1BAEND\n')
    reg = once(reg, "F'28',F'44',F'1',F'1'",
               "F'28',F'44',F'2',F'0'")
    reg = once(reg, '         DC    A(R1EXBEG),A(R1EXEND)\n',
               '         DC    A(R1BABEG),A(R1BAEND)\n'
               '         DC    A(R1EXBEG),A(R1EXEND)\n')
    reg = once(reg, "         DC    CL8'R1TEST'\n", '')
    desc = once(desc, '         EXTRN R1DISP\n',
                '         EXTRN R1DISP,R1FINA\n')
    desc = once(desc, "F'1',F'48',F'56'", "F'1',F'48',F'72'")
    desc = once(desc, "F'1',F'0',F'1',F'0',F'0',F'0'",
                "F'1',F'0',F'1',A(R1FINA),F'1',F'0'")
    desc = once(desc, 'R1EXEND  EQU   *',
                "         DC    CL8'R1BASE',F'1',F'0'\n"
                'R1EXEND  EQU   *')
    base = once(base, '         ENTRY R1BABEG,R1BAEND,R1BENT\n',
                '         ENTRY R1BABEG,R1BAEND,R1BENT\n'
                '         EXTRN R1FINB\n')
    base = once(base, "F'1',F'0',F'1',F'0',F'0',F'0'",
                "F'1',F'0',F'1',A(R1FINB),F'0',F'0'")
    extras = (('ASMB', 'R1BOBJ', base),
              ('ASMF', 'R1FOBJ', finalizer('R1FINA',
                                         profile.endswith('-error'))),
              ('ASMH', 'R1HOBJ', finalizer('R1FINB', False)))
    for title, src in [('registry',reg),('descriptor',desc),
                       *[(step,item) for step,_,item in extras]]:
        for index, line in enumerate(src.splitlines(),1):
            if not line.isascii() or len(line) > 71 or '\t' in line:
                raise ValueError(f'{title} card {index}: invalid line {line!r}')
    return reg, desc, extras


def build(profile: str, generated: str, baseline: str,
          jobcard: list[str], obj_dsn: str) -> str:
    builder = load(HERE/'make-jobs.py', 'r1_lifecycle_builder')
    reg, desc, extras = sources(profile)
    return builder.make_deck(
        'selected', jobcard, generated, baseline, obj_dsn,
        jobname_override=JOBS[profile],
        registry_override=reg, descriptor_override=desc,extra_asm=extras)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=(*PROFILES,'all'))
    p.add_argument('--generated-finish',type=Path)
    p.add_argument('--generated-stop',type=Path)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    if not args.check and (not args.generated_finish or not args.generated_stop):
        p.error('both --generated-finish and --generated-stop are required')
    profiles=PROFILES if args.profile=='all' else (args.profile,)
    builder=load(HERE/'make-jobs.py', 'r1_lifecycle_main')
    trail=builder.load(builder.BASE, 'r1_lifecycle_trailer')
    source=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    if args.check:
        dsn='HERC02.BCPL.BOOT.OBJ'
        cfg=None
    else:
        core=trail.load_core()
        cfg=core.load_config()
        spec=cfg['datasets']['BOOT_OBJ']
        if spec.get('content_type')!='object' or spec.get('dsorg')!='PO' or spec.get('recfm')!='FB' or int(spec.get('lrecl',0))!=80:
            raise ValueError('BOOT_OBJ must be an FB80 object PDS')
        dsn=core.full_dsn(cfg,spec)
    for profile in profiles:
        job=JOBS[profile]
        if args.check:
            generated=trail.sample_generated()
            jobcard=[f"//{job} JOB (BCPL),'R1 LIFE',CLASS=A,MSGCLASS=A"]
        else:
            path=args.generated_stop if profile.startswith('stop') else args.generated_finish
            generated=path.read_bytes().decode('latin-1')
            jobcard=core.authenticated_job_card(cfg,job,'R1 LIFECYCLE',redact_password=False)
        deck=build(profile,generated,source,jobcard,dsn)
        if args.check:
            print(f'CHECK {job}: {len(deck.splitlines())} cards')
        else:
            WORK.mkdir(parents=True,exist_ok=True)
            output=WORK/f'r1-life-{profile}.jcl'
            output.write_text(deck,'ascii',newline='\n')
            output.chmod(0o600)
            print(f'Candidate JCL: {output}')

if __name__ == '__main__':
    try:
        main()
    except (ValueError,OSError,UnicodeError) as exc:
        raise SystemExit(f'R.1 lifecycle generation FAILED: {exc}')
