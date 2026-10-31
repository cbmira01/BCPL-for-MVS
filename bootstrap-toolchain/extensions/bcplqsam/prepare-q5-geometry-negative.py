#!/usr/bin/env python3
"""Prepare test-only Q.5 geometry-negative JCL; never submit JES.

Reuse the established Q16FIN full 16-DD writer and native source-selected
BCEX/BCRG linkage. Instrument ASMQ only to count real OPEN macro attempts;
rejected DDs must be refused by the untouched production preflight.
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
FIXTURE = HERE / 'test-q5-geometry-negative.bcpl'
GENERATED = WORK / 'geometry-negative-generated.asm'
TARGET = WORK / 'q5geom.jcl'
JOB = 'Q5GEOM'

OPEN = (
    '         BE    QCOPENIN\n'
    '         OPEN  ((2),(OUTPUT))\n'
    '         B     QCOPENCK\n'
    'QCOPENIN OPEN  ((2),(INPUT))\n'
)
OPEN_NEW = (
    '         BE    QCOPENIN\n'
    '         L     0,Q5GOPEN\n'
    "         A     0,=F'1'\n"
    '         ST    0,Q5GOPEN\n'
    '         OPEN  ((2),(OUTPUT))\n'
    '         B     QCOPENCK\n'
    'QCOPENIN L     0,Q5GOPEN\n'
    "         A     0,=F'1'\n"
    '         ST    0,Q5GOPEN\n'
    '         OPEN  ((2),(INPUT))\n'
)
STATE = "QSQUAR   DC    F'0'\n"
STATE_NEW = STATE + "Q5GOPEN  DC    F'0'\n"
EXIT = 'QFEXIT   L     15,QFSTAT\n'
EXIT_NEW = (
    '* TEST-ONLY FINAL TRACE: OPEN COUNT, LIVE, DCBS, STAGES, STATUS.\n'
    'QFEXIT   LA    0,2\n'
    '         L     1,=A(Q5GOPEN)\n'
    '         L     15,=A(QFPROBE)\n'
    '         BALR  14,15\n'
    '         L     15,QFSTAT\n'
)
Q01 = '//Q01      DD  DSN=&&Q1H01,DISP=(OLD,DELETE),'
Q15 = '//Q15      DD  DSN=&&Q1H15,DISP=(OLD,DELETE),'
DCB = '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)'
EXTRAS = [
    '//QBAD     DD  DSN=&&Q5BAD,DISP=(NEW,DELETE),',
    '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
    '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)',
    '//QBIG     DD  DSN=&&Q5BIG,DISP=(NEW,DELETE),',
    '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
    '//             DCB=(RECFM=F,LRECL=1025,BLKSIZE=1025)',
]


def loader(filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(
        'q5geom_' + filename.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('required repository helper missing: ' + filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError('missing or duplicate production anchor: ' + old[:55])
    return source.replace(old, new, 1)


def card_check(source: str) -> None:
    if not source.endswith('\n'):
        raise ValueError('missing final newline')
    for n, line in enumerate(source.splitlines(), 1):
        if not line.isascii() or '\t' in line or len(line) > 71:
            raise ValueError(f'invalid 71-column card {n}: {line!r}')


def probe_source() -> str:
    original = loader('prepare-q1-finalizer-diagnostic.py').PROBE
    if original.count('Q1F:') != 3 or original.count('L     6,=A(QFCOUNT)') != 1:
        raise ValueError('unexpected established QFPROBE assembler')
    return original.replace('Q1F:', 'Q5G:').replace(
        'L     6,=A(QFCOUNT)', 'L     6,=A(Q5GOPEN)').replace(
        '* Q.1 TEST-ONLY FINISH DIAGNOSTIC. NO API, REGISTRY OR CORE CHANGE.',
        '* Q.5 TEST-ONLY GEOMETRY OPEN COUNT. NO PRODUCTION CHANGE.')


def instrument_asm(source: str, probe: str | None = None) -> str:
    card_check(source)
    if 'Q5GOPEN' in source or 'Q5G:X:' in source or 'QFPROBE  CSECT' in source:
        raise ValueError('test overlay already present')
    source = replace_once(source, OPEN, OPEN_NEW)
    source = replace_once(source, STATE, STATE_NEW)
    source = replace_once(source, EXIT, EXIT_NEW)
    source = replace_once(source, 'QSMCTRL  CSECT\n',
                          (probe if probe is not None else probe_source())
                          + 'QSMCTRL  CSECT\n')
    card_check(source)
    if source.count('         OPEN  ((2),(OUTPUT))') != 1 or \
       source.count('         OPEN  ((2),(INPUT))') != 1 or \
       source.count('ST    0,Q5GOPEN') != 2 or \
       source.count('L     15,=A(QFPROBE)') != 1 or \
       source.count('Q5G:X:') != 1:
        raise ValueError('unexpected instrumented OPEN/finalizer structure')
    return source


def deck_rows(template: str, baseline: str, campaign, probe: str | None = None) -> list[str]:
    """Modify only source-selected ASMQ, identity and three GO DD cards."""
    original = template.splitlines()
    campaign.verify(original, 'Q16FIN', 'finish')
    start, end = campaign.source_span(original, 'ASMQ')
    if original[start:end] != baseline.splitlines():
        raise ValueError('ASMQ differs from controlled production source')
    rows = original.copy()
    rows[start:end] = instrument_asm(baseline, probe).splitlines()
    if not rows[0].startswith('//Q16FIN JOB '):
        raise ValueError('unexpected original JOB card')
    rows[0] = '//Q5GEOM' + rows[0][8:]
    campaign.replace_one(rows, ' NAME Q16FIN(R)', ' NAME Q5GEOM(R)')
    campaign.replace_one(rows, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5GEOM),')
    if rows.count(Q01) != 1 or rows.count(Q15) != 1:
        raise ValueError('required GO reader DD not unique')
    q01 = rows.index(Q01)
    if rows[q01 + 1] != DCB:
        raise ValueError('Q01 lacks controlled original GO DCB')
    del rows[q01 + 1]
    q15 = rows.index(Q15)
    if rows[q15 + 1] != DCB:
        raise ValueError('Q15 controlled GO DCB missing')
    rows[q15 + 2:q15 + 2] = EXTRAS
    out = '\n'.join(rows) + '\n'
    card_check(out)
    if any(x in out for x in ('DISP=MOD', 'CATLG', '//EXTLIB')):
        raise ValueError('unsafe permanent-operation JCL')
    if rows.count('//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)') != 1 or \
       rows.count('//             DCB=(RECFM=F,LRECL=1025,BLKSIZE=1025)') != 1:
        raise ValueError('negative DD geometry not unique')
    # Restore the source, job identities, extra DDs and the one absent DCB;
    # any changes to writer, unrelated reader DD, link-edit, or runtime fail.
    restore = rows.copy()
    x = restore.index(EXTRAS[0])
    if restore[x:x+len(EXTRAS)] != EXTRAS:
        raise ValueError('extra DD block was changed')
    del restore[x:x+len(EXTRAS)]
    restore.insert(restore.index(Q01) + 1, DCB)
    x, y = campaign.source_span(restore, 'ASMQ')
    restore[x:y] = baseline.splitlines()
    restore[0] = original[0]
    campaign.replace_one(restore, ' NAME Q5GEOM(R)', ' NAME Q16FIN(R)')
    campaign.replace_one(restore, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5GEOM),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),')
    if restore != original:
        raise ValueError('unexpected JCL change outside approved scope')
    # Strong enough to reject malformed source, JCL card edits and silently
    # missing tracked DDs. Validates the exact restored production deck.
    campaign.verify(restore, 'Q16FIN', 'finish')
    return rows


def instrument_deck(template: str, baseline: str, campaign, probe=None) -> str:
    return '\n'.join(deck_rows(template, baseline, campaign, probe)) + '\n'


def require_fixture() -> None:
    source = FIXTURE.read_text('ascii')
    if not source.endswith('    FINISH\n$)1\n'):
        raise ValueError('BCPL fixture must finish normally')
    for clause in ('"QBAD"', '"QBIG"', '"Q01"', '"Q00"',
                   'QSAMSVC(1,Q,R) NE -6', 'R!0 NE -6 | R!1 NE 0',
                   'QSAMSVC(2,Q,R) NE 0', 'QSAMSVC(4,Q,R) NE 0',
                   'BCPLQSAM Q5 GEOMETRY NEGATIVE PASS', 'STOP(12)'):
        if clause not in source:
            raise ValueError('missing BCPL test requirement: ' + clause)
    if source.count('QSAMSVC(1,Q,R) NE -6') != 3:
        raise ValueError('require exactly three OPEN failure assertions')


def validated_compiler_source(raw: bytes, adapter) -> str:
    """Raw Cambridge CG370 is an unnamed CSECT, not ENTRY R0APP."""
    if not (100 <= len(raw.splitlines()) <= 550):
        raise ValueError('unexpected CG370 code length')
    source = raw.decode('latin-1')
    adapted = adapter(source)
    if adapted.count('         ENTRY R0APP') != 1:
        raise ValueError('CG370 adapter did not produce one application entry')
    return source


def make_deck(generated: str, jobcard: list[str], obj: str, baseline=None) -> str:
    campaign = loader('prepare-q1-campaign.py')
    query = loader('prepare-q1-query.py')
    helper = query.time_helper().trailer_helper()
    generated = validated_compiler_source(generated.encode('latin-1'),
                                          helper.application_source)
    source = baseline if baseline is not None else BASELINE.read_text('ascii')
    template = campaign.make_deck('finish', generated, jobcard, obj)
    return instrument_deck(template, source, campaign)


def check() -> None:
    require_fixture()
    campaign = loader('prepare-q1-campaign.py')
    query = loader('prepare-q1-query.py')
    helper = query.time_helper().trailer_helper()
    generated = helper.sample_generated()
    # The synthetic helper has fewer than 100 lines, but is suitable to
    # the accepted adapter; pad with assembler comments for this guard.
    lines = generated.splitlines()
    lines[-1:-1] = ['* Q5G SYNTHETIC CG370'] * max(0, 100-len(lines))
    generated = '\n'.join(lines) + '\n'
    template = campaign.make_deck('finish', generated,
        ["//Q16FIN JOB (BCPL),'Q5 GEOM CHECK',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    source = BASELINE.read_text('ascii')
    out = instrument_deck(template, source, campaign)
    if not out.startswith('//Q5GEOM JOB ') or 'Q5G:X:' not in out:
        raise ValueError('synthetic job identity/probe absent')
    for broken in (source.replace(OPEN, '', 1),
                   source.replace(STATE, '', 1),
                   source.replace(EXIT, '', 1)):
        try:
            instrument_asm(broken)
        except ValueError:
            continue
        raise ValueError('missing assembler anchor was not rejected')
    print('PASS: Q5 geometry-negative synthetic JCL', len(out.splitlines()),
          'cards; 3 corrupt assembler variants rejected; no JES')


def prepare() -> None:
    require_fixture()
    if TARGET.exists() or TARGET.is_symlink():
        raise ValueError('one-shot Q5GEOM deck already exists')
    evidence = WORK / 'q5gcomp-attempt'
    if evidence.is_symlink() or not evidence.is_dir():
        raise ValueError('native Cambridge compiler evidence missing')
    for name in ('compile.rc', 'summary.rc', 'report.rc'):
        if (evidence / name).read_text('ascii').strip() != '0':
            raise ValueError('compiler evidence return nonzero: ' + name)
    summary = (evidence / 'summary.txt').read_text('utf-8',errors='replace')
    if not re.search(r'^JOB\s+\d+\s+Q5GCOMP\s*$', summary, re.M) or \
       not re.search(r'^COMP\s+ICINT19\s+RC=0000\s*$', summary, re.M) or \
       'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise ValueError('wrong or unsuccessful native compiler JOB')
    if (evidence / 'source.sha256').read_text('ascii').split()[0] != \
       hashlib.sha256(FIXTURE.read_bytes()).hexdigest():
        raise ValueError('BCPL fixture differs from compiled input')
    path = GENERATED.resolve()
    if GENERATED.is_symlink() or path.parent != WORK.resolve() or not path.is_file():
        raise ValueError('compiled assembler not a regular workarea source')
    raw = GENERATED.read_bytes()
    if (evidence / 'assembler.sha256').read_text('ascii').split()[0] != \
       hashlib.sha256(raw).hexdigest():
        raise ValueError('compiler source digest mismatch')
    query = loader('prepare-q1-query.py')
    helper = query.time_helper().trailer_helper()
    generated = validated_compiler_source(raw, helper.application_source)
    core = helper.load_core()
    config = core.load_config()
    obj = config['datasets']['BOOT_OBJ']
    if obj.get('content_type') != 'object' or obj.get('dsorg') != 'PO' or \
       obj.get('recfm') != 'FB' or int(obj.get('lrecl',0)) != 80:
        raise ValueError('BOOT_OBJ must be accepted FB80 object PDS')
    jobcard = core.authenticated_job_card(
        config, 'Q16FIN', 'Q5 GEOMETRY NEGATIVE', redact_password=False)
    content = make_deck(generated, jobcard, core.full_dsn(config, obj))
    WORK.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(TARGET, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as f:
        f.write(content)
    print('PREPARED ONLY:',TARGET,'cards',len(content.splitlines()))
    print('SHA-256:',hashlib.sha256(content.encode('ascii')).hexdigest())
    print('No JES submission or installed MVS datasets modified')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument('--check', action='store_true')
    exclusive.add_argument('--prepare', action='store_true')
    opts = parser.parse_args()
    if opts.check:
        check()
    else:
        prepare()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError, AssertionError) as exc:
        raise SystemExit('Q5 geometry-negative preparation FAILED: '+str(exc))
