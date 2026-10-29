"""Synthetic evidence checker tests cannot substitute for native JES."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    'q2mixcheck', HERE / 'check-q2-mix-evidence.py')
assert SPEC and SPEC.loader
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


def sample():
    summary = 'JOB 7001  Q2MIX\nJOB RESULT: SUCCESS\n'
    for step in C.STEPS:
        rc = 8 if step == 'BGO' else 0
        summary += f'{step:<10} PGM=*.DD RC={rc:04d}\n'
    summary += 'Statements flagged: 0\nHighest severity: 0\n'
    report = 'CROSS REFERENCE TABLE\n'
    for name, length in (
        ('R0APP', 100), ('BCPLMAIN', 200), ('RGINIT', 60),
        ('QSMDESC', 56), ('QSMDISP', 90),
        ('DMODESC', 56), ('DMODISP', 90), ('BCPLREG', 60)):
        report += f'  {name} 00000000 {length:08X}\n'
    report += 'LOCATION  REFERS TO SYMBOL\nENTRY ADDRESS 00000000\n'
    report += 'CROSS REFERENCE TABLE\n'
    report += '  Q2MVER 00000000 00000200\n'
    report += 'LOCATION  REFERS TO SYMBOL\nENTRY ADDRESS 00000000\n'
    report += '\n'.join(C.MARKERS) + '\n'
    return summary, report


class EvidenceTests(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(C.check(*sample()), [])

    def test_missing_extension_or_wrong_registry(self):
        summary, report = sample()
        self.assertTrue(C.check(summary, report.replace(
            '  DMODESC 00000000 00000038\n', '')))
        self.assertTrue(C.check(summary, report.replace(
            '  BCPLREG 00000000 0000003C\n',
            '  BCPLREG 00000000 0000002C\n')))

    def test_failures_cannot_be_marked_pass(self):
        summary, report = sample()
        self.assertTrue(C.check(summary.replace('RC=0008', 'RC=0000'), report))
        self.assertTrue(C.check(summary, report.replace(C.MARKERS[1], '')))
        self.assertTrue(C.check(summary, report.replace(
            'ENTRY ADDRESS 00000000', 'ENTRY ADDRESS 00000100', 1)))


if __name__ == '__main__':
    unittest.main()
