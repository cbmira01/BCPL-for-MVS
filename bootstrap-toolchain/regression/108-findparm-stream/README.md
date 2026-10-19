# Regression 108 — native EXEC PARM pseudo-stream

G39 FINDPARM now returns a dedicated in-memory stream backed by the MVS
GO-step EXEC PARM parameter field, not the BCPIN DD. The runner supplies
`exec-parm.txt` containing `P`, and independently supplies the BCPIN
fixture `X`; the application must output `P`.

Both the source-runtime and installed-runtime PDS regression preparation
paths recognize `exec-parm.txt`. This is **pending TK5 verification**:
IFOX, IEWL, GO, and installed object member deployment must be proven
on the operator's system. G45 PARMS is unchanged.
