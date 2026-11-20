"""Synthetic offline checks for the rc2 add-on selective staging JCL."""
import importlib.util
from pathlib import Path
import unittest
from test_successor_contract import TestSuccessor

ROOT=Path(__file__).resolve().parents[4]
CODE=ROOT/'packaging/distribution/compiler-source/rc2-stage-draft.py'
spec=importlib.util.spec_from_file_location('rc2_stage_draft',CODE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class TestDraft(unittest.TestCase):
    def setUp(self):
        data=TestSuccessor();data.setUp()
        self.manifest=data.rc2
        self.dspal=data.dspal
        self.dspal['mvs']={'hlq':'HERC02'}
    def render(self):return mod.render(self.manifest,self.dspal,volume='TSO002')
    def test_exact_two_step_jcl(self):
        text=self.render()
        self.assertEqual(text.count(' EXEC PGM=IEBCOPY'),2)
        self.assertEqual(text.count(' SELECT MEMBER='),30)
        self.assertEqual(text.count('DISP=(NEW,CATLG,DELETE)'),2)
        self.assertIn('HERC02.BCPL.TA2STG.BT0021',text)
        self.assertIn('HERC02.BCPL.TA2STG.BT0022',text)
        self.assertNotIn('TA2STG.BT0020',text)
        self.assertNotIn('LABEL=(',text)
    def test_jcl_columns(self):
        lines=self.render().splitlines()
        self.assertTrue(all(len(v)<=80 for v in lines))
        self.assertTrue(all(len(v)<=71 for v in lines if v.startswith('//') and not v.startswith('//*')))
    def test_exact_member_selection(self):
        text=self.render()
        self.assertEqual(text.count(' SELECT MEMBER=(SNOTICE)'),1)
        self.assertEqual(text.count(' SELECT MEMBER=(CGA)'),1)
        self.assertEqual(text.count(' SELECT MEMBER=(CG)'),1)
        self.assertEqual(text.count(' SELECT MEMBER=(BCPL)'),2)
    def test_reject_foreign_volume(self):
        self.assertRaises(mod.Refusal,mod.render,self.manifest,self.dspal,volume='TSO003')
    def test_reject_unknown_source(self):
        self.dspal['datasets']['CAMB_DEMOTED']['generated_members'].pop('CGE')
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_wrong_source_identity(self):
        self.manifest['release']['native_compiler']='included'
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_overfull_mvs_member(self):
        self.manifest['datasets'][-1]['members'].append('LONGNAME9')
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_nonhistorical_member(self):
        self.manifest['datasets'][20]['members'][0]='OTHER'
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_stage_step_gap(self):
        self.manifest['datasets'][21]['sequence']=23
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_missing_job(self):
        self.manifest['datasets'].pop()
        self.assertRaises(mod.Refusal,self.render)
    def test_reject_bad_space(self):
        self.assertRaises(mod.Refusal,mod.render,self.manifest,self.dspal,volume='TSO002',directory=0)
if __name__=='__main__':unittest.main()
