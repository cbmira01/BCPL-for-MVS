#!/usr/bin/env python3
"""CO.1 compiler-only BCPL procedure-valued argument/native entry probe.

Run only the resident Cambridge compiler and textual CODE recovery. Never
assemble, link, GO, or change any permanent MVS data set or runtime object.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'packaging/milestones/coroutines/probes/co1-indirect-entry'
SOURCE = FIXTURE / 'source.bcpl'
PARM = FIXTURE / 'cambridge-parm.txt'
COMPILER = ROOT / 'tools/bootstrap/compile-mvs'
WORK = ROOT / 'workarea/co1-indirect-entry'

CHECKED = re.compile(
    r'^\s*BAL\s+14,\s*60\(11\)[^\n]*\n'
    r'\s*DC\s+A\(L(\d+)\)\s+STACK FRAME SIZE[^\n]*$', re.M
)
RAW_CHECKED = re.compile(r'^\s*BAL\s+14,\s*60\(11\)', re.M)
SIZE = re.compile(r'^L(\d+)\s+EQU\s+(\d+)\s+STACK FRAME SIZE\s*$', re.M)
INDIRECT_FORMALS = re.compile(r'^\s*STM\s+4,9,0\(15\)', re.M)
CALL = re.compile(r'^\s*BALR\s+6,4\b', re.M)
RETURN = re.compile(r'^\s*BCR\s+15,11\b', re.M)
WORKSPACE = re.compile(r'^\s*LA\s+15,\d+\(5\)', re.M)
WRONG_SERVICE = re.compile(r'^\s*BAL\s+14,(?:20|80)\(11\)', re.M)
JOB = re.compile(r'^JOB\s+(\d+)\s*$', re.M)


class ProbeError(ValueError):
    """Emitted-code oracle failed."""


def verify_assembler(text: str) -> dict[str, object]:
    """Verify prologues and normal call/return shape, not executed behavior."""
    entries = list(CHECKED.finditer(text))
    raw = len(RAW_CHECKED.findall(text))
    if raw < 4 or len(entries) != raw:
        raise ProbeError(f'checked entries: expected >=4 complete +60; {len(entries)}/{raw}')
    if WRONG_SERVICE.search(text):
        raise ProbeError('unexpected +20/+80 counting service under /CN')
    if len(INDIRECT_FORMALS.findall(text)) != 1:
        raise ProbeError('expected one CALLIND three-formal STM 4,9,0(15)')
    calls = len(CALL.findall(text))
    if calls < 3:
        raise ProbeError(f'expected >=3 BALR 6,4 calls, found {calls}')
    if not RETURN.search(text):
        raise ProbeError('missing BCR 15,11 normal return')
    if not WORKSPACE.search(text):
        raise ProbeError('missing LA 15,n(5) workspace formation')
    definitions: dict[str, list[int]] = {}
    for m in SIZE.finditer(text):
        definitions.setdefault(m.group(1), []).append(int(m.group(2)))
    sizes: list[int] = []
    for m in entries:
        vals = definitions.get(m.group(1), [])
        if len(vals) != 1 or vals[0] <= 0 or vals[0] % 4:
            raise ProbeError(f'missing, duplicate, zero or misaligned frame L{m.group(1)}')
        sizes.append(vals[0])
    return {'checked_entries': raw, 'three_formal_entries': 1,
            'ordinary_calls': calls, 'frame_sizes_bytes': sizes}


def run() -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    log, generated, summaryfile = (folder / n for n in
                                  ('compiler.log', 'generated.s370.asm', 'summary.json'))
    summary: dict[str, object] = {
        'probe': 'CO.1 /CN procedure-valued argument and indirect entry, compile-only',
        'status': 'FAIL', 'assembled': False, 'linked': False, 'native_go': False
    }
    try:
        if PARM.read_text(encoding='ascii').splitlines() != ['/CN' + '/'*77]:
            raise ProbeError('expected one 80-column /CN parameter record')
        source = SOURCE.read_text(encoding='ascii')
        if not all(s in source for s in
                   ('LET SUM2(A,B)', 'LET CALLIND(F,A,B) = F(A,B)',
                    'LET NEST(F,X)', 'NEST(SUM2,22)')):
            raise ProbeError('function-pointer fixture has changed')
        if not COMPILER.is_file():
            raise ProbeError('resident Cambridge compiler driver missing')
        summary['source_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        summary['parm_sha256'] = hashlib.sha256(PARM.read_bytes()).hexdigest()
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                              capture_output=True, text=True, check=False)
        summary['git_head'] = head.stdout.strip() if head.returncode == 0 else 'unknown'
        command = [sys.executable, str(COMPILER), str(SOURCE), '--compiler-image',
                   'CAMBCOMP', '--job-name', 'CO1IND', '--cambridge-parm',
                   str(PARM), '--output', str(generated)]
        with log.open('w', encoding='utf-8') as handle:
            run = subprocess.run(command, cwd=ROOT, stdout=handle,
                                 stderr=subprocess.STDOUT, check=False)
        summary['compiler_driver_rc'] = run.returncode
        ids = JOB.findall(log.read_text(encoding='utf-8', errors='replace'))
        if len(ids) == 1:
            summary['jes_job_id'] = ids[0]
        if run.returncode:
            raise ProbeError(f'compiler driver RC={run.returncode}')
        if len(ids) != 1:
            raise ProbeError('expected exactly one reported JES job number')
        if not generated.is_file() or not generated.stat().st_size:
            raise ProbeError('missing or empty generated assembler')
        found = verify_assembler(generated.read_text(encoding='latin-1'))
        summary.update(found)
        summary['status'] = 'PASS'
        print(f"CO.1 INDIRECT PASS: JOB {ids[0]}, checked {found['checked_entries']}, "
              f"three-formal {found['three_formal_entries']}, "
              f"calls {found['ordinary_calls']}; compile-only")
        return 0
    except (OSError, UnicodeError, ProbeError) as exc:
        summary['reason'] = str(exc)
        print(f'CO.1 INDIRECT FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        summaryfile.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        print(f'CO.1 INDIRECT evidence: {folder.relative_to(ROOT)}')


if __name__ == '__main__':
    raise SystemExit(run())
