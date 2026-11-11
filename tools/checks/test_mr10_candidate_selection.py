#!/usr/bin/env python3
"""Host-only MR10 candidate-selection tests; never contact the JES reader."""

from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
PANEL = runpy.run_path(str(ROOT / "tools/mr10/run-regression-panel"),
                       run_name="mr10_panel_test")
CORE = runpy.run_path(str(ROOT / "tools/mr10/compile-and-run-core.py"),
                      run_name="mr10_compile_core_test")


class CandidateSelectionTests(unittest.TestCase):
    def test_exact_manifest_module_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.bcpl"
            candidate.write_text("LET START() BE FINISH\n")
            selected = [{"extras": "+library/coroutines.bcpl +library/getvec.bcpl"}]
            function = PANEL["parse_module_overrides"]
            with patch.dict(function.__globals__, {"ROOT": root}):
                self.assertEqual(
                    function(["library/coroutines.bcpl=candidate.bcpl"], selected),
                    {"library/coroutines.bcpl": "candidate.bcpl"},
                )
                for spec in ("library/unknown.bcpl=candidate.bcpl",
                             "library/coroutines.bcpl=missing.bcpl",
                             "library/coroutines.bcpl",
                             "library/coroutines.bcpl=candidate.bcpl=other"):
                    with self.subTest(spec=spec), self.assertRaises(ValueError):
                        function([spec], selected)
                with self.assertRaises(ValueError):
                    function(["library/coroutines.bcpl=candidate.bcpl"] * 2, selected)

    def test_runner_forwards_candidate_and_keeps_other_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "main.bcpl"
            golden = root / "golden.expected"
            source.write_text("LET START() BE FINISH\n")
            golden.write_text("RP: ok\n")
            row = {"source": "main.bcpl", "expected": "golden.expected",
                   "extras": "+library/coroutines.bcpl +library/getvec.bcpl",
                   "compile_args": "", "expected_code": "0"}
            completed = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="RP: ok\nEXECUTION CYCLES = 1, CODE = 0\n",
            )
            function = PANEL["run_case"]
            with patch.dict(function.__globals__, {"ROOT": root}):
                with patch.object(subprocess, "run", return_value=completed) as run:
                    ok, detail = function(
                        row, Path("icint.asm"), False, root / "candidate.int",
                        {"library/coroutines.bcpl": "library/co-candidate.bcpl"},
                    )
            self.assertTrue(ok, detail)
            command = run.call_args.args[0]
            self.assertEqual(
                command[command.index("--iclib") + 1], str(root / "candidate.int")
            )
            self.assertIn("+library/co-candidate.bcpl", command)
            self.assertIn("+library/getvec.bcpl", command)
            self.assertNotIn("+library/coroutines.bcpl", command)

    def test_default_runner_preserves_canonical_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.bcpl").write_text("LET START() BE FINISH\n")
            (root / "golden.expected").write_text("RP: ok\n")
            row = {"source": "main.bcpl", "expected": "golden.expected",
                   "extras": "+library/coroutines.bcpl",
                   "compile_args": "", "expected_code": "0"}
            completed = subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="RP: ok\nEXECUTION CYCLES = 1, CODE = 0\n",
            )
            function = PANEL["run_case"]
            with patch.dict(function.__globals__, {"ROOT": root}):
                with patch.object(subprocess, "run", return_value=completed) as run:
                    self.assertTrue(function(row, Path("icint.asm"), False)[0])
            command = run.call_args.args[0]
            self.assertNotIn("--iclib", command)
            self.assertIn("+library/coroutines.bcpl", command)

    def test_generated_jcl_stages_selected_iclib(self):
        function = CORE["build_deck"]
        original = CORE["ICLIB"]
        candidate = Path("/candidate/iclib.int")

        def records(path, description, width=80):
            return "CANDIDATE\n" if path == candidate else "BASE\n"

        with patch.dict(function.__globals__, {"read_ascii_records": records}):
            args = dict(
                interpreter=None, sources=[Path("main.bcpl")],
                job_name="MR10TEST", listing="light", named_dds=[],
                installed_load="HERC02.BCPL.MR10KIT.LOAD",
            )
            selected = function(**args, iclib_path=candidate)
            standard = function(**args)
        self.assertIn("//SYSUT1   DD  *\nCANDIDATE\n/*", selected)
        self.assertNotIn("CANDIDATE", standard)
        self.assertIn("//SYSUT1   DD  *\nBASE\n/*", standard)
        self.assertEqual(original, CORE["ICLIB"])


if __name__ == "__main__":
    unittest.main()
