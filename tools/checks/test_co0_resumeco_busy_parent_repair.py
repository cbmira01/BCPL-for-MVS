#!/usr/bin/env python3
"""Offline checks for CO.0 isolated RESUMECO busy-target repair."""

from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "mr10-kit-compiler/library"
PROBES = ROOT / "mr10-kit-compiler/tests/10-coroutines"
CANONICAL = LIB / "coroutines.bcpl"
CANDIDATE = LIB / "coroutines-co0-busy-parent-candidate.bcpl"
COUNTEREXAMPLE = PROBES / "resumeco-busy-parent-co0-probe.bcpl"
REPAIR_PROBE = PROBES / "resumeco-busy-parent-co0-repair-probe.bcpl"
ALLOCATOR = LIB / "getvec-freevec.bcpl"
OLD = "   CURRCO!1 := 0\n   IF CPTR!1 \\= 0 RESULTIS -998\n"
NEW = "   IF CPTR!1 \\= 0 RESULTIS -998\n   CURRCO!1 := 0\n"
INTRO = (
    "// CO.0 ISOLATED CANDIDATE: busy RESUMECO preserves current parent.\n"
    "// Derived from canonical coroutines.bcpl; not approved for promotion.\n"
)


class BusyTargetRepairTests(unittest.TestCase):
    def test_only_change_is_check_before_parent_clear(self):
        canonical = CANONICAL.read_text(encoding="ascii")
        candidate = CANDIDATE.read_text(encoding="ascii")
        self.assertTrue(candidate.startswith(INTRO))
        self.assertEqual(canonical.count(OLD), 1)
        self.assertEqual(candidate, INTRO + canonical.replace(OLD, NEW, 1))
        self.assertEqual(candidate.count(NEW), 1)
        self.assertEqual(candidate.count("RESULTIS CHANGECO(A, CPTR)"), 2)

    def test_candidate_probe_does_not_repair_parent_itself(self):
        old = COUNTEREXAMPLE.read_text(encoding="ascii")
        new = REPAIR_PROBE.read_text(encoding="ascii")
        self.assertIn("CURRCO!1 := PARENT", old)
        self.assertNotIn("CURRCO!1 := PARENT", new)
        self.assertIn("RESULT := RESUMECO(A, 123)", new)
        self.assertIn("RESULTIS COWAIT(777)", new)
        self.assertIn("RESULTIS COWAIT(888)", new)
        self.assertIn("RESULT := CALLCO(A, B)", new)
        for marker in (
            "CO0 BUSY BEFORE", "CO0 BUSY TARGET", "CO0 BUSY RESULT",
            "CO0 BUSY PARENT KEPT", "CO0 BUSY PARENT CLEARED",
            "CO0 A GOT", "CO0 ROOT GOT", "CO0 DELETE A", "CO0 DELETE B",
        ):
            self.assertIn(marker, new)
        self.assertLess(new.index("RESULT := RESUMECO(A, 123)"),
                        new.index("RESULTIS COWAIT(777)"))

    def test_source_records_are_safe_for_80_column_staging(self):
        for path in (CANDIDATE, REPAIR_PROBE):
            content = path.read_text(encoding="ascii")
            self.assertTrue(content.strip())
            self.assertTrue(all(len(line) <= 80 for line in content.splitlines()))
            self.assertNotIn("\n/*\n", content)

    def test_generated_jcl_uses_candidate_not_canonical(self):
        core = runpy.run_path(
            str(ROOT / "tools/mr10/compile-and-run-core.py"),
            run_name="co0_busy_parent_candidate_host_test",
        )
        deck = core["build_deck"](
            interpreter=None,
            sources=[REPAIR_PROBE, ALLOCATOR, CANDIDATE],
            job_name="CO0FIX",
            listing="light",
            named_dds=[],
            installed_load="HERC02.BCPL.MR10KIT.LOAD",
        )
        for path in (REPAIR_PROBE, ALLOCATOR, CANDIDATE):
            self.assertIn(path.read_text(encoding="ascii"), deck)
        self.assertNotIn(CANONICAL.read_text(encoding="ascii"), deck)
        self.assertIn(NEW, deck)
        self.assertNotIn(OLD, deck)
        for step in (
            "STGICLIB", "COMP01", "CG01", "COMP02", "CG02",
            "COMP03", "CG03", "RUN",
        ):
            self.assertIn(f"//{step:<8} EXEC", deck)
        self.assertNotIn("//ASM      EXEC", deck)


if __name__ == "__main__":
    unittest.main()
