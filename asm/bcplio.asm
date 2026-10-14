***********************************************************************
* BCPLIO - M2.0 D1 INDEPENDENT I/O MODULE SKELETON
*
* PURPOSE: Establish a separate I/O control CSECT and its native
*          lifecycle interface prior to moving stream services.
* CSECT:   BCPLIO.  ENTRY: IOINIT, IOFIN (native-private only).
* EXTRN:   None.  No BCPL global vector entries are supplied yet.
*
* IOINIT:  R1 = original MVS EXEC parameter-list address as saved
*          by BCPLMAIN. R14 = return linkage. Saves pointer locally.
* IOFIN:   R14 = return linkage. Clears initialization flag/pointer.
* BOTH:    Preserve R0-R9, R11-R15. R10 is clobbered for the
*          module's private base. Caller must save R10 if live.
*          Condition code not specified.
* STORAGE: Local static singleton state. Not reentrant.
* IOINIT/IOFIN perform NO OPEN, PUT, GET or CLOSE in D1.
*
* THIS MODULE IS NOT YET LINKED OR CALLED BY BCPLMAIN.
* Subsequent D2/D3 work migrates QSAM/DCBs and stream handlers and
* only then redirects G entries and BCPLMAIN startup/shutdown.
* Provisional reconstruction, not a recovered Cambridge module.
***********************************************************************
BCPLIO   CSECT
         ENTRY IOINIT,IOFIN
*
IOINIT   BALR  10,0
         USING *,10
         ST    1,IOPARM
         MVI   IOACTIVE,X'01'
         BR    14
         DROP  10
*
IOFIN    BALR  10,0
         USING *,10
         MVI   IOACTIVE,X'00'
         XC    IOPARM(4),IOPARM
         BR    14
         DROP  10
*
         DS    0F
IOPARM   DC    F'0'
IOACTIVE DC    X'00'
         END   BCPLIO
