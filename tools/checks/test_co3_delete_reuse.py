#!/usr/bin/env python3
"""CO.3 delete/reuse isolation, source contracts and offline driver tests."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
MODULE=ROOT/'tools/coroutines/run-co3-delete-reuse.py'
spec=importlib.util.spec_from_file_location('co3_delete',MODULE)
co3=importlib.util.module_from_spec(spec)
spec.loader.exec_module(co3)
BASE=ROOT/'packaging/milestones/coroutines/candidates/co3-delete-reuse'

# Intentionally minimal but preserves real CG370 global trailer structure.
APP='''CO3APP   CSECT
         EXTRN C3INIT,C3CREATE,C3DELETE,C3CALL,C3WAIT,C3RESUME
         DC F'1196'
         DC F'0'
         DC F'4'
         DC A(L123)
L998     EQU *
         END   CO3APP
'''
BASE_BRIDGE='''BCPLCO   CSECT
         ENTRY CO2INIT,CHANGECO
         USING CHANGECO,4
CHANGECO STM   0,15,CO2SREG
         DROP  4
         DS    0F
ROOTPTR  DC    F'0'
REGW1    DC    F'0'
REGW2    DC    F'0'
CURPTR   DC    F'0'
         END   BCPLCO
'''

class FakeDriver:
    EXPORTS=((289,'C3INIT'),(290,'C3CREATE'),(292,'C3CALL'),
             (293,'C3WAIT'),(294,'C3RESUME'))
    co2=SimpleNamespace(checked_cards=lambda source,name: source.splitlines())
    @staticmethod
    def trailer(rows):
        last=rows.index('L998     EQU *')
        candidates=[]
        for i in range(last-1):
            a=re.fullmatch(r"         DC F'(\d+)'",rows[i])
            if not a or rows[i+1] != "         DC F'0'":
                continue
            rest=rows[i+2:last]
            if len(rest)%2==0 and all(
                re.fullmatch(r"         DC F'(\d+)'",rest[j])
                and re.fullmatch(r'         DC A\([^()]+\)',rest[j+1])
                for j in range(0,len(rest),2)
            ):
                candidates.append((i,int(a.group(1))))
        if len(candidates)!=1:
            raise co3.CandidateError('ambiguous fake global trailer')
        start,maximum=candidates[0]
        pairs=[]
        for i in range(start+2,last,2):
            n=int(re.fullmatch(r"         DC F'(\d+)'",rows[i]).group(1))
            address=re.fullmatch(r'         DC A\(([^()]+)\)',rows[i+1]).group(1)
            pairs.append((n,address))
        return start,last,maximum,pairs
    def generated_application(self, source):
        # The real base runner refers to mutable EXPORTS to synthesize aliases.
        return APP.splitlines()
    @staticmethod
    def build_deck(app,library,main,bridge,jobcard,obj):
        return bridge

class CO3DeleteReuseChecks(unittest.TestCase):
    def test_source_is_standalone_bcpl_with_private_globals(self):
        app=(BASE/'source.bcpl').read_text('ascii')
        lib=(BASE/'library.bcpl').read_text('ascii')
        for data in (app,lib):
            self.assertTrue(data.endswith('\n'))
            self.assertLessEqual(max(map(len,data.splitlines())),80)
            self.assertIn('GLOBAL $(',data)
            self.assertNotIn('CHANGECO:6',data)
        for token in ('  DELETECO:291','  CO3DROP:300','AND DELETECO(C)',
                      'CO3DROP(C)', 'FREEVEC(STACK)','FREEVEC(C)',
                      'RESULTIS TRUE'):
            self.assertIn(token,lib)
        self.assertIn('  WRCH:14',app)
        self.assertNotIn('NEWLINE()',app)
        self.assertGreaterEqual(app.count('WRCH(10)'),len(co3.EXPECTED))
        self.assertTrue(all(len('CO3BCPL '+x)<=132 for x in co3.EXPECTED))

    def test_stale_pointer_admission_and_unregister_before_freemain(self):
        source=(BASE/'library.bcpl').read_text('ascii')
        delete=source[source.index('AND DELETECO(C)'):]
        for name in ('IF P=0 RESULTIS FALSE','IF C!25 \\= 0 RESULTIS FALSE',
                     'IF CO3DROP(C) \\= 0 RESULTIS FALSE'):
            self.assertIn(name,delete)
        self.assertLess(delete.index('IF P=0 RESULTIS FALSE'),
                        delete.index('IF C!25'))
        self.assertLess(delete.index('IF CO3DROP(C)'),
                        delete.index('FREEVEC(STACK)'))
        self.assertLess(delete.index('FREEVEC(STACK)'),
                        delete.index('FREEVEC(C)'))
        self.assertIn('IF C=0 | CO3CURR \\= CO3ROOT',delete)
        self.assertIn('IF P \\= C & P!25=C RESULTIS FALSE',delete)
        self.assertIn('TEST PREV=0 THEN CO3LIST:=NEXT',delete)

    def test_native_drop_guard_sequence_and_no_unsafe_first_dereference(self):
        source=(BASE/'co3drop.inc').read_text('ascii')
        lines=source.splitlines()
        self.assertLessEqual(max(map(len,lines)),71)
        self.assertIn('CO3DROP  STM   4,10,0(15)',source)
        self.assertLess(source.index('C     7,REGW2'),source.index('L     4,0(7)'))
        self.assertLess(source.index('C     4,ROOTPTR'),source.index('L     4,0(7)'))
        self.assertLess(source.index('C     4,=F\'2\''),source.index('ST    4,0(7)'))
        self.assertLess(source.index('L     0,100(4)'),source.index('ST    4,0(7)'))
        self.assertLess(source.index('ST    4,0(7)'),source.index('ST    4,REGW2'))
        self.assertLess(source.index('ST    4,0(7)'),source.index('ST    4,REGW1'))
        self.assertNotIn('FREEMAIN',source)
        self.assertNotIn('GETMAIN',source)
        self.assertNotIn('L     2,',source)
        self.assertIn('LR    0,6',source)

    def test_bridge_is_candidate_only_and_rejects_drift(self):
        extension=(BASE/'co3drop.inc').read_text('ascii')
        candidate=co3.merge_bridge(BASE_BRIDGE,extension)
        self.assertEqual(candidate.count('         ENTRY CO3DROP'),1)
        self.assertEqual(candidate.count('CO3DROP  STM'),1)
        self.assertIn('         END   BCPLCO',candidate)
        self.assertTrue(all(len(x)<=71 for x in candidate.splitlines()))
        self.assertNotIn('CO3DROP',BASE_BRIDGE)
        for altered in (BASE_BRIDGE.replace('         ENTRY CO2INIT,CHANGECO',''),
                        BASE_BRIDGE.replace('ROOTPTR  DC', 'ROOTPTR  DS'),
                        BASE_BRIDGE+'CO3DROP\n'):
            with self.subTest(altered=altered[-15:]):
                with self.assertRaises(co3.CandidateError):
                    co3.merge_bridge(altered,extension)

    def test_export_and_application_trailer_bindings(self):
        f=FakeDriver()
        rows=co3.bind_application_export(APP.splitlines(),f)
        self.assertIn('         EXTRN CO3DROP',rows)
        self.assertIn("         DC F'1200'",rows)
        self.assertIn('         DC A(CO3DROP)',rows)
        self.assertEqual(rows.count("         DC F'1200'"),2)
        self.assertLess(rows.index('         DC A(CO3DROP)'),rows.index('L998     EQU *'))
        with self.assertRaises(co3.CandidateError):
            co3.bind_application_export(rows,f)
        with self.assertRaises(co3.CandidateError):
            co3.bind_application_export([x for x in APP.splitlines()
                                         if 'C3RESUME' not in x],f)

    def test_runner_configures_standalone_copy_without_mutating_origin(self):
        fake=FakeDriver()
        original=tuple(fake.EXPORTS)
        co3.configure(fake)
        self.assertEqual(fake.EXPORTS,co3.LIBRARY_EXPORTS)
        self.assertEqual(fake.EXPECTED,co3.EXPECTED)
        self.assertEqual(fake.FIXTURE,BASE)
        self.assertEqual(fake.WORK,co3.EVIDENCE)
        output=fake.generated_application('sample')
        self.assertIn('         EXTRN CO3DROP',output)
        deck=fake.build_deck('app','lib','main',BASE_BRIDGE,['//CO3BGO JOB'],
                             'HERC02.BCPL.BOOT.OBJ')
        self.assertIn('CO3DROP  STM',deck)
        self.assertEqual(original,FakeDriver.EXPORTS)
        with self.assertRaises(co3.CandidateError):
            co3.configure(fake)

    def test_exact_twenty_one_record_behavioral_oracle(self):
        self.assertEqual(co3.EXPECTED,(
            'MADE','FULL','A1','RA','B1','RB','DELA',
            'C1','RC','B2','RB2','DELB','C2','RC2',
            'DELC','D1','RD','D2','RD2','DELD','PASS'))
        app=(BASE/'source.bcpl').read_text('ascii')
        for marker in co3.EXPECTED:
            self.assertEqual(app.count('WRITES("CO3BCPL '+marker+'")'),1)
        self.assertIn('A:=CREATECO(AWORK,1024)',app)
        self.assertIn('B:=CREATECO(BWORK,1024)',app)
        self.assertIn('R:=CREATECO(CWORK,1024)',app)
        self.assertIn('C:=CREATECO(CWORK,1024)',app)
        self.assertIn('D:=CREATECO(CWORK,1024)',app)
        for old in ('DELETECO(A)', 'DELETECO(B)',
                    'DELETECO(C)','DELETECO(D)'):
            self.assertIn(old,app)
        self.assertNotIn('CALLCO(A,',app[app.index('IF DELETECO(A)'):])

if __name__ == '__main__':
    unittest.main()
