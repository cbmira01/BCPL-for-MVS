#!/usr/bin/env python3
"""Prepare Q5RBFIN from corrected, native-compiled Q.5 BCPL; NEVER submit JES.

Retain six trace markers from Q5RBTRC and the existing one-shot
stage-refusal/real rollback-CLOSE test. Rebuild from the source-controlled
Q16FIN baseline, not an old deck; never overwrite JOB 8142/8143 evidence.
Only the new temporary ASMQ source and JOB/load-member identity differ.
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
SOURCE = HERE / 'test-q5-open-rollback.bcpl'
BASELINE = HERE / 'bcplqsam.asm'
COMPILED = WORK / 'rollback-finish-generated.asm'
TARGET = WORK / 'q5rbfin.jcl'

SOURCE_HEAD = '73a077cbcd829f52f8657bc4a5c2d8c708ba6de0'
COMPILED_SHA256 = 'f68e03ea2cdc8bc9a25a8f4df49c8c8cc1fd4b54056eed1a858be952b207d4ed'
COMPILER_JOB = '8144'
JOB = 'Q5RBFIN'


def load(filename: str):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(
        'q5_finish_' + filename.replace('-', '_').replace('.', '_'), path)
    if spec is None or spec.loader is None:
        raise ValueError('source-controlled helper unavailable: ' + filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_corrected_source() -> None:
    source = SOURCE.read_text('ascii')
    if not source.endswith(
        '    WRITES("BCPLQSAM Q5 OPEN ROLLBACK PASS")\n'
        '    NEWLINE()\n'
        '    FINISH\n'
        '$)1\n'
    ):
        raise ValueError('corrected BCPL source lacks required FINISH ending')
    if 'STOP(12)' not in source:
        raise ValueError('test-only failure assertions missing')


def retag_trace_deck(deck: str) -> str:
    """Transform only the three Q5RBTRC identity cards to Q5RBFIN."""
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    before = deck.splitlines()
    campaign.verify(before, 'Q5RBTRC', 'finish')
    after = before.copy()
    after[0] = diag.replace_once(after[0], '//Q5RBTRC ', '//Q5RBFIN ')
    campaign.replace_one(after, ' NAME Q5RBTRC(R)', ' NAME Q5RBFIN(R)')
    campaign.replace_one(
        after, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBTRC),',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBFIN),')
    result = campaign.verify(after, JOB, 'finish')

    reverse = after.copy()
    reverse[0] = diag.replace_once(reverse[0], '//Q5RBFIN ', '//Q5RBTRC ')
    campaign.replace_one(reverse, ' NAME Q5RBFIN(R)',
                         ' NAME Q5RBTRC(R)')
    campaign.replace_one(
        reverse, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBFIN),',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5RBTRC),')
    if reverse != before or result.splitlines() != after:
        raise ValueError('unexpected JCL edit beyond three identity cards')
    return result


def instrument_deck(deck: str, baseline: str) -> str:
    trace = load('prepare-q5-rollback-trace.py')
    return retag_trace_deck(trace.instrument_deck(deck, baseline))


def check() -> None:
    """Complete synthetic JCL check; no resident access or output files."""
    require_corrected_source()
    diag = load('prepare-q1-finalizer-diagnostic.py')
    campaign = diag.load_campaign()
    sample = campaign.module('prepare-q1-query.py').time_helper().trailer_helper().sample_generated()
    baseline = BASELINE.read_text('ascii')
    original = campaign.make_deck(
        'finish', sample, ["//Q16FIN JOB (BCPL),'Q5 FIN CHECK',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    trace = load('prepare-q5-rollback-trace.py')
    traced = trace.instrument_deck(original, baseline)
    result = retag_trace_deck(traced)
    if not result.startswith('//Q5RBFIN '):
        raise ValueError('incorrect corrected test JOB identity')
    for marker in (
        'Q5R:E:', 'Q5R:L:', 'Q5R:P:POST-CLEAN',
        'Q5R:R:ROLL-RETURN', 'Q5R:T:CORE-EPILOGUE', 'Q5R:X:',
    ):
        if result.count(marker) != 1:
            raise ValueError('missing/duplicate six-phase trace marker: ' + marker)
    for bad in (
        traced.replace('//Q5RBTRC ', '//Q5WRONG ', 1),
        traced.replace(' NAME Q5RBTRC(R)', ' NAME Q5WRONG(R)', 1),
        traced.replace(' NAME Q5RBTRC(R)', '', 1),
    ):
        if bad == traced:
            raise ValueError('negative trace-deck anchor missing')
        try:
            retag_trace_deck(bad)
        except ValueError:
            pass
        else:
            raise ValueError('tampered source trace deck was accepted')
    print('PASS: Q5RBFIN synthetic 6-phase JCL:',
          len(result.splitlines()), 'cards; 3 negative identity tests; no JES')


def verified_compiler_code() -> bytes:
    """Bound the new build to verified JOB 8144, not JOB 8141 or its image."""
    require_corrected_source()
    evidence = WORK / 'q5rfcomp-attempt'
    if evidence.is_symlink() or not evidence.is_dir():
        raise ValueError('JOB 8144 compiler evidence directory missing')
    if (evidence / 'source-head.txt').read_text('ascii').strip() != SOURCE_HEAD:
        raise ValueError('compiler source revision mismatch')
    if (evidence / 'compile.rc').read_text('ascii').strip() != '0':
        raise ValueError('JOB 8144 compiler did not pass')
    if (evidence / 'job-number.txt').read_text('ascii').strip() != COMPILER_JOB:
        raise ValueError('expected original compiler JOB 8144')
    source_record = (evidence / 'source.sha256').read_text('ascii').strip().split()
    if not source_record or source_record[0] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise ValueError('compiled-source digest does not match corrected BCPL')
    summary = (evidence / 'summary.txt').read_text('utf-8', errors='replace')
    if not re.search(r'^JOB\s+8144\s+Q5RFCOMP\s*$', summary, re.M):
        raise ValueError('wrong compiler JOB identity in saved JES summary')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise ValueError('compiler JES result not clean')
    if not re.search(r'^COMP\s+ICINT19\s+RC=0000\s*$', summary, re.M):
        raise ValueError('compiler ICINT19 step not zero')
    if not re.search(r'^SVCODE\s+IEBGENER\s+RC=0000\s*$', summary, re.M):
        raise ValueError('compiler CODE recovery step not zero')
    if COMPILED.is_symlink() or COMPILED.resolve().parent != WORK.resolve():
        raise ValueError('compiled assembler is outside expected workarea')
    generated = COMPILED.read_bytes()
    if hashlib.sha256(generated).hexdigest() != COMPILED_SHA256:
        raise ValueError('JOB 8144 compiler assembler SHA-256 mismatch')
    if len(generated.splitlines()) != 311:
        raise ValueError('JOB 8144 compiler output must contain 311 lines')
    return generated


def prepare() -> None:
    if TARGET.exists() or TARGET.is_symlink():
        raise ValueError('Q5RBFIN JCL already exists; refusing overwrite')
    generated = verified_compiler_code()
    query = load('prepare-q1-query.py')
    core = query.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object'
            or spec.get('dsorg') != 'PO'
            or spec.get('recfm') != 'FB'
            or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('unapproved BOOT_OBJ input library')
    jobcard = core.authenticated_job_card(
        config, 'Q16FIN', 'Q5 FINISH TRACE', redact_password=False)
    campaign = load('prepare-q1-campaign.py')
    baseline_deck = campaign.make_deck(
        'finish', generated.decode('latin-1'), jobcard,
        core.full_dsn(config, spec))
    result = instrument_deck(baseline_deck, BASELINE.read_text('ascii'))
    WORK.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(TARGET, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(result)
    print('PREPARED ONLY:', TARGET, 'cards', len(result.splitlines()))
    print('SHA-256:', hashlib.sha256(result.encode('ascii')).hexdigest())
    print('No JES submission or installed dataset modification')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--prepare', action='store_true')
    args = p.parse_args()
    if args.check:
        check()
    else:
        prepare()


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError, AssertionError) as exc:
        raise SystemExit('Q5RBFIN preparation FAILED: ' + str(exc))
