#!/usr/bin/env bash
set -euo pipefail

# Commands operating on the TK5 environment expect TK5-relative paths.
cd /tk5

# When supplied by the host-side startup script, run TK5/Hercules using
# the invoking host user's numeric UID/GID. Files created in bind-mounted
# directories will therefore have useful ownership on the host.
if [[ -n "${MVS_UID:-}" || -n "${MVS_GID:-}" ]]; then
    if [[ -z "${MVS_UID:-}" || -z "${MVS_GID:-}" ]]; then
        echo >&2 "MVS_UID and MVS_GID must either both be set or both be unset"
        exit 64
    fi

    if [[ ! "$MVS_UID" =~ ^[0-9]+$ || ! "$MVS_GID" =~ ^[0-9]+$ ]]; then
        echo >&2 "MVS_UID and MVS_GID must be numeric"
        exit 64
    fi

    # TK5 system DASDs are mutable runtime state and must be writable by
    # the Hercules process.
    chown -R "${MVS_UID}:${MVS_GID}" /tk5/dasd

    exec gosu "${MVS_UID}:${MVS_GID}" "$@"
fi

# If no host identity was supplied, retain the container's default identity.
exec "$@"

