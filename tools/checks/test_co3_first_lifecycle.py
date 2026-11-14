#!/usr/bin/env python3
"""Offline only: CO.3 independent object linkage and exact JES oracle."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT/'tools/coroutines/run-co3-first-lifecycle.py'
spec = importlib.util.spec_from_file_location('co3', MODULE)
co3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co3)
FIXTURE = ROOT/'packaging/milestones/coroutines/candidates/co3-first-lifecycle'

APP = '''         CSECT
         EXTRN BCPLMAIN
L999     EQU *
L123     EQU *
         DC F'4'
         DC F'0'
         DC F'4'
         DC A(L123)
L998     EQU *
         END
'''
LIB = '''         CSECT
         EXTRN BCPLMAIN
L999     EQU *
L101     EQU *
L102     EQU *
L103     EQU *
L104     EQU *
         DC F'1172'
         DC F'0'
         DC F'1156'
         DC A(L101)
         DC F'1160'
         DC A(L102)
         DC F'1168'
         DC A(L103)
         DC F'1172'
         DC A(L104)
L998     EQU *
         END
'''
MAIN = '''BCPLMAIN CSECT
         ENTRY STKOVFL
STKLIM   DC    F'0'
         END BCPLMAIN
'''
SW = 'BCPLCO   CSECT\n         ENTRY CO2INIT,CHANGECO\n         END BCPLCO\n'
SUMMARY = '''JOB 7182 CO3BGO
 ASMA   PGM=IFOX00 RC=0000
 ASML   PGM=IFOX00 RC=0000
 ASMM   PGM=IFOX00 RC=0000
 ASMS   PGM=IFOX00 RC=0000
 LKED   PGM=IEWL RC=0000
 GO     PGM=GO RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
'''
REPORT = ''.join('CO3BCPL '+record+'\n' for record in co3.EXPECTED)

class CO3Checks(unittest.TestCase):
    def test_bcpl_compiler_records_and_contract(self):
        for name in ('source.bcpl','library.bcpl'):
            data=(FIXTURE/name).read_text('ascii')
            self.assertLessEqual(max(map(len,data.splitlines())),80)
            self.assertIn('GLOBAL $(',data)
            self.assertNotIn('COLIST:8',data)
            self.assertNotIn('CHANGECO:6',data)
        code=(FIXTURE/'library.bcpl').read_text('ascii')
        for token in ('LET CO3BOOT(C)','AND CREATECO(FN,SIZE)',
                      'AND CALLCO(C,A)','AND COWAIT(A)',
                      'GETVEC(1087)','FREEVEC(C)','CO2INIT('):
            self.assertIn(token,code)
        self.assertIn('A := FN(COWAIT(A)) REPEAT',code)
        self.assertEqual((FIXTURE/'cambridge-parm.txt').read_text('ascii'),
                         '/CN'+'/'*77+'\n')

    def test_separate_export_aliases(self):
        output=co3.generated_library(LIB)
        self.assertIn('CO3LIB   CSECT',output)
        self.assertIn('         ENTRY C3INIT,C3CREATE,C3CALL,C3WAIT',output)
        for symbol,label in [('C3INIT','L101'),('C3CREATE','L102'),
                             ('C3CALL','L103'),('C3WAIT','L104')]:
            self.assertIn(f'{symbol:<8} EQU   {label}',output)
        self.assertIn('L998     EQU *',output)
        self.assertIn('         END   CO3LIB',output)

    def test_export_collision_and_shape_fail_closed(self):
        with self.assertRaises(co3.CandidateError):
            co3.generated_library(LIB.replace("DC F'1156'","DC F'1180'"))
        with self.assertRaises(co3.CandidateError):
            co3.generated_library(LIB.replace('L101     EQU *','L101     DC F\'0\''))
        with self.assertRaises(co3.CandidateError):
            co3.generated_library(LIB.replace("DC F'1168'","DC F'1156'"))
        with self.assertRaises(co3.CandidateError):
            co3.generated_application(APP.replace("DC F'4'","DC F'1156'"))

    def test_independent_ifox_and_link(self):
        deck=co3.build_deck(APP,LIB,MAIN,SW,
                            ["//CO3BGO  JOB (BCPL),'CO3 NATIVE',CLASS=A"],
                            'HERC02.BCPL.BOOT.OBJ')
        for step in ('ASMA','ASML','ASMM','ASMS','LKED','GO'):
            self.assertEqual(len(re.findall(r'^//'+step+r'\s+EXEC',deck,re.M)),1)
        for temp in ('CO3APOBJ','CO3LOBJ','CO3MNOBJ','CO3SWOBJ'):
            self.assertIn(f'&&{temp}',deck)
        self.assertIn('CO3LIB   CSECT',deck)
        self.assertIn('CO3APP   CSECT',deck)
        self.assertNotIn(' INCLUDE OBJ(BCPLMAIN)',deck)
        self.assertNotIn('DISP=(NEW,CATLG)',deck)
        self.assertIn(' INCLUDE OBJ(BLIB)',deck)
        self.assertEqual(deck.count('\n/*\n'),5)
        self.assertTrue(all(len(x)<=71 and x.isascii() and '\t' not in x
                            for x in deck.splitlines()))

    def test_exact_jes_oracle(self):
        self.assertEqual(co3.assess(SUMMARY,REPORT,'7182')['bcpl_records'],
                         list(co3.EXPECTED))
        bad_reports=(REPORT.replace('CO3BCPL W2','CO3BCPL W9'),
                     REPORT+'CO3BCPL PASS\n',
                     REPORT+'CO3BCPL FCREATE\n',
                     REPORT.replace('CO3BCPL W1','CO3BCPL  W1 EXTRA'))
        for bad in bad_reports:
            with self.subTest(bad=bad):
                with self.assertRaises(co3.CandidateError):
                    co3.assess(SUMMARY,bad,'7182')
        for bad in (SUMMARY.replace('ASML   PGM=IFOX00 RC=0000', ''),
                    SUMMARY.replace('GO     PGM=GO RC=0000',
                                    'GO     PGM=GO RC=0008'),
                    SUMMARY.replace('JOB 7182','JOB 1111')):
            with self.assertRaises(co3.CandidateError):
                co3.assess(bad,REPORT,'7182')

if __name__ == '__main__':
    unittest.main()

