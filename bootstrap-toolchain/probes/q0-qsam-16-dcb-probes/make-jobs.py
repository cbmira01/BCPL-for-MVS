#!/usr/bin/env python3
"""Make test-only Q.0 multi-DCB QSAM jobs; never install object code."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / 'q0-qsam-dasd-probes' / 'make-jobs.py'
PROFILES = {'one': (1, 256), 'three': (3, 256),
            'eight': (8, 256), 'sixteen': (16, 256),
            'sixteen-512': (16, 512)}
JOB = {'one': 'Q0H1', 'three': 'Q0H3', 'eight': 'Q0H8',
       'sixteen': 'Q0H16', 'sixteen-512': 'Q0H16B'}


def harness():
    spec = importlib.util.spec_from_file_location('q0_dasd_base', BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError('missing Q.0 DASD job harness')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_source(count: int, reader: bool) -> str:
    entry = 'Q0HNR' if reader else 'Q0HNW'
    src = [
        '* Q.0 TEST ONLY: MULTIPLE SIMULTANEOUS OPEN QSAM DCBs.',
        '* EACH OWNS 1024 BYTES FROM CHECKED GETMAIN; NO BCPL API.',
        f'{entry:<8} CSECT',
        '         STM   14,12,12(13)',
        '         LR    12,15',
        f'         USING {entry},12',
        '         LA    10,4095(12)',
        '         LA    10,1(10)',
        f'         USING {entry}+4096,10',
        '         LA    9,4095(10)',
        '         LA    9,1(9)',
        f'         USING {entry}+8192,9',
        '         LA    11,SAVREG',
        '         ST    13,4(11)',
        '         ST    11,8(13)',
        '         LR    13,11',
        f'         XC    PTRS({count * 4}),PTRS',
        '         XC    NALLOC(4),NALLOC',
        '         XC    NFREE(4),NFREE',
        '         XC    STATUS(4),STATUS',
    ]
    if reader:
        src.append('         XC    EOFCOUNT(4),EOFCOUNT')
    for i in range(count):
        src += ['         GETMAIN RC,LV=1024',
                '         LTR   15,15',
                '         BNZ   ALFAIL',
                f'         ST    1,PTR{i:02d}',
                '         L     3,NALLOC',
                '         LA    3,1(3)',
                '         ST    3,NALLOC']
    for i in range(count):
        src.append(f'         OPEN  (DC{i:02d},({"INPUT" if reader else "OUTPUT"}))')
    for recno in (1, 2):
        for i in range(count):
            src.append(f'         L     1,PTR{i:02d}')
            if reader:
                src += [f'         L     0,PTR{i:02d}',
                        f'         GET   DC{i:02d},(0)',
                        f"         CLC   0(8,1),=CL8'Q0H{i:02d}R{recno:02d}'",
                        '         BNE   FAILED',
                        '         CLC   8(248,1),BLANKS',
                        '         BNE   FAILED']
                for offset in (256, 512):
                    src += [f'         CLC   {offset}(256,1),BLANKS',
                            '         BNE   FAILED']
                src += ['         CLC   768(255,1),BLANKS',
                        '         BNE   FAILED',
                        f"         CLI   1023(1),X'{('FE' if recno == 1 else 'FD')}'",
                        '         BNE   FAILED']
            else:
                for offset in (0, 256, 512, 768):
                    src.append(f'         MVC   {offset}(256,1),BLANKS')
                src += [f"         MVC   0(8,1),=CL8'Q0H{i:02d}R{recno:02d}'",
                        f"         MVI   1023(1),X'{('FE' if recno == 1 else 'FD')}'",
                        f'         L     0,PTR{i:02d}',
                        f'         PUT   DC{i:02d},(0)']
    if reader:
        for i in range(count):
            src += [f'         L     0,PTR{i:02d}',
                    f'         GET   DC{i:02d},(0)',
                    '         B     FAILED',
                    f'EOF{i:02d}   L     3,EOFCOUNT',
                    '         LA    3,1(3)',
                    '         ST    3,EOFCOUNT']
        src += ['         L     3,EOFCOUNT', f"         C     3,=F'{count}'",
                '         BNE   FAILED']
    src += ['         B     CLEANUP',
            'FAILED   LA    3,8',
            '         ST    3,STATUS',
            'CLEANUP  DS    0H']
    for i in range(count - 1, -1, -1):
        src.append(f'         CLOSE (DC{i:02d})')
    src += ['         BAL   7,DRAIN',
            '         L     3,NALLOC',
            f"         C     3,=F'{count}'",
            '         BNE   BADEND',
            '         C     3,NFREE',
            '         BNE   BADEND',
            '         L     3,STATUS',
            '         LTR   3,3',
            '         BNZ   BADEND']
    if reader:
        src += ['         OPEN  (ODCB,(OUTPUT))',
                '         PUT   ODCB,PASSREC',
                '         CLOSE (ODCB)']
    src += ['         L     13,4(13)',
            '         LM    14,12,12(13)',
            '         SR    15,15',
            '         BR    14',
            'ALFAIL   BAL   7,DRAIN',
            'BADEND   L     13,4(13)',
            '         LM    14,12,12(13)',
            '         LA    15,8',
            '         BR    14',
            '* FREE ONLY SUCCESSFULLY OWNED STAGES, IN REVERSE ORDER.',
            'DRAIN    DS    0H']
    for i in range(count - 1, -1, -1):
        src += [f'         L     1,PTR{i:02d}',
                '         LTR   1,1',
                f'         BZ    SK{i:02d}',
                '         FREEMAIN R,LV=1024,A=(1)',
                f'         XC    PTR{i:02d}(4),PTR{i:02d}',
                '         L     3,NFREE',
                '         LA    3,1(3)',
                '         ST    3,NFREE',
                f'SK{i:02d}    DS    0H']
    src += ['         BR    7',
            '         DS    0F',
            'PTRS     DS    0F']
    for i in range(count):
        src.append(f"PTR{i:02d}    DC    F'0'")
    src += ["NALLOC   DC    F'0'",
            "NFREE    DC    F'0'",
            "STATUS   DC    F'0'"]
    if reader:
        src.append("EOFCOUNT DC    F'0'")
    src += ["BLANKS   DC    CL256' '",
            'SAVREG   DS    18F']
    for i in range(count):
        macrf = 'GM' if reader else 'PM'
        eof = f',EODAD=EOF{i:02d}' if reader else ''
        src.append(f'DC{i:02d}     DCB   DDNAME=Q{i:02d},DSORG=PS,MACRF={macrf}{eof}')
    if reader:
        src += [f"PASSREC  DC    CL80'Q0 {count:02d} DCB F1024 2 RECORDS PASS'",
                'ODCB     DCB   DDNAME=QOUT,DSORG=PS,MACRF=PM']
    src += ['         LTORG', f'         END   {entry}']
    for line_no, card in enumerate(src, 1):
        if not card.isascii() or len(card) > 71 or card.startswith('//'):
            raise ValueError(f'invalid source card {line_no}: {card!r}')
    return '\n'.join(src)


def make_deck(profile: str, jobcard: list[str]) -> str:
    count, region = PROFILES[profile]
    job = JOB[profile]
    if (not jobcard or jobcard[0][2:10].rstrip() != job or
            not jobcard[0][10:].startswith(' JOB ')):
        raise ValueError('unexpected padded JOB card')
    base = harness()
    cards = [*jobcard,
             '//* Q.0 TEST ONLY: CONCURRENT F1024 DCBs AND PRIVATE STAGES',
             '//* ALL DATA SETS TEMPORARY; NO BOOT PDS UPDATES',
             *base.asm_step('ASMWR', 'HWR0OBJ', make_source(count, False)),
             *base.asm_step('ASMRD', 'HRD0OBJ', make_source(count, True)),
             *base.link_step('LKWR', 'HWR0OBJ', 'HWRMOD', 'Q0HWRMOD',
                             'Q0HNW', 'ASMWR'),
             *base.link_step('LKRD', 'HRD0OBJ', 'HRDMOD', 'Q0HRDMOD',
                             'Q0HNR', 'ASMRD'),
             f'//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION={region}K,',
             '//             TIME=(,2),COND=((0,NE,ASMWR),(0,NE,LKWR))']
    for i in range(count):
        cards += [f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d},DISP=(NEW,PASS),',
                  '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',
                  '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)']
    cards += ['//SYSUDUMP DD  SYSOUT=*',
              f'//RGO      EXEC PGM=*.LKRD.SYSLMOD,REGION={region}K,',
              '//             TIME=(,2),COND=((0,NE,WGO),(0,NE,LKRD))']
    for i in range(count):
        cards.append(f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d},DISP=(OLD,DELETE)')
    cards += ['//QOUT     DD  SYSOUT=*,',
              '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
              '//SYSUDUMP DD  SYSOUT=*', '//']
    for line_no, card in enumerate(cards, 1):
        if not card.isascii() or len(card) > 71:
            raise ValueError(f'invalid JCL card {line_no}: {card!r}')
    deck = '\n'.join(cards) + '\n'
    if deck.count('//SYSIN    DD  *') != 2 or deck.splitlines().count('/*') != 4:
        raise ValueError('unexpected number of assembler/linker inputs')
    # Restrict the check to the N QSAM input DDs. The two link-edit
    # SYSLIN object DDs also use DISP=(OLD,DELETE).
    for i in range(count):
        expected = (f'//Q{i:02d}      DD  DSN=&&Q0H{i:02d},'
                    'DISP=(OLD,DELETE)')
        if cards.count(expected) != 1:
            raise ValueError(f'temporary QSAM DD Q{i:02d} cleanup missing')
    return deck


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', choices=PROFILES)
    parser.add_argument('--check', action='store_true',
                        help='validate without credentials or output files')
    args = parser.parse_args()
    job = JOB[args.profile]
    if args.check:
        jobcard = [f"//{job:<8} JOB (BCPL),'Q0 MULTI',CLASS=A,MSGCLASS=A"]
    else:
        core = harness().config_module()
        config = core.load_config()
        jobcard = core.authenticated_job_card(
            config, job, 'Q0 MULTI', redact_password=False)
    deck = make_deck(args.profile, jobcard)
    if args.check:
        print(f'CHECK Q0 {args.profile}: {len(deck.splitlines())} cards, '
              'no credentials or JCL written')
    else:
        out = ROOT / 'workarea/qsam-q0-16-dcb' / f'q0-{args.profile}.jcl'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(deck, encoding='ascii', newline='\n')
        out.chmod(0o600)
        print('Q.0 experimental JCL:', out)


if __name__ == '__main__':
    main()
