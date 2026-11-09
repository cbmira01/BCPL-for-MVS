#!/usr/bin/env python3
"""Offline structure checks for R.0 test-only fixture and JCL generation."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r0_probe_builder', HERE / 'make-jobs.py')
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FixtureTests(unittest.TestCase):
    def test_all_profiles_have_valid_sources_and_jcl(self) -> None:
        for p, (name, code, marker) in m.PROFILES.items():
            with self.subTest(profile=p):
                card = [f"//{name:<8} JOB (BCPL),'R0 PROBE',CLASS=A"]
                deck = m.make_deck(p, card)
                cards = deck.splitlines()
                self.assertEqual(cards.count('/*'), 5)
                self.assertEqual(deck.count('//SYSIN    DD  *'), 4)
                self.assertEqual(cards[-1], '//')
                self.assertIn(marker, deck)
                self.assertIn(f"EXPECT   DC    F'{code}'", deck)
                self.assertEqual(deck.count('DSN=&&R0DOBJ,DISP=(OLD,DELETE)'), 1)
                self.assertEqual(deck.count('DSN=&&R0ROBJ,DISP=(OLD,DELETE)'), 1)
                self.assertEqual(deck.count('DSN=&&R0POBJ,DISP=(OLD,DELETE)'), 1)
                self.assertEqual(deck.count('DSN=&&R0FOBJ,DISP=(OLD,DELETE)'), 1)
                self.assertEqual(deck.count('DC    A(R0PB)'), 1)
                self.assertEqual(deck.count('DC    A(R0PE)'), 1)
                for line in cards:
                    self.assertLessEqual(len(line), 71)
                    self.assertTrue(line.isascii())

    def test_explicit_positive_and_negative_geometry(self) -> None:
        for p in m.PROFILES:
            reg = m.registry_source(p)
            pkg = m.package_source(p)
            self.assertIn("DC    F'28'", reg)
            self.assertIn("DC    CL8'PACKA   '", pkg)
            self.assertEqual(pkg.count('DC    A(R0FUNC)'), 3 if p == 'duplicate' else 2)
            self.assertEqual("DC    F'64'" in pkg, p == 'duplicate')
            self.assertEqual("DC    F'40'" in reg, p == 'badlen')
            self.assertEqual("DC    F'2'" in reg, p == 'badversion')
            self.assertEqual("DC    F'14'" in pkg, p == 'corecollision')
            self.assertEqual("DC    CL8'PACKB   '" in reg, p == 'missingreq')

    def test_bad_jobcards_rejected(self) -> None:
        for card in ('//R0VALID JOB (BCPL)', '//WRONG    JOB (BCPL)', ''):
            with self.subTest(card=card), self.assertRaises(ValueError):
                m.make_deck('valid', [card])

    def test_unknown_profile_rejected(self) -> None:
        with self.assertRaises(ValueError):
            m.make_deck('garbage', ["//R0VALID  JOB (BCPL),'X'"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
