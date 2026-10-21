* R.0 TEST ONLY: BCPL-ABI G!151 FUNCTION, NO STATE MODIFICATION.
* Compare G!76 after real BCPLMAIN startup with BLIB export trailer.
* The installed BLIB object supplies the independently relocated data.
R0CK76   CSECT
         ENTRY R0CK76
         EXTRN BLIB
         STM   4,8,0(15)
         LR    5,15
         BALR  10,0
         USING *,10
         L     8,=A(BLIB)
         LH    9,10(8)
         LTR   9,9
         BNP   R0FAIL
         C     9,=F'16384'
         BNL   R0FAIL
         AR    8,9
         LA    9,512
R0SCAN   AH    8,=H'-8'
         L     4,4(8)
         LTR   4,4
         BZ    R0FAIL
         CLC   0(4,8),=F'304'
         BE    R0FOUND
         BCT   9,R0SCAN
R0FAIL   LA    7,8
         BCR   15,11
R0FOUND  L     7,304(12)
         CR    7,4
         BNE   R0FAIL
         SR    7,7
         BCR   15,11
         DROP  10
         LTORG
         END   R0CK76
