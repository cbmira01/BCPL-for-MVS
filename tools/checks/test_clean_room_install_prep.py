#!/usr/bin/env python3
"""Offline checks for the clean-room R.5 install preparation and runbook."""
from pathlib import Path
import runpy
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PREPARER = ROOT / "tools/mvs/prepare-bcpldemo-install"
JCL = ROOT / "bootstrap-toolchain/extensions/bcpldemo/install-bcpldemo.jcl"
GUIDE = ROOT / "packaging/clean-room-mvs-reconstruction.md"


class FakeCore:
    @staticmethod
    def full_dsn(config, spec):
        return config["mvs"]["hlq"] + "." + spec["dsn"]

    @staticmethod
    def authenticated_job_card(config, name, title, redact):
        if redact:
            raise AssertionError("install deck must use real private credentials")
        return [
            f"//{name} JOB (BCPL),'{title}',CLASS=A,MSGCLASS=A,",
            "//             USER=TESTUSR,PASSWORD=TESTPASS,",
            "//             MSGLEVEL=(1,1)",
        ]


class CleanRoomInstallPreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(PREPARER))
        cls.source = JCL.read_text(encoding="ascii")
        cls.config = {
            "mvs": {"hlq": "HERC02"},
            "datasets": {
                "EXT_ASM": {"dsn": "BCPL.EXT.ASM"},
                "EXT_OBJ": {"dsn": "BCPL.EXT.OBJ"},
            },
        }

    def test_produces_private_authenticated_deck(self):
        deck = self.module["make_deck"](FakeCore, self.config, self.source)
        self.assertTrue(deck.startswith("//R5DINST JOB "))
        self.assertIn("DSN=HERC02.BCPL.EXT.ASM(BCPLDEMO)", deck)
        self.assertIn("DSN=HERC02.BCPL.EXT.OBJ(BCPLDEMO)", deck)
        self.assertEqual(deck.count("PASSWORD=TESTPASS"), 1)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "install.jcl"
            self.module["write_private_deck"](deck, output)
            self.assertEqual(output.read_text(encoding="ascii"), deck)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.module["write_private_deck"](deck, output)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_rejects_wrong_dataset_identity(self):
        changed = {
            **self.config,
            "mvs": {"hlq": "OTHER"},
        }
        with self.assertRaisesRegex(ValueError, "EXT_ASM"):
            self.module["make_deck"](FakeCore, changed, self.source)

    def test_rejects_injected_job_card(self):
        source = "//OTHER JOB (BCPL),'UNEXPECTED'\n" + self.source
        with self.assertRaisesRegex(ValueError, "must not contain a JOB"):
            self.module["make_deck"](FakeCore, self.config, source)

    def test_rejects_overlength_record(self):
        with self.assertRaisesRegex(ValueError, "overlength"):
            self.module["make_deck"](
                FakeCore, self.config, self.source + ("X" * 81) + "\n"
            )

    def test_guide_current_acceptance_and_no_inline_python(self):
        guide = GUIDE.read_text(encoding="utf-8")
        self.assertIn("tools/mvs/prepare-bcpldemo-install", guide)
        self.assertIn("tools/bootstrap/run-production-regression 0 158", guide)
        self.assertIn("| PASS | **158**", guide)
        self.assertIn("| TOTAL | **159**", guide)
        self.assertIn("eight** object members", guide)
        self.assertNotIn("python3 - <<", guide)
        self.assertNotIn("claim all five", guide)
        self.assertNotIn("the sixth native object", guide)
        self.assertNotIn("tools/mvs/job-summary NNNN", guide)
        self.assertNotIn("145 PASS, 0 FAIL", guide)


if __name__ == "__main__":
    unittest.main()
