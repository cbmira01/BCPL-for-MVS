#!/usr/bin/env python3
"""Q.5 returned-CLOSE quarantine test-only ASMQ overlay; never submit JES.

Genuine QSAM CLOSE occurs first. If it succeeds, override the first Q00
handle's returned R15 exactly once to drive production QSCQUAR. This tests
our *reaction to an injected status*, NOT an actual MVS CLOSE failure.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q5'
BASELINE = HERE / 'bcplqsam.asm'
FIXTURE = HERE / 'test-q5-returned-close.bcpl'
GENERATED = WORK / 'returned-close-generated.asm'
TARGET = WORK / 'q5rcclos.jcl'
JOB = 'Q5RCCLOS'

# Full exact baseline anchors: fail closed on any production-source change.
CLOSE = (
    'QSCEXEC  ST    2,QSCDCB\n'
    '         CLOSE ((2))\n'
    '* Q.1 PROVISIONAL RETURNED-CLOSE RULE; MVS GATE STILL OPEN.\n'
)
CLOSE_NEW = (
    'QSCEXEC  ST    2,QSCDCB\n'
    '         CLOSE ((2))\n'
    '* TEST ONLY: OVERRIDE ONE SUCCESSFUL Q00 CLOSE RETURN.\n'
    '* R15 NONZERO FROM MVS MUST NOT BE ALTERED OR CLASSIFIED.\n'
    '         LTR   15,15\n'
    '         BNZ   Q5CNORM\n'
    '         L     4,QSCCUR\n'
    "         CLC   4(4,4),=F'1'\n"
    '         BNE   Q5CNORM\n'
    "         CLC   Q5CONCE(4),=F'0'\n"
    '         BNE   Q5CNORM\n'
    '         LA    0,1\n'
    '         ST    0,Q5CONCE\n'
    '         LA    15,4\n'
    'Q5CNORM  DS    0H\n'
    '* Q.1 PROVISIONAL RETURNED-CLOSE RULE; MVS GATE STILL OPEN.\n'
)
QUAR = (
    '         L     0,QSQUAR\n'
    "         A     0,=F'1'\n"
    '         ST    0,QSQUAR\n'
    "QSCBAD   L     15,=F'-14'\n"
)
QUAR_NEW = (
    '         L     0,QSQUAR\n'
    "         A     0,=F'1'\n"
    '         ST    0,QSQUAR\n'
    '* E: INJECTION=1, LIVE=2, DCB=2, STAGE=2.\n'
    '         LA    1,Q5CONCE\n'
    '         SR    0,0\n'
    '         L     15,=A(QFPROBE)\n'
    '         BALR  14,15\n'
    "QSCBAD   L     15,=F'-14'\n"
)
SUCCESS_CLOSE = (
    '         ST    0,QSLIVE\n'
    '         SR    15,15\n'
    '         B     QSCRET\n'
)
SUCCESS_CLOSE_NEW = (
    '         ST    0,QSLIVE\n'
    '* L: QUAR=1, LIVE=1, DCB=1, STAGE=1, FINALIZER-STAT=0.\n'
    "         CLC   Q5CONCE(4),=F'1'\n"
    '         BNE   Q5CSKIP\n'
    '         LA    0,1\n'
    '         LA    1,Q5CONCE\n'
    '         L     15,=A(QFPROBE)\n'
    '         BALR  14,15\n'
    'Q5CSKIP  SR    15,15\n'
    '         B     QSCRET\n'
)
FINALIZER = 'QFEXIT   L     15,QFSTAT\n'
FINALIZER_NEW = (
    '* X: QUAR=1, LIVE=1, DCB=1, STAGE=1, STATUS=8.\n'
    'QFEXIT   LA    0,2\n'
    '         LA    1,Q5CONCE\n'
    '         L     15,=A(QFPROBE)\n'
    '         BALR  14,15\n'
    '         L     15,QFSTAT\n'
)
STATE = "QSCDCB   DC    F'0'\n"
STATE_NEW = STATE + "Q5CONCE  DC    F'0'\n"


def loader(name: str):
    path = HERE / name
    spec = importlib.util.spec_from_file_location(
        'q5returned_' + name.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('required helper unavailable: ' + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def once(text: str, original: str, replacement: str) -> str:
    if text.count(original) != 1:
        raise ValueError('missing or duplicate assembler anchor: ' + original[:65])
    return text.replace(original, replacement, 1)


def validate_cards(source: str) -> None:
    if not source.endswith('\n'):
        raise ValueError('missing final newline')
    for n, line in enumerate(source.splitlines(), 1):
        if not line.isascii() or '\t' in line or len(line) > 71:
            raise ValueError(f'invalid IFOX card {n}: {line!r}')


def probe_source() -> str:
    diag = loader('prepare-q1-finalizer-diagnostic.py')
    probe = diag.PROBE
    if probe.count('Q1F:') != 3 or probe.count('L     6,=A(QFCOUNT)') != 1:
        raise ValueError('unexpected existing Q.1 diagnostic source')
    probe = probe.replace('Q1F:', 'Q5C:')
    probe = probe.replace('L     6,=A(QFCOUNT)', 'L     6,=A(QSQUAR)')
    probe = probe.replace(
        '* Q.1 TEST-ONLY FINISH DIAGNOSTIC. NO API, REGISTRY OR CORE CHANGE.',
        '* Q.5 TEST-ONLY RETURNED-CLOSE STATUS INJECTION. NO CORE CHANGE.')
    return probe


def instrument_asm(baseline: str, probe: str | None = None) -> str:
    validate_cards(baseline)
    if 'Q5CONCE' in baseline or 'Q5C:E:' in baseline or 'QFPROBE  CSECT' in baseline:
        raise ValueError('test-only CLOSE overlay already installed')
    for original, updated in (
        (CLOSE, CLOSE_NEW), (QUAR, QUAR_NEW),
        (SUCCESS_CLOSE, SUCCESS_CLOSE_NEW),
        (FINALIZER, FINALIZER_NEW), (STATE, STATE_NEW),
    ):
        baseline = once(baseline, original, updated)
    baseline = once(baseline, 'QSMCTRL  CSECT\n',
                    (probe if probe is not None else probe_source())
                    + 'QSMCTRL  CSECT\n')
    validate_cards(baseline)
    if baseline.count('         L     15,=A(QFPROBE)') != 3:
        raise ValueError('expected exactly three Q5C diagnostic calls')
    if baseline.count('         CLOSE ((2))') != 1:
        raise ValueError('native CLOSE macro missing or duplicated')
    for name in ('Q5C:E:', 'Q5C:L:', 'Q5C:X:'):
        if baseline.count(name) != 1:
            raise ValueError('missing or duplicate WTO probe: ' + name)
    if 'Q5CNORM  DS    0H\n' not in baseline or "Q5CONCE  DC    F'0'\n" not in baseline:
        raise ValueError('one-shot status injection not generated')
    return baseline


def instrument_deck(template: str, baseline: str) -> str:
    campaign = loader('prepare-q1-campaign.py')
    original = template.splitlines()
    campaign.verify(original, 'Q16FIN', 'finish')
    start, end = campaign.source_span(original, 'ASMQ')
    if original[start:end] != baseline.splitlines():
        raise ValueError('ASMQ source is not current controlled BCPLQSAM')
    after = original.copy()
    after[start:end] = instrument_asm(baseline).splitlines()
    after[0] = once(after[0], '//Q16FIN ', '//Q5RCCLOS ')
    campaign.replace_one(after, ' NAME Q16FIN(R)', ' NAME Q5RCCLOS(R)')
    campaign.replace_one(after, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RCCLOS),')
    result = campaign.verify(after, JOB, 'finish')
    restored = after.copy()
    x, y = campaign.source_span(restored, 'ASMQ')
    restored[x:y] = baseline.splitlines()
    restored[0] = once(restored[0], '//Q5RCCLOS ', '//Q16FIN ')
    campaign.replace_one(restored, ' NAME Q5RCCLOS(R)', ' NAME Q16FIN(R)')
    campaign.replace_one(restored, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RCCLOS),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),')
    if restored != original:
        raise ValueError('changes escaped temporary ASMQ and JCL identity')
    return result


def require_fixture() -> None:
    fixture = FIXTURE.read_text('ascii')
    if not fixture.endswith('    FINISH\n$)1\n'):
        raise ValueError('test must end in explicit FINISH')
    for required in ('STOP(12)', 'QSAMSVC(4,Q,R) NE -14',
                     'QSAMSVC(4,Q,R) NE -7', 'QSAMSVC(5,Q,R) NE -7',
                     'QSAMSVC(2,Q,R) NE 0', 'QSAMSVC(4,Q,R) NE 0',
                     'BCPLQSAM Q5 CLOSE QUARANTINE PASS'):
        if required not in fixture:
            raise ValueError('BCPL assertion/record missing: ' + required)


def check() -> None:
    """Synthetic Q16FIN JCL and three damaged-source rejection cases."""
    require_fixture()
    diag = loader('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    sample = campaign.module('prepare-q1-query.py').time_helper().trailer_helper().sample_generated()
    source = BASELINE.read_text('ascii')
    template = campaign.make_deck(
        'finish', sample, ["//Q16FIN JOB (BCPL),'Q5 CLOSE CHECK',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    instrumented = instrument_deck(template, source)
    if not instrumented.startswith('//Q5RCCLOS ') or 'Q5C:X:' not in instrumented:
        raise ValueError('synthetic JCL identity/probe missing')
    for bad in (
        source.replace(CLOSE, 'QSCEXEC  ST    2,QSCDCB\n', 1),
        source.replace(STATE, '', 1),
        source.replace(FINALIZER, 'QFEXIT   L     15,QFBAD\n', 1),
    ):
        if bad == source:
            raise ValueError('test cannot construct damaged baseline')
        try:
            instrument_asm(bad)
        except ValueError:
            pass
        else:
            raise ValueError('tampered assembler was accepted')
    print('PASS: returned-CLOSE synthetic JCL:', len(instrumented.splitlines()),
          'cards; 3 negative baseline tests; no JES')


def prepare() -> None:
    """Only after independent resident compiler evidence has been accepted."""
    require_fixture()
    if TARGET.exists() or TARGET.is_symlink():
        raise ValueError('one-shot Q5RCCLOS JCL already exists')
    evidence = WORK / 'q5rccomp-attempt'
    if evidence.is_symlink() or not evidence.is_dir():
        raise ValueError('native Q5RCCOMP compiler evidence missing')
    if (evidence / 'compile.rc').read_text('ascii').strip() != '0':
        raise ValueError('compiler step did not succeed')
    summary = (evidence / 'summary.txt').read_text('utf-8', errors='replace')
    if not re.search(r'^JOB\s+\d+\s+Q5RCCOMP\s*$', summary, re.M):
        raise ValueError('wrong compiler JOB identity')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise ValueError('compiler JES result not successful')
    if not re.search(r'^COMP\s+ICINT19\s+RC=0000\s*$', summary, re.M):
        raise ValueError('native compiler COMP not RC0000')
    record = (evidence / 'source.sha256').read_text('ascii').split()
    if len(record) < 1 or record[0] != hashlib.sha256(FIXTURE.read_bytes()).hexdigest():
        raise ValueError('compiler input does not match new BCPL fixture')
    code_path = GENERATED.resolve()
    if GENERATED.is_symlink() or code_path.parent != WORK.resolve() or not code_path.is_file():
        raise ValueError('compiled output must be new Q.5 workarea file')
    generated = GENERATED.read_bytes()
    output_record = (evidence / 'assembler.sha256').read_text('ascii').split()
    if not output_record or output_record[0] != hashlib.sha256(generated).hexdigest():
        raise ValueError('native compiler assembler digest mismatch')
    if b' ENTRY R0APP' not in generated or not (100 <= len(generated.splitlines()) <= 500):
        raise ValueError('unexpected generated CG370 assembler format')
    query = loader('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    obj = config['datasets']['BOOT_OBJ']
    if obj.get('content_type') != 'object' or obj.get('dsorg') != 'PO' or \
            obj.get('recfm') != 'FB' or int(obj.get('lrecl', 0)) != 80:
        raise ValueError('unapproved BOOT_OBJ input library')
    jobcard = core.authenticated_job_card(
        config, 'Q16FIN', 'Q5 CLOSE QUARANTINE', redact_password=False)
    campaign = loader('prepare-q1-campaign.py')
    template = campaign.make_deck(
        'finish', generated.decode('latin-1'), jobcard,
        core.full_dsn(config, obj))
    result = instrument_deck(template, BASELINE.read_text('ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(TARGET, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
        out.write(result)
    print('PREPARED ONLY:', TARGET, 'cards', len(result.splitlines()))
    print('SHA-256:', hashlib.sha256(result.encode('ascii')).hexdigest())
    print('No JES submission or installed datasets modified')


def main() -> None:
    arg = argparse.ArgumentParser(description=__doc__)
    mode = arg.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--prepare', action='store_true')
    opt = arg.parse_args()
    if opt.check:
        check()
    else:
        prepare()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError, AssertionError) as exc:
        raise SystemExit('Q5RCCLOS preparation FAILED: ' + str(exc))
