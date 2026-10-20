# Milestone Runtime Extensions — R.0 candidate binary ABI and test gates

**Status: engineering proposal for owner review, NOT approved as an
exact ABI.** 20 October 2026. R.0 — Evidence and contract is in
progress; R.1 — Generic registration foundation has not started.
No `BCPLREG` assembler module, core runtime patch, or test job
is implemented by this document.

**Follow-up review (2026-10-20):** [Three unresolved R.0 questions](runtime-extensions-r0-three-design-questions-review-20261020.md)
propose independently relocated begin/end bounds, package-local
transitive dependency entries and a source-derived global-owner
ledger. If accepted, those refinements would **revise** this
initial candidate's 28-byte-table/40-byte-descriptor formulas.
Do not implement the offsets in this earlier draft as an approved ABI.
See the [partial native owner inventory](runtime-extensions-r0-native-global-owner-inventory-20261020.md).

**Later evidence and current review, 21 October 2026:** The
[JOB 2195 batched R.0 probes](runtime-extensions-r0-batch-job-2195-evidence-20261021.md)
passed. The [updated exact-ABI decision review](runtime-extensions-r0-abi-decision-review-20261021.md)
describes the **revised** paired-extent `28+8*N+8*M` table and
dependency-bearing `48+8*K+16*D` package candidate. The
single-pointer/40-byte design below is an **earlier superseded
candidate, not accepted v1**. The owner has since approved decisions
A–H in the [R.0 ABI decision record](runtime-extensions-r0-owner-abi-decisions.md).
Numeric limits, diagnostic codes and actual trailer evidence remain open.

**Governing authorities:** [Milestone Runtime Extensions](milestone-runtime-extensions.md),
[approved Q.0 error/finalizer model](qsam-q0-error-and-r0-design-decisions-20261020.md),
[Global Number Registry](global-number-registry.md), and
[Cambridge runtime/library nomenclature](runtime-and-library-nomenclature.md).

## 1. Direct source evidence: no generalized registry exists yet

| Path / symbol | Observation in tracked sources | Implication |
| --- | --- | --- |
| `bootstrap-toolchain/asm/bcplmain.asm`, generated prefix | `BCPLMAIN` obtains the generated module's end using a signed halfword at module +10; the file comments record a 16K generated-section limit | A new registration object should **not** impersonate a CG370 executable module/prefix |
| `BCPLMAIN`, `GSCAN/GINST` | Scans backward from `MODEND` for generated global pairs `(4*N,relocated address)`, preceded by `(4*MAXGN,0)`; writes globals directly | Existing importer has no bounded descriptor parser or universal duplicate-owner tracker |
| `BCPLMAIN`, `GIDONE/BLIMP` | Explicit external `BLIB`; loads its prefix +10 section-end offset, walks its generated export pairs, then installs them directly | App/BLIB precedence and same-slot overlap require a **pre-START occupancy audit**. A new registrar cannot simply check the final G vector if an earlier write already hid a duplicate |
| `BCPLMAIN`, core assignments | Explicit service globals follow the BLIB import; G!76 WRITEF has a sentinel-aware fallback; G!150 is DEBUGINT | Preserve intentional existing core behavior while detecting newly selected package conflicts |
| `BCPLMAIN`, `GLOBCNT/GVBYTES/DYNLEN` | `GLOBCNT EQU 699`; `GVBYTES=(699+1)*4`; one dynamic core block has `DYNLEN F'68592'` | A binary global number N must be in current bounds **1..699**; this WIP capacity does not confer unused-slot ownership |
| `BCPLMAIN`, `FINIMPL/STOPENT/FINEXIT` | FINISH resets `STOPRC`; STOP stores R7 in `STOPRC`; FINEXIT calls `IOFIN` before `RELMEM` which invokes `MEMDRAIN` | Add only a **generic** future hook ahead of IOFIN, preserving STOPRC and BCPL/MVS register state |
| `bootstrap-toolchain/asm/bcplio.asm`, `IOFIN` | Saves working registers, drains and CLOSEs streams and invokes `IODRAIN` | Finalizer failure diagnostics must not disrupt core character-stream cleanup |
| `bootstrap-toolchain/probes/q0-dispatcher-abi-probe/` | JOB 2157 linked an assembler `Q0DISP` export using a **test-only CG370 application trailer edit** and passed G!200/QUERY | Proves relocated external address and BCPL call ABI; **not** generic `BCPLREG` registration or finalizer ABI |

The existing global sentinel is `X'C7D3F000' + 4*N`;
G!0 is the allocated extent, not an ordinary procedure export.
The current importer does not already provide fully checked,
collision-free imports. Keep historical BLIB behavior unchanged until
the R.0 audit establishes whether any existing duplicate is intended.

## 2. Candidate R.0 wire format: explicit relocatable table

**This section proposes actual byte offsets and is NOT yet approved.**
All integers and addresses below are System/370 aligned 32-bit
fullwords in ordinary MVS object data, with IEWL resolving
`DC A(EXTERNAL)`. Character identities are fixed-size **EBCDIC**
`DC CLn'...'` constants; do not interpret these as ASCII bytes
or BCPL word pointers.

### Application `BCPLREG` header (28 bytes, seven fullwords)

| Byte offset | Size | Candidate field | Proposed contract |
| --- | ---: | --- | --- |
| 0 | 4 | magic | `CL4'BCRG'` |
| 4 | 4 | layout version | fullword 1 |
| 8 | 4 | header length | fullword 28 |
| 12 | 4 | total table bytes | fullword `28+4*N+8*M` |
| 16 | 4 | N descriptor references | unsigned nonnegative count |
| 20 | 4 | M required package identifiers | unsigned nonnegative count |
| 24 | 4 | flags/reserved | zero in v1 |
| 28 | 4*N | selected descriptors | array of relocated `A(PKGDESCR)` |
| 28+4*N | 8*M | required package IDs | array of fixed `CL8` identifiers |

No extra sentinel is needed if all counts/lengths are
validated before dereferencing. **N=0/M=0 is a legal empty table**,
of length exactly 28. The manifest/link-edit must explicitly
include a real empty `BCPLREG` object when no modules are selected;
do not require unproven weak-symbol or runtime discovery behavior.
A non-empty required list whose package is absent fails before START.

### Package descriptor header (40 bytes plus exports)

| Byte offset | Size | Candidate field | Proposed contract |
| --- | ---: | --- | --- |
| 0 | 4 | magic | `CL4'BCEX'` |
| 4 | 4 | descriptor format | fullword 1 |
| 8 | 4 | header length | fullword 40 |
| 12 | 4 | total descriptor bytes | fullword `40+8*K` |
| 16 | 8 | package ID | stable EBCDIC `CL8`; uppercase and blank padded |
| 24 | 4 | API major | fullword |
| 28 | 4 | API minor | fullword |
| 32 | 4 | K exported globals | unsigned nonnegative count |
| 36 | 4 | finalizer address | IEWL-relocated entry address, or zero |
| 40 | 8*K | export pairs | each `F'GLOBAL_NUMBER',A(ENTRY)` |

One package normally exports its single dispatcher, e.g.
`QSAMSVC:200`, but format allows K>1 for a justified module.
The package ID is a registry key, **not** a new G!N or a new
global procedure name. Eight bytes are only a candidate tradeoff;
verify uniqueness, future version negotiation and User/Site
Library naming before accepting.

**Open dependency question:** This v1 candidate only carries the
application's explicit required-package ID list; it does **not**
encode descriptor-local package dependencies. Before adoption,
R.0 must choose and test whether `BCPLREG` must enumerate
transitive package requirements explicitly or each descriptor
must carry its own dependency list. Do not publish a descriptor
as usable if a required peer service is absent. Likewise,
this first proposal has **no initializer hook**: decide whether
to add one or to require lazy initialization before accepting
stateful modules. These are deliberate **unresolved ABI choices**,
not features silently omitted from production.

**Pre-START validation proposal:** ensure readable bounded address
ranges, aligned word fields and pointers, exact length formulas
with overflow prevention, known version/magic, unique package IDs,
valid nonzero exported entry addresses, `1 <= Nglobal <= GLOBCNT`,
no duplicate slot within/across modules, no collision with effective
application/BLIB/core globals, and every declared required package
present with an acceptable API major. Reject malformed descriptor
or missing dependency before writing any optional globals. A failed
IEWL unresolved EXTRN and a startup missing-requirement diagnostic
are **different cases**, and both need explicit tests.

**Important unresolved safety boundary:** A descriptor's self-reported
length cannot prove that its address is safe to read. R.0 must
establish a linker/module **trusted extent** or equivalent
representation with safe bounded validation. Do not simply
dereference arbitrary forged addresses from a corrupt table.

### Candidate finalizer calling convention

This is **not** the BCPL `QSAMSVC` R7/R8/R9 call ABI.
Use a conventional assembler subroutine boundary, with a generic
caller-owned parameter block:

| Interface | Candidate behavior |
| --- | --- |
| R15 on entry | Linked finalizer entry address |
| R14 on entry | Return address |
| R13 on entry | Valid 18-fullword MVS save-area chain |
| R1 on entry | Byte address of 8-byte parameter block |
| Parameter +0 | 0 = ordinary FINISH, 1 = STOP(n) |
| Parameter +4 | Requested STOP code (0 on ordinary FINISH) |
| R15 on return | 0 = success, any nonzero = returned failure |
| Preserved by callee | R2–R12 and R13 by MVS linkage discipline; must return through R14 |
| Generic caller | Saves/restores any additional live BCPL/system registers, especially R0, R7–R12 and its own R14, around the call |

The caller aggregates all returned failures, continues invoking
independent finalizers in **reverse registration order exactly once**,
then invokes existing `IOFIN` and `MEMDRAIN`. Returned errors
generate a diagnostic. On ordinary FINISH, any returned finalizer
failure changes the requested clean RC=0 to **RC=8**. On STOP(n),
the preexisting requested code **n** is not overwritten. Never
reinterpret an unrecovered MVS abend as an ordinary returned status.
An implementation must verify that source `FINEXIT` preserves R10,
the relevant save-area/register invariants and MVS return R15.

**Specific compatibility risk:** BCPLMAIN initializes R0 to zero
and uses R1=4096, R2=8192, R3=12288 for generated BCPL code.
A conventional assembler finalizer should not be called as though
it were a generated BCPL procedure; a bridge must protect its
caller and restore the required execution environment before
continuing to BCPLIO and MEMDRAIN.

## 3. Design alternatives requiring a decision

| Decision | Candidate above | Alternative and tradeoff |
| --- | --- | --- |
| Extension export encoding | Explicit `(G!N,address)` pairs | Reuse CG370 trailer: less encoding duplication but relies on prefix and backward scan; risks incorrectly fabricating a compiler-generated prefix in assembler modules |
| Table termination | Bounded count+total byte length | End sentinel: simpler to read, but less defensive against malformed/unterminated entries without validated external bounds |
| Identifier/requirements | Eight-byte package IDs, explicit required-ID list | Link-only requirements: cannot detect a BCPL-declared but omitted optional global through IEWL alone |
| Finalizer ABI | MVS register/save-area callable routine | Generated BCPL procedure ABI: would entangle finalizer ordering with BCPL workspace/state |
| Startup duplicate detection | Validate effective app/BLIB/core occupancy *before* new installs | Simple sentinel-only check: misses past overwritten assignments and implicit intentional overrides |
| Generic startup linkage | Explicit `BCPLREG` in every app link-edit | Weak/absent symbol: availability under MVS 3.8 IEWL NCAL/LET not established |

## 4. R.0 evidence / negative-test matrix

| Test | Required observable result |
| --- | --- |
| Empty registry, zero requirements | Native application reaches START, ordinary FINISH RC=0, preexisting BLIB/BCPLIO regressions intact |
| One stateless assembler dispatcher | G!N populated from linked descriptor; opcode 0 QUERY works |
| One stateful assembler probe | Finalizer called once on FINISH and STOP(n), before IOFIN |
| Two selected finalizers | Trace verifies **reverse registration order**, once per entry |
| Returned error on FINISH | Diagnostic and **RC=8**, core IOFIN/MEMDRAIN still run |
| Returned error on STOP(8) / STOP(4) | Diagnostic but original STOP value unchanged |
| Duplicate exported global | Deterministic pre-START rejection with no partial install |
| Duplicate package ID / malformed count or length | Deterministic pre-START rejection |
| Missing required package | Fail before START even if caller has merely declared its BCPL header |
| Empty `BCPLREG` with optional object incidentally linked | Object not installed unless selected through descriptor table |
| Invalid finalizer address | Reject before START without executing garbage storage |
| App/BLIB/core collisions | Reject unintended duplication without breaking documented existing core/BLIB semantics |
| Full native regression after accepted change | Preserve the existing accepted baseline; no speculative promotion or refactor |

Tests that exercise malformed addresses should be constructed in
controlled isolated jobs and should **not** attempt arbitrary
unsafe memory reads. Any error path that the test cannot safely
bound remains **unverified**, not a negative result.

## 5. Approval boundary

The owner has approved **generic `BCPLREG`, descriptors with optional
finalizers, collision rejection, reverse order, FINISH RC=8 for
returned hook errors, and STOP(n) preservation**.

The **28-byte `BCPLREG` header, 40-byte package header, eight-byte
IDs, requirement-list encoding, full register/parameter convention
and exact validation algorithm above are NEW CANDIDATES**, not
owner-approved facts, MVS-proven behavior, or production code.

**Next action:** Discuss these candidate details with the owner,
resolve the storage extent and historic overlap audit, then
build *test-only* R.0 MVS proof programs on GitHub `main` once
the exact ABI is approved. R.1 remains unstarted.
