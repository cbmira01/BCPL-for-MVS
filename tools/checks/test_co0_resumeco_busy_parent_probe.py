#!/usr/bin/env python3
"""Offline CO.0 busy-parent probe checks; no JES submission."""

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT / "mr10-kit-compiler/tests/10-coroutines"
    / "resumeco-busy-parent-co0-probe.bcpl"
)
MODULES = (
    ROOT / "mr10-kit-compiler/library/getvec-freevec.bcpl",
    ROOT / "mr10-kit-compiler/library/coroutines.bcpl",
)


class BusyParentProbeTests(unittest.TestCase):
    def test_probe_is_bounded_and_uses_canonical_interfaces(self):
        source = SOURCE.read_text(encoding="ascii")
        self.assertTrue(all(len(line) <= 80 for line in source.splitlines()))
        self.assertNotIn("\n/*\n", source)
        for required in (
            "RESULT := RESUMECO(A, 123)",
            "RESULTIS COWAIT(777)",
            "RESULTIS COWAIT(888)",
            "CURRCO!1 := PARENT",
            'WRITEF("CO0 BUSY RESULT %N*N", RESULT)',
        ):
            self.assertIn(required, source)
        self.assertLess(
            source.index("RESULT := RESUMECO(A, 123)"),
            source.index("CURRCO!1 := PARENT"),
        )
        self.assertIn("RESULT := CALLCO(A, B)", source)
        self.assertIn("LET VALUE = CALLCO(B, CURRCO)", source)

    def test_host_deck_stages_three_canonical_sources(self):
        core = runpy.run_path(
            str(ROOT / "tools/mr10/compile-and-run-core.py"),
            run_name="co0_busy_parent_host_test",
        )
        deck = core["build_deck"](
            interpreter=None,
            sources=[SOURCE, *MODULES],
            job_name="CO0BUSY",
            listing="light",
            named_dds=[],
            installed_load="HERC02.BCPL.MR10KIT.LOAD",
        )
        for source in (SOURCE, *MODULES):
            self.assertIn(source.read_text(encoding="ascii"), deck)
        for step in (
            "STGICLIB", "COMP01", "CG01", "COMP02",
            "CG02", "COMP03", "CG03", "RUN",
        ):
            self.assertIn(f"//{step:<8} EXEC", deck)
        self.assertIn("6 LIP2 SG9 LP0 SIG7", deck)
        self.assertIn("LET COBOOT(FN, SIZE, C)", deck)
        self.assertNotIn("//ASM      EXEC", deck)


if __name__ == "__main__":
    unittest.main()
