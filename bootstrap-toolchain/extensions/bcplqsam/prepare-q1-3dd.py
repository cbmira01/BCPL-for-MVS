#!/usr/bin/env python3
"""Prepare isolated Q.1 native three-DD OPEN/INFO/CLOSE integration JCL.

Uses the accepted Q.0 F1024 temporary writer, and Q.1's tested native
BCX QUERY-only assembler/link template. The three input datasets are
created and populated by WGO, then opened by native GO. Never installs
objects, rewrites BCXCAT or uses a non-256K native GO.
--check is credential-free synthetic JCL verification; --generated
reads CG370 assembler from ignored workarea and only prepares local JCL.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea/bcplqsam-q1'
JOB = 'Q13DD'


def module_at(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing source-controlled helper: {path}')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def query_helper():
    return module_at(HERE / 'prepare-q1-query.py', 'q1_three_query')


def q0_writer_helper():
    return module_at(
        ROOT / 'bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py',
        'q1_three_writer')


def replace_one(cards: list[str], old: str, new: str) -> None:
    if cards.count(old) != 1:
        raise ValueError(f'unexpected Q.1 integration deck card: {old!r}')
    cards[cards.index(old)] = new


def make_deck(generated: str, jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not re.match(r'^//Q13DD\s+JOB\b', jobcard[0]):
        raise ValueError('expected authenticated Q13DD JOB card')
    q = query_helper()
    # Reuse the accepted, temporary native Q.1 BCX import construction.
    base = q.make_deck(
        generated, ["//Q1QUERY JOB (BCPL),'Q1 TEMPLATE',CLASS=A"], obj_dsn)
    cards = base.splitlines()
    cards[:1] = jobcard
    replace_one(cards, ' NAME Q1QUERY(R)', ' NAME Q13DD(R)')
    replace_one(cards, '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QUERY),',
                '//SYSLMOD  DD  DSN=&&Q1LOAD(Q13DD),')
    replace_one(cards, '//             TIME=(,2),COND=(0,NE,LKED)',
                '//             TIME=(,2),COND=((0,NE,LKED),(0,NE,WGO))')

    writer = q0_writer_helper()
    h = writer.harness()
    writer_source = writer.make_source(3, False)
    writer_cards = [
        *h.asm_step('ASMWR', 'Q1WOBJ', writer_source),
        *h.link_step('LKWR', 'Q1WOBJ', 'Q1WMOD',
                     'Q1WRMOD', 'Q0HNW', 'ASMWR'),
    ]
    # Preserve every authenticated JOB continuation card before EXEC steps.
    cards[len(jobcard):len(jobcard)] = [
        '//* Q.1 THREE INPUT DDs; Q.0 TEMPORARY F1024 WRITER',
        *writer_cards,
    ]
    go_card = '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,'
    if cards.count(go_card) != 1:
        raise ValueError('expected one native GO step')
    go_idx = cards.index(go_card)
    # The Q.0 writer must create real initialized input datasets
    # before the native application attempts its three QSAM OPENs.
    first = [
        '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=((0,NE,ASMWR),(0,NE,LKWR))',
    ]
    for i in range(3):
        first += [
            f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(NEW,PASS),',
            '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',
            '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)',
        ]
    first += ['//SYSUDUMP DD  SYSOUT=*']
    cards[go_idx:go_idx] = first
    # Attach the three existing DATASETs only to the native GO step,
    # never to the IFOX or IEWL compilation steps.
    new_go_idx = cards.index(go_card)
    go_header = '//             TIME=(,2),COND=((0,NE,LKED),(0,NE,WGO))'
    if cards[new_go_idx + 1] != go_header:
        raise ValueError('native GO conditional guard missing')
    attach = [f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE)'
              for i in range(3)]
    cards[new_go_idx + 2:new_go_idx + 2] = attach

    for n, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'invalid Q.1 three-DD IFOX/JCL card {n}: {card!r}')
    if cards.count('/*') != 8 or cards.count('//SYSIN    DD  *') != 6:
        # Five native assembler source streams plus the Q.0 writer.
        raise ValueError('expected six assembler input streams and two links')
    if cards.count('         BCXREQ BCPLQSAM') != 1:
        raise ValueError('temporary-only BCXREQ missing or duplicated')
    if any('CATLG' in card or 'DISP=MOD' in card or
           'BOOT_DEVOBJ' in card and card.startswith('//') or
           '//EXTLIB' in card for card in cards):
        raise ValueError('forbidden permanent library update')
    for i in range(3):
        if cards.count(f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},'
                       'DISP=(NEW,PASS),') != 1:
            raise ValueError(f'Q{i:02d} writer allocation missing')
        if cards.count(f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},'
                       'DISP=(OLD,DELETE)') != 1:
            raise ValueError(f'Q{i:02d} native input missing')
    if cards.count(' ENTRY R0APP') != 1 or cards.count(' ENTRY Q0HNW') != 1:
        raise ValueError('link-edit entry cards not as expected')
    return '\n'.join(cards) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='offline synthetic checks without credentials')
    parser.add_argument('--generated', type=Path,
                        help='real CG370 output of test-q1-3dd.bcpl')
    args = parser.parse_args()
    q = query_helper()
    if args.check:
        if args.generated is not None:
            parser.error('--check cannot take --generated')
        helper = q.time_helper().trailer_helper()
        deck = make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'Q1 OFFLINE',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')
        print(f'PASS: Q.1 temporary three-DD deck '
              f'({len(deck.splitlines())} cards), no MVS execution')
        return
    if args.generated is None:
        parser.error('--generated required for local authenticated JCL')
    generated = args.generated.resolve()
    if (ROOT / 'workarea').resolve() not in generated.parents:
        raise ValueError('CG370 assembler must reside under workarea/')
    core = q.time_helper().trailer_helper().load_core()
    config = core.load_config()
    spec = config['datasets']['BOOT_OBJ']
    if (spec.get('content_type') != 'object' or
        spec.get('dsorg') != 'PO' or
        spec.get('recfm') != 'FB' or
        int(spec.get('lrecl', 0)) != 80):
        raise ValueError('manifest BOOT_OBJ must be an FB80 object PDS')
    obj_dsn = core.full_dsn(config, spec)
    jobcard = core.authenticated_job_card(config, JOB, 'Q1 3DD',
                                          redact_password=False)
    deck = make_deck(generated.read_bytes().decode('latin-1'),
                     jobcard, obj_dsn)
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / 'q13dd.jcl'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
            fd = -1
            out.write(deck)
    finally:
        if fd >= 0:
            os.close(fd)
    print(f'PREPARED ONLY: {target}')
    print('Q.0 writer + Q.1 native GO REGION=256K, no installed PDS changes')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'Q.1 three-DD job preparation FAILED: {exc}')
