#!/usr/bin/env python3
"""Host-only source and runner checks for CO.1 two-worker MVS experiment."""
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
          / 'co1-bcpl-two-workers/source.bcpl')
RUNNER = ROOT / 'tools/coroutines/run-co1-bcpl-two-workers.py'
BASE = ROOT / 'packaging/milestones/coroutines/candidates/co1-bcpl-switch'
spec = importlib.util.spec_from_file_location('co1_two_workers', RUNNER)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class TwoWorkerCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text('ascii')

    def test_card_widths(self):
        self.assertTrue(self.src.isascii())
        self.assertTrue(all(len(row) <= 80 for row in self.src.splitlines()))

    def test_globals_not_production_allocations(self):
        for line in ('START:1', 'WRITES:60', 'NEWLINE:63', 'GETVEC:87',
                     'ROOTCTX:297', 'CO1INIT:298', 'CHANGECO:299'):
            self.assertIn(line, self.src)

    def test_distinct_buffers_and_descriptors(self):
        for token in ('LET ROOT=VEC 23', 'AND PEER1=VEC 23',
                      'AND PEER2=VEC 23', 'AND STACK1=GETVEC(1087)',
                      'AND STACK2=GETVEC(1087)', 'STACK1=STACK2'):
            self.assertIn(token, self.src)

    def test_both_workers_initialized_only_from_root(self):
        self.assertEqual(self.src.count('CO1INIT('), 2)
        self.assertIn('CO1INIT(ROOT,PEER1,STACK1,WORK1)', self.src)
        self.assertIn('CO1INIT(ROOT,PEER2,STACK2,WORK2)', self.src)
        self.assertLess(self.src.index('A := CHANGECO(7,PEER1)'),
                        self.src.index('CO1INIT(ROOT,PEER2,STACK2,WORK2)'))
        self.assertLess(self.src.index('CO1INIT(ROOT,PEER2,STACK2,WORK2)'),
                        self.src.index('B := CHANGECO(8,PEER2)'))

    def test_complete_two_worker_switch_schedule(self):
        schedule = ('A := CHANGECO(7,PEER1)',
                    'B := CHANGECO(8,PEER2)',
                    'C := CHANGECO(11,PEER1)',
                    'D := CHANGECO(22,PEER2)')
        offsets = [self.src.index(x) for x in schedule]
        self.assertEqual(offsets, sorted(offsets))
        for token in ('CHANGECO(101,ROOTCTX)', 'CHANGECO(202,ROOTCTX)',
                      'IF A \\=101', 'IF B \\=202',
                      'IF C \\=31', 'IF D \\=42'):
            self.assertIn(token, self.src)
        self.assertEqual(self.src.count('CHANGECO('), 6)

    def test_independent_worker_local_state_and_returns(self):
        for token in ('LET TOKEN=3101', 'LET TOKEN=4202',
                      'TOKEN \\=3101', 'TOKEN \\=4202',
                      'RESULTIS 31', 'RESULTIS 42'):
            self.assertIn(token, self.src)
        self.assertIn('ROOTFLAG=2718', self.src)
        self.assertEqual(self.src.count('ROOTFLAG \\=2718'), 4)

    def test_exact_positive_trace_and_instrumented_failures(self):
        ordered = ('CO1BCPL A1', 'CO1BCPL R1',
                   'CO1BCPL A2', 'CO1BCPL R2', 'CO1BCPL PASS')
        worker1 = self.src.split('LET WORK1(A)', 1)[1].split('LET WORK2(A)', 1)[0]
        worker2 = self.src.split('LET WORK2(A)', 1)[1].split('LET START()', 1)[0]
        root = self.src.split('LET START()', 1)[1]
        self.assertIn('"CO1BCPL A1"', worker1)
        self.assertIn('"CO1BCPL A2"', worker2)
        positions = [root.index('"'+m+'"') for m in ('CO1BCPL R1',
                                                'CO1BCPL R2',
                                                'CO1BCPL PASS')]
        self.assertEqual(positions, sorted(positions))
        for marker in ordered:
            self.assertEqual(self.src.count('"'+marker+'"'), 1)
        for marker in ('FALLOC','FINIT','FVALUE','FSECOND','FLOCAL'):
            self.assertIn('CO1BCPL '+marker, self.src)
        self.assertNotIn('"CO1BCPL FAIL"',self.src)

    def test_wrapper_selects_only_source_and_evidence(self):
        selection = probe.FixtureSelection(BASE)
        self.assertEqual(selection / 'source.bcpl', SOURCE)
        self.assertEqual(selection / 'co1change.asm', BASE / 'co1change.asm')
        self.assertEqual(selection / 'cambridge-parm.txt',
                         BASE / 'cambridge-parm.txt')
        self.assertEqual(probe.EVIDENCE, ROOT/'workarea/co1-bcpl-two-workers')

    def test_fake_runner_integration_without_mvs(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp)/'baseline.py'
            stub.write_text(
                'from pathlib import Path\n'
                "EXPECTED=('A1','R1','A2','R2','PASS')\n"
                "FIXTURE=Path('baseline')\n"
                'WORK=Path("missing")\n'
                'def execute():\n'
                ' assert (FIXTURE / "source.bcpl").name == "source.bcpl"\n'
                ' assert (FIXTURE / "co1change.asm")==Path("baseline/co1change.asm")\n'
                ' assert WORK.name == "co1-bcpl-two-workers"\n'
                ' return 17\n', encoding='utf8')
            with patch.object(probe, 'BASE_RUNNER', stub):
                self.assertEqual(probe.run(), 17)

    def test_fail_closed_if_oracle_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp)/'baseline.py'
            stub.write_text('EXPECTED=("A1","PASS")\n'
                            'FIXTURE="irrelevant"\n'
                            'def execute(): raise AssertionError("should not run")\n')
            with patch.object(probe,'BASE_RUNNER',stub):
                with self.assertRaisesRegex(RuntimeError, 'oracle changed'):
                    probe.run()

    def test_requires_explicit_run(self):
        with patch.object(sys, 'argv',['run-co1-bcpl-two-workers.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    probe.main()
        self.assertEqual(raised.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
