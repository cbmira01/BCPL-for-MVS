#!/usr/bin/env python3
"""Offline tests of the isolated CO.1 two-worker descriptor registry probe."""
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
FIXTURE = (ROOT / 'packaging/milestones/coroutines/candidates'
           / 'co1-bcpl-registry-guard')
BASE = (ROOT / 'packaging/milestones/coroutines/candidates'
        / 'co1-bcpl-switch')
RUNNER = ROOT / 'tools/coroutines/run-co1-bcpl-registry-guard.py'
spec = importlib.util.spec_from_file_location('co1_registry_guard', RUNNER)
probe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(probe)


class RegistryGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asm = (FIXTURE / 'co1change.asm').read_text('ascii')
        cls.bcpl = (FIXTURE / 'source.bcpl').read_text('ascii')
        cls.initializer = cls.asm.split('CO1INIT  STM', 1)[1].split(
            'CO1WBOOT BALR', 1)[0]
        cls.switch = cls.asm.split('CO1SW    STM', 1)[1].split(
            'CO1TERM  L', 1)[0]
        cls.reject = ('CO1TERM  L' + cls.asm.split('CO1TERM  L', 1)[1]).split(
            'CO1RET BCR', 1)[0]
        cls.root = cls.bcpl.split('LET START() BE', 1)[1]

    def test_ifox_card_format_and_label_widths(self):
        self.assertTrue(self.asm.isascii())
        for number, card in enumerate(self.asm.splitlines(), 1):
            self.assertLessEqual(len(card), 71, (number, card))
            self.assertNotIn('\t', card)
            if card and card[0] not in (' ', '*'):
                self.assertRegex(card.split()[0],
                                 r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')

    def test_bcpl_card_widths_and_global_numbers(self):
        self.assertTrue(self.bcpl.isascii())
        self.assertTrue(all(len(row) <= 80 for row in self.bcpl.splitlines()))
        for global_decl in ('START:1', 'WRITES:60', 'NEWLINE:63',
                            'GETVEC:87', 'ROOTCTX:297', 'CO1INIT:298',
                            'CHANGECO:299'):
            self.assertIn(global_decl, self.bcpl)
        self.assertNotIn('CREATECO:', self.bcpl)

    def test_initializer_has_fixed_size_root_and_two_worker_registry(self):
        for token in ("REGCNT   DC    F'0'", "REGW1    DC    F'0'",
                      "REGW2    DC    F'0'", 'ROOTPTR  DC',
                      'CO1RG1   ST    8,REGW1',
                      'CO1RG2   ST    8,REGW2',
                      "L     7,=F'-2'", 'CO1INBAD LR    0,6'):
            self.assertIn(token, self.asm)
        self.assertIn("C     4,=F'1'", self.initializer)
        self.assertIn('BC    7,CO1INBAD', self.initializer)
        self.assertEqual(self.asm.count('REGCNT   DC'), 1)
        self.assertEqual(self.asm.count('REGW1    DC'), 1)
        self.assertEqual(self.asm.count('REGW2    DC'), 1)

    def test_registry_accepts_only_first_two_distinct_workers(self):
        for instruction in ('L     4,REGCNT', 'C     7,ROOTPTR',
                            'C     8,REGW1', 'C     8,REGW2',
                            'BC    8,CO1RG2', 'B     CO1INBAD',
                            'CO1RGOK  ST    7,ROOTPTR'):
            self.assertIn(instruction, self.initializer)
        self.assertLess(self.initializer.index('B     CO1INBAD'),
                        self.initializer.index('ST    0,12(8)'))
        self.assertLess(self.initializer.index('CO1RGOK'),
                        self.initializer.index('ST    0,12(8)'))
        self.assertLess(self.initializer.index('CO1RGOK'),
                        self.initializer.index('CO1PAINT'))

    def test_initialization_error_restores_r0_r10_and_no_stack_write(self):
        reject = self.initializer.split('CO1INBAD LR', 1)[1].split('LTORG', 1)[0]
        self.assertIn('0,6', reject)
        self.assertIn("L     7,=F'-2'", reject)
        self.assertIn('L     10,24(5)', reject)
        self.assertIn('BCR   15,11', reject)
        self.assertNotIn('CURPTR', reject)
        self.assertNotIn('ROOTPTR', reject)
        self.assertNotIn('0(8)', reject)
        self.assertIn('L     10,24(5)', self.initializer.split(
            'LR    0,6              RESTORE CG370 R0', 1)[1])

    def test_switch_target_membership_precedes_any_target_dereference(self):
        needle = ('L     2,CO1SREG+32', 'SLL   2,2', 'LTR   2,2',
                  'BC    8,CO1TERM', 'C     2,ROOTPTR',
                  'C     2,REGW1', 'C     2,REGW2',
                  'BC    7,CO1TERM', 'CO1REGOK C     2,CURPTR',
                  'L     0,0(2)', "C     0,=F'3'",
                  'L     2,CURPTR', 'MVC   32(64,2),CO1SREG')
        for text in needle:
            self.assertIn(text, self.switch)
        indexes = [self.switch.index(text) for text in needle]
        self.assertEqual(indexes, sorted(indexes))
        # Membership must be established before the FIRST read at 0(R2).
        self.assertLess(self.switch.index('CO1REGOK'),
                        self.switch.index('L     0,0(2)'))
        self.assertEqual(self.switch.count('L     0,0(2)'), 1)
        self.assertLess(self.switch.index('BC    7,CO1TERM'),
                        self.switch.index('L     0,0(2)'))

    def test_unknown_and_self_rejected_before_context_mutation(self):
        start = self.switch.index('L     2,CO1SREG+32')
        end = self.switch.index('L     2,CURPTR', start)
        validation = self.switch[start:end]
        for forbidden in ('ST    2,CURPTR', 'STKLIM', 'APLIMIT',
                          '216(12)', '220(12)', 'LM    0,15,0(1)',
                          'MVC   32(64,2),CO1SREG'):
            self.assertNotIn(forbidden, validation)
        self.assertIn('CO1REGOK C     2,CURPTR', validation)
        self.assertIn('BC    8,CO1TERM        ACTIVE', validation)

    def test_rejection_uses_three_word_bcpl_return_frame(self):
        for token in ('L     0,CO1SREG+16', 'ST    0,0(5)',
                      'L     0,CO1SREG+20', 'ST    0,4(5)',
                      'L     0,CO1SREG+24', 'ST    0,8(5)',
                      "L     7,=F'-1'", 'L     2,CO1SREG+8',
                      'L     0,CO1SREG', 'L     10,CO1SREG+40',
                      'BCR   15,11'):
            self.assertIn(token, self.reject)
        self.assertEqual(re.findall(r'\bST\s+0,(\d+)\(5\)',self.reject),
                         ['0', '4', '8'])
        self.assertNotIn('STM   0,15,0(15)', self.asm)

    def test_original_context_switch_and_stack_limit_sequence_intact(self):
        for token in ('CO1SREG  DS    16F',
                      'MVC   32(64,2),CO1SREG',
                      'ST    5,52(2)', 'ST    0,60(2)',
                      'L     4,=A(STKLIM)', 'L     4,=A(APLIMIT)',
                      'ST    0,216(12)', 'ST    0,220(12)',
                      'LM    0,15,0(1)', 'CO1RET BCR'):
            self.assertIn(token, self.asm)
        self.assertIn('ST    0,0(4)           STATE=TERMINATED', self.asm)

    def test_distinct_descriptors_and_3rd_init_capacity_rejection(self):
        for token in ('LET ROOT=VEC 23', 'AND P1=VEC 23',
                      'AND P2=VEC 23', 'AND P3=VEC 23',
                      'AND STACK1=GETVEC(1087)',
                      'AND STACK2=GETVEC(1087)',
                      'STACK1=STACK2',
                      'CO1INIT(ROOT,P1,STACK1,WORK1)',
                      'CO1INIT(ROOT,P2,STACK2,WORK2)',
                      'CO1INIT(ROOT,P3,STACK1,WORK1) \\=-2'):
            self.assertIn(token.replace('\\\\=', '\\='), self.bcpl)
        self.assertEqual(self.root.count('CO1INIT('), 3)
        self.assertLess(self.root.index('CO1INIT(ROOT,P3'),
                        self.root.index('A := CHANGECO(7,P1)'))

    def test_null_unknown_self_and_terminated_negative_probes(self):
        schedule = ('A := CHANGECO(7,P1)',
                    'B := CHANGECO(8,P2)',
                    'C := CHANGECO(777,0)',
                    'D := CHANGECO(778,-1)',
                    'E := CHANGECO(779,ROOTCTX)',
                    'F := CHANGECO(11,P1)',
                    'G := CHANGECO(780,P1)',
                    'H := CHANGECO(22,P2)',
                    'I := CHANGECO(781,P2)',
                    'J := CHANGECO(782,ROOTCTX)')
        ix = [self.root.index(s) for s in schedule]
        self.assertEqual(ix, sorted(ix))
        self.assertEqual(self.bcpl.count('CHANGECO('), 12)
        for prefix in ('C', 'D', 'E', 'G', 'I', 'J'):
            self.assertIn(f'IF {prefix} \\=-1'.replace('\\\\=', '\\='),
                          self.root)
        self.assertIn('IF F \\=31'.replace('\\\\=', '\\='), self.root)
        self.assertIn('IF H \\=42'.replace('\\\\=', '\\='), self.root)
        self.assertEqual(self.root.count('ROOTFLAG \\=2718'.replace(
            '\\\\=', '\\=')), 10)

    def test_existing_two_worker_sentinels_and_termination_contract(self):
        for term in ('LET TOKEN=3101', 'LET TOKEN=4202',
                     'RETURNED := CHANGECO(101,ROOTCTX)',
                     'RETURNED := CHANGECO(202,ROOTCTX)',
                     'RESULTIS 31', 'RESULTIS 42',
                     'P1!0 \\=3', 'P2!0 \\=3'):
            self.assertIn(term.replace('\\\\=', '\\='),self.bcpl)
        for rec in ('A1', 'R1', 'A2', 'R2', 'PASS'):
            self.assertEqual(self.bcpl.count(f'"CO1BCPL {rec}"'),1)
        for rec in ('FALLOC', 'FINIT', 'FVALUE','FLOCAL','FSECOND'):
            self.assertIn(f'"CO1BCPL {rec}"',self.bcpl)

    def test_only_private_fixture_changes_and_oracle_remains_strict(self):
        selected=probe.FixtureSelection(BASE)
        self.assertEqual(selected/'source.bcpl', FIXTURE/'source.bcpl')
        self.assertEqual(selected/'co1change.asm',FIXTURE/'co1change.asm')
        self.assertEqual(selected/'cambridge-parm.txt',
                         BASE/'cambridge-parm.txt')
        self.assertEqual(probe.EVIDENCE,
                         ROOT/'workarea/co1-bcpl-registry-guard')

    def test_fake_driver_wires_fixture_without_mvs(self):
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
                ' assert WORK.name == "co1-bcpl-registry-guard"\n'
                ' return 17\n')
            with patch.object(probe,'BASE_RUNNER',fake):
                self.assertEqual(probe.run(),17)

    def test_reject_changed_native_oracle(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=Path(temp)/'baseline.py'
            fake.write_text('EXPECTED=("A1","PASS")\n'
                            'FIXTURE="unused"\n'
                            'def execute(): raise AssertionError("called")\n')
            with patch.object(probe,'BASE_RUNNER',fake):
                with self.assertRaisesRegex(RuntimeError,'oracle changed'):
                    probe.run()

    def test_no_implicit_mvs_execution(self):
        with patch.object(sys,'argv',['run-co1-bcpl-registry-guard.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    probe.main()
        self.assertEqual(caught.exception.code,2)


if __name__=='__main__':
    unittest.main()
