#!/usr/bin/env python3
"""Host-only tests for candidate native IFOX/IEWL/GO switch runner."""
import importlib.util
import json
import subprocess
import contextlib
import io
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/coroutines/run-co1-native-smoke.py'
spec = importlib.util.spec_from_file_location('co1_native_smoke', SCRIPT)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
SRC = ROOT / 'packaging/milestones/coroutines/candidates/co1-native-switch'

SUMMARY = '''JOB 5349  CO1NAT
13 NOV 26
STEP       PROGRAM      RESULT
ASMSW      IFOX00       RC=0000
ASMTST     IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         CO1NAT       RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000
'''
REPORT = ('\n CO1STAGE A1                                                                            \n'
          'CO1STAGE B1\nCO1STAGE A2\nCO1STAGE B2\nCO1STAGE PASS\n')


class CandidateTests(unittest.TestCase):
    def test_source_line_lengths(self):
        for name in ('co1switch.asm','co1native.asm'):
            self.assertTrue(smoke.checked_source(SRC/name).endswith('END\n') or
                            '         END   CO1ROOT\n' in smoke.checked_source(SRC/name))

    def test_switch_is_small_and_asm_only(self):
        s = smoke.checked_source(SRC/'co1switch.asm')
        self.assertIn('CO1SW    CSECT',s)
        for line in ('STM   0,15,0(2)', 'ST    0,28(1)',
                     'LM    0,15,0(1)', 'BCR   15,6'):
            self.assertIn(line,s)

    def test_smoke_contains_two_first_activations(self):
        s = smoke.checked_source(SRC/'co1native.asm')
        for line in ('AONE     C     7,=F\'7\'', 'BONE     C     7,=F\'8\'',
                     'ATWO     C     7,=F\'9\'', 'BTWO     C     7,=F\'10\''):
            self.assertIn(line,s)

    def test_smoke_has_independent_frames(self):
        s = smoke.checked_source(SRC/'co1native.asm')
        self.assertIn('AFRAME   DS    32F',s)
        self.assertIn('BFRAME   DS    32F',s)
        self.assertIn("C     3,=F'314'",s)
        self.assertIn("C     3,=F'2718'",s)

    def test_prints_explicit_pass_and_fail(self):
        s = smoke.checked_source(SRC/'co1native.asm')
        self.assertIn("MSGOK    DC    CL80'CO1STAGE PASS'",s)
        self.assertIn("MSGFAIL  DC    CL80'CO1STAGE FAIL'",s)

    def test_inlined_jcl_has_two_ifox_one_iewl_go(self):
        s = smoke.checked_source(SRC/'co1switch.asm')
        d = smoke.checked_source(SRC/'co1native.asm')
        deck = smoke.build_deck(s,d)
        self.assertEqual(deck.count('EXEC PGM=IFOX00'),2)
        self.assertEqual(deck.count('EXEC PGM=IEWL'),1)
        self.assertEqual(deck.count('EXEC PGM=*.LKED.SYSLMOD'),1)
        self.assertEqual(deck.count('//SYSIN    DD *'),2)
        self.assertEqual(deck.count('\n/*\n'),3)

    def test_jcl_temporary_dataset_only(self):
        deck = smoke.build_deck(smoke.checked_source(SRC/'co1switch.asm'),
                                smoke.checked_source(SRC/'co1native.asm'))
        self.assertEqual(deck.count('&&CO1'),5) # two create, two link, one go load
        self.assertNotIn('BOOT_OBJ',deck)
        self.assertNotIn('DEVOBJ',deck)
        self.assertNotIn('DISP=OLD',deck)
        self.assertIn('SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR',deck)

    def test_jcl_card_limits(self):
        deck = smoke.build_deck(smoke.checked_source(SRC/'co1switch.asm'),
                                smoke.checked_source(SRC/'co1native.asm'))
        self.assertTrue(all(len(line)<=71 for line in deck.splitlines()
                            if line.startswith('//')))

    def test_jcl_requires_source_cards(self):
        with self.assertRaisesRegex(smoke.SmokeError,'terminators'):
            smoke.build_deck('/*\n','END\n')

    def test_source_rejects_overlong_card(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'long.asm'; p.write_text('CSECT   '+'X'*72+'\n')
            with self.assertRaisesRegex(smoke.SmokeError,'invalid assembler'):
                smoke.checked_source(p)

    def test_source_rejects_inline_delimiter(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'bad.asm'; p.write_text('/*\n')
            with self.assertRaisesRegex(smoke.SmokeError,'invalid assembler'):
                smoke.checked_source(p)

    def test_successful_mvs_summary_and_output(self):
        a=smoke.assess(SUMMARY,REPORT,'5349')
        self.assertEqual(list(a['steps']),['ASMSW','ASMTST','LKED','GO'])
        self.assertEqual(a['go_records'],['A1','B1','A2','B2','PASS'])

    def test_reject_incorrect_job_id(self):
        with self.assertRaisesRegex(smoke.SmokeError,'identify'):
            smoke.assess(SUMMARY,REPORT,'5348')

    def test_reject_nonzero_assembler_rc(self):
        with self.assertRaisesRegex(smoke.SmokeError,'nonzero'):
            smoke.assess(SUMMARY.replace('RC=0000','RC=0008',1),REPORT,'5349')

    def test_reject_bypassed_link(self):
        with self.assertRaisesRegex(smoke.SmokeError,'missing'):
            smoke.assess(SUMMARY.replace('LKED       IEWL         RC=0000\n',''),REPORT,'5349')

    def test_reject_absent_go_step(self):
        with self.assertRaisesRegex(smoke.SmokeError,'missing'):
            smoke.assess(SUMMARY.replace('GO         CO1NAT       RC=0000\n',''),REPORT,'5349')

    def test_reject_extra_go_step(self):
        with self.assertRaisesRegex(smoke.SmokeError,'duplicate'):
            smoke.assess(SUMMARY.replace('GO         CO1NAT       RC=0000\n',
                                         'GO         CO1NAT       RC=0000\n'*2),REPORT,'5349')

    def test_reject_wrong_stage_order(self):
        with self.assertRaisesRegex(smoke.SmokeError,'records differ'):
            smoke.assess(SUMMARY,REPORT.replace('CO1STAGE B1','CO1STAGE X1'),'5349')

    def test_reject_explicit_fail(self):
        with self.assertRaisesRegex(smoke.SmokeError,'records differ'):
            smoke.assess(SUMMARY,REPORT+'CO1STAGE FAIL\n','5349')

    def test_reject_duplicate_pass(self):
        with self.assertRaisesRegex(smoke.SmokeError,'records differ'):
            smoke.assess(SUMMARY,REPORT+'CO1STAGE PASS\n','5349')

    def test_ignores_asm_literal_in_report(self):
        self.assertEqual(smoke.assess(SUMMARY,"MSGA1 DC CL80'CO1STAGE A1'\n"+REPORT,'5349')['go_records'][0], 'A1')

    def test_reject_incomplete_summary(self):
        with self.assertRaisesRegex(smoke.SmokeError,'zero-RC'):
            smoke.assess(SUMMARY.replace('JOB RESULT: SUCCESS','JOB RESULT: FAILURE'),REPORT,'5349')

    def test_fake_end_to_end_receipt_no_mvs_submission(self):
        # Every external command is replaced: synthetic JOB 8127, NOT JES.
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp) / 'workarea'
            fake_summary = SUMMARY.replace('5349', '8127')
            def fake_shell(cmd, **kwargs):
                if cmd[:3] == ['git', 'rev-parse', 'HEAD']:
                    return subprocess.CompletedProcess(cmd,0,'FAKEHEAD\n','')
                if 'submit-jcl' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,'JOB 8127\n','')
                if 'job-summary' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,fake_summary,'')
                if 'dump-report-for-job' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,REPORT,'')
                raise AssertionError(f'unexpected external command: {cmd}')
            with (patch.object(smoke,'WORK',work),
                  patch.object(smoke,'ROOT',Path(temp)),
                  patch.object(smoke,'SWITCH',SRC/'co1switch.asm'),
                  patch.object(smoke,'DRIVER',SRC/'co1native.asm'),
                  patch.object(smoke,'shell',side_effect=fake_shell)):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(smoke.execute(),0)
            folders = list(work.iterdir())
            self.assertEqual(len(folders),1)
            recorded=json.loads((folders[0]/'result.json').read_text())
            self.assertEqual(recorded['status'],'PASS')
            self.assertFalse(recorded['installed_mvs_object'])
            self.assertEqual(recorded['jes_job_id'],'8127')
            self.assertEqual(recorded['go_records'],['A1','B1','A2','B2','PASS'])
            self.assertTrue((folders[0]/'candidate.jcl').is_file())
            self.assertTrue((folders[0]/'job-report.log').is_file())

    def test_fake_end_to_end_rejects_wrong_native_trace(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp) / 'workarea'
            def fake_shell(cmd, **kwargs):
                if cmd[0]=='git':
                    return subprocess.CompletedProcess(cmd,0,'FAKEHEAD\n','')
                if 'submit-jcl' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,'JOB 8127\n','')
                if 'job-summary' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,SUMMARY.replace('5349','8127'),'')
                if 'dump-report-for-job' in str(cmd[0]):
                    return subprocess.CompletedProcess(cmd,0,REPORT.replace('B2','FAIL'),'')
                raise AssertionError(f'unexpected command: {cmd}')
            with (patch.object(smoke,'WORK',work),
                  patch.object(smoke,'ROOT',Path(temp)),
                  patch.object(smoke,'SWITCH',SRC/'co1switch.asm'),
                  patch.object(smoke,'DRIVER',SRC/'co1native.asm'),
                  patch.object(smoke,'shell',side_effect=fake_shell)):
                with (contextlib.redirect_stdout(io.StringIO()),
                      contextlib.redirect_stderr(io.StringIO())):
                    self.assertEqual(smoke.execute(),1)
            folder=next(work.iterdir())
            receipt=json.loads((folder/'result.json').read_text())
            self.assertEqual(receipt['status'],'FAIL')
            self.assertIn('records differ',receipt['reason'])
            self.assertTrue((folder/'job-report.log').is_file())

    def test_explicit_run_required(self):
        # Parser is deliberately CLI-gated; no automatic MVS submission.
        from unittest.mock import patch
        with patch('sys.argv',['run-co1-native-smoke.py']):
            with self.assertRaises(SystemExit) as caught:
                smoke.main()
            self.assertEqual(caught.exception.code,2)


if __name__=='__main__':
    unittest.main()
