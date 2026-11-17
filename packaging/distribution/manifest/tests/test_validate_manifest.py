"""Offline TA.0 validation tests: all fixtures are generated in temporary directories."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / "tools/distribution/validate-manifest.py"
INVENTORY = ROOT / "packaging/distribution/manifest/ta0-inventory.yaml"
spec = importlib.util.spec_from_file_location("ta0_validate", CODE)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class ManifestValidation(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.manifest = validator.load(INVENTORY)
        # Fake development map with *real selected keys/members* but no
        # connection to MVS or developer user configuration.
        datasets = {}
        for row in self.manifest["datasets"][2:]:
            key = row["dspal_key"]
            suffix = row["target_dsn_template"].replace("{HLQ}.", "")
            members, generated = {}, {}
            for m in row["members"]:
                if key in validator.BINARY_KEYS or m in row.get("generated_members", {}):
                    continue
                if key == "BOOT_SOURCE" and m == "BLIB":
                    generated[m] = "workarea/bootstrap-cambridge/demoted/blib"
                    continue
                src = f"fixture/{key}/{m}.txt"
                members[m] = src
                file = self.root / src
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("fixture only\n", encoding="utf-8")
            datasets[key] = {**row["target_dcb"], "dsn": suffix, "members": members,
                             "generated_members": generated, "populate": False}
        self.dspal = {"datasets": datasets}

    def check(self, doc=None, *, release=False):
        return validator.check(doc or self.manifest, self.dspal, self.root, release=release)

    def failure(self, text, mutation, *, release=False):
        doc = copy.deepcopy(self.manifest)
        mutation(doc)
        with self.assertRaisesRegex(validator.ManifestError, text):
            self.check(doc, release=release)

    def test_full_design_inventory(self):
        info = self.check()
        self.assertEqual(info["logical_datasets"], 20)
        self.assertEqual(info["selected_members"], 127)
        self.assertEqual(info["mr10_members"], 79)
        self.assertEqual(info["last_tape_alias"], "BCPL.BT0020")
        self.assertEqual(info["native_compiler"], "absent")

    def test_draft_not_candidate(self):
        with self.assertRaisesRegex(validator.ManifestError, "cannot freeze a design-only"):
            self.check(release=True)

    def test_candidate_without_identity_fails(self):
        self.failure("missing release version", lambda d: d.update(phase="candidate"), release=True)

    def test_reserved_bootstrap_roles(self):
        self.failure("BT0001", lambda d: d["datasets"][0].update(generator="wrong"))
        self.failure("BT0002", lambda d: d["datasets"][1].update(generator="wrong"))

    def test_position_gap(self):
        self.failure("non-contiguous", lambda d: d["datasets"][8].update(sequence=11))

    def test_wrong_group(self):
        self.failure("wrong group", lambda d: d["datasets"][8].update(group="native"))

    def test_duplicate_member(self):
        self.failure("duplicate member", lambda d: d["datasets"][3]["members"].append("SYNI"))

    def test_missing_required_member(self):
        self.failure("incorrect TA.0 member count", lambda d: d["datasets"][3]["members"].remove("TRNI"))

    def test_unmapped_member(self):
        self.failure("missing Git-backed|unmapped member", lambda d: d["datasets"][3]["members"].__setitem__(1,"UNMAPP"))

    def test_candidate_member_rejected(self):
        self.failure("candidate member", lambda d: d["datasets"][3]["members"].__setitem__(1,"ICLIBC"))

    def test_invalid_target_name(self):
        self.failure("target HLQ template mismatch", lambda d: d["datasets"][3].update(target_dsn_template="HERC02.BCPL.MR10KIT.SOURCE"))

    def test_object_baseline_guard(self):
        self.failure("accepted ten-member", lambda d: d["datasets"][12]["members"].__setitem__(0,"BCPLM99"))

    def test_load_library_dcb(self):
        self.failure("expected U 0/6144 load library", lambda d: d["datasets"][11]["target_dcb"].update(blksize=4096))

    def test_no_native_compiler_placeholder(self):
        self.failure("native_compiler|invalid", lambda d: d["release"].update(native_compiler="unknown"))
        self.failure("invalid native-only dependency closure", lambda d: d["profiles"]["native-only"].append("mr10"))

    def test_untracked_git_source(self):
        (self.root / "fixture/MR10_SOURCE/SYNI.txt").unlink()
        with self.assertRaisesRegex(validator.ManifestError, "missing or unsafe Git-backed"):
            self.check()

    def test_duplicate_yaml_keys_rejected(self):
        path = self.root / "duplicate.yaml"
        path.write_text("schema_version: 1\nschema_version: 2\n")
        with self.assertRaisesRegex(validator.ManifestError, "duplicate YAML"):
            validator.load(path)

    def test_audit_report_covers_all_members_and_keeps_rights_unreviewed(self):
        self.check()
        result = validator.provenance_report(self.manifest, self.dspal)
        self.assertEqual(result["summary"], {
            "members": 127, "git_source": 110, "generated": 2,
            "resident_binary": 15, "rights_unreviewed": 127,
            "mvs_receipts_recorded": 0})
        self.assertTrue(all(x["redistribution_review"] == "UNREVIEWED" for x in result["members"]))
        self.assertEqual(len({(x["dataset_key"], x["member"]) for x in result["members"]}), 127)

    def test_generated_and_resident_binary_lineage_are_pending(self):
        self.check()
        rows = {(x["dataset_key"], x["member"]): x for x in
                validator.provenance_report(self.manifest, self.dspal)["members"]}
        self.assertEqual(rows["BOOT_SOURCE", "BLIB"]["source_class"], "generated")
        self.assertEqual(rows["BOOT_ASM", "COROUTIN"]["source_class"], "generated")
        self.assertEqual(rows["MR10_SOURCE", "SYNI"]["source_class"], "git_source")
        self.assertEqual(rows["BOOT_OBJ", "COROUTIN"]["source_class"], "resident_binary")
        self.assertEqual(rows["BOOT_OBJ", "COROUTIN"]["source_hint_not_evidence"],
                         "BOOT_ASM(COROUTIN)")
        self.assertEqual(rows["BOOT_OBJ", "COROUTIN"]["logical_owner"], "coroutine-support")
        self.assertIsNone(rows["MR10_LOAD", "ICINT19"]["mvs_build_receipt"])

    def test_path_traversal_and_symlink_escape_rejected(self):
        self.dspal["datasets"]["MR10_SOURCE"]["members"]["SYNI"] = "../../etc/passwd"
        with self.assertRaisesRegex(validator.ManifestError, "unsafe Git-backed"):
            self.check()
        src = self.root / "elsewhere"
        src.mkdir()
        external = self.root.parent / (self.root.name + "-external")
        external.write_text("external\n")
        self.addCleanup(external.unlink)
        (src / "external").symlink_to(external)
        self.dspal["datasets"]["MR10_SOURCE"]["members"]["SYNI"] = "elsewhere/external"
        with self.assertRaisesRegex(validator.ManifestError, "unsafe Git-backed"):
            self.check()

    def test_unselected_generated_source_not_allowed(self):
        self.failure("generated_members must only name selected",
                     lambda d: d["datasets"][13]["generated_members"].update(
                         NOTHERE="unapproved generated member"))

    def test_included_compiler_requires_all_nine_datasets(self):
        def change(d):
            d["release"]["native_compiler"] = "included"
            d["profiles"]["native-only"].append("cambridge")
            d["profiles"]["combined"].append("cambridge")
        self.failure("nine compiler datasets", change)

    def test_cli_audit_json(self):
        fake = self.root / "dspal.yaml"
        fake.write_text(yaml.safe_dump(self.dspal), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(CODE),
                              "--manifest", str(INVENTORY), "--dspal", str(fake),
                              "--root", str(self.root), "--audit-json"],
                             text=True, capture_output=True, check=True)
        parsed = json.loads(run.stdout)
        self.assertEqual(parsed["summary"]["members"], 127)
        self.assertEqual(parsed["summary"]["rights_unreviewed"], 127)
        self.assertNotIn("MANIFEST PASS", run.stdout)

    def test_cli_release_gate_rejects_draft(self):
        fake = self.root / "dspal.yaml"
        fake.write_text(yaml.safe_dump(self.dspal), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(CODE),
                              "--manifest", str(INVENTORY), "--dspal", str(fake),
                              "--root", str(self.root), "--release"],
                             text=True, capture_output=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("cannot freeze a design-only", run.stderr)

    def test_draft_is_not_mutated(self):
        original = copy.deepcopy(self.manifest)
        self.check()
        self.assertEqual(original, self.manifest)


if __name__ == "__main__":
    unittest.main()
