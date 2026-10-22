***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLREG (EMPTY)
*
* Empty application-specific BCRG version-1 table.
* Selects zero optional packages and has zero requirements.
*
* LINKAGE:
* Link exactly one BCPLREG table per application.
* Select a different BCRG table when extensions are required.
* The generic registrar is implemented in BCPLRGS.
***********************************************************************

BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'28',F'0',F'0',F'0'
BCRGEND  EQU   *
         END   BCPLREG
