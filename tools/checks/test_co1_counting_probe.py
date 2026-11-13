#!/usr/bin/env python3
"""Host-only tests for the CO.1 /CPN generated-assembler oracle."""
from pathlib import Path
import runpy
import unittest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                            "bootstrap/probe-co1-counting.py"))
verify = MODULE["verify_assembler"]
ProbeError = MODULE["ProbeError"]


def fixture(entries=2, extra=1, size=44):
    result = []
    for i in range(entries):
        result.extend(["         STM 4,6,0(15)", "         BAL 14,80(11)",
                       "         DC F'0'", f"         DC A(L{700+i}) STACK FRAME SIZE"])
    for _ in range(extra):
        result.extend(["         BAL 14,20(11)", "         DC F'0'"])
    result.append("         BALR 6,4")
    for i in range(entries):
        result.append(f"L{700+i} EQU {size} STACK FRAME SIZE")
    return "\n".join(result) + "\n"


class SourceOracleTests(unittest.TestCase):
    def test_complete_entries_and_site(self):
        self.assertEqual(verify(fixture())["additional_count_sites"], 1)

    def test_two_instrumentation_sites(self):
        self.assertEqual(verify(fixture(extra=2))["additional_count_sites"], 2)

    def test_fails_without_counter_site(self):
        with self.assertRaisesRegex(ProbeError, "counter site"):
            verify(fixture(extra=0))

    def test_fails_without_counter_literal(self):
        with self.assertRaisesRegex(ProbeError, "counter site"):
            verify(fixture().replace("BAL 14,20(11)\n         DC F'0'",
                                     "BAL 14,20(11)\n         DC F'1'"))

    def test_fails_with_incomplete_checked_entry(self):
        with self.assertRaisesRegex(ProbeError, r"complete \+80"):
            verify(fixture().replace("DC A(L701) STACK FRAME SIZE", "DC F'4'"))

    def test_fails_without_two_checked_entries(self):
        with self.assertRaisesRegex(ProbeError, r"complete \+80"):
            verify(fixture(entries=1))

    def test_fails_with_bad_frame(self):
        with self.assertRaisesRegex(ProbeError, "frame size"):
            verify(fixture(size=42))

    def test_fails_with_duplicate_label(self):
        with self.assertRaisesRegex(ProbeError, "frame size"):
            verify(fixture() + "L700 EQU 44 STACK FRAME SIZE\n")

    def test_fails_if_only_checked_path_leaks(self):
        with self.assertRaisesRegex(ProbeError, "checked-only"):
            verify(fixture() + "         BAL 14,60(11)\n")

    def test_fails_without_call(self):
        with self.assertRaisesRegex(ProbeError, "BALR"):
            verify(fixture().replace("BALR 6,4", "BCR 15,6"))

    def test_fails_with_incomplete_extra_counter_site(self):
        with self.assertRaisesRegex(ProbeError, "counter site"):
            verify(fixture() + "         BAL 14,20(11)\n")

    def test_accepts_operand_whitespace(self):
        text = fixture().replace("BAL 14,20(11)", "BAL 14 , 20 ( 11 )")
        self.assertEqual(verify(text)["additional_count_sites"], 1)


if __name__ == "__main__":
    unittest.main()
