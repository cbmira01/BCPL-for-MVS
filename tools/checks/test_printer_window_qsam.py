"""Offline QSAM printer-window orchestration tests; never submit JES."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/checks/run-q2-qsam-regression.py"
SPEC = importlib.util.spec_from_file_location("qsam_window_runner", SCRIPT)
QSAM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QSAM)


class QsamPrinterWindowTests(unittest.TestCase):
    def exercise_case(self, number: int, trial: str, *, invalid_cursor=False):
        kind, _, _, markers = QSAM.CASES[number]
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            reg = base / "cases"
            case = reg / f"{number:03d}-offline"
            case.mkdir(parents=True)
            (case / "source.bcpl").write_text("LET START() BE FINISH\n")
            (case / "expected.txt").write_text("\n".join(markers) + "\n")
            (case / "qsam-native.txt").write_text(kind + "\n")
            if kind == "full":
                (case / "reader.bcpl").write_text("LET READ() = 1\n")
            if kind == "fba":
                printer = base / "printer.txt"
                printer.write_bytes(b"old printer bytes\n")

            calls = []

            def fake_invoke(args, output, limit):
                calls.append((list(args), output))
                name = Path(args[0]).name
                if len(args) > 1 and Path(args[1]).name == "compile-mvs":
                    generated = Path(args[args.index("--output") + 1])
                    generated.write_text(" ASSEMBLER SOURCE\n", encoding="ascii")
                    result = (0, "saved Cambridge CODE: synthetic\n")
                elif name == "submit-jcl":
                    result = (0, "JOB 271\n")
                elif name == "job-summary":
                    result = ((2, "job-summary: printer-window: invalid cursor\n")
                              if invalid_cursor else (0, "JOB RESULT: SUCCESS\n"))
                elif name == "dump-report-for-job":
                    result = (0, "\n".join(markers) + "\n")
                else:
                    raise AssertionError(f"unexpected command: {args}")
                output.write_text(result[1], encoding="utf-8")
                return result

            patches = [
                mock.patch.object(QSAM, "REG", reg),
                mock.patch.object(QSAM, "WORK", base / "work"),
                mock.patch.object(QSAM, "checked_fixture",
                                  side_effect=lambda directory, filename, original:
                                  directory / filename),
                mock.patch.object(QSAM, "prepare", return_value="//TEST JOB X\n"),
                mock.patch.object(QSAM, "invoke", side_effect=fake_invoke),
                mock.patch.object(QSAM, "evidence", return_value=[]),
                mock.patch.object(QSAM, "check_sysout_capture", return_value=[]),
                mock.patch.object(QSAM.time, "sleep", return_value=None),
                mock.patch.dict(os.environ, {"BCPL_PRINTER_WINDOW_TRIAL": trial}),
            ]
            if kind == "fba":
                patches.append(mock.patch.dict(QSAM.SYSOUT_PATHS, {"fba": printer}))

            with contextlib.ExitStack() as stack:
                for patcher in patches:
                    stack.enter_context(patcher)
                with contextlib.redirect_stdout(io.StringIO()):
                    result = QSAM.run(number, case)

            submit = [args for args, _ in calls if Path(args[0]).name == "submit-jcl"]
            summary = [args for args, _ in calls if Path(args[0]).name == "job-summary"]
            reports = [args for args, _ in calls
                       if Path(args[0]).name == "dump-report-for-job"]
            compiles = [args for args, _ in calls if len(args) > 1
                        and Path(args[1]).name == "compile-mvs"]
            self.assertEqual(len(compiles), 2 if kind == "full" else 1)
            self.assertEqual(len(submit), 1)
            self.assertEqual(len(summary), 1)
            self.assertEqual(len(reports), 0 if invalid_cursor else 1)
            self.assertEqual(result, 1 if invalid_cursor else 0)

            for args in submit + summary + reports:
                if trial == "1":
                    self.assertIn("--cursor-file", args)
                    cursor = Path(args[args.index("--cursor-file") + 1])
                    self.assertEqual(cursor.name, "native-printer.cursor")
                    self.assertEqual(cursor.parent, Path(submit[0][-1]).parent)
                else:
                    self.assertNotIn("--cursor-file", args)

    def test_opt_in_routing_single_extra_compiler_and_device_case(self):
        for number in (163, 168, 176):
            with self.subTest(number=number):
                self.exercise_case(number, "1")

    def test_default_preserves_existing_readers(self):
        self.exercise_case(163, "0")

    def test_invalid_cursor_stops_without_report_or_retry(self):
        self.exercise_case(163, "1", invalid_cursor=True)

    def test_invalid_trial_option_rejected(self):
        with mock.patch.dict(os.environ, {"BCPL_PRINTER_WINDOW_TRIAL": "yes"}):
            with self.assertRaisesRegex(ValueError, "must be 0 or 1"):
                QSAM.printer_args_for_attempt(Path("/tmp/offline-only"))

    def test_sysout_capture_uses_suffix_not_full_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            printer = root / "printer.txt"
            prefix = b"historical printer content\n" * 100
            fresh = b"Q4FBA001\n\nQ4FBA002X\x0cQ4FBA003\n"
            printer.write_bytes(prefix + fresh)
            with mock.patch.dict(QSAM.SYSOUT_PATHS, {"fba": printer}):
                with mock.patch.object(Path, "read_bytes",
                                       side_effect=AssertionError("full-file read")):
                    issues = QSAM.check_sysout_capture("fba", len(prefix), root)
            self.assertEqual(issues, [])
            self.assertEqual((root / "sysout-capture.bin").read_bytes(), fresh)


if __name__ == "__main__":
    unittest.main()
