*
* M4.3 private counter query through EXISTING regression G!151.
* IOACCT is present only in temporary instrumented BCPLIO.
NATIVEAD CSECT
         EXTRN IOACCT
         STM   4,8,0(15)
         LR    5,15
         LR    1,7
         L     15,=V(IOACCT)
         BALR  14,15
         LR    7,15
         BCR   15,11
         LTORG
         END
