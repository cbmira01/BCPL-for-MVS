#!/usr/bin/env python3
"""Verify observed MVS step RCs; RC8 is expected only for calibrated inequality."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

JOBS = {'calibrate': 'R0BICAL', 'member': 'R0BIMEM'}
SUCCESS = {'calibrate': {'ASMA': 0, 'ASMB': 0, 'COPYA': 0, 'SAME': 0, 'DIFFER': 8},
           'member': {'ASMMEM': 0}}
STEPS = re.compile(r'\bIEF142I\s+(\S+)\s+(\S+)\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE\s+(\d{4})\b')
NO_GO = re.compile(r'\b(?:IEF450I|IEF452I|IEF472I|IEA995I)\b[^\n]*(?:ABEND|JCL ERROR|SYSTEM|USER)', re.I)
OPEN_ERROR = re.compile(r'\b(?:IEB001I|IEB002I|IEC\d{3}I)\b', re.I)
PUNCHED = re.compile(r'TOTAL RECORDS PUNCHED\s+(\d+)')


def verify(profile: str, report: str) -> dict:
    if profile not in JOBS:
        raise ValueError('invalid profile')
    if NO_GO.search(report) or OPEN_ERROR.search(report):
        raise ValueError('operational ABEND/JCL/access error: inspect report')
    job = JOBS[profile]
    steps = {}
    for name, step, code in STEPS.findall(report):
        if name != job:
            continue
        if step in steps:
            raise ValueError(f'duplicate executed-step result: {step}')
        steps[step] = int(code)
    punched = [int(n) for n in PUNCHED.findall(report)]
    if len(punched) != (2 if profile == 'calibrate' else 1) or not all(punched):
        raise ValueError(f'nonempty assembler object decks not established: {punched}')
    req = SUCCESS[profile]
    if profile == 'calibrate':
        if steps != req:
            raise ValueError(f'expected calibration {req}, got {steps}')
        # IEBCOMPR MAY return RC8 for a utility error, so operator MUST
        # inspect its SYSPRINT for a genuine unequal-record explanation.
        return {'profile': profile, 'status': 'RC_CALIBRATION_PASSED',
                'step_codes': steps, 'ifo_x_object_records': punched, 'sysprint_review_required': True}
    if 'ASMMEM' not in steps or steps['ASMMEM'] != 0:
        raise ValueError(f'fresh BCPLMEM assembly failed: {steps}')
    if set(steps) != {'ASMMEM', 'COMPARE'}:
        raise ValueError(f'missing or extra steps: {steps}')
    rc = steps['COMPARE']
    if rc == 0:
        return {'profile': profile, 'status': 'REPORTED_EQUAL',
                'step_codes': steps, 'ifo_x_object_records': punched, 'sysprint_review_required': True}
    if rc == 8:
        return {'profile': profile, 'status': 'RC8_REVIEW_INEQUALITY_OR_ERROR',
                'step_codes': steps, 'ifo_x_object_records': punched, 'sysprint_review_required': True}
    raise ValueError(f'unknown comparator return code: {rc}')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile', choices=JOBS)
    p.add_argument('report', type=Path)
    a = p.parse_args()
    result = verify(a.profile, a.report.read_text(encoding='utf-8'))
    print(json.dumps(result, sort_keys=True))
    print('Review actual IEBCOMPR SYSPRINT before interpreting RC8 as unequal.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 B verification FAILED: {exc}')
