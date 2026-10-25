# BCPLQSAM — Q.1 source-controlled candidate

**Status (25 October 2026): Q.1 — Linkage & OPEN/CLOSE skeleton,
UNACCEPTED candidate.** The separately approved Q.0 gate and four Q.1
implementation decisions permit source work, not MVS deployment or march
closure. Actual IFOX, IEWL, native BCPL, JES/QSAM, and REGION=256K
execution are **not yet verified**.

## Scope and files

- `bcplqsam.asm`: **one** relocatable assembly object, with BCEX v1
  `QSMDESC` (`QSMBEG/QSMEND`), G!200 `QSMDISP`, private handle/DCB
  machinery, and generic `QSMFIN` finalizer. Separate internal CSECTs
  do not constitute separately selected packages.
- `bcplqsam.h`: BCPL G!200 declaration and public manifest. Including
  the header does **not** install or register the package.
- `q1-catalog.asm` + `q1-selection.asm`: **temporary source-mode**
  `BCXCAT` overlay and `BCXREQ BCPLQSAM`, using temporary `QSMOBJ`.
  Never replace the installed production `BCXCAT` member.
- `test-q1-{3dd,output,negative,finish,stop}.bcpl`: proposed native
  callers, not observed execution evidence.
- `check-q1-offline.py`: local source/card/shape checks, not assembly.

## Q.1 behavior

`QSAMSVC(op,request,result)` follows the accepted native R7/R8/R9 ABI.
QUERY returns six format-1 words, API **1.0**, supported-opcode bitmap
**`X'00000019'`** (OPEN=1, CLOSE=4, INFO=5), and capability flags **0**.
READ=2 and WRITE=3 return `QS_ERR_OPCODE=-2`. Ordinary requests have
four BCPL words and results eight; unused result words are zero.

OPEN validates DDNAME spelling, mode and reserved words, reserves one
of **16 slots**, checks DD/JFCB via non-opening RDJFCB and geometry,
opens the selected per-slot DCB, checks effective geometry and allocates
an independently owned checked **1024-byte** stage. Only a fully
acquired handle is published. Positive IDs never recycle, even after
slot reuse. Slots hold per-mode pristine DCB snapshots, restored before
subsequent OPEN. F/FB support effective LRECL 1..1024; V/VB 4..1024
including four RDW bytes. INFO reports enum, LRECL, BLKSIZE and effective
maximum **application data bytes** (F/FB LRECL, V/VB LRECL minus 4).

CLOSE on verified success releases stage and retires ID. On a returned
CLOSE failure it quarantines the occupied slot, without blind retry or
unsafe freeing. The generic R.0 finalizer closes independently held live
DCBs and signals failure for remaining uncertain ownership. BCPLREG is
responsible for ordinary FINISH RC=8 upon returned finalizer error and
preservation of explicit STOP(n). Unrecovered MVS abends are outside the
returned-error guarantee.

**Separate owner gate remains:** exceptional returned-CLOSE test
methodology and cleanup-error precedence. The candidate currently
preserves the original OPEN/stage error during rollback and retains
uncertain ownership if rollback CLOSE fails. This provisional precedence
must not be treated as approved or MVS-validated.

## Local checks and proposed MVS acceptance campaign

From the repository root, using Python only:

```sh
python3 -m py_compile \
  bootstrap-toolchain/extensions/bcplqsam/check-q1-offline.py
python3 bootstrap-toolchain/extensions/bcplqsam/check-q1-offline.py
```

Proposed MVS checks (not authorized or performed by these files): IFOX
assembly, IEWL descriptor/registration MAP and relocation, QUERY
boundary/sentinel results, three independent DDs, output OPEN/INFO/CLOSE,
invalid/missing DDs, 16 simultaneous F1024 input DDs, 17th refusal,
slot reuse/stale handles, transactional rollback, FINISH and STOP(8)
finalizers, and the accepted 00–162 regression panel (162 PASS, 0 FAIL,
one expected SKIP 083). First run the **full native BCPL 16-handle
application at REGION=256K**; higher-region execution needs explicit
owner gate review. Use temporary input DDs and temporary object decks
only. Do not submit jobs or write permanent MVS PDS members without
separate authorization.

The dispatcher source uses DCB offsets grounded in accepted BCPLIO/Q.0
probes. OPEN/CLOSE macro forms, the DCB snapshot length, actual macro
return-code semantics and post-OPEN pointer checks still require IFOX
and MVS validation. Offline source checks cannot prove those behaviors.

## Authorities

- `packaging/milestone-qsam.md`
- `packaging/bcplqsam-public-interface.md`
- `packaging/qsam-q0-staging-resource-design-decision.md`
- `packaging/qsam-q0-error-and-r0-design-decisions-20261020.md`
- `packaging/runtime-extensions-r0-owner-abi-decisions.md`
- `packaging/runtime-extensions-r0-query-abi-decision-20261021.md`
- Accepted `bootstrap-toolchain/asm/bcplrgs.asm`, `bcplio.asm` and
  `bootstrap-toolchain/extensions/bcpltime/bcpltime.asm`.

This candidate is not a Q.1 closure or approval of permanent object
installation, native regression changes, record I/O, or Q.2.

## First executable gate: IFOX assembly only (Q.1)

The repository-owned `prepare-q1-asm.py` produces `Q1QSASM`, a
single-step IFOX assembly of the actual BCPLQSAM source into disposable
`&&Q1QSOBJ`, `DISP=(NEW,DELETE)`. This does not link, run a BCPL
application, or modify permanent MVS PDS members. It is not Q.1
acceptance.

**All development and corrections are on `main`**, under the
[WSL operator command policy](../../../packaging/operator-wsl-command-policy.md).
No fail-fast option is enabled in the blocks below. The three
`set +...` commands **disable** potentially lingering Bash fail-fast
flags; conditional guards skip unsafe dependent work without exiting
the interactive WSL session.

### WSL 1: update main, run offline checks, and prepare JCL

Run from the repository root:

```bash
set +e
set +u
set +o pipefail

if git switch main; then
    work=workarea/bcplqsam-q1
    rm -f "$work/.ready-main-sha"
    if git pull --ff-only origin main; then
        q1=bootstrap-toolchain/extensions/bcplqsam
        failures=0
        mkdir -p "$work"
        python3 "$q1/check-q1-offline.py"
        rc=$?
        printf 'Source check rc=%s\n' "$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/test_prepare_q1_asm.py" -v
        rc=$?
        printf 'Operator tests rc=%s\n' "$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/prepare-q1-asm.py" --check
        rc=$?
        printf 'JCL check rc=%s\n' "$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        if [ "$failures" -eq 0 ]; then
            python3 "$q1/prepare-q1-asm.py" --prepare
            prep_rc=$?
            printf 'JCL preparation rc=%s\n' "$prep_rc"
            if [ "$prep_rc" -eq 0 ]; then
                git rev-parse HEAD > "$work/.ready-main-sha"
                printf 'Preparation marker rc=%s\n' "$?"
            fi
        else
            echo 'Offline failures: JCL preparation skipped.'
        fi
    else
        echo 'Git pull failed; checks and preparation skipped.'
    fi
else
    echo 'Could not switch to main; no other commands run.'
fi
```

### WSL 2: explicitly submit the temporary IFOX job

```bash
set +e
set +u
set +o pipefail

work=workarea/bcplqsam-q1
if [ "$(git branch --show-current)" != main ]; then
    echo 'Not on main; no JES submission.'
elif [ ! -r "$work/q1asm.jcl" ]; then
    echo 'Prepared JCL missing; no JES submission.'
elif [ ! -r "$work/.ready-main-sha" ]; then
    echo 'No successful preparation marker; no JES submission.'
elif [ "$(cat "$work/.ready-main-sha")" != "$(git rev-parse HEAD)" ]; then
    echo 'JCL belongs to another commit; no JES submission.'
elif ! git diff --quiet HEAD -- bootstrap-toolchain/extensions/bcplqsam; then
    echo 'Uncommitted Q.1 changes present; no JES submission.'
else
    submission=$(bash tools/mvs/submit-jcl --timeout 120 \
        "$work/q1asm.jcl")
    rc=$?
    printf 'Submission rc=%s; response=%s\n' "$rc" "$submission"
    if [ "$rc" -eq 0 ] &&
       [[ "$submission" =~ ^JOB[[:space:]]+[0-9]+$ ]]; then
        job=$(printf '%s\n' "$submission" | awk '{print $2}')
        printf '%s\n' "$job" > "$work/last-job.txt"
        printf 'Q1QSASM JOB %s submitted.\n' "$job"
    else
        echo 'Submission not confirmed; last JOB number unchanged.'
    fi
fi
```

### WSL 3: collect JES evidence on success or failure

```bash
set +e
set +u
set +o pipefail

work=workarea/bcplqsam-q1
if [ ! -r "$work/last-job.txt" ]; then
    echo 'No recorded JOB number.'
else
    job=$(cat "$work/last-job.txt")
    if [[ "$job" =~ ^[0-9]+$ ]]; then
        summary_rc=2
        for attempt in {1..90}; do
            bash tools/mvs/job-summary "$job" --max-rc 0 \
                > "$work/q1asm-summary.txt" 2>&1
            summary_rc=$?
            if [ "$summary_rc" -ne 2 ]; then break; fi
            sleep 2
        done

        cat "$work/q1asm-summary.txt"
        bash tools/mvs/dump-report-for-job "$job" \
            > "$work/q1asm-report.txt"
        report_rc=$?
        printf 'Report collection rc=%s\n' "$report_rc"

        if [ "$summary_rc" -eq 0 ] &&
           grep -Eq '^ASMQ[[:space:]]+.*RC=0000$' \
               "$work/q1asm-summary.txt"; then
            echo 'ASMQ RC=0000; inspect full IFOX listing.'
        else
            echo 'Failed/incomplete: inspect JES diagnostics.'
        fi
        printf 'Summary: %s/q1asm-summary.txt\n' "$work"
        printf 'Report: %s/q1asm-report.txt\n' "$work"
    else
        echo 'Invalid recorded JOB number; report not requested.'
    fi
fi
```

The job must complete with `ASMQ RC=0000` and no IFOX errors to
pass this initial gate. IEWL linkage, 16-handle native execution at
REGION=256K, QSAM and returned-CLOSE semantics remain separate
validation steps. Preserve and review JES reports on failure.
