"""Q.2 QUERY native campaign JCL and public caller structure."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "q2_query_generator", HERE / "prepare-q2-query.py")
assert SPEC and SPEC.loader
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


class QueryCapabilityCampaign(unittest.TestCase):
    def sample(self):
        return GEN.q1_query().time_helper().trailer_helper().sample_generated()

    def test_real_ifox_iewl_go_job(self):
        deck = GEN.make_deck(
            self.sample(), ["//Q2QUERY JOB (BCPL),'Q2 CHECK',CLASS=A"],
            "HERC02.BCPL.BOOT.OBJ")
        rows = deck.splitlines()
        self.assertEqual(rows.count("         BCXREQ BCPLQSAM"), 1)
        self.assertEqual(rows.count(" NAME Q2QUERY(R)"), 1)
        self.assertEqual(rows.count("/*"), 6)
        for step in ("ASMA", "ASMN", "ASMR", "ASMQ", "ASMG", "LKED", "GO"):
            self.assertEqual(
                sum(row.startswith(f"//{step:<8} EXEC ") for row in rows), 1)
        self.assertIn("//SYSLMOD  DD  DSN=&&Q2QLD(Q2QUERY),", rows)
        self.assertIn(" INCLUDE OBJ(BCPLIO)", rows)
        self.assertFalse(any(row.startswith("//QPOST") for row in rows))
        self.assertTrue(all(row.isascii() and len(row) <= 71 for row in rows))

    def test_bad_job_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Q2QUERY"):
            GEN.make_deck(
                self.sample(), ["//WRONG JOB (BCPL),'TEST',CLASS=A"],
                "HERC02.BCPL.BOOT.OBJ")

    def test_bcpl_capabilities_and_negative_calls(self):
        source = (HERE / "test-q2-query.bcpl").read_text("ascii")
        for required in (
            "I!4 NE 31 | I!5 NE 1", "I!6 NE 909",
            "QSAMSVC(0,I,5)", "QSAMSVC(0,I,0)",
            "QSAMSVC(0,I,6)", "QSAMSVC(2,0,0)",
            "QSAMSVC(3,0,0)", "QSAMSVC(99,0,0)",
            "BCPLQSAM Q2 QUERY FIXED PASS",
        ):
            self.assertIn(required, source)
        self.assertNotIn("QSAMSVC(1,", source)


if __name__ == "__main__":
    unittest.main()
