#!/usr/bin/env python3
"""Tests for reusing saved MVS compile-only evidence without a second job."""
from pathlib import Path
import importlib.util
import hashlib
import tempfile
from unittest.mock import patch
import json
import subprocess
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / 'tools/bootstrap/probe-co1-indirect-target.py'
spec = importlib.util.spec_from_file_location('co1driver', DRIVER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

OUT = ('CO.1 INDIRECT PASS: JOB 8125, checked 4, three-formal 1, calls 4; compile-only\n'
       'CO.1 INDIRECT evidence: workarea/co1-indirect-entry/FAKE-8125\n')
SUMMARY = {'status': 'PASS', 'jes_job_id': '8125', 'checked_entries': 4,
           'three_formal_entries': 1, 'ordinary_calls': 4,
           'compiler_driver_rc': 0, 'assembled': False,
           'linked': False, 'native_go': False}


class WrapperUnitTests(unittest.TestCase):
    def test_job_reconciliation(self):
        self.assertEqual(module.extract_result(OUT, SUMMARY), '8125')

    def test_bad_job(self):
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            module.extract_result(OUT, {**SUMMARY, 'jes_job_id': '8126'})

    def test_bad_counts(self):
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            module.extract_result(OUT, {**SUMMARY, 'ordinary_calls': 3})

    def test_bad_compiler_return(self):
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            module.extract_result(OUT, {**SUMMARY, 'compiler_driver_rc': 8})

    def test_native_go_cannot_be_pass(self):
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            module.extract_result(OUT, {**SUMMARY, 'native_go': True})

    def test_duplicate_status(self):
        with self.assertRaisesRegex(ValueError, 'unique'):
            module.extract_result(OUT+OUT, SUMMARY)

    def test_original_evidence_location(self):
        self.assertEqual(module.evidence_path(OUT).name, 'FAKE-8125')

    def test_reject_traversal(self):
        with self.assertRaisesRegex(ValueError, 'must be one directory'):
            module.select_reuse('workarea/co1-indirect-entry/../elsewhere')

    def test_reject_bad_evidence(self):
        with self.assertRaisesRegex(ValueError, 'one original'):
            module.evidence_path(OUT.replace('workarea/co1-indirect-entry', 'workarea/elsewhere'))

    def test_reject_nonexistent_replay(self):
        with self.assertRaisesRegex(ValueError, 'absent'):
            module.select_reuse('workarea/co1-indirect-entry/does-not-exist-12898')


    def test_replay_existing_compiler_evidence_without_submission(self):
        # A fake MVS listing exercises the evidence path; no compiler is invoked.
        with tempfile.TemporaryDirectory(prefix='co1-audit-test-') as dirname:
            scratch = Path(dirname)
            target = scratch / 'workarea/co1-indirect-entry/FAKE-8125'
            target.mkdir(parents=True)
            source = scratch / 'source.bcpl'
            parm = scratch / 'cambridge-parm.txt'
            source.write_text('LET F(X) = X\n')
            parm.write_text('/CN' + '/' * 77 + '\n')
            saved = {**SUMMARY,
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'parm_sha256': hashlib.sha256(parm.read_bytes()).hexdigest()}
            (target / 'summary.json').write_text(json.dumps(saved))
            (target / 'target-probe.log').write_text(OUT)
            (target / 'target-audit.json').write_text('{"status":"FAIL"}\n')
            (target / 'generated.s370.asm').write_text(
                'STM 4,9,0(15)\n'
                ' BAL 14,60(11)\n'
                ' DC A(L40) STACK FRAME SIZE\n'
                ' LR 5,15\n'
                ' LR 8,9\n'
                ' LR 7,8\n'
                ' L 4,12(5)\n'
                ' BALR 6,4\n'
                ' BCR 15,11\n'
            )
            with (patch.object(module, 'ROOT', scratch),
                  patch.object(module, 'BASE', scratch / 'workarea/co1-indirect-entry'),
                  patch.object(module, 'SOURCE', source),
                  patch.object(module, 'PARM', parm),
                  patch.object(module, 'parse_args', return_value=type('Args', (), {
                      'reuse_evidence': str(target)})())):
                self.assertEqual(module.run(), 0)
            receipt = json.loads((target / 'target-audit-v2.json').read_text())
            self.assertEqual(receipt['status'], 'PASS')
            self.assertTrue(receipt['reused_existing_mvs_job'])
            self.assertEqual(receipt['jes_job_id'], '8125')
            self.assertIn('12(R5)', receipt['target_origin'])
            self.assertEqual(json.loads((target / 'target-audit.json').read_text())['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
