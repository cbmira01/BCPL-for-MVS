import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).with_name('check-q5-open-rollback-evidence.py')
spec = importlib.util.spec_from_file_location('q5_evidence', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

JOB = 8888
SUM = ('JOB 8888  Q5RBOPEN\n\nSTEP       PROGRAM      RESULT\n' +
       ''.join(f'{name:<10} {"IFOX00":<12} RC=0000\n' for name in mod.STEPS) +
       '\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n' +
       'Assembler:\n  Statements flagged: 0\n  Highest severity:   0\n')
REP = 'OTHER\nBCPLQSAM Q5 OPEN ROLLBACK PASS\n'
CON = ('00:00 JOB 8888 $HASP373 Q5RBOPEN STARTED\n' +
       '00:01 JOB 8888 +Q5R:E:00000001:00000002:00000002:00000001\n' +
       '00:02 JOB 8888 +Q5R:L:00000001:00000001:00000001:00000001:00000000\n' +
       '00:03 JOB 8888 +Q5R:X:00000000:00000000:00000000:00000000:00000000\n' +
       '00:04 JOB 8888 $HASP395 Q5RBOPEN ENDED\n')

class EvidenceCheck(unittest.TestCase):
    def test_good(self):
        self.assertEqual(mod.check(JOB, SUM, REP, CON), [])

    def test_job_collision(self):
        self.assertTrue(mod.check(JOB, SUM, REP, CON.replace('JOB 8888 +Q5R:L:', 'JOB 9999 +Q5R:L:')))

    def test_close_failure(self):
        self.assertTrue(mod.check(JOB, SUM, REP, CON.replace('00000001:00000001:00000001:00000001:00000000', '00000000:00000002:00000002:00000001:FFFFFFF2')))

    def test_failing_go(self):
        self.assertTrue(mod.check(JOB, SUM.replace('HIGHEST RC: 0000', 'HIGHEST RC: 0008'), REP, CON))

    def test_missing_pass(self):
        self.assertTrue(mod.check(JOB, SUM, REP.replace(mod.PASS, 'NO PASS'), CON))

    def test_duplicate(self):
        self.assertTrue(mod.check(JOB, SUM, REP, CON+CON))

    def test_bad_order(self):
        lines=CON.splitlines()
        lines[1],lines[2]=lines[2],lines[1]
        self.assertTrue(mod.check(JOB, SUM, REP, '\n'.join(lines)))

if __name__=='__main__': unittest.main()
