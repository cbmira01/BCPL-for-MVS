"""Fail-closed tests for single-job finalizer WTO observations."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).with_name('check-q1-finalizer-diagnostic.py')
s=importlib.util.spec_from_file_location('q1fd_evidence',p)
assert s and s.loader
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)


def fixture():
    steps='\n'.join(f'{n:<10} IFOX00 RC=0000' for n in sorted(m.STEPS))
    summary='JOB 7777  Q1FDIAG\n'+steps+'\nJOB RESULT: SUCCESS\nAssembler:\n  Statements flagged: 0\n  Highest severity: 0\n'
    report='LISTING: BCPLQSAM Q1 16 FINISH PASS\nAUTHORIZATION CODE IS 00000000\nBCPLQSAM Q1 16 FINISH PASS\n'
    console=('4000  1.02.03 JOB 7777  IEF403I Q1FDIAG - STARTED - TIME=01.02.03\n'
             'FFFF  1.02.03 JOB 7777  +Q1F:E:00000000:00000010:00000010:00000010\n'
             'FFFF  1.02.03 JOB 7777  +Q1F:L:00000010:00000000:00000000:00000000:00000000\n'
             'FFFF  1.02.03 JOB 7777  +Q1F:X:00000010:00000000:00000000:00000000:00000000\n'
             '4000  1.02.04 JOB 7777  IEF404I Q1FDIAG - ENDED - TIME=01.02.04\n')
    return summary,report,console


class EvidenceTests(unittest.TestCase):
    def test_valid_triplet(self):
        self.assertEqual(m.review(*fixture()),(True,[]))

    def test_wrong_count_or_status(self):
        s,r,c=fixture()
        for bad in (c.replace('00000010:00000000','0000000F:00000000',1),
                    c.replace(':00000000\n','::00000000\n',1),
                    c.replace('Q1F:X:00000010','Q1F:X:0000000F')):
            with self.subTest(bad=bad[:70]):
                self.assertFalse(m.review(s,r,bad)[0])

    def test_wrong_order_duplicate_and_missing_phase(self):
        s,r,c=fixture()
        a=c.splitlines(keepends=True)
        for bad in (''.join(a[:1]+a[2:3]+a[1:2]+a[3:]),
                    ''.join(a[:3]+a[3:4]+a[3:]),
                    ''.join(a[:2]+a[3:])):
            self.assertFalse(m.review(s,r,bad)[0])

    def test_unrelated_job_and_listing_only(self):
        s,r,c=fixture()
        self.assertFalse(m.review(s,r,c.replace('JOB 7777  +Q1F:', 'JOB 8888  +Q1F:'))[0])
        self.assertFalse(m.review(s,r,c.replace('FFFF  1.02.03 JOB 7777  +Q1F:','000ABC  DC    C\'Q1F:'))[0])
        self.assertFalse(m.review(s,r,c+c)[0])

    def test_bad_native_proof_and_abend(self):
        s,r,c=fixture()
        self.assertFalse(m.review(s.replace('RC=0000','RC=0008',1),r,c)[0])
        self.assertFalse(m.review(s.replace('Highest severity: 0','Highest severity: 4'),r,c)[0])
        self.assertFalse(m.review(s,r.replace('AUTHORIZATION CODE IS 00000000','X'),c)[0])
        self.assertFalse(m.review(s,r,c.replace('Q1F:L:','IEF450I Q1FDIAG GO - ABEND S322\nQ1F:L:'))[0])

if __name__=='__main__':unittest.main()
