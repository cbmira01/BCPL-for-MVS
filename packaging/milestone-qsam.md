# Milestone QSAM — native BCPL sequential-record I/O

Status: **Q.0 — Reconnaissance & contract in progress** (latest JES evidence dated 2026-10-20); Q.1 not started. Independent of M4, never a prerequisite for Cambridge self-hosting.

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
| **Q.1 — Linkage & OPEN/CLOSE skeleton** | Link a separate service into a native BCPL program | Candidate `BCPLQSAM` assembler module, optional BCPL wrappers/declarations, 16-slot handle table, OPEN/CLOSE, JCL and first demo | BCPL calls assembler reliably; 3 DDs independently open/close; clean failures; linked extension auto-closes outstanding handles on FINISH/STOP via approved generic finalization; no regression |
| **Q.2 — Fixed logical records** | Make deterministic QSAM GET/PUT useful | RECFM F/FB read/write, bounds and padding rules, copy demo, EOF/error tests, round-trip checks | Byte-accurate read/write and observed EOF; overflow/invalid handle tests; all baseline regressions still pass |
| **Q.3 — Variable logical records** | Safely handle V/VB | RDW handling contract, logical data-length conversions, zero-length/limit behavior, documentation and tests | Variable lengths preserved; RDW not leaked to BCPL unless explicitly designed; error/status checks pass |
| **Q.4 — SYSOUT devices** | Prove non-disk record output | `SYSPRINT` FBA carriage-control demo; `SYSPUNCH` 80-column card-image demo; corresponding JES/JCL evidence | Generated printed and punched records verified, including carriage control and padding |
| **Q.5 — Hardening & release** | Turn experiment into a reproducible optional facility | Regression subset and negative tests, build/clean/rebuild steps, examples, documentation, object promotion decision | Clean-from-Git reconstruction, full native regression, demonstrable optional link-edit; acceptance recorded |

Each march is separately reviewable and committable. Do not start the next until gate evidence is in Git. A genuine blocker can stop the milestone without blocking M4.

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

The [period MVS size limits, allocation-failure, and finalization review](qsam-q0-record-limits-failures-finalization-review.md)
documents general Release 3.8 limits and the accepted BCPLIO `GETMAIN RC` precedent.
It proposes a *generic* optional-module finalizer ordering for owner review;
the R.0 ABI, tested BCPLQSAM record ceiling and exceptional CLOSE semantics
remain open, not approved or implemented.

The [Q.0 design review](qsam-q0-design-review-20261020.md) separates
existing public-interface commitments from proposed implementation
policies. The [approved staging and resource-management decision](qsam-q0-staging-resource-design-decision.md)
establishes private per-handle GET/PUT areas, eager checked allocation,
non-recycled handle identities, pending-record retry invariants, and
normal termination cleanup via a generic optional-extension finalizer.
Remaining Q.0 verification includes record-size boundaries, variable
zero-data-length cases, recoverable OPEN/GET/PUT/CLOSE failures, a
demonstration of pending-record retry, exact effective INFO fields,
and the shared Runtime Extensions R.0 registrar/finalizer ABI.
**Q.0 remains open; do not start Q.1 before its gate is reviewed.**

### Detailed test obligations

- Q.1: one/two/three simultaneous DDs, then 16 live handles; open failure (missing DD), read/write mode validation, repeat close, invalid and stale handles after slot reuse, cleanup after partial OPEN; resource accounting and a generic finalizer demonstrating automatic CLOSE on FINISH and STOP(8) without changing the requested termination code.
- Q.2: F and FB records, first/last record, EOF twice, precise length/padding, maximum buffer boundary, undersized buffer, failed writes/read-after-close, empty dataset.
- Q.3: V/VB record lengths (including edge values permitted by MVS), RDW/BDW handling delegated to correct QSAM interface, buffer overrun and status behavior.
- Q.4: SYSOUT print control FBA and conventional 80-byte punch records; distinguish program-supplied control/data from spool presentation.
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
