"""Offline Q.2 numbered regression integration checks; NOT native JES."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "bootstrap-toolchain/regression"
EXT = ROOT / "bootstrap-toolchain/extensions/bcplqsam"
TARGET = Path(__file__).with_name("run-q2-qsam-regression.py")
SPEC = importlib.util.spec_from_file_location("q2_numbered", TARGET)
assert SPEC is not None and SPEC.loader is not None
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def sample_source():
    query = R.load("prepare-q1-query.py")
    return query.time_helper().trailer_helper().sample_generated()


class NumberedQ2Tests(unittest.TestCase):
    def test_eight_consecutive_cases_and_exact_source_parity(self):
        self.assertEqual(list(R.CASES), list(range(163, 171)))
        for n, (kind, original, job, markers) in R.CASES.items():
            with self.subTest(n=n):
                candidates = list(REG.glob(f"{n:03d}-*"))
                self.assertEqual(len(candidates), 1)
                case = candidates[0]
                self.assertEqual((case/"qsam-native.txt").read_text().strip(),
                                 kind)
                self.assertEqual((case/"source.bcpl").read_bytes(),
                                 (EXT/original).read_bytes())
                self.assertEqual((case/"expected.txt").read_text().splitlines(),
                                 list(markers))
                self.assertTrue((case/"candidate-only.txt").is_file())
                if n == 168:
                    self.assertEqual((case/"reader.bcpl").read_bytes(),
                                     (EXT/"test-q2-read.bcpl").read_bytes())

    def test_all_existing_native_jcl_generators(self):
        code = sample_source()
        boot = "HERC02.BCPL.BOOT.OBJ"
        ext = "HERC02.BCPL.EXT.OBJ"
        for n, (kind, _, job, _) in R.CASES.items():
            with self.subTest(n=n):
                card = [f"//{job} JOB (BCPL),'Q2 OFFLINE',CLASS=A"]
                if kind == "query":
                    deck = R.load("prepare-q2-query.py").make_deck(
                        code, card, boot)
                elif kind in ("negative", "output", "finish", "stop"):
                    deck = R.load("prepare-q1-campaign.py").make_deck(
                        kind, code, card, boot)
                elif kind == "full":
                    deck = R.load("prepare-q2-consolidated.py").make_deck(
                        code, code, card, boot)
                elif kind == "stopflush":
                    deck = R.load("prepare-q2-stop-flush.py").make_deck(
                        code, card, boot)
                else:
                    deck = R.load("prepare-q2-mix.py").make_deck(
                        code, card, boot, ext)
                self.assertTrue(deck.startswith(f"//{job} JOB "))
                self.assertTrue(all(row.isascii() and len(row) <= 71
                                    for row in deck.splitlines()))
                self.assertNotIn("DISP=MOD", deck)
                self.assertNotIn("CATLG", deck)
                self.assertIn("PGM=IFOX00", deck)
                self.assertIn("PGM=IEWL", deck)
                self.assertIn("PGM=*.LKED.SYSLMOD", deck)

    def test_native_pass_checker_rejects_missing_evidence(self):
        for n in R.CASES:
            self.assertTrue(R.evidence(n, "", ""))

    def test_unmodified_prior_panel_path(self):
        script = (REG/"run-test.sh").read_text()
        self.assertIn('if [[ -f "$case_dir/qsam-native.txt" ]]; then',script)
        self.assertIn('exec python3 "$root/tools/checks/run-q2-qsam-regression.py"',
                      script)
        self.assertIn('elif [[ -f "$case_dir/extension-selection.asm" ]]',script)
        self.assertIn('if [[ -f "$case_dir/time-selection.asm" ]]; then',script)


if __name__ == "__main__":
    unittest.main()
