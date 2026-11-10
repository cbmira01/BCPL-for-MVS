"""Host-only tests of guarded MVS batch read-back acceptance. No JES requests."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import importlib.util
from importlib.machinery import SourceFileLoader
from io import StringIO
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
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
        self.assertEqual(
            accept.canonical_text(['FIRST ', '', ''], allow_terminal_blanks=True),
            'FIRST\n',
        )
        self.assertEqual(accept.terminal_blank_count(['FIRST', '', '']), 2)
        for records in ([''], ['', 'SECOND'], ['FIRST', ''], ['FIRST', '   ']):
            with self.subTest(records=records), self.assertRaises(ValueError):
                accept.canonical_text(records)
        with self.assertRaises(ValueError):
            accept.canonical_text(['', 'SECOND'], allow_terminal_blanks=True)

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
            dict(logical='DIST_DOCS', member='README', path=accept.ROOT/'README.md', records=['TEST']),
        ]
        with mock.patch.object(accept, 'git_revision', return_value='a'*40), \
             mock.patch.object(accept, 'check_clean_source'), \
             mock.patch.object(accept, 'load_population', return_value=
                SimpleNamespace(population_batches=lambda a: [a])), \
             mock.patch.object(accept, 'collect_plan', return_value=(
                 'HERC02.BCPL.DIST.DOCS', entries, {'README': 'TEST\n'})), \
             mock.patch.object(accept, 'invoke_dspal') as dspal, \
             redirect_stdout(StringIO()):
            self.assertEqual(accept.main(['--check']), 0)
        dspal.assert_not_called()

    def test_wrong_approval_blocks_without_mvs_write(self):
        entries = [dict(logical='DIST_DOCS', member='README',
                        path=accept.ROOT/'README.md', records=['TEST'])]
        with mock.patch.object(accept, 'git_revision', return_value='a'*40), \
             mock.patch.object(accept, 'check_clean_source'), \
             mock.patch.object(accept, 'load_population', return_value=
                SimpleNamespace(population_batches=lambda a: [a])), \
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
                    return subprocess.CompletedProcess(args, 0, 'JOB 14: batch 1/1 DIST_DOCS (1 members), 1.0s\n', '')
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


    def test_batch_receipts_require_all_60_plus_1_steps(self):
        stdout = (
            'JOB 910: batch 1/2 MR10_TESTS (60 members), 9.9s\n'
            'JOB 911: batch 2/2 MR10_TESTS (1 members), 1.1s\n'
        )
        receipts = accept.verify_batch_receipts(stdout, 'MR10_TESTS', [60, 1])
        self.assertEqual([r['job'] for r in receipts], [910, 911])
        for bad in (
            stdout.splitlines(keepends=True)[0],
            stdout.replace('batch 2/2', 'batch 1/2'),
            stdout.replace('JOB 911', 'JOB 910'),
            stdout.replace('(1 members)', '(2 members)'),
        ):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                accept.verify_batch_receipts(bad, 'MR10_TESTS', [60, 1])

    def test_collect_plan_limits_terminal_blank_exception_to_mr10_tests(self):
        config = {
            'mvs': {'hlq': 'HERC02'},
            'datasets': {
                'MR10_TESTS': {'dsn': 'BCPL.MR10KIT.TESTS'},
                'DIST_DOCS': {'dsn': 'BCPL.DIST.DOCS'},
            },
        }
        core = SimpleNamespace(
            load_config=lambda: config,
            full_dsn=lambda cfg, spec: cfg['mvs']['hlq'] + '.' + spec['dsn'],
        )
        class Population:
            def __init__(self, member):
                self.core = core
                self.member = member
            def preflight(self, config, target):
                return [], [dict(logical=target, member='CASE',
                                  records=self.member)], [], []
        target, actions, expected = accept.collect_plan(
            Population(['HEADER', '']), 'MR10_TESTS')
        self.assertEqual(target, 'HERC02.BCPL.MR10KIT.TESTS')
        self.assertEqual(expected, {'CASE': 'HEADER\n'})
        with self.assertRaisesRegex(ValueError, 'terminal blank'):
            accept.collect_plan(Population(['HEADER', '']), 'DIST_DOCS')

    def test_61_member_check_prints_two_job_plan_without_jes(self):
        entries = [
            dict(logical='MR10_TESTS', member=f'M{i:03d}',
                 path=accept.ROOT/'README.md', records=['DATA'])
            for i in range(61)
        ]
        entries[10]['records'].append('')
        pop = SimpleNamespace(population_batches=lambda a: [a[:60], a[60:]])
        output = StringIO()
        with mock.patch.object(accept, 'git_revision', return_value='a'*40), \
             mock.patch.object(accept, 'check_clean_source'), \
             mock.patch.object(accept, 'load_population', return_value=pop), \
             mock.patch.object(accept, 'collect_plan', return_value=(
                 'HERC02.BCPL.MR10KIT.TESTS', entries,
                 {x['member']: 'DATA\n' for x in entries})), \
             mock.patch.object(accept, 'invoke_dspal') as dspal, \
             redirect_stdout(output):
            self.assertEqual(accept.main(['--check', '--target', 'MR10_TESTS']), 0)
        dspal.assert_not_called()
        self.assertIn('Planned batch jobs: 2 (60, 1 members)', output.getvalue())
        self.assertIn('1 members contain terminal blank records', output.getvalue())

    def test_qualified_61_member_acceptance_has_two_jes_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            expected = {f'M{i:03d}': 'DATA\n' for i in range(61)}
            calls = []
            def invoke(*args):
                calls.append(args)
                if args[0] == 'populate':
                    return subprocess.CompletedProcess(args, 0,
                        'JOB 910: batch 1/2 MR10_TESTS (60 members), 9.9s\n'
                        'JOB 911: batch 2/2 MR10_TESTS (1 members), 1.1s\n', '')
                return subprocess.CompletedProcess(args, 0, expected[args[2]], '')
            with mock.patch.object(accept, 'ROOT', evidence.parent), \
                 mock.patch.object(accept, 'evidence_directory', return_value=evidence), \
                 mock.patch.object(accept, 'invoke_dspal', side_effect=invoke), \
                 redirect_stdout(StringIO()):
                rc = accept.run_acceptance(
                    'MR10_TESTS', 'HERC02.BCPL.MR10KIT.TESTS', expected, 'a'*40,
                    expected_batch_sizes=[60, 1],
                    unverified_terminal_blanks={'M010': 1},
                )
            self.assertEqual(rc, 0)
            self.assertEqual(len(calls), 62)
            summary = (evidence/'summary.json').read_text()
            self.assertIn('"qualified": true', summary)
            self.assertIn('"job": 911', summary)
            self.assertIn('"passed": true', summary)
            self.assertIn('"unverified_terminal_blank_records"', summary)

    def test_missing_second_batch_receipt_prevents_readback(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder)
            with mock.patch.object(accept, 'ROOT', evidence.parent), \
                 mock.patch.object(accept, 'evidence_directory', return_value=evidence), \
                 mock.patch.object(accept, 'invoke_dspal', return_value=
                      subprocess.CompletedProcess(['dspal'], 0,
                           'JOB 910: batch 1/2 MR10_TESTS (60 members), 2.0s\n', '')) as dspal, \
                 redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(accept.run_acceptance(
                    'MR10_TESTS', 'HERC02.BCPL.MR10KIT.TESTS',
                    {'A': 'X\n', 'B': 'Y\n'}, 'a'*40,
                    expected_batch_sizes=[1, 1]), 1)
            dspal.assert_called_once()
            self.assertIn('"passed": false', (evidence/'summary.json').read_text())

if __name__ == '__main__':
    unittest.main()
