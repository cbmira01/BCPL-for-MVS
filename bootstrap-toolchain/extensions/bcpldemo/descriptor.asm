***********************************************************************
* BCPLDEMO BCEX V1: 48-BYTE HEADER + ONE 8-BYTE DISPATCHER EXPORT.
* NO DEPENDENCIES AND NO FINALIZER.  IEWL RELOCATES DMODISP.
***********************************************************************
DMODESC  CSECT
         ENTRY DMOBEG,DMOEND
         EXTRN DMODISP
DMOBEG   DS    0F
         DC    CL4'BCEX'
         DC    F'1',F'48',F'56'
         DC    CL8'BCPLDEMO'
         DC    F'1',F'0',F'1',F'0',F'0',F'0'
         DC    F'203',A(DMODISP)
DMOEND   EQU   *
         END   DMODESC
