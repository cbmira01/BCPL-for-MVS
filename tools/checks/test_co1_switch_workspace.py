#!/usr/bin/env python3
"""Source-only guards for the CO.1 switch register-save workspace fix.

IFOX/IEWL/GO remain the authority for target execution.  These checks
reject the observed 64-byte overrun pattern before JES submission.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / ('packaging/milestones/coroutines/candidates/'
              'co1-bcpl-switch/co1change.asm')


class SwitchWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ASM.read_text('ascii')
        cls.switch = cls.source.split('CO1SW    STM', 1)[1].split(
            'CO1RET BCR', 1)[0]

    def test_fixed_format_cards_and_symbols(self):
        for n, line in enumerate(self.source.splitlines(), 1):
            self.assertLessEqual(len(line), 71, (n, line))
            self.assertTrue(line.isascii())
            if line and not line.startswith((' ', '*')):
                self.assertRegex(line.split()[0],
                                 r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')

    def test_entry_r4_is_base_before_register_changes(self):
        lines = self.source.splitlines()
        ix = next(i for i,x in enumerate(lines) if x.startswith('CO1SW '))
        self.assertEqual(lines[ix-1].strip(), 'USING CO1SW,4')
        self.assertIn('STM   0,15,CO1SREG', lines[ix])
        self.assertEqual(lines[ix+1].strip(), 'DROP  4')
        self.assertIn('LR    5,15', lines[ix+2])
        self.assertIn('BALR  10,0', lines[ix+3])

    def test_static_snapshot_is_64_bytes_outside_call_workspace(self):
        self.assertIn('CO1SREG  DS    16F', self.source)
        self.assertIn('MVC   32(64,2),CO1SREG', self.switch)
        self.assertNotIn('STM   0,15,0(15)', self.source)
        self.assertNotIn('MVC   32(64,2),0(5)', self.source)
        self.assertNotIn('L     0,60(5)', self.switch)
        self.assertEqual(self.source.count('CO1SREG  DS    16F'), 1)

    def test_three_word_return_frame_is_only_caller_workspace_write(self):
        # Generated START: frame 256, switch call W=224, spare 32 bytes.
        # Generated WORKER: frame 52, switch call W=24, spare 28 bytes.
        # A 64-byte STM at W would exceed each checked frame.
        self.assertEqual(256-224, 32)
        self.assertEqual(52-24, 28)
        self.assertEqual([int(x) for x in re.findall(
            r'\bST\s+0,(\d+)\(5\)', self.switch)], [0, 4, 8])
        self.assertIn('ST    5,52(2)', self.switch)

    def test_argument_and_return_offsets_are_from_entry_image(self):
        for needle in (
            'L     0,CO1SREG+16', 'L     0,CO1SREG+20',
            'L     0,CO1SREG+24', 'L     0,CO1SREG+28',
            'L     2,CO1SREG+32', 'ST    0,60(2)',
            'ST    0,56(2)', 'LM    0,15,0(1)',
            'CO1RET BCR   15,11',
        ):
            self.assertIn(needle, self.source)
        self.assertLess(self.switch.index('L     0,CO1SREG+16'),
                        self.switch.index('L     0,CO1SREG+28'))

    def test_stack_limits_and_r0_initializer_unchanged(self):
        for needle in ('ST    0,216(12)', 'ST    0,220(12)',
                       'L     4,=A(STKLIM)', 'L     4,=A(APLIMIT)',
                       'ST    6,0(4)', 'LR    0,6',
                       'SR    7,7', 'BCR   15,11'):
            self.assertIn(needle, self.source)

    def test_private_snapshot_is_after_data_and_before_end(self):
        end = self.source.index('         END   CO1CHG')
        scratch = self.source.index('CO1SREG  DS    16F')
        base = self.source.index('CO1SW    STM')
        self.assertTrue(base < scratch < end)
        # The assembled code is much less than 4 KB from CO1SW to data.
        self.assertLess(len(self.source[base:scratch].splitlines()), 150)


if __name__ == '__main__':
    unittest.main()
