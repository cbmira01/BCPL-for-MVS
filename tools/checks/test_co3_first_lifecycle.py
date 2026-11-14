#!/usr/bin/env python3
"""Offline only: CO.3 independent object linkage and exact JES oracle."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

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
L105     EQU *
         DC F'1176'
         DC F'0'
         DC F'1156'
         DC A(L101)
         DC F'1160'
         DC A(L102)
         DC F'1168'
         DC A(L103)
         DC F'1172'
         DC A(L104)
         DC F'1176'
         DC A(L105)
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
    def test_mvs_submission_path_and_fail_closed_preflight(self):
        # CO.2 already uses the canonical script without a .sh suffix.
        self.assertEqual(co3.SUBMIT, co3.co2.SUBMIT)
        self.assertEqual(co3.SUBMIT.name, 'submit-jcl')
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory)/n for n in
                     ('submit-jcl', 'job-summary', 'dump-report-for-job')]
            for item in paths:
                item.write_text('#!/bin/sh\nexit 0\n', encoding='ascii')
                item.chmod(0o700)
            with (patch.object(co3, 'SUBMIT', paths[0]),
                  patch.object(co3.co2, 'SUBMIT', paths[0]),
                  patch.object(co3, 'SUMMARY', paths[1]),
                  patch.object(co3, 'REPORT', paths[2])):
                co3.require_mvs_tools()
                paths[0].chmod(0o600)
                with self.assertRaisesRegex(co3.CandidateError,
                                            'not executable'):
                    co3.require_mvs_tools()
                paths[0].chmod(0o700)
                paths[1].unlink()
                with self.assertRaisesRegex(co3.CandidateError, 'missing'):
                    co3.require_mvs_tools()

    def test_bcpl_compiler_records_and_contract(self):
        for name in ('source.bcpl','parent-chain.bcpl','library.bcpl'):
            data=(FIXTURE/name).read_text('ascii')
            self.assertLessEqual(max(map(len,data.splitlines())),80)
            self.assertIn('GLOBAL $(',data)
            self.assertNotIn('COLIST:8',data)
            self.assertNotIn('CHANGECO:6',data)
        code=(FIXTURE/'library.bcpl').read_text('ascii')
        for token in ('LET CO3BOOT(C)','AND CREATECO(FN,SIZE)',
                      'AND CALLCO(C,A)','AND COWAIT(A)',
                      'AND RESUMECO(C,A)',
                      'GETVEC(1087)','FREEVEC(C)','CO2INIT('):
            self.assertIn(token,code)
        self.assertIn('A := FN(COWAIT(A)) REPEAT',code)
        self.assertEqual((FIXTURE/'cambridge-parm.txt').read_text('ascii'),
                         '/CN'+'/'*77+'\n')

    def test_separate_export_aliases(self):
        output=co3.generated_library(LIB)
        self.assertIn('CO3LIB   CSECT',output)
        self.assertIn('         ENTRY C3INIT,C3CREATE,C3CALL,C3WAIT,C3RESUME',output)
        for symbol,label in [('C3INIT','L101'),('C3CREATE','L102'),
                             ('C3CALL','L103'),('C3WAIT','L104'),('C3RESUME','L105')]:
            self.assertIn(f'{symbol:<8} EQU   {label}',output)
        self.assertIn('L998     EQU *',output)
        self.assertIn('         END   CO3LIB',output)

    def test_actual_cambridge_zero_plus_relocatable_addresses(self):
        # The first real CO.3 compiler output contained DC A(0+L3).
        generated = LIB
        for label in ('L101', 'L102', 'L103', 'L104', 'L105'):
            generated = generated.replace(f'DC A({label})',
                                          f'DC A(0+{label})')
        output = co3.generated_library(generated)
        for symbol, label in [('C3INIT','L101'),('C3CREATE','L102'),
                              ('C3CALL','L103'),('C3WAIT','L104'),('C3RESUME','L105')]:
            self.assertIn(f'{symbol:<8} EQU   {label}', output)
            self.assertNotIn(f'{symbol:<8} EQU   0+{label}', output)
        self.assertIn('         DC A(0+L101)', output)
        # Exact relocation token observed in the 14 November compiler run.
        real_shape = LIB.replace('L101', 'L3').replace(
            'DC A(L3)', 'DC A(0+L3)')
        real_output = co3.generated_library(real_shape)
        self.assertIn('C3INIT   EQU   L3', real_output)
        self.assertIn('         DC A(0+L3)', real_output)

    def test_nonzero_and_unsafe_relocation_expressions_refused(self):
        for bad in ('4+L101', '-4+L101', 'L101+4', 'L101-L102',
                    '0+L99999Z', '0+EXTERNAL'):
            with self.subTest(bad=bad):
                with self.assertRaises(co3.CandidateError):
                    co3.generated_library(LIB.replace('DC A(L101)',
                                                     f'DC A({bad})'))

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

    def test_deck_accepts_real_cg370_export_form(self):
        lib = LIB.replace('L101', 'L3').replace('DC A(L3)',
                                               'DC A(0+L3)')
        app = APP.replace('DC A(L123)', 'DC A(0+L123)')
        deck = co3.build_deck(app, lib, MAIN, SW,
                              ["//CO3BGO  JOB (BCPL),'CO3 NATIVE',CLASS=A"],
                              'HERC02.BCPL.BOOT.OBJ')
        self.assertIn('C3INIT   EQU   L3', deck)
        self.assertIn('         DC A(0+L3)', deck)
        self.assertEqual(deck.count('C3INIT   EQU   L3'), 1)

    def test_parent_chain_oracle_and_two_worker_sources(self):
        parent=(FIXTURE/'parent-chain.bcpl').read_text('ascii')
        self.assertIn('R := CALLCO(CO3LIST,22)', parent)
        self.assertIn('R := RESUMECO(CO3LIST,44)', parent)
        self.assertIn('R := RESUMECO(CO3LIST!26,0)', parent)
        self.assertIn(r'IF R \= -998 RESULTIS -21', parent)
        self.assertIn(r'KEEP \= 123', parent)
        self.assertIn(r'KEEP \= 456', parent)
        self.assertEqual(co3.PARENT_EXPECTED,
                         ('MADE','A1','B1','A2','B2','R1','A3','R2',
                          'B3','R3','A4','R4','PASS'))
        trace=''.join('CO3BCPL '+r+'\n' for r in co3.PARENT_EXPECTED)
        self.assertEqual(co3.assess(SUMMARY,trace,'7182',co3.PARENT_EXPECTED)
                         ['bcpl_records'], list(co3.PARENT_EXPECTED))
        with self.assertRaises(co3.CandidateError):
            co3.assess(SUMMARY, trace.replace('CO3BCPL B2',
                                               'CO3BCPL B1'), '7182',
                       co3.PARENT_EXPECTED)

    def test_resume_refusal_keeps_parent_before_mutation(self):
        lib=(FIXTURE/'library.bcpl').read_text('ascii')
        start=lib.index('AND RESUMECO(C,A)')
        text=lib[start:]
        self.assertLess(text.index(r'IF C!25 \= 0 RESULTIS -998'),
                        text.index('SELF!25 := 0'))
        self.assertLess(text.index('PARENT := SELF!25'),
                        text.index('C!25 := PARENT'))

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

