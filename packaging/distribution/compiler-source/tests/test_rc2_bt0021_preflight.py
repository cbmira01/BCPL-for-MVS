"""Test the TA.2 BT0021 one-target read-only gate without using MVS."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / 'rc2-bt0021-preflight.py'
spec = importlib.util.spec_from_file_location('rc2_bt21_tests', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class BT21ReadOnly(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=mod.ROOT / 'workarea')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'fake-repository'
        self.root.mkdir()
        self.work = self.root / 'workarea'
        self.work.mkdir()
        self.saved = self.work / 'ta2-rc2-cambsource-qsam-fidelity'
        self.saved.mkdir()
        self.reconciliation = self.work / 'ta2-rc2-cambsource-qsam-transport-reconciliation'
        self.reconciliation.mkdir()
        self.evidence = self.root / 'workarea/ta2-rc2-bt0021-preflight'
        patches=[patch.object(mod,'ROOT',self.root),patch.object(mod,'WORK',self.work),
                 patch.object(mod,'OUT',self.evidence),patch.object(mod,'ORIGINAL',self.saved),
                 patch.object(mod,'RECONCILED',self.reconciliation/'receipt.json')]
        for p in patches:p.start();self.addCleanup(p.stop)
        self.folder = self.evidence / 'preflight'
        self.folder.mkdir(parents=True)
        self.saved_receipt = dict(candidate='BCPL-0.1.0-rc2', mvs_job=9330,
            population_jobs=[9325,9326],status='reader-profile-reconciled',
            source_records=6577,original_cp037_pass=7,reader_profile_pass=15,
            observed_reader_overrides_hex={'|':'6A','[':'AD',']':'BD'},
            members=[{'reader_profile_match':True} for _ in range(15)])
        (self.reconciliation/'receipt.json').write_text(json.dumps(self.saved_receipt))
        (self.saved/'receipt.json').write_text(json.dumps({'status':'mismatch'}))
        (self.saved/'mvs-job-report.txt').write_text('MVS job evidence')
        (self.saved/'job-summary.txt').write_text('GO steps all RC0000')

    def test_reconciled_15_members_pass(self):
        mod.check_reconciliation(self.saved_receipt,dict(self.saved_receipt))

    def test_bad_9330_identity_fails(self):
        receipt=dict(self.saved_receipt,mvs_job=9331)
        with self.assertRaises(mod.Refusal):mod.check_reconciliation(receipt,receipt)

    def test_bad_encoding_fails(self):
        receipt=dict(self.saved_receipt,observed_reader_overrides_hex={'|':'4F'})
        with self.assertRaises(mod.Refusal):mod.check_reconciliation(receipt,receipt)

    def test_bad_member_count_fails(self):
        receipt=dict(self.saved_receipt,members=self.saved_receipt['members'][:-1])
        with self.assertRaises(mod.Refusal):mod.check_reconciliation(receipt,receipt)

    def test_original_replay_mismatch_fails(self):
        receipt=dict(self.saved_receipt)
        with self.assertRaisesRegex(mod.Refusal,'differs'):
            mod.check_reconciliation(receipt,dict(receipt,important_limit='changed'))

    def test_original_only_under_workarea_and_no_symlink(self):
        good=mod.read_original(self.saved/'receipt.json',self.saved)
        self.assertIn(b'"mismatch"',good)
        evil=self.saved/'ref'
        evil.symlink_to(self.saved/'receipt.json')
        with self.assertRaises(mod.Refusal):mod.read_original(evil,self.saved)

    def test_catalog_positive_absence(self):
        core=SimpleNamespace(dataset_missing=Mock(return_value=True),
          extract_listds_block=Mock(return_value=[]),parse_listds=Mock(return_value={}))
        mod.catalog_absent(core,'MVS LISTDS')
        core.dataset_missing.assert_called_once_with('MVS LISTDS', mod.TARGET)

    def test_catalog_contradiction_fails(self):
        core=SimpleNamespace(dataset_missing=Mock(return_value=True),
          extract_listds_block=Mock(return_value=['attrs']),
          parse_listds=Mock(return_value={'volume':'TSO002'}))
        with self.assertRaises(mod.Refusal):mod.catalog_absent(core,'MVS')

    def test_catalog_not_confirmed_fails(self):
        core=SimpleNamespace(dataset_missing=Mock(return_value=False),
          extract_listds_block=Mock(return_value=[]),parse_listds=Mock(return_value={}))
        with self.assertRaises(mod.Refusal):mod.catalog_absent(core,'MVS')

    def test_exact_release_replays_original_evidence(self):
        names=('BCPL','BLIB','CG','CGHDR','EDITMAIN','IOS','LIBHDR',
               'PM','SYN','SYNHDR','TRN','TRNHDR','MAKEOBJ','MAKELIB','PROGRAM')
        fake_manifest={'release':{'candidate_id':'BCPL-0.1.0-rc2',
                       'native_compiler':'absent'},'volume':{'volser':'BC0002'},
                       'datasets':[{}]*20+[{'members':list(names)}]}
        fake_dspal={'datasets':{'CAMB_SOURCE':{'members':{name:'archive/'+name for name in names}}}}
        fake_deck='//OUTPDS DD DSN='+mod.TARGET+'\n//S0021 EXEC PGM=IEBCOPY\n'+(' SELECT MEMBER=(BCPL)\n'*15)+'// DISP=(NEW,CATLG,DELETE)\n'
        source=SimpleNamespace(source_manifest=Mock(return_value=(fake_manifest,fake_dspal)),
                               EXPECTED_DSN=mod.SOURCE,check_frozen_source=Mock(return_value=b'X\n'))
        qsam=SimpleNamespace(NAMES=names,expected_records=Mock(return_value={'BCPL':{}}),
                             summary_steps=Mock(),parse_report=Mock(return_value=[{'member':'BCPL'}]))
        reconciler=SimpleNamespace(MEMBER_NAMES=names,reconcile=Mock(return_value=self.saved_receipt))
        stage=SimpleNamespace(render=Mock(return_value=fake_deck))
        result=mod.exact_release(stage,source,qsam,reconciler)
        self.assertEqual(result['source_records'],6577)
        self.assertFalse(result['stage_authorized'])
        self.assertEqual(source.check_frozen_source.call_count,15)
        stage.render.assert_called_once_with(fake_manifest,fake_dspal,volume='TSO002')

    def test_mvs_inquiry_two_jobs_only(self):
        core=SimpleNamespace(require_reader_ready=Mock(),
            stat_deck=Mock(return_value='//JOB EXEC PGM=IKJEFT01\n//'),
            submit_and_wait=Mock(side_effect=[(9331,'first MVS summary'),(9332,'second MVS summary')]),
            job_report=Mock(side_effect=['LISTDS missing','TSO002 IEHLIST']),
            dataset_missing=Mock(return_value=True),
            extract_listds_block=Mock(return_value=[]), parse_listds=Mock(return_value={}))
        target=SimpleNamespace(vtoc_deck=Mock(return_value='//VTOC EXEC PGM=IEHLIST\n//'),
                               vtoc_observation=Mock())
        with patch.object(mod,'query_codepage',return_value='unavailable-not-verified'):
            result=mod.live_inquiry(core,target,{'mvs':{'hlq':'HERC02'}},
                                    self.folder,{'stage_authorized':False})
        self.assertEqual(result['mvs_jobs'],{'catalog':9331,'vtoc':9332})
        self.assertFalse(result['stage_authorized'])
        self.assertEqual(core.submit_and_wait.call_count,2)
        self.assertEqual([c.kwargs['max_rc'] for c in core.submit_and_wait.call_args_list],[8,0])
        self.assertTrue((self.folder/'catalog-report.txt').is_file())
        self.assertTrue((self.folder/'vtoc-report.txt').is_file())

    def test_wrong_mvs_hlq_refused_before_io(self):
        core=SimpleNamespace(require_reader_ready=Mock())
        with self.assertRaises(mod.Refusal):
            mod.live_inquiry(core,None,{'mvs':{'hlq':'OTHER'}},self.folder,{})
        core.require_reader_ready.assert_not_called()

    def test_evidence_seal_and_overwrite_refusal(self):
        mod.save(self.folder,'run.json',b'{}\n')
        mod.seal(self.folder)
        expected=hashlib.sha256(b'{}\n').hexdigest()
        self.assertIn(expected,(self.folder/'SHA256SUMS').read_text())
        with self.assertRaises(FileExistsError):mod.save(self.folder,'run.json',b'changed')

    def test_codepage_http_capture(self):
        class Fake:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b'<body>codepage=default</body>'
        with patch.object(mod,'urlopen',return_value=Fake()) as getter:
            self.assertEqual(mod.query_codepage(self.folder),'response-captured-unparsed')
        self.assertIn('codepage',(self.folder/'hercules-codepage-response.html').read_text())
        self.assertIn('cmd=codepage',getter.call_args.args[0])

    def test_codepage_failure_fails_open_only_for_diagnostic(self):
        with patch.object(mod,'urlopen',side_effect=OSError('unavailable')):
            self.assertEqual(mod.query_codepage(self.folder),'unavailable-not-verified')
        self.assertTrue((self.folder/'hercules-codepage-unavailable.json').exists())

if __name__=='__main__':unittest.main()
