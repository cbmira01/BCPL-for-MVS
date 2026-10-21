* R.0 TEST ONLY: CHECK REAL G!150 AT START WITHOUT ALTERING IT.
* R0MARK IS THE RELOCATED APPLICATION-DECLARED G!150 OWNER.
* R0CK15 IS THE TEST-LOCAL G!151 INSPECTOR: OP 0 VALIDATES;
* OP 1 RETURNS ACTUAL G!150; OP 2 RETURNS R0MARK ADDRESS.
* BLIB EXPORT TRAILER MUST NOT PROVIDE ANOTHER G!150 OWNER.
R0O150   CSECT
         ENTRY R0MARK,R0CK15
         EXTRN BLIB
R0MARK   BCR   15,6
R0CK15   STM   4,8,0(15)
         LR    5,15
         BALR  10,0
         USING *,10
         C     7,=F'1'
         BE    R0ACT
         C     7,=F'2'
         BE    R0APPV
         LTR   7,7
         BNZ   R0FAIL
         L     7,600(12)
         L     8,=A(R0MARK)
         CR    7,8
         BE    R0FAIL
         C     7,=X'C7D3F258'
         BE    R0FAIL
* Scan the independently linked installed BLIB trailer, bounded.
         L     8,=A(BLIB)
         LH    9,10(8)
         LTR   9,9
         BNP   R0FAIL
         CH    9,=H'16384'
         BNL   R0FAIL
         LR    4,8
         LA    4,16(4)
         AR    8,9
         LA    9,512
R0SCAN   AH    8,=H'-8'
         CR    8,4
         BL    R0FAIL
         L     7,4(8)
         LTR   7,7
         BZ    R0SENT
         L     7,0(8)
         C     7,=F'600'
         BE    R0FAIL
         C     7,=F'4'
         BL    R0FAIL
         C     7,=F'2796'
         BH    R0FAIL
         TM    3(8),X'03'
         BNZ   R0FAIL
         BCT   9,R0SCAN
         B     R0FAIL
R0SENT   L     7,0(8)
         C     7,=F'4'
         BL    R0FAIL
         C     7,=F'2796'
         BH    R0FAIL
         TM    3(8),X'03'
         BNZ   R0FAIL
         SR    7,7
         BCR   15,11
R0ACT    L     7,600(12)
         BCR   15,11
R0APPV   L     7,=A(R0MARK)
         BCR   15,11
R0FAIL   LA    7,8
         BCR   15,11
         DROP  10
         LTORG
         END   R0O150
