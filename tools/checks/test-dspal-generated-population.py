#!/usr/bin/env python3
"""Offline regression tests for two-pass dspal bootstrap population."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/datasets/dspal-populate.py"
spec = importlib.util.spec_from_file_location("dspal_population_under_test", SCRIPT)
assert spec is not None and spec.loader is not None
pop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pop)


class GeneratedPopulationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.saved_root = pop.ROOT
        pop.ROOT = self.root
        self.addCleanup(setattr, pop, "ROOT", self.saved_root)
        (self.root / "tracked.txt").write_text("tracked source\n")
        self.generated_rel = "workarea/bootstrap-cambridge/demoted/blib"
        self.generated_path = self.root / self.generated_rel
        self.config = {
            "mvs": {"hlq": "TEST"},
            "text": {"host_encoding": "utf-8"},
            "datasets": {
                "BOOT_SOURCE": {
                    "dsn": "BCPL.BOOT.SOURCE",
                    "populate": True,
                    "recfm": "FB",
                    "lrecl": 80,
                    "members": {"STATIC": "tracked.txt"},
                    "generated_members": {"BLIB": self.generated_rel},
                }
            },
        }
        normalize = mock.patch.object(
            pop.io, "normalize_input_text", side_effect=lambda config, text, width: [text]
        )
        normalize.start()
        self.addCleanup(normalize.stop)

    def make_generated(self):
        self.generated_path.parent.mkdir(parents=True, exist_ok=True)
        self.generated_path.write_text("regenerated from source\n")
        manifest = {
            "format": 1,
            "trnilrg_rebuilt": True,
            "inputs": {
                "tracked.txt": hashlib.sha256(
                    (self.root / "tracked.txt").read_bytes()
                ).hexdigest(),
            },
            "outputs": {
                self.generated_rel: hashlib.sha256(
                    self.generated_path.read_bytes()
                ).hexdigest(),
            },
        }
        (self.root / "workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json").write_text(
            json.dumps(manifest)
        )

    def test_first_pass_defers_missing_generated_but_finds_static(self):
        selected, actions, unmapped, missing = pop.preflight(self.config, "all")
        self.assertEqual(len(selected), 1)
        self.assertEqual([item["member"] for item in actions], ["STATIC"])
        self.assertEqual(unmapped, [])
        self.assertEqual(len(missing), 1)
        self.assertIn("BLIB", missing[0])

    def test_second_pass_finds_both_after_generation(self):
        self.make_generated()
        _, actions, _, missing = pop.preflight(self.config, "all")
        self.assertEqual([item["member"] for item in actions], ["STATIC", "BLIB"])
        self.assertEqual(missing, [])

    def test_modified_generated_file_rejected_before_writes(self):
        self.make_generated()
        self.generated_path.write_text("stale file\n")
        with self.assertRaisesRegex(pop.DspalError, "stale or not inventoried"):
            pop.preflight(self.config, "all")

    def test_modified_input_rejected_before_writes(self):
        self.make_generated()
        (self.root / "tracked.txt").write_text("changed tracked source\n")
        with self.assertRaisesRegex(pop.DspalError, "input changed"):
            pop.preflight(self.config, "all")

    def test_generated_without_manifest_rejected(self):
        self.generated_path.parent.mkdir(parents=True, exist_ok=True)
        self.generated_path.write_text("unverified file\n")
        with self.assertRaisesRegex(pop.DspalError, "manifest.json is absent"):
            pop.preflight(self.config, "all")

    def test_missing_tracked_source_remains_hard_error(self):
        (self.root / "tracked.txt").unlink()
        with self.assertRaisesRegex(pop.DspalError, "source file not found"):
            pop.preflight(self.config, "all")

    def test_duplicate_static_generated_member_rejected(self):
        self.config["datasets"]["BOOT_SOURCE"]["generated_members"] = {
            "STATIC": self.generated_rel
        }
        with self.assertRaisesRegex(pop.DspalError, "duplicate member"):
            pop.preflight(self.config, "all")

    def test_first_real_populate_writes_static_then_returns_error(self):
        with mock.patch.object(pop.core, "require_reader_ready"), \
             mock.patch.object(pop, "require_target_datasets"), \
             mock.patch.object(pop.io, "member_put_deck", return_value="//JOB\n"), \
             mock.patch.object(pop.core, "submit_and_wait", return_value=(10, "OK")) as send:
            rc = pop.cmd_populate(self.config, "all", False, False)
            self.assertEqual(rc, 2)
            self.assertEqual(send.call_count, 1)

    def test_second_real_populate_installs_all_and_succeeds(self):
        self.make_generated()
        with mock.patch.object(pop.core, "require_reader_ready"), \
             mock.patch.object(pop, "require_target_datasets"), \
             mock.patch.object(pop.io, "member_put_deck", return_value="//JOB\n"), \
             mock.patch.object(pop.core, "submit_and_wait", return_value=(11, "OK")) as send:
            rc = pop.cmd_populate(self.config, "all", False, False)
            self.assertEqual(rc, 0)
            self.assertEqual(send.call_count, 2)


if __name__ == "__main__":
    unittest.main()
