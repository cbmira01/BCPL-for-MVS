"""Offline decoder tests, including transcription of owner-supplied MVS JOB 9044."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[4] / 'tools/distribution/decode-iebptpch-readback.py'
EXCERPT = Path(__file__).resolve().parent / 'fixtures/ta0-job9044-bcpldemo-transcribed.txt'
SPEC = importlib.util.spec_from_file_location('ta0_hex_decoder', SOURCE)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
JOBLOG = '''13.25.35 JOB 9044  $HASP373 TA0READ  STARTED - INIT  1 - CLASS A - SYS TK5R
13.25.35 JOB 9044  TA0READ    TA0HEX              IEBPTPCH  RC= 0000
IEF142I TA0READ TA0HEX - STEP WAS EXECUTED - COND CODE 0000
'''
SHA256 = 'b74b12ac496437725910ce0a1edfbbd5e55cb33e5905e405b8a6820257f30ee6'


class DecodeReadback(unittest.TestCase):
    def setUp(self):
        self.text = JOBLOG + EXCERPT.read_text(encoding='utf-8')

    def check(self, text=None, **kwargs):
        return module.decode(text if text is not None else self.text, member='BCPLDEMO',
                             job=9044, expected_records=10, **kwargs)

    def test_transcribed_live_job_9044(self):
        raw, meta = self.check()
        self.assertEqual(len(raw), 800)
        self.assertEqual(meta['record_count'], 10)
        self.assertEqual(meta['block_end_records'], [10])
        self.assertEqual(meta['sha256_of_decoded_print'], SHA256)
        self.assertEqual(raw[:4], bytes.fromhex('02C5E2C4'))
        self.assertEqual(raw[-8:], bytes.fromhex('F0F0F0F0F0F0F1F0'))

    def test_early_block_boundary_is_not_end_of_member(self):
        self.check(self.text.replace('F0F0F0F1*', 'F0F0F0F1**'))

    def test_missing_eod(self):
        with self.assertRaisesRegex(module.ReadbackError, 'end-of-data'):
            self.check(self.text.replace('END OF DATA FOR SDS OR MEMBER', 'SILENT'))

    def test_incorrect_job(self):
        with self.assertRaisesRegex(module.ReadbackError, 'JES START'):
            module.decode(self.text, member='BCPLDEMO', job=9045, expected_records=10)

    def test_failed_step(self):
        with self.assertRaisesRegex(module.ReadbackError, 'RC=0000'):
            self.check(self.text.replace('RC= 0000', 'RC= 0008'))

    def test_missing_ief142i(self):
        with self.assertRaisesRegex(module.ReadbackError, 'IEF142I'):
            self.check(self.text.replace('IEF142I TA0READ', 'IEF999I TA0READ'))

    def test_wrong_member(self):
        with self.assertRaisesRegex(module.ReadbackError, 'selected member'):
            module.decode(self.text, member='BCPLTIME', job=9044, expected_records=10)

    def test_duplicate_header(self):
        with self.assertRaisesRegex(module.ReadbackError, 'exactly one'):
            self.check(self.text + '\nMEMBER NAME  BCPLDEMO\n')

    def test_missing_record_line(self):
        first = '02C5E2C4  40404040  40400030'
        with self.assertRaisesRegex(module.ReadbackError, 'first 48-byte'):
            self.check(self.text.replace(first, 'ZZZZZZZZ  40404040  40400030', 1))

    def test_truncated_record(self):
        with self.assertRaisesRegex(module.ReadbackError, 'final 32-byte'):
            self.check(self.text.replace('F0F0F0F1*', 'F0F0F0F1', 1))

    def test_missing_final_block_marker(self):
        with self.assertRaisesRegex(module.ReadbackError, 'final physical FB block'):
            self.check(self.text.replace('F0F0F1F0**', 'F0F0F1F0*'))

    def test_expected_count_larger(self):
        with self.assertRaisesRegex(module.ReadbackError, 'first 48-byte'):
            module.decode(self.text, member='BCPLDEMO', job=9044, expected_records=11)

    def test_expected_count_smaller(self):
        with self.assertRaisesRegex(module.ReadbackError, 'final physical FB block'):
            module.decode(self.text, member='BCPLDEMO', job=9044, expected_records=9)

    def test_unexpected_content_inside_record(self):
        with self.assertRaisesRegex(module.ReadbackError, 'final 32-byte'):
            self.check(self.text.replace('C4D4D6C5  D5C44040', 'PAGE 0002\nC4D4D6C5  D5C44040', 1))

    def test_page_number_between_records(self):
        data = self.text.replace('F0F0F0F1*\n02C5E2C4', 'F0F0F0F1*\n    PAGE 0002\n02C5E2C4', 1)
        self.assertEqual(self.check(data)[1]['sha256_of_decoded_print'], SHA256)

    def test_more_records_after_expected_count(self):
        data = self.text.replace('**\n                        TTTT', '**\n' + '  '.join(['00000000'] * 12) + '\n                        TTTT')
        with self.assertRaisesRegex(module.ReadbackError, 'more hexadecimal data'):
            self.check(data)

    def test_bad_iebptpch_setting(self):
        with self.assertRaisesRegex(module.ReadbackError, 'print settings'):
            self.check(self.text.replace('TOTCONV=XE', 'TOTCONV=PZ'))

    def test_output_is_private_and_never_overwritten(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea') as folder:
            root = Path(folder)
            inp = root / 'report.txt'
            dest = root / 'obj.bin'
            inp.write_text(self.text, encoding='utf-8')
            argv = [sys.executable, '-B', str(SOURCE), '--report', str(inp),
                    '--member', 'BCPLDEMO', '--job', '9044', '--expected-records', '10',
                    '--output', str(dest)]
            run = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(dest.stat().st_size, 800)
            self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
            receipt = json.loads((root / 'obj.bin.json').read_text())
            self.assertEqual(receipt['sha256_of_decoded_print'], SHA256)
            run2 = subprocess.run(argv, capture_output=True, text=True)
            self.assertNotEqual(run2.returncode, 0)
            self.assertIn('unused absolute file', run2.stderr)

    def test_fail_no_output_on_wrong_job(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea') as folder:
            root = Path(folder)
            inp = root / 'report.txt'; dest = root / 'obj.bin'
            inp.write_text(self.text, encoding='utf-8')
            argv = [sys.executable, '-B', str(SOURCE), '--report', str(inp),
                    '--member', 'BCPLDEMO', '--job', '9999', '--expected-records', '10',
                    '--output', str(dest)]
            run = subprocess.run(argv, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(dest.exists())

    def test_source_hash_is_not_claimed(self):
        self.assertIn('NOT INDEPENDENT BINARY', self.check()[1]['status'])


if __name__ == '__main__':
    unittest.main()
