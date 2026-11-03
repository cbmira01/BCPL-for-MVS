"""Guard System/370 R0 counter increments against LA-base-address regression."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('q1offline', HERE / 'check-q1-offline.py')
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CounterIncrementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asm = (HERE / 'bcplqsam.asm').read_text(encoding='ascii')

    def test_all_five_counters_increment_via_add(self):
        CHECK.check_counter_increments(self.asm)

    def test_each_original_la_bug_is_rejected(self):
        for name in CHECK.COUNTER_NAMES:
            good = (f'         L     0,{name}\n'
                    "         A     0,=F'1'\n"
                    f'         ST    0,{name}')
            self.assertEqual(self.asm.count(good), 1, name)
            bad = good.replace("A     0,=F'1'", 'LA    0,1(0)')
            with self.subTest(counter=name):
                with self.assertRaisesRegex(AssertionError, name):
                    CHECK.check_counter_increments(self.asm.replace(good, bad, 1))

    def test_unexpected_increment_forms_are_rejected(self):
        cases = {
            'extra legacy LA': self.asm + '\n         LA    0,1(0)\n',
            'extra ADD': self.asm + "\n         A     0,=F'1'\n",
            'wrong addend': self.asm.replace("A     0,=F'1'",
                                             "A     0,=F'2'", 1),
        }
        for label, modified in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(AssertionError):
                    CHECK.check_counter_increments(modified)


if __name__ == '__main__':
    unittest.main()
