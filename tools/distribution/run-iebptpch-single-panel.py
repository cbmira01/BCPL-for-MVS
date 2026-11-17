#!/usr/bin/env python3
"""TA.0: selected FB80 member readback, one read-only MVS job per member.

Use the format proven by single-member JOB 9044. Each JES job is separately
cursor-scoped; no automatic retry, tape operation, or binary source claim.
No files are created inside the Git checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
# Centralized, symlink-safe ignored-workarea evidence policy.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path
TOOLS = ROOT / 'tools/distribution'
CORE = ROOT / 'tools/datasets/dspal-core.py'
PREP = TOOLS / 'prepare-iebptpch-readback.py'
PILOT = TOOLS / 'submit-iebptpch-pilot.py'
DECODER = TOOLS / 'decode-iebptpch-multi.py'
ALLOWED = {'MR10_OBJ': 'M', 'BOOT_OBJ': 'B', 'EXT_OBJ': 'E'}
MEMBER = re.compile(r'[A-Z@$#][A-Z0-9@$#]{0,7}\Z')
MAX_MEMBERS = 20


class PanelError(ValueError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise PanelError(message)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            'required in-repository module is missing')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def safe_json(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, sort_keys=True, indent=2) + '\n').encode('utf-8')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as inp:
        while chunk := inp.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def preflight(prep, core, *, key: str, members: list[str],
              output: Path) -> None:
    """Validate the whole panel BEFORE the first MVS submission."""
    require(key in ALLOWED, 'only three selected FB80 object PDSes supported')
    require(type(members) is list and 1 <= len(members) <= MAX_MEMBERS,
            'one to twenty members must be selected')
    require(all(type(m) is str and MEMBER.fullmatch(m) is not None for m in members),
            'all members must be legal uppercase MVS names')
    require(len(members) == len(set(members)), 'duplicate selected member')
    try:
        guard_evidence_path(output, new=True, root=ROOT)
    except ValueError as exc:
        raise PanelError('output must be a NEW private directory under workarea/') from exc
    manifest = prep.load_yaml(prep.MANIFEST)
    dspal = prep.load_yaml(prep.DSPAL)
    config = core.load_config()
    source = config['datasets'].get(key)
    require(type(source) is dict, 'active dspal dataset mapping missing')
    require(all(source.get(field) == expected for field, expected in (
        ('dsorg', 'PO'), ('recfm', 'FB'), ('lrecl', 80), ('blksize', 800))),
        'active source DCB not PO/FB/80/800')
    dsn = core.full_dsn(config, source)
    for member in members:
        body = prep.make_job_body(manifest, dspal, dataset_key=key,
                                  members=[member], hlq=config['mvs']['hlq'])
        require(f'//SYSUT1   DD DSN={dsn},DISP=SHR\n' in body,
                'active source dataset differs from selected design DCB/source')
        require('MAXNAME=1' in body and body.count('MEMBER NAME=') == 1,
                'expected single-member IEBPTPCH card not generated')


def select_members(prep, *, key: str, named: list[str] | None,
                   all_selected: bool) -> list[str]:
    require(key in ALLOWED, 'unsupported object source')
    require(all_selected != bool(named),
            'specify either repeated --member or --all-selected')
    if named:
        return named
    manifest = prep.load_yaml(prep.MANIFEST)
    entries = [r for r in manifest.get('datasets', [])
               if type(r) is dict and r.get('dspal_key') == key]
    require(len(entries) == 1 and type(entries[0].get('members')) is list,
            'manifest source selection ambiguous')
    return entries[0]['members'][:]


def run_panel(prep, core, pilot, decoder, *, key: str,
              members: list[str], output: Path) -> dict[str, Any]:
    """Execute selected member jobs sequentially, stop on any ambiguity.

    Existing pilot.run_one and decoder.process do all JES and report validation.
    A failure does not consume an unused member slot or retry MVS.
    """
    preflight(prep, core, key=key, members=members, output=output)
    os.mkdir(output, 0o700)
    items: list[dict[str, Any]] = []
    for ordinal, member in enumerate(members, 1):
        label = f'{ordinal:02d}-{member}'
        pilot_dir = output / f'{label}-pilot'
        decoded_dir = output / f'{label}-decoded'
        jobname = f'TA0{ALLOWED[key]}{ordinal:03d}'
        # No retries: partial evidence remains available for future investigation.
        receipt = None
        stage = 'pilot'
        try:
            receipt = pilot.run_one(core, prep, key=key, members=[member],
                                    output=pilot_dir, jobname=jobname)
            stage = 'decode'
            decoded = decoder.process(pilot_dir, decoded_dir, expected_counts=[])
            actual = decoded.get('members')
            require(type(actual) is list and len(actual) == 1 and
                    actual[0].get('member') == member,
                    f'{member}: decoder returned inconsistent member evidence')
            require(decoded.get('source_job') == receipt.get('job'),
                    f'{member}: decoder returned inconsistent JES job identity')
        except Exception as exc:
            # Safe, narrowly-scoped failure metadata; no JOB cards or SYSOUT.
            safe_json(output / 'failure.json', {
                'failed_member': member, 'ordinal': ordinal,
                'stage': stage, 'exception_type': type(exc).__name__,
                'pilot_job': receipt.get('job') if receipt is not None else None,
                'note': 'NO AUTOMATIC RETRY; retained pilot evidence may be partial',
            })
            raise
        items.append({
            'member': member,
            'job': receipt['job'],
            'jobname': jobname,
            'record_count_from_print': actual[0]['record_count'],
            'bytes_from_print': actual[0]['byte_count'],
            'sha256_of_decoded_print': actual[0]['sha256_of_decoded_print'],
            'pilot_receipt_sha256': file_sha256(pilot_dir / 'receipt.json'),
            'decode_receipt_sha256': file_sha256(decoded_dir / 'decode-receipt.json'),
            'pilot_directory': pilot_dir.name,
            'decoded_directory': decoded_dir.name,
        })
        # A crash after a successful member still has its pilot and decoded
        # receipts, but the panel-level receipt is written ONLY when complete.
    result = {
        'phase': 'TA.0 SINGLE-MEMBER FB80 PANEL — PRINTER-DECODE EVIDENCE ONLY',
        'dataset_key': key,
        'selected_members': members,
        'completed': len(items),
        'members': items,
        'qualifications': [
            'Every member was printed in its own read-only IEBPTPCH JES job.',
            'No automatic retry of any failed or ambiguous MVS job.',
            'Decoded bytes are printer-output evidence, not independent DASD identity.',
            'Git source linkage, rights, and release/tape acceptance remain open.',
            'The earlier JOB 9045 multi-member framing anomaly remains unresolved.',
        ],
    }
    safe_json(output / 'panel-receipt.json', result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-key', required=True,
                        choices=(*sorted(ALLOWED), 'MR10_LOAD'))
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument('--member', action='append',
                          help='repeat for each selected member; one JES job per member')
    selector.add_argument('--all-selected', action='store_true',
                          help='all canonically selected members of this object PDS')
    parser.add_argument('--output-dir', required=True, type=Path,
                        help='new private directory inside ignored workarea/')
    args = parser.parse_args(argv)
    try:
        os.umask(0o077)
        prep = load_module(PREP, 'ta0_panel_prepare')
        core = load_module(CORE, 'ta0_panel_core')
        pilot = load_module(PILOT, 'ta0_panel_pilot')
        decoder = load_module(DECODER, 'ta0_panel_decoder')
        members = select_members(prep, key=args.dataset_key,
                                 named=args.member, all_selected=args.all_selected)
        summary = run_panel(prep, core, pilot, decoder, key=args.dataset_key,
                            members=members, output=args.output_dir)
    except (PanelError, ValueError, RuntimeError, OSError, UnicodeError) as exc:
        # Avoid echoing auth-bearing reports or full exception strings.
        print(f'TA.0 SINGLE-PANEL REFUSED/STOPPED: {type(exc).__name__}',
              file=sys.stderr)
        failure = args.output_dir / 'failure.json'
        if failure.is_file() and not failure.is_symlink():
            try:
                info = json.loads(failure.read_text(encoding='utf-8'))
                print(f"  stage={info['stage']} member={info['failed_member']} "
                      f"job={info['pilot_job']}", file=sys.stderr)
            except (ValueError, OSError, KeyError, UnicodeError):
                pass
        print('No automatic retry; private evidence was retained.', file=sys.stderr)
        return 1
    print(f"TA.0 SINGLE-PANEL: {summary['dataset_key']}, "
          f"{summary['completed']} member jobs completed and decoded")
    for item in summary['members']:
        print(f"  {item['member']}: JOB {item['job']}, "
              f"{item['record_count_from_print']} FB80, "
              f"SHA-256={item['sha256_of_decoded_print']}")
    print('Printer-output hashes only; no independent DASD/source/tape acceptance.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
