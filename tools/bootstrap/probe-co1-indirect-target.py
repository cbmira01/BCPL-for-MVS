#!/usr/bin/env python3
"""One fresh MVS compile-only CALLIND target audit with retained receipts.

Runs the existing independently accepted structural compiler probe and
then checks the R4 target in the named CALLIND procedure. No IFOX/IEWL/GO.
"""
from __future__ import annotations

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
EVIDENCE = re.compile(r'^CO\.1 INDIRECT evidence: (workarea/co1-indirect-entry/[^\s/]+)\s*$', re.M)
RESULT = re.compile(r'^CO\.1 INDIRECT PASS: JOB (\d+), checked (\d+), '
                    r'three-formal (\d+), calls (\d+); compile-only\s*$', re.M)


def evidence_path(output: str) -> Path:
    paths = EVIDENCE.findall(output)
    if len(paths) != 1:
        raise ValueError('expected one fresh CO.1 INDIRECT evidence location')
    target = (ROOT / paths[0]).resolve()
    if target.parent != BASE.resolve():
        raise ValueError('evidence path must be an immediate child of workarea/co1-indirect-entry')
    return target


def extract_result(stdout: str, summary: dict[str, object]) -> str:
    found = RESULT.findall(stdout)
    if len(found) != 1:
        raise ValueError('no unique structural compiler-only PASS report')
    job, entries, formals, calls = found[0]
    if (summary.get('status') != 'PASS' or summary.get('jes_job_id') != job or
            summary.get('checked_entries') != int(entries) or
            summary.get('three_formal_entries') != int(formals) or
            summary.get('ordinary_calls') != int(calls) or
            summary.get('compiler_driver_rc') != 0 or
            summary.get('assembled') is not False or
            summary.get('linked') is not False or
            summary.get('native_go') is not False):
        raise ValueError('structural PASS differs from saved compiler summary')
    return job


def run() -> int:
    os.umask(0o077)
    folder: Path | None = None
    audit_record: dict[str, object] = {
        'probe': 'CO.1 CALLIND R4 target origin after fresh MVS compile-only',
        'status': 'FAIL', 'assembled': False, 'linked': False, 'native_go': False,
    }
    try:
        # The existing probe preserves compiler.log, generated.s370.asm and
        # summary.json even when the MVS compiler or structural oracle fails.
        with subprocess.Popen([sys.executable, str(OLD_PROBE)], cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True) as child:
            stdout, stderr = child.communicate()
            rc = child.returncode
        folder = evidence_path(stdout)
        if not folder.is_dir():
            raise ValueError('fresh evidence directory missing')
        (folder / 'target-probe.log').write_text(stdout + stderr, encoding='utf-8')
        if rc:
            raise ValueError(f'original compile-only structural probe RC={rc}')
        summary = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
        job = extract_result(stdout, summary)
        listing = (folder / 'generated.s370.asm').read_text(encoding='latin-1')
        audit_record['listing_sha256'] = hashlib.sha256(listing.encode('latin-1')).hexdigest()
        audit_record['structural_compiler_job'] = job
        audit_record['source_git_head'] = summary.get('git_head')
        audit_record['compiler_driver_rc'] = summary.get('compiler_driver_rc')
        # Import a pure parser: no resident MVS operations in this step.
        spec = importlib.util.spec_from_file_location('co1_indirect_target_audit', AUDIT)
        if spec is None or spec.loader is None:
            raise ValueError('cannot load indirect target audit')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        audit_record.update(module.audit_indirect_target(listing))
        audit_record['status'] = 'PASS'
        print(f"CO.1 TARGET PASS: JOB {job}, {audit_record['entry_label']}, "
              f"origin {audit_record['target_origin']}; compile-only")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
        audit_record['reason'] = str(exc)
        print(f'CO.1 TARGET FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        if folder is not None and folder.is_dir():
            (folder / 'target-audit.json').write_text(
                json.dumps(audit_record, indent=2) + '\n', encoding='utf-8'
            )
            print(f'CO.1 TARGET evidence: {folder.relative_to(ROOT)}')


if __name__ == '__main__':
    raise SystemExit(run())
