#!/usr/bin/env python3
"""Credential-free R.2 four-selection host checks; no MVS claimed."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def builder():
    spec = importlib.util.spec_from_file_location('r2_matrix',
                                                  HERE / 'make-matrix.py')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = builder()

    def test_b_is_independent_test_only_package(self):
        desc, dispatch = self.m.extension_sources()['b']
        self.assertIn("CL8'R2TESTB'", desc)
        self.assertIn("F'299',A(R2BDISP)", desc)
        self.assertIn("F'3',F'2',F'1',F'0',F'0',F'0'", desc)
        self.assertIn("F'1',F'3',F'2',F'8',F'5',F'0'", dispatch)
        self.assertIn("F'77',F'99'", dispatch)
        self.assertIn("MVC   0(32,8),BCQD", dispatch)
        self.assertLess(dispatch.index("C     9,=F'8'"),
                        dispatch.index('SLL   8,2'))
        self.assertIn('R2BSVC:299', (HERE / 'onlyb.bcpl').read_text())
        self.assertIn('R2BSVC:299', (HERE / 'both.bcpl').read_text())
        reg = (ROOT / 'packaging/global-number-registry.md').read_text()
        self.assertNotIn('**299**', reg)
        for text in (desc, dispatch):
            self.assertTrue(all(line.isascii() and len(line) <= 71
                                for line in text.splitlines()))

    def test_four_registry_selection_contracts(self):
        for profile, n, names in (
            ('zero', 0, ()), ('a', 1, ('BCPLDEMO',)),
            ('b', 1, ('R2TESTB',)),
            ('both', 2, ('BCPLDEMO', 'R2TESTB')),
        ):
            source = self.m.registry(profile)
            total = 28 + 16 * n
            self.assertIn(f"F'1',F'28',F'{total}',F'{n}',F'{n}',F'0'",
                          source)
            self.assertEqual(source.count('         DC    A('), n)
            for name in ('BCPLDEMO', 'R2TESTB'):
                self.assertEqual(f"CL8'{name}'" in source, name in names)
            self.assertTrue(all(row.isascii() and len(row) <= 71
                                for row in source.splitlines()))

    def test_one_core_object_is_shared_across_four_links(self):
        trail = self.m.load(self.m.TRAIL, 'r2_matrix_fixture')
        generated = {p: trail.sample_generated() for p in self.m.PROFILES}
        job = ["//R2MATRIX JOB (BCPL),'R2 MATRIX',CLASS=A,MSGCLASS=A"]
        deck = self.m.make_deck(generated, job, 'HERC02.BCPL.BOOT.OBJ')
        lines = deck.splitlines()
        self.assertEqual(lines.count('/*'), 18)
        self.assertEqual(sum(row.startswith('//ASMN') for row in lines), 1)
        self.assertEqual(sum(row.startswith('//ASMR') for row in lines), 1)
        self.assertEqual(sum(row.startswith('//ASG') for row in lines), 4)
        self.assertEqual(sum(row.startswith('//SYSLMOD') for row in lines),
                         4)
        self.assertEqual(sum(row.startswith('//OBJ ') for row in lines), 4)
        self.assertEqual(sum(row.startswith(' ENTRY R0APP') for row in lines),
                         4)
        self.assertEqual(sum('DISP=(OLD,PASS)' in row for row in lines),
                         24)
        self.assertIn('DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR', deck)
        self.assertNotIn('BOOT.DEVOBJ', deck)
        self.assertNotIn('DISP=MOD', deck)
        for p in self.m.PROFILES:
            start = lines.index(next(row for row in lines if row.startswith(
                f'//{self.m.LINK[p]:<8} EXEC')))
            end = lines.index(next(row for row in lines if row.startswith(
                f'//{self.m.GO[p]:<8} EXEC')))
            section = '\n'.join(lines[start:end])
            self.assertIn(f'DSN=&&{self.m.APP_OBJ[p]}', section)
            self.assertIn(f'DSN=&&{self.m.REG_OBJ[p]}', section)
            self.assertIn('DSN=&&R2NOBJ,DISP=(OLD,PASS)', section)
            self.assertIn('DSN=&&R2ROBJ,DISP=(OLD,PASS)', section)
            for pkg, objs in self.m.PKG_OBJ.items():
                for obj in objs:
                    self.assertEqual(f'DSN=&&{obj}' in section,
                                     pkg in self.m.SELECT[p])
        self.assertTrue(all(row.isascii() and len(row) <= 71
                            for row in lines))

    def test_generated_program_has_no_optional_trailer_bindings(self):
        for file in ('zero.bcpl', 'onlyb.bcpl', 'both.bcpl'):
            src = (HERE / file).read_text('ascii')
            self.assertIn('LET START() BE', src)
            self.assertNotIn('R0QA:298', src)
            self.assertNotIn('R1TEST', src)
        self.assertNotIn('R2BSVC:299', (HERE / 'zero.bcpl').read_text())
        self.assertNotIn('DEMOSVC:203', (HERE / 'zero.bcpl').read_text())


if __name__ == '__main__':
    unittest.main()
