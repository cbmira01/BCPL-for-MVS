#!/usr/bin/env python3
"""Verify MVS job steps and one dynamic G!150 address observation."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

JOB = 'R0G150'
EXPECTED = {'ASMA': 0, 'ASMP': 0, 'LKED': 0, 'GO': 0}
STEP = re.compile(r'\bIEF142I\s+(\S+)\s+(\S+)\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE\s+(\d{4})\b')
FORMAT = re.compile(r'^R0 G150 OVERWRITE ACT=([0-9A-F]{8}) APP=([0-9A-F]{8}) PASS$')
PUNCHED = re.compile(r'\bTOTAL RECORDS PUNCHED\s+(\d+)')
BAD = re.compile(r'\b(?:IEF450I|IEF452I|IEF472I|IEA995I)\b[^\n]*(?:ABEND|JCL ERROR|SYSTEM|USER)', re.I)


def verify(report: str) -> dict:
    if BAD.search(report):
        raise ValueError('MVS error or abend')
    steps = {}
    for job, step, code in STEP.findall(report):
        if job == JOB:
            if step in steps:
                raise ValueError(f'duplicate step {step}')
            steps[step] = int(code)
    if steps != EXPECTED:
        raise ValueError(f'wrong/missing steps: {steps}')
    punched = [int(x) for x in PUNCHED.findall(report)]
    if len(punched) != 2 or min(punched) <= 0:
        raise ValueError('missing or empty object deck')
    if report.count('NO STATEMENTS FLAGGED IN THIS ASSEMBLY') != 2:
        raise ValueError('IFOX listing errors or missing listing')
    if len(re.findall(r'HIGHEST SEVERITY WAS\s+0\b', report)) != 2:
        raise ValueError('IFOX severity evidence missing')
    matches = []
    for row in report.replace('\f', '').splitlines():
        m = FORMAT.fullmatch(row.strip())
        if m:
            matches.append(m)
    if len(matches) != 1:
        raise ValueError('exactly one runtime-computed address record required')
    actual, app = (int(x, 16) for x in matches[0].groups())
    if actual in (0, 0xC7D3F258) or app == 0 or actual == app:
        raise ValueError('actual G150 must be initialized and differ from app owner')
    return {'status': 'R0_G150_STARTUP_APP_EXPORT_OVERWRITTEN',
            'job': JOB, 'steps': steps, 'object_records': punched,
            'observed_g150_hex': f'{actual:08X}',
            'application_owner_hex': f'{app:08X}',
            'exact_debugint_address_proved': False,
            'iewl_map_review_required': True}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    arg = p.parse_args()
    print(json.dumps(verify(arg.report.read_text('utf-8')), sort_keys=True))
    print('Review IEWL MAP/XREF: G150 exporter and linked BLIB/core provenance.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 G150 report FAILED: {exc}')
