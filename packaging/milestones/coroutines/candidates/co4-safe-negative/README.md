# CO.4 — Recoverable negative-path and survivor continuity candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Evidence status:** HOST-CHECKED / NATIVE MVS PENDING
**Source authority:** GitHub `main`; accepted CO.3 runtime and library unchanged

## Purpose

Exercise bounded, non-abending refusal paths and demonstrate that a pair
of independently allocated native BCPL worker stacks remains usable after
the refusals. This is the next small candidate after the accepted CO.4
bounded stress PASS. No new runtime ABI, global allocation or descriptor
handling policy is required.

The BCPL application checks:

1. After `CO3INIT`, `CREATECO` rejects 1023, 1025 and -1 stack sizes,
   each returning zero without mutating root/registry state. Source
   confirms these size refusals occur *before* `GETVEC`.
2. `COWAIT(9)` and `RESUMECO(0,9)` from root each return -3 and leave
   root state unchanged.
3. Creation of two live workers succeeds, third creation is refused at
   fixed two-worker registration capacity, and the original workers
   remain live. The accepted CO.3 library frees both temporary vectors
   on the known `CO2INIT` refusal path, but this fixture does *not*
   independently instrument allocator byte counts.
4. Root `DELETECO(0)`, `DELETECO(ROOT)` and `DELETECO(1)` return FALSE.
   Only DELETECO is given the known nonmember scalar, and its list
   membership search precedes dereference of the target. No arbitrary,
   stale or freed pointer is passed to `CALLCO` or `RESUMECO`.
5. Each currently executing worker refuses `DELETECO(SELF)`, then
   yields once and naturally returns after a second call. The owner
   checks exact yielded/returned values, preserved local sentinels,
   root `CO3CURR` and G54/G55 after each transfer.
6. Both parent-free workers can be deleted, including list head/tail
   maintenance, with root stack metadata preserved after cleanup.

All worker stacks retain fixed 1024 safe words and 256-byte clearance.
These negative paths are *recoverable errors* under Approach A; this is
not a general invalid-address, double-free, ABA or overflow probe.

## Strict native oracle

Exactly 16 complete records in order (each emitted with `WRCH(10)`):

```text
CO4SAFE INIT
CO4SAFE SIZE
CO4SAFE ROOT
CO4SAFE MADE
CO4SAFE FULL
CO4SAFE BADDEL
CO4SAFE A1
CO4SAFE RA1
CO4SAFE B1
CO4SAFE RB1
CO4SAFE A2
CO4SAFE RA2
CO4SAFE B2
CO4SAFE RB2
CO4SAFE CLEAN
CO4SAFE PASS
```

`CO4SAFE FAIL` or any extra/malformed/truncated record is a target
failure. The thin adapter stages the accepted CO.3 BCPL library and
compiler `/CN` parameter, injects the existing `CO3DROP` into a
*temporary* IFOX bridge and reuses the independent Cambridge compiler,
4 IFOX steps, IEWL and GO pipeline. The inherited `CO3BGO` JCL job
identity and strict JES step/RC assessment are unchanged.

The operator's local `workarea/co4-safe-negative/` retains all raw
inherited receipts and a new `co4-result.json`. `--check` never submits
JES; `--run` requires explicit selection. The installed `BOOT_OBJ` is
read-only. No permanent globals, test numbering, promotion or release.

## Evidence gate

Real native acceptance requires two independent Cambridge compiler jobs,
all 4 IFOX steps RC=0000, IEWL RC=0000, GO RC=0000, JES SUCCESS/highest
RC=0000, and exact 16-record oracle. Any failure must remain a separate
FAIL receipt, never replaced or silently reclassified.

CO.4 still requires independent exact stack-limit/guard observations,
deliberate allocation-failure rollback instrumentation and remaining
exceptional cleanup review before qualified closure. CO.5 is NOT STARTED.
