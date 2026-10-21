***********************************************************************
* R.1 SELECTED SERVICE: APP-SPECIFIC REGISTRY FOR R1TEST.
* G!298 IS TEST-LOCAL; NOT A GLOBAL NUMBER REGISTRY ALLOCATION.
***********************************************************************
BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
         EXTRN R1EXBEG,R1EXEND
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'44',F'1',F'1',F'0'
         DC    A(R1EXBEG),A(R1EXEND)
         DC    CL8'R1TEST'
BCRGEND  EQU   *
         END   BCPLREG
