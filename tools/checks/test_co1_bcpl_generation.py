#!/usr/bin/env python3
"""Offline CO.1 generation-handle source, ABI, and runner probes."""
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
FIXTURE = ROOT/'packaging/milestones/coroutines/candidates/co1-bcpl-generation'
RUNNER = ROOT/'tools/coroutines/run-co1-bcpl-generation.py'
spec=importlib.util.spec_from_file_location('co1generation', RUNNER)
module=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

class GenerationProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asm=(FIXTURE/'co1change.asm').read_text('ascii')
        cls.bcpl=(FIXTURE/'source.bcpl').read_text('ascii')
        cls.init=cls.asm.split('CO1INIT  STM',1)[1].split('CO1WBOOT BALR',1)[0]
        cls.resolve=cls.asm.split('CO1RES   STM',1)[1].split('DS    0F',1)[0]
        cls.drop=cls.asm.split('CO1DROP  STM',1)[1].split('CO1RES   STM',1)[0]
        cls.root=cls.bcpl.split('LET START() BE',1)[1]
        cls.callh=cls.bcpl.split('LET CALLH(V,H)',1)[1].split('LET WORK1(A)',1)[0]

    def test_valid_assembly_cards(self):
        for n,line in enumerate(self.asm.splitlines(),1):
            self.assertTrue(line.isascii(),n)
            self.assertLessEqual(len(line),71,(n,line))
            self.assertNotIn('\t',line)
            if line and line[0] not in (' ','*'):
                self.assertRegex(line.split()[0],r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')

    def test_valid_bcpl_source(self):
        self.assertTrue(self.bcpl.isascii())
        self.assertTrue(all(len(line)<=80 for line in self.bcpl.splitlines()))
        for t in ('CO1RES:295','CO1DROP:296','ROOTCTX:297','CO1INIT:298',
                  'CHANGECO:299','FREEVEC:88'):
            self.assertIn(t,self.bcpl)

    def test_native_entries_preserved(self):
        for t in ('CO1CHG   CSECT','         ENTRY CO1INIT,CO1SW',
                  '         ENTRY CO1DROP,CO1RES', 'CO1SW    STM',
                  'CO1WBOOT BALR','CO1RET BCR', 'CO1DROP  STM',
                  'CO1RES   STM'):
            self.assertIn(t,self.asm)

    def test_new_root_and_registration_membership(self):
        for t in ('L     4,ROOTPTR','BC    8,CO1IFRST',
                  'C     7,ROOTPTR','C     8,ROOTPTR',
                  'C     8,REGW1','C     8,REGW2',
                  'L     4,REGW1','L     4,REGW2',
                  'CO1RG1   L     4,TOKW1','CO1RG2   L     4,TOKW2'):
            self.assertIn(t,self.init)
        self.assertLess(self.init.index('C     8,REGW1'),
                        self.init.index('ST    0,12(8)'))
        self.assertNotIn('REGCNT',self.asm)

    def test_generation_increments_without_wrap(self):
        for t in ("TOKW1    DC    F'2'", "TOKW2    DC    F'3'",
                  "C     4,=F'2147483638'", "A     4,=F'4'",
                  'ST    4,TOKW1', 'ST    4,TOKW2',
                  'ST    4,RETTOK','L     7,RETTOK'):
            self.assertIn(t,self.asm)
        self.assertEqual(self.asm.count("C     4,=F'2147483638'"),2)
        self.assertEqual(self.asm.count('BC    2,CO1INBAD'),2)

    def test_resolver_uses_token_before_any_descriptor_access(self):
        for t in ('C     7,TOKW1','C     7,TOKW2',
                  'CO1RS1   L     7,REGW1','CO1RS2   L     7,REGW2',
                  'CO1RNOK  SRL   7,2','SR    7,7',
                  'L     10,24(5)','LR    0,6','BCR   15,11'):
            self.assertIn(t,self.resolve)
        self.assertNotRegex(self.resolve,r'\bL\s+\d+,0\(7\)')
        self.assertNotIn('STKLIM',self.resolve)
        self.assertNotIn('APLIMIT',self.resolve)

    def test_resolver_caller_save_and_return_abi(self):
        self.assertIn('STM   4,10,0(15)',self.asm)
        for t in ('LR    6,0','LR    5,15','L     10,24(5)',
                  'LR    0,6','BCR   15,11'):
            self.assertIn(t,self.resolve)
        self.assertIn('L     10,24(5)',self.init)

    def test_revocation_clears_registry_not_token(self):
        self.assertIn('ST    4,REGW1',self.drop)
        self.assertIn('ST    4,REGW2',self.drop)
        self.assertNotIn('ST    4,TOKW1',self.drop)
        self.assertNotIn('ST    4,TOKW2',self.drop)
        self.assertIn("C     4,=F'3'",self.drop)
        self.assertIn('ST    4,0(7)',self.drop)

    def test_original_raw_switch_preserved(self):
        for t in ('CO1SW    STM   0,15,CO1SREG',
                  'C     2,REGW1','C     2,REGW2',
                  'L     0,0(2)', 'MVC   32(64,2),CO1SREG',
                  'L     4,=A(STKLIM)','L     4,=A(APLIMIT)',
                  'LM    0,15,0(1)'):
            self.assertIn(t,self.asm)

    def test_handle_facade_resolves_before_switch(self):
        self.assertIn('LET P=CO1RES(H)',self.callh)
        self.assertIn('IF P=0 RESULTIS -1',self.callh)
        self.assertIn('RESULTIS CHANGECO(V,P)',self.callh)
        self.assertLess(self.callh.index('CO1RES(H)'),
                        self.callh.index('CHANGECO(V,P)'))

    def test_same_descriptor_reused_across_two_generations(self):
        self.assertEqual(self.root.count('CO1INIT(ROOT,P1,'),2)
        self.assertIn('OLD := CO1INIT(ROOT,P1,STACK1,WORK1)',self.root)
        self.assertIn('NEW := CO1INIT(ROOT,P1,STACK2,WORK2)',self.root)
        self.assertIn('IF NEW\\=10 | NEW=OLD | CO1RES(NEW)\\=P1'.replace('\\\\','\\'),self.root)
        self.assertIn('OLD\\=6'.replace('\\\\','\\'),self.root)
        self.assertIn('CO1RES(OLD)\\=0'.replace('\\\\','\\'),self.root)
        self.assertIn('C := CALLH(777,OLD)',self.root)
        self.assertIn('D := CALLH(8,NEW)',self.root)
        self.assertIn('E := CALLH(22,NEW)',self.root)

    def test_lifecycle_order_and_stack_freeing(self):
        seq=('A := CALLH(7,OLD)','B := CALLH(11,OLD)',
             'IF CO1DROP(P1)','FREEVEC(STACK1)',
             'STACK2 := GETVEC(1087)',
             'NEW := CO1INIT(ROOT,P1,STACK2,WORK2)',
             'C := CALLH(777,OLD)',
             'D := CALLH(8,NEW)',
             'E := CALLH(22,NEW)',
             'F := CO1DROP(P1)',
             'FREEVEC(STACK2)','FREEVEC(P1)')
        where=[self.root.index(t) for t in seq]
        self.assertEqual(where,sorted(where))
        self.assertEqual(self.root.count('FREEVEC('),3)
        self.assertEqual(self.root.count('GETVEC('),3)
        self.assertIn('CALLH(888,NEW)',self.root)
        self.assertIn('CALLH(999,OLD)',self.root)

    def test_native_positive_oracle_and_negative_paths(self):
        for t in ('A1','R1','A2','R2','PASS'):
            self.assertEqual(self.bcpl.count('"CO1BCPL '+t+'"'),1)
        for t in ('FALLOC','FINIT','FVALUE','FSECOND','FLOCAL'):
            self.assertIn('"CO1BCPL '+t+'"',self.bcpl)
        self.assertIn('ROOTFLAG=2718',self.root)
        self.assertIn('RETURNED := CHANGECO(101,ROOTCTX)',self.bcpl)
        self.assertIn('RETURNED := CHANGECO(202,ROOTCTX)',self.bcpl)

    def test_handle_model_rejects_old_with_identical_address(self):
        # Model exercises ABA independent of MVS allocation randomness.
        address=0x00800100
        token=2
        registry={}
        def issue():
            nonlocal token
            if token>2147483638:raise OverflowError()
            token+=4
            registry['slot1']=(token,address)
            return token
        def resolve(t):
            return registry['slot1'][1] if 'slot1' in registry and registry['slot1'][0]==t else 0
        old=issue()
        self.assertEqual(resolve(old),address)
        del registry['slot1']
        self.assertEqual(resolve(old),0)
        new=issue()
        self.assertEqual((old,new),(6,10))
        self.assertEqual(resolve(new),address)
        self.assertEqual(resolve(old),0)

    def test_export_adapter_adds_two_ordered_pairs(self):
        rows=['CO1APP   CSECT','         EXTRN CO1INIT,CO1SW',
              "         DC F'1196'","         DC F'0'",
              "         DC F'1192'",'         DC A(CO1INIT)',
              "         DC F'1196'",'         DC A(CO1SW)',
              'L998 EQU *','         END   CO1APP']
        before=list(rows)
        actual=module.add_exports(rows,ValueError,lambda s,n:s.splitlines())
        self.assertEqual(rows,before)
        self.assertEqual(actual.count('         EXTRN CO1RES,CO1DROP'),1)
        ix=actual.index("         DC F'1180'")
        self.assertEqual(actual[ix:ix+8],
                          ["         DC F'1180'",'         DC A(CO1RES)',
                           "         DC F'1184'",'         DC A(CO1DROP)',
                           "         DC F'1192'",'         DC A(CO1INIT)',
                           "         DC F'1196'",'         DC A(CO1SW)'])

    def test_export_adapter_fails_closed(self):
        rows=['CO1APP   CSECT','         EXTRN CO1INIT,CO1SW',
              "         DC F'1192'",'         DC A(CO1INIT)',
              "         DC F'1196'",'         DC A(CO1SW)',
              'L998 EQU *','         END   CO1APP']
        for change,pattern in [
            (lambda r:r.insert(2,"         DC F'1180'"),'G!295'),
            (lambda r:r.insert(2,"         DC F'1184'"),'G!296'),
            (lambda r:r.remove('         DC A(CO1SW)'),'pairs'),
            (lambda r:r.remove('L998 EQU *'),'trailer')]:
            data=list(rows);change(data)
            with self.assertRaisesRegex(ValueError,pattern):
                module.add_exports(data,ValueError,lambda s,n:s.splitlines())

    def test_fixture_selection_uses_only_test_local_sources(self):
        base=Path('packaging/milestones/coroutines/candidates/co1-bcpl-switch')
        selected=module.FixtureSelection(base)
        self.assertEqual(selected/'source.bcpl',FIXTURE/'source.bcpl')
        self.assertEqual(selected/'co1change.asm',FIXTURE/'co1change.asm')
        self.assertEqual(selected/'cambridge-parm.txt',base/'cambridge-parm.txt')

    def test_fake_runner_integration(self):
        with tempfile.TemporaryDirectory() as directory:
            f=Path(directory)/'runner.py'
            f.write_text(
                'from pathlib import Path\n'
                'EXPECTED=("A1","R1","A2","R2","PASS")\n'
                'FIXTURE=Path("baseline")\n'
                'WORK=Path("unbound")\n'
                'CandidateError=ValueError\n'
                'def checked_cards(s,n):return s.splitlines()\n'
                'def compiled_application(source):\n'
                ' return ["CO1APP   CSECT",'
                ' "         EXTRN CO1INIT,CO1SW",'
                ' "         DC F\'1192\'", "         DC A(CO1INIT)",'
                ' "         DC F\'1196\'", "         DC A(CO1SW)",'
                ' "L998 EQU *", "         END   CO1APP"]\n'
                'def execute():\n'
                ' rows=compiled_application("generated")\n'
                ' assert "         DC A(CO1RES)" in rows\n'
                ' assert "         DC A(CO1DROP)" in rows\n'
                ' assert (FIXTURE/"source.bcpl").name=="source.bcpl"\n'
                ' assert WORK.name=="co1-bcpl-generation"\n'
                ' return 23\n')
            with patch.object(module,'BASE_RUNNER',f):
                self.assertEqual(module.run(),23)

    def test_reject_changed_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            f=Path(directory)/'runner.py'
            f.write_text('EXPECTED=("A1","PASS")\n'
                         'def execute(): raise AssertionError("not called")\n')
            with patch.object(module,'BASE_RUNNER',f):
                with self.assertRaisesRegex(RuntimeError,'oracle changed'):
                    module.run()

    def test_cli_requires_run_flag(self):
        with patch.object(sys,'argv',['run-co1-bcpl-generation.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    module.main()
        self.assertEqual(caught.exception.code,2)

if __name__=='__main__':unittest.main()
