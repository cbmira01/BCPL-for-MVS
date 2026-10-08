#!/usr/bin/env python3
"""Offline tests for manifest and BLIB object packaging contracts."""
from __future__ import annotations

import importlib.util
import re
from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name: str, path: str):
    loc = ROOT / path
    spec = importlib.util.spec_from_file_location(name, loc)
    if spec is None or spec.loader is None:
        spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(loc)))
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class ObjectPackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = module("dspal_core_test", "tools/dspal-core.py")
        cls.io = module("dspal_io_test", "tools/dspal-io.py")
        cls.read = module("dspal_read_test", "tools/dspal-read.py")
        cls.submit = module("dspal_submit_test", "tools/dspal-submit.py")
        cls.blib = module(
            "blib_card_test",
            "native-compiler/object-library/make-blib-object-job.py",
        )
        cls.builder = module("blib_builder_test", "tools/build-blib-object")
        cls.config = cls.core.load_config()

    def test_manifest_and_build_deck(self):
        d = self.config["datasets"]
        self.assertEqual(
            d["SOURCE"]["members"]["BLIB"],
            "workarea/bootstrap-cambridge/demoted/blib",
        )
        self.assertEqual(
            d["JCL"]["members"]["BLIBBLD"], "jcl/build-blib-object.jcl"
        )
        self.assertEqual(
            self.core.expected_attrs(d["OBJ"]),
            {"dsorg": "PO", "recfm": "FB", "lrecl": "80", "blksize": "800"},
        )
        self.assertEqual(d["OBJ"]["content_type"], "object")
        self.assertIs(d["OBJ"]["populate"], False)
        dsns = self.builder.require_manifest(self.core, self.config)
        self.assertEqual(dsns["OBJ"], "HERC02.BCPL.OBJ")

    def test_binary_guard_for_text_transfers(self):
        with self.assertRaisesRegex(Exception, "binary object"):
            self.io.resolve_pds(self.config, "OBJ", text_required=True)
        with self.assertRaisesRegex(Exception, "binary object"):
            self.read.resolve_text_pds(self.config, "OBJ")
        with self.assertRaisesRegex(Exception, "binary object"):
            self.submit.resolve_text_pds(self.config, "OBJ")
        # The source library remains a legal managed text destination.
        dsn, _logical, _spec = self.io.resolve_pds(
            self.config, "SOURCE", text_required=True
        )
        self.assertEqual(dsn, "HERC02.BCPL.SOURCE")

    def test_blib_card_normalization_still_standalone(self):
        source = (
            "         CSECT\n"
            "         EXTRN BCPLMAIN\n"
            "         DC A(BCPLMAIN)\n"
            "         DC F'-./,),(-*,('\n"
            "* PRINTER COMMENT \x80\n"
            "         END\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "recovered.asm"
            file.write_bytes(source.encode("latin-1"))
            prepared = self.blib.blib_cards(file)
        self.assertIn("BLIB     CSECT", prepared)
        self.assertIn("EXTRN BCPLMAIN", prepared)
        self.assertIn("DC X'80000000'", prepared)
        self.assertIn("* PRINTER COMMENT ?", prepared)
        self.assertNotIn("DC F'-./,),(-*,('", prepared)
        self.assertEqual(prepared.count("         END"), 1)

    def test_stored_jcl_compiles_and_installs_blib_in_mvs(self):
        deck = (ROOT / "jcl/build-blib-object.jcl").read_text(encoding="ascii")
        for step, program in (
            ("COMP", "ICINT19"),
            ("PREPASM", "IFOX00"),
            ("PREPLK", "IEWL"),
            ("FIXASM", "*.PREPLK.SYSLMOD"),
            ("ASMBLIB", "IFOX00"),
            ("INSTALL", "IEBGENER"),
        ):
            self.assertRegex(deck, rf"(?m)^//{step}\s+EXEC PGM={re.escape(program)}")
        self.assertIn("//SYSIN    DD DSN=HERC02.BCPL.SOURCE(BLIB)", deck)
        self.assertIn("//SYSUT2   DD DSN=HERC02.BCPL.OBJ(BLIB)", deck)
        self.assertNotIn("ENTRY BLIB\n", deck)
        self.assertNotIn("NAME BLIBCHK(R)", deck)
        self.assertIn("COND=(0,NE,ASMBLIB)", deck)
        self.assertTrue(all(len(line) <= 71 for line in deck.splitlines()))

    def test_mvs_card_repair_matches_original_forms(self):
        deck = (ROOT / "jcl/build-blib-object.jcl").read_text(encoding="ascii")
        expected = {
            "SECT1": " CSECT",
            "SECT9": "         CSECT",
            "BAD1": " DC F'-./,),(-*,('",
            "BAD9": "         DC F'-./,),(-*,('",
            "NEWSECT": "BLIB     CSECT",
            "NEWMIN": "         DC X'80000000'",
        }
        for name, wanted in expected.items():
            match = re.search(
                rf"(?m)^{name}\s+DC\s+CL80'((?:[^']|'')*)'$",
                deck,
            )
            self.assertIsNotNone(match, name)
            self.assertEqual(match.group(1).replace("''", "'"), wanted)


if __name__ == "__main__":
    unittest.main()
