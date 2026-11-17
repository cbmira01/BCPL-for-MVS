#!/usr/bin/env python3
"""TA.0: finish a decode-stopped FB80 panel using ONLY retained MVS evidence.

No JES operations; no reprinting, reassembling, dataset changes or retries.
The existing failed panel is retained (including failure.json); prior decoded
artifacts must exactly match a fresh strict decode of pinned original reports.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DIR = Path(__file__).resolve().parent


class RecoverError(ValueError):
    pass


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RecoverError(message)


def importer(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, DIR / filename)
    need(spec is not None and spec.loader is not None, 'required recovery module missing')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def plain(path: Path, *, limit: int = 1024 * 1024) -> bytes:
    need(path.is_file() and not path.is_symlink(), 'missing or linked evidence file')
    need(path.stat().st_size <= limit, 'evidence file exceeds size limit')
    return path.read_bytes()


def pinned_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(plain(path))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RecoverError('invalid retained JSON evidence') from exc
    need(type(obj) is dict, 'expected JSON evidence mapping')
    return obj


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def recover(panel, decoder, *, directory: Path, key: str, members: list[str],
            source_dataset: str) -> dict[str, Any]:
    need(directory.is_absolute() and directory.is_dir() and not directory.is_symlink()
         and not directory.resolve().is_relative_to(ROOT.resolve()),
         'existing panel must be a private directory outside checkout')
    need(type(members) is list and len(members) >= 1 and len(members) <= 20 and
         len(set(members)) == len(members), 'invalid selected members')
    need(key in panel.ALLOWED, 'unknown object-library selection')
    need(not (directory / 'panel-receipt.json').exists(),
         'panel is already complete; will not overwrite')
    failure = pinned_json(directory / 'failure.json')
    ordinal = failure.get('ordinal')
    need(failure.get('stage') == 'decode' and type(ordinal) is int and
         1 <= ordinal <= len(members) and failure.get('failed_member') == members[ordinal - 1],
         'recovery requires a retained decode-stage failure for a selected member')

    # Preflight ALL existing printed material and all previous decoded bytes
    # before producing any new file. No unsubmitted job can be guessed/retried.
    items = []
    missing = []
    for n, member in enumerate(members, 1):
        label = f'{n:02d}-{member}'
        pilot_dir = directory / f'{label}-pilot'
        decoded_dir = directory / f'{label}-decoded'
        need(pilot_dir.is_dir() and not pilot_dir.is_symlink(),
             f'{member}: missing original JES pilot; refusing to submit a new one')
        receipt, report, pins = decoder.load_evidence(pilot_dir)
        expected_jobname = f'TA0{panel.ALLOWED[key]}{n:03d}'
        need(receipt.get('dataset_key') == key and
             receipt.get('requested_members') == [member] and
             receipt.get('jobname') == expected_jobname and
             receipt.get('source_dataset') == source_dataset and
             receipt.get('step') == 'TA0HEX',
             f'{member}: original JES job/dataset identity mismatch')
        decoded = decoder.decode_multi(report, job=receipt['job'],
                                       jobname=receipt['jobname'], members=[member])
        need(list(decoded) == [member], f'{member}: decoded member identity inconsistent')
        binary, metadata = decoded[member]
        expected_sha = sha(binary)
        need(metadata['sha256_of_decoded_print'] == expected_sha and
             metadata['byte_count'] == len(binary),
             f'{member}: inconsistent regenerated member bytes')
        original_receipt = sha(plain(pilot_dir / 'receipt.json'))
        if decoded_dir.exists() or decoded_dir.is_symlink():
            need(decoded_dir.is_dir() and not decoded_dir.is_symlink(),
                 f'{member}: decoded directory invalid')
            current = plain(decoded_dir / f'{member}.fb80', limit=64*1024*1024)
            need(current == binary, f'{member}: saved decoded binary differs from original report')
            per_member = pinned_json(decoded_dir / f'{member}.fb80.json')
            overall = pinned_json(decoded_dir / 'decode-receipt.json')
            need(per_member.get('member') == member and
                 per_member.get('sha256_of_decoded_print') == expected_sha and
                 per_member.get('record_count') == metadata['record_count'] and
                 overall.get('source_job') == receipt['job'] and
                 overall.get('source_dataset') == source_dataset and
                 overall.get('source_receipt_sha256') == original_receipt and
                 overall.get('source_report_sha256') == pins['job-report.txt'] and
                 overall.get('source_printer_window_sha256') == pins['printer-window.raw'] and
                 type(overall.get('members')) is list and len(overall['members']) == 1 and
                 overall['members'][0].get('sha256_of_decoded_print') == expected_sha,
                 f'{member}: prior decoder receipt does not match original printer evidence')
        else:
            # There must be exactly the one known incomplete decode; no
            # recovery from an unknown/possibly incomplete JES submission.
            need(n == ordinal, f'{member}: missing decoded artifact outside failed ordinal')
            missing.append((pilot_dir, decoded_dir, member, receipt['job']))

        items.append({
            'member': member, 'job': receipt['job'], 'jobname': expected_jobname,
            'record_count_from_print': metadata['record_count'],
            'bytes_from_print': len(binary), 'sha256_of_decoded_print': expected_sha,
            'pilot_receipt_sha256': original_receipt,
            'pilot_directory': pilot_dir.name, 'decoded_directory': decoded_dir.name,
        })

    need(len(missing) == 1, 'expected exactly one failed decoding to recover')
    need(failure.get('pilot_job') == missing[0][3],
         'retained failure JES job number differs from pinned pilot')
    for pilot_dir, decoded_dir, member, job in missing:
        result = decoder.process(pilot_dir, decoded_dir, expected_counts=[])
        need(result.get('source_job') == job and
             result['members'][0]['member'] == member,
             'newly decoded evidence differs from expected JES member')

    for item in items:
        item['decode_receipt_sha256'] = sha(plain(
            directory / item['decoded_directory'] / 'decode-receipt.json'))
    summary = {
        'phase': 'TA.0 SINGLE-MEMBER FB80 PANEL — RECOVERED PRINTER-DECODE EVIDENCE ONLY',
        'dataset_key': key, 'selected_members': members,
        'completed': len(items), 'members': items,
        'original_failure_sha256': sha(plain(directory / 'failure.json')),
        'recovery': 'Re-decoded existing verified JES reports; ZERO new MVS jobs.',
        'qualifications': [
            'All source records came from previously submitted, SHA-pinned JES reports.',
            'No new JES submissions or retries were performed during recovery.',
            'Printer output does not establish independent DASD/source/Git identity.',
            'No rights review, tape acceptance or TA.0 closure is claimed.',
        ],
    }
    panel.safe_json(directory / 'panel-receipt.json', summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-key', required=True,
                        choices=['EXT_OBJ', 'MR10_OBJ', 'BOOT_OBJ'])
    parser.add_argument('--output-dir', required=True, type=Path,
                        help='existing failed panel directory outside checkout')
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        prep = importer('prepare-iebptpch-readback.py', 'ta0_recover_prep')
        panel = importer('run-iebptpch-single-panel.py', 'ta0_recover_panel')
        decoder = importer('decode-iebptpch-multi.py', 'ta0_recover_decoder')
        core_file = ROOT / 'tools/datasets/dspal-core.py'
        spec = importlib.util.spec_from_file_location('ta0_recover_core', core_file)
        need(spec is not None and spec.loader is not None, 'dataset mapping unavailable')
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        members = panel.select_members(prep, key=args.dataset_key, named=None,
                                       all_selected=True)
        cfg = core.load_config()
        spec = cfg['datasets'][args.dataset_key]
        need(all(spec.get(x) == y for x, y in
                 [('dsorg', 'PO'), ('recfm', 'FB'), ('lrecl', 80), ('blksize', 800)]),
             'current object PDS DCB mapping invalid')
        source_dataset = core.full_dsn(cfg, spec)
        summary = recover(panel, decoder, directory=args.output_dir,
                          key=args.dataset_key, members=members,
                          source_dataset=source_dataset)
    except (RecoverError, ValueError, RuntimeError, OSError, UnicodeError, KeyError) as exc:
        print(f'TA.0 PANEL RECOVERY REFUSED: {type(exc).__name__}', file=sys.stderr)
        print('No JES job submitted. Original evidence preserved.', file=sys.stderr)
        return 1
    print(f"TA.0 PANEL RECOVERY: {summary['dataset_key']} "
          f"{summary['completed']} previously submitted members verified; no JES jobs submitted")
    for item in summary['members']:
        print(f"  {item['member']}: JOB {item['job']}, "
              f"{item['record_count_from_print']} FB80, "
              f"SHA-256={item['sha256_of_decoded_print']}")
    print('Printer-only evidence; DASD/source identity and TA.0 acceptance remain open.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
