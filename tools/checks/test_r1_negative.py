#!/usr/bin/env python3
"""Host-only R.1 integrated negative fixture and JCL checks (not MVS)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'bootstrap-toolchain/probes/r1-registration'


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f'missing {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NegativeFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.negative = load(HERE/'make-negative-jobs.py', 'r1_negative_tests')
        cls.trailer = load(HERE.parent/'r0-export-trailer-probe/make-job.py',
                           'r1_negative_trailer_tests')

    def test_all_approved_diagnostic_ids_have_mutated_fixtures(self):
        neg = self.negative
        self.assertEqual(neg.CASES, (*range(1001, 1015), 2001))
        valid_reg = (HERE/'selected-registry.asm').read_text('ascii')
        valid_desc = (HERE/'descriptor.asm').read_text('ascii')
        for case in neg.CASES:
            with self.subTest(case=case):
                reg, desc, extra = neg.fixture(case)
                self.assertNotEqual((reg, desc, extra),
                                    (valid_reg, valid_desc, ()))
                self.assertIn('BCRGBEG', reg)
                self.assertIn('BCRGEND', reg)
                self.assertIn('R1EXBEG', desc)
                self.assertIn('R1EXEND', desc)
                self.assertTrue(reg.endswith('\n'))
                self.assertTrue(desc.endswith('\n'))
                for source in [reg, desc, *(a[2] for a in extra)]:
                    for row in source.splitlines():
                        self.assertLessEqual(len(row), 71)
                        self.assertTrue(row.isascii())
        self.assertEqual(len(neg.fixture(1011)[2]), 1)
        self.assertEqual(len(neg.fixture(1012)[2]), 1)
        self.assertEqual(len(neg.fixture(2001)[2]), 1)
        adapted = 'R1BAD    L     15,=A(IOFIN)\n'
        witness = neg.rejection_witness(adapted)
        self.assertIn('1192(12)', witness)
        self.assertIn('1196(12)', witness)
        self.assertIn("=X'C7D3F4A8'", witness)
        self.assertIn("=X'C7D3F4AC'", witness)
        self.assertIn('R1 NEGATIVE PARTIAL GLOBAL PUBLICATION', witness)
        self.assertIn('LA    15,16', witness)

    def test_each_deck_uses_temporary_objects_and_correct_job(self):
        neg = self.negative
        baseline = (ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        generated = self.trailer.sample_generated()
        for case in neg.CASES:
            with self.subTest(case=case):
                job = f'R1N{case}'
                deck = neg.make_case(
                    case, generated, baseline,
                    [f"//{job} JOB (BCPL),'NEGATIVE',CLASS=A,MSGCLASS=A"],
                    'HERC02.BCPL.BOOT.OBJ')
                rows = deck.splitlines()
                extra = case in (1011, 1012, 2001)
                self.assertEqual(rows.count('/*'), 8 if extra else 7)
                self.assertIn(f' NAME {job}(R)', rows)
                self.assertIn('//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR',
                              rows)
                self.assertTrue(all(len(r) <= 71 and r.isascii() for r in rows))
                self.assertEqual('R1LEAK' in deck, case != 2001)
                self.assertNotIn('DISP=MOD', deck)
                self.assertNotIn('BOOT.DEVOBJ', deck)
                self.assertIn(' INCLUDE OBJ(BLIB)', rows)


if __name__ == '__main__':
    unittest.main()
