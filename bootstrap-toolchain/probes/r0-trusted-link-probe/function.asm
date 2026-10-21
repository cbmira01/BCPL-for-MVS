***********************************************************************
* R.0 TEST-ONLY SEPARATELY LINKED EXECUTABLE ENTRY/HANDLER ADDRESS.
* NO HOOK OR EXPORT IS EVER CALLED BY THE VALIDATOR.
***********************************************************************
R0AFUN   CSECT
         ENTRY R0FUNC,R0FIN
R0FUNC   BR    14
R0FIN    BR    14
         END   R0AFUN
