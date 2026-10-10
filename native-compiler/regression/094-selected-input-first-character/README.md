# 094 — selected input first character from BCPIN

Status: **PENDING TK5**.

The fixture `input.records` is attached to the native GO step as
`//BCPIN DD DATA,DLM=ZZ`. The program calls FINDINPUT("BCPIN"),
SELECTINPUT(handle), and RDCH(), then passes the result to the
existing WRCH bootstrap output path. Expected output is `A`.

This first test exercises one named QSAM fixed-record input stream
only. A FINDINPUT failure prints 999 instead. Record boundaries,
newlines, repeated reads, EOF, UNRDCH, ENDREAD and alternative DD
names are outside this test's acceptance claim.
