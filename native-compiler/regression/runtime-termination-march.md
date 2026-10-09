# BCPLMAIN termination and storage reclamation march

Status: **CLOSED — 84/84 full native regression pass (2026-10-09)**

Baseline at opening: `main`, 82/82 native regressions PASS (00–081);
BCPLMAIN source and BLIB injection preflight pass.

## Observed contracts in current BCPLMAIN

- Startup obtains one contiguous allocation using `GETMAIN EC`. It
  records the address in `DYNBASE` and the constant byte length in
  `DYNLEN` (17,444).
- `RELMEM` is called from `FINRETN`, `BADRETN`, `GTOOBIG`, and
  `NOSTART`. It checks `DYNBASE`, executes `FREEMAIN R` once,
  zeroes `DYNBASE`, and returns.
- `GNOCORE` is the GETMAIN failure path and does not call `RELMEM`.
- `GETVEC` obtains **separate** MVS allocations and chains an in-block
  12-byte allocation record at `VECLIST`, with fields at offsets 0
  (BCPL word pointer), 4 (allocated byte length), and 8 (next pointer).
- `FREEVEC` unlinks the matching record and executes `FREEMAIN R`
  with the recorded length and allocation base.
- **The termination paths never drain `VECLIST`**. Consequently,
  any vectors still live at FINISH are not explicitly returned to MVS
  by this runtime (the operating system might reclaim step storage
  later, which is not an explicit runtime guarantee).
- Normal FINISH flushes a pending output record via `PUT`; explicit
  output DCB CLOSE and propagation of a BCPL return code remain
  separate reconstruction work.

## First implementation target: outstanding vector teardown

Add a common cleanup routine before the combined allocation is
freed, traversing `VECLIST` and releasing each outstanding GETVEC
allocation using the length stored in its own control record.
The routine must save the next pointer before FREEMAIN, must not
access an already-freed record, and must leave `VECLIST=0`.

Invoke common teardown on all *post-allocation* termination paths:
FINISH, unexpected START return, invalid global trailer, and missing
START. The failure-before-allocation path must remain safe.

Keep exactly the current MVS completion codes and normal output
behavior. Do not change historical BLIB or CG370 to accomplish this.

## Test plan / acceptance

1. Build and **execute locally** applicable `tools/checks/` static
   checks, including `check-native-runtime.py`, before committing
   any source or regression helper edits.
2. Add a narrow native regression where GETVEC allocations remain
   outstanding when START finishes, including more than one live
   vector; this is a behavior smoke test, **not** proof that MVS
   storage was reclaimed.
3. Where practicable, provide independent reclamation evidence
   (e.g., observable instrumentation or a dedicated termination
   diagnostic); never infer successful FREEMAIN from normal output.
4. Run targeted TK5 regressions before the full 00–081 sweep and any
   added regression. Preserve 82/82 as the known-good baseline.

## Deferred questions

- Historical FINISH/STOP/ABORT completion-code contract.
- Whether all pending DCBs require explicit CLOSE.
- FREEMAIN service return/error handling and fault injection.
- Return/ABEND behavior if the GETMAIN release fails.
- Historical `INUM`, stack high-water markers and configuration.

No executable runtime code has been changed in this audit checkpoint.

## Implementation checkpoint

Commit ad71616 changes RELMEM to detach and release each outstanding GETVEC block before freeing DYNBASE. Source width and injection anchors were checked; guest execution and independent reclamation evidence remain pending.

## Closure checkpoint — 2026-10-09

The operator ran the complete native regression panel `00..083` on
TK5/MVS 3.8J after the test-only 083 addressability correction
(commit `47103f8`): **84 PASS, 0 FAIL, TOTAL 84**.

Regression 082 passed with `42` while leaving two vectors outstanding.
Regression 083 passed with two separate output records, `42` and
`V=2 M=1`: two vector FREEMAIN call sites returned within teardown,
followed by the main allocation's FREEMAIN return site. An earlier
083 IFOX RC=0008 resulted from an unreachable end-of-CSECT literal;
the test-only instrumenter now uses the addressable `TRTXT83` data
constant. Canonical BCPLMAIN was not altered by that repair.

These results establish tested cleanup control flow and compatibility;
they do not independently prove successful storage-manager reclamation
or analyze FREEMAIN service return codes. Explicit CLOSE, STOP/ABORT
completion semantics, abnormal recovery, and historical INUM remain
outside this milestone.

**March closed.** Any further runtime lifecycle work starts in a new
march rather than extending regression 083.
