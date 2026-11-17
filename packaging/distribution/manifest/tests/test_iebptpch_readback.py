"""Offline synthetic fixtures for the TA.0 non-submitting IEBPTPCH JCL renderer."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

SOURCE = Path(__file__).resolve().parents[4] / "tools/distribution/prepare-iebptpch-readback.py"
SPEC = importlib.util.spec_from_file_location("ta0_iebptpch_prep", SOURCE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class PrepareReadback(unittest.TestCase):
    def setUp(self):
        self.manifest = {"datasets": []}
        self.dspal = {"mvs": {"hlq": "HERC02"}, "datasets": {}}
        for key, suffix, members in (
            ("MR10_OBJ", "BCPL.MR10KIT.OBJ", ["ICINT19"]),
            ("BOOT_OBJ", "BCPL.BOOT.OBJ", ["BCPLMAIN", "BLIB", "COROUTIN"]),
            ("EXT_OBJ", "BCPL.EXT.OBJ", ["BCPLDEMO", "BCPLTIME", "BCPLQSAM"]),
        ):
            self.manifest["datasets"].append({
                "dspal_key": key,
                "kind": "pds_unload", "transfer": "iebcopy_unload",
                "members": members,
                "target_dcb": {"dsorg": "PO", "recfm": "FB", "lrecl": 80, "blksize": 800},
            })
            self.dspal["datasets"][key] = {
                "dsn": suffix, "dsorg": "PO", "recfm": "FB",
                "lrecl": 80, "blksize": 800, "content_type": "object",
            }

    def render(self, key="EXT_OBJ", member="BCPLDEMO", **kwargs):
        return mod.make_job_body(self.manifest, self.dspal,
                                 dataset_key=key, member=member, **kwargs)

    def test_pilot_body_is_read_only_and_complete(self):
        body = self.render()
        self.assertIn("//SYSUT1   DD DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR\n", body)
        self.assertIn("PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1", body)
        self.assertIn("MEMBER NAME=BCPLDEMO", body)
        self.assertIn("//SYSUT2   DD SYSOUT=*", body)
        self.assertNotIn("DISP=OLD", body)
        self.assertNotIn("//TA0HEX   JOB", body)
        self.assertNotIn("STOPAFT", body)
        self.assertTrue(body.endswith("/*\n"))
        self.assertTrue(all(len(line) <= 80 for line in body.splitlines()))

    def test_each_allowed_dataset(self):
        for key, member in (("MR10_OBJ", "ICINT19"),
                            ("BOOT_OBJ", "COROUTIN"), ("EXT_OBJ", "BCPLTIME")):
            with self.subTest(key=key):
                self.assertIn(f"MEMBER NAME={member}", self.render(key, member))

    def test_site_hlq_override_only_changes_source_dataset(self):
        self.assertIn("DSN=SITEABC.BCPL.BOOT.OBJ,DISP=SHR",
                      self.render("BOOT_OBJ", "BLIB", hlq="SITEABC"))

    def test_missing_member_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "not selected"):
            self.render("BOOT_OBJ", "MISSING")

    def test_development_only_member_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "not selected"):
            self.render("BOOT_OBJ", "BCPLDEC")

    def test_lowercase_member_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "uppercase"):
            self.render(member="bcpldemo")

    def test_illegal_member_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "legal MVS"):
            self.render(member="BCPL-DEMO")

    def test_load_library_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "load libraries"):
            self.render("MR10_LOAD", "ICINT19")

    def test_unlisted_dataset_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "three FB80"):
            self.render("BOOT_SOURCE", "LIBHDR")

    def test_duplicate_dataset_key_rejected(self):
        self.manifest["datasets"].append(copy.deepcopy(self.manifest["datasets"][0]))
        with self.assertRaisesRegex(mod.PreparationError, "exactly one"):
            self.render("MR10_OBJ", "ICINT19")

    def test_mismatched_manifest_dcb_rejected(self):
        self.manifest["datasets"][2]["target_dcb"]["blksize"] = 400
        with self.assertRaisesRegex(mod.PreparationError, "selected DCB"):
            self.render()

    def test_mismatched_dspal_dcb_rejected(self):
        self.dspal["datasets"]["EXT_OBJ"]["recfm"] = "U"
        with self.assertRaisesRegex(mod.PreparationError, "binary FB80"):
            self.render()

    def test_non_object_source_rejected(self):
        self.dspal["datasets"]["EXT_OBJ"].pop("content_type")
        with self.assertRaisesRegex(mod.PreparationError, "binary FB80"):
            self.render()

    def test_missing_dspal_key_rejected(self):
        del self.dspal["datasets"]["EXT_OBJ"]
        with self.assertRaisesRegex(mod.PreparationError, "missing dspal"):
            self.render()

    def test_malformed_hlq_rejected(self):
        with self.assertRaisesRegex(mod.PreparationError, "HLQ"):
            self.render(hlq="HERC02.DATA")

    def test_missing_manifest_members_rejected(self):
        self.manifest["datasets"][2]["members"] = None
        with self.assertRaisesRegex(mod.PreparationError, "not selected"):
            self.render()

    def test_unexpected_transfer_rejected(self):
        self.manifest["datasets"][2]["transfer"] = "seq"
        with self.assertRaisesRegex(mod.PreparationError, "unsupported"):
            self.render()

    def test_missing_manifest_dataset_rejected(self):
        self.manifest["datasets"].pop()
        with self.assertRaisesRegex(mod.PreparationError, "exactly one"):
            self.render()

    def test_invalid_dsn_suffix_rejected(self):
        self.dspal["datasets"]["EXT_OBJ"]["dsn"] = "BCPL..EXT"
        with self.assertRaisesRegex(mod.PreparationError, "invalid dspal"):
            self.render()

    def test_cli_success_and_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[4] / 'workarea') as temp:
            manifest_path, dspal_path = Path(temp) / "manifest.yaml", Path(temp) / "dspal.yaml"
            manifest_path.write_text(yaml.safe_dump(self.manifest), encoding="utf-8")
            dspal_path.write_text(yaml.safe_dump(self.dspal), encoding="utf-8")
            args = [sys.executable, "-B", str(SOURCE),
                    "--manifest", str(manifest_path), "--dspal", str(dspal_path)]
            good = subprocess.run(args + ["--dataset-key", "EXT_OBJ", "--member", "BCPLDEMO"],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("DSN=HERC02.BCPL.EXT.OBJ", good.stdout)
            bad = subprocess.run(args + ["--dataset-key", "MR10_LOAD", "--member", "ICINT19"],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(bad.returncode, 1)
            self.assertEqual(bad.stdout, "")
            self.assertIn("load libraries", bad.stderr)


if __name__ == "__main__":
    unittest.main()
