"""Isolated unit checks of the Q.5 geometry preflight deck/overlay generator."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('q5_geometry_prepare',
                                              HERE / 'prepare-q5-geometry-negative.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

PROBE = ("QFPROBE  CSECT\n"
         "QFEL     WTO 'Q5G:E:00000000',MF=L\n"
         "QFLL     WTO 'Q5G:L:00000000',MF=L\n"
         "QFXL     WTO 'Q5G:X:00000000',MF=L\n")
BASE = ('QSMDESC  CSECT\n' + g.OPEN + g.EXIT + g.STATE + 'QSMCTRL  CSECT\n')


class TinyCampaign:
    def verify(self, rows, job, profile):
        if profile != 'finish' or not rows[0].startswith('//'+job+' JOB '):
            raise ValueError('invalid JOB')
        if rows.count(' NAME '+job+'(R)') != 1:
            raise ValueError('wrong link edit')
        for n in range(16):
            if rows.count(f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(OLD,DELETE),') != 1:
                raise ValueError('invalid reader DD')
            if rows.count(f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(NEW,PASS),') != 1:
                raise ValueError('invalid writer DD')
        return '\n'.join(rows) + '\n'

    def source_span(self, rows, step):
        if step != 'ASMQ':
            raise ValueError('ASMQ required')
        lo = rows.index('//SYSIN    DD  *') + 1
        return lo, rows.index('/*', lo)

    @staticmethod
    def replace_one(rows, before, after):
        if rows.count(before) != 1:
            raise ValueError('JCL edit ambiguous')
        rows[rows.index(before)] = after


def template():
    rows = ["//Q16FIN JOB (BCPL),'GEOMETRY',CLASS=A",
            '//ASMQ     EXEC PGM=IFOX00', '//SYSIN    DD  *',
            *BASE.splitlines(), '/*', ' NAME Q16FIN(R)',
            '//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),',
            '//WGO      EXEC PGM=*.LKWR.SYSLMOD,REGION=256K,']
    for n in range(16):
        rows.extend([f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(NEW,PASS),',
                     g.DCB])
    rows.append('//GO       EXEC PGM=*.LKED.SYSLMOD,REGION=256K,')
    for n in range(16):
        rows.extend([f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(OLD,DELETE),',
                     g.DCB])
    rows.extend(['//SYSPRINT DD SYSOUT=*', '//'])
    return '\n'.join(rows) + '\n'


class GeometryOverlayTests(unittest.TestCase):
    def setUp(self):
        self.campaign = TinyCampaign()

    def asm(self, s=BASE):
        return g.instrument_asm(s, PROBE)

    def deck(self, s=BASE, jcl=None):
        return g.instrument_deck(jcl or template(), s, self.campaign, PROBE)

    def test_01_source_overlay_preserves_native_open(self):
        s = self.asm()
        self.assertEqual(s.count('OPEN  ((2),(INPUT))'), 1)
        self.assertEqual(s.count('OPEN  ((2),(OUTPUT))'), 1)

    def test_02_source_overlay_instruments_both_open_sites(self):
        self.assertEqual(self.asm().count('ST    0,Q5GOPEN'), 2)

    def test_03_source_overlay_adds_state_once(self):
        self.assertEqual(self.asm().count("Q5GOPEN  DC    F'0'"),1)

    def test_04_source_overlay_finalizer_status_retained(self):
        self.assertIn('         L     15,QFSTAT\n', self.asm())

    def test_05_source_overlay_uses_literal_pointer(self):
        self.assertIn('L     1,=A(Q5GOPEN)', self.asm())

    def test_06_source_overlay_contains_one_probe_call(self):
        self.assertEqual(self.asm().count('L     15,=A(QFPROBE)'),1)

    def test_07_source_overlay_rejects_duplicate(self):
        with self.assertRaises(ValueError): self.asm(self.asm())

    def test_08_missing_open_anchor_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE.replace(g.OPEN,''))

    def test_09_duplicate_open_anchor_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE.replace(g.OPEN,g.OPEN*2))

    def test_10_missing_state_anchor_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE.replace(g.STATE,''))

    def test_11_missing_exit_anchor_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE.replace(g.EXIT,''))

    def test_12_missing_csect_anchor_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE.replace('QSMCTRL  CSECT\n',''))

    def test_13_overlong_assembler_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE+'*'*72+'\n')

    def test_14_non_ascii_assembler_rejected(self):
        with self.assertRaises(ValueError): self.asm(BASE+'*'+chr(233)+'\n')

    def test_15_deck_identifies_only_test_job(self):
        deck=self.deck()
        self.assertTrue(deck.startswith('//Q5GEOM JOB '))
        self.assertIn(' NAME Q5GEOM(R)',deck)
        self.assertNotIn('Q16FIN', deck)

    def test_16_deck_bad_block_ratio_not_opened_by_asm(self):
        deck=self.deck()
        self.assertIn('BLKSIZE=801)',deck)
        self.assertIn('Q5G:X:',deck)
        self.assertEqual(deck.count('OPEN  ((2),(INPUT))'), 1)

    def test_17_deck_big_stage_ceiling(self):
        self.assertIn('LRECL=1025,BLKSIZE=1025)', self.deck())

    def test_18_deck_omits_go_q01_geometry(self):
        deck=self.deck(); ls=deck.splitlines(); i=ls.index(g.Q01)
        self.assertNotEqual(ls[i+1],g.DCB)
        self.assertEqual(deck.count(g.DCB),31)

    def test_19_deck_preserves_all_16_writer_dds(self):
        deck=self.deck()
        for n in range(16):
            self.assertIn(f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(NEW,PASS),',deck)

    def test_20_deck_rejects_nonmatching_asm(self):
        with self.assertRaises(ValueError): self.deck(BASE+'*not baseline\n')

    def test_21_deck_rejects_modified_writer(self):
        bad=template().replace('DSN=&&Q1H12,DISP=(NEW,PASS)',
                               'DSN=&&Q1HXX,DISP=(NEW,PASS)')
        with self.assertRaises(ValueError): self.deck(jcl=bad)

    def test_22_deck_rejects_modified_reader(self):
        bad=template().replace('DSN=&&Q1H12,DISP=(OLD,DELETE)',
                               'DSN=&&Q1HXX,DISP=(OLD,DELETE)')
        with self.assertRaises(ValueError): self.deck(jcl=bad)

    def test_23_deck_rejects_missing_q01_dcb(self):
        bad=template().replace(g.Q01+'\n'+g.DCB, g.Q01)
        with self.assertRaises(ValueError): self.deck(jcl=bad)

    def test_24_unsafe_card_rejected(self):
        with self.assertRaises(ValueError):g.card_check('too-long'+'X'*72+'\n')

    def test_25_raw_cg370_adapter_accepts_unnamed_csect(self):
        raw=(b'         CSECT\n'+b'* a\n'*105+b'         END\n')
        out=g.validated_compiler_source(raw, lambda x: x+'         ENTRY R0APP')
        self.assertIn('CSECT', out)

    def test_26_raw_cg370_adapter_rejects_bad_source(self):
        with self.assertRaises(ValueError):
            g.validated_compiler_source(b'         CSECT\n'*150,
                                        lambda x: (_ for _ in ()).throw(ValueError()))

    def test_27_raw_cg370_adapter_rejects_too_short(self):
        with self.assertRaises(ValueError):
            g.validated_compiler_source(b' CSECT\n END\n', lambda x:x)

    def test_28_raw_cg370_adapter_rejects_too_long(self):
        with self.assertRaises(ValueError):
            g.validated_compiler_source(b' COMMENT\n'*551,lambda x:x)

    def test_29_fixture_pass_status_and_finish(self):
        with patch.object(g,'FIXTURE',HERE/'test-q5-geometry-negative.bcpl'):
            g.require_fixture()

    def test_30_fixture_invalid_finish_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.bcpl'
            p.write_text('STOP(12)\n',encoding='ascii')
            with patch.object(g,'FIXTURE',p):
                with self.assertRaises(ValueError): g.require_fixture()

    def test_31_fixture_missing_case_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.bcpl'
            p.write_text((HERE/'test-q5-geometry-negative.bcpl').read_text()
                         .replace('"QBAD"','"QXXX"'),encoding='ascii')
            with patch.object(g,'FIXTURE',p):
                with self.assertRaises(ValueError): g.require_fixture()

    def test_32_generator_does_not_submit_jobs(self):
        code=(HERE/'prepare-q5-geometry-negative.py').read_text()
        self.assertNotIn('submit-jcl',code)
        self.assertIn('os.O_EXCL',code)


if __name__ == '__main__':
    unittest.main()
