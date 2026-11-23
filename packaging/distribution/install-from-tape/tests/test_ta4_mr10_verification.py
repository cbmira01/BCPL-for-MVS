"""Isolated positive/refusal tests; never contact Git, Hercules or MVS."""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import unittest
from unittest.mock import patch
import tempfile

SCRIPT = (Path(__file__).resolve().parents[1] / 'scripts/ta4-mr10-verification')
loader = SourceFileLoader('ta4_verifier_test', str(SCRIPT))
spec = spec_from_loader(loader.name, loader)
ta4 = module_from_spec(spec)
spec.loader.exec_module(ta4)


def suite(selection):
    head = ''.join(f'//S{label} EXEC PGM=IEBGENER\n' for label in ('SYNI', 'TRNI', 'CGI', 'BLIBI', 'ICLIB'))
    middle = ''.join(
        f'//* CASE {n:02d}: {member}\n'
        f'//C{n:02d}A EXEC PGM=ICINT19\n'
        f'//SYSIN DD DSN={ta4.CANON}LANGDEMO({member})\n'
        f'//G{n:02d}A EXEC PGM=ICINT19\n'
        for n, member in enumerate(selection, 1))
    extras = ''
    if len(selection) == 17:
        extras = ''.join(f'//C{n:02d}B EXEC PGM=ICINT19\n'
                         f'//G{n:02d}B EXEC PGM=ICINT19\n'
                         for n in (7, 12, 17))
    runs = ''.join(f'//* EXECUTE CASE {n:02d}: {member}\n'
                   f'//R{n:02d} EXEC PGM=ICINT19\n'
                   f'//STEPLIB DD DSN={ta4.CANON}LOAD\n'
                   for n, member in enumerate(selection, 1))
    return head + middle + extras + runs + '//SYSUT2 DD DSN=&&TEMP,DISP=(NEW,PASS)\n//\n'


def source():
    return (f'//ASM EXEC PGM=IFOX00\n//SYSIN DD DSN={ta4.CANON}ASM(ICINT19)\n'
            '//LKED EXEC PGM=IEWL\n'
            f'//SYSLMOD DD DSN={ta4.CANON}LOAD,DISP=SHR\n'
            f'//SAVEOBJ EXEC PGM=IEBGENER\n//SYSUT2 DD DSN={ta4.CANON}OBJ(ICINT19)\n')


def smoke():
    return ('//* TA3GO\n' + ''.join(f'//S{x} EXEC PGM=IEBGENER\n'
            for x in ('SYNI', 'TRNI', 'CGI', 'BLIBI', 'ICLIB')) +
            '//C01A EXEC PGM=ICINT19\n//STEPLIB DD DSN=<INST>.MR10KIT.LOAD\n'
            '//G01A EXEC PGM=ICINT19\n//STEPLIB DD DSN=<INST>.MR10KIT.LOAD\n'
            '//R01 EXEC PGM=ICINT19\n//STEPLIB DD DSN=<INST>.MR10KIT.LOAD\n'
            '//SYSIN DD DSN=<INST>.MR10KIT.TESTS(SCALVEC)\n//\n')


class TestJclContract(unittest.TestCase):
    def test_build_isolated(self):
        result = ta4.build_body(source())
        self.assertEqual(ta4.STEP.findall(result), [('ALLOC', 'IEFBR14'),
                         ('ASM', 'IFOX00'), ('LKED', 'IEWL'),
                         ('SAVEOBJ', 'IEBGENER')])
        self.assertEqual(result.count('DISP=(NEW,CATLG,DELETE)'), 2)
        self.assertIn(ta4.INST + 'ASM(ICINT19)', result)
        self.assertIn(ta4.LOAD + ',DISP=SHR', result)
        self.assertIn(ta4.OBJ + '(ICINT19)', result)
        self.assertNotIn(ta4.CANON, result)

    def test_build_rejects_missing_source(self):
        with self.assertRaises(ta4.Refusal):
            ta4.build_body(source().replace('ASM(ICINT19)', 'ASM(OLD)'))

    def test_build_rejects_extra_step(self):
        with self.assertRaises(ta4.Refusal):
            ta4.build_body(source() + '//EXTRA EXEC PGM=IEFBR14\n')

    def test_build_rejects_extra_load_member(self):
        with self.assertRaises(ta4.Refusal):
            ta4.build_body(source() + f'//X DD DSN={ta4.CANON}LOAD,DISP=SHR\n')

    def test_language_selection(self):
        result, steps = ta4.suite_body(suite(ta4.LANG), ta4.LANG, 11)
        self.assertEqual(len(steps), 38)
        self.assertEqual([n for n, _ in steps if n.startswith('R')],
                         [f'R{i:02d}' for i in range(1, 12)])
        self.assertNotIn(ta4.CANON, result)
        self.assertEqual(result.count('//\n'), 1)

    def test_bcpl_selection_and_extra_modules(self):
        result, steps = ta4.suite_body(suite(ta4.BCPL), ta4.BCPL, 17)
        self.assertEqual(len(steps), 62)
        self.assertIn('//C17B EXEC PGM=ICINT19', result)

    def test_selection_drift(self):
        bad = suite(ta4.LANG).replace('CASE 04: TABVECT', 'CASE 04: WRONG')
        with self.assertRaises(ta4.Refusal):
            ta4.suite_body(bad, ta4.LANG, 11)

    def test_missing_demo_step(self):
        bad = suite(ta4.LANG).replace('//G11A EXEC PGM=ICINT19\n', '')
        with self.assertRaises(ta4.Refusal):
            ta4.suite_body(bad, ta4.LANG, 11)

    def test_no_persistent_demo_write(self):
        with self.assertRaises(ta4.Refusal):
            ta4.suite_body(suite(ta4.LANG) + '//X DD DISP=(NEW,CATLG,DELETE)\n', ta4.LANG, 11)

    def test_smoke_rebuilt_load_only(self):
        result, steps = ta4.smoke_body(smoke())
        self.assertEqual(len(steps), 8)
        self.assertEqual(result.count('DSN=' + ta4.LOAD), 3)
        self.assertIn(ta4.INST + 'TESTS(SCALVEC)', result)
        self.assertNotIn('<INST>', result)

    def test_smoke_requires_three_loads(self):
        with self.assertRaises(ta4.Refusal):
            ta4.smoke_body(smoke().replace('<INST>.MR10KIT.LOAD', 'WRONG', 1))

    def test_overlong_jcl(self):
        with self.assertRaises(ta4.Refusal):
            ta4.cards('//SYSIN DD DSN=' + 'A'*70 + '\n')

    def test_overlong_comment(self):
        ta4.cards('//*' + 'A'*76 + '\n')
        with self.assertRaises(ta4.Refusal):
            ta4.cards('//*' + 'A'*78 + '\n')

    def test_embedded_job_card(self):
        with self.assertRaises(ta4.Refusal):
            ta4.cards('//T4R1BCD JOB CLASS=A\n')

    def test_unresolved_placeholder(self):
        with self.assertRaises(ta4.Refusal):
            ta4.cards('//X DD DSN=<INST>.MR10KIT.LOAD\n')

    def test_interpreted_codes(self):
        report = 'EXECUTION CYCLES = 42, CODE = 0\n' * 3
        self.assertEqual(ta4.verify_codes(report, 3), [0, 0, 0])
        with self.assertRaises(ta4.Refusal):
            ta4.verify_codes(report, 4)
        with self.assertRaises(ta4.Refusal):
            ta4.verify_codes(report + 'EXECUTION CYCLES = 42, CODE = 1\n', 4)

    def test_demo_semantics(self):
        report = 'EXECUTION CYCLES = 42, CODE = 0\n' * 33
        report += ''.join(f'DEMO: finished {case}\n' for case in ta4.LANG)
        data = ta4.verify_demos(report, ta4.LANG,
                                 [('X', 'ICINT19')] * 33)
        self.assertEqual(len(data['demo_print_records']), 11)
        with self.assertRaises(ta4.Refusal):
            ta4.verify_demos(report.replace('DEMO: finished DECLS', 'ERROR'),
                             ta4.LANG, [('X', 'ICINT19')] * 33)

    def test_default_plan_has_no_mvs_side_effects(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4]) as temp:
            with patch.object(ta4, 'MARKER', Path(temp) / 'absent.json'), \
                 patch.object(ta4, 'plan', return_value={'synthetic': ('//\n', [])}), \
                 patch.object(ta4, 'load_tools', side_effect=AssertionError('unexpected MVS')):
                self.assertEqual(ta4.run('plan'), 0)


if __name__ == '__main__':
    unittest.main()
