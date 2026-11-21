#!/usr/bin/env python3
"""TA.2: one-shot, owner-gated IEBCOPY staging of historical BT0021 only.

No write without separate committed owner approval, exact original MVS evidence,
fresh read-only MVS LISTDS/IEHLIST, operator TTY and typed confirmation.
The permanent attempt marker is written before JES submission, never retried.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / 'workarea'
PREFLIGHT = WORK / 'ta2-rc2-bt0021-preflight/20261121T051500Z-24489'
OPERATIONS = WORK / 'ta2-rc2-bt0021-stage-operations'
MARKER = OPERATIONS / 'BT0021-TSO002-one-shot-attempt.json'
APPROVAL = HERE / 'rc2-bt0021-stage-approval.json'  # Intentionally absent pending approval.
MANIFEST = ROOT / 'packaging/distribution/manifest/releases/BCPL-0.1.0-rc2.yaml'
TARGET = 'HERC02.BCPL.TA2STG.BT0021'
VOLUME = 'TSO002'
JOBNAME = 'TA2C21ST'
MAX_FILE = 16 * 1024 * 1024
ACTIVE_FOLDER = None
HASH_ROW = re.compile(r'([0-9a-f]{64})  ([a-z0-9_.-]+)\Z')


class Refusal(ValueError):
    pass


def need(ok: bool, message: str) -> None:
    if not ok:
        raise Refusal(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_committed(path: Path) -> bytes:
    """Source-controlled stateful approval. No host files are modified."""
    need(path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(ROOT.resolve()),
         'required committed approval/manifest file missing')
    branch = subprocess.run(['git', '-C', str(ROOT), 'symbolic-ref', '--short', 'HEAD'],
                            capture_output=True, text=True, timeout=20, check=False)
    need(branch.returncode == 0 and branch.stdout.strip() == 'main',
         'stateful operation requires local main')
    diff = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain',
                           '--untracked-files=no'], capture_output=True,
                          text=True, timeout=20, check=False)
    need(diff.returncode == 0 and not diff.stdout.strip(),
         'tracked working tree not clean')
    relative = path.relative_to(ROOT).as_posix()
    recorded = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + relative],
                              capture_output=True, timeout=20, check=False)
    need(recorded.returncode == 0 and recorded.stdout == path.read_bytes(),
         'owner approval/manifest differs from HEAD')
    return recorded.stdout


def sealed_preflight(preflight, core, target) -> dict:
    """Use JOB 9331/9332 exactly once; validate saved MVS material, not a summary."""
    need(PREFLIGHT.is_dir() and not PREFLIGHT.is_symlink() and
         PREFLIGHT.resolve().is_relative_to(WORK.resolve()) and
         PREFLIGHT.name == '20261121T051500Z-24489',
         'exact accepted JOB 9331/9332 evidence unavailable')
    ledger = PREFLIGHT / 'SHA256SUMS'
    need(ledger.is_file() and not ledger.is_symlink(), 'preflight seal missing')
    files = {}
    for line in ledger.read_text(encoding='ascii').splitlines():
        m = HASH_ROW.fullmatch(line)
        need(m is not None and m[2] not in files, 'invalid preflight seal row')
        path = PREFLIGHT / m[2]
        need(path.is_file() and not path.is_symlink() and
             path.stat().st_size <= MAX_FILE,
             'preflight original file unavailable or unsafe: ' + m[2])
        contents = path.read_bytes()
        need(digest(contents) == m[1], 'preflight evidence changed: ' + m[2])
        files[m[2]] = contents
    need({x.name for x in PREFLIGHT.iterdir()} == set(files) | {'SHA256SUMS'},
         'preflight evidence file set changed')
    need({'result.json', 'catalog-report.txt', 'vtoc-report.txt',
          'catalog-summary.txt', 'vtoc-summary.txt'} <= set(files),
         'preflight original MVS reports incomplete')
    result = json.loads(files['result.json'])
    need(result.get('status') == 'READ_ONLY_MVS_TARGET_ABSENT_AND_VTOC_OBSERVED' and
         result.get('candidate') == 'BCPL-0.1.0-rc2' and
         result.get('volser') == 'BC0002' and
         result.get('target') == TARGET and
         result.get('volume') == VOLUME and
         result.get('source') == preflight.SOURCE and
         result.get('mvs_source_job') == 9330 and
         result.get('source_members') == 15 and
         result.get('source_records') == 6577 and
         result.get('stage_authorized') is False and
         result.get('mvs_jobs') == {'catalog': 9331, 'vtoc': 9332},
         'preflight receipt differs from actual owner-reported MVS result')
    cat = files['catalog-report.txt'].decode('utf-8')
    vtoc = files['vtoc-report.txt'].decode('utf-8')
    preflight.catalog_absent(core, cat)
    target.vtoc_observation(vtoc, VOLUME, [TARGET])
    for label, job in (('catalog', 9331), ('vtoc', 9332)):
        summary = files[label + '-summary.txt'].decode('utf-8')
        need(re.search(r'(?m)^JOB\s+' + str(job) + r'\s+', summary) is not None,
             'original MVS job summary mismatch: ' + label)
    return {'receipt': result, 'seal_sha256': digest(ledger.read_bytes()),
            'vtoc_report': vtoc}


def check_approval(approval: dict, preflight_data: dict, material_sha: str) -> None:
    required = {'schema_version', 'status', 'candidate', 'volser', 'volume',
                'source', 'target', 'historical_members', 'source_records',
                'source_byte_policy', 'preflight_evidence', 'preflight_jobs',
                'retry', 'production_tape_authorized'}
    need(isinstance(approval, dict) and set(approval) == required and
         approval['schema_version'] == 1 and
         approval['status'] == 'OWNER_APPROVED_ONE_SHOT_BT0021_STAGING' and
         approval['candidate'] == 'BCPL-0.1.0-rc2' and
         approval['volser'] == 'BC0002' and
         approval['volume'] == VOLUME and
         approval['target'] == TARGET and
         approval['source'] == 'HERC02.BCPL.CAMBRIDG.SOURCE' and
         approval['historical_members'] == 15 and
         approval['source_records'] == 6577 and
         approval['source_byte_policy'] ==
             'preserve-verified-hercules-translated-FB80-as-archival-source' and
         approval['preflight_evidence'] == PREFLIGHT.relative_to(ROOT).as_posix() and
         approval['preflight_jobs'] == {'catalog': 9331, 'vtoc': 9332} and
         preflight_data['receipt']['stage_deck_sha256'] == material_sha and
         approval['retry'] is False and
         approval['production_tape_authorized'] is False,
         'separate owner approval for exact bytes/one-shot stage absent or changed')


def material_body(preflight, stage, readiness, qsam, reconciler):
    plan = preflight.exact_release(stage, readiness, qsam, reconciler)
    manifest, dspal = readiness.source_manifest()
    draft = stage.render(manifest, dspal, volume=VOLUME)
    need(digest(draft.encode('ascii')) == plan['stage_deck_sha256'],
         'stage text differs from accepted MVS source plan')
    lines = draft.splitlines()
    need(len(lines) >= 19 and lines[:3] == [
         '//* TA.2 RC2 DRAFT ONLY: NOT AUTHORIZED FOR MVS SUBMISSION.',
         '//* BT0001-BT0020 ARE ALREADY ACCEPTED; DO NOT RESTAGE.',
         '//* ONE NEW HISTORICAL PDS; FAIL CLOSED IF IT EXISTS.'],
         'stage draft header differs; cannot authorize guessed JCL')
    body = '\n'.join(['//* OWNER-GATED RC2 HISTORICAL BT0021 STAGING',
                      '//* DO NOT RESTAGE BT0001-BT0020', *lines[3:]]) + '\n'
    need(body.count(' EXEC PGM=IEBCOPY') == 1 and
         body.count(' SELECT MEMBER=') == 15 and
         body.count('DISP=(NEW,CATLG,DELETE)') == 1 and
         'HERC02.BCPL.TA2STG.BT0021' in body and
         all(len(line) <= 80 for line in body.splitlines()),
         'JCL body is not exactly one 15-member NEW IEBCOPY')
    return plan, body, digest(draft.encode('ascii'))


def new_run() -> Path:
    need(WORK.is_dir() and not WORK.is_symlink() and
         WORK.resolve().is_relative_to(ROOT.resolve()) and
         not OPERATIONS.is_symlink(), 'unsafe workarea')
    OPERATIONS.mkdir(mode=0o700, exist_ok=True)
    need(not MARKER.exists() and not MARKER.is_symlink() and
         not any(OPERATIONS.iterdir()), 'BT0021 already attempted; no retry')
    run = OPERATIONS / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                        '-' + str(os.getpid()))
    run.mkdir(mode=0o700, exist_ok=False)
    return run


def save(path: Path, data: bytes) -> None:
    with os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY |
                          getattr(os, 'O_NOFOLLOW', 0), 0o600), 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def seal(folder: Path) -> None:
    files = sorted(f for f in folder.iterdir() if f.is_file() and f.name != 'SHA256SUMS')
    save(folder / 'SHA256SUMS', ''.join(digest(f.read_bytes()) + '  ' + f.name + '\n'
                                    for f in files).encode('ascii'))


def validate_job(job: int, summary: str, report: str) -> dict:
    need(type(job) is int and 1 <= job <= 9999 and
         re.search(r'(?m)^JOB\s+' + str(job) + r'\s+' + JOBNAME + r'\s*$',
                   summary) is not None and
         'JOB RESULT: SUCCESS' in summary and 'HIGHEST RC: 0000' in summary,
         'MVS staging job identity/highest RC not PASS')
    steps = re.findall(r'(?m)^([A-Z0-9]{1,8})\s+IEBCOPY\s+RC=(\d{4})\s*$', summary)
    need(steps == [('S0021', '0000')], 'not exactly one successful IEBCOPY step')
    need(len(re.findall(r'(?m)^IEF142I\s+' + JOBNAME +
                        r'\s+S0021\s+-\s+STEP WAS EXECUTED\s+-\s+COND CODE 0000\s*$',
                        report)) == 1 and
         not re.search(r'\b(?:IEF450I|IEF472I|IEA995I|ABEND)\b', report),
         'MVS IEBCOPY step is missing/duplicate or ABEND observed')
    return {'status': 'BT0021_IEBCOPY_MVS_RC0000_DIRECTORY_VERIFICATION_PENDING',
            'mvs_job': job, 'step': 'S0021', 'selected_members': 15,
            'target': TARGET, 'volume': VOLUME}


def run() -> int:
    global ACTIVE_FOLDER
    ACTIVE_FOLDER = None
    need(sys.stdin.isatty(), 'stateful IEBCOPY requires operator TTY')
    need(not MARKER.exists() and not MARKER.is_symlink(),
         'BT0021 one-shot attempt marker already exists; no retry')
    raw_approval = git_committed(APPROVAL)   # Unavailable until owner separately approves.
    git_committed(MANIFEST)
    preflight = load_module('rc2_bt21_pf', HERE / 'rc2-bt0021-preflight.py')
    stage = load_module('rc2_bt21_draft', HERE / 'rc2-stage-draft.py')
    ready = load_module('rc2_bt21_ready', HERE / 'rc2-cambsource-readiness.py')
    qsam = load_module('rc2_bt21_qsam', HERE / 'rc2-qsam-fidelity.py')
    reconcile = load_module('rc2_bt21_reconcile', HERE / 'rc2-qsam-reconcile-transport.py')
    core = load_module('rc2_bt21_core', ROOT / 'tools/datasets/dspal-core.py')
    target = load_module('rc2_bt21_vtoc', ROOT / 'packaging/distribution/create-tape/scripts/ta2-target-preflight')
    review = load_module('rc2_bt21_review', ROOT / 'packaging/distribution/create-tape/scripts/ta2-target-review')
    plan, body, sha = material_body(preflight, stage, ready, qsam, reconcile)
    saved = sealed_preflight(preflight, core, target)
    need(plan['stage_deck_sha256'] == saved['receipt']['stage_deck_sha256'],
         'original preflight/stage JCL hash differs')
    check_approval(json.loads(raw_approval), saved, sha)
    config = core.load_config()
    need(config['mvs']['hlq'] == 'HERC02', 'MVS HLQ changed')
    core.require_reader_ready(config)
    folder = new_run()
    ACTIVE_FOLDER = folder
    # Fresh MVS checks are necessary because catalog/VTOC may have changed.
    fresh = folder / 'fresh-preflight'
    fresh.mkdir(mode=0o700)
    result = preflight.live_inquiry(core, target, config, fresh, plan)
    preflight.save(fresh, 'result.json', (json.dumps(result, sort_keys=True, indent=2)+'\n').encode())
    preflight.seal(fresh)
    analysis = review.inspect_vtoc((fresh / 'vtoc-report.txt').read_text(), VOLUME, [TARGET])
    tracks = analysis['iehlist_reported_free_total_tracks']
    need(type(tracks) is int and tracks >= 50 and
         analysis['staging_names_in_formatted_vtoc'] == 0,
         'MVS TSO002 free-space/collision evidence does not support one new PDS')
    print(f'TA.2 BT0021: fresh MVS LISTDS/IEHLIST PASS; TSO002 reported free tracks {tracks}.')
    need(input('Submit the owner-approved single BT0021 IEBCOPY job? [y/N]: ').strip().upper() == 'Y',
         'operator did not confirm one-shot staging')
    need(not MARKER.exists() and not MARKER.is_symlink(), 'attempt marker appeared; refuse')
    deck = '\n'.join(core.authenticated_job_card(config, JOBNAME, 'TA2 RC2 BT0021',
                                                   redact_password=False)) + '\n' + body
    need(deck.isascii() and all(len(x) <= 80 for x in deck.splitlines()),
         'authenticated IEBCOPY deck unsafe')
    intent = {'state': 'SUBMISSION_INTENT_NO_RETRY', 'candidate': 'BCPL-0.1.0-rc2',
              'volume': VOLUME, 'target': TARGET, 'jobname': JOBNAME,
              'source_mvs_job': 9330, 'preflight_jobs': {'catalog':9331, 'vtoc':9332},
              'fresh_jobs': result['mvs_jobs'], 'attempt': folder.relative_to(ROOT).as_posix(),
              'approved_stage_jcl_sha256': sha, 'owner_approval_sha256': digest(raw_approval),
              'original_preflight_seal_sha256': saved['seal_sha256']}
    save(MARKER, (json.dumps(intent, sort_keys=True, indent=2) + '\n').encode())
    old_tmp, old_env = tempfile.tempdir, os.environ.get('TMPDIR')
    tempfile.tempdir = str(folder)
    os.environ['TMPDIR'] = str(folder)
    try:
        cursor = folder / 'stage-cursor.json'
        job, summary = core.submit_and_wait(config, deck, max_rc=0, cursor_file=cursor)
        save(folder / 'stage-summary.txt', summary.encode('utf-8'))
        report = core.job_report(job, cursor_file=cursor)
        save(folder / 'stage-report.txt', report.encode('utf-8'))
        outcome = validate_job(job, summary, report)
        save(folder / 'stage-result.json', (json.dumps(outcome, indent=2)+'\n').encode())
        seal(folder)
        print(f'TA.2 BT0021 IEBCOPY JOB {job}: RC=0000; directory/DCB verification pending.')
        print('Private MVS evidence: ' + folder.relative_to(ROOT).as_posix())
        return 0
    finally:
        tempfile.tempdir = old_tmp
        if old_env is None: os.environ.pop('TMPDIR', None)
        else: os.environ['TMPDIR'] = old_env


def load_module(name: str, path: Path):
    import importlib.machinery
    import importlib.util
    need(path.is_file() and not path.is_symlink(), 'repository dependency missing: ' + path.name)
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    need(spec is not None and spec.loader is not None, 'cannot import dependency')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='requires separate committed owner approval; one MVS IEBCOPY after fresh read-only checks')
    args = parser.parse_args(argv)
    if not args.run:
        print('TA.2 BT0021 stage runner ready; no approved write until separate committed owner decision.')
        return 0
    try:
        return run()
    except (Refusal, ValueError, TypeError, OSError, KeyError, UnicodeError, subprocess.SubprocessError) as exc:
        if ACTIVE_FOLDER is not None and ACTIVE_FOLDER.is_dir():
            try:
                fail = ACTIVE_FOLDER / 'failure.json'
                save(fail, (json.dumps({'status':'HALTED_NO_RETRY', 'reason':str(exc)})+'\n').encode())
                if not (ACTIVE_FOLDER / 'SHA256SUMS').exists(): seal(ACTIVE_FOLDER)
                print('Private MVS evidence: ' + ACTIVE_FOLDER.relative_to(ROOT).as_posix(), file=sys.stderr)
            except (OSError, Refusal, FileExistsError):
                pass
        print('TA.2 BT0021 STAGING REFUSED: ' + str(exc), file=sys.stderr)
        print('No automatic retry; review any existing workarea MVS attempt before proceeding.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
