***********************************************************************
* R2TESTB - SECOND INDEPENDENT R.2 TEST-ONLY DISPATCHER (G!299).
* R7 OPCODE/RESULT, R8 BCPL WORD POINTER, R9 WORD CAPACITY.
* QUERY V1: 8 WORDS, API 3.2, BITMAP 5, APPENDED WORDS 77/99.
* OPS 1 AND 3 RETURN 201 AND 203; ALL OTHER OPS UNSUPPORTED.
***********************************************************************
R2BDISP  CSECT
         ENTRY R2BDISP
         USING R2BDISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   OTHEROP
         LTR   8,8
         BNZ   QPTR
         LTR   9,9
         BNZ   BADARG
         LA    7,8
         BCR   15,11
QPTR     LTR   9,9
         BM    BADARG
         C     9,=F'8'
         BL    SHORT
         SLL   8,2
         MVC   0(32,8),BCQD
         LA    7,8
         BCR   15,11
OTHEROP  C     7,=F'1'
         BE    OPONE
         C     7,=F'3'
         BE    OPTHRE
         L     7,=F'-2'
         BCR   15,11
OPONE    LA    7,201
         BCR   15,11
OPTHRE   LA    7,203
         BCR   15,11
SHORT    L     7,=F'-1'
         BCR   15,11
BADARG   L     7,=F'-3'
         BCR   15,11
BCQD     DC    F'1',F'3',F'2',F'8',F'5',F'0',F'77',F'99'
         LTORG
         END   R2BDISP
