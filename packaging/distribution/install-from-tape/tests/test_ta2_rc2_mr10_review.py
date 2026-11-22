"""Synthetic negative and positive tests of the saved MVS MR10 semantic review."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/ta2-rc2-mr10-review'
loader = importlib.machinery.SourceFileLoader('ta2_review_test',str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name,loader)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def definitions():
    return [{'step':f'R{i:02d}', 'name':name, 'title':f'Case {i} {name}',
             'golden':[f'RP: A {i}',f'RP: B {i*10}'], 'expected_code':0}
            for i,name in enumerate(review.EXPECTED,1)]


def make_report(defs, add_exp=False):
    lines=['COMPILER PHASE 1 EXECUTION CYCLES = 16, CODE = 0']
    for row in defs:
        lines.append('0    TEST: '+row['title'])
        if add_exp:
            lines.extend('   '+x.replace('RP:','EXP:',1) for x in row['golden'])
        lines.extend(' '+x for x in row['golden'])
        lines.append('  EXECUTION CYCLES = 374, CODE = 0')
    return '\n'.join(lines)+'\n'

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.cases=definitions()
        self.good=make_report(self.cases)

    def test_all_12_match_no_exp_is_pending_not_release_pass(self):
        result=review.inspect(self.good,self.cases)
        self.assertEqual(result['status'],'GOLDEN_RP_CODE_MATCH_EXP_REQUIRED')
        self.assertTrue(result['golden_rp_and_code_match'])
        self.assertFalse(result['exp_contract_met'])
        self.assertEqual(result['human_signoff'],'PENDING')
        self.assertFalse(result['publication_authorized'])
        self.assertEqual(len(result['cases']),12)

    def test_full_exp_does_not_automatically_sign_off(self):
        r=review.inspect(make_report(self.cases,True),self.cases)
        self.assertEqual(r['status'],'EXP_RP_CODE_COMPARISON_PASS_HUMAN_SIGNOFF_PENDING')
        self.assertTrue(r['exp_contract_met'])
        self.assertEqual(r['human_signoff'],'PENDING')

    def test_wrong_semantic_output_fails(self):
        r=review.inspect(self.good.replace('RP: B 90','RP: B 999'),self.cases)
        self.assertEqual(r['status'],'MVS_MR10_SEMANTIC_COMPARISON_FAIL')
        self.assertFalse(r['cases'][8]['checks']['rp_matches_golden'])

    def test_wrong_interpreted_code_fails(self):
        r=review.inspect(self.good.replace('CODE = 0','CODE = 4'),self.cases)
        self.assertFalse(r['golden_rp_and_code_match'])

    def test_duplicate_code_fails(self):
        text=self.good.replace('RP: B 30','RP: B 30\nEXECUTION CYCLES = 1, CODE = 0')
        self.assertFalse(review.inspect(text,self.cases)['golden_rp_and_code_match'])

    def test_missing_code_fails(self):
        text=self.good.replace('CODE = 0','C0DE = 0')
        self.assertFalse(review.inspect(text,self.cases)['golden_rp_and_code_match'])

    def test_missing_case_fails(self):
        self.assertFalse(review.inspect(make_report(self.cases[:-1]),self.cases)['golden_rp_and_code_match'])

    def test_reordered_case_fails(self):
        swapped=self.cases[:]
        swapped[0],swapped[1]=swapped[1],swapped[0]
        self.assertFalse(review.inspect(make_report(swapped),self.cases)['golden_rp_and_code_match'])

    def test_duplicate_test_record_fails(self):
        text=self.good.replace('0    TEST: Case 5', '0    TEST: Case 4 '+self.cases[3]['name']+'\n0    TEST: Case 5')
        self.assertFalse(review.inspect(text,self.cases)['golden_rp_and_code_match'])

    def test_orphan_rp_fails(self):
        self.assertFalse(review.inspect('RP: ORPHAN\n'+self.good,self.cases)['golden_rp_and_code_match'])

    def test_invalid_exp_fails_even_when_rp_correct(self):
        text=make_report(self.cases,True).replace('EXP: B 30','EXP: B 3000')
        r=review.inspect(text,self.cases)
        self.assertEqual(r['status'],'MVS_MR10_SEMANTIC_COMPARISON_FAIL')
        self.assertTrue(r['golden_rp_and_code_match'])
        self.assertFalse(r['exp_contract_met'])

    def test_header_code_does_not_bind_to_first_test(self):
        r=review.inspect(self.good,self.cases)
        self.assertEqual(r['cases'][0]['interpreted_codes'],[0])

    def test_panel_matches_reconstructed_canonical_source_contract(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/'workarea') as base:
            root=Path(base)
            manifest=root/'manifest.tsv';jcl=root/'mrregres.jcl'
            contents=[]
            for i,row in enumerate(self.cases,1):
                s=f'sources/case{i:02d}.bcpl'; e=f'golden/case{i:02d}.expected'
                for rel, data in [(s,'LET START() BE WRITEF("TEST: '+row['title']+'*N")\n'),
                                  (e,'\n'.join(row['golden'])+'\n')]:
                    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
                contents.append('\t'.join((row['name'],'cat',s,'','',e,'0')))
            manifest.write_text('# file schema\n'+'\n'.join(contents)+'\n')
            jcl.write_text('\n'.join(f'//* EXECUTE CASE {i:02d}: {r["name"]}'
                                     for i,r in enumerate(self.cases,1)))
            with (patch.object(review,'ROOT',root),patch.object(review,'MANIFEST',manifest),
                  patch.object(review,'JCL',jcl)):
                self.assertEqual(review.panel(),self.cases)
                manifest.write_text(manifest.read_text().replace('library-scalars','typo'))
                with self.assertRaises(review.Refusal):review.panel()

    def test_write_review_evidence_sealed_under_workarea(self):
        with tempfile.TemporaryDirectory(dir=SCRIPT.parents[4]/'workarea') as base:
            d=Path(base)
            root=d/'repo';root.mkdir();output=root/'workarea';output.mkdir()
            saved=output/'old';saved.mkdir()
            with patch.object(review,'ROOT',root),patch.object(review,'OUTPUT',output):
                rec=review.inspect(self.good,self.cases)
                receipt=review.create_evidence(rec,saved,self.good)
                data=(receipt/'semantic-review.json').read_bytes()
                self.assertEqual(json.loads(data)['mvs_job'],9346)
                self.assertIn('semantic-review.json',(receipt/'SHA256SUMS').read_text())
                self.assertTrue((receipt/'SHA256SUMS').is_file())

if __name__=='__main__':
    unittest.main()
