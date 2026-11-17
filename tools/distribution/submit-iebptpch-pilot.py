#!/usr/bin/env python3
"""TA.0: one authorized read-only IEBPTPCH job and private JES evidence intake.

No tape operations, no binary acceptance; private files stay in ignored workarea/.
Runs only when explicitly invoked; default job is the two-member EXT_OBJ pilot.
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
# Centralized, symlink-safe ignored-workarea evidence policy.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path
PREP = Path(__file__).with_name('prepare-iebptpch-readback.py')
CORE = ROOT / 'tools/datasets/dspal-core.py'
JOBNAME = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}\Z')


class PilotError(ValueError):
    pass


def load_python(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PilotError(f'cannot import {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_output_dir(path: Path) -> None:
    try:
        guard_evidence_path(path, new=True, root=ROOT)
    except ValueError as exc:
        raise PilotError('output must be a new private directory under repository workarea/') from exc

def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open('rb') as file:
        while chunk := file.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def save_private(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(content)


def capture_window(core, config: dict, cursor: Path, output: Path) -> None:
    # Keep original window bytes; core.job_report() deliberately normalizes CR.
    printer = ROOT / str(config['runtime']['printer'])
    command = [sys.executable, str(ROOT / 'tools/mvs/printer-window.py'),
               'read', '--printer', str(printer), '--cursor-file', str(cursor)]
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        cp = subprocess.run(command, cwd=ROOT, stdout=stream,
                            stderr=subprocess.PIPE, check=False, timeout=120)
    if cp.returncode != 0:
        raise PilotError(f'printer-window failed (status {cp.returncode}); do not retry blindly')


def run_one(core, prep, *, key: str, members: list[str], output: Path,
            jobname: str = 'TA0MULT') -> dict:
    """One read-only JES job; output stays in ignored workarea/ and cannot overwrite."""
    if not JOBNAME.fullmatch(jobname):
        raise PilotError('invalid MVS jobname')
    validate_output_dir(output)
    config = core.load_config()
    body = prep.make_job_body(prep.load_yaml(prep.MANIFEST),
                              prep.load_yaml(prep.DSPAL),
                              dataset_key=key, members=members,
                              hlq=config['mvs']['hlq'])
    source = config['datasets'].get(key)
    if not isinstance(source, dict):
        raise PilotError('selected MVS source is missing from active dspal configuration')
    dsn = core.full_dsn(config, source)
    if f'//SYSUT1   DD DSN={dsn},DISP=SHR\n' not in body:
        raise PilotError('active MVS dataset mapping differs from the canonical design mapping')
    if not all((source.get(field) == want for field, want in
                (('dsorg', 'PO'), ('recfm', 'FB'), ('lrecl', 80), ('blksize', 800)))):
        raise PilotError('active source DCB not FB80/800; no job submitted')
    deck = '\n'.join(core.authenticated_job_card(config, jobname,
                                                 'TA0 OBJECT READBACK', False)) + '\n' + body
    # No JOB-card credentials are written to evidence files or echoed to stdout.
    os.mkdir(output, 0o700)
    cursor = output / 'cursor.json'
    save_private(output / 'job-body-redacted.jcl', body.encode('ascii'))
    job = None
    try:
        job, summary = core.submit_and_wait(config, deck, max_rc=0, cursor_file=cursor)
        save_private(output / 'job-summary.txt', summary.encode('utf-8'))
        report = core.job_report(job, cursor_file=cursor)
        if f'JOB {job}' not in report or f'PGM=IEBPTPCH' not in body:
            raise PilotError('report identity inconsistent; preserve evidence for investigation')
        save_private(output / 'job-report.txt', report.encode('utf-8'))
        capture_window(core, config, cursor, output / 'printer-window.raw')
        pin = {name: digest(output / name) for name in
               ('cursor.json', 'job-body-redacted.jcl', 'job-summary.txt',
                'job-report.txt', 'printer-window.raw')}
        receipt = {
            'phase': 'TA.0 MVS READBACK PILOT — NOT BINARY/RELEASE ACCEPTANCE',
            'job': job, 'jobname': jobname, 'step': 'TA0HEX',
            'source_dataset': dsn, 'dataset_key': key, 'requested_members': members,
            'sha256': pin, 'verification': 'IEBPTPCH RC=0000 and report captured; member bytes NOT decoded',
            'notes': ['Output reports may contain sensitive JOB credentials; do not commit.',
                      'Only reader/print evidence; independent resident bytes and build lineage absent.'],
        }
        save_private(output / 'receipt.json', (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    except Exception as exc:
        # Keep evidence/cursor for the operator; NEVER silently retry a potentially submitted job.
        save_private(output / 'failure.txt',
                     (f'JOB={job if job is not None else "unknown"}; aborted: {type(exc).__name__}\n').encode('utf-8'))
        raise
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-key', default='EXT_OBJ',
                        choices=('EXT_OBJ', 'BOOT_OBJ', 'MR10_OBJ'))
    parser.add_argument('--member', action='append', required=True,
                        help='selected FB80 member; repeat for a multi-member pilot')
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='new absolute directory outside the Git checkout')
    parser.add_argument('--jobname', default='TA0MULT')
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        core = load_python(CORE, 'ta0_mvs_core')
        prep = load_python(PREP, 'ta0_mvs_readback_prep')
        receipt = run_one(core, prep, key=args.dataset_key, members=args.member,
                          output=args.output_dir, jobname=args.jobname)
    except (PilotError, OSError, ValueError, RuntimeError) as exc:
        print(f'TA.0 PILOT ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    print(f"TA.0 IEBPTPCH RC=0000: JOB {receipt['job']} ({receipt['jobname']})"
          f" {receipt['dataset_key']}({','.join(receipt['requested_members'])})")
    print(f"Private readback evidence: {args.output_dir}")
    print('No binary comparison or release acceptance asserted.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
