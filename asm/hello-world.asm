HELLO    CSECT
HELLO    AMODE 24
HELLO    RMODE 24
         STM   14,12,12(13)       SAVE CALLER REGISTERS
         BALR  12,0
         USING *,12

         OPEN  (PRINT,(OUTPUT))

         PUT   PRINT,MESSAGE

         CLOSE (PRINT)

         LM    14,12,12(13)       RESTORE CALLER REGISTERS
         SR    15,15              RETURN CODE = 0
         BR    14

MESSAGE  DC    CL80'HELLO, WORLD!'

PRINT    DCB   DDNAME=SYSPRINT,                                   X
               DSORG=PS,                                         X
               MACRF=PM,                                         X
               RECFM=F,                                          X
               LRECL=80

         END   HELLO

