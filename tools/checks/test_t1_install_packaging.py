"""Offline T.1 packaging safety checks; no MVS actions."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config/dspal.yaml"
CATALOG = ROOT / "bootstrap-toolchain/extensions/bcx/BCXCAT.asm"
INSTALL = ROOT / "bootstrap-toolchain/jcl/t1tinst.jcl"


def mapping(text, name):
    start = re.search(rf"(?m)^  {name}:\s*$", text)
    if start is None:
        raise AssertionError(f"missing {name} manifest section")
    tail = text[start.end():]
    nxt = re.search(r"(?m)^  [A-Z][A-Z0-9_]+:\s*$", tail)
    return tail[:nxt.start()] if nxt else tail


class TestT1Packaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = CONFIG.read_text("utf-8")
        cls.catalog = CATALOG.read_text("ascii")
        cls.install = INSTALL.read_text("ascii")

    def test_manifest_members_exact_paths(self):
        expected = {
            "EXT_ASM": ("BCPLDEMO: bootstrap-toolchain/extensions/bcpldemo/bcpldemo.asm",
                        "BCPLTIME: bootstrap-toolchain/extensions/bcpltime/bcpltime.asm"),
            "EXT_SOURCE": ("DEMOHDR: bootstrap-toolchain/extensions/bcpldemo/bcpldemo.h",
                           "TIMEHDR: bootstrap-toolchain/extensions/bcpltime/bcpltime.h"),
            "EXT_MAC": ("BCXPRE: bootstrap-toolchain/extensions/bcx/BCXPRE.asm",
                        "BCXCAT: bootstrap-toolchain/extensions/bcx/BCXCAT.asm",
                        "BCXPOST: bootstrap-toolchain/extensions/bcx/BCXPOST.asm"),
            "BOOT_JCL": ("R5DINST: bootstrap-toolchain/jcl/r5dinst.jcl",
                         "T1TINST: bootstrap-toolchain/jcl/t1tinst.jcl"),
        }
        for section, lines in expected.items():
            body = mapping(self.manifest, section)
            for line in lines:
                self.assertIn("      " + line, body)
                self.assertEqual(body.count("      " + line), 1)
        self.assertIn("populate: false", mapping(self.manifest, "EXT_OBJ"))

    def test_catalog_preserves_demo_and_adds_time(self):
        for name, dsn, begin, end in (
            ("BCPLDEMO", "EXTLIB(BCPLDEMO)", "DMOBEG", "DMOEND"),
            ("BCPLTIME", "EXTLIB(BCPLTIME)", "TIMBEG", "TIMEND"),
        ):
            self.assertIn(f"('&PKG' EQ '{name}')", self.catalog)
            self.assertIn(f"SETC  '{dsn}'", self.catalog)
            self.assertIn(f"SETC  '{begin}'", self.catalog)
            self.assertIn(f"SETC  '{end}'", self.catalog)
        self.assertRegex(self.catalog, r"(?m)^\.DEMO\s+ANOP$")
        self.assertRegex(self.catalog, r"(?m)^\.TIME\s+ANOP$")
        self.assertIn("         AGO   .EXIT\n.TIME", self.catalog)
        self.assertEqual(self.catalog.count("         MEND"), 1)

    def test_install_step_sequence(self):
        steps = re.findall(r"(?m)^//([A-Z0-9]{1,8})\s+EXEC PGM=(\w+)",
                           self.install)
        self.assertEqual(steps, [("ASMTIME", "IFOX00"),
                                 ("PUTTIME", "IEBGENER"),
                                 ("READBACK", "IEBGENER"),
                                 ("VERIFY", "IEBCOMPR")])
        for step in ("ASMTIME", "PUTTIME", "READBACK"):
            self.assertIn(f"COND=(0,NE,{step})", self.install)
        self.assertIn("COMPARE TYPORG=PS", self.install)

    def test_install_writes_only_bcpltime_object(self):
        self.assertEqual(self.install.count(
            "//SYSUT2   DD DSN=HERC02.BCPL.EXT.OBJ(BCPLTIME),DISP=OLD"), 1)
        for forbidden in ("EXT.OBJ(BCPLDEMO)", "BOOT.OBJ(", "BOOT.DEVOBJ("):
            self.assertNotIn(forbidden, self.install)
        self.assertEqual(self.install.count(
            "DSN=HERC02.BCPL.EXT.OBJ(BCPLTIME),DISP=SHR"), 1)
        self.assertEqual(self.install.count(
            "DSN=HERC02.BCPL.EXT.ASM(BCPLTIME),DISP=SHR"), 1)
        self.assertEqual(self.install.count("RECFM=FB,LRECL=80,BLKSIZE=800"), 2)
        self.assertEqual(self.install.splitlines().count("/*"), 1)
        self.assertEqual(self.install.splitlines().count("//"), 1)

    def test_all_mvs_cards_valid(self):
        for path in (CATALOG, INSTALL):
            for line_no, line in enumerate(path.read_text("ascii").splitlines(), 1):
                with self.subTest(path=str(path), line=line_no):
                    self.assertLessEqual(len(line), 71)
                    self.assertTrue(line.isascii())
                    self.assertNotIn("\t", line)

    def test_manifest_object_is_nonpopulated(self):
        body = mapping(self.manifest, "EXT_OBJ")
        self.assertIn("content_type: object", body)
        self.assertIn("populate: false", body)
        self.assertNotIn("members:", body)


if __name__ == "__main__":
    unittest.main()
