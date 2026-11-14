# CO.1 — Native terminated-worker re-entry guard: JOB 5366/5367 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date; UTC evidence on 14 November)  
**Classification:** **OWNER-REPORTED NATIVE-MVS-TESTED**, bounded test-only negative-path behavior  
**Disposition:** Isolated candidate PASS; production ABI and CO.1 closure NOT APPROVED; CO.2–CO.5 NOT STARTED

## Provenance and exact operator receipt

Tested GitHub `main` revision:

`e48dd4c5573c6094a19db3bf99464ffd29d3862b`

The owner reported the following execution from the WSL checkout:

```text
Git pull RC=0
HEAD=e48dd4c5573c6094a19db3bf99464ffd29d3862b
CO.1 BCPL PASS: compiler JOB 5366, GO JOB 5367; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-terminal-guard/20261114T005751Z-0xvovg5a
CO.1 terminal-guard native runner RC=0
```

The successful native runner requires a resident Cambridge compiler
job that emits the System/370 source and a completed native `CO1BGO`
job with `ASMA`, `ASMM`, `ASMS`, `LKED`, and `GO` each RC=0000,
`JOB RESULT: SUCCESS`, and highest RC=0000. It requires exactly:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The detailed compiler listing and JES reports are preserved under the
owner's WSL evidence path but were not provided separately for
independent inspection. No independent claims about specific assembler
diagnostics or machine traces are made beyond the validated runner's
PASS oracle and reported job summary.

## Verified test-only behavior

The isolated assembly variant
`candidates/co1-bcpl-terminal-guard/co1change.asm` adds a
candidate-only state-3 `TERMINATED` marker on natural worker return.
The `CO1SW` entry examines the state of a *known-live* descriptor
before saving the outgoing context or changing the active stack
limits. When that state is 3, the variant returns `-1` to the
BCPL caller through the ordinary `RETIMPL` convention instead of
switching.

The accompanying BCPL program requires: both workers to yield
successfully; worker A to return 31 and have state 3; a second
`CHANGECO` to A to immediately return `-1` without corrupting the
root; worker B, still suspended, to resume and return 42 with state 3;
and a subsequent rejected re-entry of B returning `-1`. The root's
local sentinel is checked after each transition before printing PASS.

That is **NATIVE-MVS-TESTED evidence for this bounded termination
rejection path**, including continued execution of another suspended
worker after a rejected switch. The result is additive to the
single-worker, recursive-frame, two-worker and direct worker-to-worker
positive-path evidence through JOB 5365.

## Design and installation limits

The `TERMINATED=3` state and `-1` failure result are experimental,
not approved public API choices. The guard trusts that the descriptor
is allocated and addressable. It does **not** validate arbitrary
addresses, stale or deleted descriptors, already-active targets,
stack reuse or release, other lifecycle states, ownership, nested
error recovery, reentrancy or the entire register/PSW contract.

The candidate runner uses temporary assembly, link and GO datasets;
accepted `BOOT_OBJ` members are read-only. This run did not install
or promote any Core Runtime object, reserve production BCPL globals,
assign regression IDs, or close any milestone.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
Next work remains an owner-reviewed production descriptor, stack,
register, and lifecycle design before CO.2 implementation.
