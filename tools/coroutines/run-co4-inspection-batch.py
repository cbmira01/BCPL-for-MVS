#!/usr/bin/env python3
"""CO.4 private S1/MEMSTAT observation and deterministic refusal batch.

Never changes accepted CO.3 source, installed BOOT_OBJ, or public globals.
--check is host-only; --run explicitly submits guarded native MVS jobs.
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
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (ROOT/'packaging/milestones/coroutines/candidates'
           /'co4-inspection-batch')
EXTENSION = FIXTURE/'co4probe.inc'
WORK = ROOT/'workarea/co4-inspection-batch'
BASE = ROOT/'tools/coroutines/run-co4-safe-negative.py'

# Case labels are private candidate names, not project regression numbers.
CASES = {
    'limits': ('limits-source.bcpl', 'CO4LIM',
               ('ROOT', 'MADE', 'A1', 'RA1', 'B1', 'RB1', 'A2',
                'RA2', 'B2', 'RB2', 'CLEAN', 'PASS')),
    'account': ('account-source.bcpl', 'CO4MEM',
                ('INIT', 'INVALID', 'C03', 'C06', 'C09', 'C12',
                 'CLEAN', 'PASS')),
    'deny': ('deny-source.bcpl', 'CO4DENY',
             ('MADE', 'DENY1', 'A1', 'DENY2', 'A2', 'FULL',
              'RA3', 'B1', 'B2', 'B3', 'CLEAN', 'PASS')),
}
REQUIRED = {
    'limits': ('CO4PROB(P)', 'OBS(SELF,1024)', 'OBS(ROOT,16384)',
               'BASEBYTES+9084', 'BASEBYTES+108', 'DELETECO(A)'),
    'account': ('GETVEC(-1)', 'GETVEC(4194300)',
                'FOR I=1 TO 12 DO', 'CREATECO(WORK,1024)',
                'SNAP(P,N+5,BYTES+9084)', 'DELETECO(B)'),
    'deny': ('GETVEC:=DENY', 'GETVEC:=SAVEDGET',
             'FAILAT:=1', 'FAILAT:=2', 'REQUESTS:=0',
             'R:=CREATECO(WORK,1024)', 'SAVEDGET(N)',
             'SNAP(P,N+3,BYTES+4596)', 'CALLCO(A,13)',
             'DELETECO(B)'),
}


class CandidateError(ValueError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CandidateError(f'unavailable accepted runner: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_records(report: str, prefix: str) -> list[str]:
    found = []
    for number, raw in enumerate(report.replace('\f', '').splitlines(), 1):
        row = raw.strip()
        if not row.startswith(prefix):
            continue
        match = re.fullmatch(re.escape(prefix)+r'\s+([A-Z0-9]+)', row)
        if match is None:
            raise CandidateError(f'malformed {prefix} record at line {number}')
        found.append(match.group(1))
    return found


def validate_case(case: str, root: Path = ROOT) -> dict[str, object]:
    if case not in CASES:
        raise CandidateError(f'unknown CO.4 inspection case: {case}')
    name, prefix, expected = CASES[case]
    path = root/FIXTURE.relative_to(ROOT)/name
    raw = path.read_bytes()
    try:
        source = raw.decode('ascii')
    except UnicodeDecodeError as exc:
        raise CandidateError(f'{name}: non-ASCII BCPL') from exc
    for number, line in enumerate(source.splitlines(), 1):
        if len(line) > 80 or '\t' in line or line.startswith('Z9'):
            raise CandidateError(f'{name}: invalid FB80 card {number}')
    for token in REQUIRED[case]:
        if token not in source:
            raise CandidateError(f'{name}: missing contract {token}')
    if source.count('CO4PROB:301') != 1:
        raise CandidateError(f'{name}: private G301 probe declaration missing')
    if 'CO3ROOT:=0' not in source or 'CO3LIST:=0' not in source:
        raise CandidateError(f'{name}: root initialization missing')
    if 'MARK("FAIL")' not in source or source.count('MARK("FAIL")') != 1:
        raise CandidateError(f'{name}: failure oracle missing/duplicated')
    for token in expected:
        if source.count(f'MARK("{token}")') != 1:
            raise CandidateError(f'{name}: wrong/duplicate oracle {token}')
    for bad in ('CALLCO(1,', 'RESUMECO(1,', 'CHANGECO(1,'):
        if bad in source:
            raise CandidateError(f'{name}: unsafe descriptor API')
    if case == 'deny':
        # Fault injection is bounded and immediately undone before a probe.
        if source.count('GETVEC:=DENY') != 2 or source.count(
                'GETVEC:=SAVEDGET') != 2:
            raise CandidateError('G87 override/restore pair changed')
    return {'file': name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'oracle_prefix': prefix, 'oracle_count': len(expected)}


def validate_extension(root: Path = ROOT) -> dict[str, str]:
    raw = (root/EXTENSION.relative_to(ROOT)).read_bytes()
    try:
        source = raw.decode('ascii')
    except UnicodeDecodeError as exc:
        raise CandidateError('non-ASCII IFOX probe') from exc
    for i, line in enumerate(source.splitlines(), 1):
        if len(line) > 71 or '\t' in line:
            raise CandidateError(f'IFOX probe card {i} invalid')
    required = ('CO4PROB  STM   4,10,0(15)', 'L     4,=A(STKLIM)',
                'L     4,=A(APLIMIT)', 'L     0,CURPTR',
                'L     15,=A(MEMSTAT)', 'BALR  14,15',
                'LR    14,8', 'L     10,24(5)', 'BCR   15,11')
    if any(source.count(x) != 1 for x in required):
        raise CandidateError('unexpected test-only IFOX ABI/source contract')
    restore = ('LR    4,10', 'L     15,=A(MEMSTAT)',
               'BALR  14,15', 'LR    10,4', 'LR    14,8',
               'SR    7,7', 'B     C4PRET')
    locations = [source.find(s) for s in restore]
    if (any(source.count(s) != 1 for s in restore) or
            locations != sorted(locations) or any(x < 0 for x in locations)):
        raise CandidateError('CO4PROB must restore R10 base after MEMSTAT')
    if 'GETMAIN' in source or 'FREEMAIN' in source:
        raise CandidateError('observer must not allocate')
    return {'file': 'co4probe.inc', 'sha256': hashlib.sha256(raw).hexdigest()}


def validate_inputs() -> dict[str, object]:
    previous = load_module('co4_observe_source_pin', BASE)
    pinned = previous.validate_inputs()
    return {'accepted_co3': pinned, 'probe': validate_extension(),
            'cases': {name: validate_case(name) for name in CASES}}


def patch_bridge(baseline: str, extension: str) -> str:
    entry = '         ENTRY CO2INIT,CHANGECO\n'
    anchor = "         DS    0F\nROOTPTR  DC    F'0'"
    if baseline.count(entry) != 1 or baseline.count(anchor) != 1:
        raise CandidateError('accepted BCPLCO insertion anchors changed')
    if 'CO4PROB' in baseline or 'MEMSTAT' in baseline:
        raise CandidateError('unexpected existing observer in Core Runtime')
    if extension.count('CO4PROB  STM') != 1:
        raise CandidateError('missing observer entry')
    result = baseline.replace(entry, entry+'         ENTRY CO4PROB\n'
                              +'         EXTRN MEMSTAT\n')
    return result.replace(anchor, extension.rstrip('\n')+'\n'+anchor)


def patch_application(rows: list[str], driver) -> list[str]:
    rows = list(rows)
    marker = '         EXTRN CO3DROP'
    if rows.count(marker) != 1 or any('CO4PROB' in x for x in rows):
        raise CandidateError('CO.3 application binding drifted')
    rows.insert(rows.index(marker)+1, '         EXTRN CO4PROB')
    start, last, maximum, pairs = driver.trailer(rows)
    if 1204 in {number for number, _ in pairs}:
        raise CandidateError('G301 already allocated by application')
    rows[start] = f"         DC F'{max(maximum, 1204)}'"
    rows[last:last] = ["         DC F'1204'", '         DC A(CO4PROB)']
    return driver.co2.checked_cards('\n'.join(rows), 'CO3APP')


def configure(driver, adapter, extension: str) -> None:
    adapter.configure(driver)
    prior_application = driver.generated_application
    prior_deck = driver.build_deck

    def application(source: str) -> list[str]:
        return patch_application(prior_application(source), driver)

    def deck(app: str, lib: str, main: str, bridge: str,
             jobcard: list[str], dsn: str) -> str:
        return prior_deck(app, lib, main, patch_bridge(bridge, extension),
                          jobcard, dsn)

    driver.generated_application = application
    driver.build_deck = deck


def configure_report_decoder(driver) -> None:
    """Decode only raw JES printer output using the project's byte policy.

    dump-report-for-job streams unconverted printer bytes. The inherited
    generic subprocess wrapper uses UTF-8 under a UTF-8 host locale; a
    high-bit printer byte can abort report capture. The
    accepted dspal job_report already decodes this boundary as latin-1.
    Leave git, Cambridge compiler, submit and job-summary commands on
    their existing decoding path. Do not modify any accepted runner.
    """
    report_program = str(driver.REPORT)
    inherited_shell = driver.co2.shell

    def shell(cmd: list[str], *, timeout: int = 240):
        if cmd and cmd[0] == report_program:
            return subprocess.run(cmd, cwd=driver.ROOT, text=True,
                                  encoding='latin-1', capture_output=True,
                                  check=False, timeout=timeout)
        return inherited_shell(cmd, timeout=timeout)

    driver.co2.shell = shell


def compiler_diagnostic(evidence: Path) -> str | None:
    for job in ('CO3ACMP', 'CO3LCMP'):
        path = evidence/(job+'.log')
        if not path.is_file():
            continue
        for line in reversed(path.read_text(errors='replace').splitlines()):
            value = line.strip()
            if value.startswith('cambridge-compile-mvs:'):
                return (job+': '+value)[:215]
    return None


def native_failure_detail(evidence: Path) -> str | None:
    """One short existing JES failure diagnostic, no fresh MVS operation."""
    summary = evidence/'job-summary.log'
    report = evidence/'job-report.log'
    if not summary.is_file():
        return None
    lines = summary.read_text(encoding='latin-1').splitlines()
    parts: list[str] = []
    for line in lines:
        line = line.strip()
        match = re.fullmatch(
            r'(ASMA|ASML|ASMM|ASMS|LKED|GO)\s+\S+\s+RC=(\d{4})', line)
        if match and match.group(2) != '0000':
            parts.append(match.group(1)+' RC='+match.group(2))
    if any('ABEND:' in line and 'detected' in line.lower() for line in lines):
        parts.append('JES ABEND')
    if report.is_file():
        for line in report.read_text(encoding='latin-1').splitlines():
            if ('IEF450I' in line and 'ABEND' in line) or (
                    'PSW AT ENTRY TO ABEND' in line):
                parts.append(line.strip())
                if len(parts) >= 4:
                    break
    return '; '.join(parts)[:280] if parts else None


def run_one(key: str, session: Path, previous, hashes: dict) -> dict:
    name, prefix, expected = CASES[key]
    case_dir = session/key
    case_dir.mkdir()
    with tempfile.TemporaryDirectory(prefix='_input-', dir=case_dir) as tmp:
        stage = Path(tmp)
        shutil.copyfile(FIXTURE/name, stage/'source.bcpl')
        for file in ('library.bcpl', 'cambridge-parm.txt'):
            shutil.copyfile(previous.ACCEPTED/file, stage/file)
        driver = previous.load_module('co4ins_driver_'+key,
                                      previous.BASE_RUNNER)
        adapter = previous.load_module('co4ins_adapter_'+key,
                                       previous.CO3_ADAPTER)
        configure(driver, adapter, EXTENSION.read_text('ascii'))
        configure_report_decoder(driver)
        driver.FIXTURE = stage
        driver.WORK = case_dir
        driver.EXPECTED = expected
        driver.observed_records = lambda report: parse_records(report, prefix)
        old = set(case_dir.iterdir())
        capture = io.StringIO()
        with redirect_stdout(capture):
            rc = driver.execute('first')
        created = [p for p in case_dir.iterdir() if p not in old and
                   p.is_dir() and (p/'result.json').is_file()]
        if len(created) != 1:
            raise CandidateError(f'{key}: missing/ambiguous MVS evidence')
        evidence = created[0]
        base = json.loads((evidence/'result.json').read_text())
        if (rc == 0) != (base.get('status') == 'PASS'):
            raise CandidateError(f'{key}: executor/receipt mismatch')
        diagnostic = compiler_diagnostic(evidence) if rc else None
        native_diagnostic = native_failure_detail(evidence) if rc else None
        outcome = {
            'case': key, 'status': base['status'], 'rc': rc,
            'reason': base.get('reason') if rc else None,
            'diagnostic': diagnostic,
            'native_diagnostic': native_diagnostic,
            'native_job': base.get('native_job'),
            'compiler_jobs': {n: base.get(n) for n in
                              ('CO3ACMP_job', 'CO3LCMP_job')},
            'evidence_dir': str(evidence), 'source': hashes['cases'][key],
            'expected_bcpl_records': [prefix+' '+x for x in expected],
            'inherited_result': 'result.json',
            'inherited_runner_stdout': capture.getvalue(),
            'evidence_class': base.get('evidence_class', 'MVS-pending'),
            'installed_mvs_objects_modified': False,
        }
        (evidence/'co4-case-result.json').write_text(
            json.dumps(outcome, indent=2)+'\n')
        print('CO.4 '+key.upper()+' '+('PASS' if rc == 0 else 'FAIL'))
        if diagnostic:
            print('CO.4 '+key.upper()+' compiler: '+diagnostic)
        if native_diagnostic:
            print('CO.4 '+key.upper()+' native: '+native_diagnostic)
        return outcome


def run_batch() -> int:
    hashes = validate_inputs()
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    result = {'march': 'CO.4', 'candidate': 'inspection-batch',
              'status': 'FAIL', 'cases': [], 'source_verification': hashes,
              'installed_mvs_objects_modified': False,
              'public_global_allocation': False}
    try:
        previous = load_module('co4ins_base', BASE)
        for key in CASES:
            case_result = run_one(key, session, previous, hashes)
            result['cases'].append(case_result)
            if case_result['status'] != 'PASS':
                result['reason'] = key+': '+str(case_result['reason'])
                return 1
        result['status'] = 'PASS'
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        result['reason'] = str(exc)
        print('CO.4 inspection batch FAIL: '+str(exc))
        return 1
    finally:
        (session/'batch-result.json').write_text(
            json.dumps(result, indent=2)+'\n')
        count = sum(x['status'] == 'PASS' for x in result['cases'])
        print(f'CO.4 inspection batch {result["status"]} ({count}/3)')
        print(f'CO.4 inspection evidence: {session}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true',
                      help='host-only identity/card/oracle verification')
    mode.add_argument('--run', action='store_true',
                      help='sequentially submit three native MVS cases')
    args = parser.parse_args()
    try:
        if args.check:
            validate_inputs()
            print('CO.4 inspection batch OFFLINE CHECK PASS')
            return 0
        return run_batch()
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f'CO.4 inspection batch FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
