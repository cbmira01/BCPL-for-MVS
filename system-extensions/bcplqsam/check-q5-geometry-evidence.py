#!/usr/bin/env python3
"""Strict read-only Q.5 Q5GEOM JES/console/hardcopy acceptance checker.

Never submits JES or changes dataset contents. Printer/source assembly
mentions do not count as runtime PASS or checkpoint evidence.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

JOB = 'Q5GEOM'
STEPS = ('ASMWR', 'LKWR', 'ASMA', 'ASMN', 'ASMR', 'ASMQ',
         'ASMG', 'LKED', 'WGO', 'GO')
PASS = 'BCPLQSAM Q5 GEOMETRY NEGATIVE PASS'
TRACE = 'Q5G:X:00000001:00000000:00000000:00000000:00000000'


def check_summary(summary: str) -> tuple[list[str], int | None]:
    errors: list[str] = []
    m = re.search(r'^JOB\s+(\d+)\s+Q5GEOM\s*$', summary, re.M)
    if not m:
        errors.append('JES summary must identify Q5GEOM and job number')
        return errors, None
    job = int(m.group(1))
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        errors.append('JES not SUCCESS with highest RC=0000')
    if 'Statements flagged: 0' not in summary or \
       'Highest severity:   0' not in summary:
        errors.append('IFOX zero-severity evidence absent')
    step_lines = re.findall(
        r'^\s*(ASMWR|LKWR|ASMA|ASMN|ASMR|ASMQ|ASMG|LKED|WGO|GO)\s+'
        r'\S+(?:\s+\S+)*?\s+RC=(\d{4})\s*$', summary, re.M)
    if len(step_lines) != 10 or tuple(x[0] for x in step_lines) != STEPS:
        errors.append('wrong or missing ten native steps')
    if any(rc != '0000' for _, rc in step_lines):
        errors.append('nonzero IFOX/IEWL/WGO/GO step')
    if re.search(r'\bABEND\b|\bJCL ERROR\b', summary):
        errors.append('abnormal/JCL error')
    return errors, job


def check_report(report: str) -> list[str]:
    errors: list[str] = []
    # Only a complete standalone printed BCPL line counts; source listings
    # may legitimately contain the literal PASS text as DC/C declarations.
    lines = [x for x in report.splitlines() if x.strip() == PASS]
    if len(lines) != 1:
        errors.append(f'expected one standalone BCPL PASS, got {len(lines)}')
    # Earlier native reports show a literal source reference to BCPLREG 2001
    # in IFOX listing. Only runtime emission indicates finalizer trouble.
    if any(re.match(r'^(?:\s*\d+[.:]\d+[.:]\d+\s+JOB\s+\d+\s+)?'
                    r'\+?BCPLREG 2001 FINALIZER RETURNED NONZERO\s*$',
                    x.strip()) for x in report.splitlines()):
        errors.append('unexpected runtime BCPLREG 2001 finalizer failure')
    return errors


def check_log(log: str, job: int, label: str) -> list[str]:
    errors: list[str] = []
    lines = log.splitlines()
    lead = re.compile(r'\bJOB\s+' + str(job) + r'\s+')
    own = [(i, x) for i,x in enumerate(lines) if lead.search(x)]
    starts = [(i,x) for i,x in own if re.search(r'\$HASP373\s+Q5GEOM\s+STARTED\b', x)]
    ends = [(i,x) for i,x in own if re.search(r'\$HASP395\s+Q5GEOM\s+ENDED\b', x)]
    if len(starts) != 1 or len(ends) != 1 or starts[0][0] >= ends[0][0]:
        return [f'{label}: incomplete/ambiguous Q5GEOM START/END boundaries']
    a, b = starts[0][0], ends[0][0]
    phases = [x for i,x in own if a < i < b and re.search(r'\+Q5G:[ELX]:',x)]
    if len(phases) != 1 or '+' + TRACE not in phases[0]:
        errors.append(f'{label}: expected exactly one bounded Q5G:X zero-resource trace')
    wrong = [x for i,x in own if i <= a or i >= b if re.search(r'\+Q5G:[ELX]:', x)]
    if wrong:
        errors.append(f'{label}: Q5G markers outside job boundaries')
    return errors


def check(summary: str, report: str, console: str, hardcopy: str) -> list[str]:
    errors, job = check_summary(summary)
    errors.extend(check_report(report))
    if job is not None:
        errors.extend(check_log(console, job, 'Hercules console'))
        errors.extend(check_log(hardcopy, job, 'MVS hardcopy'))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for item in ('summary','report','console','hardcopy'):
        parser.add_argument('--'+item, type=Path, required=True)
    a = parser.parse_args()
    errors = check(*(getattr(a,name).read_text('utf-8',errors='replace') for name in
                     ('summary','report','console','hardcopy')))
    if errors:
        for message in errors:
            print('FAIL:', message)
        raise SystemExit(1)
    print('PASS: Q5GEOM native geometry, single BCPL marker, bounded zero-resource Q5G:X')


if __name__ == '__main__':
    main()
