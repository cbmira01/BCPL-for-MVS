"""No-MVS synthetic tests for read-only JOB 9317 input acceptance."""
from __future__ import annotations
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'packaging/distribution/create-tape/scripts/ta2-bootstrap-stage-verify'
loader = importlib.machinery.SourceFileLoader('bt_v_test', str(SRC))
spec = importlib.util.spec_from_loader(loader.name, loader)
v = importlib.util.module_from_spec(spec)
loader.exec_module(v)


class StageVerification(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        work = self.root / 'workarea'; work.mkdir()
        self.operations = work / 'ta2-bootstrap-stage-operations'; self.operations.mkdir()
        self.original = self.operations / '20261120T132013Z-21957'; self.original.mkdir()
        self.out = work / 'ta2-bootstrap-stage-verification'
        self.marker = self.operations / 'TA2BT-TSO002-one-shot-attempt.json'
        self.result = {'status':'SIX_STEP_MVS_STAGING_RC0000_DIRECTORY_PENDING',
                       'job':9317,'steps':6,'targets':list(v.NAMES),'volume':'TSO002'}
        self.intent = {'state':'SUBMISSION_INTENT_NO_RETRY','jobname':'TA2BTSTR',
                       'targets':list(v.NAMES), 'candidate_id':'BCPL-0.1.0-rc1',
                       'attempt_evidence':'workarea/ta2-bootstrap-stage-operations/20261120T132013Z-21957',
                       'material_jcl_sha256':'f'*64}
        self.marker.write_text(json.dumps(self.intent))
        self.data = {'stage-summary.txt':b'JOB 9317 TA2BTSTR SUCCESS',
                     'stage-report.txt':b'IEF142I success',
                     'stage-result.json':json.dumps(self.result).encode()}
        for n, raw in self.data.items(): (self.original / n).write_bytes(raw)
        self._seal()
        self.patches = [patch.object(v,'ROOT',self.root),
                        patch.object(v,'OPERATIONS',self.operations),
                        patch.object(v,'STAGED',self.original),
                        patch.object(v,'MARKER',self.marker),
                        patch.object(v,'OUT',self.out)]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)

    def _seal(self):
        s=''.join(hashlib.sha256(raw).hexdigest()+'  '+n+'\n'
                  for n,raw in sorted(self.data.items()))
        (self.original/'SHA256SUMS').write_text(s)

    def _stage(self):
        return SimpleNamespace(validate_job=Mock(return_value=self.result.copy()))

    def test_original_six_step_receipt_pass(self):
        v.stage_receipt(v.sealed(self.original),self._stage(),self.intent)

    def test_wrong_saved_job_refused(self):
        self.result['job']=9316
        with self.assertRaisesRegex(v.Refusal,'original JOB'):
            v.stage_receipt(v.sealed(self.original),self._stage(),self.intent)

    def test_mvs_stage_journal_mismatch_refused(self):
        self.intent['candidate_id']='OTHER'
        with self.assertRaisesRegex(v.Refusal,'no-retry'):
            v.stage_receipt(v.sealed(self.original),self._stage(),self.intent)

    def test_tampered_jes_report_refused(self):
        (self.original/'stage-report.txt').write_text('TAMPERED')
        with self.assertRaisesRegex(v.Refusal,'checksum'):
            v.sealed(self.original)

    def test_unsealed_file_refused(self):
        (self.original/'unexpected.txt').write_text('unexpected')
        with self.assertRaisesRegex(v.Refusal,'contents differ'):
            v.sealed(self.original)

    def test_wrong_original_folder_refused(self):
        fake=self.operations/'second';fake.mkdir()
        with self.assertRaisesRegex(v.Refusal,'original JOB'):
            v.sealed(fake)

    def _core(self):
        return SimpleNamespace(dataset_missing=Mock(return_value=False),
            extract_listds_block=Mock(return_value=['DCB']),
            parse_listds=Mock(side_effect=[
              {'volume':'TSO002','dsorg':'PS','recfm':'FB','lrecl':'80','blksize':'800'},
              {'volume':'TSO002','dsorg':'PO','recfm':'FB','lrecl':'80','blksize':'800'}]))

    def test_exact_ps_and_po_dcbs(self):
        core=self._core();v.audit_attributes(core,'MVS output');
        self.assertEqual(core.parse_listds.call_count,2)

    def test_dcb_wrong_volume_refused(self):
        core=self._core();core.parse_listds.side_effect = [
            {'volume':'TSO003','dsorg':'PS','recfm':'FB','lrecl':'80','blksize':'800'},
            {'volume':'TSO002','dsorg':'PO','recfm':'FB','lrecl':'80','blksize':'800'}]
        with self.assertRaisesRegex(v.Refusal,'DCB or volume'):
            v.audit_attributes(core,'MVS output')

    def test_missing_dataset_refused(self):
        core=self._core();core.dataset_missing.return_value=True
        with self.assertRaisesRegex(v.Refusal,'not found'):
            v.audit_attributes(core,'MVS output')

    def _ls(self, members=None):
        return SimpleNamespace(member_blocks=Mock(return_value={v.NAMES[1]:['members']}),
                               parse_members=Mock(return_value=members if members is not None else list(v.MEMBERS)))

    def test_installer_directory_four_members(self):
        ls=self._ls();v.audit_directory(ls,'MVS result');ls.parse_members.assert_called_once()

    def test_extra_member_refused(self):
        with self.assertRaisesRegex(v.Refusal,'four installer'):
            v.audit_directory(self._ls([*v.MEMBERS,'OTHER']),'MVS result')

    def test_duplicate_member_refused(self):
        with self.assertRaisesRegex(v.Refusal,'four installer'):
            v.audit_directory(self._ls(['INSTALL','DATASETS','RELEASE','RELEASE']),'MVS result')

    def test_missing_directory_refused(self):
        ls=self._ls();ls.member_blocks.return_value={}
        with self.assertRaisesRegex(v.Refusal,'directory missing'):
            v.audit_directory(ls,'MVS result')

    def test_private_evidence_no_overwrite(self):
        output=v.make_run()
        v.save(output/'verification.json',b'{}')
        v.seal(output)
        self.assertIn('verification.json',(output/'SHA256SUMS').read_text())
        with self.assertRaises(FileExistsError):v.seal(output)

    def test_no_new_submission_without_live(self):
        fake=self._stage()
        with patch.object(v,'import_script',return_value=fake):
            self.assertEqual(v.operation(False),0)
        # Source file is deliberately limited to read-only MVS inquiries.
        source=SRC.read_text()
        self.assertNotIn('IEFBR14',source)
        self.assertNotIn('DISP=(NEW',source)

    def test_two_consolidated_read_only_inquiries(self):
        output=v.make_run()
        c=SimpleNamespace(require_reader_ready=Mock(),
            stat_deck=Mock(return_value='//DUMMY JOB TEST\n'),
            submit_and_wait=Mock(side_effect=[(9318,'CAT PASS'),(9319,'LS PASS')]),
            job_report=Mock(side_effect=['DCB STAT','MEMBERS']))
        ls=SimpleNamespace(list_members_deck=Mock(return_value='//MEMBER JOB TEST\n'))
        with patch.object(v,'audit_attributes') as attrs,patch.object(v,'audit_directory') as directory:
            jobs=v.live_checks(c,ls,{},output)
        self.assertEqual(jobs,{'catalog':9318,'members':9319})
        self.assertEqual(c.submit_and_wait.call_count,2)
        self.assertEqual(c.submit_and_wait.call_args_list[0].kwargs['max_rc'],8)
        self.assertEqual(c.submit_and_wait.call_args_list[1].kwargs['max_rc'],8)
        attrs.assert_called_once();directory.assert_called_once()
        self.assertTrue((output/'catalog-report.txt').is_file())
        self.assertTrue((output/'members-report.txt').is_file())


if __name__ == '__main__':unittest.main()
