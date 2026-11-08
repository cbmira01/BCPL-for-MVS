"""Offline isolation tests for the restored object-PDS regression override."""
import importlib.util
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
GEN = ROOT / "tools" / "checks" / "prepare-runtime-pds-regression.py"
spec = importlib.util.spec_from_file_location("runtime_pds_tape_probe", GEN)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RESTORED = "HERC02.BCPL.TPOBJ.RESTORE"


class FakeCore:
    @staticmethod
    def load_config():
        descriptor = {
            "content_type": "object", "recfm": "FB", "lrecl": 80,
            "dsorg": "PO", "dsn": "BCPL.BOOT.OBJ",
        }
        return {"datasets": {
            "BOOT_OBJ": descriptor,
            "BOOT_DEVOBJ": dict(descriptor, dsn="BCPL.BOOT.DEVOBJ"),
        }}

    @staticmethod
    def full_dsn(config, spec):
        return "HERC02." + spec["dsn"]

    @staticmethod
    def authenticated_job_card(config, job, description, redact_password):
        return [f"//{job} JOB CLASS=A"]


class RestoredObjectOverrideTests(unittest.TestCase):
    def run_generator(self, number, env):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "generated.asm"
            out = Path(tmp) / "jcl.jcl"
            src.write_text("         CSECT\n         EXTRN BCPLMAIN\n         END\n", encoding="ascii")
            args = [str(GEN), str(src), str(out), "--test-number", str(number)]
            with mock.patch.dict(os.environ, env, clear=True), \
                 mock.patch.object(sys, "argv", args), \
                 mock.patch.object(mod, "load", return_value=FakeCore):
                mod.main()
            return out.read_text(encoding="ascii")

    def test_case_zero_links_restored_library_only(self):
        deck = self.run_generator(0, {
            "BCPL_RUNTIME_LIBRARY": "OBJ",
            "BCPL_RUNTIME_CANDIDATE": "0",
            "BCPL_TAPE_OBJECT_PDS": RESTORED,
        })
        self.assertIn(f"//OBJ      DD DSN={RESTORED},DISP=SHR", deck)
        self.assertNotIn("DSN=HERC02.BCPL.BOOT.OBJ", deck)
        for name in ("BCPLMAIN", "BCPLIO", "BCPLMEM", "BCPLBYTE", "BCPLAPT", "BCPLRGS", "BCPLREG", "BLIB"):
            self.assertIn(f" INCLUDE OBJ({name})", deck)
        self.assertNotIn("//DEVOBJ", deck)
        self.assertNotIn("//COREOBJ", deck)

    def test_case_three_links_restored_library_only(self):
        deck = self.run_generator(3, {
            "BCPL_RUNTIME_LIBRARY": "OBJ",
            "BCPL_RUNTIME_CANDIDATE": "0",
            "BCPL_TAPE_OBJECT_PDS": RESTORED,
        })
        self.assertIn(f"//OBJ      DD DSN={RESTORED},DISP=SHR", deck)
        self.assertNotIn("DSN=HERC02.BCPL.BOOT.OBJ", deck)

    def test_without_override_uses_production_unchanged(self):
        deck = self.run_generator(0, {
            "BCPL_RUNTIME_LIBRARY": "OBJ",
            "BCPL_RUNTIME_CANDIDATE": "0",
        })
        self.assertIn("//OBJ      DD DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR", deck)
        self.assertNotIn(RESTORED, deck)

    def test_invalid_override_and_profiles_refused(self):
        good = {"BCPL_RUNTIME_LIBRARY": "OBJ", "BCPL_RUNTIME_CANDIDATE": "0",
                "BCPL_TAPE_OBJECT_PDS": RESTORED}
        scenarios = [
            (0, dict(good, BCPL_TAPE_OBJECT_PDS="HERC02.BCPL.BOOT.OBJ")),
            (0, dict(good, BCPL_TAPE_OBJECT_PDS="")),
            (1, good),
            (0, dict(good, BCPL_RUNTIME_LIBRARY="DEVOBJ", BCPL_RUNTIME_CANDIDATE="1")),
            (0, dict(good, R1_ACCEPTANCE="1")),
        ]
        for num, env in scenarios:
            with self.subTest(number=num, environment=env):
                with self.assertRaises(ValueError):
                    self.run_generator(num, env)


if __name__ == "__main__":
    unittest.main()
