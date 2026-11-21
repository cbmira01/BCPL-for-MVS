"""TA.2 rc2 one-shot producer; offline safety/negative tests only."""
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc2-produce-once'
loader = importlib.machinery.SourceFileLoader('rc2_one_shot_test',str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name,loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def good_job():
    summary = 'JOB 9462 TA2RC2WR\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
    summary += ''.join(f'{step} {pgm} RC=0000\n' for step,pgm in mod.STAGES)
    report = ''.join(f'IEF142I TA2RC2WR {step} - STEP WAS EXECUTED - COND CODE 0000\n'
                     for step,pgm in mod.STAGES)
    return summary,report

class TestWriter(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_21_step_good(self):
        summary,report=good_job()
        self.assertIsNone(mod.validate_job(9462,summary,report))
    def test_reject_wrong_job(self):
        summary,report=good_job()
        with self.assertRaises(mod.Refusal): mod.validate_job(9463,summary,report)
    def test_reject_missing_step(self):
        summary,report=good_job()
        summary=summary.replace('T0012 IEBCOPY RC=0000\n','')
        with self.assertRaises(mod.Refusal): mod.validate_job(9462,summary,report)
    def test_reject_bad_mvs_rc(self):
        summary,report=good_job()
        summary=summary.replace('T0020 IEBCOPY RC=0000','T0020 IEBCOPY RC=0008')
        with self.assertRaises(mod.Refusal): mod.validate_job(9462,summary,report)
    def test_reject_bad_report(self):
        summary,report=good_job()
        report=report.replace('T0002 - STEP WAS EXECUTED - COND CODE 0000','T0002 - STEP WAS EXECUTED - COND CODE 0004')
        with self.assertRaises(mod.Refusal): mod.validate_job(9462,summary,report)
    def test_reject_abend(self):
        summary,report=good_job()
        with self.assertRaises(mod.Refusal): mod.validate_job(9462,summary,report+'IEF450I ABEND S0C4\n')
    def test_reject_duplicate_report(self):
        summary,report=good_job()
        with self.assertRaises(mod.Refusal): mod.validate_job(9462,summary,report+report)
    def approval(self):
        return {'schema_version':1,'status':'OWNER_APPROVED_ONE_SHOT_RC2_PRIVATE_AWS',
                'candidate':'BCPL-0.1.0-rc2','volser':'BC0002',
                'image':mod.IMAGE,'hercules_unit':'0480','datasets':21,
                'jobname':mod.JOBNAME,'jcl_sha256':'a'*64,
                'publication_authorized':False,'automatic_retry':False}
    def test_approval_exact(self):
        self.assertIsNone(mod.verify_approval(json.dumps(self.approval()).encode(),'a'*64))
    def test_approval_wrong_hash(self):
        with self.assertRaises(mod.Refusal): mod.verify_approval(json.dumps(self.approval()).encode(),'b'*64)
    def test_approval_not_publication(self):
        d=self.approval(); d['publication_authorized']=True
        with self.assertRaises(mod.Refusal): mod.verify_approval(json.dumps(d).encode(),'a'*64)
    def test_approval_unexpected_key(self):
        d=self.approval(); d['arbitrary_permission']=True
        with self.assertRaises(mod.Refusal): mod.verify_approval(json.dumps(d).encode(),'a'*64)
    def test_approval_missing(self):
        with patch.object(mod,'APPROVAL',self.path/'absent.json'):
            with self.assertRaisesRegex(mod.Refusal,'NO MEDIA AUTHORIZATION'): mod.git_approved('a'*64)
    def test_sealed_receipt(self):
        p=self.path/'seal';p.mkdir()
        (p/'result.json').write_text('{"status":"PASS"}\n')
        checksum=hashlib.sha256((p/'result.json').read_bytes()).hexdigest()
        (p/'SHA256SUMS').write_text(checksum+'  result.json\n')
        with patch.object(mod,'WORK',self.path):
            self.assertEqual(mod.sealed(p,{'result.json'})['result.json'],b'{"status":"PASS"}\n')
    def test_sealed_checksum_corruption(self):
        p=self.path/'seal';p.mkdir();(p/'result.json').write_text('{}')
        (p/'SHA256SUMS').write_text('a'*64+'  result.json\n')
        with patch.object(mod,'WORK',self.path):
            with self.assertRaises(mod.Refusal): mod.sealed(p,{'result.json'})
    def test_sealed_extra_file(self):
        p=self.path/'seal';p.mkdir();(p/'result.json').write_text('{}')
        checksum=hashlib.sha256(b'{}').hexdigest()
        (p/'SHA256SUMS').write_text(checksum+'  result.json\n')
        (p/'other').write_text('unsealed')
        with patch.object(mod,'WORK',self.path):
            with self.assertRaises(mod.Refusal): mod.sealed(p,{'result.json'})
    def test_sealed_symlink(self):
        p=self.path/'seal';p.mkdir();(p/'result.json').symlink_to(self.path/'fake')
        (p/'SHA256SUMS').write_text('a'*64+'  result.json\n')
        with patch.object(mod,'WORK',self.path):
            with self.assertRaises(mod.Refusal): mod.sealed(p,{'result.json'})
    def test_success_evidence_seal(self):
        folder=self.path/'sealed-write';folder.mkdir()
        (folder/'result.json').write_text('{"status":"PASS"}\n')
        (folder/'write-summary.txt').write_text('MVS JOB 9462\n')
        mod.seal_evidence(folder)
        with patch.object(mod,'WORK',self.path):
            items=mod.sealed(folder,{'result.json','write-summary.txt'})
        self.assertEqual(items['result.json'],b'{"status":"PASS"}\n')
        with self.assertRaises(mod.Refusal): mod.seal_evidence(folder)
    def test_evidence_seal_refuses_symlinks(self):
        folder=self.path/'seal-link';folder.mkdir()
        (folder/'linked').symlink_to(self.path/'outside')
        with self.assertRaises(mod.Refusal): mod.seal_evidence(folder)
        self.assertFalse((folder/'SHA256SUMS').exists())
    def test_marker_exclusive(self):
        p=self.path/'workarea';p.mkdir()
        ops=p/'ops'
        with patch.multiple(mod,ROOT=self.path,WORK=p,OPS=ops,MARKER=ops/'attempt.json'):
            folder=ops/'run1';folder.mkdir(parents=True)
            mod.marker_once('a'*64,folder)
            marker=json.loads((ops/'attempt.json').read_bytes())
            self.assertTrue(marker['do_not_retry'])
            with self.assertRaises(mod.Refusal): mod.marker_once('a'*64,folder)
    def test_image_reserve_exclusive(self):
        p=self.path/'image.aws'
        with patch.object(mod,'TAPE',p):
            mod.create_image()
            with self.assertRaises(FileExistsError): mod.create_image()
    def test_workspace_refuses_existing_marker(self):
        (self.path/'workarea').mkdir()
        t=self.path/'mvs-state/tape';t.mkdir(parents=True)
        ops=self.path/'workarea/ops';ops.mkdir(); (ops/'marker.json').write_text('x')
        with patch.multiple(mod,ROOT=self.path,WORK=self.path/'workarea',TAPES=t,OPS=ops,
                            MARKER=ops/'marker.json',TAPE=t/'future.aws'):
            with self.assertRaises(mod.Refusal): mod.safe_workspace()
    @staticmethod
    def hetmap_fixture(volser='BTO001', extra=None):
        lines = ["Label               : 'VOL1'",
                 f"Volume Serial       : '{volser}'",
                 "Label               : 'HDR1'",
                 "Dataset ID          : 'BCPL.BT0001'",
                 f"Volume Serial       : '{volser}'",
                 "Label               : 'HDR2'",
                 "Label               : 'EOF1'",
                 f"Volume Serial       : '{volser}'",
                 "Label               : 'EOF2'"]
        if extra is not None:
            lines.extend(extra)
        return '\n'.join(lines) + '\n'
    def test_vol1_parse_repeated_serial(self):
        self.assertEqual(mod.volser_from_hetmap(self.hetmap_fixture('BTO001')), 'BTO001')
    def test_vol1_detect_true_collision(self):
        self.assertEqual(mod.volser_from_hetmap(self.hetmap_fixture('BC0002')), 'BC0002')
    def test_vol1_missing_is_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.volser_from_hetmap(self.hetmap_fixture().replace("Label               : 'VOL1'", '', 1))
    def test_vol1_duplicate_is_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.volser_from_hetmap(self.hetmap_fixture(extra=["Label               : 'VOL1'", "Volume Serial       : 'BTO001'"]))
    def test_vol1_conflicting_secondary_label_is_refused(self):
        bad = self.hetmap_fixture().replace("Volume Serial       : 'BTO001'", "Volume Serial       : 'BC0002'", 2)
        with self.assertRaises(mod.Refusal): mod.volser_from_hetmap(bad)
    def test_vol1_duplicate_field_is_refused(self):
        bad = self.hetmap_fixture().replace("Label               : 'HDR1'",
            "Volume Serial       : 'BTO001'\nLabel               : 'HDR1'")
        with self.assertRaises(mod.Refusal): mod.volser_from_hetmap(bad)
    def test_vol1_unlabelled_image_is_refused(self):
        with self.assertRaises(mod.Refusal): mod.volser_from_hetmap("Volume Serial       : 'BTO001'\n")

    def test_new_recovery_approval_exact(self):
        valid = {'schema_version': 1,
                 'status': 'OWNER_APPROVED_NEW_PRESTATEFUL_RC2_ATTEMPT',
                 'candidate': 'BCPL-0.1.0-rc2', 'volser': mod.VOL,
                 'image': mod.IMAGE, 'hercules_unit': '0480',
                 'original_halt_evidence': mod.INCIDENT.relative_to(mod.ROOT).as_posix(),
                 'prior_write_attempt_marker_created': False,
                 'original_existing_image': 'bcpl-objtest-20261108-01.aws',
                 'jcl_sha256': 'a'*64, 'publication_authorized': False,
                 'automatic_retry': False}
        mod.verify_recovery_approval(json.dumps(valid).encode('utf-8'), 'a'*64)
        with self.assertRaises(mod.Refusal):
            mod.verify_recovery_approval(json.dumps(valid).encode('utf-8'), 'b'*64)
        valid['automatic_retry'] = True
        with self.assertRaises(mod.Refusal):
            mod.verify_recovery_approval(json.dumps(valid).encode('utf-8'), 'a'*64)
    def test_review_prior_halt_replays_sealed_original_report(self):
        work = self.path / 'workarea'; work.mkdir()
        ops = work / 'operations'; ops.mkdir()
        incident = ops / 'original'; incident.mkdir()
        failure = {'status':'HALTED_NO_RETRY',
                   'reason':'unrecognized/reused BC0002 volume in existing image: '
                            'bcpl-objtest-20261108-01.aws'}
        (incident/'failure.json').write_text(json.dumps(failure) + '\n')
        (incident/'vol-000.txt').write_text(self.hetmap_fixture('BTO001'))
        mod.seal_evidence(incident)
        with patch.multiple(mod,WORK=work,OPS=ops,INCIDENT=incident,
                            MARKER=ops/'marker.json',TAPE=self.path/'candidate.aws'):
            self.assertEqual(mod.review_prior_prestateful_halt(), 'BTO001')
            (incident/'vol-000.txt').write_text(self.hetmap_fixture('BC0002'))
            with self.assertRaises(mod.Refusal): mod.review_prior_prestateful_halt()
    def test_review_prior_halt_refuses_true_collision(self):
        work = self.path / 'workarea'; work.mkdir()
        incident = work / 'prior'; incident.mkdir()
        failure = {'status':'HALTED_NO_RETRY',
                   'reason':'unrecognized/reused BC0002 volume in existing image: '
                            'bcpl-objtest-20261108-01.aws'}
        (incident/'failure.json').write_text(json.dumps(failure)+'\n')
        (incident/'vol-000.txt').write_text(self.hetmap_fixture('BC0002'))
        mod.seal_evidence(incident)
        with patch.multiple(mod,WORK=work,INCIDENT=incident,
                            MARKER=work/'absent-marker',TAPE=work/'absent-tape.aws'):
            with self.assertRaisesRegex(mod.Refusal,'true BC0002 collision'):
                mod.review_prior_prestateful_halt()
    def test_review_prior_halt_refuses_existing_attempt_marker(self):
        work = self.path / 'workarea'; work.mkdir()
        ops = work / 'ops'; ops.mkdir()
        marker = ops / 'marker.json'; marker.write_text('occupied')
        with patch.multiple(mod,WORK=work,OPS=ops,INCIDENT=ops/'incident',
                            MARKER=marker,TAPE=work/'candidate.aws'):
            with self.assertRaisesRegex(mod.Refusal,'NEVER RETRY'):
                mod.review_prior_prestateful_halt()

    def test_git_approval_refuses_missing_prior_incident(self):
        from types import SimpleNamespace
        approval = self.path / 'approval.json'
        raw = json.dumps(self.approval()).encode('utf-8')
        approval.write_bytes(raw)
        def fake_git(args, **kwargs):
            if args[3] == 'branch': return SimpleNamespace(returncode=0,stdout='main\n')
            if args[3] == 'status': return SimpleNamespace(returncode=0,stdout='')
            if args[3] == 'show': return SimpleNamespace(returncode=0,stdout=raw)
            raise AssertionError('unexpected git call')
        with patch.multiple(mod,ROOT=self.path,APPROVAL=approval,
                            INCIDENT=self.path/'missing-original-incident',
                            MARKER=self.path/'missing-marker',
                            TAPE=self.path/'missing-image.aws'):
            with patch.object(mod.subprocess,'run',side_effect=fake_git):
                with self.assertRaisesRegex(mod.Refusal,'untrusted saved evidence folder'):
                    mod.git_approved('a'*64)

    def test_existing_media_wrong_volser(self):
        t=self.path/'tape';t.mkdir(); (t/'existing.aws').write_text('test')
        e=self.path/'evidence';e.mkdir()
        with patch.multiple(mod,TAPES=t,TAPE=t/mod.IMAGE):
            with patch.object(mod,'capture',return_value=self.hetmap_fixture("BC0002")):
                with self.assertRaises(mod.Refusal): mod.existing_media(e)
    def test_existing_media_unique(self):
        t=self.path/'tape';t.mkdir(); (t/'existing.aws').write_text('test')
        e=self.path/'evidence';e.mkdir()
        with patch.multiple(mod,TAPES=t,TAPE=t/mod.IMAGE):
            with patch.object(mod,'capture',return_value=self.hetmap_fixture("BTA101")):
                self.assertEqual(mod.existing_media(e),1)
    def test_existing_media_directory_rejected(self):
        t=self.path/'tape';t.mkdir(); (t/'unsafe').mkdir()
        e=self.path/'evidence';e.mkdir()
        with patch.multiple(mod,TAPES=t,TAPE=t/mod.IMAGE):
            with self.assertRaises(mod.Refusal): mod.existing_media(e)

if __name__=='__main__': unittest.main()
