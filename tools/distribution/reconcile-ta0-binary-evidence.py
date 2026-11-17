#!/usr/bin/env python3
"""TA.0: reconcile retained printer, IEHLIST and ICINT19 execution evidence.

No JES submission, no tape I/O, no change to resident MVS libraries.  This
re-checks the original pinned evidence and records the *limited* observations,
not source-to-DASD identity, redistribution approval or tape acceptance.
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

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard
from ta0_receipt_compat import metadata_schema

MANIFEST = ROOT / 'packaging/distribution/manifest/ta0-inventory.yaml'
LEDGER = ROOT / 'packaging/distribution/manifest/ta0-fb80-readback-acceptance-evidence-20261117.md'
DECODER = ROOT / 'tools/distribution/decode-iebptpch-multi.py'
PILOT = ROOT / 'tools/distribution/verify-icint19-executable.py'
TRIAGE = ROOT / 'tools/distribution/inspect-icint19-failed-pilot.py'
KEYS = {'EXT_OBJ': 'E', 'MR10_OBJ': 'M', 'BOOT_OBJ': 'B'}
DIRS = {'EXT_OBJ': 'ta0-ext-single-panel', 'MR10_OBJ': 'ta0-mr10-single-panel',
        'BOOT_OBJ': 'ta0-boot-single-panel'}
ROW = re.compile(r'^\|\s*(EXT_OBJ|MR10_OBJ|BOOT_OBJ)\s*\|\s*([A-Z0-9]{1,8})\s*\|\s*(\d{1,4})\s*\|\s*(\d+)\s*\|\s*`([0-9a-f]{64})`\s*\|$')
HEX = re.compile(r'[0-9a-f]{64}\Z')
MAXJSON = 1024 * 1024
MAXOBJ = 8 * 1024 * 1024


class ReconcileError(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise ReconcileError(code)


def read(path: Path, limit: int = MAXJSON) -> bytes:
    need(path.is_file() and not path.is_symlink() and path.stat().st_size <= limit,
         'MISSING_OR_UNSAFE_FILE')
    return path.read_bytes()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def js(path: Path) -> dict:
    try:
        obj = json.loads(read(path).decode('utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise ReconcileError('INVALID_JSON') from exc
    need(type(obj) is dict, 'EXPECTED_JSON_OBJECT')
    return obj


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'VALIDATOR_MISSING')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def selected() -> dict[str, list[str]]:
    inventory = yaml.safe_load(read(MANIFEST, MAXOBJ))
    need(type(inventory) is dict and inventory.get('phase') == 'design', 'MANIFEST_NOT_DESIGN')
    need(type(inventory.get('datasets')) is list, 'MANIFEST_DATASETS_INVALID')
    result = {}
    for row in inventory.get('datasets', []):
        if type(row) is dict and row.get('dspal_key') in KEYS:
            key = row['dspal_key']
            need(key not in result and row.get('target_dcb') == {
                'dsorg': 'PO', 'recfm': 'FB', 'lrecl': 80, 'blksize': 800},
                'MANIFEST_DCB_OR_SOURCE_MISMATCH')
            names = row.get('members')
            need(type(names) is list and names and len(names) == len(set(names)),
                 'MANIFEST_MEMBER_LIST_INVALID')
            result[key] = names
    need(set(result) == set(KEYS) and sum(map(len, result.values())) == 14,
         'MANIFEST_BINARY_SELECTION_CHANGED')
    return result


def reported() -> dict[tuple[str, str], tuple[int, int, str]]:
    result = {}
    text = read(LEDGER, MAXOBJ).decode('utf-8')
    for line in text.splitlines():
        m = ROW.fullmatch(line)
        if m:
            key, member, job, records, hash_hex = m.groups()
            need((key, member) not in result, 'LEDGER_DUPLICATE_MEMBER')
            result[(key, member)] = int(job), int(records), hash_hex
    need(len(result) == 14 and sum(r[1] for r in result.values()) == 902,
         'LEDGER_SELECTION_OR_RECORD_TOTAL_CHANGED')
    return result


def one_panel(decoder, base: Path, key: str, members: list[str], ledger: dict) -> list[dict]:
    folder = base / DIRS[key]
    guard(folder, new=False, root=ROOT)
    panel = js(folder / 'panel-receipt.json')
    need(panel.get('phase') in (
        'TA.0 SINGLE-MEMBER FB80 PANEL — PRINTER-DECODE EVIDENCE ONLY',
        'TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY'
    ) and panel.get('dataset_key') == key and
         panel.get('selected_members') == members and panel.get('completed') == len(members),
         'PANEL_IDENTITY_MISMATCH')
    if panel['phase'] == 'TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY':
        need(panel.get('original_failure_sha256') == digest(read(folder / 'failure.json')) and
             panel.get('recovery') == 'Re-decoded existing verified JES reports; ZERO new MVS jobs.',
             'RECOVERY_PROVENANCE_MISMATCH')
    entries = panel.get('members')
    need(type(entries) is list and len(entries) == len(members), 'PANEL_MEMBER_COUNT_MISMATCH')
    checked = []
    for n, (member, entry) in enumerate(zip(members, entries), 1):
        need(type(entry) is dict and entry.get('member') == member and
             entry.get('jobname') == f'TA0{KEYS[key]}{n:03d}' and
             entry.get('pilot_directory') == f'{n:02d}-{member}-pilot' and
             entry.get('decoded_directory') == f'{n:02d}-{member}-decoded',
             'PANEL_MEMBER_ORDER_OR_PATH_MISMATCH')
        pilot_dir = folder / entry['pilot_directory']
        decoded_dir = folder / entry['decoded_directory']
        guard(pilot_dir, new=False, root=ROOT)
        guard(decoded_dir, new=False, root=ROOT)
        receipt, report, pins = decoder.load_evidence(pilot_dir)
        need(receipt.get('dataset_key') == key and
             receipt.get('requested_members') == [member] and
             receipt.get('jobname') == entry['jobname'] and
             receipt.get('job') == entry.get('job'), 'PILOT_IDENTITY_MISMATCH')
        actual = decoder.decode_multi(report, job=receipt['job'],
                                      jobname=receipt['jobname'], members=[member])
        need(set(actual) == {member}, 'DECODED_MEMBER_IDENTITY_MISMATCH')
        binary, metadata = actual[member]
        expect = ledger.get((key, member))
        need(expect is not None and
             (receipt['job'], metadata['record_count'], digest(binary)) == expect,
             'PUBLISHED_MVS_READBACK_MISMATCH')
        need(len(binary) == 80 * metadata['record_count'] and
             entry.get('record_count_from_print') == metadata['record_count'] and
             entry.get('bytes_from_print') == len(binary) and
             entry.get('sha256_of_decoded_print') == digest(binary) and
             entry.get('pilot_receipt_sha256') == digest(read(pilot_dir / 'receipt.json')) and
             entry.get('decode_receipt_sha256') == digest(read(decoded_dir / 'decode-receipt.json')),
             'PANEL_RECEIPT_MISMATCH')
        stored = js(decoded_dir / 'decode-receipt.json')
        need(stored.get('source_job') == receipt['job'] and
             stored.get('source_dataset') == receipt.get('source_dataset') and
             stored.get('source_receipt_sha256') == digest(read(pilot_dir / 'receipt.json')) and
             stored.get('source_report_sha256') == pins['job-report.txt'] and
             stored.get('source_printer_window_sha256') == pins['printer-window.raw'] and
             type(stored.get('members')) is list and len(stored['members']) == 1,
             'DECODE_RECEIPT_SOURCE_MISMATCH_' + key + '_' + member)
        # Early printer receipts predate the page-framing fix. Their metadata
        # differs ONLY by the absent repeated_page_headings field, and is
        # accepted only when current strict decoding observes zero repetitions.
        # All saved receipt/source/file pins are still verified byte-for-byte.
        schema = metadata_schema(stored['members'][0], metadata)
        need(schema is not None,
             'DECODE_RECEIPT_METADATA_MISMATCH_' + key + '_' + member)
        need(read(decoded_dir / f'{member}.fb80', MAXOBJ) == binary,
             'DECODED_BINARY_MISMATCH')
        checked.append({'dataset_key': key, 'member': member, 'job': receipt['job'],
                        'records': metadata['record_count'], 'bytes': len(binary),
                        'printer_sha256': digest(binary),
                        'decode_receipt_schema': schema})
    return checked


def reconcile(base: Path, *, load_module=None, exec_module=None,
              triage_module=None) -> dict:
    guard(base, new=False, root=ROOT)
    choices = selected()
    ledger = reported()
    need(set(ledger) == {(key, name) for key, members in choices.items() for name in members},
         'LEDGER_AND_MANIFEST_DIFFER')
    decoder = load_module or load(DECODER, 'ta0_reconcile_decoder')
    verified = []
    for key in KEYS:
        verified += one_panel(decoder, base, key, choices[key], ledger)
    need(len(verified) == 14 and sum(x['records'] for x in verified) == 902 and
         sum(x['bytes'] for x in verified) == 72160, 'OBJECT_TOTAL_MISMATCH')
    # Invoke the exact existing, strict verification path.  A directory entry
    # or unvalidated JSON receipt alone must never count as executable use.
    load_dir = base / 'ta0-mr10-load-iehlist'
    review_dir = base / 'ta0-mr10-load-directory-reviewed'
    execution_dir = base / 'ta0-mr10-load-execution'
    for folder in (load_dir, review_dir, execution_dir):
        guard(folder, new=False, root=ROOT)
    need(js(review_dir / 'directory-review.json').get('job') == 9060,
         'LOAD_DIRECTORY_JOB_MISMATCH')
    pilot = exec_module or load(PILOT, 'ta0_reconcile_exec')
    inspector = triage_module or load(TRIAGE, 'ta0_reconcile_triage')
    core = pilot.import_file(pilot.CORE, 'ta0_reconcile_core')
    status = inspector.diagnose(pilot, core, core.load_config(),
                                evidence=load_dir, review_dir=review_dir,
                                output=execution_dir)
    need(status.get('state') == 'SAVED_EXECUTION_VERIFIED' and
         status.get('preflight') == 'OK_NOW' and
         status.get('job') == '9061', 'ICINT19_EXECUTABLE_EVIDENCE_NOT_VERIFIED')
    return {'phase': 'TA.0 RECONCILED DEVELOPMENT MVS EVIDENCE; NOT RELEASE ACCEPTANCE',
            'fb80_objects': len(verified), 'fb80_records': 902, 'fb80_bytes': 72160,
            'historical_pre_page_receipts': sum(
                item['decode_receipt_schema'] == 'PRE_PAGE_V1' for item in verified),
            'load_member': 'MR10_LOAD(ICINT19)', 'load_directory_job': 9060,
            'load_execution_job': 9061, 'load_execution_status': status['state'],
            'members': verified,
            'qualifications': [
                'Relocatable objects reconstructed from SHA-pinned printer reports only.',
                'Development ICINT19 execution is verified against pinned JES and BCPL results.',
                'No independent source-to-resident-object byte identity is established.',
                'No RECFM=U unload/restore comparison or restored executable use has been tested.',
                'No rights, candidate, tape image or release acceptance is established.']}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence-dir', required=True, type=Path)
    ap.add_argument('--output-dir', required=True, type=Path,
                    help='new private result directory under ignored workarea/')
    args = ap.parse_args(argv)
    try:
        guard(args.output_dir, new=True, root=ROOT)
        result = reconcile(args.evidence_dir)
        os.umask(0o077)
        os.mkdir(args.output_dir, 0o700)
        out = args.output_dir / 'reconciliation.json'
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write((json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    except (ValueError, OSError, UnicodeError, yaml.YAMLError) as exc:
        # Never print raw JES/report content, only the category.
        print('TA.0 BINARY EVIDENCE RECONCILIATION REFUSED: ' +
              (str(exc) if type(exc) is ReconcileError else type(exc).__name__),
              file=sys.stderr)
        return 1
    print('TA.0 BINARY EVIDENCE RECONCILED: 14/14 FB80 objects, 902 records, 72160 bytes')
    print(f"Historical pre-pagination receipts: {result['historical_pre_page_receipts']} "
          "(only zero repeated headings; original files unchanged)")
    print('MR10_LOAD(ICINT19): JOB 9060 directory; JOB 9061 saved execution verified')
    print('Read-only MVS evidence; no DASD byte identity, tape restore or release acceptance.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
