"""Synthetic gated BC0002 one-shot tape readback; no real MVS or tape operations."""
from __future__ import annotations
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ta2-rc2-readback-once'
loader=importlib.machinery.SourceFileLoader('ta2_rb_once_test',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def fake_rows():
    return [{'n':i,'target':f'HERC02.BCPL.TA2RB.BT{i:04d}',
             'source':f'HERC02.BCPL.TA2STG.BT{i:04d}',
             'dcb':{'dsorg':'PS' if i==1 else 'PO','recfm':'U' if i==12 else 'FB',
                    'lrecl':0 if i==12 else 80,'blksize':6144 if i==12 else 800},
             'members':[] if i==1 else ['M']} for i in range(1,22)]

def good_jes(job=9435):
    summary=f'JOB {job} TA2RC2RB\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
    summary+=''.join(f'R{i:04d} {"IEBGENER" if i==1 else "IEBCOPY"} RC=0000\n' for i in range(1,22))
    printer=''.join(f'IEF142I TA2RC2RB R{i:04d} - STEP WAS EXECUTED - COND CODE 0000\n' for i in range(1,22))
    return summary,printer

class TestOnce(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.work=self.root/'workarea';self.work.mkdir()
        self.rows=fake_rows()
    def test_release_identity_and_immutable_hash(self):
        self.assertEqual(mod.AWS_SHA,
            '123657b2feaeea739350853f8b8437ccb73b0e917442ddd3220589c7ae180375')
        self.assertEqual(mod.JCL_SHA,'226819ef3702234a1367c7a7df96399cf9fcaf32d99152061db1df98fed12e73')
        self.assertEqual(mod.VOLUME,'TSO002')
    def test_exact_21_step_ief142i_success(self):
        mod.check_job(9435,*good_jes())
    def test_ief142i_wrong_job_missing_step_and_bad_rc(self):
        s,p=good_jes()
        with self.assertRaises(mod.Refusal):mod.check_job(9434,s,p)
        with self.assertRaises(mod.Refusal):mod.check_job(9435,s,p.replace('R0021 - STEP','R2222 - STEP'))
        with self.assertRaises(mod.Refusal):mod.check_job(9435,s.replace('R0012 IEBCOPY RC=0000','R0012 IEBCOPY RC=0004'),p)
    def test_ief142i_abend_refusal(self):
        s,p=good_jes()
        with self.assertRaisesRegex(mod.Refusal,'ABEND'):mod.check_job(9435,s,p+'IEF450I ABEND S0C4\n')
    def test_original_preflight_receipt_must_be_exact(self):
        r={'status':'RC2_READBACK_READ_ONLY_MVS_PREFLIGHT_PASS',
           'catalog_job':9340,'vtoc_job':9341,'proposed_dasd_volume':'TSO002',
           'reported_free_tracks':15335,'target_datasets':[x['target'] for x in self.rows],
           'readback_jcl_sha256':mod.JCL_SHA,'hercules_drive_state':'EMPTY',
           'mvs_drive_state':'O-NRD','stateful_execution_authorized':False}
        evidence={'result.json':json.dumps(r).encode(),
                  'mounted-hercules.txt':b'empty',
                  'mounted-mvs.txt':b'MVS O-NRD',
                  'catalog-report.txt':b'LISTDS','vtoc-report.txt':b'IEHLIST'}
        def helper(name,path):
            if name=='ta2_rb_once_producer':return SimpleNamespace(sealed=lambda *a:evidence)
            raise AssertionError(name)
        plan=SimpleNamespace(device_identity=lambda raw:('EMPTY','*'),original_image=lambda:mod.AWS_SHA)
        with patch.object(mod,'load',side_effect=helper):
            mod.replay_accepted(plan,mod.JCL_SHA)
            r['reported_free_tracks']=0
            evidence['result.json']=json.dumps(r).encode()
            with self.assertRaisesRegex(mod.Refusal,'changed'):
                mod.replay_accepted(plan,mod.JCL_SHA)
    def test_approval_absent_before_even_consulting_mvs(self):
        with patch.object(mod,'APPROVAL',self.root/'missing.json'):
            with self.assertRaisesRegex(mod.Refusal,'CLOSED'):
                mod.verify_permission(mod.JCL_SHA)
    def test_busy_or_foreign_media_excluded(self):
        plan=SimpleNamespace(device_identity=lambda text:('FOREIGN_OR_UNRECOGNIZED','x'))
        with patch.object(mod,'report',return_value='foreign') as report:
            with self.assertRaisesRegex(mod.Refusal,'foreign'):
                mod.device(plan,SimpleNamespace(),self.root,'before')
            self.assertEqual(report.call_count,1)
    def test_empty_and_expected_device_states(self):
        for state,mvs_state in [('EMPTY','O-NRD'),('MOUNTED_BC0002','O')]:
            plan=SimpleNamespace(device_identity=lambda raw:(state,'x'))
            media=SimpleNamespace(parse_mvs=lambda raw:mvs_state)
            with patch.object(mod,'report',return_value='status'):
                self.assertEqual(mod.device(plan,media,self.root,'before'),state)
    def test_no_stateful_run_without_exact_git_approval(self):
        fakeplan=SimpleNamespace(original_image=lambda:mod.AWS_SHA)
        with patch.object(mod,'candidate',return_value=(fakeplan,self.rows,'//DECK\n',mod.JCL_SHA)):
            with patch.object(mod,'verify_permission',side_effect=mod.Refusal('no owner approval')):
                with patch.object(mod,'replay_accepted') as replay:
                    with self.assertRaisesRegex(mod.Refusal,'no owner'):
                        mod.run()
                    replay.assert_not_called()
    def test_evidence_exclusive_create_and_no_retry(self):
        marker=self.work/'intent.json'
        mod.save(marker,b'intent\n')
        with self.assertRaises(FileExistsError):mod.save(marker,b'retry\n')
        self.assertEqual(marker.read_bytes(),b'intent\n')
    def test_exact_mount_and_single_job_after_marker(self):
        source=SCRIPT.read_text()
        self.assertIn("['tools/mvs/mvs-console','--yes','tape','mount','0480',AWS.name]",source)
        self.assertLess(source.index('save(PERMANENT,'),source.index("if immediate=='EMPTY':"))
        self.assertIn('if immediate==\'EMPTY\':',source)
        self.assertNotIn("'tape','unmount'",source)
        self.assertNotIn("'hetinit'",source)
        self.assertNotIn("open(AWS,'wb'",source)
        self.assertIn("submit(core,config,auth,folder,'readback',0)",source)
    def test_readback_result_does_not_claim_content_equality(self):
        text=SCRIPT.read_text()
        self.assertIn("'member_contents_compared':False",text)
        self.assertIn("'publication_authorized':False",text)
    def test_jcl_generator_reused_not_duplicated(self):
        text=SCRIPT.read_text()
        self.assertIn('rows=plan.rows(plan.source())',text)
        self.assertIn('deck=plan.render(rows,VOLUME)',text)
        self.assertNotIn('def render(',text)
    def test_default_main_offline_when_plan_mocked(self):
        p=SimpleNamespace()
        with patch.object(mod,'candidate',return_value=(p,self.rows,'//TEST\n',mod.JCL_SHA)):
            with patch.object(mod,'run') as r:
                self.assertEqual(mod.main([]),0)
                r.assert_not_called()

if __name__=='__main__':unittest.main()
