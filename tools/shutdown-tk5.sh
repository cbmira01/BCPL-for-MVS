#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

docker compose \
    -f "$repo_root/docker/compose.yaml" \
    stop \
    --timeout 180 \
    mvs

