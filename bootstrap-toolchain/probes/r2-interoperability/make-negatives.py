#!/usr/bin/env python3
"""One batched MVS job for R.2 cross-extension acceptance/rejection cases.

The approved R.1 BCPLMAIN adaptation, BCPLREG registrar, and A/B dispatcher
are each assembled once; all objects and load modules are temporary.  Every
rejection has a separate registry/descriptor, IEWL link and GO execution.
"""
import argparse
from dataclasses import dataclass
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MATRIX = HERE / 'make-matrix.py'
WORK = ROOT / 'workarea/runtime-extensions-r2'
JOB = 'R2NEG'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ValueError(f'missing helper: {path}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def change(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'fixture anchor count not one: {old!r}')
    return source.replace(old, new)


@dataclass(frozen=True)
class Case:
    name: str
    diagnostic: int | None
    selected: tuple[str, ...]
    required: tuple[str, ...]
    mutation: str = ''
    # No object for B, while BCRG still contains a relocated B descriptor.
    omit: str = ''


CASES = (
    Case('validdep', None, ('a', 'b'), ('a', 'b'), 'dep-good'),
    Case('spanreg', 1001, ('a', 'b'), ('a', 'b'), 'reg-span'),
    Case('magicreg', 1002, ('a', 'b'), ('a', 'b'), 'reg-magic'),
    Case('sizereg', 1003, ('a', 'b'), ('a', 'b'), 'reg-size'),
    Case('spanpkg', 1004, ('a', 'b'), ('a', 'b'), 'pkg-span'),
    Case('magicpkg', 1005, ('a', 'b'), ('a', 'b'), 'pkg-magic'),
    Case('sizepkg', 1006, ('a', 'b'), ('a', 'b'), 'pkg-size'),
    Case('blankid', 1007, ('a', 'b'), ('a', 'b'), 'pkg-blank'),
    Case('badslot', 1008, ('a', 'b'), ('a', 'b'), 'global-zero'),
    Case('dupslot', 1008, ('a', 'b'), ('a', 'b'), 'global-duplicate'),
    Case('appown', 1009, ('a', 'b'), ('a', 'b'), 'global-app'),
    Case('blibown', 1009, ('a', 'b'), ('a', 'b'), 'global-blib'),
    Case('coreown', 1009, ('a', 'b'), ('a', 'b'), 'global-core'),
    Case('required', 1010, ('b',), ('a', 'b')),
    Case('missdep', 1010, ('b',), ('b',), 'dep-good'),
    Case('major', 1011, ('a', 'b'), ('a', 'b'), 'dep-major'),
    Case('minor', 1011, ('a', 'b'), ('a', 'b'), 'dep-minor'),
    Case('ordering', 1012, ('b', 'a'), ('a', 'b'), 'dep-good'),
    Case('finalptr', 1013, ('a', 'b'), ('a', 'b'), 'pkg-final'),
    Case('selfdep', 1014, ('a', 'b'), ('a', 'b'), 'dep-self'),
    Case('linkmiss', -1, ('a', 'b'), ('a', 'b'), omit='b-dispatch'),
)


def registry(selected, required):
    # Distinct order is intentional: B-before-A is the R.2 1012 case.
    pair = {'a': ('DMOBEG', 'DMOEND'), 'b': ('R2BBEG', 'R2BEND')}
    ident = {'a': 'BCPLDEMO', 'b': 'R2TESTB'}
    total = 28 + 8*len(selected) + 8*len(required)
    lines = ['BCPLREG  CSECT', '         ENTRY BCRGBEG,BCRGEND']
    if selected:
        names = ','.join(x for p in selected for x in pair[p])
        lines += ['         EXTRN ' + names]
    lines += ['BCRGBEG  DS    0F', "         DC    CL4'BCRG'",
              f"         DC    F'1',F'28',F'{total}',F'{len(selected)}',F'{len(required)}',F'0'"]
    lines += [f'         DC    A({pair[p][0]}),A({pair[p][1]})'
              for p in selected]
    lines += [f"         DC    CL8'{ident[p]}'" for p in required]
    lines += ['BCRGEND  EQU   *', '         END   BCPLREG']
    return '\n'.join(lines) + '\n'


def fixture(case: Case, extensions):
    reg = registry(case.selected, case.required)
    descriptors = {p:extensions[p][0] for p in case.selected}
    mut = case.mutation
    if mut.startswith('reg-'):
        if mut == 'reg-span':
            reg = change(reg, 'BCRGEND  EQU   *',
                         "         DC    X'00'\nBCRGEND  EQU   *")
        if mut == 'reg-magic':
            reg = change(reg, "CL4'BCRG'", "CL4'BAD!'")
        if mut == 'reg-size':
            total = 28 + 8*(len(case.selected)+len(case.required))
            reg = change(reg, f"F'28',F'{total}'", f"F'28',F'{total+4}'")
    if mut.startswith(('pkg-', 'global-', 'dep-')):
        d = descriptors['b']
        if mut == 'pkg-span':
            d = change(d, 'R2BEND   EQU   *',
                       "         DC    X'00'\nR2BEND   EQU   *")
        if mut == 'pkg-magic':
            d = change(d, "CL4'BCEX'", "CL4'BAD!'")
        if mut == 'pkg-size':
            d = change(d, "F'3',F'2',F'1',F'0',F'0',F'0'",
                       "F'3',F'2',F'2',F'0',F'0',F'0'")
        if mut == 'pkg-blank':
            d = change(d, "CL8'R2TESTB'", "CL8' '")
        slot = {'global-zero':0, 'global-duplicate':203,
                'global-app':1, 'global-blib':76,'global-core':30}.get(mut)
        if slot is not None:
            d = change(d, "F'299',A(R2BDISP)", f"F'{slot}',A(R2BDISP)")
        if mut == 'pkg-final':
            d = change(d, "F'3',F'2',F'1',F'0',F'0',F'0'",
                       "F'3',F'2',F'1',F'1',F'0',F'0'")
        if mut.startswith('dep-'):
            depname = 'R2TESTB' if mut == 'dep-self' else 'BCPLDEMO'
            major, minor = ((2,0) if mut == 'dep-major' else
                            (1,1) if mut == 'dep-minor' else (1,0))
            d = change(d, "F'1',F'48',F'56'", "F'1',F'48',F'72'")
            d = change(d, "F'3',F'2',F'1',F'0',F'0',F'0'",
                       "F'3',F'2',F'1',F'0',F'1',F'0'")
            d = change(d, 'R2BEND   EQU   *',
                       f"         DC    CL8'{depname}',F'{major}',F'{minor}'\n"
                       'R2BEND   EQU   *')
        descriptors['b'] = d
    return reg, descriptors


def witness(core):
    # Both public extension slots must remain wholly unpublished on reject.
    old = 'R1BAD    LR    9,10\n         L     15,=A(IOFIN)\n'
    new = ('R1BAD    LR    9,10\n'
           '         L     1,812(12)\n'
           "         C     1,=X'C7D3F32C'\n"
           '         BNE   R2LEAK\n'
           '         L     1,1196(12)\n'
           "         C     1,=X'C7D3F4AC'\n"
           '         BNE   R2LEAK\n'
           '         B     R2CLEAN\n'
           "R2LEAK   WTO   'R2 PARTIAL GLOBAL PUBLICATION'\n"
           '         L     15,=A(IOFIN)\n'
           '         BALR  14,15\n'
           '         LR    10,9\n'
           '         BAL   14,RELMEM\n'
           '         L     13,4(13)\n'
           '         LM    14,12,12(13)\n'
           '         LA    15,16\n'
           '         BR    14\n'
           'R2CLEAN  L     15,=A(IOFIN)\n')
    return change(core, old, new)


def build(generated, jobcard, dsn):
    if set(generated) != {'zero','both'}:
        raise ValueError('require zero and both generated BCPL sources')
    if not jobcard or jobcard[0].split()[:2] != ['//R2NEG', 'JOB']:
        raise ValueError('wrong authenticated job identity')
    m = load(MATRIX, 'r2_neg_matrix')
    trail = m.load(m.TRAIL, 'r2_neg_trailer')
    patch = m.load(m.PATCHER, 'r2_neg_patcher')
    prov = m.load(m.PROVENANCE, 'r2_neg_provenance')
    ext = m.extension_sources()
    core = witness(patch.adapt((ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')))
    inputs = [
        ('ASZ', 'NAPPZ', trail.application_source(generated['zero'])),
        ('ASX', 'NAPPX', trail.application_source(generated['both'])),
        ('ASMN','NCORE',trail.checked_asm(core,'core/witness')),
        ('ASMR','NREGS',trail.checked_asm((ROOT/'bootstrap-toolchain/asm/bcplrgs.asm').read_text('ascii'),'registrar')),
    ]
    for p, ds, disp, d_obj, s_obj in (
        ('a','ASDA','ASSA','NADESC','NADISP'),
        ('b','ASDB','ASSB','NBDESC','NBDISP')):
        inputs.append((ds,d_obj,trail.checked_asm(ext[p][0],p+' descriptor')))
        inputs.append((disp,s_obj,trail.checked_asm(ext[p][1],p+' dispatcher')))
    cases = []
    for i, case in enumerate(CASES,1):
        reg, desc = fixture(case,ext)
        # Check source provenance, except intentional finalizer-pointer case.
        # Its numeric nonzero field is an intentionally untrusted fixture.
        if case.selected:
            prov.check(reg, '\n'.join(desc.values()),
                       [ext[p][1] for p in case.selected],
                       allow_untrusted_fixture=(case.name=='finalptr'))
        index=f'{i:02d}'
        reg_obj=f'NG{index}'
        inputs.append((f'AG{index}',reg_obj,trail.checked_asm(reg,case.name+' registry')))
        desc_obj={}
        for p in case.selected:
            if desc[p] != ext[p][0]:
                obj=f'ND{index}'
                inputs.append((f'AD{index}',obj,trail.checked_asm(desc[p],case.name+' descriptor')))
                desc_obj[p]=obj
            else:
                desc_obj[p]='NADESC' if p=='a' else 'NBDESC'
        cases.append((case,index,reg_obj,desc_obj))
    cards = [*jobcard, '//* R.2 BATCHED NEGATIVES AND DEPENDENCIES',
             '//* ALL OBJECTS TEMPORARY; BOOT_OBJ READ ONLY',
             '//* EXPECTED RC12 CASES DO NOT BLOCK LATER LINKS']
    for step,obj,src in inputs:
        cards += trail.asm_step(step,obj,src)
    for case,index,regobj,descobj in cases:
        lid=f'L{index}'
        go=f'G{index}'
        loadname=f'R2N{index}'
        objs=['NAPPX' if case.name=='validdep' else 'NAPPZ',
              'NCORE','NREGS',regobj]
        for p in case.selected:
            objs.append(descobj[p])
            if not (p=='b' and case.omit=='b-dispatch'):
                objs.append('NADISP' if p=='a' else 'NBDISP')
        cards += [
            f'//{lid:<8} EXEC PGM=IEWL,REGION=256K,',
            "//             PARM='NCAL,LIST,XREF,MAP'",
            f'//OBJ      DD  DSN={dsn},DISP=SHR',
        ]
        for j,obj in enumerate(objs):
            cards.append(('//SYSLIN   DD  ' if j==0 else '//         DD  ')+
                         f'DSN=&&{obj},DISP=(OLD,PASS)')
        cards += ['//         DD  *',
                  *(f' INCLUDE OBJ({x})' for x in m.CORE),
                  ' ENTRY R0APP',f' NAME {loadname}(R)','/*',
                  f'//SYSLMOD  DD  DSN=&&NL{index}({loadname}),',
                  '//             UNIT=SYSDA,SPACE=(1024,(50,20,1)),',
                  '//             DISP=(NEW,PASS)',
                  '//SYSUT1   DD  UNIT=SYSDA,SPACE=(1024,(50,20))',
                  '//SYSPRINT DD  SYSOUT=*',
                  f'//{go:<8} EXEC PGM=*.{lid}.SYSLMOD,REGION=256K,',
                  f'//             TIME=(,2),COND=(0,NE,{lid})',
                  '//SYSPRINT DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=132,',
                  '//             BLKSIZE=132)',
                  '//SYSUDUMP DD  SYSOUT=*']
    cards.append('//')
    for n,row in enumerate(cards,1):
        if not row.isascii() or len(row)>71 or '\t' in row:
            raise ValueError(f'invalid JCL card {n}: {row!r}')
    if cards.count('/*') != len(inputs)+len(CASES):
        raise ValueError('missing assembler/link instream terminators')
    if sum(row.startswith('//ASMN') for row in cards)!=1:
        raise ValueError('must assemble core once')
    if any('BOOT.DEVOBJ' in x or 'DISP=MOD' in x for x in cards):
        raise ValueError('persistent object write forbidden')
    return '\n'.join(cards)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--generated-dir',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    if not a.check and not a.generated_dir:
        p.error('--generated-dir required outside --check')
    m=load(MATRIX,'r2_neg_config')
    trail=m.load(m.TRAIL,'r2_neg_fixture')
    gen=({x:(a.generated_dir / f'{x}.s370.asm').read_bytes().decode('latin-1')
          for x in ('zero','both')} if a.generated_dir else
         {x:trail.sample_generated() for x in ('zero','both')})
    if a.check:
        card=["//R2NEG JOB (BCPL),'R2 NEGATIVE',CLASS=A,MSGCLASS=A"]
        dsn='HERC02.BCPL.BOOT.OBJ'
    else:
        core=trail.load_core()
        cfg=core.load_config()
        spec=cfg['datasets']['BOOT_OBJ']
        if (spec.get('content_type')!='object' or spec.get('dsorg')!='PO'
                or spec.get('recfm')!='FB' or int(spec.get('lrecl',0))!=80):
            raise ValueError('BOOT_OBJ must be FB80 object PDS')
        dsn=core.full_dsn(cfg,spec)
        card=core.authenticated_job_card(cfg,JOB,'R2 NEGATIVE BATCH',
                                         redact_password=False)
    deck=build(gen,card,dsn)
    if a.check:
        print(f'CHECK {JOB}: {len(CASES)} cases; {len(deck.splitlines())} cards; no credentials or files written')
    else:
        dest=a.output or (WORK/'r2-negatives.jcl')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(deck,encoding='ascii',newline='\n')
        dest.chmod(0o600)
        print(f'Candidate JCL: {dest}')


if __name__=='__main__':
    try:main()
    except (OSError,UnicodeError,ValueError) as e:
        raise SystemExit(f'R.2 negatives FAILED: {e}')
