#!/usr/bin/env python3
"""Read-only rc2 extension: draft only the two new PDS selective IEBCOPY steps.

Does not stage MVS datasets, modify accepted BT0001-BT0020, or write a tape.
Production submission requires a separate owner-approved, no-retry runner and
fresh read-only MVS/VTOC preflight. Space numbers are proposals only.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
LIB=Path(__file__).resolve().parent
QUAL=re.compile(r'[A-Z@#$][A-Z0-9@#$]{0,7}\Z')

class Refusal(ValueError): pass

def need(ok,why):
    if not ok: raise Refusal(why)

def checked_dsn(name):
    need(isinstance(name,str) and len(name)<=44 and
         all(QUAL.fullmatch(part) for part in name.split('.')),
         'invalid MVS dataset name')
    return name

def render(manifest:dict,dspal:dict,*,volume:str, primary:int=40,
           secondary:int=10,directory:int=20)->str:
    """Render the known accepted IEBCOPY pattern for *new* BT0021/22 only."""
    need(manifest['release']['candidate_id']=='BCPL-0.1.0-rc2' and
         manifest['release']['cambridge_source']=='included' and
         manifest['release']['native_compiler']=='absent' and
         manifest['volume']['volser']=='BC0002',
         'source-only successor identity mismatch')
    need(volume=='TSO002','volume is a proposal requiring fresh MVS approval')
    need(all(type(x) is int and 1<=x<=999 for x in (primary,secondary,directory)),
         'staging SPACE must be explicit positive track/directory values')
    need(len(manifest['datasets'])==22,'22 logical datasets required')
    rows=manifest['datasets'][20:]
    need([r['sequence'] for r in rows]==[21,22] and
         [r['dspal_key'] for r in rows]==['CAMB_SOURCE','CAMB_DEMOTED'],
         'not the approved two-PDS source extension')
    hlq=dspal['mvs']['hlq']
    need(hlq=='HERC02','source staging restricted to accepted HERC02 namespace')
    cards=['//* TA.2 RC2 DRAFT ONLY: NOT AUTHORIZED FOR MVS SUBMISSION.',
           '//* BT0001-BT0020 ARE ALREADY ACCEPTED; DO NOT RESTAGE.',
           '//* TWO NEW PDS INPUTS; FAIL CLOSED IF EITHER EXISTS.']
    total=0
    for i,r in enumerate(rows):
        n=21+i; key=r['dspal_key']; source=dspal['datasets'][key]
        need(r['group']=='cambridge-source' and r['owner']=='cambridge-compiler-source'
             and r['kind']=='pds_unload' and r['transfer']=='iebcopy_unload',
             'source distribution role mismatch')
        need(r['target_dcb']=={'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800},
             'unexpected source PDS DCB')
        need(len(r['members'])==15 and len(set(r['members']))==15 and
             all(QUAL.fullmatch(m) for m in r['members']),
             'source members not exact, unique MVS names')
        names=set(source.get('members',{}))|set(source.get('generated_members',{}))
        need(set(r['members'])==names,'selected source members disagree with dspal')
        source_dsn=checked_dsn(hlq+'.'+source['dsn'])
        target_dsn=checked_dsn(f'HERC02.BCPL.TA2STG.BT{n:04d}')
        need(source_dsn!=target_dsn,'source/destination collision')
        cards.extend([
            f'//S{n:04d} EXEC PGM=IEBCOPY,REGION=512K'+(',COND=(0,NE)' if i else ''),
            '//SYSPRINT DD SYSOUT=*',
            f'//INPDS DD DSN={source_dsn},DISP=SHR',
            f'//OUTPDS DD DSN={target_dsn},',
            '//            DISP=(NEW,CATLG,DELETE),UNIT=SYSDA,',
            f'//            VOL=SER={volume},',
            f'//            SPACE=(TRK,({primary},{secondary},{directory})),',
            '//            DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)',
            '//SYSUT3 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
            '//SYSUT4 DD UNIT=SYSDA,SPACE=(TRK,(10,5))',
            '//SYSIN DD *',
            ' COPY OUTDD=OUTPDS,INDD=INPDS',
        ])
        cards.extend(f' SELECT MEMBER=({m})' for m in r['members'])
        cards.append('/*');total+=len(r['members'])
    cards.append('//')
    need(total==30 and sum(' EXEC PGM=IEBCOPY' in x for x in cards)==2,
         'source staging step/member count mismatch')
    need(all(x.isascii() and '\t' not in x and len(x)<=80 for x in cards) and
         all(len(x)<=71 for x in cards if x.startswith('//') and not x.startswith('//*')),
         'overwidth/unsafe FB80 JCL card')
    return '\n'.join(cards)+'\n'

def load_contract():
    p=LIB/'successor-contract.py'; spec=importlib.util.spec_from_file_location('source_contract',p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,help='exclusive new draft file below repository workarea')
    p.add_argument('--volume',default='TSO002',help='proposed staging DASD; not approval')
    args=p.parse_args(argv)
    try:
        c=load_contract()
        rc1,rc2,dspal,reg=[c.read_yaml(path) for path in (c.RC1,c.RC2,c.DSPAL,c.REGISTRY)]
        sel=__import__('json').loads(c.SELECTION.read_text())
        c.verify(rc1,rc2,dspal,reg,sel,c.RC2.read_bytes())
        jcl=render(rc2,dspal,volume=args.volume)
        if args.output:
            output=args.output.resolve(); work=(ROOT/'workarea').resolve()
            need(output.is_relative_to(work) and output!=work and not output.exists() and
                 output.parent.is_dir() and not output.parent.is_symlink(),
                 'draft output must be a NEW file below workarea')
            with output.open('x',encoding='ascii') as fp:fp.write(jcl)
        print('TA.2 RC2 STAGE DRAFT: 2 IEBCOPY steps; 30 selected members; FB80 PASS')
        print('DRAFT ONLY: no MVS staging/tape, no new allocation or write approved')
        return 0
    except (Refusal,Exception) as e:
        print('TA.2 RC2 STAGE DRAFT HALTED: '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
