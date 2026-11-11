#!/usr/bin/env python3
"""Host-only post-promotion checks for the paired MR10 coroutine repair."""

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[2] / "mr10-kit-compiler"


class CanonicalCoroutinePromotionTests(unittest.TestCase):
    def test_canonical_iclib_matches_executable_candidate(self):
        canonical = (ROOT / "source/iclib.int").read_text(encoding="ascii")
        candidate = (ROOT / "source/iclib-co0-candidate.int").read_text(
            encoding="ascii"
        )
        stripped = "\n".join(
            line for line in candidate.split("\n")
            if not line.lstrip().startswith("//")
        )
        self.assertEqual(canonical, stripped)
        self.assertTrue(canonical.rstrip().endswith("\nZ"))
        self.assertTrue(all(len(line) <= 80 for line in canonical.splitlines()))

    def test_canonical_iclib_stages_in_real_jcl_deck(self):
        core = runpy.run_path(
            str(ROOT.parent / "tools/mr10/compile-and-run-core.py"),
            run_name="mr10_canonical_staging_test",
        )
        source = ROOT / "tests/00-regression-panel/data-movement/scalar-vector.bcpl"
        deck = core["build_deck"](
            interpreter=None,
            sources=[source],
            job_name="CO0CHECK",
            listing="light",
            named_dds=[],
            installed_load="HERC02.BCPL.MR10KIT.LOAD",
        )
        self.assertNotIn("//ASM      EXEC", deck)
        self.assertIn("STGICLIB EXEC PGM=IEBGENER", deck)
        marker = "//SYSUT1   DD  *\\n"
        stage = deck.split("//STGICLIB", 1)[1]
        staged_records = stage.split(marker, 1)[1].split("/*\\n", 1)[0]
        canonical = (ROOT / "source/iclib.int").read_text(encoding="ascii")
        self.assertEqual(staged_records, canonical)
        self.assertFalse(
            any(record.startswith("//") for record in staged_records.splitlines())
        )
        self.assertIn("6 LIP2 SG9 LP0 SIG7", staged_records)
        self.assertNotIn("--iclib", deck)
        self.assertNotIn("CO.0 EXPERIMENT", deck)

    def test_canonical_coroutine_library_matches_candidate(self):
        canonical = (ROOT / "library/coroutines.bcpl").read_text(encoding="ascii")
        candidate = (ROOT / "library/coroutines-co0-candidate.bcpl").read_text(
            encoding="ascii"
        )
        # Only the four candidate-only introductory comment lines differ.
        self.assertEqual(canonical, "\n".join(candidate.split("\n")[4:]))
        self.assertIn("LET COBOOT(FN, SIZE, C)", canonical)
        self.assertIn("P!0 := P", canonical)
        self.assertIn("P!1 := COBOOT", canonical)
        self.assertIn("RESULTIS CHANGECO(0, C)", canonical)
        self.assertTrue(all(len(line) <= 80 for line in canonical.splitlines()))


if __name__ == "__main__":
    unittest.main()
