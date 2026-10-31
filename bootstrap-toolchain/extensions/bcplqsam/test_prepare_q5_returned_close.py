"""Unit tests for Q.5 returned-CLOSE status-injection source/JCL safety."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('prepare-q5-returned-close.py')
spec = importlib.util.spec_from_file_location('q5_returned_close', SCRIPT)
q5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q5)

BASE = (
    'QSMDESC  CSECT\n'
    + q5.CLOSE
    + '         LTR   15,15\n         BNZ   QSCQUAR\n'
    + q5.SUCCESS_CLOSE
    + q5.QUAR
    + q5.STATE
    + q5.FINALIZER
    + 'QSMCTRL  CSECT\n'
)
PROBE = (
    'QFPROBE  CSECT\n'
    "QFEL     WTO 'Q5C:E:00000000',MF=L\n"
    "QFLL     WTO 'Q5C:L:00000000',MF=L\n"
    "QFXL     WTO 'Q5C:X:00000000',MF=L\n"
)


class TinyCampaign:
    def verify(self, rows, job, profile):
        if profile != 'finish' or not rows[0].startswith('//'+job+' JOB '):
            raise ValueError('wrong job profile')
        if rows.count(' NAME '+job+'(R)') != 1:
            raise ValueError('missing job link name')
        return '\n'.join(rows)+'\n'

    def source_span(self, rows, step):
        if step != 'ASMQ':
            raise ValueError('wrong step')
        lo = rows.index('//SYSIN    DD  *') + 1
        return lo, rows.index('/*', lo)

    def replace_one(self, rows, original, replacement):
        if rows.count(original) != 1:
            raise ValueError('missing JCL identity card')
        rows[rows.index(original)] = replacement


def minimal_deck():
    return '\n'.join([
        "//Q16FIN JOB (BCPL),'Q5 TEST',CLASS=A",
        '//ASMQ     EXEC PGM=IFOX00', '//SYSIN    DD  *',
        *BASE.splitlines(), '/*', ' NAME Q16FIN(R)',
        '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),', '//', '',
    ])


class Q5CloseOverlay(unittest.TestCase):
    def test_success_source(self):
        src = q5.instrument_asm(BASE, PROBE)
        self.assertEqual(src.count('CLOSE ((2))'), 1)
        self.assertIn('ST    0,Q5CONCE', src)
        self.assertIn('LA    15,4', src)
        self.assertIn("Q5CONCE  DC    F'0'", src)
        self.assertIn("CLC   4(4,4),=F'1'", src)
        self.assertIn('Q5CSKIP  SR    15,15', src)
        self.assertIn('QFEXIT   LA    0,2', src)
        self.assertEqual(src.count('L     15,=A(QFPROBE)'), 3)

    def test_real_close_precedes_injection(self):
        src = q5.instrument_asm(BASE, PROBE)
        self.assertLess(src.index('CLOSE ((2))'), src.index("ST    0,Q5CONCE"))
        self.assertLess(src.index('CLOSE ((2))'), src.index('LA    15,4'))
        self.assertLess(src.index('LTR   15,15\n         BNZ   Q5CNORM'),
                        src.index('LA    15,4'))
        self.assertLess(src.index('LA    15,4'), src.index('Q5CNORM  DS'))

    def test_reject_repeat(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(q5.instrument_asm(BASE, PROBE), PROBE)

    def test_reject_missing_close_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.CLOSE, ''), PROBE)

    def test_reject_duplicated_close_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.CLOSE, q5.CLOSE * 2), PROBE)

    def test_reject_missing_quarantine_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.QUAR, ''), PROBE)

    def test_reject_missing_clean_return_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.SUCCESS_CLOSE, ''), PROBE)

    def test_reject_missing_finalizer_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.FINALIZER, ''), PROBE)

    def test_reject_missing_private_state_anchor(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE.replace(q5.STATE, ''), PROBE)

    def test_reject_no_probe(self):
        with self.assertRaises(ValueError):
            q5.instrument_asm(BASE, '')

    def test_reject_overlong_card(self):
        with self.assertRaisesRegex(ValueError, 'invalid IFOX card'):
            q5.instrument_asm(BASE + '*'*72 + '\n', PROBE)

    def test_reject_non_ascii(self):
        with self.assertRaisesRegex(ValueError, 'invalid IFOX card'):
            q5.instrument_asm(BASE + '*é\n', PROBE)

    def test_deck_three_identities(self):
        fake = TinyCampaign()
        with patch.object(q5, 'loader', return_value=fake):
            with patch.object(q5, 'probe_source', return_value=PROBE):
                deck = q5.instrument_deck(minimal_deck(), BASE)
        self.assertTrue(deck.startswith('//Q5RCCLOS JOB '))
        self.assertIn(' NAME Q5RCCLOS(R)\n', deck)
        self.assertIn('DSN=&&Q1LOAD(Q5RCCLOS)', deck)
        self.assertNotIn('Q16FIN', deck)
        self.assertEqual(deck.count('         CLOSE ((2))'), 1)

    def test_deck_reject_stale_baseline(self):
        fake = TinyCampaign()
        with patch.object(q5, 'loader', return_value=fake):
            with self.assertRaises(ValueError):
                q5.instrument_deck(minimal_deck(), BASE + '*new\n')

    def test_deck_reject_wrong_link_identity(self):
        fake = TinyCampaign()
        with patch.object(q5, 'loader', return_value=fake):
            with patch.object(q5, 'probe_source', return_value=PROBE):
                with self.assertRaises(ValueError):
                    q5.instrument_deck(
                        minimal_deck().replace(' NAME Q16FIN(R)',
                                               ' NAME Q16WRONG(R)'), BASE)

    def test_source_fixture_guard(self):
        with patch.object(q5, 'FIXTURE', Path(__file__).with_name('test-q5-returned-close.bcpl')):
            q5.require_fixture()

    def test_source_missing_finish_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'bad.bcpl'
            target.write_text('STOP(12)\n', encoding='ascii')
            with patch.object(q5, 'FIXTURE', target):
                with self.assertRaises(ValueError):
                    q5.require_fixture()

    def test_no_persistent_mvs_operations_in_generator(self):
        code = SCRIPT.read_text('utf-8')
        self.assertNotIn('submit-jcl', code)
        self.assertNotIn('subprocess.', code)
        self.assertNotIn('DISP=MOD', code)
        self.assertNotIn('CATLG', code)
        self.assertIn('os.O_EXCL', code)


if __name__ == '__main__':
    unittest.main()
