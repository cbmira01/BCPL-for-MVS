"""Host-only Stage 2B suite validation and wrapper tests (never submits JES)."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "tests" / "run-suite"
SPEC = importlib.util.spec_from_loader("stage2b_run_suite", SourceFileLoader("stage2b_run_suite", str(SOURCE)))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import stage2b suite runner")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class TestStage2BSuites(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.create_fixture()

    def create_fixture(self):
        suites = self.root / "tests" / "suites"
        cases = self.root / "bootstrap-toolchain" / "regression"
        suites.mkdir(parents=True)
        cases.mkdir(parents=True)
        lines = {name: ["\t".join(MOD.HEADERS)] for name in MOD.SUITES}
        for i in range(177):
            name = ("bootstrap" if i <= 145 else "runtime-extensions" if i <= 158
                    else "bcpltime" if i <= 162 else "bcplqsam")
            ident = MOD.canonical(i)
            directory = f"{ident}-fake-case"
            home = cases / directory
            home.mkdir()
            if name == "bcplqsam":
                (home / "qsam-native.txt").touch()
            if name == "bcpltime":
                (home / "time-selection.asm").touch()
            if name == "runtime-extensions":
                (home / "extension-selection.asm").touch()
            policy = "skip-installed" if i == 83 else "device-opt-in" if i in (175, 176) else "standard"
            prereqs = ["boot-obj"]
            if i == 175:
                prereqs.append("jes-punch")
            if i == 176:
                prereqs.append("jes-printer")
            row = (ident, directory, ",".join(MOD.PROFILES), ",".join(prereqs), "demo", policy)
            lines[name].append("\t".join(row))
        for name, entries in lines.items():
            (suites / f"{name}.tsv").write_text("\n".join(entries) + "\n", encoding="utf-8")
        folder = self.root / "tools" / "bootstrap"
        folder.mkdir(parents=True)
        stub = '''#!/usr/bin/env python3
import os
from pathlib import Path
import sys
n = int(sys.argv[1])
assert sys.argv[2] == '--log-dir'
logs = Path(sys.argv[3]); assert logs.is_absolute(); logs.mkdir(parents=True, exist_ok=True)
assert os.getenv('Q4_PUNCH_RESUME') is None
(logs / 'marker').write_text(str(n))
ident = f'{n:02d}' if n <= 52 else f'{n:03d}'
print(f'PASS  {ident}  fake-case')
print('PASS  1\\nFAIL  0\\nSKIP  0\\nTOTAL 1')
'''
        for executable in MOD.PROFILES:
            filename = "run-production-regression" if executable == "production" else "run-installed-r5-t1-regression"
            dest = folder / filename
            dest.write_text(stub, encoding="utf-8")
            dest.chmod(0o755)

    def test_complete_manifest_and_ownership(self):
        suites = MOD.validate(self.root)
        self.assertEqual({s: len(c) for s, c in suites.items()}, dict(zip(MOD.SUITES, MOD.COUNTS)))
        self.assertEqual([x.ident for x in suites["bootstrap"][:2]], ["00", "01"])
        self.assertEqual(suites["bcplqsam"][-1].ident, "176")

    def test_duplicate_and_missing_case_rejected(self):
        file = self.root / "tests" / "suites" / "bcplqsam.tsv"
        original = file.read_text()
        file.write_text(original.replace("163-fake-case", "162-fake-case", 1))
        with self.assertRaises(MOD.ManifestError):
            MOD.validate(self.root)
        file.write_text(original)
        (self.root / "bootstrap-toolchain/regression/176-fake-case/qsam-native.txt").unlink()
        with self.assertRaises(MOD.ManifestError):
            MOD.validate(self.root)

    def test_invalid_paths_and_profiles_rejected(self):
        file = self.root / "tests" / "suites" / "bootstrap.tsv"
        original = file.read_text()
        file.write_text(original.replace("00-fake-case", "../00-fake-case", 1))
        with self.assertRaises(MOD.ManifestError):
            MOD.validate(self.root)
        file.write_text(original.replace("production,installed-r5-t1", "broken-profile", 1))
        with self.assertRaises(MOD.ManifestError):
            MOD.validate(self.root)

    def test_no_duplicate_suite_reporting_and_case_filter(self):
        a = SimpleNamespace(suite="bcpltime", case=[160], tag=[])
        cases = MOD.selected_cases(MOD.validate(self.root)["bcpltime"], a)
        self.assertEqual([x.number for x in cases], [160])
        a.case = [170]
        with self.assertRaises(MOD.ManifestError):
            MOD.selected_cases(MOD.validate(self.root)["bcpltime"], a)

    def test_native_dispatch_preserves_run_scoped_logs(self):
        rows = MOD.validate(self.root)["bcpltime"]
        a = SimpleNamespace(suite="bcpltime", profile="installed-r5-t1", allow_device=False)
        self.assertEqual(MOD.run(self.root, rows[:2], a), 0)
        evidence = list((self.root / "workarea/test-suites").iterdir())
        self.assertEqual(len(evidence), 1)
        data = json.loads((evidence[0] / "summary.json").read_text())
        self.assertEqual(data["counts"], {"PASS": 2, "FAIL": 0, "SKIP": 0, "BLOCKED": 0})
        self.assertTrue((evidence[0] / "case-159/native-logs/marker").is_file())
        self.assertTrue((evidence[0] / "case-160/runner.log").is_file())
        self.assertEqual(MOD.run(self.root, rows[:1], a), 0)
        self.assertEqual(len(list((self.root / "workarea/test-suites").iterdir())), 2)

    def test_skip_083_and_block_device_without_jcl(self):
        bootstrap = MOD.validate(self.root)["bootstrap"]
        a = SimpleNamespace(suite="bootstrap", profile="production", allow_device=False)
        self.assertEqual(MOD.run(self.root, [bootstrap[83]], a), 0)
        qsam = MOD.validate(self.root)["bcplqsam"]
        a.suite = "bcplqsam"
        self.assertEqual(MOD.run(self.root, qsam[-2:], a), 2)
        entries = list((self.root / "workarea/test-suites").iterdir())
        blocked = [p for p in entries if "bcplqsam" in p.name][0]
        self.assertFalse((blocked / "case-175").exists())
        self.assertEqual(json.loads((blocked / "summary.json").read_text())["counts"]["BLOCKED"], 2)

    def test_explicit_device_opt_in_still_never_resumes_punch(self):
        qsam = MOD.validate(self.root)["bcplqsam"]
        a = SimpleNamespace(suite="bcplqsam", profile="production", allow_device=True)
        self.assertEqual(MOD.run(self.root, qsam[-2:-1], a), 0)


if __name__ == "__main__":
    unittest.main()
