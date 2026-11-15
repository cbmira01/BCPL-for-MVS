#!/usr/bin/env python3
"""Offline-only tests of CO.4 batch staging, strict oracles and fail-fast."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'tools/coroutines/run-co4-verification-batch.py'
spec = importlib.util.spec_from_file_location('co4_batch', TARGET)
if spec is None or spec.loader is None:
    raise RuntimeError('runner not found')
co4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co4)


class OracleAndSourceTests(unittest.TestCase):
    def test_exact_case_order_and_names(self):
        self.assertEqual(tuple(co4.CASES), ('stack', 'churn', 'busy'))
        self.assertEqual(tuple(len(v[2]) for v in co4.CASES.values()),
                         (6, 7, 10))

    def test_case_sources_validate(self):
        for key in co4.CASES:
            with self.subTest(key=key):
                value = co4.validate_case(key)
                self.assertEqual(value['expected_count'],
                                 str(len(co4.CASES[key][2])))
                self.assertEqual(len(value['sha256']), 64)

    def test_strict_order_oracle(self):
        for key, (_, prefix, expected) in co4.CASES.items():
            with self.subTest(key=key):
                report = 'unrelated record\n' + '\n'.join(
                    prefix + ' ' + token for token in expected)
                self.assertEqual(co4.parse_records(report, prefix),
                                 list(expected))

    def test_malformed_record_rejected(self):
        for prefix in ('CO4STK', 'CO4CHURN', 'CO4BUSY'):
            for malformed in (prefix, prefix + ' EXTRA BAD',
                              prefix + ' BAD-1'):
                with self.subTest(row=malformed):
                    with self.assertRaisesRegex(co4.CandidateError,
                                                'malformed'):
                        co4.parse_records(malformed, prefix)

    def test_drifted_marker_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            file = co4.FIXTURE/'stack-source.bcpl'
            (fixture/file.name).write_text(file.read_text().replace(
                'MARK("PASS")', 'MARK("BROKEN")'))
            with self.assertRaisesRegex(co4.CandidateError,
                                        'missing/duplicate marker PASS'):
                co4.validate_case('stack', fixture)

    def test_unsafe_descriptor_api_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            file = co4.FIXTURE/'busy-source.bcpl'
            (fixture/file.name).write_text(file.read_text().replace(
                'MARK("MADE")', 'MARK("MADE")\n    CALLCO(1,0)'))
            with self.assertRaisesRegex(co4.CandidateError,
                                        'unsafe arbitrary descriptor'):
                co4.validate_case('busy', fixture)

    def test_no_bad_cards_and_no_hardcoded_stale_pointer_calls(self):
        for source, _, _ in co4.CASES.values():
            lines = (co4.FIXTURE/source).read_text().splitlines()
            self.assertTrue(all(len(s) <= 80 and s.isascii()
                                and '\t' not in s for s in lines))
            joined = '\n'.join(lines)
            self.assertNotIn('CALLCO(1,', joined)
            self.assertNotIn('RESUMECO(1,', joined)

    def test_source_case_distinction(self):
        self.assertIn('META!0', (co4.FIXTURE/'stack-source.bcpl').read_text())
        self.assertIn('FOR I=1 TO 16 DO',
                      (co4.FIXTURE/'churn-source.bcpl').read_text())
        self.assertIn('RESUMECO(PARENT,0)',
                      (co4.FIXTURE/'busy-source.bcpl').read_text())


class NativeAdapterOfflineTests(unittest.TestCase):
    def test_run_one_stages_and_writes_synthetic_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            accepted = path/'accepted'
            accepted.mkdir()
            (accepted/'library.bcpl').write_text('NOT A COMPILER INPUT\n')
            (accepted/'cambridge-parm.txt').write_text('/CN'+'/'*77+'\n')
            session = path/'session'
            session.mkdir()

            class Driver:
                def execute(self, scenario):
                    self_outer.assertEqual(scenario, 'first')
                    self_outer.assertEqual(self.EXPECTED,
                                           co4.CASES['stack'][2])
                    self_outer.assertEqual(
                        (self.FIXTURE/'library.bcpl').read_text(),
                        'NOT A COMPILER INPUT\n')
                    report = '\n'.join('CO4STK '+s for s in self.EXPECTED)
                    self_outer.assertEqual(self.observed_records(report),
                                           list(self.EXPECTED))
                    d = self.WORK/'synthetic-NOT-JES'
                    d.mkdir()
                    (d/'result.json').write_text(json.dumps({
                        'status':'PASS', 'native_job':'NOT-JES',
                        'evidence_class':'HOST-SYNTHETIC'}))
                    return 0

            class Adapter:
                pass

            class Prior:
                ACCEPTED = accepted
                BASE_RUNNER = path/'unused-base.py'
                CO3_ADAPTER = path/'unused-adapter.py'

                @staticmethod
                def load_module(name, filename):
                    return Driver() if 'driver_' in name else Adapter()

                @staticmethod
                def configure(driver, adapter, fixture, work):
                    driver.FIXTURE = fixture
                    driver.WORK = work

            self_outer = self
            hashes = {'cases': {'stack': co4.validate_case('stack')}}
            result = co4.run_one('stack', session, Prior(), hashes)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['native_job'], 'NOT-JES')
            self.assertEqual(result['evidence_class'], 'HOST-SYNTHETIC')
            self.assertTrue((session/'stack'/'synthetic-NOT-JES'/
                             'co4-case-result.json').is_file())
            self.assertFalse(list((session/'stack').glob('_input-*')))

    def _fake_batch(self, failure_case):
        with tempfile.TemporaryDirectory() as temp:
            place = Path(temp)
            emitted = []

            def fake_one(key, session, previous, hashes):
                emitted.append(key)
                if key == failure_case:
                    return {'case':key, 'status':'FAIL', 'rc':1}
                return {'case':key, 'status':'PASS', 'rc':0}

            with (mock.patch.object(co4,'WORK',place),
                  mock.patch.object(co4,'validate_inputs',return_value={}),
                  mock.patch.object(co4,'load_module',return_value=object()),
                  mock.patch.object(co4,'run_one',side_effect=fake_one)):
                rc = co4.run_batch()
            results = list(place.glob('*/batch-result.json'))
            self.assertEqual(len(results), 1)
            outcome = json.loads(results[0].read_text())
            self.assertEqual(outcome['status'], 'FAIL' if failure_case else 'PASS')
            return rc, emitted, outcome

    def test_batch_three_case_pass(self):
        rc, names, result = self._fake_batch(None)
        self.assertEqual(rc, 0)
        self.assertEqual(names, ['stack', 'churn', 'busy'])
        self.assertEqual(len(result['cases']), 3)

    def test_batch_fail_fast(self):
        rc, names, result = self._fake_batch('churn')
        self.assertEqual(rc, 1)
        self.assertEqual(names, ['stack', 'churn'])
        self.assertEqual(len(result['cases']), 2)

    def test_inherited_validator_is_mandatory(self):
        class FakePrevious:
            @staticmethod
            def validate_inputs():
                raise ValueError('CO.3 pin mismatch')
        with mock.patch.object(co4,'load_module',return_value=FakePrevious()):
            with self.assertRaisesRegex(ValueError,'pin mismatch'):
                co4.validate_inputs()


if __name__ == '__main__':
    unittest.main()
