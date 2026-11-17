#!/usr/bin/env python3
"""TA.0: non-submitting diagnosis of an interrupted ICINT19 executable-use pilot.

Read the existing private workarea evidence and re-run the *same* preflight
and JES semantic validator as the original pilot. Never print private JES
output, alter a receipt, or resubmit MVS JCL.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).with_name('verify-icint19-executable.py')
EXPECTED = ('job-body.jcl', 'cursor.json', 'job-summary.txt', 'job-report.txt',
            'printer-window.raw', 'receipt.json', 'failure.txt')
SUMMARY = re.compile(r'^JOB\s+([0-9]{1,4})\s+TA0ICEX\s*$', re.M)
FAILURE = re.compile(r'^JOB=(unknown|[0-9]{1,4}); type=[A-Za-z][A-Za-z0-9_]*\n?\Z')
SAFE_CAUSES = frozenset({
    'retained IEHLIST directory review does not match pinned original',
    'unexpected observed ICINT19 directory entry/attributes; review required',
    'active MR10_LOAD source differs from IEHLIST evidence',
    'MRREGRES source revision changed: review before running',
    'MRREGRES diagnostic body is scoped to the verified HERC02 development installation',
    'MRREGRES source missing original steps',
    'MRREGRES step missing, duplicated or program changed',
    'MRREGRES step delimiter missing',
    'unexpected JCL block content',
    'unexpected executable steps in extracted body',
    'interpreter STEPLIB does not consistently select reviewed MR10_LOAD',
    'scalar-vector test source not selected',
    'invalid JCL card width',
    'scalar-vector golden output changed',
    'missing or duplicated JES START/END identity',
    'missing, bypassed, reordered or failed IEBGENER/ICINT19 step',
    'potential MVS ABEND',
    'executed scalar-vector RP records differ from golden output',
    'missing or unsuccessful interpreted CODE= records',
})


def pilot_module():
    spec = importlib.util.spec_from_file_location('ta0_icint19_pilot_inspected', PILOT)
    if spec is None or spec.loader is None:
        raise ValueError('PILOT_SOURCE_MISSING')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cause(error: BaseException) -> str:
    value = str(error)
    if value.startswith('missing or duplicated successful IEF142I: '):
        step = value.rsplit(': ', 1)[-1]
        if step in ('SSYNI', 'STRNI', 'SCGI', 'SBLIBI', 'SICLIB', 'C01A', 'G01A', 'R01'):
            return 'IEF142I_MISSING_OR_DUPLICATE_' + step
    if value in SAFE_CAUSES:
        return value.upper().replace(' ', '_').replace('/', '_').replace(':', '')
    return type(error).__name__.upper()


def diagnose(pilot, core, config, *, evidence: Path, review_dir: Path,
             output: Path) -> dict[str, str]:
    # A new destination can only mean preflight stopped before mkdir.
    # An existing destination may contain a previously submitted JES job.
    pilot.external(output, new=not output.exists())
    preflight_error = None
    try:
        pilot.validated_inputs(core, config, evidence=evidence, review_dir=review_dir)
    except Exception as exc:
        preflight_error = cause(exc)

    if not output.exists():
        return {'state': 'NO_OUTPUT_DIRECTORY',
                'preflight': 'OK_NOW' if preflight_error is None else preflight_error,
                'job': 'unknown'}
    # Do not follow links, do not display any content, and reject unexpected
    # directory entries rather than using them as evidence.
    entries = list(output.iterdir())
    for path in entries:
        if path.name not in EXPECTED or not path.is_file() or path.is_symlink():
            raise ValueError('UNEXPECTED_OR_LINKED_PILOT_EVIDENCE')
    present = {p.name for p in entries}
    fail_job = None
    if 'failure.txt' in present:
        raw = pilot.read_plain(output/'failure.txt', 1024)
        marker = FAILURE.fullmatch(raw.decode('ascii'))
        if marker is None:
            raise ValueError('INVALID_FAILURE_MARKER')
        fail_job = marker.group(1)

    if 'receipt.json' in present:
        return {'state': 'RECEIPT_ALREADY_PRESENT',
                'preflight': preflight_error or 'OK_NOW',
                'job': fail_job or 'unknown'}

    if 'job-report.txt' not in present:
        # A cursor alone cannot establish whether the socket reader accepted
        # the JCL. Never automatically retry the job.
        stage = 'SUBMISSION_STATUS_UNCERTAIN' if 'cursor.json' in present else 'NO_CAPTURED_JOB'
        return {'state': stage, 'preflight': preflight_error or 'OK_NOW',
                'job': fail_job or 'unknown'}
    if 'job-summary.txt' not in present or 'cursor.json' not in present or 'job-body.jcl' not in present:
        return {'state': 'INCOMPLETE_SAVED_JES_EVIDENCE',
                'preflight': preflight_error or 'OK_NOW',
                'job': fail_job or 'unknown'}

    report = pilot.read_plain(output/'job-report.txt').decode('utf-8')
    summary = pilot.read_plain(output/'job-summary.txt', 1024 * 1024).decode('utf-8')
    matches = SUMMARY.findall(summary)
    if len(matches) != 1 or not (1 <= int(matches[0]) <= 9999):
        return {'state': 'SAVED_SUMMARY_JOB_UNCERTAIN',
                'preflight': preflight_error or 'OK_NOW', 'job': fail_job or 'unknown'}
    job = str(int(matches[0]))
    if fail_job is not None and fail_job != job:
        return {'state': 'SAVED_JES_JOB_ID_CONFLICT',
                'preflight': preflight_error or 'OK_NOW', 'job': 'unknown'}
    try:
        pilot.validate_report(report, job=int(job), gold=pilot.GOLDEN)
    except Exception as exc:
        return {'state': 'SAVED_JES_REPORT_REJECTED', 'reason': cause(exc),
                'preflight': preflight_error or 'OK_NOW', 'job': job}
    if 'printer-window.raw' not in present:
        state = 'JES_REPORT_VALID_BUT_PRINTER_WINDOW_MISSING'
    else:
        state = 'JES_REPORT_VALID_BUT_NO_FINAL_RECEIPT'
    return {'state': state, 'preflight': preflight_error or 'OK_NOW', 'job': job}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iehlist-evidence', type=Path, required=True)
    ap.add_argument('--review-dir', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args(argv)
    try:
        mod = pilot_module()
        core = mod.import_file(mod.CORE, 'ta0_inspect_config')
        result = diagnose(mod, core, core.load_config(), evidence=args.iehlist_evidence,
                          review_dir=args.review_dir, output=args.output_dir)
    except (OSError, ValueError, RuntimeError, UnicodeError, UnicodeDecodeError) as error:
        print('TA.0 ICINT19 FAILURE INSPECTION REFUSED: ' + cause(error), file=sys.stderr)
        return 1
    print('TA.0 ICINT19 FAILURE INSPECTION: ' + result['state'] + ' JOB=' + result['job'])
    if 'reason' in result:
        print('  REPORT CHECK: ' + result['reason'])
    print('  CURRENT PREFLIGHT: ' + result['preflight'])
    print('Read-only saved MVS evidence; no JES job submitted or retried.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
