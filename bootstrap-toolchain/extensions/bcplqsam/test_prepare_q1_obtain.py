"""Test-only nonopening OBTAIN instrumentation and negative anchors."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

p=Path(__file__).with_name('prepare-q1-obtain.py')
s=importlib.util.spec_from_file_location('q1_obtain',p)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

BASE=('QIDPROB  CSECT\n'
      'QIDRUN   STM   14,12,12(13)\n'
      "         C     2,=F'72'\n"+m.INSERT_AFTER+
      'QIDBACK  L     14,QIDRET\n'
      "QIDRCB   DC    C'Q1I:Q00:RC=',8C'0'\n")

class ObtainPreparationTest(unittest.TestCase):
    def test_twin_raw_48_byte_dscb_fields_and_read_only_macro(self):
        out=m.extension(BASE)
        self.assertEqual(out.count('         OBTAIN QOBLIST'),1)
        self.assertIn('QOBLIST  CAMLST SEARCH,QOBNAME,QOBVOL,QOBWORK',out)
        self.assertIn('QOBD0B   DC    C\'Q1O:Q00:DS0=\',96C\'0\'',out)
        self.assertIn('QOBD1B   DC    C\'Q1O:Q00:DS1=\',96C\'0\'',out)
        self.assertEqual(out.count('         LA    2,108'),2)
        self.assertIn("         C     2,=F'108'",out)
        self.assertNotIn("         C     2,=F'72'",out)
        self.assertIn('QOBWORK  DS    CL140',out)
        self.assertIn("QOBRCB   DC    C'Q1O:Q00:RC=',8C'0'",out)
        self.assertIn('         CLI   117(6),X\'01\'',out)
        self.assertIn("         CLC   118(6),=CL6' '",out)
        self.assertIn('QOBSKIP',out)
        self.assertIn('         BNE   QOBRET0',out)
        for line in out.splitlines():
            self.assertLessEqual(len(line),71,line)
        for forbidden in ('         OPEN  ','         SCRATCH ','         RENAME ',
                          '         PUT   ','         GET   '):
            self.assertNotIn(forbidden,m.READ_PROBE)

    def test_missing_or_duplicate_anchor_rejected(self):
        for src in ('QIDPROB  CSECT\n',BASE+BASE,
                    BASE.replace("QIDRCB   DC    C'Q1I:Q00:RC='",'X')):
            with self.subTest(src=src[:30]):
                with self.assertRaises(ValueError):m.extension(src)

    def test_instrumentation_changes_only_asmq_source_span(self):
        original='QSMCORE  CSECT\nQSMCTRL  CSECT\n'
        deck='//Q13DD JOB (BCPL),CLASS=A\n//ASMQ EXEC PGM=IFOX00\n' + original + '/*\n//GO EXEC PGM=TEST\n'
        def validated(src):
            rows=src.splitlines()
            return rows,2,4
        fake=SimpleNamespace(validate_deck=validated,PROBE_CSECT=BASE,
            instrument_asm=lambda src:src.replace('QSMCTRL  CSECT\n',BASE+'QSMCTRL  CSECT\n'),
            cards_are_valid=lambda src:src.endswith('\n') and all(len(t)<=71 for t in src.splitlines()))
        with patch.object(m,'identity_module',return_value=fake):
            generated=m.instrument_deck(deck,original)
        self.assertIn('         OBTAIN QOBLIST',generated)
        self.assertIn("         C     2,=F'108'",generated)
        self.assertEqual(generated.count('QIDPROB  CSECT'),1)
        self.assertIn('//GO EXEC PGM=TEST\n',generated)
        self.assertIn('//Q13DD JOB (BCPL),CLASS=A\n',generated)
        with patch.object(m,'identity_module',return_value=fake):
            with self.assertRaises(ValueError):
                m.instrument_deck(deck,original+'INVALID\n')

    def test_no_submit_and_output_immutable(self):
        src=p.read_text()
        self.assertNotIn('submit-jcl',src)
        self.assertNotIn('subprocess',src)
        self.assertIn('os.O_EXCL',src)
        self.assertIn('ident.validate_deck(deck)',src)
        self.assertIn('rows[left:right]!=baseline.splitlines()',src)
        self.assertIn("src.count(original)!=1",src)

if __name__=='__main__':unittest.main()
