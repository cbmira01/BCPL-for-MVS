#!/usr/bin/env python3
"""Offline, synthetic-only CO.1 BCPL candidate and MVS runner checks."""
from __future__ import annotations
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT/'tools/coroutines/run-co1-bcpl-switch.py'
FIXTURE = ROOT/'packaging/milestones/coroutines/candidates/co1-bcpl-switch'
spec=importlib.util.spec_from_file_location('co1_bcpl_switch',RUNNER)
co=importlib.util.module_from_spec(spec)
spec.loader.exec_module(co)
SAMPLE='''         CSECT
         EXTRN BCPLMAIN
L999     STM   14,12,12(13)
         BCR   15,4
         DC    AL2(L998-L999)
         DC    A(BCPLMAIN)
         DC F'2796'
         DC F'0'
         DC F'4'
         DC A(L999)
L998     EQU   *
         END
'''
MAIN='''BCPLMAIN CSECT
         ENTRY STKOVFL
STKLIM   DC    F'0'
         END   BCPLMAIN
'''
SUMMARY='''JOB 8301  CO1BGO
STEP       PROGRAM      RESULT
ASMA       IFOX00       RC=0000
ASMM       IFOX00       RC=0000
ASMS       IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         CO1BGO       RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
'''
REPORT='''CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
'''
JOB_CARD=["//CO1BGO  JOB (BCPL),'CO1 BCPL NATIVE',CLASS=A"]
OBJ='HERC02.BCPL.BOOT.OBJ'


class CandidateTests(unittest.TestCase):
    def test_assembly_and_bcpl_card_lengths(self):
        co.checked_cards((FIXTURE/'co1change.asm').read_text('ascii'),'switch')
        self.assertTrue(all(len(r)<=80 for r in
             (FIXTURE/'source.bcpl').read_text('ascii').splitlines()))
        self.assertEqual((FIXTURE/'cambridge-parm.txt').read_text('ascii').splitlines(),
                         ['/CN'+'/'*77])

    def test_switch_symbol_limit_rejected_before_mvs(self):
        source=(FIXTURE/'co1change.asm').read_text('ascii')
        co.checked_cards(source,'CO1CHG')
        altered=source.replace('CO1RET BCR', 'CO1RETURN BCR')
        self.assertNotEqual(altered,source)
        with self.assertRaisesRegex(co.CandidateError,'invalid IFOX label'):
            co.checked_cards(altered,'CO1CHG')
        with self.assertRaisesRegex(co.CandidateError,'invalid IFOX label'):
            co.build_deck(SAMPLE,MAIN,altered,JOB_CARD,OBJ)

    def test_switch_preserves_register_image_then_return_frame(self):
        code=(FIXTURE/'co1change.asm').read_text('ascii')
        for line in ('STM   0,15,0(15)', 'MVC   32(64,2),0(5)',
                     'ST    0,52(2)', 'ST    0,56(2)',
                     'L     0,16(5)', 'ST    0,0(5)',
                     'L     0,20(5)', 'ST    0,4(5)',
                     'L     0,24(5)', 'ST    0,8(5)',
                     'LM    0,15,0(1)', 'CO1RET BCR   15,11'):
            self.assertIn(line,code)

    def test_worker_initialization_and_stack_bounds(self):
        code=(FIXTURE/'co1change.asm').read_text('ascii')
        for token in ('CO1WBOOT BALR  6,4', 'L     0,24(5)',
                      'L     0,=F\'4096\'', 'A     0,=F\'256\'',
                      'ST    0,20(8)', 'ST    0,24(8)',
                      'L     4,=A(STKLIM)', 'L     4,=A(APLIMIT)',
                      'ST    0,216(12)', 'ST    0,220(12)'):
            self.assertIn(token,code)
        self.assertNotIn('L     0,0(0)',code)
        self.assertNotIn('LA    0,256(0)',code)
        self.assertNotIn('ST    4,-4(',code)

    def test_diagnostic_bcpl_failure_sites(self):
        source=(FIXTURE/'source.bcpl').read_text('ascii')
        for record in ('FALLOC','FINIT','FARG','FLOCAL','FVALUE','FSECOND'):
            self.assertIn('CO1BCPL '+record,source)
        self.assertNotIn('CO1BCPL FAIL',source)
        self.assertIn('IF A \\=7 RESULTIS 97',source)
        self.assertIn('IF LOCAL \\=314 | B \\=10 RESULTIS 98',source)

    def test_diagnostic_go_records_are_rejected_but_extracted(self):
        for status in ('FALLOC','FINIT','FARG','FLOCAL',
                       'FVALUE','FSECOND'):
            output='CO1BCPL '+status+'\n'
            self.assertEqual(co.observed_records(output),[status])
            with self.subTest(status=status),self.assertRaisesRegex(
                    co.CandidateError,'native BCPL records differ'):
                co.assess(SUMMARY,output,'8301')
        self.assertEqual(co.observed_records(REPORT),
                         ['A1','R1','A2','R2','PASS'])
        self.assertEqual(co.observed_records(
            "MSG DC CL80'CO1BCPL FARG'\n"+REPORT),
            ['A1','R1','A2','R2','PASS'])

    def test_trailer_exports_two_test_local_globals(self):
        source='\n'.join(co.compiled_application(SAMPLE))
        self.assertIn('EXTRN CO1INIT,CO1SW',source)
        self.assertIn("DC F'1192'\n         DC A(CO1INIT)",source)
        self.assertIn("DC F'1196'\n         DC A(CO1SW)",source)
        self.assertIn('CO1APP   CSECT',source)
        self.assertIn('END   CO1APP',source)

    def test_reject_existing_public_global_export(self):
        bad=SAMPLE.replace("DC F'4'", "DC F'1196'")
        with self.assertRaisesRegex(co.CandidateError,'already exported'):
            co.compiled_application(bad)

    def test_reject_malformed_trailer(self):
        bad=SAMPLE.replace('DC A(L999)', "DC X'12345678'")
        with self.assertRaises(co.CandidateError):
            co.compiled_application(bad)

    def test_candidate_runtime_only_patch(self):
        result='\n'.join(co.candidate_main(MAIN))
        self.assertIn('ENTRY STKOVFL,STKLIM',result)
        self.assertIn('ENTRY STKOVFL\n',MAIN)

    def test_deck_linkage_and_no_installed_writes(self):
        deck=co.build_deck(SAMPLE,MAIN,(FIXTURE/'co1change.asm').read_text('ascii'),
                           JOB_CARD,OBJ)
        self.assertEqual(deck.count('EXEC PGM=IFOX00'),3)
        self.assertEqual(deck.count('EXEC PGM=IEWL'),1)
        self.assertEqual(deck.count('EXEC PGM=*.LKED.SYSLMOD'),1)
        self.assertEqual(deck.count('\n/*\n'),4)
        for name in ('BCPLIO','BCPLMEM','BCPLBYTE','BCPLAPT','BCPLRGS','BCPLREG','BLIB'):
            self.assertIn(f' INCLUDE OBJ({name})',deck)
        self.assertNotIn(' INCLUDE OBJ(BCPLMAIN)',deck)
        self.assertNotIn('DISP=(NEW,CATLG)',deck)
        self.assertNotIn('BOOT.DEVOBJ',deck)
        self.assertIn('//OBJ      DD DSN='+OBJ+',DISP=SHR',deck)
        self.assertTrue(all(len(r)<=71 for r in deck.splitlines()
                            if r.startswith('//')))

    def test_deck_rejects_jcl_delimiter_in_source(self):
        with self.assertRaisesRegex(co.CandidateError,'JCL delimiter'):
            co.build_deck(SAMPLE,MAIN,'/*\n',JOB_CARD,OBJ)

    def test_accept_exact_completed_native_evidence(self):
        self.assertEqual(co.assess(SUMMARY,REPORT,'8301')['bcpl_records'],
                         ['A1','R1','A2','R2','PASS'])

    def test_reject_wrong_job(self):
        with self.assertRaisesRegex(co.CandidateError,'identity'):
            co.assess(SUMMARY,REPORT,'8302')

    def test_reject_nonzero_ifox(self):
        with self.assertRaises(co.CandidateError):
            co.assess(SUMMARY.replace('RC=0000','RC=0008',1),REPORT,'8301')

    def test_reject_missing_link_or_go(self):
        for step in ('LKED', 'GO'):
            bad='\n'.join(r for r in SUMMARY.splitlines() if not r.startswith(step))
            with self.subTest(step=step),self.assertRaises(co.CandidateError):
                co.assess(bad,REPORT,'8301')

    def test_reject_mismatched_or_duplicate_output(self):
        for bad in (REPORT.replace('CO1BCPL R1','CO1BCPL R3'),
                    REPORT+'CO1BCPL PASS\n',REPORT+'CO1BCPL FAIL\n'):
            with self.subTest(report=bad), self.assertRaises(co.CandidateError):
                co.assess(SUMMARY,bad,'8301')

    def test_ignores_asm_literals_as_bcpl_output(self):
        extra="MSGA DC CL80'CO1BCPL A1'\n"
        self.assertEqual(co.assess(SUMMARY,extra+REPORT,'8301')['bcpl_records'][0],'A1')

    def test_synthetic_end_to_end_receipt_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            fixture=tmp/'fixture';fixture.mkdir()
            for name in ('source.bcpl','cambridge-parm.txt','co1change.asm'):
                (fixture/name).write_bytes((FIXTURE/name).read_bytes())
            main=tmp/'bcplmain.asm';main.write_text(MAIN)
            def fake_shell(cmd,**kwargs):
                if cmd[:3]==['git','rev-parse','HEAD']:
                    return subprocess.CompletedProcess(cmd,0,'FAKEHEAD\n','')
                if str(co.COMPILER) in [str(x) for x in cmd]:
                    target=Path(cmd[cmd.index('--output')+1]);target.write_text(SAMPLE)
                    return subprocess.CompletedProcess(cmd,0,'JOB 8300\n','')
                if 'submit-jcl' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,'JOB 8301\n','')
                if 'job-summary' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,SUMMARY,'')
                if 'dump-report-for-job' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,REPORT,'')
                raise AssertionError('unexpected host command '+repr(cmd))
            with (patch.object(co,'ROOT',tmp),patch.object(co,'FIXTURE',fixture),
                  patch.object(co,'MAIN',main),patch.object(co,'WORK',tmp/'workarea'),
                  patch.object(co,'COMPILER',tmp/'fake-compiler'),
                  patch.object(co,'SUBMIT',tmp/'submit-jcl'),
                  patch.object(co,'SUMMARY',tmp/'job-summary'),
                  patch.object(co,'REPORT',tmp/'dump-report-for-job'),
                  patch.object(co,'config_and_object',return_value=(JOB_CARD,OBJ)),
                  patch.object(co,'shell',side_effect=fake_shell),
                  contextlib.redirect_stdout(io.StringIO())):
                self.assertEqual(co.execute(),0)
            run=next((tmp/'workarea').iterdir())
            receipt=json.loads((run/'result.json').read_text())
            self.assertEqual(receipt['status'],'PASS')
            self.assertEqual(receipt['compiler_job_id'],'8300')
            self.assertEqual(receipt['native_job_id'],'8301')
            self.assertFalse(receipt['installed_mvs_objects_modified'])
            self.assertFalse(receipt['co2_opened'])
            for name in ('compiler.log','candidate.jcl','submission.log',
                         'job-summary.log','job-report.log'):
                self.assertTrue((run/name).is_file(),name)

    def test_cli_requires_explicit_run(self):
        with patch('sys.argv',['run-co1-bcpl-switch.py']):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                co.main()
            self.assertEqual(caught.exception.code,2)


if __name__=='__main__':
    unittest.main()
