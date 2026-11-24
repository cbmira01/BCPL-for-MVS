"""Offline release-driver tests. No GitHub writes, JES, Docker or tape I/O."""
from copy import deepcopy
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import io
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import shutil
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import yaml
import release as r
import mvs_release as mvs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
loader = SourceFileLoader('create_release_under_test', str(HERE/'create-release'))
cr = module_from_spec(spec_from_loader(loader.name,loader)); loader.exec_module(cr)


def registry():
    entries=[dict(candidate_id=f'BCPL-0.1.0-rc{n}',version=f'0.1.0-rc{n}',volser=f'BC{n:04d}',
                  source_commit='a'*40,manifest_sha256='b'*64,state='reserved') for n in range(1,5)]
    return dict(schema_version=1,candidates=entries,lifecycle={'BCPL-0.1.0-rc4':{'technical_state':'accepted-qualified'}},
                integration_tests={'BCPL-0.1.0-tooltest1':{'volser':'BC0005','state':'used-private-test-pass'}})


def registry_text():
    reg=registry(); tests=reg.pop('integration_tests'); lifecycle=reg.pop('lifecycle')
    # YAML's indentless list format is not the canonical file's format.
    lines=['schema_version: 1','candidates:']
    for entry in reg['candidates']:
        lines.append('  - '+ '\n    '.join(f'{k}: {v}' for k,v in entry.items()))
    return ('\n'.join(lines)+'\n\n# Lifecycle annotations preserve the original reservation contract above.\n'+
            yaml.safe_dump({'lifecycle':lifecycle},sort_keys=False)+
            '\n# Private, non-publication tool verification volumes. Preserve permanently;\n'+
            yaml.safe_dump({'integration_tests':tests},sort_keys=False))


class ReleaseDriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); dist=self.root/'packaging/distribution'; manifests=dist/'manifest/releases'
        manifests.mkdir(parents=True); (dist/'registry').mkdir(); (dist/'create-tape').mkdir()
        base=manifests/'BCPL-0.1.0-rc4.yaml'; shutil.copyfile(ROOT/'packaging/distribution/manifest/releases'/base.name,base)
        budget=dist/'create-tape/ta2-stage-space-proposal-20261119.json'
        shutil.copyfile(ROOT/'packaging/distribution/create-tape'/budget.name,budget)
        shutil.copyfile(ROOT/'LICENSE.md',self.root/'LICENSE.md')
        reg=dist/'registry/releases.yaml'; reg.write_text(registry_text())
        work=self.root/'workarea'; work.mkdir(); out=work/'create-release'; out.mkdir(); tapes=self.root/'mvs-state/tape'; tapes.mkdir(parents=True)
        self.paths=patch.multiple(cr,ROOT=self.root,DIST=dist,MANIFESTS=manifests,BASE=base,REGISTRY=reg,WORK=work,OUT=out,TAPES=tapes)
        self.paths.start(); self.addCleanup(self.paths.stop)
        self.evidence=work/'prepared'; self.evidence.mkdir()
        self.input={'mode':'prepared','source_commit':'a'*40,'sources':{str(n):f'HERC02.BCPL.PREP.BT{n:04d}' for n in range(4,22)},
                    'allocations':cr.allocation_budget(),'evidence':'workarea/prepared'}
        (self.evidence/'prepared-inputs.json').write_text(json.dumps({k:v for k,v in self.input.items() if k!='evidence'}))
        (self.evidence/'report.txt').write_text('synthetic source preparation receipt\n'); mvs.seal(self.evidence)
        self.input['evidence_seal_sha256']=cr.digest(self.evidence/'SHA256SUMS')
        self.manifest=cr.build_manifest(registry(),self.input)

    def test_next_identity(self):
        self.assertEqual(cr.next_identity(registry()),('BCPL-0.1.0-rc5','BC0006'))
        self.assertEqual(cr.next_identity(registry(),'0.2.0-rc1'),('BCPL-0.2.0-rc1','BC0006'))
        reg=registry(); reg['integration_tests']['failed']={'volser':'BC0088'}
        self.assertEqual(cr.next_identity(reg)[1],'BC0089')
        reg['integration_tests']['failed']['volser']='BC9999'
        with self.assertRaises(r.Refusal): cr.next_identity(reg)

    def test_protected_images(self):
        reg=registry(); reg['lifecycle']['BCPL-0.1.0-rc4'].update(volser='BC0004',aws_sha256=cr.ORIGINALS['bcpl-0.1.0-rc4-BC0004.aws'])
        self.assertEqual(cr.protected_images(reg),cr.ORIGINALS)
        reg['lifecycle']['BCPL-0.1.0-rc4']['aws_sha256']='f'*64
        with self.assertRaises(r.Refusal): cr.protected_images(reg)

    def test_registry_conflicts(self):
        reg=registry(); reg['integration_tests']['BCPL-0.1.0-tooltest1']['volser']='BC0004'
        with self.assertRaises(r.Refusal): cr.next_identity(reg)
        with self.assertRaises(r.Refusal): cr.next_identity(registry(),'0.1.0-rc4')
        with self.assertRaises(r.Refusal): cr.next_identity(registry(),'0.1.0')

    def test_reservation_immutable(self):
        data=yaml.safe_dump(self.manifest,sort_keys=False).encode(); entry=cr.new_entry(self.manifest,data)
        old=registry_text(); new=cr.append_reservation(old,entry)
        expected=registry(); expected['candidates'].append(entry)
        self.assertEqual(yaml.safe_load(new),expected)
        self.assertEqual(cr.check_reservation(expected,self.manifest,data),'BC0006')
        with self.assertRaises(r.Refusal): cr.check_reservation(expected,self.manifest,data+b'\n')
        expected['lifecycle'][entry['candidate_id']]={'technical_state':'failed'}
        with self.assertRaises(r.Refusal): cr.check_reservation(expected,self.manifest,data)

    def test_input_seal_and_binding(self):
        with patch.object(cr,'git',return_value='same'):
            cr.check_inputs(self.input)
            wrong=deepcopy(self.input); wrong['sources']['4']='HERC02.BCPL.OTHER.BT0004'
            with self.assertRaises(r.Refusal): cr.check_inputs(wrong)
            (self.evidence/'report.txt').write_text('changed')
            with self.assertRaises(r.Refusal): cr.check_inputs(self.input)

    def test_input_scope(self):
        for key,value in [('mode','unknown'),('source_commit','main'),('sources',{}),('allocations',{}),('secret','do not embed')]:
            bad=deepcopy(self.input); bad[key]=value
            with self.subTest(key=key),self.assertRaises((r.Refusal,KeyError)): cr.check_inputs(bad,check_evidence=False)

    def test_materials(self):
        p=cr.materials(self.manifest)
        self.assertEqual(len(p['targets']),45); self.assertEqual(len(set(p['targets'])),45)
        self.assertEqual(p['stage'],'HERC02.BCPL.R0006ST.')
        self.assertEqual(p['writer'].count(' SELECT MEMBER='),150)
        self.assertEqual(p['writer'].count('LABEL=('),21)
        self.assertEqual(p['writer'].count('SER=BC0006'),21)
        self.assertEqual(set(p['docs']),set(cr.DOC_MEMBERS))
        self.assertIn('LABEL=(2,SL)',p['boot']); self.assertIn('SER=BC0006',p['members']['RESTORE'])
        self.assertIn('Permission is hereby granted',p['docs']['LICENSE'])
        for text in [p['boot'],*p['docs'].values(),*p['members'].values()]:
            self.assertTrue(all(line.isascii() and len(line)<=80 for line in text.splitlines()))
            self.assertNotIn('BC0004',text)
        for name,_,rows,body in p['profiles'].values():
            self.assertTrue(name.startswith('HERC02.BCPL.R0006'))
            self.assertIn('SER=BC0006',body)
        docs=cr.docs_deck(p); stage=mvs.stage_deck(p['boot'],p['members'],stage=p['stage'],dasd=cr.DASD)
        for deck,alloc,steps in [(docs,1,7),(stage,2,9)]:
            outer='\n'.join(mvs.jcl_control_cards(deck.splitlines()))
            self.assertEqual(outer.count('DISP=(NEW,CATLG,DELETE)'),alloc)
            self.assertEqual(outer.count('EXEC PGM=IEBGENER'),steps)
        self.assertEqual(docs.count('DSN=HERC02.BCPL.R0006ST.BT0003('),7)

    def test_manifest_scope(self):
        for edit in ('native','source','selection','extra','collision'):
            m=deepcopy(self.manifest)
            if edit=='native': m['release']['native_compiler']='included'
            if edit=='source': m['release']['source_commit']='b'*40
            if edit=='selection': m['datasets'][3]['members'].pop()
            if edit=='extra': m['unexpected']='value'
            if edit=='collision': m['producer_inputs']['sources']['4']='HERC02.BCPL.R0006ST.BT0003'
            with self.subTest(edit=edit),self.assertRaises(r.Refusal): cr.materials(m)

    def test_prepare_and_reserve(self):
        inputs=self.root/'inputs.json'; inputs.write_text(json.dumps(self.input))
        args=SimpleNamespace(reuse_rc4=False,inputs=inputs,version=None)
        with patch.object(cr,'clean_main',return_value='a'*40),patch.object(cr,'git',return_value='same'),redirect_stdout(io.StringIO()):
            cr.prepare(args); draft=cr.OUT/'BCPL-0.1.0-rc5-BC0006-reservation'
            self.assertEqual(yaml.safe_load(cr.REGISTRY.read_text()),registry())
            self.assertTrue((draft/'SHA256SUMS').is_file())
            with patch.object(cr,'confirm',return_value=False): cr.reserve(draft)
            self.assertFalse((cr.MANIFESTS/'BCPL-0.1.0-rc5.yaml').exists())
            with patch.object(cr,'confirm',return_value=True): cr.reserve(draft)
            target=cr.MANIFESTS/'BCPL-0.1.0-rc5.yaml'
            self.assertEqual(cr.check_reservation(cr.read_registry(),r.read_manifest(target),target.read_bytes()),'BC0006')
            with self.assertRaises(r.Refusal): cr.reserve(draft)

    def test_inquiry_termination(self):
        for name in ('DSPALST','DSPALLS'):
            deck=f'//{name} JOB X\n//             USER=X\n//             MSGLEVEL=(1,1)\n//SYSIN DD *\n LISTDS X LABEL\n/*\n'
            self.assertEqual(mvs.deck_without_job(deck,name),'//SYSIN DD *\n LISTDS X LABEL\n/*\n//\n')
            self.assertEqual(mvs.deck_without_job(deck+'//\n',name),mvs.deck_without_job(deck,name))
            with self.assertRaises(r.Refusal): mvs.deck_without_job(deck.replace('/*\n',''),name)

    def test_package_and_record(self):
        data=yaml.safe_dump(self.manifest,sort_keys=False).encode(); path=cr.MANIFESTS/'BCPL-0.1.0-rc5.yaml'; path.write_bytes(data)
        cr.REGISTRY.write_text(cr.append_reservation(cr.REGISTRY.read_text(),cr.new_entry(self.manifest,data)))
        folder=cr.OUT/'result-fixture'; folder.mkdir(); image=cr.TAPES/'bcpl-0.1.0-rc5-BC0006.aws'; image.write_bytes(b'fixture-not-real-aws')
        profiles={k:dict(pdses=p,members=n,functional=({s:{'cases':v} for s,v in zip(('language','bcpl','regression'),(11,17,12))} if k!='NATIVE' else {}))
                  for k,p,n in [('MR10',11,94),('NATIVE',11,71),('COMBINED',20,150)]}
        result=dict(candidate='BCPL-0.1.0-rc5',volser='BC0006',source_commit='a'*40,producer_commit='c'*40,
                    aws_sha256=cr.digest(image),profiles=profiles,status='PRIVATE_CANDIDATE_VERIFIED_QUALIFIED',publication_authorized=False)
        notices={n:b'notice fixture' for n in cr.NOTICE_FILES}
        archive,sha=cr.package(folder,path,data,image,result,notices)
        with ZipFile(archive) as z:
            self.assertEqual(z.read(image.name),image.read_bytes()); self.assertEqual(z.read(path.name),data)
            self.assertIn(b'BC0006',z.read('README.md'))
            for line in z.read('SHA256SUMS').decode().splitlines():
                checksum,name=line.split('  '); self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),checksum)
        result.update(archive=archive.name,archive_sha256=sha)
        (folder/'result.json').write_text(json.dumps(result)); rel='workarea/create-release/result-fixture'
        proposed=dict(candidate_id=result['candidate'],technical_state='verified-qualified-pending-owner-review',volser=result['volser'],
                      aws_sha256=result['aws_sha256'],archive_sha256=sha,private_evidence=rel,publication_authorized=False)
        (folder/'proposed-lifecycle.json').write_text(json.dumps(proposed)); mvs.seal(folder)
        (cr.OUT/'BC0006-no-retry.json').write_text(json.dumps(dict(candidate=result['candidate'],evidence=rel,head='c'*40)))
        with patch.object(cr,'clean_main',return_value='c'*40),patch.object(cr,'confirm',return_value=True),redirect_stdout(io.StringIO()):
            cr.record(folder)
            self.assertEqual(cr.read_registry()['lifecycle'][result['candidate']]['publication_authorized'],False)
            with self.assertRaises(r.Refusal): cr.record(folder)


    def simulate_run(self, *, approve=True, fail_write=False):
        """Exercise driver wiring with synthetic transport; not MVS acceptance."""
        plan=cr.materials(self.manifest); cid='BCPL-0.1.0-rc5'; vol='BC0006'
        path=cr.MANIFESTS/(cid+'.yaml'); data=yaml.safe_dump(self.manifest).encode()
        image=cr.TAPES/'bcpl-0.1.0-rc5-BC0006.aws'
        jcl=cr.ROOT/'mr10-kit-compiler/jcl'; jcl.mkdir(parents=True)
        suite='//S1 EXEC PGM=ICINT19\n//\n'
        for _,_,name,_,_ in cr.SUITES: (jcl/name).write_text(suite)
        cfg={'mvs':{'hlq':'HERC02','batch_user':'HERC02'},'runtime':{'docker_container':'mvs38j','reader_host':'127.0.0.1',
             'reader_port':3505,'hercules_host':'127.0.0.1','hercules_port':8038,'printer':'mvs-state/prt/prt00e.txt'}}
        for name in cr.NOTICE_FILES:
            p=cr.ROOT/name; p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists(): p.write_text('synthetic notice\n')
        core=SimpleNamespace(load_config=lambda:cfg,require_reader_ready=lambda cfg:None,stat_deck=lambda cfg,names:
            '//DSPALST JOB X\n//             USER=X\n//             MSGLEVEL=(1,1)\n//SYSIN DD *\n/*\n',
            dataset_missing=lambda report,name:True,extract_listds_block=lambda report,name:[],batch_password=lambda cfg:'password')
        vtoc=SimpleNamespace(inspect_vtoc=lambda report,volume,names:{'iehlist_reported_free_total_tracks':8000})
        state={'mounted':False,'jobs':[],'commands':[]}
        def fake_job(core,cfg,folder,key,name,body,expected,max_rc=0,**kwargs):
            state['jobs'].append(key); report='synthetic report'
            if key=='write' and fail_write: raise RuntimeError('synthetic write failure')
            if key=='boot': report=plan['boot']
            for label,(_,_,_,canonical) in plan['profiles'].items():
                if key==label.lower()+'-view': report=canonical+' COPY OUTDD=OUTPDS,INDD=INTAPE\n'
                if key.startswith(label.lower()+'-doc-'): report=plan['docs'][key.split('-doc-')[1]]
            if key.startswith('stage-doc-'): report=plan['docs'][key[len('stage-doc-'):]]
            if key.endswith('-read'): report=suite
            return len(state['jobs']),report,'JOB RESULT: SUCCESS'
        def fake_command(folder,key,args):
            state['commands'].append(key)
            if key.endswith('-hercules'):
                return 'HHC02279I 0480 3420 '+('/tk5/tape/'+image.name if state['mounted'] else '* EMPTY')+'\n'
            if key.endswith('-mvs'): return '480 3400 '+('O' if state['mounted'] else 'O-NRD')+'\n'
            if key.endswith('-mount'): state['mounted']=True
            if key=='unmount': state['mounted']=False
            if key=='initialize': image.write_bytes(b'fixture-aws')
            return 'synthetic command result'
        with ExitStack() as stack:
            def mock(obj,name,**kwargs): return stack.enter_context(patch.object(obj,name,**kwargs))
            mock(cr,'clean_main',return_value='c'*40); mock(cr,'valid_plan',return_value=(path,data,self.manifest,vol,plan))
            mock(cr,'originals'); mock(cr,'check_docker'); mock(cr,'confirm',return_value=approve)
            mock(cr,'load',side_effect=[core,object(),vtoc])
            mock(r,'read_mr10_panel',create=True,return_value=[{}]*12)
            mock(r,'evaluate_hetmap',create=True,return_value={'logical_datasets':21,'physical_files':64})
            mock(r,'inspect_mr10',create=True,return_value={'exp_contract_met':True,'golden_rp_and_code_match':True})
            mock(mvs,'verify_inventory',side_effect=lambda core,cfg,ls,folder,label,rows,volume:(1,2,sum(len(row[2]) for row in rows)))
            mock(mvs,'submit_job',side_effect=fake_job); mock(mvs,'run_command',side_effect=fake_command)
            mock(mvs,'exact_listds',return_value=({'volume':'TSO002','dsorg':'PS','recfm':'FB','lrecl':'80','blksize':'800'},[]))
            mock(mvs,'suite_deck',return_value=(suite,[('S1','ICINT19')]))
            mock(mvs,'profile_result',return_value=1); mock(mvs,'verify_demos',return_value={'synthetic':True})
            with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()): rc=cr.run(cid)
        folders=[p for p in cr.OUT.iterdir() if p.is_dir()]; self.assertEqual(len(folders),1)
        self.assertTrue((folders[0]/'SHA256SUMS').is_file())
        return rc,state,folders[0]

    def test_simulated_full_run(self):
        rc,state,folder=self.simulate_run()
        self.assertEqual(rc,0); self.assertFalse(state['mounted'])
        self.assertTrue((cr.OUT/'BC0006-no-retry.json').is_file())
        result=json.loads((folder/'result.json').read_text())
        self.assertEqual(result['status'],'PRIVATE_CANDIDATE_VERIFIED_QUALIFIED')
        self.assertEqual(sum(s['cases'] for p in result['profiles'].values() for s in p['functional'].values()),80)
        self.assertTrue((folder/result['archive']).is_file())
        self.assertFalse(result['publication_authorized'])

    def test_simulated_decline(self):
        rc,state,folder=self.simulate_run(approve=False)
        self.assertEqual(rc,0); self.assertNotIn('stage',state['jobs']); self.assertNotIn('initialize',state['commands'])
        self.assertFalse((cr.OUT/'BC0006-no-retry.json').exists())
        self.assertEqual(json.loads((folder/'result.json').read_text())['status'],'DECLINED_NO_WRITE')

    def test_simulated_write_failure(self):
        rc,state,folder=self.simulate_run(fail_write=True)
        self.assertEqual(rc,2); self.assertTrue((cr.OUT/'BC0006-no-retry.json').is_file())
        self.assertTrue(json.loads((folder/'failure.json').read_text())['no_retry'])
        self.assertFalse((folder/'result.json').exists())
        self.assertNotIn('boot',state['jobs'])

    def test_no_retry_guard(self):
        (cr.OUT/'BC0006-no-retry.json').write_text('{}')
        with patch.object(cr,'clean_main',return_value='a'*40),patch.object(cr,'valid_plan',return_value=(None,b'',self.manifest,'BC0006',{})),patch.object(cr,'load') as load:
            with self.assertRaises(r.Refusal): cr.run('BCPL-0.1.0-rc5')
            load.assert_not_called()


if __name__=='__main__': unittest.main()
