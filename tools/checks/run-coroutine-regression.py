#!/usr/bin/env python3
"""Run one numbered CO.5 native coroutine regression with candidate-only linkage.

The existing accepted CO.2/CO.3/CO.4 runners own BCPL compilation, IFOX,
IEWL, GO, JES validation, and original exact-record oracles.  This adapter
preserves each runner's independent receipt and enforces the immutable numbered
fixture oracle before reporting success to the Bootstrap regression harness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RUNNERS = ROOT / 'tools/coroutines'
WORK = ROOT / 'workarea/co5-coroutines'

# Single source of truth for the numbered case -> accepted native driver route.
# No permanent MVS installation, public G! allocation, or library source copy.
CASES = {
    177: ('run-co2-native-changeco.py', (), 'co2-native-changeco', None),
    178: ('run-co2-native-continuations.py', (), 'co2-native-continuations', None),
    179: ('run-co3-first-lifecycle.py', ('--scenario', 'first'), 'co3-first-lifecycle', None),
    180: ('run-co3-first-lifecycle.py', ('--scenario', 'parent-chain'), 'co3-first-lifecycle', None),
    181: ('run-co3-delete-reuse.py', (), 'co3-delete-reuse', None),
    182: ('run-co4-bounded-stress.py', (), 'co4-bounded-stress', None),
    183: ('run-co4-safe-negative.py', (), 'co4-safe-negative', None),
    184: ('run-co4-verification-batch.py', (), None, 'stack'),
    185: ('run-co4-verification-batch.py', (), None, 'churn'),
    186: ('run-co4-verification-batch.py', (), None, 'busy'),
    187: ('run-co4-inspection-batch.py', (), None, 'limits'),
    188: ('run-co4-inspection-batch.py', (), None, 'deny'),
    189: ('run-co4-inspection-batch.py', (), None, 'account'),
}

SOURCE_REFS = {
    177: 'packaging/milestones/coroutines/candidates/co2-native-changeco/source.bcpl',
    178: 'packaging/milestones/coroutines/candidates/co2-native-continuations/source.bcpl',
    179: 'packaging/milestones/coroutines/candidates/co3-first-lifecycle/source.bcpl',
    180: 'packaging/milestones/coroutines/candidates/co3-first-lifecycle/parent-chain.bcpl',
    181: 'packaging/milestones/coroutines/candidates/co3-delete-reuse/source.bcpl',
    182: 'packaging/milestones/coroutines/candidates/co4-bounded-stress/source.bcpl',
    183: 'packaging/milestones/coroutines/candidates/co4-safe-negative/source.bcpl',
    184: 'packaging/milestones/coroutines/candidates/co4-verification-batch/stack-source.bcpl',
    185: 'packaging/milestones/coroutines/candidates/co4-verification-batch/churn-source.bcpl',
    186: 'packaging/milestones/coroutines/candidates/co4-verification-batch/busy-source.bcpl',
    187: 'packaging/milestones/coroutines/candidates/co4-inspection-batch/limits-source.bcpl',
    188: 'packaging/milestones/coroutines/candidates/co4-inspection-batch/deny-source.bcpl',
    189: 'packaging/milestones/coroutines/candidates/co4-inspection-batch/account-source.bcpl',
}

PREFIXES = {177: 'CO2BCPL', 178: 'CO2BCPL', 179: 'CO3BCPL',
            180: 'CO3BCPL', 181: 'CO3BCPL', 182: 'CO4BCPL',
            183: 'CO4SAFE'}


class RegressionError(ValueError):
    pass


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RegressionError(f'unavailable candidate runner: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(case_dir: Path, number: int) -> tuple[list[str], Path]:
    if case_dir.parent.resolve() != (ROOT / 'tests/coroutines').resolve():
        raise RegressionError('fixture outside numbered coroutine suite')
    if not re.fullmatch(rf'{number:03d}-[a-z0-9-]+', case_dir.name):
        raise RegressionError('numbered fixture directory does not match case ID')
    if (case_dir / 'coroutine-native.txt').read_text('ascii').strip() != 'candidate-source':
        raise RegressionError('missing or invalid candidate-only marker')
    rel = (case_dir / 'source-reference.txt').read_text('ascii').strip()
    if not rel or rel.startswith('/') or '..' in Path(rel).parts:
        raise RegressionError('unsafe source reference')
    if rel != SOURCE_REFS[number]:
        raise RegressionError('source reference does not match accepted candidate')
    source = (ROOT / rel).resolve()
    if not source.is_relative_to(ROOT.resolve()) or not source.is_file():
        raise RegressionError(f'missing Git-controlled BCPL source: {rel}')
    if not rel.endswith('.bcpl'):
        raise RegressionError('source reference must be BCPL')
    raw = (case_dir / 'expected.txt').read_bytes()
    try:
        records = raw.decode('ascii').splitlines()
    except UnicodeError as exc:
        raise RegressionError('non-ASCII BCPL output oracle') from exc
    if not records or not all(re.fullmatch(r'CO(?:2|3|4[A-Z]*)BCPL\s+[A-Z0-9]+|CO4(?:SAFE|STK|CHURN|BUSY|LIM|DENY|MEM)\s+[A-Z0-9]+', x) for x in records):
        # CO4BCPL and the individual CO4... prefixes are intentional.
        raise RegressionError('invalid or empty exact-record oracle')
    if records[-1].split()[-1] != 'PASS' or len(set(records)) != len(records):
        raise RegressionError('coroutine oracle must end PASS and contain unique records')
    if (case_dir / 'README.md').is_file() is False:
        raise RegressionError('case lacks README')
    return records, source


def accepted_contract(number: int, runner: Path, records: list[str]) -> None:
    if number >= 184:
        return
    module = load_module(runner, f'co5_contract_{number}')
    expected = getattr(module, 'PARENT_EXPECTED' if number == 180 else 'EXPECTED')
    wanted = [PREFIXES[number] + ' ' + token for token in expected]
    if records != wanted:
        raise RegressionError('numbered oracle differs from accepted native runner')


def native_records(result: dict, number: int, records: list[str]) -> None:
    if result.get('status') != 'PASS':
        raise RegressionError('native result is not PASS')
    if result.get('installed_mvs_objects_modified') is not False:
        raise RegressionError('native receipt does not certify read-only BOOT_OBJ')
    expected_tokens = [line.split(' ', 1)[1] for line in records]
    observed = (result.get('observed_native_records') if number in (177, 178)
                else result.get('bcpl_records'))
    if observed != expected_tokens:
        raise RegressionError(f'actual native record sequence differs: {observed!r}')
    steps = result.get('steps')
    required = ({'ASMA', 'ASMM', 'ASMS', 'LKED', 'GO'} if number <= 178 else
                {'ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO'})
    if not isinstance(steps, dict) or set(steps) != required or any(value != 0 for value in steps.values()):
        raise RegressionError(f'IFOX/IEWL/GO receipt incomplete: {steps!r}')
    if not (result.get('native_job_id') or result.get('native_job')):
        raise RegressionError('missing native JES job identity')
    if number <= 178:
        if not result.get('compiler_job_id'):
            raise RegressionError('missing Cambridge compiler job identity')
    elif not (result.get('CO3ACMP_job') and result.get('CO3LCMP_job')):
        raise RegressionError('missing independent application/library compiler jobs')


def run_single_candidate(number: int, runner: Path, extra: tuple, work_name: str,
                         records: list[str], source: Path) -> Path:
    evidence_root = ROOT / 'workarea' / work_name
    evidence_root.mkdir(parents=True, exist_ok=True)
    before = {p.resolve() for p in evidence_root.iterdir() if p.is_dir()}
    command = [sys.executable, '-B', str(runner), *extra, '--run']
    completed = subprocess.run(command, cwd=ROOT, capture_output=True,
                               text=True, errors='replace', check=False)
    print(completed.stdout, end='')
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end='')
    fresh = [p for p in evidence_root.iterdir() if p.is_dir() and p.resolve() not in before
             and (p / 'result.json').is_file()]
    if len(fresh) != 1:
        raise RegressionError(f'expected one fresh native receipt, found {len(fresh)}')
    receipt = fresh[0]
    result = json.loads((receipt / 'result.json').read_text('utf-8'))
    if completed.returncode != 0:
        raise RegressionError(f'candidate runner RC={completed.returncode}; evidence={receipt}')
    native_records(result, number, records)
    # Verify the report itself using the established candidate parser's strict
    # full-record oracle; receipt status alone is not accepted as output proof.
    report = (receipt / 'job-report.log').read_text('latin-1')
    if number <= 178:
        module = load_module(runner if number == 177 else RUNNERS / 'run-co2-native-changeco.py', 'co5_co2')
        parser = module.observed_records
        if number == 178:
            # The continuation fixture supplies the expanded set of output tokens.
            import re as regex
            matched = []
            for raw in report.replace('\f', '').splitlines():
                row = raw.strip()
                if not row.startswith('CO2BCPL'):
                    continue
                m = regex.fullmatch(r'CO2BCPL\s+([A-Z0-9]+)', row)
                if m is None:
                    raise RegressionError('malformed CO2 BCPL record')
                matched.append(m.group(1))
            if matched != [line.split(' ', 1)[1] for line in records]:
                raise RegressionError('CO2 continuation record mismatch')
        elif parser(report) != [line.split(' ', 1)[1] for line in records]:
            raise RegressionError('CO2 report record mismatch')
    else:
        # CO3/CO4 accepted parsers each check exact prefixes and ordering;
        # repeat an independent, strict prefix and token comparison here.
        prefix = records[0].split()[0]
        found = []
        for raw in report.replace('\f', '').splitlines():
            row = raw.strip()
            if not row.startswith(prefix):
                continue
            if re.fullmatch(re.escape(prefix) + r'\s+[A-Z0-9]+', row) is None:
                raise RegressionError(f'malformed {prefix} JES record')
            found.append(row)
        if found != records:
            raise RegressionError('JES BCPL records do not match exact oracle')
    return receipt


def run_batch_case(number: int, runner: Path, case_key: str,
                   records: list[str], source: Path) -> Path:
    batch = load_module(runner, f'co5_batch_{number}')
    hashes = batch.validate_inputs()  # Existing accepted source/hash/oracle pins.
    declared_source, prefix, tokens = batch.CASES[case_key]
    expected = [prefix + ' ' + t for t in tokens]
    if records != expected:
        raise RegressionError('numbered oracle disagrees with accepted candidate')
    if source != (batch.FIXTURE / declared_source).resolve():
        raise RegressionError('numbered source disagrees with accepted candidate')
    WORK.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(prefix=f'{number:03d}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    if number in (184, 185, 186):
        previous = batch.load_module(f'co5_previous_{number}', batch.SAFE_RUNNER)
    else:
        previous = batch.load_module(f'co5_previous_{number}', batch.BASE)
    item = batch.run_one(case_key, session, previous, hashes)
    (session / 'case-result.json').write_text(json.dumps(item, indent=2) + '\n', encoding='utf-8')
    if item.get('status') != 'PASS' or item.get('rc') != 0:
        raise RegressionError(f'candidate native case not PASS; evidence={session}')
    evidence = Path(item['evidence_dir'])
    if not evidence.is_absolute():
        evidence = ROOT / evidence
    evidence = evidence.resolve()
    if not evidence.is_relative_to(session.resolve()) or not (evidence / 'result.json').is_file():
        raise RegressionError('batch evidence path did not resolve to run session')
    result = json.loads((evidence / 'result.json').read_text('utf-8'))
    native_records(result, number, records)
    report = (evidence / 'job-report.log').read_text('latin-1')
    if batch.parse_records(report, prefix) != list(tokens):
        raise RegressionError('batch JES output disagrees with exact numbered oracle')
    return evidence


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('number', type=int, choices=sorted(CASES))
    parser.add_argument('case_dir', type=Path)
    parser.add_argument('--check', action='store_true', help='host-only case validation')
    parser.add_argument('--run', action='store_true', help='submit guarded native MVS work')
    args = parser.parse_args(argv)
    if args.check == args.run:
        parser.error('select exactly one of --check or --run')
    number = args.number
    script, extra, work_name, case_key = CASES[number]
    try:
        records, source = fixture(args.case_dir.resolve(), number)
        runner = RUNNERS / script
        if not runner.is_file():
            raise RegressionError(f'missing accepted runner: {script}')
        accepted_contract(number, runner, records)
        if args.check:
            if case_key is not None:
                batch = load_module(runner, f'co5_check_{number}')
                hashes = batch.validate_inputs()
                name, prefix, tokens = batch.CASES[case_key]
                if records != [prefix + ' ' + t for t in tokens] or source != (batch.FIXTURE / name).resolve():
                    raise RegressionError('numbered fixture differs from accepted native case')
            print(f'CO.5 {number:03d} host fixture CHECK PASS: {len(records)} records')
            return 0
        os.umask(0o077)
        if case_key is None:
            receipt = run_single_candidate(number, runner, extra, work_name, records, source)
        else:
            receipt = run_batch_case(number, runner, case_key, records, source)
        # Preserve actual native records in JES reports, not console chatter.
        print(f'CO.5 {number:03d} native JES oracle PASS; evidence={receipt}')
        return 0
    except (RegressionError, OSError, ValueError, UnicodeError) as exc:
        print(f'CO.5 {number:03d} FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
