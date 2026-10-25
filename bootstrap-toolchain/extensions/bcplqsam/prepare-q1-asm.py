#!/usr/bin/env python3
"""Prepare an isolated IFOX syntax/OBJECT gate for Q.1 BCPLQSAM.

--check: no credentials, output files, MVS jobs or PDS writes.
--prepare: make credential-bearing JCL only in ignored workarea/ (0600).
Never submits to JES. Object output is a DISPOSABLE sequential && dataset.
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
JOB = 'Q1QSASM'
SOURCE = HERE / 'bcplqsam.asm'


def source_cards() -> list[str]:
    cards = SOURCE.read_text(encoding='ascii').splitlines()
    if not cards:
        raise ValueError('missing BCPLQSAM source')
    for no, card in enumerate(cards, 1):
        if (len(card) > 71 or not card.isascii() or '\t' in card or
                card.startswith('//') or card == '/*'):
            raise ValueError(f'invalid IFOX source card {no}: {card!r}')
    if 'QSMDESC  CSECT' not in cards or 'QSMFIN   CSECT' not in cards:
        raise ValueError('missing BCEX descriptor or generic finalizer')
    if not any(line == '         END' for line in cards):
        raise ValueError('source lacks END card')
    return cards


def build(job_card: list[str]) -> str:
    if not job_card or not re.match(r'^//Q1QSASM\s+JOB\b', job_card[0]):
        raise ValueError('expected Q1QSASM JOB card')
    cards = [
        *job_card,
        '//* Q.1 IFOX ONLY: TEMP OBJECT, NO INSTALLED PDS WRITES',
        '//ASMQ     EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSPUNCH DD  DUMMY',
        '//SYSGO    DD  DSN=&&Q1QSOBJ,UNIT=SYSDA,',
        '//             SPACE=(80,(300,100)),DISP=(NEW,DELETE),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSIN    DD  *',
        *source_cards(),
        '/*',
        '//',
    ]
    for no, card in enumerate(cards, 1):
        if len(card) > 71 or not card.isascii() or '\t' in card:
            raise ValueError(f'invalid JCL/IFOX card {no}: {card!r}')
    if cards.count('/*') != 1 or cards.count('//SYSIN    DD  *') != 1:
        raise ValueError('unexpected inline source boundary')
    if any('DISP=MOD' in card or 'CATLG' in card or 'BOOT_OBJ' in card
           or 'BOOT_DEVOBJ' in card or 'EXT_OBJ' in card
           for card in cards):
        raise ValueError('forbidden persistent object-library reference')
    if not any('DISP=(NEW,DELETE)' in card for card in cards):
        raise ValueError('missing temporary-object disposal')
    return '\n'.join(cards) + '\n'


def local_job_card() -> list[str]:
    helper = ROOT / 'tools/datasets/dspal-core.py'
    spec = importlib.util.spec_from_file_location('q1_dspal_core', helper)
    if spec is None or spec.loader is None:
        raise ValueError('missing repository-owned JOB-card provider')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = module.load_config()
    return module.authenticated_job_card(config, JOB, 'Q1 IFOX',
                                         redact_password=False)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true',
                        help='offline card validation, no files or credentials')
    action.add_argument('--prepare', action='store_true',
                        help='create protected local JCL; no JES submission')
    args = p.parse_args()
    if args.check:
        jcl = build(["//Q1QSASM JOB (BCPL),'Q1 OFFLINE',CLASS=A"])
        print(f'PASS: Q.1 temporary IFOX job, {len(jcl.splitlines())} cards; '
              'no credentials, no MVS execution')
        return
    jcl = build(local_job_card())
    WORK.mkdir(parents=True, exist_ok=True)
    output = WORK / 'q1asm.jcl'
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii', newline='\n') as stream:
            fd = -1
            stream.write(jcl)
    finally:
        if fd != -1:
            os.close(fd)
    print(f'PREPARED only: {output}')
    print('MVS IFOX not run. Use tools/mvs/submit-jcl explicitly.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f'Q.1 IFOX preparation FAILED: {exc}')
