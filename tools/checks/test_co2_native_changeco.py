#!/usr/bin/env python3
"""Offline source, JCL and synthetic-evidence checks for CO.2."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT/'bootstrap-toolchain/asm/bcplco.asm'
FIXTURE = ROOT/'packaging/milestones/coroutines/candidates/co2-native-changeco'
RUNNER = ROOT/'tools/coroutines/run-co2-native-changeco.py'
spec = importlib.util.spec_from_file_location('co2_native', RUNNER)
assert spec and spec.loader
co = importlib.util.module_from_spec(spec)
spec.loader.exec_module(co)

SAMPLE = """         CSECT
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
"""
MAIN = """BCPLMAIN CSECT
         ENTRY STKOVFL
STKLIM   DC    F'0'
         END   BCPLMAIN
"""
SUMMARY = """JOB 8301  CO2BGO
STEP       PROGRAM      RESULT
ASMA       IFOX00       RC=0000
ASMM       IFOX00       RC=0000
ASMS       IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         CO2BGO       RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
"""
REPORT = "".join("CO2BCPL "+x+"\n" for x in co.EXPECTED)
CARD = ["//CO2BGO  JOB (BCPL),'CO2 BCPL NATIVE',CLASS=A"]
OBJ = "HERC02.BCPL.BOOT.OBJ"


class CO2Tests(unittest.TestCase):
    def test_assembly_is_valid_ifox_card_deck(self):
        code = ASM.read_text('ascii')
        co.checked_cards(code, 'BCPLCO')
        self.assertIn('BCPLCO   CSECT', code)
        self.assertIn('ENTRY CO2INIT,CHANGECO', code)
        self.assertNotIn('CO1SW', code)
        self.assertNotIn('CO1CHG', code)

    def test_switch_preserves_registers_and_limits(self):
        code = ASM.read_text('ascii')
        for expected in (
            'CHANGECO    STM   0,15,CO2SREG',
            'MVC   32(64,2),CO2SREG',
            'L     0,CO2SREG+16',
            'ST    0,0(5)',
            'L     0,CO2SREG+20',
            'ST    0,4(5)',
            'L     0,CO2SREG+24',
            'ST    0,8(5)',
            'LM    0,15,0(1)',
            'L     4,=A(STKLIM)',
            'L     4,=A(APLIMIT)',
            'ST    0,216(12)',
            'ST    0,220(12)',
            'CO2WBOOT BALR  6,4',
            'CO2WDONE BALR  10,0',
            'CO2TERM L',
        ):
            self.assertIn(expected, code)

    def test_membership_before_target_read(self):
        switch = ASM.read_text('ascii').split(
            'CHANGECO    STM', 1)[1].split('CO2RET ', 1)[0]
        self.assertLess(switch.index('C     2,REGW1'),
                        switch.index('L     0,0(2)'))
        self.assertLess(switch.index('C     2,REGW2'),
                        switch.index('L     0,0(2)'))
        self.assertIn('C     2,CURPTR', switch)
        self.assertIn("C     0,=F'3'", switch)

    def test_bcpl_nested_worker_hop_and_boundaries(self):
        src = (FIXTURE/'source.bcpl').read_text('ascii')
        self.assertTrue(all(len(line) <= 80 for line in src.splitlines()))
        for x in ('NEST1(3)', 'NEST2(4)', 'PEER1:295', 'PEER2:296',
                  'ROOTCTX:297', 'CO2INIT:298', 'CHANGECO:299',
                  'STACKBASE \\= PEER1!4', 'STACKEND \\= PEER2!6',
                  'CHANGECO(17,PEER2)', 'CHANGECO(23,PEER1)',
                  'CHANGECO(33,ROOTCTX)', 'CHANGECO(55,P2)',
                  'CHANGECO(44,P1)', 'RESULTIS 31', 'RESULTIS 42'):
            self.assertIn(x, src)
        self.assertNotIn('STACK1!0 :=', src)
        self.assertEqual((FIXTURE/'cambridge-parm.txt')
                         .read_text('ascii').splitlines(), ['/CN'+'/'*77])

    def test_compiler_export_adapter(self):
        app = '\n'.join(co.compiled_application(SAMPLE))
        self.assertIn('CO2APP   CSECT', app)
        self.assertIn('EXTRN CO2INIT,CHANGECO', app)
        self.assertIn("DC F'1192'\n         DC A(CO2INIT)", app)
        self.assertIn("DC F'1196'\n         DC A(CHANGECO)", app)

    def test_no_export_collision(self):
        bad = SAMPLE.replace("DC F'4'", "DC F'1196'")
        with self.assertRaises(co.CandidateError):
            co.compiled_application(bad)

    def test_jcl_produces_temporary_objects_only(self):
        deck = co.build_deck(SAMPLE, MAIN, ASM.read_text('ascii'), CARD, OBJ)
        self.assertEqual(deck.count('EXEC PGM=IFOX00'), 3)
        self.assertEqual(deck.count('EXEC PGM=IEWL'), 1)
        self.assertEqual(deck.count('EXEC PGM=*.LKED.SYSLMOD'), 1)
        self.assertEqual(deck.count('\n/*\n'), 4)
        for m in ('BCPLIO','BCPLMEM','BCPLBYTE','BCPLAPT',
                  'BCPLRGS','BCPLREG','BLIB'):
            self.assertIn(' INCLUDE OBJ('+m+')', deck)
        self.assertIn('//OBJ      DD DSN='+OBJ+',DISP=SHR', deck)
        self.assertNotIn('DISP=(NEW,CATLG)', deck)
        self.assertNotIn(' INCLUDE OBJ(BCPLMAIN)', deck)
        self.assertTrue(all(len(row)<=71 for row in deck.splitlines()))

    def test_strict_completed_job_oracle(self):
        self.assertEqual(co.assess(SUMMARY, REPORT, '8301')
                         ['bcpl_records'], list(co.EXPECTED))
        for summary, report, job in (
            (SUMMARY, REPORT, '8302'),
            (SUMMARY.replace('RC=0000','RC=0008',1), REPORT, '8301'),
            (SUMMARY, REPORT.replace('CO2BCPL B2','CO2BCPL B1'), '8301'),
            (SUMMARY, REPORT+'CO2BCPL PASS\n', '8301'),
            (SUMMARY, REPORT+'CO2BCPL FTERM\n', '8301'),
        ):
            with self.subTest(job=job, report=report), self.assertRaises(
                    co.CandidateError):
                co.assess(summary, report, job)

    def test_synthetic_driver_receipt_is_not_native_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            def fake_shell(cmd, **kwargs):
                if cmd[:3] == ['git','rev-parse','HEAD']:
                    return subprocess.CompletedProcess(cmd, 0, 'FAKEHEAD\n','')
                if str(co.COMPILER) in [str(x) for x in cmd]:
                    Path(cmd[cmd.index('--output')+1]).write_text(SAMPLE)
                    return subprocess.CompletedProcess(cmd,0,'JOB 8300\n','')
                if 'submit-jcl' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,'JOB 8301\n','')
                if 'job-summary' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,SUMMARY,'')
                if 'dump-report-for-job' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,REPORT,'')
                raise AssertionError(repr(cmd))
            with (patch.object(co,'ROOT',tmp),
                  patch.object(co,'MAIN',tmp/'bcplmain.asm'),
                  patch.object(co,'WORK',tmp/'evidence'),
                  patch.object(co,'SUBMIT',tmp/'submit-jcl'),
                  patch.object(co,'SUMMARY',tmp/'job-summary'),
                  patch.object(co,'REPORT',tmp/'dump-report-for-job'),
                  patch.object(co,'config_and_object',return_value=(CARD,OBJ)),
                  patch.object(co,'shell',side_effect=fake_shell),
                  contextlib.redirect_stdout(io.StringIO())):
                (tmp/'bcplmain.asm').write_text(MAIN)
                self.assertEqual(co.execute(),0)
            root = next((tmp/'evidence').iterdir())
            record = json.loads((root/'result.json').read_text())
            self.assertEqual(record['status'], 'PASS')
            self.assertEqual(record['git_head'], 'FAKEHEAD')
            self.assertFalse(record['production_abi_approved'])
            self.assertFalse(record['installed_mvs_objects_modified'])
            self.assertFalse(record['co2_accepted'])
            self.assertEqual(record['native_job_id'], '8301')
            self.assertTrue((root/'candidate.jcl').is_file())

    def test_cli_requires_run_flag(self):
        with patch.object(sys,'argv',['run-co2-native-changeco.py']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    co.main()
        self.assertEqual(cm.exception.code,2)


if __name__ == '__main__':
    unittest.main()
