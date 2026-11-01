#!/usr/bin/env python3
"""Offline checks for the single-JES-job purgebcpl inventory preflight."""

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PURGE_PATH = ROOT / "tools" / "datasets" / "dspal-purge.py"


def load_purge():
    spec = importlib.util.spec_from_file_location("dspal_purge_bulk", PURGE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load dspal-purge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


purge = load_purge()


class BulkPurgePreflightTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "mvs": {
                "hlq": "HERC02",
                "batch_user": "HERC02",
                "batch_password": "TESTPASS",
            },
            "datasets": {
                "FIRST": {"dsn": "BCPL.FIRST"},
                "SECOND": {"dsn": "BCPL.SECOND"},
                "THIRD": {"dsn": "BCPL.THIRD"},
            },
        }
        self.first = "HERC02.BCPL.FIRST"
        self.second = "HERC02.BCPL.SECOND"
        self.third = "HERC02.BCPL.THIRD"

    def test_single_bulk_preflight_only_deletes_existing(self):
        inventory = {"FIRST": {}, "SECOND": None, "THIRD": {}}
        output = StringIO()
        with (
            patch.object(purge.core, "require_reader_ready") as ready,
            patch.object(
                purge.core, "managed_inventory",
                return_value=(101, "LISTDS report", inventory),
            ) as bulk,
            patch.object(
                purge.core, "submit_and_wait", return_value=(102, ""),
            ) as submit,
            redirect_stdout(output),
        ):
            self.assertEqual(purge.cmd_purgebcpl(self.config, True, False), 0)
        ready.assert_called_once_with(self.config)
        bulk.assert_called_once_with(self.config)
        submit.assert_called_once()
        deck = submit.call_args.args[1]
        self.assertIn(" DELETE '" + self.first + "'", deck)
        self.assertIn(" DELETE '" + self.third + "'", deck)
        self.assertNotIn(" DELETE '" + self.second + "'", deck)
        self.assertIn("preflight completed as JOB 101", output.getvalue())
        self.assertIn("deletion completed as JOB 102", output.getvalue())

    def test_all_missing_skips_deletion(self):
        inventory = {"FIRST": None, "SECOND": None, "THIRD": None}
        output = StringIO()
        with (
            patch.object(purge.core, "require_reader_ready"),
            patch.object(
                purge.core, "managed_inventory",
                return_value=(201, "", inventory),
            ) as bulk,
            patch.object(purge.core, "submit_and_wait") as submit,
            patch.object(purge, "confirm_deletion") as confirm,
            redirect_stdout(output),
        ):
            self.assertEqual(purge.cmd_purgebcpl(self.config, False, False), 0)
        bulk.assert_called_once()
        submit.assert_not_called()
        confirm.assert_not_called()
        self.assertIn("No managed datasets exist", output.getvalue())

    def test_show_jcl_is_offline_and_redacted(self):
        output = StringIO()
        with (
            patch.object(purge.core, "require_reader_ready") as ready,
            patch.object(purge.core, "managed_inventory") as bulk,
            patch.object(purge.core, "submit_and_wait") as submit,
            redirect_stdout(output),
        ):
            self.assertEqual(purge.cmd_purgebcpl(self.config, False, True), 0)
        ready.assert_not_called()
        bulk.assert_not_called()
        submit.assert_not_called()
        self.assertIn("PASSWORD=REDACTED", output.getvalue())
        self.assertIn(" DELETE '" + self.first + "'", output.getvalue())

    def test_inventory_failure_prevents_delete(self):
        with (
            patch.object(purge.core, "require_reader_ready"),
            patch.object(
                purge.core, "managed_inventory",
                side_effect=purge.DspalError("unparseable LISTDS"),
            ),
            patch.object(purge.core, "submit_and_wait") as submit,
            patch.object(purge, "confirm_deletion") as confirm,
        ):
            with self.assertRaises(purge.DspalError):
                purge.cmd_purgebcpl(self.config, True, False)
        submit.assert_not_called()
        confirm.assert_not_called()

    def test_confirmation_rejection_prevents_delete(self):
        inventory = {"FIRST": {}, "SECOND": None, "THIRD": None}
        with (
            patch.object(purge.core, "require_reader_ready"),
            patch.object(
                purge.core, "managed_inventory",
                return_value=(301, "", inventory),
            ),
            patch("builtins.input", return_value="NO"),
            patch.object(purge.core, "submit_and_wait") as submit,
            redirect_stdout(StringIO()),
        ):
            with self.assertRaises(purge.DspalError):
                purge.cmd_purgebcpl(self.config, False, False)
        submit.assert_not_called()

    def test_deletion_failure_is_not_reported_as_success(self):
        inventory = {"FIRST": {}, "SECOND": {}, "THIRD": {}}
        with (
            patch.object(purge.core, "require_reader_ready"),
            patch.object(
                purge.core, "managed_inventory",
                return_value=(401, "", inventory),
            ),
            patch.object(
                purge.core, "submit_and_wait",
                side_effect=purge.DspalError("delete failed"),
            ) as submit,
            redirect_stdout(StringIO()),
        ):
            with self.assertRaises(purge.DspalError):
                purge.cmd_purgebcpl(self.config, True, False)
        submit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
