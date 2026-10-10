#!/usr/bin/env python3
"""Standalone unit checks for combined-JES logical-record matching."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

CHECK=Path(__file__).resolve().parent/"check-combined-jes-records.py"
spec=importlib.util.spec_from_file_location("jeschecker",CHECK)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CheckCombinedJES(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
    def write(self, name, text):
        p=self.path/name
        p.write_text(text,encoding="utf-8")
        return p
    def test_two_records_and_empty_record(self):
        report=self.write("report","ASSEMBLER A\\nAUTHORIZATION CODE IS 0.\\nA\\n\\nB\\n")
        fixture=self.write("fixture","A\\n\\nB\\n")
        self.assertEqual(module.validate(fixture,report,"SYSPRINT"),1)
    def test_wrong_leading_blank_fails(self):
        report=self.write("report","AUTHORIZATION CODE IS 0.\\n A\\n")
        fixture=self.write("fixture","A\\n")
        with self.assertRaises(ValueError):
            module.validate(fixture,report,"SYSPRINT")
    def test_missing_linker_boundary_fails(self):
        report=self.write("report","A\\n")
        fixture=self.write("fixture","A\\n")
        with self.assertRaisesRegex(ValueError,"boundary"):
            module.validate(fixture,report,"SYSPRINT")
    def test_noncontiguous_records_fail(self):
        report=self.write("report","AUTHORIZATION CODE IS 0.\\nA\\nOTHER\\nB\\n")
        fixture=self.write("fixture","A\\nB\\n")
        with self.assertRaises(ValueError):
            module.validate(fixture,report,"BCPALT")
    def test_exact_132_record(self):
        report=self.write("report","AUTHORIZATION CODE IS 0.\\n"+ "A"*132+"\\n")
        fixture=self.write("fixture","A"*132+"\\n")
        self.assertEqual(module.validate(fixture,report,"SYSPRINT"),1)
    def test_empty_fixture_rejected(self):
        report=self.write("report","AUTHORIZATION CODE IS 0.\\nA\\n")
        fixture=self.write("fixture","")
        with self.assertRaises(ValueError):
            module.validate(fixture,report,"SYSPRINT")
    def test_old_source_listing_cannot_satisfy(self):
        report=self.write("report","A\\nAUTHORIZATION CODE IS 0.\\nB\\n")
        fixture=self.write("fixture","A\\n")
        with self.assertRaises(ValueError):
            module.validate(fixture,report,"SYSPRINT")
if __name__=="__main__":
    unittest.main()
