#!/usr/bin/env python3
"""Host-only tests for source-independent CALLIND prologue identification."""
import importlib.util
from pathlib import Path
import unittest

TARGET = Path(__file__).resolve().parents[1] / 'bootstrap/co1-indirect-target-audit.py'
spec = importlib.util.spec_from_file_location('co1audit', TARGET)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)
verify = audit_module.audit_indirect_target
Error = audit_module.TargetAuditError


def fixture(*, label=True, target='L 4,12(5)', after='', r7_modified=True,
            second_entry=True, before_call='', between_prologues='', name_sep=False):
    a = ["L10 EQU * ENTRY TO SUM2", '         STM 4,8,0(15)',
         '         BAL 14,60(11)', '         DC A(L70) STACK FRAME SIZE',
         '         LA 15,16(5)', '         BALR 6,4', '         BCR 15,11']
    if label:
        a.append('L11 EQU * ENTRY TO CALLIND' if not name_sep else 'L11 EQU * ENTRY TO')
        if name_sep:
            a.append('CALLIND')
    a.extend(['         STM 4,9,0(15)',
              '         BAL 14,60(11)',
              '         DC A(L71) STACK FRAME SIZE',
              '         LR 5,15',
              '         LA 15,24(5)',
              '         LR 8,9'])
    if r7_modified:
        a.append('         LR 7,8')
    a.extend(between_prologues.splitlines())
    a.append('         ' + target)
    a.extend(before_call.splitlines())
    if after:
        a.append('         ' + after)
    a.extend(['         BALR 6,4', '         BCR 15,11'])
    if second_entry:
        a.extend(['L12 EQU * ENTRY TO NEST', '         STM 4,8,0(15)',
                  '         BAL 14,60(11)', '         DC A(L72) STACK FRAME SIZE',
                  '         LA 15,24(5)', '         BALR 6,4',
                  '         BCR 15,11'])
    return '\n'.join(a) + '\n'


class AuditTests(unittest.TestCase):
    def test_reproduce_failed_name_assumption(self):
        result = verify(fixture(label=False))
        self.assertEqual(result['name_labels_found'], 2)
        self.assertIn('unique STM', result['identification'])
        self.assertEqual(result['balr_count'], 1)

    def test_separate_name_line(self):
        result = verify(fixture(name_sep=True))
        self.assertIn('P!3', result['target_origin'])

    def test_standard_name(self):
        self.assertEqual(verify(fixture())['name_labels_found'], 3)

    def test_spilled_target(self):
        self.assertIn('12(R5)', verify(fixture())['target_origin'])

    def test_unmodified_r7(self):
        self.assertIn('R7', verify(fixture(target='LR 4,7', r7_modified=False))['target_origin'])

    def test_modified_r7_fails(self):
        with self.assertRaisesRegex(Error, 'R7 origin changed'):
            verify(fixture(target='LR 4,7'))

    def test_missing_three_arg(self):
        with self.assertRaisesRegex(Error, 'one three-formal'):
            verify(fixture().replace('STM 4,9,0(15)', 'STM 4,8,0(15)'))

    def test_duplicate_three_arg(self):
        with self.assertRaisesRegex(Error, 'one three-formal'):
            verify(fixture()+'STM 4,9,0(15)\n')

    def test_missing_checked(self):
        with self.assertRaisesRegex(Error, 'adjacent checked'):
            verify(fixture().replace('BAL 14,60(11)\n         DC A(L71)', 'BAL 14,80(11)\n         DC A(L71)'))

    def test_missing_frame(self):
        with self.assertRaisesRegex(Error, 'adjacent checked'):
            verify(fixture().replace('DC A(L71) STACK FRAME SIZE', "DC F'0'"))

    def test_misordered_checked(self):
        with self.assertRaisesRegex(Error, 'adjacent checked'):
            verify(fixture().replace('STM 4,9,0(15)\n         BAL 14', 'STM 4,9,0(15)\n LR 5,15\n         BAL 14'))

    def test_return_missing(self):
        with self.assertRaisesRegex(Error, 'one CALLIND normal return'):
            verify(fixture().replace('BALR 6,4\n         BCR 15,11\nL12', 'BALR 6,4\n         LR 5,5\nL12'))

    def test_double_return(self):
        with self.assertRaisesRegex(Error, 'one CALLIND normal return'):
            verify(fixture().replace('BALR 6,4\n         BCR 15,11\nL12', 'BALR 6,4\n BCR 15,11\n BCR 15,11\nL12'))

    def test_missing_target_call(self):
        with self.assertRaisesRegex(Error, 'one BALR'):
            verify(fixture().replace('L 4,12(5)\n         BALR 6,4', 'L 4,12(5)\n         LR 2,2'))

    def test_two_calls_in_target(self):
        with self.assertRaisesRegex(Error, 'one BALR'):
            verify(fixture().replace('L 4,12(5)\n         BALR 6,4', 'L 4,12(5)\n BALR 6,4\n BALR 6,4'))

    def test_wrong_target_register(self):
        with self.assertRaisesRegex(Error, 'not traced'):
            verify(fixture(target='LR 4,8'))

    def test_wrong_stack_offset(self):
        with self.assertRaisesRegex(Error, 'not traced'):
            verify(fixture(target='L 4,16(5)'))

    def test_target_clobber(self):
        with self.assertRaisesRegex(Error, 'not traced'):
            verify(fixture(after='LR 4,8'))

    def test_hidden_lm(self):
        with self.assertRaisesRegex(Error, 'R4 origin obscured'):
            verify(fixture(after='LM 4,8,0(5)'))

    def test_control_transfer_after_target(self):
        with self.assertRaisesRegex(Error, 'unexpected control transfer'):
            verify(fixture(after='B OTHER'))

    def test_control_transfer_before_target(self):
        with self.assertRaisesRegex(Error, 'unexpected control transfer'):
            verify(fixture(before_call=' B OTHER\n'))

    def test_distant_target(self):
        with self.assertRaisesRegex(Error, 'too distant'):
            verify(fixture(after='LR 8,8\n' * 10))

    def test_ignored_other_procedure_calls(self):
        self.assertEqual(verify(fixture())['balr_count'], 1)

    def test_no_following_procedure(self):
        self.assertEqual(verify(fixture(second_entry=False))['balr_count'], 1)

    def test_bounded_by_next_prologue(self):
        with self.assertRaisesRegex(Error, 'normal return'):
            verify(fixture().replace('BALR 6,4\n         BCR 15,11\nL12', 'BALR 6,4\nL12'))


if __name__ == '__main__':
    unittest.main()
