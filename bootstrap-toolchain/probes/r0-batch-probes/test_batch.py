#!/usr/bin/env python3
"""Offline fixture/structure sanity only, not executable MVS evidence."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('batch', HERE / 'make-batch.py')
assert spec and spec.loader
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


def reference(selection, required):
    selected = [batch.PACKAGES[tag] for tag in selection]
    for idx, (name, maj, minor, global_no, dep) in enumerate(selected):
        if global_no in (14, 200) or not 299 <= global_no <= 305:
            return 40
        for prev in selected[:idx]:
            if prev[0] == name:
                return 28
            if prev[3] == global_no:
                return 32
        if dep:
            depname, wantmaj, wantmin = dep
            matches = [j for j, d in enumerate(selected)
                       if d[0] == depname]
            if not matches:
                return 12
            j = matches[0]
            other = selected[j]
            if other[1] != wantmaj or other[2] < wantmin:
                return 16
            if j >= idx:
                return 20
    for required_name in required:
        if required_name not in [x[0] for x in selected]:
            return 36
    return 0


class R0Batch(unittest.TestCase):
    def test_all_dependent_scenarios_are_meaningful(self):
        self.assertEqual(len(batch.CASES), 14)
        for ident, selection, requirements, expected, title in batch.CASES:
            with self.subTest(ident=ident):
                self.assertEqual(reference(selection, requirements), expected)
                self.assertLessEqual(len(selection), 3)
                self.assertLessEqual(len(requirements), 1)
                self.assertTrue(title)

    def test_relocatable_symbols_and_extents(self):
        src = batch.package_source()
        for tag, package in batch.PACKAGES.items():
            with self.subTest(package=tag):
                self.assertIn('R0'+tag+'B', src)
                self.assertIn('R0'+tag+'E', src)
                self.assertIn("DC    F'" + str(56+16*int(bool(package[4])))+"'",src)
        reg = batch.registry_source()
        self.assertEqual(reg.count("CL80'R0 D"),len(batch.CASES))
        self.assertEqual(reg.count('A(R0'), 2 * sum(len(sel) for _,sel,_,_,_ in batch.CASES))

    def test_all_asm_columns(self):
        for name in ('master.asm','dependency.asm','finalizer.asm','hooks.asm'):
            with self.subTest(name=name):
                source = batch.input_source(name)
                self.assertTrue(source)
                for line in source.splitlines():
                    if line and not line.startswith((" ", "*")):
                        self.assertLessEqual(len(line.split()[0]), 8)

    def test_one_job_and_expected_markers(self):
        cards = ["//R0BATCH JOB (BCPL),'R0 BATCH',CLASS=A,MSGCLASS=A"]
        deck = batch.make_deck(cards)
        self.assertEqual(deck.splitlines().count('/*'),7)
        self.assertEqual(deck.count('//SYSIN    DD  *'),6)
        self.assertEqual(len(batch.expected_markers()),20)
        self.assertEqual(len(set(batch.expected_markers())),20)
        self.assertIn(' ENTRY R0BM\n',deck)
        self.assertIn('COND=(0,NE,LKED)',deck)
        for line in deck.splitlines():
            self.assertTrue(line.isascii())
            self.assertLessEqual(len(line),71)

    def test_bad_job_rejected(self):
        with self.assertRaises(ValueError):
            batch.make_deck(["//WRONG   JOB (BCPL),'X'"])


if __name__=='__main__':
    unittest.main(verbosity=2)
