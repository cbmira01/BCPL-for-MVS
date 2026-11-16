#!/usr/bin/env python3
"""Verify the exact production BOOT_OBJ inventory after clean-room rebuild."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import VerificationError, inventory_members, required_inventory


def verify_listing(stdout: str, dsn: str) -> frozenset[str]:
    members = inventory_members(stdout, dsn)
    required_inventory('BOOT_OBJ', members)
    return members


def main() -> int:
    try:
        source = ROOT / 'tools/datasets/dspal-core.py'
        spec = importlib.util.spec_from_file_location('co5_dspal_core', source)
        if spec is None or spec.loader is None:
            raise RuntimeError('cannot load dspal configuration')
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        cfg = core.load_config()
        dsn = core.full_dsn(cfg, cfg['datasets']['BOOT_OBJ'])
        result = subprocess.run(
            [str(ROOT / 'tools/datasets/dspal'), 'ls', 'BOOT_OBJ'],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=180)
        if result.returncode != 0:
            raise RuntimeError(f'MVS inventory command RC={result.returncode}')
        members = verify_listing(result.stdout, dsn)
    except (OSError, ValueError, RuntimeError, VerificationError,
            subprocess.TimeoutExpired) as exc:
        print(f'BOOT_OBJ INVENTORY FAIL: {exc}', file=sys.stderr)
        return 1
    print(f'BOOT_OBJ INVENTORY PASS: {len(members)} exact production members')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
