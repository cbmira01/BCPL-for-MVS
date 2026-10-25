"""Offline-only tests: Q.1 IFOX job generator safety and basic structure."""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
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


    def test_wsl_runbook_uses_python_and_bounded_one_shot_reporting(self):
        """Documented operator blocks must not exit WSL or call Python with Bash."""
        readme = (HERE / 'README.md').read_text(encoding='utf-8')
        blocks = re.findall(r'```bash\n(.*?)\n```', readme, re.S)
        self.assertEqual(len(blocks), 3)
        for index, script in enumerate(blocks, 1):
            self.assertTrue(script.startswith(
                'set +e\nset +u\nset +o pipefail\n'), index)
            self.assertNotRegex(script, r'(?m)^\s*set\s+-')
            self.assertNotRegex(script, r'(?m)^\s*exit\b')
            syntax = subprocess.run(
                ['bash', '-n'], input=script, text=True,
                capture_output=True, check=False)
            self.assertEqual(syntax.returncode, 0, syntax.stderr)
        report = blocks[2]
        self.assertIn('python3 tools/mvs/job-summary', report)
        self.assertNotIn('bash tools/mvs/job-summary', report)
        self.assertIn('timeout -k 2s 15s', report)
        self.assertNotIn('for attempt in', report)
        self.assertEqual(report.count('python3 tools/mvs/job-summary'), 1)


if __name__ == '__main__':
    unittest.main()
