#!/usr/bin/env python3
"""TA.2: read-only MVS QSAM test of all 15 frozen Cambridge FB80 PDS members.

IFOX + IEWL build a temporary, in-job program which GETs each MVS member,
counts every 80-byte record (including all-blank records), and reports two
rolling checksums over original EBCDIC bytes. There is no PDS write or tape
operation. All original JES evidence is kept under repository workarea.
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
import tempfile

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / 'workarea'
EVIDENCE = WORK / 'ta2-rc2-cambsource-qsam-fidelity'
ASM = HERE / 'rc2-qsam-fidelity.asm'
DSN = 'HERC02.BCPL.CAMBRIDG.SOURCE'
NAMES = ('BCPL', 'BLIB', 'CG', 'CGHDR', 'EDITMAIN', 'IOS', 'LIBHDR',
         'PM', 'SYN', 'SYNHDR', 'TRN', 'TRNHDR', 'MAKEOBJ', 'MAKELIB', 'PROGRAM')
REPORT_LINE = re.compile(
    r'(?m)^\s{0,3}BCSRC MEMBER=([A-Z0-9@$#]{1,8})\s+'
    r'COUNT=([0-9A-F]{8}) TRAIL=([0-9A-F]{8}) '
    r'FNV=([0-9A-F]{8}) SUM=([0-9A-F]{8})\s*$')


class Refusal(ValueError):
    pass


def require(ok: bool, why: str) -> None:
    if not ok:
        raise Refusal(why)


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f'missing {name}')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def fingerprint(raw: bytes) -> dict[str, int]:
    """Compute exact 80-byte CP037 FB80 record metrics (no text normalization)."""
    require(raw and raw.endswith(b'\n') and b'\r' not in raw,
            'noncanonical frozen historical source')
    try:
        source_records = raw[:-1].decode('ascii').split('\n')
    except UnicodeError as exc:
        raise Refusal('non-ASCII historical source') from exc
    fnv, checksum, trailing = 0x811C9DC5, 0, 0
    for record in source_records:
        encoded = record.encode('cp037')
        require(len(encoded) <= 80 and all(32 <= ord(c) <= 126 for c in record),
                'historical record exceeds FB80 or has control characters')
        ebcdic = encoded.ljust(80, b'\x40')
        trailing = trailing + 1 if ebcdic == b'\x40' * 80 else 0
        for value in ebcdic:
            fnv = ((fnv ^ value) * 16777619) & 0xFFFFFFFF
            checksum = (checksum + value) & 0xFFFFFFFF
    return dict(count=len(source_records), trail=trailing, fnv=fnv, sum=checksum)


def expected_records(readiness, manifest: dict, dspal: dict) -> dict[str, dict]:
    names = manifest['datasets'][20]['members']
    require(names == list(NAMES), 'rc2 historical source selection/order changed')
    mapping = dspal['datasets']['CAMB_SOURCE']['members']
    require(set(mapping) == set(names) and not dspal['datasets']['CAMB_SOURCE'].get('generated_members'),
            'derived/demoted source is not permitted')
    result = {}
    for name in names:
        raw = readiness.check_frozen_source(mapping[name])
        result[name] = {**fingerprint(raw), 'git_sha256': hashlib.sha256(raw).hexdigest()}
    require(sum(x['count'] for x in result.values()) == 6577,
            'historical source record inventory changed')
    return result


def source_cards() -> list[str]:
    src = ASM.read_text(encoding='ascii')
    lines = src.splitlines()
    require(src.endswith('\n') and len(lines) > 60 and
            all(line.isascii() and len(line) <= 71 and line != '/*' for line in lines),
            'unsafe IFOX source cards')
    require('END   BCSRCV' in lines[-1] and 'MACRF=GM,EODAD=ATEOD' in src,
            'not the approved read-only QSAM reader')
    return lines


def render_jcl(job_cards: list[str], names: tuple[str, ...] = NAMES) -> str:
    require(tuple(names) == NAMES, 'only exact canonical 15-member test permitted')
    cards = list(job_cards) + [
        '//* TA.2: READ-ONLY HISTORICAL SOURCE FB80 RECORD VERIFICATION',
        '//ASM      EXEC PGM=IFOX00,',
        "//             PARM='OBJECT,NODECK,NOLIST,NOXREF',REGION=256K",
        '//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD SYSOUT=*',
        '//SYSPUNCH DD DUMMY',
        '//SYSGO    DD DSN=&&OBJSET,UNIT=SYSDA,SPACE=(80,(300,100)),',
        '//             DISP=(MOD,PASS)',
        '//SYSIN    DD *',
        *source_cards(),
        '/*',
        '//LKED     EXEC PGM=IEWL,PARM=\'NCAL,LIST\',REGION=256K,',
        '//             COND=(0,NE)',
        '//SYSLIN   DD DSN=&&OBJSET,DISP=(OLD,DELETE)',
        '//         DD *',
        ' ENTRY BCSRCV',
        ' NAME BCSRCV(R)',
        '/*',
        '//SYSLMOD  DD DSN=&&GOSET(BCSRCV),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(MOD,PASS)',
        '//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD SYSOUT=*',
    ]
    for index, name in enumerate(names, 1):
        cards.extend([
            f'//GO{index:04d}   EXEC PGM=*.LKED.SYSLMOD,PARM=\'{name}\',',
            '//             COND=(0,NE)',
            f'//QIN      DD DSN={DSN}({name}),DISP=SHR',
            '//QOUT     DD SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSUDUMP DD SYSOUT=*',
        ])
    cards.append('//')
    require(all(x.isascii() and '\t' not in x and len(x) <= 80 for x in cards),
            'overwidth JCL card')
    require(all(len(x) <= 71 for x in cards if x.startswith('//') and not x.startswith('//*')),
            'overwidth JCL statement')
    require(sum(' EXEC PGM=*.LKED.SYSLMOD' in s for s in cards) == 15,
            'wrong GO count')
    return '\n'.join(cards) + '\n'


def parse_report(report: str, expected: dict[str, dict]) -> list[dict]:
    found = REPORT_LINE.findall(report.replace('\r', ''))
    require(len(found) == len(NAMES),
            f'MVS QSAM SYSOUT has {len(found)} record summaries; expected 15')
    require([r[0] for r in found] == list(NAMES),
            'MVS summaries are missing, reordered or duplicated')
    result = []
    for name, c, trail, fnv, summed in found:
        actual = dict(count=int(c, 16), trail=int(trail, 16),
                      fnv=int(fnv, 16), sum=int(summed, 16))
        expected_row = {k: expected[name][k] for k in ('count', 'trail', 'fnv', 'sum')}
        result.append(dict(member=name, observed=actual, expected=expected_row,
                           match=actual == expected_row))
    return result


def summary_steps(summary: str):
    steps = re.findall(r'(?m)^(GO\d{4})\s+\S+\s+RC=0000\s*$', summary)
    require(steps == [f'GO{i:04d}' for i in range(1, 16)],
            f'MVS did not verify all 15 GO steps: {steps!r}')


def run() -> int:
    require(WORK.is_dir() and not WORK.is_symlink(), 'workarea unavailable')
    require(not EVIDENCE.exists() and not EVIDENCE.is_symlink(),
            'private MVS evidence already exists; do not overwrite or resubmit')
    readiness = import_file('ta2_qsam_readiness', HERE / 'rc2-cambsource-readiness.py')
    population = import_file('ta2_qsam_population', HERE / 'rc2-populate-cambsource-once.py')
    readback = import_file('ta2_qsam_readback', HERE / 'rc2-cambsource-record-readback.py')
    core = import_file('ta2_qsam_dspal', ROOT / 'tools/datasets/dspal-core.py')
    manifest, dspal = readiness.source_manifest()
    readiness.verify_sources(manifest, dspal)
    population.check_effective_config(dspal, core.load_config())
    jobs = readback.verify_population(population, readiness, manifest)
    require(tuple(jobs) == (9325, 9326), 'accepted historical MVS jobs differ')
    expected = expected_records(readiness, manifest, dspal)
    require(expected['BLIB']['trail'] == 2 and expected['LIBHDR']['trail'] == 1
            and expected['TRNHDR']['trail'] == 1,
            'frozen trailing-blank source inventory changed')
    cfg = core.load_config()
    card = core.authenticated_job_card(cfg, 'BCSRCRD', 'TA2 CAMB QSAM', redact_password=False)
    deck = render_jcl(card)
    # Reserve evidence before the first JES operation; never blind-retry.
    EVIDENCE.mkdir(mode=0o700)
    report_path = EVIDENCE / 'receipt.json'
    receipt = {'status': 'submitted-or-ambiguous', 'candidate': 'BCPL-0.1.0-rc2',
               'population_jobs': list(jobs), 'expected': expected,
               'assertion': 'full-80-byte-CP037-FNV1a32-sum32-count-and-trailing',
               'raw_data_in_mvs_source_pds_only': True}
    report_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='ascii')
    os.environ['TMPDIR'] = str(WORK)
    tempfile.tempdir = str(WORK)
    cfg['runtime']['completion_timeout'] = 600
    try:
        job, summary = core.submit_and_wait(cfg, deck, max_rc=0)
    except Exception as exc:
        (EVIDENCE / 'submission-error.txt').write_text(str(exc) + '\n', encoding='utf-8')
        raise Refusal('MVS run failed or ambiguous; review preserved evidence before any retry') from exc
    receipt['mvs_verification_job'] = job
    (EVIDENCE / 'job-summary.txt').write_text(summary + '\n', encoding='utf-8')
    try:
        report = core.job_report(job)
        (EVIDENCE / 'mvs-job-report.txt').write_text(report, encoding='utf-8')
        summary_steps(summary)
        rows = parse_report(report, expected)
        receipt['results'] = rows
        receipt['status'] = 'pass' if all(x['match'] for x in rows) else 'mismatch'
    except Exception as exc:
        receipt['status'] = 'report-incomplete'
        receipt['reason'] = str(exc)
        raise
    finally:
        report_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(f'TA.2 RC2 MVS QSAM JOB {job}: '
          f'{sum(x["match"] for x in rows)}/15 full-FB80 fingerprints PASS')
    if receipt['status'] != 'pass':
        for row in rows:
            if not row['match']:
                print(f"  {row['member']}: MVS {row['observed']}; frozen {row['expected']}")
        print(f'Evidence: {EVIDENCE.relative_to(ROOT)}')
        return 2
    print('MVS record count, trailing blanks, CP037 FNV and sum: 15/15 PASS')
    print(f'Evidence: {EVIDENCE.relative_to(ROOT)}')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-mvs', action='store_true', required=True)
    parser.parse_args(argv)
    try:
        return run()
    except (Refusal, OSError, ValueError, KeyError, UnicodeError) as exc:
        print('TA.2 RC2 QSAM VERIFICATION HALTED: ' + str(exc), file=sys.stderr)
        if EVIDENCE.is_dir():
            print('Evidence: ' + str(EVIDENCE.relative_to(ROOT)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
