***********************************************************************
* R.0 TEST ONLY: CONVENTIONAL ASSEMBLER FINALIZER CALL TARGETS.
* R1 POINTS TO: MODE, STOPCODE, TRACEPTR, FAILURE MASK.
* R15 RETURNS 0 OR 8; RESTORE CALLER R2-R12 AND R13.
***********************************************************************
R0HOOK   CSECT
         ENTRY R0FA,R0FB
R0FA     STM   14,12,12(13)
         LR    12,15
         USING R0FA,12
         LA    11,SAVEA
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         L     2,8(1)
         L     3,0(2)
         LA    4,4(2)
         AR    4,3
         MVI   0(4),C'A'
         LA    3,1(3)
         ST    3,0(2)
         L     4,12(1)
         N     4,=F'2'
         SR    15,15
         LTR   4,4
         BZ    RETURNA
         LA    15,8
RETURNA  L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         DS    0F
SAVEA    DS    18F
R0FB     STM   14,12,12(13)
         LR    12,15
         DROP  12
         USING R0FB,12
         LA    11,SAVEB
         ST    13,4(11)
         ST    11,8(13)
         LR    13,11
         L     2,8(1)
         L     3,0(2)
         LA    4,4(2)
         AR    4,3
         MVI   0(4),C'B'
         LA    3,1(3)
         ST    3,0(2)
         L     4,12(1)
         N     4,=F'1'
         SR    15,15
         LTR   4,4
         BZ    RETURNB
         LA    15,8
RETURNB  L     13,4(13)
         LM    14,14,12(13)
         LM    0,12,20(13)
         BR    14
         LTORG
         DS    0F
SAVEB    DS    18F
         END   R0HOOK
