#!/usr/bin/env python3
"""CO.4 deterministic native verification batch, isolated evidence per case.

Only --run performs MVS submissions. --check does source checks offline.
Reuse the previously native-tested CO.3 compiler/IFOX/IEWL/GO harness.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'packaging/milestones/coroutines/candidates/co4-verification-batch'
WORK = ROOT / 'workarea/co4-verification-batch'
SAFE_RUNNER = ROOT / 'tools/coroutines/run-co4-safe-negative.py'

# Case identifiers are private candidate names, NOT regression test numbers.
CASES = {
    'stack': ('stack-source.bcpl', 'CO4STK',
              ('ROOT', 'MADE', 'YIELD', 'RETURN', 'CLEAN', 'PASS')),
    'churn': ('churn-source.bcpl', 'CO4CHURN',
              ('INIT', 'C04', 'C08', 'C12', 'C16', 'CLEAN', 'PASS')),
    'busy': ('busy-source.bcpl', 'CO4BUSY',
             ('MADE', 'REFUSE', 'A1', 'RA1', 'B2', 'RB2', 'A2',
              'RA2', 'CLEAN', 'PASS')),
}

REQUIRED = {
    'stack': ('CHECK(16448)', 'CHECK(1088)', 'SELF!5', 'GUARD!0',
              'META!0', 'AND GUARD=STACKEND-2', 'AND META=STACKEND-1',
              'DEEP(5,X)', 'DELETECO(A)'),
    'churn': ('FOR I=1 TO 16 DO', 'CREATECO(WORKA,1024)',
              'CREATECO(WORKB,1024)', 'CREATECO(WORKA,1024)',
              'CALLCO(A,I*10+1)', 'CALLCO(B,I*20+1)',
              'DELETECO(A)', 'DELETECO(B)'),
    'busy': ('CALLCO(PARENT,0)', 'RESUMECO(PARENT,0)',
             'RESUMECO(SELF,0)', 'RESUMECO(CO3ROOT,0)',
             'CALLCO(B,21)', 'CALLCO(B,22)', 'CALLCO(A,12)',
             'DELETECO(A)', 'DELETECO(B)'),
}


class CandidateError(ValueError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateError(f'missing imported runner: {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def parse_records(report: str, prefix: str) -> list[str]:
    """Strict per-case JES record extraction, rejecting malformed markers."""
    found = []
    for line_no, raw in enumerate(report.replace('\f', '').splitlines(), 1):
        line = raw.strip()
        if not line.startswith(prefix):
            continue
        match = re.fullmatch(re.escape(prefix) + r'\s+([A-Z0-9]+)', line)
        if match is None:
            raise CandidateError(f'malformed {prefix} record at line {line_no}')
        found.append(match.group(1))
    return found


def validate_case(key: str, fixture: Path = FIXTURE) -> dict[str, str]:
    source, prefix, expected = CASES[key]
    raw = (fixture / source).read_bytes()
    try:
        code = raw.decode('ascii')
    except UnicodeDecodeError as exc:
        raise CandidateError(f'{source}: non-ASCII source') from exc
    for number, line in enumerate(code.splitlines(), 1):
        if len(line) > 80 or '\t' in line:
            raise CandidateError(f'{source}: non-FB80 card {number}')
    if key == 'stack':
        # Cambridge BCPL declaration groups must precede commands.
        # The first attempt contained a LET after an IF inside CHECK.
        check_body = code.split('AND CHECK(WORDS) = VALOF', 1)[1].split(
            'AND DEEP(N,X) = VALOF', 1)[0]
        if 'IF ' not in check_body or 'LET ' in check_body.split('IF ', 1)[1]:
            raise CandidateError(f'{source}: late declaration in CHECK')
    for token in REQUIRED[key]:
        if token not in code:
            raise CandidateError(f'{source}: source contract absent: {token}')
    for token in expected:
        if len(re.findall(r'\bMARK\("' + token + r'"\)', code)) != 1:
            raise CandidateError(f'{source}: missing/duplicate marker {token}')
    if code.count('MARK("FAIL")') != 1:
        raise CandidateError(f'{source}: missing/duplicate FAIL marker')
    for bad in ('CALLCO(1,', 'RESUMECO(1,', 'CHANGECO(1,'):
        if bad in code:
            raise CandidateError(f'{source}: unsafe arbitrary descriptor API')
    return {'source_file': source, 'sha256': hashlib.sha256(raw).hexdigest(),
            'prefix': prefix, 'expected_count': str(len(expected))}


def validate_inputs() -> dict[str, object]:
    # Existing, reviewed CO.4 validator pins all accepted CO.3 source blobs.
    previous = load_module('co4_prior_native_validator', SAFE_RUNNER)
    prior = previous.validate_inputs()
    return {'accepted_co3': prior,
            'cases': {case: validate_case(case) for case in CASES}}


def compiler_failure_detail(evidence: Path) -> str | None:
    """Return at most one bounded compiler diagnostic; never dump JES text."""
    for name in ('CO3ACMP', 'CO3LCMP'):
        log = evidence / f'{name}.log'
        if not log.is_file():
            continue
        for line in reversed(log.read_text(errors='replace').splitlines()):
            text = line.strip()
            if text.startswith('cambridge-compile-mvs:'):
                return f'{name}: {text[:200]}'
    return None


def run_one(key: str, session: Path, previous, hashes: dict) -> dict:
    source_name, prefix, expected = CASES[key]
    case_dir = session / key
    case_dir.mkdir()
    with tempfile.TemporaryDirectory(prefix='_input-', dir=case_dir) as tmp:
        stage = Path(tmp)
        shutil.copyfile(FIXTURE / source_name, stage / 'source.bcpl')
        for name in ('library.bcpl', 'cambridge-parm.txt'):
            shutil.copyfile(previous.ACCEPTED / name, stage / name)
        driver = previous.load_module('co4batch_driver_' + key,
                                      previous.BASE_RUNNER)
        adapter = previous.load_module('co4batch_adapter_' + key,
                                       previous.CO3_ADAPTER)
        previous.configure(driver, adapter, stage, case_dir)
        driver.EXPECTED = expected
        driver.observed_records = lambda report: parse_records(report, prefix)
        before = set(case_dir.iterdir())
        capture = io.StringIO()
        with redirect_stdout(capture):
            rc = driver.execute('first')
        created = [p for p in case_dir.iterdir() if p not in before and
                   p.is_dir() and (p / 'result.json').is_file()]
        if len(created) != 1:
            raise CandidateError(f'{key}: missing/ambiguous native receipt')
        evidence = created[0]
        raw = json.loads((evidence / 'result.json').read_text())
        if (rc == 0) != (raw.get('status') == 'PASS'):
            raise CandidateError(f'{key}: inconsistent executor result')
        try:
            evidence_name = str(evidence.relative_to(ROOT))
        except ValueError:
            evidence_name = str(evidence)
        detail = compiler_failure_detail(evidence) if rc != 0 else None
        outcome = {
            'case': key, 'status': raw['status'], 'rc': rc,
            'reason': raw.get('reason') if rc != 0 else None,
            'compiler_diagnostic': detail,
            'evidence_dir': evidence_name,
            'native_job': raw.get('native_job'),
            'compiler_jobs': {k: raw.get(k) for k in
                              ('CO3ACMP_job', 'CO3LCMP_job')},
            'source': hashes['cases'][key],
            'expected_bcpl_records': [prefix + ' ' + x for x in expected],
            'inherited_result': 'result.json',
            'inherited_runner_stdout': capture.getvalue(),
            'evidence_class': raw.get('evidence_class', 'MVS-pending'),
            'installed_mvs_objects_modified': False,
        }
        (evidence / 'co4-case-result.json').write_text(
            json.dumps(outcome, indent=2) + '\n')
        print(f'CO.4 {key.upper()} ' + ('PASS' if rc == 0 else 'FAIL'))
        if detail:
            print(f'CO.4 {key.upper()} diagnostic: {detail}')
        return outcome


def run_batch() -> int:
    hashes = validate_inputs()
    WORK.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    result = {'march': 'CO.4', 'candidate': 'verification-batch',
              'status': 'FAIL', 'cases': [], 'source_verification': hashes,
              'installed_mvs_objects_modified': False}
    try:
        previous = load_module('co4_native_batch_base', SAFE_RUNNER)
        for key in CASES:
            item = run_one(key, session, previous, hashes)
            result['cases'].append(item)
            if item['status'] != 'PASS':
                result['reason'] = f"{key}: {item.get('reason') or 'native result FAIL'}"
                return 1
        result['status'] = 'PASS'
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        result['reason'] = str(exc)
        print(f'CO.4 batch FAIL: {exc}')
        return 1
    finally:
        (session / 'batch-result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(f'CO.4 batch {result["status"]} '
              f'({sum(x["status"] == "PASS" for x in result["cases"])}/3)')
        print(f'CO.4 batch evidence: {session}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument('--check', action='store_true',
                         help='offline only; no MVS operations')
    options.add_argument('--run', action='store_true',
                         help='submit sequential guarded native MVS jobs')
    args = parser.parse_args()
    try:
        if args.check:
            validate_inputs()
            print('CO.4 three-case batch OFFLINE CHECK PASS')
            return 0
        return run_batch()
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f'CO.4 three-case batch FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
