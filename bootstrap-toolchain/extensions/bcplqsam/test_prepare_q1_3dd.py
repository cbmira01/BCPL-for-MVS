"""Offline contracts for temporary Q.1 native three-DD OPEN/INFO/CLOSE."""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'q1_three_gate', HERE / 'prepare-q1-3dd.py')
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class Q1ThreeDDTest(unittest.TestCase):
    def make(self):
        helper = GATE.query_helper().time_helper().trailer_helper()
        return GATE.make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'Q1 CHECK',CLASS=A"],
            'HERC02.BCPL.BOOT.OBJ')

    def test_full_temporary_writer_native_pipeline(self):
        rows = self.make().splitlines()
        self.assertEqual(rows.count('/*'), 8)
        self.assertEqual(rows.count('//SYSIN    DD  *'), 6)
        steps = ('ASMWR', 'LKWR', 'ASMA', 'ASMN', 'ASMR',
                 'ASMQ', 'ASMG', 'LKED', 'WGO', 'GO')
        indices = []
        for step in steps:
            matches = [i for i, row in enumerate(rows)
                       if row.startswith(f'//{step:<8} EXEC')]
            self.assertEqual(len(matches), 1, step)
            indices.append(matches[0])
        self.assertEqual(indices, sorted(indices))
        self.assertEqual(rows.count('         BCXREQ BCPLQSAM'), 1)
        self.assertEqual(rows.count(' ENTRY R0APP'), 1)
        self.assertEqual(rows.count(' ENTRY Q0HNW'), 1)
        self.assertIn('//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,', rows)
        self.assertIn('//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,', rows)
        self.assertIn(' NAME Q13DD(R)', rows)
        self.assertIn('         BCXREQ BCPLQSAM', rows)
        self.assertIn('//             TIME=(,2),COND=((0,NE,LKED),(0,NE,WGO))',rows)
        for i in range(3):
            self.assertEqual(rows.count(
                f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(NEW,PASS),'), 1)
            self.assertEqual(rows.count(
                f'//Q{i:02d}      DD  DSN=&&Q1H{i:02d},DISP=(OLD,DELETE)'), 1)
        self.assertTrue(all(len(c) <= 71 and c.isascii() for c in rows))
        for bad in ('CATLG', 'DISP=MOD', '//EXTLIB', 'BOOT_DEVOBJ'):
            if bad == 'BOOT_DEVOBJ':
                self.assertFalse(any(c.startswith('//') and bad in c
                                     for c in rows))
            else:
                self.assertNotIn(bad, '\n'.join(rows))

    def test_bcpl_caller_is_three_dd_only(self):
        src = (HERE / 'test-q1-3dd.bcpl').read_text('ascii')
        self.assertEqual(src.count('QSAMSVC(1,Q,R)'), 3)
        self.assertEqual(src.count('QSAMSVC(5,Q,R)'), 1)
        self.assertEqual(src.count('QSAMSVC(4,Q,R)'), 4)
        self.assertIn('QSAMSVC:200', src)
        self.assertNotIn('QSAMSVC(2,Q,R)', src)
        self.assertNotIn('QSAMSVC(3,Q,R)', src)
        self.assertLessEqual(max(map(len, src.splitlines())), 80)
        self.assertEqual((HERE / 'expected-q1-3dd.txt').read_text(),
                         'BCPLQSAM Q1 THREE DD PASS\n')

    def test_multi_card_authenticated_job_header_preserved(self):
        helper = GATE.query_helper().time_helper().trailer_helper()
        cards = GATE.make_deck(
            helper.sample_generated(),
            ["//Q13DD JOB (BCPL),'Q1 CHECK',CLASS=A,",
             "//             MSGCLASS=A"],
            'HERC02.BCPL.BOOT.OBJ').splitlines()
        self.assertEqual(cards[1], '//             MSGCLASS=A')
        self.assertTrue(cards[2].startswith('//* Q.1 THREE INPUT DDs'))

    def test_job_card_rejection(self):
        sample = GATE.query_helper().time_helper().trailer_helper().sample_generated()
        with self.assertRaisesRegex(ValueError, 'Q13DD'):
            GATE.make_deck(sample, ["//WRONG JOB X"], 'HERC02.BCPL.BOOT.OBJ')

    def test_no_files_in_check_and_protected_jcl(self):
        sample = GATE.query_helper().time_helper().trailer_helper().sample_generated()
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            file = work / 'generated.asm'
            file.write_text(sample, encoding='ascii')
            with (patch.object(GATE, 'WORK', work),
                  patch.object(GATE, 'local_job_card', create=True,
                               return_value=[])):
                deck = self.make()
                self.assertNotIn('DISP=MOD', deck)
                self.assertFalse((work / 'q13dd.jcl').exists())

    def test_wsl_runbook_no_failfast_or_polling(self):
        readme = (HERE / 'q1-three-runbook.md').read_text('utf-8')
        blocks = re.findall(r'```bash\n(.*?)\n```',
                            readme, re.S)
        self.assertEqual(len(blocks), 3)
        for block in blocks:
            self.assertTrue(block.startswith('set +e\nset +u\nset +o pipefail\n'))
            self.assertNotRegex(block, r'(?m)^\s*set\s+-')
            self.assertNotRegex(block, r'(?m)^\s*exit\b')
            parsed = subprocess.run(
                ['bash', '-n'], input=block,
                capture_output=True, text=True, check=False)
            self.assertEqual(parsed.returncode, 0, parsed.stderr)
        self.assertNotIn('for attempt in', blocks[2])
        self.assertIn('python3 tools/mvs/job-summary', blocks[2])
        self.assertIn('timeout -k 2s 15s', blocks[2])


if __name__ == '__main__':
    unittest.main()
