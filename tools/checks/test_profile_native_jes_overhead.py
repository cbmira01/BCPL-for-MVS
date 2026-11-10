"""Host-only checks for the read-only JES overhead timing trial."""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/tests/profile-native-jes-overhead"
NS = runpy.run_path(str(SCRIPT))


def job_banner(number: int, name: str, begin: str, end: str) -> str:
    return (f"****A START JOB {number} {name} ROOM TEST 10.10.10 AM 10 NOV 26\n"
            f"IEF403I {name} - STARTED - TIME={begin}\n"
            f"IEF404I {name} - ENDED - TIME={end}\n"
            f"****A END JOB {number} {name}\n")


class ProfileNativeJesOverheadTests(unittest.TestCase):
    def test_midnight_and_one_pass_last_complete_occurrence(self):
        self.assertEqual(NS["job_seconds"]("23.59.59", "00.00.02"), 3)
        self.assertIsNone(NS["job_seconds"](None, "00.00.02"))
        with tempfile.TemporaryDirectory() as scratch:
            printer = Path(scratch) / "printer.txt"
            printer.write_text(
                job_banner(23, "RG000C", "11.00.00", "11.00.01")
                + job_banner(23, "RG000C", "11.01.00", "11.01.05")
                + "****A START JOB 24 RG000R ROOM TEST\nIEF403I RG000R - STARTED - TIME=11.00.00\n"
                + job_banner(25, "UNRELATED", "11.00.00", "11.00.01"),
                encoding="utf-8")
            result = NS["printer_jobs"](printer, {(23, "RG000C"), (24, "RG000R")})
            self.assertEqual(result[(23, "RG000C")], 5)
            self.assertNotIn((24, "RG000R"), result)  # incomplete job

    def test_incomplete_later_reuse_invalidates_older_job(self):
        with tempfile.TemporaryDirectory() as scratch:
            printer = Path(scratch) / "printer.txt"
            printer.write_text(
                job_banner(23, "RG000C", "11.00.00", "11.00.01")
                + "****A START JOB 23 RG000C ROOM TEST\n"
                + "IEF403I RG000C - STARTED - TIME=11.01.00\n", encoding="utf-8")
            result = NS["printer_jobs"](printer, {(23, "RG000C")})
            self.assertNotIn((23, "RG000C"), result)

    def test_case_logs_and_cli_are_read_only(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix="profile-jes-fixture-") as scratch:
            top = Path(scratch)
            evidence = top / "project"
            native = top / "native"
            evidence.mkdir()
            native.mkdir()
            (evidence / "summary.json").write_text(
                '{"suites":[{"name":"bootstrap","native_evidence":"'
                + native.relative_to(ROOT).as_posix() + '"}]}\n', encoding="utf-8")
            (native / "summary.json").write_text(
                '{"started_utc":"2026-11-10T02:00:00+00:00",'
                '"cases":[{"id":"00","status":"PASS","directory":"00-first"},'
                '{"id":"01","status":"PASS","directory":"01-next"}]}\n',
                encoding="utf-8")
            start = datetime(2026, 11, 10, 2, 0, tzinfo=timezone.utc).timestamp()
            for ident, jobs, finished in [("00", [10, 11], 23.7), ("01", [12, 13], 47.4)]:
                case = native / f"case-{ident}"
                (case / "native-logs").mkdir(parents=True)
                (case / "native-logs" / "case.log").write_text(
                    "".join(f"JOB {id}\n" for id in jobs), encoding="utf-8")
                log = case / "runner.log"
                log.write_text("PASS\n", encoding="utf-8")
                os.utime(log, (start + finished, start + finished))
            printer = top / "printer.txt"
            printer.write_text("".join([
                job_banner(10, "RG000C", "10.00.00", "10.00.01"),
                job_banner(11, "RG000R", "10.00.04", "10.00.06"),
                job_banner(12, "RG001C", "10.00.10", "10.00.13"),
                job_banner(13, "RG001R", "10.00.15", "10.00.20"),
            ]), encoding="utf-8")
            before = {p: p.stat().st_mtime_ns for p in top.rglob("*") if p.is_file()}
            proc = subprocess.run([str(SCRIPT), "--evidence", str(evidence),
                                   "--printer", str(printer), "--case", "0",
                                   "--case", "1", "--bench", "0"],
                                  cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("RG000C#10=1s", proc.stdout)
            self.assertIn("RG001R#13=5s", proc.stdout)
            self.assertIn("23.7", proc.stdout)
            after = {p: p.stat().st_mtime_ns for p in top.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
