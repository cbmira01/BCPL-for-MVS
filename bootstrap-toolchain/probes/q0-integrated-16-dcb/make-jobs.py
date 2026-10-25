#!/usr/bin/env python3
"""Generate a temporary-only Q.0 native BCPL / sixteen-QSAM-DCB JES job."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WRITER = ROOT / 'bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py'
TRAIL = ROOT / 'bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py'
WORK = ROOT / 'workarea/qsam-q0-integrated'
PROFILES = {'finish': ('Q0NFIN', 256), 'stop': ('Q0NSTP', 256),
            'finish-512': ('Q0NF512', 512), 'stop-512': ('Q0NS512', 512)}
COUNT = 16


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing Git source: {path}')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def registry():
    return '\n'.join([
        '* Q.0 FIXTURE REGISTRY. G!299 IS TEST-ONLY.',
        'BCPLREG  CSECT',
        '         ENTRY BCRGBEG,BCRGEND',
        '         EXTRN Q0TBEG,Q0TEND',
        'BCRGBEG  DS    0F',
        "         DC    CL4'BCRG'",
        "         DC    F'1',F'28',F'44',F'1',F'1',F'0'",
        '         DC    A(Q0TBEG),A(Q0TEND)',
        "         DC    CL8'Q0PROBE'",
        'BCRGEND  EQU   *',
        '         END']) + '\n'


def extension():
    """Registered test-only native dispatcher + MVS finalizer.

    The BCPL caller issues operation 1: 16 checked private stages,
    16 OPEN input DCBs, one verified 1024-byte record per DCB. It
    deliberately leaves all handles OPEN for FINISH/STOP finalization.
    The finalizer closes all sixteen, frees stages, checks counts.
    """
    a = [
        '* Q.0 NATIVE INTEGRATION TEST ONLY. NOT BCPLQSAM G!200.',
        'Q0TDESC  CSECT',
        '         ENTRY Q0TBEG,Q0TEND',
        'Q0TBEG   DS    0F',
        "         DC    CL4'BCEX'",
        "         DC    F'1',F'48',F'56'",
        "         DC    CL8'Q0PROBE'",
        "         DC    F'1',F'0',F'1',A(Q0TFIN),F'0',F'0'",
        "         DC    F'299',A(Q0TDISP)",
        'Q0TEND   EQU   *',
        'Q0TDISP  CSECT',
        '         ENTRY Q0TDISP,Q0TFIN',
        '         STM   4,9,0(15)',
        '         LR    5,15',
        '         STM   0,1,24(5)',
        '         USING Q0TDISP,4',
        "         C     7,=F'1'",
        '         BNE   Q0TBOP',
        '         L     15,=A(Q0TINIT)',
        '         BALR  14,15',
        '         LR    7,15',
        '         LM    0,1,24(5)',
        '         BCR   15,11',
        "Q0TBOP   L     7,=F'-2'",
        '         LM    0,1,24(5)',
        '         BCR   15,11',
        '         LTORG',
        '* PRIVATE MVS HELPER; PUBLIC TEST OPCODE IS NOT QSAMSVC.',
        'Q0TINIT  DS    0H',
        '         STM   14,12,12(13)',
        '         LR    12,15',
        '         USING Q0TINIT,12',
        '         LA    10,4095(12)',
        '         LA    10,1(10)',
        '         USING Q0TINIT+4096,10',
        '         LA    9,4095(10)',
        '         LA    9,1(9)',
        '         USING Q0TINIT+8192,9',
        '         LA    11,ISAVE',
        '         ST    13,4(11)',
        '         ST    11,8(13)',
        '         LR    13,11',
        '         XC    PTRS(64),PTRS',
        '         XC    NALLOC(4),NALLOC',
        '         XC    NFREE(4),NFREE',
        '         XC    NOPEN(4),NOPEN',
        '         XC    NCLOSE(4),NCLOSE',
    ]
    for i in range(COUNT):
        a += ['         GETMAIN RC,LV=1024',
              '         LTR   15,15',
              '         BNZ   Q0TALFL',
              f'         ST    1,PTR{i:02d}',
              '         L     3,NALLOC',
              '         LA    3,1(3)',
              '         ST    3,NALLOC']
    for i in range(COUNT):
        a += [f'         OPEN  (DC{i:02d},(INPUT))',
              '         L     3,NOPEN',
              '         LA    3,1(3)',
              '         ST    3,NOPEN']
    for i in range(COUNT):
        a += [f'         L     0,PTR{i:02d}',
              f'         GET   DC{i:02d},(0)',
              f'         L     1,PTR{i:02d}',
              f"         CLC   0(8,1),=CL8'Q0H{i:02d}R01'",
              '         BNE   Q0TERR',
              "         CLI   1023(1),X'FE'",
              '         BNE   Q0TERR']
    a += ["         WTO   'Q0 NATIVE 16 OPEN READ PASS'",
          '         SR    15,15',
          '         B     Q0TRET',
          "Q0TALFL  WTO   'Q0 NATIVE STAGE ALLOCATION FAILED'",
          ]
    # No OPEN has occurred yet. Release every acquired private stage.
    for i in range(COUNT-1, -1, -1):
        a += [f'         L     1,PTR{i:02d}',
              '         LTR   1,1',
              f'         BZ    Q0SK{i:02d}',
              '         FREEMAIN R,LV=1024,A=(1)',
              f'         XC    PTR{i:02d}(4),PTR{i:02d}',
              '         L     3,NFREE',
              '         LA    3,1(3)',
              '         ST    3,NFREE',
              f'Q0SK{i:02d}   DS    0H']
    a += ['         LA    15,8',
          '         B     Q0TRET',
          "Q0TERR   WTO   'Q0 NATIVE RECORD VERIFICATION FAILED'",
          '         LA    15,8',
          'Q0TRET   L     13,4(13)',
          '         LM    14,12,12(13)',
          '         BR    14',
          '         LTORG',
          '* R1 -> 8-BYTE PUBLIC FINISH/STOP BLOCK; R15 RETURN CODE.',
          'Q0TFIN   DS    0H',
          '         STM   14,12,12(13)',
          '         LR    12,15',
          '         USING Q0TFIN,12',
          '         LA    10,4095(12)',
          '         LA    10,1(10)',
          '         USING Q0TFIN+4096,10',
          '         LA    11,FSAVE',
          '         ST    13,4(11)',
          '         ST    11,8(13)',
          '         LR    13,11',
          '         L     3,0(1)',
          '         ST    3,WHY',
          '         LTR   3,3',
          '         BM    Q0TBAD',
          "         C     3,=F'1'",
          '         BH    Q0TBAD',
          '         L     3,NOPEN',
          "         C     3,=F'16'",
          '         BNE   Q0TBAD',
          '         L     3,NALLOC',
          "         C     3,=F'16'",
          '         BNE   Q0TBAD']
    for i in range(COUNT-1, -1, -1):
        a += [f'         CLOSE (DC{i:02d})',
              '         L     3,NCLOSE',
              '         LA    3,1(3)',
              '         ST    3,NCLOSE']
    for i in range(COUNT-1, -1, -1):
        a += [f'         L     1,PTR{i:02d}',
              '         LTR   1,1',
              '         BZ    Q0TBAD',
              '         FREEMAIN R,LV=1024,A=(1)',
              f'         XC    PTR{i:02d}(4),PTR{i:02d}',
              '         L     3,NFREE',
              '         LA    3,1(3)',
              '         ST    3,NFREE']
    a += ['         L     3,NCLOSE',
          "         C     3,=F'16'",
          '         BNE   Q0TBAD',
          '         C     3,NFREE',
          '         BNE   Q0TBAD',
          '         L     3,WHY',
          '         LTR   3,3',
          '         BNZ   Q0TSTOP',
          "         WTO   'Q0 FINALIZER FINISH 16 CLOSE FREE PASS'",
          '         B     Q0TGOOD',
          "Q0TSTOP  WTO   'Q0 FINALIZER STOP 16 CLOSE FREE PASS'",
          'Q0TGOOD  SR    15,15',
          '         B     Q0TFRET',
          "Q0TBAD   WTO   'Q0 FINALIZER BAD STATE'",
          '         LA    15,8',
          'Q0TFRET  ST    15,FRESULT',
          '         L     13,4(13)',
          '         LM    14,12,12(13)',
          '         L     15,FRESULT',
          '         BR    14',
          '         DS    0F',
          'ISAVE    DS    18F',
          'FSAVE    DS    18F',
          "WHY      DC    F'0'",
          "FRESULT  DC    F'0'",
          'PTRS     DS    0F']
    for i in range(COUNT):
        a.append(f"PTR{i:02d}    DC    F'0'")
    a += ["NALLOC   DC    F'0'",
          "NFREE    DC    F'0'",
          "NOPEN    DC    F'0'",
          "NCLOSE   DC    F'0'"]
    for i in range(COUNT):
        a.append(f'DC{i:02d}     DCB   DDNAME=Q{i:02d},DSORG=PS,MACRF=GM,EODAD=Q0TERR')
    a += ['         LTORG', '         END']
    return '\n'.join(a) + '\n'


def checked(cards):
    for n, c in enumerate(cards, 1):
        if not c.isascii() or len(c) > 71 or '\t' in c:
            raise ValueError(f'bad IFOX/JCL card {n}: {c!r}')


def deck(profile, generated, jobcard, objdsn):
    job, region = PROFILES[profile]
    if not jobcard or not re.match(r'^//'+job+r'\s+JOB\b', jobcard[0]):
        raise ValueError('invalid padded JOB card')
    q = load(WRITER, 'q0_writer')
    base = q.harness()
    t = load(TRAIL, 'q0_native')
    writer = q.make_source(COUNT, False)
    # application_source returns a list of complete IFOX cards, while
    # the established Q.0 asm_step adapter accepts source text.
    app = '\n'.join(t.application_source(generated)) + '\n'
    ext, reg = extension(), registry()
    for source in (writer, app, ext, reg):
        checked(source.splitlines())
    cards = [*jobcard,
             '//* Q.0 TEMPORARY NATIVE 16-DCB / REG FINALIZER TEST',
             *base.asm_step('ASMWR', 'Q0WOBJ', writer),
             *base.asm_step('ASMA', 'Q0AOBJ', app),
             *base.asm_step('ASMT', 'Q0TOBJ', ext),
             *base.asm_step('ASMG', 'Q0GOBJ', reg),
             *base.link_step('LKWR', 'Q0WOBJ', 'Q0WMOD',
                             'Q0WRITER', 'Q0HNW', 'ASMWR'),
             '//LKED     EXEC PGM=IEWL,REGION=256K,',
             "//             PARM='NCAL,LIST,XREF,MAP',",
             '//             COND=(0,NE)',
             f'//OBJ      DD  DSN={objdsn},DISP=SHR',
             '//SYSLIN   DD  DSN=&&Q0AOBJ,DISP=(OLD,DELETE)',
             '//         DD  DSN=&&Q0TOBJ,DISP=(OLD,DELETE)',
             '//         DD  DSN=&&Q0GOBJ,DISP=(OLD,DELETE)',
             '//         DD  *',
             ' INCLUDE OBJ(BCPLMAIN)',
             ' INCLUDE OBJ(BCPLRGS)',
             ' INCLUDE OBJ(BCPLIO)',
             ' INCLUDE OBJ(BCPLMEM)',
             ' INCLUDE OBJ(BCPLBYTE)',
             ' INCLUDE OBJ(BCPLAPT)',
             ' INCLUDE OBJ(BLIB)',
             ' ENTRY R0APP',
             f' NAME {job}(R)',
             '/*',
             f'//SYSLMOD  DD  DSN=&&Q0NLOAD({job}),UNIT=SYSDA,',
             '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
             '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
             '//SYSPRINT DD  SYSOUT=*',
             '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,',
             '//             TIME=(,2),COND=(0,NE)']
    for i in range(COUNT):
        cards += [f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d},DISP=(NEW,PASS),',
                  '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',
                  '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)']
    cards += ['//SYSUDUMP DD  SYSOUT=*',
              f'//GO       EXEC PGM=*.LKED.SYSLMOD,REGION={region}K,',
              '//             TIME=(,2),COND=(0,NE)']
    for i in range(COUNT):
        cards.append(f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d},DISP=(OLD,DELETE)')
    cards += ['//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
              '//             BLKSIZE=132)',
              '//SYSUDUMP DD  SYSOUT=*', '//']
    checked(cards)
    if cards.count('/*') != 6:
        raise ValueError('unexpected IFOX/IEWL stream count')
    for i in range(COUNT):
        if sum(f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d}' in c
               for c in cards) != 2:
            raise ValueError('QSAM temporary allocation mismatch')
    if any('DISP=MOD' in c or 'CATLG' in c for c in cards):
        raise ValueError('persistent MVS output forbidden')
    return '\n'.join(cards) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=PROFILES)
    p.add_argument('--generated', type=Path)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    job, _ = PROFILES[args.profile]
    t = load(TRAIL, 'q0_trailer')
    if args.check:
        generated = t.sample_generated()
        jobcard = [f"//{job:<8} JOB (BCPL),'Q0 NATIVE',CLASS=A"]
        objdsn = 'HERC02.BCPL.BOOT.OBJ'
    else:
        if args.generated is None:
            p.error('real generated native ASM required')
        generated = args.generated.read_bytes().decode('latin-1')
        core = t.load_core()
        cfg = core.load_config()
        spec = cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
                or spec.get('recfm') != 'FB' or int(spec.get('lrecl',0)) != 80):
            raise ValueError('BOOT_OBJ is not FB80 object PDS')
        objdsn = core.full_dsn(cfg, spec)
        jobcard = core.authenticated_job_card(
            cfg, job, 'Q0 NATIVE', redact_password=False)
    jcl = deck(args.profile, generated, jobcard, objdsn)
    if args.check:
        print(f'CHECK {job}: {len(jcl.splitlines())} cards; '
              'no credentials, no MVS writes')
        return
    WORK.mkdir(parents=True, exist_ok=True)
    dest = WORK / f'{args.profile}.jcl'
    dest.write_text(jcl, encoding='ascii', newline='\n')
    dest.chmod(0o600)
    print(f'Prepared temporary-only MVS job: {dest}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, UnicodeError) as e:
        raise SystemExit(f'Q.0 integrated generator FAILED: {e}')
