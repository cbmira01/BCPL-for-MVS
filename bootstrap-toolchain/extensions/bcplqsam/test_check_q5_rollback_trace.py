"""Pure offline tests for six-marker Q5RBTRC evidence acceptance."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).with_name('check-q5-rollback-trace.py')
spec = importlib.util.spec_from_file_location('q5_trace_evidence', path)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

JOB = 8889
SUMMARY = (
    'JOB 8889  Q5RBTRC\n\nSTEP       PROGRAM      RESULT\n'
    + ''.join(f'{s:<10} {"IFOX00":<12} RC=0000\n' for s in checker.STEPS)
    + '\nJOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
    + 'Assembler:\n  Statements flagged: 0\n  Highest severity:   0\n'
)
REPORT = 'BCPLQSAM Q5 OPEN ROLLBACK PASS\n'
CONSOLE = (
    '00:00 JOB 8889 $HASP373 Q5RBTRC STARTED\n'
    '00:01 JOB 8889 +Q5R:E:00000001:00000002:00000002:00000001\n'
    '00:02 JOB 8889 +Q5R:L:00000001:00000001:00000001:00000001:00000000\n'
    '00:03 JOB 8889 +Q5R:P:POST-CLEAN\n'
    '00:04 JOB 8889 +Q5R:R:ROLL-RETURN\n'
    '00:05 JOB 8889 +Q5R:T:CORE-EPILOGUE\n'
    '00:06 JOB 8889 +Q5R:X:00000000:00000000:00000000:00000000:00000000\n'
    '00:07 JOB 8889 $HASP395 Q5RBTRC ENDED\n'
)

class TraceCheck(unittest.TestCase):
    def test_success(self):
        self.assertEqual(checker.check(JOB, SUMMARY, REPORT, CONSOLE), [])

    def test_partial_after_rollback(self):
        partial = '\n'.join(line for line in CONSOLE.splitlines()
                            if '+Q5R:P:' not in line and '+Q5R:R:' not in line
                            and '+Q5R:T:' not in line and '+Q5R:X:' not in line)
        self.assertTrue(checker.check(JOB, SUMMARY, REPORT, partial))

    def test_missing_go(self):
        self.assertTrue(checker.check(JOB,
            SUMMARY.replace('GO         IFOX00       RC=0000\n', ''),
            REPORT, CONSOLE))

    def test_wrong_job(self):
        self.assertTrue(checker.check(JOB, SUMMARY, REPORT,
            CONSOLE.replace('JOB 8889 +Q5R:R:', 'JOB 9999 +Q5R:R:')))

    def test_duplicate_probe(self):
        extra = '00:05 JOB 8889 +Q5R:T:CORE-EPILOGUE\n'
        self.assertTrue(checker.check(JOB, SUMMARY, REPORT,
            CONSOLE.replace('00:07 JOB', extra + '00:07 JOB')))

    def test_bad_counter(self):
        self.assertTrue(checker.check(JOB, SUMMARY, REPORT,
            CONSOLE.replace('00000002:00000002:00000001',
                            '00000002:00000002:00000002', 1)))

    def test_bad_order(self):
        rows = CONSOLE.splitlines()
        rows[2], rows[3] = rows[3], rows[2]
        self.assertTrue(checker.check(JOB, SUMMARY, REPORT, '\n'.join(rows)))

    def test_missing_success_record(self):
        self.assertTrue(checker.check(JOB, SUMMARY, '', CONSOLE))

if __name__ == '__main__':
    unittest.main()
