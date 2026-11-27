"""Host-only CO.5 production source, JCL, and installed-link contract tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(module_name, filename):
    spec = importlib.util.spec_from_file_location(module_name, filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREP = load("co5_prepare", ROOT / "tools/coroutines/prepare-production-library.py")
VERIFY = load("co5_verify", ROOT / "tools/coroutines/verify-installed-production.py")
CAND = load("co5_candidate", ROOT / "tools/coroutines/run-co3-delete-reuse.py")


class ProductionCoroutineTests(unittest.TestCase):
    def test_public_globals_and_accepted_bcpl_body(self):
        PREP.source_check()
        self.assertEqual(len(PREP.GLOBALS), 12)
        self.assertEqual(set(PREP.GLOBALS.values()), set(range(289, 301)))

    def test_machine_bridge_matches_accepted_co3_merge(self):
        original = (ROOT / "bootstrap-toolchain/asm/bcplco.asm").read_text("ascii")
        extension = (ROOT /
                     "packaging/milestones/coroutines/candidates/co3-delete-reuse"
                     "/co3drop.inc").read_text("ascii")
        production = (ROOT / "bootstrap-toolchain/asm/bcplco-production.asm"
                      ).read_text("ascii")
        expected = CAND.merge_bridge(original, extension)
        marker = "BCPLCO   CSECT"
        # DR.5 added full-card assembler comments to the production sources.
        # Keep exact equality of every executable/data/directive card.
        def body(source):
            self.assertEqual(source.count(marker), 1)
            return [row for row in source.split(marker, 1)[1].splitlines()
                    if not row.startswith("*")]
        self.assertEqual(body(production), body(expected))
        self.assertEqual(production.count("CO3DROP  STM"), 1)
        self.assertTrue(all(line.isascii() and len(line) <= 71
                            for line in production.splitlines()))

    def test_stklim_export_and_installer_jobs(self):
        VERIFY.preflight()
        main = (ROOT / "bootstrap-toolchain/asm/bcplmain.asm"
                ).read_text("ascii")
        self.assertEqual(main.count("ENTRY STKOVFL,STKLIM"), 1)
        for job, member in [("bldcorco.jcl", "BCPLCO"),
                            ("bldcorlb.jcl", "COROUTIN")]:
            jcl = (ROOT / "bootstrap-toolchain/jcl" / job).read_text("ascii")
            self.assertTrue(all(len(row) <= 71 for row in jcl.splitlines()))
            self.assertIn(f"BOOT.OBJ({member})", jcl)
            self.assertIn(f"BOOT.ASM({member})", jcl)
            self.assertIn("PGM=IFOX00", jcl)
            self.assertIn("PGM=IEBGENER", jcl)
            self.assertIn("PGM=IEBCOMPR", jcl)
            self.assertNotIn("BOOT.DEVOBJ", jcl)

    def test_installed_linker_deck_has_no_candidate_objects(self):
        fake = SimpleNamespace(
            generated_application=lambda source: ["CO3APP   CSECT",
                                                    "         END   CO3APP"],
            co2=SimpleNamespace(
                asm_step=lambda name, mem, rows:
                ["//ASMA     EXEC PGM=IFOX00", "//SYSIN DD *",
                 *rows, "/*"]),
        )
        deck = VERIFY.build_deck(
            fake, "compiled", ["//COPRVER JOB (BCPL),'TEST'"],
            "HERC02.BCPL.BOOT.OBJ")
        for member in ("BCPLMAIN", "BCPLCO", "COROUTIN", "BLIB"):
            self.assertIn(f" INCLUDE OBJ({member})", deck)
        self.assertEqual(deck.count(" EXEC PGM=IFOX00"), 1)
        self.assertNotIn("DISP=(NEW,CATLG)", deck)

    def test_installed_link_result_oracle(self):
        expected = ["MADE", "A1", "PASS"]
        summary = ("JOB 6001 COPRVER\n"
                   "ASMA IFOX00 RC=0000\n"
                   "LKED IEWL RC=0000\n"
                   "GO PGM RC=0000\n"
                   "JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n")
        report = "\n".join("CO3BCPL " + v for v in expected)
        self.assertEqual(VERIFY.assess(summary, report, "6001", expected)
                         ["steps"], {"ASMA": 0, "LKED": 0, "GO": 0})
        with self.assertRaises(ValueError):
            VERIFY.assess(summary, report, "6002", expected)
        with self.assertRaises(ValueError):
            VERIFY.assess(summary.replace("GO PGM RC=0000",
                                          "GO PGM RC=0012"),
                          report, "6001", expected)
        with self.assertRaises(ValueError):
            VERIFY.assess(summary, report + "\nCO3BCPL BAD",
                          "6001", expected)


if __name__ == "__main__":
    unittest.main()
