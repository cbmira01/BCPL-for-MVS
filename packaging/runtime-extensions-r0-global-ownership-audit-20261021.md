# Milestone Runtime Extensions — R.0 application/BLIB/Core Runtime ownership audit

**Date:** 21 October 2026. **March:** R.0 — Evidence and contract (open).
**Scope:** Git-source inventory plus actual application/BLIB exported
slots from JOB 2197 and installed-runtime G!76 precedence from JOB 2199.
This is still **not** a complete effective owner ledger, approved
slot-waiver implementation, or executable package registrar.

Source authority: [Global Number Registry](global-number-registry.md),
[historical LIBHDR](../richards-bcpltape/sys3/bcpl/libhdr),
[canonical bootstrap BCPLMAIN](../bootstrap-toolchain/asm/bcplmain.asm),
[reconstructed BLIB source](../cambridge-compiler/source/blib.bcpl),
[prior G1–G99 source reconciliation](../bootstrap-toolchain/asm/bcplmain-wip/libhdr-global-reconciliation-20261011.md),
and [direct native-write inventory](runtime-extensions-r0-native-global-owner-inventory-20261020.md).
The `cambridge-compiler/asm/bcplmain.asm` file is a **different
compiler target**, not substituted for the bootstrap runtime audited here.

**Decision E is now owner-approved** under the
[R.0 owner ABI record](runtime-extensions-r0-owner-abi-decisions.md):
this effective-ledger and transactional-collision policy is required,
while actual application/BLIB trailer decoding and verified legacy
exceptions remain incomplete. This approval does not turn a
source-derived candidate into measured executable evidence.

**New actual MVS evidence:** [JOBs 2196–2197](runtime-extensions-r0-trailer-job-2197-evidence-20261021.md)
verified the relocated exports of a sample application (**G!1**) and
installed `BOOT_OBJ(BLIB)` (**21 globals**). No application/BLIB
collision was observed. BLIB's only overlap with source-derived
Core Runtime direct stores is **G!76**. JOB 2197 did not execute
`BCPLMAIN`; a subsequent [actual-runtime JOB 2199
probe](runtime-extensions-r0-g76-job-2199-evidence-20261021.md)
**PASSED** and established the BLIB-present G!76 precedence at START.
The BLIB-absent fallback remains untested.

## Current actual startup writer order

| Stage | Source location in canonical BCPLMAIN | Observed action / consequence |
| --- | --- | --- |
| 1 | `GINIT`, about lines 666–675 | G!0 = 699; paint G!1–699 with `X'C7D3F000'+4*N` sentinel |
| 2 | `MODEND/GSCAN/GINST`, about 613–620 and 677–706 | Read current application's compiler-generated export trailer and **write each `(4*N,address)` pair** into G, without recording ownership |
| 3 | `GIDONE/BLIMP`, about 710–725 | Resolve explicitly linked `BLIB` prefix/trailer and install its exports, possibly overwriting an application writer |
| 4 | Startup native writes, about 730–820 | Set core services/metadata. Preserve imported G!76 when present; otherwise install `WRITEST` fallback |
| 5 | `IOINIT`/`IOBIND` then `START`, about 825–858 | Initialize stream service and enter application; **no generic BCPLREG stage currently exists** |

**Important:** The application and BLIB scans use a trailer sentinel
and maximum-global checks, **not** an independently trusted
begin/end descriptor extent or duplicate-owner ledger. An observed
final non-sentinel value cannot reveal earlier overridden writers.
Never infer that a header's named global is installed solely from its
`GLOBAL` declaration.

## Concrete direct runtime owners

This is an exhaustive list of the **explicit startup stores to G**
visible in this reviewed `BCPLMAIN`, not an exhaustive inventory
of indirect writes by all runtime modules:

| G! numbers | Observed owning function or metadata |
| --- | --- |
| 0 | Vector-extent metadata, 699 (not callable) |
| 6, 52, 53, 54, 55 | BCPLMAIN save-area and program/stack-extent metadata |
| 11, 12, 13, 14, 15, 16, 17 | BCPLIO entry addresses set by BCPLMAIN |
| 30 | `STOPENT` in BCPLMAIN |
| 33, 39, 41, 42, 46, 47 | BCPLIO entry addresses set by BCPLMAIN |
| 40 | `APTOVEC` address from BCPLAPT |
| 76 | Only if still unset: BCPLMAIN local `WRITEST`; imported BLIB `WRITEF` is preferred |
| 85, 86 | Machine-dependent GETBYTE/PUTBYTE from BCPLBYTE |
| 87, 88 | Dynamic-storage GETVEC/FREEVEC from BCPLMEM |
| 150 | Provisional BCPLMAIN `DEBUGINT`, **also a known full-compiler conflict** |

The precise R12 displacements are `4*N`; see the
[source-linked per-slot table](runtime-extensions-r0-native-global-owner-inventory-20261020.md).
`G!1 START` is **application-trailer owned**; it is checked for
non-sentinel after the BLIB pass, not published by a direct native
store. `G!30` STOP is a native entry, not a selected finalizer.

## BLIB source-derived export names (21, now cross-checked with JOB 2197)

The current [reconstructed BLIB source](../cambridge-compiler/source/blib.bcpl)
contains top-level routine definitions matching these LIBHDR slots.
This identifies **source ownership**, not a fully decoded installed
object trailer:

| G! | BLIB source declarations |
| --- | --- |
| 3, 4, 5 | ABORT, BACKTRACE, ERRORMESSAGE |
| 56, 58, 59 | STACKHWM, INPROGRAM, VALIDPOINTER |
| 60, 62, 63, 64, 65 | WRITES, WRITEN, NEWLINE, NEWPAGE, WRITEO |
| 66, 67, 68, 69, 70 | PACKSTRING, UNPACKSTRING, WRITED, WRITEARG, READN |
| 74, 75, 76, 77, 78 | WRITEX, WRITEHEX, WRITEF, WRITEOCT, MAPSTORE |

`PRINTWIDTH` is a source-local helper and not a named historical
LIBHDR global. **JOB 2197 now verifies that the current installed and linked BLIB
exports exactly those 21 global numbers.** The original source-name
association remains source-derived: the GO program measured relocated
slot/address pairs, not original BCPL procedure names. Build provenance
for the installed BLIB object is still unverified. The earlier
G1–G99 reconciliation remains the per-slot historical table.

## Unresolved or deliberately reserved ownership

| Global / set | Meaning | Safe classification |
| --- | --- | --- |
| 2, 7–10, 18–29, 31–32, 34–38, 43–45, 48–49, 51, 57, 61, 71–73, 79–84, 89–99 | Historical or special positions not proven present by this specific source audit | **Not free**; inspect other source/runtime exports before allocation |
| 23–29 | Historical record I/O and time/date names | Do not silently repurpose for QSAM or clock extension |
| 50, 73 | Historical unnamed/spare positions | Not freely assignable |
| 57 | Commented OS/CMS marker in LIBHDR | Historical data slot, precise current representation unresolved |
| 76 | BLIB WRITEF versus BCPLMAIN fallback | **BLIB-present precedence passed JOB 2199**; BLIB-absent fallback remains untested; no general waiver |
| 94 | Historical LIBHDR assigns both OPENBLOCKFILE and UPDATEBLOCKFILE | Ambiguous **header alias**, not proof of two linked writers |
| 150 | BCPLMAIN DEBUGINT versus full Cambridge compiler FORMTREE use | Known cross-component conflict, not an available extension slot |
| 200, 201, 202 | Officially allocated BCPLQSAM, BCPLTIME, BCPLDEC dispatchers | **Reserved for those owners**; not installed by allocation |
| 299–305 | Standalone R.0 test fixture numbers only | Not assigned or authorized public allocations |

Historical `FIRSTFREEGLOBAL=150` is **not** a vacancy guarantee.
Compiler `CGHDR` and MR10-local allocations have additional
contexts; the [registry](global-number-registry.md) must be
consulted for every real application or compiler load.

## Owner-approved pre-START collision policy (not yet implemented)

1. At reproducible **link preparation**, decode the **actual**
   application's CG370 global trailer and the **actual installed**
   BLIB object trailer. Record `(N, address, origin, symbol,
   evidence)` for each export; do **not** infer from names alone.
2. Combine those entries with the explicit native map above, all
   historical/compiler reservations applicable to that executable,
   and the official System Extension allocation table.
3. Record **every actual duplicate** as `historical/verified
   precedence` (with listing, exact winner and regression) or
   `unresolved`. **BLIB-present G!76 precedence** is verified by
   JOB 2199 and is the narrow historical exception; this is not a
   general override waiver. The BLIB-absent fallback is still open.
4. For selected optional packages, require matching registered
   owner for each slot, no two selected owners, no duplicate within
   a package, and no collision with application/BLIB/core (including
   prior writers hidden by replacement). **No general legacy
   override waiver.**
5. Validate the complete selected table and its transitive required
   packages **before any optional G!N publication**, retaining
   current legacy import precedence for otherwise unchanged
   programs. Produce deterministic diagnostics on conflict; do not
   retrofit a new failure onto an accepted historical overlap.

## Remaining R.0 evidence before calling this a *complete* ledger

- **Completed for one representative application and installed BLIB:**
  JOB 2197 recorded G!1 plus 21 BLIB slots and zero application/BLIB
  overlaps. Larger applications and compiler programs still need their
  own per-executable ledger. Installed BLIB object-build provenance
  remains an explicit evidence gap.
- **Completed (BLIB-present path only):** JOB 2199 verified that the
  installed runtime's G!76 matches the installed BLIB export at START.
  Still review the BLIB-absent fallback and possible indirect writers.
- Demonstrate a selected extension's attempted G!N collision with
  an **actual** application/BLIB/native writer, rejecting before
  START and publishing **no** optional entry.
- Distinguish build-time trusted object/extent validation from what
  arbitrary relocated pointers can safely prove at runtime.

The [test-only 20-case JOB 2195](runtime-extensions-r0-batch-job-2195-evidence-20261021.md)
confirms internal duplicate/required/known G!14 and G!200 fixture
rejections. It **does not** perform this effective legacy ledger
audit or demonstrate transactional installation in BCPLMAIN.

**Finding:** JOB 2197 establishes actual application/installed-BLIB
export ownership **for the linked sample only**. G!76 is the only
observed BLIB versus source-derived native direct-store overlap.
BLIB-present historical G!76 precedence is **verified in JOB 2199**.
The complete effective ownership ledger, BLIB-absent fallback,
other indirect owners, and installed object provenance remain
unverified. R.0 stays open.
