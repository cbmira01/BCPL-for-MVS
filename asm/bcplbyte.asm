***********************************************************************
* BCPLBYTE -- PROPOSED INDEPENDENT MACHINE-DEPENDENT BCPL SERVICE
*
* First object-module extraction from BCPLMAIN-WIP.
* Public entry symbols: GETBYTE and PUTBYTE (LIBHDR G85 and G86).
* No private BCPLMAIN storage is referenced.
*
* BCPL entry register contract:
* R5 current BCPL frame, R6 BCPL return address
* R7 pointer argument / return result
* R8 byte offset, R9 byte to write
* R4 restored from 0(R5), R0 and R1-R3 retained unchanged.
*
* This file is NOT yet used by normal regression linkage.
***********************************************************************
BCPLBYTE CSECT
         ENTRY GETBYTE,PUTBYTE
*
* GETBYTE(S,I) -> R7
* S is a BCPL word pointer; I is an unrestricted byte offset.
GETBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         SR    7,7
         IC    7,0(14)
         L     4,0(5)
         BCR   15,6
*
* PUTBYTE(S,I,BYTE): stores low eight bits of R9.
PUTBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         STC   9,0(14)
         L     4,0(5)
         BCR   15,6
         END   BCPLBYTE
