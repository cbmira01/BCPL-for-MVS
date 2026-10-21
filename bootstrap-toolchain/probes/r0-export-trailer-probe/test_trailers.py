"""Offline regression checks for the R.0 export-trailer observer utilities."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


make = load("r0_trail_make", "make-job.py")
parse = load("r0_trail_parse", "parse-report.py")


def synthetic_report(app=(1,), blib=(60, 76)):
    cards = []
    for module, numbers in (("APP", app), ("BLIB", blib)):
        cards.append(f"R0TR {module:<4} BEGIN")
        for n in numbers:
            cards.append(f"R0TR {module:<4} OFF={n*4:08X} ADDR={0x1000+n*4:08X}")
        cards.append(f"R0TR {module:<4} LIMIT={699*4:08X}")
        cards.append(f"R0TR {module:<4} END COUNT={len(numbers):08X}")
    cards.append("R0TR PASS APP AND INSTALLED BLIB")
    return "\n".join(cards) + "\n"


class GenerationTests(unittest.TestCase):
    def test_source_transform(self):
        rows = make.application_source(make.sample_generated())
        self.assertEqual(rows[0], "R0APP    CSECT")
        self.assertEqual(rows[1], "         ENTRY R0APP")
        self.assertEqual(rows[-1], "         END   R0APP")
        self.assertEqual(rows.count("         EXTRN BCPLMAIN"), 1)

    def test_reject_invalid_app(self):
        with self.assertRaisesRegex(ValueError, "L998"):
            make.application_source("         CSECT\n         EXTRN BCPLMAIN\n         END\n")
        with self.assertRaisesRegex(ValueError, "one unnamed"):
            make.application_source(make.sample_generated().replace(
                "         EXTRN BCPLMAIN", "         EXTRN OTHER"))

    def test_jcl_has_only_temporary_outputs(self):
        observer = (HERE / "trailer-observer.asm").read_text("ascii")
        deck = make.make_deck(
            ["//R0TRAIL  JOB (BCPL),'R0 TRAILER',CLASS=A,MSGCLASS=A"],
            observer, make.sample_generated(), "HERC02.BCPL.BOOT.OBJ")
        self.assertEqual(deck.count("/*\n"), 3)
        self.assertIn(" INCLUDE OBJ(BLIB)\n", deck)
        self.assertIn(" ENTRY R0TRACE\n", deck)
        self.assertNotIn("DISP=(NEW,CATLG)", deck)
        self.assertNotIn("SYSUT2   DD  DSN=", deck)
        self.assertTrue(all(len(line) <= 71 for line in deck.splitlines()))

    def test_source_cards_fit_ifox(self):
        make.checked_asm((HERE / "trailer-observer.asm").read_text("ascii"),
                         "observer")


class ParsingTests(unittest.TestCase):
    def test_two_actual_exports(self):
        data = parse.parse_report(synthetic_report())
        self.assertEqual(len(data["application"]["exports"]), 1)
        self.assertEqual(len(data["installed_blib"]["exports"]), 2)
        self.assertEqual(data["blib_core_direct_potential_overlaps"], [76])
        self.assertFalse(data["production_registration_test"])

    def test_actual_overlap_reported_not_waived(self):
        data = parse.parse_report(synthetic_report(app=(1, 76)))
        self.assertEqual(data["app_blib_overlaps"], [76])

    def test_reject_incomplete(self):
        with self.assertRaisesRegex(ValueError, "missing/out-of-order"):
            parse.parse_report(synthetic_report().replace(
                "R0TR BLIB END COUNT=00000002\n", ""))

    def test_reject_bad_count(self):
        with self.assertRaisesRegex(ValueError, "count mismatch"):
            parse.parse_report(synthetic_report().replace(
                "END COUNT=00000002", "END COUNT=00000003"))

    def test_reject_duplicate(self):
        with self.assertRaisesRegex(ValueError, "duplicate actual"):
            parse.parse_report(synthetic_report(blib=(76, 76)))

    def test_reject_unaligned(self):
        with self.assertRaisesRegex(ValueError, "invalid exported"):
            parse.parse_report(synthetic_report().replace("OFF=000000F0", "OFF=000000F1"))

    def test_reject_invalid_trailer(self):
        report = synthetic_report().replace("R0TR BLIB LIMIT=00000AEC",
                                            "R0TR BLIB ERROR INVALID TRAILER")
        with self.assertRaisesRegex(ValueError, "observer diagnosed"):
            parse.parse_report(report)

    def test_reject_unverified_pass(self):
        with self.assertRaisesRegex(ValueError, "missing/out-of-order"):
            parse.parse_report(synthetic_report().replace(
                "R0TR PASS APP AND INSTALLED BLIB", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
