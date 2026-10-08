#!/usr/bin/env python3
"""Generate authenticated, non-destructive HERC02.BCPL.OBJ allocation JCL."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_core():
    path = ROOT / "tools" / "dspal-core.py"
    spec = importlib.util.spec_from_file_location("dspal_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    core = load_core()
    config = core.load_config()
    dsn = core.full_dsn(config, {"dsn": "BCPL.OBJ"})
    spec = {
        "type": "pds", "dsorg": "PO", "recfm": "FB",
        "lrecl": 80, "blksize": 800, "space_unit": "TRK",
        "primary": 10, "secondary": 5, "directory": 20,
    }
    lines = core.authenticated_job_card(
        config, "BLIBALOC", "BLIB OBJ ALLOC", redact_password=False
    )
    lines.extend([
        "//* ONLY SUBMIT AFTER VERIFYING THIS DSN IS NOT IN THE CATALOG.",
        "//* DISP=NEW WILL NOT REPLACE AN EXISTING DATA SET.",
        "//ALLOC    EXEC PGM=IEFBR14",
        f"//OBJ      DD DSN={dsn},DISP=(NEW,CATLG,DELETE),",
        f"//             UNIT={config['mvs']['default_unit']},",
        f"//             {core.allocation_clause(config, spec)},",
        f"//             {core.dcb_clause(spec)}",
        "//",
    ])
    deck = "\n".join(lines) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        args.output.chmod(0o600)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="ascii", newline="\n") as out:
        out.write(deck)
    print(args.output)


if __name__ == "__main__":
    main()
