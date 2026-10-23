#!/usr/bin/env python3
"""R.4 generator-only checks; no MVS execution or credentials."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def build_module():
    spec = importlib.util.spec_from_file_location('r4_iewl_probe',
                                                  HERE / 'make-job.py')
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = build_module()

    def test_combined_has_exactly_two_csects_and_one_end(self):
        for pkg, names in (('a', ('DMODESC', 'DMODISP')),
                           ('b', ('R2BDSC', 'R2BDISP'))):
            text = self.m.combined_source(pkg)
            self.assertEqual(text.count(' CSECT'), 2)
            self.assertEqual(text.count('         END   '), 1)
            for name in names:
                self.assertIn(f'{name:<8} CSECT', text)
            self.assertNotIn('         EXTRN ' + names[1], text)

    def test_weak_symbols_are_explicit_and_all_profiles_distinct(self):
        sources = [self.m.observer(p) for p in self.m.PROFILES]
        self.assertEqual(len(set(sources)), 4)
        for profile, src in zip(self.m.PROFILES, sources):
            self.assertIn('WXTRN DMOBEG,DMOEND,DMODISP', src)
            self.assertIn('WXTRN R2BBEG,R2BEND,R2BDISP', src)
            if profile != 'zero':
                self.assertIn("C     0,=F'56'", src)
                self.assertIn("CLC   0(4,15),=CL4'BCEX'", src)
                self.assertIn('L     0,52(15)', src)
                self.assertNotIn('0(4,0)', src)
                self.assertNotIn('52(0)', src)
            self.assertNotIn('BCPLREG', src.split('R4WEAK   CSECT')[1])
            self.assertIn('         SR    15,15', src)
            self.assertIn('BAD      LA    15,12', src)

    def test_no_selected_module_automatically_enters_link(self):
        card = ["//R4WXLINK JOB (BCPL),'R4 WXTRN',CLASS=A,MSGCLASS=A"]
        deck = self.m.make_deck(card)
        lines = deck.splitlines()
        self.assertEqual(deck.count(' INCLUDE PKGA'), 2)
        self.assertEqual(deck.count(' INCLUDE PKGB'), 2)
        self.assertEqual(sum(x.startswith('//SYSLMOD') for x in lines), 4)
        self.assertEqual(deck.count('         WXTRN DMOBEG'), 4)
        self.assertEqual(lines.count('/*'), 10)
        self.assertNotIn(' INCLUDE OBJ(', deck)
        self.assertNotIn('BOOT_OBJ', '\n'.join(
            x for x in lines if x.startswith('//') and 'DD ' in x))
        self.assertNotIn('DISP=MOD', deck)
        for profile in self.m.PROFILES:
            link = self.m.LINK[profile]
            start = next(i for i,x in enumerate(lines)
                         if x.startswith(f'//{link:<8} EXEC'))
            end = next(i for i,x in enumerate(lines[start:],start)
                       if x.startswith('//SYSLMOD'))
            section = '\n'.join(lines[start:end])
            syslin_pos = section.index('//SYSLIN   DD')
            self.assertIn('//         DD  *', section[syslin_pos:])
            self.assertLess(section.index('//PKGA'), syslin_pos)
            self.assertLess(section.index('//PKGB'), syslin_pos)
            self.assertEqual(' INCLUDE PKGA' in section,
                             'a' in self.m.SELECTION[profile])
            self.assertEqual(' INCLUDE PKGB' in section,
                             'b' in self.m.SELECTION[profile])
        self.assertTrue(all(x.isascii() and len(x) <= 71
                            for x in lines))

    def test_bad_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'invalid IFOX'):
            self.m.checked_cards(' '*72, 'bad')
        with self.assertRaisesRegex(ValueError, 'JCL delimiter'):
            self.m.checked_cards('/*\n', 'bad')
        with self.assertRaisesRegex(ValueError, 'unknown profile'):
            self.m.observer('unknown')


if __name__ == '__main__':
    unittest.main()
