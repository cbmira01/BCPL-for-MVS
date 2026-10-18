*===================================================================
* BCPLAPT -- TEMPORARY BCPL VECTOR AND CALL SERVICE
*
* APTOVEC (G!40) calls a supplied BCPL function with a
* temporary VEC N placed in the current stack workspace.
* R7 is the function entry address; R8 is N.
* Allocate N+1 words, adjust the next workspace, and call
* the function with the new vector pointer in R7.
* The vector is released automatically when this call returns.
* BCPLMAIN sets APLIMIT to the safe stack end. An invalid
* size or stack overflow branches to the STKOVFL handler.
*===================================================================
*
*------------------------------------------------------------------
* MODULE ENTRY
* Export the APTOVEC procedure and the limit word set by BCPLMAIN.
*------------------------------------------------------------------
BCPLAPT  CSECT
         ENTRY APTOVEC,APLIMIT
         EXTRN STKOVFL
*
*------------------------------------------------------------------
* APTOVEC(F,N) -- G!40
* Validate N and the available stack, form a temporary vector in
* the new frame, and call F with that vector and N.
*------------------------------------------------------------------
APTOVEC  STM   4,6,0(15)
         ST    10,12(15)
         LR    5,15
         BALR  10,0
         USING *,10
         LTR   8,8
         BM    APERROR
         C     8,APMAXN
         BH    APERROR
         LR    14,8
         SLL   14,2
         LA    14,20(14)
         LR    4,15
         AR    4,14
         LR    14,4
         LA    14,16(14)
         C     14,APLIMIT
         BH    APERROR
         LR    14,7
         LA    7,16(15)
         SRL   7,2
         LR    15,4
         LR    4,14
         L     10,12(5)
         BALR  6,4
         L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* BAD SIZE OR STACK OVERFLOW
* Transfer control to BCPLMAIN's STKOVFL handler.
*------------------------------------------------------------------
APERROR  L     4,=A(STKOVFL)
         BR    4
         LTORG
*
*------------------------------------------------------------------
* SIZE AND STACK BOUNDS
* APMAXN limits vector size. BCPLMAIN writes the safe stack end
* into APLIMIT.
*------------------------------------------------------------------
APMAXN   DC    F'16380'
APLIMIT  DC    F'0'
         DROP  10
         END   BCPLAPT
