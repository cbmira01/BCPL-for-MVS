import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'reconstruction/verify.py'
spec = importlib.util.spec_from_file_location('verify_fixture', PATH)
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)


def fixture(name: str, *, omit=None, wrong_rc=None, wrong_program=None,
            interpreter_count=None, asm_severity=True, positive=True):
    lines = [f'JOB 888  {name}', '', 'STEP       PROGRAM      RESULT']
    for step in v.EXPECTED_STEPS[name]:
        if omit == step:
            continue
        program = v.EXPECTED_PROGRAMS[name].get(step, 'DYNAMIC')
        if step == wrong_program:
            program = 'BADPROG'
        lines.append(f'{step:<10} {program:<12} RC={4 if step == wrong_rc else 0:04d}')
    lines.extend(['', 'JOB RESULT: SUCCESS', 'HIGHEST RC: 0000'])
    if asm_severity:
        lines.extend(['', 'Assembler:', '  Highest severity:   0'])
    count = v.CODE_COUNTS.get(name, 0) if interpreter_count is None else interpreter_count
    report = ('INTERPRETER CODE=0\n' * count) + ('HIGHEST SEVERITY WAS 0\n' * v.ASSEMBLER_COUNTS.get(name, 0)) + '\nIEBCOMPR READBACK COMPLETE\n'
    return '\n'.join(lines) + '\n', report


class PayloadTests(unittest.TestCase):
    def test_all_seven_payloads_accept_complete_synthetic_jobs(self):
        for name in v.EXPECTED_STEPS:
            with self.subTest(job=name):
                summary, report = fixture(name)
                checked = v.verify_payload(name, 888, 777, summary, report)
                self.assertEqual(checked.job, name)
                self.assertEqual(len(checked.step_codes), len(v.EXPECTED_STEPS[name]))

    def test_icint19_cycle_count_completions_are_exact_records(self):
        actual = ('  EXECUTION CYCLES = 137316, CODE = 0\n'
                  '  EXECUTION CYCLES = 70818, CODE = 0\n'
                  '  EXECUTION CYCLES = 3290, CODE = 0\n')
        self.assertEqual(len(v.CODE_RECORD.findall(actual)), 3)
        for invalid in ('//* CODE=0', 'SOURCE: CODE=0',
                        'EXECUTION CYCLES = 3290, CODE = 4',
                        'EXECUTION CYCLES = 3290, CODE = 0 TRAILING'):
            with self.subTest(invalid=invalid):
                self.assertEqual(v.CODE_RECORD.findall(invalid), [])

    def test_cambridge_payload_accepts_cycle_count_code_records(self):
        summary, _ = fixture('CAMBBLD')
        report = ('EXECUTION CYCLES = 3290, CODE = 0\n' * 22)
        result = v.verify_payload('CAMBBLD', 888, 777, summary, report)
        self.assertEqual(result.interpreter_codes, 22)
        with self.assertRaisesRegex(v.VerificationError, '22'):
            v.verify_payload('CAMBBLD', 888, 777, summary, report.replace(
                'EXECUTION CYCLES = 3290, CODE = 0\n', '', 1))

    def test_missing_step_is_rejected_even_with_success_and_highest_zero(self):
        for name in v.EXPECTED_STEPS:
            with self.subTest(job=name):
                summary, report = fixture(name, omit=v.EXPECTED_STEPS[name][-1])
                with self.assertRaisesRegex(v.VerificationError, 'steps'):
                    v.verify_payload(name, 888, 777, summary, report)

    def test_wrong_step_program_rejected(self):
        summary, report = fixture('BCPLQSAM', wrong_program='VERIFY')
        with self.assertRaisesRegex(v.VerificationError, 'IEBCOMPR'):
            v.verify_payload('BCPLQSAM', 888, 777, summary, report)

    def test_nonzero_step_rejected(self):
        summary, report = fixture('BLDBMAIN', wrong_rc='PUTMEM')
        with self.assertRaisesRegex(v.VerificationError, 'nonzero'):
            v.verify_payload('BLDBMAIN', 888, 777, summary, report)

    def test_missing_22nd_code_zero_rejected(self):
        summary, report = fixture('CAMBBLD', interpreter_count=21)
        with self.assertRaisesRegex(v.VerificationError, '22'):
            v.verify_payload('CAMBBLD', 888, 777, summary, report)

    def test_jcl_comment_not_counted_as_interpreter_code(self):
        summary, report = fixture('CAMBBLD', interpreter_count=21)
        report += '//* BAD STEP CODE=0\n'
        with self.assertRaisesRegex(v.VerificationError, '22'):
            v.verify_payload('CAMBBLD', 888, 777, summary, report)

    def test_missing_ifox_severity_is_rejected(self):
        summary, report = fixture('BLDBMAIN', asm_severity=False)
        with self.assertRaisesRegex(v.VerificationError, 'severity'):
            v.verify_payload('BLDBMAIN', 888, 777, summary, report)

    def test_payload_job_identity_must_match(self):
        summary, report = fixture('IC19BLD')
        with self.assertRaisesRegex(v.VerificationError, 'identity'):
            v.verify_payload('IC19BLD', 889, 777, summary, report)

    def test_compare_failure_overrides_rc0(self):
        summary, report = fixture('BCPLTIME')
        with self.assertRaisesRegex(v.VerificationError, 'IEBCOMPR'):
            v.verify_payload('BCPLTIME', 888, 777, summary, report + 'DATA SETS ARE NOT EQUAL\n')

    def test_parse_submission_exact_identity(self):
        text = 'Submitted HERC02.BCPL.BOOT.JCL(BLIBBLD)\nLauncher: JOB 777\nPayload:  JOB 888\n'
        self.assertEqual(v.parse_submission(text, member='BLIBBLD'), (777, 888))
        with self.assertRaises(v.VerificationError):
            v.parse_submission(text.replace('BLIBBLD', 'CAMBBLD'), member='BLIBBLD')

    def test_extra_member_rejected(self):
        with self.assertRaisesRegex(v.VerificationError, 'inventory'):
            v.required_inventory('BOOT_OBJ', v.RUNTIME_MEMBERS | {'STALE'})

    def test_complete_cambcomp_inventory(self):
        v.required_inventory('BOOT_INTCODE_COMPLETE',
            frozenset((*v.CAMB_UNITS, 'CAMBCOMP', 'TRNILRG')))

    def test_duplicate_inventory_rejected(self):
        with self.assertRaisesRegex(v.VerificationError, 'duplicate'):
            v.inventory_members('HERC02.BCPL.BOOT.OBJ:\n    BLIB\n    BLIB\n', 'HERC02.BCPL.BOOT.OBJ')


if __name__ == '__main__':
    unittest.main()
