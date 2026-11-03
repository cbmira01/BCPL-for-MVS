"""Offline tests for the disposable Q.1 IFOX+IEWL linkage job."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('q1_link', HERE / 'prepare-q1-link.py')
assert SPEC is not None and SPEC.loader is not None
LINK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINK)


class Q1LinkTest(unittest.TestCase):
    def make(self):
        return LINK.make_deck(["//Q1QSLNK JOB (BCPL),'Q1 CHECK',CLASS=A"])

    def test_single_ifox_and_iewl_only(self):
        deck = self.make()
        lines = deck.splitlines()
        self.assertEqual(lines.count('/*'), 2)
        self.assertEqual(lines.count('//SYSIN    DD  *'), 1)
        self.assertEqual(lines.count(' ENTRY QSMBEG'), 1)
        self.assertEqual(lines.count(' NAME Q1QSAM(R)'), 1)
        self.assertIn('//LKED     EXEC PGM=IEWL,REGION=256K,', lines)
        self.assertIn('COND=(0,NE,ASMQ)', deck)
        self.assertIn('DSN=&&Q1QSOBJ,DISP=(OLD,DELETE)', deck)
        self.assertIn('SPACE=(80,(300,100)),DISP=(NEW,PASS)', deck)
        self.assertIn('DSN=&&Q1LOAD(Q1QSAM),UNIT=SYSDA,', deck)
        self.assertIn('SPACE=(1024,(50,20,1)),DISP=(NEW,DELETE)', deck)
        self.assertIn('QSMBEG   DS    0F', deck)
        self.assertIn('QSMFIN   CSECT', deck)
        for unsafe in ('//GO ', 'CATLG', 'DISP=MOD', 'BOOT_OBJ',
                       'BOOT_DEVOBJ', '//EXTLIB'):
            self.assertNotIn(unsafe, deck)
        for line in lines:
            self.assertTrue(line.isascii())
            self.assertLessEqual(len(line), 71)

    def test_wrong_jobcard_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Q1QSLNK'):
            LINK.make_deck(["//Q1QSASM JOB (BCPL),'INVALID',CLASS=A"])

    def test_no_source_mutation_and_protected_jcl(self):
        source = HERE / 'bcplqsam.asm'
        baseline = source.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            with (patch.object(LINK, 'WORK', Path(tmp)),
                  patch.object(LINK, 'local_job_card',
                               return_value=[
                                  "//Q1QSLNK JOB (BCPL),'Q1 CHECK',CLASS=A"
                               ]),
                  patch('sys.argv', ['prepare-q1-link.py', '--prepare'])):
                LINK.main()
            path = Path(tmp) / 'q1link.jcl'
            self.assertTrue(path.is_file())
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIn('//LKED     EXEC', path.read_text())
        self.assertEqual(source.read_bytes(), baseline)

    def test_offline_runbook_no_polling_or_failfast(self):
        readme = (HERE / 'README.md').read_text(encoding='utf-8')
        blocks = re.findall(r'```bash\n(.*?)\n```', readme, re.S)
        self.assertGreaterEqual(len(blocks), 3)
        for block in blocks:
            self.assertTrue(block.startswith('set +e\nset +u\nset +o pipefail\n'))
            self.assertNotRegex(block, r'(?m)^\s*set\s+-')
            self.assertNotRegex(block, r'(?m)^\s*exit\b')
        self.assertNotIn('for attempt in', blocks[-1])


if __name__ == '__main__':
    unittest.main()
