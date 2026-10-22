#!/usr/bin/env python3
"""Credential-free R.2 BCPLDEMO source and candidate JCL checks."""
import importlib.util
from pathlib import Path
import re
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXT = ROOT / 'bootstrap-toolchain/extensions/bcpldemo'
REG = ROOT / 'packaging/global-number-registry.md'


def load():
    spec = importlib.util.spec_from_file_location('r2_demogen', HERE/'make-job.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DemoHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load()

    def test_real_permanent_global_and_no_trailer_binding(self):
        reg = REG.read_text('utf-8')
        header = (EXT/'bcpldemo.h').read_text('ascii')
        caller = (HERE/'demo.bcpl').read_text('ascii')
        self.assertIn('**203**', reg)
        self.assertIn('DEMOSVC:203', header)
        self.assertIn('DEMOSVC:203', caller)
        self.assertNotIn('R0QA:298', caller)
        self.assertIn('DEMOSVC(0,0,0)', caller)
        self.assertIn('DEMOSVC(1,VALUES,3)', caller)

    def test_bcplreg_links_descriptor_and_declares_requirement(self):
        registry, descriptor, dispatch = self.builder.sources()
        self.assertIn('A(DMOBEG),A(DMOEND)', registry)
        self.assertIn("CL8'BCPLDEMO'", registry)
        self.assertIn("F'203',A(DMODISP)", descriptor)
        self.assertIn("F'1',F'48',F'56'", descriptor)
        self.assertIn("F'1',F'0',F'1',F'0',F'0',F'0'", descriptor)
        self.assertIn('ENTRY DMODISP', dispatch)
        self.assertNotIn('R1TEST', registry)

    def test_query_vector_and_opcode_dispatch_guards(self):
        asm = (EXT/'dispatcher.asm').read_text('ascii')
        self.assertRegex(asm, r'(?m)^QPTR\s+LTR   9,9$')
        self.assertLess(asm.index("C     9,=F'6'"), asm.index('SLL   8,2'))
        self.assertIn("C     9,=F'3'", asm)
        self.assertIn("ST    14,8(8)", asm)
        self.assertIn("L     7,=F'-2'", asm)
        self.assertIn("L     7,=F'-1'", asm)
        self.assertIn("L     7,=F'-3'", asm)
        self.assertIn("BCR   15,11", asm)
        self.assertFalse(any(len(line) > 71 for line in asm.splitlines()))

    def test_real_r1_registration_overlay_and_temp_jcl(self):
        trail = self.builder.load(self.builder.TRAIL, 'r2_fixture_trail')
        jcl = self.builder.make_deck(trail.sample_generated(),
                 ["//R2DEMO JOB (BCPL),'R2 DEMO',CLASS=A,MSGCLASS=A"],
                 'HERC02.BCPL.BOOT.OBJ')
        self.assertIn('//ASMD', jcl)
        self.assertIn('//ASMS', jcl)
        self.assertIn('DSN=&&R2DOBJ', jcl)
        self.assertIn('DSN=&&R2SOBJ', jcl)
        self.assertIn('DSN=HERC02.BCPL.BOOT.OBJ,DISP=SHR', jcl)
        self.assertIn('ENTRY R0APP', jcl)
        self.assertIn('NAME R2DEMO(R)', jcl)
        self.assertIn('//* R.2 BCPLDEMO BCPLREG CANDIDATE', jcl)
        self.assertNotIn('R1TEST', jcl)
        self.assertNotIn(' INCLUDE OBJ(BCPLMAIN)', jcl)
        self.assertNotIn('DISP=MOD', jcl)
        self.assertNotIn('BOOT.DEVOBJ', jcl)
        self.assertEqual(jcl.splitlines().count('/*'), 7)
        self.assertTrue(all(row.isascii() and len(row) <= 71
                            for row in jcl.splitlines()))


if __name__ == '__main__':
    unittest.main()
