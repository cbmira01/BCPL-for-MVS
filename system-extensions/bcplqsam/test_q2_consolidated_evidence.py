"""Offline verifier tests for Q2FULL JES evidence parsing."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "q2evidence", HERE / "check-q2-consolidated-evidence.py")
assert SPEC is not None and SPEC.loader is not None
EVID = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVID)


class Q2EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.summary = "\n".join(
            f"{step} JOB STEP RESULT RC=0000" for step in EVID.STEPS)
        self.report = "\n".join(EVID.MARKERS)

    def test_complete_pass(self):
        self.assertEqual(EVID.check(self.summary, self.report), [])

    def test_each_missing_step_fails(self):
        for step in EVID.STEPS:
            with self.subTest(step=step):
                bad = self.summary.replace(
                    f"{step} JOB STEP RESULT RC=0000",
                    f"{step} JOB STEP RESULT RC=0008")
                self.assertTrue(EVID.check(bad, self.report))

    def test_each_missing_pass_marker_fails(self):
        for marker in EVID.MARKERS:
            with self.subTest(marker=marker):
                self.assertTrue(EVID.check(
                    self.summary, self.report.replace(marker, "")))

    def test_literal_in_listing_does_not_pass(self):
        bad = "\n".join(
            "PASSREC  DC CL80'" + marker + "'" for marker in EVID.MARKERS)
        self.assertTrue(EVID.check(self.summary, bad))

    def test_wrong_sequence_is_rejected(self):
        self.assertTrue(EVID.check(
            self.summary, "\n".join(reversed(EVID.MARKERS))))


if __name__ == "__main__":
    unittest.main()
