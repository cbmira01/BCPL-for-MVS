#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage: tools/submit-jcl.sh [--timeout SECONDS] JCL

Submit a JCL deck to the local TK5 socket reader and print the JES job
number on stdout. Progress and errors are written to stderr.

Options:
  --timeout SECONDS    Maximum time to wait for JES to start the job.
                       Default: 120 seconds.
  -h, --help           Show this help.
USAGE
}

timeout=120

while (( $# )); do
    case "$1" in
        --timeout)
            [[ $# -ge 2 ]] || { usage >&2; exit 64; }
            timeout=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo >&2 "unknown option: $1"
            usage >&2
            exit 64
            ;;
        *)
            break
            ;;
    esac
done

[[ $# -eq 1 ]] || { usage >&2; exit 64; }

jcl=$1

[[ -r "$jcl" ]] || {
    echo >&2 "cannot read JCL: $jcl"
    exit 66
}

[[ "$timeout" =~ ^[0-9]+$ ]] || {
    echo >&2 "--timeout must be an integer"
    exit 64
}

# Locate the repository root relative to this script.
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd -- "$script_dir/.." && pwd)"

# Fixed TK5 configuration for this repository.
reader_port=3505
printer="$root/mvs-state/prt/prt00e.txt"

[[ -e "$printer" ]] || {
    echo >&2 "printer log not found: $printer"
    exit 66
}

command -v nc >/dev/null 2>&1 || {
    echo >&2 "nc is required"
    exit 69
}

command -v timeout >/dev/null 2>&1 || {
    echo >&2 "timeout is required"
    exit 69
}

# Extract the job name from the JOB statement.
jobname=$(
    awk '
        /^\/\/[^*][^[:space:]]*[[:space:]]+JOB([[:space:],]|$)/ {
            name=$1
            sub(/^\/\//, "", name)
            print toupper(name)
            exit
        }
    ' "$jcl"
)

[[ -n "$jobname" ]] || {
    echo >&2 "unable to identify JOB name in $jcl"
    exit 65
}

# Only examine printer output produced after this submission.
start_line=$(wc -l < "$printer")

printf 'submitting %s as %s through reader port %s\n' \
    "$jcl" "$jobname" "$reader_port" >&2

set +e
timeout 5s nc -N 127.0.0.1 "$reader_port" < "$jcl"
nc_rc=$?
set -e

if (( nc_rc != 0 && nc_rc != 124 )); then
    echo >&2 "socket-reader submission failed with rc=$nc_rc"
    exit 74
fi

if (( nc_rc == 124 )); then
    echo >&2 "socket-reader connection did not close after EOF; continuing to watch JES"
fi

deadline=$((SECONDS + timeout))

while (( SECONDS <= deadline )); do
    match=$(
        tail -n "+$((start_line + 1))" "$printer" 2>/dev/null |
            grep -m1 -E "\\\$HASP373[[:space:]]+${jobname}([[:space:]]|$)" || true
    )

    if [[ -n "$match" ]]; then
        job=$(awk '{print $3}' <<<"$match")

        if [[ "$job" =~ ^[0-9]+$ ]]; then
            printf 'JOB %s\n' "$job"
            exit 0
        fi

        echo >&2 "found JES start line but could not parse job number:"
        echo >&2 "$match"
        exit 65
    fi

    sleep 0.5
done

echo >&2 "timed out after ${timeout}s waiting for \$HASP373 ${jobname}"
echo >&2 "the submitted job may still be running; inspect $printer"
exit 75


