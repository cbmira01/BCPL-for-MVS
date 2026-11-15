#!/usr/bin/env python3
"""CO.4 recoverable negative-path native candidate.

Reuse the accepted CO.3 candidate adapter and independent-compilation
pipeline without changing either.  --check is strictly offline;
--run is an explicit operator-controlled MVS submission.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co4-safe-negative')
ACCEPTED = (ROOT / 'packaging/milestones/coroutines/candidates'
            / 'co3-delete-reuse')
WORK = ROOT / 'workarea/co4-safe-negative'
BASE_RUNNER = ROOT / 'tools/coroutines/run-co3-first-lifecycle.py'
CO3_ADAPTER = ROOT / 'tools/coroutines/run-co3-delete-reuse.py'
EXPECTED = ('INIT', 'SIZE', 'ROOT', 'MADE', 'FULL', 'BADDEL',
            'A1', 'RA1', 'B1', 'RB1', 'A2', 'RA2', 'B2', 'RB2',
            'CLEAN', 'PASS')

# Git blob identities of the accepted CO.3 files at authoritative
# main aca120fdf444e8aa8a14f8167b1fb2a74f28f337.
CO3_BLOBS = {
    'library.bcpl': '1dfd3e22b9580ced14d356e76b816220300eac17',
    'co3drop.inc': '869479a8718dc5a4cb0b716ac6a22de56e0c4e9d',
    'cambridge-parm.txt': '2d280050102b2e98caaf96541f59a39eb473da9c',
}


class CandidateError(ValueError):
    pass


def git_blob_id(data: bytes) -> str:
    prefix = f'blob {len(data)}\0'.encode('ascii')
    return hashlib.sha1(prefix + data).hexdigest()


def validate_inputs(root: Path = ROOT) -> dict[str, str]:
    """Fail closed on unsupported CO.3 source drift; perform no I/O to MVS."""
    fixture = root / FIXTURE.relative_to(ROOT)
    accepted = root / ACCEPTED.relative_to(ROOT)
    source = fixture / 'source.bcpl'
    raw = source.read_bytes()
    try:
        code = raw.decode('ascii')
    except UnicodeDecodeError as exc:
        raise CandidateError('CO.4 BCPL must be ASCII') from exc
    for number, row in enumerate(code.splitlines(), 1):
        if len(row) > 80 or '\t' in row:
            raise CandidateError(f'CO.4 BCPL card {number} exceeds 80 columns')
    # Source-contract tripwire, not a substitute for real BCPL parsing.
    for token in ('CREATECO(AWORK,1023)', 'CREATECO(AWORK,1025)',
                  'CREATECO(AWORK,-1)', 'CREATECO(AWORK,1024)',
                  'CREATECO(BWORK,1024)', 'COWAIT(9)',
                  'RESUMECO(0,9)', 'DELETECO(0)',
                  'DELETECO(ROOT)', 'DELETECO(1)',
                  'DELETECO(SELF)', 'CALLCO(A,11)', 'CALLCO(B,21)',
                  'CALLCO(A,12)', 'CALLCO(B,22)',
                  'DELETECO(A)', 'DELETECO(B)'):
        if token not in code:
            raise CandidateError(f'CO.4 negative source contract changed: {token}')
    for bad in ('CALLCO(1,', 'RESUMECO(1,', 'CHANGECO(1,'):
        if bad in code:
            raise CandidateError('unsafe descriptor passed to callable interface')
    for token in EXPECTED:
        if len(re.findall(r'\bMARK\("' + token + r'"\)', code)) != 1:
            raise CandidateError(f'CO.4 output marker not unique: {token}')
    if 'MARK("FAIL")' not in code:
        raise CandidateError('CO.4 negative-output marker missing')
    observed = {'co4_source_sha256': hashlib.sha256(raw).hexdigest()}
    for name, expected in CO3_BLOBS.items():
        actual = git_blob_id((accepted / name).read_bytes())
        if actual != expected:
            raise CandidateError(f'accepted CO.3 source drift: {name}')
        observed[name + '_git_blob'] = actual
    if (accepted / 'cambridge-parm.txt').read_text('ascii').splitlines() != [
            '/CN' + '/' * 77]:
        raise CandidateError('accepted Cambridge /CN options changed')
    for path in (root / BASE_RUNNER.relative_to(ROOT),
                 root / CO3_ADAPTER.relative_to(ROOT),
                 root / 'bootstrap-toolchain/asm/bcplco.asm',
                 root / 'bootstrap-toolchain/asm/bcplmain.asm'):
        if not path.is_file():
            raise CandidateError(f'missing accepted runner/runtime: {path}')
    return observed


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateError(f'unavailable inherited runner: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def observed_records(report: str) -> list[str]:
    """Parse only exact CO4SAFE records; reject truncation/extra tokens."""
    found: list[str] = []
    for line_no, raw in enumerate(report.replace('\f', '').splitlines(), 1):
        row = raw.strip()
        if not row.startswith('CO4SAFE'):
            continue
        match = re.fullmatch(r'CO4SAFE\s+([A-Z0-9]+)', row)
        if match is None:
            raise CandidateError(f'malformed CO.4 record at JES line {line_no}')
        found.append(match.group(1))
    return found


def configure(driver, adapter, staged_fixture: Path, work: Path) -> None:
    """Apply the accepted CO.3 machinery, then select only CO.4 inputs."""
    adapter.configure(driver)
    driver.FIXTURE = staged_fixture
    driver.WORK = work
    driver.EXPECTED = EXPECTED
    driver.observed_records = observed_records


def run() -> int:
    hashes = validate_inputs()
    WORK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='_input-', dir=WORK) as tmp:
        stage = Path(tmp)
        shutil.copyfile(FIXTURE / 'source.bcpl', stage / 'source.bcpl')
        for name in ('library.bcpl', 'cambridge-parm.txt'):
            shutil.copyfile(ACCEPTED / name, stage / name)
        driver = load_module('co4_co3_engine', BASE_RUNNER)
        adapter = load_module('co4_co3_adapter', CO3_ADAPTER)
        configure(driver, adapter, stage, WORK)
        existing = set(WORK.iterdir())
        inherited_stdout = io.StringIO()
        with redirect_stdout(inherited_stdout):
            rc = driver.execute('first')
        created = [p for p in WORK.iterdir()
                   if p not in existing and p.is_dir() and
                   (p / 'result.json').is_file()]
        if len(created) != 1:
            raise CandidateError('CO.4 must produce exactly one new evidence run')
        evidence_dir = created[0]
        inherited = json.loads((evidence_dir / 'result.json').read_text())
        if (rc == 0) != (inherited.get('status') == 'PASS'):
            raise CandidateError('CO.4 executor status contradicts its receipt')
        receipt = {
            'march': 'CO.4', 'candidate': 'safe-negative',
            'status': inherited['status'],
            'expected_bcpl_records': ['CO4SAFE ' + x for x in EXPECTED],
            'co3_executor_result': 'result.json',
            'co3_executor_stdout': inherited_stdout.getvalue(),
            'source_verification': hashes,
            'git_head': inherited.get('git_head', 'unknown'),
            'native_job': inherited.get('native_job'),
            'compiler_jobs': {key: inherited.get(key)
                              for key in ('CO3ACMP_job', 'CO3LCMP_job')},
            'evidence_class': inherited.get('evidence_class', 'MVS-pending'),
            'installed_mvs_objects_modified': False,
            'public_global_allocation': False,
        }
        (evidence_dir / 'co4-result.json').write_text(
            json.dumps(receipt, indent=2) + '\n')
        print('CO.4 safe negative ' + ('PASS' if rc == 0 else 'FAIL'))
        print(f'CO.4 native execution RC={rc}')
        print(f'CO.4 evidence: {evidence_dir}')
        return rc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true',
                      help='validate source and pinned baselines; no JES')
    mode.add_argument('--run', action='store_true',
                      help='explicitly submit two Cambridge and one native job')
    args = parser.parse_args()
    try:
        if args.check:
            result = validate_inputs()
            print('CO.4 safe negative OFFLINE CHECK PASS')
            for key, value in result.items():
                print(f'{key}: {value}')
            return 0
        return run()
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f'CO.4 safe negative FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
