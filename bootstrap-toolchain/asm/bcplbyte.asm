***********************************************************************
* BCPL FOR MVS 3.8 RECONSTRUCTION - BCPLBYTE
*
* Core Runtime byte access using native System/370 code.
* GETBYTE(S,I) reads a byte; PUTBYTE(S,I,B) writes one.
*
* CALLING CONVENTION:
* BCPL pointer S is word-addressed, converted to bytes.
* R7 holds pointer/result, R8 offset, R9 write byte.
* R5 is the BCPL frame, R6 return linkage.
***********************************************************************

* BCPLMAIN installs these byte primitives at G!85 and G!86.
***********************************************************************
BCPLBYTE CSECT
         ENTRY GETBYTE,PUTBYTE
*
* GETBYTE(S,I) -> R7
* S is a BCPL word pointer; I is an unrestricted byte offset.
* GETBYTE(S,I) returns byte 0..255 through R7. S is a
* BCPL word pointer; I counts bytes from that address.
* The caller must provide a valid readable address and offset.
GETBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         SR    7,7
         IC    7,0(14)
         L     4,0(5)
         BCR   15,6
*
* PUTBYTE(S,I,BYTE): stores low eight bits of R9.
* PUTBYTE(S,I,B) writes the low eight bits of R9 only.
* Storage bounds and writability belong to the caller.
* Neither primitive translates the contents as characters.
PUTBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         STC   9,0(14)
         L     4,0(5)
         BCR   15,6
         END   BCPLBYTE
