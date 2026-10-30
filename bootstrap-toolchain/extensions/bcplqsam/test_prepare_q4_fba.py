#!/usr/bin/env python3
"""Offline Q.4 FBA generator tests; never submit JES or allocate MVS data."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def module():
    spec = importlib.util.spec_from_file_location(
        "test_q4_fba_generator", HERE / "prepare-q4-fba.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Q.4 FBA generator missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestQ4FBAGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = module()
        cls.p = cls.m.punch_helper()
        cls.t0 = cls.p.query_helper().time_helper()
        cls.generated = cls.t0.trailer_helper().sample_generated()
        cls.jobcard = ["//Q4FBA JOB (BCPL),'Q4 FBA CHECK',CLASS=A"]
        cls.obj = "HERC02.BCPL.BOOT.OBJ"

    def deck(self):
        return self.m.make_deck(self.generated, self.jobcard,
                                self.obj).splitlines()

    def test_synthetic_deck(self):
        rows = self.deck()
        self.assertEqual(rows.count("//Q4PRINT  DD  SYSOUT=A,"), 1)
        self.assertEqual(rows.count(self.m.FBA133), 3)
        self.assertIn(" ENTRY Q4FAV", rows)
        self.assertIn(" NAME Q4FBA(R)", rows)
        # IFOX requires a temporary SYSPUNCH DD for its object deck.
        self.assertEqual(
            rows.count("//SYSPUNCH DD  DSN=&&Q1REGD,UNIT=SYSDA,"), 1)
        self.assertNotIn("//SYSPUNCH DD  SYSOUT=B,", rows)
        self.assertEqual(rows[-1], "//")

    def test_printer_renaming_is_rejected(self):
        rows = self.deck()
        rows[rows.index("//Q4PRINT  DD  SYSOUT=A,")] = (
            "//Q4PRINT  DD  SYSOUT=B,")
        with self.assertRaises(ValueError):
            self.m.verify(rows)

    def test_temporary_geometry_change_is_rejected(self):
        rows = self.deck()
        at = rows.index(self.m.temp_dd(True)[0])
        rows[at + 2] = (
            "//             DCB=(RECFM=FB,LRECL=133,BLKSIZE=133)")
        with self.assertRaises(ValueError):
            self.m.verify(rows)

    def test_permanent_allocation_is_rejected(self):
        rows = self.deck()
        rows.insert(-1, "//BAD      DD  DISP=MOD")
        with self.assertRaises(ValueError):
            self.m.verify(rows)

    def test_card_width_violation_is_rejected(self):
        rows = self.deck()
        rows.insert(-1, "//*" + "X" * 72)
        with self.assertRaises(ValueError):
            self.m.verify(rows)

    def test_ascii_source_widths(self):
        for name, width in (("test-q4-fba.bcpl", 80),
                            ("q4-fba-verify.asm", 71)):
            lines = (HERE / name).read_text(encoding="ascii").splitlines()
            self.assertTrue(lines)
            self.assertTrue(all(len(line) <= width for line in lines))

    def test_asa_vector(self):
        prefix = "Q4FBA00".encode("cp037")
        for i, asa in enumerate((0x40, 0xF0, 0xF1)):
            expected = bytearray(b"\x40" * 133)
            expected[0] = asa
            expected[1:8] = prefix
            expected[8] = 0xF1 + i
            if i == 1:
                expected[132] = 0xE7
            if i == 2:
                expected[132] = 0xE8
            self.assertEqual(expected[1:9].decode("cp037"),
                             f"Q4FBA00{i + 1}")
            self.assertEqual(len(expected), 133)


if __name__ == "__main__":
    unittest.main()
