#!/usr/bin/env python3
"""One private full-volume integration exercise of release.py; never publish.

Default: offline plan. --run: read-only preflight, one confirmation, no retry.
Historical helpers are used only for established MVS/JES transport and evidence.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
import release
import yaml

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'packaging/distribution'
CREATE = DIST / 'create-tape/scripts'
INSTALL = DIST / 'install-from-tape/scripts'
TAPES = ROOT / 'mvs-state/tape'
WORK = ROOT / 'workarea'
OUT = WORK / 'release-integration'
VOL = 'BC0005'
ID = 'BCPL-0.1.0-tooltest1'
IMAGE = TAPES / 'bcpl-0.1.0-tooltest1-BC0005.aws'
MARKER = OUT / 'BC0005-no-retry.json'
HLQ, DASD, UNIT = 'HERC02', 'TSO002', '480'
STAGE = 'HERC02.BCPL.X5ST.'
SOURCE = 'HERC02.BCPL.TA2R3S.'
SITES = {'mr10-only': 'X5MR', 'native-only': 'X5NT', 'combined': 'X5CB'}
MEMBERS = ('INSTALL', 'DATASETS', 'RELEASE', 'RESTORE', 'COPY', 'MR10', 'NATIVE', 'COMBINED')
BASE_SHA = '72c241201a95953546923f62ea6bfb43fcf56349c5ec7618671d7802d2ee6c1a'
ORIGINALS = {
    'bcpl-0.1.0-rc3-BC0003.aws': '6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1',
    'bcpl-0.1.0-rc4-BC0004.aws': '7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    need(path.is_file() and not path.is_symlink(), 'missing/linked file: ' + str(path))
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def load(path):
    need(path.is_file() and not path.is_symlink(), 'missing trusted helper: ' + str(path))
    loader = SourceFileLoader('integration_' + path.name, str(path))
    spec = spec_from_loader(loader.name, loader)
    mod = module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def plan():
    base = DIST / 'manifest/releases/BCPL-0.1.0-rc4.yaml'
    need(sha(base) == BASE_SHA, 'frozen RC4 manifest changed')
    registry = yaml.safe_load((DIST/'registry/releases.yaml').read_text())
    tests = registry['integration_tests']
    entry = tests[ID]
    need(entry == {'volser': VOL, 'base_manifest_sha256': BASE_SHA,
                   'image': IMAGE.name, 'state': 'reserved-private-test'}, 'test reservation differs')
    volumes = [x['volser'] for x in registry['candidates']] + [x['volser'] for x in tests.values()]
    need(len(volumes) == len(set(volumes)), 'registry VOLSER collision')
    m = deepcopy(release.read_manifest(base))
    m['release'].update(candidate_id=ID, version='0.1.0-tooltest1')
    m['volume'].update(volser=VOL, registry_reservation=ID)
    rows = m['datasets']
    need(len(rows) == 21 and tuple(rows[1]['members']) == MEMBERS and
         m['release']['native_compiler'] == 'absent', 'unexpected frozen release scope')
    for row in rows:
        n = row['sequence']
        row['producer_source_dsn'] = (STAGE if n <= 2 else SOURCE) + f'BT{n:04d}'
    budget = json.loads((DIST/'create-tape/ta2-stage-space-proposal-20261119.json').read_text())
    need(budget['volume'] == DASD, 'allocation budget volume differs')
    sizes = {r['sequence']: (r['primary_tracks'], r['secondary_tracks'], r['directory_blocks'])
             for r in budget['targets']}
    sizes[21] = (100, 10, 10)
    need(set(sizes) == set(range(3, 22)), 'allocation map differs')
    writer = release.render_write_jcl(m, unit=UNIT)
    need(writer.count(' SELECT MEMBER=') == 150 and writer.count('LABEL=(') == 21, 'writer selection differs')
    docs = ['PRIVATE MVS RELEASE TOOL INTEGRATION TEST - NOT FOR DISTRIBUTION.',
            f'{ID} / {VOL}; 21 STANDARD-LABELED DATASETS.',
            'NATIVE CAMBRIDGE COMPILER ABSENT; HISTORICAL SOURCE INCLUDED.',
            'RESTORE BT0002 USING IEBCOPY INTO A NEW SITE DIST.INST PDS.',
            'USE MR10, NATIVE OR COMBINED JOB MEMBERS WITH A SITE JOB CARD.',
            'BT0003 THROUGH BT0021 REUSE ACCEPTED RC4 PAYLOAD SELECTION.',
            'BT0003 DOCUMENTATION IS HISTORICAL AND NOT VALID FOR THIS TEST.',
            'NO PUBLICATION OR NATIVE FUNCTIONAL ACCEPTANCE IS IMPLIED.']
    boot = release.checked_lines(docs)
    members = {'INSTALL': boot, 'DATASETS': release.checked_lines([
        f'BT{r["sequence"]:04d} {r["group"]} {r["target_dsn_template"]}' for r in rows[2:]]),
        'RELEASE': boot, 'RESTORE': boot,
        'COPY': ' COPY OUTDD=OUTPDS,INDD=INTAPE\n'}
    profiles = {}
    for profile, site in SITES.items():
        label, _ = release.PROFILES[profile]
        prefix = f'{HLQ}.BCPL.{site}'
        positions = release.profile_positions(m, profile)
        body = release.render_install_jcl(m, sizes, profile, hlq=HLQ, site=site,
                                          tape_unit=UNIT, dasd_unit='SYSDA', dasd_vol=DASD)
        members[label] = body
        targets = [(2, prefix+'.DIST.INST', list(MEMBERS))]
        for n in positions:
            r = rows[n-1]
            targets.append((n, prefix+'.'+r['target_dsn_template'][len('{HLQ}.BCPL.'):],
                            r['members'], r['target_dcb']))
        profiles[label] = (prefix, positions, targets, body)
    counts = [(len(p[2]), sum(len(r[2]) for r in p[2])) for p in profiles.values()]
    need(counts == [(11,94),(11,71),(20,150)], 'profile inventory differs')
    targets = [STAGE+'BT0001', STAGE+'BT0002'] + [r[1] for p in profiles.values() for r in p[2]]
    need(len(targets) == len(set(targets)) == 44 and all(release.safe_dsn(x) for x in targets),
         'invalid/overlapping target inventory')
    need(tuple(members) == MEMBERS, 'installer inventory differs')
    tracks = 6+55+3*25+sum(sizes[n][0]+sizes[n][1] for p in profiles.values() for n in p[1])+100
    return m, writer, boot, members, profiles, targets, tracks


def originals():
    for name, expected in ORIGINALS.items():
        need(sha(TAPES/name) == expected, 'accepted original changed: '+name)


def drive(rc3, media, folder, key):
    h = rc3.run_command(folder,key+'-hercules',['tools/mvs/mvs-console','tape','status',UNIT])
    g = rc3.run_command(folder,key+'-mvs',['tools/mvs/mvs-console','mvs','tapes'])
    rows = re.findall(r'\bHHC02279I\s+(?:[0-9A-Fa-f]+:)?0480\s+3420\s+(.*)',h)
    need(len(rows)==1 and 'busy' not in rows[0].lower(), 'ambiguous/busy tape drive')
    state = media.parse_mvs(g)
    if re.match(r'\*\s',rows[0]):
        need(state=='O-NRD', 'empty tape not confirmed by MVS')
        return 'EMPTY'
    names = [n for n in (*ORIGINALS, IMAGE.name) if re.search(r'(?<![A-Za-z0-9_.-])'+re.escape(n)+r'(?![A-Za-z0-9_.-])',rows[0])]
    need(state=='O' and len(names)==1, 'foreign or non-idle media; refusing to displace')
    return names[0]


def run(live):
    m, writer, boot, members, profiles, targets, tracks = plan()
    print(f'PRIVATE TEST PLAN: {VOL}; 21 datasets; 44 new DASD targets; {tracks} track planning allowance; 80 MR10 cases.')
    if not live:
        return 0
    folder = rc3 = None
    marked = False
    try:
        need(sys.stdin.isatty(), 'operator terminal required')
        need(WORK.is_dir() and not WORK.is_symlink() and not OUT.is_symlink() and
             not MARKER.exists() and not MARKER.is_symlink(), 'unsafe workarea or consumed marker; NO RETRY')
        need(TAPES.is_dir() and not TAPES.is_symlink() and not IMAGE.exists() and not IMAGE.is_symlink(), 'test image exists or tape directory unsafe')
        rc3 = load(CREATE/'ta2-rc3-consolidated')
        git = rc3.check_git()
        originals()
        gen = load(CREATE/'ta3-rc4-installer')
        ops = load(CREATE/'ta3-rc4-production')
        prod = load(CREATE/'ta2-rc2-produce-once')
        media = load(CREATE/'ta2-rc2-media-preflight')
        vtoc = load(CREATE/'ta2-target-review')
        installed = load(CREATE/'ta2-rc3-installed-mr10-continuation')
        ref = load(INSTALL/'ta3-rc3-recipient')
        rem = load(INSTALL/'ta3-rc3-remaining-profiles')
        rec = load(INSTALL/'ta3-rc4-recipient')
        ta4 = load(INSTALL/'ta4-mr10-verification')
        ta7 = load(INSTALL/'ta7-clean-namespace')
        core = load(ROOT/'tools/datasets/dspal-core.py')
        ls = load(ROOT/'tools/datasets/dspal-ls.py')
        cfg = core.load_config()
        need(cfg['mvs']['hlq']==HLQ and cfg['mvs']['batch_user']==HLQ, 'unexpected MVS site/user')
        need(all(cfg['runtime'].get(k)==v for k,v in {'docker_container':'mvs38j','reader_host':'127.0.0.1',
             'reader_port':3505,'hercules_host':'127.0.0.1','hercules_port':8038,'printer':'mvs-state/prt/prt00e.txt'}.items()), 'unexpected MVS transport')
        core.require_reader_ready(cfg)
        stage = gen.stage_deck(boot,members).replace(gen.STAGE,STAGE).replace('TA.3 RC4','PRIVATE TEST')
        expected_stage = [('B0001','IEBGENER'),('A0002','IEFBR14')]+[(f'M{i:04d}','IEBGENER') for i in range(1,9)]
        outer = '\n'.join(rc3.jcl_control_cards(stage.splitlines()))
        need(re.findall(r'(?m)^//([A-Z][0-9]{4}) EXEC PGM=(IEBGENER|IEFBR14)',outer)==expected_stage and
             outer.count('DISP=(NEW,CATLG,DELETE)')==2 and gen.STAGE not in stage, 'stage deck scope differs')
        cases = release.read_mr10_panel(ROOT, ROOT/'mr10-kit-compiler/tests/00-regression-panel/manifest.tsv',ROOT/'mr10-kit-compiler/jcl/run-regression-tests.jcl')
        # Only adapt the pure suite-deck helper's site allowlist, never its runner.
        ta7.SITES = {'MR10':SITES['mr10-only'],'NATIVE':SITES['native-only'],'COMBINED':SITES['combined']}
        suites = {}
        for label,(prefix,_,rows,_) in profiles.items():
            if label=='NATIVE':
                continue
            allowed = {r[1] for r in rows}
            suites[label] = []
            for key,member,filename,count in ta7.SUITES:
                source = (ROOT/'mr10-kit-compiler/jcl'/filename).read_text('ascii')
                ta7.suite_deck(source,prefix,count,allowed,ta4)
                suites[label].append((key,member,source,count))
        OUT.mkdir(mode=0o700,exist_ok=True)
        folder = OUT/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+str(os.getpid()))
        folder.mkdir(mode=0o700)
        def save(key,value):
            rc3.artifact(folder,key+'.json',json.dumps(value,indent=2)+'\n')
        def job(key,name,body,steps):
            return ref.mvs_job(rc3,core,cfg,folder,key,name,body,steps)
        def unmount(key):
            rc3.run_command(folder,key,['tools/mvs/mvs-console','--yes','tape','unmount',UNIT])
            need(drive(rc3,media,folder,key+'-check')=='EMPTY','tape not safely released')
        save('manifest',m)
        rc3.artifact(folder,'writer.jcl',writer)
        prod.check_docker(folder)
        entries = sorted(TAPES.iterdir())
        need(len(entries)<=64,'unexpectedly large tape directory')
        for i,p in enumerate(entries):
            if p.name=='.gitkeep':
                continue
            need(p.is_file() and not p.is_symlink() and p.suffix.lower() in ('.aws','.het'),'unexpected tape entry')
            labels = rc3.run_command(folder,f'media-{i:03d}',['docker','exec','mvs38j','hetmap','-l','/tk5/tape/'+p.name])
            need(prod.volser_from_hetmap(labels)!=VOL,'test VOLSER already present: '+p.name)
        prior = drive(rc3,media,folder,'before')
        need(prior!=IMAGE.name,'test tape already mounted')
        sources = [(r['sequence'],r['producer_source_dsn'],r['members'],r['target_dcb']) for r in m['datasets'][2:]]
        pre = ops.report_catalog(gen,rc3,core,cfg,folder,'preflight',[(r[1],r[3]) for r in sources],targets)
        cat,dirjob,total = rem.verify(rc3,ref,core,cfg,installed,ls,folder,'source',sources)
        need(total==142,'accepted source directory count differs')
        body = ('//VTOC EXEC PGM=IEHLIST\n//SYSPRINT DD SYSOUT=*\n//VOL DD UNIT=SYSDA,VOL=SER='+DASD+',DISP=SHR\n//SYSIN DD *\n LISTVTOC FORMAT,VOL=SYSDA='+DASD+'\n/*\n//\n')
        vjob,report,_ = job('vtoc','ITVTOC',body,[('VTOC','IEHLIST')])
        space = vtoc.inspect_vtoc(report,DASD,targets)
        free = space['iehlist_reported_free_total_tracks']
        need(free is not None and 2*tracks<=free,'insufficient or unverified VTOC planning capacity')
        save('preflight',dict(catalog_job=pre,source_catalog=cat,source_directory=dirjob,vtoc_job=vjob,space=space,planning_tracks=tracks,targets=targets,prior_media=prior))
        need(drive(rc3,media,folder,'after-preflight')==prior,'drive changed during preflight')
        originals()
        print(f'PREFLIGHT PASS: JOBS {pre}/{cat}/{dirjob}/{vjob}; 44 absent targets; {free} reported free tracks; drive {prior}.')
        if input(f'Create {VOL}, stage two inputs and install/test three profiles ONCE? [y/N]: ').strip().upper()!='Y':
            save('result',{'status':'DECLINED_NO_WRITE'}); rc3.seal(folder); return 0
        need(not IMAGE.exists() and not IMAGE.is_symlink() and git('status','--porcelain','--untracked-files=no').strip()==b'', 'image or tracked checkout changed')
        rc3.exclusive(MARKER,(json.dumps({'candidate':ID,'volser':VOL,'head':git('rev-parse','HEAD').decode().strip(),'evidence':str(folder.relative_to(ROOT)),'targets':targets,'publication_authorized':False})+'\n').encode())
        marked=True
        staged,_,_ = job('stage','ITSTAGE',stage,expected_stage)
        ops.report_catalog(gen,rc3,core,cfg,folder,'staged',[(r[1],r[3]) for r in sources],targets[:2])
        rem.verify(rc3,ref,core,cfg,installed,ls,folder,'staged-installer',[(2,targets[1],list(MEMBERS))])
        print(f'STAGE PASS: JOB {staged}; new BT0001/BT0002.')
        originals()
        need(drive(rc3,media,folder,'before-write')==prior,'drive changed before write')
        if prior!='EMPTY':
            unmount('release-prior')
        rc3.exclusive(IMAGE,b'')
        rc3.run_command(folder,'initialize',['docker','exec','--user',f'{os.getuid()}:{os.getgid()}','mvs38j','hetinit','-d','-i','/tk5/tape/'+IMAGE.name,VOL])
        rc3.run_command(folder,'mount-write',['tools/mvs/mvs-console','--yes','tape','mount',UNIT,IMAGE.name])
        need(drive(rc3,media,folder,'write-ready')==IMAGE.name,'test tape not mounted')
        wrote,_,_ = job('write','ITWRITE',writer,[(f'T{i:04d}','IEBGENER' if i==1 else 'IEBCOPY') for i in range(1,22)])
        labels = rc3.run_command(folder,'aws-labels',['docker','exec','mvs38j','hetmap','-l','/tk5/tape/'+IMAGE.name])
        files = rc3.run_command(folder,'aws-files',['docker','exec','mvs38j','hetmap','-f','/tk5/tape/'+IMAGE.name])
        structure = release.evaluate_hetmap(labels,files,volser=VOL,count=len(m['datasets']))
        save('tape-review',structure)
        tape_sha = sha(IMAGE)
        originals()
        print(f'TAPE PASS: JOB {wrote}; 21 datasets/64 files; SHA256 {tape_sha}.')
        def mount(key):
            state = drive(rc3,media,folder,key+'-before')
            need(state in ('EMPTY',IMAGE.name),'foreign medium appeared during test')
            need(sha(IMAGE)==tape_sha,'test tape changed')
            if state=='EMPTY':
                rc3.run_command(folder,key+'-mount',['tools/mvs/mvs-console','--yes','tape','mount',UNIT,IMAGE.name])
            need(drive(rc3,media,folder,key+'-ready')==IMAGE.name,'test tape not ready')
        mount('boot-tape')
        body = rec.boot_and_installer(ref,profiles['MR10'][0],vol=VOL)['TA3BOOT']
        bootjob,report,_ = job('boot','ITBOOT',body,[('BOOTREAD','IEBGENER')])
        need(VOL in report and 'NATIVE CAMBRIDGE COMPILER ABSENT' in report,'wrong bootstrap')
        results = {}
        for label,(prefix,positions,rows,canonical) in profiles.items():
            key = label.lower()
            mount(key+'-bt2-tape')
            bt,_,_ = job(key+'-bt2','ITBT2',rec.boot_and_installer(ref,prefix,vol=VOL)['TA3BT2'],[('BT2REST','IEBCOPY')])
            view,report,_ = job(key+'-view','ITVIEW',rec.readback_deck(prefix,label),[('P0001','IEBGENER'),('P0002','IEBGENER')])
            deck = rec.extract_profile(report,canonical)
            need('COPY OUTDD=OUTPDS,INDD=INTAPE' in report,'installed COPY card missing')
            mount(key+'-profile-tape')
            name = {'MR10':'ITMR10','NATIVE':'ITNATV','COMBINED':'ITCOMB'}[label]
            restored,report,summary = job(key+'-restore',name,deck,None)
            rec.profile_result(name,report,summary,positions)
            cat,directory,total = rem.verify(rc3,ref,core,cfg,installed,ls,folder,key,rows)
            detail = {'installer':bt,'readback':view,'restore':restored,'catalog':cat,'directory':directory,'pdses':len(rows),'members':total,'functional':{}}
            print(f'{label} INSTALL PASS: {len(rows)} PDSes/{total} members; JOB {restored}.')
            allowed = {r[1] for r in rows}
            for suite,member,source,count in suites.get(label,[]):
                tag = key+'-'+suite
                read = ('//READJCL EXEC PGM=IEBGENER,REGION=512K\n//SYSPRINT DD SYSOUT=*\n//SYSIN DD DUMMY\n//SYSUT1 DD DSN='+prefix+'.MR10KIT.JCL('+member+'),\n//            DISP=SHR\n//SYSUT2 DD SYSOUT=*\n//\n')
                readjob,report,_ = job(tag+'-read','ITJCL',read,[('READJCL','IEBGENER')])
                body,steps = ta7.suite_deck(ta7.read_cards(report,source),prefix,count,allowed,ta4)
                jid,report,_ = job(tag,'IT'+member[:6],body,steps)
                if suite=='regression':
                    semantic = release.inspect_mr10(report,cases)
                    need(semantic['exp_contract_met'] and semantic['golden_rp_and_code_match'],'MR10 semantic comparison failed')
                    n = len(cases)
                else:
                    selection = ta4.LANG if suite=='language' else ta4.BCPL
                    semantic = ta4.verify_demos(report,selection,steps)
                    n = len(selection)
                save(tag+'-semantics',dict(semantic,mvs_job=jid,readback_job=readjob))
                detail['functional'][suite]={'job':jid,'cases':n}
                print(f'{label} {member} PASS: {n} cases; JOB {jid}.')
            results[label]=detail
            save(key+'-checkpoint',detail)
        need(sum(r['pdses'] for r in results.values())==42 and sum(r['members'] for r in results.values())==315 and
             sum(s['cases'] for r in results.values() for s in r['functional'].values())==80,'final acceptance counts differ')
        final = drive(rc3,media,folder,'final')
        need(final in ('EMPTY',IMAGE.name),'unexpected final tape state')
        if final==IMAGE.name:
            unmount('release-test')
        originals()
        need(sha(IMAGE)==tape_sha,'test image changed during installation')
        save('result',{'status':'PRIVATE_RELEASE_INTEGRATION_PASS','candidate':ID,'volser':VOL,'aws_sha256':tape_sha,'stage_job':staged,'write_job':wrote,'boot_job':bootjob,'profiles':results,'publication_authorized':False,'independent_mvs_system':False})
        rc3.seal(folder)
        print('INTEGRATION PASS: 42 PDSes/315 members; 24 regressions/56 demos; accepted tapes unchanged.')
        return 0
    except (Exception,KeyboardInterrupt) as exc:
        if folder is not None:
            try:
                save('failure',{'reason':str(exc),'no_retry':marked})
                rc3.seal(folder)
            except Exception:
                pass
        print('INTEGRATION HALTED: '+str(exc)+(' (NO RETRY)' if marked else ''),file=sys.stderr)
        return 2
    finally:
        if folder is not None:
            print('Evidence: '+str(folder.relative_to(ROOT)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    try:
        raise SystemExit(run(parser.parse_args().run))
    except (Exception,KeyboardInterrupt) as exc:
        print('INTEGRATION REFUSED: '+str(exc),file=sys.stderr)
        raise SystemExit(2)
