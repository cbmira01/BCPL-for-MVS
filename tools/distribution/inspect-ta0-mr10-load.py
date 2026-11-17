#!/usr/bin/env python3
"""TA.0: one read-only IEHLIST FORMAT pilot of MR10_LOAD(ICINT19).

Checks existing, SHA-pinned LISTDS/LISTDS MEMBERS evidence before submitting
one JES job.  Stores private reports; does not decode or compare RECFM=U bytes,
run ICINT19, perform IEBCOPY, write tape, or assert release acceptance.
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

import yaml

ROOT = Path(__file__).resolve().parents[2]
# Centralized, symlink-safe ignored-workarea evidence policy.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path
CORE = ROOT / 'tools/datasets/dspal-core.py'
INVENTORY = ROOT / 'packaging/distribution/manifest/ta0-inventory.yaml'
DSPAL = ROOT / 'config/dspal.yaml'
MEMBER = 'ICINT19'
KEY = 'MR10_LOAD'
JOBNAME = 'TA0LDIR'
DD = {'dsorg': 'PO', 'recfm': 'U', 'lrecl': 0, 'blksize': 6144}
CHECKS = ('MR10_LOAD.txt', 'MR10_LOAD.stat-raw.txt')
QUAL = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}\Z')
UNIT = re.compile(r'[A-Z0-9@$#]{1,8}\Z')
VOL = re.compile(r'[A-Z0-9]{1,6}\Z')
SHA = re.compile(r'[0-9a-f]{64}\Z')


class LoadError(ValueError):
    pass


def need(good: bool, why: str) -> None:
    if not good:
        raise LoadError(why)


def load_core():
    spec = importlib.util.spec_from_file_location('ta0_load_core', CORE)
    need(spec is not None and spec.loader is not None, 'missing dspal core')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def external_existing(path: Path) -> None:
    try:
        guard_evidence_path(path, new=False, root=ROOT)
    except ValueError as exc:
        raise LoadError('evidence must be an existing private workarea/ directory') from exc


def external_new(path: Path) -> None:
    try:
        guard_evidence_path(path, new=True, root=ROOT)
    except ValueError as exc:
        raise LoadError('output must be a new private directory under workarea/') from exc

def read_file(parent: Path, name: str, max_bytes: int = 1024 * 1024) -> bytes:
    p = parent / name
    need(p.is_file() and not p.is_symlink() and p.stat().st_size <= max_bytes,
         'missing, linked or oversized evidence file: ' + name)
    return p.read_bytes()


def pinned_inventory(root: Path) -> dict[str, bytes]:
    external_existing(root)
    hashes = read_file(root, 'SHA256SUMS').decode('ascii')
    expected: dict[str, str] = {}
    for line in hashes.splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9._-]+)', line)
        need(match is not None, 'malformed SHA256SUMS')
        digest, name = match.groups()
        need(name not in expected, 'duplicate SHA256SUMS record')
        expected[name] = digest
    results = {}
    for name in CHECKS:
        need(name in expected, 'missing pinned file: ' + name)
        data = read_file(root, name, 8 * 1024 * 1024)
        need(hashlib.sha256(data).hexdigest() == expected[name],
             'checksum mismatch: ' + name)
        results[name] = data
    return results


def canonical_source(config: dict, *, manifest: dict, dspal: dict, core) -> str:
    rows = [r for r in manifest.get('datasets', [])
            if type(r) is dict and r.get('dspal_key') == KEY]
    need(len(rows) == 1, 'canonical manifest missing unique MR10_LOAD')
    row = rows[0]
    need(row.get('kind') == 'pds_unload' and
         row.get('transfer') == 'iebcopy_unload' and
         row.get('target_dcb') == DD and row.get('members') == [MEMBER],
         'MR10_LOAD does not match approved TA.0 selection')
    a = config.get('datasets', {}).get(KEY)
    b = dspal.get('datasets', {}).get(KEY)
    need(type(a) is dict and type(b) is dict and
         a.get('type') == b.get('type') == 'loadlib' and
         all(a.get(k) == b.get(k) == value for k, value in DD.items()) and
         a.get('dsn') == b.get('dsn'),
         'active/source MR10_LOAD DCB or dataset mapping differs')
    dsn = core.full_dsn(config, a)
    need(len(dsn) <= 44 and all(QUAL.fullmatch(q) for q in dsn.split('.')),
         'invalid MR10_LOAD dataset name')
    return dsn


def saved_dcb(core, files: dict[str, bytes], dsn: str) -> str:
    try:
        listing = files['MR10_LOAD.txt'].decode('utf-8')
        report = files['MR10_LOAD.stat-raw.txt'].decode('utf-8')
    except UnicodeError as exc:
        raise LoadError('saved LISTDS evidence is not UTF-8') from exc
    need(re.search(r'^' + re.escape(dsn) + r':\s*$', listing, re.M) is not None and
         re.search(r'^\s*' + MEMBER + r'\s*$', listing, re.M) is not None,
         'saved MVS member inventory does not select ICINT19')
    block = core.extract_listds_block(report, dsn)
    need(bool(block), 'saved LISTDS LABEL response missing dataset identity')
    attrs = core.parse_listds(block)
    need(all(attrs.get(k) == str(v) for k, v in DD.items()),
         'saved LISTDS LABEL DCB not PO/U/0/6144')
    volser = attrs.get('volume', '')
    need(VOL.fullmatch(volser) is not None, 'no trusted volume serial in saved LISTDS')
    return volser


def make_body(dsn: str, volser: str, unit: str) -> str:
    need(VOL.fullmatch(volser) is not None and UNIT.fullmatch(unit) is not None,
         'unsafe volume or device unit')
    need(len(dsn) <= 44 and all(QUAL.fullmatch(q) for q in dsn.split('.')),
         'unsafe selected dataset name')
    # IEHLIST requires a DD associated with the DASD volume.  The existing
    # load PDS is allocated DISP=SHR; no new dataset or output DD is created.
    cards = [
        '//* TA.0 DIRECTORY-ONLY PO/U LOAD INSPECTION; NOT BYTE PROOF.',
        '//DIRLIST  EXEC PGM=IEHLIST',
        '//SYSPRINT DD SYSOUT=*',
        f'//VOLDD    DD DSN={dsn},',
        f'//            DISP=SHR,UNIT={unit},VOL=SER={volser}',
        '//SYSIN    DD *',
        f' LISTPDS DSNAME={dsn},VOL={unit}={volser},FORMAT',
        '/*',
    ]
    need(all(len(c) <= 80 for c in cards), 'IEHLIST JCL exceeds FB80 width')
    return '\n'.join(cards) + '\n'


def private_file(path: Path, content: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(content)


def save_window(core, config: dict, cursor: Path, dest: Path) -> None:
    reader = ROOT / 'tools/mvs/printer-window.py'
    printer = ROOT / str(config['runtime']['printer'])
    with dest.open('xb') as out:
        os.fchmod(out.fileno(), 0o600)
        process = subprocess.run([sys.executable, str(reader), 'read',
                                  '--printer', str(printer), '--cursor-file', str(cursor)],
                                 cwd=ROOT, stdout=out, stderr=subprocess.PIPE,
                                 check=False, timeout=120)
    need(process.returncode == 0, 'printer-window cursor read failed')


def run(core, config: dict, *, evidence: Path, output: Path) -> dict:
    external_new(output)
    sources = pinned_inventory(evidence)
    manifest = yaml.safe_load(INVENTORY.read_text(encoding='utf-8'))
    public = yaml.safe_load(DSPAL.read_text(encoding='utf-8'))
    dsn = canonical_source(config, manifest=manifest, dspal=public, core=core)
    volume = saved_dcb(core, sources, dsn)
    unit = str(config.get('mvs', {}).get('default_unit', '')).upper()
    body = make_body(dsn, volume, unit)
    # The JOB card is never persisted: it can contain a batch password.
    deck = '\n'.join(core.authenticated_job_card(config, JOBNAME,
                    'TA0 LOAD DIRECTORY', False)) + '\n' + body
    os.mkdir(output, 0o700)
    private_file(output / 'job-body.jcl', body.encode('ascii'))
    cursor = output / 'cursor.json'
    job = None
    try:
        job, summary = core.submit_and_wait(config, deck, max_rc=0,
                                            cursor_file=cursor)
        private_file(output / 'job-summary.txt', summary.encode('utf-8'))
        report = core.job_report(job, cursor_file=cursor)
        # Directory syntax/semantics are a separate MVS-driven review gate.
        # Only assert trusted JES identity, utility step and successful return.
        need(re.search(r'\bJOB\s+' + str(job) + r'\s+\$HASP373\s+' + JOBNAME, report),
             'JES START identity missing')
        need(re.search(r'\bJOB\s+' + str(job) + r'\s+\$HASP395\s+' + JOBNAME, report),
             'JES END identity missing')
        need(re.search(r'\b' + JOBNAME + r'\s+DIRLIST\s+IEHLIST\s+RC=\s*0000', report),
             'IEHLIST RC=0000 not confirmed')
        private_file(output / 'job-report.txt', report.encode('utf-8'))
        save_window(core, config, cursor, output / 'printer-window.raw')
        pins = {}
        for name in ('cursor.json','job-body.jcl','job-summary.txt','job-report.txt',
                     'printer-window.raw'):
            pins[name] = hashlib.sha256(read_file(output, name, 64*1024*1024)).hexdigest()
        receipt = {
            'phase': 'TA.0 LOAD DIRECTORY PILOT — NOT LOAD BYTE OR RELEASE ACCEPTANCE',
            'job': job, 'jobname': JOBNAME, 'dataset_key': KEY,
            'dsn': dsn, 'member': MEMBER, 'source_volume': volume,
            'source_dcb': DD, 'directory_utility': 'IEHLIST LISTPDS FORMAT',
            'saved_listds_sha256': {n:hashlib.sha256(b).hexdigest() for n,b in sources.items()},
            'sha256': pins,
            'qualifications': [
                'A zero RC does not prove ICINT19 was listed; inspect saved LISTPDS output.',
                'Directory attributes are not an independent RECFM=U load-module byte comparison.',
                'No executable-use, unload/restore, source revision or tape proof established.'
            ],
        }
        private_file(output / 'receipt.json', (json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode())
    except Exception as exc:
        private_file(output / 'failure.txt',
                     f'JOB={job if job is not None else "unknown"}; phase={type(exc).__name__}\n'.encode())
        raise
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        core = load_core()
        config = core.load_config()
        receipt = run(core, config, evidence=args.evidence_dir,
                      output=args.output_dir)
    except (LoadError, OSError, ValueError, RuntimeError, yaml.YAMLError,
            subprocess.TimeoutExpired) as exc:
        # Avoid printing private reports or credential-bearing exception text.
        print(f'TA.0 MR10_LOAD DIRECTORY REFUSED/FAILED: {type(exc).__name__}',file=sys.stderr)
        print('No automatic JES retry; private evidence is retained if submitted.',file=sys.stderr)
        return 1
    print(f"TA.0 MR10_LOAD DIRECTORY: JOB {receipt['job']} {receipt['jobname']} IEHLIST RC=0000")
    print(f"Private evidence: {args.output_dir}")
    print('Listing requires inspection; no load bytes, executable or tape verified.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
