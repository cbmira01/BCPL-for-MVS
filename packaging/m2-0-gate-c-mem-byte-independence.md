# M2.0 Gate C — BCPLMEM / BCPLBYTE Independence

**Status: ACCEPTED — Gate C closed (14 October 2026).**
Date: 14 October 2026.

## Source audit

**BCPLMEM:** `asm/bcplmem.asm` is a standalone BCPLMEM CSECT exporting GETVEC (G87), FREEVEC (G88) and private native MEMDRAIN, MEMBIND, MEMSTAT. Its state is locally owned: VECLIST, counters, VECPUB pointer, save areas and vector descriptors. It is deliberately a nonreentrant singleton. GETVEC/FREEVEC use BCPL R5/R6/R7 convention and restore R4; MEMDRAIN/MEMBIND use private R14 linkage. MEMBIND receives a *published slot address* (G6!48) from BCPLMAIN instead of resolving a private BCPLMAIN storage label. BCPLMAIN installs external GETVEC/FREEVEC into G87/G88, calls MEMBIND during bootstrap and MEMDRAIN then MEMBIND(0) on cleanup. This is a proper service boundary, not a candidate for another M2.0 refactoring.

**BCPLBYTE:** `asm/bcplbyte.asm` owns a separate BCPLBYTE CSECT with GETBYTE and PUTBYTE. It has no EXTRN, private state, allocator dependency or BCPLMAIN private-label dependency. BCPL registers: R7 word-pointer, R8 byte offset, R9 stored byte, R5 frame, R6 linkage; GETBYTE returns unsigned byte in R7 and PUTBYTE stores low 8 bits. Both restore R4 from 0(R5). Its source header's old statement claiming it is not used by normal regression linkage is stale and should be cleaned up in Gate E documentation review.

**Discovered Gate C defect:** prior canonical `asm/bcplmain.asm` installed `=A(GETBYTE)`/`=A(PUTBYTE)` into G85/G86, but also defined local GETBYTE and PUTBYTE labels. Therefore the addresses resolved **locally**, even when a distinct BCPLBYTE object was included in the link-edit. Presence of a separate CSECT was not proof of actual dispatch. The Gate C change declares `EXTRN GETBYTE,PUTBYTE` and removes the two duplicate local bodies. G85/G86 now require external BCPLBYTE resolution and their BCPL-facing contracts remain unchanged. This is a service-ownership correction, not new functionality. Git commit `03633ddbc08c65ea52f2a42110d21650266b5f07`.

## Resident DEVOBJ acceptance procedure

1. Synchronize **only** `SOURCE(BCPLMAIN)` from canonical `asm/bcplmain.asm`, verify readback of external references and absence of local label definitions.
2. Rebuild only `DEVOBJ(BCPLMAIN)` using resident `JCL(BLDDEVN)`; require assembler and install CC 0000. BCPLMEM and BCPLBYTE objects from previously accepted independent M1.8 builds remain unchanged.
3. Run focused installed DEVOBJ tests for byte access (particularly BCPL byte/string operation paths) and memory lifecycle (GETVEC/FREEVEC; accepted earlier tests 27, 28, 30, 123). Record exact tests and outputs.
4. Inspect IEWL `MAP,XREF` from at least one relevant installed DEVOBJ application, verifying GETBYTE/PUTBYTE resolve to distinct BCPLBYTE CSECT and GETVEC/FREEVEC/MEMBIND/MEMDRAIN to BCPLMEM; no unresolved symbols or accidental BCPLMAIN local definitions.
5. No production OBJ promotion. Full 124-case panel is reserved for Gate F.

## Execution and linkage evidence — accepted 14 October 2026

- Operator synchronized only `SOURCE(BCPLMAIN)`: remove JOB 1274, compress JOB 1275, put JOB 1276, readback JOB 1277. The readback shows `EXTRN GETBYTE,PUTBYTE`; no BCPLMAIN local GETBYTE/PUTBYTE definitions survived.
- Resident `BLDDEVN` launcher JOB 1279 / payload **JOB 1280** rebuilt `DEVOBJ(BCPLMAIN)`. IFOX00 ASMMMAIN RC=0000, IEBGENER PUTMAIN RC=0000; zero flagged assembler statements and zero highest severity. Assembler External Symbol Dictionary contains `GETBYTE ER 0007`, `PUTBYTE ER 0008`.
- Focused installed DEVOBJ execution: 04 (JOB 1283), 27 (1285), 28 (1287), 29 (1289), 30 (1291), 069 (1293), 123 (1295). **7 PASS, 0 FAIL, 0 SKIP**. For all seven JES jobs: ASMAP IFOX00 RC=0000, LKED IEWL RC=0000 and GO RC=0000.
- Each of the seven IEWL maps explicitly includes `OBJ(BCPLMAIN)`, `OBJ(BCPLBYTE)`, `OBJ(BCPLAPT)`, `OBJ(BCPLMEM)`, `OBJ(BLIB)` as independent members. Their cross-reference tables demonstrate that `GETBYTE` and `PUTBYTE` resolve **only to BCPLBYTE**, and `GETVEC`, `FREEVEC`, `MEMDRAIN`, `MEMBIND` resolve **to BCPLMEM**, with BCPLMAIN references.
- Representative JOB 1283 link-edit map: `BCPLBYTE` starts X'1638', length **X'26'**; GETBYTE X'1638', PUTBYTE X'164C'. `BCPLMEM` starts X'16D0', length **X'2AC'**; GETVEC X'16D0', FREEVEC X'17AE', MEMDRAIN X'1856', MEMBIND X'18B6'. The cross-reference row assigns GETBYTE/PUTBYTE to BCPLBYTE and allocation/lifecycle symbols to BCPLMEM. In all other jobs the addresses differ by relocation but the resolution pattern is identical.
- Independent BCPLMEM/BCPLBYTE source state and historical M1.8 rebuild provenance are unchanged. No production `HERC02.BCPL.OBJ` write is requested or claimed.

**Gate C ACCEPTED**. Both service families are independently linked and operational in DEVOBJ. Gate D is next: assess and select first substantial extraction (BCPLIO versus BCPLSTACK), retaining narrow implementation scope. M2.0 as a whole remains open and the full native regression panel is reserved for Gate F.
