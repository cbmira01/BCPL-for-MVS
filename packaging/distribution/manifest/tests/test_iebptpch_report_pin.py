"""Additional saved-report provenance and discrepancy tests for TA.0."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/distribution/decode-iebptpch-readback.py'
EXCERPT = Path(__file__).resolve().parent / 'fixtures/ta0-job9044-bcpldemo-transcribed.txt'
JOBLOG = '''13.25.35 JOB 9044  $HASP373 TA0READ  STARTED - INIT  1 - CLASS A - SYS TK5R
13.25.35 JOB 9044  TA0READ    TA0HEX              IEBPTPCH  RC= 0000
IEF142I TA0READ TA0HEX - STEP WAS EXECUTED - COND CODE 0000
'''
HISTORIC_SHA = 'b74b12ac496437725910ce0a1edfbbd5e55cb33e5905e405b8a6820257f30ee6'
ACTUAL_REPORTED_SHA = 'a9207bbac0624a34f945630c354b4883f6f6ed526350a0e395e5aa5d99fc49f0'


class ReportPinTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.report = self.root / 'report.txt'
        self.report.write_text(JOBLOG + EXCERPT.read_text(encoding='utf-8'))
        self.out = self.root / 'obj.fb80'

    def launch(self, *args):
        return subprocess.run([sys.executable, '-B', str(SOURCE), '--report', str(self.report),
                               '--member', 'BCPLDEMO', '--job', '9044',
                               '--expected-records', '10', '--output', str(self.out), *args],
                              capture_output=True, text=True)

    def test_report_sha256_captured(self):
        cp = self.launch('--expected-sha256', HISTORIC_SHA)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        meta = json.loads((self.root / 'obj.fb80.json').read_text())
        self.assertEqual(meta['sha256_of_saved_report'], hashlib.sha256(self.report.read_bytes()).hexdigest())
        self.assertEqual(meta['independent_expected_sha256_matched'], True)

    def test_reported_live_digest_rejected_against_fixture(self):
        cp = self.launch('--expected-sha256', ACTUAL_REPORTED_SHA)
        self.assertEqual(cp.returncode, 1)
        self.assertIn('do not match', cp.stderr)
        self.assertFalse(self.out.exists())
        self.assertFalse((self.root / 'obj.fb80.json').exists())

    def test_bad_expected_hash_rejected(self):
        cp = self.launch('--expected-sha256', '1234')
        self.assertEqual(cp.returncode, 1)
        self.assertFalse(self.out.exists())

    def test_wrong_report_changes_report_pin(self):
        cp = self.launch()
        self.assertEqual(cp.returncode, 0, cp.stderr)
        saved = json.loads((self.root / 'obj.fb80.json').read_text())
        self.assertEqual(saved['sha256_of_saved_report'], hashlib.sha256(self.report.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
