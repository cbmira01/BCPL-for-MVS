# CO.1 — Two independent native BCPL workers: JOB 5362/5363 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026, Louisville local date  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** (bounded two-worker positive path)  
**Disposition:** Isolated candidate PASS; CO.1 production design gate OPEN; CO.2–CO.5 NOT STARTED.

## Exact source revision and operator receipt

The owner successfully fast-forwarded their WSL checkout to GitHub
`main` at `0ec7d868a146889309a1ae42f3d2a37a7d3d2ed0` and
executed `tools/coroutines/run-co1-bcpl-two-workers.py --run`.

The owner-reported output:

```text
Git pull RC=0
HEAD=0ec7d868a146889309a1ae42f3d2a37a7d3d2ed0
CO.1 BCPL PASS: compiler JOB 5362, GO JOB 5363; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-two-workers/20261114T002045Z-xpgnb44v
CO.1 two-worker native runner RC=0
```

The evidence directory has a UTC date of 14 November; the local
Louisville date at submission was 13 November. Detailed printer and
JES receipts were not separately provided for inspection, so the
step return codes are attributed to the runner's validated PASS
assessment and the owner's report, rather than independent parsing
by the assistant.

## Native acceptance oracle

The two-worker wrapper substitutes only the BCPL source fixture in
the established `run-co1-bcpl-switch.py` workflow. The runner
requires successful resident Cambridge compilation, a correct
`CO1BGO` JES job identity, `JOB RESULT: SUCCESS`, highest
RC=0000, and all five steps `ASMA`, `ASMM`, `ASMS`, `LKED`,
`GO` present and individually RC=0000. It matches exactly:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The tested BCPL source uses two separately allocated
`GETVEC(1087)` worker stacks and two 24-word descriptors. Worker 1
receives 7, yields 101, and remains suspended while the root
initializes worker 2. Worker 2 receives 8, yields 202, and is suspended.
The root resumes worker 1 with 11 and worker 2 with 22.
The workers check independent local sentinels (3101 and 4202)
and return 31 and 42 naturally, with the root checking both return
values and its own local sentinel. These checks are required before
the final `PASS` record.

This establishes that the current isolated `CO1INIT` and
`CO1SW` implementation can support **two simultaneously live
worker contexts in this cooperative interleaving**, including
initializing a second worker while the first is suspended,
restoring their independent stack/register state, and resuming each
to normal return.

## Scope of qualification and next design gate

The real native execution uses the same separately assembled
`CO1CHG` tested previously under JOB 5358/5359, privately assembled
tracked `BCPLMAIN`, and read-only accepted `BOOT_OBJ` members.
JCL creates only temporary object/load datasets. This is a
**candidate baseline promotion in evidence**, not installation or
promotion of any Core Runtime object, public global numbers, or
released ABI.

Two workers are not arbitrary many; the test does not cover nested
worker-to-worker switches, descriptor validation, terminated-worker
re-entry, deletion/reuse, error recovery, reentrancy, scheduling,
PSW condition-code guarantees, near-boundary recursion or all
stack/guard cases. The static `CO1SREG` scratch and root/worker
pointers remain deliberately unapproved production decisions.

CO.1 remains **IN PROGRESS** pending an owner-reviewed descriptor,
stack, register, global allocation and lifecycle contract. CO.0 is
CLOSED with qualifications and CO.2–CO.5 remain NOT STARTED.
