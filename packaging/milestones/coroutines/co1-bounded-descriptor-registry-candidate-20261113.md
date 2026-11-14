# CO.1 — Bounded descriptor registry and invalid-switch guard candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date)  
**Evidence:** SOURCE-OBSERVED and ASSISTANT HOST-TESTED; **native MVS result PENDING**  
**Baseline:** GitHub `main` at `2fd11b2f0a805fb68187eeeebe0698d4a209d437`

## Verified baseline and investigated deficiency

The accepted, owner-reported native JOBs **5366/5367** compiled,
assembled, linked, and executed the isolated terminated-worker guard
variant successfully under MVS 3.8J, with three IFOX RC=0000 steps,
IEWL RC=0000, GO RC=0000 and `A1 R1 A2 R2 PASS`. That candidate returns
`-1` for a known-live descriptor after its worker has returned.

The verified assembly nevertheless executes `L 0,0(2)` on the supplied
context address **before proving that it belongs to a known
coroutine**. A null or arbitrary unregistered BCPL word pointer can
therefore cause an uncontrolled MVS addressing exception instead of a
BCPL-level rejection. The native PASS did not exercise these inputs.

## Minimal, isolated native design

The new candidate is separate from the accepted baseline:

- `candidates/co1-bcpl-registry-guard/co1change.asm`
- `candidates/co1-bcpl-registry-guard/source.bcpl`
- `tools/coroutines/run-co1-bcpl-registry-guard.py`
- `tools/checks/test_co1_bcpl_registry_guard.py`

The `CO1CHG` source keeps the established 24-word descriptor,
`CO1SREG` 64-byte private register buffer, synthetic BCPL return frame,
`STKLIM`/`APLIMIT`, G54/G55 update path and worker return trampoline.
It adds a **module-private, fixed-capacity registry** containing the
original root descriptor address and exactly **two** worker descriptor
addresses. These addresses are stored in machine byte units, not BCPL
word-pointer units.

On `CO1INIT` the candidate admits the first two distinct worker
descriptors under the same root. A duplicate, changed-root or third
worker registration returns the **test-only** value `-2` before writing
any descriptor or painting a stack. The failure path restores the
compiler-visible R0 and incoming R10 and returns through the ordinary
BCPL system-vector return mechanism. The successful path also restores
the original R10 after preparing the worker image.

On `CO1SW`, the candidate first captures R0–R15 in `CO1SREG`, converts
R8's original BCPL target word pointer to a byte address, and checks:

1. zero pointer: reject before any target dereference;
2. target not equal to the registered root or either worker: reject
   before any target dereference;
3. registered descriptor equals `CURPTR` (the active context): reject;
4. registered, nonactive descriptor has state `TERMINATED=3`: reject.

All four rejection cases return the **test-only** value `-1`, using the
existing three-word `RETIMPL` frame. Rejection does not change
`CURPTR`, either native checked-stack limit, the stack global entries,
or the outgoing register snapshot. Accepted switches use the exact
existing transfer path.

**Safety limitation:** This is only a bounded *known-address membership*
check, not a capability or allocation-liveness system. A registered
descriptor must stay allocated for the entire test. The registry does
not remove stale addresses, validate arbitrary `CO1INIT` input
pointers, handle memory reuse, prevent accidental aliasing of stack
storage or support reentrancy/MVS subtasks. None of the new state or
error codes is an approved production ABI.

## Actual BCPL test contract

The BCPL fixture allocates two independent `GETVEC(1087)` stacks and
three live 24-word descriptors (root, worker 1, worker 2). It also
provides a *third descriptor* used only to prove the fixed registry
refuses a third `CO1INIT` with `-2`, before changing the live workers.
The third request reuses the first stack pointer deliberately; the
rejection is required to occur **before** any stack write.

The root starts worker 1 with 7 and worker 2 with 8. They yield 101
and 202 while preserving independent local variables. While both are
suspended, the root tries `CHANGECO` targeting `0` (null), `-1`
(unregistered byte address after shift) and the active root descriptor;
each must immediately return `-1`, without losing root local state.
The root resumes worker 1 with 11; it returns 31 naturally and is
marked terminated, then its attempted re-entry is rejected. The root
then resumes worker 2 with 22; it returns 42 and is marked terminated,
then a second attempted re-entry is rejected. Finally the root repeats
its active-target rejection. Only then may the fixture print `PASS`.

The original strict five-record native oracle remains:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Unexpected behavior prints one of the inherited failure markers or
fails the exact output oracle; it must not be treated as a PASS simply
because a JES step returned RC=0.

## Reproducibility, verification and gates

`tools/coroutines/run-co1-bcpl-registry-guard.py --run` reuses the
proven `run-co1-bcpl-switch.py` compiler/IFOX/IEWL/GO driver and
retains the tested `/CN` option and read-only installed `BOOT_OBJ`
members. It substitutes **only** the BCPL source, private IFOX module
and evidence directory `workarea/co1-bcpl-registry-guard/<UTC>/`. The
JCL uses temporary object and load datasets; it does not install
anything or modify the previously verified `CO1CHG`.

**Assistant host verification:** 16/16 new registry-guard tests and
13/13 prior terminal-guard tests passed in an independent workspace
(29 total). Python syntax checks passed. IFOX fixed-format card widths
and eight-character labels passed host checks, as did source-oracle
structure, registry-before-dereference ordering, the negative return
ABI, absence of switch-side effects on rejection, and synthetic runner
failure handling. These tests are not equivalent to real IFOX, IEWL,
Cambridge compilation or MVS GO evidence.

**Next gate:** run the candidate on real MVS, record compiler JOB,
actual assembler/linker/GO step RCs and five ordered records. Only
that native evidence can decide whether this experimental guard works.
No new Bootstrap regression ID is assigned, no historical source
changes, and no installed runtime object is promoted.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
