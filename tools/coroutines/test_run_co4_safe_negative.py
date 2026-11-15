#!/usr/bin/env python3
"""Host-only checks of the CO.4 negative-path candidate (never JES)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'tools/coroutines/run-co4-safe-negative.py'
spec = importlib.util.spec_from_file_location('co4_safe_candidate', TARGET)
if spec is None or spec.loader is None:
    raise RuntimeError('safe negative runner missing')
co4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co4)


class SourceContractTests(unittest.TestCase):
    def test_exact_sixteen_record_oracle(self):
        self.assertEqual(co4.EXPECTED,
                         ('INIT', 'SIZE', 'ROOT', 'MADE', 'FULL', 'BADDEL',
                          'A1', 'RA1', 'B1', 'RB1', 'A2', 'RA2', 'B2', 'RB2',
                          'CLEAN', 'PASS'))

    def test_fully_formed_oracle_only(self):
        self.assertEqual(co4.observed_records('unrelated\nCO4SAFE INIT\n'), ['INIT'])
        for malformed in ('CO4SAFE BAD EXTRA', 'CO4SAFE ', 'CO4SAFE AB-1'):
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(co4.CandidateError, 'malformed'):
                    co4.observed_records(malformed)

    def test_source_has_safe_refusals_and_recovery(self):
        src = (co4.FIXTURE / 'source.bcpl').read_text('ascii')
        self.assertIn('CREATECO(AWORK,-1)', src)
        self.assertIn('CREATECO(AWORK,1023)', src)
        self.assertIn('CREATECO(AWORK,1025)', src)
        self.assertIn('COWAIT(9)', src)
        self.assertIn('RESUMECO(0,9)', src)
        self.assertIn('DELETECO(1)', src)
        self.assertIn('IF DELETECO(SELF) RESULTIS', src)
        self.assertIn('R:=CALLCO(A,12)', src)
        self.assertIn('R:=CALLCO(B,22)', src)
        self.assertNotIn('CALLCO(1,', src)
        self.assertNotIn('RESUMECO(1,', src)
        self.assertNotIn('CHANGECO(1,', src)
        self.assertEqual(src.count('MARK("FAIL")'), 1)
        self.assertEqual(src.count('MARK("PASS")'), 1)
        self.assertTrue(all(len(line) <= 80 and '\t' not in line
                            for line in src.splitlines()))

    def test_pins_are_git_blobs(self):
        self.assertNotEqual(co4.git_blob_id(b'first'), co4.git_blob_id(b'second'))
        self.assertEqual(co4.CO3_BLOBS['cambridge-parm.txt'],
                         '2d280050102b2e98caaf96541f59a39eb473da9c')

    def test_source_oracle_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / co4.FIXTURE.relative_to(co4.ROOT)
            target.mkdir(parents=True)
            src = (co4.FIXTURE / 'source.bcpl').read_text('ascii')
            (target / 'source.bcpl').write_text(
                src.replace('MARK("RB2")', 'MARK("BROKEN")'))
            with self.assertRaisesRegex(co4.CandidateError, 'marker not unique'):
                co4.validate_inputs(root)

    def test_unsafe_descriptor_api_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / co4.FIXTURE.relative_to(co4.ROOT)
            target.mkdir(parents=True)
            src = (co4.FIXTURE / 'source.bcpl').read_text('ascii')
            (target / 'source.bcpl').write_text(src.replace(
                'IF DELETECO(1) DO FAIL()',
                'IF DELETECO(1) DO FAIL()\n    R:=CALLCO(1,0)'))
            with self.assertRaisesRegex(co4.CandidateError,
                                        'unsafe descriptor'):
                co4.validate_inputs(root)

    def test_accepted_co3_source_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / co4.FIXTURE.relative_to(co4.ROOT)
            accepted = root / co4.ACCEPTED.relative_to(co4.ROOT)
            target.mkdir(parents=True)
            accepted.mkdir(parents=True)
            shutil.copyfile(co4.FIXTURE / 'source.bcpl', target / 'source.bcpl')
            for name in co4.CO3_BLOBS:
                (accepted / name).write_text('tampered content\n')
            with self.assertRaisesRegex(co4.CandidateError,
                                        'accepted CO.3 source drift'):
                co4.validate_inputs(root)

    def test_adapter_override_uses_safe_oracle(self):
        class Driver:
            pass
        class Adapter:
            @staticmethod
            def configure(driver):
                driver.adapter_active = True
        d = Driver()
        co4.configure(d, Adapter, Path('/fixture'), Path('/work'))
        self.assertTrue(d.adapter_active)
        self.assertEqual(d.EXPECTED, co4.EXPECTED)
        self.assertIs(d.observed_records, co4.observed_records)


class IsolatedExecutorTests(unittest.TestCase):
    def _run_fake(self, exit_code: int):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture, accepted, work = (root / x for x in ('fixture','accepted','work'))
            fixture.mkdir()
            accepted.mkdir()
            (fixture / 'source.bcpl').write_text('FAKE NOT BCPL\n')
            (accepted / 'library.bcpl').write_text('FAKE LIBRARY\n')
            (accepted / 'cambridge-parm.txt').write_text('/CN'+'/'*77+'\n')
            outer = self
            class Driver:
                def execute(self, scenario):
                    outer.assertEqual(scenario, 'first')
                    outer.assertEqual(self.EXPECTED, co4.EXPECTED)
                    p = self.WORK / 'FAKE-NOT-MVS'
                    p.mkdir()
                    (p / 'result.json').write_text(json.dumps({
                        'status': 'PASS' if exit_code == 0 else 'FAIL',
                        'git_head': 'FAKE', 'native_job': 'FAKE',
                        'evidence_class': 'HOST-SYNTHETIC'}))
                    return exit_code
            class Adapter:
                @staticmethod
                def configure(driver):
                    driver.adapter_active = True
            with (mock.patch.object(co4,'FIXTURE',fixture),
                  mock.patch.object(co4,'ACCEPTED',accepted),
                  mock.patch.object(co4,'WORK',work),
                  mock.patch.object(co4,'validate_inputs',return_value={'fake':'only'}),
                  mock.patch.object(co4,'load_module',side_effect=[Driver(),Adapter])):
                result = co4.run()
            self.assertEqual(result, exit_code)
            evidence = json.loads((work/'FAKE-NOT-MVS'/'co4-result.json').read_text())
            self.assertEqual(evidence['status'], 'PASS' if exit_code == 0 else 'FAIL')
            self.assertEqual(evidence['candidate'], 'safe-negative')
            self.assertEqual(evidence['evidence_class'], 'HOST-SYNTHETIC')
            self.assertEqual(len(evidence['expected_bcpl_records']), 16)
            self.assertFalse(list(work.glob('_input-*')))

    def test_synthetic_success(self):
        self._run_fake(0)

    def test_synthetic_failure(self):
        self._run_fake(1)


if __name__ == '__main__':
    unittest.main()
