"""Host-only CO.6 suite selection and truthful evidence classification tests.

Never submits JES. The original fixed-stack probe must not become
PASS, SKIP, or OBSERVED through coordinator aggregation.
"""
from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tools/tests/run-project-regressions'
SPEC = importlib.util.spec_from_loader(
    'co6_project_coordinator', SourceFileLoader('co6_project_coordinator', str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('unable to import project regression coordinator')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CO6CoroutineSuiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch_root = patch.object(MOD, 'ROOT', self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        self.evidence = self.root / 'workarea/mr10-probes/session'
        self.evidence.mkdir(parents=True)
        self.cases = list(MOD.MR10_COROUTINE_PROBES)

    def receipt(self, statuses):
        items = []
        for ident, status in zip(self.cases, statuses):
            items.append({'id': ident, 'status': status,
                          'verification': 'ACCEPTED',
                          **({'reason': 'interpreted CODE=-1'} if status == 'FAIL' else {})})
        counts = {k: statuses.count(k) for k in ('PASS', 'FAIL', 'OBSERVED', 'NOT_RUN')}
        status = 'FAIL' if counts['FAIL'] else 'UNVERIFIED' if counts['OBSERVED'] else 'PASS'
        (self.evidence / 'summary.json').write_text(json.dumps({
            'suite': 'mr10-probes', 'selected_cases': self.cases,
            'cases': items, 'counts': counts, 'status': status,
        }), encoding='utf-8')
        rc = 1 if counts['FAIL'] else 3 if counts['OBSERVED'] else 0
        return MOD.parse_mr10_probes(f'MR10 PROBE EVIDENCE: {self.evidence}\n', self.cases, rc)

    def test_suite_is_selectable_and_keeps_five_historical_identifiers(self):
        self.assertIn('mr10-coroutines', MOD.SUITES)
        self.assertEqual(self.cases, [
            '10-coroutines/compiler-probe',
            '10-coroutines/frame-layout-probe',
            '10-coroutines/fixed-stack-producer-consumer',
            '10-coroutines/resumeco-chain',
            '10-coroutines/create-delete-static-pool',
        ])
        self.assertTrue(set(self.cases).issubset(MOD.ACCEPTED_MR10_PROBES))
        self.assertEqual(len(MOD.ACCEPTED_MR10_PROBES), 11)
        self.assertIn('coroutines', MOD.NATIVE_SUITES)

    def test_suite_uses_existing_real_mr10_runner(self):
        command = MOD.suite_command('mr10-coroutines', {'mr10-coroutines': self.cases}, None, False)
        self.assertEqual(command[:2], [str(MOD.MR10_PROBES), '--run'])
        self.assertEqual(command[-1], '--continue-known-fixed-stack-failure')
        self.assertEqual(command[2:-1:2], ['--case'] * 5)
        self.assertEqual(command[3:-1:2], self.cases)

    def test_original_legacy_failure_is_retained(self):
        result = self.receipt(['PASS', 'PASS', 'FAIL', 'NOT_RUN', 'NOT_RUN'])
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['counts']['FAIL'], 1)
        self.assertEqual(result['counts']['PASS'], 2)
        self.assertEqual(result['cases'][2]['id'], '10-coroutines/fixed-stack-producer-consumer')
        self.assertEqual(result['cases'][2]['status'], 'FAIL')
        self.assertEqual(result['cases'][2]['reason'], 'interpreted CODE=-1')
        self.assertEqual(result['cases'][3]['status'], 'NOT_RUN')

    def test_known_failure_continuation_cannot_report_pass(self):
        result = self.receipt(['PASS', 'PASS', 'FAIL', 'PASS', 'PASS'])
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['counts'],
                         {'PASS': 4, 'FAIL': 1, 'SKIP': 0,
                          'BLOCKED': 0, 'TOTAL': 5})

    def test_five_pass_requires_real_five_pass_receipt(self):
        result = self.receipt(['PASS'] * 5)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['counts'], {
            'PASS': 5, 'FAIL': 0, 'SKIP': 0, 'BLOCKED': 0, 'TOTAL': 5,
        })

    def test_observation_is_blocked_not_pass(self):
        result = self.receipt(['OBSERVED'] + ['PASS'] * 4)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['counts']['BLOCKED'], 1)

    def test_progress_preserves_names_and_failure(self):
        self.assertEqual(MOD.progress_case(
            'mr10-coroutines', 'FAIL     10-coroutines/fixed-stack-producer-consumer: CODE=-1'),
            'FAIL    10-coroutines/fixed-stack-producer-consumer')

    def test_extra_or_missing_case_is_rejected(self):
        self.receipt(['PASS'] * 5)
        target = self.evidence / 'summary.json'
        body = json.loads(target.read_text())
        body['selected_cases'][2] = '10-coroutines/fixed-stack-co0-candidate'
        target.write_text(json.dumps(body))
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_mr10_probes(f'MR10 PROBE EVIDENCE: {self.evidence}\n', self.cases, 0)


if __name__ == '__main__':
    unittest.main()
