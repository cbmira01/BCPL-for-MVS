#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

BOOT=native-compiler/bootstrap-cambridge
TRNI="$BOOT/trni-large-names.int"
ICINT=asm/icintv19.asm

# Rebuild deterministic Cambridge bootstrap source derivatives every time.
python3 "$BOOT/make-demoted.py"

# V19 is generated, not authoritative source.  Recreate it if local cleanup
# removed it; do not overwrite an existing candidate automatically.
if [[ ! -f "$ICINT" ]]; then
    python3 "$BOOT/make-icintv19.py"
fi

# The larger-name MR10 translator is also generated.  Build it only when it is
# absent because doing so itself submits compiler work to MVS.
if [[ ! -f "$TRNI" ]]; then
    bash "$BOOT/build-mr10-trni-large-names.sh"
fi

# Load order is intentional.  The Cambridge BCPL master is first so its START
# is the resident image entry; all remaining implementation sections follow and
# rendezvous through the shared global vector.  bootstrap-host.bcpl supplies
# only host services proven missing from the current MR10 runtime.  BLIBI and
# ICLIB are appended by compile-and-run after these generated modules.
exec tools/compile-and-run --results --timeout 600 \
    --trni "$TRNI" \
    --dd OPTIONS="$BOOT/options-large-tree.txt" \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd SYNHDR=richards-bcpltape/bcplib/bcpl/synhdr \
    --dd TRNHDR=richards-bcpltape/bcplib/bcpl/trnhdr \
    --dd CGHDR=richards-bcpltape/bcplib/bcpl/cghdr \
    "$ICINT" \
    "$BOOT/demoted/bcpl" \
    +"$BOOT/demoted/syn" \
    +"$BOOT/demoted/lex" \
    +"$BOOT/demoted/trna" \
    +"$BOOT/demoted/trnb" \
    +"$BOOT/demoted/cga" \
    +"$BOOT/demoted/cgb" \
    +"$BOOT/demoted/cgc" \
    +"$BOOT/demoted/cgd" \
    +"$BOOT/demoted/cge" \
    +"$BOOT/bootstrap-host.bcpl"
