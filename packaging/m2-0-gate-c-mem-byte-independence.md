# M2.0 Gate C — BCPLMEM / BCPLBYTE Independence

**Status: canonical BCPLBYTE integration committed; MVS candidate acceptance pending.**
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

**Disposition:** source-boundary correction committed; independent MVS verification pending. Gate C cannot be closed solely on source audit or historic M1.8 tests.
