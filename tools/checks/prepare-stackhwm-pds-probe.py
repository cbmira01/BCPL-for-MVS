#!/usr/bin/env python3
"""Prepare standalone installed-PDS STACKHWM probe; does not submit JCL.

Uses the existing Cambridge compiler driver and installed-runtime JCL
preparer. No numbered regression directory or OBJ member is modified.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools/checks/stackhwm-pds-probe.bcpl"
OUT = ROOT / "workarea/stackhwm-pds-probe"
NAME = "stackhwm-pds-probe"


def run(*argv: str) -> None:
    subprocess.run([sys.executable, *map(str, argv)], cwd=ROOT, check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / f"{NAME}.bcpl"
    source.write_bytes(SOURCE.read_bytes())
    deck = OUT / "stackhwm-installed.jcl"
    deck.unlink(missing_ok=True)
    generated = ROOT / "workarea" / f"{NAME}.s370.asm"
    generated.unlink(missing_ok=True)
    run(ROOT / "tools/native/compile-mvs", source,
        "--job-name", "RG120C", "--listing", "light", "--timeout", "180")
    if not generated.is_file():
        raise RuntimeError(f"expected Cambridge CODE at {generated}")
    run(ROOT / "tools/checks/prepare-runtime-pds-regression.py",
        generated, deck, "--test-number", "120")
    cards = deck.read_text(encoding="ascii")
    for wanted in (
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(BLIB)",
        "//GO       EXEC",
    ):
        if wanted not in cards:
            raise RuntimeError(f"missing probe deck contract: {wanted}")
    if "DSN=HERC02.BCPL.OBJ(" in cards:
        raise RuntimeError("unexpected PDS member update DD")
    print(f"Generated: {generated}")
    print(f"Read-only installed-PDS linkage probe: {deck}")
    print("Review JCL before running. No job submitted; no OBJ members changed.")
    print("The JCL may contain local authentication details. Do not commit it.")
    print("Submit: tools/mvs/submit-jcl " + str(deck.relative_to(ROOT)))
    print("Inspect: tools/mvs/job-summary <job-number>")
    print("Report: tools/mvs/dump-report-for-job <job-number>")
    print("Inspect IEWL MAP/XREF for BLIB and runtime calls,")
    print("and GO output for STACKBASE/STACKEND/STACKHWM.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"prepare-stackhwm-pds-probe: {exc}")
