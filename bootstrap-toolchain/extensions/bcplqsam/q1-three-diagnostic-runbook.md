# BCPLQSAM Q.1 — three-DD GO RC=8 diagnostic-only rerun

**Status:** Diagnostic investigation following native **Q13DD JOB 6605**
(GO RC=0008), **not** an accepted Q.1 milestone result.

The original test caller `test-q1-3dd.bcpl` and the Q.1 assembler
`bcplqsam.asm` remain **unchanged**. Instead,
`test-q1-3dd-diag.bcpl` preserves every original `QSAMSVC` call,
assertion and `STOP(8)` condition, but captures return status in a
local BCPL word and emits flushed `Q13D` stage/return-code records
using Base Library `WRITES:60` and `WRITEN:62`; the current
newline experiment calls Core Runtime `WRCH:14` with value 10. The first native report
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
Use the existing three WSL blocks below to generate **a new job**.
The inspection block writes its summary/report under the numeric JOB
ID, preserving both the original JOB 6607 report and the next result.
Do not overwrite the prior unnumbered diagnostic report.

**JOB 6609 diagnostic finding:** QUERY reports descriptor words
`I!0..I!2 = 1 1 0`, the correct values, but GO again returned
RC=0012 and the filtered report showed no subsequent
`Q13D QUERY I3/I4/I5=` marker. The supplied trace is **not**
proof that the source assertion failed; it could omit partial
or non-`Q13D` runtime/JES output. See
`packaging/qsam-q1-go-6609-query-prefix-diagnostic-20261026.md`.
**Inspect the already saved JOB 6609 report first; do not immediately
compile or submit another job.** The third block now preserves
existing per-JOB report files, prints matching diagnostic records,
and displays the raw trailing GO suffix, including non-matching
lines. No new JES submission is required for this inspection.

**JOB 6609 read-only follow-up (26 October 2026):** The operator's
preserved full JES report contains 8,959 lines. The final IEWL
authorization boundary is line 8919; native diagnostic records are
lines 8923–8929, ending with correct QUERY words 0–2 (1 1 0).
The remaining GO suffix contains JES banners but no second QUERY
record, partial diagnostic, or explicit abend message. Read-only
inspection of JOB 6608's preserved generated assembler found both
20-byte EBCDIC QUERY label literals and generated calls for the two
groups, separated by NEWLINE. No QSAM OPEN was reached in the
observable trace. GO RC=0012 still has no uniquely identified cause;
BCPLIO's output-buffer STOP(12) path is only a hypothesis.

The diagnostic-only caller now emits Q13D QUERY 012 NL RETURNED
after the first QUERY newline, flushes the second QUERY prefix by
itself, and emits separate flushed Q13D QUERY I3=, I4=, and I5=
records. These markers distinguish the last completed output
boundary if a subsequent call does not return. The original 14
QSAMSVC calls and all STOP(8) assertions are retained, and
bcplqsam.asm, the original caller, and the JCL generator are
unchanged. This source/test preparation is **not** authorization to
submit WSL 2, change installed MVS datasets, or accept Q.1.
Run offline checks before any separately authorized MVS compile/GO.

**JOBs 6612–6613 (26 October 2026):** The revised caller compiled in
JOB 6612 (host RC=0) and ran as Q13DD JOB 6613. All nine prerequisite
MVS steps returned RC=0000 (IFOX highest severity 0, no flagged
statements); native GO returned RC=0012. The collected report
`workarea/bcplqsam-q1/q13dd-diag-6613-report.txt` has 8,999 lines;
the last IEWL authorization boundary is line 8959. The same seven
flushed Q13D records appear, ending with correct QUERY I0/I1/I2=1 1 0
at line 8969. Neither the new post-newline marker nor a partial
following record appears. The expected final PASS marker is absent.
This does not prove that a fixed record count caused GO RC=0012.

**Approved next diagnostic — record-count shift:** Insert exactly two
short, independently flushed records, `Q13D SHIFT 01` and
`Q13D SHIFT 02`, immediately after `Q13D START` and before the
first QSAMSVC call. All existing QUERY instrumentation, the original
14 QSAMSVC calls, STOP(8) assertions, QSAM assembler and temporary
JCL generator remain unchanged. If exactly seven records are again
emitted, the seventh should now be `Q13D CALL 03 RC=-3` in the
expected path. If the last visible record remains the QUERY I0/I1/I2
triplet, nine records should be visible including the two SHIFT
markers. Other outcomes need independent interpretation and do not
by themselves distinguish an output-buffer error from runtime or
code-generation faults. Compile into a new revision-specific local
filename; preserve earlier JOB 6613 and compiler evidence. One
separately owner-approved temporary Q13DD run may use the existing
REGION=256K generator; no permanent MVS changes or Q.1 acceptance.

**JOBs 6614–6615 (26 October 2026) — record-count-shift result:**
JOB 6614 successfully compiled the two-marker caller (host RC=0).
Q13DD JOB 6615 completed all nine prerequisite steps at RC=0000;
native GO returned RC=0012. Its report,
`workarea/bcplqsam-q1/q13dd-shift-6615-report.txt`, has 9,017
lines and the final IEWL authorization boundary at line 8976. After
`Q13D START`, both `Q13D SHIFT` records appeared. GO output
stopped with the partial text `Q13D CALL 04 RC` (missing `=6`),
not at the same logical QUERY statement. The visible output matches
a 132-character accumulation before the next attempted character,
consistent with BCPLIO's 132-byte buffer and STOP(12) overflow
path. This supports, but does not conclusively prove, a newline
character-code mismatch: the historical Base Library's NEWLINE()
uses WRCH('*N'), while the Core Runtime's IOWRCH flushes on
the integer character code 10.

**Approved diagnostic — explicit numeric newline:** The diagnostic
caller only now uses `WRCH(10)` (Core Runtime global G!14)
where it formerly called `NEWLINE()` (Base Library global G!63).
The original QSAM caller and QSAM assembler remain untouched;
the 14 service calls, every STOP(8) assertion, and the SHIFT/QUERY
markers are preserved. A new offline check enforces the newline
substitution. The next controlled temporary Q13DD run uses the
same JCL generator, 256K GO region, and fresh evidence filenames;
no installed MVS dataset changes or milestone acceptance are
authorized.

**JOB 6617 OPEN-stage investigation (26 October 2026):** The WRCH(10)
caller was compiled in JOB 6616 and ran as Q13DD JOB 6617. All
nine prerequisite MVS steps returned zero. GO RC=0008 followed the
first OPEN returning QS_ERR_OPEN=-6 with result (-6,0,0); QUERY
and unsupported-opcode tests passed. The preserved full report
workarea/bcplqsam-q1/q13dd-wrch-6617-report.txt has IEF237I messages
confirming Q00/Q01/Q02 allocated in both WGO and GO. No operating
system message identifies which internal OPEN path returned -6.

**Approved diagnostic-only ASMQ variant:** The source-controlled helper
prepare-q1-3dd-open-diag.py replaces ONLY the ASMQ SYSIN body of a
locally prepared temporary Q13DD deck. Baseline bcplqsam.asm, the
existing generator, the original caller, and all public QS_ERR_*
statuses remain unchanged. On recoverable failures, the variant
uses private BCPLIO IODIAG to prepend one short primary-buffer
marker: Q1O:RDJFCB, Q1O:PREFORM, Q1O:DCBPTR, or Q1O:POSTFORM.
These distinguish a nonzero RDJFCB return, failed preflight
geometry, zero DCB+48 after OPEN, or failed post-OPEN geometry.
The private call preserves R0-R9/R11-R14 and clobbers R10/R15;
the variant rebuilds the R10 high base and leaves R7 carrying
the original error. IODIAG does not flush by itself; inspect full
GO records, including lines combining Q1O and Q13D prefixes.
Compilation and native execution remain unverified. No permanent
MVS dataset update or Q.1 acceptance follows from preparation.

**JOB 6618 (26 October 2026) — pre-OPEN geometry failure:**
Q13DD JOB 6618 assembled and linked successfully (all prerequisite
steps RC=0000) but GO returned RC=0008 at the first OPEN.
The single private trace `Q1O:PREFORM Q13D CALL 07 RC=-6`
identifies failure in QCVFORM, before MVS OPEN. The current
F1024 input DDs request RECFM=F, LRECL=1024, BLKSIZE=1024.
The accepted Q.0 JOB 2172 confirmed JFCB geometry offsets for FB80
only; these F1024 raw input values have not yet been measured.

**Approved raw preflight diagnostic:** The isolated ASMQ variant
adds a QDGTRACE call just before the original QCVFORM, saving and
restoring R0–R15 while formatting the live R3, R5 and R6 values
into one 45-byte `Q1O:GEOM R3=hhhhhhhh R5=hhhhhhhh R6=hhhhhhhh `
buffer with EBCDIC hexadecimal digits. R3 is raw RECFM from JFCB
+100; R5 is signed-halfword LRECL from +104; R6 is signed-halfword
BLKSIZE from +102. The nominal F1024 values in registers would be
`00000080 / 00000400 / 00000400` respectively. The emitter uses
private BCPLIO.IODIAG to append the trace to primary SYSPRINT;
the existing four failure markers remain. Capture the full
GO suffix because `Q1O:GEOM`, `Q1O:PREFORM` and `Q13D` may share
one record. No bypass of QCVFORM, error-contract revision,
permanent MVS writes or Q.1 acceptance is authorized.

**Q.0-to-Q.1 JFCB discrepancy (after JOB 6619):**
The Q.0 geometry probe (QS0GEOM JOB 2172) supplied explicit DCB
attributes on QGOOD/QBAD in the *same* GO step issuing RDJFCB.
Q.1's Q13DD WGO created F1024 temporary datasets using DCB=
(RECFM=F,LRECL=1024,BLKSIZE=1024), but the subsequent GO step
allocated Q00/Q01/Q02 with DISP=(OLD,DELETE) and *no DCB*.
JOB 6619 returned RDJFCB R15=0 but all three geometry inputs
(RECFM/LRECL/BLKSIZE) were zero. RDJFCB delivers the current
job's JFCB; dataset-label/DSCB attributes may be merged at OPEN,
which the existing preflight blocked. This is the leading cause
of the zero fields, not proof of incorrect EXLST relocation.

**Opt-in temporary-only comparison:**
`prepare-q1-3dd-go-dcb.py` modifies only the Q00/Q01/Q02 GO reader
DD statements in a previously prepared Q13DD geometry diagnostic
deck. It adds the same `DCB=(RECFM=F,LRECL=1024,BLKSIZE=1024)`
that the writer already used, matching the explicit-JCL-attribute
pattern demonstrated by Q.0. The earlier ASMQ geometry trace and
four OPEN stage markers, original Q.1 generator, assembler and
BCPL caller remain intact; GO REGION=256K and temporary-only
allocations are unchanged. The tool refuses overwrites.
**This is an experiment, not a general API requirement.**
Whether an ordinary DD lacking DCB= must be supported, and how
pre-OPEN validation can safely determine its DSCB geometry,
requires separate owner-reviewed design before changing
`bcplqsam.asm`. No MVS execution or Q.1 acceptance is implied.

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
        summary="$work/q13dd-diag-${job}-summary.txt"
        report="$work/q13dd-diag-${job}-report.txt"

        if [ -s "$summary" ]; then
            echo "Using preserved summary: $summary"
        else
            timeout -k 2s 15s python3 tools/mvs/job-summary \
                "$job" --max-rc 0 > "$summary" 2>&1
            echo "Summary collection RC=$?"
        fi
        cat "$summary"

        if [ -s "$report" ]; then
            echo "Using preserved JES report: $report"
            report_rc=0
        else
            timeout -k 2s 15s bash tools/mvs/dump-report-for-job \
                "$job" > "$report"
            report_rc=$?
            echo "JES report collection RC=$report_rc"
        fi

        if [ "$report_rc" -eq 0 ]; then
            python3 - "$report" <<'PY'
from pathlib import Path
import sys
rows = Path(sys.argv[1]).read_text(encoding='latin-1').splitlines()
cuts = [i for i, row in enumerate(rows)
        if 'AUTHORIZATION CODE IS' in row]
if not cuts:
    print('No IEWL authorization boundary found; inspect report manually.')
else:
    suffix = rows[cuts[-1] + 1:]
    first = cuts[-1] + 2
    print('===== GO suffix diagnostic records =====')
    found = 0
    for no, row in enumerate(suffix, first):
        if ('Q13D' in row or 'BCPLREG 2001' in row or
                'ABEND' in row or 'S0C' in row):
            print(f'{no}: {row!r}')
            found += 1
    if not found:
        print('No expected native diagnostic records found.')
    print('===== Raw GO suffix: last 100 lines =====')
    for no in range(max(0, len(suffix) - 100), len(suffix)):
        print(f'{first + no}: {suffix[no]!r}')
PY
            echo "===== Native output verification ====="
            python3 tools/checks/check-combined-jes-records.py \
                "$q1/expected-q1-3dd.txt" \
                "$report" --destination SYSPRINT
            echo "Expected final marker RC=$?"
        else
            echo "JES report missing; no runtime trace available."
        fi

        echo "Summary: $summary"
        echo "Report:  $report"
    else
        echo "Invalid or pending diagnostic JOB ID."
    fi
fi
```

For JOB 6609, use the third block above **without running
WSL 1 or WSL 2**. It reads preserved per-JOB report files where
available. Inspect the raw suffix for partial lines and independent
GO/JES errors, then decide whether another instrumented MVS run is
needed. Do not infer an incorrect QUERY descriptor from its
correct `I!0..I!2` prefix. Q.1 is still open.
