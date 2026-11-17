"""Offline tests for read-only, pinned MVS report heading diagnosis."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[4]
SRC = HERE / 'tools/distribution/diagnose-iebptpch-headings.py'
SPEC = importlib.util.spec_from_file_location('ta0_diag', SRC)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

REQ = ['BCPLTIME', 'BCPLQSAM']
PFX = 'IEF142I TA0MULT TA0HEX - STEP WAS EXECUTED - COND CODE 0000\n'


class HeadingTests(unittest.TestCase):
    def test_normal_two(self):
        r = mod.inspect(PFX + '         MEMBER NAME=BCPLTIME\n' +
                        '         MEMBER NAME=BCPLQSAM\nMEMBER NAME  BCPLTIME\n' +
                        'MEMBER NAME  BCPLQSAM\n', REQ)
        self.assertEqual(r['printed_headers_exact'], REQ)
        self.assertEqual(r['member_control_statements'], REQ)
        self.assertTrue(r['header_count_matches_request'])
        self.assertFalse(r['missing_requested_members'])

    def test_missing_second(self):
        r = mod.inspect('MEMBER NAME  BCPLTIME\n', REQ)
        self.assertEqual(r['missing_requested_members'], ['BCPLQSAM'])
        self.assertFalse(r['header_count_matches_request'])

    def test_reversed_order_diagnosis_only(self):
        r = mod.inspect('MEMBER NAME  BCPLQSAM\nMEMBER NAME  BCPLTIME\n', REQ)
        self.assertTrue(r['printed_headers_appear_out_of_order'])
        self.assertFalse(r['missing_requested_members'])

    def test_carriage_control_prefix_is_not_exact(self):
        r = mod.inspect('  MEMBER NAME   BCPLTIME\n1MEMBER NAME  BCPLQSAM\n', REQ)
        self.assertEqual(r['printed_headers_exact'], [])
        self.assertEqual(r['printed_headers_whitespace_tolerant'], ['BCPLTIME'])
        self.assertEqual(r['nonstandard_embedded_header_candidates'], ['BCPLQSAM'])

    def test_formfeed_and_pagebreak(self):
        r = mod.inspect('\fMEMBER NAME  BCPLTIME\r\nMEMBER NAME  BCPLQSAM\n', REQ)
        self.assertEqual(r['printed_headers_exact'], REQ)

    def test_unexpected_duplicate(self):
        r = mod.inspect('MEMBER NAME  BCPLTIME\nMEMBER NAME  BCPLTIME\nMEMBER NAME  WRONG\n', REQ)
        self.assertEqual(r['duplicated_printed_members'], ['BCPLTIME'])
        self.assertEqual(r['unexpected_printed_members'], ['WRONG'])

    def test_member_control_not_interpreted_as_heading(self):
        r = mod.inspect('         MEMBER NAME=BCPLTIME\n', REQ)
        self.assertEqual(r['printed_headers_whitespace_tolerant'], [])
        self.assertEqual(r['member_control_statements'], ['BCPLTIME'])

    def test_hex_and_identity_not_exposed(self):
        h = '02C5E2C4  ' + '40404040  ' * 10 + '00000000'
        s = '40404040  ' * 7 + 'F0F0F0F1*'
        r = mod.inspect('USER=HERC02,PASSWORD=FAKE\n' + h + '\n' + s + '\n', REQ)
        self.assertEqual(r['first_hex_line_count'], 1)
        self.assertEqual(r['second_hex_line_count'], 1)
        self.assertNotIn('PASSWORD', repr(r))
        self.assertNotIn('02C5E2C4', repr(r))

    def test_refuses_unbounded_large_report(self):
        with self.assertRaisesRegex(ValueError, 'line limit'):
            mod.inspect('A\n' * (mod.MAX_LINES + 1), REQ)


if __name__ == '__main__':
    unittest.main()
