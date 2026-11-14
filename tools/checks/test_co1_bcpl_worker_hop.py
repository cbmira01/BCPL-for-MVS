#!/usr/bin/env python3
"""Host-only structure and driver guards for CO.1 direct worker hop."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'packaging/milestones/coroutines/candidates'
          / 'co1-bcpl-worker-hop/source.bcpl')
RUNNER = ROOT / 'tools/coroutines/run-co1-bcpl-worker-hop.py'
BASE = ROOT / 'packaging/milestones/coroutines/candidates/co1-bcpl-switch'
spec = importlib.util.spec_from_file_location('co1_worker_hop', RUNNER)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class WorkerHopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text('ascii')
        cls.a = cls.src.split('LET WORK1(A)', 1)[1].split('LET WORK2(A)', 1)[0]
        cls.b = cls.src.split('LET WORK2(A)', 1)[1].split('LET START()', 1)[0]
        cls.root = cls.src.split('LET START()', 1)[1]

    def test_ascii_records_and_bcpl_structure(self):
        self.assertTrue(self.src.isascii())
        self.assertTrue(all(len(line) <= 80 for line in self.src.splitlines()))
        self.assertEqual(self.src.count('LET WORK1(A)'), 1)
        self.assertEqual(self.src.count('LET WORK2(A)'), 1)
        self.assertEqual(self.src.count('LET START() BE'), 1)
        self.assertEqual(self.src.count('$(1'), 3)
        self.assertEqual(self.src.count('$)1'), 3)
        self.assertEqual(self.src.count('$(2'), 6)
        self.assertEqual(self.src.count('$)2'), 6)

    def test_test_local_globals_and_historical_imports(self):
        for declaration in ('START:1', 'WRITES:60', 'NEWLINE:63',
                            'GETVEC:87', 'PEER1:295', 'PEER2:296',
                            'ROOTCTX:297', 'CO1INIT:298', 'CHANGECO:299'):
            self.assertIn(declaration, self.src)
        self.assertEqual(self.src.count('ROOTCTX := ROOT'), 1)
        self.assertEqual(self.src.count('PEER1 := P1'), 1)
        self.assertEqual(self.src.count('PEER2 := P2'), 1)

    def test_distinct_live_worker_allocations_and_descriptors(self):
        for token in ('LET ROOT=VEC 23', 'AND P1=VEC 23', 'AND P2=VEC 23',
                      'AND STACK1=GETVEC(1087)', 'AND STACK2=GETVEC(1087)',
                      'STACK1=STACK2', 'CO1INIT(ROOT,P1,STACK1,WORK1)',
                      'CO1INIT(ROOT,P2,STACK2,WORK2)'):
            self.assertIn(token, self.root)
        self.assertLess(self.root.index('CO1INIT(ROOT,P1'),
                        self.root.index('CO1INIT(ROOT,P2'))
        self.assertLess(self.root.index('CO1INIT(ROOT,P2'),
                        self.root.index('A := CHANGECO(7,PEER1)'))

    def test_worker_a_to_worker_b_then_worker_b_to_worker_a(self):
        self.assertIn('FROMB := CHANGECO(17,PEER2)', self.a)
        self.assertIn('FROMROOT := CHANGECO(23,PEER1)', self.b)
        self.assertIn('IF FROMB \\=23 | TOKEN \\=3101 RESULTIS 98', self.a)
        self.assertIn('IF A \\=17 | PEER2!1 \\=ROOTCTX RESULTIS 97', self.b)
        self.assertIn('IF A \\=7 | PEER1!1 \\=ROOTCTX RESULTIS 97', self.a)

    def test_direct_hop_has_no_root_intermediate(self):
        self.assertNotIn('CHANGECO(17,ROOTCTX)', self.a)
        self.assertNotIn('CHANGECO(23,ROOTCTX)', self.b)
        self.assertIn('FROMROOT := CHANGECO(33,ROOTCTX)', self.a)
        self.assertEqual(self.src.count('CHANGECO('), 6)

    def test_natural_return_from_both_workers(self):
        self.assertIn('LET TOKEN=3101', self.a)
        self.assertIn('LET TOKEN=4202', self.b)
        self.assertIn('IF FROMROOT \\=44 | TOKEN \\=3101 RESULTIS 98', self.a)
        self.assertIn('IF FROMROOT \\=55 | TOKEN \\=4202 RESULTIS 98', self.b)
        self.assertIn('RESULTIS 31', self.a)
        self.assertIn('RESULTIS 42', self.b)
        self.assertIn('B := CHANGECO(55,PEER2)', self.root)
        self.assertIn('C := CHANGECO(44,PEER1)', self.root)
        self.assertIn('IF B \\=42', self.root)
        self.assertIn('IF C \\=31', self.root)

    def test_root_checks_its_sentinel_after_every_return(self):
        self.assertIn('AND ROOTFLAG=2718', self.root)
        self.assertEqual(self.root.count('ROOTFLAG \\=2718'), 3)
        self.assertIn('IF A \\=33', self.root)
        self.assertEqual(self.root.count('FINISH'), 7)

    def test_strict_output_markers_appear_in_expected_control_path(self):
        for token, body in (('A1', self.a), ('R1', self.b),
                            ('A2', self.a), ('R2', self.root),
                            ('PASS', self.root)):
            self.assertIn('WRITES("CO1BCPL '+token+'")', body)
            self.assertEqual(self.src.count('"CO1BCPL '+token+'"'), 1)
        self.assertLess(self.a.index('"CO1BCPL A1"'),
                        self.a.index('FROMB := CHANGECO'))
        self.assertLess(self.a.index('FROMB := CHANGECO'),
                        self.a.index('"CO1BCPL A2"'))
        self.assertLess(self.b.index('"CO1BCPL R1"'),
                        self.b.index('FROMROOT := CHANGECO'))
        self.assertLess(self.root.index('"CO1BCPL R2"'),
                        self.root.index('B := CHANGECO'))
        self.assertLess(self.root.index('C := CHANGECO'),
                        self.root.index('"CO1BCPL PASS"'))

    def test_fail_closed_output_diagnostics(self):
        for name in ('FALLOC', 'FINIT', 'FVALUE', 'FSECOND', 'FLOCAL'):
            self.assertIn('WRITES("CO1BCPL '+name+'")', self.root)
        self.assertNotIn('CO1BCPL FAIL', self.src)

    def test_fixture_keeps_original_s370_and_compiler_options(self):
        selection = probe.FixtureSelection(BASE)
        self.assertEqual(selection/'source.bcpl', SOURCE)
        self.assertEqual(selection/'co1change.asm', BASE/'co1change.asm')
        self.assertEqual(selection/'cambridge-parm.txt', BASE/'cambridge-parm.txt')
        self.assertEqual(probe.EVIDENCE, ROOT/'workarea/co1-bcpl-worker-hop')

    def test_synthetic_successful_runner_wiring_without_MVS(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp)/'baseline.py'
            stub.write_text(
                'from pathlib import Path\n'
                'EXPECTED=("A1","R1","A2","R2","PASS")\n'
                'FIXTURE=Path("baseline")\n'
                'WORK=Path("missing")\n'
                'def execute():\n'
                ' assert (FIXTURE/"source.bcpl").name == "source.bcpl"\n'
                ' assert (FIXTURE/"co1change.asm") == Path("baseline/co1change.asm")\n'
                ' assert WORK.name == "co1-bcpl-worker-hop"\n'
                ' return 17\n')
            with patch.object(probe, 'BASE_RUNNER', stub):
                self.assertEqual(probe.run(), 17)

    def test_reject_modified_native_output_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub=Path(tmp)/'baseline.py'
            stub.write_text('EXPECTED=("A1","PASS")\n'
                            'FIXTURE="irrelevant"\n'
                            'def execute(): raise AssertionError("called")\n')
            with patch.object(probe, 'BASE_RUNNER', stub):
                with self.assertRaisesRegex(RuntimeError, 'oracle changed'):
                    probe.run()

    def test_run_flag_required_without_submitting_jobs(self):
        with patch.object(sys, 'argv', ['run-co1-bcpl-worker-hop.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    probe.main()
        self.assertEqual(caught.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
