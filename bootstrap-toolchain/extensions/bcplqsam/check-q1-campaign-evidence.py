#!/usr/bin/env python3
"""Review preserved Q.1 campaign JES evidence; never submit/accept on behalf of owner.

Read native full JES report and tools/mvs/job-summary text as separate inputs.
The checker distinguishes expected explicit STOP(8) from accidental GO RC=8,
requires real GO output *after* the final linker boundary, and is fail closed.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

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


def review(profile: str, summary: str, report: str) -> tuple[bool, list[str]]:
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
        if count!=1:
            errors.append(f'actual native marker count {count} for {marker!r}')
    bad=BAD.findall(scan)
    if bad: errors.append('native abnormal/finalizer messages: '+str(bad[:5]))
    return not errors,errors


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',required=True,choices=CASES)
    p.add_argument('--summary',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path)
    a=p.parse_args()
    ok,problems=review(a.profile,a.summary.read_text(encoding='latin-1'),
                       a.report.read_text(encoding='latin-1'))
    print(f'{"PASS" if ok else "NOT VERIFIED"}: Q.1 {a.profile} evidence')
    for e in problems:print(' - '+e)
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
