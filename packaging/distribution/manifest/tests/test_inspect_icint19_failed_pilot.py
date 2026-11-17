"""No-JES tests of saved ICINT19 failure triage. All files stay ignored workarea/."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT/'tools/distribution/inspect-icint19-failed-pilot.py'
spec = importlib.util.spec_from_file_location('ta0_exec_triage', SOURCE)
assert spec and spec.loader
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)

# Reuse the already tested exact JES fixture and pilot parser.
from test_verify_icint19_executable import mod as pilot, sample_report


class Core:
    def full_dsn(self, cfg, spec):
        return 'HERC02.BCPL.MR10KIT.LOAD'


class Triage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.evidence = self.folder/'iehlist'; self.evidence.mkdir()
        self.review = self.folder/'review'; self.review.mkdir()
        self.output = self.folder/'pilot'
        self.core=Core()
        self.cfg={}
        self.patch=patch.object(pilot,'validated_inputs',return_value=({}, {}, b'', '', ''))
        self.patch.start();self.addCleanup(self.patch.stop)

    def result(self):
        return triage.diagnose(pilot,self.core,self.cfg,evidence=self.evidence,
                               review_dir=self.review,output=self.output)

    def write(self, name, content):
        if not self.output.is_dir(): self.output.mkdir(mode=0o700)
        if isinstance(content,str): content=content.encode('utf-8')
        (self.output/name).write_bytes(content)

    def populate(self, *, report=None, summary='JOB 9070 TA0ICEX\n', failure='JOB=9070; type=ExecEvidenceError\n'):
        self.write('cursor.json','{}\n')
        self.write('job-body.jcl','//* approved original JCL\n')
        self.write('job-summary.txt',summary)
        self.write('job-report.txt',sample_report() if report is None else report)
        self.write('failure.txt',failure)

    def test_fails_preflight_without_submitting_or_creating(self):
        self.patch.stop()
        with patch.object(pilot,'validated_inputs',side_effect=pilot.ExecEvidenceError('scalar-vector golden output changed')):
            result=self.result()
        self.assertEqual(result['state'],'NO_OUTPUT_DIRECTORY')
        self.assertEqual(result['preflight'],'SCALAR-VECTOR_GOLDEN_OUTPUT_CHANGED')
        self.assertFalse(self.output.exists())

    def test_no_output_and_current_preflight_ok(self):
        result=self.result()
        self.assertEqual(result['state'],'NO_OUTPUT_DIRECTORY')
        self.assertEqual(result['preflight'],'OK_NOW')

    def test_cursor_with_failed_submission_is_uncertain(self):
        self.write('job-body.jcl','//* no password\n')
        self.write('cursor.json','{}\n')
        self.write('failure.txt','JOB=unknown; type=RuntimeError\n')
        self.assertEqual(self.result()['state'],'SUBMISSION_STATUS_UNCERTAIN')

    def test_successful_saved_report_detected_but_not_accepted(self):
        self.populate()
        self.assertEqual(self.result()['state'],'JES_REPORT_VALID_BUT_PRINTER_WINDOW_MISSING')
        self.write('printer-window.raw',b'raw\n')
        self.assertEqual(self.result()['state'],'JES_REPORT_VALID_BUT_NO_FINAL_RECEIPT')

    def test_bad_report_detected_by_canonical_validator(self):
        self.populate(report=sample_report().replace('RP: SCALAR 17 42','RP: SCALAR 99 42'))
        result=self.result()
        self.assertEqual(result['state'],'SAVED_JES_REPORT_REJECTED')
        self.assertEqual(result['reason'],'EXECUTED_SCALAR-VECTOR_RP_RECORDS_DIFFER_FROM_GOLDEN_OUTPUT')

    def test_failed_mvs_step_detected(self):
        self.populate(report=sample_report().replace('C01A ICINT19 RC= 0000','C01A ICINT19 RC= 0008'))
        self.assertIn('BYPASSED',self.result()['reason'])

    def test_conflicting_job_rejected(self):
        self.populate(failure='JOB=9069; type=ExecEvidenceError\n')
        self.assertEqual(self.result()['state'],'SAVED_JES_JOB_ID_CONFLICT')

    def test_missing_cursor_is_untrusted(self):
        self.populate();(self.output/'cursor.json').unlink()
        self.assertEqual(self.result()['state'],'INCOMPLETE_SAVED_JES_EVIDENCE')

    def test_unknown_file_fails_closed(self):
        self.write('extra.txt','private\n')
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_OR_LINKED'):
            self.result()

    def test_symlink_evidence_rejected(self):
        self.write('cursor.json','{}\n')
        (self.output/'cursor.json').unlink()
        (self.output/'cursor.json').symlink_to(self.review)
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_OR_LINKED'):
            self.result()

    def test_malformed_failure_marker_rejected(self):
        self.write('failure.txt','PASSWORD=SECRET\n')
        with self.assertRaisesRegex(ValueError,'INVALID_FAILURE_MARKER'):
            self.result()

    def test_no_side_effects_or_jobs(self):
        self.populate()
        before={p.name:p.read_bytes() for p in self.output.iterdir()}
        self.result()
        self.assertEqual({p.name:p.read_bytes() for p in self.output.iterdir()},before)

    def test_source_path_guard_does_not_accept_home(self):
        with self.assertRaises(pilot.ExecEvidenceError):
            triage.diagnose(pilot,self.core,self.cfg,evidence=self.evidence,
                            review_dir=self.review,output=Path.home()/'ta0-elsewhere')


    def prepare_signed_receipt(self):
        # Construct a real-format receipt and matching simulated MVS result.
        # The saved directory review is mocked, never reconstructed or edited.
        summary='JOB 9070  TA0ICEX\nSTEP       PROGRAM      RESULT\n'
        summary+=''.join(f'{st:<10} {pg:<12} RC=0000\n'
                         for st, pg in zip(pilot.STEPS, pilot.PROGRAMS))
        summary+='\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        self.populate(summary=summary)
        (self.output/'failure.txt').unlink()
        self.write('printer-window.raw', b'SIMULATED CURSOR WINDOW\n')
        (self.review/'directory-review.json').write_text('{}\n')
        body='//* approved original JCL\n'
        source=b'approved-source-body\n'
        (self.output/'job-body.jcl').write_text(body)
        self.gold=self.folder/'golden.expected'
        self.gold.write_text('\n'.join(pilot.GOLDEN)+'\n')
        self.gold_patch=patch.object(pilot,'GOLD',self.gold)
        self.gold_patch.start();self.addCleanup(self.gold_patch.stop)
        self.patch.stop()
        self.patch=patch.object(pilot,'validated_inputs',return_value=(
            {'job':9060,'dsn':'HERC02.BCPL.MR10KIT.LOAD'},
            {},source,body,'deadbeef'*5))
        self.patch.start();self.addCleanup(self.patch.stop)
        receipt={
            'phase':triage.PHASE,'job':9070,'jobname':'TA0ICEX',
            'source_dsn':'HERC02.BCPL.MR10KIT.LOAD','source_directory_job':9060,
            'review_receipt_sha256':pilot.sha((self.review/'directory-review.json').read_bytes()),
            'source_jcl_git_blob':'deadbeef'*5,
            'source_jcl_sha256':pilot.sha(source),
            'golden_sha256':pilot.sha(self.gold.read_bytes()),
            'sha256':{x:pilot.sha((self.output/x).read_bytes()) for x in triage.PINNED},
            'result':pilot.validate_report(sample_report(),job=9070,gold=pilot.GOLDEN),
            'qualifications':['Read-only installed load verification']*4,
        }
        (self.output/'receipt.json').write_text(json.dumps(receipt)+'\n')
        return receipt

    def change_receipt(self, f):
        path=self.output/'receipt.json'
        data=json.loads(path.read_text())
        f(data)
        path.write_text(json.dumps(data)+'\n')

    def test_saved_receipt_fully_revalidated(self):
        self.prepare_signed_receipt()
        original={p.name:p.read_bytes() for p in self.output.iterdir()}
        result=self.result()
        self.assertEqual(result['state'],'SAVED_EXECUTION_VERIFIED')
        self.assertEqual(result['job'],'9070')
        self.assertEqual(result['reason'],'PINNED_JES_AND_BCPL_RESULT_VERIFIED')
        self.assertEqual({p.name:p.read_bytes() for p in self.output.iterdir()},original)

    def test_receipt_has_to_be_valid_json(self):
        self.prepare_signed_receipt()
        (self.output/'receipt.json').write_text('{not-json}')
        self.assertEqual(self.result()['reason'],'RECEIPT_JSON_INVALID')

    def test_receipt_requires_all_pinned_files(self):
        self.prepare_signed_receipt()
        (self.output/'printer-window.raw').unlink()
        self.assertEqual(self.result()['reason'],'RECEIPT_FILE_SET_INVALID')

    def test_receipt_with_failure_marker_is_never_accepted(self):
        self.prepare_signed_receipt()
        self.write('failure.txt','JOB=9070; type=ExecEvidenceError\n')
        self.assertEqual(self.result()['reason'],'RECEIPT_FILE_SET_INVALID')

    def test_receipt_detects_modified_report_bytes(self):
        self.prepare_signed_receipt()
        self.write('job-report.txt',sample_report().replace('SCALAR 17 42','SCALAR 99 42'))
        self.assertEqual(self.result()['reason'],'RECEIPT_PIN_MISMATCH')

    def test_receipt_rejects_forged_digest_and_invalid_result(self):
        self.prepare_signed_receipt()
        self.change_receipt(lambda data:data['sha256'].__setitem__('cursor.json','f'*64))
        self.assertEqual(self.result()['reason'],'RECEIPT_PIN_MISMATCH')
        self.change_receipt(lambda data:data['sha256'].__setitem__(
            'cursor.json',pilot.sha((self.output/'cursor.json').read_bytes())))
        self.change_receipt(lambda data:data['result']['rp_records'].append('RP: FAKE 1'))
        self.assertEqual(self.result()['reason'],'RECEIPT_RESULT_MISMATCH')

    def test_receipt_rejects_report_even_after_repinning(self):
        self.prepare_signed_receipt()
        p=self.output/'job-report.txt';p.write_text(p.read_text().replace('CODE=0','CODE=4'))
        self.change_receipt(lambda data:data['sha256'].__setitem__('job-report.txt',pilot.sha(p.read_bytes())))
        self.assertEqual(self.result()['reason'],'RECEIPT_MVS_REPORT_FAILED')

    def test_receipt_rejects_changed_job_identity(self):
        self.prepare_signed_receipt()
        self.change_receipt(lambda data:data.__setitem__('job',9999))
        self.assertEqual(self.result()['reason'],'RECEIPT_JES_SUMMARY_MISMATCH')

    def test_receipt_rejects_source_binding_mismatch(self):
        self.prepare_signed_receipt()
        self.change_receipt(lambda data:data.__setitem__('source_directory_job',9059))
        self.assertEqual(self.result()['reason'],'RECEIPT_SOURCE_BINDING_MISMATCH')

    def test_receipt_rejects_mutated_job_body_after_repin(self):
        self.prepare_signed_receipt()
        p=self.output/'job-body.jcl';p.write_text('//* DIFFERENT DECK\n')
        self.change_receipt(lambda data:data['sha256'].__setitem__('job-body.jcl',pilot.sha(p.read_bytes())))
        self.assertEqual(self.result()['reason'],'RECEIPT_JCL_BINDING_MISMATCH')

    def test_receipt_not_accepted_if_current_preflight_changed(self):
        self.prepare_signed_receipt()
        self.patch.stop()
        with patch.object(pilot,'validated_inputs',side_effect=pilot.ExecEvidenceError(
            'MRREGRES source revision changed: review before running')):
            self.assertEqual(self.result()['reason'],'CURRENT_PREFLIGHT_FAILED')

    def test_receipt_rejects_missing_step_in_summary_even_after_repin(self):
        self.prepare_signed_receipt()
        p=self.output/'job-summary.txt';p.write_text(p.read_text().replace('R01        ICINT19      RC=0000\n',''))
        self.change_receipt(lambda data:data['sha256'].__setitem__('job-summary.txt',pilot.sha(p.read_bytes())))
        self.assertEqual(self.result()['reason'],'RECEIPT_JES_SUMMARY_MISMATCH')

    def test_receipt_rejects_added_unknown_field(self):
        self.prepare_signed_receipt()
        self.change_receipt(lambda data:data.__setitem__('additional','untrusted'))
        self.assertEqual(self.result()['reason'],'RECEIPT_SCHEMA_MISMATCH')


if __name__ == '__main__':
    unittest.main()
