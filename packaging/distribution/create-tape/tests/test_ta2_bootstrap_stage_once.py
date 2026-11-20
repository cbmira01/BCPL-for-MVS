"""TA.2 six-step MVS staging bounded tests (no JES, Docker or Git writes)."""
from __future__ import annotations
import hashlib
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
import json
import yaml
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-bootstrap-stage-once'
loader = SourceFileLoader('ta2_stage_synthetic', str(SRC))
spec = spec_from_loader(loader.name, loader)
mod = module_from_spec(spec)
loader.exec_module(mod)


class StageSafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.approval = {
          'schema_version':1, 'status':'OWNER_APPROVED_ONE_SHOT_BT0001_BT0002_STAGING',
          'volume':'TSO002','targets':list(mod.NAMES),
          'space':{'BT0001':{'primary':5,'secondary':1},
                   'BT0002':{'primary':20,'secondary':5,'directory':10}},
          'steps':6,'retry':False,
          'mvs_preflight_evidence':'workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572',
          'saved_review_evidence':'workarea/ta2-bootstrap-preflight-review/20261120T030402Z-20698',
          'production_tape_authorized':False,
        }
        self.manifest = {'release':{'candidate_id':'ABC','version':'0.1.0-rc1',
                                     'source_commit':'1'*40,'native_compiler':'absent'},
                         'volume':{'volser':'BC0001'}}
        self.identity = {
            'schema_version':1,'status':'OWNER_APPROVED_BOOTSTRAP_IDENTITY',
            'candidate_id':'ABC','version':'0.1.0-rc1','source_commit':'1'*40,
            'volser':'BC0001','manifest_sha256':'a'*64,'native_compiler':'absent',
            'production_tape_authorized':False,
        }
        self.material = {
          'BT0001': 'STAGE BOOTSTRAP',
          'INSTALL': 'INSTALL', 'DATASETS': 'DATASETS', 'RELEASE': 'RELEASE',
          'RESTORE': '//R0003 EXEC PGM=IEBCOPY\n/*\n//',
        }
        self.body = self.jcl()

    def jcl(self):
        lines = ['//* ALLOWED ONE-SHOT JCL']
        for idx,(step,pgm) in enumerate(mod.STEPS):
            lines.extend([f'//{step} EXEC PGM={pgm},COND=(0,NE)' if idx else f'//{step} EXEC PGM={pgm}',
                           f'//SYSUT1 DD DATA,DLM=ZZ' if pgm == 'IEBGENER' else '//DUMMY DD DUMMY'])
            if pgm == 'IEBGENER':
                lines.extend([self.material['RESTORE'] if step == 'M0004' else 'HELLO', 'ZZ'])
            if step=='B0001':
                lines.append('//SYSUT2 DD DSN='+mod.NAMES[0]+',')
                lines.append('//            DISP=(NEW,CATLG,DELETE)')
            if step=='B0002':
                lines.append('//OUTPDS DD DSN='+mod.NAMES[1]+',')
                lines.append('//            DISP=(NEW,CATLG,DELETE)')
        lines.append('//')
        return '\n'.join(lines)+'\n'

    def summary(self, job=9315, rc='0000'):
        return '\n'.join([f'JOB {job} TA2BTSTR', 'JOB RESULT: SUCCESS',
            'HIGHEST RC: 0000']+[f'{step} {pgm} RC={rc}' for step,pgm in mod.STEPS])+'\n'

    def report(self):
        return '\n'.join(f'IEF142I TA2BTSTR {step} - STEP WAS EXECUTED - COND CODE 0000'
                         for step,_ in mod.STEPS)+'\n'

    def test_exact_six_stage_programs(self):
        self.assertEqual(mod.STEPS, [('B0001','IEBGENER'),('B0002','IEFBR14'),
            ('M0001','IEBGENER'),('M0002','IEBGENER'),('M0003','IEBGENER'),('M0004','IEBGENER')])

    def test_approved_scope_and_identity_pass(self):
        mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_approval_cannot_grant_tape(self):
        self.approval['production_tape_authorized']=True
        with self.assertRaisesRegex(mod.Refusal,'scope'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_approval_cannot_be_retried(self):
        self.approval['retry']=True
        with self.assertRaisesRegex(mod.Refusal,'scope'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_approval_cannot_stage_more_datasets(self):
        self.approval['targets'].append('HERC02.BCPL.TA2STG.BT0003')
        with self.assertRaisesRegex(mod.Refusal,'scope'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_candidate_identity_must_be_separate_approval(self):
        self.identity['status']='PROPOSED'
        with self.assertRaisesRegex(mod.Refusal,'identity'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_candidate_manifest_digest_binds_identity(self):
        with self.assertRaisesRegex(mod.Refusal,'identity'):
            mod.load_approval(self.approval,self.identity,self.manifest,'b'*64)

    def test_candidate_manifest_release_drift(self):
        self.manifest['release']['candidate_id']='DIFFERENT'
        with self.assertRaisesRegex(mod.Refusal,'candidate_id'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_proposed_dcb_space_immutable(self):
        self.approval['space']['BT0002']['directory']=0
        with self.assertRaisesRegex(mod.Refusal,'scope'):
            mod.load_approval(self.approval,self.identity,self.manifest,'a'*64)

    def test_six_step_deck_safe_instream_data(self):
        mod.check_deck(self.body)

    def test_embedded_jcl_not_an_extra_execution_step(self):
        self.assertIn('//R0003 EXEC PGM=IEBCOPY',self.body)
        mod.check_deck(self.body)

    def test_stage_jcl_cannot_target_existing_pds(self):
        bad=self.body.replace('HERC02.BCPL.TA2STG.BT0001',
                              'HERC02.BCPL.TA2STG.BT0003')
        with self.assertRaisesRegex(mod.Refusal,'six approved'):
            mod.check_deck(bad)

    def test_stage_jcl_requires_5_instream_panels(self):
        with self.assertRaisesRegex(mod.Refusal,'six approved'):
            mod.check_deck(self.body.replace('DD DATA,DLM=ZZ','DD DUMMY',1))

    def test_stage_jcl_rejects_second_write_allocation(self):
        with self.assertRaisesRegex(mod.Refusal,'six approved'):
            mod.check_deck(self.body.replace('DISP=(NEW,CATLG,DELETE)',
                                             'DISP=(NEW,CATLG,DELETE)',1).replace(
                                             'DISP=(NEW,CATLG,DELETE)', 'DISP=OLD', 1))

    def test_stage_jcl_rejects_overwide_card(self):
        with self.assertRaisesRegex(mod.Refusal,'FB80-safe'):
            mod.check_deck(self.body+'X'*81+'\n')

    def test_stage_jcl_rejects_undelimited_payload(self):
        with self.assertRaisesRegex(mod.Refusal,'nested|unterminated'):
            mod.check_deck(self.body.replace('ZZ\n//SYSUT2','ZZZ\n//SYSUT2',1))

    def test_authenticated_deck_not_written_to_disk(self):
        core = types.SimpleNamespace(authenticated_job_card=Mock(return_value=[
            "//TA2BTSTR JOB (BCPL),'STAGE',CLASS=A,MSGCLASS=A,",
            '//           USER=USER01,PASSWORD=SECRET']))
        deck=mod.authenticated_deck(core,{},self.body)
        self.assertIn('PASSWORD=SECRET',deck)
        self.assertTrue(deck.endswith('//\n'))

    def test_six_step_mvs_rc_success(self):
        r=mod.validate_job(9315,self.summary(),self.report())
        self.assertEqual((r['steps'],r['status']),(6,'SIX_STEP_MVS_STAGING_RC0000_DIRECTORY_PENDING'))

    def test_step_failure_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'all six'):
            mod.validate_job(9315,self.summary(rc='0004'),self.report())

    def test_duplicate_ief142_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'duplicate'):
            mod.validate_job(9315,self.summary(),self.report()+self.report().splitlines()[0]+'\n')

    def test_wrong_jobname_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'job/RC'):
            mod.validate_job(9315,self.summary().replace('TA2BTSTR','OTHER'),self.report())

    def test_report_abend_refused(self):
        with self.assertRaisesRegex(mod.Refusal,'ABEND'):
            mod.validate_job(9315,self.summary(),self.report()+'IEA995I ABEND\n')

    def test_one_shot_marker_exclusive(self):
        with patch.object(mod, 'MARKER', self.root/'intent.json'):
            mod.save_json(mod.MARKER,{'state':'SUBMISSION_INTENT_NO_RETRY'})
            with self.assertRaises(FileExistsError):
                mod.save_json(mod.MARKER,{'state':'SUBMISSION_INTENT_NO_RETRY'})

    def test_saved_review_binds_exact_evidence(self):
        with patch.object(mod, 'PREFLIGHT', self.root/'orig'):
            (self.root/'orig').mkdir()
            (self.root/'orig'/'SHA256SUMS').write_text('sealed')
            orig={'jobs':{'catalog':9313,'vtoc':9314},'volume':'TSO002','targets':list(mod.NAMES)}
            review={'status':'READ_ONLY_SAVED_MVS_REVIEW_PASS','source_evidence':'orig',
                'source_seal_sha256':hashlib.sha256(b'sealed').hexdigest(),
                'volume':'TSO002','targets':list(mod.NAMES),'jobs':orig['jobs'],
                'iehlist_reported_free_tracks':15400,'proposed_track_budget':31}
            with patch.object(mod, 'ROOT', self.root):
                # Source path is relative to the mock repository root.
                mod.check_saved_review(review,orig)
                review['iehlist_reported_free_tracks']=42
                with self.assertRaisesRegex(mod.Refusal,'checkpoint'):
                    mod.check_saved_review(review,orig)

    def _simulated_live(self, failing=False):
        """Synthetic full guard -> fresh MVS inquiry -> one irreversible intent."""
        work=self.root/'workarea'; work.mkdir()
        stage=work/'ta2-bootstrap-stage-operations'
        stage.mkdir()
        candidate_dir=self.root/'packaging/distribution/manifest/releases'
        candidate_dir.mkdir(parents=True)
        mf=candidate_dir/'ABC.yaml'
        manifest_raw=yaml.safe_dump(self.manifest,sort_keys=False).encode()
        mf.write_bytes(manifest_raw)
        self.identity['manifest_sha256']=mod.sha(manifest_raw)
        design=self.root/'design.yaml';design.write_text('{}')
        stage_approval=self.root/'approval.json';stage_approval.write_text(json.dumps(self.approval))
        identity_approval=self.root/'identity.json';identity_approval.write_text(json.dumps(self.identity))
        origreview=work/'ta2-bootstrap-preflight-review/20261120T030402Z-20698'
        origreview.mkdir(parents=True)
        origflight=work/'ta2-bootstrap-target-preflight/20261120T025333Z-20572'
        origflight.mkdir(parents=True)
        (origreview/'SHA256SUMS').write_text('original seal')
        module_paths=[mod.STAGE_APPROVAL,mod.IDENTITY_APPROVAL]
        core=types.SimpleNamespace(load_config=Mock(return_value={'mvs':{'hlq':'HERC02'}}),
            require_reader_ready=Mock(), authenticated_job_card=Mock(return_value=[
                "//TA2BTSTR JOB (BCPL),'BT STAGE',CLASS=A,MSGCLASS=A,",
                '//           USER=U,PASSWORD=SECRET']),
            submit_and_wait=Mock(side_effect=RuntimeError('MVS failure') if failing else None,
                                 return_value=(9315,self.summary())),
            job_report=Mock(return_value=self.report()))
        def fresh(core,config,target,folder):
            (folder/'catalog-report.txt').write_text('catalog absent')
            (folder/'vtoc-report.txt').write_text('TSO002 15000 free tracks')
            return {'status':'GOOD'}
        preflight=types.SimpleNamespace(inquire=Mock(side_effect=fresh),seal=mod.seal)
        vparser=types.SimpleNamespace(inspect_vtoc=Mock(return_value={
            'iehlist_reported_free_total_tracks':15000,
            'staging_names_in_formatted_vtoc':0}))
        generator=types.SimpleNamespace(validate=Mock(),render=Mock(return_value={
            'STAGE-NEW-BT0001-BT0002.jcl':self.body.encode(),
            'materials.json':b'{"test":"material"}'
        }))
        modules=[generator,core,preflight,types.SimpleNamespace(),vparser]
        def import_tool(name,path): return modules.pop(0)
        def committed(path):
            if path.name==stage_approval.name: return stage_approval.read_bytes()
            if path.name==identity_approval.name: return identity_approval.read_bytes()
            if path==mf:return manifest_raw
            raise AssertionError('unexpected committed path '+str(path))
        patches=[patch.object(mod,'ROOT',self.root),patch.object(mod,'STAGE_APPROVAL',stage_approval),
            patch.object(mod,'IDENTITY_APPROVAL',identity_approval),
            patch.object(mod,'RELEASES',candidate_dir),
            patch.object(mod,'DESIGN',design),
            patch.object(mod,'OPERATIONS',stage),
            patch.object(mod,'MARKER',stage/'TA2BT-TSO002-one-shot-attempt.json'),
            patch.object(mod,'REVIEW',origreview),
            patch.object(mod,'PREFLIGHT',origflight),
            patch.object(mod,'git_committed',side_effect=committed),
            patch.object(mod,'review_original',return_value={}),
            patch.object(mod,'import_script',side_effect=import_tool),
            patch.object(mod.sys.stdin,'isatty',return_value=True),
            patch('builtins.input',return_value='y')]
        for obj in patches: obj.start()
        try: rc=mod.run_guarded(mf)
        finally:
            for obj in reversed(patches):obj.stop()
        return rc,stage,core

    def test_synthetic_mvs_one_shot_execution_pass(self):
        rc,stage,core=self._simulated_live()
        self.assertEqual(rc,0)
        self.assertEqual(core.submit_and_wait.call_count,1)
        self.assertEqual(core.job_report.call_count,1)
        marker=json.loads((stage/'TA2BT-TSO002-one-shot-attempt.json').read_text())
        self.assertEqual(marker['state'],'SUBMISSION_INTENT_NO_RETRY')
        run=next(x for x in stage.iterdir() if x.is_dir())
        self.assertEqual(json.loads((run/'stage-result.json').read_text())['steps'],6)
        self.assertTrue((run/'SHA256SUMS').exists())
        self.assertTrue((run/'preflight'/'SHA256SUMS').exists())
        self.assertFalse(any(b'SECRET' in p.read_bytes() for p in run.rglob('*') if p.is_file()))

    def test_synthetic_mvs_failure_retains_irreversible_marker(self):
        rc,stage,core=self._simulated_live(failing=True)
        self.assertEqual(rc,2)
        self.assertEqual(core.submit_and_wait.call_count,1)
        self.assertTrue((stage/'TA2BT-TSO002-one-shot-attempt.json').is_file())
        run=next(x for x in stage.iterdir() if x.is_dir())
        self.assertFalse((run/'stage-result.json').exists())
        self.assertEqual(json.loads((run/'failure.json').read_text())['state'],
                         'STOP_NO_RETRY')

    def test_plan_does_not_contact_mvs(self):
        with patch.object(mod, 'import_script', side_effect=AssertionError('MVS unexpectedly contacted')):
            self.assertEqual(mod.main([]),0)

    def test_run_refuses_without_manifest(self):
        self.assertEqual(mod.main(['--run']),2)


if __name__=='__main__':
    unittest.main()
