"""Offline safety, JCL-shape, no-retry and MVS-result tests for RC3."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ta2-rc3-consolidated'
loader = importlib.machinery.SourceFileLoader('ta2_rc3', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def rows():
    result=[]
    for n in range(1,22):
        d={'dsorg':'PS' if n==1 else 'PO','recfm':'U' if n==12 else 'FB',
           'lrecl':0 if n==12 else 80,'blksize':6144 if n==12 else 800}
        result.append({'n':n,'dcb':d,'source':mod.SRC+f'BT{n:04d}',
                       'stage':mod.STAGE+f'BT{n:04d}',
                       'target':mod.INSTALL+f'BT{n:04d}',
                       'space':(5,1,0) if n==1 else (20,5,10)})
    return result


class Tests(unittest.TestCase):
    def setUp(self):
        self.rows=rows()
        self.changes=[(f'T{i:07d}',f'src{i}',f'WRITEF("TEST: T{i}*N")\nWRITEF("EXP: X*N")\n')
                      for i in range(1,13)]
        self.boot={'BT0001':'BOOT RC3\n',**{x:'RELEASE RC3\n' for x in mod.MEMBERS}}

    def test_stage_card_contract(self):
        deck=mod.stage_body(self.rows,self.changes,self.boot)
        self.assertEqual(deck.count(' EXEC PGM='),37)
        self.assertEqual(deck.count('DISP=(NEW,CATLG,DELETE)'),21)
        self.assertEqual(deck.count('DLM=Z9'),17)
        self.assertEqual(deck.count(' COPY OUTDD=OUTPDS,INDD=INPDS'),20)
        self.assertIn('DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144',deck)
        self.assertNotIn(mod.INSTALL,deck)
        self.assertNotIn('DSN=BCPL.BT',deck)
        self.assertTrue(all(len(x)<=80 for x in deck.splitlines()))
        self.assertTrue(all(len(x)<=71 for x in deck.splitlines() if x.startswith('//') and not x.startswith('//*')))

    def test_real_bcpl_source_comment_width_in_dd_data(self):
        # The twelve canonical MR10 sources have 73-column // separators.
        comment = '// ' + '=' * 70
        self.assertEqual(len(comment), 73)
        deck = mod.cards(['//E0001 EXEC PGM=IEBGENER',
                          '//SYSUT1 DD DATA,DLM=Z9',
                          comment, '// ' + 'X' * 77, 'Z9',
                          '//SYSUT2 DD DSN=OUTPUT,DISP=SHR'])
        self.assertIn(comment, deck)
        self.assertEqual(len('// ' + 'X' * 77), 80)
        changes = list(self.changes)
        member, path, content = changes[0]
        changes[0] = (member, path, comment + '\n' + content)
        staged = mod.stage_body(self.rows, changes, self.boot)
        self.assertIn(comment, staged)

    def test_dd_data_not_permit_actual_overwidth_jcl(self):
        with self.assertRaisesRegex(mod.Refusal, 'JCL operands over column 71'):
            mod.cards(['//E0001 EXEC PGM=IEBGENER',
                       '//SYSUT1 DD DATA,DLM=Z9',
                       '// ' + '=' * 70, 'Z9', '//X DD ' + 'a' * 72])
        with self.assertRaisesRegex(mod.Refusal, 'not FB80-safe'):
            mod.cards(['//SYSUT1 DD DATA,DLM=Z9',
                       '// ' + '=' * 78, 'Z9'])
        with self.assertRaisesRegex(mod.Refusal, 'unterminated DD DATA'):
            mod.cards(['//SYSUT1 DD DATA,DLM=Z9',
                       '// ' + '=' * 70])
        with self.assertRaisesRegex(mod.Refusal, 'orphan in-stream Z9'):
            mod.cards(['Z9'])

    def test_reject_data_delimiter_and_overwidth(self):
        with self.assertRaises(mod.Refusal):mod.in_data('Z9-A\n')
        with self.assertRaises(mod.Refusal):mod.cards(['//X DD ' + 'a'*72])
        with self.assertRaises(mod.Refusal):mod.stage_body(self.rows,[(f'X{i:07d}','p','Z9-COLLISION\n') for i in range(12)],self.boot)

    def test_stage_refuses_missing_changes(self):
        with self.assertRaises(mod.Refusal):mod.stage_body(self.rows,self.changes[:11],self.boot)

    def test_mvs_step_success_must_be_exact(self):
        def fake_core(summary):
            core=Mock()
            core.authenticated_job_card.return_value=['//TA2R3STG JOB (BCPL)']
            core.submit_and_wait.return_value=(9370,summary)
            core.job_report.return_value='IEF142I TA2R3STG S0001 - STEP WAS EXECUTED - COND CODE 0000'
            return core
        success='JOB 9370 TA2R3STG\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\nS0001 IEBGENER RC=0000\n'
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            folder=Path(d)
            core=fake_core(success)
            job,*_=mod.mvs_job(core,{},folder,'stage','TA2R3STG','//', [('S0001','IEBGENER')])
            self.assertEqual(job,9370)
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            with self.assertRaises(mod.Refusal):
                mod.mvs_job(fake_core(success.replace('S0001 IEBGENER RC=0000','S0001 IEBGENER RC=0004')),
                            {},Path(d),'stage','TA2R3STG','//',[('S0001','IEBGENER')])

    def test_one_shot_marker_exclusive(self):
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            mark=Path(d)/'marker'
            mod.exclusive(mark,b'ONCE')
            with self.assertRaises(FileExistsError):mod.exclusive(mark,b'TWICE')
            self.assertEqual(mark.read_bytes(),b'ONCE')

    def test_catalog_guard_on_absence_and_dcb(self):
        core=Mock()
        core.stat_deck.return_value='//STAT EXEC PGM=IKJEFT01\n'
        core.submit_and_wait.return_value=(9371,'STATS')
        core.job_report.return_value='MVS report'
        core.dataset_missing.side_effect=lambda report,dsn: dsn.startswith((mod.STAGE,mod.INSTALL))
        core.extract_listds_block.side_effect=lambda report,dsn:[dsn]
        def parse(block):
            n=int(block[0][-4:]);d=self.rows[n-1]['dcb']
            return {'volume':'TSO002','dsorg':d['dsorg'],'recfm':d['recfm'],
                    'lrecl':str(d['lrecl']),'blksize':str(d['blksize'])}
        core.parse_listds.side_effect=parse
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            self.assertEqual(mod.catalog(core,{},Path(d),self.rows),9371)
        core.dataset_missing.side_effect=lambda report,dsn:False
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            with self.assertRaises(mod.Refusal):mod.catalog(core,{},Path(d),self.rows)

    def test_postrestore_catalog_dcb_and_volume(self):
        core = Mock()
        core.stat_deck.return_value = '//STAT EXEC PGM=IKJEFT01\n'
        core.submit_and_wait.return_value = (
            9373, 'JOB 9373 DSPALST\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n')
        core.job_report.return_value = 'MVS LISTDS RECIPIENT'
        core.dataset_missing.return_value = False
        core.extract_listds_block.side_effect = lambda report, dsn: [dsn]
        def parse(block):
            n = int(block[0][-4:])
            d = self.rows[n-1]['dcb']
            return {'volume':'TSO002','dsorg':d['dsorg'],'recfm':d['recfm'],
                    'lrecl':str(d['lrecl']),'blksize':str(d['blksize'])}
        core.parse_listds.side_effect = parse
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            self.assertEqual(mod.catalog(core,{},Path(d),self.rows,recipient=True),9373)
        core.parse_listds.side_effect = lambda block: dict(parse(block), volume='TSO003')
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            with self.assertRaises(mod.Refusal):
                mod.catalog(core,{},Path(d),self.rows,recipient=True)

    def test_all_63_regression_jes_steps(self):
        import re
        deck = mod.JCL.read_text('ascii')
        expected = re.findall(
            r'(?m)^//([A-Z0-9]{1,8})\s+EXEC PGM=(IEBGENER|ICINT19)\b', deck)
        self.assertEqual(len(expected), 63)
        summary = 'JOB 9374 TA2R3MR\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
        summary += '\n'.join(f'{n} {p} RC=0000' for n,p in expected) + '\n'
        report = '\n'.join(
            f'IEF142I TA2R3MR {n} - STEP WAS EXECUTED - COND CODE 0000'
            for n,_ in expected) + '\n'
        mod.verify_regression_execution(summary,report,deck)
        with self.assertRaises(mod.Refusal):
            mod.verify_regression_execution(
                summary.replace('C01A ICINT19 RC=0000\n',''),report,deck)
        with self.assertRaises(mod.Refusal):
            mod.verify_regression_execution(
                summary.replace('R12 ICINT19 RC=0000','R12 ICINT19 RC=0004'),report,deck)
        with self.assertRaises(mod.Refusal):
            mod.verify_regression_execution(
                summary,report.replace(
                    'IEF142I TA2R3MR C01A - STEP WAS EXECUTED - COND CODE 0000\n',''),deck)
        with self.assertRaises(mod.Refusal):
            mod.verify_regression_execution(
                summary,report +
                    'IEF142I TA2R3MR R12 - STEP WAS EXECUTED - COND CODE 0000\n',deck)

    def test_semantics_bind_real_rc3_job_id(self):
        reviewer = Mock()
        reviewer.panel.return_value = []
        reviewer.inspect.return_value = {
            'exp_contract_met': True, 'golden_rp_and_code_match': True,
            'status': 'EXP_RP_CODE_COMPARISON_PASS_HUMAN_SIGNOFF_PENDING',
            'mvs_job': 9346}
        result = mod.validated_semantics(reviewer,'REAL SYSOUT',9375)
        self.assertEqual(result['mvs_job'],9375)
        self.assertEqual(result['candidate_id'],'BCPL-0.1.0-rc3')
        reviewer.inspect.return_value['exp_contract_met'] = False
        with self.assertRaises(mod.Refusal):
            mod.validated_semantics(reviewer,'BAD SYSOUT',9375)

    def test_revised_bootstrap_and_nineteenth_installer_dataset(self):
        class Boot:
            @staticmethod
            def installer_members(manifest, first20):
                assert len(first20) == 20
                restore = ['//* OLD 18-PDS RESTORE']
                for i in range(3, 21):
                    restore += [f'//R{i:04d} EXEC PGM=IEBCOPY',
                                ' COPY OUTDD=OUTPDS,INDD=INTAPE']
                restore.append('//')
                return {'INSTALL':'REVIEW ALL 18 TARGET DSNS\n',
                        'DATASETS':'BCPL.BT0020 -> <HLQ>.BCPL.EXT.MAC\n',
                        'RELEASE':'VOLSER BC0003\n', 'RESTORE':'\n'.join(restore)+'\n'}
            @staticmethod
            def bootstrap(manifest, rows):
                return 'CANDIDATE BCPL-0.1.0-rc3\nVOLUME BC0003\nBCPL.BT0021\n'
        entries=[{} for _ in range(20)] + [{'target_dsn_template':'{HLQ}.BCPL.CAMBRIDG.SOURCE'}]
        m={'datasets':entries}
        result=mod.materials(m,Boot)
        self.assertIn('ALL 19 TARGET',result['INSTALL'])
        self.assertIn('BCPL.BT0021',result['DATASETS'])
        self.assertEqual(result['RESTORE'].count(' COPY OUTDD=OUTPDS,INDD=INTAPE'),19)
        self.assertIn('VOL=SER=BC0003,LABEL=(21,SL)',result['RESTORE'])
        self.assertNotIn('BC0002',''.join(result.values()))

    def test_media_collision_refusal(self):
        with tempfile.TemporaryDirectory(dir=mod.WORK) as d:
            original=mod.TAPES;image=mod.IMAGE
            try:
                mod.TAPES=Path(d);mod.IMAGE=Path(d)/'future.aws'
                (Path(d)/'older.aws').write_bytes(b'old')
                with patch.object(mod,'run_command',return_value='VOL1'):
                    prod=Mock();prod.volser_from_hetmap.return_value='BC0003'
                    with self.assertRaises(mod.Refusal):mod.existing_media(Path(d),prod)
            finally:
                mod.TAPES=original;mod.IMAGE=image

if __name__ == '__main__':unittest.main()
