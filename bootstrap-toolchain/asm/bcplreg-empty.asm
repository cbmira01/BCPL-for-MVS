***********************************************************************
* R.1 EMPTY APPLICATION-SPECIFIC BCPLREG TABLE.  BCRG VERSION 1.
* INCLUDE EXACTLY ONE BCPLREG TABLE WITH EVERY BCPL APPLICATION.
***********************************************************************
BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'28',F'0',F'0',F'0'
BCRGEND  EQU   *
         END   BCPLREG
