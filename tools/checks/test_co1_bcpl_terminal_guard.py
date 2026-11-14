#!/usr/bin/env python3
"""Offline source, ABI and runner safeguards for CO.1 terminal-guard probe."""
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
FIXTURE = ROOT / ('packaging/milestones/coroutines/candidates/'
                  'co1-bcpl-terminal-guard')
BASE = ROOT / ('packaging/milestones/coroutines/candidates/'
               'co1-bcpl-switch')
RUNNER = ROOT / 'tools/coroutines/run-co1-bcpl-terminal-guard.py'
spec = importlib.util.spec_from_file_location('co1_terminal_guard', RUNNER)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class TerminalGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bcpl = (FIXTURE / 'source.bcpl').read_text('ascii')
        cls.asm = (FIXTURE / 'co1change.asm').read_text('ascii')
        cls.worker_exit = cls.asm.split('CO1WDONE BALR', 1)[1].split(
            'CO1BAD', 1)[0]
        cls.switch = cls.asm.split('CO1SW    STM', 1)[1].split(
            'CO1RET BCR', 1)[0]
        cls.reject = ('CO1TERM  L' + cls.asm.split('CO1TERM  L', 1)[1]).split(
            'CO1RET BCR', 1)[0]
        cls.root = cls.bcpl.split('LET START() BE', 1)[1]

    def test_fixed_format_assembly_and_bcpl_input(self):
        for number, row in enumerate(self.asm.splitlines(), 1):
            self.assertLessEqual(len(row), 71, (number, row))
            self.assertTrue(row.isascii())
            if row and not row.startswith((' ', '*')):
                self.assertRegex(row.split()[0],
                                 r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')
        self.assertTrue(self.bcpl.isascii())
        self.assertTrue(all(len(r) <= 80 for r in self.bcpl.splitlines()))

    def test_terminal_state_written_before_natural_return_switch(self):
        for text in ('L     4,CURPTR', 'LA    0,3', 'ST    0,0(4)',
                     'L     8,ROOTPTR', 'L     4,=A(CO1SW)',
                     'BALR  6,4'):
            self.assertIn(text, self.worker_exit)
        indices = [self.worker_exit.index(x) for x in
                   ('L     4,CURPTR', 'LA    0,3', 'ST    0,0(4)',
                    'L     8,ROOTPTR', 'L     4,=A(CO1SW)',
                    'BALR  6,4')]
        self.assertEqual(indices, sorted(indices))

    def test_reject_known_terminated_target_before_source_snapshot(self):
        for text in ('L     2,CO1SREG+32', 'SLL   2,2', 'L     0,0(2)',
                     "C     0,=F'3'", 'BC    8,CO1TERM',
                     'L     2,CURPTR', 'MVC   32(64,2),CO1SREG'):
            self.assertIn(text, self.switch)
        self.assertLess(self.switch.index('BC    8,CO1TERM'),
                        self.switch.index('L     2,CURPTR'))
        self.assertLess(self.switch.index('BC    8,CO1TERM'),
                        self.switch.index('MVC   32(64,2),CO1SREG'))

    def test_reject_makes_only_three_word_return_frame(self):
        for text in ('L     0,CO1SREG+16', 'ST    0,0(5)',
                     'L     0,CO1SREG+20', 'ST    0,4(5)',
                     'L     0,CO1SREG+24', 'ST    0,8(5)',
                     "L     7,=F'-1'", 'BCR   15,11'):
            self.assertIn(text, self.reject)
        self.assertEqual(re.findall(r'\bST\s+0,(\d+)\(5\)', self.reject),
                         ['0', '4', '8'])
        self.assertNotIn('STM   0,15,0(15)', self.asm)

    def test_reject_restores_r0_r2_r10_and_does_not_change_context(self):
        for text in ('L     2,CO1SREG+8', 'L     0,CO1SREG',
                     'L     10,CO1SREG+40'):
            self.assertIn(text, self.reject)
        self.assertLess(self.reject.index('L     0,CO1SREG'),
                        self.reject.index('L     10,CO1SREG+40'))
        for token in ('CURPTR', 'STKLIM', 'APLIMIT', '216(12)', '220(12)',
                      'LM    0,15', 'BALR'):
            self.assertNotIn(token, self.reject)
        self.assertIn('ST    5,52(2)', self.switch)
        self.assertIn('LM    0,15,0(1)', self.switch)

    def test_candidate_is_only_live_descriptor_guard(self):
        self.assertIn('CO1SREG  DS    16F', self.asm)
        self.assertIn('CO1INIT  STM   4,10,0(15)', self.asm)
        self.assertIn('CO1WBOOT BALR  6,4', self.asm)
        self.assertIn('CO1RET BCR   15,11', self.asm)
        self.assertIn('No arbitrary-pointer, stale-pointer', self.asm)

    def test_two_distinct_allocations_and_temporary_globals(self):
        for token in ('START:1', 'WRITES:60', 'NEWLINE:63',
                      'GETVEC:87', 'ROOTCTX:297', 'CO1INIT:298',
                      'CHANGECO:299', 'LET ROOT=VEC 23',
                      'AND P1=VEC 23', 'AND P2=VEC 23',
                      'AND STACK1=GETVEC(1087)',
                      'AND STACK2=GETVEC(1087)',
                      'STACK1=STACK2'):
            self.assertIn(token, self.bcpl)
        self.assertEqual(self.root.count('CO1INIT('), 2)

    def test_both_workers_suspend_then_naturally_return(self):
        for token in ('CHANGECO(101,ROOTCTX)',
                      'CHANGECO(202,ROOTCTX)',
                      'RETURNED \\=11', 'RETURNED \\=22',
                      'RESULTIS 31', 'RESULTIS 42'):
            self.assertIn(token.replace('\\\\','\\'), self.bcpl)
        self.assertEqual(self.bcpl.count('CHANGECO('), 8)

    def test_terminal_resume_rejection_and_liveness_after_first(self):
        schedule = ('A := CHANGECO(7,P1)', 'B := CHANGECO(8,P2)',
                    'C := CHANGECO(11,P1)', 'D := CHANGECO(777,P1)',
                    'E := CHANGECO(22,P2)', 'F := CHANGECO(888,P2)')
        offsets = [self.root.index(x) for x in schedule]
        self.assertEqual(offsets, sorted(offsets))
        for text in ('IF C \\=31 | P1!0 \\=3',
                     'IF D \\=-1 | P1!0 \\=3',
                     'IF E \\=42 | P2!0 \\=3',
                     'IF F \\=-1 | P2!0 \\=3'):
            self.assertIn(text.replace('\\\\','\\'), self.root)
        self.assertEqual(self.root.count('ROOTFLAG \\=2718'.replace('\\\\','\\')), 6)

    def test_exact_positive_trace_and_failing_oracle(self):
        for token in ('A1', 'R1', 'A2', 'R2', 'PASS'):
            self.assertEqual(self.bcpl.count('"CO1BCPL '+token+'"'), 1)
        self.assertLess(self.root.index('"CO1BCPL R1"'),
                        self.root.index('B := CHANGECO(8,P2)'))
        self.assertLess(self.root.index('"CO1BCPL R2"'),
                        self.root.index('C := CHANGECO(11,P1)'))
        for bad in ('FALLOC', 'FINIT', 'FVALUE', 'FLOCAL', 'FSECOND'):
            self.assertIn('"CO1BCPL '+bad+'"', self.root)

    def test_fixture_wires_only_new_bcpl_and_asm(self):
        selected=probe.FixtureSelection(BASE)
        self.assertEqual(selected/'source.bcpl', FIXTURE/'source.bcpl')
        self.assertEqual(selected/'co1change.asm', FIXTURE/'co1change.asm')
        self.assertEqual(selected/'cambridge-parm.txt', BASE/'cambridge-parm.txt')
        self.assertEqual(probe.EVIDENCE, ROOT/'workarea/co1-bcpl-terminal-guard')

    def test_fake_driver_integration_and_bad_oracle(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=Path(temp)/'baseline.py'
            fake.write_text(
                'from pathlib import Path\n'
                'EXPECTED=("A1","R1","A2","R2","PASS")\n'
                'FIXTURE=Path("baseline")\n'
                'WORK=Path("missing")\n'
                'def execute():\n'
                ' assert (FIXTURE/"source.bcpl").name == "source.bcpl"\n'
                ' assert (FIXTURE/"co1change.asm").name == "co1change.asm"\n'
                ' assert (FIXTURE/"cambridge-parm.txt") == Path("baseline/cambridge-parm.txt")\n'
                ' assert WORK.name == "co1-bcpl-terminal-guard"\n'
                ' return 17\n')
            with patch.object(probe, 'BASE_RUNNER', fake):
                self.assertEqual(probe.run(),17)
            fake.write_text('EXPECTED=("A1","PASS")\n'
                            'FIXTURE="unused"\n'
                            'def execute(): raise AssertionError("unexpected")\n')
            with patch.object(probe, 'BASE_RUNNER', fake):
                with self.assertRaisesRegex(RuntimeError, 'oracle changed'):
                    probe.run()

    def test_cli_rejects_unspecified_mvs_execution(self):
        with patch.object(sys,'argv',['run-co1-bcpl-terminal-guard.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    probe.main()
        self.assertEqual(caught.exception.code,2)


if __name__=='__main__':
    unittest.main()
