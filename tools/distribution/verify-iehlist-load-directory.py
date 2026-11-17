#!/usr/bin/env python3
"""TA.0: inspect pinned JOB 9060-style IEHLIST FORMAT evidence, without JES calls.

A formatted PDS directory can show a load-module directory entry. It cannot
validate the module's data bytes, executability, or tape restore fidelity.
The raw job report is never printed, nor copied to Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
# Centralized, symlink-safe ignored-workarea evidence policy.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path
EXPECTED_PHASE = 'TA.0 LOAD DIRECTORY PILOT — NOT LOAD BYTE OR RELEASE ACCEPTANCE'
FILES = frozenset(('cursor.json', 'job-body.jcl', 'job-summary.txt',
                   'job-report.txt', 'printer-window.raw'))
DCB = {'dsorg': 'PO', 'recfm': 'U', 'lrecl': 0, 'blksize': 6144}
MAX_BYTES = 64 * 1024 * 1024
NAME = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}\Z')
DSN = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+\Z')
VOLSER = re.compile(r'[A-Z0-9]{1,6}\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')
HEADING = re.compile(r'\bMEMBER\s+ENTRY\s+ATTR\b')
ROW = re.compile(r'^\s*([A-Z@$#][A-Z0-9@$#]{0,7})(\*?)\s+([0-9A-F]{6})\s+([0-9A-F]{4})(?:\s|$)')
TITLE = re.compile(r'\bSYSTEMS SUPPORT UTILITIES\s*-{2,}\s*IEHLIST\b')
DIR = re.compile(r'^\s*DIRECTORY INFO FOR SPECIFIED PDS ON VOL\s+([A-Z0-9]{1,6})\s*$')
FOOT = re.compile(r'^\s*OF THE\s+\d+\s+DIRECTORY BLOCKS ALLOCATED TO THIS PDS\b')


class EvidenceError(ValueError):
    pass


def need(test: bool, message: str) -> None:
    if not test:
        raise EvidenceError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_bytes(folder: Path, name: str, limit: int = MAX_BYTES) -> bytes:
    path = folder / name
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= limit,
         'MISSING_OR_UNSAFE_EVIDENCE')
    return path.read_bytes()


def check_paths(evidence: Path, output: Path) -> None:
    try:
        guard_evidence_path(evidence, new=False, root=ROOT)
    except ValueError as exc:
        raise EvidenceError('BAD_EVIDENCE_LOCATION') from exc
    try:
        guard_evidence_path(output, new=True, root=ROOT)
    except ValueError as exc:
        raise EvidenceError('BAD_OUTPUT_LOCATION') from exc

def pinned_files(folder: Path) -> tuple[dict, dict[str, bytes]]:
    try:
        receipt = json.loads(file_bytes(folder, 'receipt.json', 1024 * 1024))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError('INVALID_RECEIPT') from exc
    need(type(receipt) is dict and receipt.get('phase') == EXPECTED_PHASE,
         'INVALID_RECEIPT_PHASE')
    job = receipt.get('job')
    dsn = receipt.get('dsn')
    volume = receipt.get('source_volume')
    need(type(job) is int and 1 <= job <= 9999 and receipt.get('jobname') == 'TA0LDIR'
         and receipt.get('dataset_key') == 'MR10_LOAD'
         and receipt.get('member') == 'ICINT19', 'WRONG_JOB_OR_MEMBER')
    need(type(dsn) is str and DSN.fullmatch(dsn) is not None
         and type(volume) is str and VOLSER.fullmatch(volume) is not None
         and receipt.get('source_dcb') == DCB
         and receipt.get('directory_utility') == 'IEHLIST LISTPDS FORMAT',
         'WRONG_SOURCE_OR_DCB')
    pins = receipt.get('sha256')
    need(type(pins) is dict and pins.keys() == FILES,
         'INVALID_PINNED_FILES')
    for name, digest in pins.items():
        need(type(digest) is str and HEX.fullmatch(digest) is not None,
             'INVALID_DIGEST')
    contents = {name: file_bytes(folder, name) for name in sorted(FILES)}
    for name, data in contents.items():
        need(sha(data) == pins[name], 'ATTACHMENT_HASH_MISMATCH')
    return receipt, contents


def validate_report(receipt: dict, files: dict[str, bytes]) -> str:
    try:
        report = files['job-report.txt'].decode('utf-8')
        summary = files['job-summary.txt'].decode('utf-8')
        body = files['job-body.jcl'].decode('ascii')
    except UnicodeError as exc:
        raise EvidenceError('INVALID_TEXT_ENCODING') from exc
    job = str(receipt['job'])
    name = receipt['jobname']
    need('\x00' not in report and '\x00' not in summary and '\x00' not in body,
         'INVALID_REPORT_BYTES')
    start = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP373\s+' + name + r'\s+STARTED\b', report, re.M)
    end = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP395\s+' + name + r'\s+ENDED\b', report, re.M)
    step = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+' + name + r'\s+DIRLIST\s+IEHLIST\s+RC=\s*0000\s*$', report, re.M)
    need(start == [job] and end == [job] and step == [job], 'JES_IDENTITY_OR_RC_MISMATCH')
    need(len(re.findall(r'^IEF142I\s+' + name + r'\s+DIRLIST\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE 0000\s*$', report, re.M)) == 1,
         'MVS_STEP_RC_MISMATCH')
    need(not re.search(r'\b(?:IEF450I|IEF472I|IEA995I)\b', report),
         'POTENTIAL_ABEND')
    need(re.search(r'^JOB\s+' + job + r'\s+' + name + r'\b', summary, re.M) is not None and
         re.search(r'\bDIRLIST\s+IEHLIST\s+RC=0000\b', summary) is not None,
         'JOB_SUMMARY_MISMATCH')
    need(body.count('//DIRLIST  EXEC PGM=IEHLIST') == 1
         and f'LISTPDS DSNAME={receipt["dsn"]},' in body
         and 'FORMAT' in body and 'DISP=SHR' in body
         and f'={receipt["source_volume"]},FORMAT' in body,
         'JOB_BODY_MISMATCH')
    return report


def parse_directory(report: str, *, dsn: str, volser: str,
                    member: str) -> dict:
    """Conservatively recognize an IEHLIST edited PDS directory section.

    Require a title and directory section, then a typed member row *after*
    the MEMBER/ENTRY/ATTR column headings. Echoed control cards never count.
    """
    lines = report.replace('\r', '').replace('\f', '\n').splitlines()
    need(any(TITLE.search(line) for line in lines), 'IEHLIST_FORMAT_UNRECOGNIZED')
    beginnings = [(i, m.group(1)) for i, line in enumerate(lines)
                  if (m := DIR.fullmatch(line))]
    need(len(beginnings) == 1 and beginnings[0][1] == volser,
         'DIRECTORY_VOLUME_MISMATCH_OR_MISSING')
    begin = beginnings[0][0]
    # A standalone DSN in the formatted section binds the directory to the
    # library. The JCL control echo alone does not establish that association.
    need(any(line.strip() == dsn for line in lines[begin+1:begin+15]),
         'DIRECTORY_DATASET_MISMATCH_OR_MISSING')
    headings = [i for i in range(begin+1, len(lines)) if HEADING.search(lines[i])]
    need(len(headings) >= 1 and headings[0] <= begin + 90,
         'MEMBER_COLUMNS_MISSING')
    found = []
    other = 0
    first = headings[0]
    seen_footer = False
    for line in lines[first+1:]:
        if FOOT.search(line):
            seen_footer = True
            break
        if (match := ROW.match(line)):
            n, alias, entry, attributes = match.groups()
            if n == member:
                found.append((alias, entry, attributes))
            else:
                other += 1
    need(seen_footer, 'DIRECTORY_FOOTER_MISSING')
    need(len(found) == 1 and found[0][0] == '',
         'MEMBER_ROW_MISSING_DUPLICATED_OR_ALIAS')
    alias, entry, attributes = found[0]
    # Preserve bit field, but do not interpret the EXEC bit or claim program
    # execution from IEHLIST directory metadata.
    return {'member': member, 'entry_point_hex': entry,
            'attributes_hex': attributes, 'other_member_rows': other,
            'directory_volume': volser, 'directory_dataset': dsn,
            'format': 'IEHLIST EDITED PDS DIRECTORY',
            'status': 'MEMBER_DIRECTORY_ENTRY_OBSERVED_NOT_BINARY_VERIFICATION'}


def verify(evidence: Path, output: Path) -> dict:
    check_paths(evidence, output)
    receipt, files = pinned_files(evidence)
    report = validate_report(receipt, files)
    detail = parse_directory(report, dsn=receipt['dsn'],
                             volser=receipt['source_volume'],
                             member=receipt['member'])
    result = {
        'phase': 'TA.0 IEHLIST LOAD DIRECTORY REVIEW ONLY',
        'job': receipt['job'], 'jobname': receipt['jobname'],
        'source_receipt_sha256': sha(file_bytes(evidence, 'receipt.json', 1024*1024)),
        'source_job_report_sha256': sha(files['job-report.txt']),
        'source_printer_window_sha256': sha(files['printer-window.raw']),
        'directory': detail,
        'qualifications': [
            'IEHLIST formatted directory only; not a byte-level load module proof.',
            'No load-module execution, IEBCOPY unload/restore, source revision or tape validation.',
            'The 14 FB80 object-member printer hashes are separate evidence.',
        ],
    }
    os.mkdir(output, 0o700)
    path = output / 'directory-review.json'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os,'O_NOFOLLOW',0), 0o600)
    with os.fdopen(fd, 'wb') as target:
        target.write((json.dumps(result, indent=2, sort_keys=True)+'\n').encode('utf-8'))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        result = verify(args.evidence_dir, args.output_dir)
    except (EvidenceError, OSError, UnicodeError) as exc:
        code = str(exc) if isinstance(exc, EvidenceError) else 'IO_OR_ENCODING_ERROR'
        print(f'TA.0 IEHLIST REVIEW REFUSED: {code}', file=sys.stderr)
        print('Preserved original evidence; no JES job submitted.', file=sys.stderr)
        return 1
    item = result['directory']
    print(f"TA.0 LOAD DIRECTORY JOB {result['job']}: {item['member']} observed, "
          f"entry={item['entry_point_hex']} attr={item['attributes_hex']}")
    print('Directory evidence only; no load bytes or executable-use verified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
