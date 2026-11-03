"""Offline Q.5 packaging tests: no JES submission, no MVS writes."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "q5_release", HERE / "prepare-q5-release-campaign.py")
q5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q5)


class Q5ReleaseDeckTests(unittest.TestCase):
    def test_comments_do_not_trigger_persistent_output_guard(self):
        q5.reject_permanent_library_operations([
            "* objects; no BOOT_OBJ or BOOT_DEVOBJ installation is implied.",
            "//* Never use DISP=MOD or CATLG in a real JCL DD.",
        ])

    def test_active_persistent_controls_are_rejected(self):
        for row in (
            "//OUT      DD  DSN=SITE.OUTPUT,DISP=MOD",
            "//OUT      DD  DSN=SITE.OUTPUT,DISP=(NEW,CATLG)",
            " INCLUDE BOOT_DEVOBJ(BCPLMAIN)",
        ):
            with self.subTest(row=row):
                with self.assertRaisesRegex(ValueError, "permanent library"):
                    q5.reject_permanent_library_operations([row])

    def test_temporary_selected_and_excluded_link_decks(self):
        query = q5.load(HERE / "prepare-q1-query.py", "q5_release_test_query")
        sample = query.time_helper().trailer_helper().sample_generated()
        cards = q5.make_deck(
            sample, sample,
            ["//Q5PKG JOB (BCPL),'Q5 CHECK',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")
        self.assertIn("//SGO ", cards)
        self.assertIn("//NGO ", cards)
        self.assertEqual(cards.count(" COMPARE TYPORG=PS"), 1)
        self.assertEqual(cards.count("         BCXREQ BCPLQSAM"), 1)
        self.assertIn("DSN=&&Q5QOBJ,DISP=(OLD,PASS)", cards)
        self.assertTrue(all(len(row) <= 71 and row.isascii()
                            for row in cards.splitlines()))


if __name__ == "__main__":
    unittest.main()
