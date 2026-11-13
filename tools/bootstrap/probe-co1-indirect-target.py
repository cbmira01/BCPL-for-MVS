#!/usr/bin/env python3
"""Audit a fresh or saved MVS compiler-only CALLIND listing.

--reuse-evidence replays retained MVS compiler output without JES submission.
Never modifies the preexisting target-audit.json from a failed run.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'workarea/co1-indirect-entry'
OLD_PROBE = ROOT / 'tools/bootstrap/probe-co1-indirect-entry.py'
AUDIT = ROOT / 'tools/bootstrap/co1-indirect-target-audit.py'
SOURCE = ROOT / 'packaging/milestones/coroutines/probes/co1-indirect-entry/source.bcpl'
PARM = ROOT / 'packaging/milestones/coroutines/probes/co1-indirect-entry/cambridge-parm.txt'
EVIDENCE = re.compile(r'^CO\.1 INDIRECT evidence: (workarea/co1-indirect-entry/[^\s/]+)\s*$', re.M)
RESULT = re.compile(r'^CO\.1 INDIRECT PASS: JOB (\d+), checked (\d+), '
                    r'three-formal (\d+), calls (\d+); compile-only\s*$', re.M)


def evidence_path(output: str) -> Path:
    paths = EVIDENCE.findall(output)
    if len(paths) != 1:
        raise ValueError('expected exactly one original MVS evidence location')
    target = (ROOT / paths[0]).resolve()
    if target.parent != BASE.resolve():
        raise ValueError('evidence path is outside the expected MVS workarea')
    return target


def select_reuse(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    if resolved.parent != BASE.resolve():
        raise ValueError('reuse path must be one directory under workarea/co1-indirect-entry')
    if not resolved.is_dir():
        raise ValueError('saved MVS evidence directory is absent')
    return resolved


def extract_result(output: str, summary: dict[str, object]) -> str:
    result = RESULT.findall(output)
    if len(result) != 1:
        raise ValueError('saved evidence lacks a unique structural compiler PASS')
    job, entries, formals, calls = result[0]
    if (summary.get('status') != 'PASS' or summary.get('jes_job_id') != job or
            summary.get('checked_entries') != int(entries) or
            summary.get('three_formal_entries') != int(formals) or
            summary.get('ordinary_calls') != int(calls) or
            summary.get('compiler_driver_rc') != 0 or
            summary.get('assembled') is not False or
            summary.get('linked') is not False or
            summary.get('native_go') is not False):
        raise ValueError('saved structural PASS disagrees with summary.json')
    return job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-evidence', metavar='WORKAREA_PATH',
                        help='audit saved MVS compiler output, without new JES submission')
    return parser.parse_args()


def run() -> int:
    os.umask(0o077)
    args = parse_args()
    folder: Path | None = None
    replay = args.reuse_evidence is not None
    receipt: dict[str, object] = {
        'probe': 'CO.1 verified CALLIND R4 target origin from MVS compiler text',
        'audit_version': 2, 'status': 'FAIL', 'reused_existing_mvs_job': replay,
        'assembled': False, 'linked': False, 'native_go': False,
    }
    try:
        if replay:
            folder = select_reuse(args.reuse_evidence)
            output = (folder / 'target-probe.log').read_text(encoding='utf-8')
        else:
            # The original structural probe preserves its full compiler output.
            process = subprocess.run([sys.executable, '-B', str(OLD_PROBE)], cwd=ROOT,
                                     text=True, capture_output=True, check=False)
            output = process.stdout + process.stderr
            folder = evidence_path(output)
            if not folder.is_dir():
                raise ValueError('new compiler evidence directory missing')
            (folder / 'target-probe.log').write_text(output, encoding='utf-8')
            if process.returncode:
                raise ValueError(f'original compiler structural probe RC={process.returncode}')
        summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
        if not isinstance(summary, dict):
            raise ValueError('saved compiler summary is not a JSON object')
        job = extract_result(output, summary)
        if summary.get('source_sha256') != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
            raise ValueError('saved compiler source hash differs from tracked probe fixture')
        if summary.get('parm_sha256') != hashlib.sha256(PARM.read_bytes()).hexdigest():
            raise ValueError('saved compiler parameter hash differs from tracked /CN fixture')
        assembler = (folder / 'generated.s370.asm').read_bytes()
        receipt['listing_sha256'] = hashlib.sha256(assembler).hexdigest()
        receipt['source_git_head'] = summary.get('git_head')
        receipt['compiler_driver_rc'] = summary.get('compiler_driver_rc')
        receipt['jes_job_id'] = job
        spec = importlib.util.spec_from_file_location('co1_target_audit', AUDIT)
        if spec is None or spec.loader is None:
            raise ValueError('could not import target audit')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt.update(module.audit_indirect_target(assembler.decode('latin-1')))
        receipt['status'] = 'PASS'
        qualifier = 'saved MVS compiler evidence; no new JES' if replay else 'compile-only'
        print(f"CO.1 TARGET PASS: JOB {job}, R4 from {receipt['target_origin']}; {qualifier}")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        receipt['reason'] = str(exc)
        print(f'CO.1 TARGET FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        if folder is not None and folder.is_dir():
            name = 'target-audit-v2.json' if replay else 'target-audit.json'
            (folder / name).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
            print(f'CO.1 TARGET evidence: {folder.relative_to(ROOT)}')


if __name__ == '__main__':
    raise SystemExit(run())
