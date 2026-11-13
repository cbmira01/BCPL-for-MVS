#!/usr/bin/env python3
"""Host-only structural/driver tests for the CO.1 nested BCPL probe."""
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
          / 'co1-bcpl-nested/source.bcpl')
RUNNER = ROOT / 'tools/coroutines/run-co1-bcpl-nested.py'

spec = importlib.util.spec_from_file_location('co1_nested', RUNNER)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class NestedCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text('ascii')

    def test_source_records(self):
        self.assertTrue(self.source.isascii())
        self.assertTrue(all(len(line) <= 80 for line in
                            self.source.splitlines()))

    def test_test_local_global_contract(self):
        for name in ('START:1', 'WRITES:60', 'NEWLINE:63', 'GETVEC:87',
                     'ROOTCTX:297', 'CO1INIT:298', 'CHANGECO:299'):
            self.assertIn(name, self.source)

    def test_six_live_recursive_frames(self):
        self.assertIn('LET DEEP(N) = VALOF', self.source)
        self.assertIn('K := DEEP(N-1)', self.source)
        self.assertIn('K := DEEP(5)', self.source)
        self.assertIn('LET SENTINEL=410+N', self.source)
        self.assertIn('IF SENTINEL \\=410+N RESULTIS 92', self.source)
        self.assertIn('IF K \\=28 RESULTIS 98', self.source)
        self.assertIn('RESULTIS K+N', self.source)

    def test_two_switches_and_natural_worker_return(self):
        self.assertEqual(self.source.count('CHANGECO('), 3)
        self.assertIn('CHANGECO(9,ROOTCTX)', self.source)
        self.assertIn('CHANGECO(7,PEER)', self.source)
        self.assertIn('CHANGECO(10,PEER)', self.source)
        self.assertIn('RESULTIS 11', self.source)
        self.assertIn('ROOTFLAG=2718', self.source)

    def test_output_oracle_is_unchanged(self):
        for marker in ('A1', 'R1', 'A2', 'R2', 'PASS'):
            self.assertEqual(self.source.count('"CO1BCPL '+marker+'"'),1)
        self.assertIn('"CO1BCPL FVALUE"', self.source)
        self.assertIn('"CO1BCPL FSECOND"', self.source)

    def test_fixture_selection_reuses_accepted_asm(self):
        base = ROOT / 'packaging/milestones/coroutines/candidates/co1-bcpl-switch'
        selection = probe.FixtureSelection(base)
        self.assertEqual(selection / 'source.bcpl', SOURCE)
        self.assertEqual(selection / 'co1change.asm', base / 'co1change.asm')
        self.assertEqual(selection / 'cambridge-parm.txt',
                         base / 'cambridge-parm.txt')

    def test_run_uses_driver_without_mvs_calls(self):
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / 'base.py'
            fake.write_text("EXPECTED = ('A1','R1','A2','R2','PASS')\n"
                            "from pathlib import Path\n"
                            "FIXTURE = Path('unused')\n"
                            "WORK = None\n"
                            "def execute():\n"
                            "    assert WORK.name == 'co1-bcpl-nested'\n"
                            "    assert (FIXTURE / 'source.bcpl').name == 'source.bcpl'\n"
                            "    assert (FIXTURE / 'co1change.asm').name == 'co1change.asm'\n"
                            "    return 17\n")
            with patch.object(probe, 'BASE_RUNNER', fake):
                self.assertEqual(probe.run(),17)

    def test_changed_baseline_oracle_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / 'base.py'
            fake.write_text("EXPECTED=('A1','PASS')\n"
                            "FIXTURE='unused'\n"
                            "def execute(): raise AssertionError('called')\n")
            with patch.object(probe, 'BASE_RUNNER', fake):
                with self.assertRaisesRegex(RuntimeError, 'oracle changed'):
                    probe.run()

    def test_requires_explicit_run(self):
        with patch.object(sys,'argv',['run-co1-bcpl-nested.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    probe.main()
        self.assertEqual(cm.exception.code,2)


if __name__ == '__main__':
    unittest.main()
