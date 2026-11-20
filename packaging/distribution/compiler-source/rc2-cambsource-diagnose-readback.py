#!/usr/bin/env python3
"""TA.2: diagnose existing MVS CAMB_SOURCE readback evidence; no JES or writes.

Prints only member, job, logical record counts/lengths and first mismatch
position. Never reads or modifies live MVS, nor retries a readback.
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
EVIDENCE = ROOT / 'workarea/ta2-rc2-cambsource-record-readback'


class DiagnosisError(ValueError):
    pass


def require(condition: bool, why: str) -> None:
    if not condition:
        raise DiagnosisError(why)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f'missing {name}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def safe_read(path: Path, *, limit: int = 2_000_000) -> bytes:
    require(EVIDENCE.is_dir() and not EVIDENCE.is_symlink(),
            'saved MVS evidence directory missing/unsafe')
    require(path.is_file() and not path.is_symlink() and
            path.resolve().is_relative_to(EVIDENCE.resolve()) and
            path.stat().st_size <= limit, f'missing/unsafe MVS evidence: {path.name}')
    return path.read_bytes()


def lines(text: str) -> list[str]:
    # Preserve all records including interior blanks. A missing final LF is
    # a content mismatch and is reported independently.
    out = text.split('\n')
    return out[:-1] if text.endswith('\n') else out


def first_mismatch(expected: str, actual: str) -> dict:
    a, b = lines(expected), lines(actual)
    pos = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
               min(len(a), len(b)))
    ea = a[pos] if pos < len(a) else None
    ab = b[pos] if pos < len(b) else None
    result = {
        'expected_records': len(a), 'observed_records': len(b),
        'expected_final_lf': expected.endswith('\n'),
        'observed_final_lf': actual.endswith('\n'),
        'first_different_record': pos + 1,
        'expected_length': len(ea) if ea is not None else None,
        'observed_length': len(ab) if ab is not None else None,
    }
    if ea is None:
        result['type'] = 'extra-records-at-end'
    elif ab is None:
        result['type'] = 'missing-records-at-end'
    elif pos + 1 < len(a) and ea != ab and a[pos + 1] == ab:
        result['type'] = 'possible-missing-expected-record'
    elif pos + 1 < len(b) and ea != ab and ea == b[pos + 1]:
        result['type'] = 'possible-extra-observed-record'
    else:
        result['type'] = 'record-content-difference'
    if ea is not None and ab is not None:
        c = next((j for j in range(min(len(ea), len(ab))) if ea[j] != ab[j]),
                 min(len(ea), len(ab)))
        result['first_different_column'] = c + 1
        result['expected_codepoint'] = f'U+{ord(ea[c]):04X}' if c < len(ea) else 'EOL'
        result['observed_codepoint'] = f'U+{ord(ab[c]):04X}' if c < len(ab) else 'EOL'
    return result


def diagnostic(receipt: dict, text_by_member: dict[str, str],
               expected_by_member: dict[str, str], selected: list[str]) -> list[dict]:
    require(receipt.get('candidate_id') == 'BCPL-0.1.0-rc2' and
            receipt.get('status') == 'incomplete' and
            receipt.get('population_jobs') == [9325, 9326],
            'not the expected failed rc2 MVS readback receipt')
    observed = receipt.get('members')
    require(isinstance(observed, list) and 0 < len(observed) <= 15,
            'no recorded MVS readback members')
    require([r.get('member') for r in observed] == selected[:len(observed)],
            'saved MVS members differ from canonical selection/order')
    results = []
    for row in observed:
        name = row['member']
        actual, expected = text_by_member[name], expected_by_member[name]
        normalized_sha = hashlib.sha256(expected.encode('utf-8')).hexdigest()
        readback_sha = hashlib.sha256(actual.encode('utf-8')).hexdigest()
        require(row.get('normalized_sha256') == normalized_sha and
                row.get('readback_sha256') == readback_sha,
                f'{name}: evidence hash differs from saved comparison receipt')
        require(row.get('match') is (actual == expected),
                f'{name}: saved match flag differs from saved MVS content')
        require(isinstance(row.get('job'), int) and row['job'] > 0,
                f'{name}: missing MVS GET job number')
        results.append({'member': name, 'job': row['job'],
                        'match': actual == expected,
                        **({} if actual == expected else first_mismatch(expected, actual))})
    require(any(not row['match'] for row in results),
            'saved failed readback contains no mismatched member')
    return results


def run() -> int:
    rb = load('ta2_diagnose_rb', HERE / 'rc2-cambsource-record-readback.py')
    ready = load('ta2_diagnose_ready', HERE / 'rc2-cambsource-readiness.py')
    manifest, dspal = ready.source_manifest()
    names = manifest['datasets'][20]['members']
    require(len(names) == 15 and
            set(names) == set(dspal['datasets']['CAMB_SOURCE']['members']),
            'historical selection changed')
    receipt = json.loads(safe_read(EVIDENCE / 'receipt.json'))
    members = receipt.get('members')
    require(isinstance(members, list), 'malformed MVS receipt')
    actual, expected = {}, {}
    for row in members:
        name = row.get('member')
        require(isinstance(name, str) and name in names,
                'unknown MVS member in saved receipt')
        expected[name] = rb.normalize_expected(ready.check_frozen_source(
            dspal['datasets']['CAMB_SOURCE']['members'][name]))[0]
        actual[name] = safe_read(EVIDENCE / (name + '.txt')).decode('utf-8')
    rows = diagnostic(receipt, actual, expected, names)
    print(f'TA.2 RC2 SAVED READBACK: {len(rows)}/15 members examined; '
          f'{sum(not x["match"] for x in rows)} mismatch(es)')
    for row in rows:
        if row['match']:
            print(f'  {row["member"]}: MVS JOB {row["job"]}, normalized records PASS')
        else:
            print(f'  {row["member"]}: MVS JOB {row["job"]}, MISMATCH')
            for key in ('type', 'first_different_record', 'expected_records',
                        'observed_records', 'expected_final_lf', 'observed_final_lf',
                        'expected_length', 'observed_length',
                        'first_different_column', 'expected_codepoint',
                        'observed_codepoint'):
                if key in row:
                    print(f'    {key}: {row[key]}')
    print('Diagnostic only: original MVS evidence unchanged; no re-read or MVS write')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saved-evidence', action='store_true', required=True)
    ap.parse_args(argv)
    try:
        return run()
    except (DiagnosisError, OSError, ValueError, UnicodeError, KeyError) as exc:
        print('TA.2 RC2 SAVED READBACK DIAGNOSIS REFUSED: ' + str(exc),
              file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
