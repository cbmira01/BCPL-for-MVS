#!/usr/bin/env python3
"""Prepare BCPLQSAM Q.1 temporary-only IFOX+IEWL linkage gate.

Uses the Q.1 source-controlled IFOX deck generator; keeps all assembled
objects and the linked load module in temporary MVS datasets.
--check uses a synthetic JOB card. --prepare writes local mode-0600 JCL.
No JES submission, BCPL GO, or permanent MVS PDS updates occur here.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / 'workarea' / 'bcplqsam-q1'
JOB = 'Q1QSLNK'


def asm_helper():
    path = HERE / 'prepare-q1-asm.py'
    spec = importlib.util.spec_from_file_location('q1_asm_helper', path)
    if spec is None or spec.loader is None:
        raise ValueError('Q.1 IFOX source-controlled helper missing')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_deck(jobcard: list[str]) -> str:
    if not jobcard or not re.match(r'^//Q1QSLNK\s+JOB\b', jobcard[0]):
        raise ValueError('expected Q1QSLNK JOB card')
    original = asm_helper().build(
        ["//Q1QSASM JOB (BCPL),'Q1 LINK SYNTHETIC',CLASS=A"])
    cards = original.splitlines()
    if cards[0][:9] != '//Q1QSASM' or cards[-1] != '//':
        raise ValueError('unexpected Q.1 assembler deck structure')
    cards = [*jobcard, *cards[1:-1]]
    obj_dispositions = [i for i, card in enumerate(cards)
                        if 'SPACE=(80,(300,100)),DISP=(NEW,DELETE)' in card]
    if len(obj_dispositions) != 1:
        raise ValueError('expected one temporary object output')
    index = obj_dispositions[0]
    cards[index] = cards[index].replace('DISP=(NEW,DELETE)',
                                        'DISP=(NEW,PASS)')
    cards += [
        '//* Q.1 LINK TEST; NO EXECUTION OR PERMANENT LIBRARY UPDATE',
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE,ASMQ)",
        '//SYSLIN   DD  DSN=&&Q1QSOBJ,DISP=(OLD,DELETE)',
        '//         DD  *',
        ' ENTRY QSMBEG',
        ' NAME Q1QSAM(R)',
        '/*',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q1QSAM),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,DELETE)',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD  SYSOUT=*',
        '//',
    ]
    for line_no, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71 or '\t' in card:
            raise ValueError(f'invalid IFOX/JCL card {line_no}: {card!r}')
    if cards.count('/*') != 2 or cards.count('//SYSIN    DD  *') != 1:
        raise ValueError('expected one assembler source and one IEWL control')
    if any('CATLG' in card or 'DISP=MOD' in card or 'BOOT_OBJ' in card
           or 'BOOT_DEVOBJ' in card or '//GO ' in card
           for card in cards):
        raise ValueError('forbidden permanent object or execution reference')
    if not any('DISP=(NEW,DELETE)' in card for card in cards):
        raise ValueError('missing disposable load-module output')
    return '\n'.join(cards) + '\n'


def local_job_card() -> list[str]:
    helper = ROOT / 'tools/datasets/dspal-core.py'
    spec = importlib.util.spec_from_file_location('q1_link_core', helper)
    if spec is None or spec.loader is None:
        raise ValueError('missing authenticated JOB-card helper')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.authenticated_job_card(
        module.load_config(), JOB, 'Q1 LINK', redact_password=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true',
                      help='offline synthetic card validation only')
    mode.add_argument('--prepare', action='store_true',
                      help='write protected local JCL; do not submit')
    args = parser.parse_args()
    if args.check:
        deck = make_deck(["//Q1QSLNK JOB (BCPL),'Q1 CHECK',CLASS=A"])
        print(f'PASS: Q.1 temporary IFOX+IEWL deck: '
              f'{len(deck.splitlines())} cards, no MVS execution')
        return
    deck = make_deck(local_job_card())
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / 'q1link.jcl'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as out:
            fd = -1
            out.write(deck)
    finally:
        if fd != -1:
            os.close(fd)
    print(f'PREPARED only: {target}')
    print('This program does not submit JES jobs or install MVS objects.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f'Q.1 IEWL preparation FAILED: {exc}')
