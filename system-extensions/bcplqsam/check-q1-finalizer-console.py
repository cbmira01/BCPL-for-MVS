#!/usr/bin/env python3
"""Read-only, fail-closed Q.1 finalizer WTO observation from TK5 console.

MVS WTO records may be absent from JES printer output.  This checker
requires a single bounded IEF403I..IEF404I interval for the matching job
name, an actual runtime WTO within that interval, and no finalizer error.
A marker found only in an IFOX listing or storage dump NEVER counts.
Even a PASS is a bounded console observation, not Q.1 acceptance.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

TRACE = 'BCPLQSAM Q1 FINALIZER 16 CLOSE PASS'
ERROR = 'BCPLREG 2001 FINALIZER RETURNED NONZERO'
JOB = {'finish':('Q16FIN',0),'stop':('Q16STP',8)}
SIZE_LIMIT = 64 * 1024 * 1024


def review(profile: str, summary: str, console: str) -> tuple[bool,list[str]]:
    if profile not in JOB:
        raise ValueError('finalization applies only to finish/stop')
    job, want_rc=JOB[profile]
    problems=[]
    if not re.search(rf'^JOB\s+\d+\s+{job}\s*$',summary,re.M):
        problems.append('summary job identity mismatch')
    steps=re.findall(r'^\s*GO\s+.*?\bRC=(\d{4})\s*$',summary,re.M)
    if len(steps)!=1 or int(steps[0])!=want_rc:
        problems.append('GO return code not verified')
    started=re.compile(rf'\bIEF403I\s+{job}\s+-\s+STARTED\b',re.I)
    ended=re.compile(rf'\bIEF404I\s+{job}\s+-\s+ENDED\b',re.I)
    windows=[]
    open_at=None
    for n,line in enumerate(console.splitlines(),1):
        if started.search(line):
            if open_at is not None:
                problems.append('overlapping/duplicate START for job')
            open_at=n
        if ended.search(line):
            if open_at is None:
                problems.append('END without matching START')
            else:
                windows.append((open_at,n))
                open_at=None
    if open_at is not None:
        problems.append('START without matching END')
    if len(windows)!=1:
        problems.append('expected exactly one start/end interval, found '+str(len(windows)))
    if len(windows)==1:
        a,b=windows[0]
        segment=console.splitlines()[a-1:b]
        valid=[]
        for i,line in enumerate(segment,a):
            if TRACE not in line:
                continue
            # IFOX expands WTO to message-text DCs.  These are not console WTOs.
            if re.search(r'\bWTO\s+[\x27\"]',line) or 'MESSAGE TEXT' in line:
                continue
            if re.match(r'^\s*[0-9A-F]{4,8}\s+[0-9A-F]{8}\b',line):
                continue  # storage dump, not an operator message
            valid.append(i)
        if len(valid)!=1:
            problems.append(f'expected one execution WTO, found {len(valid)}')
        if ERROR in '\n'.join(segment):
            problems.append('BCPLREG finalizer returned nonzero')
        if re.search(r'\b(?:IEF450I|IEF472I|ABEND\s+S\w+)\b',
                     '\n'.join(segment),re.I):
            problems.append('abend/abnormal completion within job interval')
    return not problems,problems


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',choices=JOB,required=True)
    p.add_argument('--summary',type=Path,required=True)
    p.add_argument('--console',type=Path,required=True)
    args=p.parse_args()
    for path in (args.summary,args.console):
        if not path.is_file() or path.stat().st_size>SIZE_LIMIT:
            p.error(f'file missing or exceeds 64 MiB: {path}')
    ok,issues=review(args.profile,
                     args.summary.read_text(encoding='latin-1'),
                     args.console.read_text(encoding='latin-1'))
    print(('PASS' if ok else 'NOT VERIFIED')+': '+args.profile+
          ' finalizer console observation (NOT Q.1 acceptance)')
    for issue in issues:
        print(' - '+issue)
    return 0 if ok else 1


if __name__=='__main__':
    raise SystemExit(main())
