"""Offline strict TA.2 readback JCL and guard tests (no MVS operations)."""
import importlib.machinery
import importlib.util
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/ta2-rc2-readback-plan'
loader=importlib.machinery.SourceFileLoader('ta2_rc2_rb_plan',str(SCRIPT))
spec=importlib.util.spec_from_loader(loader.name,loader)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fake_plan():
    result=[]
    for n in range(1,22):
        d={'dsorg':'PS' if n==1 else 'PO',
           'recfm':'U' if n==12 else 'FB',
           'lrecl':0 if n==12 else 80,
           'blksize':6144 if n==12 else 800}
        members=([] if n==1 else ['INSTALL','DATASETS','RELEASE','RESTORE'] if n==2
                 else [f'M{k:07d}' for k in range(110)] if n==3
                 else [f'S{k:07d}' for k in range(15)] if n==21 else ['MISC'])
        result.append({'target_dcb':d,'members':members,
                       'producer_source_dsn':f'HERC02.BCPL.TA2STG.BT{n:04d}'})
    return {'volume':{'volser':'BC0002'},'datasets':result}

def stage_budget():
    return {'status':'VOLUME_APPROVED_SPACE_AND_WRITE_UNAPPROVED',
            'volume':'TSO002', 'primary_total':645,'secondary_total':65,
            'targets':[{'sequence':i,'primary_tracks':135 if i==20 else 30,
                        'secondary_tracks':14 if i==20 else 3,'directory_blocks':7}
                       for i in range(3,21)]}

class ReadbackPlanTests(unittest.TestCase):
    def setUp(self):
        self.original=mod.SPACE
        self.tmpfile=Path('/tmp/never-read-stage-budget')
        self.budget=stage_budget()
        self.real_read=Path.read_text
        self.data=fake_plan()
        self.rows=self.alloc()
    def alloc(self):
        original=mod.SPACE
        with patch.object(Path,'read_text',autospec=True,
                          side_effect=lambda path:json.dumps(self.budget) if path==original else self.real_read(path)):
            return mod.rows(self.data)
    def test_contract_and_21_allocations(self):
        self.assertEqual(len(self.rows),21)
        self.assertEqual(sum(len(r['members']) for r in self.rows),146)
        self.assertEqual(sum(r['space'][0] for r in self.rows),770)
        self.assertEqual(sum(r['space'][1] for r in self.rows),81)
        self.assertEqual(self.rows[11]['dcb']['recfm'],'U')
        self.assertEqual(self.rows[-1]['space'],(100,10,10))
    def test_twenty_one_exact_read_steps(self):
        s=mod.render(self.rows,'TSO002')
        self.assertEqual(s.count(' EXEC PGM=IEBGENER'),1)
        self.assertEqual(s.count(' EXEC PGM=IEBCOPY'),20)
        self.assertEqual(s.count('DISP=OLD'),21)
        self.assertEqual(s.count('DISP=(NEW,CATLG,DELETE)'),21)
        self.assertEqual(s.count('VOL=(PRIVATE,RETAIN,SER=BC0002)'),21)
        self.assertEqual(s.count('LABEL=('),21)
        self.assertEqual(s.count('DSN=HERC02.BCPL.TA2RB.BT'),21)
    def test_21st_step_and_load_library_preserved(self):
        s=mod.render(self.rows,'TSO002')
        self.assertIn('//R0021 EXEC PGM=IEBCOPY',s)
        self.assertIn('LABEL=(21,SL)',s)
        block=s.split('//R0012 EXEC')[1].split('//R0013 EXEC')[0]
        self.assertIn('DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144',block)
    def test_no_tape_output_or_stage_modifications(self):
        s=mod.render(self.rows,'TSO002')
        self.assertNotIn('OUTTAPE',s)
        self.assertNotIn('DSN=HERC02.BCPL.TA2STG.',s)
        self.assertNotIn('DISP=(NEW,KEEP',s)
    def test_cards_fit_column_71(self):
        s=mod.render(self.rows,'TSO002')
        self.assertTrue(all(len(row)<=80 for row in s.splitlines()))
        self.assertTrue(all(len(row)<=71 for row in s.splitlines()
                 if row.startswith('//') and not row.startswith('//*')))
    def test_no_implicit_dasd_choice(self):
        self.assertNotEqual(hashlib.sha256(mod.render(self.rows,'TSO002').encode()).hexdigest(),
                            hashlib.sha256(mod.render(self.rows,'TSO003').encode()).hexdigest())
    def test_reject_reserved_or_invalid_volser(self):
        for v in ('BC0002','BTA101','BTA102','BTO001','BAD-V','SEVEN77',''):
            with self.subTest(v=v),self.assertRaises(mod.Refusal):mod.render(self.rows,v)
    def test_refuse_wrong_sequence(self):
        p=self.rows.copy();p[-1]=dict(p[-1],n=20)
        with self.assertRaises(mod.Refusal):mod.render(p,'TSO002')
    def test_refuse_changed_load_dcb(self):
        p=fake_plan();p['datasets'][11]['target_dcb']={'dsorg':'PO','recfm':'FB','lrecl':80,'blksize':800}
        with self.assertRaisesRegex(mod.Refusal,'BT0012 DCB changed'):
            with patch.object(Path,'read_text',autospec=True,side_effect=lambda _:json.dumps(self.budget)):
                mod.rows(p)
    def test_refuse_budget_drift(self):
        budget=stage_budget();budget['primary_total']=0
        with self.assertRaises(mod.Refusal):
            with patch.object(Path,'read_text',autospec=True,side_effect=lambda _:json.dumps(budget)):
                mod.rows(fake_plan())
    def test_no_mvs_readback_submission_in_plan(self):
        content=SCRIPT.read_text()
        self.assertNotIn('TA2RC2RB JOB',content)
        self.assertNotIn("'hetinit'",content)
        self.assertNotIn("'tape','mount'",content)
        self.assertNotIn("'--run'",content)
    def test_readonly_mvs_preflight_checks_sources_and_target(self):
        s=SCRIPT.read_text()
        self.assertIn('core.stat_deck(config,names+sources)',s)
        self.assertIn('core.dataset_missing(report',s)
        self.assertIn('target.vtoc_observation(vrept,volume,names)',s)
        self.assertIn('producer.check_docker(folder)',s)

if __name__=='__main__':unittest.main()
