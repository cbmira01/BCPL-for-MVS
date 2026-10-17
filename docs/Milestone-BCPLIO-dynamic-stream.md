# Milestone - BCPLIO dynamic stream

Status: M0/M1/M2 accepted; M3 logical gate accepted; M4.0/M4.1/M4.2/M4.3/M4.4 CLOSED (M4.2/M4.3 scoped, M4.4 DEVOBJ compatibility, 2026-10-17); M5 open  
Date: 2026-10-15  
Project: BCPL for MVS 3.8 reconstruction  
Target: native BCPL runtime (BCPLIO and its BCPLMAIN integration)

## M4.4 formally closed — full DEVOBJ compatibility (2026-10-17)

All M4.4 gates are accepted. Full 00..145 candidate
regression (owner-executed at `a572e77`) was
**145 PASS / 0 FAIL / 1 expected SKIP (083)**.
After the candidate RC-fixture reconciliation in
`48c6012`, the owner ran the stricter source and
saved-log checks successfully: **145/145 existing
logs audited, no detected abends/known-defect
exceptions**. Compile-only 048 was accounted for.
For BCPLM6/D6, stack-overflow cases 052 and 093
correctly produced GO RC0000 and `STACK OVERFLOW`;
the RC0012 D7/BCPLM7 expectations were preserved
in separate original fixtures. The 144 actual GO
steps have expected RC distribution:
0000=139, 0008=3, 0012=1, 0100=1.

**M4.4 CLOSED.** No runtime source, PDS objects
or public ABI changed, and no production OBJ
promotion occurred. The [M4.4 closure record]
(Milestone-BCPLIO-dynamic-stream-M4.4-plan.md)
contains the observed run/audit commands, caveats,
and locally generated JES job manifest path.
**M5 remains OPEN** for truly lossless per-DD
physical SYSOUT and record-attribution verification;
the dynamic-stream parent milestone is not closed.

## M4.4.2 — per-case log audit helper staged (2026-10-17)

A repository-owned verifier,
`tools/checks/check-m44-full-panel-logs.py`,
can inspect the operator's existing 145 saved case
logs and write `workarea/native-regression/m44-00-145-jobs.tsv`
with job IDs and key step return codes. It also flags
any accepted S322/known-runtime-defect condition.
This helper **has not yet been run by the operator**,
and does not submit jobs. M4.4.1's full 145-PASS
result stands; formal M4.4.2 audit remains pending.
M5 physical DD attribution remains separate.

## M4.4.2 audit discrepancy — 2026-10-17

The full candidate runner reported 145 PASS / 0 FAIL /
1 expected SKIP, but a stricter saved-log audit
reported two GO-return-code discrepancies: **052
and 093 returned RC0000 even though their
`expected-go-rc.txt` files specify 0012**.
Both are stack-overflow tests, outside BCPLIO.
The three other initial findings concern test
048, a deliberately compile-only test; the
audit has been corrected for its absent GO/LKED.

The native runner currently counts RC0000 as PASS
without consulting a conflicting nonzero-RC fixture.
The BCPLM6/D6 and BCPLM7/D7 stack-overflow
expectations require explicit reconciliation; no
test fixtures or runtime objects were modified.
**M4.4 formal closure remains BLOCKED** despite
the outer 145-PASS result. M5 remains separate.
See the [M4.4 plan](Milestone-BCPLIO-dynamic-stream-M4.4-plan.md).

## M4.4.1 accepted — entire 00..145 DEVOBJ candidate PASS (2026-10-17)

The owner ran the previously authorized, complete
DEVOBJ BCPLM6 candidate panel after
`check-m44-compatibility.py --candidate` PASSED.
The provided console report enumerates 00..145
with **145 PASS, 0 FAIL, 1 expected SKIP (083),
TOTAL 146**. All cases 133..145 passed in
this full-panel execution. This supersedes the
00..132 as the latest complete accepted compatibility
checkpoint, without asserting any runtime-object
promotion or physical DD identity verification.

**M4.4.1 ACCEPTED; M4.4.2 log-level audit pending.**
The summary omits individual MVS jobs and condition
codes and the runner can count an S322
`PASS WITH KNOWN RUNTIME DEFECT` as PASS.
Review saved `workarea/native-regression/logs/`
without rerunning the suite, and reconcile exceptions
before closing M4.4. See the
[M4.4 plan](Milestone-BCPLIO-dynamic-stream-M4.4-plan.md).

## M4.4.1 — owner authorizes complete candidate panel (2026-10-17)

The owner explicitly lifted the previously recorded deferral:
**run the full DEVOBJ BCPLM6 00..145 candidate panel.**
M4.4.0 source-only readiness is accepted; before
execution, validate the four candidate environment
variables with `check-m44-compatibility.py --candidate`.
Expected: **145 PASS / 0 FAIL / 1 SKIP 083**.
**Authorization is recorded, but execution results are
not yet supplied.** M4.4 remains OPEN pending the
actual complete suite and evidence review. No runtime
rebuild, installed-object promotion or change to the
M5 DD-attribution scope is authorized. See the
[M4.4 plan](Milestone-BCPLIO-dynamic-stream-M4.4-plan.md).

## M4.4.0 accepted — read-only preflight (2026-10-17)

Owner-reported `git pull` through `7d718d1` and
all three preparation checks: **M4.4 compatibility
preflight PASS, M4.3 private source audit PASS,
native regression numbering PASS**.
The verified suite contains **00..145**, 146
contiguous cases, with candidate-only 124..145,
the expected source-only skip 083, and isolated
accounting cases 139..145.
The candidate environment was **not checked**;
no JES test was submitted and **no complete
compatibility run occurred**. M4.4.0 is
accepted; M4.4.1 is **owner-deferred** until
the owner explicitly authorizes the full
00..145 DEVOBJ run. M4.4 and M5 remain open.
See the [M4.4 plan]
(Milestone-BCPLIO-dynamic-stream-M4.4-plan.md).

## M4.4.0 source-only compatibility preparation (2026-10-17)

M4.3 is closed. The [M4.4 compatibility procedure]
(Milestone-BCPLIO-dynamic-stream-M4.4-plan.md) is staged with a
new non-submitting checker:
tools/checks/check-m44-compatibility.py.
The current numbered corpus 00..145 contains 146 cases;
the expected eventual full DEVOBJ checkpoint is
**145 PASS / 0 FAIL / 1 intentional SKIP 083**.
The last accepted complete panel remains 00..132
(132 PASS, 0 FAIL, 1 expected skip), with 133..145
accepted in targeted runs only.

The prior owner decision **to defer the full suite**
is preserved: this is a source-only preparation gate,
NOT an observed preflight or full-panel PASS. Runtime
and PDS members are unchanged; M5 DD-specific attribution
remains separate.

## M4.3 closed — scoped resource accounting (2026-10-17)

**M4.3 is CLOSED.** Final JES details were supplied for all seven
isolated candidate runs: GO jobs **7880, 7882, 7884,
7887, 7889, 7891, 7893**; Cambridge compilation jobs
**7879, 7881, 7883, 7886, 7888, 7890, 7892**.
ASMAP and ASMFIO always returned RC0000; ASMNAT
returned RC0000 in tests 139 and 142–145; LKED always
returned RC0000. GO returned RC0000 for all except
regression **141 / JOB 7884**, whose STOP(8) GO RC0008
was expected and its regression outcome was PASS.
Thus focused regressions **139–145: 7 PASS / 0 FAIL**
across their targeted runs. M4.3 source checks also passed.

Measured scope: private counter values through explicit close,
simulated returned allocation/OPEN failure and later retry;
post-IODRAIN empty resource lists and balanced
GETMAIN/FREEMAIN and QSAM OPEN/CLOSE counts.
This does not prove physical MVS reclamation or
recoverability of actual abends. Isolated test-private
BCPLIO was used, not installed into OBJ or DEVOBJ;
the ABI and production modules remain untouched.
**M4.4 and M5 remain OPEN; full regression remains
owner-deferred.** The detailed run table and caveats
are in the [M4.3 acceptance record]
(Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).
## M4.3.2b accepted — focused 142–145 PASS (2026-10-17)

At source revision `ce8d3e1`, the owner reran the
source checks: terminal assertions, native shim,
80-column BCPL records, combined synthetic fault
source, and private accounting checks all PASS.
Candidate-only native **142 descriptor32 PASS,
143 buffer268 PASS, 144 handle16 PASS,
145 pre-SVC19 OPEN denial PASS: 4 PASS / 0 FAIL /
0 SKIP**. The deterministic BCPL assertions
check returned failure accounting, retry, two
explicit CLOSEs, and terminal IODRAIN equality
and empty DHEAD/HHEAD. This completes all
focused M4.3 gates, together with 139–141.
**Formal M4.3 closure remains pending extraction
of the successful MVS JOB numbers and step codes
from local regression logs**, required by the
previously agreed acceptance procedure.
No independent physical MVS storage-free proof
or actual SVC19 error-return recovery is asserted;
full native panel remains deferred; installed
runtime and public ABI unchanged. See the
[M4.3 plan](Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).

## M4.3 accounting infrastructure and test 139 staged (2026-10-17)

Test-private accounting generator and static checker are committed.
Candidate-only compiled BCPL regression **139** uses existing regression
G151 to call a separate native assembler shim, which reads a private
IOACCT counter table in a temporary BCPLIO object. ASMFIO and ASMNAT
are separately assembled, and the job links with DEVOBJ(BCPLM6)
without overwriting installed BCPLIO. The test asserts allocation,
release, and real SVC19/SVC20 call-path counts, duplicate FIND,
tombstone retention, and close/reopen. See the
[M4.3 plan](Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).

**M4.3 remains OPEN.** No static checker execution, IFOX/IEWL/GO
PASS, final IODRAIN balance or failure-path accounting is claimed.
Full regression remains owner-deferred; OBJ/DEVOBJ are unchanged.
## M4.3.2a accepted (2026-10-17)

The operator supplied targeted source audit PASS and 140 FINISH
PASS / 141 STOP(8) PASS, **2 PASS / 0 FAIL / 0 SKIP**.
These private post-IODRAIN cases assert empty DHEAD/HHEAD
and balanced descriptor/region/handle and OPEN/CLOSE counts.
No physical free verification or rerun JES IDs were supplied.
**M4.3.2b recoverable-error resource accounting is next**;
M4.3 overall remains OPEN. See the
[M4.3 plan](Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).

## M4.3.1 acceptance (2026-10-17)

The owner supplied a fresh focused rerun: **139 PASS / 0 FAIL /
0 SKIP**, plus **source accounting and native-helper audits PASS**.
M4.3.0 and M4.3.1 are accepted. The successful rerun's individual
JES job IDs and step codes were not included in the supplied output.
The passing assertions cover GETMAIN/FREEMAIN and QSAM SVC
counter observations **before IOFIN**, duplicate FIND, retired
tombstones, and explicit close/reopen. The count checker
is test-only and does not establish host reclamation independently.
**M4.3.2 remains OPEN** for FINISH/STOP IODRAIN and synthetic
fault accounting; no production code, PDS member or
global-vector ABI change. See [M4.3 plan](Milestone-BCPLIO-dynamic-stream-M4.3-plan.md).

## M4.2 closure and remaining marches (2026-10-17)

The owner accepted a narrower, historically appropriate responsibility
boundary. **M4.2 is CLOSED**, under the [revised M4.2 acceptance](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md):
BCPLIO translates character streams to/from record-oriented QSAM and
responds correctly to errors for which MVS returns control. The
programmer/JCL provides compatible DD allocations; MVS validates
datasets and may abend on unrecoverable errors. BCPLIO does **not**
promise to catch S013 or manufacture a real failing OPEN to prove its
return-to-caller branch.

Focused **134–138 individually PASS** (135–138 contain specifically
described synthetic fault paths). Exploratory **JOB 7874, 7875, 7876**
all returned nonzero DD02 handles; they neither proved an unsuccessful
SVC19 nor demonstrated GET from DD02. The M4.2 source-inspected
cleanup branch and regression 138 support scoped recovery, **not**
instrumented proof of matching FREEMAIN/CLOSE calls. See the
[programmer-facing dataset contract](BCPLIO-JCL-QSAM-stream-contract.md).

**Next: M4.3** independent descriptor (32), region (268), and handle
(16) ownership counts, SVC19/SVC20 counts and cleanup validation
without changing the public ABI. M4.4's full native panel remains
owner-deferred (last accepted full 00..132: 132 PASS, 0 FAIL, one
expected SKIP 083). M5 physical DD attribution and overall milestone
acceptance remain open. No runtime source was changed and no
DEVOBJ/OBJ promotion is authorized by this decision.

## M0 gate decision (2026-10-16)

**ACCEPTED.** The owner approved stable non-recycled opaque handle identities, duplicate FIND returning the same active handle, lowercase-to-uppercase DD-name normalization, zero/non-destructive ordinary FIND failure, and preservation of existing stream semantics. Baseline: commit `73a6591d7dc574603b19ea025a3d8c9a428f5e36`, native regression 00–123: **123 PASS, 0 FAIL, 1 expected SKIP (083)**. Production default links BCPLMAIN from OBJ and does not include BCPLIO separately; historical Gate D D6 modular candidate acceptance is distinct. Detailed contract, implementation map, evidentiary limitations and future tests: [Milestone-BCPLIO-dynamic-stream-M0-contract.md](Milestone-BCPLIO-dynamic-stream-M0-contract.md). No M1 implementation began as part of M0 acceptance.

## Purpose and decision

Implement in the **native core BCPL stream runtime** the dynamic, arbitrary-DD-name stream capability already demonstrated by the MR10 INTCODE interpreter `ICINT v19`. This is a runtime compatibility/completion milestone, **not** a new QSAM application library and **not** an optional runtime extension.

A BCPL application should be able to say `FINDINPUT("CUSTOMER")` or `FINDOUTPUT("REPORT")`, where the named DD is supplied through the GO step's JCL, without adding that DD name to assembler source or reserving a fixed BCPLIO slot. The caller receives an opaque stream handle and continues to use the historical BCPL stream operations. The runtime manages MVS DCBs, QSAM record buffers, OPEN/CLOSE, resource ownership, selection, and cleanup.

**Clarification:** DD-name *discovery* means resolving a particular name supplied by the application and checking its JCL allocation (as ICINT uses RDJFCB); it does not mean enumerating all allocated DD statements. These are BCPL streams, not physical S/370 channels or MVS channel addresses.

## Historical and current evidence

- `mr10-kit-compiler/asm/icintv19.asm`: V15 arbitrary DD discovery; V16 GETMAIN-backed dynamically allocated descriptors/DCBs/buffers, linked active-stream list, conditional allocation failure, RDJFCB validation, release on ENDREAD/ENDWRITE. `DYNFIND`, `DYFALLOC`, `DYFVERIF`, `DYNFRE...`, name normalization and `OPENSTRM` are implementation study points. The interpreter retains special static streams `INTIN`, `SYSPRINT`, `INTCODE`. Its generic discovered streams use 80-byte text records.
- `mr10-kit-compiler/tests/07-many-streams/main.bcpl` and README: established interpreter demonstration opening twelve independently named DD01..DD12 input streams simultaneously and reading/closing each.
- `mr10-kit-compiler/tests/06-dynamic-streams/`: multi-level historical dynamic stream tests.
- `native-compiler/asm/bcplio.asm`: current separate BCPLIO implementation recognizes only `BCPIN`, `BCPINB`, `SYSPRINT`, `BCPALT` with static DCBs and handles. The PARM pseudo-stream is separate.
- `native-compiler/asm/bcplmain-wip/20-streams-and-services.asmfrag`: older/bootstrap stream logic; ascertain actual installed canonical owner before editing.
- `native-compiler/regression/native-stream-contract.md`: accepted *fixed-DD* behavior, remaining observability/attribution caveats, and current stream ABI. In particular G11 SELECTINPUT, G12 SELECTOUTPUT, G13 RDCH, G14 WRCH, G15 UNRDCH, G16 INPUT, G17 OUTPUT, G33 WRAPOUTPUT, G39 FINDPARM, G41 FINDOUTPUT, G42 FINDINPUT, G46 ENDREAD, G47 ENDWRITE.
- `native-compiler/regression/094-... through 119-...`: baseline focused regression corpus, notably 114 interleaving, 115 output reopening, 116 unknown names, 117 EOF/unread, 118 re-open and 119 shutdown.
- Native regression panel historically has 124 cases (00..123), but run the current panel and report its actual count, baseline, commit and failures; do not silently assume green.

Read the code and current MVS PDS/build inventory before modifying anything. Do not equate the interpreter's host X-operation internals with the native BCPL procedure ABI.

## Scope

**Required:**
1. Arbitrary valid MVS DD-name lookup by `FINDINPUT`/`FINDOUTPUT` (case/length normalization documented; MVS DD names are at most eight characters); no compile-time named-DD allowlist.
2. Dynamically allocated, independently owned, per-stream descriptor, DCB and record buffer, suitable for more than twelve simultaneous ordinary input streams; no fixed slot-count ceiling.
3. Opaque BCPL stream handles preserving existing word-address conventions and G-slot/calling ABI. Validate selected/open handles; never expose raw DCB pointers as arbitrary BCPL memory to programs.
4. Independent stream state: position, record boundaries, EOF, one-character UNRDCH, output buffering, and input/output selection; switching streams must not corrupt state.
5. Repeated FIND of an already-open name returns a consistent documented handle/behavior; failures (unknown/unallocated DD, storage exhaustion, OPEN failure) are nonfatal and return the historical failure indication where feasible, without perturbing current selection.
6. ENDREAD/ENDWRITE and process termination flush/close and reclaim objects exactly once; support reopen by name after close and distinguish stale from live handles.
7. Retain standard streams and FINDPARM semantics; do not regress compiler output, SYSOUT, EXEC PARM, FINISH/STOP cleanup, or established BLIB stream operations.
8. A precise record/character contract covering FB80 input trimming, synthetic newline, output recordization, ASCII/ EBCDIC conversion, significant trailing blanks, record length, and empty lines. Preserve existing accepted behavior initially; identify historical differences rather than quietly changing semantics.
9. Documentation: descriptor ownership, linked-list/index design, DD-name validation, status/failure map, register and storage contracts, and limits imposed by MVS/resource availability.

**Not in scope:** a general-purpose BCPLQSAM or BCPLVSAM library; keyed/binary/variable-record application I/O; DD enumeration; dynamic allocation of datasets/SVC 99; arbitrary file-system paths; new BCPL syntax or compiler G slots; general reentrant/multitasking runtime redesign; migrating interpreter-produced binaries or the Cambridge compiler as a prerequisite.

### Architecture rules / collected wisdom

- BCPL streams are a **core runtime service** because the historical language/BLIB stream interface depends on them. The QSAM implementation is a host-specific internal adapter, not evidence that every MVS-dependent facility belongs in BCPLMAIN.
- Application-facing record-oriented **BCPLQSAM** and future **BCPLVSAM** remain optional separately linked libraries, distinct from the character-oriented BCPL stream abstraction. Avoid duplicating ownership and semantics through premature generalization.
- Reuse ICINT v19's proven dynamic allocation and RDJFCB approach conceptually; port/adapt under the native procedure calling convention rather than copying blindly.
- Favor simple historically intelligible assembler, independently testable helpers, and tightly defined ownership. Keep BCPLMAIN small; prefer BCPLIO to own DCBs, buffers and stream registry.
- Stream handle identity and validity must be reasoned about explicitly. On close, the runtime must not accidentally accept a stale handle whose address has been reused; document the practical design (e.g. retained control identities/generation checks) and its trade-offs.
- Preserve known working behavior before adding features. Distinguish code inspection, assembly success, JCL execution, and verified output assertions. Make regression claims only from observed evidence.
- The runtime should rely on JCL DD allocation, not assume or hardcode every application name. DD lookup failure should not by itself cause an abend.
- Avoid inventing a new extension dispatcher, global assignment scheme, or mandatory library packaging solely for this work.

## March plan (each march has a review/commit gate)

### M0 — Baseline, contract, and implementation map
Inventory installed/current BCPLMAIN/BCPLIO source and MVS PDS object/link paths, and compare them with ICINT v19. Run native regression, pin SHA/job/evidence, identify precise G slot and native register/handle contract. Specify DD naming, duplicate lookup, special streams, resource lifetime, error behaviors, and record semantics in a design note. **Exit:** approved contract and green (or explicitly characterized) baseline; no functional changes.

### M1 — Dynamic descriptor and DD discovery
Implement runtime-owned dynamically allocated descriptors/DCBs/buffers, name normalization, RDJFCB-based DD resolution, active-stream registry, and conditional GETMAIN failure. Preserve bootstrap streams/special semantics. First test arbitrary third input DD beyond BCPIN/BCPINB and a third output DD beyond BCPALT. **Exit:** arbitrary allocated names open; unallocated names return zero without changing selection; no fixed-name allowlist; **permanent compiled-BCPL regression tests for each newly exposed M1 capability pass under MVS, alongside the unchanged baseline panel**. Standalone assembler probes remain supplementary infrastructure tests, not substitutes for BCPL-level verification.

### M2 — Input stream behavior and multiplicity
Implement independent GET/record cursors, synthetic newlines, EOF, UNRDCH, SELECTINPUT/INPUT, ENDREAD/reopen. Run 3, then 12, then 13+ concurrent independent input streams (13+ verifies we did not merely replace a twelve-slot table). **Exit:** correct data/EOF and interleaving for all streams; cleanup and reopen correct.

### M3 — Output and mixed-stream behavior
Implement independent PUT buffers, SELECTOUTPUT/OUTPUT, WRCH/WRAPOUTPUT, FINDOUTPUT, ENDWRITE, flushing, and mixed read/write interleaving. Preserve SYSPRINT standard output and any existing BCPALT behavior. **Exit:** named outputs receive exactly their own records, including empty/partial-final records under the documented contract; no cross-DD corruption.

### M4 — Failure paths and lifecycle hardening
Test absent DD, invalid/overlength name, DCB OPEN failure after allocation discovery, resource exhaustion (ideally deterministic fault injection), failed selection, duplicate FIND, close/reopen, stale handle, EOF+UNRDCH, FINISH/STOP/nonzero exit. Ensure DCB CLOSE/FREEMAIN correctness and do not suppress MVS diagnostics. **Exit:** documented deterministic outcomes and no leaks/double-close in supported paths.

### M5 — Integration, documentation and acceptance
Re-run entire native regression panel including BLIB/compiler smoke tests; **expand the focused test corpus already begun in M1** under existing `native-compiler/regression` patterns. Validate separate JES DD output attribution using a lossless method (the existing contract warns aggregated printer text cannot prove DD identity). Update stream contract, runtime docs, build/rebuild procedure, and acceptance evidence. **Exit:** all new tests + baseline pass, documented remaining deviations/limits, accepted native dynamic-stream milestone.

## Proposed testing matrix

| Test | Expected evidence |
|---|---|
| Known defaults BCPIN/BCPINB/SYSPRINT/BCPALT | Existing behavior unchanged |
| FINDINPUT("CUSTOMER") with //CUSTOMER | nonzero handle, correct characters |
| FINDOUTPUT("REPORT") with //REPORT | nonzero handle; exact DD-specific records |
| Unknown/unallocated and invalid DD names | zero; selected input/output unchanged |
| 12 simultaneous DD01..DD12 | interpreter-equivalent output and independent handles |
| 13 or 16 simultaneous streams | proves dynamically scalable registry, subject to MVS resource limits |
| Interleave A/B/C reads, EOF, UNRDCH | independent cursor, pushback, EOF |
| Interleave two or more outputs | records never mixed; exact per-DD comparison |
| Duplicate FIND; ENDREAD/ENDWRITE; reopen | documented stable handle/lifecycle behavior |
| FINISH, STOP, abnormal/error path | flush/close/reclaim within stated guarantees |
| Allocation/OPEN failure | predictable return/status; no abend for ordinary failures |
| Blank records, trailing blanks, newline, EBCDIC | matches published record contract |
| Full native regression 00..current end | zero new failures; job/step/output evidence |

Implement tests in the style of the existing numbered native regression directory and its runner, allocating DD statements dynamically in JCL generation as needed. Compare against ICINT's 07-many-streams as a **behavioral reference**; do not presume identical handles or internal object layout. For outputs, use DD-specific captured spool artifacts or another demonstrably lossless extraction, **not** concatenated `prt00e.txt` as sole evidence. Check appropriate assembler/link/go condition codes and failure diagnostics.

## Acceptance criteria

A native BCPL application compiled by our native compiler can request an arbitrary, JCL-allocated DD by name via normal BCPL stream calls; can retain at least twelve simultaneously open ordinary streams (and demonstrate a thirteenth if MVS resources permit); can switch among streams with independent state; and can close/reopen and complete with reliable cleanup. Existing baseline stream/BLIB/compiler regression remains green. The interface remains ordinary historical BCPL, and no native compiler change or extra library extension is required.

## Implementation status after JOB 7065 (MVS 2026-10-17)

The separately linked DEVOBJ candidate has passed compiled-BCPL dynamic
output/input regressions **124–129**, including twelve simultaneous input
DDs, normalized duplicate-FIND identity, and automatic flushing of
unfinished dynamic output buffers at FINISH and STOP(8).
BCPLIO source at commit `8597a88` was assembled and installed in
development-only `BLDDEVI` payload **JOB 7065** (ASMIO/PUTIO RC0000,
zero flagged statements). The operator then ran the complete **00–129**
panel, observing **129 PASS / 0 FAIL / 1 expected SKIP (083)**.

**The M1 DD discovery and installation engineering criteria are satisfied**
for this candidate. The broader dynamic-stream milestone is **not closed**:
the original M2 threshold requires 13+ simultaneous independent streams
and close/reopen semantics, while M4/M5 still require resource failures,
instrumented reclamation, and lossless DD-specific output attribution.
Regression 130 (sixteen concurrent input DDs) PASSED on DEVOBJ; no higher count is planned. Regression 131 (reopen same output DD with a fresh nonrecycled handle) also PASSED on DEVOBJ. The complete 00..131 DEVOBJ panel now PASSED (131 PASS, 0 FAIL, expected skip 083); candidate-only regression 132 also PASSED, demonstrating input-DD close/reopen with fresh stable identity (without reading the reopened DD DATA). The complete 00..132 compatibility sweep is pending. Failure injection, reclamation accounting and lossless DD-specific attribution remain open.
See `Milestone-BCPLIO-dynamic-stream-M1-progress.md` and
`Milestone-BCPLIO-dynamic-stream-M2-progress.md`.

Production `HERC02.BCPL.NATIVE.OBJ` is unchanged; no promotion is
authorized by these test results.

## M2 close gate — complete native regression (MVS 2026-10-17)

**ACCEPTED AND CLOSED.** Development-only BCPLM6 + BCPLIO linked
from `HERC02.BCPL.NATIVE.DEVOBJ` passed the complete
`00..132` compiled-native-BCPL panel: **132 PASS, 0 FAIL,
1 expected SKIP (083), 133 total**. The operator pulled through
`c4f7a8d` before execution. Regressions 130, 131 and 132 passed
within this full run, establishing 16 concurrently open dynamic
input streams and fresh, nonrecycled same-DD output/input handle
identities after ENDWRITE/ENDREAD. Duplicate FIND and stale
selection semantics also passed.

The accepted input-reopen guarantee concerns handle identity and
successful repeated OPEN. The test deliberately does **not**
read a reopened instream `DD DATA` allocation or promise any
QSAM rewind behavior. The full M2 record is
[Milestone-BCPLIO-dynamic-stream-M2-progress.md](Milestone-BCPLIO-dynamic-stream-M2-progress.md).

**This closes only M2**, not the overall dynamic-stream milestone.
M3 mixed input/output and strict physical DD attribution need an
explicit exit review; M4 failure-path/accounting and M5 integration
remain open. Production `NATIVE.OBJ` stays unchanged.

## Following march preparation — M3/M4 (2026-10-17)

Following formal M2 closure, reviewed the parent milestone's
outstanding **mixed-stream** requirement before attempting M4.
Existing dynamic output, duplicate FIND, termination-flush and
reopen behavior have substantial compiled-BCPL evidence.
However, the current combined JES checker cannot independently
prove physical DD attribution. These are different issues.

- [M3 output/mixed-stream review](Milestone-BCPLIO-dynamic-stream-M3-review.md)
  records accepted previous evidence and stages permanent candidate-only
  **regression 133**, two dynamic inputs interleaved with two
  independently buffered named dynamic outputs. **Not yet run.**
- [M4 failure/lifecycle inventory](Milestone-BCPLIO-dynamic-stream-M4-inventory.md)
  maps existing `IONORM`, `DDVERIFY`, `DALLOC`,
  `HNEW`, `DQOPEN`, `DQCLOSE`, `DREL` and
  `IODRAIN` to failure and resource-accounting proof
  obligations. No new M4 tests or runtime changes have run.

Full milestone closure still requires M3 exit evidence,
M4 deterministic failure/resource accounting, and M5
lossless DD-specific physical attribution, documentation,
and final full-panel acceptance. Production OBJ has not been
modified or promoted.


## M3 logical gate accepted, M4.0 staged (MVS 2026-10-17)

The operator pulled repository head through `b25d643` and ran
compiled-BCPL native candidate regression **133** individually,
observing **PASS 1, FAIL 0, SKIP 0, TOTAL 1**. It exercises two
concurrently open dynamic DD DATA input streams and two independent
dynamic SYSOUT output buffers with repeated read/write switching.
No runtime source or installed objects changed. The established
**full** DEVOBJ panel remains `00..132` at 132 PASS / 0 FAIL /
expected SKIP 083; a full 00..133 pass has not yet been submitted.

The M3 *logical functional* gate is now demonstrated. The complete
M3 physical DD-integrity claim and M5 final exit remain open
until lossless DD-specific JES2 SYSOUT attribution has been
implemented and verified. Do not equate combined-JES logical
record matching with proof of physical DD association.

A new permanent candidate-only test **134** is staged at
`native-compiler/regression/134-dynamic-dd-invalid-name-preservation/`.
It verifies invalid/overlength/absent DD-name FIND failures are
zero-valued and non-destructive to selected streams; it has
**not** yet run under MVS. See
[M4 failure/lifecycle inventory](Milestone-BCPLIO-dynamic-stream-M4-inventory.md).
M4 fault injection, CLOSE/FREEMAIN accounting and M5 physical
record attribution still await acceptance. No DEVOBJ-to-OBJ
promotion is authorized.


## M4.0 validation after M3 mixed-mode regression (MVS 2026-10-17)

The operator pulled through `3678e54` and ran the permanent
compiled-BCPL candidate regression **134**, observing
**PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**. The test exercises
five invalid or unallocated DD names through both FINDINPUT and
FINDOUTPUT, checks their zero returns, confirms preservation of
selected input/output handles and an independent input cursor,
and verifies subsequent valid normalized duplicate FINDs.
This **accepts M4.0 ordinary negative-name behavior**. It is not
evidence for true QSAM OPEN error recovery or resource exhaustion.

Regressions **133 and 134 both passed individually** against
unchanged DEVOBJ(BCPLM6 + BCPLIO), with no rebuild.
The complete accepted compatibility panel remains `00..132`;
the next required full checkpoint is `00..134`, expected
**134 PASS, 0 FAIL, 1 expected SKIP 083, TOTAL 135**.

Following this checkpoint, M4 requires design and isolated
instrumentation for conditional GETMAIN failure, QSAM OPEN failure,
matching FREEMAIN / CLOSE accounting and termination cleanup.
M5 still owns lossless physical DD attribution and final
integration acceptance. Neither candidate object promotion nor
overall milestone closure is authorized.

## M4.1 — explicit deferral and fault-injection development (2026-10-17)

**Owner decision:** Defer the full native `00..134` compatibility
panel and proceed directly into **M4.1 deterministic
allocation-failure verification**. The last accepted full panel
remains `00..132` (132 PASS, no FAIL, source-only SKIP 083).
Focused tests 133 and 134 both passed individually. The
deferral is intentional, neither a failure nor a completed
compatibility gate. Do not promote PDS members or close the
parent milestone on the strength of the targeted tests alone.

M4.1 now has a [complete source-transform, test-only JCL and
acceptance plan](Milestone-BCPLIO-dynamic-stream-M4.1-plan.md):
strict test-only copy of canonical BCPLIO, inline assembly
into a temporary `&&IOOBJ` object, linked with existing
development `BCPLM6` and all other normally installed
objects. The standalone mode-based generator deterministically
fails the second GETMAIN invocation at each of the 32-, 268-,
and 16-byte dynamic-stream allocation points. Permanent
candidate-only compiled BCPL cases 135–137 are staged.

**No new MVS evidence for 135–137 exists yet.** Begin with
focused regression **135** and investigate test-only
ASMFIO/LKED linkage results before expanding testing. Installed
DEVOBJ and production NATIVE.OBJ remain unchanged. M4.2 true
OPEN failures, M4.3 independent resource accounting and M5
physical DD attribution are still outstanding.


## M4.1 descriptor failure gate — PASS 135

Owner-selected continuation into M4.1 remains in force:
the complete 00..134 compatibility panel is deferred.
The operator pulled through `175fc2e`, passed the
source-only fault-generator checker for all three 32/268/16
modes, then executed targeted regression **135**
under the isolated test-only BCPLIO assembler/link
route. Result: **PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.

This verifies synthetically failed descriptor32 allocation
recovery and subsequent BCPL stream usability under MVS.
It does **not** verify genuine low-memory behavior,
the pending 268/16 tests, or independent resource counts.
No installed runtime object was changed. The next
focused gate is regression **136**, then **137**.
See [M4.1 plan](Milestone-BCPLIO-dynamic-stream-M4.1-plan.md).


## M4.1 second allocation failure gate — PASS 136

The operator pulled through `831ee82` and ran targeted
candidate regression **136** with a temporary instrumented
BCPLIO object. Reported **PASS 1 / FAIL 0 / SKIP 0 /
TOTAL 1**. The tested synthetic 268-byte QSAM-region
allocation failure followed successful 32-byte descriptor
allocation; recovery returned zero, preserved the previously
selected DD01 cursor, and permitted successful DD02 retry.
This is not separate proof of GETMAIN/FREEMAIN accounting
or actual MVS low-storage failure.

**M4.1 status: 135 and 136 individually accepted; 137 pending.**
The owner's full-panel deferral remains in force. No installed
DEVOBJ or production OBJ objects were promoted or modified
by the isolated test harness. M4.2, M4.3 and M5 remain open.


## M4.1 closure — all three targeted allocation failures PASS

The operator pulled through `ccb0f1b` and ran focused
regression **137**, observing `PASS 137` and
**PASS 1 / FAIL 0 / SKIP 0 / TOTAL 1**.
This completes the individually verified, test-only M4.1
synthetic GETMAIN error-path matrix:

- 135: 32-byte descriptor allocation failure — PASS.
- 136: 268-byte QSAM region allocation failure — PASS.
- 137: 16-byte stable-handle allocation failure after
  successful OPEN — PASS.

Each checked zero-valued FIND failure, preservation of an
existing DD01 selected input/cursor, and successful subsequent
DD02 allocation and stream operation. These do not establish
real low-storage exhaustion or independently counted
CLOSE/FREEMAIN calls. **M4.1 CLOSED** for synthetic
fault-path recovery only. The complete regression panel
remains **explicitly deferred by the owner**. The
latest full accepted panel is still 00..132, 132 PASS,
0 FAIL, source-only SKIP 083. No installed PDS objects
or canonical BCPLIO assembler source were changed.

Next milestones: M4.2 QSAM OPEN failure diagnostics,
M4.3 independent resource accounting, and M5 physical DD
output attribution and final integration.


## M4.2 OPEN-failure analysis and staged probe 138

After accepting M4.1's three focused synthetic allocation
failure tests (135–137 PASS individually), inspected
canonical `native-compiler/asm/bcplio.asm` for
`DQOPEN` SVC19 return and `DIFIND`/`DQFIND`
cleanup handling. MVS OPEN can sometimes leave an
unopened DCB and continue, but other DCB/mode errors
may produce an x13 system abend. A genuine host
failure is therefore not interchangeable with a
synthetic nonzero return from DQOPEN.

The [M4.2 contract and test plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md)
distinguishes these cases. Permanent regression **138**
is now **STAGED ONLY** with a development-only, temporary
BCPLIO assembled into the GO JCL; its second
DQOPEN attempt returns nonzero before SVC19, and a
third attempt performs normal SVC19. This checks the
nonfatal cleanup/retry branch but **does not** establish
how MVS 3.8J responds to a real incompatible-DD OPEN.
A separate exploratory real-OPEN failure gate and
M4.3 resource accounting remain required.

Nothing has been rebuilt or promoted in installed
`DEVOBJ` or production `OBJ`. The owner's full
native regression deferral is still in effect.


## M4.2 synthetic OPEN failure case — PASS 138

After pulling through `5c890d3`, the operator accepted
the host-side source transformer check for private synthetic
pre-SVC19 DQOPEN denial and ran compiled-BCPL regression
**138** with the isolated test-only BCPLIO object. Outcome:
**PASS 1, FAIL 0, SKIP 0, TOTAL 1**.
The failed FIND returned zero, retained a previously
selected input stream and cursor, and permitted successful
retry. This completes **M4.2.0 only**.

The denial is generated **before SVC19**; no genuinely
unsuccessful QSAM OPEN has yet been demonstrated, and
S013/IEC/IEF behavior under MVS 3.8J remains uncharacterized.
M4.2.1 and M4.3 still require separate diagnostic evidence.
The owner's full-panel deferral remains in force, with
the most recent full acceptance 00..132. No installed
development or production runtime PDS member was changed.


## Real QSAM OPEN diagnostic — separate M4.2.1 probe STAGED

After focused synthetic DQOPEN branch test 138 PASS,
staged a **separate non-regression real OPEN diagnostic**
under `native-compiler/probes/m42-real-open/`.
A standalone `RG890R` GO job can be regenerated
from the Cambridge BCPL source. It links the **normal
installed DEVOBJ(BCPLM6 + BCPLIO)** without a synthetic
fault and supplies `DD02 DD SYSOUT=*` while compiled
BCPL requests `FINDINPUT("DD02")`.

The staging includes a non-submitting deck generator and
source-only JCL guard. This experiment deliberately
allows an MVS S013 or other system abend as a possible
diagnostic outcome; it does **not** designate an abend
as a regression PASS. It can also return zero before
SVC19 at RDJFCB, so diagnostic causation must not be
assumed. **No source checker execution, generated-deck
build, real GO job, or SVC19 failure result has been
reported yet.** The operator must review JCL before
submitting and preserve exact JES/IEC/IEF diagnostics.
See [M4.2 plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md).
The full native regression panel remains owner-deferred.


## M4.2.1 Cambridge compilation and exploratory JCL — PREPARED

After pulling to `ab44dad`, the operator completed the
standard Cambridge compilation, `JOB 7873`, saving
`workarea/m42-real-open/generated.s370.asm`. The
DEVOBJ/BCPLM6 candidate JCL generator then reported
successful construction of
`workarea/m42-real-open/real-open.jcl`.
The generator printed `DD01=DATA; DD02=SYSOUT` and
reported no JES submission of the exploratory deck.
**This is a preparation checkpoint only.**
The real `RG890R` GO job has **not** been run,
and actual QSAM OPEN/IEC/IEF/S013 behavior remains unknown.
Do not confuse Cambridge `JOB 7873` with the GO job.
The user-directed full regression deferral is unchanged.


## M4.2.1 exploratory MVS GO job — JOB 7874 RC0000

The owner submitted the prepared `RG890R`
real-OPEN exploration as **JOB 7874**. The reported
JES step summary was IFOX00 `ASMAP RC0000`,
IEWL `LKED RC0000`, GO `RC0000`; job SUCCESS,
highest RC0000, no abend reported. The operator
saved the complete report as
`workarea/m42-real-open/real-open-report.txt`,
but its contents have not yet been provided.

This normal outcome is a useful diagnostic checkpoint,
**not proof that a genuine incompatible QSAM OPEN
reached SVC19 or returned gracefully**. RDJFCB
can reject DD02 earlier. Actual program markers
and IEC/IEF diagnostics must be read before an
M4.2.1 disposition. M4.3 and M5 remain open;
the complete native regression panel remains
owner-deferred.


## M4.2.1 complete JOB 7874 report — unexpected successful handle

The owner supplied `workarea/m42-real-open/real-open-report.txt`
for `RG890R` JOB 7874. The report shows
JES2 allocated `DD02 DD SYSOUT=*`, IEWL linked
normal DEVOBJ `BCPLM6` and `BCPLIO`, and
ASMAP/LKED/GO all completed RC0000. The program
printed `M42 BEFORE FIND DD02`,
`M42 DD02 RETURNED HANDLE`, and
`M42 SURVIVED FIND DD02`; no OPEN error or abend
was reported.

`DIFIND` source flow confirms that creating a new
nonzero handle requires `DDVERIFY`, `DALLOC`,
`DQOPEN` (real SVC19), and `HNEW`.
Thus the system did **not reject** this SYSOUT-as-input
OPEN, contrary to the probe's intended failure condition.
The BCPL program did not try to read that handle.
**M4.2.1 actual failed-OPEN acceptance NOT MET; M4.2 stays open.**
Next explore a nonmember, read-only PDS as a QSAM
input DD, preserving exact JES diagnostics.
No canonical BCPLIO or installed object changed.
Full native regression remains deferred.


## M4.2.2 PDS-without-member diagnostic staged

Given that JOB 7874 successfully returned a
`FINDINPUT("DD02")` handle for a SYSOUT-allocated
DD, staged a different read-only QSAM input OPEN
candidate: `DD02 DD DSN=SYS1.MACLIB,DISP=SHR`,
a partitioned dataset **without a member**.
A separate exploratory `RG891R` builder generates
the JCL from the existing Cambridge assembler
produced by JOB 7873; no new compiler job or
canonical runtime source modifications are required.

Full instructions:
[native-compiler/probes/m42-pds-open/README.md](../native-compiler/probes/m42-pds-open/README.md).
The job has **NOT been prepared or submitted on TK5**
and a failing OPEN is not assumed. Record the actual
IEC/IEF/program results before any M4.2 closure.
The full regression panel stays owner-deferred.


## M4.2.2 RG891R exploratory JCL generation successful

Following a fast-forward to `3235115`, the operator ran
the existing DEVOBJ/BCPLM6 non-submitting JCL generator
using the Cambridge assembler produced in JOB 7873.
The generator successfully wrote
`workarea/m42-real-open/pds-open.jcl` with
`DD01 DD DATA` and read-only `DD02 DD
DSN=SYS1.MACLIB,DISP=SHR` (PDS without member).
**RG891R has not been submitted; no real OPEN failure
was measured and no PDS member was changed.**
M4.2 remains open and the full panel deferred.


## M4.2.2 exploratory JOB 7875 — executed without abend

The owner submitted the previously prepared RG891R
read-only `SYS1.MACLIB` without-member QSAM input
OPEN experiment as **JOB 7875**, on 17 October 2026.
The supplied summary reports ASMAP/LKED/GO all
`RC0000`, overall success, and no system abend.
The operator saved the complete JES output as
`workarea/m42-real-open/pds-open-report.txt`,
but it is not yet attached. Until the BCPL diagnostic
records and IEC/IEF messages are reviewed, a zero
`FINDINPUT` versus returned handle, and RDJFCB versus
SVC19 attribution remain unresolved. M4.2 does not
close; full native regression remains owner-deferred.


## M4.2.2 full JOB 7875 result — valid handle, no OPEN failure

The owner supplied the full `RG891R` JOB 7875
JES report for the read-only, no-member
`SYS1.MACLIB` QSAM input candidate. GO
`DD02` was allocated to `SYS1.MACLIB` and
JES records include `390 ALLOCATED TO DD02`.
The compiled BCPL source emitted
`M42 BEFORE FIND DD02`,
`M42 DD02 RETURNED HANDLE`,
`M42 SURVIVED FIND DD02`; GO RC0000
with no IEC OPEN errors or abend.

Together with the earlier SYSOUT-as-input JOB 7874,
**both actual-OPEN exploratory attempts returned handles**.
This does not demonstrate successful GET from either
DD, nor the requested actual OPEN failure recovery.
M4.2 remains OPEN; source-guided candidate for
the next experiment is deliberate incompatibility
of QSAM FB record length and block size at OPEN.
The full regression panel remains owner-deferred;
no canonical runtime or installed objects changed.


## M4.2.3 malformed QSAM FB DCB probe staged

The actual JFCB/OPEN experiments in JOB 7874
and JOB 7875 both returned nonzero DD02
handles despite unconventional allocations,
so no real QSAM OPEN rejection has been
observed. Staged standalone `RG892R`,
a third **non-regression** JCL probe with
`DD02 SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)`.
For QSAM FB this block length is not a
multiple of record length (a potential S013-20
OPEN-time error). The result remains to be
observed; JCL/DD validation might reject it
before OPEN. Existing compiled BCPL output
is reused; no canonical runtime objects
are changed. See [M4.2 plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md)
and [RG892R procedure](../native-compiler/probes/m42-fb-open/README.md).
The full native regression panel is still
owner-deferred.


## M4.2.3 malformed-FB exploratory job — JCL prepared

Operator pulled through `19e658a` and successfully
created `workarea/m42-real-open/fb-open.jcl`
for `RG892R`: DD02 SYSOUT with FB LRECL 80,
BLKSIZE 81. The builder confirmed the GO deck
**was not submitted** and no installed PDS object
was changed. No JCL/OPEN outcome is claimed.
Single exploratory GO execution and JES evidence
are pending; M4.2 remains open. Owner-deferred
native regression remains deferred.


## M4.2.3 actual RG892R/JOB 7876 — third returned handle

The owner supplied the complete RG892R JOB
7876 spool with intentionally inconsistent
`DD02 SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=81)`.
JES allocated DD02, IFOX/IEWL/GO all RC0000,
and the ordinary development BCPLIO was linked.
Compiled BCPL printed
`M42 BEFORE FIND DD02`,
`M42 DD02 RETURNED HANDLE`, and
`M42 SURVIVED FIND DD02`.
No OPEN error/abend or successful GET
from the DD02 handle was demonstrated.

The three real-OPEN DD-allocation probes
(7874 SYSOUT, 7875 nonmember PDS,
7876 invalid FB SYSOUT) all returned handles,
so **none met M4.2 actual failed-OPEN gate**.
The next step is a source-only historical DCB
layout verification and a tightly scoped,
private BCPLIO SVC19 observability design
before requesting any more operator runs.
No installed runtime or production object
changed. Full regression is owner-deferred.


## M4.2 source-level course correction — period IBM guide

Following JOB 7876's third returned DD02 handle,
reviewed IBM `GC26-3875-0`, the OS/VS2 MVS
Release 3.8 Data Management Services Guide,
June 1979 revision, page 86. Its QSAM printer
device section says FB datasets have DCB block
size normalized to LRECL and are treated as
unblocked F. This provides a credible explanation
for the failure of the malformed FB SYSOUT DD
to provoke an OPEN rejection. It is not a
measured after-OPEN DCB trace.

The next M4.2 gate moves away from arbitrary
JCL allocation mismatches to verification
of historical DCB field offsets and **DD02-only,
test-only** observation immediately around
real SVC19, with normal DD01 as a control.
Review [M4.2 plan](Milestone-BCPLIO-dynamic-stream-M4.2-plan.md)
before staging further execution. Production
and installed candidate object PDS members
are unchanged. The full regression remains
owner-deferred.

## Handoff / next-conversation prompt

We are working in `cbmira01/BCPL-for-MVS`, on **Milestone - BCPLIO dynamic stream**. Treat this document as the scope and march contract. Start with **M0 only**: inspect installed/canonical BCPLMAIN and BCPLIO sources and object/PDS build path; inspect `mr10-kit-compiler/asm/icintv19.asm` dynamic streams (RDJFCB, GETMAIN, descriptor list, OPEN/CLOSE), `native-compiler/asm/bcplio.asm`, `native-compiler/regression/native-stream-contract.md`, and interpreter test `07-many-streams`. Run the current native baseline and record commit, actual tests and evidence. Propose the native ABI-compatible descriptor/ownership design and exact contract of all affected G entry points, error cases, standard streams and record semantics. Preserve the BCPL programmer-facing API, current runtime/BLIB functionality, and ordinary QSAM library separation. Do not implement M1 before M0 review/acceptance. Use `tools/checks/` for reusable repository-owned analysis aids if useful. Keep changes incremental, document evidence and commit each accepted march.
