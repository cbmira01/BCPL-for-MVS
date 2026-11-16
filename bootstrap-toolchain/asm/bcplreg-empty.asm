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

* Every native application must link exactly one BCPLREG.
* This version 1 table deliberately selects zero optional
* packages and has no outstanding package requirements.
BCPLREG  CSECT
         ENTRY BCRGBEG,BCRGEND
* The fixed 28-byte header carries signature, version,
* header and total length, zero counts, and reserved zero.
* RGINIT validates the bounds up to BCRGEND at startup.
BCRGBEG  DS    0F
         DC    CL4'BCRG'
         DC    F'1',F'28',F'28',F'0',F'0',F'0'
BCRGEND  EQU   *
         END   BCPLREG
