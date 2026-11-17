"""TA.0: page-continuation checks; no JES submission, no private object fixture."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[4]
HELPER = ROOT / 'tools/distribution/iebptpch-page-framing.py'
SPEC = importlib.util.spec_from_file_location('ta0_page_framing', HELPER)
assert SPEC is not None and SPEC.loader is not None
pages = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pages)
HEADER = re.compile(r'^MEMBER NAME  ([A-Z@$#][A-Z0-9@$#]{0,7})\s*$')
FIRST = re.compile(r'^(?:[0-9A-F]{8}  ){11}[0-9A-F]{8}$')
SECOND = re.compile(r'^((?:[0-9A-F]{8}  ){7}[0-9A-F]{8})(\*\*|\*)$')


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def record(number: int, *, block_end: bool = False) -> list[str]:
    chunks = [f'{(number * 100 + index):08X}' for index in range(20)]
    return ['  '.join(chunks[:12]), '  '.join(chunks[12:]) + ('**' if block_end else '*')]


def unwrap(lines: list[str], members: list[str]):
    return pages.coalesce_page_headings(
        lines, members=members, header=HEADER, first=FIRST,
        second=SECOND, require=check)


class Continuation(unittest.TestCase):
    def test_single_page(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1, block_end=True)]
        clean, heads, repeats = unwrap(lines, ['BCPLQSAM'])
        self.assertEqual(clean, lines)
        self.assertEqual(heads, [(1, 'BCPLQSAM')])
        self.assertEqual(repeats, {'BCPLQSAM': 0})

    def test_page_repeats_within_physical_block(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1),
                 '                            PAGE 0002', 'MEMBER NAME  BCPLQSAM',
                 *record(2, block_end=True)]
        clean, heads, repeats = unwrap(lines, ['BCPLQSAM'])
        self.assertEqual(heads, [(1, 'BCPLQSAM')])
        self.assertEqual(repeats, {'BCPLQSAM': 1})
        self.assertEqual(sum(HEADER.fullmatch(x) is not None for x in clean), 1)
        self.assertEqual(sum(SECOND.fullmatch(x) is not None for x in clean), 2)
        self.assertTrue(any('PAGE 0002' in x for x in clean))

    def test_multiple_pages_and_distinct_selected_members(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLTIME', *record(1),
                 'PAGE 0002', 'MEMBER NAME  BCPLTIME', *record(2, block_end=True),
                 'PAGE 0003', 'MEMBER NAME  BCPLQSAM', *record(3, block_end=True)]
        clean, heads, repeats = unwrap(lines, ['BCPLTIME', 'BCPLQSAM'])
        self.assertEqual([name for _, name in heads], ['BCPLTIME', 'BCPLQSAM'])
        self.assertEqual(repeats, {'BCPLTIME': 1, 'BCPLQSAM': 0})
        self.assertEqual(sum(HEADER.fullmatch(x) is not None for x in clean), 2)

    def test_missing_page_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1),
                 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'PAGE marker'):
            unwrap(lines, ['BCPLQSAM'])

    def test_skipped_page_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1),
                 'PAGE 0003', 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'PAGE marker'):
            unwrap(lines, ['BCPLQSAM'])

    def test_repeated_page_with_no_complete_record_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM',
                 'PAGE 0002', 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'no complete FB80 record'):
            unwrap(lines, ['BCPLQSAM'])

    def test_corrupted_previous_record_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', record(1)[0],
                 'NOT HEX', 'PAGE 0002', 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'no complete FB80 record'):
            unwrap(lines, ['BCPLQSAM'])

    def test_wrong_member_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'printed member headers'):
            unwrap(lines, ['BCPLTIME'])

    def test_missing_member_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLTIME', *record(1, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'printed member headers'):
            unwrap(lines, ['BCPLTIME', 'BCPLQSAM'])

    def test_unselected_member_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLTIME', *record(1, block_end=True),
                 'PAGE 0002', 'MEMBER NAME  UNLISTED', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'printed member headers'):
            unwrap(lines, ['BCPLTIME'])

    def test_reordered_member_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1, block_end=True),
                 'PAGE 0002', 'MEMBER NAME  BCPLTIME', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'printed member headers'):
            unwrap(lines, ['BCPLTIME', 'BCPLQSAM'])

    def test_old_member_reappears_after_new_member_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLTIME', *record(1, block_end=True),
                 'PAGE 0002', 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True),
                 'PAGE 0003', 'MEMBER NAME  BCPLTIME', *record(3, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'printed member headers'):
            unwrap(lines, ['BCPLTIME', 'BCPLQSAM'])

    def test_repeated_member_on_same_page_refused(self):
        lines = ['PAGE 0001', 'MEMBER NAME  BCPLQSAM', *record(1),
                 'MEMBER NAME  BCPLQSAM', *record(2, block_end=True)]
        with self.assertRaisesRegex(ValueError, 'PAGE marker'):
            unwrap(lines, ['BCPLQSAM'])

    def test_page_control_not_mistaken_for_print_heading(self):
        lines = ['MEMBER NAME=BCPLQSAM', 'PAGE 0001', 'MEMBER NAME  BCPLQSAM',
                 *record(1, block_end=True)]
        clean, heads, repeats = unwrap(lines, ['BCPLQSAM'])
        self.assertEqual(heads, [(2, 'BCPLQSAM')])
        self.assertEqual(repeats['BCPLQSAM'], 0)


if __name__ == '__main__':
    unittest.main()
