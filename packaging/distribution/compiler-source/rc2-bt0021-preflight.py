#!/usr/bin/env python3
"""TA.2 BT0021: read-only, MVS-evidenced preflight for historical source PDS.

One catalog LISTDS and one IEHLIST/VTOC inquiry; no PDS, tape or source write.
Replays original JOB 9330 evidence and reconciled source checksums. Captures
Hercules's codepage display when available; never changes its configuration.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCRIPTS = ROOT / 'packaging/distribution/create-tape/scripts'
WORK = ROOT / 'workarea'
OUT = WORK / 'ta2-rc2-bt0021-preflight'
RECONCILED = WORK / 'ta2-rc2-cambsource-qsam-transport-reconciliation/receipt.json'
ORIGINAL = WORK / 'ta2-rc2-cambsource-qsam-fidelity'
TARGET = 'HERC02.BCPL.TA2STG.BT0021'
SOURCE = 'HERC02.BCPL.CAMBRIDG.SOURCE'
VOLUME = 'TSO002'
JOB = 9330
MAX_EVIDENCE = 4_000_000


class Refusal(ValueError):
    pass


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def load(name: str, path: Path):
    need(path.is_file() and not path.is_symlink(), 'missing repository module: ' + path.name)
    if path.suffix == '.py':
        spec = importlib.util.spec_from_file_location(name, path)
    else:
        loader = importlib.machinery.SourceFileLoader(name, str(path))
        spec = importlib.util.spec_from_loader(name, loader)
    need(spec is not None and spec.loader is not None, 'unavailable repository module')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def read_original(path: Path, root: Path, maximum: int = MAX_EVIDENCE) -> bytes:
    need(root.is_dir() and not root.is_symlink() and
         root.resolve().is_relative_to(WORK.resolve()),
         'unsafe saved-MVS-evidence root')
    need(path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(root.resolve()) and
         path.stat().st_size < maximum,
         'missing/unsafe original MVS evidence: ' + path.name)
    return path.read_bytes()


def check_reconciliation(saved: dict, replay: dict) -> None:
    need(saved.get('status') == 'reader-profile-reconciled' and
         saved.get('candidate') == 'BCPL-0.1.0-rc2' and
         saved.get('mvs_job') == JOB and
         saved.get('population_jobs') == [9325, 9326] and
         saved.get('source_records') == 6577 and
         saved.get('original_cp037_pass') == 7 and
         saved.get('reader_profile_pass') == 15 and
         saved.get('observed_reader_overrides_hex') ==
             {'|': '6A', '[': 'AD', ']': 'BD'} and
         len(saved.get('members', [])) == 15 and
         all(x.get('reader_profile_match') is True for x in saved['members']),
         'saved JOB 9330 transport receipt does not meet accepted bounds')
    need(saved == replay,
         'saved transport reconciliation differs from independently replayed JES evidence')


def exact_release(stage, readiness, qsam, reconciler) -> dict:
    manifest, dspal = readiness.source_manifest()
    original_names = reconciler.MEMBER_NAMES
    need(tuple(qsam.NAMES) == tuple(original_names),
         'MVS QSAM and historical reconciliation member lists disagree')
    need(manifest['release']['candidate_id'] == 'BCPL-0.1.0-rc2' and
         manifest['volume']['volser'] == 'BC0002' and
         manifest['release']['native_compiler'] == 'absent' and
         tuple(manifest['datasets'][20]['members']) == original_names and
         SOURCE == readiness.EXPECTED_DSN,
         'release identity/source-only member selection changed')
    deck = stage.render(manifest, dspal, volume=VOLUME)
    need(deck.count(' EXEC PGM=IEBCOPY') == 1 and
         deck.count(' SELECT MEMBER=') == 15 and
         TARGET in deck and 'DISP=(NEW,CATLG,DELETE)' in deck and
         all('BT00' not in row or 'BT0021' in row for row in deck.splitlines()
             if row.startswith('//OUTPDS')),
         'BT0021 selective IEBCOPY staging contract changed')
    # Replay original saved MVS JOB 9330 evidence instead of resubmitting it.
    stored = json.loads(read_original(RECONCILED, RECONCILED.parent, 160_000))
    original = json.loads(read_original(ORIGINAL / 'receipt.json', ORIGINAL, 160_000))
    report = read_original(ORIGINAL / 'mvs-job-report.txt', ORIGINAL).decode('utf-8')
    summary = read_original(ORIGINAL / 'job-summary.txt', ORIGINAL, 160_000).decode('utf-8')
    expected = qsam.expected_records(readiness, manifest, dspal)
    qsam.summary_steps(summary)
    observed = qsam.parse_report(report, expected)
    source_map = dspal['datasets']['CAMB_SOURCE']['members']
    sources = {name: readiness.check_frozen_source(source_map[name])
               for name in original_names}
    replay = reconciler.reconcile(original, sources, observed, summary)
    check_reconciliation(stored, replay)
    return {'candidate': 'BCPL-0.1.0-rc2', 'volser': 'BC0002',
            'source': SOURCE, 'target': TARGET, 'volume': VOLUME,
            'stage_deck_sha256': hashlib.sha256(deck.encode('ascii')).hexdigest(),
            'reconciliation_sha256': hashlib.sha256(
                read_original(RECONCILED, RECONCILED.parent, 160_000)).hexdigest(),
            'mvs_source_job': JOB, 'source_members': len(original_names),
            'source_records': 6577,
            'source_encoding': 'observed Hercules input byte profile, not CP037',
            'rights': 'unresolved',
            'stage_authorized': False}


def catalog_absent(core, report: str) -> None:
    need(core.dataset_missing(report, TARGET),
         'MVS LISTDS did not positively confirm BT0021 catalog absence')
    block = core.extract_listds_block(report, TARGET)
    need(not (block and core.parse_listds(block)),
         'BT0021 has contradictory catalog attributes')


def safe_folder() -> Path:
    need(WORK.is_dir() and not WORK.is_symlink() and
         WORK.resolve().is_relative_to(ROOT.resolve()) and
         not OUT.is_symlink(), 'unsafe repository workarea')
    OUT.mkdir(mode=0o700, exist_ok=True)
    folder = OUT / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                    '-' + str(os.getpid()))
    folder.mkdir(mode=0o700, exist_ok=False)
    return folder


def save(folder: Path, filename: str, content: bytes) -> None:
    need('/' not in filename and filename not in ('.', '..') and
         folder.resolve().is_relative_to(WORK.resolve()), 'unsafe evidence file')
    path = folder / filename
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags, 0o600), 'wb') as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def seal(folder: Path) -> None:
    files = sorted(path for path in folder.iterdir() if path.is_file() and
                   path.name != 'SHA256SUMS')
    rows = ''.join(hashlib.sha256(x.read_bytes()).hexdigest() + '  ' + x.name + '\n'
                   for x in files)
    save(folder, 'SHA256SUMS', rows.encode('ascii'))


def query_codepage(folder: Path) -> str:
    """No-operand Hercules panel query; failure is recorded, not guessed."""
    url = 'http://127.0.0.1:8038/cgi-bin/tasks/cmd?' + urlencode({'cmd': 'codepage'})
    try:
        with urlopen(url, timeout=6) as response:
            need(response.status == 200, 'Hercules HTTP response not successful')
            body = response.read(65537)
            need(0 < len(body) <= 65536, 'Hercules codepage response too large/empty')
        save(folder, 'hercules-codepage-response.html', body)
        return 'response-captured-unparsed'
    except (OSError, ValueError) as exc:
        save(folder, 'hercules-codepage-unavailable.json',
             (json.dumps({'status': 'unavailable', 'reason': type(exc).__name__})+'\n').encode())
        return 'unavailable-not-verified'


def live_inquiry(core, target, config: dict, folder: Path, plan: dict) -> dict:
    need(config['mvs']['hlq'] == 'HERC02', 'MVS user namespace changed')
    core.require_reader_ready(config)
    old_tmp, old_env = tempfile.tempdir, os.environ.get('TMPDIR')
    tempfile.tempdir = str(folder)
    os.environ['TMPDIR'] = str(folder)
    jobs = {}
    try:
        operations = (
            ('catalog', core.stat_deck(config, [TARGET]), 8,
             lambda report: catalog_absent(core, report)),
            ('vtoc', target.vtoc_deck(core, config, VOLUME), 0,
             lambda report: target.vtoc_observation(report, VOLUME, [TARGET])),
        )
        for name, deck, max_rc, check in operations:
            need(deck.isascii() and all(len(line) <= 80 for line in deck.splitlines()),
                 'invalid read-only MVS JCL')
            cursor = folder / (name + '-cursor.json')
            number, summary = core.submit_and_wait(
                config, deck, max_rc=max_rc, cursor_file=cursor)
            need(type(number) is int and 1 <= number <= 9999,
                 'ambiguous MVS job number')
            save(folder, name + '-summary.txt', summary.encode('utf-8'))
            report = core.job_report(number, cursor_file=cursor)
            save(folder, name + '-report.txt', report.encode('utf-8'))
            check(report)
            jobs[name] = number
    finally:
        tempfile.tempdir = old_tmp
        if old_env is None:
            os.environ.pop('TMPDIR', None)
        else:
            os.environ['TMPDIR'] = old_env
    need(set(jobs) == {'catalog', 'vtoc'} and jobs['catalog'] != jobs['vtoc'],
         'MVS preflight job results missing or duplicated')
    hercules = query_codepage(folder)
    return {**plan, 'status': 'READ_ONLY_MVS_TARGET_ABSENT_AND_VTOC_OBSERVED',
            'mvs_jobs': jobs, 'hercules_codepage': hercules,
            'vtoc_qualification': 'No numeric free-space claim; raw IEHLIST retained',
            'source_qualification': '15/15 mapped FB80 fingerprints; historical compiler lexical compatibility unproved',
            'stage_authorized': False}


def execute(live: bool) -> int:
    stage = load('ta2_bt21_stage', HERE / 'rc2-stage-draft.py')
    readiness = load('ta2_bt21_readiness', HERE / 'rc2-cambsource-readiness.py')
    qsam = load('ta2_bt21_qsam', HERE / 'rc2-qsam-fidelity.py')
    reconciler = load('ta2_bt21_reconcile', HERE / 'rc2-qsam-reconcile-transport.py')
    plan = exact_release(stage, readiness, qsam, reconciler)
    if not live:
        print('TA.2 BT0021: 15/15 original MVS source records and rc2 selective staging plan PASS.')
        print('No JES submission, DASD allocation, tape, or encoding-policy approval.')
        return 0
    core = load('ta2_bt21_core', ROOT / 'tools/datasets/dspal-core.py')
    target = load('ta2_bt21_vtoc', SCRIPTS / 'ta2-target-preflight')
    folder = safe_folder()
    try:
        result = live_inquiry(core, target, core.load_config(), folder, plan)
        save(folder, 'result.json', (json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
        seal(folder)
        print('TA.2 BT0021 READ-ONLY MVS PREFLIGHT PASS: target catalog-absent; TSO002 VTOC observed.')
        print('MVS JOBS: LISTDS ' + str(result['mvs_jobs']['catalog']) +
              ', IEHLIST ' + str(result['mvs_jobs']['vtoc']) + '.')
        print('Hercules CODEPAGE query: ' + result['hercules_codepage'] + '.')
        print('Original source JOB 9330: 15/15 transport-encoded members, 6577 FB80 records.')
        print('Staging NOT authorized; source encoding and rights remain qualified.')
        print('Private evidence: ' + folder.relative_to(ROOT).as_posix())
        return 0
    except Exception as exc:
        save(folder, 'failure.json', (json.dumps({'status':'REFUSED',
                 'reason':str(exc)}) + '\n').encode('utf-8'))
        seal(folder)
        print('TA.2 BT0021 PREFLIGHT REFUSED: ' + str(exc), file=sys.stderr)
        print('Private evidence: ' + folder.relative_to(ROOT).as_posix(), file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true',
                        help='two read-only MVS jobs; no staging writes')
    args = parser.parse_args(argv)
    try:
        return execute(args.live)
    except (Refusal, ValueError, OSError, KeyError, TypeError, UnicodeError) as exc:
        print('TA.2 BT0021 PREFLIGHT REFUSED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
