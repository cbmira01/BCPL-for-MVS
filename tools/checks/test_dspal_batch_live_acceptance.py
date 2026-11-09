"""Host-only tests of guarded MVS batch read-back acceptance. No JES requests."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import importlib.util
from importlib.machinery import SourceFileLoader
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / 'datasets/verify-populate-batch'
spec = importlib.util.spec_from_loader(
    'batch_acceptance_under_test',
    SourceFileLoader('batch_acceptance_under_test', str(SCRIPT)),
)
assert spec is not None and spec.loader is not None
accept = importlib.util.module_from_spec(spec)
spec.loader.exec_module(accept)


class AcceptanceTests(unittest.TestCase):
    def test_expected_canonical_fb80_text(self):
        self.assertEqual(accept.canonical_text(['FIRST ', '', 'THIRD  ']),
                         'FIRST\n\nTHIRD\n')
        self.assertEqual(accept.canonical_text([]), '')
        for records in ([''], ['', 'SECOND'], ['FIRST', '']):
            with self.subTest(records=records), self.assertRaises(ValueError):
                accept.canonical_text(records)

    def test_approval_required_before_preflight_or_jes(self):
        with mock.patch.object(accept, 'git_revision') as git, \
             mock.patch.object(accept, 'invoke_dspal') as dspal, \
             redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                accept.main(['--run'])
        git.assert_not_called()
        dspal.assert_not_called()

    def test_check_only_does_not_submit(self):
        entries = [
            dict(logical='DIST_DOCS', member='README', path=accept.ROOT/'README.md'),
        ]
        with mock.patch.object(accept, 'git_revision', return_value='a'*40), \
             mock.patch.object(accept, 'check_clean_source'), \
             mock.patch.object(accept, 'load_population', return_value=object()), \
             mock.patch.object(accept, 'collect_plan', return_value=(
                 'HERC02.BCPL.DIST.DOCS', entries, {'README': 'TEST\n'})), \
             mock.patch.object(accept, 'invoke_dspal') as dspal, \
             redirect_stdout(StringIO()):
            self.assertEqual(accept.main(['--check']), 0)
        dspal.assert_not_called()

    def test_wrong_approval_blocks_without_mvs_write(self):
        entries = [dict(logical='DIST_DOCS', member='README',
                        path=accept.ROOT/'README.md')]
        with mock.patch.object(accept, 'git_revision', return_value='a'*40), \
             mock.patch.object(accept, 'check_clean_source'), \
             mock.patch.object(accept, 'load_population', return_value=object()), \
             mock.patch.object(accept, 'collect_plan', return_value=(
                 'HERC02.BCPL.DIST.DOCS', entries, {'README': 'TEST\n'})), \
             mock.patch.object(accept, 'invoke_dspal') as dspal, \
             redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(accept.main(['--run', '--approve-dsn',
                                          'HERC02.BCPL.EXT.SOURCE']), 2)
        dspal.assert_not_called()

    def test_run_success_confirms_each_member_and_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            expected = {'README': 'HELLO\n', 'VERIFY': 'CHECK\n'}
            calls = []
            def invoke(*args):
                calls.append(args)
                if args[0] == 'populate':
                    return subprocess.CompletedProcess(args, 0,
                         'JOB 14: batch 1/1 DIST_DOCS (2 members), 1.0s\n', '')
                return subprocess.CompletedProcess(args, 0,
                         expected[args[2]], '')
            with mock.patch.object(accept, 'ROOT', evidence.parent), \
                 mock.patch.object(accept, 'evidence_directory', return_value=evidence), \
                 mock.patch.object(accept, 'invoke_dspal', side_effect=invoke), \
                 redirect_stdout(StringIO()):
                self.assertEqual(accept.run_acceptance(
                    'DIST_DOCS', 'HERC02.BCPL.DIST.DOCS', expected, 'a'*40), 0)
            self.assertEqual(calls, [
                ('populate', 'DIST_DOCS', '--batch'),
                ('get', 'DIST_DOCS', 'README', '-'),
                ('get', 'DIST_DOCS', 'VERIFY', '-'),
            ])
            self.assertIn('"passed": true', (evidence/'summary.json').read_text())

    def test_mismatch_stops_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            def invoke(*args):
                if args[0] == 'populate':
                    return subprocess.CompletedProcess(args, 0, 'JOB 14: batch 1/1\n', '')
                return subprocess.CompletedProcess(args, 0, 'ALTERED\n', '')
            with mock.patch.object(accept, 'ROOT', evidence.parent), \
                 mock.patch.object(accept, 'evidence_directory', return_value=evidence), \
                 mock.patch.object(accept, 'invoke_dspal', side_effect=invoke), \
                 redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(accept.run_acceptance(
                    'DIST_DOCS', 'HERC02.BCPL.DIST.DOCS', {'README': 'HELLO\n'}, 'a'*40), 1)
            self.assertIn('"passed": false', (evidence/'summary.json').read_text())
            self.assertEqual((evidence/'get-README.actual.txt').read_text(), 'ALTERED\n')

    def test_failed_population_never_reads_members(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            with mock.patch.object(accept, 'ROOT', evidence.parent), \
                 mock.patch.object(accept, 'evidence_directory', return_value=evidence), \
                 mock.patch.object(accept, 'invoke_dspal', return_value=
                     subprocess.CompletedProcess(['dspal'], 2, '', 'JES error')) as dspal, \
                 redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(accept.run_acceptance(
                    'DIST_DOCS', 'HERC02.BCPL.DIST.DOCS', {'README': 'HELLO\n'}, 'a'*40), 1)
            dspal.assert_called_once_with('populate', 'DIST_DOCS', '--batch')


if __name__ == '__main__':
    unittest.main()
