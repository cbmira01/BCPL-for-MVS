#!/usr/bin/env python3
"""Prepare Q5STDIAG from a completed current-source regression 167. No JES.

Only native regression 167 evidence that passes its established MVS
step/output checker and uses the exact current BCPLQSAM assembler is
eligible. The Q.1 historical deck is never silently substituted.
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
CASE = ROOT / 'bootstrap-toolchain/regression/167-qsam-sixteen-stop'
NATIVE = ROOT / 'workarea/native-regression/167-qsam-sixteen-stop'
OUTPUT = ROOT / 'workarea/bcplqsam-q5/q5stdiag.jcl'
BASELINE = HERE / 'bcplqsam.asm'


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('module unavailable: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_source_fixture() -> None:
    fixture = (CASE / 'source.bcpl').read_bytes()
    canonical = (HERE / 'test-q1-stop.bcpl').read_bytes()
    if fixture != canonical:
        raise ValueError('regression 167 source differs from canonical STOP')
    expected = (CASE / 'expected.txt').read_text('ascii').splitlines()
    if expected != ['BCPLQSAM Q1 16 STOP PASS']:
        raise ValueError('regression 167 expected output differs')
    if (CASE / 'qsam-native.txt').read_text('ascii').strip() != 'stop':
        raise ValueError('regression 167 profile is not STOP')


def verify_candidate(path: Path, q5, runner, baseline: str) -> str:
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError('candidate uses a symbolic link')
    if path.resolve().parent.parent != NATIVE.resolve():
        raise ValueError('candidate escapes native 167 workarea')
    attempt = path.parent
    job = (attempt / 'job-number.txt').read_text('ascii').strip()
    if re.fullmatch(r'[0-9]+', job) is None:
        raise ValueError('missing/invalid JES job number')
    summary = (attempt / 'summary.txt').read_text('utf-8')
    report = (attempt / 'report.txt').read_text('utf-8')
    if re.search(rf'^JOB\s+{re.escape(job)}\s+Q16STP\s*$',
                 summary, re.MULTILINE) is None:
        raise ValueError('JES summary does not match recorded job number')
    errors = runner.evidence(167, summary, report)
    if errors:
        raise ValueError('regression 167 native evidence failed: ' +
                         '; '.join(errors))
    # This also verifies Q16STP JCL, all DDs, all 71-column cards,
    # exact embedded current assembler and no permanent dataset writes.
    return q5.instrument_deck(path.read_text('ascii'), baseline)


def select_candidate(q5, runner, baseline: str) -> tuple[Path, str]:
    paths = sorted(NATIVE.glob('native-*/native.jcl'),
                   key=lambda p: (p.stat().st_mtime_ns, str(p)),
                   reverse=True)
    if not paths:
        raise ValueError('no preserved native regression 167 decks found')
    failures = []
    for path in paths:
        try:
            return path, verify_candidate(path, q5, runner, baseline)
        except (OSError, UnicodeError, ValueError) as exc:
            failures.append(f'{path.parent.name}: {exc}')
    raise ValueError('no completed current-source regression 167 deck: ' +
                     ' | '.join(failures[:4]))


def prepare() -> None:
    assert_source_fixture()
    q5 = load_module(HERE / 'prepare-q5-stop-diagnostic.py', 'q5_stop')
    runner = load_module(ROOT / 'tools/checks/run-q2-qsam-regression.py',
                         'q5_regression_evidence')
    baseline = BASELINE.read_text('ascii')
    source, deck = select_candidate(q5, runner, baseline)
    if OUTPUT.exists():
        raise ValueError('Q5STDIAG output already exists; will not overwrite')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(OUTPUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(deck)
    print('PASS: verified current-source native regression 167')
    print('Source:', source)
    print('PREPARED ONLY:', OUTPUT, 'cards', len(deck.splitlines()))
    print('SHA-256:', hashlib.sha256(deck.encode('ascii')).hexdigest())
    print('No JES submission or installed MVS dataset change')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    assert_source_fixture()
    q5 = load_module(HERE / 'prepare-q5-stop-diagnostic.py', 'q5_stop')
    if args.check:
        q5.offline_check()
        print('PASS: Q.5 regression-167 preparation dependencies; no JES')
    else:
        prepare()


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError, AssertionError) as exc:
        raise SystemExit('Q5STDIAG regression preparation FAILED: ' + str(exc))
