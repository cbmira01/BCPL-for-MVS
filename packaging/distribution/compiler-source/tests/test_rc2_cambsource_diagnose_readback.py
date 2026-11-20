"""Offline tests for saved MVS readback diagnosis; no MVS or network I/O."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'packaging/distribution/compiler-source/rc2-cambsource-diagnose-readback.py'
spec = importlib.util.spec_from_file_location('ta2_diag', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def hashtext(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class DiagnoseSavedMVS(unittest.TestCase):
    def fixture(self, expected='A\nB\n', actual='A\nC\n', match=False):
        row = {'member': 'BCPL', 'job': 9330, 'match': match,
               'normalized_sha256': hashtext(expected),
               'readback_sha256': hashtext(actual)}
        receipt = {'candidate_id': 'BCPL-0.1.0-rc2',
                   'population_jobs': [9325, 9326], 'status': 'incomplete',
                   'members': [row]}
        return receipt, {'BCPL': actual}, {'BCPL': expected}, ['BCPL', 'BLIB']

    def test_mismatch_record_column_and_codepoint(self):
        args = self.fixture()
        rows = mod.diagnostic(*args)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['member'], 'BCPL')
        self.assertEqual(rows[0]['type'], 'record-content-difference')
        self.assertEqual(rows[0]['first_different_record'], 2)
        self.assertEqual(rows[0]['first_different_column'], 1)
        self.assertEqual(rows[0]['expected_codepoint'], 'U+0042')
        self.assertEqual(rows[0]['observed_codepoint'], 'U+0043')

    def test_missing_record(self):
        first = mod.first_mismatch('A\nB\nC\n', 'A\nC\n')
        self.assertEqual(first['type'], 'possible-missing-expected-record')
        self.assertEqual((first['expected_records'], first['observed_records']), (3, 2))

    def test_extra_record(self):
        first = mod.first_mismatch('A\nC\n', 'A\nB\nC\n')
        self.assertEqual(first['type'], 'possible-extra-observed-record')

    def test_missing_tail_and_final_lf(self):
        first = mod.first_mismatch('A\nB\n', 'A\n')
        self.assertEqual(first['type'], 'missing-records-at-end')
        self.assertFalse(mod.first_mismatch('A\nB\n', 'A\nB')['observed_final_lf'])

    def test_record_length_difference(self):
        first = mod.first_mismatch('A\nB\n', 'A\nBX\n')
        self.assertEqual(first['first_different_column'], 2)
        self.assertEqual(first['expected_codepoint'], 'EOL')
        self.assertEqual(first['observed_codepoint'], 'U+0058')

    def test_receipt_forged_mvs_hash_rejected(self):
        data = list(self.fixture())
        data[0]['members'][0]['readback_sha256'] = '0' * 64
        with self.assertRaisesRegex(mod.DiagnosisError, 'hash differs'):
            mod.diagnostic(*data)

    def test_member_not_frozen_order_rejected(self):
        data = list(self.fixture())
        data[0]['members'][0]['member'] = 'BLIB'
        with self.assertRaisesRegex(mod.DiagnosisError, 'selection/order'):
            mod.diagnostic(*data)

    def test_candidate_and_job_identity_rejected(self):
        data = list(self.fixture())
        data[0]['population_jobs'] = [1, 2]
        with self.assertRaisesRegex(mod.DiagnosisError, 'expected failed'):
            mod.diagnostic(*data)

    def test_success_report_cannot_be_diagnosed_as_failure(self):
        with self.assertRaisesRegex(mod.DiagnosisError, 'no mismatched'):
            mod.diagnostic(*self.fixture(expected='A\n', actual='A\n', match=True))

    def test_missing_job_refused(self):
        data = list(self.fixture())
        data[0]['members'][0]['job'] = None
        with self.assertRaisesRegex(mod.DiagnosisError, 'job number'):
            mod.diagnostic(*data)


if __name__ == '__main__':
    unittest.main()
