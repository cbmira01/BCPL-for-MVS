#!/usr/bin/env python3
"""Offline M5.5 runner/freshness checks (no MVS/JES work)."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).with_name("m55-final-evidence.py")
SPEC = importlib.util.spec_from_file_location("m55_final_evidence", PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def fixture(names=None):
    if names is None:
        names = {n: f"{n:02d}" if n <= 52 else f"{n:03d}"
                 for n in range(146)}
    sections = ["NATIVE REGRESSION  00..145  (146 tests)"]
    for n, name in names.items():
        if n == 83:
            sections.append(
                f"SKIP  083  {name} (source-only instrumentation)")
        else:
            sections.extend((f"RUN   {name}  {name}",
                             f"PASS  {name}  {name}"))
    sections += ["", "NATIVE REGRESSION COMPLETE", "PASS  145",
                 "FAIL  0", "SKIP  1", "TOTAL 146", ""]
    return names, "\n".join(sections)


class PanelTests(unittest.TestCase):
    def test_exact_positive_panel(self):
        names, report = fixture()
        gate.parse_runner(report, names)

    def test_actual_repo_case_names_and_footer(self):
        # Use the real native runner discovery to catch formatting drift.
        names = gate.cases()
        _, report = fixture(names)
        gate.parse_runner(report, names)

    def test_footer_pass_number_cannot_steal_next_line(self):
        # A regression of the original failure: \s in the field
        # separator made "PASS  145\nFAIL  0" an extra PASS record.
        names, report = fixture()
        gate.parse_runner(report, names)
        self.assertIn("PASS  145\nFAIL  0\nSKIP  1", report)

    def test_missing_case_rejected(self):
        names, report = fixture()
        with self.assertRaisesRegex(ValueError, "PASS lines"):
            gate.parse_runner(report.replace("PASS  100  100\n", ""), names)

    def test_duplicate_case_rejected(self):
        names, report = fixture()
        with self.assertRaisesRegex(ValueError, "RUN lines"):
            gate.parse_runner(report.replace("RUN   101  101\n",
                "RUN   101  101\nRUN   101  101\n"), names)

    def test_wrong_aggregate_summary_rejected(self):
        names, report = fixture()
        with self.assertRaisesRegex(ValueError, "summary"):
            gate.parse_runner(report.replace("PASS  145\n", "PASS  144\n"), names)

    def test_wrong_skip_rejected(self):
        names, report = fixture()
        with self.assertRaisesRegex(ValueError, "SKIP"):
            gate.parse_runner(report.replace("SKIP  083  083", "SKIP  083  CHANGED"),
                              names)

    def test_wrong_range_rejected(self):
        names, report = fixture()
        with self.assertRaisesRegex(ValueError, "banner"):
            gate.parse_runner(report.replace("00..145", "00..144"), names)

    def test_stale_and_updated_log_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            case = folder / "100-test.log"
            case.write_text("OLD\n")
            os.utime(case, ns=(1_000_000_000, 1_000_000_000))
            baseline = gate.file_stat(case)
            fresh_after = 2_000_000_000
            self.assertTrue(gate.check_fresh(
                {100: "100-test"}, {"100-test": baseline},
                fresh_after, folder))
            case.write_text("NEW\n")
            os.utime(case, ns=(3_000_000_000, 3_000_000_000))
            self.assertEqual(gate.check_fresh(
                {100: "100-test"}, {"100-test": baseline},
                fresh_after, folder), [])

    def test_missing_and_empty_case_logs_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            self.assertIn("missing", " ".join(gate.check_fresh(
                {100: "100-test"}, {"100-test": None}, 1, folder)))
            (folder / "100-test.log").write_bytes(b"")
            os.utime(folder / "100-test.log", ns=(10, 10))
            self.assertIn("empty", " ".join(gate.check_fresh(
                {100: "100-test"}, {"100-test": None}, 1, folder)))


if __name__ == "__main__":
    unittest.main()
