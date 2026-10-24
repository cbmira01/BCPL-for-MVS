#!/usr/bin/env python3
"""Offline checks for resident R.5 BCPLDEMO installation JCL (no MVS jobs)."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config/dspal.yaml"
JCL = ROOT / "bootstrap-toolchain/jcl/r5dinst.jcl"
RUNBOOK = ROOT / "packaging/clean-room-mvs-reconstruction.md"
SUBMIT = ROOT / "tools/datasets/dspal-submit.py"


class R5InstalledJobMember(unittest.TestCase):
    def test_canonical_jcl_manifest_member(self):
        config = MANIFEST.read_text(encoding="utf-8")
        section = config.split("\n  BOOT_JCL:\n", 1)[1].split(
            "\n  BOOT_OBJ:\n", 1
        )[0]
        self.assertEqual(
            section.count("R5DINST: bootstrap-toolchain/jcl/r5dinst.jcl"), 1
        )
        self.assertTrue(JCL.is_file())
        checker = (ROOT / "tools/checks/check-native-jcl-manifest.py").read_text()
        self.assertIn('"R5DINST",', checker)
        self.assertIn("PASS: 13 canonical BOOT_JCL members", checker)

    def test_job_is_a_clean_fb80_body(self):
        body = JCL.read_text(encoding="ascii")
        records = body.splitlines()
        self.assertTrue(records)
        self.assertEqual(records[-1], "//")
        self.assertTrue(all(len(line) <= 80 and line.isascii() for line in records))
        self.assertFalse(any(
            re.match(r"^//[^* ]\S*\s+JOB\b", line) for line in records
        ))
        self.assertNotIn("PASSWORD=", body)
        self.assertNotIn("USER=", body)
        steps = re.findall(r"^//(\w+)\s+EXEC PGM=(\w+)", body, flags=re.M)
        self.assertEqual(
            steps,
            [
                ("ASMDEMO", "IFOX00"),
                ("PUTDEMO", "IEBGENER"),
                ("READBACK", "IEBGENER"),
                ("VERIFY", "IEBCOMPR"),
            ],
        )

    def test_binary_object_install_has_readback_comparison(self):
        body = JCL.read_text(encoding="ascii")
        self.assertIn(
            "DSN=HERC02.BCPL.EXT.ASM(BCPLDEMO),DISP=SHR", body
        )
        self.assertIn(
            "DSN=HERC02.BCPL.EXT.OBJ(BCPLDEMO),DISP=OLD", body
        )
        self.assertIn("EXEC PGM=IEBCOMPR", body)
        self.assertIn("COMPARE TYPORG=PS", body)
        self.assertIn("COND=(0,NE,ASMDEMO)", body)
        self.assertIn("COND=(0,NE,PUTDEMO)", body)
        self.assertIn("COND=(0,NE,READBACK)", body)
        self.assertNotIn("DSN=HERC02.BCPL.BOOT.OBJ(", body)
        self.assertNotIn("DSN=HERC02.BCPL.BOOT.DEVOBJ(", body)

    def test_dspal_submit_owns_credentials_and_internal_reader(self):
        source = SUBMIT.read_text(encoding="utf-8")
        self.assertIn("authenticated_job_card", source)
        self.assertIn("SYSOUT=(A,INTRDR)", source)
        self.assertIn("Payload:  JOB", source)
        self.assertIn("wait_for_payload_completion", source)

    def test_runbook_uses_single_resident_submit_command(self):
        guide = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("tools/datasets/dspal submit BOOT_JCL R5DINST", guide)
        self.assertIn("tools/bootstrap/run-production-regression 0 162", guide)
        self.assertIn("| PASS | **162**", guide)
        self.assertIn("| TOTAL | **163**", guide)
        for obsolete in (
            "python3 - <<",
            "tools/mvs/prepare-bcpldemo-install",
            "workarea/runtime-extensions-r5/install-bcpldemo.jcl",
            "tools/mvs/submit-jcl workarea/runtime-extensions-r5",
        ):
            self.assertNotIn(obsolete, guide)


if __name__ == "__main__":
    unittest.main()
