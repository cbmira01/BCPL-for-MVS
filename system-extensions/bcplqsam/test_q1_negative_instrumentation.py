"""Guard test-only negative caller expected statuses and bounded diagnostics."""
from __future__ import annotations
from pathlib import Path
import re
import unittest

SRC=Path(__file__).with_name('test-q1-negative.bcpl')
EXPECT=[('1','-4'),('1','-4'),('1','-5'),
        ('1','-3'),('1','-3'),('4','-7'),('5','-7')]


class NativeNegativeCaller(unittest.TestCase):
    def test_seven_requests_and_original_error_contract(self):
        src=SRC.read_text(encoding='ascii')
        matched=re.findall(r'RC := QSAMSVC\((\d+),Q,R\)\s*'
                           r'IF RC NE (-?\d+) DO Q1NEGFAIL\((\d+),RC\)',src)
        self.assertEqual([(op,expect) for op,expect,_ in matched],EXPECT)
        self.assertEqual([int(n) for _,_,n in matched],list(range(1,8)))
        self.assertEqual(src.count('QSAMSVC('),7)

    def test_failure_is_printed_once_before_stop(self):
        src=SRC.read_text(encoding='ascii')
        self.assertIn('WRITEF:76;',src)
        self.assertIn('WRITEF("BCPLQSAM Q1 NEGATIVE FAIL %N RC=%N", N, RC)',src)
        self.assertIn('LET Q1NEGFAIL(N, RC) BE',src)
        begin=src.index('LET Q1NEGFAIL(N, RC) BE')
        end=src.index('LET START() BE')
        helper=src[begin:end]
        self.assertIn('NEWLINE()',helper)
        self.assertEqual(helper.count('STOP(8)'),1)
        self.assertEqual(src.count('STOP(8)'),1)
        self.assertIn('WRITES("BCPLQSAM Q1 NEGATIVE PASS")',src)
        self.assertTrue(src.rstrip().endswith('$)1'))

    def test_no_added_io_or_permanent_actions(self):
        src=SRC.read_text(encoding='ascii')
        for text in ('GETREC','PUTREC','OBTAIN','OPEN(', 'CLOSE(', 'GETMAIN', 'submit'):
            self.assertNotIn(text,src)


if __name__=='__main__':unittest.main()
