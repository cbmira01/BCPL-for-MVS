#!/usr/bin/env python3
"""CO.4 ACCOUNT + DENY MVS follow-up; preserve the proven LIMITS case.

Each case receives independent Cambridge/IFOX/IEWL/GO/JES evidence.
Continue after an oracle-only failure (GO was already RC=0000), but
stop on compile, JES, abend, evidence or infrastructure failure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT/'tools/coroutines/run-co4-inspection-batch.py'
WORK = ROOT/'workarea/co4-inspection-followup'
CASES = ('account', 'deny')


class FollowupError(ValueError):
    pass


def load_prior():
    spec = importlib.util.spec_from_file_location('co4_inspection_prior', PRIOR)
    if spec is None or spec.loader is None:
        raise FollowupError('accepted inspection runner unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_diagnostics(prior) -> None:
    """Diagnostic markers appear only on a failed path, never on PASS."""
    signatures = {
        'account': ('FALLOC', 'FPROB0', 'FINIT0', 'FPROBE',
                    'FLIMIT', 'FCURR', 'FCOUNT', 'FBYTES', 'FPEAK',
                    'FBPROBE', 'FBOOT', 'FBCOUNT', 'FBBYTES', 'FBPEAK'),
        'deny': ('FALLOC', 'FPROB0', 'FINIT0', 'FMAKE',
                 'FPROBE', 'FCOUNT', 'FBYTES', 'FPEAK'),
    }
    for key, tokens in signatures.items():
        source, _, _ = prior.CASES[key]
        content = (prior.FIXTURE/source).read_text('ascii')
        for token in tokens:
            if content.count(f'MARK("{token}")') != 1:
                raise FollowupError(f'{key}: diagnostic marker {token} drift')
        if content.count('MARK("FAIL")') != 1:
            raise FollowupError(f'{key}: failure sentinel drift')
        if 'SNAP(N,B)' not in content or 'LET P=PROBEPTR' not in content:
            raise FollowupError(f'{key}: SNAP contract changed')
        if content.count('PROBEPTR:=P') != 1:
            raise FollowupError(f'{key}: probe pointer publication drift')
        if key == 'account':
            # Only the two snapshots before first CREATECO may observe
            # unregistered private CURPTR=0. After that, SNAP remains strict.
            if (content.count('AND BOOTSNAP(N,B) = VALOF') != 1 or
                    content.count('IF BOOTSNAP(N+1,BYTES+108)=FALSE') != 2 or
                    'P!4 \\= 0 | CO3CURR \\= CO3ROOT' not in content or
                    content.count('IF SNAP(N+1,BYTES+108)=FALSE') != 1 or
                    content.index('IF BOOTSNAP(') > content.index(
                        'FOR I=1 TO 12 DO')):
                raise FollowupError('account: bootstrap CURPTR contract drift')


def validate_inputs(prior) -> dict:
    pins = prior.validate_inputs()
    if tuple(prior.CASES) != ('limits', 'account', 'deny'):
        raise FollowupError('accepted three-case definitions changed')
    source_diagnostics(prior)
    return pins


def oracle_only_failure(item: dict) -> bool:
    """The inherited JES gate validates all zero-RC steps first."""
    return (item.get('status') == 'FAIL' and item.get('rc') == 1
            and bool(item.get('native_job'))
            and str(item.get('reason') or '').startswith(
                'wrong ordered BCPL records:'))


def run_followup(prior, *, work: Path = WORK,
                 cases: tuple[str, ...] = CASES) -> int:
    if (not cases or len(set(cases)) != len(cases) or
            any(case not in CASES for case in cases)):
        raise FollowupError('invalid selected CO.4 cases')
    pins = validate_inputs(prior)
    os.umask(0o077)
    work.mkdir(parents=True, exist_ok=True)
    session = Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=work))
    receipt = {
        'march': 'CO.4', 'candidate': 'inspection-followup',
        'status': 'FAIL', 'cases': [], 'selected_cases': list(cases),
        'source_verification': pins,
        'previous_limits_pass_git_head':
            'b0ce46fd965d1ca7720594fc5516ad7dd12f3993',
        'installed_mvs_objects_modified': False,
        'public_global_allocation': False,
    }
    try:
        previous = prior.load_module('co4_followup_prior_base', prior.BASE)
        for key in cases:
            item = prior.run_one(key, session, previous, pins)
            receipt['cases'].append(item)
            if item.get('status') != 'PASS' and not oracle_only_failure(item):
                receipt['reason'] = f'{key}: infrastructure/JES failure'
                print('CO.4 followup STOP: non-oracle failure')
                break
            if oracle_only_failure(item):
                print('CO.4 followup: continue after zero-RC oracle mismatch')
        else:
            if all(x.get('status') == 'PASS' for x in receipt['cases']):
                receipt['status'] = 'PASS'
        if receipt['status'] != 'PASS' and 'reason' not in receipt:
            receipt['reason'] = 'one or more exact native BCPL oracles failed'
        return 0 if receipt['status'] == 'PASS' else 1
    except (OSError, ValueError, UnicodeError) as exc:
        receipt['reason'] = str(exc)
        print(f'CO.4 followup FAIL: {exc}')
        return 1
    finally:
        (session/'batch-result.json').write_text(
            json.dumps(receipt, indent=2)+'\n')
        passed = sum(x.get('status') == 'PASS' for x in receipt['cases'])
        print(f'CO.4 followup {receipt["status"]} '
              f'({passed}/{len(cases)} PASS)')
        print(f'CO.4 followup evidence: {session}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--check', action='store_true',
                         help='offline source/contract validation; no MVS')
    actions.add_argument('--run', action='store_true',
                         help='explicitly submit ACCOUNT then DENY')
    parser.add_argument('--case', choices=CASES,
                        help='run one pending case; default runs both')
    args = parser.parse_args()
    if args.check and args.case:
        parser.error('--case requires --run (offline check validates both)')
    try:
        prior = load_prior()
        if args.check:
            validate_inputs(prior)
            print('CO.4 inspection followup OFFLINE CHECK PASS')
            return 0
        selected = (args.case,) if args.case else CASES
        return run_followup(prior, cases=selected)
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f'CO.4 followup FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
