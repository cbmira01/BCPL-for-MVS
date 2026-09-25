#!/usr/bin/env bash
set -euo pipefail

cd /tk5

if [[ ! -f conf/tk5.cnf ]]; then
    echo >&2 "TK5 configuration not found: /tk5/conf/tk5.cnf"
    exit 64
fi

if [[ ! -f scripts/ipl.rc ]]; then
    echo >&2 "TK5 IPL script not found: /tk5/scripts/ipl.rc"
    exit 64
fi

# Retain TK5 local parameter overrides used by its IPL/HAO scripts.
if [[ -f local_conf/tk5.parm ]]; then
    # shellcheck disable=SC1091
    source local_conf/tk5.parm
fi

# Cause Hercules to execute the standard TK5 IPL sequence.
export HERCULES_RC=scripts/ipl.rc

# Maintain a separate Hercules/MVS console log for each run, with
# 3033.log pointing to the current run.
log_dir=log
mkdir -p "$log_dir"

run_stamp=$(date -u +%Y%m%dT%H%M%S.%NZ)
log_file="$log_dir/3033-$run_stamp.log"
current_log="$log_dir/3033.log"

rm -f -- "$current_log"
: > "$log_file"
ln -s -- "$(basename "$log_file")" "$current_log"

herc_pid=
tail_pid=
shutdown_requests=0

cleanup() {
    if [[ -n "$tail_pid" ]] && kill -0 "$tail_pid" 2>/dev/null; then
        kill "$tail_pid" 2>/dev/null || true
        wait "$tail_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT

request_guest_shutdown() {
    shutdown_requests=$((shutdown_requests + 1))

    if (( shutdown_requests == 1 )); then
        echo >&2 "Container stop requested; initiating orderly TK5 shutdown"

        if ! curl --fail --silent --show-error --get \
            --data-urlencode 'cmd=script scripts/shutdown' \
            'http://127.0.0.1:8038/cgi-bin/tasks/cmd' >/dev/null; then
            echo >&2 "Unable to request TK5 shutdown through Hercules HTTP interface"
            echo >&2 "Hercules remains running; Docker stop grace period may force termination"
        fi
    else
        echo >&2 "Repeated stop signal; forwarding TERM to Hercules"

        if [[ -n "$herc_pid" ]]; then
            kill -TERM "$herc_pid" 2>/dev/null || true
        fi
    fi
}
trap request_guest_shutdown TERM INT

# Run Hercules without its interactive host console. Operator commands can
# be issued through the Hercules HTTP interface.
hercules -n -f conf/tk5.cnf -o "$log_file" &
herc_pid=$!

# Mirror the Hercules/MVS event log to the container's stdout so it appears
# in `docker compose up` and `docker compose logs`.
tail -n +1 --pid="$herc_pid" -F "$log_file" &
tail_pid=$!

rc=0

while kill -0 "$herc_pid" 2>/dev/null; do
    if wait "$herc_pid"; then
        rc=0
    else
        rc=$?

        # A trapped signal can interrupt wait while Hercules remains alive.
        if kill -0 "$herc_pid" 2>/dev/null; then
            continue
        fi
    fi
    break
done

wait "$tail_pid" 2>/dev/null || true
tail_pid=

exit "$rc"

