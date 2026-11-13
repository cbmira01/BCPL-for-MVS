***********************************************************************
* CO1SW - isolated native context-transfer candidate, NOT production
* R2 = address of outgoing 16-word register image
* R1 = address of incoming 16-word register image
* R0 = BCPL result value delivered to incoming R7
* R6 is the continuation set by the caller's BALR 6,4.
* This test-only convention is NOT the approved CHANGECO public ABI.
***********************************************************************
CO1SW    CSECT
         ENTRY CO1SW
         STM   0,15,0(2)          SAVE OUTGOING R0-R15
         ST    0,28(1)            DELIVER VALUE TO INCOMING R7
         LM    0,15,0(1)          RESTORE INCOMING R0-R15
         BCR   15,6              RESUME SAVED CONTINUATION
         END
