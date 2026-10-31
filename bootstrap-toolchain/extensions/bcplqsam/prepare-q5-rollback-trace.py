#!/usr/bin/env python3
"""Q.5 test-only trace of JOB 8142 S0C1. Prepare new Q5RBTRC, never submit.

Reuse JOB 8141's compiled BCPL and exact production BCPLQSAM source.
Do not modify/reuse the failed Q5RBOPEN deck or attempt marker.
Three new probe phases identify core execution after the rollback WTO:
P = post-cleanup, R = rollback-return, T = QSMCORE epilogue entry.
These are location markers, not assertions of a valid BCPL return.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

import importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q5'
OUTPUT = WORK / 'q5rbtrc.jcl'
COMPILED = WORK / 'rollback-generated.asm'
ORIGINAL_HEAD = '6edce7df7024973258cbaf8353209859a93daa29'
COMPILED_SHA256 = '7a36834df35a191f07b4d8113b6d493cec014840f8571ab3c9ebd314534eb721'

def load(filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(
        'q5trace_' + filename.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('helper not found: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise ValueError('missing/duplicate trace anchor: ' + before[:50])
    return text.replace(before, after, 1)

PROBE_DISPATCH = (
    "         C     0,=F'2'\n"
    "         BE    QFPEX\n"
    "         B     QFPDONE\n"
)
PROBE_DISPATCH_NEW = (
    "         C     0,=F'2'\n"
    "         BE    QFPEX\n"
    "         C     0,=F'3'\n"
    "         BE    Q5RPST\n"
    "         C     0,=F'4'\n"
    "         BE    Q5RRLL\n"
    "         C     0,=F'5'\n"
    "         BE    Q5RTRN\n"
    "         B     QFPDONE\n"
)
PROBE_RETURN = "QFPDONE  L     13,4(13)\n"
PROBE_RETURN_NEW = (
    "Q5RPST   WTO   MF=(E,Q5RPL)\n"
    "         B     QFPDONE\n"
    "Q5RRLL   WTO   MF=(E,Q5RRL)\n"
    "         B     QFPDONE\n"
    "Q5RTRN   WTO   MF=(E,Q5RTL)\n"
    "         B     QFPDONE\n"
    + PROBE_RETURN
)
PROBE_LIST = (
    "QFXL     WTO 'Q5R:X:00000000:00000000:00000000:00000000:00000000',MF=L\n"
)
PROBE_LIST_NEW = PROBE_LIST + (
    "Q5RPL    WTO 'Q5R:P:POST-CLEAN',MF=L\n"
    "Q5RRL    WTO 'Q5R:R:ROLL-RETURN',MF=L\n"
    "Q5RTL    WTO 'Q5R:T:CORE-EPILOGUE',MF=L\n"
)
AFTER_CLEAN = "Q5RBDONE L     7,QCERRPRI\n"
AFTER_CLEAN_NEW = (
    "Q5RBDONE LA    0,3\n"
    "         L     15,=A(QFPROBE)\n"
    "         BALR  14,15\n"
    "         L     7,QCERRPRI\n"
)
ROLL_RETURN = "QCROLLRT LR    15,7\n"
ROLL_RETURN_NEW = (
    "QCROLLRT LA    0,4\n"
    "         L     15,=A(QFPROBE)\n"
    "         BALR  14,15\n"
    "         LR    15,7\n"
)
CORE_RET = "QCRET    ST    15,QCSTATUS\n         L     13,4(13)\n"
CORE_RET_NEW = (
    "QCRET    ST    15,QCSTATUS\n"
    "         CLC   Q5ONCE(4),=F'2'\n"
    "         BNE   Q5RTRDN\n"
    "         LA    0,3\n"
    "         ST    0,Q5ONCE\n"
    "         LA    0,5\n"
    "         L     15,=A(QFPROBE)\n"
    "         BALR  14,15\n"
    "Q5RTRDN  L     13,4(13)\n"
)

def instrument_asm(baseline: str) -> str:
    prior = load('prepare-q5-open-rollback.py')
    diag = load('prepare-q1-finalizer-diagnostic.py')
    source = prior.instrument_asm(baseline)
    for a, b in (
        (PROBE_DISPATCH, PROBE_DISPATCH_NEW),
        (PROBE_RETURN, PROBE_RETURN_NEW),
        (PROBE_LIST, PROBE_LIST_NEW),
        (AFTER_CLEAN, AFTER_CLEAN_NEW),
        (ROLL_RETURN, ROLL_RETURN_NEW),
        (CORE_RET, CORE_RET_NEW),
    ):
        source = once(source, a, b)
    diag.validate_cards(source)
    for marker in ('Q5R:E:', 'Q5R:L:', 'Q5R:X:',
                   'Q5R:P:POST-CLEAN', 'Q5R:R:ROLL-RETURN',
                   'Q5R:T:CORE-EPILOGUE'):
        if source.count(marker) != 1:
            raise ValueError('trace marker not unique: ' + marker)
    if source.count('         L     15,=A(QFPROBE)') != 6:
        raise ValueError('expected six register-preserving probe calls')
    return source

def instrument_deck(deck: str, baseline: str) -> str:
    prior = load('prepare-q5-open-rollback.py')
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    before = prior.instrument_deck(deck, baseline).splitlines()
    campaign.verify(before, 'Q5RBOPEN', 'finish')
    a, b = campaign.source_span(before, 'ASMQ')
    if before[a:b] != prior.instrument_asm(baseline).splitlines():
        raise ValueError('original Q5RBOPEN overlay mismatch')
    after = before.copy()
    after[a:b] = instrument_asm(baseline).splitlines()
    after[0] = once(after[0], '//Q5RBOPEN ', '//Q5RBTRC ')
    campaign.replace_one(after, ' NAME Q5RBOPEN(R)', ' NAME Q5RBTRC(R)')
    campaign.replace_one(after,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBOPEN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBTRC),')
    output = campaign.verify(after, 'Q5RBTRC', 'finish')

    restored = after.copy()
    x, y = campaign.source_span(restored, 'ASMQ')
    restored[x:y] = prior.instrument_asm(baseline).splitlines()
    restored[0] = once(restored[0], '//Q5RBTRC ', '//Q5RBOPEN ')
    campaign.replace_one(restored, ' NAME Q5RBTRC(R)', ' NAME Q5RBOPEN(R)')
    campaign.replace_one(restored,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBTRC),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBOPEN),')
    if restored != before or output.splitlines() != after:
        raise ValueError('unexpected JCL differences beyond trace overlay')
    return output

def synthetic_check() -> None:
    prior = load('prepare-q5-open-rollback.py')
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    generated = campaign.module('prepare-q1-query.py').time_helper().trailer_helper().sample_generated()
    baseline = (HERE / 'bcplqsam.asm').read_text('ascii')
    original = campaign.make_deck('finish', generated,
                                  ["//Q16FIN JOB (BCPL),'Q5 TRACE',CLASS=A"],
                                  'HERC02.BCPL.BOOT.OBJ')
    result = instrument_deck(original, baseline)
    if not result.startswith('//Q5RBTRC '):
        raise ValueError('wrong trace job name')
    if 'Q5R:T:CORE-EPILOGUE' not in result:
        raise ValueError('new trace absent')
    cases = (
        baseline.replace('         GETMAIN RC,LV=1024\n',
                         '         GETMAIN RC,LV=1020\n', 1),
        baseline.replace('QCERRPRI DC   F\'0\'\n', '', 1),
        baseline.replace('QCRET    ST    15,QCSTATUS\n',
                         'QCRET    ST    15,QCBROKEN\n', 1),
    )
    for case in cases:
        if case == baseline:
            raise ValueError('negative-case anchor missing')
        try:
            instrument_asm(case)
        except ValueError:
            pass
        else:
            raise ValueError('tampered baseline accepted')
    print('PASS: Q5RBTRC synthetic JCL', len(result.splitlines()),
          'cards; 3 negative tests; no JES')

def prepare() -> None:
    evidence = WORK / 'q5rbcomp-attempt'
    if (evidence / 'source-head.txt').read_text('ascii').strip() != ORIGINAL_HEAD:
        raise ValueError('wrong source revision for retained compiled BCPL')
    if (evidence / 'compile.rc').read_text('ascii').strip() != '0':
        raise ValueError('compiler job not accepted')
    if COMPILED.is_symlink() or COMPILED.resolve().parent != WORK.resolve():
        raise ValueError('compiled source outside Q.5 workarea')
    code = COMPILED.read_bytes()
    if hashlib.sha256(code).hexdigest() != COMPILED_SHA256:
        raise ValueError('retained JOB 8141 compiler output digest mismatch')
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise ValueError('Q5RBTRC output already exists; no overwrite')
    query = load('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
            or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('unapproved BOOT_OBJ library')
    card = core.authenticated_job_card(config, 'Q16FIN',
                                        'Q5 ROLLBACK TRACE',
                                        redact_password=False)
    campaign = load('prepare-q1-campaign.py')
    original = campaign.make_deck('finish', code.decode('latin-1'),
                                  card, core.full_dsn(config, spec))
    result = instrument_deck(original, (HERE / 'bcplqsam.asm').read_text('ascii'))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(OUTPUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(result)
    print('PREPARED ONLY:', OUTPUT, 'cards', len(result.splitlines()))
    print('SHA-256:', hashlib.sha256(result.encode('ascii')).hexdigest())
    print('No JES submission or installed dataset modification')

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--prepare', action='store_true')
    args = p.parse_args()
    if args.check:
        synthetic_check()
    else:
        prepare()

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError, AssertionError) as exc:
        raise SystemExit('Q5RBTRC preparation FAILED: ' + str(exc))
