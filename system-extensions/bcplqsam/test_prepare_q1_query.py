"""Offline validations for Q.1 QUERY-only native integration preparer."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'q1_query_generator', HERE / 'prepare-q1-query.py')
assert SPEC is not None and SPEC.loader is not None
QUERY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QUERY)


class NativeQueryTest(unittest.TestCase):
    def make(self):
        helper = QUERY.time_helper().trailer_helper()
        return QUERY.make_deck(
            helper.sample_generated(),
            ["//Q1QUERY JOB (BCPL),'Q1 OFFLINE',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')

    def test_temp_native_integration_steps(self):
        deck = self.make()
        cards = deck.splitlines()
        self.assertEqual(cards.count('/*'), 6)
        for step in ('ASMA', 'ASMN', 'ASMR', 'ASMQ', 'ASMG', 'LKED',
                     'GO'):
            self.assertEqual(sum(c.startswith(f'//{step:<8} EXEC')
                                 for c in cards), 1, step)
        self.assertEqual(cards.count('         BCXREQ BCPLQSAM'), 1)
        self.assertIn(' ENTRY R0APP', cards)
        self.assertIn(' NAME Q1QUERY(R)', cards)
        self.assertIn('//QSMOBJ   DD  DSN=&&Q1QSOBJ,DISP=(OLD,PASS)',
                      cards)
        self.assertIn('PARM=\'NCAL,LIST,XREF,MAP\',', deck)
        self.assertIn('PGM=*.LKED.SYSLMOD,REGION=256K,', deck)
        self.assertNotIn('//Q00', deck)
        self.assertNotIn('//Q01', deck)
        self.assertIn('INCLUDE OBJ(BLIB)', deck)
        self.assertIn('SYS1.MACLIB,DISP=SHR', deck)
        for unsafe in ('DISP=MOD', 'CATLG', '//EXTLIB'):
            self.assertNotIn(unsafe, deck)
        # The accepted BCPLMAIN source may *comment* on BOOT_DEVOBJ.
        # Prohibit actual JCL references, not source commentary.
        self.assertFalse(any('BOOT_DEVOBJ' in row and
                             row.startswith('//') for row in cards))
        for row in cards:
            self.assertTrue(row.isascii())
            self.assertLessEqual(len(row), 71)

    def test_required_bcxreq_card_missing_or_duplicated(self):
        """Reject missing/duplicated real fixed-column selection cards."""
        t0 = QUERY.time_helper()
        read_cards = t0.read_cards
        for copies in (0, 2):
            with self.subTest(selection_copies=copies):
                def altered_cards(helper, path):
                    rows = read_cards(helper, path)
                    if path.name == 'q1-selection.asm':
                        original = '         BCXREQ BCPLQSAM'
                        self.assertEqual(rows.count(original), 1)
                        rows = [r for r in rows if r != original]
                        rows.extend([original] * copies)
                    return rows
                with (patch.object(QUERY, 'time_helper', return_value=t0),
                      patch.object(t0, 'read_cards',
                                   side_effect=altered_cards)):
                    with self.assertRaisesRegex(ValueError,
                                                'BCPLQSAM requirement'):
                        self.make()

    def test_no_query_of_or_open_of_qsam_dcb(self):
        src = (HERE / 'test-q1-query.bcpl').read_text('ascii')
        self.assertIn('QSAMSVC:200', src)
        self.assertIn('QSAMSVC(0,0,0)', src)
        self.assertIn('BCPLQSAM Q1 QUERY PASS', src)
        for opcode in ('1', '4', '5'):
            self.assertNotIn(f'QSAMSVC({opcode},', src)
        self.assertLessEqual(max(map(len, src.splitlines())), 80)
        self.assertEqual((HERE / 'expected-q1-query.txt').read_text(),
                         'BCPLQSAM Q1 QUERY PASS\n')

    def test_reject_wrong_job_and_object_name(self):
        helper = QUERY.time_helper().trailer_helper()
        sample = helper.sample_generated()
        with self.assertRaisesRegex(ValueError, 'Q1QUERY'):
            QUERY.make_deck(sample, ["//WRONG JOB X"], 'HERC02.BCPL.BOOT.OBJ')
        with self.assertRaisesRegex(ValueError, 'BOOT_OBJ'):
            QUERY.make_deck(
                sample, ["//Q1QUERY JOB (BCPL),'Q1',CLASS=A"], 'BAD-DSN')

    def test_wsl_commands_no_failfast_and_single_inspection(self):
        doc = (HERE / 'q1-query-runbook.md').read_text('utf-8')
        blocks = re.findall(r'```bash\n(.*?)\n```',
                            doc, re.S)
        self.assertEqual(len(blocks), 3)
        for block in blocks:
            self.assertTrue(block.startswith(
                'set +e\nset +u\nset +o pipefail\n'))
            self.assertNotRegex(block, r'(?m)^\s*set\s+-')
            self.assertNotRegex(block, r'(?m)^\s*exit\b')
            check = subprocess.run(
                ['bash', '-n'], input=block, text=True,
                capture_output=True, check=False)
            self.assertEqual(check.returncode, 0, check.stderr)
        self.assertNotIn('for attempt in', blocks[2])
        self.assertIn('python3 tools/mvs/job-summary', blocks[2])
        self.assertIn('timeout -k 2s 15s', blocks[2])


if __name__ == '__main__':
    unittest.main()
