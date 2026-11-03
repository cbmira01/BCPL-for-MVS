#!/usr/bin/env python3
"""Q.5: one real 1024-byte GETMAIN refusal inside BCPLQSAM.

Use JOB 8144's existing Cambridge-compiled rollback BCPL application.
The temporary ASMQ overlay saturates the 256K region by retaining real
1024-byte GETMAIN RC allocations before Q01's unchanged 1024-byte stage
GETMAIN. On return it releases test allocations, then uses production
QCSTFAIL/QCCLEAN/QSMCLS1. No permanent MVS dataset is modified.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'workarea/bcplqsam-q5'
BASELINE = HERE / 'bcplqsam.asm'
## The accepted JOB 8144 image is verified by prepare-q5-rollback-finish.
OUTPUT = WORK / 'q5rgm.jcl'
JOB = 'Q5RGM'

STAGE = ("         GETMAIN RC,LV=1024\n"
         "         LTR   15,15\n"
         "         BNZ   QCSTFAIL\n")
STAGE_TEST = """         CLC   QCNAME(8),=CL8'Q01'
         BNE   Q5RNEXT
         CLC   Q5RONCE(4),=F'0'
         BNE   Q5RNEXT
         LA    0,1
         ST    0,Q5RONCE
         BAL   14,Q5RFILL
Q5RNEXT  GETMAIN RC,LV=1024
         CLC   Q5RONCE(4),=F'1'
         BNE   Q5RPOST
         LA    0,2
         ST    0,Q5RONCE
         ST    15,Q5RSTRC
         ST    1,Q5RSTPTR
         BAL   14,Q5RFREE
* Issue runtime evidence ONLY if both genuine GETMAINs returned R15=4
* and every test-held 1024-byte allocation has been freed.
         CLC   Q5RFRC(4),=F'4'
         BNE   Q5RNOMSG
         CLC   Q5RSTRC(4),=F'4'
         BNE   Q5RNOMSG
         CLC   Q5RCNT(4),Q5RFREED
         BNE   Q5RNOMSG
         CLC   Q5RCNT(4),=F'0'
         BE    Q5RNOMSG
         WTO   'Q5RGM:REAL:GM1024-RC4:ALL-FREED'
Q5RNOMSG L     1,Q5RSTPTR
         L     15,Q5RSTRC
Q5RPOST  LTR   15,15
         BNZ   QCSTFAIL
"""
HELPERS = """* Q.5 TEST-ONLY bounded GETMAIN pressure. No synthetic error.
* Each 1024-byte block links to its predecessor in its first word.
Q5RFILL  ST    14,Q5RSAVE
Q5RFLOOP CLC   Q5RCNT(4),=F'512'
         BNL   Q5RLIMIT
         GETMAIN RC,LV=1024
         LTR   15,15
         BNZ   Q5RFEND
         L     0,Q5RHEAD
         ST    0,0(1)
         ST    1,Q5RHEAD
         L     0,Q5RCNT
         A     0,=F'1'
         ST    0,Q5RCNT
         B     Q5RFLOOP
Q5RLIMIT L     15,=F'-99'
Q5RFEND  ST    15,Q5RFRC
         L     14,Q5RSAVE
         BR    14
* Return test-held storage BEFORE invoking production rollback CLOSE.
Q5RFREE  ST    14,Q5RSAVE
Q5RFLP   L     1,Q5RHEAD
         LTR   1,1
         BZ    Q5RFDONE
         L     0,0(1)
         ST    0,Q5RHEAD
         FREEMAIN R,LV=1024,A=(1)
         L     0,Q5RFREED
         A     0,=F'1'
         ST    0,Q5RFREED
         B     Q5RFLP
Q5RFDONE L     14,Q5RSAVE
         BR    14
"""
DATA = """Q5RONCE  DC    F'0'
Q5RHEAD  DC    F'0'
Q5RCNT   DC    F'0'
Q5RFREED DC    F'0'
Q5RFRC   DC    F'0'
Q5RSTRC  DC    F'0'
Q5RSTPTR DC    F'0'
Q5RSAVE  DC    F'0'
"""


def module(name: str):
    spec = importlib.util.spec_from_file_location(
        'q5rgm_' + name.replace('-', '_'), HERE / name)
    if spec is None or spec.loader is None:
        raise ValueError('missing existing BCPLQSAM helper: ' + name)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def one(src: str, old: str, new: str) -> str:
    if src.count(old) != 1:
        raise ValueError('changed production anchor: ' + old[:45])
    return src.replace(old, new, 1)


def instrument(src: str) -> str:
    src = one(src, STAGE, STAGE_TEST)
    # Place helper instructions before QSMCORE's final LTORG so new
    # helper operands receive addressable literals. JOB 8153 IFO209.
    src = one(src, '         LTORG\n'
                   '* PRIVATE CORE FIELDS (NO OS-MODULE WRITE OWNERSHIP).\n',
              HELPERS + '         LTORG\n'
              '* PRIVATE CORE FIELDS (NO OS-MODULE WRITE OWNERSHIP).\n')
    src = one(src, "QCERRPRI DC   F'0'\n", "QCERRPRI DC   F'0'\n" + DATA)
    for i, row in enumerate(src.splitlines(), 1):
        if not row.isascii() or '\t' in row or len(row) > 71:
            raise ValueError(f'IFOX card {i} malformed: {row!r}')
    if src.count('GETMAIN RC,LV=1024') != 2:
        raise ValueError('expected the pressure and original stage GETMAIN')
    return src


def prepare() -> None:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise ValueError('Q5RGM one-shot deck already exists')
    # Reuse the accepted JOB 8144 verifier: original compiler JOB,
    # exact source digest, archived JES success and 311-line CODE image.
    # rollback-generated.asm belongs to failed JOB 8141 and is NOT input.
    finish = module('prepare-q5-rollback-finish.py')
    raw = finish.verified_compiler_code()
    campaign = module('prepare-q1-campaign.py')
    query = module('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
            or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('expected read-only FB80 BOOT_OBJ')
    jobcard = core.authenticated_job_card(
        config, 'Q16FIN', 'Q5 REAL GETMAIN', redact_password=False)
    original = campaign.make_deck('finish', raw.decode('latin-1'),
                                  jobcard, core.full_dsn(config, spec))
    rows = original.splitlines()
    start, end = campaign.source_span(rows, 'ASMQ')
    base = BASELINE.read_text('ascii')
    if rows[start:end] != base.splitlines():
        raise ValueError('native ASMQ source differs from GitHub baseline')
    rows[start:end] = instrument(base).splitlines()
    if not rows[0].startswith('//Q16FIN '):
        raise ValueError('unexpected JOB card')
    rows[0] = '//Q5RGM' + rows[0][8:]
    campaign.replace_one(rows, ' NAME Q16FIN(R)', ' NAME Q5RGM(R)')
    campaign.replace_one(rows,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RGM),')
    result = campaign.verify(rows, JOB, 'finish')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(OUTPUT, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(result)
    print('PREPARED:', OUTPUT, 'JCL cards', len(rows))
    print('SHA-256:', hashlib.sha256(result.encode('ascii')).hexdigest())
    print('MVS JES has not yet been submitted')


if __name__ == '__main__':
    try:
        prepare()
    except (OSError, ValueError, UnicodeError) as e:
        raise SystemExit('Q5RGM preparation failed: ' + str(e))
