"""Offline tests of the standalone development-probe dispatcher; all runners are fake."""
from __future__ import annotations

import contextlib
from importlib.machinery import SourceFileLoader
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "mr10/run-dev-probes"
SPEC = importlib.util.spec_from_loader("mr10_dev_probes_runner", SourceFileLoader("mr10_dev_probes_runner", str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import MR10 development-probe runner")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class MR10DevelopmentProbeRunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mr10-probes-runner-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for key, value in {
            "ROOT": self.root,
            "COMPILE": self.root / "tools/mr10/compile-and-run",
            "CURRENT": self.root / "mr10-kit-compiler/asm/CURRENT",
            "EVIDENCE_ROOT": self.root / "workarea/mr10-probes",
        }.items():
            previous = getattr(MOD, key)
            setattr(MOD, key, value)
            self.addCleanup(setattr, MOD, key, previous)
        self.make_file("mr10-kit-compiler/asm/CURRENT", "icintv19.asm\n")
        self.make_file("mr10-kit-compiler/asm/icintv19.asm")
        self.rows = []
        for case_id in (*MOD.PROVISIONAL, "02-honors-thesis-and-mapstore/honors-thesis"):
            self.rows.append(dict(
                case_id=case_id,
                engine="compile-and-run" if case_id in MOD.PROVISIONAL else "run-intcode",
                interpreter="current" if case_id in MOD.PROVISIONAL else "v12",
                source=f"mr10-kit-compiler/tests/{case_id.split('/')[0]}/main.bcpl",
                modules=("mr10-kit-compiler/tests/04-module-test/module-test-2.bcpl"
                         if case_id == "04-module-test" else
                         "mr10-kit-compiler/library/getvec-freevec.bcpl"
                         if case_id == "11-getvec-freevec" else ""),
                dd_bindings=("EXTRA=mr10-kit-compiler/tests/05-named-dd/extra.bcpl"
                             if case_id == "05-named-dd" else ""),
                sysin="", expected_code="0", oracle="pending:test", artifacts="none",
                verification="UNVERIFIED",
            ))
        for row in self.rows:
            self.make_file(row["source"])
            for part in row["modules"].split(";") if row["modules"] else []:
                self.make_file(part)
            for binding in row["dd_bindings"].split(";") if row["dd_bindings"] else []:
                self.make_file(binding.split("=", 1)[1])
        patcher = patch.object(MOD, "manifest_cases", side_effect=lambda: self.rows)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch.object(MOD, "git_head", return_value="a" * 40)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.make_fake_compiler()

    def make_file(self, relative, content="fixture\n"):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def make_fake_compiler(self):
        # The compiler is a Python stub and cannot contact Hercules/JES.
        script = '''#!/usr/bin/env python3
import os
from pathlib import Path
import sys
args = sys.argv[1:]
jcl = Path(args[args.index("--jcl")+1])
case = jcl.stem.replace("--", "/")
Path(jcl).write_text("//FAKE JOB\\n", encoding="utf-8")
if os.environ.get("PROBE_RUNNER_RC"):
    print("FAKE RUNNER ERROR")
    sys.exit(int(os.environ["PROBE_RUNNER_RC"]))
print("JOB 8123")
print("INTCODE SYSTEM ENTERED")
expected = %r
lines = list(expected[case])
if os.environ.get("PROBE_MISSING_TRACE"):
    lines = lines[:-1]
if os.environ.get("PROBE_REORDER"):
    lines = list(reversed(lines))
for line in lines:
    print(line)
if not os.environ.get("PROBE_NO_CODE"):
    print("EXECUTION CYCLES = 42, CODE = " + os.environ.get("PROBE_BAD_CODE", "0"))
''' % MOD.TRACE
        path = MOD.COMPILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(script, encoding="utf-8")
        path.chmod(0o755)

    def cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = MOD.main(list(args))
        return rc, stdout.getvalue(), stderr.getvalue()

    def evidence(self):
        runs = list(MOD.EVIDENCE_ROOT.iterdir())
        self.assertEqual(len(runs), 1)
        return json.loads((runs[0] / "summary.json").read_text()), runs[0]

    def test_host_check_never_executes_compiler(self):
        rc, out, err = self.cli("--check")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("6 provisional; host-only", out)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_list_shows_full_historical_id_without_execution(self):
        rc, out, err = self.cli("--list")
        self.assertEqual(rc, 0)
        self.assertIn("04-module-test\tPROVISIONAL", out)
        self.assertIn("02-honors-thesis-and-mapstore/honors-thesis\tNOT_IMPLEMENTED", out)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_list_subset(self):
        rc, out, _ = self.cli("--list", "--case", "09-multiple-assignment")
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.splitlines()), 1)

    def test_requires_explicit_run_selection(self):
        rc, _, err = self.cli("--run")
        self.assertEqual(rc, 2)
        self.assertIn("requires --case", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_rejects_unknown_case_without_execution(self):
        rc, _, err = self.cli("--run", "--case", "12-made-up")
        self.assertEqual(rc, 2)
        self.assertIn("unknown probe", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_historical_probe_is_rejected_before_jes(self):
        rc, _, err = self.cli("--run", "--case", "02-honors-thesis-and-mapstore/honors-thesis")
        self.assertEqual(rc, 2)
        self.assertIn("no JES submitted", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_mixed_selection_fails_preflight_without_jes(self):
        rc, _, err = self.cli("--run", "--case", "04-module-test", "--case", "02-honors-thesis-and-mapstore/honors-thesis")
        self.assertEqual(rc, 2)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_rejects_duplicate_case(self):
        rc, _, err = self.cli("--run", "--case", "04-module-test", "--case", "04-module-test")
        self.assertEqual(rc, 2)
        self.assertIn("duplicate", err)

    def test_provisional_scope_only_with_run(self):
        rc, _, err = self.cli("--list", "--all-provisional")
        self.assertEqual(rc, 2)
        self.assertIn("requires --run", err)

    def test_selected_case_evidence_is_unverified(self):
        rc, output, err = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual((rc, err), (3, ""))
        self.assertIn("OBSERVED 05-named-dd", output)
        self.assertNotIn("PASS 05-named-dd", output)
        summary, root = self.evidence()
        self.assertEqual(summary["status"], "UNVERIFIED")
        self.assertEqual(summary["verification"], "UNVERIFIED")
        self.assertEqual(summary["git_head"], "a" * 40)
        self.assertEqual(summary["counts"], {"OBSERVED": 1, "FAIL": 0, "NOT_RUN": 0})
        item = summary["cases"][0]
        self.assertEqual(item["status"], "OBSERVED")
        self.assertTrue((self.root / item["log"]).is_file())
        self.assertTrue((self.root / item["jcl"]).is_file())
        self.assertIn("EXTRA=", " ".join(item["command"]))
        self.assertEqual(len(item["job_name"]), 8)
        self.assertEqual(item["jes_job_id"], "8123")
        self.assertEqual(item["expected_code"], 0)
        self.assertEqual(item["interpreted_code"], 0)
        self.assertTrue(item["expected_oracle"].startswith("pending:"))

    def test_multiple_cases_run_in_manifest_order(self):
        rc, _, _ = self.cli("--run", "--case", "11-getvec-freevec", "--case", "04-module-test")
        self.assertEqual(rc, 3)
        s, root = self.evidence()
        self.assertEqual([x["id"] for x in s["cases"]], ["04-module-test", "11-getvec-freevec"])
        self.assertEqual(s["counts"]["OBSERVED"], 2)
        self.assertTrue(any("+" in a for a in s["cases"][0]["command"]))
        self.assertTrue(any("+" in a for a in s["cases"][1]["command"]))
        self.assertEqual(len(set(x["job_name"] for x in s["cases"])), 2)

    def test_all_six_provisional_cases_with_stubs(self):
        rc, out, err = self.cli("--run", "--all-provisional")
        self.assertEqual((rc, err), (3, ""))
        s, root = self.evidence()
        self.assertEqual(len(s["cases"]), 6)
        self.assertEqual(s["counts"]["OBSERVED"], 6)
        self.assertFalse(any(line.startswith("PASS ") for line in out.splitlines()))

    def test_runner_nonzero_stops_following_cases(self):
        with patch.dict(os.environ, {"PROBE_RUNNER_RC": "7"}):
            rc, out, _ = self.cli("--run", "--all-provisional")
        self.assertEqual(rc, 1)
        s, _ = self.evidence()
        self.assertEqual(s["status"], "FAIL")
        self.assertEqual(s["cases"][0]["runner_rc"], 7)
        self.assertEqual(s["cases"][1]["status"], "NOT_RUN")
        self.assertEqual(s["counts"], {"OBSERVED": 0, "FAIL": 1, "NOT_RUN": 5})

    def test_missing_code_is_fail_not_observed(self):
        with patch.dict(os.environ, {"PROBE_NO_CODE": "1"}):
            rc, _, _ = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 1)
        s, _ = self.evidence()
        self.assertIn("expected one interpreted completion code", s["cases"][0]["reason"])

    def test_nonzero_interpreted_code_is_fail(self):
        with patch.dict(os.environ, {"PROBE_BAD_CODE": "5"}):
            rc, _, _ = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 1)

    def test_missing_trace_is_fail(self):
        with patch.dict(os.environ, {"PROBE_MISSING_TRACE": "1"}):
            rc, _, _ = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 1)

    def test_reordered_trace_is_fail(self):
        with patch.dict(os.environ, {"PROBE_REORDER": "1"}):
            rc, _, _ = self.cli("--run", "--case", "09-multiple-assignment")
        self.assertEqual(rc, 1)

    def test_bad_manifest_aborts_before_jes(self):
        with patch.object(MOD, "manifest_cases", side_effect=MOD.ProbeError("manifest corrupted")):
            rc, _, err = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 2)
        self.assertIn("manifest corrupted", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_missing_current_asm_aborts_before_jes(self):
        (self.root / "mr10-kit-compiler/asm/icintv19.asm").unlink()
        rc, _, err = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 2)
        self.assertIn("not found", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_no_git_head_aborts_before_jes(self):
        with patch.object(MOD, "git_head", side_effect=MOD.ProbeError("cannot determine HEAD")):
            rc, _, err = self.cli("--run", "--case", "05-named-dd")
        self.assertEqual(rc, 2)
        self.assertIn("cannot determine HEAD", err)
        self.assertFalse(MOD.EVIDENCE_ROOT.exists())

    def test_missing_job_id_cannot_be_observed(self):
        trace = MOD.TRACE["05-named-dd"]
        body = "\n".join(["INTCODE SYSTEM ENTERED", *trace, "EXECUTION CYCLES = 2, CODE = 0"])
        state, reason = MOD.assess_output("05-named-dd", body, 0)
        self.assertEqual(state, "FAIL")
        self.assertIn("JES job ID", reason)

    def test_duplicate_job_id_is_ambiguous(self):
        trace = MOD.TRACE["05-named-dd"]
        body = "\n".join(["JOB 123", "JOB 124", "INTCODE SYSTEM ENTERED", *trace, "EXECUTION CYCLES = 2, CODE = 0"])
        self.assertEqual(MOD.assess_output("05-named-dd", body, 0)[0], "FAIL")

    def test_missing_icint_banner_is_fail(self):
        trace = MOD.TRACE["05-named-dd"]
        body = "\n".join(["JOB 123", *trace, "EXECUTION CYCLES = 2, CODE = 0"])
        state, reason = MOD.assess_output("05-named-dd", body, 0)
        self.assertEqual(state, "FAIL")
        self.assertIn("ICINT execution banner", reason)

    def test_interpreter_error_marker_is_fail(self):
        trace = MOD.TRACE["05-named-dd"]
        body = "\n".join(["JOB 123", "INTCODE SYSTEM ENTERED", *trace, "INTCODE ERROR", "EXECUTION CYCLES = 2, CODE = 0"])
        self.assertEqual(MOD.assess_output("05-named-dd", body, 0)[0], "FAIL")

    def test_trace_assertion_requires_order_and_uniqueness(self):
        trace = MOD.TRACE["09-multiple-assignment"]
        body = "\n".join(["JOB 8123", "INTCODE SYSTEM ENTERED", *trace, "EXECUTION CYCLES = 1, CODE = 0"])
        self.assertEqual(MOD.assess_output("09-multiple-assignment", body, 0)[0], "OBSERVED")
        self.assertEqual(MOD.assess_output("09-multiple-assignment", body + "\n" + trace[0], 0)[0], "FAIL")
        self.assertEqual(MOD.assess_output("09-multiple-assignment", body, 8)[0], "FAIL")


if __name__ == "__main__":
    unittest.main()
