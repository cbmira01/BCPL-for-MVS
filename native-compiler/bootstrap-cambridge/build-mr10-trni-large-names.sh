#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

python3 native-compiler/bootstrap-cambridge/make-mr10-trn-large-names.py

srcdir=native-compiler/bootstrap-cambridge/mr10-trn-large-names
mapfile -t sections < <(printf '%s\n' "$srcdir"/trn[0-9]* | sort -V)
if (( ${#sections[@]} == 0 )); then
    echo "no generated TRN sections found" >&2
    exit 2
fi

modules=("${sections[0]}")
for section in "${sections[@]:1}"; do
    modules+=("+$section")
done

tools/compile-and-run --save-intcode \
    --dd OPTIONS=native-compiler/bootstrap-cambridge/options-large-tree.txt \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd TRNHDR="$srcdir/trnhdr" \
    asm/icintv19.asm \
    "${modules[@]}"

target=native-compiler/bootstrap-cambridge/trni-large-names.int
: > "$target"
for section in "${sections[@]}"; do
    stem=$(basename "$section")
    cat "workarea/$stem.intcode" >> "$target"
done

echo "generated $target"
wc -c "$target"
