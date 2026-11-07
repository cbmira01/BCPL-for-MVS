"""Offline tests for the simple reconstruction driver; no MVS or JES access."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'reconstruction/rebuild-from-source'


@unittest.skipUnless(shutil.which('script'), 'util-linux script(1) is required for PTY fixture')
class SimpleReconstructionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        destination = self.root / 'tools/reconstruction/rebuild-from-source'
        destination.parent.mkdir(parents=True)
        shutil.copyfile(SOURCE, destination)
        self.call_log = self.root / 'calls.txt'
        stub = """#!/usr/bin/env bash
printf '%s %s\\n' "${0##*/}" "$*" >> "$MOCK_LOG"
if [ "${0##*/}" = clean-workarea ]; then
    read -r answer
    [ "$answer" = DELETE ] || exit 3
fi
if [ "$1" = purgebcpl ] && [ "$2" != --show-jcl ]; then
    read -r answer
    [ "$answer" = YES ] || exit 3
fi
if [ "$1" = --with-trnilrg ]; then
    mkdir -p workarea/bootstrap-cambridge
    echo '{"trnilrg_rebuilt": true}' > workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
fi
if [ "${0##*/}" = compile-mvs ]; then
    mkdir -p workarea
    echo CSECT > workarea/m3-clean-smoke.s370.asm
fi
if [ "${0##*/}" = dspal ] && [ "$*" = 'populate all' ]; then
    exit 2
fi
if [ "${MOCK_FAIL:-}" = "${0##*/}:$*" ]; then
    exit 7
fi
exit 0
"""
        for name in (
            'tools/mvs/start-tk5', 'tools/datasets/dspal',
            'tools/bootstrap/prepare-bootstrap', 'tools/clean-workarea',
            'tools/mr10/compile-and-run', 'tools/bootstrap/compile-mvs',
            'bin/git',
        ):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(stub, encoding='utf-8')
            path.chmod(0o755)

    def invoke(self, *, approve=True, fail=None):
        env = os.environ.copy()
        env['PATH'] = str(self.root / 'bin') + os.pathsep + env['PATH']
        env['MOCK_LOG'] = str(self.call_log)
        if fail:
            env['MOCK_FAIL'] = fail
        # script(1) allocates an interactive PTY for the child command.
        answers = ('YES\nYES\nDELETE\n' + 'YES\n' * 16) if approve else 'NO\n'
        return subprocess.run(
            ['script', '-q', '-e', '-c',
             'bash tools/reconstruction/rebuild-from-source', '/dev/null'],
            cwd=self.root, env=env, input=answers,
            capture_output=True, text=True, check=False,
        )

    def test_shell_syntax(self):
        result = subprocess.run(['bash', '-n', str(SOURCE)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_declined_confirmation_runs_nothing(self):
        result = self.invoke(approve=False)
        self.assertEqual(result.returncode, 3, result.stdout[-1000:])
        self.assertFalse(self.call_log.exists())

    def test_full_rebuild_allows_only_expected_first_population_rc2(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
        self.assertIn('REBUILD COMMANDS COMPLETED', result.stdout)
        commands = self.call_log.read_text(encoding='utf-8')
        self.assertIn('dspal populate all\n', commands)
        self.assertIn('dspal submit BOOT_JCL BCPLQSAM\n', commands)
        self.assertNotIn('run-project-regressions', commands)
        self.assertNotIn('jes-idle', commands)

    def test_error_stops_and_never_runs_downstream_build(self):
        result = self.invoke(fail='dspal:submit MR10_JCL IC19BLD')
        self.assertEqual(result.returncode, 7, result.stdout[-1000:])
        self.assertIn('STOPPED: Guide Step 3', result.stdout)
        self.assertNotIn('submit BOOT_JCL CAMBBLD',
                         self.call_log.read_text(encoding='utf-8'))

    def test_no_resume_arguments(self):
        result = subprocess.run(
            ['bash', str(SOURCE), '--resume'],
            cwd=self.root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('always starts at Step 0', result.stderr)


if __name__ == '__main__':
    unittest.main()
