*
* M4.3 private counter query through EXISTING regression G!151.
* IOACCT is present only in temporary instrumented BCPLIO.
NATIVEAD CSECT
         EXTRN IOACCT
         STM   4,8,0(15)
         LR    5,15
         LR    1,7
* IFOX needs explicit base addressing for the external V literal.
* R10 is scratch by the private IOACCT convention.
         BALR  10,0
         USING *,10
         L     15,=V(IOACCT)
         BALR  14,15
         LR    7,15
         BCR   15,11
         DROP  10
         LTORG
         END
