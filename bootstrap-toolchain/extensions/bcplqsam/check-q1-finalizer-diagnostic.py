#!/usr/bin/env python3
"""Fail-closed Q1FDIAG JES + WTO triplet checker. Never submits JES."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

JOB='Q1FDIAG'
STEPS={'ASMWR','LKWR','ASMA','ASMN','ASMR','ASMQ','ASMG','LKED','WGO','GO'}
STEP_RE=re.compile(r'^\s*(ASMWR|LKWR|ASMA|ASMN|ASMR|ASMQ|ASMG|LKED|WGO|GO)\s+\S.*?\bRC=(\d{4})\s*$',re.M)
JOB_RE=re.compile(r'^JOB\s+(\d+)\s+Q1FDIAG\s*$',re.M)
REC_RE=re.compile(r'\bJOB\s+(\d+)\s+\+Q1F:([ELX]):([^\s]+)')
TRACE=re.compile(r'^([0-9A-F]{8})(?::[0-9A-F]{8})+$')
BAD=re.compile(r'\b(?:IEF450I|IEF472I|IEA995I)\b|BCPLREG 2001 FINALIZER RETURNED NONZERO',re.I)
EXPECTED={'E':(0,16,16,16),'L':(16,0,0,0,0),'X':(16,0,0,0,0)}
SIZE_LIMIT=64*1024*1024


def review(summary: str, report: str, console: str)->tuple[bool,list[str]]:
    problems=[]
    jobs=JOB_RE.findall(summary)
    if len(jobs)!=1:
        problems.append('missing or duplicate Q1FDIAG JOB identity')
    job=jobs[0] if len(jobs)==1 else None
    steps={}
    for match in STEP_RE.finditer(summary):
        step,rc=match.groups()
        if step in steps:
            problems.append('duplicate '+step+' step')
        steps[step]=int(rc)
    if set(steps)!=STEPS:
        problems.append('incomplete native ten-step execution')
    if any(rc!=0 for rc in steps.values()):
        problems.append('nonzero native step RC')
    for name in ('Statements flagged','Highest severity'):
        m=re.search(rf'{name}:\s*(\d+)',summary)
        if m is None or int(m.group(1))!=0:
            problems.append(f'{name} not zero')
    if 'JOB RESULT: SUCCESS' not in summary:
        problems.append('job success not established')
    rows=report.splitlines()
    boundaries=[i for i,line in enumerate(rows) if 'AUTHORIZATION CODE IS' in line]
    if not boundaries:
        problems.append('post-link boundary absent')
    else:
        native=rows[boundaries[-1]+1:]
        if sum('BCPLQSAM Q1 16 FINISH PASS' in row for row in native)!=1:
            problems.append('application 16-handle PASS absent/duplicated')
        if BAD.search('\n'.join(native)):
            problems.append('abnormal message in native report')
    if not job:
        return False,problems
    start=re.compile(r'\bJOB\s+'+re.escape(job)+r'\s+IEF403I\s+Q1FDIAG\s+-\s+STARTED\b')
    end=re.compile(r'\bJOB\s+'+re.escape(job)+r'\s+IEF404I\s+Q1FDIAG\s+-\s+ENDED\b')
    # Require job-number correlation in BOTH boundaries and each WTO.
    lines=console.splitlines()
    intervals=[]
    opened=None
    for i,line in enumerate(lines):
        if start.search(line):
            if opened is not None:
                problems.append('nested start boundary')
            opened=i
        if end.search(line):
            if opened is None:
                problems.append('end without start boundary')
            else:
                intervals.append((opened,i))
                opened=None
    if opened is not None:
        problems.append('unterminated job interval')
    if len(intervals)!=1:
        problems.append('expected one bounded Q1FDIAG job interval')
        return False,problems
    lo,hi=intervals[0]
    segment=lines[lo+1:hi]
    if BAD.search('\n'.join(segment)):
        problems.append('finalizer error/abend in job interval')
    found=[]
    for line in segment:
        match=REC_RE.search(line)
        if match is None:
            if '+Q1F:' in line:
                problems.append('unparseable Q1F console record')
            continue
        if match.group(1)!=job:
            problems.append('unrelated JOB number in Q1F record')
            continue
        phase,payload=match.group(2),match.group(3)
        if not TRACE.fullmatch(payload):
            problems.append('malformed '+phase+' diagnostic hex')
            continue
        values=tuple(int(v,16) for v in payload.split(':'))
        found.append((phase,values))
    if [x[0] for x in found]!=['E','L','X']:
        problems.append('expected exactly one ordered E,L,X triplet')
    for phase,values in found:
        if values!=EXPECTED[phase]:
            problems.append(f'{phase} values {values} expected {EXPECTED[phase]}')
    return not problems,problems


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--summary',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path)
    p.add_argument('--console',required=True,type=Path)
    a=p.parse_args()
    for path in (a.summary,a.report,a.console):
        if not path.is_file() or path.stat().st_size>SIZE_LIMIT:
            p.error(f'missing or >64MiB: {path}')
    ok,errors=review(*(p.read_text('latin-1') for p in (a.summary,a.report,a.console)))
    print(('PASS' if ok else 'NOT VERIFIED')+': Q1FDIAG test-only native finalizer diagnostic')
    for err in errors:print(' - '+err)
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
