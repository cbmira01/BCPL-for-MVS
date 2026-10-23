#!/usr/bin/env python3
"""R.5 non-MVS checks for the eight-member production object layout."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class R5ProductionPackaging(unittest.TestCase):
    def test_seven_assembler_and_install_steps(self):
        deck = (ROOT / "bootstrap-toolchain/jcl/bldbmain.jcl").read_text("ascii")
        asm = re.findall(r"^//(\w+)\s+EXEC PGM=IFOX00,", deck, re.M)
        put = re.findall(r"^//(\w+)\s+EXEC PGM=IEBGENER,", deck, re.M)
        self.assertEqual(asm, ["ASMMMAIN", "ASMMMEM", "ASMMBYTE", "ASMMAPT",
                               "ASMMIO", "ASMRGS", "ASMREG"])
        self.assertEqual(put, ["PUTMAIN", "PUTMEM", "PUTBYTE", "PUTAPT",
                               "PUTIO", "PUTRGS", "PUTREG"])
        for name in ("BCPLRGS", "BCPLREG"):
            self.assertIn(f"BOOT.ASM({name})", deck)
            self.assertIn(f"BOOT.OBJ({name})", deck)
        self.assertTrue(all(len(row) <= 80 and row.isascii()
                            for row in deck.splitlines()))

    def test_link_profiles_and_single_default_table(self):
        source = (ROOT / "tools/checks/prepare-runtime-pds-regression.py").read_text()
        self.assertIn("INCLUDE OBJ(BCPLRGS)", source)
        self.assertIn("INCLUDE OBJ(BCPLREG)", source)
        self.assertIn('library == "OBJ" and os.environ.get("R1_ACCEPTANCE") != "1"',
                      source)

    def test_extension_regression_keeps_application_table(self):
        source = (ROOT / "tools/checks/prepare-r5-extension-regression.py").read_text()
        self.assertIn("R5REGD", source)
        self.assertIn('t.asm_step("ASMR", "R5RGOBJ", rgs)', source)
        self.assertNotIn("INCLUDE OBJ(BCPLREG)", source)

    def test_production_wrapper(self):
        wrapper = (ROOT / "tools/bootstrap/run-production-regression").read_text()
        self.assertIn("BCPL_RUNTIME_LIBRARY=OBJ", wrapper)
        self.assertIn("BCPLRGS BCPLREG BLIB", wrapper)


if __name__ == "__main__":
    unittest.main()
