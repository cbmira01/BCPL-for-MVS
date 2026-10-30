#!/usr/bin/env python3
"""Q.5 test-only OPEN rollback: one injected refusal, real QSAM CLOSE.

Generate temporary IFOX/IEWL/GO JCL only; never submit JES. A real
QSAM OPEN of Q01 succeeds first; the injected stage refusal skips
GETMAIN and enters production QCSTFAIL/QCCLEAN. Native CLOSE is real.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q5'
BASELINE = HERE / 'bcplqsam.asm'
FIXTURE = HERE / 'test-q5-open-rollback.bcpl'
GENERATED = WORK / 'rollback-generated.asm'
TARGET = WORK / 'q5rbopen.jcl'
JOB = 'Q5RBOPEN'

# Full source-controlled anchors: any competing source revision fails closed.
STAGE = '         GETMAIN RC,LV=1024\n'
STAGE_NEW = ("         CLC   QCNAME(8),=CL8'Q01'\n"
             "         BNE   Q5NOGM\n"
             "         CLC   Q5ONCE(4),=F'0'\n"
             "         BNE   Q5NOGM\n"
             "         LA    0,1\n"
             "         ST    0,Q5ONCE\n"
             "         L     1,=A(Q5REASN)\n"
             "         SR    0,0\n"
             "         L     15,=A(QFPROBE)\n"
             "         BALR  14,15\n"
             "         LA    15,4\n"
             "         B     QCSTFAIL\n"
             "Q5NOGM   GETMAIN RC,LV=1024\n")
CLEAN = ('         BALR  14,15\n'
         '         L     7,QCERRPRI\n')
CLEAN_NEW = ("         BALR  14,15\n"
             "         CLC   Q5ONCE(4),=F'1'\n"
             "         BNE   Q5RBDONE\n"
             "         LA    0,2\n"
             "         ST    0,Q5ONCE\n"
             "         L     6,=A(QFSTAT)\n"
             "         ST    15,0(6)\n"
             "         SR    0,0\n"
             "         LTR   15,15\n"
             "         BNZ   Q5RBSTAT\n"
             "         LA    0,1\n"
             "Q5RBSTAT L     6,=A(QFCOUNT)\n"
             "         ST    0,0(6)\n"
             "         L     1,=A(Q5REASN)\n"
             "         LA    0,1\n"
             "         L     15,=A(QFPROBE)\n"
             "         BALR  14,15\n"
             "Q5RBDONE L     7,QCERRPRI\n")
FIN_EXIT = 'QFEXIT   L     15,QFSTAT\n'
FIN_EXIT_NEW = ('QFEXIT   LA    0,2\n'
                '         L     15,=A(QFPROBE)\n'
                '         BALR  14,15\n'
                '         L     15,QFSTAT\n')
STATE = "QCERRPRI DC   F'0'\n"
STATE_NEW = STATE + "Q5ONCE   DC    F'0'\nQ5REASN  DC    F'1'\n"


def load(name: str):
    path = HERE / name
    spec = importlib.util.spec_from_file_location('q5rb_' + name.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('helper unavailable: ' + str(path))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def instrument_asm(source: str) -> str:
    diag = load('prepare-q1-finalizer-diagnostic.py')
    diag.validate_cards(source)
    if 'QFPROBE  CSECT' in source or 'Q5R:E:' in source:
        raise ValueError('already instrumented')
    # Rollback injection on Q01 ONLY, after genuine OPEN and geometry
    # validation, just before the 1024-byte private-stage GETMAIN.
    source = diag.replace_once(source, STAGE, STAGE_NEW)
    source = diag.replace_once(source,
                               'QCCLEAN  ST    7,QCERRPRI\n'
                               '         L     4,QCCUR\n'
                               '         L     15,=A(QSMCLS1)\n' + CLEAN,
                               'QCCLEAN  ST    7,QCERRPRI\n'
                               '         L     4,QCCUR\n'
                               '         L     15,=A(QSMCLS1)\n' + CLEAN_NEW)
    source = diag.replace_once(source, FIN_EXIT, FIN_EXIT_NEW)
    source = diag.replace_once(source, STATE, STATE_NEW)
    probe = diag.PROBE.replace('Q1F:', 'Q5R:')
    probe = probe.replace('* Q.1 TEST-ONLY FINISH DIAGNOSTIC. NO API, REGISTRY OR CORE CHANGE.',
                          '* Q.5 TEST-ONLY OPEN ROLLBACK PROBE. NO CORE CHANGE.')
    source = diag.replace_once(source, 'QSMCTRL  CSECT\n',
                               probe + 'QSMCTRL  CSECT\n')
    diag.validate_cards(source)
    if source.count('         L     15,=A(QFPROBE)') != 3:
        raise ValueError('expected exactly three diagnostic calls')
    for marker in ('Q5R:E:', 'Q5R:L:', 'Q5R:X:'):
        if source.count(marker) != 1:
            raise ValueError('missing/duplicate diagnostic WTO: ' + marker)
    return source


def instrument_deck(deck: str, baseline: str) -> str:
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    before = deck.splitlines()
    campaign.verify(before, 'Q16FIN', 'finish')
    start, stop = campaign.source_span(before, 'ASMQ')
    if before[start:stop] != baseline.splitlines():
        raise ValueError('ASMQ is not the exact current source')
    changed = before.copy()
    changed[start:stop] = instrument_asm(baseline).splitlines()
    changed[0] = diag.replace_once(changed[0], '//Q16FIN ', '//Q5RBOPEN ')
    campaign.replace_one(changed, ' NAME Q16FIN(R)', ' NAME Q5RBOPEN(R)')
    campaign.replace_one(changed,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBOPEN),')
    output = campaign.verify(changed, JOB, 'finish')
    restored = changed.copy()
    left, right = campaign.source_span(restored, 'ASMQ')
    restored[left:right] = baseline.splitlines()
    restored[0] = diag.replace_once(restored[0], '//Q5RBOPEN ', '//Q16FIN ')
    campaign.replace_one(restored, ' NAME Q5RBOPEN(R)', ' NAME Q16FIN(R)')
    campaign.replace_one(restored,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBOPEN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),')
    if restored != before or output.splitlines() != changed:
        raise ValueError('unexpected change outside test-only ASMQ/identity')
    return output


def check() -> None:
    if 'BCPLQSAM Q5 OPEN ROLLBACK PASS' not in FIXTURE.read_text('ascii'):
        raise ValueError('canonical BCPL test marker missing')
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    sample = campaign.module('prepare-q1-query.py').time_helper().trailer_helper().sample_generated()
    raw = BASELINE.read_text('ascii')
    deck = campaign.make_deck('finish', sample,
                              ["//Q16FIN JOB (BCPL),'Q5 CHECK',CLASS=A"],
                              'HERC02.BCPL.BOOT.OBJ')
    prepared = instrument_deck(deck, raw)
    if 'Q5RBOPEN' not in prepared or 'Q5R:E:' not in prepared:
        raise ValueError('generated diagnostic missing')
    for damaged in (
        raw.replace(STAGE, '         GETMAIN RC,LV=1020\n', 1),
        raw.replace(STATE, '', 1),
        raw.replace(FIN_EXIT, '', 1),
    ):
        if damaged == raw:
            raise ValueError('negative-case anchor missing')
        try:
            instrument_asm(damaged)
        except ValueError:
            pass
        else:
            raise ValueError('modified BCPLQSAM source was accepted')
    print('PASS: Q5RBOPEN synthetic instrumented deck:',
          len(prepared.splitlines()), 'cards; 3 negative source tests; no JES')


def prepare() -> None:
    path = GENERATED.resolve()
    if path.parent != WORK.resolve() or not path.is_file():
        raise ValueError('compiled BCPL must be under Q.5 workarea')
    if TARGET.exists():
        raise ValueError('output exists; refusing overwrite')
    query = load('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
            or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('unapproved BOOT_OBJ library')
    jobcard = core.authenticated_job_card(config, 'Q16FIN', 'Q5 ROLLBACK',
                                          redact_password=False)
    campaign = load('prepare-q1-campaign.py')
    original = campaign.make_deck('finish', path.read_bytes().decode('latin-1'),
                                  jobcard, core.full_dsn(config, spec))
    result = instrument_deck(original, BASELINE.read_text('ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    fd = os.open(TARGET, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
        out.write(result)
    print('PREPARED ONLY:', TARGET, 'cards', len(result.splitlines()))
    print('SHA-256:', hashlib.sha256(result.encode('ascii')).hexdigest())
    print('No JES submission or installed dataset modification')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    if args.check:
        check()
    else:
        prepare()


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError, AssertionError) as exc:
        raise SystemExit('Q5RBOPEN preparation FAILED: ' + str(exc))
