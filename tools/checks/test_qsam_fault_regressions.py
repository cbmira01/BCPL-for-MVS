"""Host-only tests of private DR.5 QSAM diagnostic contracts."""
import contextlib
import io
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
FAULTS = runpy.run_path(str(ROOT / "tools/checks/qsam-fault-regressions.py"))
EXT = ROOT / "system-extensions/bcplqsam"


class FaultTests(unittest.TestCase):
    def test_combined_overlay_actual_source(self):
        base = (EXT / "bcplqsam.asm").read_text("ascii")
        source = FAULTS["combined_overlay"](base)
        self.assertEqual(source.count("         CLOSE ((2))"), 1)
        self.assertEqual(source.count("GETMAIN RC,LV=1024"), 1)
        for marker in FAULTS["TRACE"]["combined"]:
            self.assertEqual(source.count(marker), 1)
        self.assertTrue(all(len(r) <= 71 and r.isascii() for r in source.splitlines()))
        for anchor in ("QCERRPRI DC   F'0'\n", "QFEXIT   L     15,QFSTAT\n",
                       "         GETMAIN RC,LV=1024\n"):
            with self.subTest(anchor=anchor), self.assertRaises(ValueError):
                FAULTS["combined_overlay"](base.replace(anchor, "", 1))

    def test_actual_generators(self):
        runner = runpy.run_path(str(ROOT / "tools/checks/run-q2-qsam-regression.py"))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(runner["check_faults"](), 0)
        for n in (198, 199, 200):
            self.assertIn(f"CHECK {n}: private diagnostic", out.getvalue())

    def test_job_bound_markers(self):
        for kind in FAULTS["KINDS"]:
            with self.subTest(kind=kind):
                job = "1234"
                name = FAULTS["JOBS"][kind]
                want = FAULTS["TRACE"][kind]
                start = f"JOB {job} $HASP373 {name}  STARTED\n"
                end = f"JOB {job} $HASP395 {name}  ENDED\n"
                rows = [f"JOB {job} +{x}\n" for x in want]
                text = start + "".join(rows) + end
                read = lambda value, number=job: FAULTS["job_markers"](
                    value, number, name, kind)
                self.assertEqual(read(text), want)
                self.assertIsNone(read(text, "9999"))
                self.assertIsNone(read(start + "".join(rows)))
                self.assertNotEqual(read(start + "".join(rows[:-1]) + end), want)
                self.assertNotEqual(read(start + "".join(rows) + rows[-1] + end), want)


if __name__ == "__main__":
    unittest.main()
