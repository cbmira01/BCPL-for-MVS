# CO.1 — Native nested-frame coroutine probe: JOB 5360/5361 PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED** (isolated nested-frame positive path)  
**Disposition:** Nested-frame candidate PASS; **CO.1 production design gate OPEN**, CO.2–CO.5 NOT STARTED

## Exact source and operator evidence

The test was submitted against GitHub `main` at:

`2742a766891b8ac65a0551f0994f42b76388c452`

The owner's terminal output:

```text
Git pull RC=0
HEAD=2742a766891b8ac65a0551f0994f42b76388c452
CO.1 BCPL PASS: compiler JOB 5360, GO JOB 5361; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-nested/20261113T234153Z-sxwgp23i
CO.1 nested BCPL runner RC=0
```

The runner `tools/coroutines/run-co1-bcpl-nested.py` imports the
unchanged, previously verified `run-co1-bcpl-switch.py` native runner,
substituting only `candidates/co1-bcpl-nested/source.bcpl`.
The native-switch source, assembler/compiler parameters, private
runtime link and positive output oracle are reused without modification.

The reused runner reports PASS only after successful Cambridge
compilation, JES `CO1BGO` success with highest RC=0000, five distinct
steps (`ASMA`, `ASMM`, `ASMS`, `LKED`, `GO`) each RC=0000, and
the exact ordered output records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

The detailed JES reports, generated assembler and machine-readable
receipt are retained in the owner's WSL `workarea/` path; they have
**not** been independently reviewed in full here. The compiler and
native job numbers above come from the owner's actual runner output.

## Tested BCPL behavior

The checked-entry `/CN` fixture enters `WORKER` with value seven,
then calls `DEEP(5)`. The recursive calls keep **six live `DEEP`
activations**, each with an independent local sentinel.
The deepest frame yields nine to the root, and later resumes with
ten. The program checks the deepest sentinel, emits `A2`, and
unwinds through the other five frames, checking each local sentinel.
The aggregate result is verified as 28 in `WORKER`, which returns
11 naturally to the root. The root checks its own local sentinel
after both transfers.

The observed success establishes this **specific positive scenario**
for context restoration, persistent nested local data and ordinary
generated BCPL return linkage under real MVS. It does not prove
arbitrarily deep recursion, exact high-water or guard behavior,
interleaving among several workers, invalid/stale descriptor safety,
termination/re-entry policies, clean cancellation, storage reuse,
subtask reentrancy or complete compiler/ABI conformance.

## Provenance and disposition

The original single-worker and workspace-corrected native passes
remain documented separately as JOBs 5356/5357 and 5358/5359.
The current experiment is *additional native evidence*, not a
replacement for either baseline or a separately numbered regression.

The installed `BOOT_OBJ` remained read-only; IFOX/IEWL/GO operate
on temporary candidate datasets. No installed Core Runtime object,
Global Number Registry allocation, final `CHANGECO` interface,
release asset, or milestone closure is claimed or authorized.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
Next design review: finalize the production descriptor state/ownership,
register/PSW condition-code policy, active stack bounds and guards,
first-entry/exit lifecycle and public global/callable API before
CO.2.
