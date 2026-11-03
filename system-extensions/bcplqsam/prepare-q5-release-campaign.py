#!/usr/bin/env python3
"""Q.5 consolidated temporary-object packaging and optional-linkage MVS job.

Two BCPL sources must first be compiled by the resident demoted Cambridge
compiler. Build a temporary FB80 object PDS from Git-controlled BCPLQSAM,
read back/compare the relocatable member, and link/run selected and unselected
BCPL applications in ONE Q5PKG native job. Never writes installed PDSes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'workarea/bcplqsam-q5'
JOB = 'Q5PKG'
OUTPUT = WORK / 'q5pkg.jcl'
SELECTED_SOURCE = ROOT / 'bootstrap-toolchain/regression/163-qsam-query-capabilities/source.bcpl'
UNSELECTED_SOURCE = ROOT / 'bootstrap-toolchain/regression/146-optional-empty/source.bcpl'
SELECTED_RESULT = 'BCPLQSAM Q4 QUERY CARRIAGE PASS'
UNSELECTED_RESULT = 'R5 EXT 146 PASS'
SELECTED_STEPS = ('ASMA', 'ASMN', 'ASMR', 'ASMQ', 'ASMG', 'LKED', 'GO')
UNSELECTED_STEPS = ('ASMA', 'ASMN', 'ASMR', 'ASMG', 'LKED', 'GO')


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('helper unavailable: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_sources() -> None:
    a = SELECTED_SOURCE.read_text('ascii')
    b = UNSELECTED_SOURCE.read_text('ascii')
    if SELECTED_RESULT not in a or 'QSAMSVC:200' not in a:
        raise ValueError('selected case 163 source no longer matches Q.4')
    if UNSELECTED_RESULT not in b or 'QSAMSVC' in b:
        raise ValueError('unselected case 146 source changed')
    if not a.endswith('    FINISH\n$)1\n') or not b.endswith('    FINISH\n$)1\n'):
        raise ValueError('both native BCPL clients must FINISH')


def rename_steps(cards: list[str], prefix: str, expected: tuple[str, ...]) -> list[str]:
    """Give both halves unique MVS EXEC names, including COND/PGM references."""
    found = tuple(re.match(r'^//([A-Z0-9]{1,8})\s+EXEC\b', row).group(1)
                  for row in cards if re.match(r'^//[A-Z0-9]{1,8}\s+EXEC\b', row))
    if found != expected:
        raise ValueError(f'{prefix}: step layout changed: {found!r}')
    mapping = {name: prefix + name for name in expected}
    pattern = re.compile(r'\b(' + '|'.join(expected) + r')\b')
    result = []
    for row in cards:
        if row.startswith('//') and not row.startswith('//*'):
            row = pattern.sub(lambda m: mapping[m.group(1)], row)
            step = re.match(r'^//([A-Z0-9]{1,8})\s+EXEC\b', row)
            if step:
                row = f'//{step.group(1):<8} EXEC' + row[step.end():]
        result.append(row)
    actual = tuple(re.match(r'^//([A-Z0-9]{1,8})\s+EXEC\b', row).group(1)
                   for row in result if re.match(r'^//[A-Z0-9]{1,8}\s+EXEC\b', row))
    if actual != tuple(mapping[n] for n in expected):
        raise ValueError(f'{prefix}: step retagging failed')
    return result


def pds_steps() -> list[str]:
    """IEFBR14 allocation; IEBGENER binary copy/readback; IEBCOMPR."""
    return [
        '//ALLOC    EXEC PGM=IEFBR14,COND=(0,NE)',
        '//Q5PDS    DD  DSN=&&Q5QOBJ,DISP=(NEW,PASS),',
        '//             UNIT=SYSDA,SPACE=(TRK,(15,5,10)),',
        '//             DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//PUTQ     EXEC PGM=IEBGENER,COND=(0,NE)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSIN    DD  DUMMY',
        '//SYSUT1   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)',
        '//SYSUT2   DD  DSN=&&Q5QOBJ(BCPLQSAM),DISP=(OLD,PASS)',
        '//READQ    EXEC PGM=IEBGENER,COND=(0,NE)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSIN    DD  DUMMY',
        '//SYSUT1   DD  DSN=&&Q5QOBJ(BCPLQSAM),DISP=(OLD,PASS)',
        '//SYSUT2   DD  DSN=&&Q5READ,UNIT=SYSDA,',
        '//             SPACE=(TRK,(15,5)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//VERIFY   EXEC PGM=IEBCOMPR,COND=(0,NE)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSUT1   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)',
        '//SYSUT2   DD  DSN=&&Q5READ,DISP=(OLD,PASS)',
        '//SYSIN    DD  *',
        ' COMPARE TYPORG=PS',
        '/*',
    ]


def make_deck(selected: str, unselected: str,
              jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r'^//Q5PKG\s+JOB\b', jobcard[0]):
        raise ValueError('Q5PKG authenticated JOB card required')
    checked_sources()
    q = load(HERE / 'prepare-q1-query.py', 'q5pkg_query')
    r5 = load(ROOT / 'tools/checks/prepare-r5-extension-regression.py', 'q5pkg_r5')
    selected_rows = q.make_deck(
        selected, ["//Q1QUERY JOB (BCPL),'Q5 TEMP SOURCE',CLASS=A"], obj_dsn
    ).splitlines()
    unselected_rows = r5.make_deck(
        146, unselected, ["//RG146R JOB (BCPL),'Q5 TEMP SOURCE',CLASS=A"],
        obj_dsn, mode='source'
    ).splitlines()

    # Q.1 catalog selects a temporary sequential object. For the release
    # candidate, IEWL must instead INCLUDE the named member of our new
    # TEMPORARY object PDS (same binary object after readback comparison).
    catalog = "&BXCLIB  SETC  'QSMOBJ'"
    if selected_rows.count(catalog) != 1:
        raise ValueError('BCXCAT selection catalog has changed')
    selected_rows[selected_rows.index(catalog)] = "&BXCLIB  SETC  'EXTLIB'"
    obj_line = '//QSMOBJ   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)'
    if selected_rows.count(obj_line) != 1:
        raise ValueError('selected IEWL object DD changed')
    selected_rows[selected_rows.index(obj_line)] = (
        '//EXTLIB   DD  DSN=&&Q5QOBJ,DISP=(OLD,PASS)')
    anchor = '//ASMG     EXEC PGM=IFOX00,REGION=256K,'
    if selected_rows.count(anchor) != 1:
        raise ValueError('selected ASMG insertion point changed')
    selected_rows[selected_rows.index(anchor):selected_rows.index(anchor)] = pds_steps()

    if selected_rows[-1] != '//' or unselected_rows[-1] != '//':
        raise ValueError('unexpected template end of job')
    sel = rename_steps(selected_rows[1:-1], 'S',
                       ('ASMA', 'ASMN', 'ASMR', 'ASMQ', 'ALLOC', 'PUTQ',
                        'READQ', 'VERIFY', 'ASMG', 'LKED', 'GO'))
    unsel = rename_steps(unselected_rows[1:-1], 'N', UNSELECTED_STEPS)
    cards = [*jobcard,
             '//* Q.5 TEMPORARY PDS; NO PERMANENT INSTALL OR PROMOTION',
             *sel,
             '//* Q.5 EXCLUDED APPLICATION; NO BCPLQSAM SELECT/OBJECT',
             *unsel, '//']
    for n, row in enumerate(cards, 1):
        if not row.isascii() or '\t' in row or len(row) > 71:
            raise ValueError(f'JCL/IFOX card {n} invalid: {row!r}')
    if cards.count('         BCXREQ BCPLQSAM') != 1:
        raise ValueError('selected package request missing/duplicate')
    if cards.count("&BXCLIB  SETC  'EXTLIB'") != 1:
        raise ValueError('temporary candidate catalog incorrect')
    if cards.count('//EXTLIB   DD  DSN=&&Q5QOBJ,DISP=(OLD,PASS)') != 1:
        raise ValueError('PDS object link must occur only once')
    if any('CATLG' in row or 'DISP=MOD' in row or 'BOOT_DEVOBJ' in row
           for row in cards):
        raise ValueError('permanent library operation forbidden')
    if cards.count(' COMPARE TYPORG=PS') != 1:
        raise ValueError('binary object readback verification missing')
    if cards.count('//') != 1:
        raise ValueError('unexpected job terminator')
    if not any(row.startswith('//SGO ') for row in cards) or not any(
            row.startswith('//NGO ') for row in cards):
        raise ValueError('selected and unselected GO required')
    return '\n'.join(cards) + '\n'


def under_workarea(path: Path) -> Path:
    target = path.resolve()
    if WORK.resolve() != target.parent or path.is_symlink() or not target.is_file():
        raise ValueError('CG370 output must be a regular file in Q.5 workarea')
    return target


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--prepare', action='store_true')
    ap.add_argument('--selected', type=Path)
    ap.add_argument('--unselected', type=Path)
    args = ap.parse_args()
    if args.check:
        if args.selected or args.unselected:
            ap.error('--check takes no compiler-output paths')
        q = load(HERE / 'prepare-q1-query.py', 'q5pkg_synthetic_query')
        sample = q.time_helper().trailer_helper().sample_generated()
        deck = make_deck(sample, sample,
                         ["//Q5PKG JOB (BCPL),'Q5 CHECK',CLASS=A"],
                         'HERC02.BCPL.BOOT.OBJ')
        print('PASS: Q5PKG temporary binary PDS + selected/unselected JCL',
              len(deck.splitlines()), 'cards; no JES')
        return
    if args.selected is None or args.unselected is None:
        ap.error('--prepare requires --selected and --unselected')
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise ValueError('Q5PKG JCL already exists; refusing overwrite')
    a = under_workarea(args.selected).read_bytes()
    b = under_workarea(args.unselected).read_bytes()
    if not a or not b:
        raise ValueError('missing compiled native code')
    q = load(HERE / 'prepare-q1-query.py', 'q5pkg_config_query')
    core = q.time_helper().trailer_helper().load_core()
    cfg = core.load_config()
    spec = cfg['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or spec.get('dsorg') != 'PO'
            or spec.get('recfm') != 'FB' or int(spec.get('lrecl', 0)) != 80):
        raise ValueError('unapproved BOOT_OBJ manifest')
    jobcard = core.authenticated_job_card(cfg, JOB, 'Q5 RELEASE',
                                          redact_password=False)
    deck = make_deck(a.decode('latin-1'), b.decode('latin-1'),
                     jobcard, core.full_dsn(cfg, spec))
    WORK.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(OUTPUT, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
        stream.write(deck)
    print('PREPARED:', OUTPUT, 'cards', len(deck.splitlines()))
    print('Deck SHA-256:', hashlib.sha256(deck.encode('ascii')).hexdigest())
    print('Selected CODE SHA-256:', hashlib.sha256(a).hexdigest())
    print('Unselected CODE SHA-256:', hashlib.sha256(b).hexdigest())
    print('No JES submission or permanent dataset write')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit('Q5PKG preparation failed: ' + str(exc))
