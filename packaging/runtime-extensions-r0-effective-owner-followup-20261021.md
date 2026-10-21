# Milestone Runtime Extensions — R.0 effective global ownership follow-up

**Date:** 21 October 2026.
**March:** **R.0 — Evidence and contract (open)**.
**Scope:** source audit and now **approved, host-tested test-only**
G!76 no-export fallback fixture. The [probe](../bootstrap-toolchain/probes/r0-g76-noexport-probe/README.md)
is prepared; **actual MVS execution and IEWL MAP inspection remain
pending**. No accepted object mutation is claimed. Next march **R.1 —
Generic registration foundation** remains not started.
**Git review revision:** `7c101d9fd1796a3729551ad6c650e1faa0791469`.

**Authorities:** [Milestone Runtime Extensions](milestone-runtime-extensions.md);
[owner-approved Decision E](runtime-extensions-r0-owner-abi-decisions.md);
[Global Number Registry](global-number-registry.md);
[prior source and MVS owner audit](runtime-extensions-r0-global-ownership-audit-20261021.md);
[actual JOB 2197 exports](runtime-extensions-r0-trailer-job-2197-evidence-20261021.md);
[actual JOB 2199 G!76 precedence](runtime-extensions-r0-g76-job-2199-evidence-20261021.md).

## Why the BLIB-absent test needs an explicit design

The **accepted bootstrap** `bootstrap-toolchain/asm/bcplmain.asm`
declares `EXTRN BLIB` and unconditionally uses the relocated
`BLIB` prefix to scan its global export trailer at `BLIMP`.
It initializes the G vector with sentinels, imports the application's
trailer first, imports the BLIB trailer second, and then publishes core
entries. For G!76 at byte offset 304, its conditional
`WRITEST` store executes **only if** G!76 still equals
`X'C7D3F130'` (the G!76 sentinel). An imported BLIB WRITEF
address is preserved.

JOB 2199 established the **BLIB-present** path under the real
installed bootstrap BCPLMAIN. **Omitting `BLIB` from IEWL without
replacing the external symbol fails linkage**, so it would *not*
exercise the no-G!76-export branch. Treat “BLIB absent” as two
distinct propositions:

1. **No BLIB object linked:** unsupported by the current
   mandatory `EXTRN BLIB` dependency; this would require a
   different core implementation (not authorized in R.0).
2. **No BLIB G!76 export:** technically feasible using a **temporary
   link-compatible `BLIB` CSECT** with a valid CG370-style prefix
   and empty export trailer, while linking the **installed**
   `BOOT_OBJ(BCPLMAIN)` and its ordinary other core object members.
   The installed BLIB member would *not* be included in that test
   load module. This is a proposed bounded proxy for the
   **G!76 sentinel/fallback branch**, **not** a proof that the
   system can run with no `BLIB` symbol at all.

**Owner-approved test (implemented as a host-tested fixture; MVS pending):** Assemble the
no-export `BLIB` CSECT into a temporary object; compile a minimal
BCPL START with the installed interpreter-hosted **demoted Cambridge
compiler**; keep the installed BCPLMAIN/BCPLIO/BCPLMEM/BCPLBYTE/
BCPLAPT objects as read-only link inputs; link only temporary objects
and a temporary load module. The application uses **G!76 WRITEF**
with a numeric formatting test and core termination, **not**
BLIB-provided WRITES/NEWLINE or other absent BLIB services.
Require a unique actual GO output marker with the formatted number,
IFOX/IEWL/GO RC=0000, a MAP/XREF showing the temporary BLIB symbol
owner, and confirmation that the temporary BLIB trailer has zero
G!76 export pairs. Do not install, replace or touch `BOOT_OBJ(BLIB)`.

The trial should be described **“BLIB G!76 export absent”**,
never “no BLIB linked,” and no untested full-runtime
BLIB-optional packaging claim should follow.

## Indirect binding versus actual global owners

This review separates startup publication of G!N entries from
writes to *data reachable through* a BCPL global pointer.

| Module and source | Actual inspected behavior | Ownership conclusion |
| --- | --- | --- |
| `bootstrap-toolchain/asm/bcplmain.asm` | Initializes G!0–699, imports application and BLIB trailers, publishes native direct entries including G!76 conditional and G!150 DEBUGINT | Fixed G-vector **startup writer**; all pairs imported from trailers need per-executable verification |
| `bootstrap-toolchain/asm/bcplmem.asm` | `MEMBIND` receives R1 pointing to the **G!6 save-area slot G6!48**, retains pointer in `VECPUB`, then writes the allocator free-list head to `0(R1)` | An indirect *save-area field* write; **not** publication of global G!48 |
| `bootstrap-toolchain/asm/bcplio.asm` | `IOBIND` stores overflow callback in private `IOOVHAND`; other I/O entry routines work through private descriptors/caller-provided addresses | No additional hard-coded G!N **startup publication** found in reviewed assembly; do not assert that arbitrary caller memory is protected |
| `bootstrap-toolchain/asm/bcplapt.asm` | `BCPLMAIN` sets exported `APLIMIT` and publishes `APTOVEC` at G!40 | `APLIMIT` is **not** a second global-vector entry writer |
| `bootstrap-toolchain/asm/bcplbyte.asm` | `PUTBYTE` writes through a BCPL word pointer plus caller-supplied byte offset | Caller-directed memory store, **not** a fixed startup G!N owner; general arbitrary writes remain outside this narrow audit |

This is a **source review**, not a machine-executed full
transitive-writer proof or an assertion that every indirect
pointer is safe. The ordinary application and BLIB imported
trailers remain dynamic per executable.

## G!150 is a demonstrated cross-component declaration conflict

- The accepted bootstrap `BCPLMAIN` publishes its local
  `DEBUGINT` at **G!150** (`ST 1,600(12)`).
- `cambridge-compiler/source/bcpl.bcpl` **declares**
  `FORMTREE:150` and **calls** `FORMTREE()`.
- `cambridge-compiler/source/synhdr.bcpl` also declares
  `FORMTREE:150`; `cambridge-compiler/source/syn.bcpl`
  contains its implementation.
- `cambridge-compiler/asm/bcplmain.asm` is a separate,
  unaccepted compiler-target runtime and *also* documents
  G!150 DEBUGINT vs FORMTREE. It is **not** the installed
  `BOOT_OBJ(BCPLMAIN)` basis of this audit.

These are **actual source declarations and a runtime startup
writer**, not yet evidence of the fully linked native Cambridge
compiler's effective G!150 address at START. Under current
startup order, a compiler application G!150 trailer would
be overwritten by the core's DEBUGINT publication.
Do **not** bless that collision as historical precedence, reassign
FORMTREE, modify DEBUGINT or claim compiler integration solved.
Treat G!150 as an **unresolved cross-component conflict**, with
no optional-package ownership waiver.

## Next decision and proposed R.0 tests

1. **Owner-approved no-G!76-export BLIB CSECT:** the [test-only
   probe](../bootstrap-toolchain/probes/r0-g76-noexport-probe/README.md)
   is now committed with a fixed 24-byte temporary prefix/trailer,
   one START/WRITEF numeric-format application and 18 host tests
   passing. **MVS job numbers/step RCs and temporary BLIB IEWL
   symbol ownership remain to be observed.** This tests the branch,
   not physically missing BLIB linkage.
2. **Per-executable owner proof:** build a separate link/read-only
   observer with an actual application export at G!150, an
   independently decoded installed BLIB trailer, and the
   source-identified native DEBUGINT writer. Record all owners
   before the final value hides overwritten entries.
   Distinguish a test-local G!150 fixture from the not-yet-running
   *full* Cambridge compiler; do not claim the latter has been
   tested.
3. **Collision contract:** in an isolated R.0 *test harness*,
   reject a selected optional descriptor that conflicts with
   a **measured** application, BLIB, or native owner *before*
   publishing any optional globals. This does not implement the
   real R.1 startup registrar and is not proof of its RC=12
   behavior.
4. Keep real `BCPLREG` startup adaptation, transactionality
   in production, finalizer integration and accepted-object
   changes in **R.1** or later as specified by the milestone.

**Disposition:** This source follow-up has identified the exact
absence/linkage distinction and confirmed G!150 as an unresolved
cross-component declaration conflict. A no-G!76-export fallback probe is **prepared but has not run on
MVS**. No new legacy precedence exception is accepted.
**R.0 remains open; R.1 has not started.**
