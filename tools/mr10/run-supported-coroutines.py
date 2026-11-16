#!/usr/bin/env python3
"""CO.6 supported MR10 coroutine regression; preserve historical negative.

Four canonical accepted development probes are run through run-dev-probes;
the separately named, valid-frame corrected fixture is compiled and run
with the same exact golden/JES check functions. --check never contacts MVS.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'mr10-kit-compiler/tests/10-coroutines/supported-manifest.tsv'
CANDIDATE = ROOT / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-co0-candidate.bcpl'
GOLDEN = ROOT / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-co0-candidate.expected'
HISTORICAL = ROOT / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-producer-consumer.bcpl'
HISTORICAL_GOLDEN = ROOT / 'mr10-kit-compiler/tests/10-coroutines/fixed-stack-producer-consumer.expected'
PROBES = ROOT / 'tools/mr10/run-dev-probes'
COMPILE = ROOT / 'tools/mr10/compile-and-run'
WORK = ROOT / 'workarea/mr10-supported-coroutines'
OLD_ID = '10-coroutines/fixed-stack-producer-consumer'
NEW_ID = '10-coroutines/fixed-stack-co0-candidate'
ACCEPTED = (
    '10-coroutines/compiler-probe',
    '10-coroutines/frame-layout-probe',
    '10-coroutines/resumeco-chain',
    '10-coroutines/create-delete-static-pool',
)
CASES = (*ACCEPTED, NEW_ID)
FIXED_BLOBS = {
    'candidate': 'e71b2268a9471aa0c960978f873917cf59c4d97c',
    'original': 'a36c336d03491544393325628fa0b8cb6dd54530',
    'original_golden': 'cf072c158142e0c0f653028e8b0fcb07b43b7a0e',
}
GOLDEN_LINES = tuple(
    line for i in range(1, 6)
    for line in (f'PRODUCER: {i}', f'CONSUMER: {i}')
)


class SupportedError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SupportedError(message)


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def validate() -> dict[str, str]:
    """Pin independent case identities and accepted historical bytes."""
    with MANIFEST.open(encoding='ascii', newline='') as handle:
        table = csv.DictReader(handle, delimiter='\t')
        require(table.fieldnames == ['case_id', 'source', 'oracle'],
                'supported manifest columns changed')
        rows = list(table)
    require(len(rows) == len(CASES) and
            [x['case_id'] for x in rows] == list(CASES),
            'supported case identities/order changed')
    root = ROOT.resolve()
    for entry in rows:
        ident = entry['case_id']
        for key in ('source', 'oracle'):
            rel = Path(entry[key])
            require(not rel.is_absolute() and '..' not in rel.parts and
                    '\\' not in entry[key] and len(entry) == 3,
                    f'{ident}: unsafe manifest path')
            path = (ROOT / rel).resolve()
            require(path.is_relative_to(root) and path.is_file(),
                    f'{ident}: missing/outside-repository {key}')
            name = ident.split('/')[-1]
            require(entry[key] == f'mr10-kit-compiler/tests/10-coroutines/{name}.' +
                    ('bcpl' if key == 'source' else 'expected'),
                    f'{ident}: source/oracle location changed')
    require(rows[-1]['source'] == str(CANDIDATE.relative_to(ROOT)) and
            rows[-1]['oracle'] == str(GOLDEN.relative_to(ROOT)),
            'corrected-frame candidate mapping changed')
    hashes = {'candidate': blob(CANDIDATE), 'original': blob(HISTORICAL),
              'original_golden': blob(HISTORICAL_GOLDEN)}
    require(hashes == FIXED_BLOBS,
            'historical or proven valid-frame source/golden bytes changed')
    expected = GOLDEN.read_text('ascii').splitlines()
    require(expected == list(GOLDEN_LINES) and
            HISTORICAL_GOLDEN.read_text('ascii').splitlines() == expected,
            'supported fixed-frame golden changed')
    require(all(x.isascii() and len(x) <= 80 for x in
                CANDIDATE.read_text('ascii').splitlines()),
            'corrected-frame BCPL violates source cards')
    for executable in (PROBES, COMPILE):
        require(executable.is_file(), f'missing established MR10 runner {executable}')
    require((ROOT / 'mr10-kit-compiler/asm/CURRENT').is_file(),
            'missing interpreter selection')
    require((ROOT / 'mr10-kit-compiler/asm/icintv19.asm').is_file(),
            'missing canonical ICINT19')
    return hashes


def load_probes():
    loader = SourceFileLoader('co6_supported_accepted_runner', str(PROBES))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    require(spec is not None and spec.loader is not None,
            'cannot import established MR10 probe validation')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_host(command: list[str], output: Path) -> int:
    with output.open('w', encoding='utf-8') as stream:
        return subprocess.run(command, cwd=ROOT, stdout=stream,
                              stderr=subprocess.STDOUT, check=False).returncode


def run_accepted(folder: Path, probe) -> dict:
    """Validate runner's entire four-probe receipt, not just RC=0."""
    log_path = folder / 'four-accepted.log'
    cmd = [sys.executable, '-B', str(PROBES), '--run']
    for ident in ACCEPTED:
        cmd += ['--case', ident]
    rc = run_host(cmd, log_path)
    log = log_path.read_text(encoding='utf-8', errors='replace')
    matches = re.findall(r'(?m)^MR10 PROBE EVIDENCE: (.+)\s*$', log)
    require(len(matches) == 1, 'accepted MR10 receipt path missing/ambiguous')
    path = Path(matches[0].strip()).resolve()
    require(path.parent == (ROOT / 'workarea/mr10-probes').resolve() and
            (path / 'summary.json').is_file(),
            'MR10 accepted receipt outside established workarea')
    payload = json.loads((path / 'summary.json').read_text(encoding='utf-8'))
    require(payload.get('suite') == 'mr10-probes' and
            payload.get('selected_cases') == list(ACCEPTED) and
            payload.get('continue_known_fixed_stack_failure') is False,
            'accepted MR10 source selection or mode changed')
    cases = payload.get('cases')
    require(isinstance(cases, list) and len(cases) == 4 and
            [x.get('id') for x in cases] == list(ACCEPTED),
            'accepted MR10 receipt case identities changed')
    counts = {k: sum(x.get('status') == k for x in cases)
              for k in ('PASS', 'FAIL', 'OBSERVED', 'NOT_RUN')}
    require(payload.get('counts') == counts and
            all(x.get('status') in counts for x in cases),
            'accepted MR10 statuses/counts invalid')
    require(counts['OBSERVED'] == 0, 'accepted MR10 probe must not remain OBSERVED')
    require((payload.get('status') == 'PASS') == (rc == 0) and
            (rc == (1 if counts['FAIL'] else 3 if counts['OBSERVED'] else 0)),
            'accepted MR10 runner RC/status disagreement')
    # Existing accepted runner already validated the entire raw JES output.
    for item in cases:
        if item.get('status') == 'PASS':
            require(item.get('verification') == 'ACCEPTED' and
                    item.get('runner_rc') == 0 and
                    item.get('interpreted_code') == 0 and
                    bool(item.get('jes_job_id')) and
                    len(item.get('jes_step_codes', [])) == len(probe.expected_jes_steps(item['id'])) and
                    item.get('jes_phase_codes') == [0] *
                    (1 + 2 * sum(n.startswith('COMP') for n, _ in
                                 probe.expected_jes_steps(item['id']))),
                    'accepted MR10 PASS lacks verified JES/ICINT receipt')
    return {'rc': rc, 'result': payload.get('status'), 'cases': cases,
            'source_evidence': str(path.relative_to(ROOT))}


def run_fixed(folder: Path, probe) -> dict:
    """Same code/golden/JES checks as accepted historical fixed-stack case."""
    interp = probe.current_interpreter()
    require(interp.resolve() == (ROOT / 'mr10-kit-compiler/asm/icintv19.asm').resolve(),
            'supported corrected frame requires canonical ICINT19')
    name = 'CO6VALID'
    jcl = folder / 'fixed-frame.jcl'
    log_path = folder / 'fixed-frame.log'
    cmd = [str(COMPILE), '--results', '--jcl', str(jcl), '--job-name', name,
           str(interp), str(CANDIDATE)]
    rc = run_host(cmd, log_path)
    output = log_path.read_text(encoding='utf-8', errors='replace')
    jobs = probe.JOB_RE.findall(output)
    require(rc == 0 and len(jobs) == 1,
            f'corrected-frame MR10 compiler RC={rc}, JES IDs={jobs}')
    require(probe.CODE_RE.findall(output) == ['0'],
            f'corrected-frame interpreted CODE is not zero: {probe.CODE_RE.findall(output)}')
    probe.verify_accepted_output(output, GOLDEN)
    # Reuse original *structural* JES contract (10 steps, 3 phase CODE=0)
    # without renaming/reclassifying the distinct original failing test.
    jes = probe.verify_jes_steps(jobs[0], name, folder, OLD_ID)
    return {'status': 'PASS', 'id': NEW_ID, 'jes_job_id': jobs[0],
            'runner_rc': rc, 'interpreted_code': 0,
            'golden': str(GOLDEN.relative_to(ROOT)),
            'source': str(CANDIDATE.relative_to(ROOT)),
            'jes_contract_template': OLD_ID, **jes}



def verify_coordinator_result(log: str, rc: int) -> dict:
    """Independent read-only revalidation for the project suite coordinator."""
    matches = re.findall(r'(?m)^MR10 SUPPORTED EVIDENCE: (.+)\s*$', log)
    require(len(matches) == 1, 'supported MR10 evidence path missing/ambiguous')
    folder = Path(matches[0].strip()).resolve()
    require(folder.parent == WORK.resolve() and
            (folder / 'summary.json').is_file(),
            'supported MR10 evidence outside expected workarea')
    result = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    require(result.get('schema') == 1 and
            result.get('suite') == 'mr10-coroutines-supported' and
            result.get('selected_cases') == list(CASES) and
            result.get('source_blobs') == FIXED_BLOBS,
            'supported MR10 evidence identity/source mismatch')
    cases = result.get('cases')
    require(isinstance(cases, list) and len(cases) == 5 and
            [x.get('id') for x in cases] == list(CASES),
            'supported MR10 case identities/order mismatch')
    states = [x.get('status') for x in cases]
    require(all(x in ('PASS', 'FAIL', 'NOT_RUN') for x in states),
            'unsupported MR10 result state')
    counts = {x: states.count(x) for x in ('PASS', 'FAIL', 'NOT_RUN')}
    require(counts == result.get('counts'),
            'supported MR10 receipt counts mismatch')
    if 'FAIL' in states:
        first = states.index('FAIL')
        require(states[:first] == ['PASS']*first and
                states[first+1:] == ['NOT_RUN'] * (len(states)-first-1),
                'supported MR10 FAIL did not fail-stop')
    else:
        require(states == ['PASS']*5,
                'incomplete supported MR10 campaign without failure')
    status = 'FAIL' if counts['FAIL'] else 'PASS'
    require(result.get('status') == status and rc == (1 if status == 'FAIL' else 0),
            'supported MR10 runner RC disagrees with evidence')

    # Four accepted cases must have their own established runner receipt.
    if any(x == 'PASS' for x in states[:4]):
        rel = result.get('accepted_evidence')
        require(isinstance(rel, str) and rel and
                not Path(rel).is_absolute() and '..' not in Path(rel).parts,
                'accepted MR10 subreceipt location missing/unsafe')
        folder_accepted = (ROOT / rel).resolve()
        require(folder_accepted.parent == (ROOT / 'workarea/mr10-probes').resolve(),
                'accepted MR10 subreceipt outside allowed workarea')
        source = json.loads((folder_accepted / 'summary.json').read_text('utf-8'))
        require(source.get('suite') == 'mr10-probes' and
                source.get('selected_cases') == list(ACCEPTED) and
                source.get('continue_known_fixed_stack_failure') is False,
                'accepted MR10 subreceipt misidentified')
        originals = source.get('cases')
        require(isinstance(originals, list) and len(originals) == 4 and
                [x.get('id') for x in originals] == list(ACCEPTED),
                'accepted MR10 cases reordered')
        for item, original in zip(cases[:4], originals):
            require(item['status'] == original.get('status'),
                    'accepted MR10 status differs from source receipt')
            if item['status'] == 'PASS':
                steps = original.get('jes_step_codes')
                codes = original.get('jes_phase_codes')
                declared_steps = load_probes().expected_jes_steps(item['id'])
                expected_steps = [{'step': step, 'program': pgm, 'rc': 0}
                                  for step, pgm in declared_steps]
                expected_codes = [0] * (1 + 2 * sum(
                    step.startswith('COMP') for step, _ in declared_steps))
                require(original.get('verification') == 'ACCEPTED' and
                        original.get('runner_rc') == 0 and
                        original.get('interpreted_code') == 0 and
                        item.get('jes_job_id') == original.get('jes_job_id') and
                        bool(item.get('jes_job_id')) and
                        steps == expected_steps and codes == expected_codes,
                        'accepted MR10 PASS lacks source JES verification')
    if cases[4]['status'] == 'PASS':
        item = cases[4]
        require(item.get('runner_rc') == 0 and item.get('interpreted_code') == 0 and
                bool(item.get('jes_job_id')) and
                item.get('jes_contract_template') == OLD_ID and
                item.get('source') == str(CANDIDATE.relative_to(ROOT)) and
                item.get('golden') == str(GOLDEN.relative_to(ROOT)) and
                item.get('jes_phase_codes') == [0, 0, 0] and
                item.get('jes_step_codes') == [
                    {'step': name, 'program': program, 'rc': 0}
                    for name, program in load_probes().expected_jes_steps(OLD_ID)],
                'corrected-frame JES/ICINT receipt incomplete')
        log_path = folder / 'fixed-frame.log'
        require(log_path.is_file(), 'corrected-frame compiler output missing')
        raw = log_path.read_text('utf-8', errors='replace')
        module = load_probes()
        require(module.JOB_RE.findall(raw) == [item['jes_job_id']] and
                module.CODE_RE.findall(raw) == ['0'],
                'corrected-frame compiler log does not confirm job/CODE=0')
        module.verify_accepted_output(raw, GOLDEN)
        jes_report = ROOT / item['jes_report']
        require(jes_report.resolve().parent == folder and jes_report.is_file(),
                'corrected-frame JES report not retained in run evidence')
        module.verify_jes_output_records(
            [line.strip() for line in jes_report.read_text('utf-8').splitlines()],
            GOLDEN_LINES)
    return {'status': status,
            'counts': {'PASS': counts['PASS'], 'FAIL': counts['FAIL'],
                       'SKIP': 0, 'BLOCKED': 0, 'TOTAL': 5},
            'supported_evidence': str(folder.relative_to(ROOT)),
            'cases': [{'id': x['id'], 'status': x['status'],
                       **({'reason': x.get('reason', 'see source evidence')}
                          if x['status'] == 'FAIL' else {})}
                      for x in cases]}


def save(path: Path, data: dict) -> None:
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def validate_baseline(probe) -> None:
    """Check the immutable historical accepted manifest and original JES shape."""
    require(probe.current_interpreter().resolve() ==
            (ROOT / 'mr10-kit-compiler/asm/icintv19.asm').resolve(),
            'supported MR10 coroutine suite requires canonical ICINT19')
    rows = probe.manifest_cases()
    accepted = {x['case_id']: x for x in rows if x['verification'] == 'ACCEPTED'}
    require(all(ident in accepted for ident in ACCEPTED) and
            OLD_ID in accepted and NEW_ID not in {x['case_id'] for x in rows},
            'historical MR10 manifest contract drift')
    require(probe.EXTRAS.TRACE[OLD_ID] == GOLDEN_LINES,
            'accepted original MR10 trace differs from valid-frame oracle')
    require(probe.expected_jes_steps(OLD_ID) == list(probe.EXPECTED_STEPS),
            'original fixed-stack JES step contract changed')


def execute() -> int:
    hashes = validate()
    probe = load_probes()
    # Historical validator runs host-only; never changes the accepted cases.
    validate_baseline(probe)
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{os.getpid()}-', dir=WORK))
    receipt = {'schema': 1, 'suite': 'mr10-coroutines-supported',
               'git_head': probe.git_head(), 'source_blobs': hashes,
               'selected_cases': list(CASES), 'status': 'IN_PROGRESS',
               'cases': [{'id': x, 'status': 'NOT_RUN'} for x in CASES]}
    path = folder / 'summary.json'
    save(path, receipt)
    print(f'MR10 SUPPORTED EVIDENCE: {folder}', flush=True)
    try:
        four = run_accepted(folder, probe)
        receipt['accepted_evidence'] = four['source_evidence']
        for i, src in enumerate(four['cases']):
            receipt['cases'][i] = {'id': src['id'], 'status': src['status'],
                                   **({'jes_job_id': src['jes_job_id']} if
                                      src.get('jes_job_id') else {}),
                                   **({'reason': src.get('reason', 'see source receipt')} if
                                      src['status'] == 'FAIL' else {})}
            print(f"{src['status']:<7} {src['id']}: accepted MR10 JES contract", flush=True)
        require(four['result'] in ('PASS', 'FAIL', 'UNVERIFIED'),
                'accepted runner returned invalid status')
        if four['rc'] != 0:
            raise SupportedError(f"four accepted MR10 probes returned {four['result']}")
        try:
            fixed = run_fixed(folder, probe)
            receipt['cases'][4] = fixed
            print(f'PASS    {NEW_ID}: valid-frame golden/JES contract', flush=True)
        except (OSError, ValueError) as exc:
            receipt['cases'][4] = {'id': NEW_ID, 'status': 'FAIL', 'reason': str(exc)}
            print(f'FAIL    {NEW_ID}: {exc}', flush=True)
    except (OSError, ValueError) as exc:
        receipt['reason'] = str(exc)
        if all(row['status'] == 'NOT_RUN' for row in receipt['cases']):
            receipt['cases'][0] = {'id': CASES[0], 'status': 'FAIL',
                                   'reason': str(exc)}
    finally:
        states = [r['status'] for r in receipt['cases']]
        counts = {k: states.count(k) for k in ('PASS', 'FAIL', 'NOT_RUN')}
        receipt['counts'] = counts
        receipt['status'] = 'PASS' if counts == {'PASS': 5, 'FAIL': 0, 'NOT_RUN': 0} else 'FAIL'
        save(path, receipt)
        print(f'MR10 SUPPORTED RESULT: {receipt["status"]}', flush=True)
    return 0 if receipt['status'] == 'PASS' else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true', help='offline source-contract checks only')
    group.add_argument('--run', action='store_true', help='submit real MR10 compiler/JES jobs')
    args = parser.parse_args(argv)
    try:
        if args.check:
            validate()
            validate_baseline(load_probes())
            print('MR10 SUPPORTED CHECK: PASS (5 source-verified cases; host-only)')
            return 0
        return execute()
    except (SupportedError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'MR10 supported preflight FAIL: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
