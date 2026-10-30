#!/usr/bin/env python3
"""Prepare ONE test-only Q5STDIAG job from preserved Q16STP JCL. No JES.

Reuse the source-controlled Q.1 three-checkpoint finalizer probe unchanged.
Only the JOB identity, temporary load-member identity, and ASMQ source
may change. Preserve all 16 temporary F1024 DDs and GO REGION=256K.
The resulting Q1F:E/L/X WTO records require target-MVS verification.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
Q1WORK = ROOT / 'workarea/bcplqsam-q1'
Q5WORK = ROOT / 'workarea/bcplqsam-q5'
BASELINE = HERE / 'bcplqsam.asm'


def load_diagnostic():
    path = HERE / 'prepare-q1-finalizer-diagnostic.py'
    spec = importlib.util.spec_from_file_location('q5_q1_finalizer_probe', path)
    if spec is None or spec.loader is None:
        raise ValueError('Q.1 diagnostic helper unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def instrument_deck(deck: str, baseline: str) -> str:
    diag = load_diagnostic()
    campaign = diag.load_campaign()
    before = deck.splitlines()
    campaign.verify(before, 'Q16STP', 'stop')
    first, last = campaign.source_span(before, 'ASMQ')
    baseline_cards = baseline.splitlines()
    if before[first:last] != baseline_cards:
        raise ValueError('ASMQ does not match exact source-controlled baseline')

    changed = before.copy()
    modified_asm = diag.instrument_asm(baseline)
    changed[first:last] = modified_asm.splitlines()
    changed[0] = diag.replace_once(changed[0], '//Q16STP ',
                                   '//Q5STDIAG ')
    campaign.replace_one(changed, ' NAME Q16STP(R)',
                         ' NAME Q5STDIAG(R)')
    campaign.replace_one(changed,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16STP),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5STDIAG),')
    result = campaign.verify(changed, 'Q5STDIAG', 'stop')

    # Independently reverse the three permitted JCL edits and source
    # substitution. Every other card must be exactly preserved.
    restored = changed.copy()
    new_first, new_last = campaign.source_span(restored, 'ASMQ')
    restored[new_first:new_last] = baseline_cards
    restored[0] = diag.replace_once(restored[0], '//Q5STDIAG ',
                                    '//Q16STP ')
    campaign.replace_one(restored, ' NAME Q5STDIAG(R)',
                         ' NAME Q16STP(R)')
    campaign.replace_one(restored,
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q5STDIAG),',
                         '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16STP),')
    if restored != before:
        raise ValueError('unexpected JCL changes outside ASMQ')
    if result.splitlines() != changed:
        raise ValueError('generated deck changed during verification')
    for marker in ('Q1F:E:', 'Q1F:L:', 'Q1F:X:'):
        if modified_asm.count(marker) != 1:
            raise ValueError('missing/duplicate diagnostic marker: ' + marker)
    return result


def confined(path: Path, root: Path, description: str) -> Path:
    checked = path.resolve()
    if root.resolve() not in checked.parents:
        raise ValueError(description + ' must be inside ' + str(root))
    return checked


def offline_check() -> None:
    diag = load_diagnostic()
    campaign = diag.load_campaign()
    sample = campaign.module('prepare-q1-query.py').time_helper() \
        .trailer_helper().sample_generated()
    original = campaign.make_deck(
        'stop', sample, ["//Q16STP JOB (BCPL),'Q5 CHECK',CLASS=A"],
        'HERC02.BCPL.BOOT.OBJ')
    baseline = BASELINE.read_text(encoding='ascii')
    changed = instrument_deck(original, baseline)
    if ('//Q5STDIAG JOB ' not in changed or
            ' NAME Q5STDIAG(R)' not in changed or
            '         BCXREQ BCPLQSAM' not in changed or
            changed.count('//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)') != 32):
        raise ValueError('synthetic STOP deck failed invariant check')

    # A modified production assembler, or a missing STOP DD, must fail
    # closed rather than silently generate untrustworthy native evidence.
    for tampered in (
        original.replace('QSMFIN   CSECT', 'QSMFINX  CSECT', 1),
        original.replace('//Q15      DD  DSN=&&Q1H15,DISP=(OLD,DELETE),',
                         '//Q15      DD  DSN=&&Q1HXX,DISP=(OLD,DELETE),', 1),
    ):
        if tampered == original:
            raise ValueError('offline negative-case anchor absent')
        try:
            instrument_deck(tampered, baseline)
        except ValueError:
            pass
        else:
            raise ValueError('tampered STOP deck was not rejected')
    print('PASS: Q5STDIAG synthetic STOP deck, 2 rejection tests;',
          len(changed.splitlines()), 'cards; no JES')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.check:
        if args.input or args.output:
            parser.error('--check is pathless')
        offline_check()
        return
    if args.input is None or args.output is None:
        parser.error('--input and --output required')

    source = confined(args.input, Q1WORK, 'preserved Q16STP input')
    target = confined(args.output, Q5WORK, 'Q.5 diagnostic output')
    if source == target or target.exists():
        raise ValueError('output must be new and distinct')
    content = instrument_deck(source.read_text(encoding='ascii'),
                              BASELINE.read_text(encoding='ascii'))
    Q5WORK.mkdir(parents=True, exist_ok=True)
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
        out.write(content)
    print('PREPARED ONLY:', target, 'cards', len(content.splitlines()))
    print('SHA-256:', hashlib.sha256(content.encode('ascii')).hexdigest())
    print('No JES submission or installed MVS dataset change')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError, AssertionError) as exc:
        raise SystemExit('Q5STDIAG preparation FAILED: ' + str(exc))
