"""Approval tests against the immutable Step 3 reconstruction scope."""
from __future__ import annotations

import importlib.machinery
import io
from pathlib import Path
import types
import unittest
from dataclasses import FrozenInstanceError

SCRIPT = Path(__file__).resolve().parents[1] / 'reconstruction' / 'authorize'
loader = importlib.machinery.SourceFileLoader('reconstruction_authorize_test', str(SCRIPT))
authorize = types.ModuleType(loader.name)
authorize.__file__ = str(SCRIPT)
import sys
sys.modules[loader.name] = authorize
loader.exec_module(authorize)


def ready_report(*, datasets=2):
    return '\n'.join([
        'CLEAN-ROOM RECONSTRUCTION — READ-ONLY PREFLIGHT / DRY-RUN',
        'Git: ' + 'a'*40 + ' (branch main)',
        'Target: HLQ=HERC02 batch-user=HERC02',
        'Effective non-secret config SHA-256: ' + 'b'*64,
        'Exact operation contract SHA-256: ' + 'c'*64,
        'Host cleanup scope SHA-256: ' + 'd'*64,
        f'Approved dataset count: {datasets}',
        '  managed: BOOT_OBJ HERC02.BCPL.BOOT.OBJ',
        '  managed: EXT_OBJ HERC02.BCPL.EXT.OBJ',
        'READY — read-only preflight passed; no authorization or execution performed.',
        '',
    ])


class AuthorizeTests(unittest.TestCase):
    def setUp(self):
        self.report = ready_report()
        self.calls = 0
        self.output = io.StringIO()

    def planner(self):
        self.calls += 1
        return self.report, []

    def approve(self, answer=None, interactive=True):
        phrase = 'REBUILD HERC02 ' + authorize.digest_report(self.report)[:12]
        return authorize.request_approval(self.planner, output=self.output,
                                          read_line=lambda prompt: phrase if answer is None else answer,
                                          interactive=interactive)

    def test_exact_acknowledgment_is_ephemeral_and_bound(self):
        approved = self.approve()
        self.assertEqual(approved.git_sha, 'a'*40)
        self.assertEqual(approved.hlq, 'HERC02')
        self.assertEqual(len(approved.managed_dsns), 2)
        self.assertEqual(approved.config_digest, 'b'*64)
        self.assertEqual(approved.operation_digest, 'c'*64)
        self.assertEqual(approved.cleanup_digest, 'd'*64)
        self.assertEqual(self.calls, 2)
        self.assertIn('ONE-RUN SCOPE ACKNOWLEDGMENT', self.output.getvalue())
        authorize.verify_approval(approved, self.planner)
        self.assertEqual(self.calls, 3)

    def test_approval_bound_to_full_preview_content(self):
        approved = self.approve()
        self.report = self.report.replace('Git: ', 'Git: ', 1).replace(
            'READY —', 'READY —')
        self.report = self.report.replace('  managed: EXT_OBJ ', '  managed: OTHER ') 
        with self.assertRaisesRegex(authorize.ApprovalError, 'scope changed'):
            authorize.verify_approval(approved, self.planner)

    def test_private_configuration_override_changes_digest(self):
        approved = self.approve()
        self.report = self.report.replace('b'*64, 'e'*64)
        with self.assertRaisesRegex(authorize.ApprovalError, 'scope changed'):
            authorize.verify_approval(approved, self.planner)

    def test_no_tty_blocks_before_prompt(self):
        with self.assertRaisesRegex(authorize.ApprovalError, 'interactive terminal required'):
            self.approve(interactive=False)
        self.assertEqual(self.calls, 1)

    def test_bad_phrase_does_not_authorize(self):
        with self.assertRaises(authorize.ApprovalError) as raised:
            self.approve(answer='YES')
        self.assertEqual(raised.exception.code, 3)
        self.assertEqual(self.calls, 1)

    def test_eof_cancels(self):
        def eof(prompt):
            raise EOFError()
        with self.assertRaises(authorize.ApprovalError) as raised:
            authorize.request_approval(self.planner, output=self.output,
                                       read_line=eof, interactive=True)
        self.assertEqual(raised.exception.code, 3)

    def test_preflight_errors_block_without_prompt(self):
        def blocked():
            return self.report, ['unavailable']
        with self.assertRaisesRegex(authorize.ApprovalError, 'preflight BLOCKED'):
            authorize.request_approval(blocked, output=self.output,
                                       read_line=lambda prompt: self.fail('prompted'), interactive=True)

    def test_preflight_drift_during_prompt_refuses(self):
        def change(prompt):
            self.report = self.report.replace('c'*64, 'f'*64)
            return 'REBUILD HERC02 ' + authorize.digest_report(ready_report())[:12]
        with self.assertRaisesRegex(authorize.ApprovalError, 'scope changed'):
            authorize.request_approval(self.planner, output=self.output,
                                       read_line=change, interactive=True)

    def test_second_preflight_can_be_blocked(self):
        def drifting():
            self.calls += 1
            return self.report, ([] if self.calls == 1 else ['BLOCKED'])
        with self.assertRaisesRegex(authorize.ApprovalError, 'BLOCKED'):
            authorize.request_approval(drifting, output=self.output,
                                       read_line=lambda _: 'REBUILD HERC02 ' + authorize.digest_report(self.report)[:12],
                                       interactive=True)

    def test_missing_dataset_scope_blocked(self):
        self.report = self.report.replace('  managed: EXT_OBJ HERC02.BCPL.EXT.OBJ\n', '')
        with self.assertRaisesRegex(authorize.ApprovalError, 'inventory'):
            self.approve()

    def test_count_mismatch_blocked(self):
        self.report = ready_report(datasets=29)
        with self.assertRaisesRegex(authorize.ApprovalError, 'inventory'):
            self.approve()

    def test_duplicate_dataset_blocked(self):
        self.report = self.report.replace('EXT_OBJ HERC02.BCPL.EXT.OBJ', 'BOOT_OBJ HERC02.BCPL.BOOT.OBJ')
        with self.assertRaisesRegex(authorize.ApprovalError, 'inventory'):
            self.approve()

    def test_unrecognized_preview_blocked(self):
        self.report = self.report.replace('READ-ONLY PREFLIGHT', 'DESTRUCTIVE PREFLIGHT')
        with self.assertRaisesRegex(authorize.ApprovalError, 'unrecognized'):
            self.approve()

    def test_incomplete_preflight_blocked(self):
        self.report = self.report.replace('READY — read-only', 'BLOCKED — read-only')
        with self.assertRaisesRegex(authorize.ApprovalError, 'not READY'):
            self.approve()

    def test_approval_data_is_immutable(self):
        approved = self.approve()
        with self.assertRaises(FrozenInstanceError):
            approved.git_sha = 'bad'


if __name__ == '__main__':
    unittest.main()
