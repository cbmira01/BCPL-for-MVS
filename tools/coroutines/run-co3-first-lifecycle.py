#!/usr/bin/env python3
"""CO.3: compile two BCPL units independently, then IFOX/IEWL/native GO.

Candidate only; source-based export aliases; no installed MVS object writes.
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
           / 'co3-first-lifecycle')
WORK = ROOT / 'workarea/co3-first-lifecycle'
COMPILER = ROOT / 'tools/bootstrap/compile-mvs'
SUBMIT = ROOT / 'tools/mvs/submit-jcl'
SUMMARY = ROOT / 'tools/mvs/job-summary'
REPORT = ROOT / 'tools/mvs/dump-report-for-job'
MAIN = ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'
BRIDGE = ROOT / 'bootstrap-toolchain/asm/bcplco.asm'
CO2_RUNNER = ROOT / 'tools/coroutines/run-co2-native-changeco.py'
JOB_RE = re.compile(r'^JOB\s+(\d+)\s*$', re.M)
EXPECTED = ('MADE', 'W1', 'R1', 'W2', 'R2', 'W3', 'R3', 'PASS')
PARENT_EXPECTED = ('MADE', 'A1', 'B1', 'A2', 'B2', 'R1',
                   'A3', 'R2', 'B3', 'R3', 'A4', 'R4', 'PASS')
STEPS = ('ASMA', 'ASML', 'ASMM', 'ASMS', 'LKED', 'GO')
# The entire namespace is private to this candidate application.
EXPORTS = ((289, 'C3INIT'), (290, 'C3CREATE'),
           (292, 'C3CALL'), (293, 'C3WAIT'), (294, 'C3RESUME'))

spec = importlib.util.spec_from_file_location('co3_co2_driver', CO2_RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError('CO.2 candidate runner unavailable')
co2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co2)

class CandidateError(ValueError):
    pass


def unique(rows: list[str], pattern: str, description: str) -> int:
    found = [i for i, row in enumerate(rows) if re.fullmatch(pattern, row)]
    if len(found) != 1:
        raise CandidateError(f'{description}: expected once, found {len(found)}')
    return found[0]


def trailer(rows: list[str]) -> tuple[int, int, int, list[tuple[int, str]]]:
    """Require a single, wholly well-formed CG370 global export trailer."""
    last = unique(rows, r'L998\s+EQU\s+\*\s*', 'CG370 L998')
    full = re.compile(r"\s*DC\s+F'(-?\d+)'\s*")
    addr = re.compile(r'\s*DC\s+A\(([^()]+)\)\s*')
    candidates: list[int] = []
    for i in range(last - 1):
        a, b = full.fullmatch(rows[i]), full.fullmatch(rows[i+1])
        if not a or not b or int(b.group(1)) != 0:
            continue
        rest = rows[i+2:last]
        if len(rest) % 2 == 0 and all(
            full.fullmatch(rest[k]) and addr.fullmatch(rest[k+1])
            for k in range(0, len(rest), 2)
        ):
            candidates.append(i)
    if len(candidates) != 1:
        raise CandidateError('ambiguous CG370 global export trailer')
    start = candidates[0]
    maximum = int(full.fullmatch(rows[start]).group(1))
    pairs = [(int(full.fullmatch(rows[i]).group(1)),
              addr.fullmatch(rows[i+1]).group(1))
             for i in range(start+2, last, 2)]
    if len({number for number, _ in pairs}) != len(pairs):
        raise CandidateError('duplicate compiled global exports')
    return start, last, maximum, pairs


def generated_library(source: str) -> list[str]:
    """Export symbolic aliases for compiler-generated BCPL procedures.

    The library remains an independent IFOX CSECT and object module.
    Its own trailer is retained as compiler output, not folded into the app.
    """
    rows = co2.checked_cards(''.join(x if ord(x) < 128 else '?'
                                  for x in source), 'CO3LIB')
    start, last, maximum, pairs = trailer(rows)
    required = {number*4 for number, _ in EXPORTS}
    if {number for number, _ in pairs} != required:
        raise CandidateError(f'unexpected CO.3 library exports: {pairs}')
    # CG370 GENDCA emits "DC A(0+L<n>)" for exported entry points.
    # Retain only a zero addend: the IFOX ENTRY alias must designate the
    # exact relocatable procedure entry, never an offset into its body.
    addresses: dict[int, str] = {}
    for number, _ in EXPORTS:
        expression = dict(pairs)[number*4]
        match = re.fullmatch(r'(?:0\+)?(L\d{1,5})', expression)
        if match is None:
            raise CandidateError(
                f'unsupported CG370 procedure address: {expression!r}')
        label = match.group(1)
        if sum(bool(re.match(rf'^{re.escape(label)}\s+EQU\s+', row))
               for row in rows[:start]) != 1:
            raise CandidateError(f'CG370 procedure label missing: {label}')
        addresses[number*4] = label
    csect = unique(rows, r'\s*CSECT\s*', 'CG370 library CSECT')
    unique(rows, r'\s*EXTRN\s+BCPLMAIN\s*', 'CG370 BCPLMAIN external')
    end = unique(rows, r'\s*END(?:\s+.*)?', 'CG370 library END')
    rows[csect] = 'CO3LIB   CSECT'
    rows.insert(csect+1, '         ENTRY C3INIT,C3CREATE,C3CALL,C3WAIT,C3RESUME')
    end = unique(rows, r'\s*END(?:\s+.*)?', 'CG370 library END')
    aliases = [f'{symbol:<8} EQU   {addresses[slot*4]}'
               for slot, symbol in EXPORTS]
    rows[end:end+1] = [*aliases, '         END   CO3LIB']
    return co2.checked_cards('\n'.join(rows), 'CO3LIB')


def generated_application(source: str) -> list[str]:
    """Use CO.2's proven test-local native bindings, add BCPL aliases."""
    rows = co2.compiled_application(source)
    start, last, maximum, pairs = trailer(rows)
    occupied = {number for number, _ in pairs}
    extras = [(slot*4, symbol) for slot, symbol in EXPORTS]
    if any(number in occupied for number, _ in extras):
        raise CandidateError('application overwrites a CO.3 library global')
    replacement = [f"         DC F'{max(maximum, 299*4)}'",
                   "         DC F'0'"]
    for number, symbol in [*pairs, *extras]:
        replacement += [f"         DC F'{number}'", f'         DC A({symbol})']
    rows[start:last] = replacement
    csect = unique(rows, r'CO2APP\s+CSECT\s*', 'CO2 application CSECT')
    rows[csect] = 'CO3APP   CSECT'
    native = unique(rows, r'\s*EXTRN\s+CO2INIT,CHANGECO\s*',
                    'CO.2 machine external')
    rows.insert(native+1, '         EXTRN C3INIT,C3CREATE,C3CALL,C3WAIT,C3RESUME')
    end = unique(rows, r'\s*END\s+CO2APP\s*', 'CO2 application END')
    rows[end] = '         END   CO3APP'
    return co2.checked_cards('\n'.join(rows), 'CO3APP')


def build_deck(application: str, library: str, main: str, bridge: str,
               jobcard: list[str], obj_dsn: str) -> str:
    if not jobcard or not jobcard[0].startswith('//CO3BGO '):
        raise CandidateError('authenticated CO3BGO job card required')
    if not re.fullmatch(r'[A-Z@$#][A-Z0-9@$#]{0,7}(?:\.[A-Z@$#][A-Z0-9@$#]{0,7})+', obj_dsn):
        raise CandidateError('invalid BOOT_OBJ DSN')
    app = generated_application(application)
    lib = generated_library(library)
    runtime = co2.candidate_main(main)
    sw = co2.checked_cards(bridge, 'BCPLCO')
    if 'BCPLCO   CSECT' not in sw:
        raise CandidateError('BCPLCO CSECT missing')
    cards = [*jobcard, '//* CO.3 PRIVATE CANDIDATE; INSTALLED BOOT_OBJ READ ONLY.']
    cards += co2.asm_step('ASMA', 'CO3APOBJ', app)
    cards += co2.asm_step('ASML', 'CO3LOBJ', lib)
    cards += co2.asm_step('ASMM', 'CO3MNOBJ', runtime)
    cards += co2.asm_step('ASMS', 'CO3SWOBJ', sw)
    cards += [
        '//LKED     EXEC PGM=IEWL,REGION=256K,',
        "//             PARM='NCAL,LIST,XREF,MAP',COND=(0,NE)",
        f'//OBJ      DD DSN={obj_dsn},DISP=SHR',
        '//SYSLIN   DD DSN=&&CO3APOBJ,DISP=(OLD,DELETE)',
        '//         DD DSN=&&CO3LOBJ,DISP=(OLD,DELETE)',
        '//         DD DSN=&&CO3MNOBJ,DISP=(OLD,DELETE)',
        '//         DD DSN=&&CO3SWOBJ,DISP=(OLD,DELETE)',
        '//         DD *',
        ' INCLUDE OBJ(BCPLIO)',
        ' INCLUDE OBJ(BCPLMEM)',
        ' INCLUDE OBJ(BCPLBYTE)',
        ' INCLUDE OBJ(BCPLAPT)',
        ' INCLUDE OBJ(BCPLRGS)',
        ' INCLUDE OBJ(BCPLREG)',
        ' INCLUDE OBJ(BLIB)',
        ' ENTRY CO3APP',
        ' NAME CO3BGO(R)',
        '/*',
        '//SYSLMOD  DD DSN=&&CO3LOAD(CO3BGO),UNIT=SYSDA,',
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
    for i, line in enumerate(cards, 1):
        if not line.isascii() or len(line) > 71 or '\t' in line:
            raise CandidateError(f'bad JCL/IFOX card {i}: {line!r}')
    if cards.count('/*') != 5 or 'DISP=(NEW,CATLG)' in '\n'.join(cards):
        raise CandidateError('unacceptable JCL terminators or permanent output')
    return '\n'.join(cards)+'\n'


def observed_records(report: str) -> list[str]:
    found: list[str] = []
    for i, raw in enumerate(report.replace('\f', '').splitlines(), 1):
        row = raw.strip()
        if not row.startswith('CO3BCPL'):
            continue
        match = re.fullmatch(r'CO3BCPL\s+([A-Z0-9]+)', row)
        if match is None:
            raise CandidateError(f'malformed CO3 record at JES line {i}')
        found.append(match.group(1))
    return found


def assess(summary: str, report: str, job: str,
           expected: tuple[str, ...] = EXPECTED) -> dict[str, object]:
    if not re.search(rf'^JOB\s+{re.escape(job)}\s+CO3BGO\s*$', summary, re.M):
        raise CandidateError('wrong GO job identity')
    if 'JOB RESULT: SUCCESS' not in summary or 'HIGHEST RC: 0000' not in summary:
        raise CandidateError('native JES summary unsuccessful or highest RC nonzero')
    steps: dict[str,int] = {}
    for line in summary.splitlines():
        m = re.fullmatch(r'\s*(ASMA|ASML|ASMM|ASMS|LKED|GO)\s+.*?RC=(\d{4})\s*', line)
        if m:
            if m.group(1) in steps:
                raise CandidateError('duplicate JES step')
            steps[m.group(1)] = int(m.group(2))
    if set(steps) != set(STEPS) or any(value != 0 for value in steps.values()):
        raise CandidateError(f'missing/nonzero JES step(s): {steps}')
    records = observed_records(report)
    if records != list(expected):
        raise CandidateError(f'wrong ordered BCPL records: {records}')
    return {'steps': steps, 'bcpl_records': records}


def config_and_object() -> tuple[list[str], str]:
    core_path = ROOT/'tools/datasets/dspal-core.py'
    loader = importlib.util.spec_from_file_location('co3_dspal', core_path)
    if loader is None or loader.loader is None:
        raise CandidateError('dspal configuration loader unavailable')
    core = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(core)
    cfg = core.load_config()
    obj = cfg['datasets']['BOOT_OBJ']
    if (obj.get('dsorg') != 'PO' or obj.get('recfm') != 'FB' or
        int(obj.get('lrecl', 0)) != 80 or
        obj.get('content_type') != 'object'):
        raise CandidateError('BOOT_OBJ must be a binary FB80 object PDS')
    return (core.authenticated_job_card(cfg, 'CO3BGO',
                                        'CO3 NATIVE LIB',
                                        redact_password=False),
            core.full_dsn(cfg, obj))


def require_mvs_tools() -> None:
    """Reject missing launch/evidence tools before submitting compiler jobs."""
    if SUBMIT != co2.SUBMIT:
        raise CandidateError('CO.3 submit tool differs from CO.2 baseline')
    for path in (SUBMIT, SUMMARY, REPORT):
        if not path.is_file() or not os.access(path, os.X_OK):
            raise CandidateError(f'MVS tool missing or not executable: {path}')


def execute(scenario: str = 'first') -> int:
    os.umask(0o077)
    WORK.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(
        prefix=f'{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-', dir=WORK))
    if scenario not in ('first', 'parent-chain'):
        raise CandidateError(f'unknown CO.3 scenario: {scenario}')
    result: dict[str, object] = {
        'status': 'FAIL', 'march': 'CO.3', 'scenario': scenario,
        'evidence_class': 'MVS-pending',
        'installed_mvs_objects_modified': False,
        'public_global_allocation': False,
    }
    try:
        require_mvs_tools()
        parm = FIXTURE/'cambridge-parm.txt'
        if parm.read_text('ascii').splitlines() != ['/CN'+'/'*77]:
            raise CandidateError('checked Cambridge /CN required')
        app = 'parent-chain.bcpl' if scenario == 'parent-chain' else 'source.bcpl'
        sources = (FIXTURE/app, FIXTURE/'library.bcpl')
        for item in (*sources, parm, BRIDGE, MAIN):
            result[str(item.relative_to(ROOT))+'_sha256'] = hashlib.sha256(
                item.read_bytes()).hexdigest()
        head = co2.shell(['git', 'rev-parse', 'HEAD'], timeout=15)
        result['git_head'] = head.stdout.strip() if head.returncode == 0 else 'unknown'
        generated = []
        for source, job in zip(sources, ('CO3ACMP', 'CO3LCMP')):
            listing = folder/f'{source.stem}.s370.asm'
            run = co2.shell([sys.executable, '-B', str(COMPILER), str(source),
                             '--job-name', job, '--cambridge-parm', str(parm),
                             '--output', str(listing)], timeout=240)
            (folder/f'{job}.log').write_text(run.stdout+run.stderr)
            jobs = JOB_RE.findall(run.stdout)
            if run.returncode or len(jobs) != 1 or not listing.is_file():
                raise CandidateError(f'{job} compiler RC={run.returncode}, jobs={jobs}')
            result[job+'_job'] = jobs[0]
            result[job+'_sha256'] = hashlib.sha256(listing.read_bytes()).hexdigest()
            generated.append(listing.read_text('latin-1'))
        jobcard, dsn = config_and_object()
        deck = build_deck(generated[0], generated[1],
                          MAIN.read_text('ascii'), BRIDGE.read_text('ascii'),
                          jobcard, dsn)
        (folder/'candidate.jcl').write_text(deck, encoding='ascii')
        launch = co2.shell([str(SUBMIT), '--cursor-file', str(folder/'printer.cursor'),
                            str(folder/'candidate.jcl')], timeout=140)
        (folder/'submission.log').write_text(launch.stdout+launch.stderr)
        jobs = JOB_RE.findall(launch.stdout)
        if launch.returncode or len(jobs) != 1:
            raise CandidateError(f'GO submit RC={launch.returncode}, jobs={jobs}')
        job = jobs[0]
        result['native_job'] = job
        deadline = time.monotonic()+200
        summary = ''
        while time.monotonic() < deadline:
            chk = co2.shell([str(SUMMARY), job, '--cursor-file',
                             str(folder/'printer.cursor'), '--max-rc', '0'],
                            timeout=25)
            summary = chk.stdout+chk.stderr
            (folder/'job-summary.log').write_text(summary)
            if chk.returncode in (0, 1):
                result['job_summary_rc'] = chk.returncode
                break
            time.sleep(2)
        else:
            raise CandidateError('incomplete native JES summary (timeout)')
        report = co2.shell([str(REPORT), job, '--cursor-file',
                            str(folder/'printer.cursor')], timeout=45)
        (folder/'job-report.log').write_text(report.stdout+report.stderr)
        if report.returncode:
            raise CandidateError('native JES report retrieval failure')
        expected = PARENT_EXPECTED if scenario == 'parent-chain' else EXPECTED
        result.update(assess(summary, report.stdout, job, expected))
        result['status'] = 'PASS'
        result['evidence_class'] = 'OWNER-REPORTED NATIVE-MVS-TESTED'
        print(f'CO.3 first lifecycle PASS: compiler JOBS '
              f'{result["CO3ACMP_job"]}/{result["CO3LCMP_job"]}, '
              f'native JOB {job}; IFOX 4, IEWL 1, GO 1')
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired, UnicodeError) as exc:
        result['reason'] = str(exc)
        print(f'CO.3 first lifecycle FAIL: {exc}', file=sys.stderr)
        return 1
    finally:
        (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')
        print(f'CO.3 first lifecycle evidence: {folder.relative_to(ROOT)}')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenario', choices=('first', 'parent-chain'),
                   default='first', help='select a CO.3 native oracle')
    p.add_argument('--run', action='store_true',
                   help='submit two BCPL compiler jobs and one native job')
    args = p.parse_args()
    if not args.run:
        p.error('MVS execution requires explicit --run')
    return execute(args.scenario)


if __name__ == '__main__':
    raise SystemExit(main())

