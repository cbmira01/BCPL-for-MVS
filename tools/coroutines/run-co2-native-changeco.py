#!/usr/bin/env python3
"""CO.2 test-only Cambridge BCPL/IFOX/IEWL/native-GO transfer.

One resident compiler job and one three-IFOX native job. Only temporary
MVS datasets; the accepted BOOT_OBJ library is read-only. Full receipts
remain under workarea; console output is intentionally brief.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co2-native-changeco')
WORK = ROOT / 'workarea/co2-native-changeco'
COMPILER = ROOT / 'tools/bootstrap/compile-mvs'
SUBMIT = ROOT / 'tools/mvs/submit-jcl'
SUMMARY = ROOT / 'tools/mvs/job-summary'
REPORT = ROOT / 'tools/mvs/dump-report-for-job'
CORE = ROOT / 'tools/datasets/dspal-core.py'
MAIN = ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'
JOB_RE = re.compile(r'^JOB\s+(\d+)\s*$', re.M)
OUTPUT_RE = re.compile(
    r'^CO2BCPL\s+(A1|B1|A2|R1|B2|R2|PASS|FALLOC|FINIT|FARG|'
    r'FLOCAL|FVALUE|FSECOND|FTERM)\s*$'
)
EXPECTED = ('A1', 'B1', 'A2', 'R1', 'B2', 'R2', 'PASS')
STEPS = ('ASMA', 'ASMM', 'ASMS', 'LKED', 'GO')


class CandidateError(ValueError):
    """Source, JCL, or MVS acceptance mismatch."""


def checked_cards(text: str, name: str) -> list[str]:
    rows = text.rstrip('\n').splitlines()
    if not rows:
        raise CandidateError(f'{name}: empty source')
    for i, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise CandidateError(f'{name}:{i}: invalid IFOX source card')
        if row == '/*' or row.startswith('//'):
            raise CandidateError(f'{name}:{i}: JCL delimiter in source')
        # IFOX assembler symbols are limited to eight characters.  Check
        # our separately assembled candidate before any JES submission.
        if name == 'BCPLCO' and row and row[0] not in (' ', '*'):
            label = row.split(None, 1)[0]
            if not re.fullmatch(r'[A-Z@$#][A-Z0-9@$#]{0,7}', label):
                raise CandidateError(
                    f'{name}:{i}: invalid IFOX label {label!r}')
    return rows


def compiled_application(source: str) -> list[str]:
    """Bind two test-local globals using the proven regression-26 trailer."""
    source = ''.join(c if ord(c) < 128 else '?' for c in source)
    rows = checked_cards(source, 'CG370')
    def unique(pattern: str, label: str) -> int:
        indexes = [i for i, row in enumerate(rows) if re.fullmatch(pattern, row)]
        if len(indexes) != 1:
            raise CandidateError(f'{label}: expected one, found {len(indexes)}')
        return indexes[0]
    csect = unique(r'\s*CSECT\s*', 'generated CSECT')
    unique(r'\s*EXTRN\s+BCPLMAIN\s*', 'BCPLMAIN EXTRN')
    end = unique(r'\s*END(?:\s+.*)?', 'generated END')
    last = unique(r'L998\s+EQU\s+\*\s*', 'CG370 trailer end')
    fullword = re.compile(r"\s*DC\s+F'(-?\d+)'\s*")
    address = re.compile(r'\s*DC\s+A\(([^()]+)\)\s*')
    candidates = []
    for i in range(last - 1):
        first = fullword.fullmatch(rows[i])
        second = fullword.fullmatch(rows[i + 1])
        if not first or not second or int(second.group(1)) != 0:
            continue
        tail = rows[i + 2:last]
        if len(tail) % 2 == 0 and all(
            fullword.fullmatch(tail[k]) and address.fullmatch(tail[k+1])
            for k in range(0, len(tail), 2)
        ):
            candidates.append(i)
    if len(candidates) != 1:
        raise CandidateError('ambiguous CG370 global export trailer')
    start = candidates[0]
    maximum = int(fullword.fullmatch(rows[start]).group(1))
    pairs = [(int(fullword.fullmatch(rows[i]).group(1)),
              address.fullmatch(rows[i+1]).group(1))
             for i in range(start + 2, last, 2)]
    for slot in (298*4, 299*4):
        if any(item[0] == slot for item in pairs):
            raise CandidateError(f'G!{slot//4} already exported by compiler')
    replacement = [f"         DC F'{max(maximum, 299*4)}'",
                   "         DC F'0'"]
    for number, addr in [*pairs, (298*4, 'CO2INIT'), (299*4, 'CHANGECO')]:
        replacement += [f"         DC F'{number}'", f'         DC A({addr})']
    rows[start:last] = replacement
    # Edit by value: the trailer replacement changes all later indexes.
    csect = unique(r'\s*CSECT\s*', 'generated CSECT')
    end = unique(r'\s*END(?:\s+.*)?', 'generated END')
    rows[csect] = 'CO2APP   CSECT'
    rows.insert(csect+1, '         EXTRN CO2INIT,CHANGECO')
    end = unique(r'\s*END(?:\s+.*)?', 'generated END')
    rows[end] = '         END   CO2APP'
    return checked_cards('\n'.join(rows), 'CO2APP')


def candidate_main(source: str) -> list[str]:
    """Export private stack-limit symbol in *this job*, not BOOT_OBJ."""
    anchor = '         ENTRY STKOVFL\n'
    if source.count(anchor) != 1:
        raise CandidateError('BCPLMAIN STKOVFL entry shape changed')
    if 'STKLIM   DC    F\'0\'' not in source:
        raise CandidateError('BCPLMAIN STKLIM layout changed')
    return checked_cards(source.replace(anchor,
                         '         ENTRY STKOVFL,STKLIM\n', 1), 'CO2MAIN')


def asm_step(name: str, member: str, rows: list[str]) -> list[str]:
    return [
        f'//{name:<8} EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        '//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD SYSOUT=*',
        '//SYSPUNCH DD DUMMY',
        f'//SYSGO    DD DSN=&&{member},UNIT=SYSDA,',
        '//             SPACE=(80,(300,100)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSIN    DD *', *rows, '/*'
    ]


def build_deck(generated: str, main: str, bridge: str,
               jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not jobcard[0].startswith('//CO2BGO '):
        raise CandidateError('authenticated CO2BGO job card required')
    if not re.fullmatch(r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+', obj_dsn):
        raise CandidateError('invalid BOOT_OBJ DSN')
    app = compiled_application(generated)
    runtime = candidate_main(main)
    sw = checked_cards(bridge, 'BCPLCO')
    if 'BCPLCO   CSECT' not in sw or '         ENTRY CO2INIT,CHANGECO' not in sw:
        raise CandidateError('BCPLCO entry source shape changed')
    cards = [*jobcard, '//* CO.2 ISOLATED CANDIDATE. BOOT_OBJ READ ONLY.']
    cards += asm_step('ASMA', 'CO2APOBJ', app)
    cards += asm_step('ASMM', 'CO2MNOBJ', runtime)
    cards += asm_step('ASMS', 'CO2SWOBJ', sw)
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE)",
        f'//OBJ      DD DSN={obj_dsn},DISP=SHR',
        '//SYSLIN   DD DSN=&&CO2APOBJ,DISP=(OLD,DELETE)',
        '//         DD DSN=&&CO2MNOBJ,DISP=(OLD,DELETE)',
        '//         DD DSN=&&CO2SWOBJ,DISP=(OLD,DELETE)',
        '//         DD *',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' INCLUDE OBJ(BCPLRGS)',
        ' INCLUDE OBJ(BCPLREG)',
        ' INCLUDE OBJ(BLIB)',
        ' ENTRY CO2APP',
        ' NAME CO2BGO(R)',
        '/*',
        '//SYSLMOD  DD DSN=&&CO2LOAD(CO2BGO),UNIT=SYSDA,',
        '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
        '//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))',
        '//SYSPRINT DD SYSOUT=*',
        '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
        '//             TIME=(,2),COND=(0,NE,LKED)',
        '//SYSPRINT DD SYSOUT=*,',
        '//             DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)',
        '//SYSUDUMP DD SYSOUT=*',
        '//',
    ]
    for n, row in enumerate(cards, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row:
            raise CandidateError(f'bad JCL/IFOX card {n}: {row!r}')
    if cards.count('/*') != 4 or any('DISP=(NEW,CATLG)' in row for row in cards):
        raise CandidateError('unexpected JCL terminator or cataloged output')
    return '\n'.join(cards) + '\n'


def observed_records(report: str) -> list[str]:
    """Accept BCPL markers only if well formed; ignore assembler literals.

    A corrupted or unknown line beginning CO2BCPL is a failure, not
    background JES text that can be silently discarded.
    """
    records: list[str] = []
    for number, raw in enumerate(report.replace('\f', '').splitlines(), 1):
        line = raw.strip()
        if not line.startswith('CO2BCPL'):
            continue
        match = OUTPUT_RE.fullmatch(line)
        if match is None:
            raise CandidateError(
                f'malformed native BCPL record at report line {number}: '
                f'{line[:71]!r}')
        records.append(match.group(1))
    return records


def assess(summary: str, report: str, job: str) -> dict[str, object]:
    if not re.search(rf'^JOB\s+{re.escape(job)}\s+CO2BGO\s*$', summary, re.M):
        raise CandidateError('wrong completed GO job identity')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise CandidateError('native job did not complete successfully at RC=0')
    steps: dict[str,int] = {}
    for line in summary.splitlines():
        m = re.fullmatch(r'\s*(ASMA|ASMM|ASMS|LKED|GO)\s+.*?RC=(\d{4})\s*', line)
        if m:
            if m.group(1) in steps:
                raise CandidateError('duplicate native JES step')
            steps[m.group(1)] = int(m.group(2))
    if set(steps) != set(STEPS) or any(value != 0 for value in steps.values()):
        raise CandidateError(f'missing or nonzero native JES steps: {steps}')
    actual = observed_records(report)
    if actual != list(EXPECTED):
        raise CandidateError(f'native BCPL records differ: {actual}')
    return {'steps':steps, 'bcpl_records':actual}


def shell(cmd: list[str], *, timeout: int=240) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True,
                          check=False, timeout=timeout)


def config_and_object() -> tuple[list[str],str]:
    spec = importlib.util.spec_from_file_location('co1_dspal',CORE)
    if spec is None or spec.loader is None:
        raise CandidateError('missing dspal configuration loader')
    core=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    cfg=core.load_config()
    obj=cfg['datasets']['BOOT_OBJ']
    if (obj.get('dsorg')!='PO' or obj.get('recfm')!='FB' or
        int(obj.get('lrecl',0))!=80 or obj.get('content_type')!='object'):
        raise CandidateError('BOOT_OBJ must be a binary FB80 object PDS')
    return (core.authenticated_job_card(cfg,'CO2BGO','CO2 BCPL NATIVE',
                                        redact_password=False),
            core.full_dsn(cfg,obj))


def execute() -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-',dir=WORK))
    result:dict[str,object]={'status':'FAIL','evidence_class':'MVS-pending',
        'march':'CO.2','production_abi_approved':False,
        'installed_mvs_objects_modified':False,'co2_accepted':False}
    try:
        source=FIXTURE/'source.bcpl'
        parm=FIXTURE/'cambridge-parm.txt'
        bridge=ROOT/'bootstrap-toolchain/asm/bcplco.asm'
        if parm.read_text('ascii').splitlines()!=['/CN'+'/'*77]:
            raise CandidateError('candidate must compile under /CN')
        for filename in (source,parm,bridge,MAIN):
            result[filename.name+'_sha256']=hashlib.sha256(filename.read_bytes()).hexdigest()
        head=shell(['git','rev-parse','HEAD'],timeout=15)
        result['git_head']=head.stdout.strip() if head.returncode==0 else 'unknown'
        listing=folder/'generated.s370.asm'
        cmd=[sys.executable,'-B',str(COMPILER),str(source),
             '--job-name','CO2BCMP','--cambridge-parm',str(parm),
             '--output',str(listing)]
        compiler=shell(cmd,timeout=240)
        (folder/'compiler.log').write_text(compiler.stdout+compiler.stderr)
        result['compiler_driver_rc']=compiler.returncode
        comp_jobs=JOB_RE.findall(compiler.stdout)
        if compiler.returncode or len(comp_jobs)!=1 or not listing.is_file():
            raise CandidateError(f'compiler RC={compiler.returncode}, jobs={len(comp_jobs)}')
        result['compiler_job_id']=comp_jobs[0]
        result['generated_sha256']=hashlib.sha256(listing.read_bytes()).hexdigest()
        jobcard,dsn=config_and_object()
        deck=build_deck(listing.read_text('latin-1'),
                        MAIN.read_text('ascii'),bridge.read_text('ascii'),jobcard,dsn)
        (folder/'candidate.jcl').write_text(deck,'ascii')
        run=shell([str(SUBMIT),'--cursor-file',str(folder/'printer.cursor'),
                   str(folder/'candidate.jcl')],timeout=140)
        (folder/'submission.log').write_text(run.stdout+run.stderr)
        result['submit_rc']=run.returncode
        jobs=JOB_RE.findall(run.stdout)
        if run.returncode or len(jobs)!=1:
            raise CandidateError(f'GO submission RC={run.returncode}, jobs={len(jobs)}')
        job=jobs[0]
        result['native_job_id']=job
        deadline=time.monotonic()+200
        summary=''
        while time.monotonic()<deadline:
            check=shell([str(SUMMARY),job,'--cursor-file',
                         str(folder/'printer.cursor'),'--max-rc','0'],timeout=25)
            summary=check.stdout+check.stderr
            (folder/'job-summary.log').write_text(summary)
            if check.returncode in (0,1):
                result['job_summary_rc']=check.returncode
                break
            time.sleep(2)
        else:
            raise CandidateError('timeout awaiting complete native JES summary')
        report=shell([str(REPORT),job,'--cursor-file',
                      str(folder/'printer.cursor')],timeout=45)
        (folder/'job-report.log').write_text(report.stdout+report.stderr)
        result['job_report_rc']=report.returncode
        if report.returncode:
            raise CandidateError('unable to recover native JES report')
        result['observed_native_records'] = observed_records(report.stdout)
        result.update(assess(summary,report.stdout,job))
        result['status']='PASS'
        result['evidence_class']='OWNER-REPORTED NATIVE-MVS-TESTED'
        print(f'CO.2 BCPL PASS: compiler JOB {comp_jobs[0]}, GO JOB {job}; '
              'IFOX 3, IEWL 1, GO 1; ' + ' '.join(EXPECTED))
        return 0
    except (OSError,ValueError,subprocess.TimeoutExpired,UnicodeError) as exc:
        result['reason']=str(exc)
        print(f'CO.2 BCPL FAIL: {exc}',file=sys.stderr)
        return 1
    finally:
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(f'CO.2 BCPL evidence: {folder.relative_to(ROOT)}')


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='submit two candidate-only MVS jobs')
    args=parser.parse_args()
    if not args.run:
        parser.error('MVS execution requires explicit --run')
    return execute()


if __name__=='__main__':
    raise SystemExit(main())
