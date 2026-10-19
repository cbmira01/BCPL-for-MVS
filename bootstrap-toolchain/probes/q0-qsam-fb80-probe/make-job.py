#!/usr/bin/env python3
"""Generate a disposable MVS Q.0 FB80 QSAM experiment.

This uses the repository's proven IFOX/IEWL/GO job generator, authenticates
using the effective local dspal settings, and adds DD DATA input and SYSOUT
output.  It does not install an MVS object or update a PDS member.
"""
from __future__ import annotations

from pathlib import Path
import importlib.util
from importlib.machinery import SourceFileLoader
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT / "workarea/qsam-q0-fb80"


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        spec = importlib.util.spec_from_loader(
            name, SourceFileLoader(name, str(path))
        )
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def make() -> Path:
    jobmod = module(ROOT / "tools/mvs/make-asm-job", "q0_asm_job")
    core = module(ROOT / "tools/datasets/dspal-core.py", "q0_dspal")
    config = core.load_config()
    source = jobmod.check_source(HERE / "fixed-fb80.asm")
    cards = jobmod.make_deck(
        source, "fixed-fb80.asm", "Q0FBPRB", "QS0FBR", "heavy", None
    ).splitlines()
    if not (cards[0].startswith("//QS0FBR") and
            cards[1] == "//             MSGLEVEL=(1,1)"):
        raise ValueError("unrecognized make-asm-job header")
    # The generated job file is PRIVATE: never commit credentials to Git.
    cards[:2] = core.authenticated_job_card(
        config, "QS0FBR", "QSAM Q0 FB80", redact_password=False
    )
    anchor = "//SYSUDUMP DD  SYSOUT=*"
    if cards.count(anchor) != 1 or cards[-1] != "//":
        raise ValueError("unrecognized GO DD layout")
    i = cards.index(anchor) + 1
    records = ["Q0FIX001" + " " * 71 + "X",
               "Q0FIX002" + " " * 71 + "Y"]
    assert all(len(r) == 80 for r in records)
    cards[i:i] = [
        "//QIN      DD DATA,DLM=QZ",
        *records, "QZ",
        "//QOUT     DD SYSOUT=*,",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
    ]
    if any((len(line) > 71 and line not in records) or
           not line.isascii() for line in cards):
        raise ValueError("invalid JCL card (DATA records may be 80)")
    WORK.mkdir(parents=True, exist_ok=True)
    outfile = WORK / "qs0-fb80.jcl"
    outfile.write_text("\n".join(cards) + "\n", encoding="ascii")
    return outfile


if __name__ == "__main__":
    try:
        print("Q.0 QSAM job:", make())
    except (OSError, ValueError, RuntimeError) as exc:
        raise SystemExit(f"Q.0 FB80 probe generation failed: {exc}")
