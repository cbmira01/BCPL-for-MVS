"""Offline integration tests for opt-in JES printer-window consumers."""
from __future__ import annotations

import ast
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MVS = ROOT / "tools/mvs"


def entry(number: int, name: str, marker: str, *, complete: bool = True) -> str:
    # job-summary's START_JOB_RE requires whitespace after the date field.
    body = (
        f"****A  START  JOB {number:4d}  {name} TEST "
        "ROOM A 10.10.10 AM 10 NOV 26 \n"
        f"IEF403I {name} - STARTED - TIME=10.10.10\n"
        f"10.10.10 JOB {number} {name} COMP ICINT19 RC=0000\n"
        f"{marker}\n"
    )
    return body + (
        f"IEF404I {name} - ENDED - TIME=10.10.11\n"
        f"****A   END   JOB {number:4d}  {name}\n"
        if complete else ""
    )


class PrinterWindowIntegration(unittest.TestCase):
    def capture(self, printer: Path, cursor: Path) -> None:
        proc = subprocess.run(
            [sys.executable, str(MVS / "printer-window.py"), "capture",
             "--printer", str(printer), "--cursor-file", str(cursor)],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def summary(self, job: int, printer: Path, cursor: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(MVS / "job-summary"), str(job), "--file", str(printer),
             "--max-rc", "0", "--cursor-file", str(cursor)],
            cwd=ROOT, capture_output=True, text=True)

    def test_job_summary_ignores_old_and_rejects_incomplete_latest(self):
        with tempfile.TemporaryDirectory() as folder:
            printer, cursor = Path(folder) / "printer.txt", Path(folder) / "cursor.json"
            printer.write_text(entry(271, "OLDJOB", "OLD"), encoding="utf-8")
            self.capture(printer, cursor)
            with printer.open("a", encoding="utf-8") as output:
                output.write(entry(271, "RG000C", "NEW"))
            result = self.summary(271, printer, cursor)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("JOB 271  RG000C", result.stdout)
            self.assertNotIn("OLDJOB", result.stdout)
            legacy = subprocess.run(
                [str(MVS / "job-summary"), "271", "--file", str(printer),
                 "--max-rc", "0"],
                cwd=ROOT, capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout),
                             (legacy.returncode, legacy.stdout))
            with printer.open("a", encoding="utf-8") as output:
                output.write(entry(271, "RG000C", "NEW_INCOMPLETE", complete=False))
            result = self.summary(271, printer, cursor)
            self.assertEqual(result.returncode, 2)
            self.assertIn("has no END JOB banner", result.stderr)

    def test_cursor_invalid_fails_without_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            printer, cursor = Path(folder) / "printer.txt", Path(folder) / "cursor.json"
            printer.write_text(entry(271, "RG000C", "OLD"), encoding="utf-8")
            self.capture(printer, cursor)
            printer.write_text(entry(271, "RG000C", "REPLACED"), encoding="utf-8")
            result = self.summary(271, printer, cursor)
            self.assertEqual(result.returncode, 2)
            self.assertIn("printer-window:", result.stderr)

    def test_dump_report_is_scoped_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scripts = root / "tools/mvs"
            scripts.mkdir(parents=True)
            for name in ("dump-report-for-job", "printer-window.py"):
                shutil.copyfile(MVS / name, scripts / name)
            printer = root / "mvs-state/prt/prt00e.txt"
            printer.parent.mkdir(parents=True)
            cursor = root / "cursor.json"
            printer.write_text(entry(271, "OLDRUN", "OLD_REPORT"), encoding="utf-8")
            self.capture(printer, cursor)
            with printer.open("a", encoding="utf-8") as output:
                output.write(entry(271, "RG000R", "NEW_REPORT"))
            command = ["bash", str(scripts / "dump-report-for-job"),
                       "271", "--cursor-file", str(cursor)]
            current = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(current.returncode, 0, current.stderr)
            self.assertIn("NEW_REPORT", current.stdout)
            self.assertNotIn("OLD_REPORT", current.stdout)
            legacy = subprocess.run(["bash", str(scripts / "dump-report-for-job"), "271"],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual((legacy.returncode, legacy.stdout),
                             (current.returncode, current.stdout))
            printer.write_text(entry(271, "RG000R", "WRONG"), encoding="utf-8")
            invalid = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)

    def test_shell_syntax_and_python_imports(self):
        for relative in (
            "tools/mvs/submit-jcl",
            "tools/mvs/dump-report-for-job",
            "bootstrap-toolchain/regression/run-test.sh",
        ):
            with self.subTest(relative=relative):
                process = subprocess.run(["bash", "-n", str(ROOT / relative)],
                                         capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
        for relative in ("tools/mvs/job-summary", "tools/datasets/dspal-core.py",
                         "tools/bootstrap/compile-mvs"):
            with self.subTest(relative=relative):
                ast.parse((ROOT / relative).read_text("utf-8"))


if __name__ == "__main__":
    unittest.main()
