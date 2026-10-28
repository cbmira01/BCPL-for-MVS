"""Offline Q.2 source-state regression tests; no IFOX or JES."""
from __future__ import annotations

from pathlib import Path
import re
import unittest

HERE = Path(__file__).resolve().parent
ASM = HERE / 'bcplqsam.asm'


def check_q2(asm: str) -> None:
    """Check structural ordering and invariants before native validation."""
    assert asm.count('QSMIO    CSECT') == 1
    assert asm.count('         GET   (2),(1)') == 1
    assert asm.count('         PUT   (2),(1)') == 1
    assert asm.count('         MVCL  4,6') == 2
    assert "QISTATES DC    16X'00'" in asm
    assert "QIPENDS  DC    16F'0'" in asm
    assert asm.count('         D     2,=F' + "'44'") == 3
    assert '         C     7,=F' + "'2'" in asm
    assert '         C     7,=F' + "'3'" in asm
    # Q.1 capability bits stay unchanged until actual native Q.2 PASS.
    assert asm.count('         LA    14,25') == 1
    # Snapshot each full 44-byte slot; Q.2 uses disjoint state arrays.
    assert 'QSSLOTS  DS    0F' in asm
    assert 'QISTATES DC    16X' + "'00'" in asm
    assert asm.index('QIPENDS  DC') < asm.index('QSSLOTS  DS')
    rd = asm.split('QSMIO    CSECT', 1)[1]
    rd = rd.split('QSMFIN   CSECT', 1)[0]
    for k in ('QIOEOD', 'QIOSYN', 'QICAPCK', 'QIOSHORT',
              'QIOEOF', 'QIOREADR', 'QIWRITE', 'QIOLEN',
              'QIORESER', 'QIOEXIT'):
        assert re.search(r'^' + k + r'\s', rd, re.M), k
    for k in ('BE    QIOEOF', 'BE    QICAPCK',
              'BL    QIOSHORT', 'BNE   QIOLEN'):
        assert k in rd
    assert rd.index("CLI   0(6),X'02'") < rd.index('BE    QIOEOF')
    assert rd.index('BE    QIOEOF') < rd.index("CLI   0(6),X'01'")
    assert rd.index("CLI   0(6),X'01'") < rd.index('BE    QICAPCK')
    assert rd.index('BE    QICAPCK') < rd.index('GET   (2),(1)')
    assert rd.index('GET   (2),(1)') < rd.index('\nQICAPCK ')
    assert rd.index('CR    3,5') < rd.index('BL    QIOSHORT')
    assert rd.index('BL    QIOSHORT') < rd.index('MVCL  4,6')
    assert rd.index('BNE   QIOLEN') < rd.rindex('MVCL  4,6')
    assert 'QIOEOD   L     6,QISTPTR' in rd
    assert 'MVI   0(6),X' + "'02'" in rd
    assert "L     15,=F'-1'" in rd
    assert "L     15,=F'-10'" in rd
    assert "L     15,=F'-12'" in rd
    assert "L     15,=F'-13'" in rd
    for i in range(16):
        assert re.search(
            rf'^QI{i:02d}\s+DCB\s+.*EODAD=E,SYNAD=QS$',
            asm, re.M)
        assert re.search(
            rf'^QO{i:02d}\s+DCB\s+.*SYNAD=QS$',
            asm, re.M)
    # Every IFOX source card stays within fixed-column budget.
    assert all(len(line) <= 71 and line.isascii() and '\t' not in line
               for line in asm.splitlines())


class Q2SourceRegression(unittest.TestCase):
    def test_current_source(self):
        check_q2(ASM.read_text(encoding='ascii'))

    def test_rejects_lost_eodad_and_synad(self):
        src = ASM.read_text(encoding='ascii')
        for symptom in ('EODAD=E,', ',SYNAD=QS'):
            with self.subTest(symptom=symptom):
                with self.assertRaises(AssertionError):
                    check_q2(src.replace(symptom, '', 1))

    def test_rejects_changed_retry_and_eof_order(self):
        src = ASM.read_text(encoding='ascii')
        for symptom in ('BE    QICAPCK', 'BE    QIOEOF',
                        'BL    QIOSHORT', 'BNE   QIOLEN'):
            with self.subTest(symptom=symptom):
                with self.assertRaises(AssertionError):
                    check_q2(src.replace(symptom, 'B     QIOEXIT', 1))

    def test_rejects_unverified_advertising(self):
        src = ASM.read_text(encoding='ascii')
        with self.assertRaises(AssertionError):
            check_q2(src.replace('LA    14,25', 'LA    14,31'))

    def test_rejects_copy_or_stage_regression(self):
        src = ASM.read_text(encoding='ascii')
        for symptom in ('         MVCL  4,6', "QIPENDS  DC    16F'0'"):
            with self.subTest(symptom=symptom):
                with self.assertRaises(AssertionError):
                    check_q2(src.replace(symptom, '', 1))


if __name__ == '__main__':
    unittest.main()
