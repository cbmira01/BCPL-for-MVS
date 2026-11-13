# CO.1 — Nested checked BCPL frames across a native context switch

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Date:** 13 November 2026  
**Evidence:** SOURCE-OBSERVED + ASSISTANT HOST-TESTED candidate; real MVS result PENDING  
**Baseline:** GitHub `main` `9b0006423c07dae200dcc3b9b5ee8bb64c459725`

## Baseline promotion boundary

Owner-reported Cambridge compiler JOB **5358** and native JOB **5359**
passed under MVS 3.8J after the `CO1SW` 64-byte workspace overrun was
corrected to use private `CO1SREG` scratch. Their exact accepted candidate
trace was `A1 R1 A2 R2 PASS` with three IFOX RC=0, IEWL RC=0, GO RC=0.
That corrected source is now the **CO.1 verified experimental baseline**.
It is not installed Core Runtime or the approved final coroutine ABI.

## Next isolated experiment

The new `candidates/co1-bcpl-nested/source.bcpl` creates a private
worker stack through `GETVEC(1087)`, calls the already tested
`CO1INIT(root,worker,stack,procedure)` and starts `WORKER` by
`CHANGECO(7,peer)`. Unlike the earlier one-worker example,
`WORKER` calls `DEEP(5)`, maintaining six nested checked BCPL frames
from depth five through zero. The deepest frame:

1. Prints `A1`, yields value 9 to the root, and suspends all six frames.
2. Resumes when the root calls `CHANGECO(10,peer)`; checks the incoming
   value and the deepest-frame sentinel, then prints `A2`.
3. Returns 13; the five live callers verify their own sentinel values
   during recursive unwind and add 1+2+3+4+5, yielding 28.
4. `WORKER` checks that result and returns 11 by its normal generated
   BCPL return linkage, leading the root to print `R2` then `PASS`.

Root also verifies its own local sentinel (2718) after both transitions.
If argument passing, local storage or return propagation fails, the
program prints a distinct failure record and does not satisfy the
complete positive-output oracle.

## Execution and isolation

`tools/coroutines/run-co1-bcpl-nested.py --run` imports the previously
accepted `run-co1-bcpl-switch.py` runner without changing that file.
It substitutes **only** this new BCPL source, keeping the exact tracked
`co1change.asm` and `/CN` compiler option fixture. The native job card,
three independent IFOX steps, IEWL temporary link, native GO step,
read-only installed `BOOT_OBJ`, and strict success oracle are inherited
unchanged. Evidence is separate under `workarea/co1-bcpl-nested/<UTC>/`.

A true PASS requires resident Cambridge compilation, all five native
JES steps at RC=0000, and the exact five ordered records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The wrapper's intentional source-selection adapter avoids modifying or
replacing the accepted baseline fixture. It does not install or
overwrite any permanent MVS datasets. The nested test is new **CO.1
architecture evidence**, not a numbered Bootstrap regression or
production `CHANGECO` implementation. The actual compiler, IFOX,
IEWL and GO results must decide whether any further change is required.

## Assistant checks and outstanding gates

In an isolated workspace, Python syntax checks and **9/9 host-only
tests PASS**. The tests cover ASCII/card lengths, test-local globals,
recursion/sentinel structure, real switch call sites, five ordered
success records, failure records, fixture selection, simulated runner
integration, changed-oracle rejection and mandatory explicit `--run`.
They do not constitute native MVS execution evidence.

The native call/return mechanism still requires owner-reviewed
production decisions for the descriptor and save set, active stack
limits/guards, public globals, lifecycle and invalid-descriptor
behavior. Only the existing one-worker positive path has passed
MVS so far; nested-frame verification is pending.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**

## Post-execution note — JOB 5360/5361 PASS

Owner-reported native MVS execution on 13 November 2026 has now
completed successfully for this exact fixture and runner, using
GitHub `main` `2742a766891b8ac65a0551f0994f42b76388c452`.
Resident Cambridge compiler JOB **5360** and native JOB **5361**
produced the five ordered records `A1 R1 A2 R2 PASS`; the runner
reported three IFOX, IEWL and GO steps all RC=0000, and runner RC=0.
The retained evidence directory is
`workarea/co1-bcpl-nested/20261113T234153Z-sxwgp23i`.
See [the native JOB 5360/5361 evidence record](co1-nested-frames-jes-5360-5361-pass-20261113.md).

This supersedes this note's earlier pending-execution language for the
positive nested-frame test, without changing the candidate or approving
production ABI, general stack safety, error paths, or lifecycle semantics.
