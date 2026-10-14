HELLO    CSECT
         STM   14,12,12(13)       SAVE CALLER REGISTERS
         BALR  12,0               ESTABLISH BASE REGISTER
         USING *,12

         LA    11,SAVEAREA         ADDRESS OUR SAVE AREA
         ST    13,4(11)            BACKWARD CHAIN TO CALLER
         ST    11,8(13)            FORWARD CHAIN FROM CALLER
         LR    13,11               ESTABLISH OUR SAVE AREA

         OPEN  (PRINT,(OUTPUT))
         PUT   PRINT,MESSAGE
         CLOSE (PRINT)

         L     13,4(13)            RESTORE CALLER SAVE AREA
         LM    14,12,12(13)        RESTORE CALLER REGISTERS
         SR    15,15               RETURN CODE = 0
         BR    14                  RETURN TO CALLER

         DS    0F
SAVEAREA DS    18F

MESSAGE  DC    CL80'HELLO, WORLD!'

PRINT    DCB   DDNAME=SYSPRINT,DSORG=PS,MACRF=PM,RECFM=F,LRECL=80

         END   HELLO

