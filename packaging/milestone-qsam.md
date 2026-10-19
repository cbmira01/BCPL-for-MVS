# Milestone QSAM — native BCPL sequential-record I/O

Status: **proposed, not started** (2026-10-15). Independent of M4, never a prerequisite for Cambridge self-hosting.

## Purpose and historical positioning

Create an optional, understandable native MVS 3.8J QSAM extension, provisionally named `BCPLQSAM`, callable from programs compiled with the *current native compiler*. It provides sequential *logical-record* access to DDNAMEs through an assembler service and a documented BCPL API. It is a new MVS extension, **not** claimed to be recovered historical Cambridge support. VSAM is excluded.

Why now: 124 native regression cases already exercise a substantial compiler/runtime baseline (the recorded M3 acceptance was 123 PASS, 0 FAIL, 1 expected SKIP). This is a bounded end-user interoperability demonstration: assembler procedure linkage, global-vector publication, handles, errors, fixed/variable record handling and SYSOUT, without affecting M4's self-hosting work.

## Optional module integration dependency

The proposed [Milestone Runtime Extensions](milestone-runtime-extensions.md) defines shared link-edit selection and global-vector registration. Once accepted, BCPLQSAM should use it instead of implementing an independent registry. Q.0 may proceed with ABI exploration before that work, but automatic optional registration needs a separately verified shared mechanism. Neither milestone blocks M4.

### Shared optional-module dispatch architecture

See [Milestone Runtime Extensions](milestone-runtime-extensions.md). The preferred R.0 design is *one* global-vector slot for a BCPLQSAM dispatcher with package-local stable opcodes, beginning with **opcode 0**, a side-effect-free numeric API/capability query into caller-owned BCPL words. The named OPENREC/READREC/WRITEREC/CLOSEREC operations below are logical services, not preallocated public global numbers. Neither package global slot nor opcodes are approved yet. A query reporting support for a record operation does not guarantee that a DD is allocated or OPEN succeeds. Keep any historical `READREC`/`WRITEREC` `LIBHDR` contracts distinct.

## Non-negotiable architecture

- Keep `BCPLMAIN` as coordinator and preserve `BCPLIO` character-stream semantics; do not rewrite BCPLIO to depend on QSAM. Add a separate, selectively linkable `BCPLQSAM` and, only if necessary, minimal startup/global registration integration consistent with the *actual* ABI.
- Use the current repo manifest and tooling: `config/dspal.yaml`, `tools/datasets/dspal`, `NATIVE_*`. Do not revive superseded `HERC02.BCPL.OBJ` or legacy SOURCE/JCL/DEVOBJ commands. Do not modify CAMB_* in this milestone.
- Git source is authoritative. Object decks, generated JCL, listings and dataset contents are rebuildable, not migrated. Candidate objects stay in `BOOT_DEVOBJ` until separately accepted. Never silently replace accepted `BOOT_OBJ`.
- Determine and document existing native BCPL->assembler call/return, parameter representation, pointer/byte-address rules, register discipline, global-vector allocation/initialization, and module-link behavior **before** allocating numbers or writing entry stubs.
- Avoid hidden compiler changes, dependence on unreconstructed M4 components, new background processes, or broad refactoring.
- Target a table of **16 concurrently open handles** initially, private to BCPLQSAM, with a handle encoding/table organization that can expand without API change. Validate stale/invalid handles. DDNAME is a dataset allocation name, not necessarily the handle and not necessarily a unique open dataset.
- The actual BCPL API must follow the native compiler's tested string/buffer conventions; do not pass the address of a BCPL string literal as though it were a raw byte buffer. Establish bounds, word-vs-byte length, EBCDIC and padding rules explicitly.

## Provisional API — subject to Q0 evidence

```text
OPENREC(ddname, mode)                  -> positive handle, or failure
READREC(handle, buffer, capacity)      -> logical data length, EOF, or error
WRITEREC(handle, buffer, length)       -> status / actual length by contract
CLOSEREC(handle)                       -> status
RECSTATUS(handle or last-operation)    -> detailed status, if needed
```

Names and global numbers are **unassigned** until ABI review. Prefer a separate BCPL declarations/manifest header and explicitly installed global entries. Do not presume linking an object automatically installs global slots. Define an unambiguous status scheme for EOF, zero-length logical records, oversize records, open failures, and EODAD/SYNAD or equivalent exceptional completion. Make close failure observable. Do not conflate a valid zero-length record with EOF. Define handling for all partially opened resources and DD allocation errors.

DDNAME contract: eight-character uppercased/padded DDNAME, explicit allowable characters and validation. DDs are allocated in JCL; no dynamic allocation in milestone. Describe file mode and close behavior. Reserve control-block storage in the assembler module; expose only opaque handles and BCPL buffer pointers. Protect against writing beyond capacity. Decide reentrancy/serial use clearly; no unverified claims of reentrancy.

## March roadmap and acceptance gates

| March | Objective | Concrete deliverables | Gate to close |
| --- | --- | --- | --- |
| **Q.0 — Reconnaissance & contract** | Verify the actual native runtime/linkage and MVS QSAM constraints | API/ABI spec, global-number allocation plan, buffer/string representation, DCB/DDNAME and error semantics, examples, test matrix, MVS 3.8 references | Evidence-backed design approved; no speculative ABI or record-size claims |
| **Q.1 — Linkage & OPEN/CLOSE skeleton** | Link a separate service into a native BCPL program | Candidate `BCPLQSAM` assembler module, optional BCPL wrappers/declarations, 16-slot handle table, OPEN/CLOSE, JCL and first demo | BCPL calls assembler reliably; 3 DDs independently open/close; clean failures and no regression |
| **Q.2 — Fixed logical records** | Make deterministic QSAM GET/PUT useful | RECFM F/FB read/write, bounds and padding rules, copy demo, EOF/error tests, round-trip checks | Byte-accurate read/write and observed EOF; overflow/invalid handle tests; all baseline regressions still pass |
| **Q.3 — Variable logical records** | Safely handle V/VB | RDW handling contract, logical data-length conversions, zero-length/limit behavior, documentation and tests | Variable lengths preserved; RDW not leaked to BCPL unless explicitly designed; error/status checks pass |
| **Q.4 — SYSOUT devices** | Prove non-disk record output | `SYSPRINT` FBA carriage-control demo; `SYSPUNCH` 80-column card-image demo; corresponding JES/JCL evidence | Generated printed and punched records verified, including carriage control and padding |
| **Q.5 — Hardening & release** | Turn experiment into a reproducible optional facility | Regression subset and negative tests, build/clean/rebuild steps, examples, documentation, object promotion decision | Clean-from-Git reconstruction, full native regression, demonstrable optional link-edit; acceptance recorded |

Each march is separately reviewable and committable. Do not start the next until gate evidence is in Git. A genuine blocker can stop the milestone without blocking M4.

### Detailed test obligations

- Q.1: one/two/three simultaneous DDs, open failure (missing DD), read/write mode validation, repeat close, invalid handle, handle reuse, cleanup after partial open.
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
