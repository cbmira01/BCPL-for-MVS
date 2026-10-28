"""Offline unit tests for the single-job Q2FULL JCL builder.

No credentials, compiler execution, JES submission, or MVS mutations.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PATH = HERE / "prepare-q2-consolidated.py"
SPEC = importlib.util.spec_from_file_location("q2fullprep", PATH)
assert SPEC is not None and SPEC.loader is not None
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class ConsolidatedCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        q = GEN.query_helper()
        cg = q.time_helper().trailer_helper().sample_generated()
        cls.deck = GEN.make_deck(
            cg, cg, ["//Q2FULL JOB (BCPL),'Q2 TEST',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")

    def test_all_assemble_link_execution_phases_present(self):
        rows = self.deck.splitlines()
        self.assertEqual(rows.count("//SYSIN    DD  *"), 7)
        self.assertEqual(rows.count("/*"), 10)
        for step in ("ASMA", "ASMB", "ASMV", "ASMN", "ASMR",
                     "ASMQ", "ASMG", "LKED", "LKRD", "LKVR",
                     "WGO", "RGO", "VGO"):
            self.assertEqual(sum(
                row.startswith(f"//{step:<8} EXEC ") for row in rows), 1,
                step)
        self.assertEqual(rows.count(" ENTRY R0APP"), 2)
        self.assertEqual(rows.count(" ENTRY Q2VFY"), 1)

    def test_temporary_dd_handoff_and_geometry(self):
        rows = self.deck.splitlines()
        for name, ds, fmt in (("QFOUT", "Q2F", "F"),
                              ("QBOUT", "Q2B", "FB"),
                              ("QEMPTY", "Q2E", "F")):
            for disposition, create in (("NEW,PASS", True),
                                         ("OLD,DELETE", False)):
                target = GEN.dd(name, ds, disposition, fmt, new=create)
                i = rows.index(target[0])
                self.assertEqual(rows[i:i+len(target)], target)
        for disposition, create in (("NEW,PASS", True),
                                     ("OLD,DELETE", False)):
            target = GEN.dd("QBCOPY", "Q2C", disposition, "FB",
                            new=create)
            i = rows.index(target[0])
            self.assertEqual(rows[i:i+len(target)], target)
        self.assertIn("Q2VFY", self.deck)

    def test_all_cards_are_bounded_and_no_permanent_output(self):
        rows = self.deck.splitlines()
        self.assertTrue(all(len(r) <= 71 and r.isascii()
                            and "\t" not in r for r in rows))
        self.assertNotIn("CATLG", self.deck)
        self.assertNotIn("DISP=MOD", self.deck)
        self.assertNotIn("BOOT_DEVOBJ", self.deck)
        self.assertEqual(rows.count("         BCXREQ BCPLQSAM"), 1)

    def test_reader_link_uses_renamed_writer_template(self):
        """Catch Q1QUERY-era names after writer link has been renamed."""
        writer = [
            GEN.LINK,
            "//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)",
            " NAME Q2WRIT(R)",
            "//SYSLMOD  DD  DSN=&&Q2WLD(Q2WRIT),",
        ]
        reader = GEN.link_reader(writer)
        self.assertIn("//LKRD     EXEC PGM=IEWL,REGION=256K,", reader)
        self.assertIn("//SYSLIN   DD  DSN=&&Q2RDOBJ,DISP=(OLD,PASS)",
                      reader)
        self.assertIn(" NAME Q2READ(R)", reader)
        self.assertIn("//SYSLMOD  DD  DSN=&&Q2RLD(Q2READ),", reader)

    def test_link_source_and_load_identity(self):
        rows = self.deck.splitlines()
        writer_begin = GEN.part(rows, "//LKED     EXEC ")
        reader_begin = GEN.part(rows, "//LKRD     EXEC ")
        verifier_begin = GEN.part(rows, "//LKVR     EXEC ")
        writer = rows[writer_begin:reader_begin]
        reader = rows[reader_begin:verifier_begin]
        self.assertIn("//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)",
                      writer)
        self.assertIn("//SYSLMOD  DD  DSN=&&Q2WLD(Q2WRIT),", writer)
        self.assertIn("//SYSLIN   DD  DSN=&&Q2RDOBJ,DISP=(OLD,PASS)",
                      reader)
        self.assertIn("//SYSLMOD  DD  DSN=&&Q2RLD(Q2READ),", reader)
        wrong = list(rows)
        wrong[wrong.index(
            "//SYSLIN   DD  DSN=&&Q2RDOBJ,DISP=(OLD,PASS)"
        )] = "//SYSLIN   DD  DSN=&&Q1APOBJ,DISP=(OLD,PASS)"
        with self.assertRaisesRegex(ValueError, "LKRD"):
            GEN.verify(wrong)

    def test_rejects_removed_required_phase(self):
        rows = self.deck.splitlines()
        rows.remove("//VGO      EXEC PGM=*.LKVR.SYSLMOD,REGION=256K,")
        with self.assertRaises(ValueError):
            GEN.verify(rows)

    def test_rejects_geometry_and_illegal_output(self):
        rows = self.deck.splitlines()
        # Target Q.2 data DD, not the earlier assembler object DDs,
        # which can also have FB80/800 DCB cards.
        q_b = GEN.dd("QBOUT", "Q2B", "NEW,PASS", "FB", new=True)
        rows[rows.index(q_b[0]) + 2] = (
            "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=801)")
        with self.assertRaises(ValueError):
            GEN.verify(rows)
        rows = self.deck.splitlines()
        rows.insert(-1, "//QFOUT    DD  DSN=HERC02.TEST,DISP=(NEW,CATLG)")
        with self.assertRaises(ValueError):
            GEN.verify(rows)

    def test_rejects_wrong_job_identity(self):
        rows = self.deck.splitlines()
        rows[0] = "//Q2WRONG JOB (BCPL),'Q2 TEST',CLASS=A"
        with self.assertRaises(ValueError):
            GEN.verify(rows)


if __name__ == "__main__":
    unittest.main()
