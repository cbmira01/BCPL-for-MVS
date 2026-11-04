"""Regression tests for reused JES job numbers in MR10 printer reports."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "mr10" / "compile-and-run-core.py"
SPEC = importlib.util.spec_from_file_location("mr10_report_core", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load MR10 report extractor")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def job(number, name, content, completed=True):
    start = (
        f"****A  START  JOB {number:4d}  {name}  "
        f"PRINTER1 JOB {number:4d} START A****\n"
    )
    end = (
        f"****A   END   JOB {number:4d}  {name}\n"
        if completed else ""
    )
    return start + content + end


class MR10JobNumberReuseTests(unittest.TestCase):
    def test_single_completed_job(self):
        report = job(9316, "BCSCALAR", "CURRENT REPORT\n")
        self.assertEqual(
            MOD.extract_complete_job(report, 9316),
            "CURRENT REPORT\n"
        )

    def test_latest_completed_job_selected(self):
        report = (
            job(9316, "DSPALST", "OLD REPORT\n")
            + job(9316, "BCSCALAR", "CURRENT REPORT\n")
        )
        self.assertEqual(
            MOD.extract_complete_job(report, 9316),
            "CURRENT REPORT\n"
        )

    def test_latest_incomplete_does_not_return_old_report(self):
        report = (
            job(9316, "DSPALST", "OLD REPORT\n")
            + job(9316, "BCSCALAR", "CURRENT PARTIAL\n", False)
        )
        self.assertIsNone(
            MOD.extract_complete_job(report, 9316)
        )

    def test_interleaved_other_jobs(self):
        report = (
            job(9316, "DSPALST", "OLD\n")
            + job(9317, "BCBYTES", "OTHER\n")
            + job(9316, "BCSCALAR", "NEW\n")
        )
        self.assertEqual(
            MOD.extract_complete_job(report, 9316),
            "NEW\n"
        )
        self.assertEqual(
            MOD.extract_complete_job(report, 9317),
            "OTHER\n"
        )

    def test_missing_job(self):
        self.assertIsNone(
            MOD.extract_complete_job(
                job(9317, "BCBYTES", "DATA\n"), 9316
            )
        )

    def test_pipeline_validation_uses_latest_execution(self):
        entries = (
            "INTCODE SYSTEM ENTERED\n"
            "EXECUTION CYCLES = 10, CODE = 0\n"
        ) * 3
        report = (
            job(9316, "DSPALST", "OLD\n")
            + job(9316, "BCSCALAR", entries)
        )
        current = MOD.extract_complete_job(report, 9316)
        self.assertEqual(
            MOD.interpreted_execution_codes(current), [0, 0, 0]
        )
        MOD.validate_compiler_pipeline(current, 1)


if __name__ == "__main__":
    unittest.main()
