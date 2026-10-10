#!/usr/bin/env python3
"""Regression tests for assembler source name-field validation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

CHECKER = Path(__file__).with_name("check-asm-source.py")
spec = importlib.util.spec_from_file_location("asm_checker", CHECKER)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class SymbolLengthTests(unittest.TestCase):
    def check(self, source: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.asm"
            path.write_text(source, encoding="ascii")
            return checker.check_file(path)

    def test_original_failure(self):
        errors = self.check("INCURRENT DC   F'0'\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("INCURRENT", errors[0])
        self.assertIn("exceeds 8 characters", errors[0])

    def test_fixed_and_eight_character_symbols(self):
        self.assertEqual(self.check("INCURR DC F'0'\nABCDEFGH EQU *\n"), [])

    def test_references_are_not_definition_fields(self):
        self.assertEqual(self.check("         L 14,INCURRENT\n"), [])

    def test_comments_and_quoted_strings(self):
        self.assertEqual(self.check(
            "* INCURRENT DC F'0'\n         DC C'INCURRENT'\n"
        ), [])

    def test_unlabelled_continuation(self):
        self.assertEqual(self.check(
            "         DC CL8'FIRST',                 X\n"
            "               CL4'NEXT'\n"
        ), [])

    def test_more_than_eight_characters(self):
        errors = self.check("LONGSYMBOL DC F'0'\n")
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
