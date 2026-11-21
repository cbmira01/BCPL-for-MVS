#!/usr/bin/env python3
"""TA.2: reconcile saved JOB 9330 against observed TK5 reader byte mapping.

No MVS submission or source/dataset writes. Read original QSAM JES evidence,
verify its 15 observations, and compare to independently frozen historical
source bytes using the three empirically established transfer substitutions.
Original CP037 mismatches stay recorded; this is *not* a CP037-fidelity PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / 'workarea'
ORIGINAL = WORK / 'ta2-rc2-cambsource-qsam-fidelity'
RECONCILED = WORK / 'ta2-rc2-cambsource-qsam-transport-reconciliation'
# Observed from JOB 9330, not a blanket IBM-1047 or CP037 code-page claim.
READER_BYTES = {'|': 0x6A, '[': 0xAD, ']': 0xBD}
FROZEN = '78baec9a8546e4ab09caee779aa2b675379272f3'
MEMBER_NAMES = ('BCPL', 'BLIB', 'CG', 'CGHDR', 'EDITMAIN', 'IOS', 'LIBHDR',
                'PM', 'SYN', 'SYNHDR', 'TRN', 'TRNHDR', 'MAKEOBJ', 'MAKELIB',
                'PROGRAM')


class Refusal(ValueError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Refusal(message)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'missing canonical verifier')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixed80(raw: bytes, changes: dict[str, int]) -> dict[str, int | str]:
    """Fingerprint every byte of each FB80 record, preserving blank tails."""
    need(raw and raw.endswith(b'\n') and b'\r' not in raw,
         'frozen source lacks canonical LF termination')
    try:
        records = raw[:-1].decode('ascii').split('\n')
    except UnicodeDecodeError as exc:
        raise Refusal('non-ASCII frozen source') from exc
    fnv, total, trailing = 0x811C9DC5, 0, 0
    digest = hashlib.sha256()
    for line in records:
        need(len(line) <= 80 and all(32 <= ord(char) <= 126 for char in line),
             'unrepresentable frozen FB80 source record')
        data = bytes(changes.get(char, char.encode('cp037')[0]) for char in line)
        data = data.ljust(80, b'\x40')
        digest.update(data)
        trailing = trailing + 1 if data == b'\x40' * 80 else 0
        for byte in data:
            fnv = ((fnv ^ byte) * 0x01000193) & 0xFFFFFFFF
            total = (total + byte) & 0xFFFFFFFF
    return {'count': len(records), 'trail': trailing,
            'fnv': fnv, 'sum': total, 'sha256': digest.hexdigest()}


def reconcile(saved: dict, source_bytes: dict[str, bytes],
              actual_report: list[dict], saved_summary: str) -> dict:
    """Demand exact saved-report agreement and successful full-source match."""
    need(saved.get('candidate') == 'BCPL-0.1.0-rc2' and
         saved.get('population_jobs') == [9325, 9326] and
         saved.get('mvs_verification_job') == 9330 and
         saved.get('status') == 'mismatch',
         'not the accepted JOB 9330 original mismatch evidence')
    results = saved.get('results')
    need(isinstance(results, list) and len(results) == 15 and
         [x.get('member') for x in results] == list(MEMBER_NAMES),
         'saved member sequence is incomplete or changed')
    need(results == actual_report,
         'saved receipt differs from original MVS JES report')
    need(saved_summary.strip() != '', 'missing original MVS job summary')
    need(list(source_bytes) == list(MEMBER_NAMES),
         'frozen selected sources are missing or reordered')
    recorded = saved.get('expected')
    need(isinstance(recorded, dict) and set(recorded) == set(MEMBER_NAMES),
         'saved expected inventory is not the frozen selection')
    rows = []
    old_pass, mapped_pass = 0, 0
    for row in results:
        name = row['member']
        raw = source_bytes[name]
        cp = fixed80(raw, {})
        mapped = fixed80(raw, READER_BYTES)
        original = {k: cp[k] for k in ('count', 'trail', 'fnv', 'sum')}
        observed = row.get('observed')
        need(row.get('expected') == original and
             recorded[name].get('git_sha256') == hashlib.sha256(raw).hexdigest() and
             all(recorded[name].get(k) == original[k] for k in original) and
             row.get('match') is (observed == original),
             f'{name}: original CP037 evidence drifted')
        need(isinstance(observed, dict) and
             set(observed) == {'count', 'trail', 'fnv', 'sum'} and
             all(type(v) is int for v in observed.values()),
             f'{name}: malformed original MVS observation')
        candidate = {k: mapped[k] for k in ('count', 'trail', 'fnv', 'sum')}
        matches = observed == candidate
        old_pass += int(observed == original)
        mapped_pass += int(matches)
        rows.append({'member': name,
                     'mvs_raw_counts_match': observed['count'] == mapped['count'] and
                                              observed['trail'] == mapped['trail'],
                     'cp037_expected_match': observed == original,
                     'reader_profile_match': matches,
                     'observed': observed, 'reader_profile_expected': candidate,
                     'mapped_fb80_sha256': mapped['sha256']})
    need(old_pass == 7 and mapped_pass == 15 and
         all(x['mvs_raw_counts_match'] for x in rows),
         'observed byte fingerprints are not reconciled by the exact reader profile')
    return {'candidate': 'BCPL-0.1.0-rc2',
            'population_jobs': [9325, 9326], 'mvs_job': 9330,
            'status': 'reader-profile-reconciled',
            'important_limit': 'NOT literal CP037 byte fidelity',
            'observed_reader_overrides_hex': {k: f'{v:02X}' for k, v in READER_BYTES.items()},
            'original_cp037_pass': old_pass, 'reader_profile_pass': mapped_pass,
            'source_records': sum(x['reader_profile_expected']['count'] for x in rows),
            'members': rows}


def saved_file(path: Path, max_bytes: int) -> str:
    need(ORIGINAL.is_dir() and not ORIGINAL.is_symlink() and
         WORK.is_dir() and not WORK.is_symlink(),
         'original MVS evidence is absent or unsafe')
    need(path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(ORIGINAL.resolve()) and
         path.stat().st_size < max_bytes,
         'missing or unsafe saved MVS evidence: ' + path.name)
    return path.read_text(encoding='utf-8')


def run() -> int:
    need(not RECONCILED.exists() and not RECONCILED.is_symlink(),
         'reconciliation evidence exists: no overwrites')
    readiness = load('ta2_reader_ready', HERE / 'rc2-cambsource-readiness.py')
    qsam = load('ta2_reader_qsam', HERE / 'rc2-qsam-fidelity.py')
    manifest, dspal = readiness.source_manifest()
    expected = qsam.expected_records(readiness, manifest, dspal)
    need(tuple(manifest['datasets'][20]['members']) == MEMBER_NAMES and
         readiness.FROZEN == FROZEN, 'source release selection/freeze drifted')
    sources = {name: readiness.check_frozen_source(
        dspal['datasets']['CAMB_SOURCE']['members'][name]) for name in MEMBER_NAMES}
    receipt = json.loads(saved_file(ORIGINAL / 'receipt.json', 100_000))
    report = saved_file(ORIGINAL / 'mvs-job-report.txt', 2_000_000)
    summary = saved_file(ORIGINAL / 'job-summary.txt', 100_000)
    qsam.summary_steps(summary)
    parsed = qsam.parse_report(report, expected)
    out = reconcile(receipt, sources, parsed, summary)
    RECONCILED.mkdir(mode=0o700)
    (RECONCILED / 'receipt.json').write_text(json.dumps(out, indent=2) + '\n',
                                             encoding='utf-8')
    print(f'TA.2 RC2 MVS JOB 9330: {out["reader_profile_pass"]}/15 '
          f'FB80 record/byte fingerprints reconciled')
    print(f'  original CP037: {out["original_cp037_pass"]}/15; '
          f'observed reader byte profile: {out["reader_profile_pass"]}/15')
    print('  |: 4F -> 6A; [: BA -> AD; ]: BB -> BD')
    print(f'  records: {out["source_records"]}; original JOB 9330 '
          'receipt and JES report preserved')
    print('  RELEASE GATE: mapped transport matches; literal CP037 fidelity '
          'not established; BT0021 staging not authorized')
    print('Evidence: ' + str(RECONCILED.relative_to(ROOT)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved-job9330', action='store_true', required=True)
    parser.parse_args(argv)
    try:
        return run()
    except (Refusal, OSError, ValueError, KeyError, UnicodeError) as exc:
        print('TA.2 RC2 TRANSPORT RECONCILIATION REFUSED: ' + str(exc),
              file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
