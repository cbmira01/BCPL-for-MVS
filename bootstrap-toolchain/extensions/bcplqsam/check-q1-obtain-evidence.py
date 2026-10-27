#!/usr/bin/env python3
"""Fail-closed read-only JOB Q13DD OBTAIN observation review.

Extract raw returned 96-byte DSCB data for each of Q00/Q01/Q02.
Candidate offsets are advisory, NOT accepted production definitions.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

STEPS={'ASMWR','LKWR','ASMA','ASMN','ASMR','ASMQ','ASMG','LKED','WGO','GO'}
STEP_RE=re.compile(r'^\s*(ASMWR|LKWR|ASMA|ASMN|ASMR|ASMQ|ASMG|LKED|WGO|GO)\s+\S.*?\bRC=(\d{4})\s*$',re.M)
MARK=re.compile(r'Q1([IO]):(Q0[012]):(RC|NM0|NM1|VOL|MET|DS0|DS1|SKIP)=?([0-9A-F]*)')
LENGTHS={'I':{'RC':8,'NM0':44,'NM1':44,'VOL':60,'MET':12},
         'O':{'RC':8,'DS0':96,'DS1':96}}


def review(report: str, summary: str):
    lines=report.splitlines()
    borders=[i for i,s in enumerate(lines) if 'AUTHORIZATION CODE IS' in s]
    problems=[]
    if not re.search(r'^JOB\s+\d+\s+Q13DD\s*$',summary,re.M):
        problems.append('Q13DD summary JOB record missing')
    code={}
    for step,rc in STEP_RE.findall(summary):
        if step in code:problems.append('duplicate step '+step)
        code[step]=int(rc)
    if set(code)!=STEPS:problems.append('incomplete native job steps')
    for step,rc in code.items():
        want=8 if step=='GO' else 0
        if rc!=want:problems.append(f'{step} RC={rc:04d}, expected {want:04d}')
    severity=re.search(r'Highest severity:\s*(\d+)',summary)
    flagged=re.search(r'Statements flagged:\s*(\d+)',summary)
    if not severity or int(severity.group(1))!=0:
        problems.append('assembler severity not zero')
    if not flagged or int(flagged.group(1))!=0:
        problems.append('assembler flagged statements not zero')
    if not borders:
        return False,{},['linker/native output boundary missing']
    native=lines[borders[-1]+1:]
    fields={(dd,k):{} for dd in ('Q00','Q01','Q02') for k in 'IO'}
    for row in native:
        matches=list(MARK.finditer(row))
        if len(matches)>1:
            problems.append('multiple diagnostic fields on one output record')
            continue
        if not matches:
            if 'Q1I:' in row or 'Q1O:' in row:
                problems.append('malformed/incomplete diagnostic record')
            continue
        match=matches[0]
        key,dd,field,value=match.groups()
        bucket=fields[(dd,key)]
        if field in bucket:problems.append(f'{dd} {key} duplicate {field}')
        bucket[field]=value
    result={}
    for dd in ('Q00','Q01','Q02'):
        ident=fields[(dd,'I')];obt=fields[(dd,'O')]
        for key,bucket in [('I',ident),('O',obt)]:
            for fld,expected in LENGTHS[key].items():
                if fld not in bucket or len(bucket[fld])!=expected:
                    problems.append(f'{dd}: {key}.{fld} incomplete/missing')
        if 'SKIP' in obt:problems.append(f'{dd} OBTAIN skipped')
        if ident.get('RC')!='00000000' or obt.get('RC')!='00000000':
            problems.append(f'{dd}: nonzero/unknown macro return')
        if any(f not in ident for f in ('NM0','NM1','VOL','MET')) or \
           any(f not in obt for f in ('DS0','DS1')):continue
        try:
            name=bytes.fromhex(ident['NM0']+ident['NM1']).decode('cp037').strip()
            volume=bytes.fromhex(ident['VOL']).decode('cp037').strip()
            data=bytes.fromhex(obt['DS0']+obt['DS1'])
        except (UnicodeError,ValueError):
            problems.append(dd+': unparseable JFCB/DSCB bytes')
            continue
        if len(data)!=96:
            problems.append(dd+': DSCB data is not 96 bytes')
            continue
        result[dd]={'name':name,'volume':volume,
                    'candidate_dsorg':data[38],
                    'candidate_recfm':data[40],
                    'candidate_blksize':int.from_bytes(data[42:44],'big'),
                    'candidate_lrecl':int.from_bytes(data[44:46],'big')}
        if ident['MET'][:2]!='01':
            problems.append(dd+': not a single-volume JFCB')
        if not name or not volume:
            problems.append(dd+': allocated identity/volume missing')
    if re.search(r'\b(?:IEF450I|IEF472I|IEA995I|S013-\d+)\b',
                 '\n'.join(native)):
        problems.append('possible native MVS abend')
    return not problems,result,problems


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',required=True,type=Path)
    p.add_argument('--summary',required=True,type=Path)
    args=p.parse_args()
    ok,res,problems=review(args.report.read_text(encoding='latin-1'),
                           args.summary.read_text(encoding='latin-1'))
    for dd,item in res.items():
        print(f'{dd}: {item["name"]} on {item["volume"]}')
        print(f'  candidate DSORG={item["candidate_dsorg"]:02X} '
              f'RECFM={item["candidate_recfm"]:02X} '
              f'BLKSIZE={item["candidate_blksize"]} '
              f'LRECL={item["candidate_lrecl"]}')
    for e in problems:print(' - NOT VERIFIED:',e)
    print(('OBSERVATION COMPLETE' if ok else 'NOT VERIFIED')+
          ': raw DSCB extraction; geometry offsets still require approval')
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
