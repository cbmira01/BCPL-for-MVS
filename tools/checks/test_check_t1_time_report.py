import importlib.util
from pathlib import Path
import unittest

NAME = Path(__file__).with_name('check-t1-time-report.py')
spec = importlib.util.spec_from_file_location('t1_report', NAME)
t1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1)


def report(demo=False, registry=44):
    entries = [('R0APP', 100), ('BCPLMAIN', 100), ('RGINIT', 100),
               ('TIMDESC', 56), ('TIMDISP', 100), ('BCPLREG', registry)]
    if demo:
        entries += [('DMODESC', 56), ('DMODISP', 100)]
    rows = '\n'.join(f'  {name} 00000000 {size:08X}'
                     for name, size in entries)
    return 'ENTRY ADDRESS 00000000\nCROSS REFERENCE TABLE\n' + rows + '\nLOCATION  REFERS TO SYMBOL\n'


class TestT1Map(unittest.TestCase):
    def test_time_alone(self):
        self.assertFalse(t1.verify(report(), 159))

    def test_both_all_orders(self):
        for n in (160, 161, 162):
            self.assertFalse(t1.verify(report(True, 60), n))

    def test_reject_extraneous_demo(self):
        self.assertTrue(t1.verify(report(True, 44), 159))

    def test_reject_missing_demo(self):
        self.assertTrue(t1.verify(report(False, 60), 160))

    def test_reject_wrong_registry_length(self):
        self.assertTrue(t1.verify(report(True, 68), 162))

    def test_reject_nonzero_entry(self):
        bad = report(True, 60).replace('ENTRY ADDRESS 00000000',
                                       'ENTRY ADDRESS 00000004')
        self.assertTrue(t1.verify(bad, 160))

    def test_reject_duplicate_section(self):
        bad = report(True, 60).replace('  TIMDESC 00000000 00000038',
                                        '  TIMDESC 00000000 00000038\n  TIMDESC 00000100 00000038')
        self.assertTrue(t1.verify(bad, 161))


if __name__ == '__main__':
    unittest.main()
