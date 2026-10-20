#!/usr/bin/env python3
"""Prepare standalone Milestone QSAM Q.0 pending-READ retry probe."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
JOB = 'QS0RETRY'


def harness():
    spec = importlib.util.spec_from_file_location('q0_dasd_base', PARENT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'QSAM DASD probe harness not found: {PARENT}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source(filename: str) -> str:
    content = (HERE / filename).read_text(encoding='ascii')
    for lineno, card in enumerate(content.splitlines(), 1):
        if not card.isascii() or len(card) > 71 or card.startswith('//') or card == '/*':
            raise ValueError(f'invalid IFOX source card {filename}:{lineno}: {card!r}')
    return content.rstrip('\n')


def make_deck(jobcard: list[str]) -> str:
    if not jobcard or not jobcard[0].startswith('//'+JOB):
        raise ValueError('unexpected JOB card')
    base = harness()
    writer = source('retry-write.asm')
    reader = source('retry-read.asm')
    cards = [
        *jobcard,
        '//* Q.0 TEST ONLY - PRIVATE FB80 STAGE, 2 SHORT READ RETRIES',
        '//* TWO DISTINCT RECORDS, EODAD, PERSISTENT EOF, NO PDS WRITES',
        *base.asm_step('ASMWR', 'PRWOBJ', writer),
        *base.asm_step('ASMRD', 'PRROBJ', reader),
        *base.link_step('LKWR', 'PRWOBJ', 'PRWMOD', 'Q0PRWMOD',
                        'Q0PRW', 'ASMWR'),
        *base.link_step('LKRD', 'PRROBJ', 'PRRMOD', 'Q0PRRMOD',
                        'Q0PRR', 'ASMRD'),
        '//WGO      EXEC PGM=*.LKWR.SYSLMOD,TIME=(,1),',
        '//             COND=((0,NE,ASMWR),(0,NE,LKWR))',
        '//QDISK    DD  DSN=&&Q0RETRY,DISP=(NEW,PASS),',
        '//             UNIT=SYSDA,SPACE=(TRK,(1,1)),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSUDUMP DD  SYSOUT=*',
        '//RGO      EXEC PGM=*.LKRD.SYSLMOD,TIME=(,1),',
        '//             COND=((0,NE,WGO),(0,NE,LKRD))',
        '//QDISK    DD  DSN=&&Q0RETRY,DISP=(OLD,DELETE)',
        '//QOUT     DD  SYSOUT=*,',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSPRINT DD  SYSOUT=*',
        '//SYSUDUMP DD  SYSOUT=*',
        '//',
    ]
    for lineno, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f'bad JCL card {lineno}: {card!r}')
    deck = '\n'.join(cards) + '\n'
    required = (
        "DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//QDISK    DD  DSN=&&Q0RETRY,DISP=(NEW,PASS),",
        "//QDISK    DD  DSN=&&Q0RETRY,DISP=(OLD,DELETE)",
        "Q0 FB80 PENDING RETRIES 2 RECORDS PASS",
        "CLC   DEST(80),SENTINEL",
        "GET   QDCB,STAGE",
        "EODAD=ATEND",
        "Q0PND001", "Q0PND002",
        "CLI   DEST+8,X'00'", "CLI   DEST+8,X'FF'",
        "C     15,=F'-1'",
    )
    for text in required:
        if text not in deck:
            raise ValueError(f'missing essential probe element: {text}')
    if deck.count('GET   QDCB,STAGE') != 1:
        raise ValueError('unexpected duplicate QSAM GET location')
    if deck.count('PUT   QDCB,AREA') != 2:
        raise ValueError('unexpected QSAM data writer PUT count')
    if '//SYSIN    DD  *' not in deck or cards.count('/*') != 4:
        raise ValueError('malformed in-stream assembler/link-editor sections')
    return deck


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='static source/JCL validation, no job credentials or file output')
    args = parser.parse_args()
    if args.check:
        jobcard = [f"//{JOB} JOB (BCPL),'Q0 RETRY',CLASS=A,MSGCLASS=A"]
    else:
        parent = harness()
        config = parent.config_module()
        settings = config.load_config()
        jobcard = config.authenticated_job_card(
            settings, JOB, 'Q0 PENDING RETRY', redact_password=False)
    deck = make_deck(jobcard)
    if args.check:
        print(f'CHECK RETRY: {len(deck.splitlines())} cards; source/JCL OK; no deck written')
        return
    path = ROOT / 'workarea/qsam-q0-pending-retry' / 'q0-retry.jcl'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(deck, encoding='ascii', newline='\n')
    path.chmod(0o600)
    print(f'Q.0 pending-READ retry JCL: {path}')


if __name__ == '__main__':
    main()
