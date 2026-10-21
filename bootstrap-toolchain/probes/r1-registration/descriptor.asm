***********************************************************************
* R.1 TRIVIAL SERVICE BCEX V1.  ONE EXPORT, NO DEPENDENCIES.
***********************************************************************
R1DESC   CSECT
         ENTRY R1EXBEG,R1EXEND
         EXTRN R1DISP
R1EXBEG  DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'R1TEST'
         DC    F'1',F'0',F'1',F'0',F'0',F'0'
         DC    F'298',A(R1DISP)
R1EXEND  EQU   *
         END   R1DESC
