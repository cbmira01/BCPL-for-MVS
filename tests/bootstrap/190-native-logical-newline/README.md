# 190 — Native logical newline

Compile with resident CAMBCOMP; link installed BOOT_OBJ including BLIB. Require both *N representations 10, ordinary EBCDIC A=193, input record delimiters/EOF, WRITEF, WRITES, NEWLINE and direct WRCH. IFOX/IEWL/GO then separate IFOX/IEWL/QSAM checker compare six full blank-padded FB132 records and exact EOF. Derived from DR.5 JOB 9504; first regular-suite execution and full supported production campaign PASS after CAMBBLD JOB 9925. No persistent writes.
