#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

BOOT=native-compiler/bootstrap-cambridge
TRNI=workarea/bootstrap-cambridge/trni-large-names.int
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
    --dd CAMBPARM="$BOOT/cambridge-options.txt" \
    --dd LIBHDR=richards-bcpltape/sys3/bcpl/libhdr \
    --dd SYNHDR=richards-bcpltape/bcplib/bcpl/synhdr \
    --dd TRNHDR=richards-bcpltape/bcplib/bcpl/trnhdr \
    --dd CGHDR=richards-bcpltape/bcplib/bcpl/cghdr \
    "$ICINT" \
    "workarea/bootstrap-cambridge/demoted/bcpl" \
    +"workarea/bootstrap-cambridge/demoted/syn" \
    +"workarea/bootstrap-cambridge/demoted/lex" \
    +"workarea/bootstrap-cambridge/demoted/trna" \
    +"workarea/bootstrap-cambridge/demoted/trnb" \
    +"workarea/bootstrap-cambridge/demoted/cga" \
    +"workarea/bootstrap-cambridge/demoted/cgb" \
    +"workarea/bootstrap-cambridge/demoted/cgc" \
    +"workarea/bootstrap-cambridge/demoted/cgd" \
    +"workarea/bootstrap-cambridge/demoted/cge" \
    +"$BOOT/bootstrap-host.bcpl"
