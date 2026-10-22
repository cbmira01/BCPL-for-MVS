#!/usr/bin/env python3
"""Independent R.1 actual-owner collision probes (test-only objects).

G!1: compiled application START; G!76: linked historical BLIB WRITEF;
G!30: Core Runtime STOP. Require diagnostic 1009 and unchanged G!298/299.
Never modify BOOT_OBJ or an accepted Core Runtime module.
"""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path
import os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = Path(os.environ['R1_CAMPAIGN_STAGE']) if os.environ.get(
    'R1_CAMPAIGN_STAGE') else ROOT / 'workarea/runtime-extensions-r1'
PROFILES = {'app':(1,'R1OAPP'), 'blib':(76,'R1OBLIB'),
            'core':(30,'R1OCORE')}


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing dependency {path}')
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(profile, generated, baseline, jobcard, dsn):
    if profile not in PROFILES:
        raise ValueError(f'unknown profile {profile}')
    slot,job=PROFILES[profile]
    neg=load(HERE/'make-negative-jobs.py','r1_owner_neg')
    builder=load(HERE/'make-jobs.py','r1_owner_builder')
    patch=load(ROOT/'tools/checks/r1_prepare_candidate.py','r1_owner_patch')
    registry,descriptor,_=neg.fixture(1009)
    anchor="F'1',A(R1DISP)"
    if descriptor.count(anchor)!=1:
        raise ValueError('expected one export relocation in descriptor')
    descriptor=descriptor.replace(anchor,f"F'{slot}',A(R1DISP)")
    core=neg.rejection_witness(patch.adapt(baseline))
    # Test-only: inspect the actual recorded prior-writer class in the
    # R.1-private ledger. 1=application, 2=BLIB, 4=Core Runtime.
    class_bit={'app':1,'blib':2,'core':4}[profile]
    old='R1BAD    LR    9,10\n'
    new=(old + '         L     4,=A(R1OWNB)\n'
         + f"         CLI   {slot}(4),X'{class_bit:02X}'\n"
         + '         BE    R1OWNOK\n'
         + "         WTO   'R1 OWNER LEDGER MISMATCH'\n"
         + '         B     R1LEAK\n'
         + 'R1OWNOK EQU   *\n')
    if core.count(old)!=1:
        raise ValueError('owner witness insertion anchor missing')
    core=core.replace(old,new)
    return builder.make_deck('selected',jobcard,generated,baseline,dsn,
                             jobname_override=job,
                             registry_override=registry,
                             descriptor_override=descriptor,
                             core_override=core)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('profile',choices=(*PROFILES,'all'))
    p.add_argument('--generated',type=Path)
    p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if not a.check and a.generated is None:
        p.error('--generated required outside --check')
    builder=load(HERE/'make-jobs.py','r1_owner_config')
    trail=builder.load(builder.BASE,'r1_owner_trail')
    source=(ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
    generated=trail.sample_generated() if a.check else a.generated.read_bytes().decode('latin1')
    if a.check:
        config=None
        dsn='HERC02.BCPL.BOOT.OBJ'
    else:
        core=trail.load_core()
        config=core.load_config()
        spec=config['datasets']['BOOT_OBJ']
        if (spec.get('content_type')!='object' or spec.get('dsorg')!='PO'
            or spec.get('recfm')!='FB' or int(spec.get('lrecl',0))!=80):
            raise ValueError('BOOT_OBJ is not an FB80 object PDS')
        dsn=core.full_dsn(config,spec)
    for profile in PROFILES if a.profile=='all' else (a.profile,):
        slot,job=PROFILES[profile]
        card=[f"//{job} JOB (BCPL),'R1 OWNER',CLASS=A,MSGCLASS=A"] if a.check else core.authenticated_job_card(config,job,'R1 OWNER',redact_password=False)
        deck=build(profile,generated,source,card,dsn)
        if a.check:
            print(f'CHECK {job}: G!{slot}; {len(deck.splitlines())} cards')
        else:
            WORK.mkdir(parents=True,exist_ok=True)
            output=WORK/f'r1-owner-{profile}.jcl'
            output.write_text(deck,'ascii',newline='\n')
            output.chmod(0o600)
            print(f'Candidate JCL: {output}')


if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,UnicodeError) as e:
        raise SystemExit(f'R.1 actual-owner JCL FAILED: {e}')
