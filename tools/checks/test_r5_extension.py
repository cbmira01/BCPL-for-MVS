"""R.5 host-only tests of MVS JCL preparation and IEWL MAP checks."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class R5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = load("r5_prep",
            ROOT / "tools/checks/prepare-r5-extension-regression.py")
        cls.v = load("r5_map",
            ROOT / "tools/checks/check-r5-extension-report.py")
        cls.trail = cls.p.trail_module()

    def make(self, n, mode="source", extlib=None):
        return self.p.make_deck(
            n, self.trail.sample_generated(),
            [f"//RG{n:03d}R JOB (BCPL),'R5 TEST',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ", mode, extlib)

    def test_all_thirteen_cases_are_buildable(self):
        for n in range(146, 159):
            with self.subTest(number=n):
                deck = self.make(n)
                self.assertIn("//GO       EXEC", deck)
                self.assertIn(" ENTRY R0APP", deck)
                self.assertIn("SYSPUNCH DD  DSN=&&R5REGD", deck)
                self.assertIn("DISP=SHR", deck)
                self.assertNotIn("DISP=MOD", deck)
                self.assertTrue(all(len(l) <= 71 for l in deck.splitlines()))

    def test_include_and_exclude(self):
        for n in (146, 158):
            deck = self.make(n)
            self.assertNotIn("//ASMD", deck)
            self.assertNotIn("//PKGA", deck)
            self.assertNotIn("EXTLIB   DD", deck)
        for n in range(147, 158):
            deck = self.make(n)
            self.assertIn("//ASMD", deck)
            self.assertIn("//PKGA", deck)

    def test_installed_object_pds_is_read_only(self):
        deck = self.make(147, "installed", "HERC02.BCPL.EXT.OBJ")
        self.assertNotIn("//ASMD", deck)
        self.assertIn(
            "//EXTLIB   DD  DSN=HERC02.BCPL.EXT.OBJ,DISP=SHR", deck)
        self.assertNotIn("//PKGA", deck)
        with self.assertRaises(ValueError):
            self.make(147, "installed", "BAD..DSN")

    def test_combined_descriptor_and_dispatcher(self):
        path = (ROOT / "bootstrap-toolchain/extensions/bcpldemo/"
                "bcpldemo.asm")
        data = path.read_text("ascii")
        self.assertEqual(data.count("DMODESC  CSECT"), 1)
        self.assertEqual(data.count("DMODISP  CSECT"), 1)
        self.assertEqual(data.count("         END\n"), 1)
        self.assertNotIn("EXTRN DMODISP", data)
        self.assertIn("A(DMODISP)", data)
        self.assertTrue(all(len(row) <= 71 for row in data.splitlines()))

    def fake_map(self, size, selected=True, entry="000000"):
        lines = [
            "CROSS REFERENCE TABLE",
            "  R0APP          000000 0000B0",
            "  BCPLMAIN       0000B0 001048",
            "  RGINIT         0010F8 000A20",
            f"  BCPLREG        001D18 {size:06X}",
        ]
        if selected:
            lines.extend([
                "  DMODESC        001C18 000038",
                "  DMODISP        001C50 0000C8",
            ])
        return "\n".join(lines + [
            f" ENTRY ADDRESS       {entry}",
            "LOCATION  REFERS TO SYMBOL",
        ]) + "\n"

    def test_report_profiles(self):
        self.assertEqual(self.v.verify(self.fake_map(28, False), 146), [])
        self.assertEqual(self.v.verify(self.fake_map(28, False), 158), [])
        self.assertEqual(self.v.verify(self.fake_map(36), 156), [])
        self.assertEqual(self.v.verify(self.fake_map(44), 147), [])
        self.assertEqual(self.v.verify(self.fake_map(44), 157), [])

    def test_report_rejects_unexpected_selection(self):
        self.assertTrue(self.v.verify(self.fake_map(28, False), 147))
        self.assertTrue(self.v.verify(self.fake_map(44), 158))
        self.assertTrue(self.v.verify(self.fake_map(44,
                                                     entry="0000B0"), 147))


if __name__ == "__main__":
    unittest.main()
