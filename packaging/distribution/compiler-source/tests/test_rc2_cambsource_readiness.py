"""TA.2 source-population preflight tests: synthetic MVS directory reports only."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "packaging/distribution/compiler-source/rc2-cambsource-readiness.py"
spec = importlib.util.spec_from_file_location("ta2_cambsource_readiness", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MEMBERS = [
    "BCPL", "BLIB", "CG", "CGHDR", "EDITMAIN", "IOS", "LIBHDR",
    "PM", "SYN", "SYNHDR", "TRN", "TRNHDR", "MAKEOBJ", "MAKELIB", "PROGRAM",
]
RECORDS = [490, 474, 2255, 219, 113, 97, 50, 231, 1099,
           81, 1162, 100, 113, 72, 21]
HEAD = "HERC02.BCPL.CAMBRIDG.SOURCE:\n"


class SourcePopulationReadinessTests(unittest.TestCase):
    def test_saved_mvs_empty_is_pending_not_success(self):
        self.assertEqual(mod.inspect_listing(HEAD + "    (empty)\n", MEMBERS), "empty")

    def test_all_historical_members_ready_for_next_verification(self):
        report = HEAD + "".join(f"    {m}\n" for m in MEMBERS)
        self.assertEqual(mod.inspect_listing(report, MEMBERS), "complete")

    def test_partial_is_not_accepted(self):
        self.assertEqual(mod.inspect_listing(HEAD + "    BCPL\n", MEMBERS), "partial")

    def test_unknown_member_refused(self):
        with self.assertRaisesRegex(mod.Refusal, "unselected"):
            mod.inspect_listing(HEAD + "    DEMOTED\n", MEMBERS)

    def test_other_dataset_refused(self):
        with self.assertRaisesRegex(mod.Refusal, "approved"):
            mod.inspect_listing("HERC02.BCPL.CAMBRIDG.DEMOTED:\n    (empty)\n",
                                MEMBERS)

    def test_empty_plus_member_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_listing(HEAD + "    (empty)\n    BCPL\n", MEMBERS)

    def test_duplicate_member_refused(self):
        with self.assertRaisesRegex(mod.Refusal, "duplicate"):
            mod.inspect_listing(HEAD + "    BCPL\n    BCPL\n", MEMBERS)

    def test_no_members_block_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.inspect_listing(HEAD, MEMBERS)

    def test_exact_15_historical_sources_fit_two_bounded_batches(self):
        batches = mod.batch_plan(list(zip(MEMBERS, RECORDS)))
        self.assertEqual(batches, [MEMBERS[:8], MEMBERS[8:]])
        self.assertEqual(sum(RECORDS), 6577)
        self.assertEqual(sum(RECORDS[:8]) + 7 * 8, 3985)
        self.assertEqual(sum(RECORDS[8:]) + 7 * 7, 2697)

    def test_oversize_single_member_refused(self):
        with self.assertRaises(mod.Refusal):
            mod.batch_plan([("CG", 4000)])


if __name__ == "__main__":
    unittest.main()
