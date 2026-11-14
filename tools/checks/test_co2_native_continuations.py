#!/usr/bin/env python3
"""CO.2 repeat-yield test: source and wrapper guards; no MVS jobs."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'packaging/milestones/coroutines/candidates'
          / 'co2-native-continuations/source.bcpl')
RUNNER = ROOT / 'tools/coroutines/run-co2-native-continuations.py'
spec = importlib.util.spec_from_file_location('co2_continuations', RUNNER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CO2ContinuedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text('ascii')
        cls.one = cls.source.split('LET DEEP1(N)', 1)[1].split('LET DEEP2(N)', 1)[0]
        cls.two = cls.source.split('LET DEEP2(N)', 1)[1].split('LET WORK1(A)', 1)[0]
        cls.root = cls.source.split('LET START() BE', 1)[1]

    def test_valid_bcpl_cards_and_scopes(self):
        self.assertTrue(self.source.isascii())
        self.assertTrue(all(len(line) <= 80 for line in self.source.splitlines()))
        for depth in (1, 2):
            self.assertEqual(self.source.count(f'$({depth}'),
                             self.source.count(f'$){depth}'))

    def test_test_only_globals_and_two_allocations(self):
        for s in ('PEER1:295','PEER2:296','ROOTCTX:297',
                  'CO2INIT:298','CHANGECO:299',
                  'AND P1=VEC 23','AND P2=VEC 23',
                  'AND STACK1=GETVEC(1087)','AND STACK2=GETVEC(1087)'):
            self.assertIn(s, self.source)
        self.assertNotIn('STACK1!0', self.source)
        self.assertNotIn('STACK2!0', self.source)

    def test_two_suspensions_in_each_nested_stack(self):
        for token, body in (('CHANGECO(111,PEER2)', self.one),
                            ('CHANGECO(112,PEER2)', self.one),
                            ('CHANGECO(211,PEER1)', self.two),
                            ('CHANGECO(212,PEER1)', self.two)):
            self.assertIn(token, body)
        self.assertEqual(self.one.count('CHANGECO('), 2)
        self.assertEqual(self.two.count('CHANGECO('), 2)
        self.assertIn('IF GUARD \\=510+N RESULTIS 98', self.one)
        self.assertIn('IF GUARD \\=710+N RESULTIS 98', self.two)

    def test_stack_boundaries_checked_after_each_resume(self):
        self.assertEqual(self.one.count('STACKBASE \\= PEER1!4'), 3)
        self.assertEqual(self.two.count('STACKBASE \\= PEER2!4'), 3)
        self.assertEqual(self.root.count('STACKBASE \\= ROOTBASE'), 2)
        self.assertEqual(self.root.count('STACKEND \\= ROOTEND'), 2)

    def test_ordered_oracle_and_natural_worker_returns(self):
        for word in mod.EXPECTED:
            self.assertEqual(self.source.count('"CO2BCPL '+word+'"'), 1)
        self.assertEqual(self.source.count('RESULTIS 31'),1)
        self.assertEqual(self.source.count('RESULTIS 42'),1)
        self.assertIn('IF R \\=31', self.root)
        self.assertIn('IF R \\=42', self.root)
        self.assertIn('IF CHANGECO(99,P1) \\=-1', self.root)

    def test_wrapper_selects_source_and_preserves_base(self):
        baseline = Path('fixture')
        selected = mod.FixtureSelection(baseline)
        self.assertEqual(selected/'source.bcpl', SOURCE)
        self.assertEqual(selected/'cambridge-parm.txt',
                         baseline/'cambridge-parm.txt')
        self.assertEqual(mod.EVIDENCE, ROOT/'workarea/co2-native-continuations')

    def test_fake_driver_oracle_wiring_without_MVS(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/'fake_driver.py'
            file.write_text(
                'from pathlib import Path\n'
                'EXPECTED=("A1","B1","A2","R1","B2","R2","PASS")\n'
                'FIXTURE=Path("baseline")\n'
                'WORK=Path("evidence")\n'
                'def execute():\n'
                ' from pathlib import Path\n'
                ' assert len(EXPECTED)==9\n'
                ' assert (FIXTURE/"source.bcpl").name=="source.bcpl"\n'
                ' assert (FIXTURE/"cambridge-parm.txt") == '
                'Path("baseline/cambridge-parm.txt")\n'
                ' assert OUTPUT_RE.fullmatch("CO2BCPL X1")\n'
                ' assert not OUTPUT_RE.fullmatch("CO2BCPL UNEXPECTED")\n'
                ' assert WORK.name=="co2-native-continuations"\n'
                ' return 17\n')
            with patch.object(mod, 'BASE_RUNNER', file):
                self.assertEqual(mod.run(), 17)

    def test_unchanged_baseline_required(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'broken.py'
            file.write_text('EXPECTED=("A1","PASS")\n'
                            'def execute(): raise AssertionError("called")\n')
            with patch.object(mod, 'BASE_RUNNER', file):
                with self.assertRaisesRegex(RuntimeError, 'oracle changed'):
                    mod.run()

    def test_baseline_native_report_parser_fails_closed(self):
        spec = importlib.util.spec_from_file_location('co2_oracle', mod.BASE_RUNNER)
        self.assertIsNotNone(spec)
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
        report = ''.join('CO2BCPL '+x+'\n' for x in mod.BASE_EXPECTED)
        self.assertEqual(baseline.observed_records(report),
                         list(mod.BASE_EXPECTED))
        for suffix in ('CO2BCPL UNEXPECTED', 'CO2BCPL PASS EXTRA',
                       'CO2BCPL', 'CO2BCPL-FTERM'):
            with self.subTest(suffix=suffix):
                with self.assertRaises(baseline.CandidateError):
                    baseline.observed_records(report+suffix+'\n')
        self.assertEqual(baseline.observed_records(
            "SOURCE DC CL80'CO2BCPL PASS'\n"+report),
            list(mod.BASE_EXPECTED))

    def test_explicit_run_required(self):
        with patch.object(sys, 'argv', ['run-co2-native-continuations.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    mod.main()
        self.assertEqual(ctx.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
