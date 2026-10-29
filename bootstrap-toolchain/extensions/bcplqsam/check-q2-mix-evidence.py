#!/usr/bin/env python3
"""Fail-closed review of real Q2MIX JES, IFOX, IEWL and GO evidence.

BGO emits the BCPL marker; VGO independently GETs the FB80 record.
IEWL's application MAP must hold both descriptors and 60-byte BCPLREG.
No physical DD attribution is inferred from combined SYSOUT.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

STEPS = ('ASMA', 'ASMV', 'ASMN', 'ASMR', 'ASMQ', 'ASMG',
         'LKED', 'LKVR', 'BGO', 'VGO')
MARKERS = ('Q2 MIX BCPLQSAM BCPLDEMO WRITTEN PASS',
           'Q2 MIX BCPLQSAM BCPLDEMO FB80 EXACT PASS')
ENTRY = re.compile(
    r'(?im)^[ \t\f]*[01+]?[ \t\f]*ENTRY[ \t]+ADDRESS[ \t]+'
    r'([0-9A-F]{1,8})[ \t]*$')


def check(summary: str, report: str) -> list[str]:
    errors: list[str] = []
    if len(re.findall(r'^JOB\s+\d+\s+Q2MIX\s*$', summary, re.M)) != 1:
        errors.append('Q2MIX JOB identity missing or duplicated')
    got: dict[str, list[int]] = {}
    for line in summary.splitlines():
        match = re.match(
            r'^\s*(ASMA|ASMV|ASMN|ASMR|ASMQ|ASMG|LKED|LKVR|BGO|VGO)'
            r'\s+\S.*?\bRC=(\d{4})\s*$', line)
        if match:
            got.setdefault(match.group(1), []).append(int(match.group(2)))
    if set(got) != set(STEPS):
        errors.append('native ten-step coverage incomplete')
    for step in STEPS:
        value = got.get(step, [])
        want = 8 if step == 'BGO' else 0
        if value != [want]:
            errors.append(f'{step}: expected sole RC={want:04d}, got {value}')
    for label in ('Statements flagged', 'Highest severity'):
        match = re.search(rf'{label}:\s*(\d+)', summary)
        if not match or int(match.group(1)) != 0:
            errors.append(label + ' not proven zero')
    if 'JOB RESULT: SUCCESS' not in summary:
        errors.append('JES job success absent')

    records = [r.strip() for r in report.replace('\f', '').splitlines()]
    for marker in MARKERS:
        if records.count(marker) != 1:
            errors.append('missing/duplicate exact native record: ' + marker)
    if all(m in records for m in MARKERS):
        if records.index(MARKERS[0]) >= records.index(MARKERS[1]):
            errors.append('independent verification did not follow BCPL')
    if any(re.match(r'^Q2 MIX FAIL\b', r) for r in records):
        errors.append('BCPL application emitted failure')

    chunks = report.replace('\f', '').split('CROSS REFERENCE TABLE')
    if len(chunks) != 3:
        errors.append('expected two IEWL CROSS REFERENCE TABLEs')
    else:
        maps = [c.split('LOCATION  REFERS TO SYMBOL', 1)[0]
                for c in chunks[1:]]
        def entries(mapping: str) -> dict[str, list[int]]:
            found: dict[str, list[int]] = {}
            for name, length in re.findall(
                r'(?m)^  ([A-Z0-9@$#]{1,8})\s+'
                r'[0-9A-F]{1,8}\s+([0-9A-F]{1,8})\s*$',
                mapping):
                found.setdefault(name, []).append(int(length, 16))
            return found
        first, second = (entries(m) for m in maps)
        for name, length in (
            ('R0APP', None), ('BCPLMAIN', None), ('RGINIT', None),
            ('QSMDESC', 56), ('QSMDISP', None),
            ('DMODESC', 56), ('DMODISP', None), ('BCPLREG', 60)):
            present = first.get(name, [])
            if len(present) != 1 or (
                length is not None and present[0] != length):
                errors.append(f'IEWL application {name}: {present}, want {length}')
        for name in ('TIMDESC', 'TIMDISP'):
            if first.get(name):
                errors.append('unselected extension present: ' + name)
        if len(second.get('Q2MVER', [])) != 1:
            errors.append('independent verifier missing from IEWL MAP')
        if second.get('QSMDESC') or second.get('DMODESC'):
            errors.append('verifier must not link optional packages')
    addresses = ENTRY.findall(report)
    if len(addresses) != 2 or any(int(x, 16) != 0 for x in addresses):
        errors.append('expected two zero-valued IEWL ENTRY ADDRESS fields')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--summary', required=True, type=Path)
    ap.add_argument('--report', required=True, type=Path)
    args = ap.parse_args()
    errors = check(
        args.summary.read_text('latin-1'),
        args.report.read_text('latin-1'))
    print('Q2MIX NATIVE EVIDENCE: ' + ('NOT VERIFIED' if errors else 'PASS'))
    for item in errors:
        print(' - ' + item)
    if not errors:
        print('Two required BCEX packages, 60-byte BCPLREG, verified FB80')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
