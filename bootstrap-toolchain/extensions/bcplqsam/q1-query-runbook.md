# BCPLQSAM Q.1 — native QUERY-only integration runbook

**Status:** Test candidate, not an accepted Q.1 march closure. This
runs a compiled native BCPL application under the temporary Runtime
Extensions BCX selection mechanism, with **no QSAM DDs and no
OPEN/CLOSE operations**. The only public BCPL service exercised is
`QSAMSVC:200`, QUERY and unsupported-opcode responses. Generic
FINISH finalization runs with no live handles. Actual 3-DD and
16-handle OPEN/CLOSE tests remain separate and require source review.

This reuses the **demoted Cambridge compiler under ICINT19** to
*generate* System/370 assembler; the compiler itself is not the
separately reconstructed native Cambridge compiler.

**Offline preparation correction:** The first Q1QUERY attempt on `main`
at `ba222b77` stopped safely before compilation. The generator
mistakenly matched an unindented `BCXREQ BCPLQSAM` token, whereas the
actual IFOX selection card is `         BCXREQ BCPLQSAM`.
The fixed-column check now requires exactly one such card; regression
tests explicitly reject zero or two. That operator log is **not**
MVS/JES evidence and no Q1QUERY job was submitted in that attempt.

All development remains on `main`. No downloads. JCL uses
temporary object, registry, and load data sets only. **None of these
blocks enables Bash fail-fast or issues top-level `exit`.** The
WSL terminal stays usable if a prerequisite fails. Run each block
from the existing Git checkout root.

## WSL 1 — update main, check and compile, prepare the QUERY job

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if git switch main; then
    mkdir -p "$work"
    rm -f "$work/.ready-query-main-sha"
    if git pull --ff-only origin main; then
        git log -1 --oneline
        failures=0

        python3 "$q1/check-q1-offline.py"
        rc=$?
        echo "Source checker RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/test_prepare_q1_query.py" -v
        rc=$?
        echo "QUERY generator tests RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/prepare-q1-query.py" --check
        rc=$?
        echo "Synthetic JCL check RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        if [ "$failures" -eq 0 ]; then
            timeout -k 5s 240s python3 tools/bootstrap/compile-mvs                 "$q1/test-q1-query.bcpl"                 --job-name Q1QCOMP                 --output "$work/query-generated.asm"
            compile_rc=$?
            echo "Native-code generation RC=$compile_rc"

            if [ "$compile_rc" -eq 0 ]; then
                python3 "$q1/prepare-q1-query.py"                     --generated "$work/query-generated.asm"
                prep_rc=$?
                echo "QUERY JCL preparation RC=$prep_rc"
                if [ "$prep_rc" -eq 0 ]; then
                    git rev-parse HEAD > "$work/.ready-query-main-sha"
                    echo "Q1QUERY prepared at current main commit."
                fi
            else
                echo "Compile failed/timed out; no QUERY JCL prepared."
            fi
        else
            echo "$failures offline checks failed; no MVS compile."
        fi
    else
        echo "Git pull failed; no Q.1 compilation."
    fi
else
    echo "Could not switch to main; no Q.1 compilation."
fi
```

## WSL 2 — submit one temporary native QUERY job

**This block submits to MVS JES.** Do not retry on a timeout
without checking whether JES already accepted the job.

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ "$(git branch --show-current)" != main ]; then
    echo "Not on main; QUERY submission skipped."
elif [ ! -r "$work/q1query.jcl" ] ||
     [ ! -r "$work/.ready-query-main-sha" ]; then
    echo "No successfully prepared QUERY job."
elif [ "$(cat "$work/.ready-query-main-sha")" != "$(git rev-parse HEAD)" ]; then
    echo "QUERY JCL was prepared from a different commit."
elif ! git diff --quiet HEAD -- "$q1"; then
    echo "Uncommitted Q.1 source changes; no submission."
else
    if [ -r "$work/q1query-last-job.txt" ]; then
        cp "$work/q1query-last-job.txt" "$work/q1query-previous-job.txt"
    fi

    if printf 'PENDING\n' > "$work/q1query-last-job.txt"; then
        submission=$(timeout -k 2s 100s bash tools/mvs/submit-jcl             --timeout 90 "$work/q1query.jcl")
        submit_rc=$?
        echo "Submission RC=$submit_rc"
        echo "$submission"

        if [ "$submit_rc" -eq 0 ] &&
           [[ "$submission" =~ ^JOB[[:space:]]+[0-9]+$ ]]; then
            job=$(printf '%s\n' "$submission" | awk '{print $2}')
            printf '%s\n' "$job" > "$work/q1query-last-job.txt"
            echo "Q1QUERY submitted as JOB $job."
        else
            echo "No confirmed JOB number. Inspect JES before retrying."
        fi
    else
        echo "Unable to reset current JOB marker; not submitted."
    fi
fi
```

## WSL 3 — inspect once, preserve report and verify GO output

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ ! -r "$work/q1query-last-job.txt" ]; then
    echo "No recorded Q1QUERY job."
else
    job=$(cat "$work/q1query-last-job.txt")
    if [[ "$job" =~ ^[0-9]+$ ]]; then
        timeout -k 2s 15s python3 tools/mvs/job-summary             "$job" --max-rc 0 > "$work/q1query-summary.txt" 2>&1
        summary_rc=$?
        cat "$work/q1query-summary.txt"
        echo "Summary command RC=$summary_rc"

        timeout -k 2s 15s bash tools/mvs/dump-report-for-job             "$job" > "$work/q1query-report.txt"
        report_rc=$?
        echo "Report collection RC=$report_rc"

        if [ "$summary_rc" -eq 0 ] && [ "$report_rc" -eq 0 ]; then
            steps_ok=1
            for step in ASMA ASMN ASMR ASMQ ASMG LKED GO; do
                grep -Eq "^$step[[:space:]]+.*RC=0000$"                     "$work/q1query-summary.txt"
                step_rc=$?
                if [ "$step_rc" -ne 0 ]; then
                    echo "Missing successful $step step."
                    steps_ok=0
                fi
            done

            python3 tools/checks/check-combined-jes-records.py                 "$q1/expected-q1-query.txt"                 "$work/q1query-report.txt" --destination SYSPRINT
            records_rc=$?
            echo "GO record check RC=$records_rc"

            if [ "$steps_ok" -eq 1 ] && [ "$records_rc" -eq 0 ]; then
                echo "Q.1 native QUERY-only GO gate PASS."
            else
                echo "QUERY gate not confirmed; inspect JES report."
            fi
        else
            echo "JES result missing/incomplete; inspect or rerun later."
        fi
        echo "Summary: $work/q1query-summary.txt"
        echo "Report:  $work/q1query-report.txt"
    else
        echo "Invalid or pending JOB number."
    fi
fi
```

A `Q1QUERY` pass is narrower than the Q.1 acceptance criteria:
it tests linkage, registration, G!200 QUERY, unsupported opcodes and
normal FINISH without live QSAM resources. It does **not** prove
OPEN/CLOSE rollback ownership, INFO, 3-DD QSAM activity or 16
concurrent handles.
