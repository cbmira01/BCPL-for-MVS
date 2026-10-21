#!/usr/bin/env python3
"""Check actual R0G76F MVS step outcomes and formatted G!76 GO output."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

JOB = 'R0G76F'
MARKER = 'R0 G76 FALLBACK 31415 PASS'
REQUIRED = {'ASMA': 0, 'ASMB': 0, 'LKED': 0, 'GO': 0}
STEPS = re.compile(
    r'\bIEF142I\s+(\S+)\s+(\S+)\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE\s+(\d{4})\b'
)
BAD = re.compile(r'\b(?:IEF450I|IEF452I|IEF472I|IEA995I)\b[^\n]*(?:ABEND|JCL ERROR|SYSTEM|USER)', re.I)
PUNCHED = re.compile(r'\bTOTAL RECORDS PUNCHED\s+(\d+)')


def verify(report: str) -> dict:
    if BAD.search(report):
        raise ValueError('JCL/ABEND detected')
    step_codes: dict[str, int] = {}
    for name, step, code in STEPS.findall(report):
        if name != JOB:
            continue
        if step in step_codes:
            raise ValueError(f'duplicate step {step}')
        step_codes[step] = int(code)
    if step_codes != REQUIRED:
        raise ValueError(f'wrong or missing steps {step_codes}')
    records = list(map(int, PUNCHED.findall(report)))
    if len(records) != 2 or not all(records):
        raise ValueError(f'missing/empty IFOX object: {records}')
    if report.count('NO STATEMENTS FLAGGED IN THIS ASSEMBLY') != 2:
        raise ValueError('IFOX flagged statements or missing listings')
    if not re.search(r'\bHIGHEST SEVERITY WAS\s+0\b', report):
        raise ValueError('missing IFOX severity confirmation')
    # The source fixture embeds "%N", not the rendered number.  Only
    # exact runtime-formatted text can match this marker, not JCL echo.
    lines = [x.strip() for x in report.replace('\f', '').splitlines()]
    markers = [x for x in lines if x == MARKER]
    if len(markers) != 1:
        raise ValueError(f'expected one exact formatted GO marker, got {len(markers)}')
    return {'status': 'R0_G76_NO_EXPORT_FALLBACK_PASS',
            'job': JOB, 'step_codes': step_codes,
            'ifo_x_object_records': records, 'marker': MARKER,
            'iewl_map_review_required': True}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    result = verify(args.report.read_text('utf-8'))
    import json
    print(json.dumps(result, sort_keys=True))
    print('Review IEWL MAP/XREF: BLIB owner must be temporary ASMB.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 G76 no-export FAILED: {exc}')
