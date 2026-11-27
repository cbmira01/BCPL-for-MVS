"""DR.5 DEBUGINT private runtime deck: host-only, no MVS submission."""
import os
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
DRIVER = runpy.run_path(str(ROOT / "tools/checks/run-dr5-debugint-verification.py"))
BUILDER = runpy.run_path(str(ROOT / "tools/checks/prepare-runtime-pds-regression.py"))
APP = "         CSECT\n         EXTRN BCPLMAIN\n         DC F'600'\n         END\n"


class DebugintPrivateDeckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT / "workarea")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.generated = self.folder / "generated.asm"
        self.generated.write_text(APP, encoding="ascii")
        self.source = DRIVER["ASM"].read_text("ascii")
        self.config = {"datasets": {
            name: {"dsn": "DR5.BCPL." + suffix, "content_type": "object",
                   "recfm": "FB", "lrecl": 80, "dsorg": "PO"}
            for name, suffix in (("BOOT_OBJ", "BOOT.OBJ"), ("BOOT_DEVOBJ", "BOOT.DEVOBJ"))
        }}
        self.core = SimpleNamespace(
            load_config=lambda: self.config,
            full_dsn=lambda config, spec: spec["dsn"],
            authenticated_job_card=lambda config, name, description, redact_password:
                [f"//{name} JOB (BCPL),'OFFLINE'"])
        self.argv = []

    def build(self, args):
        self.argv = list(args)
        main = BUILDER["main"]
        with patch.dict(os.environ, {"BCPL_RUNTIME_LIBRARY": "OBJ",
                                    "BCPL_RUNTIME_CANDIDATE": "0"}, clear=True), \
             patch.dict(main.__globals__, {"load": lambda path, name: self.core}), \
             patch.object(sys, "argv", [str(x) for x in args]):
            main()

    def ordinary(self):
        deck = self.folder / "ordinary.jcl"
        self.build(["prepare", self.generated, deck, "--test-number", "906",
                    "--case-dir", DRIVER["FIX"]])
        return deck.read_text("ascii")

    def test_real_builder_preserves_application_and_installed_service_selection(self):
        ordinary = self.ordinary()
        private = DRIVER["private_cards"](ordinary, self.source)
        self.assertEqual(ordinary.split("//LKED", 1)[0],
                         private.split("//* DR.5 PRIVATE", 1)[0])
        self.assertNotIn("NATIVEAD", private)
        self.assertNotIn(" INCLUDE OBJ(BCPLMAIN)", private)
        self.assertEqual(private.count(self.source.rstrip("\n")), 1)
        for member in ("BCPLIO", "BCPLBYTE", "BCPLAPT", "BCPLMEM",
                       "BLIB", "BCPLRGS", "BCPLREG"):
            self.assertEqual(private.count(f" INCLUDE OBJ({member})"), 1)
        self.assertIn("//         DD DSN=&&NATOBJ,DISP=(OLD,DELETE)", private)
        self.assertIn("COND=((0,NE,ASMAP),(0,NE,ASMNAT),(0,NE,LKED))", private)
        self.assertTrue(all(len(row) <= 71 for row in private.splitlines()))

    def test_refuse_native_global_and_invalid_deck(self):
        ordinary = self.ordinary()
        for invalid in (ordinary.replace("EXTRN BCPLMAIN", "EXTRN NATIVEAD"),
                        ordinary.replace(" INCLUDE OBJ(BCPLMAIN)\n", ""),
                        DRIVER["private_cards"](ordinary, self.source)):
            with self.subTest(deck=invalid[:40]):
                with self.assertRaises(ValueError):
                    DRIVER["private_cards"](invalid, self.source)

    def test_native_driver_uses_ordinary_builder_before_private_overlay(self):
        def run(args, log, env):
            if str(args[0]) == "python3":
                self.build(args[1:])
                self.assertNotIn("--native", self.argv)
                return "prepared"
            self.assertEqual(args[0], "tools/mvs/submit-jcl")
            deck = Path(args[-1]).read_text("ascii")
            self.assertNotIn("NATIVEAD", deck)
            self.assertNotIn(" INCLUDE OBJ(BCPLMAIN)", deck)
            self.assertIn(self.source, deck)
            return "JOB 1\n"

        expected = DRIVER["FIX"].joinpath("expected.txt").read_text("ascii").splitlines()
        common = {"run": run, "job_id": lambda output: "1",
                  "receipt": lambda *args: "AUTHORIZATION CODE IS\n" + "\n".join(expected),
                  "CODE": __import__("re").compile(r"EXECUTION CYCLES"),
                  "records": lambda report: report.strip().splitlines()}
        self.assertEqual(DRIVER["native"](common, self.folder / "private",
                                         self.generated, {}, private=True),
                         {"job": "1", "records": expected})


if __name__ == "__main__":
    unittest.main()
