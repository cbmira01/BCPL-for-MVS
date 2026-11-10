"""Guard the active Q.1 sixteen-handle JCL generator against archived-path drift.

These tests generate only synthetic, credential-free JCL; never submit JES.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
WRITER = ROOT / "bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py"
ARCHIVED_DASD = ROOT / "packaging/archive/qsam/probes/q0-qsam-dasd-probes/make-jobs.py"


class QsamActiveProbeDependencyTests(unittest.TestCase):
    def test_real_archived_helper_and_synthetic_multi_dcb_decks(self):
        spec = importlib.util.spec_from_file_location("qsam_active_16dcb", WRITER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual(module.BASE, ARCHIVED_DASD)
        self.assertTrue(ARCHIVED_DASD.is_file())
        helper = module.harness()
        self.assertTrue(callable(helper.asm_step))
        self.assertTrue(callable(helper.link_step))

        for profile, count in (("three", 3), ("sixteen", 16)):
            with self.subTest(profile=profile):
                job = module.JOB[profile]
                cards = [f"//{job:<8} JOB (BCPL),'Q0 OFFLINE',CLASS=A"]
                deck = module.make_deck(profile, cards)
                self.assertEqual(deck.count("//SYSIN    DD  *"), 2)
                self.assertEqual(deck.splitlines().count("/*"), 4)
                self.assertIn(f"//Q{count-1:02d}      DD  DSN=&&Q0H{count-1:02d},", deck)
                self.assertNotIn("CATLG", deck)

    def test_q1_real_source_chain_synthetic_checks(self):
        commands = (
            ("bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py",
             ["three", "--check"], "CHECK Q0 three:"),
            ("system-extensions/bcplqsam/prepare-q1-3dd.py",
             ["--check"], "PASS: Q.1 temporary three-DD deck"),
            ("system-extensions/bcplqsam/prepare-q1-campaign.py",
             ["--check"], "PASS: Q16FIN finish"),
        )
        for script, arguments, marker in commands:
            with self.subTest(script=script):
                process = subprocess.run(
                    [sys.executable, "-B", str(ROOT / script), *arguments],
                    cwd=ROOT, capture_output=True, text=True,
                    timeout=45, check=False,
                )
                self.assertEqual(
                    process.returncode, 0,
                    f"{script} failed:\n{process.stdout}\n{process.stderr}",
                )
                self.assertIn(marker, process.stdout)
                if script.endswith("prepare-q1-campaign.py"):
                    self.assertIn("PASS: Q16STP stop", process.stdout)


if __name__ == "__main__":
    unittest.main()
