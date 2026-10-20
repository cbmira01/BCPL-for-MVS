# Milestone QSAM — Q.0 resource allocation and rollback probe

**Status: prepared and locally checked; NOT YET RUN ON MVS.** The
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

## MVS execution (after adding these sources to the GitHub repository)

```sh
cd ~/Source/Repos/BCPL-for-MVS
PROBE=bootstrap-toolchain/probes/q0-qsam-resource-probes
python3 "$PROBE/make-jobs.py" --check
python3 "$PROBE/make-jobs.py"
bash tools/mvs/submit-jcl workarea/qsam-q0-resource/q0-resource.jcl
# Replace JOBNUMBER with the submitted job number:
tools/mvs/dump-report-for-job JOBNUMBER
```

Expected steps: `ASM`, `LKED`, `GO`, each RC=0000; expected `QOUT`:

```text
Q0 GETMAIN RC ROLLBACK 3 ALLOC 3 FREE PASS
```

Generation produces a private 0600 JCL file in ignored `workarea/`.
Do **not** commit generated decks; they may embed local job-card
credentials. No accepted PDS objects or native runtime components
are changed by this job. **JES execution proof is still pending.**
