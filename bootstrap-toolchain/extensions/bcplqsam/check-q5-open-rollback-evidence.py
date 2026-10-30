#!/usr/bin/env python3
"""Review real JOB Q5RBOPEN evidence; no JES, MVS writes or retries."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

STEPS = ('ASMWR', 'LKWR', 'ASMA', 'ASMN', 'ASMR',
         'ASMQ', 'ASMG', 'LKED', 'WGO', 'GO')
EXPECTED = {
    'E': (1, 2, 2, 1),         # injection after Q01 OPEN: live 2, DCB 2, stage 1
    'L': (1, 1, 1, 1, 0),      # one real rollback CLOSE: Q00 still live
    'X': (0, 0, 0, 0, 0),      # both public handles closed at FINISH
}
PASS = 'BCPLQSAM Q5 OPEN ROLLBACK PASS'


def check(job: int, summary: str, report: str, console: str) -> list[str]:
    issues: list[str] = []
    if len(re.findall(rf'^JOB {job}\s+Q5RBOPEN\s*$', summary, re.M)) != 1:
        issues.append('wrong/missing JOB identity')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        issues.append('JES summary not a clean zero-RC completion')
    found: dict[str, list[int]] = {}
    for match in re.finditer(r'^([A-Z0-9]{2,8})\s+\S+\s+RC=(\d{4})\s*$',
                             summary, re.M):
        if match.group(1) in STEPS:
            found.setdefault(match.group(1), []).append(int(match.group(2)))
    for step in STEPS:
        if found.get(step) != [0]:
            issues.append(f'{step}: required one RC=0000; got {found.get(step)}')
    for label in ('Statements flagged', 'Highest severity'):
        match = re.search(rf'{label}:\s*(\d+)', summary)
        if match is None or int(match.group(1)) != 0:
            issues.append(label + ' not independently zero')
    records = [line.strip() for line in report.replace('\f', '').splitlines()]
    if records.count(PASS) != 1:
        issues.append('exact BCPL PASS record absent or duplicated')

    # Require an ordered, singular console interval for this precise JOB.
    lines = console.splitlines()
    starts = [i for i, row in enumerate(lines)
              if re.search(rf'\bJOB\s+{job}\s+\$HASP373\s+Q5RBOPEN STARTED', row)]
    ends = [i for i, row in enumerate(lines)
            if re.search(rf'\bJOB\s+{job}\s+\$HASP395\s+Q5RBOPEN ENDED', row)]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        issues.append('one complete JOB-correlated console interval required')
        return issues
    interval = lines[starts[0]:ends[0]+1]
    readings = []
    for row in interval:
        match = re.search(rf'\bJOB\s+{job}\s+\+Q5R:([ELX]):'
                          r'((?:[0-9A-F]{8}:){3,4}[0-9A-F]{8})(?![0-9A-F:])',
                          row)
        if match:
            readings.append((match.group(1), tuple(int(x, 16) for x in
                                                      match.group(2).split(':'))))
    if [x[0] for x in readings] != ['E', 'L', 'X']:
        issues.append('expected exactly three ordered E/L/X rollback WTOs')
    for phase, values in readings:
        if values != EXPECTED[phase]:
            issues.append(f'Q5R:{phase}: observed {values}, expected {EXPECTED[phase]}')
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, type=int)
    parser.add_argument('--summary', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--console', required=True, type=Path)
    args = parser.parse_args()
    issues = check(args.job,
                   args.summary.read_text('utf-8', errors='replace'),
                   args.report.read_text('utf-8', errors='replace'),
                   args.console.read_text('utf-8', errors='replace'))
    if issues:
        for error in issues:
            print('NOT VERIFIED:', error)
        raise SystemExit(1)
    print(f'PASS: Q5RBOPEN JOB {args.job}: real rollback CLOSE and recovery; '
          '3 native counters; GO RC=0000')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit('Q5RBOPEN evidence FAILED: ' + str(exc))
