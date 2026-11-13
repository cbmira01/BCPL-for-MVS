#!/usr/bin/env python3
"""Host-only structural tests for CO.1 procedure-valued BCPL call probe."""
from pathlib import Path
import runpy
import unittest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                            'bootstrap/probe-co1-indirect-entry.py'))
verify = MODULE['verify_assembler']
ProbeError = MODULE['ProbeError']


def sample(entries=4, calls=4, size=44, formals=9):
    lines = []
    for n in range(entries):
        lines.extend([
            f'         STM 4,{formals if n == 1 else 8},0(15)',
            '         BAL 14,60(11)',
            f'         DC A(L{700+n}) STACK FRAME SIZE',
        ])
    lines.append('         LA 15,20(5)')
    lines.extend(['         BALR 6,4']*calls)
    lines.append('         BCR 15,11')
    lines.extend([f'L{700+n} EQU {size} STACK FRAME SIZE' for n in range(entries)])
    return '\n'.join(lines) + '\n'


class IndirectEntryTests(unittest.TestCase):
    def test_valid(self):
        a = verify(sample())
        self.assertEqual((a['checked_entries'],a['three_formal_entries'],a['ordinary_calls']), (4,1,4))

    def test_five_entries(self):
        self.assertEqual(verify(sample(entries=5))['checked_entries'], 5)

    def test_three_entries_insufficient(self):
        with self.assertRaisesRegex(ProbeError, 'expected >=4'): verify(sample(entries=3))

    def test_missing_inline_word(self):
        with self.assertRaisesRegex(ProbeError, 'complete'): verify(sample().replace('DC A(L700)', 'DC F\'0\''))

    def test_extraneous_partial_checked_entry(self):
        with self.assertRaisesRegex(ProbeError, 'complete'): verify(sample() + '         BAL 14,60(11)\n')

    def test_counted_entry_leak(self):
        with self.assertRaisesRegex(ProbeError, 'counting service'): verify(sample() + '         BAL 14,80(11)\n')

    def test_missing_three_formals(self):
        with self.assertRaisesRegex(ProbeError, 'CALLIND'): verify(sample(formals=8))

    def test_duplicate_three_formals(self):
        with self.assertRaisesRegex(ProbeError, 'CALLIND'): verify(sample() + '         STM 4,9,0(15)\n')

    def test_insufficient_calls(self):
        with self.assertRaisesRegex(ProbeError, '>=3'): verify(sample(calls=2))

    def test_missing_return(self):
        with self.assertRaisesRegex(ProbeError, 'normal return'): verify(sample().replace('BCR 15,11', 'BCR 15,6'))

    def test_missing_workspace(self):
        with self.assertRaisesRegex(ProbeError, 'workspace'): verify(sample().replace('LA 15,20(5)', 'LR 15,5'))

    def test_missing_frame_label(self):
        with self.assertRaisesRegex(ProbeError, 'frame'): verify(sample().replace('L700 EQU 44 STACK FRAME SIZE', ''))

    def test_duplicate_frame_label(self):
        with self.assertRaisesRegex(ProbeError, 'frame'): verify(sample()+'L700 EQU 44 STACK FRAME SIZE\n')

    def test_bad_frame_alignment(self):
        with self.assertRaisesRegex(ProbeError, 'frame'): verify(sample(size=42))

    def test_zero_frame(self):
        with self.assertRaisesRegex(ProbeError, 'frame'): verify(sample(size=0))

    def test_two_digit_frame_labels(self):
        self.assertEqual(verify(sample().replace('L700','L70'))['checked_entries'],4)


if __name__ == '__main__':
    unittest.main()
