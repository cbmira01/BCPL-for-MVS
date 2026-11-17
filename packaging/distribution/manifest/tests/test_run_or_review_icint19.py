"""TA.0 single-entry ICINT19 gate. Mocked MVS only; no JES traffic."""
from __future__ import annotations

import importlib.util
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[4]
FILE=ROOT/'tools/distribution/run-or-review-icint19.py'
SPEC=importlib.util.spec_from_file_location('ta0_gate_test',FILE)
assert SPEC and SPEC.loader
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

from test_verify_icint19_executable import mod as pilot
from test_inspect_icint19_failed_pilot import triage


class Core:
    def __init__(self): self.jes=0


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'workarea')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.iehlist=self.root/'iehlist'; self.iehlist.mkdir()
        self.review=self.root/'review'; self.review.mkdir()
        self.output=self.root/'execution'
        self.core=Core()
        self.config={}

    def call(self):
        return mod.decision(pilot, triage, self.core, self.config,
                            evidence=self.iehlist, review_dir=self.review,
                            output=self.output)

    def test_missing_output_executes_one_guarded_pilot(self):
        def simulated(core, cfg, *, evidence, review_dir, output):
            core.jes+=1
            output.mkdir()
            return {'job':9081}
        with patch.object(pilot,'run',side_effect=simulated):
            result=self.call()
        self.assertEqual(self.core.jes,1)
        self.assertEqual(result['state'],'NEW_EXECUTION_VALIDATED')
        self.assertEqual(result['job'],'9081')
        self.assertEqual(result['submitted_now'],'YES')

    def test_prior_output_is_never_resubmitted(self):
        self.output.mkdir()
        with patch.object(pilot,'run',side_effect=AssertionError('repeated JES')) as submit:
            with patch.object(triage,'diagnose',return_value={
                'state':'SAVED_JES_REPORT_REJECTED','job':'9080',
                'preflight':'OK_NOW','reason':'MISSING_OR_UNSUCCESSFUL_INTERPRETED_CODE=_RECORDS'}):
                result=self.call()
        submit.assert_not_called()
        self.assertEqual(result['state'],'SAVED_JES_REPORT_REJECTED')
        self.assertEqual(result['submitted_now'],'NO')
        self.assertEqual(result['job'],'9080')

    def test_prior_receipt_does_not_trigger_new_JES(self):
        self.output.mkdir()
        (self.output/'receipt.json').write_text('{}\n')
        with patch.object(pilot,'run',side_effect=AssertionError('repeated JES')) as submit:
            with patch.object(triage,'diagnose',return_value={'state':'RECEIPT_ALREADY_PRESENT','job':'unknown','preflight':'OK_NOW'}):
                result=self.call()
        submit.assert_not_called()
        self.assertEqual(result['state'],'RECEIPT_ALREADY_PRESENT')

    def test_preflight_refusal_does_not_create_directory(self):
        with patch.object(pilot,'run',side_effect=pilot.ExecEvidenceError('scalar-vector golden output changed')):
            result=self.call()
        self.assertEqual(result['state'],'NO_OUTPUT_DIRECTORY')
        self.assertEqual(result['preflight'],'SCALAR-VECTOR_GOLDEN_OUTPUT_CHANGED')
        self.assertFalse(self.output.exists())

    def test_post_failure_only_diagnoses_saved_evidence(self):
        def broken(core,cfg,*,evidence,review_dir,output):
            output.mkdir()
            (output/'cursor.json').write_text('{}\n')
            raise RuntimeError('contains private credentials')
        with patch.object(pilot,'run',side_effect=broken) as submit:
            with patch.object(triage,'diagnose',return_value={'state':'SUBMISSION_STATUS_UNCERTAIN','job':'unknown','preflight':'OK_NOW'}):
                result=self.call()
        submit.assert_called_once()
        self.assertEqual(result['state'],'SUBMISSION_STATUS_UNCERTAIN')
        self.assertEqual(result['submitted_now'],'NOT_CONFIRMED')
        self.assertNotIn('credentials',str(result))

    def test_existing_symlink_rejected_without_JES(self):
        self.output.symlink_to(self.iehlist,target_is_directory=True)
        with patch.object(pilot,'run') as submit:
            with self.assertRaises(pilot.ExecEvidenceError): self.call()
        submit.assert_not_called()

    def test_unsafe_home_location_rejected_without_JES(self):
        with patch.object(pilot,'run') as submit:
            with self.assertRaises(pilot.ExecEvidenceError):
                mod.decision(pilot,triage,self.core,self.config,evidence=self.iehlist,
                             review_dir=self.review,output=Path.home()/'ta0-out')
        submit.assert_not_called()

    def test_existing_empty_directory_is_not_reused(self):
        self.output.mkdir()
        with patch.object(pilot,'run',side_effect=AssertionError('repeated JES')) as submit:
            with patch.object(triage,'diagnose',return_value={'state':'NO_CAPTURED_JOB','job':'unknown','preflight':'OK_NOW'}):
                result=self.call()
        submit.assert_not_called()
        self.assertEqual(result['state'],'NO_CAPTURED_JOB')

    def test_broken_symlink_rejected_without_JES(self):
        self.output.symlink_to(self.root/'missing')
        with patch.object(pilot,'run') as submit:
            with self.assertRaises(pilot.ExecEvidenceError): self.call()
        submit.assert_not_called()


    def test_main_produces_only_compact_safe_status(self):
        args=['--iehlist-evidence',str(self.iehlist),
              '--review-dir',str(self.review),'--output-dir',str(self.output)]
        out,err=io.StringIO(),io.StringIO()
        with patch.object(mod,'load',side_effect=[pilot,triage]), \
             patch.object(pilot,'import_file',return_value=SimpleNamespace(
                 load_config=lambda: {})), \
             patch.object(mod,'decision',return_value={
                 'state':'SAVED_JES_REPORT_REJECTED', 'job':'9070',
                 'preflight':'OK_NOW', 'reason':'SAFE_REASON',
                 'submitted_now':'NO'}), \
             contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            rc=mod.main(args)
        self.assertEqual(rc,1)
        self.assertIn('SAVED_JES_REPORT_REJECTED',out.getvalue())
        self.assertIn('SUBMITTED_IN_THIS_INVOCATION=NO',out.getvalue())
        self.assertNotIn('PASSWORD',out.getvalue()+err.getvalue())
        self.assertNotIn('JCL',out.getvalue()+err.getvalue())
        self.assertFalse(self.output.exists())

    def test_main_good_execution_returns_zero(self):
        args=['--iehlist-evidence',str(self.iehlist),
              '--review-dir',str(self.review),'--output-dir',str(self.output)]
        out=io.StringIO()
        with patch.object(mod,'load',side_effect=[pilot,triage]), \
             patch.object(pilot,'import_file',return_value=SimpleNamespace(
                 load_config=lambda: {})), \
             patch.object(mod,'decision',return_value={
                 'state':'NEW_EXECUTION_VALIDATED', 'job':'9070',
                 'preflight':'PASS', 'reason':'NOT_APPLICABLE',
                 'submitted_now':'YES'}), \
             contextlib.redirect_stdout(out):
            rc=mod.main(args)
        self.assertEqual(rc,0)
        self.assertIn('NEW_EXECUTION_VALIDATED',out.getvalue())

    def test_saved_validated_receipt_is_success_without_job(self):
        self.output.mkdir()
        with patch.object(pilot,'run',side_effect=AssertionError('repeated JES')) as submit:
            with patch.object(triage,'diagnose',return_value={
                 'state':'SAVED_EXECUTION_VERIFIED','job':'9061',
                 'preflight':'OK_NOW','reason':'PINNED_JES_AND_BCPL_RESULT_VERIFIED'}):
                result=self.call()
        submit.assert_not_called()
        self.assertEqual(result['state'],'SAVED_EXECUTION_VERIFIED')
        self.assertEqual(result['job'],'9061')
        self.assertEqual(result['submitted_now'],'NO')

    def test_saved_validated_receipt_cli_success(self):
        args=['--iehlist-evidence',str(self.iehlist),
              '--review-dir',str(self.review),'--output-dir',str(self.output)]
        out=io.StringIO()
        with patch.object(mod,'load',side_effect=[pilot,triage]), \
             patch.object(pilot,'import_file',return_value=SimpleNamespace(
                 load_config=lambda: {})), \
             patch.object(mod,'decision',return_value={
                 'state':'SAVED_EXECUTION_VERIFIED', 'job':'9061',
                 'preflight':'OK_NOW', 'reason':'PINNED_JES_AND_BCPL_RESULT_VERIFIED',
                 'submitted_now':'NO'}), \
             contextlib.redirect_stdout(out):
            rc=mod.main(args)
        self.assertEqual(rc,0)
        self.assertIn('SAVED_EXECUTION_VERIFIED',out.getvalue())
        self.assertIn('SUBMITTED_IN_THIS_INVOCATION=NO',out.getvalue())


if __name__=='__main__': unittest.main()
