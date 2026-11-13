#!/usr/bin/env python3
"""Host-only tests for the CO.1 CK-C compiler-only assembler validator."""

from pathlib import Path
import runpy
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "bootstrap/probe-co1-ckc.py"
PROBE = runpy.run_path(str(SCRIPT))
verify = PROBE["verify_assembler"]
Error = PROBE["VerificationError"]


def sample(*, entries=2, second_word=True, wrong_service=False, size=44):
    lines = []
    for i in range(entries):
        lines.extend([
            "         STM   4,6,0(15)",
            f"         BAL   14,{60 if wrong_service else 80}(11)",
            "         DC    F'0'",
        ])
        if second_word:
            lines.append(f"         DC    A(L{700 + i}) STACK FRAME SIZE")
    lines.extend(["         BALR  6,4"])
    for i in range(entries):
        lines.append(f"L{700+i} EQU   {size} STACK FRAME SIZE")
    return "\n".join(lines) + "\n"


class CheckCO1CKC(unittest.TestCase):
    def test_two_valid_entries(self):
        actual = verify(sample())
        self.assertEqual(actual["checked_counted_entries"], 2)
        self.assertEqual(actual["frame_sizes_bytes"], [44, 44])

    def test_one_entry_is_insufficient(self):
        with self.assertRaisesRegex(Error, "at least two"):
            verify(sample(entries=1))

    def test_missing_second_word_fails(self):
        with self.assertRaisesRegex(Error, "complete"):
            verify(sample(second_word=False))

    def test_checked_only_fails(self):
        with self.assertRaisesRegex(Error, "at least two"):
            verify(sample(wrong_service=True))

    def test_mixed_entry_fails(self):
        example = sample().replace("BAL   14,80(11)", "BAL   14,60(11)", 1)
        with self.assertRaisesRegex(Error, "complete"):
            verify(example)

    def test_missing_equs_fails(self):
        with self.assertRaisesRegex(Error, "frame-size EQU"):
            verify(sample().replace("L701 EQU   44 STACK FRAME SIZE", ""))

    def test_duplicate_equs_fails(self):
        with self.assertRaisesRegex(Error, "expected one"):
            verify(sample() + "L700 EQU   44 STACK FRAME SIZE\n")

    def test_misaligned_frame_fails(self):
        with self.assertRaisesRegex(Error, "invalid frame size"):
            verify(sample(size=42))

    def test_zero_frame_fails(self):
        with self.assertRaisesRegex(Error, "invalid frame size"):
            verify(sample(size=0))

    def test_missing_nested_call_fails(self):
        with self.assertRaisesRegex(Error, "BALR"):
            verify(sample().replace("BALR  6,4", "BCR   15,6"))

    def test_valid_spaced_operands(self):
        example = sample().replace("14,80(11)", "14 , 80 ( 11 )")
        self.assertEqual(verify(example)["checked_counted_entries"], 2)


if __name__ == "__main__":
    unittest.main()
