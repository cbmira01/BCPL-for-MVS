#!/usr/bin/env bash
# Consolidated Q.0 MVS batch. All output temporary; BOOT_OBJ read-only.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
source="$root/bootstrap-toolchain/probes/q0-integrated-16-dcb"
work="$root/workarea/qsam-q0-integrated"
generator="$source/make-jobs.py"
if [[ $# -eq 1 && $1 == --check ]]; then
    for profile in finish stop finish-512 stop-512; do
        python3 "$generator" "$profile" --check
    done
    bash -n "$source/run-batch.sh"
    echo "Q.0 synthetic batch preflight passed; MVS not executed"
    exit 0
fi
if (( $# != 1 )) || [[ $1 != --execute ]]; then
    echo "Usage: run-batch.sh --check|--execute" >&2
    exit 64
fi
umask 077
mkdir -p "$work"
for profile in finish stop; do
    compile=Q0NFINC
    [[ $profile == stop ]] && compile=Q0NSTPC
    python3 "$root/tools/bootstrap/compile-mvs" "$source/$profile.bcpl" \
        --job-name "$compile" --output "$work/$profile.asm"
    python3 "$generator" "$profile" --generated "$work/$profile.asm"
done
for profile in finish stop; do
    response=$(bash "$root/tools/mvs/submit-jcl" --timeout 120 \
        "$work/$profile.jcl")
    if ! [[ $response =~ ^JOB[[:space:]]+([0-9]+)$ ]]; then
        echo "Unexpected JES submission: $response" >&2
        exit 65
    fi
    job=${BASH_REMATCH[1]}
    echo "$job" > "$work/$profile.job"
    echo "Q.0 $profile JOB $job"
    deadline=$((SECONDS+240))
    while :; do
        set +e
        summary=$("$root/tools/mvs/job-summary" "$job" --max-rc 8 2>&1)
        rc=$?
        set -e
        if (( rc != 2 )); then break; fi
        if (( SECONDS >= deadline )); then
            echo "Incomplete JOB $job; inspect JES" >&2
            exit 75
        fi
        sleep 2
    done
    printf '%s\n' "$summary" > "$work/$profile.summary"
    bash "$root/tools/mvs/dump-report-for-job" "$job" \
        > "$work/$profile.report"
    python3 "$source/verify-report.py" "$profile" \
        "$work/$profile.summary" "$work/$profile.report"
    echo "Q.0 $profile verified (JOB $job)"
done
echo "Q.0 integrated batch PASS; owner Q.0 gate review still required"
