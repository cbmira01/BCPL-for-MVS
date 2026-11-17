"""Offline JCL scope/HLQ dependency scanner tests; no JES or tape operations."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCANNER_PATH = ROOT / "tools/distribution/audit-jcl-dependencies.py"
INVENTORY = ROOT / "packaging/distribution/manifest/ta0-inventory.yaml"
_spec = importlib.util.spec_from_file_location("ta0_jcl_audit", SCANNER_PATH)
assert _spec and _spec.loader
scanner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scanner)


class JCLDependencyAudit(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        self.manifest = scanner._validation.load(INVENTORY)
        datasets = {}
        for row in self.manifest["datasets"][2:]:
            key = row["dspal_key"]
            members = {}
            for member in row["members"]:
                if key in scanner._validation.BINARY_KEYS or member in row.get("generated_members", {}):
                    continue
                if key == "BOOT_SOURCE" and member == "BLIB":
                    continue
                src = f"fixture/{key}/{member}.txt"
                members[member] = src
                location = self.root / src
                location.parent.mkdir(parents=True, exist_ok=True)
                if key == "MR10_JCL":
                    text = ("//GO EXEC PGM=ICINT19\n"
                            "//STEPLIB DD DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR\n"
                            "//SYSIN DD DSN=HERC02.BCPL.MR10KIT.SOURCE(SYNI),DISP=SHR\n")
                elif key == "BOOT_JCL":
                    text = ("//ASM EXEC PGM=IFOX00\n"
                            "//SYSLIB DD DSN=SYS1.MACLIB,DISP=SHR\n"
                            "//SYSIN DD DSN=HERC02.BCPL.BOOT.ASM(BCPLMAIN),DISP=SHR\n"
                            "//SYSPUNCH DD DSN=&&OBJ,DISP=(NEW,PASS)\n")
                else:
                    text = "placeholder source\n"
                location.write_text(text, encoding="utf-8")
            data = {**row["target_dcb"],
                    "dsn": row["target_dsn_template"].removeprefix("{HLQ}."),
                    "members": members,
                    "generated_members": ({"BLIB": "workarea/bootstrap-cambridge/demoted/blib"}
                                          if key == "BOOT_SOURCE" else {}),
                    "populate": False}
            datasets[key] = data
        self.dspal = {"datasets": datasets}
        scanner._validation.check(self.manifest, self.dspal, self.root)

    def _jcl(self, key="MR10_JCL", name="MRREGRES"):
        return self.root / self.dspal["datasets"][key]["members"][name]

    def _audit(self):
        return scanner.audit(self.manifest, self.dspal, self.root)

    def test_ten_jobs_and_profile_independence(self):
        report = self._audit()
        self.assertEqual(report["summary"], {
            "jobs": 10, "unresolved_dependencies": 0,
            "jobs_requiring_site_adaptation": 10,
            "jobs_referencing_sys1_maclib": 6,
            "mr10_jobs": 4, "native_jobs": 6})
        self.assertFalse(report["problems"])
        self.assertFalse(any("CAMBCOMP" in str(x) for x in report["jobs"]))

    def test_missing_job_cards_explicit(self):
        report = self._audit()
        self.assertTrue(all(not x["has_job_card"] for x in report["jobs"]))
        self.assertTrue(all("site JOB card required" in x["adaptations_required"]
                            for x in report["jobs"]))

    def test_site_hlq_not_treated_as_recipient_ready(self):
        report = self._audit()
        self.assertTrue(all(x["development_hlq_present"] for x in report["jobs"]))
        self.assertTrue(all("replace development HERC02 HLQ" in x["adaptations_required"]
                            for x in report["jobs"]))

    def test_unknown_dataset_fails(self):
        with self._jcl().open("a") as dest:
            dest.write("//BAD DD DSN=HERC02.BCPL.BOOT.DEVOBJ,DISP=SHR\n")
        self.assertIn("unselected permanent DSN", " ".join(self._audit()["problems"]))

    def test_cross_profile_dependency_fails(self):
        with self._jcl().open("a") as dest:
            dest.write("//BAD DD DSN=HERC02.BCPL.BOOT.OBJ(BCPLMAIN),DISP=SHR\n")
        self.assertIn("cross-profile reference", " ".join(self._audit()["problems"]))

    def test_unselected_member_fails(self):
        with self._jcl().open("a") as dest:
            dest.write("//BAD DD DSN=HERC02.BCPL.MR10KIT.SOURCE(ICLIBC),DISP=SHR\n")
        self.assertIn("unselected PDS member", " ".join(self._audit()["problems"]))

    def test_executable_mr10_without_load_reference_fails(self):
        path = self._jcl()
        path.write_text("//GO EXEC PGM=ICINT19\n"
                        "//SYSIN DD DSN=HERC02.BCPL.MR10KIT.SOURCE(SYNI)\n")
        self.assertIn("without selected MR10_LOAD", " ".join(self._audit()["problems"]))

    def test_undeclared_program_fails(self):
        with self._jcl().open("a") as dest:
            dest.write("//INJ EXEC PGM=CAMBCOMP\n")
        self.assertIn("program dependency not in verified scope: CAMBCOMP",
                      " ".join(self._audit()["problems"]))

    def test_other_permanent_dsn_fails(self):
        with self._jcl().open("a") as dest:
            dest.write("//DATA DD DSN=OTHER.PROJ.DATA,DISP=SHR\n")
        self.assertIn("external permanent DSN", " ".join(self._audit()["problems"]))

    def test_comment_and_instream_card_not_dependency(self):
        with self._jcl().open("a") as dest:
            dest.write("//* IGNORE DD DSN=HERC02.BAD.BAD\n")
            dest.write("  DSN=HERC02.BAD.BAD (in-stream data)\n")
        self.assertFalse(self._audit()["problems"])

    def test_job_card_removes_one_adaptation(self):
        path = self._jcl()
        path.write_text("//TESTJOB JOB (1),'A',CLASS=A\n" + path.read_text())
        row = next(x for x in self._audit()["jobs"] if x["member"] == "MRREGRES")
        self.assertTrue(row["has_job_card"])
        self.assertNotIn("site JOB card required", row["adaptations_required"])

    def test_unlinked_source_is_reported_as_error(self):
        self._jcl().unlink()
        self.assertIn("missing/unsafe Git JCL source", " ".join(self._audit()["problems"]))

    def test_site_adapted_jcl_can_pass_read_only_strict_check(self):
        for key in ("MR10_JCL", "BOOT_JCL"):
            for member, path in self.dspal["datasets"][key]["members"].items():
                loc = self.root / path
                loc.write_text("//TA0JOB JOB (1),\'RELEASE\',CLASS=A\n" +
                               loc.read_text().replace("HERC02.", "SITEABC."),
                               encoding="utf-8")
        report = scanner.audit(self.manifest, self.dspal, self.root, site_hlq="SITEABC")
        self.assertFalse(report["problems"])
        self.assertEqual(report["summary"]["jobs_requiring_site_adaptation"], 0)
        self.assertTrue(all(x["has_job_card"] for x in report["jobs"]))

    def test_invalid_site_hlq_fails_closed(self):
        with self.assertRaisesRegex(scanner.JCLAuditError, "invalid site HLQ"):
            scanner.audit(self.manifest, self.dspal, self.root, site_hlq="NOT.LEGAL")

    def test_cli_strict_accepts_site_adapted_fixture(self):
        for key in ("MR10_JCL", "BOOT_JCL"):
            for path in self.dspal["datasets"][key]["members"].values():
                loc = self.root / path
                loc.write_text("//TA0JOB JOB (1),\'RELEASE\',CLASS=A\n" +
                               loc.read_text().replace("HERC02.", "SITEABC."),
                               encoding="utf-8")
        config = self.root / "dspal.yaml"
        config.write_text(yaml.safe_dump(self.dspal), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(SCANNER_PATH),
                              "--manifest", str(INVENTORY),
                              "--dspal", str(config), "--root", str(self.root),
                              "--hlq", "SITEABC", "--strict"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("0 require site adaptation", run.stdout)

    def test_cli_json_and_strict_fail(self):
        path = self.root / "dspal.yaml"
        path.write_text(yaml.safe_dump(self.dspal), encoding="utf-8")
        cmd = [sys.executable, "-B", str(SCANNER_PATH), "--manifest", str(INVENTORY),
               "--dspal", str(path), "--root", str(self.root)]
        import json
        out = subprocess.run(cmd + ["--json"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout)["summary"]["jobs"], 10)
        strict = subprocess.run(cmd + ["--strict"], capture_output=True, text=True)
        self.assertNotEqual(strict.returncode, 0)
        self.assertIn("10 require site adaptation", strict.stdout)


if __name__ == "__main__":
    unittest.main()
