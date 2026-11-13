#!/usr/bin/env python3
"""Host-only wrapper consistency tests; synthetic jobs are never MVS proof."""
from pathlib import Path
import runpy
import unittest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                            'bootstrap/probe-co1-indirect-target.py'))
path_for = MODULE['evidence_path']
extract = MODULE['extract_result']


def sample():
    output = ('CO.1 INDIRECT PASS: JOB 8125, checked 4, three-formal 1, '
              'calls 4; compile-only\n'
              'CO.1 INDIRECT evidence: workarea/co1-indirect-entry/FAKE-8125\n')
    summary = {'status': 'PASS', 'jes_job_id': '8125', 'checked_entries': 4,
               'three_formal_entries': 1, 'ordinary_calls': 4,
               'compiler_driver_rc': 0, 'assembled': False,
               'linked': False, 'native_go': False}
    return output, summary


class WrapperTests(unittest.TestCase):
    def test_consistent_report(self):
        out, summary = sample()
        self.assertEqual(extract(out, summary), '8125')

    def test_detect_wrong_job(self):
        out, summary = sample()
        summary['jes_job_id'] = '8126'
        with self.assertRaisesRegex(ValueError, 'differs'): extract(out, summary)

    def test_detect_wrong_count(self):
        out, summary = sample()
        summary['ordinary_calls'] = 5
        with self.assertRaisesRegex(ValueError, 'differs'): extract(out, summary)

    def test_detect_nonzero_compiler(self):
        out, summary = sample()
        summary['compiler_driver_rc'] = 4
        with self.assertRaisesRegex(ValueError, 'differs'): extract(out, summary)

    def test_detect_native_go(self):
        out, summary = sample()
        summary['native_go'] = True
        with self.assertRaisesRegex(ValueError, 'differs'): extract(out, summary)

    def test_detect_multiple_result_lines(self):
        out, summary = sample()
        with self.assertRaisesRegex(ValueError, 'no unique'):
            extract(out + out, summary)

    def test_accept_single_evidence_folder(self):
        out, _ = sample()
        self.assertEqual(path_for(out).name, 'FAKE-8125')

    def test_reject_parent_traversal(self):
        out, _ = sample()
        with self.assertRaisesRegex(ValueError, 'expected one fresh'):
            path_for(out.replace('FAKE-8125', '../oops'))

    def test_reject_unrelated_location(self):
        out, _ = sample()
        with self.assertRaisesRegex(ValueError, 'expected one fresh'):
            path_for(out.replace('workarea/co1-indirect-entry', 'workarea/elsewhere'))

    def test_no_evidence(self):
        with self.assertRaisesRegex(ValueError, 'expected one fresh'):
            path_for('CO.1 TARGET PASS: JOB 8125')


if __name__ == '__main__':
    unittest.main()
