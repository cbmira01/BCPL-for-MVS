#!/usr/bin/env python3
"""Offline M5.2 fault-injection checks; does not submit to JES."""
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).with_name("m52-padding-negative.py")
spec = importlib.util.spec_from_file_location("m52_padding", P)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SAMPLE = """//RG124R JOB (X),'BCPL'
//* RUNTIME LIBRARY: DEVOBJ; APP ASSEMBLY ONLY
//* D3 BCPLMAIN+BCPLIO CANDIDATE: 1
//ASMAP EXEC PGM=IFOX00
//LKED EXEC PGM=IEWL
 INCLUDE OBJ(BCPLM6)
 INCLUDE OBJ(BCPLIO)
//GO EXEC PGM=*.LKED.SYSLMOD
//SYSPRINT DD SYSOUT=*
//REPORT   DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//REPORT2  DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD SYSOUT=*
//
"""


class NegativeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fb = module.positive_verifier()
        cls.original_asm = cls.fb.verifier(
            ["BCPL REPORT A", "BCPL REPORT B"], ["BCPL REPORT2 PART"])
        cls.original_deck = cls.fb.transform(SAMPLE, cls.original_asm)
        cls.neg_deck, cls.neg_asm = module.negative_variant(
            cls.original_deck.encode("ascii"), cls.original_asm.encode("ascii"))

    def test_positive_identity_and_only_one_fault(self):
        a, b = self.neg_deck.decode(), self.original_deck
        self.assertEqual(
            a.replace("//M52PAD JOB", "//M5D124B JOB", 1)
             .replace(module.INSTRUCTION + "\n", "", 1), b)
        self.assertEqual(a.count(module.INSTRUCTION), 1)

    def test_last_padding_byte_and_exact_clc(self):
        self.assertEqual(" ".encode("cp037"), b"\x40")
        self.assertEqual("X".encode("cp037"), b"\xe7")
        self.assertEqual(
            "BCPL REPORT A".encode("cp037").ljust(132, b"\x40")[-1], 0x40)
        self.assertIn("CLC   BUF1(132),EXP11", self.neg_asm.decode())
        self.assertIn("CLC   BUF2(132),EXP21", self.neg_asm.decode())

    def test_source_cannot_be_pre_modified(self):
        bad = self.original_asm.replace(
            "         OPEN  (DCB2,(INPUT))\n",
            "         OPEN  (DCB2,(INPUT))\n" + module.INSTRUCTION + "\n")
        with self.assertRaisesRegex(ValueError, "pre-mutated"):
            module.negative_variant(self.original_deck.encode(), bad.encode())

    def test_reject_wrong_job(self):
        with self.assertRaisesRegex(ValueError, "M5D124B"):
            module.negative_variant(
                self.original_deck.replace("M5D124B", "BADNAME").encode(),
                self.original_asm.encode())

    def test_reject_incorrect_dataset(self):
        with self.assertRaisesRegex(ValueError, "dataset binding"):
            module.negative_variant(
                self.original_deck.replace("&&M5RPT2", "&&WRONG2").encode(),
                self.original_asm.encode())

    def test_expected_verifier_eod_and_counts(self):
        a = self.neg_asm.decode()
        self.assertIn("EOD1     CLI   N1,X'02'", a)
        self.assertIn("EOD2     CLI   N2,X'01'", a)
        self.assertEqual(a.count("B     BAD"), 2)
        self.assertIn("DDNAME=REPORT2", a)
        self.assertIn("DDNAME=REPORT,", a)

    def test_binary_record_mutations_expected_to_differ(self):
        # Independent byte-sequence model, not an MVS assembler execution.
        expected = {
            "REPORT": [line.encode("cp037").ljust(132, b"\x40")
                       for line in ("BCPL REPORT A", "BCPL REPORT B")],
            "REPORT2": ["BCPL REPORT2 PART".encode("cp037").ljust(132, b"\x40")],
        }
        actual = {key: rows[:] for key, rows in expected.items()}
        self.assertEqual(actual, expected)
        bad = [
            {**actual, "REPORT": actual["REPORT"][:1]},  # missing
            {**actual, "REPORT": actual["REPORT"] + actual["REPORT"][:1]},  # extra
            {**actual, "REPORT": list(reversed(actual["REPORT"]))},
            {"REPORT": actual["REPORT2"], "REPORT2": actual["REPORT"]},
            {**actual, "REPORT": [bytes([actual["REPORT"][0][0] ^ 1]) +
                                  actual["REPORT"][0][1:], actual["REPORT"][1]]},
            {**actual, "REPORT": [actual["REPORT"][0][:-1] + b"\xe7",
                                  actual["REPORT"][1]]},
            {**actual, "REPORT2": [actual["REPORT2"][0][:-1]]},
            {**actual, "REPORT2": [actual["REPORT2"][0] + b"\x40"]},
        ]
        for case, candidate in enumerate(bad):
            with self.subTest(case=case):
                self.assertNotEqual(candidate, expected)


if __name__ == "__main__":
    unittest.main()
