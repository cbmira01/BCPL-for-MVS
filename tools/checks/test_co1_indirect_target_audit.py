#!/usr/bin/env python3
"""Host-only unit tests for the CO.1 indirect CALLIND target parser."""
from pathlib import Path
import runpy
import unittest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                            'bootstrap/co1-indirect-target-audit.py'))
audit = MODULE['audit_indirect_target']
Error = MODULE['TargetAuditError']


def fixture(target='L 4,12(5)', include_other=True, after=None, change_r7=True):
    code = ['L11 EQU * ENTRY TO SUM2', 'STM 4,8,0(15)', 'BALR 6,4',
            'L12 EQU * ENTRY TO CALLIND', '         STM 4,9,0(15)',
            '         BAL 14,60(11)', '         DC A(L43) STACK FRAME SIZE',
            '         LR 5,15', '         LA 15,24(5)',
            '         LR 8,9']
    if change_r7:
        code.append('         LR 7,8')
    code.append('         ' + target)
    if after:
        code.append('         ' + after)
    code.append('         BALR 6,4')
    if include_other:
        code.extend(['L13 EQU * ENTRY TO NEST', '         L 4,123(12)',
                     '         BALR 6,4', 'L14 EQU * ENTRY TO START'])
    return '\n'.join(code) + '\n'


class TargetAuditTests(unittest.TestCase):
    def test_spilled_formal(self):
        result = audit(fixture())
        self.assertEqual(result['entry_label'], 'L12')
        self.assertIn('P!3', result['target_origin'])
        self.assertEqual(result['balr_count'], 1)

    def test_incoming_formal_register(self):
        self.assertIn('R7', audit(fixture(target='LR 4,7', change_r7=False))['target_origin'])

    def test_reject_modified_r7_formal(self):
        with self.assertRaisesRegex(Error, 'R7 formal F origin obscured'):
            audit(fixture(target='LR 4,7'))

    def test_no_following_procedure(self):
        self.assertEqual(audit(fixture(include_other=False))['balr_count'], 1)

    def test_no_callind_entry(self):
        with self.assertRaisesRegex(Error, 'ENTRY TO CALLIND'):
            audit(fixture().replace('ENTRY TO CALLIND', 'ENTRY TO OMITTED'))

    def test_duplicate_entry(self):
        with self.assertRaisesRegex(Error, 'ENTRY TO CALLIND'):
            audit(fixture() + fixture())

    def test_missing_three_formal_prologue(self):
        with self.assertRaisesRegex(Error, 'STM 4,9'):
            audit(fixture().replace('STM 4,9', 'STM 4,8'))

    def test_missing_checked_entry(self):
        with self.assertRaisesRegex(Error, 'BAL 14,60'):
            audit(fixture().replace('BAL 14,60', 'BAL 14,80'))

    def test_no_target_call(self):
        with self.assertRaisesRegex(Error, 'BALR 6,4'):
            audit(fixture().replace('         BALR 6,4\nL13 EQU', '         BCR 15,11\nL13 EQU'))

    def test_two_target_calls(self):
        with self.assertRaisesRegex(Error, 'exactly one BALR'):
            audit(fixture().replace('         BALR 6,4\nL13 EQU', '         BALR 6,4\n         BALR 6,4\nL13 EQU'))

    def test_wrong_target_register(self):
        with self.assertRaisesRegex(Error, 'formal F'):
            audit(fixture(target='LR 4,8'))

    def test_wrong_saved_formal_offset(self):
        with self.assertRaisesRegex(Error, 'formal F'):
            audit(fixture(target='L 4,16(5)'))

    def test_target_clobbered(self):
        with self.assertRaisesRegex(Error, 'formal F'):
            audit(fixture(after='LR 4,8'))

    def test_intervening_branch_rejected(self):
        with self.assertRaisesRegex(Error, 'obscures R4'):
            audit(fixture(after='B NEXT'))

    def test_intervening_multi_load_rejected(self):
        with self.assertRaisesRegex(Error, 'obscures R4'):
            audit(fixture(after='LM 4,8,0(5)'))

    def test_missing_r4_def(self):
        with self.assertRaisesRegex(Error, 'no identifiable R4'):
            audit(fixture(target='LR 3,7'))

    def test_distant_r4_def(self):
        listing = fixture().replace('         BALR 6,4\nL13 EQU',
                                    ''.join('         LR 8,8\n' for _ in range(9)) +
                                    '         BALR 6,4\nL13 EQU')
        with self.assertRaisesRegex(Error, 'too distant'):
            audit(listing)

    def test_valid_label_case(self):
        self.assertEqual(audit(fixture().replace('ENTRY TO CALLIND',
                                                 'ENTRY TO callind'))['entry_label'], 'L12')

    def test_foreign_call_ignored(self):
        self.assertEqual(audit(fixture())['call_line'], 13)


if __name__ == '__main__':
    unittest.main()
