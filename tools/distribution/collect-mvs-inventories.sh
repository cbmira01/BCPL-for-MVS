#!/usr/bin/env bash
# TA.0: eight read-only LISTDS MVS jobs, with private host-side evidence.
# Does not extract binary records, submit IEBPTPCH, or establish source lineage.
set -euo pipefail

usage() {
    echo 'Usage: collect-mvs-inventories.sh --dry-run | --run --output /absolute/new/directory' >&2
}

keys=(MR10_OBJ MR10_LOAD BOOT_OBJ EXT_OBJ)
if [[ $# -eq 1 && $1 == --dry-run ]]; then
    for key in "${keys[@]}"; do
        printf 'MVS LISTDS MEMBERS + LABEL: %s\n' "$key"
    done
    exit 0
fi
if [[ $# -ne 3 || $1 != --run || $2 != --output || -z $3 ]]; then
    usage
    exit 2
fi

out=$3
if [[ ! -d .git || ! -x tools/datasets/dspal ]]; then
    echo 'Run from the BCPL-for-MVS checkout root.' >&2
    exit 2
fi
if [[ $out != /* || -e $out || -L $out ]]; then
    echo 'Output must be a new, absolute, unused directory.' >&2
    exit 2
fi
parent=$(dirname -- "$out")
if [[ ! -d $parent || -L $parent ]]; then
    echo 'Output parent must exist and not be a symlink.' >&2
    exit 2
fi
repo=$(pwd -P)
workarea="$repo/workarea"
resolved=$(realpath -m -- "$out")
if [[ ! -d $workarea || -L $workarea || $out != "$workarea/"* ||
      $resolved != "$workarea/"* ]]; then
    echo 'Evidence must be inside the repository ignored workarea/ directory.' >&2
    exit 2
fi

umask 077
mkdir -m 700 -- "$out"
# Context only; independently establish any actual source-to-MVS binding.
git rev-parse HEAD > "$out/collection-git-head.txt"

files=()
for key in "${keys[@]}"; do
    inv="$out/${key}.txt"
    dcb="$out/${key}.stat-raw.txt"
    tools/datasets/dspal ls "$key" > "$inv"
    files+=("$inv")
    tools/datasets/dspal stat "$key" --raw > "$dcb"
    files+=("$dcb")
done
(
    cd -- "$out"
    sha256sum -- MR10_OBJ.txt MR10_OBJ.stat-raw.txt \
        MR10_LOAD.txt MR10_LOAD.stat-raw.txt \
        BOOT_OBJ.txt BOOT_OBJ.stat-raw.txt \
        EXT_OBJ.txt EXT_OBJ.stat-raw.txt collection-git-head.txt > SHA256SUMS
)
printf 'Read-only MVS inventory/DCB evidence captured: %s\n' "$out"
printf '%s\n' 'These reports do not prove object bytes or source revision binding.'
