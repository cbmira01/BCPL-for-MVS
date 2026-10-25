"""Offline-only tests: Q.1 IFOX job generator safety and basic structure."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('q1prepare', HERE / 'prepare-q1-asm.py')
assert SPEC is not None and SPEC.loader is not None
PREP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREP)


class PrepareQ1ASMTest(unittest.TestCase):
    def test_single_asm_temporary_only(self):
        deck = PREP.build(["//Q1QSASM JOB (BCPL),'Q1 CHECK',CLASS=A"])
        self.assertEqual(deck.count('//SYSIN    DD  *'), 1)
        self.assertEqual(deck.splitlines().count('/*'), 1)
        self.assertIn('//* Q.1 IFOX ONLY', deck)
        self.assertIn('         ENTRY QSMFIN', deck)
        self.assertIn('//SYSGO    DD  DSN=&&Q1QSOBJ,UNIT=SYSDA,', deck)
        self.assertIn('DISP=(NEW,DELETE)', deck)
        for unsafe in ('CATLG', 'DISP=MOD', 'BOOT_OBJ', 'BOOT_DEVOBJ',
                       'EXT_OBJ', 'IEBCOPY', 'IEFBR14', '//GO '):
            self.assertNotIn(unsafe, deck)

    def test_unsupported_job_name(self):
        with self.assertRaisesRegex(ValueError, 'Q1QSASM'):
            PREP.build(["//WRONG JOB (BCPL),'BAD',CLASS=A"])

    def test_preparer_protected_local_file_no_submission(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            with (patch.object(PREP, 'WORK', path),
                  patch.object(PREP, 'local_job_card', return_value=[
                      "//Q1QSASM JOB (BCPL),'Q1 CHECK',CLASS=A"]),
                  patch('sys.argv', ['prepare-q1-asm.py', '--prepare'])):
                PREP.main()
            output = path / 'q1asm.jcl'
            self.assertTrue(output.is_file())
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertIn('         END\n/*\n//', output.read_text())


if __name__ == '__main__':
    unittest.main()
