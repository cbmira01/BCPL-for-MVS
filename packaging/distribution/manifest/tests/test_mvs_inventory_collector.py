"""Isolated mock tests: no calls to real MVS, JES, or a real user's checkout."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

COLLECTOR = Path(__file__).resolve().parents[4] / 'tools/distribution/collect-mvs-inventories.sh'
SHA = 'ab' * 20


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        (self.repo / '.git').mkdir()
        (self.repo / 'tools/datasets').mkdir(parents=True)
        dspal = self.repo / 'tools/datasets/dspal'
        dspal.write_text('''#!/usr/bin/env bash
set -euo pipefail
if [[ $1 == ls && $# == 2 ]]; then
  printf 'HERC02.BCPL.%s:\\n    ICINT19\\n' "$2"
elif [[ $1 == stat && $3 == --raw && $# == 3 ]]; then
  printf 'JOB 21 DSPALST\\n%s RECFM=FB DSORG=PO\\n' "$2"
else
  exit 77
fi
''', encoding='utf-8')
        dspal.chmod(0o755)
        bindir = self.root / 'bin'
        bindir.mkdir()
        git = bindir / 'git'
        git.write_text('#!/bin/sh\nprintf "%s\\n" "' + SHA + '"\n', encoding='utf-8')
        git.chmod(0o755)
        self.env = {**os.environ, 'PATH': f'{bindir}:{os.environ["PATH"]}'}

    def run_collector(self, *args):
        return subprocess.run(['bash', str(COLLECTOR), *map(str, args)],
                              cwd=self.repo, env=self.env, capture_output=True, text=True)

    def test_dry_run_never_invokes_mvs(self):
        result = self.run_collector('--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('MVS LISTDS'), 4)
        self.assertFalse((self.repo / 'workarea').exists())

    def test_capture_and_checksum(self):
        out = self.root / 'evidence'
        result = self.run_collector('--run', '--output', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(out.iterdir())), 10)
        self.assertIn('MR10_LOAD', (out / 'MR10_LOAD.stat-raw.txt').read_text())
        self.assertEqual((out / 'collection-git-head.txt').read_text().strip(), SHA)
        self.assertEqual(len((out / 'SHA256SUMS').read_text().splitlines()), 9)
        self.assertEqual(out.stat().st_mode & 0o777, 0o700)
        import hashlib
        for line in (out / 'SHA256SUMS').read_text().splitlines():
            digest, name = line.split('  ')
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest)

    def test_rejects_existing_destination(self):
        out = self.root / 'evidence'
        out.mkdir()
        result = self.run_collector('--run', '--output', out)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(list(out.iterdir()), [])

    def test_rejects_output_inside_checkout(self):
        result = self.run_collector('--run', '--output', self.repo / 'new-evidence')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.repo / 'new-evidence').exists())

    def test_rejects_relative_output(self):
        result = self.run_collector('--run', '--output', 'evidence')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.repo / 'evidence').exists())

    def test_rejects_missing_parent(self):
        result = self.run_collector('--run', '--output', self.root / 'missing' / 'new')
        self.assertEqual(result.returncode, 2)

    def test_unknown_option_fails(self):
        result = self.run_collector('--go')
        self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
