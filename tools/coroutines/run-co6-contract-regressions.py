#!/usr/bin/env python3
"""CO.6 paired MR10/native coroutine regression panel.

--check / --list never submit MVS work. --run executes each separately
accepted paired driver, validates independent MVS receipts, and fails closed.
The historical MR10 fixed-stack probe is not part of this suite and is never
reported as passing or skipped here.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'tests/suites/coroutine-contract.tsv'
WORK = ROOT / 'workarea/co6-contract-regressions'
CASES = (
    ('co6-pair', 'tools/coroutines/run-co6-pair.py',
     'packaging/milestones/coroutines/candidates/co6-pair/expected.txt',
     'CO6PAIR', 'workarea/co6-pair', 11),
    ('co6-nested', 'tools/coroutines/run-co6-nested.py',
     'packaging/milestones/coroutines/candidates/co6-nested/expected.txt',
     'CO6NEST', 'workarea/co6-nested', 18),
)
EVIDENCE = re.compile(r'(?m)^CO\.6 PAIRED EVIDENCE: (\S+)\s*$')
JOBS = re.compile(r'^\d+$')
NATIVE_STEPS = {'ASMA': 0, 'ASML': 0, 'ASMM': 0,
                'ASMS': 0, 'LKED': 0, 'GO': 0}


class RegressionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RegressionError(message)


def manifest_cases() -> list[tuple]:
    require(MANIFEST.is_file(), 'missing CO.6 contract manifest')
    with MANIFEST.open('r', encoding='ascii', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        require(reader.fieldnames == ['case_id', 'runner', 'oracle'],
                'unexpected CO.6 regression manifest columns')
        records = list(reader)
    require(len(records) == len(CASES), 'CO.6 regression cases changed')
    for row, (ident, runner, oracle, prefix, evidence, count) in zip(records, CASES):
        require(row == {'case_id': ident, 'runner': runner, 'oracle': oracle},
                f'CO.6 regression case contract mismatch: {ident}')
        for rel in (runner, oracle):
            p = (ROOT / rel).resolve()
            require(p.is_relative_to(ROOT.resolve()) and p.is_file(),
                    f'missing or unsafe CO.6 input: {rel}')
        lines = (ROOT / oracle).read_text('ascii').splitlines()
        require(len(lines) == count and
                all(re.fullmatch(prefix + r' [A-Z0-9]+', x) for x in lines) and
                lines[-1] == prefix + ' PASS' and len(set(lines)) == count,
                f'bad CO.6 exact-record oracle: {ident}')
    return list(CASES)


def preflight(cases: list[tuple]) -> None:
    for ident, runner, _, _, _, _ in cases:
        proc = subprocess.run([sys.executable, '-B', str(ROOT / runner), '--check'],
                              cwd=ROOT, capture_output=True, text=True, check=False)
        require(proc.returncode == 0,
                f'CO.6 {ident} host preflight failed: {(proc.stdout + proc.stderr).strip()}')


def git_head() -> str:
    p = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                       capture_output=True, text=True, check=False)
    sha = p.stdout.strip()
    require(p.returncode == 0 and re.fullmatch(r'[a-f0-9]{40}', sha) is not None,
            'cannot pin the source Git revision')
    return sha


def strict_receipt(receipt: dict, case: tuple) -> dict:
    ident, _, oracle, _, _, count = case
    expected = [line.split(' ', 1)[1] for line in
                (ROOT / oracle).read_text('ascii').splitlines()]
    require(len(expected) == count, f'{ident}: stale oracle')
    require(receipt.get('status') == 'PASS' and
            receipt.get('selected') == ['mr10', 'native'] and
            isinstance(receipt.get('paths'), dict) and
            set(receipt['paths']) == {'mr10', 'native'},
            f'{ident}: missing complete MR10/native PASS evidence')
    mr10, native = receipt['paths']['mr10'], receipt['paths']['native']
    require(isinstance(mr10, dict) and mr10.get('status') == 'PASS' and
            mr10.get('records') == expected and
            mr10.get('phase_codes') == [0] * 7 and
            mr10.get('steps') == 14 and
            isinstance(mr10.get('job'), str) and
            JOBS.fullmatch(mr10['job']) is not None,
            f'{ident}: incomplete interpreted ICINT/JES evidence')
    jobs = native.get('compiler_jobs') if isinstance(native, dict) else None
    require(isinstance(native, dict) and native.get('status') == 'PASS' and
            native.get('records') == expected and
            native.get('steps') == NATIVE_STEPS and
            isinstance(jobs, list) and len(jobs) == 2 and
            all(isinstance(x, str) and JOBS.fullmatch(x) for x in jobs) and
            isinstance(native.get('native_job'), str) and
            JOBS.fullmatch(native['native_job']) is not None,
            f'{ident}: incomplete native Cambridge/IFOX/IEWL/GO evidence')
    return {'mr10_job': mr10['job'], 'compiler_jobs': jobs,
            'native_job': native['native_job'], 'records': count}


def result_path(log: str, case: tuple) -> Path:
    ident, _, _, _, root, _ = case
    matches = EVIDENCE.findall(log)
    require(len(matches) == 1, f'{ident}: ambiguous/missing paired evidence')
    raw = Path(matches[0])
    path = (raw if raw.is_absolute() else ROOT / raw).resolve()
    require(path.parent == (ROOT / root).resolve() and path.is_dir() and
            (path / 'result.json').is_file(),
            f'{ident}: result outside independent paired MVS evidence root')
    return path


def store(path: Path, obj: dict) -> None:
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def execute(cases: list[tuple]) -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    folder = Path(tempfile.mkdtemp(
        prefix=f'{now:%Y%m%dT%H%M%SZ}-{os.getpid()}-', dir=WORK))
    summary_path = folder / 'summary.json'
    summary = {'schema': 1, 'suite': 'coroutine-contract', 'git_head': git_head(),
               'started_utc': now.isoformat(), 'selected_cases': [c[0] for c in cases],
               'status': 'IN_PROGRESS',
               'cases': [{'id': c[0], 'status': 'NOT_RUN'} for c in cases]}
    store(summary_path, summary)
    print(f'CO6 REGRESSION EVIDENCE: {folder}', flush=True)
    for row, case in zip(summary['cases'], cases):
        ident, runner = case[:2]
        log_path = folder / f'{ident}.log'
        row['runner_log'] = str(log_path.relative_to(ROOT))
        try:
            with log_path.open('w', encoding='utf-8') as output:
                proc = subprocess.run([sys.executable, '-B', str(ROOT / runner), '--run'],
                                      cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                      check=False)
            log = log_path.read_text(encoding='utf-8', errors='replace')
            path = result_path(log, case)
            payload = json.loads((path / 'result.json').read_text('utf-8'))
            require(proc.returncode == 0, f'{ident}: paired runner RC={proc.returncode}')
            details = strict_receipt(payload, case)
            row.update({'status': 'PASS', 'paired_evidence':
                        str(path.relative_to(ROOT)), **details})
        except (OSError, RegressionError, ValueError, UnicodeError,
                json.JSONDecodeError) as exc:
            row.update({'status': 'FAIL', 'reason': str(exc)})
        store(summary_path, summary)
        print(f"{row['status']:<7} {ident}: {row.get('reason', 'exact paired MVS oracle and JES receipt')}",
              flush=True)
        if row['status'] != 'PASS':
            break
    summary['counts'] = {status: sum(c['status'] == status for c in summary['cases'])
                         for status in ('PASS', 'FAIL', 'NOT_RUN')}
    summary['status'] = ('PASS' if summary['counts']['PASS'] == len(cases)
                         else 'FAIL')
    summary['finished_utc'] = datetime.now(timezone.utc).isoformat()
    store(summary_path, summary)
    print('CO6 REGRESSION RESULT: ' + summary['status'], flush=True)
    print('SUMMARY: ' + str(summary_path), flush=True)
    return 0 if summary['status'] == 'PASS' else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true', help='host-only validation')
    modes.add_argument('--list', action='store_true', help='show paired case identities')
    modes.add_argument('--run', action='store_true', help='execute paired MVS regression suite')
    args = parser.parse_args(argv)
    try:
        cases = manifest_cases()
        if args.list:
            for case in cases:
                print(f'{case[0]}\tpaired MR10/native\t{case[5]} records')
            return 0
        preflight(cases)
        if args.check:
            print(f'CO6 CONTRACT CHECK: PASS ({len(cases)} cases; host-only)')
            return 0
        return execute(cases)
    except (OSError, RegressionError, UnicodeError, csv.Error) as exc:
        print(f'CO6 CONTRACT CHECK: FAIL ({exc})', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
