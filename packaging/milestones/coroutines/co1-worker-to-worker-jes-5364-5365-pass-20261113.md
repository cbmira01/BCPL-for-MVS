# CO.1 — Direct worker-to-worker native BCPL transfer: JOB 5364/5365 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date)  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** (bounded positive path)  
**Disposition:** Candidate native execution PASS; CO.1 production design gate OPEN. CO.2–CO.5 NOT STARTED.

## Exact tested source and native operator receipt

GitHub `main` tested revision:

`1e7ae65ab97f0272313144946b1eb5714546b1ae`

The owner ran the guarded WSL command
`tools/coroutines/run-co1-bcpl-worker-hop.py --run`.
The reported console output was:

```text
Git pull RC=0
HEAD=1e7ae65ab97f0272313144946b1eb5714546b1ae
CO.1 BCPL PASS: compiler JOB 5364, GO JOB 5365; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-worker-hop/20261114T003613Z-6asqe2ka
CO.1 worker-hop native runner RC=0
```

The UTC evidence folder is dated 14 November; the owner's Louisville-local
session was 13 November. Full compiler/JES printer reports remain on
the owner's WSL filesystem; the assistant has not independently
examined those reports. The job numbers and step summary above are
taken from the owner's actual runner output. The validated runner
requires successful Cambridge compilation, five native JES steps
(`ASMA`, `ASMM`, `ASMS`, `LKED`, `GO`) each RC=0000, completed
`CO1BGO` identity and success, highest RC=0000, and the exact
ordered GO records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

## Behavior established under MVS

The isolated application allocates independent private stacks and
descriptor vectors for workers A and B, and initializes both while
the root is active.

- Root starts A with 7; A prints `A1` and transfers directly to B
  with 17, without an intermediate root return.
- B validates its creation-parent pointer (the root), prints `R1`
  and transfers directly back to A with 23.
- A resumes at the outstanding `CHANGECO`, validates value 23 and its
  local sentinel (3101), prints `A2`, then yields 33 to the root.
- The root validates 33 and sentinel 2718, prints `R2`, and resumes
  B with 55. B validates its local sentinel (4202) and resumes to
  natural return 42.
- The root then resumes A with 44; A validates its sentinel and returns
  31 naturally. The root checks both worker results before `PASS`.

The successful execution therefore provides **NATIVE-MVS-TESTED**
evidence for direct A → B → A context switching, preservation of
continuations and live local variables across such transfers, and
subsequent ordinary compiler-generated BCPL return linkage. The
creation-parent words remain rooted at the original root context;
direct context transfer is not evidence of dynamic parent reassignment.

## Limits and architectural disposition

The working source is a test-only `CO1CHG` and BCPL candidate using
fixture-local G!295–G!299; these globals and the 24-word descriptor are
not approved production interfaces. `CO1SW` retains its private
register scratch area and cooperative single-MVS-task limitation.

This PASS does **not** establish arbitrary coroutine scheduling,
parent-chain `CALLCO`/`RESUMECO` semantics, lifecycle, invalid or
stale descriptor recovery, deletion/reuse, reentrant operation,
complete PSW/register-state policies, or near-boundary stack guards.

The runner assembled temporary native objects and a load module with
the installed `BOOT_OBJ` read-only. No installed Core Runtime object,
Global Number Registry allocation, or numbered regression was
promoted.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
The next engineering gate is the owner-reviewed production native
ABI/stack/descriptor/lifecycle contract, not further promotion of the
experimental interface without that approval.
