#!/usr/bin/env python3
"""Candidate-only CO.1 IFOX / IEWL / native GO context-transfer smoke.

Creates one inlined two-CSECT assembly job using temporary MVS datasets.
Saves full local receipts under workarea; never writes installed MVS PDS.
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
import time

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / 'packaging/milestones/coroutines/candidates/co1-native-switch'
SWITCH = CANDIDATE / 'co1switch.asm'
DRIVER = CANDIDATE / 'co1native.asm'
WORK = ROOT / 'workarea/co1-native-switch'
SUBMIT = ROOT / 'tools/mvs/submit-jcl'
SUMMARY = ROOT / 'tools/mvs/job-summary'
REPORT = ROOT / 'tools/mvs/dump-report-for-job'
JOB_RE = re.compile(r'^JOB\s+(\d+)\s*$', re.M)
STAGE = re.compile(r'^CO1STAGE\s+(A1|B1|A2|B2|PASS|FAIL)\s*$')
STEPS = ('ASMSW', 'ASMTST', 'LKED', 'GO')
EXPECTED = ('A1', 'B1', 'A2', 'B2', 'PASS')


class SmokeError(ValueError):
    """Failed source, JCL or real MVS acceptance criterion."""


def checked_source(path: Path) -> str:
    source = path.read_text(encoding='ascii')
    if not source.strip():
        raise SmokeError(f'empty assembler file: {path.name}')
    for n, line in enumerate(source.splitlines(), 1):
        if len(line) > 71 or line == '/*' or '\t' in line:
            raise SmokeError(f'invalid assembler card in {path.name}:{n}')
    return source.rstrip('\n') + '\n'


def step(name: str, source: str, obj: str) -> str:
    return (f'//{name:<8} EXEC PGM=IFOX00,\n'
            "//             PARM='OBJECT,NODECK,LIST,XREF(SHORT)',REGION=256K\n"
            '//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR\n'
            '//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))\n'
            '//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))\n'
            '//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))\n'
            '//SYSPRINT DD SYSOUT=*\n'
            '//SYSPUNCH DD DUMMY\n'
            f'//SYSGO    DD DSN=&&{obj},UNIT=SYSDA,SPACE=(80,(300,100)),\n'
            '//             DISP=(MOD,PASS)\n'
            '//SYSIN    DD *\n'
            + source + '/*\n//*\n')


def build_deck(source_switch: str, source_driver: str) -> str:
    if any(line == '/*' for text in (source_switch, source_driver)
           for line in text.splitlines()):
        raise SmokeError('inlined assembler contains JCL SYSIN terminators')
    deck = ("//CO1NAT   JOB (BCPL),'CO1 NATIVE SMOKE',CLASS=A,MSGCLASS=A,\n"
            '//             MSGLEVEL=(1,1)\n'
            '//* Candidate-only: no permanent MVS object/data-set writes.\n'
            + step('ASMSW', source_switch, 'CO1SWO')
            + step('ASMTST', source_driver, 'CO1TSTO')
            + "//LKED     EXEC PGM=IEWL,PARM='LET,NCAL,MAP',REGION=256K,\n"
            + '//             COND=((4,LT,ASMSW),(4,LT,ASMTST))\n'
            + '//SYSLIN   DD DSN=&&CO1SWO,DISP=(OLD,DELETE)\n'
            + '//         DD DSN=&&CO1TSTO,DISP=(OLD,DELETE)\n'
            + '//         DD *\n'
            + '  ENTRY CO1ROOT\n'
            + '  NAME CO1NAT(R)\n'
            + '/*\n'
            + '//SYSLMOD  DD DSN=&&CO1LOAD(CO1NAT),UNIT=SYSDA,\n'
            + '//             SPACE=(1024,(50,20,1)),DISP=(MOD,PASS)\n'
            + '//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))\n'
            + '//SYSPRINT DD SYSOUT=*\n'
            + '//*\n'
            + '//GO       EXEC PGM=*.LKED.SYSLMOD,\n'
            + '//             COND=((4,LT,ASMSW),(4,LT,ASMTST),\n'
            + '//             (4,LT,LKED))\n'
            + '//SYSPRINT DD SYSOUT=*,\n'
            + '//             DCB=(RECFM=F,LRECL=80,BLKSIZE=80)\n'
            + '//SYSUDUMP DD SYSOUT=*\n'
            + '//\n')
    if any(len(line) > 71 for line in deck.splitlines() if line.startswith('//')):
        raise SmokeError('JCL card exceeds column 71')
    if deck.count('//SYSIN    DD *\n') != 2 or deck.count('\n/*\n') != 3:
        raise SmokeError('incorrect inlined source/data terminators')
    return deck


def assess(summary: str, report: str, job: str) -> dict[str, object]:
    if not re.search(rf'^JOB\s+{re.escape(job)}\s+CO1NAT\s*$', summary, re.M):
        raise SmokeError('job-summary did not identify this CO1NAT job')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise SmokeError('JES job-summary did not establish zero-RC success')
    step_rcs = {}
    for line in summary.splitlines():
        m = re.match(r'^\s*(ASMSW|ASMTST|LKED|GO)\s+.*?\s+RC=(\d{4})\s*$', line)
        if m:
            if m.group(1) in step_rcs:
                raise SmokeError('duplicate JES step in job-summary')
            step_rcs[m.group(1)] = int(m.group(2))
    if set(step_rcs) != set(STEPS) or any(step_rcs[k] != 0 for k in STEPS):
        raise SmokeError(f'missing or nonzero IFOX/IEWL/GO steps: {step_rcs}')
    stages = [m.group(1) for line in report.replace('\f', '').splitlines()
              if (m := STAGE.fullmatch(line.strip()))]
    if stages != list(EXPECTED):
        raise SmokeError(f'native GO records differ: {stages}')
    return {'steps': step_rcs, 'go_records': stages}


def shell(cmd: list[str], *, timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True,
                          check=False, timeout=timeout)


def execute() -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    receipt = path / 'result.json'
    result: dict[str, object] = {'status': 'FAIL', 'kind': 'candidate-only native IFOX/IEWL/GO',
                                 'installed_mvs_object': False, 'co2_accepted': False}
    try:
        sw = checked_source(SWITCH)
        driver = checked_source(DRIVER)
        if 'STM   0,15,0(2)' not in sw or 'LM    0,15,0(1)' not in sw:
            raise SmokeError('CO1SW context-save/restore source contract changed')
        if 'CO1ROOT  CSECT' not in driver or 'END   CO1ROOT' not in driver:
            raise SmokeError('native test control section changed')
        (path / 'candidate.jcl').write_text(build_deck(sw, driver), encoding='ascii')
        result['sources_sha256'] = {name: hashlib.sha256(content.encode('ascii')).hexdigest()
                                    for name, content in [('co1switch.asm', sw), ('co1native.asm', driver)]}
        git = shell(['git', 'rev-parse', 'HEAD'], timeout=15)
        result['git_head'] = git.stdout.strip() if git.returncode == 0 else 'unknown'
        submission = shell([str(SUBMIT), '--cursor-file', str(path / 'printer.cursor'),
                            str(path / 'candidate.jcl')], timeout=140)
        (path / 'submission.log').write_text(submission.stdout + submission.stderr)
        result['submit_rc'] = submission.returncode
        ids = JOB_RE.findall(submission.stdout)
        if submission.returncode or len(ids) != 1:
            raise SmokeError(f'JES submission RC={submission.returncode}, jobs={len(ids)}')
        job = ids[0]
        result['jes_job_id'] = job
        summary = ''
        deadline = time.monotonic() + 200
        while time.monotonic() < deadline:
            s = shell([str(SUMMARY), job, '--cursor-file', str(path / 'printer.cursor'),
                       '--max-rc', '0'], timeout=25)
            summary = s.stdout + s.stderr
            (path / 'job-summary.log').write_text(summary)
            # RC=2 means not yet found/incomplete; RC=1 means completed FAIL.
            if s.returncode in (0, 1):
                result['job_summary_rc'] = s.returncode
                break
            time.sleep(2)
        else:
            raise SmokeError('timed out waiting for complete JES job summary')
        report = shell([str(REPORT), job, '--cursor-file', str(path / 'printer.cursor')],
                       timeout=45)
        (path / 'job-report.log').write_text(report.stdout + report.stderr)
        result['job_report_rc'] = report.returncode
        if report.returncode:
            raise SmokeError('cannot recover full completed JES report')
        result.update(assess(summary, report.stdout, job))
        result['status'] = 'PASS'
        print(f"CO.1 NATIVE PASS: JOB {job}, IFOX 2, IEWL 1, GO 1; "
              'A1 B1 A2 B2 PASS')
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired, UnicodeError) as exc:
        result['reason'] = str(exc)
        print(f'CO.1 NATIVE FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        receipt.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(f'CO.1 NATIVE evidence: {path.relative_to(ROOT)}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='submit one candidate-only MVS job')
    args = parser.parse_args()
    if not args.run:
        parser.error('MVS execution requires explicit --run')
    return execute()


if __name__ == '__main__':
    raise SystemExit(main())
