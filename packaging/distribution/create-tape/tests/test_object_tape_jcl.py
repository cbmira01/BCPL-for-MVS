"""Offline checks for object-library tape JCL; never submit a JES job."""
from pathlib import Path
import re
import unittest

JCL = Path(__file__).resolve().parents[1] / "jcl"
NAMES = ("TO01PRE", "TO02UNLD", "TO03REST", "TO04COMP")


def body(job):
    return (JCL / f"{job}.jcl").read_text(encoding="ascii")


class ObjectTapeJCLTests(unittest.TestCase):
    def test_cards_and_review_gate(self):
        for job in NAMES:
            with self.subTest(job=job):
                source = body(job)
                self.assertTrue(source.endswith("/*\n//\n"))
                self.assertIn("SEPARATE APPROVAL", source)
                self.assertNotRegex(source, r"(?m)^//[^\s*]+\s+JOB\b")
                for n, card in enumerate(source.splitlines(), 1):
                    self.assertLessEqual(len(card), 80, (job, n))
                    self.assertNotIn("\t", card)

    def test_source_is_read_only_and_new_destinations(self):
        prepare, restore = body("TO01PRE"), body("TO03REST")
        self.assertIn("HERC02.BCPL.BOOT.OBJ,DISP=SHR", prepare)
        self.assertIn("HERC02.BCPL.TPOBJ.SRC,", prepare)
        self.assertIn("HERC02.BCPL.TPOBJ.RESTORE,", restore)
        for job in (prepare, restore):
            self.assertIn("DCB=(DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800)", job)
            self.assertIn("DISP=(NEW,CATLG,DELETE)", job)
        for job in NAMES:
            self.assertNotRegex(body(job), r"(?m)^//\S+\s+DD\s+DSN=HERC02.BCPL.BOOT.OBJ,\s*$")

    def test_tape_labels_and_file_one(self):
        unload, restore = body("TO02UNLD"), body("TO03REST")
        for deck in (unload, restore):
            self.assertIn("DSN=HERC02.BCTO01,UNIT=480", deck)
            self.assertIn("VOL=SER=BTO001,LABEL=(1,SL)", deck)
        self.assertIn("DISP=(NEW,KEEP)", unload)
        self.assertIn("DISP=OLD", restore)
        self.assertNotIn("RECFM=FB", unload)

    def test_iebbcopy_and_iebcompr_controls(self):
        for job in NAMES[:3]:
            self.assertIn("EXEC PGM=IEBCOPY", body(job))
        self.assertIn("COPY OUTDD=OUTPDS,INDD=INPDS", body("TO01PRE"))
        self.assertIn("COPY OUTDD=OUTTAPE,INDD=INPDS", body("TO02UNLD"))
        self.assertIn("COPY OUTDD=OUTPDS,INDD=INTAPE", body("TO03REST"))
        self.assertIn("EXEC PGM=IEBCOMPR", body("TO04COMP"))
        self.assertIn("COMPARE TYPORG=PO", body("TO04COMP"))

    def test_no_text_transport_or_production_writes(self):
        for job in NAMES:
            self.assertNotIn("PGM=IEBGENER", body(job))
            self.assertNotIn("DISP=MOD", body(job))
            self.assertNotIn("DSN=HERC02.BCPL.BOOT.OBJ,DISP=OLD", body(job))


if __name__ == "__main__":
    unittest.main()
