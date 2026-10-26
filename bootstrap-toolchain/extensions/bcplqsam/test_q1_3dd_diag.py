"""Offline checks for the diagnostic-only Q.1 native three-DD caller."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import unittest

HERE = Path(__file__).resolve().parent


class Q13DDDiagnosticTest(unittest.TestCase):
    def test_diagnostic_preserves_original_calls_and_assertions(self):
        original = (HERE / 'test-q1-3dd.bcpl').read_text('ascii')
        diagnostic = (HERE / 'test-q1-3dd-diag.bcpl').read_text('ascii')
        original_calls = re.findall(
            r'IF QSAMSVC\(([^)]*)\) NE (-?\d+) DO STOP\(8\)',
            original)
        diag_calls = re.findall(
            r'S := QSAMSVC\(([^)]*)\)', diagnostic)
        diag_goals = re.findall(
            r'IF S NE (-?\d+) DO STOP\(8\)', diagnostic)
        self.assertEqual(len(original_calls), 14)
        self.assertEqual(diag_calls, [call for call, _ in original_calls])
        self.assertEqual(diag_goals, [goal for _, goal in original_calls])
        self.assertEqual(diagnostic.count('STOP(8)'),
                         original.count('STOP(8)'))
        self.assertEqual(
            diagnostic.count('WRITES("Q13D CALL '), 22)
        self.assertEqual(diagnostic.count(' BEFORE")'), 5)
        self.assertIn('WRITEN:62', diagnostic)
        self.assertIn('WRITES("Q13D START")', diagnostic)
        self.assertIn('BCPLQSAM Q1 THREE DD PASS', diagnostic)
        self.assertEqual(diagnostic.count('FINISH'), original.count('FINISH'))
        self.assertLessEqual(max(map(len, diagnostic.splitlines())), 80)
        self.assertFalse(any('QSAMSVC(2,Q,R)' in l or
                             'QSAMSVC(3,Q,R)' in l
                             for l in diagnostic.splitlines()))
        self.assertEqual(original.count('LET Q = VEC 3'), 1)
        self.assertEqual(original.count('LET R = VEC 7'), 1)
        self.assertIn('LET Q = VEC 3', diagnostic)
        self.assertIn('LET R = VEC 7', diagnostic)
        self.assertEqual(diagnostic.count('Q!0 := "Q0'), 3)

    def test_six_word_query_dump_before_failed_assertion(self):
        source = (HERE / 'test-q1-3dd-diag.bcpl').read_text('ascii')
        self.assertIn('LET I = VEC 5', source)
        dump_start = source.index('WRITES("Q13D QUERY I0/I1/I2=")')
        dump_end = source.index('WRITES("Q13D ASSERT 02 BEFORE")')
        dump = source[dump_start:dump_end]
        self.assertEqual(
            re.findall(r'WRITEN\(I!(\d)\)', dump),
            ['0', '1', '2', '3', '4', '5'])
        self.assertIn('WRITES("Q13D QUERY I3/I4/I5=")', dump)
        after = source.index('WRITES("Q13D ASSERT 02 AFTER")')
        condition = source.index(
            'IF I!0 NE 1 | I!1 NE 1 | I!2 NE 0 DO STOP(8)')
        self.assertLess(dump_end, condition)
        self.assertLess(condition, after)
        self.assertIn('Q13D ASSERT 03 BEFORE', source[after:])

    def test_diagnostic_requires_no_new_jcl_or_permanent_writes(self):
        run = (HERE / 'q1-three-diagnostic-runbook.md').read_text('utf-8')
        self.assertIn('prepare-q1-3dd.py', run)
        self.assertIn('test-q1-3dd-diag.bcpl', run)
        self.assertIn('q13dd-diag-last-job.txt', run)
        self.assertIn('Q13DCMP', run)
        self.assertIn('REGION=256K', run)
        self.assertNotIn('BOOT_DEVOBJ)', run)
        self.assertNotIn('CATLG', run)
        self.assertNotIn('DISP=MOD', run)

    def test_three_wsl_blocks_preserve_interactive_shell(self):
        run = (HERE / 'q1-three-diagnostic-runbook.md').read_text('utf-8')
        blocks = re.findall(r'```bash\n(.*?)\n```',
                            run, re.S)
        self.assertEqual(len(blocks), 3)
        for number, block in enumerate(blocks, 1):
            self.assertTrue(block.startswith(
                'set +e\nset +u\nset +o pipefail\n'), number)
            self.assertNotRegex(block, r'(?m)^\s*set\s+-')
            self.assertNotRegex(block, r'(?m)^\s*exit\b')
            syntax = subprocess.run(['bash', '-n'], input=block,
                                    text=True, capture_output=True,
                                    check=False)
            self.assertEqual(syntax.returncode, 0, syntax.stderr)
        self.assertNotIn('for attempt in', blocks[2])
        self.assertIn('python3 tools/mvs/job-summary', blocks[2])
        self.assertIn('timeout -k 2s 15s', blocks[2])
        self.assertIn('Q13D', blocks[2])


if __name__ == '__main__':
    unittest.main()
