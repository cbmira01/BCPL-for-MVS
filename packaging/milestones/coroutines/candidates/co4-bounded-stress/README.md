# CO.4 — Bounded native stress and refusal candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Baseline:** GitHub `main` at `aca120fdf444e8aa8a14f8167b1fb2a74f28f337`
**Status:** SOURCE PREPARED / HOST CHECKED; **NOT NATIVE MVS TESTED**.

## Scope

The independent `source.bcpl` test uses the accepted CO.3 candidate
`library.bcpl` **without copying it into this source directory**.
The host runner stages that exact library, its `/CN` compiler parameter,
and the new application source in a temporary workarea. The accepted
CO.3 `co3drop.inc` is injected into an isolated BCPLCO IFOX assembly
stream by the unchanged CO.3 adapter. The original `BCPLCO`, `BCPLMAIN`,
`BCPLMEM`, all accepted CO.3 fixtures/runners, and installed `BOOT_OBJ`
remain unmodified. No public global slots are assigned.

This first candidate covers the agreed C4-01/C4-02 and selected
C4-03/C4-04 paths:

- Root plus two known-live workers, each with the accepted fixed
  1024-word safe stack and 256-byte clearance.
- Direct `CHANGECO` refusal of zero and a known, unregistered scalar.
  No arbitrary machine address is dereferenced.
- Worker self-`CALLCO` refusal (`-2`) and null `RESUMECO`
  refusal (`-998`) while attached to a known-live root.
- Fifteen `COWAIT` suspensions per worker with four recursive ancestor
  frames held live, followed by a 16th call returning through those
  frames and `CO3BOOT` to root. Total: 32 alternating root-to-worker
  calls and 30 explicit worker `COWAIT` suspensions in `DEEP`.
- Check worker-local sentinels, input/output values and root
  `CO3CURR`, `CO3LIST`, G54/G55 after each transfer.
- Delete both inactive, parent-free workers; verify list and root
  stack metadata after cleanup.

This candidate does **not** prove raw `STKLIM`/`APLIMIT` values, a
precise guard boundary, allocation-failure rollback, true ABA safety,
or protection from stale/freed addresses. Those remain later CO.4 work.

## Oracle and MVS evidence gate

Exactly nine complete, individually flushed application records:

```text
CO4BCPL MADE
CO4BCPL REFUSED
CO4BCPL R04
CO4BCPL R08
CO4BCPL R12
CO4BCPL R16
CO4BCPL DELA
CO4BCPL DELB
CO4BCPL PASS
```

`FAIL` is an explicit failure record, never a permitted oracle token.
The CO.4 adapter substitutes an exact `CO4BCPL` parser into the accepted
CO.3 runner; the inherited `CO3BGO` JES job identity is retained so that
no accepted JCL / authenticated job card machinery is changed.

A valid target PASS requires two independent Cambridge compilation jobs,
four IFOX, one IEWL and one GO zero-RC steps, JES SUCCESS with highest
RC=0000, and the exact ordered nine-record oracle. The runner retains
all native evidence in `workarea/co4-bounded-stress/`, including the
inherited raw `result.json` and an added `co4-result.json` with the
correct CO.4 evidence classification. Old CO.3 receipts are untouched.

## Verification commands (repository root)

Offline checks, **no JES submission**:

```bash
python3 -B tools/coroutines/run-co4-bounded-stress.py --check
python3 -B -m unittest discover \
    -s tools/coroutines -p 'test_run_co4_bounded_stress.py' -v
```

For a **separately authorized** native attempt, the operator may run:

```bash
tools/coroutines/run-co4-bounded-stress.py --run
```

The `--run` form submits two Cambridge compilation jobs and one
IFOX/IEWL/GO native job. It is **not** executed during candidate
preparation or offline verification. The `--check` path is read-only
and never starts a compiler or JES job.

## Source identity and limitations

The host validator pins the *Git blob identities* of the accepted
CO.3 library, unregister extension, and compiler options. It also
checks the new BCPL source's card lengths and named oracle sites.
These source checks do not replace real Cambridge parsing, compilation,
IFOX assembly, IEWL resolution or native execution.

For the candidate's output, `WRCH(10)` is used rather than `NEWLINE()`
to preserve the accepted CO.3 output-record convention. The inherited
CO.3 execution engine may label its internal `result.json` and
console messages as CO.3; the separate `co4-result.json` is the
CO.4-specific receipt and points back to that unmodified evidence.

No test IDs are allocated or renumbered. No commit, push, runtime
promotion, installation or release is implied by this candidate.
