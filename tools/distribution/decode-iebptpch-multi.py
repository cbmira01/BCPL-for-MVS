#!/usr/bin/env python3
"""TA.0: decode cursor-pinned, multi-member IEBPTPCH FB80 printer evidence.

Does not submit MVS JCL, modify MVS datasets, or establish source lineage.
The independently observed record count is UNKNOWN unless provided separately.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
# Centralized, symlink-safe ignored-workarea evidence policy.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path
SOURCE = Path(__file__).with_name('decode-iebptpch-readback.py')
MAX_REPORT = 32 * 1024 * 1024
MAX_RAW = 64 * 1024 * 1024
MAX_RECORDS = 100000
MAX_MEMBERS = 20
DSN = re.compile(r'[A-Z@$#][A-Z0-9@$#-]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#-]{0,7}){1,}\Z')
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
SOURCE_FILES = frozenset({
    'cursor.json', 'job-body-redacted.jcl', 'job-summary.txt',
    'job-report.txt', 'printer-window.raw',
})
PAGE_TITLE = re.compile(r'^PRINT/PUNCH DATA SET UTILITY\s+PAGE\s+\d{4}\s*$')
JOB_PAGES = re.compile(r'^\s*PAGE\s+\d{4}\s*$')


class MultiError(ValueError):
    """Missing, ambiguous or unsupported MVS evidence."""


def need(yes: bool, message: str) -> None:
    if not yes:
        raise MultiError(message)


def module():
    spec = importlib.util.spec_from_file_location('ta0_single_decoder', SOURCE)
    if spec is None or spec.loader is None:
        raise MultiError('single-member decoder is unavailable')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def safe_file(directory: Path, name: str, *, limit: int) -> bytes:
    path = directory / name
    need(path.is_file() and not path.is_symlink(), f'not a plain evidence file: {name}')
    need(path.stat().st_size <= limit, f'evidence file exceeds limit: {name}')
    return path.read_bytes()


def load_evidence(directory: Path) -> tuple[dict[str, Any], str, dict[str, str]]:
    """Verify all five original evidence file pins BEFORE trusting any report."""
    try:
        guard_evidence_path(directory, new=False, root=ROOT)
    except ValueError as exc:
        raise MultiError('evidence directory must be under repository workarea/') from exc
    original = safe_file(directory, 'receipt.json', limit=1024 * 1024)
    try:
        receipt = json.loads(original)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise MultiError('invalid evidence receipt JSON') from exc
    need(type(receipt) is dict, 'invalid evidence receipt root')
    need(receipt.get('phase') == 'TA.0 MVS READBACK PILOT — NOT BINARY/RELEASE ACCEPTANCE',
         'receipt phase does not identify approved pilot')
    job = receipt.get('job')
    jobname = receipt.get('jobname')
    members = receipt.get('requested_members')
    single = module()
    need(type(job) is int and 1 <= job <= 9999, 'invalid JES job number in receipt')
    need(type(jobname) is str and single.MEMBER.fullmatch(jobname) is not None,
         'invalid jobname in receipt')
    need(receipt.get('step') == 'TA0HEX', 'unexpected MVS step')
    need(receipt.get('dataset_key') in ('MR10_OBJ', 'BOOT_OBJ', 'EXT_OBJ'),
         'dataset is not a selected FB80 object PDS')
    dsn = receipt.get('source_dataset')
    need(type(dsn) is str and len(dsn) <= 44 and DSN.fullmatch(dsn) is not None,
         'invalid selected source dataset')
    need(type(members) is list and 1 <= len(members) <= MAX_MEMBERS and
         all(type(m) is str and single.MEMBER.fullmatch(m) is not None for m in members)
         and len(set(members)) == len(members), 'invalid or duplicate selected members')
    pins = receipt.get('sha256')
    need(type(pins) is dict and pins.keys() == SOURCE_FILES,
         'missing or additional saved evidence file pins')
    for name, expected in pins.items():
        need(type(expected) is str and SHA256.fullmatch(expected) is not None,
             f'invalid saved digest: {name}')
    files = {}
    for name in sorted(SOURCE_FILES):
        contents = safe_file(directory, name,
                             limit=MAX_RAW if name == 'printer-window.raw' else MAX_REPORT)
        need(hashlib.sha256(contents).hexdigest() == pins[name],
             f'evidence digest mismatch: {name}')
        files[name] = contents
    try:
        report = files['job-report.txt'].decode('utf-8')
        summary = files['job-summary.txt'].decode('utf-8')
        deck = files['job-body-redacted.jcl'].decode('ascii')
    except UnicodeError as exc:
        raise MultiError('unsupported text encoding in retained evidence') from exc
    need(f'JOB {job}' in summary and jobname in summary and
         re.search(r'\bTA0HEX\s+IEBPTPCH\s+RC=0000\b', summary) is not None,
         'saved job-summary does not confirm the expected successful job')
    need(f'//SYSUT1   DD DSN={dsn},DISP=SHR\n' in deck,
         'saved job body does not match claimed input dataset')
    need(f'PRINT TYPORG=PO,TOTCONV=XE,MAXNAME={len(members)}' in deck,
         'saved job body does not match member count')
    need(re.findall(r'^\s*MEMBER NAME=([A-Z@$#][A-Z0-9@$#]{0,7})\s*$', deck, re.M) == members,
         'saved job body does not match selected member order')
    return receipt, report, {name: hashlib.sha256(content).hexdigest()
                             for name, content in files.items()}


def verify_job(report: str, *, job: int, jobname: str, members: list[str]) -> None:
    """Reject inconsistent JES/IEBPTPCH identity, nonzero RC and unexpected controls."""
    need('\x00' not in report, 'NUL in report')
    need('END OF DATA FOR SDS OR MEMBER' in report,
         'missing IEBPTPCH end-of-data evidence')
    number = len(members)
    ctrl = re.findall(r'^\s*PRINT\s+TYPORG=PO,TOTCONV=XE,MAXNAME=(\d+)\s*$',
                      report, re.M)
    need(ctrl == [str(number)], 'IEBPTPCH control statement mismatch or duplicate')
    selected = re.findall(r'^\s*MEMBER NAME=([A-Z@$#][A-Z0-9@$#]{0,7})\s*$',
                          report, re.M)
    need(selected == members, 'IEBPTPCH control-member order does not match receipt')
    start = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP373\s+' +
                       re.escape(jobname) + r'\s+STARTED\b', report, re.M)
    need(start == [str(job)], 'missing or duplicate JES START identity')
    end = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP395\s+' +
                     re.escape(jobname) + r'\s+ENDED\b', report, re.M)
    need(end == [str(job)], 'missing or duplicate JES END identity')
    step = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+' + re.escape(jobname) +
                      r'\s+TA0HEX\s+IEBPTPCH\s+RC=\s*0000\s*$', report, re.M)
    need(step == [str(job)], 'IEBPTPCH TA0HEX RC=0000 not uniquely proven')
    ief = re.findall(r'^IEF142I\s+' + re.escape(jobname) +
                     r'\s+TA0HEX\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE 0000\s*$',
                     report, re.M)
    need(len(ief) == 1, 'IEF142I TA0HEX RC=0000 not uniquely proven')
    need(re.search(r'\b(?:IEF450I|IEF472I|IEA995I)\b', report) is None,
         'potential ABEND message in report')


def parse_member_records(lines: list[str], *, name: str, last: bool, single) -> tuple[bytes, list[int], int]:
    raw = bytearray()
    block_ends = []
    n = 0
    i = 0
    trailing = False
    while i < len(lines):
        line = lines[i].rstrip(' ')
        if not line or JOB_PAGES.fullmatch(line) or PAGE_TITLE.fullmatch(line):
            i += 1
            continue
        if single.FIRST.fullmatch(line):
            need(not trailing, f'{name}: additional binary data after printer trailer')
            need(n < MAX_RECORDS, f'{name}: exceeds record-count limit')
            need(i + 1 < len(lines), f'{name}: last record is truncated')
            next_line = lines[i + 1].rstrip(' ')
            match = single.SECOND.fullmatch(next_line)
            need(match is not None, f'{name}: invalid 32-byte record continuation')
            second, marker = match.groups()
            data = bytes.fromhex(''.join(line.split('  ') + second.split('  ')))
            need(len(data) == 80, f'{name}: not an FB80 record')
            raw.extend(data)
            n += 1
            if marker == '**':
                block_ends.append(n)
            i += 2
            continue
        need(single.SECOND.fullmatch(line) is None,
             f'{name}: unattached 32-byte record continuation')
        if last and n and block_ends and block_ends[-1] == n:
            # Hercules printer art follows the utility's final member. No
            # further hex records or member headings are permitted anywhere.
            trailing = True
            i += 1
            continue
        raise MultiError(f'{name}: unexpected content in member body (line {i + 1})')
    need(n > 0, f'{name}: no binary records printed')
    need(block_ends and block_ends[-1] == n,
         f'{name}: no final FB block boundary before next member/end')
    return bytes(raw), block_ends, n


def decode_multi(report: str, *, job: int, jobname: str,
                 members: list[str], expected: dict[str, int] | None = None) -> dict[str, tuple[bytes, dict]]:
    single = module()
    verify_job(report, job=job, jobname=jobname, members=members)
    lines = report.replace('\r', '').replace('\f', '\n').splitlines()
    # IEBPTPCH repeats a member heading at every printed PAGE (JOB 9048).
    # Fold only sequential same-member page continuations, never logical
    # member transitions or malformed/missing records.
    page_source = Path(__file__).with_name('iebptpch-page-framing.py')
    page_spec = importlib.util.spec_from_file_location('ta0_iebptpch_page_framing', page_source)
    need(page_spec is not None and page_spec.loader is not None,
         'IEBPTPCH page-continuation validator is unavailable')
    pages = importlib.util.module_from_spec(page_spec)
    page_spec.loader.exec_module(pages)
    lines, headers, page_repeats = pages.coalesce_page_headings(
        lines, members=members, header=single.HEADER,
        first=single.FIRST, second=single.SECOND, require=need)
    need(expected is None or set(expected) == set(members),
         'expected record counts must cover all selected members')
    result = {}
    for offset, (start, name) in enumerate(headers):
        end = headers[offset + 1][0] if offset + 1 < len(headers) else len(lines)
        raw, blocks, count = parse_member_records(
            lines[start + 1:end], name=name, last=offset == len(headers) - 1,
            single=single)
        if expected is not None:
            need(expected[name] == count,
                 f'{name}: observed {count} records, expected {expected[name]}')
        result[name] = (raw, {
            'member': name,
            'job': job,
            'record_count': count,
            'record_length': 80,
            'byte_count': len(raw),
            'block_end_records': blocks,
            'sha256_of_decoded_print': hashlib.sha256(raw).hexdigest(),
            'expected_records_supplied': expected is not None,
            'repeated_page_headings': page_repeats[name],
            'qualification': 'PRINT-ONLY; NO INDEPENDENT DASD BYTE OR SOURCE PROVENANCE',
        })
    return result


def parse_expected(raw: list[str], members: list[str]) -> dict[str, int] | None:
    if not raw:
        return None
    result: dict[str, int] = {}
    for item in raw:
        key, separator, count = item.partition(':')
        need(separator == ':' and key in members and key not in result and
             count.isascii() and count.isdecimal() and 0 < int(count) <= MAX_RECORDS,
             'invalid --expected-records entry; use MEMBER:POSITIVE_COUNT')
        result[key] = int(count)
    need(set(result) == set(members), 'expected counts must cover every selected member')
    return result


def private_write(path: Path, contents: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as target:
        target.write(contents)


def process(evidence: Path, output: Path, *, expected_counts: list[str]) -> dict:
    try:
        guard_evidence_path(output, new=True, root=ROOT)
    except ValueError as exc:
        raise MultiError('output must be a new directory under repository workarea/') from exc
    receipt, report, pins = load_evidence(evidence)
    members = receipt['requested_members']
    expected = parse_expected(expected_counts, members)
    decoded = decode_multi(report, job=receipt['job'], jobname=receipt['jobname'],
                           members=members, expected=expected)
    summary = {
        'phase': 'TA.0 — DECODED MULTI-MEMBER IEBPTPCH PRINTER REPORT',
        'source_job': receipt['job'], 'source_jobname': receipt['jobname'],
        'source_dataset': receipt['source_dataset'],
        'source_receipt_sha256': hashlib.sha256(
            safe_file(evidence, 'receipt.json', limit=1024*1024)).hexdigest(),
        'source_report_sha256': pins['job-report.txt'],
        'source_printer_window_sha256': pins['printer-window.raw'],
        'members': [meta for _, meta in decoded.values()],
        'qualification': [
            'Record counts are derived from printed output; optional expected counts are operator assertions, not independent source verification.',
            'Printer text extraction is not an independent DASD byte comparison.',
            'No source-to-MVS revision binding, rights review or tape acceptance.',
        ],
    }
    os.mkdir(output, 0o700)
    for name, (binary, meta) in decoded.items():
        private_write(output / f'{name}.fb80', binary)
        private_write(output / f'{name}.fb80.json',
                      (json.dumps(meta, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    private_write(output / 'decode-receipt.json',
                  (json.dumps(summary, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True, type=Path,
                        help='existing private directory written by submit-iebptpch-pilot.py')
    parser.add_argument('--output-dir', required=True, type=Path,
                        help='new private directory under repository workarea/')
    parser.add_argument('--expected-records', action='append', default=[],
                        help='optional independent MEMBER:COUNT; specify once for each member')
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        receipt = process(args.evidence_dir, args.output_dir,
                          expected_counts=args.expected_records)
    except (MultiError, OSError, ValueError, UnicodeError) as exc:
        print(f'TA.0 MULTI READBACK FAIL: {exc}', file=sys.stderr)
        return 1
    print(f"TA.0 JOB {receipt['source_job']} multi-member printer readback:")
    for member in receipt['members']:
        print(f"  {member['member']}: {member['record_count']} FB80 records, "
              f"{member['byte_count']} bytes, SHA-256={member['sha256_of_decoded_print']}")
    print('Observed printer-output bytes only; source/DASD identity remains unverified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
