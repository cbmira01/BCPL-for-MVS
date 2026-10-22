***********************************************************************
* R.2 BCPLDEMO-ONLY BCPLREG.  APP REQUIRES THIS SELECTED PACKAGE.
* SOURCE/IEWL SELECTS DMOBEG/DMOEND; GLOBALS ARE NOT APP TRAILER.
***********************************************************************
BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
         EXTRN DMOBEG,DMOEND
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'44',F'1',F'1',F'0'
         DC    A(DMOBEG),A(DMOEND)
         DC    CL8'BCPLDEMO'
BCRGEND  EQU   *
         END   BCPLREG
