# CO.1 — JOB 5358/5359 native switch workspace correction PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** (isolated corrected candidate)  
**Disposition:** Candidate positive path PASS; production ABI and CO.1 closure **NOT APPROVED**.

## Exact revision and operator evidence

GitHub `main` / tested HEAD:

`70b450b9130dcd378cf1028197494a9d75dcfcb8`

The owner submitted the guarded MVS-facing command from the WSL
checkout. Its output was:

```text
Git pull RC=0
HEAD=70b450b9130dcd378cf1028197494a9d75dcfcb8
CO.1 BCPL PASS: compiler JOB 5358, GO JOB 5359; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-switch/20261113T211053Z-49qph4nh
CO.1 native BCPL runner RC=0
```

The detailed compiler and JES receipts remain under the owner's
`workarea/` path and have not been independently supplied in full.
The source-controlled runner's PASS oracle requires a successful
resident Cambridge compiler run and a matching `CO1BGO` JES job with
all five native steps `ASMA`, `ASMM`, `ASMS`, `LKED`, `GO`
present at RC=0000, `JOB RESULT: SUCCESS`, `HIGHEST RC: 0000`,
and exactly these GO output records, in order:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Thus the **owner-observed MVS evidence** supports successful
compilation, assembly, link-edit and execution of the corrected
one-worker native BCPL coroutine candidate.

## What changed since the previous native PASS

JOB 5356/5357 established the first successful native BCPL coroutine
positive path, but the generated `/CN` call workspaces offered only
28 bytes (WORKER) and 32 bytes (START). The original
`STM 0,15,0(15)` stored 64 bytes at W, beyond either frame. That
source-level overrun invalidated any broader inference of caller
workspace safety from the earlier PASS.

The corrected `CO1SW` is in
`packaging/milestones/coroutines/candidates/co1-bcpl-switch/co1change.asm`.
It saves R0–R15 in module-private `CO1SREG DS 16F`, copies
the image into the outgoing context descriptor, and writes only the
three required `RETIMPL` words at W+0/4/8. It preserves the previous
R0 initialisation fix and the checked-stack limit switching behavior.

Prior to this native run, 14/14 focused assistant-side host checks
passed and the exact assembly blob matched GitHub blob
`8d2cff1b89619733ea2ac82aedacaf18c74dda45`.
JOB 5358/5359 now adds independent target-native positive-path
evidence for that revision, without claiming a formally
verified memory-safety proof.

## Constraints and remaining design work

- The new buffer is **module-private static storage**. Reentrancy,
  independent MVS subtasks, and preemptive use are not supported or
  proven; this candidate is cooperative, single-task only.
- No invalid, stale, terminated or currently active descriptor
  checks or deletion/reuse semantics were verified.
- No near-boundary recursion, stack exhaustion, guard corruption,
  condition-code preservation policy, multi-worker scheduling,
  resource cleanup or complete public coroutine API was tested.
- Test-local globals G!297–299 and the 24-word descriptor are not
  approved production allocations or a frozen ABI.
- The runner used only temporary MVS assembler, linker and GO
  datasets, with installed `BOOT_OBJ` read-only. No installed
  runtime object, regression ID or public release was promoted.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
The next checkpoint is the owner-reviewed native ABI, descriptor,
stack/guard, and lifecycle contract, not a declaration of CO.1
closure. The record makes no request for a repeat native run.
