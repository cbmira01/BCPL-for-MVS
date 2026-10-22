***********************************************************************
* BCPLDEMO: PERMANENT OPTIONAL PACKAGE, PUBLIC DISPATCHER G!203.
* DEMOSVC IS THE BCPL GLOBAL NAME; DMODISP IS THE IEWL ENTRY SYMBOL.
* NATIVE BCPL ABI: R7 OPCODE/RESULT; R8 VECTOR; R9 WORD CAPACITY.
* BCPL POINTERS ARE WORD ADDRESSES; SHIFT BY 2 ONLY AFTER VALIDATION.
* EXAMPLE IS STATELESS: NO INIT AND NO FINALIZER.
***********************************************************************
DMODISP  CSECT
         ENTRY DMODISP
         USING DMODISP,4
         STM   4,9,0(15)
         LR    5,15
         LTR   7,7
         BNZ   OTHEROP
*
* OPCODE 0: SHARED QUERY V1.  (0,0,0) IS THE SIZE INQUIRY.
* REJECT BAD PAIRS BEFORE CAPACITY CHECK; NEVER PARTIALLY WRITE.
*
         LTR   8,8
         BNZ   QPTR
         LTR   9,9
         BNZ   BADARG
         LA    7,6
         BCR   15,11
QPTR     LTR   9,9
         BM    BADARG
         C     9,=F'6'
         BL    SHORT
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
*
* OPCODE 1: GETVALUES(VEC, CAPACITY); THREE BCPL FULLWORDS.
* RESULT IS 3 OR -1 TOO SMALL OR -3 BAD ARGUMENT.
* CONTENTS 10,20,30 ARE FIXED SAMPLE DATA, NOT POINTERS.
*
OTHEROP  C     7,=F'1'
         BNE   BADOP
         LTR   8,8
         BZ    BADARG
         LTR   9,9
         BM    BADARG
         C     9,=F'3'
         BL    SHORT
         SLL   8,2
         LA    14,10
         ST    14,0(8)
         LA    14,20
         ST    14,4(8)
         LA    14,30
         ST    14,8(8)
         LA    7,3
         BCR   15,11
BADOP    L     7,=F'-2'
         BCR   15,11
SHORT    L     7,=F'-1'
         BCR   15,11
BADARG   L     7,=F'-3'
         BCR   15,11
         LTORG
         END   DMODISP
