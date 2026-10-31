#!/usr/bin/env python3
"""Check Q5RBTRC evidence, or report the last reached marker after an abend.

Read-only. A partial trace is diagnostic information, never acceptance.
The trace overlays the same compiled BCPL test as failed JOB 8142.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

ORDER = ('E', 'L', 'P', 'R', 'T', 'X')
VALUES = {
    'E': ('00000001', '00000002', '00000002', '00000001'),
    'L': ('00000001', '00000001', '00000001', '00000001', '00000000'),
    'X': ('00000000', '00000000', '00000000', '00000000', '00000000'),
}
TEXT = {'P': 'POST-CLEAN', 'R': 'ROLL-RETURN', 'T': 'CORE-EPILOGUE'}
STEPS = ('ASMWR', 'LKWR', 'ASMA', 'ASMN', 'ASMR',
         'ASMQ', 'ASMG', 'LKED', 'WGO', 'GO')
SUCCESS = 'BCPLQSAM Q5 OPEN ROLLBACK PASS'


def check(job: int, summary: str, report: str, console: str) -> list[str]:
    problems: list[str] = []
    if len(re.findall(rf'^JOB\s+{job}\s+Q5RBTRC\s*$', summary, re.M)) != 1:
        problems.append('JES job identity missing/ambiguous')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        problems.append('JES result is not zero-RC success')
    results: dict[str, list[str]] = {}
    for m in re.finditer(r'^([A-Z0-9]{2,8})\s+\S+\s+RC=(\d{4})\s*$',
                         summary, re.M):
        if m.group(1) in STEPS:
            results.setdefault(m.group(1), []).append(m.group(2))
    for step in STEPS:
        if results.get(step) != ['0000']:
            problems.append(f'{step} expected one RC=0000; observed {results.get(step)}')
    for label in ('Statements flagged', 'Highest severity'):
        m = re.search(rf'{label}:\s*(\d+)', summary)
        if m is None or int(m.group(1)) != 0:
            problems.append(label + ' not confirmed zero')
    records = [s.strip() for s in report.replace('\f', '').splitlines()]
    if records.count(SUCCESS) != 1:
        problems.append('exact BCPL PASS marker not present exactly once')

    rows = console.splitlines()
    beginnings = [i for i, s in enumerate(rows) if re.search(
        rf'\bJOB\s+{job}\s+\$HASP373\s+Q5RBTRC STARTED', s)]
    endings = [i for i, s in enumerate(rows) if re.search(
        rf'\bJOB\s+{job}\s+\$HASP395\s+Q5RBTRC ENDED', s)]
    if len(beginnings) != 1 or len(endings) != 1 or beginnings[0] >= endings[0]:
        problems.append('one complete same-JOB console interval required')
        return problems

    seen = []
    for s in rows[beginnings[0]:endings[0]+1]:
        m = re.search(rf'\bJOB\s+{job}\s+\+Q5R:([ELXPRT]):([A-Z0-9: -]+)$', s)
        if not m:
            continue
        phase, value = m.group(1), m.group(2).strip()
        seen.append(phase)
        if phase in VALUES and tuple(value.split(':')) != VALUES[phase]:
            problems.append(f'{phase} counter mismatch: {value}')
        if phase in TEXT and value != TEXT[phase]:
            problems.append(f'{phase} checkpoint mismatch: {value}')
    print('Observed Q5RBTRC phases:', ' '.join(seen) or '(none)')
    if tuple(seen) != ORDER:
        problems.append('expected exactly ordered E L P R T X; last observed = ' +
                        (seen[-1] if seen else '(none)'))
    return problems


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--job', required=True, type=int)
    p.add_argument('--summary', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--console', required=True, type=Path)
    a = p.parse_args()
    errors = check(a.job,
                   a.summary.read_text('utf-8', errors='replace'),
                   a.report.read_text('utf-8', errors='replace'),
                   a.console.read_text('utf-8', errors='replace'))
    if errors:
        for error in errors:
            print('NOT VERIFIED:', error)
        raise SystemExit(1)
    print(f'PASS: Q5RBTRC JOB {a.job}: six ordered probes and native BCPL return')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit('Q5RBTRC evidence FAILED: ' + str(exc))
