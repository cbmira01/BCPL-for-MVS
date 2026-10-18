*===================================================================
* BCPLBYTE -- BYTE ACCESS TO BCPL WORD STORAGE
*
* GETBYTE (G!85) reads one unsigned byte.
* PUTBYTE (G!86) stores the low eight bits of its value.
* R7 carries the BCPL word pointer and returns the result.
* R8 is the byte offset; PUTBYTE also uses R9 for the value.
* Byte address = (word pointer * 4) + byte offset.
* R5 is the current workspace; R6 is the return address.
* Restore R4 from 0(R5) before return. R0-R3 stay unchanged.
* No BCPLMAIN private storage is needed.
*===================================================================
*
*------------------------------------------------------------------
* MODULE ENTRY
* Expose independent byte-access routines to the runtime linker.
*------------------------------------------------------------------
BCPLBYTE CSECT
         ENTRY GETBYTE,PUTBYTE
*
*------------------------------------------------------------------
* GETBYTE(S,I) -- G!85
* Shift the BCPL word pointer S by two, add byte offset I, and load
* one unsigned byte into R7.
*------------------------------------------------------------------
GETBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         SR    7,7
         IC    7,0(14)
         L     4,0(5)
         BCR   15,6
*
*------------------------------------------------------------------
* PUTBYTE(S,I,B) -- G!86
* Compute the same byte address and store the low byte of R9.
*------------------------------------------------------------------
PUTBYTE  LR    14,7
         SLL   14,2
         AR    14,8
         STC   9,0(14)
         L     4,0(5)
         BCR   15,6
         END   BCPLBYTE
