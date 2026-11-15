#!/usr/bin/env python3
"""Host-only checks for the isolated CO.4 candidate; NEVER submit JES."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'tools/coroutines/run-co4-bounded-stress.py'
spec = importlib.util.spec_from_file_location('co4_runner_under_test', RUNNER)
if spec is None or spec.loader is None:
    raise RuntimeError('CO.4 runner not found')
co4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co4)


class SourceContractTests(unittest.TestCase):
    def test_nine_exact_oracle_tokens(self):
        self.assertEqual(co4.EXPECTED,
                         ('MADE', 'REFUSED', 'R04', 'R08', 'R12',
                          'R16', 'DELA', 'DELB', 'PASS'))

    def test_co4_oracle_extracts_exact_records(self):
        report = 'unrelated\nCO4BCPL MADE\nCO4BCPL REFUSED\n'
        self.assertEqual(co4.observed_records(report), ['MADE', 'REFUSED'])

    def test_co4_oracle_rejects_truncation(self):
        with self.assertRaisesRegex(co4.CandidateError, 'malformed'):
            co4.observed_records('CO4BCPL BAD EXTRA\n')

    def test_git_blob_identity_is_content_sensitive(self):
        self.assertNotEqual(co4.git_blob_id(b'CO3'),
                            co4.git_blob_id(b'CO4'))

    def test_expected_source_structure_is_safe(self):
        code = (co4.FIXTURE / 'source.bcpl').read_text('ascii')
        self.assertIn('FOR I=1 TO 15 DO', code)
        self.assertIn('FOR I=1 TO 16 DO', code)
        self.assertIn('DEEP(N-1,WHO,INPUT)', code)
        self.assertEqual(code.count('CREATECO('), 2)
        self.assertEqual(code.count('CHANGECO(123,'), 2)
        self.assertNotIn('DELETECO(1)', code)
        self.assertNotIn('CALLCO(1,', code)
        self.assertTrue(all(len(s) <= 80 for s in code.splitlines()))

    def test_pin_rejects_co3_library_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / co4.FIXTURE.relative_to(co4.ROOT)
            dst = root / co4.ACCEPTED.relative_to(co4.ROOT)
            src.mkdir(parents=True)
            dst.mkdir(parents=True)
            shutil.copyfile(co4.FIXTURE / 'source.bcpl',
                            src / 'source.bcpl')
            for name in co4.CO3_BLOBS:
                (dst / name).write_bytes(b'untrusted source drift\n')
            for path in (co4.BASE_RUNNER, co4.CO3_ADAPTER,
                         co4.ROOT / 'bootstrap-toolchain/asm/bcplco.asm',
                         co4.ROOT / 'bootstrap-toolchain/asm/bcplmain.asm'):
                mirror = root / path.relative_to(co4.ROOT)
                mirror.parent.mkdir(parents=True, exist_ok=True)
                mirror.write_text('offline stub\n')
            with self.assertRaisesRegex(co4.CandidateError,
                                        'accepted CO.3 source drift'):
                co4.validate_inputs(root)

    def test_pin_rejects_output_oracle_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / co4.FIXTURE.relative_to(co4.ROOT)
            dst = root / co4.ACCEPTED.relative_to(co4.ROOT)
            src.mkdir(parents=True)
            dst.mkdir(parents=True)
            code = (co4.FIXTURE / 'source.bcpl').read_text('ascii')
            (src / 'source.bcpl').write_text(
                code.replace('MARK("R16")', 'MARK("BAD")'))
            with self.assertRaisesRegex(co4.CandidateError,
                                        'CO.4 output marker not unique'):
                co4.validate_inputs(root)

    def test_adapter_configures_only_new_fixture_and_oracle(self):
        class StubDriver:
            FIXTURE = None
            WORK = None
            EXPECTED = None
            inherited = False

        class StubAdapter:
            @staticmethod
            def configure(driver):
                driver.inherited = True

        driver = StubDriver()
        fixture = Path('/candidate')
        work = Path('/workarea')
        co4.configure(driver, StubAdapter, fixture, work)
        self.assertTrue(driver.inherited)
        self.assertEqual(driver.FIXTURE, fixture)
        self.assertEqual(driver.WORK, work)
        self.assertEqual(driver.EXPECTED, co4.EXPECTED)
        self.assertIs(driver.observed_records, co4.observed_records)


class ExecutorAdapterTests(unittest.TestCase):
    def exercise_fake_executor(self, return_code: int):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = root / 'fixture'
            accepted = root / 'accepted'
            work = root / 'work'
            fixture.mkdir()
            accepted.mkdir()
            (fixture / 'source.bcpl').write_text('START\n')
            (accepted / 'library.bcpl').write_text('CO3 library\n')
            (accepted / 'cambridge-parm.txt').write_text('/CN' + '/'*77+'\n')
            self_outer = self

            class FakeDriver:
                FIXTURE = None
                WORK = None
                EXPECTED = None

                def execute(self, scenario):
                    self_outer.assertEqual(scenario, 'first')
                    self_outer.assertEqual(self.EXPECTED, co4.EXPECTED)
                    self_outer.assertEqual(
                        (self.FIXTURE/'library.bcpl').read_text(),
                        'CO3 library\n')
                    evidence = self.WORK / 'synthetic-TEST-NOT-MVS'
                    evidence.mkdir()
                    receipt = {
                        'status': 'PASS' if return_code == 0 else 'FAIL',
                        'git_head': 'FAKE-NOT-A-GIT-SHA',
                        'native_job': 'FAKE-NOT-JES',
                        'CO3ACMP_job': 'FAKE-A',
                        'CO3LCMP_job': 'FAKE-L',
                        'evidence_class': 'SYNTHETIC-HOST-TEST',
                    }
                    (evidence/'result.json').write_text(json.dumps(receipt))
                    print('synthetic adapter exercised; not JES evidence')
                    return return_code

            class FakeAdapter:
                @staticmethod
                def configure(driver):
                    driver.accepted_co3_adapter = True

            with (mock.patch.object(co4, 'FIXTURE', fixture),
                  mock.patch.object(co4, 'ACCEPTED', accepted),
                  mock.patch.object(co4, 'WORK', work),
                  mock.patch.object(co4, 'validate_inputs',
                                    return_value={'synthetic': 'true'}),
                  mock.patch.object(co4, 'load_module',
                                    side_effect=[FakeDriver(), FakeAdapter])):
                rc = co4.run()
            self.assertEqual(rc, return_code)
            receipt = json.loads((work/'synthetic-TEST-NOT-MVS'/
                                  'co4-result.json').read_text())
            self.assertEqual(receipt['march'], 'CO.4')
            self.assertEqual(receipt['status'],
                             'PASS' if rc == 0 else 'FAIL')
            self.assertEqual(receipt['expected_bcpl_records'],
                             ['CO4BCPL '+x for x in co4.EXPECTED])
            self.assertEqual(receipt['evidence_class'],
                             'SYNTHETIC-HOST-TEST')
            self.assertFalse(list(work.glob('_input-*')))

    def test_synthetic_success_receipt(self):
        self.exercise_fake_executor(0)

    def test_synthetic_failure_receipt(self):
        self.exercise_fake_executor(1)


if __name__ == '__main__':
    unittest.main()
