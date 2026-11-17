#!/usr/bin/env python3
"""TA.0: bounded MVS ICINT19 executable-use pilot, using canonical MRREGRES case 01.

Runs one authorized JES job. Sources are read-only, and all created MVS
working datasets are temporary && names. The result is *not* a RECFM=U byte
comparison, a tape restore test, or the full 12-case MRREGRES acceptance.
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
JCL = ROOT / 'mr10-kit-compiler/jcl/run-regression-tests.jcl'
GOLD = ROOT / 'mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.expected'
CORE = ROOT / 'tools/datasets/dspal-core.py'
REVIEW = ROOT / 'tools/distribution/verify-iehlist-load-directory.py'
NAME = 'TA0ICEX'
STEPS = ('SSYNI', 'STRNI', 'SCGI', 'SBLIBI', 'SICLIB', 'C01A', 'G01A', 'R01')
PROGRAMS = ('IEBGENER',) * 5 + ('ICINT19',) * 3
# Git blob of the accepted, existing 12-case MRREGRES source, not an alternative suite.
# Reject an edited suite before selecting or submitting a subset of its steps.
SOURCE_BLOB = '28abf582b286401f483f1c11fcd63e303764f75e'
GOLDEN = ('RP: SCALAR 17 42', 'RP: VECTOR 5 10 15 20')
MAX_REPORT = 32 * 1024 * 1024
SHA = re.compile(r'[0-9a-f]{64}\Z')
EXEC = re.compile(r'^//([A-Z0-9]{1,8})\s+EXEC\s+PGM=([A-Z0-9]+)', re.M)
STEP_RC = re.compile(r'^\s*\S+\s+JOB\s+(\d+)\s+TA0ICEX\s+([A-Z0-9]{1,8})\s+(IEBGENER|ICINT19)\s+RC=\s*(\d{4})\s*$', re.M)
CODE = re.compile(r'\bCODE\s*=\s*([0-9]+)\b')
RP = re.compile(r'(?<![A-Z])RP:\s*(SCALAR|VECTOR)\s+([0-9 ]+)\b')


class ExecEvidenceError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ExecEvidenceError(message)


def import_file(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'required repo module missing')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_plain(path: Path, max_size: int = MAX_REPORT) -> bytes:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= max_size,
            'required source/evidence missing, linked or oversized')
    return path.read_bytes()


def private(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)


def external(path: Path, *, new: bool) -> None:
    require(path.is_absolute() and not path.is_symlink() and
            not path.resolve().is_relative_to(ROOT.resolve()),
            'private evidence path must be absolute and outside Git checkout')
    if new:
        require(not path.exists() and path.parent.is_dir() and not path.parent.is_symlink(),
                'output must be a new directory with existing plain parent')
    else:
        require(path.is_dir(), 'source evidence directory does not exist')


def validate_directory(evidence: Path, review_dir: Path):
    """Re-derive the reviewed IEHLIST identity and reject stale/transformed receipts."""
    external(evidence, new=False)
    external(review_dir, new=False)
    inspector = import_file(REVIEW, 'ta0_exec_review')
    original, pinned = inspector.pinned_files(evidence)
    report = inspector.validate_report(original, pinned)
    row = inspector.parse_directory(report, dsn=original['dsn'],
                                    volser=original['source_volume'], member='ICINT19')
    saved = json.loads(read_plain(review_dir / 'directory-review.json', 1024*1024))
    require(type(saved) is dict and saved.get('directory') == row and
            saved.get('job') == original['job'] and
            saved.get('source_receipt_sha256') == sha(read_plain(evidence/'receipt.json', 1024*1024)) and
            saved.get('source_job_report_sha256') == sha(pinned['job-report.txt']) and
            saved.get('source_printer_window_sha256') == sha(pinned['printer-window.raw']),
            'retained IEHLIST directory review does not match pinned original')
    require(row['entry_point_hex'] == '000000' and row['attributes_hex'] == '02E2',
            'unexpected observed ICINT19 directory entry/attributes; review required')
    return original, saved


def canonical_steps(source: bytes, *, hlq: str, load_dsn: str) -> tuple[str, str]:
    """Extract exactly eight proven MRREGRES blocks; no hand-coded substitute JCL."""
    git_blob = hashlib.sha1(b'blob ' + str(len(source)).encode('ascii') + b'\0' + source).hexdigest()
    require(git_blob == SOURCE_BLOB, 'MRREGRES source revision changed: review before running')
    require(hlq == 'HERC02' and load_dsn == 'HERC02.BCPL.MR10KIT.LOAD',
            'MRREGRES diagnostic body is scoped to the verified HERC02 development installation')
    text = source.decode('ascii')
    matches = list(EXEC.finditer(text))
    require(len(matches) > 8, 'MRREGRES source missing original steps')
    chosen = []
    for name, program in zip(STEPS, PROGRAMS):
        match_list = [m for m in matches if m.group(1) == name]
        require(len(match_list) == 1 and match_list[0].group(2) == program,
                'MRREGRES step missing, duplicated or program changed')
        match = match_list[0]
        next_comment = text.find('\n//*', match.start())
        require(next_comment != -1, 'MRREGRES step delimiter missing')
        block = text[match.start():next_comment+1]
        require(block.count('EXEC PGM=') == 1 and all(len(line) <= 80 for line in block.splitlines()),
                'unexpected JCL block content')
        chosen.append(block)
    body = '//* TA.0 READ-ONLY ORIGINAL PDS INPUTS; TEMPORARY && WORK ONLY.\n'
    body += '//* CANONICAL MRREGRES SCALAR-VECTOR CASE 01 ONLY.\n'
    body += '//* THIS IS NOT 12-CASE TA.4 REGRESSION ACCEPTANCE.\n'
    body += ''.join(block + '//*\n' for block in chosen)
    require(tuple(m.group(1) for m in EXEC.finditer(body)) == STEPS,
            'unexpected executable steps in extracted body')
    require(body.count('DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR') == 3,
            'interpreter STEPLIB does not consistently select reviewed MR10_LOAD')
    require('DSN=HERC02.BCPL.MR10KIT.TESTS(SCALVEC)' in body,
            'scalar-vector test source not selected')
    require('DISP=SHR' in body and all(len(line) <= 80 for line in body.splitlines()),
            'invalid JCL card width')
    return body, git_blob


def validate_report(text: str, *, job: int, gold: tuple[str,...]) -> dict:
    start = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP373\s+' + NAME + r'\s+STARTED\b', text, re.M)
    end = re.findall(r'^\s*\S+\s+JOB\s+(\d+)\s+\$HASP395\s+' + NAME + r'\s+ENDED\b', text, re.M)
    require(start == [str(job)] and end == [str(job)], 'missing or duplicated JES START/END identity')
    rows = STEP_RC.findall(text)
    require([(name, program) for number, name, program, rc in rows] == list(zip(STEPS, PROGRAMS))
            and all(int(number) == job and rc == '0000' for number, _, _, rc in rows),
            'missing, bypassed, reordered or failed IEBGENER/ICINT19 step')
    for step in STEPS:
        msg = re.findall(r'^IEF142I\s+TA0ICEX\s+' + step +
                         r'\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE 0000\s*$', text, re.M)
        require(len(msg) == 1, 'missing or duplicated successful IEF142I: ' + step)
    require(not re.search(r'\b(?:IEF450I|IEF472I|IEA995I)\b', text), 'potential MVS ABEND')
    seen = tuple('RP: ' + m.group(1) + ' ' + ' '.join(m.group(2).split())
                 for m in RP.finditer(text))
    require(seen == gold, 'executed scalar-vector RP records differ from golden output')
    codes = [int(x) for x in CODE.findall(text)]
    require(len(codes) >= 3 and all(v == 0 for v in codes),
            'missing or unsuccessful interpreted CODE= records')
    return {'program_steps': list(STEPS), 'step_rc': [0]*len(STEPS),
            'interpreted_codes': codes, 'rp_records': list(seen),
            'verification': 'DEVELOPMENT MR10_LOAD ICINT19 EXECUTED; NOT LOAD BYTE OR TAPE PROOF'}


def save_window(core, config: dict, cursor: Path, output: Path) -> None:
    printer = ROOT / str(config['runtime']['printer'])
    cmd = [sys.executable, str(ROOT/'tools/mvs/printer-window.py'), 'read',
           '--printer', str(printer), '--cursor-file', str(cursor)]
    fd = os.open(output, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as file:
        proc = subprocess.run(cmd, cwd=ROOT, stdout=file, stderr=subprocess.PIPE, check=False, timeout=120)
    require(proc.returncode == 0, 'printer-window read failed; do not retry')


def run(core, config: dict, *, evidence: Path, review_dir: Path, output: Path) -> dict:
    external(output, new=True)
    original, reviewed = validate_directory(evidence, review_dir)
    spec = config.get('datasets', {}).get('MR10_LOAD')
    require(type(spec) is dict and core.full_dsn(config, spec) == original['dsn']
            and spec.get('dsorg') == 'PO' and spec.get('recfm') == 'U'
            and spec.get('lrecl') == 0 and spec.get('blksize') == 6144,
            'active MR10_LOAD source differs from IEHLIST evidence')
    source = read_plain(JCL)
    body, origin_blob = canonical_steps(source, hlq=config['mvs']['hlq'], load_dsn=original['dsn'])
    gold = tuple(read_plain(GOLD, 1024).decode('ascii').splitlines())
    require(gold == GOLDEN, 'scalar-vector golden output changed')
    deck = '\n'.join(core.authenticated_job_card(config, NAME,
                             'TA0 ICINT19 EXEC', False)) + '\n' + body
    os.mkdir(output, 0o700)
    private(output / 'job-body.jcl', body.encode('ascii'))
    cursor = output / 'cursor.json'
    job = None
    try:
        job, summary = core.submit_and_wait(config, deck, max_rc=0, cursor_file=cursor)
        private(output / 'job-summary.txt', summary.encode('utf-8'))
        report = core.job_report(job, cursor_file=cursor)
        private(output / 'job-report.txt', report.encode('utf-8'))
        result = validate_report(report, job=job, gold=GOLDEN)
        save_window(core, config, cursor, output/'printer-window.raw')
        hashes = {p:sha(read_plain(output/p, MAX_REPORT*2)) for p in
                  ('cursor.json','job-body.jcl','job-summary.txt','job-report.txt','printer-window.raw')}
        receipt = {'phase':'TA.0 MR10_LOAD EXECUTABLE PILOT — NOT TAPE OR RELEASE ACCEPTANCE',
                   'job':job,'jobname':NAME,'source_dsn':original['dsn'],
                   'source_directory_job':original['job'],
                   'review_receipt_sha256':sha(read_plain(review_dir/'directory-review.json',1024*1024)),
                   'source_jcl_git_blob': origin_blob,
                   'source_jcl_sha256':sha(source),'golden_sha256':sha(read_plain(GOLD,1024)),
                   'sha256':hashes,'result':result,
                   'qualifications':[
                     'ICINT19 ran from current development MR10_LOAD via STEPLIB, not a restored image.',
                     'No independent RECFM=U byte equality or load-library unload/restore was tested.',
                     'Only scalar-vector case 01 was exercised; not full 12-case MRREGRES.',
                     'No MVS source-to-Git ancestry or redistribution rights proven.']}
        private(output/'receipt.json', (json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode('utf-8'))
        return receipt
    except Exception as exc:
        private(output/'failure.txt', f'JOB={job if job is not None else "unknown"}; type={type(exc).__name__}\n'.encode())
        raise


def main(argv: list[str] | None = None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iehlist-evidence',type=Path,required=True)
    ap.add_argument('--review-dir',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args(argv)
    try:
        os.umask(0o077)
        core=import_file(CORE,'ta0_exec_core')
        receipt=run(core,core.load_config(),evidence=args.iehlist_evidence,
                    review_dir=args.review_dir,output=args.output_dir)
    except (ExecEvidenceError,OSError,UnicodeError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        print(f'TA.0 ICINT19 EXEC PILOT REFUSED/FAILED: {type(exc).__name__}',file=sys.stderr)
        print('Private evidence retained; no automatic resubmission.',file=sys.stderr)
        return 1
    print(f"TA.0 MR10_LOAD EXECUTABLE: JOB {receipt['job']} {NAME}: "
          '8 steps RC=0000, 3 ICINT19 invocations, scalar-vector RP matched')
    print('Development load executable-use only; no RECFM=U byte/tape acceptance.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
