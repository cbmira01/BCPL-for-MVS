"""Synthetic positive and fail-closed native Q5GEOM evidence tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location(
    'q5geometrychecker',Path(__file__).with_name('check-q5-geometry-evidence.py'))
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

SUMMARY=('JOB 8150  Q5GEOM\n31 OCT 26  09.00.00 - 09.00.01\n\n'
         'STEP       PROGRAM      RESULT\n'+
         ''.join(f'{n:<10} IFOX00       RC=0000\n' for n in c.STEPS)+
         '\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n\nAssembler:\n'
         '  Statements flagged: 0\n  Highest severity:   0\n')
REPORT=(c.PASS+'\n')
CONSOLE=('07:00 / 9.00 JOB 8150  $HASP373 Q5GEOM STARTED\n'
         '07:01 / 9.01 JOB 8150  +'+c.TRACE+'\n'
         '07:02 / 9.02 JOB 8150  $HASP395 Q5GEOM ENDED\n')
HARDCOPY=('4000  9.00 JOB 8150  $HASP373 Q5GEOM STARTED\n'
          'FFFF  9.01 JOB 8150  +'+c.TRACE+'\n'
          '4000  9.02 JOB 8150  $HASP395 Q5GEOM ENDED\n')


class GeometryEvidenceTests(unittest.TestCase):
    def verify(self,s=SUMMARY,r=REPORT,k=CONSOLE,h=HARDCOPY):
        return c.check(s,r,k,h)

    def test_01_exact_evidence_passes(self):
        self.assertEqual(self.verify(),[])

    def test_02_missing_bcpl_pass_fails(self):
        self.assertTrue(self.verify(r=''))

    def test_03_duplicate_bcpl_pass_fails(self):
        self.assertTrue(self.verify(r=REPORT*2))

    def test_04_wrong_job_summary_fails(self):
        self.assertTrue(self.verify(s=SUMMARY.replace('Q5GEOM','WRONGJOB')))

    def test_05_nonzero_native_go_fails(self):
        self.assertTrue(self.verify(s=SUMMARY.replace('GO         IFOX00       RC=0000',
                                                        'GO         IFOX00       RC=0008')))

    def test_06_assembler_severity_fails(self):
        self.assertTrue(self.verify(s=SUMMARY.replace('Highest severity:   0',
                                                     'Highest severity:   8')))

    def test_07_missing_console_boundaries_fails(self):
        self.assertTrue(self.verify(k=CONSOLE.replace('$HASP395','NOTENDED')))

    def test_08_wrong_hardcopy_marker_fails(self):
        self.assertTrue(self.verify(h=HARDCOPY.replace('00000001:','00000002:',1)))

    def test_09_duplicate_console_marker_fails(self):
        duplicated=CONSOLE.replace('07:02 / 9.02 JOB',
                                   '07:01 / 9.01 JOB 8150  +'+c.TRACE+'\n07:02 / 9.02 JOB')
        self.assertTrue(self.verify(k=duplicated))

    def test_10_runtime_finalizer_message_fails(self):
        self.assertTrue(self.verify(r=REPORT+'BCPLREG 2001 FINALIZER RETURNED NONZERO\n'))


if __name__=='__main__':
    unittest.main()
