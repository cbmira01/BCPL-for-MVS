***********************************************************************
* R.2 TEST-ONLY EXTENSION B: BCEX V1, 1 GLOBAL, NO DEPENDENCIES.
* G!299 IS A TEST FIXTURE, NOT A PERMANENT PUBLIC ALLOCATION.
***********************************************************************
R2BDSC   CSECT
         ENTRY R2BBEG,R2BEND
         EXTRN R2BDISP
R2BBEG   DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'R2TESTB'
         DC    F'3',F'2',F'1',F'0',F'0',F'0'
         DC    F'299',A(R2BDISP)
R2BEND   EQU   *
         END   R2BDSC
