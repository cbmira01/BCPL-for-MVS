#!/usr/bin/env python3
"""CO.1 worker-entry/return ABI evidence: one MVS compiler-only run.

No assembler/link-edit/GO. Does not synthesize or install a coroutine frame.
"""
from __future__ import annotations

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
FIXTURE = ROOT / 'packaging/milestones/coroutines/probes/co1-worker-entry'
SOURCE = FIXTURE / 'source.bcpl'
PARM = FIXTURE / 'cambridge-parm.txt'
COMPILER = ROOT / 'tools/bootstrap/compile-mvs'
RUNTIME = ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'
ORACLE = ROOT / 'tools/bootstrap/co1-worker-frame-oracle.py'
WORK = ROOT / 'workarea/co1-worker-entry'
JOB = re.compile(r'^JOB\s+(\d+)\s*$', re.M)


class ProbeError(ValueError):
    pass


def load_oracle():
    spec = importlib.util.spec_from_file_location('co1_worker_frame_oracle', ORACLE)
    if spec is None or spec.loader is None:
        raise ProbeError('worker frame oracle module missing')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run() -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    log = folder / 'compiler.log'
    output = folder / 'generated.s370.asm'
    summary_path = folder / 'summary.json'
    result: dict[str, object] = {
        'probe': 'CO.1 one-argument worker entry and native source return-frame contract',
        'status': 'FAIL', 'assembled': False, 'linked': False, 'native_go': False,
        'model_only_first_activation': True,
    }
    try:
        if PARM.read_text(encoding='ascii').splitlines() != ['/CN' + '/' * 77]:
            raise ProbeError('parameter file must be one 80-column /CN record')
        src = SOURCE.read_text(encoding='ascii')
        if not all(token in src for token in ('LET WORKER(ARG) = ARG+1',
                                              'LET INVOKE(F,VALUE) = F(VALUE)',
                                              'INVOKE(WORKER,41)')):
            raise ProbeError('BCPL worker-entry source fixture changed')
        if not COMPILER.is_file() or not RUNTIME.is_file():
            raise ProbeError('resident compiler driver or tracked runtime source missing')
        mod = load_oracle()
        result.update(mod.verify_runtime_return(RUNTIME.read_text(encoding='ascii')))
        result['source_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        result['parm_sha256'] = hashlib.sha256(PARM.read_bytes()).hexdigest()
        result['runtime_source_sha256'] = hashlib.sha256(RUNTIME.read_bytes()).hexdigest()
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True,
                              capture_output=True, check=False)
        result['git_head'] = head.stdout.strip() if head.returncode == 0 else 'unknown'
        cmd = [sys.executable, '-B', str(COMPILER), str(SOURCE), '--compiler-image',
               'CAMBCOMP', '--job-name', 'CO1WRET', '--cambridge-parm', str(PARM),
               '--output', str(output)]
        with log.open('w', encoding='utf-8') as handle:
            proc = subprocess.run(cmd, cwd=ROOT, stdout=handle,
                                  stderr=subprocess.STDOUT, check=False)
        result['compiler_driver_rc'] = proc.returncode
        found = JOB.findall(log.read_text(encoding='utf-8', errors='replace'))
        if len(found) == 1:
            result['jes_job_id'] = found[0]
        if proc.returncode != 0:
            raise ProbeError(f'compiler driver RC={proc.returncode}')
        if len(found) != 1:
            raise ProbeError('expected exactly one JES job number')
        if not output.is_file() or not output.stat().st_size:
            raise ProbeError('compiler emitted no assembler listing')
        contents = output.read_text(encoding='latin-1')
        result['listing_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
        result.update(mod.verify_compiler_listing(contents))
        result['status'] = 'PASS'
        print(f"CO.1 WORKER PASS: JOB {found[0]}, entries 0/1/2, "
              f"calls {result['ordinary_calls']}, checked 3; compile-only")
        return 0
    except (OSError, UnicodeError, ProbeError, ValueError) as exc:
        result['reason'] = str(exc)
        print(f'CO.1 WORKER FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        summary_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(f'CO.1 WORKER evidence: {folder.relative_to(ROOT)}')


if __name__ == '__main__':
    raise SystemExit(run())
