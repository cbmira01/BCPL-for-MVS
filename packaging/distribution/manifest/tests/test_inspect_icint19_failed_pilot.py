"""No-JES tests of saved ICINT19 failure triage. All files stay ignored workarea/."""
from __future__ import annotations

import importlib.util
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


if __name__ == '__main__':
    unittest.main()
