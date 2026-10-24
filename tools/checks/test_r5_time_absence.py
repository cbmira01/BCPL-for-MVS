"""R.5 exclusion protection extended to installed BCPLTIME."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "r5_report", HERE / "check-r5-extension-report.py")
r5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r5)


def report(demo=False, time=False, registry=28):
    sections = [("R0APP", 20), ("BCPLMAIN", 100), ("RGINIT", 100),
                ("BCPLREG", registry)]
    if demo:
        sections += [("DMODESC", 56), ("DMODISP", 90)]
    if time:
        sections += [("TIMDESC", 56), ("TIMDISP", 120)]
    return ("ENTRY ADDRESS 00000000\nCROSS REFERENCE TABLE\n" +
            "".join(f"  {name} 00000000 {size:08X}\n"
                    for name, size in sections) +
            "LOCATION  REFERS TO SYMBOL\n")


class R5NoTime(unittest.TestCase):
    def test_empty_unselected(self):
        for number in (146, 158):
            self.assertEqual(r5.verify(report(), number), [])

    def test_demo_only(self):
        for number in (147, 155, 157):
            self.assertEqual(r5.verify(report(True, False, 44), number), [])
        self.assertEqual(r5.verify(report(True, False, 36), 156), [])

    def test_reject_time_when_no_extensions(self):
        for number in (146, 158):
            problems = r5.verify(report(False, True), number)
            self.assertTrue(any("TIMDESC" in x for x in problems))
            self.assertTrue(any("TIMDISP" in x for x in problems))

    def test_reject_time_when_demo_only(self):
        problems = r5.verify(report(True, True, 44), 151)
        self.assertEqual(len([x for x in problems if "BCPLTIME" in x]), 2)


if __name__ == "__main__":
    unittest.main()
