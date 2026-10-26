# BCPLQSAM Q.1 — integrated three-DD OPEN/INFO/CLOSE test

**Status:** Unaccepted Q.1 test candidate. The QUERY-only gate passed in
MVS JOB 6603. This next test exercises real F1024 QSAM OPEN/INFO/CLOSE
of three simultaneously live handles at **native GO REGION=256K**.

The generator reuses the accepted Q.0 **three-DD temporary writer**
from `q0-qsam-16-dcb-probes/make-jobs.py`. This creates three initialized
datasets with two F1024 records apiece, before native GO opens them;
the native BCPL application does not perform READ/WRITE and therefore
does not advance Q.2. The temporary BCX catalog and all objects are
compiled/link-edited in the same job. Installed `BOOT_OBJ`,
`BOOT_DEVOBJ`, production `BCXCAT` and permanent PDS datasets are
never modified.

**Risk boundary:** This is the first production-candidate real
QSAM OPEN/CLOSE test. QSAM abnormal completion can ABEND rather than
return a BCPL error. The JCL includes `SYSUDUMP`; preserve its JES
diagnostics if execution fails. Never resubmit an unconfirmed job
without checking JES. Returned-CLOSE fault injection and
cleanup-error precedence remain unapproved and **not tested** here.

All blocks below disable any inherited shell fail-fast settings,
guard dependent operations without top-level exit, and use bounded
non-polling JOB inspection. Execute from the existing Git repository
root on WSL. GitHub `main` remains authoritative.

## WSL 1 — update main, validate, compile, prepare three-DD JCL

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if git switch main; then
    mkdir -p "$work"
    rm -f "$work/.ready-three-main-sha"
    if git pull --ff-only origin main; then
        git log -1 --oneline
        failures=0

        python3 "$q1/check-q1-offline.py"
        rc=$?
        echo "Source invariants RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/test_prepare_q1_3dd.py" -v
        rc=$?
        echo "Three-DD unit tests RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/prepare-q1-3dd.py" --check
        rc=$?
        echo "Synthetic three-DD JCL RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        if [ "$failures" -eq 0 ]; then
            timeout -k 5s 240s python3 tools/bootstrap/compile-mvs \
                "$q1/test-q1-3dd.bcpl" \
                --job-name Q13COMP \
                --output "$work/three-generated.asm"
            compile_rc=$?
            echo "BCPL compilation RC=$compile_rc"

            if [ "$compile_rc" -eq 0 ] &&
               [ -s "$work/three-generated.asm" ]; then
                python3 "$q1/prepare-q1-3dd.py" \
                    --generated "$work/three-generated.asm"
                prep_rc=$?
                echo "Three-DD JCL preparation RC=$prep_rc"

                if [ "$prep_rc" -eq 0 ]; then
                    if git rev-parse HEAD > "$work/.ready-three-main-sha"; then
                        echo "Q13DD prepared against current main."
                    else
                        echo "Could not record preparation revision."
                    fi
                fi
            else
                echo "BCPL compilation unsuccessful; no JCL prepared."
            fi
        else
            echo "$failures offline checks failed; no BCPL compilation."
        fi
    else
        echo "Git pull unsuccessful; no Q.1 execution preparation."
    fi
else
    echo "Cannot switch to main; no Q.1 execution preparation."
fi
```

## WSL 2 — explicitly submit Q13DD once

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ "$(git branch --show-current)" != main ]; then
    echo "Not on main; no submission."
elif [ ! -r "$work/q13dd.jcl" ] ||
     [ ! -r "$work/.ready-three-main-sha" ]; then
    echo "Missing prepared Q13DD JCL or readiness marker."
elif [ "$(cat "$work/.ready-three-main-sha")" != "$(git rev-parse HEAD)" ]; then
    echo "Q13DD preparation does not match current main HEAD."
elif ! git diff --quiet HEAD -- "$q1"; then
    echo "Uncommitted BCPLQSAM changes; no submission."
else
    if [ -r "$work/q13dd-last-job.txt" ]; then
        cp "$work/q13dd-last-job.txt" "$work/q13dd-previous-job.txt"
    fi
    if printf 'PENDING\n' > "$work/q13dd-last-job.txt"; then
        submission=$(timeout -k 2s 100s bash tools/mvs/submit-jcl \
            --timeout 90 "$work/q13dd.jcl")
        submit_rc=$?
        echo "Q13DD submission RC=$submit_rc"
        echo "$submission"

        if [ "$submit_rc" -eq 0 ] &&
           [[ "$submission" =~ ^JOB[[:space:]]+[0-9]+$ ]]; then
            job=$(printf '%s\n' "$submission" | awk '{print $2}')
            printf '%s\n' "$job" > "$work/q13dd-last-job.txt"
            echo "Q13DD submitted as JOB $job."
        else
            echo "Submission not confirmed; inspect JES before retrying."
        fi
    else
        echo "Could not reset JOB marker; nothing submitted."
    fi
fi
```

## WSL 3 — single bounded JES inspection and expected result

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ ! -r "$work/q13dd-last-job.txt" ]; then
    echo "No recorded Q13DD JOB."
else
    job=$(cat "$work/q13dd-last-job.txt")
    if [[ "$job" =~ ^[0-9]+$ ]]; then
        timeout -k 2s 15s python3 tools/mvs/job-summary \
            "$job" --max-rc 0 > "$work/q13dd-summary.txt" 2>&1
        summary_rc=$?
        cat "$work/q13dd-summary.txt"
        echo "Summary RC=$summary_rc"

        timeout -k 2s 15s bash tools/mvs/dump-report-for-job \
            "$job" > "$work/q13dd-report.txt"
        report_rc=$?
        echo "JES report RC=$report_rc"

        steps_ok=1
        for step in ASMWR LKWR ASMA ASMN ASMR ASMQ ASMG LKED WGO GO; do
            if ! grep -Eq "^$step[[:space:]]+.*RC=0000$" \
                "$work/q13dd-summary.txt"; then
                echo "Missing successful $step step."
                steps_ok=0
            fi
        done

        # Collect negative evidence even when native GO returned RC=8.
        records_rc=99
        if [ "$report_rc" -eq 0 ]; then
            echo "===== MVS/JES diagnostic messages ====="
            grep -Ein \
                'BCPLQSAM|BCPLREG|FINALIZER|ABEND|S0C|STOP|GO |IEF142I' \
                "$work/q13dd-report.txt" | tail -90
            echo "===== Last 100 JES report lines ====="
            tail -100 "$work/q13dd-report.txt"
            python3 tools/checks/check-combined-jes-records.py \
                "$q1/expected-q1-3dd.txt" \
                "$work/q13dd-report.txt" --destination SYSPRINT
            records_rc=$?
            echo "Native output marker check RC=$records_rc"
        else
            echo "JES report unavailable; marker not checked."
        fi

        if [ "$summary_rc" -eq 0 ] && [ "$steps_ok" -eq 1 ] &&
           [ "$report_rc" -eq 0 ] && [ "$records_rc" -eq 0 ]; then
            echo "Q.1 three-DD native OPEN/INFO/CLOSE gate PASS."
        else
            echo "Three-DD gate NOT confirmed; preserve JES diagnostics."
        fi
        echo "Summary: $work/q13dd-summary.txt"
        echo "Report:  $work/q13dd-report.txt"
    else
        echo "Invalid/pending Q13DD JOB ID; no inspection."
    fi
fi
```

**Negative-evidence policy (JOB 6605):** GO RC=0008 was observed
despite successful assembler/linker/writer steps. Even when GO fails,
inspect the saved full report and run the output-marker check. A
marker-check failure does not identify the failing BCPL assertion,
and a matching marker cannot override an unsuccessful GO RC.

A GO RC=0000 and matching logical output establish the exercised
three-DD OPEN/INFO/CLOSE and explicit successful-close path. The
combined JES report verifier does not independently establish
physical output DD attribution. This does **not** accept the
full Q.1 milestone; sixteen live handles, FINISH/STOP with live
resources, exceptional returned-CLOSE and full native regression
still require separate evidence.
