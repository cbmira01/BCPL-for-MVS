#!/usr/bin/env python3
"""Offline batching and bulk init checks; never submit JES work."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pop = load("tools/datasets/dspal-populate.py", "dspal_batch_tests")
init = load("tools/datasets/dspal-init.py", "dspal_bulk_init_tests")


def action(member, logical="FIRST", records=None):
    return {
        "logical": logical, "dsn": "HERC02.BCPL." + logical,
        "member": member, "records": ["DATA"] if records is None else records,
        "path": ROOT / "README.md",
        "spec": {"recfm": "FB", "lrecl": 80, "blksize": 800, "dsorg": "PO"},
    }


class BatchPopulationTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "mvs": {"hlq": "HERC02", "batch_user": "HERC02",
                    "batch_password": "SECRET"},
            "datasets": {"FIRST": {"dsn": "BCPL.FIRST"}},
        }

    def test_group_and_step_limits(self):
        parts = pop.population_batches([
            action("A"), action("B"), action("C", logical="SECOND")
        ])
        self.assertEqual([len(p) for p in parts], [2, 1])
        many = [action(f"M{i}") for i in range(pop.BATCH_MAX_STEPS + 1)]
        self.assertEqual([len(p) for p in pop.population_batches(many)],
                         [pop.BATCH_MAX_STEPS, 1])

    def test_card_limit_and_oversize_rejected(self):
        with self.assertRaises(pop.DspalError):
            pop.population_batches([
                action("BIG", records=["X"] * pop.BATCH_MAX_CARDS)
            ])

    def test_jcl_steps_delimiters_and_redaction(self):
        records = ["Z0 collision", "//JCL-like data", "/*"]
        deck = pop.batched_put_deck(
            self.config, [action("A", records=records), action("B")],
            redact_password=True,
        )
        self.assertIn("//P0001", deck)
        self.assertIn("//P0002", deck)
        self.assertIn("COND=(0,NE)", deck)
        self.assertIn("//JCL-like data\n", deck)
        self.assertIn("/*\n", deck)
        self.assertNotIn("SECRET", deck)
        with self.assertRaises(pop.DspalError):
            pop.batched_put_deck(
                self.config, [action("A"), action("B", logical="SECOND")]
            )

    def test_summary_checks_all_steps(self):
        report = ("JOB RESULT: SUCCESS\n"
                  "P0001      IEBGENER     RC=0000\n"
                  "P0002      IEBGENER     RC=0000\n")
        pop.verify_batch_summary(report, 2)
        with self.assertRaises(pop.DspalError):
            pop.verify_batch_summary(report, 3)
        with self.assertRaises(pop.DspalError):
            pop.verify_batch_summary(report.replace("SUCCESS", "FAILURE"), 2)

    def test_opt_in_uses_one_job_legacy_uses_two(self):
        actions = [action("A"), action("B")]
        report = ("JOB RESULT: SUCCESS\n"
                  "P0001      IEBGENER     RC=0000\n"
                  "P0002      IEBGENER     RC=0000\n")
        with patch.object(pop, "preflight", return_value=([], actions, [], [])), \
             patch.object(pop.core, "require_reader_ready"), \
             patch.object(pop, "require_target_datasets"), \
             patch.object(pop.core, "submit_and_wait", return_value=(123, report)) as send, \
             redirect_stdout(StringIO()):
            self.assertEqual(pop.cmd_populate(
                self.config, "all", False, False, batch=True), 0)
            self.assertEqual(send.call_count, 1)
        with patch.object(pop, "preflight", return_value=([], actions, [], [])), \
             patch.object(pop.core, "require_reader_ready"), \
             patch.object(pop, "require_target_datasets"), \
             patch.object(pop.io, "member_put_deck", return_value="//JOB\n"), \
             patch.object(pop.core, "submit_and_wait", return_value=(124, report)) as send, \
             redirect_stdout(StringIO()):
            self.assertEqual(pop.cmd_populate(
                self.config, "all", False, False), 0)
            self.assertEqual(send.call_count, 2)


class BulkInitTests(unittest.TestCase):
    def test_one_listds_preflight_one_alloc_job(self):
        config = {"mvs": {"hlq": "HERC02"}, "datasets": {
            "FIRST": {"dsn": "BCPL.FIRST"},
            "SECOND": {"dsn": "BCPL.SECOND"},
        }}
        with patch.object(init.core, "require_reader_ready"), \
             patch.object(init.core, "managed_inventory",
                          return_value=(101, "", {"FIRST": None, "SECOND": None})) as inventory, \
             patch.object(init.core, "submit_and_wait", return_value=(102, "")) as send, \
             patch.object(init.core, "initbcpl_deck", return_value="//JOB") as deck, \
             redirect_stdout(StringIO()):
            self.assertEqual(init.cmd_initbcpl(config, False), 0)
        inventory.assert_called_once_with(config)
        send.assert_called_once()
        self.assertEqual(deck.call_args.kwargs["logicals"], ["FIRST", "SECOND"])


if __name__ == "__main__":
    unittest.main()
