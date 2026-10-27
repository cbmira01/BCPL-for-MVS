from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).with_name('check-q1-obtain-evidence.py')
s=importlib.util.spec_from_file_location('ob_ev',p)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def summary():
    steps=['ASMWR','LKWR','ASMA','ASMN','ASMR','ASMQ','ASMG','LKED','WGO','GO']
    body='\n'.join(f'{x:<10} PGM=*.DD RC={8 if x=="GO" else 0:04}' for x in steps)
    return 'JOB 9999  Q13DD\n'+body+'\nStatements flagged: 0\nHighest severity: 0\n'

def sample():
    rows=['AUTHORIZATION CODE IS 00']
    for i in range(3):
        name=f'SYS26300.T191241.RA000.Q13DD.Q1H{i:02d}'.ljust(44)
        volume=f'WORK0{i+1}'.ljust(30)
        data=bytearray(96)
        data[38]=0x40
        data[40]=0x80
        data[42:44]=(1024).to_bytes(2,'big')
        data[44:46]=(1024).to_bytes(2,'big')
        fields={
         'Q1I:Q%02d:RC='%i:'00000000',
         'Q1I:Q%02d:NM0='%i:name[:22].encode('cp037').hex().upper(),
         'Q1I:Q%02d:NM1='%i:name[22:].encode('cp037').hex().upper(),
         'Q1I:Q%02d:VOL='%i:volume.encode('cp037').hex().upper(),
         'Q1I:Q%02d:MET='%i:'010000000000',
         'Q1O:Q%02d:RC='%i:'00000000',
         'Q1O:Q%02d:DS0='%i:data[:48].hex().upper(),
         'Q1O:Q%02d:DS1='%i:data[48:].hex().upper()}
        rows += [k+v for k,v in fields.items()]
    return '\n'.join(rows)+'\n'

class ObtainEvidenceTest(unittest.TestCase):
    def test_three_raw_dscbs_extracted(self):
        ok,values,errors=m.review(sample(),summary())
        self.assertTrue(ok,errors)
        self.assertEqual(len(values),3)
        self.assertEqual(values['Q00']['candidate_lrecl'],1024)
        self.assertEqual(values['Q00']['candidate_blksize'],1024)
    def test_missing_or_bad_return_fails(self):
        text=sample()
        self.assertFalse(m.review(text.replace('Q1O:Q00:RC=00000000','Q1O:Q00:RC=00000008'),summary())[0])
        self.assertFalse(m.review(text.replace('Q1O:Q01:DS1=','Q1O:Q01:MISSING='),summary())[0])
        self.assertFalse(m.review(text.replace('Q1I:Q02:MET=010000000000','Q1I:Q02:MET=020000000000'),summary())[0])
        self.assertFalse(m.review(text.replace('AUTHORIZATION CODE IS','BAD SOURCE'),summary())[0])
    def test_concatenated_diagnostic_records_fail(self):
        text=sample().replace('Q1I:Q00:RC=00000000\n',
                              'Q1I:Q00:RC=00000000')
        ok, _, issues=m.review(text, summary())
        self.assertFalse(ok)
        self.assertTrue(any('multiple diagnostic fields' in x for x in issues))

    def test_skip_and_duplicate_fail(self):
        self.assertFalse(m.review(sample()+'Q1O:Q00:SKIP\n',summary())[0])
        self.assertFalse(m.review(sample()+'Q1O:Q01:RC=00000000\n',summary())[0])

if __name__=='__main__':unittest.main()
