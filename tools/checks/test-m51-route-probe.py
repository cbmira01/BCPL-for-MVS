#!/usr/bin/env python3
"""Pure M5.1 probe fixture tests; no Docker/Hercules/JES."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("m51-route-probe.py")
spec = importlib.util.spec_from_file_location("m51_route_probe", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SAMPLE = """//RG114R JOB (ACCT),'TEST'
//* RUNTIME LIBRARY: DEVOBJ; APP ASSEMBLY ONLY
//* D3 BCPLMAIN+BCPLIO CANDIDATE: 1
//ASMAP EXEC PGM=IFOX00
//LKED EXEC PGM=IEWL
 INCLUDE OBJ(BCPLM6)
 INCLUDE OBJ(BCPLIO)
//GO EXEC PGM=*.LKED.SYSLMOD
//SYSPRINT DD SYSOUT=*
//BCPALT DD SYSOUT=*
//SYSUDUMP DD SYSOUT=*
//
"""


class ProbeContractTests(unittest.TestCase):
    def test_candidate_go_source(self):
        module.check_source(SAMPLE)

    def test_reject_non_devobj(self):
        with self.assertRaisesRegex(ValueError, "DEVOBJ"):
            module.check_source(SAMPLE.replace(
                "RUNTIME LIBRARY: DEVOBJ", "RUNTIME LIBRARY: OBJ"))

    def test_reject_wrong_candidate_member(self):
        with self.assertRaisesRegex(ValueError, "BCPLM6"):
            module.check_source(SAMPLE.replace("BCPLM6", "BCPLM7"))

    def test_reject_missing_io(self):
        with self.assertRaisesRegex(ValueError, "BCPLIO"):
            module.check_source(SAMPLE.replace(" INCLUDE OBJ(BCPLIO)", ""))

    def test_reject_missing_second_dd(self):
        with self.assertRaisesRegex(ValueError, "BCPALT"):
            module.check_source(SAMPLE.replace("//BCPALT DD SYSOUT=*\n", ""))

    def test_reject_duplicate_go(self):
        with self.assertRaisesRegex(ValueError, "GO"):
            module.check_source(SAMPLE.replace(
                "//GO EXEC", "//GO EXEC PGM=*.LKED.SYSLMOD\n//GO EXEC", 1))


if __name__ == "__main__":
    unittest.main()
