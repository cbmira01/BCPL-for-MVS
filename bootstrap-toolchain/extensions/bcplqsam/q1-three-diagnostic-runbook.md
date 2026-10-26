# BCPLQSAM Q.1 — three-DD GO RC=8 diagnostic-only rerun

**Status:** Diagnostic investigation following native **Q13DD JOB 6605**
(GO RC=0008), **not** an accepted Q.1 milestone result.

The original test caller `test-q1-3dd.bcpl` and the Q.1 assembler
`bcplqsam.asm` remain **unchanged**. Instead,
`test-q1-3dd-diag.bcpl` preserves every original `QSAMSVC` call,
assertion and `STOP(8)` condition, but captures return status in a
local BCPL word and emits flushed `Q13D` stage/return-code records
using the already-established Base Library `WRITES:60`,
`WRITEN:62` and `NEWLINE:63` functions. The first native report
containing `Q13D` lines should identify the first unexpected
status or assertion. Diagnostics are printed **before** the existing
stop on assertion failure; GO may still return 8.

Reuse the **same** temporary-only native three-DD `Q13DD` JCL
generator and Q.0 test writer, with the diagnostic caller's compiled
System/370 source. JOB name `Q13DD` is reused deliberately; JES
assigns a new numeric JOB ID and we store it in a **separate**
`q13dd-diag-last-job.txt`. Local `q13dd.jcl` is regenerated for
this diagnostic caller, while the prior JOB 6605 report and
`q13dd-last-job.txt` remain untouched.

**JOB 6607 diagnostic finding:** All nine prerequisite MVS steps
returned zero but native GO returned RC=0012. Runtime traces ended at
`Q13D ASSERT 02 BEFORE` after QUERY returned 6, before the first
OPEN. The subsequent condition checks descriptor words `I!0..I!2`.
The diagnostic caller now also prints all six descriptor words
(`Q13D QUERY I0/I1/I2=` and `Q13D QUERY I3/I4/I5=`) and an
`ASSERT 02 AFTER` marker, while leaving the vector size, 14
QSAMSVC calls, and every original STOP(8) assertion unchanged.
See `packaging/qsam-q1-go-6607-query-descriptor-diagnostic-20261026.md`.
Use the existing three WSL blocks below to generate **a new job**;
the previous JOB 6607 report remains in workarea.

All WSL blocks are bounded, no polling, no fail-fast, no top-level
shell exit. Execute from the existing checkout on GitHub `main`.
The temporary dataset writer may run on MVS; no permanent object,
production catalog, or installed PDS changes are permitted.
Native GO remains **REGION=256K**.

## WSL 1 — update main, validate, compile diagnostic caller and prepare

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if git switch main; then
    mkdir -p "$work"
    rm -f "$work/.ready-three-diag-main-sha"
    rm -f "$work/.ready-three-diag-jcl-sha256"
    if git pull --ff-only origin main; then
        git log -1 --oneline
        failures=0

        python3 "$q1/check-q1-offline.py"
        rc=$?
        echo "Q.1 source check RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/test_prepare_q1_3dd.py" -v
        rc=$?
        echo "Three-DD generator tests RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/test_q1_3dd_diag.py" -v
        rc=$?
        echo "Diagnostic preservation tests RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        python3 "$q1/prepare-q1-3dd.py" --check
        rc=$?
        echo "Temporary JCL check RC=$rc"
        if [ "$rc" -ne 0 ]; then failures=$((failures + 1)); fi

        if [ "$failures" -eq 0 ]; then
            timeout -k 5s 240s python3 tools/bootstrap/compile-mvs \
                "$q1/test-q1-3dd-diag.bcpl" \
                --job-name Q13DCMP \
                --output "$work/three-diag-generated.asm"
            compile_rc=$?
            echo "Diagnostic BCPL compilation RC=$compile_rc"

            if [ "$compile_rc" -eq 0 ] &&
               [ -s "$work/three-diag-generated.asm" ]; then
                python3 "$q1/prepare-q1-3dd.py" \
                    --generated "$work/three-diag-generated.asm"
                prep_rc=$?
                echo "Diagnostic JCL preparation RC=$prep_rc"

                if [ "$prep_rc" -eq 0 ] &&
                   [ -s "$work/q13dd.jcl" ]; then
                    if git rev-parse HEAD > "$work/.ready-three-diag-main-sha" &&
                       sha256sum "$work/q13dd.jcl" \
                         > "$work/.ready-three-diag-jcl-sha256"; then
                        echo "Diagnostic Q13DD prepared for this main commit."
                    else
                        rm -f "$work/.ready-three-diag-main-sha"
                        echo "Could not record diagnostic readiness."
                    fi
                fi
            else
                echo "Diagnostic compile failed; no job prepared."
            fi
        else
            echo "$failures offline checks failed; no MVS compile."
        fi
    else
        echo "Git pull failed; no diagnostic preparation."
    fi
else
    echo "Could not switch to main; no diagnostic preparation."
fi
```

## WSL 2 — explicitly submit one diagnostic Q13DD JES job

This submission **runs the same writer plus three-DD native OPEN/INFO/CLOSE
sequence** as JOB 6605. It does not run a different QSAM source. A
submission timeout is unconfirmed; check JES before retrying.

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ "$(git branch --show-current)" != main ]; then
    echo "Not on main; nothing submitted."
elif [ ! -r "$work/q13dd.jcl" ] ||
     [ ! -r "$work/.ready-three-diag-main-sha" ] ||
     [ ! -r "$work/.ready-three-diag-jcl-sha256" ]; then
    echo "Diagnostic Q13DD readiness missing; not submitted."
elif [ "$(cat "$work/.ready-three-diag-main-sha")" != \
       "$(git rev-parse HEAD)" ]; then
    echo "Prepared Q13DD belongs to another main commit."
elif ! sha256sum --status -c "$work/.ready-three-diag-jcl-sha256"; then
    echo "Q13DD JCL has changed or checksum failed; not submitted."
elif ! git diff --quiet HEAD -- "$q1"; then
    echo "Uncommitted Q.1 changes; nothing submitted."
else
    if [ -r "$work/q13dd-diag-last-job.txt" ]; then
        cp "$work/q13dd-diag-last-job.txt" \
           "$work/q13dd-diag-previous-job.txt"
    fi
    if printf 'PENDING\n' > "$work/q13dd-diag-last-job.txt"; then
        submission=$(timeout -k 2s 100s bash tools/mvs/submit-jcl \
            --timeout 90 "$work/q13dd.jcl")
        submit_rc=$?
        printf 'Q13DD diagnostic submit RC=%s\n' "$submit_rc"
        printf '%s\n' "$submission"

        if [ "$submit_rc" -eq 0 ] &&
           [[ "$submission" =~ ^JOB[[:space:]]+[0-9]+$ ]]; then
            job=$(printf '%s\n' "$submission" | awk '{print $2}')
            printf '%s\n' "$job" > "$work/q13dd-diag-last-job.txt"
            echo "Diagnostic Q13DD JOB $job submitted."
        else
            echo "Submission unconfirmed; inspect JES before retrying."
        fi
    else
        echo "Could not reset diagnostic JOB marker."
    fi
fi
```

## WSL 3 — inspect new diagnostic JOB once, including GO RC=8

```bash
set +e
set +u
set +o pipefail

q1=bootstrap-toolchain/extensions/bcplqsam
work=workarea/bcplqsam-q1

if [ ! -r "$work/q13dd-diag-last-job.txt" ]; then
    echo "No recorded diagnostic JOB."
else
    job=$(cat "$work/q13dd-diag-last-job.txt")
    if [[ "$job" =~ ^[0-9]+$ ]]; then
        timeout -k 2s 15s python3 tools/mvs/job-summary \
            "$job" --max-rc 0 > "$work/q13dd-diag-summary.txt" 2>&1
        summary_rc=$?
        cat "$work/q13dd-diag-summary.txt"
        echo "Summary command RC=$summary_rc"

        timeout -k 2s 15s bash tools/mvs/dump-report-for-job \
            "$job" > "$work/q13dd-diag-report.txt"
        report_rc=$?
        echo "JES report collection RC=$report_rc"

        if [ "$report_rc" -eq 0 ]; then
            python3 - "$work/q13dd-diag-report.txt" <<'PY'
from pathlib import Path
import sys
rows = Path(sys.argv[1]).read_text(encoding='latin-1').splitlines()
cuts = [i for i, row in enumerate(rows)
        if 'AUTHORIZATION CODE IS' in row]
if not cuts:
    print('No IEWL authorization boundary found.')
else:
    suffix = rows[cuts[-1] + 1:]
    print('===== Actual native GO output (Q13D diagnostics) =====')
    found = 0
    for no, row in enumerate(suffix, cuts[-1] + 2):
        if row.lstrip().startswith('Q13D') or 'BCPLREG 2001' in row:
            print(f'{no}: {row}')
            found += 1
    if found == 0:
        print('No Q13D runtime trace found in GO suffix.')
PY
            echo "===== Native output verification ====="
            python3 tools/checks/check-combined-jes-records.py \
                "$q1/expected-q1-3dd.txt" \
                "$work/q13dd-diag-report.txt" --destination SYSPRINT
            echo "Expected final marker RC=$?"
        else
            echo "JES report missing; no runtime trace available."
        fi

        echo "Summary: $work/q13dd-diag-summary.txt"
        echo "Report:  $work/q13dd-diag-report.txt"
    else
        echo "Invalid or pending diagnostic JOB ID."
    fi
fi
```

Paste the **native GO output (Q13D diagnostics)** with the JOB
summary. The last emitted `Q13D CALL NN RC=` or `ASSERT NN` record
should isolate a failing public operation or assertion. If no
`Q13D START` appears, investigate startup and JES output collection
before touching the QSAM core. This diagnostic result, by itself,
does not close Q.1.
