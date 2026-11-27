#!/usr/bin/env python3
"""DR.5 installed QSAM adapter: actual macro streams, not stripped fixtures."""
import contextlib
import io
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = runpy.run_path(str(ROOT / "tools/checks/qsam-installed-mode.py"))
BCX = ROOT / "system-extensions/bcx"
QSAM = ROOT / "system-extensions/bcplqsam"


def macro_stream(mixed=False):
    prefix = "q2-mix" if mixed else "q1"
    return [line for path in (BCX / "BCXPRE.asm",
                              QSAM / (prefix + "-catalog.asm"),
                              QSAM / (prefix + "-selection.asm"),
                              BCX / "BCXPOST.asm")
            for line in path.read_text("ascii").splitlines()]


class MacroStreamTests(unittest.TestCase):
    def test_real_macro_prototypes_are_not_invocations(self):
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                rows = macro_stream(mixed)
                self.assertIn("         BCXREQ &PKG", rows)
                expected = ["         BCXREQ BCPLQSAM"]
                if mixed:
                    expected.append("         BCXREQ BCPLDEMO")
                expected += ["         BCXEND", "         END   BCPLREG"]
                self.assertEqual(ADAPTER["macro_invocations"](rows), expected)

    def test_malformed_definition_boundaries_rejected(self):
        for cards in (["         MEND"], ["         MACRO"],
                      ["         MACRO", "         MACRO", "         MEND"]):
            with self.subTest(cards=cards), self.assertRaises(ValueError):
                ADAPTER["macro_invocations"](cards)

    def test_extra_top_level_selection_is_visible(self):
        rows = macro_stream()
        rows.insert(-2, "         BCXSEL BCPLTIME")
        self.assertIn("         BCXSEL BCPLTIME",
                      ADAPTER["macro_invocations"](rows))


class IntegratedDeckTests(unittest.TestCase):
    def test_all_fourteen_actual_generators_both_modes(self):
        runner = runpy.run_path(str(ROOT / "tools/checks/run-q2-qsam-regression.py"))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(runner["check"](), 0)
        self.assertEqual(output.getvalue().count("CHECK "), 15)
        self.assertIn("QSAM dual-mode synthetic JCL CHECK PASS (14 cases; no MVS)",
                      output.getvalue())


if __name__ == "__main__":
    unittest.main()
