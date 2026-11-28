from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[2]
m = runpy.run_path(str(ROOT / "tools/checks/run-dr5-blib-build-verification.py"))


class BlibBuildTests(unittest.TestCase):
    def test_private_decks_use_production_gate_and_no_installed_destination(self):
        body = m["JCL"].read_text("ascii")
        for negative in (False, True):
            deck = m["deck_for"](body, ["//DR5BLPOS JOB (BCPL),'TEST'"], negative)
            self.assertIn(m["PRIVATE"], deck)
            self.assertNotIn(m["TARGET"], deck)
            self.assertIn(m["BAD_PARAM"] if negative else m["PARAM"], deck)
            self.assertEqual(len((m["BAD_PARAM"] if negative else m["PARAM"])), 80)
            self.assertEqual(deck.count("COND=(0,NE)"), 6)
        for malformed in (body.replace(m["TARGET"], "//SYSUT2 DD DUMMY"),
                          body.replace("COND=(0,NE)", "COND=(8,LT)", 1),
                          body.replace(m["PARAM"], "/N")):
            with self.assertRaises(ValueError):
                m["deck_for"](malformed, ["//DR5BLPOS JOB (BCPL),'TEST'"])

    def evidence(self, negative):
        name = "DR5BLNEG" if negative else "DR5BLPOS"
        steps = m["STEPS"][:5] if negative else m["STEPS"]
        summary = "JOB 1234  " + name + "\n"
        for step, pgm in steps:
            code = 8 if negative and step == "FIXASM" else 0
            summary += f"{step:<10} {pgm or 'PGM=*.DD':<12} RC={code:04d}\n"
        summary += ("JOB RESULT: FAILURE\nHIGHEST RC: 0008\n" if negative
                    else "JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n")
        report = f" EXECUTION CYCLES = 9515157, CODE = {8 if negative else 0}\n"
        report += "HIGHEST SEVERITY WAS 0\n" * (1 if negative else 2)
        if negative:
            for step, pgm in m["STEPS"][5:]:
                report += f"22.22.25 JOB 1234 {name} {step} {pgm} *FLUSH*\n"
        return name, summary, report

    def test_positive_and_negative_evidence(self):
        for negative in (False, True):
            name, summary, report = self.evidence(negative)
            result = m["assess"]("1234", name, summary, report, int(negative), negative)
            self.assertEqual(result["compiler_code"], 8 if negative else 0)
            self.assertEqual(result["installation_flushed"], negative)

    def test_reject_missing_duplicate_or_malformed_completion(self):
        for negative in (False, True):
            name, summary, report = self.evidence(negative)
            for changed in (report.replace("EXECUTION CYCLES", "OTHER"),
                            report + report.splitlines()[0] + "\n",
                            report.replace("CODE = ", "CODE = 0"),
                            report.replace("CODE = ", "CODE = -")):
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    m["assess"]("1234", name, summary, changed, int(negative), negative)

    def test_negative_requires_actual_gate_and_both_flushed_steps(self):
        name, summary, report = self.evidence(True)
        for changed in (report.replace("ASMBLIB IFOX00 *FLUSH*", ""),
                        report.replace("INSTALL IEBGENER *FLUSH*", "")):
            with self.assertRaises(ValueError):
                m["assess"]("1234", name, summary, changed, 1, True)
        for changed in (summary.replace("RC=0008", "RC=0000"),
                        summary + "INSTALL IEBGENER RC=0000\n",
                        summary + "ABEND: detected\n"):
            with self.assertRaises(ValueError):
                m["assess"]("1234", name, changed, report, 1, True)
