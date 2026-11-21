"""Offline fail-closed tests; no MVS/JES or Git remote access."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

PATH = Path(__file__).resolve().parents[1] / 'rc2-bt0021-stage-once.py'
spec = importlib.util.spec_from_file_location('rc2_bt21_stage_tests', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class StageOnceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.work = self.root / 'workarea'
        self.work.mkdir()
        self.pre = self.work / 'ta2-rc2-bt0021-preflight/20261121T051500Z-24489'
        self.pre.mkdir(parents=True)
        self.operations = self.work / 'stage-operations'
        self.marker = self.operations / 'BT0021-TSO002-one-shot-attempt.json'
        for name, path in [('ROOT',self.root),('WORK',self.work),('PREFLIGHT',self.pre),
                           ('OPERATIONS',self.operations),('MARKER',self.marker)]:
            p=patch.object(m,name,path);p.start();self.addCleanup(p.stop)
        self.result={'status':'READ_ONLY_MVS_TARGET_ABSENT_AND_VTOC_OBSERVED',
                     'candidate':'BCPL-0.1.0-rc2','volser':'BC0002',
                     'target':m.TARGET,'volume':m.VOLUME,
                     'source':'HERC02.BCPL.CAMBRIDG.SOURCE','mvs_source_job':9330,
                     'source_members':15,'source_records':6577,'stage_authorized':False,
                     'mvs_jobs':{'catalog':9331,'vtoc':9332},
                     'stage_deck_sha256':'f'*64}
        self.raw={'result.json':(json.dumps(self.result)+'\n').encode(),
                  'catalog-report.txt':b'LISTDS target absent',
                  'vtoc-report.txt':b'IEHLIST TSO002',
                  'catalog-summary.txt':b'JOB 9331 DSPALST\n',
                  'vtoc-summary.txt':b'JOB 9332 TA2VTOC\n'}
        for name,body in self.raw.items():(self.pre/name).write_bytes(body)
        self.reseal()
        self.core=SimpleNamespace(dataset_missing=Mock(return_value=True),
           extract_listds_block=Mock(return_value=[]),parse_listds=Mock(return_value={}))
        self.pf=SimpleNamespace(SOURCE='HERC02.BCPL.CAMBRIDG.SOURCE',
            catalog_absent=Mock())
        self.target=SimpleNamespace(vtoc_observation=Mock())

    def reseal(self):
        (self.pre/'SHA256SUMS').write_text(''.join(
            hashlib.sha256(body).hexdigest() + '  ' + name + '\n'
            for name,body in sorted(self.raw.items())))

    def acceptance(self):return m.sealed_preflight(self.pf,self.core,self.target)

    def approval(self,saved=None):
        if saved is None:saved=self.acceptance()
        return {'schema_version':1,'status':'OWNER_APPROVED_ONE_SHOT_BT0021_STAGING',
                'candidate':'BCPL-0.1.0-rc2','volser':'BC0002','volume':'TSO002',
                'source':'HERC02.BCPL.CAMBRIDG.SOURCE','target':m.TARGET,
                'historical_members':15,'source_records':6577,
                'source_byte_policy':'preserve-verified-hercules-translated-FB80-as-archival-source',
                'preflight_evidence':self.pre.relative_to(self.root).as_posix(),
                'preflight_jobs':{'catalog':9331,'vtoc':9332},
                'retry':False,'production_tape_authorized':False}

    def test_original_mvs_9331_9332_seal_passes(self):
        got=self.acceptance()
        self.assertEqual(got['receipt']['mvs_jobs'], {'catalog':9331,'vtoc':9332})
        self.pf.catalog_absent.assert_called_once()
        self.target.vtoc_observation.assert_called_once()

    def test_missing_or_mismatched_job_refused(self):
        self.result['mvs_jobs']['catalog']=9333
        self.raw['result.json']=(json.dumps(self.result)+'\n').encode()
        (self.pre/'result.json').write_bytes(self.raw['result.json']);self.reseal()
        with self.assertRaises(m.Refusal):self.acceptance()

    def test_changed_report_refused_before_stage(self):
        (self.pre/'vtoc-report.txt').write_text('tampered')
        with self.assertRaisesRegex(m.Refusal,'changed'):self.acceptance()

    def test_extra_file_refused(self):
        (self.pre/'new.txt').write_text('other')
        with self.assertRaisesRegex(m.Refusal,'set changed'):self.acceptance()

    def test_symlink_refused(self):
        (self.pre/'vtoc-report.txt').unlink()
        (self.pre/'vtoc-report.txt').symlink_to(self.pre/'catalog-report.txt')
        with self.assertRaises(m.Refusal):self.acceptance()

    def test_approved_exact_contract(self):
        self.assertIsNone(m.check_approval(self.approval(),self.acceptance(),'f'*64))

    def test_approval_refuses_writes_without_encoding_policy(self):
        approved=self.approval();approved['source_byte_policy']='cp037'
        with self.assertRaisesRegex(m.Refusal,'owner approval'):
            m.check_approval(approved,self.acceptance(),'f'*64)

    def test_approval_refuses_tape_authorization(self):
        approved=self.approval();approved['production_tape_authorized']=True
        with self.assertRaises(m.Refusal):m.check_approval(approved,self.acceptance(),'f'*64)

    def test_approval_refuses_wrong_deck_hash(self):
        with self.assertRaises(m.Refusal):m.check_approval(self.approval(),self.acceptance(),'0'*64)

    def test_approval_refuses_wrong_original_job_identity(self):
        approved=self.approval();approved['preflight_jobs']['catalog']=9334
        with self.assertRaises(m.Refusal):m.check_approval(approved,self.acceptance(),'f'*64)

    def test_one_shot_marker_blocks_second_operation(self):
        first=m.new_run()
        m.save(self.marker,b'{}')
        with self.assertRaisesRegex(m.Refusal,'already attempted'):m.new_run()
        self.assertTrue(first.exists())

    def test_stage_job_one_step_pass(self):
        summary='JOB 9333 TA2C21ST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\nS0021 IEBCOPY RC=0000\n'
        report='IEF142I TA2C21ST S0021 - STEP WAS EXECUTED - COND CODE 0000\n'
        self.assertEqual(m.validate_job(9333,summary,report)['mvs_job'],9333)

    def test_stage_job_second_step_refused(self):
        summary='JOB 9333 TA2C21ST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\nS0021 IEBCOPY RC=0000\nS0022 IEBCOPY RC=0000\n'
        report='IEF142I TA2C21ST S0021 - STEP WAS EXECUTED - COND CODE 0000\n'
        with self.assertRaises(m.Refusal):m.validate_job(9333,summary,report)

    def test_stage_job_nonzero_rc_or_abend_refused(self):
        summary='JOB 9333 TA2C21ST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0008\nS0021 IEBCOPY RC=0008\n'
        with self.assertRaises(m.Refusal):m.validate_job(9333,summary,'IEF142I ...')
        summary=summary.replace('0008','0000')
        with self.assertRaises(m.Refusal):m.validate_job(9333,summary,'ABEND')

    def test_material_body_exact_one_target(self):
        lines=['//* TA.2 RC2 DRAFT ONLY: NOT AUTHORIZED FOR MVS SUBMISSION.',
               '//* BT0001-BT0020 ARE ALREADY ACCEPTED; DO NOT RESTAGE.',
               '//* ONE NEW HISTORICAL PDS; FAIL CLOSED IF IT EXISTS.',
               '//S0021 EXEC PGM=IEBCOPY',
               '//OUTPDS DD DSN=HERC02.BCPL.TA2STG.BT0021,',
               '// DISP=(NEW,CATLG,DELETE)',
               *[' SELECT MEMBER=(BLIB)']*15,'//']
        draft='\n'.join(lines)+'\n'
        pf=SimpleNamespace(exact_release=Mock(return_value={'stage_deck_sha256':m.digest(draft.encode())}))
        stage=SimpleNamespace(render=Mock(return_value=draft))
        readiness=SimpleNamespace(source_manifest=Mock(return_value=({'datasets':[]},{'datasets':{}})))
        plan,body,sha=m.material_body(pf,stage,readiness,None,None)
        self.assertEqual(sha,plan['stage_deck_sha256'])
        self.assertIn('OWNER-GATED',body)
        self.assertNotIn('DRAFT ONLY',body)
        self.assertEqual(body.count(' SELECT MEMBER='),15)

    def test_missing_owner_approval_prevents_mvs_call(self):
        with patch('sys.stdin.isatty',return_value=True),patch.object(m,'git_committed',side_effect=m.Refusal('approval missing')) as git:
            with self.assertRaisesRegex(m.Refusal,'approval missing'):m.run()
            git.assert_called_once_with(m.APPROVAL)
        self.assertFalse(self.operations.exists())


if __name__=='__main__':unittest.main()
