#!/usr/bin/env bash
set -u
set -o pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd -- "$script_dir/../.." && pwd)"

export CAMBRIDGE_COMPILE="$root/tools/cambridge-compile-mvs"
exec bash "$script_dir/run-test.sh" "$@"
