#!/usr/bin/env python3
"""TA.0: one safe entry point for ICINT19 execution or existing-evidence review.

If the selected output directory exists, inspect it without submitting JCL,
regardless of whether the original job finished successfully. If it is absent,
run the canonical eight-step MVS pilot at most once. A failed or ambiguous
submission never triggers an automatic JES retry. All evidence stays in
repository workarea/ and no private report is echoed to the console.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).with_name('verify-icint19-executable.py')
INSPECTOR = Path(__file__).with_name('inspect-icint19-failed-pilot.py')


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('TA0_MODULE_UNAVAILABLE')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decision(pilot, inspector, core, config, *, evidence: Path,
             review_dir: Path, output: Path) -> dict[str, str]:
    # Validate even an existing output path before looking at any saved data.
    # Broken symlinks report False for exists(); the path guard still rejects.
    pilot.external(output, new=not output.exists())
    if output.exists():
        detail = inspector.diagnose(pilot, core, config, evidence=evidence,
                                    review_dir=review_dir, output=output)
        return {'state': detail['state'], 'job': detail.get('job', 'unknown'),
                'preflight': detail.get('preflight', 'UNKNOWN'),
                'reason': detail.get('reason', 'NOT_APPLICABLE'),
                'submitted_now': 'NO'}
    try:
        result = pilot.run(core, config, evidence=evidence,
                           review_dir=review_dir, output=output)
    except (OSError, ValueError, RuntimeError, UnicodeError,
            subprocess.TimeoutExpired) as exc:
        # Preflight failure has no output directory; post-submission status may
        # be uncertain. Inspect saved evidence and never retry automatically.
        if output.exists():
            detail = inspector.diagnose(pilot, core, config,
                                        evidence=evidence, review_dir=review_dir,
                                        output=output)
        else:
            detail = {'state': 'NO_OUTPUT_DIRECTORY', 'job': 'unknown',
                      'preflight': inspector.cause(exc)}
        return {'state': detail['state'], 'job': detail.get('job', 'unknown'),
                'preflight': detail.get('preflight', 'UNKNOWN'),
                'reason': detail.get('reason', 'NOT_APPLICABLE'),
                'submitted_now': 'NOT_CONFIRMED'}
    return {'state': 'NEW_EXECUTION_VALIDATED', 'job': str(result['job']),
            'preflight': 'PASS', 'reason': 'NOT_APPLICABLE',
            'submitted_now': 'YES'}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iehlist-evidence', required=True, type=Path)
    ap.add_argument('--review-dir', required=True, type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        os.umask(0o077)
        pilot = load(PILOT, 'ta0_icint19_once')
        inspector = load(INSPECTOR, 'ta0_icint19_review')
        core = pilot.import_file(pilot.CORE, 'ta0_icint19_core')
        detail = decision(pilot, inspector, core, core.load_config(),
                          evidence=args.iehlist_evidence, review_dir=args.review_dir,
                          output=args.output_dir)
    except (OSError, ValueError, RuntimeError, UnicodeError,
            subprocess.TimeoutExpired) as exc:
        # Never print error text from possible private reports or JOB cards.
        print('TA.0 ICINT19 GATE REFUSED: ' + type(exc).__name__, file=sys.stderr)
        print('No automatic JES retry.', file=sys.stderr)
        return 1
    print('TA.0 ICINT19 GATE: ' + detail['state'] + ' JOB=' + detail['job'])
    print('  PREFLIGHT=' + detail['preflight'] + ' REPORT=' + detail['reason'])
    print('  SUBMITTED_IN_THIS_INVOCATION=' + detail['submitted_now'])
    print('Private evidence remains in workarea/; no automatic JES retry.')
    return 0 if detail['state'] in ('NEW_EXECUTION_VALIDATED', 'SAVED_EXECUTION_VERIFIED') else 1


if __name__ == '__main__':
    raise SystemExit(main())
