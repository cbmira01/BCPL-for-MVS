#!/usr/bin/env python3
"""Offline contract/safety tests for the T.0 JCL generator (no MVS)."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "prepare_bcpltime_t0", HERE / "prepare-bcpltime-t0.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class T0JobGenerationTests(unittest.TestCase):
    def setUp(self):
        self.sample = mod.trailer_helper().sample_generated()
        self.job = ["//T0TIME JOB (BCPL),'OFFLINE',CLASS=A"]
        self.obj = "HERC02.BCPL.BOOT.OBJ"

    def test_single_temporary_job_with_correct_link_inputs(self):
        deck = mod.make_deck(self.sample, self.job, self.obj)
        self.assertEqual(deck.count("/*\n"), 6)
        for step in ("ASMA", "ASMN", "ASMR", "ASMT", "ASMG",
                     "LKED", "GO"):
            self.assertIn(f"//{step:<8} EXEC", deck)
        self.assertIn("//TIMEOBJ  DD  DSN=&&T0TMOBJ,DISP=(OLD,PASS)", deck)
        self.assertIn("//OBJ      DD  DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR", deck)
        self.assertIn("BCXREQ BCPLTIME", deck)
        self.assertIn("&BXCLIB  SETC  'TIMEOBJ'", deck)
        self.assertIn(" ENTRY R0APP", deck)
        self.assertIn(" NAME T0TIME(R)", deck)
        self.assertIn("TIME  DEC", deck)
        self.assertIn("STCK  CLKBUF", deck)
        for part in ("BOOT_OBJ", "EXTLIB", "DISP=MOD", "CATLG"):
            # BOOT_OBJ may be mentioned in a read-only JCL comment only.
            if part != "BOOT_OBJ":
                self.assertNotIn(part, deck)
        for row in deck.splitlines():
            self.assertTrue(row.isascii())
            self.assertLessEqual(len(row), 71)
        self.assertNotIn("PASSWORD=", deck)

    def test_invalid_job_card_fails_closed(self):
        with self.assertRaises(ValueError):
            mod.make_deck(self.sample, ["//WRONG JOB (BCPL)"], self.obj)

    def test_invalid_dataset_name_fails_closed(self):
        with self.assertRaises(ValueError):
            mod.make_deck(self.sample, self.job, "HERC02.BCPL.OBJ,DISP=OLD")

    def test_poisoned_generated_source_fails_closed(self):
        with self.assertRaises(ValueError):
            mod.make_deck(self.sample + "//EVIL JOB\n", self.job, self.obj)


if __name__ == "__main__":
    unittest.main()
