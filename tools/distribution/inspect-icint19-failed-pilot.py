#!/usr/bin/env python3
"""TA.0: non-submitting diagnosis of an interrupted ICINT19 executable-use pilot.

Read the existing private workarea evidence and re-run the *same* preflight
and JES semantic validator as the original pilot. Never print private JES
output, alter a receipt, or resubmit MVS JCL.
"""
from __future__ import annotations

import argparse
import json
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).with_name('verify-icint19-executable.py')
EXPECTED = ('job-body.jcl', 'cursor.json', 'job-summary.txt', 'job-report.txt',
            'printer-window.raw', 'receipt.json', 'failure.txt')
PINNED = frozenset(('job-body.jcl', 'cursor.json', 'job-summary.txt',
                    'job-report.txt', 'printer-window.raw'))
RECEIPT_FIELDS = frozenset(('phase', 'job', 'jobname', 'source_dsn',
                            'source_directory_job', 'review_receipt_sha256',
                            'source_jcl_git_blob', 'source_jcl_sha256',
                            'golden_sha256', 'sha256', 'result', 'qualifications'))
PHASE = 'TA.0 MR10_LOAD EXECUTABLE PILOT — NOT TAPE OR RELEASE ACCEPTANCE'
SUM_STEPS = re.compile(r'^\s*([A-Z][A-Z0-9]{0,7})\s+(IEBGENER|ICINT19)\s+RC=\s*(\d{4})\s*$', re.M)
DIGEST = re.compile(r'[0-9a-f]{64}\Z')
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


class ReceiptRejected(ValueError):
    """Private receipt could not be revalidated; message is an allowlisted code."""


def insist(test: bool, code: str) -> None:
    if not test:
        raise ReceiptRejected(code)


def verify_saved_receipt(pilot, *, output: Path, review_dir: Path,
                         validated: tuple, present: set[str]) -> str:
    """Recompute source, byte pins, JES results and BCPL semantics; no I/O writes.

    A receipt is an assertion by the original pilot, not automatic proof.
    No saved metadata, including the job number, is trusted until all
    independent checks pass using the original checked-in validators.
    """
    insist(present == PINNED | {'receipt.json'}, 'RECEIPT_FILE_SET_INVALID')
    try:
        receipt = json.loads(pilot.read_plain(output/'receipt.json', 1024 * 1024).decode('utf-8'))
    except (UnicodeError, ValueError):
        raise ReceiptRejected('RECEIPT_JSON_INVALID') from None
    insist(type(receipt) is dict and receipt.keys() == RECEIPT_FIELDS,
           'RECEIPT_SCHEMA_MISMATCH')
    job = receipt['job']
    insist(type(job) is int and 1 <= job <= 9999 and
           receipt['phase'] == PHASE and receipt['jobname'] == pilot.NAME,
           'RECEIPT_JOB_IDENTITY_MISMATCH')
    original, _, source, body, source_blob = validated
    insist(receipt['source_dsn'] == original['dsn'] and
           receipt['source_directory_job'] == original['job'] and
           receipt['source_jcl_git_blob'] == source_blob and
           receipt['source_jcl_sha256'] == pilot.sha(source) and
           receipt['golden_sha256'] == pilot.sha(pilot.read_plain(pilot.GOLD, 1024)) and
           receipt['review_receipt_sha256'] == pilot.sha(
               pilot.read_plain(review_dir/'directory-review.json', 1024 * 1024)),
           'RECEIPT_SOURCE_BINDING_MISMATCH')
    pins = receipt['sha256']
    insist(type(pins) is dict and pins.keys() == PINNED and
           all(type(d) is str and DIGEST.fullmatch(d) is not None for d in pins.values()),
           'RECEIPT_PINS_INVALID')
    for name in PINNED:
        data = pilot.read_plain(output/name, pilot.MAX_REPORT * 2)
        insist(pilot.sha(data) == pins[name], 'RECEIPT_PIN_MISMATCH')
    insist(pilot.read_plain(output/'job-body.jcl') == body.encode('ascii'),
           'RECEIPT_JCL_BINDING_MISMATCH')
    summary = pilot.read_plain(output/'job-summary.txt', 1024 * 1024).decode('utf-8')
    insist(SUMMARY.findall(summary) == [str(job)] and
           SUM_STEPS.findall(summary) == [(step, program, '0000')
                                          for step, program in zip(pilot.STEPS, pilot.PROGRAMS)] and
           len(re.findall(r'^JOB RESULT:\s+SUCCESS\s*$', summary, re.M)) == 1 and
           len(re.findall(r'^HIGHEST RC:\s+0000\s*$', summary, re.M)) == 1,
           'RECEIPT_JES_SUMMARY_MISMATCH')
    report = pilot.read_plain(output/'job-report.txt').decode('utf-8')
    try:
        result = pilot.validate_report(report, job=job, gold=pilot.GOLDEN)
    except Exception:
        raise ReceiptRejected('RECEIPT_MVS_REPORT_FAILED') from None
    insist(receipt['result'] == result and
           type(receipt['qualifications']) is list and
           len(receipt['qualifications']) == 4 and
           all(type(x) is str for x in receipt['qualifications']),
           'RECEIPT_RESULT_MISMATCH')
    return str(job)


def diagnose(pilot, core, config, *, evidence: Path, review_dir: Path,
             output: Path) -> dict[str, str]:
    # A new destination can only mean preflight stopped before mkdir.
    # An existing destination may contain a previously submitted JES job.
    pilot.external(output, new=not output.exists())
    preflight_error = None
    validated = None
    try:
        validated = pilot.validated_inputs(core, config, evidence=evidence, review_dir=review_dir)
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
        if preflight_error is not None:
            return {'state': 'SAVED_RECEIPT_REJECTED', 'job': 'unknown',
                    'preflight': preflight_error, 'reason': 'CURRENT_PREFLIGHT_FAILED'}
        try:
            job = verify_saved_receipt(pilot, output=output,
                                       review_dir=review_dir,
                                       validated=validated, present=present)
        except (ReceiptRejected, OSError, ValueError, UnicodeError) as exc:
            why = str(exc) if isinstance(exc, ReceiptRejected) else 'RECEIPT_READ_ERROR'
            return {'state': 'SAVED_RECEIPT_REJECTED', 'job': 'unknown',
                    'preflight': 'OK_NOW', 'reason': why}
        return {'state': 'SAVED_EXECUTION_VERIFIED', 'preflight': 'OK_NOW',
                'job': job, 'reason': 'PINNED_JES_AND_BCPL_RESULT_VERIFIED'}

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
