#!/usr/bin/env python3
"""Host-only post-promotion checks for the paired MR10 coroutine repair."""

from pathlib import Path
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
