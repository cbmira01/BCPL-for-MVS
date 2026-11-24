"""Offline tests of the extracted BC0005 MVS helper contracts. No live MVS."""
from pathlib import Path
import os
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import mvs_release as m
from release import Refusal


class MVSReleaseTests(unittest.TestCase):
    def test_stage_cards(self):
        members = {name: 'TEXT\n' for name in m.MEMBERS}
        members['MR10'] = '//R0003 EXEC PGM=IEBCOPY\n//OUT DD DISP=(NEW,CATLG,DELETE)\n//\n'
        deck = m.stage_deck('BOOT\n', members, stage='HERC02.BCPL.NEW.', dasd='TSO002')
        outer = '\n'.join(m.jcl_control_cards(deck.splitlines()))
        self.assertEqual(outer.count(' EXEC PGM=IEBGENER'), 9)
        self.assertEqual(outer.count(' EXEC PGM=IEFBR14'), 1)
        self.assertEqual(outer.count('DISP=(NEW,CATLG,DELETE)'), 2)
        self.assertEqual(outer.count('DD DATA,DLM=Z9'), 9)
        self.assertNotIn('R0003 EXEC', outer)
        self.assertIn('HERC02.BCPL.NEW.BT0002(MR10)', deck)
        self.assertIn(members['MR10'], deck)
        for bad in ('', 'Z9\n', 'X'*81+'\n'):
            with self.subTest(bad=bad), self.assertRaises(Refusal):
                m.stage_deck(bad, members, stage='HERC02.BCPL.NEW.', dasd='TSO002')
        with self.assertRaises(Refusal):
            m.stage_deck('BOOT\n', members, stage='BAD\n//.', dasd='TSO002')

    def test_control_cards(self):
        with self.assertRaises(Refusal):
            m.jcl_control_cards(['//SYSUT1 DD DATA,DLM=Z9','//S EXEC PGM=IEBGENER'])
        with self.assertRaises(Refusal):
            m.jcl_control_cards(['Z9'])
        with self.assertRaises(Refusal):
            m.jcl_control_cards(['//'+ 'X'*70])

    def test_bootstrap(self):
        boot, installer = m.bootstrap_decks('HERC02.BCPL.NEW', volser='BC0010', tape_unit='480',
                                            dasd_unit='SYSDA', dasd_vol='TSO002')
        self.assertIn('LABEL=(1,SL),DISP=OLD', boot)
        self.assertIn('LABEL=(2,SL),DISP=OLD', installer)
        self.assertIn('DSN=HERC02.BCPL.NEW.DIST.INST,', installer)
        self.assertIn('DISP=(NEW,CATLG,DELETE)', installer)
        self.assertIn('SER=BC0010', boot)
        self.assertNotIn('<', boot+installer)
        self.assertNotIn('BC0003', boot+installer)
        with self.assertRaises(Refusal):
            m.bootstrap_decks('HERC02.BCPL.NEW', volser='BC0010', tape_unit='480',
                              dasd_unit='SYSDA', dasd_vol='BC0010')

    def test_installer_readback(self):
        deck = m.readback_deck('HERC02.BCPL.NEW', 'MR10')
        self.assertIn('DIST.INST(MR10)', deck)
        self.assertIn('DIST.INST(COPY)', deck)
        self.assertEqual(deck.count('DISP=SHR'), 2)
        canonical = '//GO EXEC M10PROC\n//\n'
        report = 'PAGE 1\n  //GO EXEC M10PROC  \nPAGE 2\n  //\n'
        self.assertEqual(m.extract_profile(report, canonical), canonical)
        self.assertEqual(m.read_cards(report, canonical), canonical)
        for f in (m.extract_profile, m.read_cards):
            with self.assertRaises(Refusal):
                f(report.replace('M10PROC','BADPROC'), canonical)
        with self.assertRaises(Refusal):
            m.readback_deck('HERC02.BCPL.NEW','UNKNOWN')

    def test_proc_results(self):
        summary = 'JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        rows = ''.join(f'IEF142I TESTJOB GO.R{n:04d} - STEP WAS EXECUTED - COND CODE 0000\n' for n in (3,4))
        self.assertEqual(m.profile_result('TESTJOB',rows,summary,(3,4)),2)
        for bad in (rows.replace('0000','0004',1), rows+rows, rows.replace('R0003','R0005'), rows+'IEF450I ABEND\n'):
            with self.assertRaises(Refusal):
                m.profile_result('TESTJOB',bad,summary,(3,4))
        with self.assertRaises(Refusal):
            m.profile_result('TESTJOB','',summary,())

    def test_tape_state(self):
        empty = 'HHC02279I 0480 3420 * EMPTY\n'
        loaded = 'HHC02279I 0480 3420 /tk5/tape/test.aws\n'
        self.assertEqual(m.drive_state(empty,'480 3400 O-NRD',['test.aws']),'EMPTY')
        self.assertEqual(m.drive_state(loaded,'480 3400 O',['test.aws']),'test.aws')
        for h,g in ((loaded,'480 3400 O-NRD'), (empty,'480 3400 O'),
                    (loaded.replace('test.aws','oldtest.aws'),'480 3400 O'),
                    (loaded,'480 3400 O ALLOCATED'),(loaded+loaded,'480 3400 O'),
                    (loaded,'480 3400 O\n480 3400 O-NRD')):
            with self.assertRaises(Refusal):
                m.drive_state(h,g,['test.aws'])

    def test_volser(self):
        labels = "Label : 'VOL1'\nVolume Serial : 'BC0010'\nLabel : 'HDR1'\nVolume Serial : 'BC0004'\n"
        self.assertEqual(m.volser_from_hetmap(labels),'BC0010')
        with self.assertRaises(Refusal):
            m.volser_from_hetmap(labels+labels)

    def test_listds_exact(self):
        def parse(block):
            return dict(volume='TSO002',dsorg='PO' if 'PO' in block[2] else 'PS',recfm='FB',lrecl='80',blksize='800')
        core = SimpleNamespace(parse_listds=parse)
        report = 'HERC02.BCPL.BOOT\n RECFM DSORG\n FB PS\nHERC02.BCPL.BOOT.JCL\n RECFM DSORG\n FB PO\n'
        self.assertEqual(m.exact_listds(core,report,'HERC02.BCPL.BOOT')[0]['dsorg'],'PS')
        self.assertEqual(m.exact_listds(core,report,'HERC02.BCPL.BOOT.JCL')[0]['dsorg'],'PO')
        with self.assertRaises(Refusal):
            m.exact_listds(core,report,'HERC02.BCPL')
        with self.assertRaises(Refusal):
            m.exact_listds(core,report+'HERC02.BCPL.BOOT\n RECFM DSORG\n FB PO\n','HERC02.BCPL.BOOT')

    def test_inventory(self):
        name = 'HERC02.BCPL.NEW.DIST.INST'
        header = '//{} JOB X\n//             USER=X\n//             MSGLEVEL=(1,1)\n//\n'
        core = SimpleNamespace(stat_deck=lambda cfg,names:header.format('DSPALST'),
                               parse_listds=lambda b:dict(volume='TSO002',dsorg='PO',recfm='FB',lrecl='80',blksize='800'))
        ls = SimpleNamespace(list_members_deck=lambda cfg,names:header.format('DSPALLS'),
                             member_blocks=lambda report,names:{name:['COPY']},parse_members=lambda b:b)
        with tempfile.TemporaryDirectory() as d:
            results = [(1,name+'\n RECFM DSORG\n FB PO\n',''), (2,'directory','')]
            with patch.object(m,'submit_job',side_effect=results) as submit:
                self.assertEqual(m.verify_inventory(core,{},ls,Path(d),'test',[(2,name,['COPY'])],volume='TSO002'),(1,2,1))
                self.assertEqual(submit.call_count,2)
            with patch.object(m,'submit_job',side_effect=results):
                with self.assertRaises(Refusal):
                    m.verify_inventory(core,{},ls,Path(d),'test',[(2,name,['WRONG'])],volume='TSO002')
            with patch.object(m,'submit_job',side_effect=results) as submit:
                with self.assertRaises(Refusal):
                    m.verify_inventory(core,{},ls,Path(d),'test',[(2,name,['COPY'])],volume='OTHER1')
                self.assertEqual(submit.call_count,1)

    def test_submit_job(self):
        body = '//STEP1 EXEC PGM=IEBGENER\n//\n'
        summary = 'JOB 1234 TESTJOB\nSTEP1 IEBGENER RC=0000\nJOB RESULT: SUCCESS\n'
        report = 'IEF142I TESTJOB STEP1 - STEP WAS EXECUTED - COND CODE 0000\n'
        core = Mock()
        core.authenticated_job_card.return_value = ['//TESTJOB JOB SECRET']
        core.submit_and_wait.return_value = (1234,summary)
        core.job_report.return_value = report
        oldenv, oldtemp = os.environ.get('TMPDIR'), tempfile.tempdir
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            self.assertEqual(m.submit_job(core,{},p,'test','TESTJOB',body,[('STEP1','IEBGENER')]),(1234,report,summary))
            self.assertEqual((p/'test-body.jcl').read_text(),body)
            self.assertNotIn('SECRET',''.join(x.read_text() for x in p.iterdir()))
            self.assertEqual(os.environ.get('TMPDIR'),oldenv)
            self.assertEqual(tempfile.tempdir,oldtemp)
            with self.assertRaises(Refusal):
                m.submit_job(core,{},p,'inject','TESTJOB','//BAD JOB X\n//\n',[])
            core.job_report.return_value = report.replace('0000','0004')
            with self.assertRaises(Refusal):
                m.submit_job(core,{},p,'failed','TESTJOB',body,[('STEP1','IEBGENER')])
            self.assertTrue((p/'failed-report.txt').is_file())
            self.assertEqual(core.submit_and_wait.call_count,2)

    def test_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            m.artifact(p,'one.txt','data')
            with self.assertRaises(FileExistsError):
                m.artifact(p,'one.txt','wrong')
            with self.assertRaises(Refusal):
                m.artifact(p,'../wrong.txt','data')
            m.seal(p)
            self.assertEqual((p/'SHA256SUMS').read_text(),m.digest(b'data')+'  one.txt\n')
            with self.assertRaises(Refusal):
                m.seal(p)

    def test_demos(self):
        steps = [('C01','ICINT19'),('R01','ICINT19')]
        report = 'EXECUTION CYCLES = 1, CODE = 0\nDEMO: OK\nEXECUTION CYCLES = 2, CODE = 0\n'
        self.assertEqual(m.verify_demos(report,['ONE'],steps)['interpreted_zero_codes'],2)
        for bad in (report.replace('DEMO:','OTHER:'), report.replace('CODE = 0','CODE = 4',1),report+'DEMO: EXTRA\n'):
            with self.assertRaises(Refusal):
                m.verify_demos(bad,['ONE'],steps)

    def test_suite_binding(self):
        canonical = ''.join(f'//S{i:02d} EXEC PGM=IEBGENER\n' for i in range(5))
        canonical += '//R01 EXEC PGM=ICINT19\n//STEPLIB DD DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR\n//\n'
        prefix = 'HERC02.BCPL.NEW'
        allowed = {prefix+'.MR10KIT.LOAD'}
        body,steps = m.suite_deck(canonical,prefix,6,allowed)
        self.assertEqual(len(steps),6)
        self.assertIn('DSN=HERC02.BCPL.NEW.MR10KIT.LOAD',body)
        for bad in (canonical.replace('DISP=SHR','DISP=OLD'),canonical.replace('MR10KIT.LOAD','OTHER.LOAD'),canonical+'//R02 EXEC PGM=ICINT19\n//\n'):
            with self.assertRaises(Refusal):
                m.suite_deck(bad,prefix,6,allowed)


if __name__ == '__main__':
    unittest.main()
