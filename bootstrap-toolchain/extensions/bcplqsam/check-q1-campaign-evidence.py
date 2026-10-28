#!/usr/bin/env python3
"""Review preserved Q.1 campaign JES evidence; never submit/accept on behalf of owner.

Read native full JES report and tools/mvs/job-summary text as separate inputs.
A finalizer WTO may live in the TK5 console rather than the printer report;
when supplied, require a bounded, uniquely matched IEF403I/IEF404I job window.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
CASES = {
    'finish': ('Q16FIN', {'ASMWR','LKWR','ASMA','ASMN','ASMR',
                        'ASMQ','ASMG','LKED','WGO','GO'}, 0,
               ['BCPLQSAM Q1 16 FINISH PASS',
                'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS']),
    'stop': ('Q16STP', {'ASMWR','LKWR','ASMA','ASMN','ASMR',
                      'ASMQ','ASMG','LKED','WGO','GO'}, 8,
             ['BCPLQSAM Q1 16 STOP PASS',
              'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS']),
    'negative': ('Q1NEG', {'ASMA','ASMN','ASMR','ASMQ','ASMG','LKED','GO'},
                 0, ['BCPLQSAM Q1 NEGATIVE PASS']),
    'output': ('Q1OUT', {'ASMA','ASMN','ASMR','ASMQ','ASMG','LKED','GO'},
               0, ['BCPLQSAM Q1 OUTPUT PASS']),
}
STEPS = re.compile(r'^\s*(ASMWR|LKWR|ASMA|ASMN|ASMR|ASMQ|ASMG|LKED|WGO|GO)\s+\S.*?\bRC=(\d{4})\s*$',re.M)
BAD = re.compile(r'\b(?:IEF450I|IEF472I|IEA995I|S013-[0-9A-F]+|BCPLREG 2001)\b', re.I)
NEG_FAIL = re.compile(r'^\s*BCPLQSAM Q1 NEGATIVE FAIL (\d+) RC=(-?\d+)\s*$',re.M)
FINAL = 'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS'


def finalizer_check(profile: str, summary: str, console: str) -> tuple[bool,list[str]]:
    path=HERE/'check-q1-finalizer-console.py'
    spec=importlib.util.spec_from_file_location('q1_console',path)
    if not spec or not spec.loader:
        raise RuntimeError('finalizer console helper unavailable')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.review(profile,summary,console)


def review(profile: str, summary: str, report: str,
           console: str | None = None) -> tuple[bool, list[str]]:
    job, expected, go_rc, markers = CASES[profile]
    errors=[]
    if not re.search(rf'^JOB\s+\d+\s+{job}\s*$',summary,re.M):
        errors.append('summary JOB name/number missing or wrong')
    got={}
    for match in STEPS.finditer(summary):
        step,rc=match.groups()
        if step in got: errors.append('duplicate summary step '+step)
        got[step]=int(rc)
    if set(got)!=expected:
        errors.append(f'expected steps {sorted(expected)}, got {sorted(got)}')
    for step,rc in got.items():
        want=go_rc if step=='GO' else 0
        if rc!=want:
            errors.append(f'{step} RC={rc:04d}, expected {want:04d}')
    severity=re.search(r'Highest severity:\s*(\d+)',summary)
    flagged=re.search(r'Statements flagged:\s*(\d+)',summary)
    if not severity or int(severity.group(1))!=0:
        errors.append('assembler severity not proven zero')
    if not flagged or int(flagged.group(1))!=0:
        errors.append('assembler statements flagged/unknown')
    rows=report.splitlines()
    boundaries=[i for i,v in enumerate(rows) if 'AUTHORIZATION CODE IS' in v]
    if not boundaries:
        errors.append('native post-link output boundary absent')
        native=[]
    else:
        native=rows[boundaries[-1]+1:]
    scan='\n'.join(native)
    for marker in markers:
        count=sum(marker in s for s in native)
        if marker!=FINAL:
            if count!=1:
                errors.append(f'actual native marker count {count} for {marker!r}')
        elif count!=1:
            if count>1:
                errors.append('duplicate native finalizer marker')
            elif console is None:
                errors.append('finalizer WTO not in printer; provide --console')
            # A supplied console must still be independently verified below.
    if profile in ('finish','stop') and console is not None:
        verified,problems=finalizer_check(profile,summary,console)
        if not verified:
            errors.extend('console: '+p for p in problems)
        # Console is additive evidence, not a bypass for invalid native output.
    if profile=='negative':
        failures=NEG_FAIL.findall(scan)
        for number,actual in failures[:5]:
            errors.append(f'negative assertion {number} returned {actual}')
        if len(failures)>1:
            errors.append('multiple negative failure diagnostics')
    bad=BAD.findall(scan)
    if bad: errors.append('native abnormal/finalizer messages: '+str(bad[:5]))
    return not errors,errors


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',required=True,choices=CASES)
    p.add_argument('--summary',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path)
    p.add_argument('--console',type=Path)
    a=p.parse_args()
    if a.console is not None and a.profile not in ('finish','stop'):
        p.error('--console only applies to finish/stop')
    if a.console is not None and a.console.stat().st_size>64*1024*1024:
        p.error('console evidence exceeds 64 MiB; supply a bounded excerpt')
    console = a.console.read_text(encoding='latin-1') if a.console else None
    ok,problems=review(a.profile,a.summary.read_text(encoding='latin-1'),
                       a.report.read_text(encoding='latin-1'),console)
    print(f'{"PASS" if ok else "NOT VERIFIED"}: Q.1 {a.profile} evidence')
    for e in problems:print(' - '+e)
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
