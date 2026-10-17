# 140 — M4.3.2a terminal resource accounting

STAGED, NOT EXECUTED. Test-only BCPLIO asserts zero DHEAD/HHEAD and balanced 32/268/16-byte GETMAIN/FREEMAIN and dynamic QSAM OPEN/CLOSE counters after IODRAIN. On mismatch it intentionally executes an invalid opcode (S0C1), so normal completion is required for PASS. Reuses the proven logical program and expected output fixtures of regression 128. No runtime object installation or new BCPL global.
