"""Offline, non-executing checks for first scratch-tape JCL."""
from pathlib import Path
import re
import unittest

JCL = Path(__file__).resolve().parents[1] / "jcl"
NAMES = ("TP01PRE", "TP02UNLD", "TP03REST", "TP04COMP")


def read_deck(name):
    return (JCL / f"{name}.jcl").read_text(encoding="ascii")


class ScratchTapeJclTests(unittest.TestCase):
    def test_ascii_cards_and_no_embedded_job_cards(self):
        for name in NAMES:
            with self.subTest(name=name):
                deck = read_deck(name)
                self.assertTrue(deck.endswith("/*\n//\n"))
                self.assertNotRegex(deck, r"(?m)^//[^\s*]+\s+JOB\b")
                self.assertIn("SEPARATE APPROVAL", deck)
                for number, line in enumerate(deck.splitlines(), 1):
                    self.assertLessEqual(len(line), 80, (name, number))
                    self.assertNotIn("\t", line)

    def test_source_read_only_and_scratch_outputs_new(self):
        prepare = read_deck("TP01PRE")
        restore = read_deck("TP03REST")
        self.assertIn("HERC02.BCPL.DIST.DOCS,DISP=SHR", prepare)
        self.assertIn("HERC02.BCPL.TPTEST.SRC,", prepare)
        self.assertIn("HERC02.BCPL.TPTEST.RESTORE,", restore)
        for deck in (prepare, restore):
            self.assertIn("DISP=(NEW,CATLG,DELETE)", deck)

    def test_tape_dsn_volser_labels_match(self):
        unload = read_deck("TP02UNLD")
        restore = read_deck("TP03REST")
        for deck in (unload, restore):
            self.assertIn("DSN=HERC02.BCTP01,UNIT=480", deck)
            self.assertIn("VOL=SER=BTP001,LABEL=(1,SL)", deck)
        self.assertIn("DISP=(NEW,KEEP)", unload)
        self.assertIn("DISP=OLD", restore)
        self.assertNotIn("RECFM=FB", unload)

    def test_mvs_utility_control_statements(self):
        for name in NAMES[:3]:
            self.assertIn("EXEC PGM=IEBCOPY", read_deck(name))
        self.assertIn("COPY OUTDD=OUTPDS,INDD=INPDS", read_deck("TP01PRE"))
        self.assertIn("COPY OUTDD=OUTTAPE,INDD=INPDS", read_deck("TP02UNLD"))
        self.assertIn("COPY OUTDD=OUTPDS,INDD=INTAPE", read_deck("TP03REST"))
        compare = read_deck("TP04COMP")
        self.assertIn("EXEC PGM=IEBCOMPR", compare)
        self.assertIn("COMPARE TYPORG=PO", compare)


if __name__ == "__main__":
    unittest.main()
