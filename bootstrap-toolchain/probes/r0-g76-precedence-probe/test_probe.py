"""Offline structural safeguards; not MVS execution evidence."""
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(filename, name):
    path = HERE / filename
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.make = load('make-job.py', 'g76make')
        cls.verify = load('verify-report.py', 'g76verify')
        cls.trailer = cls.make.load(cls.make.TRAIL, 'g76trailfixture')
        cls.asm = (HERE / 'check76.asm').read_text('ascii')

    def test_program_calls_verifier_and_emits_unique_marker(self):
        src = (HERE / 'source.bcpl').read_text('ascii')
        self.assertIn('CHECK76:151', src)
        self.assertIn('IF CHECK76() NE 0 DO STOP(8)', src)
        self.assertEqual(src.count('R0 G76 INSTALLED BLIB PASS'), 1)

    def test_generated_app_preserves_start_and_injects_only_g151(self):
        rows = self.make.application_source(self.trailer.sample_generated())
        self.assertEqual(rows.count('         EXTRN R0CK76'), 1)
        self.assertEqual(rows.count("         DC F'604'"), 1)
        self.assertIn('         DC A(R0CK76)', rows)
        helper = self.make.load(self.make.HELPER, 'g76helpcheck')
        a, maximum, pairs = helper.find_trailer(rows)
        self.assertEqual(maximum, 699 * 4)
        self.assertEqual([p[0] for p in pairs], [4, 604])
        self.assertEqual(rows.count('R0APP    CSECT'), 1)
        self.assertEqual(rows.count('         END   R0APP'), 1)

    def test_reject_application_with_unexpected_exports(self):
        generated = self.trailer.sample_generated().replace(
            '         DC    A(L999)\nL998',
            "         DC A(L999)\n         DC F'300'\n"
            '         DC    A(L999)\nL998')
        with self.assertRaisesRegex(ValueError, 'export only START'):
            self.make.application_source(generated)

    def test_reject_non_cg370_assembly(self):
        with self.assertRaises(ValueError):
            self.make.application_source('INVALID CSECT\n')

    def test_native_asm_checks_real_blib_export_and_g76(self):
        self.assertIn('         EXTRN BLIB', self.asm)
        self.assertIn('         L     8,=A(BLIB)', self.asm)
        self.assertIn("         CLC   0(4,8),=F'304'", self.asm)
        self.assertIn('R0FOUND  L     7,304(12)', self.asm)
        self.assertIn('         CR    7,4', self.asm)
        self.assertIn('R0FAIL   LA    7,8', self.asm)
        self.assertIn('         BCR   15,11', self.asm)
        self.assertNotIn('         ST    7,304(12)', self.asm)
        for index, line in enumerate(self.asm.splitlines(), 1):
            self.assertLessEqual(len(line), 71, index)

    def test_jcl_uses_only_read_only_installed_objects(self):
        jcl = self.make.make_deck(
            ["//R0G76   JOB (BCPL),'G76 PROBE',CLASS=A,MSGCLASS=A"],
            self.trailer.sample_generated(), self.asm,
            'HERC02.BCPL.BOOT.OBJ')
        self.assertIn(' INCLUDE OBJ(BCPLMAIN)', jcl)
        self.assertIn(' INCLUDE OBJ(BLIB)', jcl)
        self.assertIn(' ENTRY R0APP', jcl)
        self.assertIn(' ENTRY R0CK76', jcl)
        self.assertEqual(jcl.count('DISP=SHR'), 3)
        self.assertNotIn('BOOT.DEVOBJ', jcl)
        self.assertIn('PGM=*.LKED.SYSLMOD', jcl)
        self.assertEqual(jcl.splitlines().count('/*'), 3)

    def test_verifier_rejects_missing_and_duplicate_markers(self):
        for report in ('', 'R0 G76 WRONG PASS\n',
                       'R0 G76 INSTALLED BLIB PASS\n' * 2):
            with self.assertRaises(ValueError):
                self.verify.verify(report)
        self.verify.verify('line\nR0 G76 INSTALLED BLIB PASS  \n')


if __name__ == '__main__':
    unittest.main()
