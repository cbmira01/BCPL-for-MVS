"""Host-only project coordinator checks for accepted MR10 development probes.

No test in this module submits JES work.
"""
from __future__ import annotations

import csv
import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools/tests/run-project-regressions"
SPEC = importlib.util.spec_from_loader(
    "project_regressions_probe_test", SourceFileLoader(
        "project_regressions_probe_test", str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import project regression coordinator")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ProjectMR10ProbesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old_root = MOD.ROOT
        MOD.ROOT = self.root
        self.addCleanup(setattr, MOD, "ROOT", self.old_root)
        self.folder = self.root / "workarea/mr10-probes" / "synthetic"
        self.folder.mkdir(parents=True)
        self.accepted = list(MOD.ACCEPTED_MR10_PROBES)

    def evidence(self, states):
        cases = [{"id": ident, "verification": "ACCEPTED", "status": state}
                 for ident, state in zip(self.accepted, states)]
        counts = {name: states.count(name)
                  for name in ("PASS", "FAIL", "OBSERVED", "NOT_RUN")}
        status = ("FAIL" if counts["FAIL"] else
                  "UNVERIFIED" if counts["OBSERVED"] else "PASS")
        payload = {"suite": "mr10-probes", "selected_cases": self.accepted,
                   "cases": cases, "counts": counts, "status": status}
        (self.folder / "summary.json").write_text(
            json.dumps(payload), encoding="utf-8")
        log = f"MR10 PROBE EVIDENCE: {self.folder}\nMR10 PROBE RESULT: {status}\n"
        rc = 1 if counts["FAIL"] else 3 if counts["OBSERVED"] else 0
        return log, rc

    def test_six_pinned_accepted_cases_match_manifest(self):
        with (ROOT / "mr10-kit-compiler/tests/dev-probes-manifest.tsv").open(
                encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        accepted = [row["case_id"] for row in rows
                    if row["verification"] == "ACCEPTED"]
        self.assertEqual(accepted, self.accepted)
        self.assertEqual(len(accepted), 6)
        self.assertEqual(len(rows), 17)

    def test_inventory_keeps_mr10_probes_out_of_native_manifests(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        saved = {key: getattr(MOD, key) for key in (
            "MR10", "NATIVE", "MR10_PROBES", "MR10_PROBES_MANIFEST",
            "NATIVE_MANIFESTS")}
        for key, value in saved.items():
            self.addCleanup(setattr, MOD, key, value)

        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        for key in ("MR10", "NATIVE", "MR10_PROBES"):
            setattr(MOD, key, bin_dir / key)
            getattr(MOD, key).touch()
        (self.root / "tools/mr10").mkdir(parents=True)
        (self.root / "tools/mr10/compile-and-run").touch()
        MOD.MR10_PROBES_MANIFEST = self.root / "dev-probes.tsv"
        with MOD.MR10_PROBES_MANIFEST.open("w") as handle:
            handle.write("case_id\tverification\n")
            for ident in self.accepted:
                handle.write(f"{ident}\tACCEPTED\n")
        MOD.NATIVE_MANIFESTS = self.root / "native"
        MOD.NATIVE_MANIFESTS.mkdir()
        for suite in MOD.NATIVE_SUITES:
            (MOD.NATIVE_MANIFESTS / f"{suite}.tsv").write_text(
                f"case_id\tdirectory\n00\t{suite}-fixture\n")

        with (
            patch.object(MOD, "mr10_cases", return_value=["syntax/example"]),
            patch.object(MOD.subprocess, "run",
                         return_value=SimpleNamespace(returncode=0, stdout="OK")),
        ):
            selected = MOD.inventory()
        self.assertEqual(list(selected), list(MOD.SUITES))
        self.assertEqual(selected["mr10-probes"], self.accepted)

    def test_suite_command_selects_only_accepted_ids(self):
        command = MOD.suite_command(
            "mr10-probes", {"mr10-probes": self.accepted}, None, False)
        self.assertEqual(command[:2], [str(MOD.MR10_PROBES), "--run"])
        self.assertEqual(command[2::2], ["--case"] * 6)
        self.assertEqual(command[3::2], self.accepted)
        self.assertNotIn("--all-candidates", command)
        self.assertNotIn("--profile", command)

    def test_other_suite_commands_unchanged(self):
        cases = {"mr10": ["syntax/example"], "bcplqsam": ["175"]}
        self.assertEqual(MOD.suite_command("mr10", cases, None, False),
                         [str(MOD.MR10)])
        self.assertEqual(
            MOD.suite_command("bcplqsam", cases, "production", True),
            [str(MOD.NATIVE), "bcplqsam", "--run", "--profile",
             "production", "--allow-device"])

    def test_progress_names_and_legacy_formats(self):
        self.assertEqual(
            MOD.progress_case("mr10-probes",
                              "PASS     04-module-test: golden output"),
            "PASS    04-module-test")
        self.assertEqual(
            MOD.progress_case("mr10-probes",
                              "OBSERVED 10-coroutines/compiler-probe: experimental"),
            "OBSERVED 10-coroutines/compiler-probe")
        self.assertEqual(
            MOD.progress_case("mr10", "PASS syntax/example\n"),
            "PASS    syntax/example")
        self.assertEqual(
            MOD.progress_case("bootstrap",
                              "PASS 00 00-most-degenerate-bcpl-program: RC=0"),
            "PASS    00  most-degenerate-bcpl-program")

    def test_accepted_pass(self):
        log, rc = self.evidence(["PASS"] * 6)
        result = MOD.parse_mr10_probes(log, self.accepted, rc)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"],
                         {"PASS": 6, "FAIL": 0, "SKIP": 0, "BLOCKED": 0,
                          "TOTAL": 6})

    def test_failure_preserves_not_run_cases(self):
        log, rc = self.evidence(["PASS", "FAIL"] + ["NOT_RUN"] * 4)
        result = MOD.parse_mr10_probes(log, self.accepted, rc)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["counts"]["PASS"], 1)
        self.assertEqual(result["cases"][2]["status"], "NOT_RUN")

    def test_unverified_observation_cannot_pass(self):
        log, rc = self.evidence(["OBSERVED"] + ["PASS"] * 5)
        result = MOD.parse_mr10_probes(log, self.accepted, rc)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["counts"]["BLOCKED"], 1)

    def test_unaccepted_or_reordered_cases_rejected(self):
        log, rc = self.evidence(["PASS"] * 6)
        file = self.folder / "summary.json"
        payload = json.loads(file.read_text())
        payload["cases"][0]["id"] = "08-character-translation"
        file.write_text(json.dumps(payload))
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_mr10_probes(log, self.accepted, rc)

    def test_false_acceptance_rejected(self):
        log, rc = self.evidence(["PASS"] * 6)
        file = self.folder / "summary.json"
        payload = json.loads(file.read_text())
        payload["cases"][0]["verification"] = "UNVERIFIED"
        file.write_text(json.dumps(payload))
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_mr10_probes(log, self.accepted, rc)

    def test_inconsistent_status_and_rc_rejected(self):
        log, _ = self.evidence(["PASS"] * 6)
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_mr10_probes(log, self.accepted, 1)

    def test_unexpected_undelivered_cases_rejected(self):
        log, _ = self.evidence(["PASS"] * 5 + ["NOT_RUN"])
        with self.assertRaises(MOD.VerificationError):
            MOD.parse_mr10_probes(log, self.accepted, 0)


if __name__ == "__main__":
    unittest.main()
