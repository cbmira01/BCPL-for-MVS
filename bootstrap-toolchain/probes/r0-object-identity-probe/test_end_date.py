"""Negative and positive tests for the approved narrow END-date exception."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location('r0_end_date_auditor', HERE / 'audit-end-date.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def end_record(day: int) -> bytes:
    rec = bytearray(b'\x40' * 80)
    rec[:4] = bytes.fromhex('02C5D5C4')
    rec[32] = 0xF1
    rec[47:52] = f'26{day:03d}'.encode('cp037')
    rec[-8:] = b'00000018'.decode('ascii').encode('cp037')
    return bytes(rec)


def dump(label: str, record: bytes, physical=2, logical=8) -> str:
    hexdump = record.hex().upper()
    return (f'    DDNAME = {label}\n'
            f'    PHYSICAL RECORD NUMBER = {physical:08d}  LOGICAL RECORD NUMBER WITHIN PHYSICAL RECORD = {logical:08d}\n'
            f'{hexdump[:120]}\n{hexdump[120:]}\n')


def sample(a: bytes | None = None, b: bytes | None = None, count=18,
           extra='', location_a=(2, 8), location_b=(2, 8)) -> str:
    a = end_record(292) if a is None else a
    b = end_record(294) if b is None else b
    return ('IEF142I R0BIMEM ASMMEM - STEP WAS EXECUTED - COND CODE 0000\n'
            'IEF142I R0BIMEM COMPARE - STEP WAS EXECUTED - COND CODE 0008\n'
            'TOTAL RECORDS PUNCHED                        18\n'
            '                                   COMPARE UTILITY PAGE 0001\n'
            ' COMPARE TYPORG=PS\n'
            'IEB221I    RECORDS ARE NOT EQUAL\n'
            + dump('SYSUT1', a, *location_a)
            + dump('SYSUT2', b, *location_b) + extra
            + f'    END OF JOB-TOTAL NUMBER OF RECORDS COMPARED = {count:08d}\n')


class EndDayEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = staticmethod(load().audit)

    def reject(self, report, error=None):
        with self.assertRaises(ValueError) as raised:
            self.audit(report)
        if error:
            self.assertIn(error, str(raised.exception))

    def test_one_final_end_record_date_only_is_content_equal(self):
        result = self.audit(sample())
        self.assertEqual(result['classification'], 'CONTENT_EQUAL_EXCEPT_END_RUN_DAY')
        self.assertFalse(result['strict_binary_identity'])
        self.assertEqual(result['records_compared'], 18)
        self.assertEqual(result['differing_columns_1_based'], [52])
        self.assertEqual((result['installed_run_day'], result['rebuilt_run_day']), (292, 294))

    def test_any_one_or_all_three_run_day_digits_may_vary(self):
        for x,y in [(101, 102), (100, 200), (111, 222), (292,294)]:
            r=self.audit(sample(end_record(x), end_record(y)))
            self.assertTrue(r['normalized_content_identity'])

    def test_same_date_cannot_explain_reported_inequality(self):
        self.reject(sample(end_record(292),end_record(292)), 'outside allowed')

    def test_nondate_idr_changes_rejected(self):
        for index in (4,32,34,46,47,48,52,72,79):
            r=bytearray(end_record(294));r[index] ^= 1
            self.reject(sample(b=bytes(r)), 'outside allowed' if index not in (32,47,48) else None)

    def test_not_end_record_rejected(self):
        a=bytearray(end_record(292));b=bytearray(end_record(294))
        a[1:4]=b'XYZ';b[1:4]=b'XYZ'
        self.reject(sample(bytes(a),bytes(b)), 'not between OBJ END')

    def test_missing_unbounded_and_malformed_hex_rejected(self):
        s=sample()
        self.reject(s.replace('02C5D5C4', '02C5D5C', 1), 'exactly 80')
        self.reject(s.replace('02C5D5C4','02C5D5CZ',1), 'exactly 80')
        self.reject(s.replace('02C5D5C4','02C5D5C4\n',1), 'exactly 80')

    def test_more_than_one_discrepancy_rejected(self):
        self.reject(sample(extra='IEB221I    RECORDS ARE NOT EQUAL\n'), 'precisely one')

    def test_unexpected_utility_message_rejected(self):
        self.reject(sample(extra='IEB222I KEYS ARE NOT EQUAL\n'), 'precisely one')

    def test_fewer_records_than_assembler_rejected(self):
        self.reject(sample(count=17), 'compared 17 records')

    def test_not_final_record_rejected(self):
        self.reject(sample(location_b=(2,7)), 'record positions')
        self.reject(sample(location_a=(2,7),location_b=(2,7)), 'not the final')

    def test_missing_completed_comparison_rejected(self):
        self.reject(sample().replace('END OF JOB-TOTAL NUMBER OF RECORDS COMPARED', 'RECORD COUNT UNKNOWN'), 'completed-record count')

    def test_wrong_comparison_type_rejected(self):
        self.reject(sample().replace('COMPARE TYPORG=PS','COMPARE TYPORG=PO'), 'TYPORG=PS')

    def test_misleading_utility_rc8_not_accepted(self):
        self.reject(sample().replace('IEB221I    RECORDS ARE NOT EQUAL', 'IEB001I SYSUT1 NOT OPENED'))

    def test_strict_rc0_not_reclassified_as_date_exception(self):
        self.reject(sample().replace('COMPARE - STEP WAS EXECUTED - COND CODE 0008',
                                     'COMPARE - STEP WAS EXECUTED - COND CODE 0000'),
                    'no run-day exception applies')

    def test_day_must_be_valid_ebcdic_decimal(self):
        b=bytearray(end_record(294));b[50]=0x40
        self.reject(sample(b=bytes(b)), 'not EBCDIC decimal')
        b=bytearray(end_record(294));b[49:52]=b'000'.decode().encode('cp037')
        self.reject(sample(b=bytes(b)), 'outside Julian day range')

    def test_not_date_only_when_year_changes(self):
        b=bytearray(end_record(294));b[48]=0xF7
        self.reject(sample(b=bytes(b)), 'outside allowed')

    def test_unchanged_original_step_verifier_rejects_bad_rc(self):
        self.reject(sample().replace('COMPARE - STEP WAS EXECUTED - COND CODE 0008',
                                     'COMPARE - STEP WAS EXECUTED - COND CODE 0012'))


if __name__ == '__main__':
    unittest.main()
