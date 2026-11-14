#!/usr/bin/env python3
"""Host-only checks for the isolated CO.1 registry revocation candidate."""
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
FIXTURE = (ROOT/'packaging/milestones/coroutines/candidates'
           /'co1-bcpl-revocation')
RUNNER = ROOT/'tools/coroutines/run-co1-bcpl-revocation.py'
spec = importlib.util.spec_from_file_location('co1revocation', RUNNER)
probe = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(probe)


class RevocationProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asm = (FIXTURE/'co1change.asm').read_text('ascii')
        cls.bcpl = (FIXTURE/'source.bcpl').read_text('ascii')
        cls.drop = cls.asm.split('CO1DROP  STM',1)[1].split('DS    0F',1)[0]
        cls.sw = cls.asm.split('CO1SW    STM',1)[1].split('CO1TERM  L',1)[0]
        cls.root = cls.bcpl.split('LET START() BE',1)[1]

    def test_source_card_widths(self):
        self.assertTrue(self.bcpl.isascii())
        self.assertTrue(self.asm.isascii())
        self.assertTrue(all(len(line)<=80 for line in self.bcpl.splitlines()))
        self.assertTrue(all(len(line)<=71 for line in self.asm.splitlines()))
        self.assertFalse(any('\t' in line for line in self.asm.splitlines()))

    def test_ifox_symbols_at_most_eight_characters(self):
        for line in self.asm.splitlines():
            if line and line[0] not in (' ', '*'):
                self.assertRegex(line.split()[0],r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')

    def test_separate_entry_keeps_baseline_runner_constraint(self):
        self.assertIn('         ENTRY CO1INIT,CO1SW',self.asm)
        self.assertIn('         ENTRY CO1DROP',self.asm)
        self.assertIn('CO1CHG   CSECT',self.asm)
        self.assertEqual(self.asm.count('CO1DROP  STM'),1)
        self.assertIn('CO1RET BCR   15,11',self.asm)

    def test_revoke_checks_registry_before_target_load(self):
        for token in ('SLL   7,2', 'LTR   7,7', 'C     7,REGW1',
                      'C     7,REGW2', 'CO1DCHK  C     7,CURPTR',
                      'L     4,0(7)', "C     4,=F'3'"):
            self.assertIn(token,self.drop)
        self.assertLess(self.drop.index('C     7,REGW2'),self.drop.index('L     4,0(7)'))
        self.assertLess(self.drop.index('CO1DCHK'),self.drop.index('L     4,0(7)'))
        self.assertEqual(self.drop.count('L     4,0(7)'),1)

    def test_revoke_refuses_active_and_suspended(self):
        self.assertIn('BC    8,CO1DFAIL       ACTIVE CONTEXT',self.drop)
        self.assertIn('BC    7,CO1DFAIL       NOT TERMINATED',self.drop)
        self.assertIn('BC    8,CO1DFAIL       REJECT NULL',self.drop)
        self.assertIn('BC    7,CO1DFAIL       UNKNOWN OR REVOKED',self.drop)

    def test_state_four_written_before_registry_removal(self):
        sequence=('LA    4,4','ST    4,0(7)', 'SR    4,4',
                  'C     7,REGW1','ST    4,REGW2','CO1DCLR ST    4,REGW1')
        ix=[]
        last=0
        for token in sequence:
            last=self.drop.index(token,last)
            ix.append(last)
            last+=len(token)
        self.assertEqual(ix,sorted(ix))
        self.assertIn('CO1DOK  SR    7,7',self.drop)
        self.assertEqual(self.drop.count('ST    4,0(7)'),1)

    def test_does_not_reopen_registry_slots(self):
        self.assertIn('REGCNT   DC    F\'0\'',self.asm)
        self.assertIn('REGW1    DC    F\'0\'',self.asm)
        self.assertIn('REGW2    DC    F\'0\'',self.asm)
        self.assertNotIn('ST    4,REGCNT',self.drop)
        self.assertNotIn('CO1RG1',self.drop)
        self.assertNotIn('CO1RG2',self.drop)

    def test_bcpl_return_writes_only_original_call_workspace(self):
        self.assertIn('STM   4,10,0(15)',self.asm)
        self.assertIn('LR    6,0',self.drop)
        self.assertIn('LR    5,15',self.drop)
        self.assertIn("L     7,=F'-2'",self.drop)
        self.assertIn('LR    0,6',self.drop)
        self.assertIn('L     10,24(5)',self.drop)
        self.assertIn('BCR   15,11',self.drop)
        for text in ('STKLIM','APLIMIT','216(12)','220(12)', 'LM    0,15'):
            self.assertNotIn(text,self.drop)

    def test_existing_switch_membership_guard_unchanged(self):
        for text in ('L     2,CO1SREG+32','C     2,REGW1',
                     'C     2,REGW2','BC    7,CO1TERM',
                     'CO1REGOK C     2,CURPTR',
                     'L     0,0(2)', 'MVC   32(64,2),CO1SREG'):
            self.assertIn(text,self.sw)
        self.assertLess(self.sw.index('BC    7,CO1TERM'),self.sw.index('L     0,0(2)'))

    def test_test_only_global_and_real_freevec(self):
        for t in ('GETVEC:87','FREEVEC:88','CO1DROP:296',
                  'ROOTCTX:297','CO1INIT:298','CHANGECO:299'):
            self.assertIn(t,self.bcpl)
        self.assertEqual(self.root.count('FREEVEC('),4)
        self.assertEqual(self.root.count('CO1DROP('),8)

    def test_independent_allocated_descriptor_and_stack(self):
        for t in ('LET ROOT=VEC 23','AND P1=GETVEC(23)',
                  'AND P2=GETVEC(23)','AND STACK1=GETVEC(1087)',
                  'AND STACK2=GETVEC(1087)',
                  'CO1INIT(ROOT,P1,STACK1,WORK1)',
                  'CO1INIT(ROOT,P2,STACK2,WORK2)',
                  'P1=P2 | STACK1=STACK2'):
            self.assertIn(t,self.bcpl)

    def test_revoke_requires_termination_and_keeps_second_worker(self):
        order=('A := CHANGECO(7,P1)', 'B := CHANGECO(8,P2)',
               'C := CHANGECO(11,P1)','D := CO1DROP(P1)',
               'FREEVEC(STACK1)','FREEVEC(P1)',
               'E := CHANGECO(777,STALE1)',
               'G := CHANGECO(22,P2)',
               'H := CO1DROP(P2)',
               'FREEVEC(STACK2)','FREEVEC(P2)',
               'I := CHANGECO(888,STALE2)')
        ix=[self.root.index(t) for t in order]
        self.assertEqual(ix,sorted(ix))
        self.assertIn('P1!0 \\=3',self.root)
        self.assertIn('P1!0 \\=4',self.root)
        self.assertIn('P2!0 \\=3',self.root)
        self.assertIn('P2!0 \\=4',self.root)
        self.assertIn('G \\=42',self.root)

    def test_old_pointer_rejected_without_access_to_freed_descriptor(self):
        for token in ('STALE1 := P1', 'STALE2 := P2',
                      'E := CHANGECO(777,STALE1)',
                      'F := CO1DROP(STALE1)',
                      'I := CHANGECO(888,STALE2)',
                      'J := CO1DROP(STALE2)',
                      'IF E \\=-1 | F \\=-2',
                      'IF I \\=-1 | J \\=-2'):
            self.assertIn(token,self.root)
        self.assertNotIn('GETVEC(',self.root.split('FREEVEC(P1)',1)[1])
        self.assertNotIn('CO1INIT(',self.root.split('FREEVEC(P1)',1)[1])

    def test_denied_drop_does_not_stop_valid_workers(self):
        self.assertIn('CO1DROP(P2) \\=-2 | CO1DROP(ROOT) \\=-2',self.root)
        self.assertIn('CO1DROP(P2) \\=-2 | CO1DROP(-1) \\=-2',self.root)
        self.assertLess(self.root.index('CO1DROP(P2) \\=-2 | CO1DROP(-1)'),
                        self.root.index('C := CHANGECO(11,P1)'))

    def test_strict_five_record_oracle(self):
        for token in ('A1','R1','A2','R2','PASS'):
            self.assertEqual(self.bcpl.count('"CO1BCPL '+token+'"'),1)
        for token in ('FALLOC','FINIT','FVALUE','FSECOND','FLOCAL'):
            self.assertIn('"CO1BCPL '+token+'"',self.bcpl)

    def test_driver_export_adapter_inserts_one_slot_and_import(self):
        rows=['CO1APP   CSECT', '         EXTRN CO1INIT,CO1SW',
              '         DC F\'1196\'', '         DC F\'0\'',
              '         DC F\'1192\'', '         DC A(CO1INIT)',
              '         DC F\'1196\'', '         DC A(CO1SW)',
              'L998 EQU *', '         END   CO1APP']
        def checked(text,unused):return text.splitlines()
        added=probe.add_drop_export(rows, ValueError, checked)
        self.assertIn('         EXTRN CO1DROP',added)
        self.assertEqual(added.count("         DC F'1184'"),1)
        self.assertEqual(added.count('         DC A(CO1DROP)'),1)
        self.assertLess(added.index('         DC A(CO1DROP)'),
                        added.index('         DC A(CO1INIT)'))
        self.assertEqual(rows.count('         EXTRN CO1DROP'),0)

    def test_driver_rejects_existing_slot_and_bad_trailer(self):
        base=['CO1APP   CSECT','         EXTRN CO1INIT,CO1SW',
              "         DC F'1184'", '         DC A(EXISTING)',
              "         DC F'1192'",'         DC A(CO1INIT)',
              "         DC F'1196'",'         DC A(CO1SW)',
              'L998 EQU *','         END   CO1APP']
        with self.assertRaisesRegex(ValueError,'G!296 taken'):
            probe.add_drop_export(base,ValueError,lambda x,y:x.splitlines())
        base[0]='WRONG  CSECT'
        with self.assertRaisesRegex(ValueError,'CSECT'):
            probe.add_drop_export(base,ValueError,lambda x,y:x.splitlines())

    def test_driver_fixture_changes_only_candidate_inputs(self):
        old=ROOT/'packaging/milestones/coroutines/candidates/co1-bcpl-switch'
        selected=probe.FixtureSelection(old)
        self.assertEqual(selected/'source.bcpl',FIXTURE/'source.bcpl')
        self.assertEqual(selected/'co1change.asm',FIXTURE/'co1change.asm')
        self.assertEqual(selected/'cambridge-parm.txt',old/'cambridge-parm.txt')
        self.assertEqual(probe.EVIDENCE, ROOT/'workarea/co1-bcpl-revocation')

    def test_runner_wires_adapter_without_mvs(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'baseline.py'
            path.write_text(
                'from pathlib import Path\n'
                'EXPECTED=("A1","R1","A2","R2","PASS")\n'
                'FIXTURE=Path("baseline")\n'
                'WORK=Path("missing")\n'
                'CandidateError=ValueError\n'
                'def checked_cards(x,y):return x.splitlines()\n'
                'def compiled_application(x):\n'
                ' return ["CO1APP   CSECT", "         EXTRN CO1INIT,CO1SW",'
                ' "         DC F\'1192\'", "         DC A(CO1INIT)",'
                ' "         DC F\'1196\'", "         DC A(CO1SW)",'
                ' "L998 EQU *", "         END   CO1APP"]\n'
                'def execute():\n'
                ' result=compiled_application("fake")\n'
                ' assert "         DC A(CO1DROP)" in result\n'
                ' assert (FIXTURE/"source.bcpl").name=="source.bcpl"\n'
                ' assert (FIXTURE/"co1change.asm").name=="co1change.asm"\n'
                ' assert WORK.name=="co1-bcpl-revocation"\n'
                ' return 17\n')
            with patch.object(probe,'BASE_RUNNER',path):
                self.assertEqual(probe.run(),17)

    def test_oracle_change_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'baseline.py'
            path.write_text('EXPECTED=("A1","PASS")\n'
                            'def execute(): raise AssertionError("called")\n')
            with patch.object(probe,'BASE_RUNNER',path):
                with self.assertRaisesRegex(RuntimeError,'oracle changed'):
                    probe.run()

    def test_cli_requires_explicit_mvs_run(self):
        with patch.object(sys,'argv',['run-co1-bcpl-revocation.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    probe.main()
        self.assertEqual(caught.exception.code,2)


if __name__=='__main__':
    unittest.main()
