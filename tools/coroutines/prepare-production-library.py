#!/usr/bin/env python3
"""Prepare installed COROUTIN IFOX from separately Cambridge-compiled BCPL.

The production BCPL body equals the accepted CO.3 lifecycle library after
two header comments. Preserve the tested CG370 export/alias transforms.
This command makes only a host-generated file; it does not install MVS objects.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "packaging/milestones/coroutines/candidates/co3-delete-reuse"
BASE = ROOT / "tools/coroutines/run-co3-first-lifecycle.py"
ADAPTER = ROOT / "tools/coroutines/run-co3-delete-reuse.py"
PROD = ROOT / "bootstrap-toolchain/library/coroutines.bcpl"
HDR = ROOT / "bootstrap-toolchain/library/coroutines.h"
GLOBALS = {
    "CO3INIT": 289, "CREATECO": 290, "DELETECO": 291,
    "CALLCO": 292, "COWAIT": 293, "RESUMECO": 294,
    "CO3CURR": 295, "CO3ROOT": 296, "CO3LIST": 297,
    "CO2INIT": 298, "CHANGECO": 299, "CO3DROP": 300,
}


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check() -> None:
    accepted = (CAND / "library.bcpl").read_text("ascii").splitlines()
    production = PROD.read_text("ascii").splitlines()
    if len(accepted) < 15 or production[2:] != accepted[2:]:
        raise ValueError("production BCPL body differs from accepted CO.3")
    if "Private G289-300" not in accepted[1]:
        raise ValueError("accepted CO.3 source contract has changed")
    actual = {}
    for row in HDR.read_text("ascii").splitlines():
        row = row.strip()
        if ":" not in row or row.startswith("//"):
            continue
        name, number = row.split(":")
        if name in actual or not number.isdigit():
            raise ValueError("invalid or repeated production global")
        actual[name] = int(number)
    if actual != GLOBALS:
        raise ValueError(f"wrong production global declarations: {actual}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="source check only")
    ap.add_argument("--compiled", type=Path, help="raw CG370 listing")
    ap.add_argument("--output", type=Path, help="prepared IFOX file")
    args = ap.parse_args()
    source_check()
    if args.check and args.compiled is None and args.output is None:
        print("Production BCPL source/global check PASS")
        return 0
    if args.compiled is None or args.output is None:
        ap.error("--compiled and --output must be provided together")
    if args.compiled.resolve() == args.output.resolve():
        ap.error("refusing to overwrite compiler output in place")
    driver = load("co5_lib_base", BASE)
    adapter = load("co5_lib_adapter", ADAPTER)
    adapter.configure(driver)
    rows = driver.generated_library(args.compiled.read_text("latin-1"))
    if sum(row.startswith("C3DELETE EQU") for row in rows) != 1:
        raise ValueError("DELETECO native alias missing")
    if not any("ENTRY C3INIT,C3CREATE,C3DELETE" in row for row in rows):
        raise ValueError("production BCPL exports missing")
    if rows[-1].strip() != "END   CO3LIB":
        raise ValueError("unexpected CG370 library terminator")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(rows) + "\n", encoding="ascii")
    print(f"Prepared IFOX COROUTIN: {args.output} ({len(rows)} cards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
