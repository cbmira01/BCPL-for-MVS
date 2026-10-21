#!/usr/bin/env python3
"""R.0 Decision G numeric limits: independent IFOX/IEWL/GO batch."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'workarea/runtime-extensions-r0-g-limits'
JOB = 'R0GLIMIT'

# label, kind (1 registry, 2 package), first count, second count, expected.
# Boundaries only. Full header/ownership/hook tests are host-reference cases.
CASES = (
    ('REG EMPTY',1,0,0,0),
    ('REG ONE',1,1,0,0),
    ('REG 32-32',1,32,32,0),
    ('REG N33',1,33,0,1003),
    ('REG M33',1,0,33,1003),
    ('REG NNEG',1,-1,0,1003),
    ('REG MNEG',1,0,-1,1003),
    ('PKG MIN',2,1,0,0),
    ('PKG MAX',2,8,16,0),
    ('PKG KZERO',2,0,0,1006),
    ('PKG K9',2,9,0,1006),
    ('PKG D17',2,1,17,1006),
    ('PKG KNEG',2,-1,0,1006),
    ('PKG DNEG',2,1,-1,1006),
)


def cards_ok(rows: list[str]) -> list[str]:
    for n, row in enumerate(rows, 1):
        if not row.isascii() or len(row) > 71 or '\t' in row or row == '/*' or row.startswith('//'):
            raise ValueError(f'bad IFOX card {n}: {row!r}')
    return rows


def data_source() -> list[str]:
    cards=['* R.0 DECISION G TEST-ONLY RELOCATABLE DATA.',
           'R0GDAT   CSECT', '         ENTRY R0GDATA',
           f"R0GDATA  DC    F'{len(CASES)}'"]
    for i,(label,kind,a,b,expected) in enumerate(CASES,1):
        cards += [f"         DC    F'{kind}',F'{a}',F'{b}',F'{expected}'",
                  f"         DC    CL80'R0 G{i:02d} {label} PASS'"]
    cards += ['         END   R0GDAT']
    return cards_ok(cards)


def asm_step(step:str,obj:str,rows:list[str])->list[str]:
    return [f'//{step:<8} EXEC PGM=IFOX00,REGION=256K,',
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        '//SYSLIB   DD  DSN=SYS1.MACLIB,DISP=SHR',
        '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1700,(600,100))',
        '//SYSUT2   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSUT3   DD  UNIT=SYSDA,SPACE=(1700,(300,50))',
        '//SYSPRINT DD  SYSOUT=*', '//SYSPUNCH DD  DUMMY',
        f'//SYSGO    DD  DSN=&&{obj},UNIT=SYSDA,',
        '//             SPACE=(80,(300,100)),DISP=(NEW,PASS),',
        '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
        '//SYSIN    DD  *', *rows, '/*']


def deck(jobcard:list[str])->str:
    if not jobcard or jobcard[0].split()[:2] != ['//R0GLIMIT','JOB']:
        raise ValueError('bad authenticated R0GLIMIT job card')
    driver = cards_ok((HERE/'check.asm').read_text('ascii').splitlines())
    cards=[*jobcard,'//* R.0 G LIMIT PROBE: TEMPORARY OBJECTS ONLY',
           *asm_step('ASMC','R0COBJ',driver),
           *asm_step('ASMD','R0DOBJ',data_source()),
           '//LKED     EXEC PGM=IEWL,REGION=256K,',
           "//             PARM='NCAL,LIST,XREF,MAP',",
           '//             COND=((0,NE,ASMC),(0,NE,ASMD))',
           '//SYSLIN   DD  DSN=&&R0COBJ,DISP=(OLD,DELETE)',
           '//         DD  DSN=&&R0DOBJ,DISP=(OLD,DELETE)',
           '//         DD  *', ' ENTRY R0GCHK', ' NAME R0GLIMIT(R)', '/*',
           '//SYSLMOD  DD  DSN=&&R0LOAD(R0GLIMIT),UNIT=SYSDA,',
           '//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)',
           '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
           '//SYSPRINT DD  SYSOUT=*',
           '//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,',
           '//             TIME=(,2),COND=(0,NE,LKED)',
           '//QOUT     DD  SYSOUT=*,',
           '//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)',
           '//SYSUDUMP DD  SYSOUT=*','//']
    for i,row in enumerate(cards,1):
        if not row.isascii() or len(row)>71 or '\t' in row:
            raise ValueError(f'bad JCL card {i}: {row!r}')
    if cards.count('/*')!=3:
        raise ValueError('expected two IFOX sources, one IEWL input')
    return '\n'.join(cards)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.check:
        jobcard=["//R0GLIMIT JOB (BCPL),'R0 G LIMITS',CLASS=A,MSGCLASS=A"]
    else:
        file=ROOT/'tools/datasets/dspal-core.py'
        spec=importlib.util.spec_from_file_location('r0gcore',file)
        if spec is None or spec.loader is None:
            raise ValueError('missing job card provider')
        core=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        cfg=core.load_config()
        jobcard=core.authenticated_job_card(cfg,JOB,'R0 G LIMITS',redact_password=False)
    text=deck(jobcard)
    if a.check:
        print(f'CHECK R.0 G LIMITS: {len(text.splitlines())} JCL cards; '
              f'{len(CASES)} cases; no credentials/JCL written')
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        file=OUT/'r0-g-limits.jcl'
        file.write_text(text,encoding='ascii',newline='\n')
        file.chmod(0o600)
        print(f'Generated R.0 G test-only JCL: {file}')


if __name__=='__main__':
    try: main()
    except (OSError,ValueError) as ex:
        raise SystemExit(f'R.0 G generator failed: {ex}')
