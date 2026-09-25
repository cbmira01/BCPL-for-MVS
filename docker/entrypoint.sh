#!/usr/bin/env bash
set -euo pipefail

# Commands operating on the TK5 environment expect TK5-relative paths.
cd /tk5

exec "$@"

