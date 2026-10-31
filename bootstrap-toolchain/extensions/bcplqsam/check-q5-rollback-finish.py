#!/usr/bin/env python3
"""Read-only acceptance check for exactly JOB 8145 Q5RBFIN.

The test-only WTO overlay emits an extra P after X. The IFOX listing
must demonstrate the actual SVC 35 -> Q5RPST fall-through before this
precise E L P R T X P sequence can count as accepted evidence.
No JES execution, no dataset changes, and no relaxation of Q5RBTRC.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re

JOB = 8145
NAME = 'Q5RBFIN'
HEAD = '862eedcaf6290dc9f577af299bd0049cc4a1c04e'
DECK_SHA = 'e315f22394c9a0fa7118abfaf330c73869936406cebe2e1f8ae4acc7306e4b70'
ASM_SHA = 'f68e03ea2cdc8bc9a25a8f4df49c8c8cc1fd4b54056eed1a858be952b207d4ed'
STEPS = (
    ('ASMWR', 'IFOX00'), ('LKWR', 'IEWL'),
    ('ASMA', 'IFOX00'), ('ASMN', 'IFOX00'),
    ('ASMR', 'IFOX00'), ('ASMQ', 'IFOX00'),
    ('ASMG', 'IFOX00'), ('LKED', 'IEWL'),
    ('WGO', 'PGM=*.DD'), ('GO', 'PGM=*.DD'),
)
ORDER = ('E', 'L', 'P', 'R', 'T', 'X', 'P')
COUNTERS = {
    'E': '00000001:00000002:00000002:00000001',
    'L': '00000001:00000001:00000001:00000001:00000000',
    'X': '00000000:00000000:00000000:00000000:00000000',
}
WORDS = {'P': 'POST-CLEAN', 'R': 'ROLL-RETURN', 'T': 'CORE-EPILOGUE'}
PASS = 'BCPLQSAM Q5 OPEN ROLLBACK PASS'


def fallthrough_confirmed(report: str) -> bool:
    """Prove QFPEX SVC=35 is adjacent to Q5RPST in actual IFOX listing."""
    rows = report.replace('\f', '').splitlines()
    for i in range(2, len(rows) - 2):
        if not re.search(r'\bWTO\s+MF=\(E,QFXL\)\s*$', rows[i - 2]):
            continue
        if not re.search(r'\bLA\s+1,QFXL\b', rows[i - 1]):
            continue
        svc = re.match(r'^\s*([0-9A-F]{6})\s+0A23\s+\d+\+\s+SVC\s+35\b', rows[i])
        if svc is None:
            continue
        if not re.search(r'\bQ5RPST\s+WTO\s+MF=\(E,Q5RPL\)\s*$', rows[i + 1]):
            continue
        next_inst = re.match(
            r'^\s*([0-9A-F]{6})\s+4110\s+[0-9A-F]{4}\s+'
            r'[0-9A-F]{5}\s+\d+\+Q5RPST\s+LA\s+1,Q5RPL\b',
            rows[i + 2],
        )
        if next_inst and int(next_inst.group(1), 16) == int(svc.group(1), 16) + 2:
            return True
    return False


def phases(console: str, label: str) -> tuple[list[tuple[str, str]], list[str]]:
    problems = []
    rows = console.splitlines()
    start = [i for i, row in enumerate(rows) if re.search(
        rf'\bJOB\s+{JOB}\s+\$HASP373\s+{NAME}\s+STARTED\b', row)]
    end = [i for i, row in enumerate(rows) if re.search(
        rf'\bJOB\s+{JOB}\s+\$HASP395\s+{NAME}\s+ENDED\b', row)]
    if len(start) != 1 or len(end) != 1 or start[0] >= end[0]:
        return [], [label + ': exactly one complete JOB 8145 interval required']
    found = []
    pattern = rf'\bJOB\s+{JOB}\s+\+Q5R:([ELPRTX]):([A-Z0-9: -]+)\s*$'
    for row in rows[start[0]:end[0] + 1]:
        m = re.search(pattern, row)
        if m:
            found.append((m.group(1), m.group(2).strip()))
    if tuple(phase for phase, _ in found) != ORDER:
        problems.append(label + ': expected E L P R T X P exactly; observed ' +
                        ' '.join(phase for phase, _ in found))
    for phase, value in found:
        if phase in COUNTERS and value != COUNTERS[phase]:
            problems.append(f'{label}: {phase} counter mismatch: {value}')
        if phase in WORDS and value != WORDS[phase]:
            problems.append(f'{label}: {phase} marker mismatch: {value}')
    return found, problems


def check(summary: str, report: str, console: str, hardcopy: str) -> list[str]:
    problems = []
    if len(re.findall(rf'^JOB\s+{JOB}\s+{NAME}\s*$', summary, re.M)) != 1:
        problems.append('wrong/ambiguous JES summary identity')
    if summary.count('JOB RESULT: SUCCESS') != 1 or summary.count('HIGHEST RC: 0000') != 1:
        problems.append('JES not confirmed successful with highest RC 0000')
    observed = re.findall(r'^([A-Z0-9]{2,8})\s+(\S+)\s+RC=(\d{4})\s*$',
                          summary, re.M)
    if observed != [(step, pgm, '0000') for step, pgm in STEPS]:
        problems.append('ten exact IFOX/IEWL/WGO/GO step results not verified')
    for name in ('Statements flagged', 'Highest severity'):
        found = re.findall(rf'{name}:\s*(\d+)', summary)
        if found != ['0']:
            problems.append(f'assembler {name} is not exactly zero')
    if [s.strip() for s in report.replace('\f', '').splitlines()].count(PASS) != 1:
        problems.append('expected exactly one complete native BCPL PASS record')
    if not fallthrough_confirmed(report):
        problems.append('IFOX SVC 35 -> Q5RPST immediate fall-through unproven')
    got_console, errors = phases(console, '3033 console')
    problems.extend(errors)
    got_hardcopy, errors = phases(hardcopy, 'MVS hardcopy')
    problems.extend(errors)
    if got_console != got_hardcopy:
        problems.append('console and hardcopy diagnostic sequences disagree')
    return problems


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(attempt: Path, deck: Path, assembler: Path) -> list[str]:
    problems = []
    required = {
        'source-head.txt': HEAD,
        'job-number.txt': str(JOB),
        'submit.rc': '0',
        'summary.rc': '0',
        'report.rc': '0',
    }
    for name, expected in required.items():
        try:
            actual = (attempt / name).read_text('ascii').strip()
        except OSError:
            actual = '(missing)'
        if actual != expected:
            problems.append(f'{name}: expected {expected!r}, got {actual!r}')
    for file, expected, name in (
        (deck, DECK_SHA, 'prepared JCL'),
        (assembler, ASM_SHA, 'JOB 8144 compiled assembler'),
    ):
        try:
            actual = sha(file)
        except OSError:
            actual = '(missing)'
        if actual != expected:
            problems.append(f'{name} SHA-256 mismatch')
    for name, expected in (
        ('jcl.sha256', DECK_SHA), ('assembler.sha256', ASM_SHA),
    ):
        try:
            data = (attempt / name).read_text('ascii').split()
        except OSError:
            data = []
        if len(data) != 2 or data[0] != expected:
            problems.append(f'{name}: attempt digest mismatch')
    return problems


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attempt', required=True, type=Path)
    p.add_argument('--deck', required=True, type=Path)
    p.add_argument('--assembler', required=True, type=Path)
    p.add_argument('--console', required=True, type=Path)
    p.add_argument('--hardcopy', required=True, type=Path)
    args = p.parse_args()
    errors = provenance(args.attempt, args.deck, args.assembler)
    for filename in ('summary.txt', 'report.txt'):
        if not (args.attempt / filename).is_file():
            errors.append('missing evidence: ' + filename)
    if errors:
        for error in errors:
            print('NOT VERIFIED:', error)
        raise SystemExit(1)
    try:
        contents = [
            (args.attempt / 'summary.txt').read_text('utf-8', errors='replace'),
            (args.attempt / 'report.txt').read_text('utf-8', errors='replace'),
            args.console.read_text('utf-8', errors='replace'),
            args.hardcopy.read_text('utf-8', errors='replace'),
        ]
    except OSError as exc:
        raise SystemExit('Q5RBFIN evidence unavailable: ' + str(exc))
    errors = check(*contents)
    if errors:
        for error in errors:
            print('NOT VERIFIED:', error)
        raise SystemExit(1)
    print('PASS: Q5RBFIN JOB 8145 native GO RC=0000, BCPL PASS,')
    print('      six primary checkpoints E L P R T X, zero finalizer counters,')
    print('      documented test-only QFPEX -> Q5RPST extra P (IFOX-proven).')
    print('      Console and hardcopy agree. No JES submission.')


if __name__ == '__main__':
    main()
