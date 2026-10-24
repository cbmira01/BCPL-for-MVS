#!/usr/bin/env python3
"""Offline positive/negative IEWL MAP parser tests; no JES activity."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'check_bcpltime_t0_report', HERE / 'check-bcpltime-t0-report.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MAP = '''IEWL MAP
 ENTRY ADDRESS       00000000
 CROSS REFERENCE TABLE
  R0APP      00000000 00000100
  BCPLMAIN   00000100 00000800
  RGINIT     00000900 000001A0
  BCPLREG    00000B00 0000002C
  TIMDESC    00000C00 00000038
  TIMDISP    00000D00 00000124
 LOCATION  REFERS TO SYMBOL
 END
'''

class ReportTests(unittest.TestCase):
    def test_valid_link(self):
        self.assertEqual(mod.verify(MAP), [])

    def test_required_descriptor_and_registry(self):
        self.assertTrue(any('TIMDESC' in s for s in mod.verify(
            MAP.replace('TIMDESC', 'BADCODE'))))
        self.assertTrue(any('44 bytes' in s for s in mod.verify(
            MAP.replace('0000002C', '00000024'))))

    def test_entry_and_absent_extension(self):
        self.assertTrue(mod.verify(MAP.replace('00000000\n CROSS',
                                               '00000010\n CROSS')))
        self.assertTrue(any('BCPLDEMO' in s for s in mod.verify(
            MAP.replace(' LOCATION',
                        '  DMODISP    00001100 00000010\n LOCATION'))))

    def test_no_map(self):
        self.assertTrue(mod.verify('no IEWL report'))

if __name__ == '__main__':
    unittest.main()
