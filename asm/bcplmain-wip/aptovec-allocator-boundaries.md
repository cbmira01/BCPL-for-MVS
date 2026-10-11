# APTOVEC and allocator/termination boundary review

Status: **design review only — no executable changes** (2026-10-10).
Companion: [dependency-map.md](dependency-map.md). Source inspected:
`10-bootstrap-and-system.asmfrag`, `20-streams-and-services.asmfrag`,
`30-control-data-and-end.asmfrag`. Current opt-in external BCPLBYTE suite:
120/120 PASS. The interfaces below are **design proposals**, not historical
entry points or tested assembler linkage.

## Decision

**Do not extract APTOVEC or GETVEC/FREEVEC yet.** APTOVEC is the
smaller code extraction but has a direct cross-boundary error transfer into
the shared termination system; the allocator has an explicit state owner
whose lifetime crosses into FINISH/STOP and failed startup. First design
the boundary and an isolated, opt-in linker probe; preserve monolithic
default and existing regression results.

## 1. APTOVEC: exact implementation dependencies

The current G!40 entry `APTOVEC` receives **R7=F, R8=N** and invokes
`F(V,N)`; the temporary vector uses **N+1 words** in BCPL stack space.
It stores R4–R6 at 0(R15), sets R5=R15, checks N >= 0 and N <=
`APMAXN` (16380), computes a candidate next frame at
`old R15 + 20 + 4*N`, and checks an additional 16 bytes of headroom
against the absolute byte address `STKLIM`. The address of the
temporary vector is `(old R15 + 16)>>2` in R7; R8 remains N. It sets
R15 to the next workspace, uses R4 to call F via BALR R6,R4, and
after the generated return service has restored its frame, restores
R6 from 8(R5), R5 from 4(R5), R4 from 0(R5), returning via R6.
These are source-visible behaviors, not a guarantee that all size and
arithmetic extremes are safe.

Dependencies that prevent mechanical extraction:

| Edge | Current instruction or state | Required boundary |
|---|---|---|
| G!40 -> APTOVEC | BCPLMAIN installs `LA 1,APTOVEC` at 160(R12) | External relocatable address, as already proven with G85/G86 |
| APTOVEC -> stack limit | `C 14,STKLIM` | Access to runtime-owned absolute end-of-safe-stack address |
| APTOVEC -> overflow | `BM STKOVFL`, `BH STKOVFL` | **Nonreturning** transfer into BCPLMAIN termination/output subsystem |
| APTOVEC -> generated F | `BALR 6,4` | Preserve generated BCPL R0/R1–R3, R5/R6, R11/R12, R15 conventions |
| APTOVEC -> BCPL return | `RETIMPL` through R11 executable S+0 | Frame return must remain compatible |
| APTOVEC -> literal/data | `APMAXN DC F'16380'` | Move the constant with CSECT, recheck addressability |

A direct `EXTRN STKOVFL` is **not a sufficient design**: the
current `STKOVFL` uses `STKMSG`, `OUTBUF`, `OUTPOS` and
branches to `FINIMPL`, all BCPLMAIN-owned, R11-relative
and lifetime-sensitive. Additionally `STKOVFL` is used by the
system-vector stack-check path. The current diagnostic goes through
`FINIMPL`, selecting the existing completion behavior. No new
completion code should be invented during extraction.

### Candidate internal interface: APTOVEC support

For analysis, propose a **runtime support context** with at least:
- `stack_safe_end_byte` — absolute byte address corresponding to the
  current `STKLIM`, read-only to APTOVEC;
- `overflow_transfer` — explicit nonreturning runtime failure entry,
  carrying the same stack-overflow behavior as the current `STKOVFL`;
- a documented way to locate this support context without clobbering
  generated BCPL permanent registers.

**Open design question:** where that context pointer lives.
Using an additional published BCPL global, or quietly repurposing
R13, R11, or R12, would alter external contracts. A first opt-in
probe may instead give the new CSECT relocatable addresses for the
limit and a BCPLMAIN-owned adapter through an explicit private
interface, with a clear plan to replace static coupling later.
That avoids inventing an ABI before measured assembler/linker work.

### Proposed APTOVEC extraction gates

1. Establish exact count/offset/addressing of cross-CSECT symbols in
   a test-local source copy; guard no change to S+0/+20/+40/+60/+80
   dispatch and no change to public G assignments.
2. Design a BCPLMAIN-owned error adapter reached from extracted
   APTOVEC with a **nonreturning branch** and the same output/exit path.
   Confirm base-register reachability; do not confuse MVS R14 linkage
   with BCPL R6 linkage.
3. Assemble an independently linked APTOVEC object using an opt-in
   harness (no in-place replacement of canonical source).
4. Execute APTOVEC regressions 091, 092, 093 including nested call,
   large vector, and overflow; compare exact output and completion.
5. Run the full 120-test suite; accept only if all pass, including
   storage cleanup and BLIB cases.

## 2. GETVEC/FREEVEC and RELMEM: actual ownership

G!87 `GETVEC` accepts N in R7, rejects negative or overlarge N,
computes `4*(N+1)+12` bytes, and uses `GETMAIN EC`.
Its allocation record is **three fullwords** at the obtained byte
address: `+0 = BCPL word pointer`, `+4 = byte length`,
`+8 = next record byte address`. User payload begins at +12,
and records are pushed onto `VECLIST`.

G!88 `FREEVEC` receives the BCPL word pointer in R7, scans the
list, unlinks on match, and calls `FREEMAIN R`. Zero and unknown
pointer are currently no-ops. GETVEC/FREEVEC preserve R0–R3,
R5/R6 and R15 across MVS services using **static shared** saved
register slots, and restore caller R4 using 0(R5).

`RELMEM` is invoked from FINISH/STOP and post-allocation error
paths. It repeatedly detaches the first `VECLIST` record **before**
freeing it, then releases the **distinct** combined global-vector/
stack allocation `DYNBASE` of size `DYNLEN`, and clears
`DYNBASE`. On GETMAIN failure before a main allocation,
`GNOCORE` correctly bypasses RELMEM.

| Current data | Writer(s) | Reader(s) | Proposed owner |
|---|---|---|---|
| `VECLIST` | GETVEC, FREEVEC, RELMEM | GETVEC, FREEVEC, RELMEM | Future allocator module |
| `GVRMAX/GVRLEN/GVRADDR` | GETVEC; constant GVRMAX | GETVEC | Future allocator module |
| `GVRSAVE/GVRPSAVE/GVRLSAVE/GVRWSAVE` | GETVEC | GETVEC | Future allocator module |
| `FVRSAVE/FVPSAVE/FVLSAVE/FVWSAVE` | FREEVEC | FREEVEC | Future allocator module |
| `RELRET` | RELMEM | RELMEM | Core termination (today) |
| `DYNBASE/DYNLEN` | Startup, RELMEM | Startup, RELMEM | BCPLMAIN core |
| `STKLIM` | Startup | STKIMPL, APTOVEC | BCPLMAIN core |

### Candidate internal interface: BCPLMEM

Define the allocator's **private** operations conceptually:

- `mem_init()`: reset allocator's list state at startup, after
  runtime setup but before BCPL code can allocate (the current
  static list starts at zero; repeated invocation semantics unproven).
- `getvec(N) -> V`: existing G87 calling convention.
- `freevec(V)`: existing G88 calling convention.
- `mem_release_all()`: called by BCPLMAIN termination to detach
  and free all live vector allocations; **does not free DYNBASE**.
  Return/clobber and error behavior must be defined separately
  for this *private* native call, not assumed to be a BCPL procedure.
- `mem_reset_or_finalize()` (optional): only if real repeated
  invocation or task-lifetime evidence requires it.

This is **not** a recommendation to add new BCPL global numbers.
The only public/global interfaces remain G87/G88; the private
teardown entry would be called by BCPLMAIN, not application BCPL.
The allocator owns `VECLIST` and all helper saved-register images;
BCPLMAIN owns `DYNBASE/DYNLEN`, the MVS return and DCB cleanup.

### Teardown ordering invariant

`FINISH / STOP / post-allocation error`
→ `close/flush runtime-owned output and input streams`
→ `allocator.mem_release_all()`
→ `FREEMAIN R (DYNBASE,DYNLEN)`
→ `restore MVS caller registers and return requested RC`.

Failure before DYNBASE exists follows the distinct GNOCORE path.
The detached-head-first algorithm must be preserved exactly.
MVS storage service failures are not fully characterized; do not claim
FREEMAIN success from GO RC alone. Existing regression 083 uses
test-only instrumentation for stronger but bounded evidence.

### Reentrancy and register constraints

Neither implementation is reentrant: GETVEC, FREEVEC and RELMEM
use static scratch/storage, and the runtime is organized around
singleton MVS DCBs and save areas. Splitting CSECTs **does not**
make them reentrant. Future module design must either preserve this
single-invocation contract explicitly or introduce a separately
validated context-per-invocation abstraction. Do not share GETVEC
scratch across concurrent nested calls without proof.

## 3. Candidate choice and build policy

| Criterion | APTOVEC | BCPLMEM allocator |
|---|---|---|
| Existing G entry | G40 | G87/G88 |
| Persistent private state | Constant APMAXN, shared STKLIM | VECLIST and multiple saved-register fields |
| Return path | Nested generated BCPL call | Direct G-call return + private teardown |
| Error / exit coupling | Strong: branches to STKOVFL | Strong: RELMEM must own vector release |
| Smallest safe first experiment | Adapter interface + external G40 | Separate private teardown contract first |
| Recommended status | **Next extraction experiment, after adapter design** | **Defer executable split**, retain documented ownership plan |

**Recommendation:** Next implementation march should attempt a
test-local, opt-in APTOVEC extraction, not an immediate allocator
restructuring. Success requires normal, large, and overflow APTOVEC
cases to pass, *followed by all 120 regressions*. For BCPLMEM,
first specify private teardown linkage and state representation.
Neither requires PDS object installation now.

## Evidence limits

All exact source-level claims above come from the current assembler
fragments. The private entry names and context proposal are
**new designs**, not recovered historical interfaces. The review is
not a formal liveness, instruction-addressability, or control-flow
proof. It does not certify behavior under negative-size integer
overflow, reentrant invocation, or all MVS allocation failures.

## Opt-in APTOVEC two-object experiment prepared

This design is now implemented as an **isolated test fixture**, not a
production module: `tools/checks/bcplapt-linkage-probe.asm` contains
independently assembled `BCPLAPT CSECT`, and
`tools/checks/prepare-bcplapt-runtime-probe.py` prepares regressions
091, 092, or 093 from their existing generated `native-test.asm`.
Original source, canonical BCPLMAIN, and the standard runner are untouched.

The experiment deliberately uses *two private relocatable data/control
edges*, without claiming they are historical interfaces:

- BCPLMAIN exports `STKOVFL`; BCPLAPT branches to it on error.
  Thus the existing runtime still formats and terminates on overflow.
- BCPLAPT exports writable `APLIMIT`; BCPLMAIN copies its already
  computed `STKLIM` absolute-byte-address value into that word
  before running START. BCPLAPT tests against its local word.
- BCPLMAIN places externally resolved `APTOVEC` in G!40.
- BCPLAPT uses R10 as an independent assembler base, saving/restoring
  its incoming value through unused temporary workspace slot 12(R15)
  before invoking the nested BCPL function. This behavior is to be
  tested, not inferred from link-edit success alone.

The probe is intentionally **not** combined with the separate
BCPLBYTE-object option: each builds the ordinary monolithic byte
services plus external BCPLAPT, holding the variable under test to
APTOVEC. Production extraction must revisit the private edge design
and final assembler-source packaging.

Run one case at a time on TK5:

```sh
git pull --ff-only
python3 -m py_compile tools/checks/prepare-bcplapt-runtime-probe.py
tools/run-native-regression 91 --show-output
python3 tools/checks/prepare-bcplapt-runtime-probe.py 91
bash tools/submit-jcl \
  workarea/native-regression/091-aptovec-nested-call/aptovec-object-probe/aptovec-object-probe.jcl
tools/job-summary JOBNUMBER
tools/dump-report-for-job JOBNUMBER
```

Repeat for 092 and 093 using their corresponding workarea directory.
Expected output for 091 and 092: `42`. For 093:
`STACK OVERFLOW` and **no `999`**. All four steps
ASMBCPL/ASMNAT/LKED/GO must complete RC=0000, including the
intentional controlled overflow case. Confirm the external symbol
resolution in IEWL, not only GO RC.

**Status: untested on TK5.** No guest execution, linker acceptance, or
full 120-test acceptance is claimed. Continue with focused jobs before
any runner integration.
