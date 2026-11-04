"""Stage 3 coordinator host-only tests; execution uses fake runners."""
from __future__ import annotations

import contextlib
import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "tests" / "run-project-regressions"
SPEC = importlib.util.spec_from_loader(
    "stage3_coordinator", SourceFileLoader("stage3_coordinator", str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Stage 3 coordinator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class Stage3HostTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="bcpl-stage3-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for key, value in {
            "ROOT": self.root,
            "NATIVE": self.root / "tools/tests/run-suite",
            "MR10": self.root / "tools/mr10/run-regression-panel",
            "MR10_MANIFEST": self.root / "mr10-kit-compiler/tests/00-regression-panel/manifest.tsv",
            "NATIVE_MANIFESTS": self.root / "tests/suites",
            "RUN_ROOT": self.root / "workarea/project-regressions",
        }.items():
            previous = getattr(MOD, key)
            setattr(MOD, key, value)
            self.addCleanup(setattr, MOD, key, previous)
        patcher = patch.object(MOD, "git_head", return_value="test-git-revision")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.fixtures()

    def write_executable(self, name, source):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        path.chmod(0o755)

    def fixtures(self):
        folder = self.root / "fixture"
        folder.mkdir()
        entries = (
            ("scalar-vector", "data-movement"),
            ("nested-recursion", "calls"),
        )
        lines = []
        for name, category in entries:
            (folder / f"{name}.bcpl").write_text("LET START() BE STOP(0)\n")
            (folder / f"{name}.expected").write_text("RP: OK\n")
            lines.append("\t".join((name, category,
                f"fixture/{name}.bcpl", "", "",
                f"fixture/{name}.expected", "0")))
        MOD.MR10_MANIFEST.parent.mkdir(parents=True)
        MOD.MR10_MANIFEST.write_text("\n".join(lines) + "\n")
        self.native_ids = {
            "bootstrap": ["00", "01"],
            "runtime-extensions": ["147"],
            "bcpltime": ["159"],
            "bcplqsam": ["163", "175", "176"],
        }
        MOD.NATIVE_MANIFESTS.mkdir(parents=True)
        for suite, ids in self.native_ids.items():
            data = "case_id\tdirectory\n" + "".join(
                f"{ident}\t{ident}-fake-case\n" for ident in ids)
            (MOD.NATIVE_MANIFESTS / f"{suite}.tsv").write_text(data)
        self.write_executable("tools/mr10/compile-and-run",
                              "#!/bin/sh\nexit 0\n")
        self.write_executable("tools/mr10/run-regression-panel", '''#!/usr/bin/env python3
import os
from pathlib import Path
import sys
assert os.environ.get('Q4_PUNCH_RESUME') is None
Path('mr10-invoked').write_text('yes')
mode = os.environ.get('STAGE3_FAKE_MR10', 'PASS')
print('MR10 internal detail')
print('REGRESSION PANEL')
for label in ('data-movement/scalar-vector', 'calls/nested-recursion'):
    print(('FAIL' if mode == 'FAIL' and label.startswith('calls/') else 'PASS') + '  ' + label)
print('REGRESSION PANEL COMPLETE')
print('PASS  ' + ('1' if mode == 'FAIL' else '2'))
print('FAIL  ' + ('1' if mode == 'FAIL' else '0'))
print('TOTAL 2')
sys.exit(1 if mode == 'FAIL' else 0)
''')
        self.write_executable("tools/tests/run-suite", '''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
import tempfile
if sys.argv[1:] == ['--check']:
    print('test native manifests: OK')
    sys.exit(0)
assert len(sys.argv) in (5, 6)
assert sys.argv[2:5] == ['--run', '--profile', sys.argv[4]]
allow_device = sys.argv[5:] == ['--allow-device']
assert not sys.argv[5:] or allow_device
assert not allow_device or sys.argv[1] == 'bcplqsam'
assert os.environ.get('Q4_PUNCH_RESUME') is None
suite, profile = sys.argv[1], sys.argv[4]
with Path('native-invocations').open('a') as handle:
    handle.write(suite + ':' + profile + ('+device' if allow_device else '') + '\\n')
ids = {'bootstrap': ['00', '01'], 'runtime-extensions': ['147'],
       'bcpltime': ['159'], 'bcplqsam': ['163', '175', '176']}[suite]
state = os.environ.get('STAGE3_FAKE_NATIVE', 'PASS')
if state == 'BAD_ID':
    ids = ['999']
state = 'PASS' if state == 'BAD_ID' else state
path = Path(tempfile.mkdtemp(dir=Path('workarea/test-suites').resolve()))
states = {ident: ('BLOCKED' if suite == 'bcplqsam' and ident in ('175', '176')
          and not allow_device and state == 'PASS' else state) for ident in ids}
counts = {x: sum(value == x for value in states.values())
          for x in ('PASS', 'FAIL', 'SKIP', 'BLOCKED')}
(path / 'summary.json').write_text(json.dumps({
    'suite': suite, 'profile': profile, 'counts': counts,
    'cases': [{'id': x, 'status': states[x]} for x in ids]}) + '\\n')
print('native internal detail')
for ident in ids:
    print(f"{states[ident]:<7} {ident} {ident}-fake-case: result", flush=True)
print('Evidence: ' + str(path))
sys.exit(1 if counts['FAIL'] else 2 if counts['BLOCKED'] else 0)
''')
        (self.root / "workarea/test-suites").mkdir(parents=True)

    def invoke(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                rc = MOD.main(list(args))
            except SystemExit as exc:
                rc = exc.code
        return rc, stdout.getvalue(), stderr.getvalue()

    def report(self):
        runs = list(MOD.RUN_ROOT.iterdir())
        self.assertEqual(len(runs), 1)
        return json.loads((runs[0] / "summary.json").read_text())

    def test_offline_check_and_list_do_not_execute(self):
        rc, text, _ = self.invoke("--check")
        self.assertEqual(rc, 0)
        self.assertIn("PROJECT SUITE CHECK: PASS", text)
        self.assertIn("mr10\t2\t", text)
        rc, text, _ = self.invoke("--list", "--suite", "bcpltime")
        self.assertEqual(rc, 0)
        self.assertIn("bcpltime\t1\t", text)
        self.assertNotIn("bootstrap\t", text)
        self.assertFalse((self.root / "mr10-invoked").exists())
        self.assertFalse((self.root / "native-invocations").exists())

    def test_run_requires_explicit_suites_and_native_profile(self):
        for arguments in (
            ("--run",),
            ("--run", "--suite", "bootstrap"),
            ("--run", "--suite", "mr10", "--profile", "production"),
            ("--check", "--profile", "production"),
            ("--run", "--suite", "mr10", "--suite", "mr10"),
        ):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.invoke(*arguments)[0], 2)
        self.assertFalse(MOD.RUN_ROOT.exists())

    def test_mr10_separate_case_identity_and_counts(self):
        with patch.dict(os.environ, {"Q4_PUNCH_RESUME": "1"}):
            rc, output, errors = self.invoke("--run", "--suite", "mr10")
        self.assertEqual((rc, errors), (0, ""))
        self.assertIn("PROJECT REGRESSION RESULT: PASS", output)
        report = self.report()
        mr10 = report["suites"][0]
        self.assertEqual(mr10["status"], "PASS")
        self.assertEqual(mr10["counts"]["PASS"], 2)
        self.assertIsNone(mr10["counts"]["BLOCKED"])
        self.assertEqual([c["id"] for c in mr10["cases"]],
            ["data-movement/scalar-vector", "calls/nested-recursion"])
        self.assertTrue(all(s["status"] == "NOT_SELECTED"
                            for s in report["suites"][1:]))
        self.assertFalse((self.root / "native-invocations").exists())

    def test_mixed_run_has_independent_results_and_logs(self):
        rc, _, _ = self.invoke("--run", "--suite", "bcpltime",
                               "--suite", "mr10", "--profile", "installed-r5-t1")
        self.assertEqual(rc, 0)
        report = self.report()
        self.assertEqual(report["selected_suites"], ["mr10", "bcpltime"])
        self.assertEqual(report["native_profile"], "installed-r5-t1")
        self.assertEqual(report["git_head"], "test-git-revision")
        self.assertEqual([s["status"] for s in report["suites"]],
            ["PASS", "NOT_SELECTED", "NOT_SELECTED", "PASS", "NOT_SELECTED"])
        self.assertEqual(report["suites"][3]["cases"],
                         [{"id": "159", "status": "PASS"}])
        run_dir = next(MOD.RUN_ROOT.iterdir())
        self.assertTrue((run_dir / "bcpltime.log").is_file())
        self.assertEqual((self.root / "native-invocations").read_text(),
                         "bcpltime:installed-r5-t1\n")

    def test_mr10_failure_stops_before_native(self):
        with patch.dict(os.environ, {"STAGE3_FAKE_MR10": "FAIL"}):
            rc, _, _ = self.invoke("--run", "--suite", "mr10",
                                   "--suite", "bootstrap", "--profile", "production")
        self.assertEqual(rc, 1)
        report = self.report()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["suites"][0]["counts"],
            {"PASS": 1, "FAIL": 1, "SKIP": None, "BLOCKED": None, "TOTAL": 2})
        self.assertEqual(report["suites"][1]["status"], "NOT_RUN")
        self.assertFalse((self.root / "native-invocations").exists())

    def test_native_blocked_stops_before_next_suite(self):
        with patch.dict(os.environ, {"STAGE3_FAKE_NATIVE": "BLOCKED"}):
            rc, _, _ = self.invoke("--run", "--suite", "bootstrap",
                                   "--suite", "bcpltime", "--profile", "production")
        self.assertEqual(rc, 2)
        report = self.report()
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["suites"][1]["counts"]["BLOCKED"], 2)
        self.assertEqual(report["suites"][3]["status"], "NOT_RUN")
        self.assertEqual((self.root / "native-invocations").read_text(),
                         "bootstrap:production\n")

    def test_malformed_native_result_fails_closed(self):
        with patch.dict(os.environ, {"STAGE3_FAKE_NATIVE": "BAD_ID"}):
            rc, _, _ = self.invoke("--run", "--suite", "bcpltime",
                                   "--profile", "production")
        self.assertEqual(rc, 1)
        self.assertEqual(self.report()["suites"][3]["status"], "FAIL")
        self.assertIn("case IDs", self.report()["suites"][3]["error"])

    def test_device_cases_remain_blocked_without_opt_in(self):
        rc, output, errors = self.invoke("--run", "--suite", "bcplqsam",
                                         "--profile", "installed-r5-t1")
        self.assertEqual((rc, errors), (2, ""))
        self.assertIn("PROJECT REGRESSION RESULT: BLOCKED", output)
        report = self.report()
        self.assertFalse(report["allow_device"])
        self.assertEqual(report["suites"][4]["counts"],
                         {"PASS": 1, "FAIL": 0, "SKIP": 0, "BLOCKED": 2, "TOTAL": 3})
        self.assertEqual((self.root / "native-invocations").read_text(),
                         "bcplqsam:installed-r5-t1\n")

    def test_explicit_device_opt_in_only_reaches_bcplqsam(self):
        rc, output, errors = self.invoke("--run", "--suite", "mr10",
                                         "--suite", "bootstrap",
                                         "--suite", "bcplqsam",
                                         "--profile", "installed-r5-t1",
                                         "--allow-device")
        self.assertEqual((rc, errors), (0, ""))
        self.assertIn("PROJECT REGRESSION RESULT: PASS", output)
        report = self.report()
        self.assertTrue(report["allow_device"])
        self.assertEqual(report["suites"][4]["counts"],
                         {"PASS": 3, "FAIL": 0, "SKIP": 0, "BLOCKED": 0, "TOTAL": 3})
        self.assertEqual((self.root / "native-invocations").read_text(),
                         "bootstrap:installed-r5-t1\nbcplqsam:installed-r5-t1+device\n")
        self.assertTrue((self.root / "mr10-invoked").is_file())

    def test_device_opt_in_rejects_unrelated_or_host_only_modes(self):
        for arguments in (
            ("--check", "--allow-device"),
            ("--list", "--suite", "bcplqsam", "--allow-device"),
            ("--run", "--suite", "mr10", "--allow-device"),
            ("--run", "--suite", "bootstrap", "--profile", "production",
             "--allow-device"),
        ):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.invoke(*arguments)[0], 2)
        self.assertFalse(MOD.RUN_ROOT.exists())
        self.assertFalse((self.root / "native-invocations").exists())

    def test_progress_streams_both_runner_formats_and_preserves_logs(self):
        rc, output, errors = self.invoke("--run", "--suite", "mr10",
                                         "--suite", "bootstrap",
                                         "--suite", "bcplqsam",
                                         "--profile", "installed-r5-t1",
                                         "--allow-device", "--progress")
        self.assertEqual((rc, errors), (0, ""))
        for result in ("PASS    data-movement/scalar-vector",
                       "PASS    calls/nested-recursion",
                       "PASS    00", "PASS    01",
                       "PASS    163", "PASS    175", "PASS    176"):
            self.assertIn(result, output)
        self.assertNotIn("MR10 internal detail", output)
        self.assertNotIn("native internal detail", output)
        report = self.report()
        self.assertTrue(report["progress"])
        self.assertEqual(report["status"], "PASS")
        run_dir = next(MOD.RUN_ROOT.iterdir())
        self.assertIn("MR10 internal detail", (run_dir / "mr10.log").read_text())
        self.assertIn("native internal detail", (run_dir / "bootstrap.log").read_text())
        self.assertIn("native internal detail", (run_dir / "bcplqsam.log").read_text())
        self.assertEqual((self.root / "native-invocations").read_text(),
                         "bootstrap:installed-r5-t1\nbcplqsam:installed-r5-t1+device\n")

    def test_default_mode_does_not_echo_individual_cases(self):
        rc, output, _ = self.invoke("--run", "--suite", "bootstrap",
                                    "--profile", "production")
        self.assertEqual(rc, 0)
        self.assertNotIn("PASS    00", output)
        self.assertNotIn("native internal detail", output)
        self.assertFalse(self.report()["progress"])
        run_dir = next(MOD.RUN_ROOT.iterdir())
        self.assertIn("PASS    00", (run_dir / "bootstrap.log").read_text())

    def test_progress_rejected_in_host_only_modes(self):
        for args in (("--list", "--progress"),
                     ("--check", "--progress"),
                     ("--list", "--suite", "mr10", "--progress")):
            with self.subTest(args=args):
                self.assertEqual(self.invoke(*args)[0], 2)
        self.assertFalse(MOD.RUN_ROOT.exists())

    def test_progress_reports_blocked_cases_without_device_opt_in(self):
        rc, output, errors = self.invoke("--run", "--suite", "bcplqsam",
                                         "--profile", "installed-r5-t1",
                                         "--progress")
        self.assertEqual((rc, errors), (2, ""))
        self.assertIn("PASS    163", output)
        self.assertIn("BLOCKED 175", output)
        self.assertIn("BLOCKED 176", output)
        report = self.report()
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["suites"][4]["counts"]["BLOCKED"], 2)
        self.assertFalse(report["allow_device"])

    def test_progress_failure_stops_before_next_suite(self):
        with patch.dict(os.environ, {"STAGE3_FAKE_MR10": "FAIL"}):
            rc, output, errors = self.invoke("--run", "--suite", "mr10",
                                             "--suite", "bootstrap",
                                             "--profile", "production",
                                             "--progress")
        self.assertEqual((rc, errors), (1, ""))
        self.assertIn("FAIL    calls/nested-recursion", output)
        self.assertEqual(self.report()["suites"][1]["status"], "NOT_RUN")
        self.assertFalse((self.root / "native-invocations").exists())

    def test_missing_mr10_fixture_fails_offline_check(self):
        (self.root / "fixture/scalar-vector.expected").unlink()
        rc, _, message = self.invoke("--check")
        self.assertEqual(rc, 2)
        self.assertIn("missing/outside-repository", message)
        self.assertFalse((self.root / "mr10-invoked").exists())


if __name__ == "__main__":
    unittest.main()
