# Milestone QSAM — Q.0 resource allocation and rollback probe

**Status: `QS0RES` PASSED on MVS in JOB 2175 and `QS0FAIL` PASSED in JOB 2176 (2026-10-20). The guarded `QS0NOMEM` test remains unexecuted.** The
standalone `QS0RES` experiment uses IFOX and MVS `GETMAIN RC` /
`FREEMAIN R` to test resource ownership, rollback, and continuation
after an intentionally injected failure. It does **not** implement
BCPLQSAM or allocate public handles. March Q.0 remains open.

This follows the approved
[Q.0 staging/resource-management decision](../../../packaging/qsam-q0-staging-resource-design-decision.md)
without changing its API or committing to a fixed record-size ceiling.

## Precisely what it tests

The `GO` program executes only on temporary load modules and writes a
PASS marker to `QOUT` (SYSOUT). Its data stages are MVS-owned storage:

1. Issue `GETMAIN RC,LV=80` to acquire A, representing an existing
   input handle's stage. Write and retain sentinel bytes `5A` and `A5`.
2. Issue `GETMAIN RC,LV=96` to acquire B for an uncommitted handle
   setup; verify two live allocations in its private counter.
3. **Inject a nonzero status instead of issuing the next GETMAIN.**
   This deterministic simulated failure exercises rollback without
   attempting MVS storage exhaustion. Free B using `FREEMAIN R,LV=96`,
   clear its pointer, and verify A is unchanged and still counted live.
4. Acquire C through `GETMAIN RC,LV=80`; validate sentinel bytes in
   both A and C; release C and A using `FREEMAIN R,LV=80`.
5. Require recorded successful acquisitions = 3, frees = 3, and
   remaining live allocations = 0. Emit the PASS record.

The real conditional `GETMAIN RC` sites check `R15` and return RC=8
on a failed acquisition. The failure path releases only nonzero
recorded allocations in reverse acquisition order. `FREEMAIN` does
not provide a portable verification that every byte was reclaimed;
this is an ownership/counter and noncorruption experiment.

**The failure is injected. This is not evidence that MVS returned a
storage-shortage code.** This safe first experiment should precede
a separately reviewed, opt-in real-shortage test. It does not exercise
QSAM `OPEN` or `GET`, dynamically allocated DCBs, or recovery of a
pending record after a true allocation failure.

## MVS execution (QS0RES observed in JOB 2175)

```sh
cd ~/Source/Repos/BCPL-for-MVS
PROBE=bootstrap-toolchain/probes/q0-qsam-resource-probes
python3 "$PROBE/make-jobs.py" --check
python3 "$PROBE/make-jobs.py"
bash tools/mvs/submit-jcl workarea/qsam-q0-resource/q0-resource.jcl
# Replace JOBNUMBER with the submitted job number:
tools/mvs/dump-report-for-job JOBNUMBER
```

Observed JOB 2175: `ASM`, `LKED`, `GO` each RC=0000; `QOUT` contained:

```text
Q0 GETMAIN RC ROLLBACK 3 ALLOC 3 FREE PASS
```

Generation produces a private 0600 JCL file in ignored `workarea/`.
Do **not** commit generated decks; they may embed local job-card
credentials. No accepted PDS objects or native runtime components
were changed by JOB 2175. [Execution evidence](../../../packaging/qsam-q0-resource-evidence-20261020.md) records the precise limits of that PASS.

## QS0FAIL — actual rollback-handler path (prepared, not run)

The separate `failure-path.asm` / `make-failure-job.py` pair tests
the failure-specific `ROLLBACK` branch used when a conditional
`GETMAIN RC` returns nonzero during an unpublished setup. This
experiment *deliberately injects* a nonzero `R15` **after** small,
real allocations of A (80 bytes), B (96 bytes), and C (64 bytes).

It must enter `ROLLBACK` exactly once, free C before B, and keep A
and its sentinel bytes intact. The test checks two releases and one
remaining live allocation, then acquires D (80 bytes), validates both
A/D, releases D and A, and checks **4 acquisitions, 4 frees, 0 live**.
This test runs the rollback-handler branch, unlike JOB 2175, but
does **not** produce a real storage shortage or exercise the separate
fatal `FAILED` routine. An unexpected allocation error causes RC=8.

Run from repository root, after pulling `main`:

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-resource-probes
python3 "$PROBE/make-failure-job.py" --check
python3 "$PROBE/make-failure-job.py"
bash tools/mvs/submit-jcl workarea/qsam-q0-resource/q0-failure-path.jcl
tools/mvs/dump-report-for-job JOBNUMBER
```

Expected for `QS0FAIL`: three steps `ASM`, `LKED`, `GO`
at RC=0000 and the SYSOUT marker:

```text
Q0 RESOURCE FAILED PATH 4 ALLOC 4 FREE PASS
```

The generator's safe `--check` produces no authenticated JCL and
validated a 230-card deck locally. The ordinary generated deck is
mode 0600 under ignored `workarea/`; it may contain JOB card secrets
and must never be committed. **JOB 2176 PASSED in MVS, but the
failure was deliberately injected, not a genuine storage shortage.**

[JOB 2176 evidence](../../../packaging/qsam-q0-failure-path-evidence-20261020.md)
records the tested shared rollback handler, reverse-order C/B release,
and preservation of independent storage A. The new
[QS0NOMEM bounded conditional-refusal experiment](README-shortage.md)
is opt-in and **has not run on MVS**. Never claim that a source/JCL
check establishes real returned-control allocation failure.
