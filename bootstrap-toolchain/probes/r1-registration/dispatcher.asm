***********************************************************************
* R.1 TEST SERVICE: BCPL QUERY V1, ONE OPTIONAL G!298 DISPATCHER.
* NATIVE BCPL ABI R7=OPCODE/RESULT, R8=POINTER, R9=CAPACITY.
***********************************************************************
R1DISP   CSECT
         ENTRY R1DISP
         USING R1DISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   UNSUP
         LTR   8,8
         BNZ   HASPTR
         LTR   9,9
         BNZ   BADARG
         LA    7,6
         BCR   15,11
HASPTR   LTR   9,9
         BM    BADARG
         C     9,=F'6'
         BL    TOOSMALL
         SLL   8,2
         LA    14,1
         ST    14,0(8)
         ST    14,4(8)
         SR    14,14
         ST    14,8(8)
         LA    14,6
         ST    14,12(8)
         LA    14,1
         ST    14,16(8)
         SR    14,14
         ST    14,20(8)
         LA    7,6
         BCR   15,11
UNSUP    C     7,=F'1'
         BNE   BADOP
         LA    7,101
         BCR   15,11
BADOP    L     7,=F'-2'
         BCR   15,11
TOOSMALL L     7,=F'-1'
         BCR   15,11
BADARG   L     7,=F'-3'
         BCR   15,11
         LTORG
         END   R1DISP
