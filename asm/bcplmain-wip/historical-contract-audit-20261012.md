# BCPLMAIN historical contract audit — stack and interface checkpoint

**Status:** Evidence-only; no assembler, PDS, or regression changes. Audit follows accepted G39 march (source regression 108; JOB 7333 AMAIN/IMAIN RC=0000; installed PDS 119/119; mixed mode 120/120). Those acceptance observations were supplied by the TK5 operator.

## Scope and source priority

Primary source: `richards-bcpltape/bcplib/bcpl/blib` (historical high-level implementations); `richards-bcpltape/sys3/bcpl/libhdr` (names/numbers); `richards-bcpltape/km10/bcplmac` (historical control-block definitions). Reconstruction source: `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag` and `30-control-data-and-end.asmfrag`. Prior repository audits: `libhdr-global-reconciliation-20261011.md`, `system-vector-global-audit-20261011.md`, `runtime-globals-45-56-57-investigation-20261011.md`, `g45-parms-historical-contract-20261011.md`, `docs/stack-check-contract.md`.

An interface declaration or BLIB source definition is not proof of a particular object member's export, and observed tests do not establish historical semantics beyond the asserted tests.

## Highest-priority contract: G54/G55/G56

| Item | Direct evidence / current state | Gap |
| --- | --- | --- |
| G54 STACKBASE | Published by reconstructed startup as `DYNWORK >> 2` (word pointer). Historical BLIB references STACKBASE. | Whether all original stack initialization and guard conventions are met |
| G55 STACKEND | Published as `DYNEND >> 2` (includes 256-byte provisional clearance above the 16,384-word safe region). | This value is used as a **metadata location** by historical STACKHWM, not just an extent |
| G56 STACKHWM | Historical BLIB defines `STACKHWM()`; `MAPSTORE()` calls it and reports stack utilization. | The reconstructed startup does not populate its required marker words or initialization pointer |
| MVS stack state | BCPLMAC `STKBASE`, `STKLIM`, `STKHIGH` record byte addresses; `INUM` is stack clearance. WIP has dynamic allocation and its own `STKLIM`. | Historical clearance policy and precise correspondence of published `STACKEND` to `STKHIGH` remain unproven |

### Literal historical BLIB algorithm and necessary invariants

At lines approximately 229–239 in `bcplib/bcpl/blib`, G56 uses (all offsets below are **BCPL words**):

```bcpl
LET Q = !(STACKEND-1)
UNLESS !(STACKEND-2) = EVENSTACK RESULTIS OVERFLOW
UNLESS STACKBASE <= Q < STACKEND RESULTIS OVERFLOW
UNLESS !Q = EVENSTACK RESULTIS UNSET
FOR P = Q-2 TO STACKBASE BY -2 DO
$( UNLESS P!1 = ODDSTACK  RESULTIS P+2
   UNLESS P!0 = EVENSTACK RESULTIS P+1 $)
```

Its constants are `EVENSTACK=#X5C40E2E3`, `ODDSTACK=#XC3D2405C`, `OVERFLOW=0`, `UNSET=1`.

**Direct consequences:**

1. `!(STACKEND-2)` must be the even sentinel; `!(STACKEND-1)` must hold a valid BCPL-word address Q into the stack region (initialization limit).
2. `!Q` must contain the even sentinel to distinguish an initialized region from `UNSET`.
3. Descending from Q-2, pairs are expected as `P!0=EVENSTACK`, `P!1=ODDSTACK`. The order of these tests and the return addresses `P+2` / `P+1` matter.
4. Q must be chosen so this alternating, even-aligned-with-respect-to-start layout is consistent down to STACKBASE and does not collide with the two STACKEND metadata words.
5. The function deliberately returns 0 for detected overflow/inconsistent top marker, 1 for uninitialized-marker condition, or a word-address high-water result when markers are disturbed. It does **not** return a raw byte count.
6. A caller that invokes STACKHWM while its own call frames are active may overwrite low stack sentinels; a useful regression must account for that and not assert a simplistic constant result.

**Current WIP mismatch:** `30-control-data-and-end.asmfrag` states stack marker initialization is unfinished. Startup fills G54/G55 but not the alternating stack sentinel pattern or two end metadata cells. Existing checked-entry tests validate a provisional safe boundary; they do not establish STACKHWM correctness. In particular, a zero-initialized or untouched GETMAIN region cannot satisfy the historical algorithm merely because its bounds are valid.

### Design questions requiring resolution before code

- What is the correct historical Q initialization limit and how does its placement relate to `INUM`, `STKLIM`, and `STKHIGH`? Do not infer it from the names alone.
- Is `STACKEND` intentionally at the one-past-allocation boundary, with the two preceding words reserved from active stack use? The algorithm assumes those slots are available for metadata. WIP's 256-byte headroom may make that possible, but it is only an architectural inference.
- Does the installed `OBJ(BLIB)` member export G56 as expected? The historical source says yes, but inspection of the installed object/trailer is a separate verification gate.
- What deterministic observable output and acceptable range can be asserted in a focused native regression without assuming an exact high-water word address across varying load placements?
- How should marker state be initialized in startup without overwriting the first live BCPL frame, and what invariant is needed when the stack approaches the reserved metadata?

## Other audited contract gaps (no new implementation)

| Interface / responsibility | What is established | Open issue / owner |
| --- | --- | --- |
| G39 FINDPARM | Accepted EXEC PARM memory-stream implementation, production installed; independent from QSAM input | Closed march; preserve behavior |
| G45 PARMS | Historical parameter-string global distinct from G39's stream descriptor | Representation, producer, storage lifetime unknown; no invented startup pointer |
| G57 environment marker | LIBHDR comment says global 57 set to OS or CMS | Data encoding and concrete consumer remain unknown |
| G6 SAVEAREA | WIP publishes R13 as word pointer | Historical save-area layout differs from provisional WIP; audit consumers before calling complete |
| G52/G53 LOADPOINT/ENDPOINT | WIP publishes main-module extent | Dynamic module/load-chain semantics absent |
| G7–G10 LOAD/UNLOAD | Named by LIBHDR and historic library structure | No verified callable loader contract |
| System vector R11 | Offset 0 return, +20 count, +40 FIN, +60 checked stack, +80 checked/count in WIP | Original bodies/counter semantics not recovered; current behavior regression-tested but not historically exact |
| Stream I/O | Multiple QSAM streams plus EXEC PARM pseudo-stream validated | Historical BSAM/BPAM/block/terminal interfaces largely unrecovered |
| Recovery | BCPLMAC names STAE/SPIE state; BLIB ABORT diagnoses stack faults | Native interrupt-to-ABORT bridge not reconstructed |
| External objects | Installed BCPLMAIN, BLIB, BCPLBYTE, BCPLAPT, BCPLMEM accepted by operational tests | Do not equate five production objects with the original multi-member library's complete interface |

## Recommended next bounded gate

**Evidence/probe before mutation.** Check the actual installed BLIB G56 symbol in IEWL listing or exported global trailer. Then build a test-local G56 probe that asks BLIB's STACKHWM for a result using current unmodified BCPLMAIN; capture actual behavior without calling it historically correct. Separately derive the marker layout and initialization bounds from BCPLMAC/BLIB sources. Only then propose a narrowly tested stack-marker initialization change, preserving the current stack limit, reserved headroom, and external object architecture.

**Non-goals:** No G45/G57 guessed representation, allocator redesign, new access methods, loader, STAE/SPIE implementation, or PDS installation in this audit.
