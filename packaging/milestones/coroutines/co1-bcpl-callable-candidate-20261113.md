# CO.1 — BCPL-callable native coroutine transfer candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026  
**Owner decision:** The candidate **design direction** was approved on
13 November. The owner separately authorized tested source commits on
GitHub `main` and candidate-only MVS execution. The production CO.1
acceptance gate remains OPEN; CO.2–CO.5 remain NOT STARTED.

## Why this is the next implementation

JOB 5349 proved an isolated assembler-native context switch under MVS
(IFOX 2, IEWL 1, GO 1; root/A1/B1/A2/B2/root), with owner-reported JES
success. It did **not** prove that a compiler-generated BCPL function could
call the switch or execute on an independently checked worker stack.

This candidate is the smallest integrated experiment that addresses those
gaps. It is new native System/370 work, **not an MR10-kit change**. MR10
remains closed and is used only as classified behavioral reference.

## Experiment and its limitations

- Source: `candidates/co1-bcpl-switch/source.bcpl`.
- Separate IFOX routine: `candidates/co1-bcpl-switch/co1change.asm`.
- Resident compiler options: `candidates/co1-bcpl-switch/cambridge-parm.txt`
  (single checked-entry `/CN` control record).
- Runner: `tools/coroutines/run-co1-bcpl-switch.py --run`.
- Offline checks: `tools/checks/test_co1_bcpl_switch.py`.

The test application declares **test-local** G!297 `ROOTCTX`, G!298
`CO1INIT`, and G!299 `CHANGECO`. The runner applies regression-26-style
compiler trailer augmentation to install G!298/299 from a separately
assembled CSECT. These are **not** permanent global allocations, and they
do not change the Global Number Registry. The proposed production
G!204–G!211 allocation remains pending collision audit and acceptance.

The compact **24-word candidate descriptor** is as follows. Pointers in
application-visible fields are BCPL word pointers; machine addresses in
private fields are explicitly identified:

| Word | Meaning |
|---:|---|
| 0 | Candidate state: root active=1, new worker=2 (incomplete lifecycle) |
| 1 | Worker parent, BCPL word pointer |
| 2 | Reserved list link |
| 3 | Owned allocation pointer, BCPL word pointer |
| 4 | Stack base, BCPL word pointer |
| 5 | Safe stack limit, machine byte address |
| 6 | Allocated stack end, BCPL word pointer |
| 7 | First worker procedure address |
| 8–23 | Saved machine R0–R15, 16 fullwords |

**`CO1INIT(root,worker,stack,procedure)`** constructs a synthetic
caller frame and first-entry continuation. Its `stack` must be the
live, exact `GETVEC(1087)` allocation; the 4096-byte safe working area
has 256 bytes of clearance. It paints the working stack and writes the
same `STACKHWM` guard/end markers used by `BCPLMAIN`. The root descriptor
borrows (does not own) the pre-existing `BCPLMAIN` working stack.

**`CHANGECO(value,target)`** accepts value in R7, a valid-live descriptor
word pointer in R8, and returns the resumed value in R7. This low-level
module saves a 16-register image, makes a valid three-word frame for
`RETIMPL` on resumption, restores the incoming image and transfers
through the saved R6. Never-run workers enter the trampoline and call an
actual compiler-generated BCPL `WORKER` procedure with its normal
checked-entry linkage. Natural worker return passes its result back
to root; it does not yet implement permanent termination/re-entry rules.

The S1 installer changes **both** `BCPLMAIN STKLIM` and `BCPLAPT
APLIMIT`, as well as G54 `STACKBASE` and G55 `STACKEND`, before switching
register images. No BCPL call or MVS access method occurs inside that
critical sequence. For candidate linkage only, the runner assembles a
private copy of the *tracked* `BCPLMAIN` source, adding an `ENTRY STKLIM`
directive. The tracked runtime source and installed object remain
unchanged. `BCPLAPT` is linked read-only from the accepted production
library; its installed provenance must match the tracked external
`APLIMIT` design.

**Explicit exclusions:** invalid or stale descriptor safety, general
stack-size selection, allocation rollback, independent worker deletion,
re-entry after natural return, production register-save set and
condition-code contract, hostile stack guard corruption, error recovery,
and the final public coroutine-library ABI. The temporary switch's
64-byte register snapshot requires caller workspace and has not yet
been proved safe at the stack boundary. These are remaining design/
implementation/robustness questions, not accepted behaviors.

## Candidate-only MVS execution path

The runner compiles the real BCPL test via installed Cambridge
`CAMBCOMP`/`ICINT19` (one compiler job), recovers the emitted native
System/370 assembly, builds a separate native job and requires all of:

1. `ASMA` — independently assemble generated BCPL through IFOX00, RC=0.
2. `ASMM` — independently assemble the private BCPLMAIN export copy, RC=0.
3. `ASMS` — independently assemble the new switch module, RC=0.
4. `LKED` — link temporary objects plus read-only `BOOT_OBJ` core
   members (`BCPLIO`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLRGS`,
   `BCPLREG`, `BLIB`), RC=0.
5. `GO` — run the resulting temporary MVS load module, RC=0, emitting
   exactly these ordered records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The runner preserves its compiler log, generated machine source, JCL,
submission report, JES step summary, full job report, source digests,
and machine-readable result in a distinct
`workarea/co1-bcpl-switch/<UTC>/` directory. It prints only a brief
result and evidence path to WSL. It rejects missing or nonzero JES
steps, missing/extra/out-of-order native output and `FAIL` output.

The job uses only `&&` temporary datasets; read-only `BOOT_OBJ` and
`SYS1.MACLIB` inputs are never staged or overwritten. No regression
number is added, no installed core object is promoted, and no public
release contract is changed.

## Evidence classification and decision boundary

At source-commit time: **SOURCE-OBSERVED + ASSISTANT HOST-TESTED**
(Python syntax, fixed-format assembler/JCL cards, trailer adaptation,
stack/continuation invariants, negative acceptance tests and synthetic
end-to-end receipts). **Real BCPL/IFOX/IEWL/GO execution is pending.**
Synthetic job IDs produced by host unit tests are not JES evidence.

The first actual MVS run will be recorded separately, with its actual
JOB numbers, exact IFOX/IEWL/GO RCs and native records; a failure must
be diagnosed from retained real output. No result should be promoted
to accepted production `CHANGECO` until the complete CO.1 design gate
and later CO.2–CO.5 acceptance gates have been explicitly satisfied.

## Post-JOB 5357 candidate safety erratum — 13 November 2026

The original source-commit-time statement that the 64-byte register
snapshot used the caller's BCPL workspace was **not a safe design**.
The owner's actual Cambridge-generated `/CN` listing established a
52-byte WORKER frame with `W=P+24` (28 bytes remaining), and a 256-byte
START frame with `W=P+224` (32 bytes remaining). The original
`STM 0,15,0(15)` wrote 64 bytes at W, crossing either generated frame
boundary. Native JOB 5357 passing does **not** prove frame-bound safety.

The corrective candidate uses `CO1SREG DS 16F`, a private 64-byte
register scratch area within `CO1CHG`, before copying registers to
the outgoing 24-word descriptor. It retains only the necessary
three-word RETIMPL frame in W. See
[CO.1 switch workspace correction](co1-switch-workspace-safety-candidate-20261113.md).
This is a *new unverified candidate* until a fresh real MVS run. The
original historical candidate explanation above remains preserved as
the state at its initial source commit.
