#!/usr/bin/env python3
"""Host-only tests for CO.1 four-argument and nested-call compiler output."""
from pathlib import Path
import runpy
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "bootstrap/probe-co1-native-call-abi.py"
MODULE = runpy.run_path(str(SCRIPT))
verify = MODULE["verify_assembler"]
ProbeError = MODULE["ProbeError"]


def sample(entries=3, calls=3, size=44, four=True):
    lines = []
    for n in range(entries):
        lines.append(f"         STM 4,{10 if four and n == 1 else 6},0(15)")
        lines.append("         BAL 14,60(11)")
        lines.append(f"         DC A(L{700+n}) STACK FRAME SIZE")
    lines.extend(["         LA 15,24(5)"])
    lines.extend(["         BALR 6,4"] * calls)
    lines.append("         BCR 15,11")
    for n in range(entries):
        lines.append(f"L{700+n} EQU {size} STACK FRAME SIZE")
    return "\n".join(lines) + "\n"


class NativeCallAbiTest(unittest.TestCase):
    def test_valid(self):
        data = verify(sample())
        self.assertEqual(data["checked_entries"], 3)
        self.assertEqual(data["four_argument_entry"], 1)
        self.assertEqual(data["ordinary_calls"], 3)

    def test_one_extra_entry(self):
        self.assertEqual(verify(sample(entries=4))["checked_entries"], 4)

    def test_too_few_checked_entries(self):
        with self.assertRaisesRegex(ProbeError, "3 complete"):
            verify(sample(entries=2))

    def test_missing_inline_frame(self):
        with self.assertRaisesRegex(ProbeError, "complete"):
            verify(sample().replace("DC A(L700) STACK FRAME SIZE", "DC F'0'"))

    def test_extra_bad_checked_entry(self):
        with self.assertRaisesRegex(ProbeError, "complete"):
            verify(sample() + "         BAL 14,60(11)\n")

    def test_wrong_service(self):
        with self.assertRaisesRegex(ProbeError, "counting service"):
            verify(sample() + "         BAL 14,80(11)\n")

    def test_missing_four_register_save(self):
        with self.assertRaisesRegex(ProbeError, "four-argument callee"):
            verify(sample(four=False))

    def test_duplicate_four_register_save(self):
        with self.assertRaisesRegex(ProbeError, "four-argument callee"):
            verify(sample() + "         STM 4,10,0(15)\n")

    def test_fewer_calls(self):
        with self.assertRaisesRegex(ProbeError, "three BALR"):
            verify(sample(calls=2))

    def test_missing_return(self):
        with self.assertRaisesRegex(ProbeError, "system-vector return"):
            verify(sample().replace("BCR 15,11", "BCR 15,6"))

    def test_missing_workspace(self):
        with self.assertRaisesRegex(ProbeError, "workspace formation"):
            verify(sample().replace("LA 15,24(5)", "LR 15,5"))

    def test_unaligned_frame(self):
        with self.assertRaisesRegex(ProbeError, "frame EQU"):
            verify(sample(size=42))

    def test_zero_frame(self):
        with self.assertRaisesRegex(ProbeError, "frame EQU"):
            verify(sample(size=0))

    def test_missing_frame_definition(self):
        with self.assertRaisesRegex(ProbeError, "frame EQU"):
            verify(sample().replace("L700 EQU 44 STACK FRAME SIZE", ""))

    def test_duplicate_frame_definition(self):
        with self.assertRaisesRegex(ProbeError, "frame EQU"):
            verify(sample() + "L700 EQU 44 STACK FRAME SIZE\n")


if __name__ == "__main__":
    unittest.main()
