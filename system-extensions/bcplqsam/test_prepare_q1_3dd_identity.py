"""Offline negative and isolation tests for Q.1 identity-only preparation."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'q1_identity', HERE / 'prepare-q1-3dd-identity.py')
assert spec is not None and spec.loader is not None
ident = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ident)


# Reduced ASMQ source fixture with exactly the anchored production path.
# The real --check validates a freshly generated complete Q13DD deck.
ASM = '''QSMCORE  CSECT
         ST    8,QCREQ
         ST    9,QCRES
         C     7,=F'1'
         BE    QCOPEN
         RDJFCB ((2))
         OPEN  ((2),(OUTPUT))
QCOPENIN OPEN  ((2),(INPUT))
QSMCTRL  CSECT
QS00     DC    F'0'
'''


def synthetic_deck(asm: str = ASM) -> str:
    lines = [
        "//Q13DD JOB (BCPL),'IDENTITY',CLASS=A",
        '//ASMQ     EXEC PGM=IFOX00',
        '//SYSIN    DD  *',
        *asm.splitlines(),
        '/*',
        '//ASMG     EXEC PGM=IFOX00',
    ]
    # Five other native IFOX source streams plus one WGO writer: 6 total.
    for _ in range(5):
        lines += ['//SYSIN    DD  *', '         END', '/*']
    lines += [
        '         BCXREQ BCPLQSAM',
        '/*',
        '/*',
        ident.WGO,
    ]
    for n in range(3):
        lines += [
            f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},DISP=(NEW,PASS),',
            '//             UNIT=SYSDA,SPACE=(TRK,(2,1)),',
            '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)',
        ]
    lines += [ident.GO]
    for n in range(3):
        lines += [f'//Q{n:02d}      DD  DSN=&&Q1H{n:02d},'
                  'DISP=(OLD,DELETE)']
    return '\n'.join(lines)+'\n'


class IdentityPreparationTest(unittest.TestCase):
    def test_instrumented_asm_fail_closed_no_open(self):
        new = ident.instrument_asm(ASM)
        self.assertIn("L     15,=F'-6'\n         B     QCRET", new)
        self.assertIn('QIDSKIP  C     7,=F\'1\'', new)
        self.assertEqual(new.count('         RDJFCB ((2))'), 2)
        self.assertEqual(new.count('         BAL   14,QIDREAD'), 3)
        self.assertEqual(new.count('         BAL   14,QIDOUT'), 5)
        self.assertEqual(new.count('QCOPENIN OPEN  ((2),(INPUT))'), 1)
        self.assertTrue(ident.cards_are_valid(new))
        self.assertIn('         XC    0(176,7),0(7)', new)
        self.assertNotIn('IC    3,0(0,1)', new)
        self.assertIn("N     4,=X'0000000F'", new)
        for fragment in ('LA    6,118(6)',
                         'MVC   QIDMET(1),117(6)',
                         'MVC   QIDMET+1(1),100(6)',
                         'MVC   QIDMET+2(2),102(6)',
                         'MVC   QIDMET+4(2),104(6)'):
            self.assertIn(fragment, new)
        self.assertEqual(new.count('QIDPROB  CSECT'), 1)

    def test_bounded_separate_records_and_native_output_abi(self):
        src = ident.PROBE_CSECT
        self.assertIn('         EXTRN IOREPL,IOWRCH,IOSTAT', src)
        self.assertIn('ST    5,QIDWORK', src)
        self.assertIn("QIDWORK  DC    F'0'", src)
        self.assertNotIn('IODIAG', src)
        self.assertIn("         C     2,=F'72'\n         BH    QIDBAD", src)
        # The longest raw-hex record is 12 + 30*2 = 72 bytes;
        # the accepted primary buffer is 132 bytes.
        labels = {'RC': 'QIDRCB', 'NM0': 'QIDN0B',
                  'NM1': 'QIDN1B', 'VOL': 'QIDVLB',
                  'MET': 'QIDMTB'}
        sizes = []
        for kind, label in labels.items():
            found = re.search(
                rf"^{label}\s+DC\s+C'([^']*)',(\d+)C'0'$",
                src, re.MULTILINE)
            self.assertIsNotNone(found, kind)
            self.assertEqual(found.group(1), f'Q1I:Q00:{kind}=')
            byte_count = len(found.group(1)) + int(found.group(2))
            sizes.append(byte_count)
            self.assertIn(f'LA    1,{label}\n'
                          f'         LA    2,{byte_count}\n'
                          '         BAL   14,QIDOUT', src)
        self.assertEqual(sizes, [19, 56, 56, 72, 24])
        self.assertLessEqual(max(sizes), 72)
        self.assertLess(max(sizes), 132)
        out = src[src.index('QIDOUT   STM'):src.index('         LTORG')]
        order = ('L     15,=A(IOREPL)', 'BALR  14,15',
                 'LTR   15,15', 'BNZ   QIDBAD',
                 'L     5,QIDWORK', 'LA    7,10', 'L     15,=A(IOWRCH)',
                 'BALR  6,15', 'L     15,=A(IOSTAT)',
                 'BALR  14,15', 'LTR   15,15')
        position = 0
        for text in order:
            position = out.index(text, position) + len(text)
        self.assertIn("WTO   'Q1I OUTPUT ERROR'", out)

    def test_output_failure_aborts_remaining_queries(self):
        src = ident.PROBE_CSECT
        self.assertIn('XC    QIDERR(4),QIDERR', src)
        self.assertIn("ST    0,QIDERR", src)
        self.assertEqual(src.count("CLC   QIDERR(4),=F'0'"), 7)
        self.assertEqual(src.count('BNE   QIDBACK'), 6)
        self.assertEqual(src.count('BNE   QIDEXIT'), 2)
        self.assertEqual(src.count('BAL   14,QIDOUT'), 5)
        self.assertEqual(src.count('BAL   14,QIDREAD'), 3)
        # The first failed output cannot be followed by an NM0 read;
        # subsequent DD probes are guarded separately.
        self.assertRegex(src, r'BAL   14,QIDOUT\n'
                              r"         CLC   QIDERR\(4\),=F'0'\n"
                              r'         BNE   QIDBACK\n')
        self.assertEqual(src.count("L     15,=F'-6'"), 0)
        new = ident.instrument_asm(ASM)
        self.assertIn("L     15,=F'-6'", new)

    def test_jcl_edits_only_temporary_asmq(self):
        old = synthetic_deck()
        new = ident.instrument_deck(old, ASM)
        source = ident.instrument_asm(ASM)
        self.assertEqual(new.replace(source, ASM, 1), old)
        self.assertIn(ident.GO, new)
        self.assertIn(ident.WGO, new)
        self.assertNotIn('//             DCB=', new.split(ident.GO, 1)[1])
        self.assertTrue(ident.cards_are_valid(new))
        self.assertEqual(new.count('//SYSIN    DD  *'), 6)
        self.assertEqual(new.count('/*'), 8)

    def test_wrong_deck_and_duplicate_probes_rejected(self):
        old = synthetic_deck()
        with self.assertRaises(ValueError):
            ident.instrument_deck(old, ASM+'* mismatch\n')
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace('REGION=256K',
                                             'REGION=512K'), ASM)
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace(
                '//Q00      DD  DSN=&&Q1H00,DISP=(OLD,DELETE)',
                '//Q00      DD  DSN=&&Q1H00,DISP=(OLD,DELETE),\n'
                '//             DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)'), ASM)
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace('BCXREQ BCPLQSAM',
                                             'BCXREQ OTHER'), ASM)
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace('Q13DD JOB', 'FOO JOB'), ASM)
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace('//ASMQ ', '//ASMX '), ASM)
        with self.assertRaises(ValueError):
            ident.instrument_asm(ident.instrument_asm(ASM))
        with self.assertRaises(ValueError):
            ident.instrument_deck(old.replace(
                '//Q01      DD  DSN=&&Q1H01,DISP=(OLD,DELETE)',
                '//Q01      DD  DSN=FOO,DISP=SHR'), ASM)

    def test_paths_and_card_width_fail_closed(self):
        with self.assertRaises(ValueError):
            ident.under_workarea(Path('/tmp/untrusted.jcl'))
        with self.assertRaises(ValueError):
            ident.instrument_asm(ASM.replace('QSMCTRL  CSECT',
                                             'QSMCTRL  CSECT\t'))
        with self.assertRaises(ValueError):
            ident.validate_deck(synthetic_deck().replace(
                'DSN=&&Q1H00', 'DSN=FOOXYZ'))


if __name__ == '__main__':
    unittest.main()
