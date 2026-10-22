#!/usr/bin/env python3
"""Host checks for the R.1 no-output normal-FINISH isolation probe."""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / 'bootstrap-toolchain/probes/r1-registration'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class NoOutputProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load(PROBE/'make-jobs.py', 'r1_no_output_builder')
        cls.trailer = load(PROBE.parent/'r0-export-trailer-probe/make-job.py',
                           'r1_no_output_trailer')

    def test_no_output_start_calls_finish_without_output(self):
        source = (PROBE/'no-output.bcpl').read_text('ascii').upper()
        self.assertIn('START:1', source)
        self.assertIn('FINISH', source)
        self.assertNotIn('WRITES', source)
        self.assertNotIn('NEWLINE', source)
        self.assertNotIn('STOP(', source)

    def test_jcl_uses_empty_registry_without_optional_dispatcher(self):
        root_src = (ROOT/'bootstrap-toolchain/asm/bcplmain.asm').read_text('ascii')
        deck = self.builder.make_deck(
            'no-output',
            ["//R1NOOUT JOB (BCPL),'NO OUTPUT',CLASS=A,MSGCLASS=A"],
            self.trailer.sample_generated(), root_src,
            'HERC02.BCPL.BOOT.OBJ')
        empty = self.builder.make_deck(
            'empty',
            ["//R1EMPTY JOB (BCPL),'NO OUTPUT',CLASS=A,MSGCLASS=A"],
            self.trailer.sample_generated(), root_src,
            'HERC02.BCPL.BOOT.OBJ')
        # Normal startup and object selection stay identical; only the
        # human-facing test identity/profile differs.
        canonical = deck.replace('R1NOOUT','R1EMPTY').replace(
            'R.1 NO-OUTPUT BCPLREG CANDIDATE',
            'R.1 EMPTY BCPLREG CANDIDATE')
        self.assertEqual(canonical,empty)
        self.assertIn('//R1NOOUT JOB ',deck)
        self.assertIn(' NAME R1NOOUT(R)',deck)
        self.assertEqual(deck.splitlines().count('/*'), 5)
        self.assertIn('//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR',deck)
        self.assertIn('BCPLREG', deck)
        self.assertNotIn('ASMD',deck)
        self.assertNotIn('ASMS',deck)
        self.assertNotIn('DISP=MOD',deck)
        for card in deck.splitlines():
            self.assertTrue(card.isascii())
            self.assertLessEqual(len(card), 71)


if __name__ == '__main__':
    unittest.main()
