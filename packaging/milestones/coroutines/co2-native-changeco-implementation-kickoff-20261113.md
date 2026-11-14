# CO.2 — Native CHANGECO Implementation: kickoff and handoff

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation (**IN PROGRESS**)  
**Date:** 13 November 2026 (Louisville local date)  
**Authority:** [Qualified CO.1 owner acceptance](co1-formal-acceptance-and-co2-transition-20261113.md)  
**Baseline `main`:** `1c42c02b360c933318f85cfb61e6c64b341c58e6`

## Immediate mission

Proceed from the already NATIVE-MVS-TESTED CO.1 IFOX candidates to
an isolated, maintainable **Core Runtime** native `CHANGECO`
implementation for Cambridge-compiled System/370 BCPL applications
on MVS 3.8J. The Cambridge compiler may continue to run under
INTCODE while generating native System/370 assembly.

Implement the smallest production-directed primitive compatible with
the **qualified** CO.1 decisions: valid/live opaque descriptor
precondition (Approach A), independent checked stacks (S1), coordinated
`STKLIM`, `APLIMIT`, G54/G55, full required machine context,
legitimate first activation and natural BCPL return. Keep parent,
library lifecycle, release and comprehensive robustness out of CO.2
unless an isolated mechanism requires them. Do not copy test-local
G!295–299 into the Global Number Registry as public allocations.

## Source and verification starting points

- Governing [milestone](milestone-implement-coroutine-support-for-native-compiler.md)
  and [research/design gates](coroutine-research-and-design-gates.md).
- [CO.1 source investigation](co1-native-abi-and-stack-source-investigation-20261112.md),
  [qualified closure](co1-formal-acceptance-and-co2-transition-20261113.md)
  and latest [JOB 5372/5373 native evidence](co1-generation-token-same-address-jes-5372-5373-pass-20261113.md).
- Working isolated IFOX and BCPL reference:
  `packaging/milestones/coroutines/candidates/co1-bcpl-generation/`.
  Earlier probes and evidence exist under
  `packaging/milestones/coroutines/candidates/`.
- Verified driver model:
  `tools/coroutines/run-co1-bcpl-switch.py`;
  preserve strict completed-JOB, IFOX/IEWL/GO step-RC and native
  output checks, read-only `BOOT_OBJ`, temporary object/load datasets.
- Architecture: `packaging/architecture/runtime-and-library-nomenclature.md`,
  `runtime-contract-v1.md`, `stack-check-contract.md`, and
  `global-number-registry.md`.

## Execution sequence and independent CO.2 gate

1. Audit the last accepted IFOX candidate against native CG370
   generated code, `BCPLMAIN`, `BCPLAPT`, `BCPLMEM` and IFOX/IEWL
   linkage. Explicitly distinguish the verified switch mechanics
   from experimental descriptor/registration/lifecycle APIs.
2. Produce a **separate isolated** CO.2 assembler implementation and
   minimal native BCPL caller. Confirm the register, stack-limit,
   first-entry, suspend/resume and return contracts without altering
   installed objects or assigning a public global slot prematurely.
3. Perform all offline host/source/test checks in the assistant's
   separate workspace and commit exact tested artifacts to GitHub
   `main`. Do not create branches or untracked files in the owner's
   checkout; supply shell command blocks **only** for MVS-facing work.
4. Have the owner run one guarded, compact real-MVS candidate command.
   Require one Cambridge compiler job, the expected independent IFOX
   and IEWL steps at RC=0000, native GO at RC=0000, and a specific
   ordered BCPL behavioral oracle. Retain JES receipts under
   `workarea/` and classify owner-reported evidence accurately.
   Investigate failed MVS results before further design excursions.
5. Verify at least two live contexts, first activation, independent
   stacks and checked limits, nested surviving BCPL frames,
   direct suspend/resume, values, ordinary natural return and
   root stack-bound restoration. Document negative-path limitations.
   Do not infer broader lifecycle/robustness from a positive-path run.

**CO.2 acceptance requires focused owner-reviewed actual MVS
IFOX/IEWL/GO evidence from candidate objects and an explicit separate
acceptance decision.** CO.3–CO.5 remain NOT STARTED.

## Hard boundaries

No changes to historical sources, no installed `BOOT_OBJ` overwrite,
no automatic promotion of test-only globals, no release publication,
no regression renumbering, no MVS subtask/preemptive scheduling.
`CO1SW`, `CO1INIT`, `CO1DROP` and `CO1RES` are research names, not
automatically production ABI names. Preserve native checked entry and
`RETIMPL`; reconcile unsupported condition-code/PSW guarantees
before asserting a full production ABI.

**CO.1 CLOSED (qualified); CO.2 IN PROGRESS; CO.3–CO.5 NOT STARTED.**
