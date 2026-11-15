"""MR10 Development Probe fail-stop receipts: host-only, no JES."""
from __future__ import annotations

from importlib.machinery import SourceFileLoader
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'tests/run-project-regressions'
SPEC = importlib.util.spec_from_loader(
    'co5_probe_failstop', SourceFileLoader('co5_probe_failstop', str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('cannot load project regression coordinator')
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class ProbeFailStopHostTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='co5-mr10-failstop-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        patcher = patch.object(MOD, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.receipt = self.root / 'workarea/mr10-probes/session'
        self.receipt.mkdir(parents=True)
        self.identities = ['04-module-test', '05-named-dd',
                           '10-coroutines/compiler-probe']

    def verify(self, statuses, *, legacy_pending=False, unaccepted=None,
               wrong_counts=False, rc=None):
        cases = []
        for index, (ident, status) in enumerate(zip(self.identities, statuses)):
            item = {'id': ident, 'status': status}
            if not (legacy_pending and status == 'NOT_RUN'):
                item['verification'] = ('UNVERIFIED' if index == unaccepted
                                        else 'ACCEPTED')
            if status == 'FAIL':
                item['reason'] = 'IFOX JES step RC=0012'
            cases.append(item)
        counts = {kind: sum(row['status'] == kind for row in cases)
                  for kind in ('PASS', 'FAIL', 'OBSERVED', 'NOT_RUN')}
        payload = {
            'suite': 'mr10-probes', 'selected_cases': self.identities,
            'cases': cases, 'status': ('FAIL' if counts['FAIL'] else
                                     'UNVERIFIED' if counts['OBSERVED'] else 'PASS'),
            'counts': ({**counts, 'FAIL': 0} if wrong_counts else counts),
        }
        (self.receipt / 'summary.json').write_text(json.dumps(payload))
        if rc is None:
            rc = 1 if counts['FAIL'] else 3 if counts['OBSERVED'] else 0
        return MOD.parse_mr10_probes(
            f'MR10 PROBE EVIDENCE: {self.receipt}\n', self.identities, rc)

    def test_all_accepted_pass(self):
        actual = self.verify(['PASS', 'PASS', 'PASS'])
        self.assertEqual((actual['status'], actual['counts']['PASS']),
                         ('PASS', 3))

    def test_fail_stop_reports_real_failing_case(self):
        actual = self.verify(['PASS', 'FAIL', 'NOT_RUN'])
        self.assertEqual(actual['status'], 'FAIL')
        self.assertEqual(actual['cases'][1]['reason'], 'IFOX JES step RC=0012')
        self.assertEqual(actual['counts']['FAIL'], 1)

    def test_legacy_not_run_case_without_verification(self):
        actual = self.verify(['PASS', 'FAIL', 'NOT_RUN'], legacy_pending=True)
        self.assertEqual(actual['status'], 'FAIL')

    def test_unaccepted_executed_case_rejected(self):
        with self.assertRaisesRegex(MOD.VerificationError,
                                    'unaccepted case selected'):
            self.verify(['PASS', 'PASS', 'PASS'], unaccepted=1)

    def test_unaccepted_unexecuted_case_rejected(self):
        with self.assertRaisesRegex(MOD.VerificationError,
                                    'unaccepted case selected'):
            self.verify(['PASS', 'FAIL', 'NOT_RUN'], unaccepted=2)

    def test_inconsistent_counts_rejected(self):
        with self.assertRaisesRegex(MOD.VerificationError, 'counts disagree'):
            self.verify(['PASS', 'FAIL', 'NOT_RUN'], wrong_counts=True)

    def test_inconsistent_return_code_rejected(self):
        with self.assertRaisesRegex(MOD.VerificationError, 'RC=0'):
            self.verify(['PASS', 'FAIL', 'NOT_RUN'], rc=0)

    def test_unexecuted_without_failure_rejected(self):
        with self.assertRaisesRegex(MOD.VerificationError, 'unexecuted cases'):
            self.verify(['PASS', 'PASS', 'NOT_RUN'])


if __name__ == '__main__':
    unittest.main()
