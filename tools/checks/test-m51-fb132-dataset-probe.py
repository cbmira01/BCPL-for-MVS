#!/usr/bin/env python3
"""Offline-only source/JCL transformation checks for M5.1.2."""
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).with_name("m51-fb132-dataset-probe.py")
spec = importlib.util.spec_from_file_location("fb132", p)
fb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fb)
SAMPLE = """//RG124R JOB (X),'BCPL'
//* RUNTIME LIBRARY: DEVOBJ; APP ASSEMBLY ONLY
//* D3 BCPLMAIN+BCPLIO CANDIDATE: 1
//ASMAP EXEC PGM=IFOX00
//LKED EXEC PGM=IEWL
 INCLUDE OBJ(BCPLM6)
 INCLUDE OBJ(BCPLIO)
//GO EXEC PGM=*.LKED.SYSLMOD
//SYSPRINT DD SYSOUT=*
//REPORT   DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//REPORT2  DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)
//SYSUDUMP DD SYSOUT=*
//
"""


class TestDatasetProbe(unittest.TestCase):
    def setUp(self):
        self.asm = fb.verifier(["BCPL REPORT A", "BCPL REPORT B"],
                               ["BCPL REPORT2 PART"])

    def test_full_132_byte_compare_and_eof(self):
        self.assertIn("CLC   BUF1(132),EXP11", self.asm)
        self.assertIn("CLC   BUF1(132),EXP12", self.asm)
        self.assertIn("CLC   BUF2(132),EXP21", self.asm)
        self.assertIn("GET   DCB1,BUF1\n         B     BAD", self.asm)
        self.assertIn("STM   14,12,12(13)", self.asm)
        self.assertIn("LR    12,15", self.asm)
        self.assertIn("ST    13,OLDSAVE+4", self.asm)
        self.assertIn("LA    13,NEWSAVE", self.asm)
        self.assertIn("OLDSAVE  DS    18F", self.asm)
        self.assertIn("NEWSAVE  DS    18F", self.asm)
        self.assertEqual(self.asm.count("LM    14,12,12(13)"), 2)
        self.assertNotIn("SAV14", self.asm)
        self.assertIn("GET   DCB2,BUF2\n         B     BAD", self.asm)

    def test_generated_go_verifier_and_dataset_identity(self):
        deck = fb.transform(SAMPLE, self.asm)
        self.assertIn("//M5D124B JOB", deck)
        self.assertIn("//VCHK     EXEC", deck)
        self.assertEqual(deck.count("DSN=&&M5RPT1"), 2)
        self.assertEqual(deck.count("DSN=&&M5RPT2"), 2)
        self.assertNotIn("//REPORT   DD SYSOUT=*", deck)

    def test_reject_non_candidate(self):
        with self.assertRaisesRegex(ValueError, "DEVOBJ"):
            fb.transform(SAMPLE.replace("RUNTIME LIBRARY: DEVOBJ",
                                        "RUNTIME LIBRARY: OBJ"), self.asm)

    def test_reject_missing_report2(self):
        with self.assertRaisesRegex(ValueError, "REPORT2"):
            fb.transform(SAMPLE.replace(
                "//REPORT2  DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)\n",
                ""), self.asm)

    def test_reject_fixture_drift(self):
        with self.assertRaisesRegex(ValueError, "drifted"):
            fb.verifier(["ALTERED"], ["BCPL REPORT2 PART"])

    def test_review_bundle_exact_and_tampered(self):
        from hashlib import sha256
        source = SAMPLE.encode("ascii")
        deck = fb.transform(SAMPLE, self.asm).encode("ascii")
        asm = self.asm.encode("ascii")
        records1 = b"BCPL REPORT A\nBCPL REPORT B\n"
        records2 = b"BCPL REPORT2 PART\n"
        base = {
            "schema": "m51-dataset-readback-v2",
            "job": fb.JOB, "writer": "GO", "verifier": "VCHK",
            "state": "PREPARED_NOT_EXECUTED",
        }
        for key, payload in (
            ("source_sha256", source),
            ("deck_sha256", deck),
            ("asm_sha256", asm),
            ("report_fixture_sha256", records1),
            ("report2_fixture_sha256", records2),
        ):
            base[key] = sha256(payload).hexdigest()
        fb.review_bundle(source, deck, asm, records1, records2, base)
        with self.assertRaisesRegex(ValueError, "SHA256"):
            fb.review_bundle(source, deck + b"\\n", asm,
                             records1, records2, base)
        altered = dict(base)
        altered["deck_sha256"] = sha256(deck + b"\\n").hexdigest()
        with self.assertRaisesRegex(ValueError, "JCL differs"):
            fb.review_bundle(source, deck + b"\\n", asm,
                             records1, records2, altered)
        with self.assertRaisesRegex(ValueError, "staging state"):
            fb.review_bundle(source, deck, asm, records1,
                             records2, {**base, "state": "VERIFIED"})


if __name__ == "__main__":
    unittest.main()
