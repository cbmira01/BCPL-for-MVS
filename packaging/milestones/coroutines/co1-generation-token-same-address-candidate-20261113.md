# CO.1 — Generation-aware coroutine handles: same-address reuse candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date)  
**Evidence:** SOURCE-OBSERVED + ASSISTANT HOST-TESTED; **native MVS PENDING**  
**Verified baseline:** GitHub `main` at `be4a0b924a391019a09260b0fbc67b0fc49e013f`

## Motivation and explicit scope

The owner-reported native Cambridge/IFOX/IEWL/GO pass for JOB 5370/5371
verified revocation-before-`FREEVEC` and rejection of saved raw pointers
**while no registry slot was re-registered**. That test did not cover an
ABA event: a new coroutine receiving an old descriptor address.

This isolated CO.1 candidate models ABA **deterministically by
reinitializing the same still-allocated descriptor vector** after the
first worker terminates and is revoked. It does **not** claim the MVS
`GETMAIN` allocator returned a previously freed descriptor address;
that would require a separate, nondeterministic allocation-reuse test.
The former stack *is* released through `FREEVEC` and replaced with a new
`GETVEC(1087)` stack before second activation.

## Candidate-only identity and ABI experiment

- The tested `CO1CHG` IFOX module retains the 24-word descriptor, checked
  stack switch, `CO1SW` raw-descriptor transfer and `CO1DROP` revocation.
  An extra entry `CO1RES` maps an integer token to a registered **live**
  descriptor pointer, without dereferencing supplied token-derived
  addresses or freed descriptors.
- Test-only global declarations are `CO1RES:295`, `CO1DROP:296`,
  `ROOTCTX:297`, `CO1INIT:298`, `CHANGECO:299`. Slots 295–299 are **not
  reserved** for the production Cambridge runtime; this is a private
  application export trailer in one temporary native load module.
- `CO1INIT` now returns an experimental positive token. Worker slots
  seed tokens at 2 and 3; each registration adds 4. First registration
  of slot one returns 6; after revocation, re-registering the same
  slot returns 10. A signed-32-bit upper bound prevents wrapping to an
  earlier token. Registry membership remains limited to **two
  simultaneous workers**, with no permanent full-lifetime worker count.
- `CO1DROP` clears a terminated worker's live descriptor registry slot
  but **preserves its last token**. A newly registered worker at the
  same address receives a different token. The root and another valid
  worker retain their existing context-switch contract.
- The new `CO1RES(token)` procedure checks only its module-private
  token and live-address cells and returns either the current BCPL word
  pointer or zero. It preserves the established BCPL return linkage and
  original R0/R10. The BCPL `CALLH(value,token)` routine resolves the
  token, returns `-1` on failure, and invokes the tested raw
  `CHANGECO(value,pointer)` only for a live resolution.

**Important production gap:** This is a **test-only BCPL façade**. Raw
`CHANGECO` is still exported, and the check-then-switch is not atomic
across asynchronous MVS tasks. It only demonstrates identity across
controlled, cooperative lifetimes. Production code must enforce opaque
handle validation at the context-switch boundary (and decide handle
ownership, revocation, synchronization, and export policy). Do not
promote the façade as a complete use-after-free defense.

## Native BCPL test contract

The BCPL fixture allocates one `GETVEC(23)` descriptor and a first
`GETVEC(1087)` stack. It registers `WORK1`, receives token **6**, and
calls `CALLH(7,6)`. WORK1 prints `A1`, yields 101 and later resumes
with 11, checks its local sentinel, and returns 31 naturally. The root
prints `R1`, checks the result and termination state, revokes the
worker, and releases only its original stack.

The root then allocates a replacement stack and registers `WORK2`
**against the exact same still-allocated descriptor word pointer**.
The new token must equal **10**, differ from 6, and resolve to the
same descriptor word address. The old token must resolve to zero even
though the descriptor has been reinitialized, and `CALLH(777,6)` must
return `-1` without changing active state. WORK2 then starts with 8,
prints `A2`, yields 202, and later resumes with 22 to return 42;
the root prints `R2`, validates all values and sentinels, and revokes
the worker. Finally, after freeing the second stack and descriptor,
**both old and new handles** must be rejected without dereferencing
freed memory. Only then can the program print `PASS`.

The inherited strict native GO oracle is exactly:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Any unsuccessful compiler/IFOX/IEWL/GO step, missing or extra BCPL
record, inconsistent token, mishandled return or local-state failure
invalidates acceptance. No real MVS execution is claimed yet.

## Runner, independent host checks, and approval boundary

`tools/coroutines/run-co1-bcpl-generation.py --run` uses the existing
resident Cambridge compiler and three-IFOX/IEWL/native-GO coordinator.
It selects only this new BCPL source and IFOX candidate and adds the
private G!295/G!296 exports to the established G!298/G!299 generated
export trailer, checking for collisions and unexpected shapes. It
reuses the accepted `/CN` compiler option and reads installed
`BOOT_OBJ` members without altering them. The JCL creates temporary
native objects/load module; reports go to
`workarea/co1-bcpl-generation/<UTC>/`.

The assistant's independent workspace checks passed **20/20 tests**:
source formats, 71-column IFOX cards and eight-character labels,
first-entry and re-entry contract, signed generation exhaustion,
`CO1RES` register and return-frame semantics, `CO1DROP` revocation,
BCPL switch wrapper ordering, deterministic same-address test trace,
strict output oracle, synthetic identical-address ABA model, isolated
runner export patch, collision rejection, and explicit `--run`.
These are HOST-TESTED checks only, not native execution evidence.

This candidate makes no changes to the production Core Runtime,
original CO.1 probe sources, historic code, permanent Global Number
Registry, existing regression IDs, or release artifacts. The CO.1
owner-reviewed descriptor/stack/ABI/lifecycle design gate remains open.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
