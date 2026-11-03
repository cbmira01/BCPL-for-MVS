"""Offline strict acceptance tests for Q5RBFIN JOB 8145; no MVS execution."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'q5_finish_evidence', HERE / 'check-q5-rollback-finish.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

SUMMARY = (
    'JOB 8145  Q5RBFIN\n'
    'Q5 FINISH TRACE\n'
    '31 OCT 26  04.46.05 - 04.46.06\n'
    'STEP       PROGRAM      RESULT\n'
    + ''.join(f'{step:<10} {pgm:<12} RC=0000\n'
              for step, pgm in checker.STEPS)
    + 'JOB RESULT: SUCCESS\nHIGHEST RC: 0000\n'
    + 'Assembler:\n  Statements flagged: 0\n  Highest severity:   0\n'
)
# Actual IFOX address, opcode, source-label relationship (the same sequence
# as JOB 8145's QFPROBE listing; not just a narrative explanation).
PROOF = (
    '                                   1200          WTO   MF=(E,QFXL)\n'
    '0010C6 4110 C2CC      01244        1201+         LA    1,QFXL\n'
    '0010CA 0A23                        1202+         SVC   35\n'
    '                                   1203 Q5RPST   WTO   MF=(E,Q5RPL)\n'
    '0010CC 4110 C304      0127C        1204+Q5RPST   LA    1,Q5RPL\n'
    '0010D0 0A23                        1205+         SVC   35\n'
    '0010D2 47F0 C172      010EA        1206          B     QFPDONE\n'
)
REPORT = PROOF + '\nBCPLQSAM Q5 OPEN ROLLBACK PASS\n'
MESSAGES = (
    'Q5R:E:00000001:00000002:00000002:00000001',
    'Q5R:L:00000001:00000001:00000001:00000001:00000000',
    'Q5R:P:POST-CLEAN',
    'Q5R:R:ROLL-RETURN',
    'Q5R:T:CORE-EPILOGUE',
    'Q5R:X:00000000:00000000:00000000:00000000:00000000',
    'Q5R:P:POST-CLEAN',
)


def log(messages=MESSAGES, hardcopy=False):
    prefix = 'FFFF  4.46.06' if hardcopy else '03:46:06 / 4.46.06'
    entries = [f'{prefix} JOB 8145  $HASP373 Q5RBFIN  STARTED']
    entries.extend(f'{prefix} JOB 8145  +{msg}' for msg in messages)
    entries.append(f'{prefix} JOB 8145  $HASP395 Q5RBFIN  ENDED')
    return '\n'.join(entries) + '\n'


CONSOLE = log()
HARDCOPY = log(hardcopy=True)


class Q5RBFINCheck(unittest.TestCase):
    def test_success(self):
        self.assertEqual(checker.check(SUMMARY, REPORT, CONSOLE, HARDCOPY), [])

    def test_confirmed_assembled_fallthrough(self):
        self.assertTrue(checker.fallthrough_confirmed(REPORT))

    def test_reject_missing_x(self):
        c = log(MESSAGES[:5] + MESSAGES[6:])
        self.assertTrue(checker.check(SUMMARY, REPORT, c, HARDCOPY))

    def test_reject_missing_extra_p(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT, log(MESSAGES[:-1]), log(MESSAGES[:-1], True)))

    def test_reject_additional_probe(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT, log(MESSAGES + MESSAGES[-1:]), HARDCOPY))

    def test_reject_wrong_counter(self):
        bad = CONSOLE.replace('00000000:00000000:00000000:00000000:00000000',
                              '00000000:00000000:00000000:00000001:00000000')
        self.assertTrue(checker.check(SUMMARY, REPORT, bad, HARDCOPY))

    def test_reject_wrong_order(self):
        bad = list(MESSAGES)
        bad[2], bad[3] = bad[3], bad[2]
        self.assertTrue(checker.check(SUMMARY, REPORT, log(bad), HARDCOPY))

    def test_reject_mismatched_hardcopy(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT, CONSOLE, HARDCOPY.replace('+Q5R:T:', '+Q5R:Z:')))

    def test_reject_incomplete_job_interval(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT,
            CONSOLE.replace('$HASP395 Q5RBFIN', '$HASP395 Q5WRONG'),
            HARDCOPY))

    def test_reject_wrong_jes_job(self):
        self.assertTrue(checker.check(
            SUMMARY.replace('JOB 8145  Q5RBFIN', 'JOB 8144  Q5RBFIN'),
            REPORT, CONSOLE, HARDCOPY))

    def test_reject_nonzero_go(self):
        self.assertTrue(checker.check(
            SUMMARY.replace('PGM=*.DD     RC=0000',
                            'PGM=*.DD     RC=0008'),
            REPORT, CONSOLE, HARDCOPY))

    def test_reject_missing_pass(self):
        self.assertTrue(checker.check(SUMMARY, PROOF, CONSOLE, HARDCOPY))

    def test_reject_duplicated_pass(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT + checker.PASS + '\n', CONSOLE, HARDCOPY))

    def test_reject_no_fallthrough_listing(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT.replace('0010CC', '0010CE'),
            CONSOLE, HARDCOPY))

    def test_reject_wrong_assembled_opcode(self):
        self.assertTrue(checker.check(
            SUMMARY, REPORT.replace('0010CA 0A23', '0010CA 0700'),
            CONSOLE, HARDCOPY))

    def test_reject_asma_flagged(self):
        self.assertTrue(checker.check(
            SUMMARY.replace('Statements flagged: 0', 'Statements flagged: 1'),
            REPORT, CONSOLE, HARDCOPY))

    def test_provenance_guard(self):
        with tempfile.TemporaryDirectory(prefix='q5rbfin-') as root:
            root = Path(root)
            a = root / 'attempt'
            a.mkdir()
            deck = root / 'q5rbfin.jcl'
            asm = root / 'rollback-finish-generated.asm'
            deck.write_text('temporary', encoding='ascii')
            asm.write_text('temporary', encoding='ascii')
            files = {
                'source-head.txt': checker.HEAD,
                'job-number.txt': '8145',
                'submit.rc': '0',
                'summary.rc': '0',
                'report.rc': '0',
                'jcl.sha256': checker.DECK_SHA + '  q5rbfin.jcl',
                'assembler.sha256': checker.ASM_SHA + '  rollback-finish-generated.asm',
            }
            for name, value in files.items():
                (a / name).write_text(value + '\n', encoding='ascii')
            # Independent content pin must reject arbitrary renamed fixtures.
            self.assertTrue(checker.provenance(a, deck, asm))
            self.assertNotIn('source-head.txt', '\n'.join(checker.provenance(a, deck, asm)))
            (a / 'source-head.txt').write_text('WRONG\n', encoding='ascii')
            self.assertTrue(any('source-head.txt' in message
                                for message in checker.provenance(a, deck, asm)))


if __name__ == '__main__':
    unittest.main()
