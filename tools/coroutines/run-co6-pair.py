#!/usr/bin/env python3
"""CO.6: independently execute a paired MR10/native BCPL coroutine oracle.

--check is host-only. --run submits one MR10 compiler/interpreter job,
two Cambridge compilation jobs and one isolated IFOX/IEWL/native GO job.
Never installs or overwrites BOOT_OBJ. Full JES evidence goes to workarea.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'packaging/milestones/coroutines/candidates/co6-pair'
ACCEPTED = ROOT / 'packaging/milestones/coroutines/candidates/co3-delete-reuse'
WORK = ROOT / 'workarea/co6-pair'
CO3_DRIVER = ROOT / 'tools/coroutines/run-co3-first-lifecycle.py'
CO3_ADAPTER = ROOT / 'tools/coroutines/run-co3-delete-reuse.py'
DEPENDENCY_GIT_BLOBS = {
    'library.bcpl': '1dfd3e22b9580ced14d356e76b816220300eac17',
    'co3drop.inc': '869479a8718dc5a4cb0b716ac6a22de56e0c4e9d',
    'cambridge-parm.txt': '2d280050102b2e98caaf96541f59a39eb473da9c',
}
MR10 = ROOT / 'tools/mr10/compile-and-run'
ICINT = ROOT / 'mr10-kit-compiler/asm/icintv19.asm'
MR10_MODULES = (
    ROOT / 'mr10-kit-compiler/library/getvec-freevec.bcpl',
    ROOT / 'mr10-kit-compiler/library/coroutines.bcpl',
)
SUMMARY = ROOT / 'tools/mvs/job-summary'
REPORT = ROOT / 'tools/mvs/dump-report-for-job'
ORACLE = ('MADE', 'W1', 'R1', 'W2', 'R2', 'W3', 'R3',
          'W4', 'R4', 'DEL', 'PASS')
EXPECTED_STEPS = (
    ('ASM', 'IFOX00'), ('LKED', 'IEWL'),
    ('STGSYNI', 'IEBGENER'), ('STGTRNI', 'IEBGENER'),
    ('STGCGI', 'IEBGENER'), ('STGBLIB', 'IEBGENER'),
    ('STGICLIB', 'IEBGENER'),
    ('COMP01', 'RUNMOD'), ('CG01', 'RUNMOD'),
    ('COMP02', 'RUNMOD'), ('CG02', 'RUNMOD'),
    ('COMP03', 'RUNMOD'), ('CG03', 'RUNMOD'),
    ('RUN', 'RUNMOD'),
)
CODE_RE = re.compile(r'EXECUTION CYCLES\s*=\s*\d+,\s*CODE\s*=\s*(-?\d+)')
JOB_RE = re.compile(r'(?m)^JOB\s+(\d+)\s*$')
STEP_RE = re.compile(r'^\s*([A-Z0-9]+)\s+([A-Z0-9]+)\s+RC=(\d{4})\s*$')


class PairError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise PairError(reason)


def records(text: str) -> list[str]:
    """Return only complete, unambiguous CO6PAIR logical records."""
    seen = []
    for line in text.replace('\f', '').splitlines():
        row = line.strip()
        if not row.startswith('CO6PAIR'):
            continue
        match = re.fullmatch(r'CO6PAIR\s+([A-Z0-9]+)', row)
        if match is None:
            raise PairError(f'malformed CO6PAIR output: {row!r}')
        seen.append(match.group(1))
    return seen


def validate_inputs() -> dict[str, str]:
    oracle = (FIXTURE / 'expected.txt').read_text('ascii').splitlines()
    require(oracle == ['CO6PAIR ' + x for x in ORACLE],
            'paired golden oracle changed')
    observed = {}
    for flavor in ('mr10', 'native'):
        path = FIXTURE / (flavor + '.bcpl')
        raw = path.read_bytes()
        source = raw.decode('ascii')
        for number, row in enumerate(source.splitlines(), 1):
            require(len(row) <= 80 and '\t' not in row,
                    f'{flavor} BCPL card {number} exceeds 80 columns')
        for marker in ORACLE:
            require(source.count('MARK("' + marker + '")') == 1,
                    f'{flavor}: missing or repeated {marker} marker')
        for snippet in ('CALLCO(CO,11)', 'CALLCO(CO,31)',
                        'CALLCO(CO,51)', 'CALLCO(CO,71)',
                        'COWAIT(21)', 'COWAIT(41)',
                        'DELETECO(CO)', 'KEEP=717'):
            require(snippet in source, f'{flavor}: missing {snippet}')
        observed[flavor + '_sha256'] = hashlib.sha256(raw).hexdigest()
    require('CREATECO(WORK,100)' in (FIXTURE / 'mr10.bcpl').read_text('ascii'),
            'MR10 interpreted allocation contract changed')
    require('CREATECO(WORK,1024)' in (FIXTURE / 'native.bcpl').read_text('ascii'),
            'native checked stack contract changed')
    for path in (*MR10_MODULES, ICINT, MR10, CO3_DRIVER, CO3_ADAPTER,
                 SUMMARY, REPORT, ACCEPTED / 'library.bcpl',
                 ACCEPTED / 'cambridge-parm.txt', ACCEPTED / 'co3drop.inc'):
        require(path.is_file(), f'missing required Git-backed input: {path}')
    for name, expected in DEPENDENCY_GIT_BLOBS.items():
        raw = (ACCEPTED / name).read_bytes()
        prefix = f'blob {len(raw)}\0'.encode('ascii')
        actual = hashlib.sha1(prefix + raw).hexdigest()
        require(actual == expected, f'accepted CO.3 dependency drift: {name}')
    require((ACCEPTED / 'cambridge-parm.txt').read_text('ascii').splitlines()
            == ['/CN' + '/'*77], 'native Cambridge checked /CN contract changed')
    return observed


def shell(args: list[str], log: Path, timeout: int = 600) -> subprocess.CompletedProcess:
    with log.open('w', encoding='utf-8') as stream:
        return subprocess.run(args, cwd=ROOT, stdout=stream,
                              stderr=subprocess.STDOUT, timeout=timeout,
                              check=False)


def run_mr10(folder: Path) -> dict:
    output = folder / 'mr10-compile.log'
    command = [str(MR10), '--results', '--job-name', 'CO6MPAIR',
               '--jcl', str(folder / 'mr10.jcl'), str(ICINT),
               str(FIXTURE / 'mr10.bcpl'),
               *(('+' + str(p)) for p in MR10_MODULES)]
    proc = shell(command, output)
    text = output.read_text(encoding='utf-8', errors='replace')
    jobs = JOB_RE.findall(text)
    require(proc.returncode == 0 and len(jobs) == 1,
            f'MR10 compiler RC={proc.returncode}, jobs={jobs}')
    job = jobs[0]
    summary_file = folder / 'mr10-jes-summary.log'
    report_file = folder / 'mr10-jes-report.log'
    summary_proc = shell([str(SUMMARY), job, '--max-rc', '0'], summary_file)
    report_proc = shell([str(REPORT), job], report_file)
    summary = summary_file.read_text(encoding='utf-8', errors='replace')
    report = report_file.read_text(encoding='utf-8', errors='replace')
    require(summary_proc.returncode == 0 and report_proc.returncode == 0,
            'MR10 JES retrieval or return-code failure')
    require(re.search(rf'^JOB\s+{re.escape(job)}\s+CO6MPAIR\s*$', summary, re.M)
            is not None and 'JOB RESULT: SUCCESS' in summary and
            'HIGHEST RC: 0000' in summary, 'MR10 JES job/status mismatch')
    steps = [m.groups() for line in summary.splitlines()
             if (m := STEP_RE.fullmatch(line))]
    require(steps == [(name, pgm, '0000') for name, pgm in EXPECTED_STEPS],
            f'MR10 missing or nonzero JES steps: {steps}')
    codes = [int(value) for value in CODE_RE.findall(report)]
    require(codes == [0]*7, f'MR10 interpreted phase codes: {codes}')
    actual = records(report)
    require(actual == list(ORACLE), f'MR10 program records: {actual}')
    return {'status': 'PASS', 'job': job, 'steps': len(steps),
            'phase_codes': codes, 'records': actual}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f'cannot import native driver: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_native(folder: Path) -> dict:
    native_work = folder / 'native'
    native_work.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='_inputs-', dir=folder) as tmp:
        stage = Path(tmp)
        shutil.copyfile(FIXTURE / 'native.bcpl', stage / 'source.bcpl')
        for item in ('library.bcpl', 'cambridge-parm.txt'):
            shutil.copyfile(ACCEPTED / item, stage / item)
        driver = load_module(CO3_DRIVER, 'co6_co3_driver')
        adapter = load_module(CO3_ADAPTER, 'co6_co3_adapter')
        adapter.configure(driver)
        driver.FIXTURE = stage
        driver.WORK = native_work
        driver.EXPECTED = ORACLE
        driver.observed_records = records
        before = set(native_work.iterdir())
        output = io.StringIO()
        with redirect_stdout(output):
            rc = driver.execute('first')
        (folder / 'native-driver.log').write_text(output.getvalue(), encoding='utf-8')
        created = [p for p in native_work.iterdir() if p not in before and
                   p.is_dir() and (p / 'result.json').is_file()]
        require(len(created) == 1, 'native runner did not produce one evidence receipt')
        receipt = created[0]
        result = json.loads((receipt / 'result.json').read_text('utf-8'))
        require(rc == 0 and result.get('status') == 'PASS',
                f'native runner failure: {result.get("reason", "RC=" + str(rc))}')
        require(result.get('bcpl_records') == list(ORACLE),
                'native receipt disagrees with paired oracle')
        require(result.get('steps') == {name: 0 for name in
                ('ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO')},
                'native IFOX/IEWL/GO receipts incomplete')
        require(result.get('native_job') and result.get('CO3ACMP_job') and
                result.get('CO3LCMP_job'), 'native compiler/GO job identity missing')
        require(records((receipt / 'job-report.log').read_text('latin-1')) ==
                list(ORACLE), 'native raw JES oracle mismatch')
        return {'status': 'PASS', 'compiler_jobs': [result['CO3ACMP_job'],
                result['CO3LCMP_job']], 'native_job': result['native_job'],
                'steps': result['steps'], 'records': result['bcpl_records'],
                'evidence': str(receipt.relative_to(ROOT))}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true', help='host-only source verification')
    mode.add_argument('--run', action='store_true', help='run both MVS paths independently')
    mode.add_argument('--run-mr10', action='store_true', help='run interpreted MVS path only')
    mode.add_argument('--run-native', action='store_true', help='run native MVS path only')
    args = parser.parse_args(argv)
    try:
        hashes = validate_inputs()
        if args.check:
            print('CO.6 paired source and oracle CHECK PASS')
            return 0
        os.umask(0o077)
        WORK.mkdir(parents=True, exist_ok=True)
        folder = Path(tempfile.mkdtemp(
            prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
        result = {'march': 'CO.6', 'status': 'FAIL',
                  'sources': hashes, 'selected': [], 'paths': {}}
        for name, action in (('mr10', run_mr10), ('native', run_native)):
            if args.run or getattr(args, 'run_' + name):
                result['selected'].append(name)
                try:
                    result['paths'][name] = action(folder)
                    print(f'CO.6 {name.upper()} PASS')
                except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                    result['paths'][name] = {'status': 'FAIL', 'reason': str(exc)}
                    print(f'CO.6 {name.upper()} FAIL: {exc}', file=sys.stderr)
        result['status'] = ('PASS' if all(
            item['status'] == 'PASS' for item in result['paths'].values())
            else 'FAIL')
        (folder / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
        print('CO.6 PAIRED RESULT: ' + result['status'])
        print('CO.6 PAIRED EVIDENCE: ' + str(folder.relative_to(ROOT)))
        return 0 if result['status'] == 'PASS' else 1
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'CO.6 paired preflight FAIL: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
