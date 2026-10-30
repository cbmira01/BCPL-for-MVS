# Milestone QSAM — native BCPL sequential-record I/O

**Current status (30 October 2026): Q.4 — SYSOUT devices IN PROGRESS.** Q.3 — Variable logical records remains CLOSED, with native acceptance and 00–174 full production regression evidence in the [Q.3 closure](qsam-q3-closure-20261030.md). The owner ran the [Q.4 FB80 SYSPUNCH demonstration](qsam-q4-punch-evidence-20261030.md): compiler JOB 7725 and native IFOX/IEWL/BCPL/independent-verifier JOB 7726 passed, with three expected class-B punch card images plus one blank separator confirmed by the 172-byte ASCII capture. The owner also ran the Q.4 FBA133 printer demonstration: compiler JOB 7727 and native IFOX/IEWL/BCPL/independent-verifier JOB 7728 passed, with observed ASA spacing and page eject in the Hercules class-A ASCII printer capture; see the [FBA evidence](qsam-q4-fba-evidence-20261030.md). Numbered QUERY regressions 163/170 and FBA case 176 have passed the first focused native Q.4 panel. Punch case 175 completed native BCPL/IFOX/IEWL successfully in JOB 7755 but the class-B writer was PAUSED; after operator `$S PUN1`, JES2 delivered the exact 172-byte capture and purged the job. The focused runner originally reported 13 PASS/1 FAIL before that delayed delivery; the full panel was correctly skipped. Fresh focused/full acceptance with explicit writer control remains **PENDING**; see the [Q.4 numbered punch incident](qsam-q4-numbered-punch-incident-20261030.md). Q.4 and Milestone QSAM remain OPEN. Q.5 — Hardening & release remains future. BCPLQSAM is a temporary source-mode optional System Extension; no permanent MVS object was installed. Older dated Q.0/Q.1/Q.2 notes below remain historical.

## Purpose and historical positioning

Create an optional, understandable native MVS 3.8J QSAM extension, provisionally named `BCPLQSAM`, callable from programs compiled with the *current native compiler*. It provides sequential *logical-record* access to DDNAMEs through an assembler service and a documented BCPL API. It is a new MVS extension, **not** claimed to be recovered historical Cambridge support. VSAM is excluded.

Why now: 124 native regression cases already exercise a substantial compiler/runtime baseline (the recorded M3 acceptance was 123 PASS, 0 FAIL, 1 expected SKIP). This is a bounded end-user interoperability demonstration: assembler procedure linkage, global-vector publication, handles, errors, fixed/variable record handling and SYSOUT, without affecting M4's self-hosting work.

## Optional module integration dependency

The proposed [Milestone Runtime Extensions](milestone-runtime-extensions.md) defines shared link-edit selection and global-vector registration. Once accepted, BCPLQSAM should use it instead of implementing an independent registry. Q.0 may proceed with ABI exploration before that work, but automatic optional registration needs a separately verified shared mechanism. Neither milestone blocks M4.

### Shared optional-module dispatch architecture

See [Milestone Runtime Extensions](milestone-runtime-extensions.md). The preferred R.0 design is *one* global-vector slot for a BCPLQSAM dispatcher with package-local stable opcodes, beginning with **opcode 0**, a side-effect-free numeric API/capability query into caller-owned BCPL words. The named OPENREC/READREC/WRITEREC/CLOSEREC placeholders below are conceptual services, not callable public global numbers; the actual API is the [QSAMSVC dispatcher](bcplqsam-public-interface.md). G!200 is now assigned to `QSAMSVC` in the [Global Number Registry](global-number-registry.md); package-local opcodes remain subject to Q.0 validation. A query reporting support for a record operation does not guarantee that a DD is allocated or OPEN succeeds. Keep any historical `READREC`/`WRITEREC` `LIBHDR` contracts distinct.

## Non-negotiable architecture

- Keep `BCPLMAIN` as coordinator and preserve `BCPLIO` character-stream semantics; do not rewrite BCPLIO to depend on QSAM. Add a separate, selectively linkable `BCPLQSAM` and, only if necessary, minimal startup/global registration integration consistent with the *actual* ABI.
- Use the current repo manifest and tooling: `config/dspal.yaml`, `tools/datasets/dspal`, `NATIVE_*`. Do not revive superseded `HERC02.BCPL.OBJ` or legacy SOURCE/JCL/DEVOBJ commands. Do not modify CAMB_* in this milestone.
- Git source is authoritative. Object decks, generated JCL, listings and dataset contents are rebuildable, not migrated. Candidate objects stay in `BOOT_DEVOBJ` until separately accepted. Never silently replace accepted `BOOT_OBJ`.
- Determine and document existing native BCPL->assembler call/return, parameter representation, pointer/byte-address rules, register discipline, global-vector allocation/initialization, and module-link behavior **before** allocating numbers or writing entry stubs.
- Avoid hidden compiler changes, dependence on unreconstructed M4 components, new background processes, or broad refactoring.
- Target a table of **16 concurrently open handles** initially, private to BCPLQSAM, with a handle encoding/table organization that can expand without API change. Validate stale/invalid handles. DDNAME is a dataset allocation name, not necessarily the handle and not necessarily a unique open dataset.
- The actual BCPL API must follow the native compiler's tested string/buffer conventions; do not pass the address of a BCPL string literal as though it were a raw byte buffer. Establish bounds, word-vs-byte length, EBCDIC and padding rules explicitly.

## Public API — Q.0 reviewed design, native verification pending

```text
OPENREC(ddname, mode)                  -> positive handle, or failure
READREC(handle, buffer, capacity)      -> logical data length, EOF, or error
WRITEREC(handle, buffer, length)       -> status / actual length by contract
CLOSEREC(handle)                       -> status
RECSTATUS(handle or last-operation)    -> detailed status, if needed
```

The public dispatcher `QSAMSVC:200` is allocated in the [Global Number Registry](global-number-registry.md). The reviewed [BCPLQSAM Public Interface Specification](bcplqsam-public-interface.md) defines the explicit opcode, mode, record-format and error constants, request/result vectors and QUERY layout. Execution and MVS 3.8 limits still need Q.0 verification. Prefer a separate BCPL declarations/manifest header and explicitly installed global entries. Do not presume linking an object automatically installs global slots. Define an unambiguous status scheme for EOF, zero-length logical records, oversize records, open failures, and EODAD/SYNAD or equivalent exceptional completion. Make close failure observable. Do not conflate a valid zero-length record with EOF. Define handling for all partially opened resources and DD allocation errors.

DDNAME contract: eight-character uppercased/padded DDNAME, explicit allowable characters and validation. DDs are allocated in JCL; no dynamic allocation in milestone. Describe file mode and close behavior. Reserve control-block storage in the assembler module; expose only opaque handles and BCPL buffer pointers. Protect against writing beyond capacity. Decide reentrancy/serial use clearly; no unverified claims of reentrancy.

## March roadmap and acceptance gates

| March | Objective | Concrete deliverables | Gate to close |
| --- | --- | --- | --- |
| **Q.0 — Reconnaissance & contract** | Verify the actual native runtime/linkage and MVS QSAM constraints | API/ABI spec, global-number allocation plan, buffer/string representation, DCB/DDNAME and error semantics, examples, test matrix, MVS 3.8 references | Evidence-backed design approved; no speculative ABI or record-size claims |
| **Q.1 — Linkage & OPEN/CLOSE skeleton (CLOSED, 28 Oct 2026)** | Link a separate service into a native BCPL program | Candidate `BCPLQSAM` assembler module, optional BCPL wrappers/declarations, 16-slot handle table, OPEN/CLOSE, JCL and first demo | Owner-narrowed gate: native BCPL linkage, three F1024 DDs, 16-handle lifecycle, output OPEN/INFO/CLOSE and normal FINISH 16-CLOSE accounting; ordinary negatives, independent STOP cleanup and full regression explicitly deferred, not marked PASS (see closure record) |
| **Q.2 — Fixed logical records (CLOSED, 29 Oct 2026)** | Make deterministic QSAM GET/PUT useful | RECFM F/FB read/write, bounds and padding rules, copy demo, EOF/error tests, round-trip checks | Byte-accurate read/write and observed EOF; overflow/invalid handle tests; all baseline regressions still pass |
| **Q.3 — Variable logical records (CLOSED, 30 Oct 2026)** | Safely handle V/VB | RDW handling contract, logical data-length conversions, zero-length/limit behavior, documentation and tests | Variable lengths preserved; RDW not leaked to BCPL unless explicitly designed; error/status checks pass |
| **Q.4 — SYSOUT devices** | Prove non-disk record output | `Q4PRINT` FBA carriage-control demo (separate from BCPLIO `SYSPRINT`); `SYSPUNCH` 80-column card-image demo; corresponding JES/JCL evidence | Generated printed and punched records verified, including carriage control and padding |
| **Q.5 — Hardening & release** | Turn experiment into a reproducible optional facility | Regression subset and negative tests, build/clean/rebuild steps, examples, documentation, object promotion decision | Clean-from-Git reconstruction, full native regression, demonstrable optional link-edit; acceptance recorded |

Each march is separately reviewable and committable. Do not start the next until gate evidence is in Git. A genuine blocker can stop the milestone without blocking M4.

**Owner revision, 28 October 2026:** [Q.1 CLOSED](qsam-q1-closure-20261028.md) by an explicit exception to its earlier clean-failure, STOP-accounting and no-regression prerequisites. [Q.2 OPEN](qsam-q2-kickoff-20261028.md). Those unfinished checks remain declared regression/hardening obligations, not passing Q.1 evidence. No new native job, MVS installed-dataset change or Q.2 implementation is implied.

### Q.0 execution evidence and remaining gate (2026-10-19)

The [test-only G!200 dispatcher ABI probe](../bootstrap-toolchain/probes/q0-dispatcher-abi-probe/README.md) **passed** with owner-provided JES evidence:
[Q.0 dispatcher ABI evidence](qsam-q0-dispatcher-abi-evidence-20261019.md).
The demoted Cambridge compiler produced the BCPL caller in **JOB 2156**.
**JOB 2157** independently assembled the caller and Q0DISP (IFOX RC=0000
each), link-edited with accepted BOOT_OBJ members (IEWL RC=0000), and
executed (GO RC=0000; the BCPL test printed `42`). This demonstrated
R7/R8/R9, BCPL word-pointer vectors, G!200 at displacement 800, QUERY,
and correct return to BCPL. The test-only generated-trailer export is
**not** the Runtime Extensions registrar.

The standalone [FB80 QSAM GET/PUT probe](../bootstrap-toolchain/probes/q0-qsam-fb80-probe/README.md)
**passed on MVS/TK5 in JOB 2159** (ASM, LKED and GO each RC=0000).
The [JOB 2159 evidence](qsam-q0-fb80-evidence-20261020.md) records two
80-byte logical records, preserved blank bytes and trailing markers,
QSAM OPEN/GET/PUT/CLOSE and EODAD. JOB 2158 was rejected for JCL errors
before execution. Because JOB 2159 read a JCL DD DATA stream and wrote
SYSOUT, it did **not** prove physical deblocking of an FB DASD dataset.

The [standalone DASD QSAM probes](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/README.md)
have now **passed** on MVS/TK5: **JOB 2160** (FB80 DASD, 23 records,
BLKSIZE=800), **JOB 2161** (RECFM=V, 15 variable records), and
**JOB 2162** (RECFM=VB, 15 variable records). All six steps in
each job returned RC=0000; the independent readers emitted the
expected PASS records. See [JOB 2160–2162 execution evidence](qsam-q0-dasd-evidence-20261020.md).
These experiments establish supported behavior at the tested record
sizes, **not** an unrestricted MVS record-size limit.
The [four fixed-record boundary tests](qsam-q0-fixed-boundary-evidence-20261020.md)
subsequently passed: JOB 2163 (F80), JOB 2165 (F1024), JOB 2166
(FB8K) and JOB 2167 (FB16K), all six steps RC=0000. JOB 2164
failed in IFOX before correction and is recorded separately.
The [corrected probe source](../bootstrap-toolchain/probes/q0-qsam-boundary-probes/README.md)
is in Git. Q.0 remains open, and Q.1 has not started.

The [zero-payload V/VB DASD evidence](qsam-q0-zero-record-evidence-20261020.md)
records **JOB 2168 (VZERO)** and **JOB 2169 (VBZERO)**, both PASS with
six RC=0000 steps and independent readback of fifteen logical records.
Record 15 contained a four-byte RDW and zero data bytes; EODAD occurred
after that record. This establishes the tested QSAM zero-payload behavior,
not a completed BCPLQSAM READ implementation.

The [Q.0 non-opening DD inquiry evidence](qsam-q0-dd-inquiry-evidence-20261020.md)
records **JOB 2170 / QS0DDCHK**: ASM/LKED/GO all RC=0000;
RDJFCB R15=0 for allocated QPRES and R15=4 for unallocated QMISS,
with neither DD opened. The [incompatible-OPEN negative experiment](qsam-q0-open-incompatible-evidence-20261020.md)
**JOB 2171** ended with **S013-20** at QSAM OPEN for temporary
FB80/801 geometry; ASM/LKED both RC=0000. MVS did not return a
recoverable result to the caller. The [Q.0 JFCB geometry and empty-EOF evidence](qsam-q0-geometry-empty-eof-evidence-20261020.md)
records **JOB 2172 / QS0GEOM** (ASM/LKED/GO all RC=0000) and
**JOB 2173 / QS0EMPTY** (all six ASM/link/run steps RC=0000).
JOB 2172 validated non-opening RDJFCB JFCB fields for FB80/800
and FB80/801 and rejected the incompatible allocation *before OPEN*.
JOB 2173 observed EODAD once on an empty FB80 dataset, with two
application-level read requests but no second QSAM GET. These are
standalone probes, **not an implemented BCPLQSAM READ/OPEN**.
Q.0 remains open.


The [period MVS size limits, allocation-failure, and finalization review](qsam-q0-record-limits-failures-finalization-review.md)
documents general Release 3.8 limits and the accepted BCPLIO `GETMAIN RC` precedent.
It proposes a *generic* optional-module finalizer ordering for owner
review; the R.0 ABI and exceptional CLOSE semantics remain open.
The separate **1024-byte total private stage ceiling is now approved
as an initial implementation policy**, not yet implemented in BCPLQSAM.

The [Q.0 design review](qsam-q0-design-review-20261020.md) separates
existing public-interface commitments from proposed implementation
policies. The [approved staging and resource-management decision](qsam-q0-staging-resource-design-decision.md)
establishes private per-handle GET/PUT areas, eager checked allocation,
non-recycled handle identities, pending-record retry invariants, and
normal termination cleanup via a generic optional-extension finalizer.
The [Q.0 pending logical-record retry evidence](qsam-q0-pending-retry-evidence-20261020.md)
records **JOB 2174 / QS0RETRY**: six MVS steps RC=0000, a valid
private FB80 pending-record retry with unchanged caller buffers on
capacity error, correct record order, and persistent EOF. This was a
standalone assembler test with **static** staging, not a completed
BCPLQSAM READ implementation.

The [Q.0 resource allocation evidence](qsam-q0-resource-evidence-20261020.md)
records **JOB 2175 / QS0RES**: ASM/LKED/GO all RC=0000 and
three successful small conditional GETMAIN acquisitions matched by three
FREEMAIN releases. An injected failure exercised the *explicit*
rollback sequence. The [JOB 2176 / QS0FAIL evidence](qsam-q0-failure-path-evidence-20261020.md)
records ASM/LKED/GO all RC=0000 and the shared ROLLBACK handler with
injected nonzero R15: C-before-B release, surviving A, renewed D and
four acquisitions/four frees. **Neither test caused actual MVS
storage shortage**, nor implemented the public BCPLQSAM API.

The [real conditional GETMAIN refusal evidence](qsam-q0-real-getmain-refusal-evidence-20261020.md)
records **JOB 2177 / QS0NOMEM**: ASM/LKED/GO RC=0000; with
GO REGION=256K a single 1 MiB conditional GETMAIN returned **R15=4**.
The program rolled back its unpublished setup, preserved independent
storage, and resumed small allocations (3 acquired, 3 released, 0 live).
This closes resource-refusal reconnaissance, **not** the Q.0 gate.

The [post-OPEN INFO execution evidence](qsam-q0-post-open-info-evidence-20261020.md)
records **JOBs 2178 / QS0INFV and 2179 / QS0INFVB PASS**: six steps
RC=0000 for each and effective V/VB DCB fields mapped to enum 3/4 and
96 payload bytes at LRECL=100. These are standalone, not public QSINFO.

The [1024-byte stage experiments](qsam-q0-1024-byte-stage-evidence-20261020.md)
**PASSED on MVS/TK5 in JOBs 2180–2182**. The V/VB tests exercised
RDW-inclusive logical lengths 4/16/1024 and the complete 1020-byte
full-record payload; the storage test held sixteen separate 1024-byte
private GETMAIN areas and released them. Based on these results the
owner **approved 1024 total private staging bytes per BCPLQSAM handle**
as the initial implementation limit (F/FB up to 1024 data bytes,
V/VB up to 1020 data bytes). The source/JCL and reproducibility details
are in the [Q.0 probe README](../bootstrap-toolchain/probes/q0-qsam-ceiling-probes/README.md).

The 16-stage test did **not** OPEN sixteen QSAM DCBs or establish a
full-job memory budget. The owner has now separately **approved the
[Q.0 error/finalization policy and concurrent-DCB experiment](qsam-q0-error-and-r0-design-decisions-20261020.md)**.
The [test-only 1/3/8/16 DCB experiments](qsam-q0-concurrent-dcb-evidence-20261020.md)
**PASSED on MVS/TK5 in JOBs 2183–2186**: every ASMWR, ASMRD,
LKWR, LKRD, WGO and RGO returned RC=0000, and each reader emitted
the corresponding QOUT PASS marker. The 16-DCB `Q0H16` job held
sixteen OPEN F1024 DCBs plus sixteen independent 1024-byte stages
under **GO REGION=256K**; the 512K fallback was not needed.
The linked writer and reader operated on independent temporary
datasets, interleaved records and performed normal cleanup.
These are standalone assembler tests, **not** the completed BCPLQSAM
handle-table or an end-to-end BCPL application memory budget.
The shared Milestone Runtime Extensions
[R.0 — Evidence and contract review](runtime-extensions-r0-evidence-and-contract-20261020.md)
has started as a source/ABI investigation, not as implementation.
A [candidate exact table/finalizer ABI](runtime-extensions-r0-candidate-binary-abi-20261020.md)
has been proposed **for owner review**, not approved or implemented.
These standalone programs are not production BCPLQSAM acceptance.

Remaining Q.0 verification includes **testing the approved error and
returned-CLOSE ownership rules**, the production INFO mapping,
the complete **BCPLQSAM + core runtime/application** handle budget,
and **confirming the exact R.0 registration/finalizer ABI**. The architectural R.0 model,
reverse finalizer ordering and normal FINISH RC=8 returned-error
policy are now approved; no working implementation exists. The tested GETMAIN R15=4
return, binary boundary data and valid zero-payload V/VB records are
established as standalone MVS evidence, **not** as final BCPL API tests.
The numeric stage ceiling has been decided, not yet implemented.
**Q.0 remains open; do not start Q.1 before its gate is reviewed.**

### Detailed test obligations

- Q.1: one/two/three simultaneous DDs, then 16 live handles; open failure (missing DD), read/write mode validation, repeat close, invalid and stale handles after slot reuse, cleanup after partial OPEN; resource accounting and a generic finalizer demonstrating automatic CLOSE on FINISH and STOP(8) without changing the requested termination code.
- Q.2: F and FB records, first/last record, EOF twice, precise length/padding, maximum buffer boundary, undersized buffer, failed writes/read-after-close, empty dataset.
- Q.3: V/VB record lengths (including edge values permitted by MVS), RDW/BDW handling delegated to correct QSAM interface, buffer overrun and status behavior.
- Q.4: SYSOUT print control FBA via separately allocated `Q4PRINT` and conventional 80-byte punch records via `SYSPUNCH`; distinguish program-supplied control/data from spool presentation.
- Q.5: independent assembly into the right candidate object PDS, optional link-edit with native compiled application and necessary runtime, self-contained rebuild recipe, evidence from actual MVS job outputs; full native regression must remain green (allow only previously documented expected skips).

## Proposed source layout (adjust after reconnaissance)

- `asm/bcplqsam.asm` **or** established runtime-source convention discovered in Q.0.
- `bootstrap-toolchain/qsam/` for BCPL demonstrations, declaration file, tests, and build JCL, if compatible with current layout.
- `packaging/milestone-qsam.md` is the milestone authority; refer to it from `packaging/README.md`.
- Use `tools/checks/` for any investigator/developer-specific disposable checks, without mixing them into official production tooling.
- Document the effective compile–assemble–link–run and `dspal` command sequences from the **live** manifest, never guessed dataset names or commands.

## Out of scope / possible successors

VSAM (ESDS/KSDS/RRDS), PDS directory/member creation and STOW, dynamic allocation, BSAM/EXCP, random positioning, asynchronous/deblocking extensions, transparent conversion of historical BCPL character streams to QSAM, compiler front-end/code generator modifications, and migration of compiled/binary components into M4.

## Handoff instructions for the implementer

1. Read `packaging/README.md`, the clean-room runbook, manifest, current native runtime acceptance records, source and regression harness. Check the current branch/head and working tree where applicable.
2. Start **Q.0 only**. Inventory global slots and runtime ABI; inspect real BCPL data/string representations and assembler linkage; verify QSAM details using contemporary MVS 3.8 documentation and local tests when necessary.
3. Report explicit interface decisions (especially byte buffers, record sizes, return/status contract, initialization/global registration and linkage) and a precise implementation/test map before modifying runtime source.
4. Keep scope independent of M4. Preserve baseline and candidate-object separation, and keep evidence and decisions in `packaging/`.
5. Once Q.0 is accepted, implement one march at a time, compile and test on TK5, record JES job IDs/condition codes and reproducible commands, commit each accepted march. Never claim a test passed without observed output.

## Q.0 current dependency reconciliation and consolidated probe (25 October 2026)

The paragraphs above describing Runtime Extensions R.0 as unimplemented reflect
the **historical 20 October Q.0 evidence state**, not GitHub's accepted
25 October baseline. The approved R.0–R.5 Runtime Extensions marches are now
individually CLOSED; R.1 provides actual BCEX/BCRG version-1 startup
registration, reverse-order finalization and verified FINISH/STOP error
handling. R.4/R.5 provide known-package IEWL/BCX selection and installed
optional-package production patterns. BCPLDEMO and BCPLTIME are the accepted
reference installations. Overall expanded Runtime Extensions milestone owner
disposition remains separate from closure of its individual marches.

The [Q.0 consolidated gate review](qsam-q0-consolidated-gate-review.md)
reconciles the earlier obligations. The [test-only integrated 16-DCB
native BCPL/FINISH/STOP batch](../bootstrap-toolchain/probes/q0-integrated-16-dcb/README.md)
is now PREPARED, **not MVS executed**. It uses the accepted BCEX/BCRG
and Core Runtime without implementing public QSAMSVC:200, altering the compiler
or modifying MVS object PDSes. Historic Q.0 jobs 2157 and 2159–2186 remain
standalone evidence, not a production BCPLQSAM acceptance.

The specific resource-coexistence gate remains subject to the actual batch
JES/IEWL/GO evidence, and returned/exceptional QSAM CLOSE ownership remains
an explicitly acknowledged limitation requiring owner Q.0 disposition and
later implementation validation. **Q.0 remains IN PROGRESS; Q.1 has not
started.** No Q.1 authorization or Q.0 closure is implied by this update.

## Q.1 JOB 6620 scoped integration result (26 October 2026)

The [JOB 6620 evidence record](qsam-q1-job-6620-explicit-go-dcb-evidence-20261026.md) documents all ten
`Q13DD` steps RC=0000, three valid F1024 non-opening JFCB preflights,
three successful OPEN/INFO/CLOSE handles (1–3), expected
`QS_ERR_HANDLE=-7` for repeated CLOSE, and
`BCPLQSAM Q1 THREE DD PASS`. This **opt-in** comparison supplied
explicit GO reader DD geometry. It establishes the three-DD
demonstration only in that configuration; behavior without reader
`DCB=` is unverified. **Owner approved the fail-closed hybrid production geometry policy**
on 26 October 2026: see the [geometry-policy and allocation-identity
review](qsam-q1-geometry-policy-and-allocation-identity-review-20261026.md). The first unfinished gate is determining
the actual allocation identity/volume before an `OBTAIN`-based
fallback. This is design approval, **not** permission to modify
`bcplqsam.asm` or submit JES without a separate reviewed test plan. The native 16-handle, resource
cleanup, FINISH/STOP(8), and regression acceptance gates remain.
**Q.1 remains OPEN and NOT ACCEPTED; do not start Q.2.**

## Current owner disposition — 28 October 2026

**Q.1 — Linkage & OPEN/CLOSE skeleton CLOSED; Q.2 — Fixed logical records OPEN / NOT ACCEPTED.** This supersedes the 25–26 October historical statements above that Q.1 was open and Q.2 must not begin. The owner accepted the documented narrower Q.1 scope and explicitly deferred incomplete negative, STOP-finalizer and full-panel checks. See the [formal Q.1 closure](qsam-q1-closure-20261028.md) and [Q.2 kickoff](qsam-q2-kickoff-20261028.md).
