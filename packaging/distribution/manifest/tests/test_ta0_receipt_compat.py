"""Isolated no-MVS checks for TA.0 historical decoded-member receipt compatibility."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/distribution/ta0_receipt_compat.py'
spec = importlib.util.spec_from_file_location('ta0_receipt_compat', SOURCE)
assert spec and spec.loader
compat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compat)


def metadata(repeats=0):
    return {'member': 'BCPLTIME', 'job': 9047, 'record_count': 12,
            'record_length': 80, 'byte_count': 960,
            'block_end_records': [10, 12],
            'sha256_of_decoded_print': '2' * 64,
            'expected_records_supplied': False,
            'qualification': 'PRINT-ONLY; NO INDEPENDENT DASD BYTE OR SOURCE PROVENANCE',
            'repeated_page_headings': repeats}


class MetadataSchema(unittest.TestCase):
    def test_present_schema_unmodified(self):
        actual = metadata(5)
        self.assertEqual(compat.metadata_schema(actual, actual), 'PAGE_AWARE_V2')

    def test_real_pre_page_framing_variant(self):
        actual = metadata(0)
        before = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        self.assertEqual(compat.metadata_schema(before, actual), 'PRE_PAGE_V1')
        self.assertNotIn('repeated_page_headings', before)

    def test_missing_heading_counter_when_real_pages_exist_fails(self):
        actual = metadata(5)
        before = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        self.assertIsNone(compat.metadata_schema(before, actual))

    def test_stale_counter_fails(self):
        actual = metadata(4)
        saved = metadata(5)
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_altered_sha_never_accepted(self):
        actual = metadata()
        saved = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        saved['sha256_of_decoded_print'] = '0' * 64
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_altered_record_count_never_accepted(self):
        actual = metadata()
        saved = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        saved['record_count'] = 13
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_altered_block_boundaries_never_accepted(self):
        actual = metadata()
        saved = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        saved['block_end_records'] = [12]
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_missing_other_field_rejected(self):
        actual = metadata()
        saved = {k:v for k,v in actual.items() if k not in ('repeated_page_headings', 'job')}
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_extra_field_rejected(self):
        actual = metadata()
        saved = {**actual, 'new_metadata': 0}
        self.assertIsNone(compat.metadata_schema(saved, actual))

    def test_bad_counter_type_rejected(self):
        actual = metadata(False)
        self.assertIsNone(compat.metadata_schema(actual, actual))

    def test_negative_counter_rejected(self):
        actual = metadata(-1)
        self.assertIsNone(compat.metadata_schema(actual, actual))

    def test_non_dict_rejected(self):
        self.assertIsNone(compat.metadata_schema([], metadata()))
        self.assertIsNone(compat.metadata_schema(metadata(), None))

    def test_legacy_bool_expected_records_detected(self):
        actual = metadata()
        saved = {k:v for k,v in actual.items() if k != 'repeated_page_headings'}
        saved['expected_records_supplied'] = True
        self.assertIsNone(compat.metadata_schema(saved, actual))


if __name__ == '__main__':
    unittest.main()
