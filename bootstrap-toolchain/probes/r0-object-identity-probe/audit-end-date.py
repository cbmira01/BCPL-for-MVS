#!/usr/bin/env python3
"""R.0 Decision A: narrowly classify IEBCOMPR END run-day differences.

This reads only an existing JES text report. It never alters an object deck.
Strict binary equality always remains false when IEBCOMPR returns RC=8.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
END_PREFIX = bytes.fromhex('02C5D5C4')  # X'02' then EBCDIC 'END'
RUN_DAY = range(49, 52)              # zero-based; OBJ columns 50-52
HEX_LINE = re.compile(r'^\s*([0-9A-F]{2}){10,}\s*$')
COMPARE_TITLE = re.compile(r'^\s*COMPARE UTILITY\s+PAGE\s+\d+\s*$')
COUNT = re.compile(r'END OF JOB-TOTAL NUMBER OF RECORDS COMPARED\s*=\s*(\d+)')
LOC = re.compile(r'^\s*PHYSICAL RECORD NUMBER\s*=\s*(\d+)\s+LOGICAL RECORD NUMBER WITHIN PHYSICAL RECORD\s*=\s*(\d+)\s*$')
DD = re.compile(r'^\s*DDNAME\s*=\s*(SYSUT[12])\s*$')
ERROR = re.compile(r'\bIEB\d{3}I\b')


def verifier():
    spec = importlib.util.spec_from_file_location('r0biverify_date_audit', HERE / 'verify-report.py')
    if spec is None or spec.loader is None:
        raise ValueError('cannot load member step-code verifier')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_record(lines: list[str], i: int, label: str) -> tuple[bytes, int, int, int]:
    """Read one bounded IEBCOMPR hexadecimal DDNAME record display."""
    if i >= len(lines) or not (m := DD.fullmatch(lines[i])) or m.group(1) != label:
        raise ValueError(f'missing {label} for differing record')
    i += 1
    if i >= len(lines) or not (m := LOC.fullmatch(lines[i])):
        raise ValueError(f'missing {label} physical/logical record position')
    physical, logical = (int(x) for x in m.groups())
    i += 1
    parts = []
    while i < len(lines) and HEX_LINE.fullmatch(lines[i]):
        parts.append(lines[i].strip())
        i += 1
        if len(parts) > 4:
            raise ValueError(f'{label}: excessive record dump lines')
    hexdata = ''.join(parts)
    if len(hexdata) != 160:
        raise ValueError(f'{label}: need exactly 80 binary bytes, got {len(hexdata)//2}')
    return bytes.fromhex(hexdata), physical, logical, i


def day_of_year(record: bytes) -> int:
    # IDR1 is present (byte 33), version/year are unchanged elsewhere.
    # Accept only three EBCDIC numeric digits for the run day.
    digits = record[49:52]
    if len(digits) != 3 or any(not (0xF0 <= c <= 0xF9) for c in digits):
        raise ValueError('END run-day field is not EBCDIC decimal')
    day = int(''.join(str(c - 0xF0) for c in digits))
    if not 1 <= day <= 366:
        raise ValueError('END run-day number outside Julian day range')
    return day


def audit(report: str) -> dict:
    """Prove only printed disagreement is the END run-day (OBJ 50-52).

    This is a qualified IEBCOMPR evidence interpretation, not a second
    raw-binary comparison or a provenance/cryptographic attestation.
    """
    observed = verifier().verify('member', report)
    if observed['status'] == 'REPORTED_EQUAL':
        raise ValueError('strict comparison already equal; no run-day exception applies')
    if observed['status'] != 'RC8_REVIEW_INEQUALITY_OR_ERROR':
        raise ValueError('not an RC=8 unequal-record report')
    punched = observed['ifo_x_object_records'][0]
    lines = report.splitlines()
    headings = [i for i, line in enumerate(lines) if COMPARE_TITLE.fullmatch(line)]
    if len(headings) != 1:
        raise ValueError(f'expected one COMPARE SYSPRINT section, got {len(headings)}')
    section = lines[headings[0] + 1:]
    ends = [i for i, line in enumerate(section) if COUNT.search(line)]
    if len(ends) != 1:
        raise ValueError('missing or repeated IEBCOMPR completed-record count')
    section = section[:ends[0] + 1]
    if [line.strip() for line in section if line.strip() == 'COMPARE TYPORG=PS'] != ['COMPARE TYPORG=PS']:
        raise ValueError('expected one sequential IEBCOMPR COMPARE TYPORG=PS operation')
    count = int(COUNT.search(section[-1]).group(1))
    if count != punched or count == 0:
        raise ValueError(f'compared {count} records, IFOX punched {punched}')
    messages = [m.group(0) for line in section for m in ERROR.finditer(line)]
    if messages != ['IEB221I']:
        raise ValueError(f'not precisely one IEB221I discrepancy: {messages}')
    starts = [i for i, line in enumerate(section) if re.match(r'^\s*IEB221I\s+RECORDS ARE NOT EQUAL\s*$', line)]
    if len(starts) != 1:
        raise ValueError('missing precise IEB221I mismatch header')
    i = starts[0] + 1
    installed, ap, al, i = read_record(section, i, 'SYSUT1')
    rebuilt, bp, bl, i = read_record(section, i, 'SYSUT2')
    if i != len(section) - 1:
        raise ValueError('unexpected content after discrepancy record dump')
    if (ap, al) != (bp, bl) or ap < 1 or not (1 <= al <= 10):
        raise ValueError('different/out-of-bounds SYSUT1/SYSUT2 record positions')
    if (ap-1)*10 + al != count:  # FB80, BLKSIZE=800; END must be last.
        raise ValueError('unequal record is not the final logical FB/80 record')
    if not installed.startswith(END_PREFIX) or not rebuilt.startswith(END_PREFIX):
        raise ValueError('disagreement is not between OBJ END records')
    if installed[32] != 0xF1 or rebuilt[32] != 0xF1:
        raise ValueError('END record does not identify one assembler IDR')
    if any(not (0xF0 <= c <= 0xF9) for c in installed[47:49]):
        raise ValueError('END run year is not EBCDIC decimal')
    if any(not (0xF0 <= c <= 0xF9) for c in rebuilt[47:49]):
        raise ValueError('rebuilt END run year is not EBCDIC decimal')
    # Only these three bytes may differ. All other IDR fields including
    # assembler ID/version/revision/year and the END sequence must match.
    differences = [j for j in range(80) if installed[j] != rebuilt[j]]
    if not differences or any(j not in RUN_DAY for j in differences):
        raise ValueError(f'differences outside allowed OBJ columns 50-52: {[j+1 for j in differences]}')
    old_day, new_day = day_of_year(installed), day_of_year(rebuilt)
    year = installed[47:49].decode('cp037')
    return {'classification': 'CONTENT_EQUAL_EXCEPT_END_RUN_DAY',
            'strict_binary_identity': False, 'normalized_content_identity': True,
            'records_compared': count, 'differing_record': count,
            'differing_columns_1_based': [j+1 for j in differences],
            'ignored_columns_1_based': [50, 51, 52],
            'run_year_2_digit': year, 'installed_run_day': old_day,
            'rebuilt_run_day': new_day,
            'note': 'IEBCOMPR discrepancy-only evidence; not a normalized raw-object export'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job_report', type=Path, help='Complete existing R0BIMEM JES report')
    args = parser.parse_args()
    try:
        result = audit(args.job_report.read_text('utf-8'))
    except (OSError, ValueError) as exc:
        raise SystemExit(f'R.0 END run-day audit REJECTED: {exc}')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
