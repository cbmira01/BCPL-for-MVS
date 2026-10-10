#!/usr/bin/env python3
"""Offline positive/negative tests for separated TK5 printer files."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

module_path=Path(__file__).with_name("check-dd-attribution.py")
spec=importlib.util.spec_from_file_location("dd_attribution",module_path)
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

def printer(cls,job,jobname,printer,payload):
    banner=lambda kind: (f"****{cls}  {kind}  JOB {job}  {jobname}    ASM LINK GO"
                         f"  PRINTER{printer[-1]}  SYS TK5R  JOB {job}  {kind}  {cls}****\n")
    return (banner("START")*4)+payload+(banner("END")*4)

class AttributionTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        d=Path(self.directory.name)
        self.a=d/"a.txt"
        self.z=d/"z.txt"
        self.ea=d/"expected-a.txt"
        self.ez=d/"expected-z.txt"
        self.ea.write_text("AB\nC\n")
        self.ez.write_text("1\n2\n")
        self.prefix=b"OLD PRINTER OUTPUT\n"
        self.write("AB\nC\n","1\n2\n")
    def write(self,a_payload,z_payload):
        self.a.write_bytes(self.prefix+printer("A",5512,"AT114R","PRINTER1",a_payload).encode())
        self.z.write_bytes(self.prefix+printer("Z",5512,"AT114R","PRINTER2",z_payload).encode())
    def check(self,**updates):
        fields=dict(a_path=self.a,z_path=self.z,
                    a_offset=len(self.prefix),z_offset=len(self.prefix),
                    job=5512,jobname="AT114R",expected_a=self.ea,expected_z=self.ez)
        fields.update(updates)
        return checker.verify(**fields)
    def test_positive(self):
        self.check()
    def test_ff_before_primary_record(self):
        self.write("\\x0cAB\\nC\\n","1\\n2\\n")
        self.check()
    def test_ff_does_not_mask_leading_space(self):
        self.write("\\x0c AB\\nC\\n","1\\n2\\n")
        with self.assertRaisesRegex(ValueError,"class A missing"):
            self.check()
    def test_missing_alt_record(self):
        self.write("AB\nC\n","1\n")
        with self.assertRaisesRegex(ValueError,"class Z missing"):
            self.check()
    def test_swapped_outputs(self):
        self.write("1\n2\n","AB\nC\n")
        with self.assertRaises(ValueError):
            self.check()
    def test_cross_contamination(self):
        self.write("AB\nC\n1\n","1\n2\n")
        with self.assertRaisesRegex(ValueError,"class A includes a BCPALT record"):
            self.check()
    def test_wrong_job(self):
        with self.assertRaisesRegex(ValueError,"section absent"):
            self.check(job=5513)
    def test_invalid_offset(self):
        with self.assertRaisesRegex(ValueError,"invalid start offset"):
            self.check(z_offset=999999)
    def test_foreign_job_banner(self):
        self.write("AB\nC\n****A  START  JOB 9000  FOREIGN  PRINTER1\n","1\n2\n")
        with self.assertRaisesRegex(ValueError,"foreign JES"):
            self.check()
    def test_same_file(self):
        with self.assertRaisesRegex(ValueError,"different"):
            self.check(z_path=self.a)

if __name__=="__main__":
    unittest.main()
