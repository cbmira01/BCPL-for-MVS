#!/usr/bin/env python3
"""Fail-closed local source inspection of all M4.1 BCPLIO fault variants.

No MVS connection, JCL submission, or installed PDS modification.
Not a substitute for IFOX00 assembly and runtime regression results.
"""
from __future__ import annotations

from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    namespace = runpy.run_path(
        str(ROOT / "tools/checks/prepare-bcplio-m41-fault.py"),
        run_name="bcplio_m41_fault_library",
    )
    instrument = namespace["instrument"]
    sites = namespace["SITES"]
    original = (
        ROOT / "bootstrap-toolchain/asm/bcplio.asm"
    ).read_text(encoding="ascii")
    total_getmains = original.count("GETMAIN RC,LV=")
    for mode, (anchor, prefix, data_anchor) in sites.items():
        generated = instrument(original, mode)
        phase = prefix + "PH"
        assert original.count(anchor) == 1, mode
        assert generated.count(anchor) == 0, mode
        assert generated.count("GETMAIN RC,LV=") == total_getmains, mode
        assert generated.count(f"{phase:<8} DC    X'00'") == 1, mode
        assert generated.count(f"CLI   {phase},X'01'") == 1, mode
        assert generated.count("         LA    15,8") >= 1, mode
        assert data_anchor in generated, mode
        assert all(len(line) <= 71 for line in generated.splitlines()), mode
        try:
            instrument(generated, mode)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{mode}: reinstrumentation not rejected")
        print(f"M4.1 {mode}: anchor unique, single fault armed, "
              "re-instrumentation rejected, IFOX card width OK")
    print("M4.1 source-only checks: PASS (MVS execution NOT attempted)")


if __name__ == "__main__":
    main()
