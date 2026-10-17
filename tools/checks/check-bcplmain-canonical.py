#!/usr/bin/env python3
"""Check canonical BCPLMAIN source and the no-promotion manifest boundary.

The current developed BCPLMAIN is D6/BCPLM6. The earlier M1.6
pre-D6 canonical equivalence test is now historical, not an active gate.
This check never writes to a PDS, rebuilds objects, or runs MVS jobs.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ASM = ROOT / "native-compiler/asm"
CANONICAL = ASM / "bcplmain.asm"
BASELINE = ASM / "history/bcplmain-pre-d6-production.asm"
MANIFEST = ROOT / "config/dspal.yaml"


def main() -> None:
    source = CANONICAL.read_text(encoding="ascii")
    baseline = BASELINE.read_text(encoding="ascii")
    mapping = MANIFEST.read_text(encoding="utf-8")

    for entry in ("BCPLMAIN CSECT", "         END   BCPLMAIN"):
        if source.count(entry) != 1:
            raise ValueError(f"unexpected canonical assembly anchor: {entry}")
    if source == baseline:
        raise ValueError("canonical source was accidentally reverted to pre-D6")
    for key, path in (
        ("BCPLM6", "native-compiler/asm/bcplmain.asm"),
        ("BCPLMAIN",
         "native-compiler/asm/history/bcplmain-pre-d6-production.asm"),
        ("BCPLM7", "native-compiler/asm/history/bcplmain-d7-candidate.asm"),
        ("BCPLMEM", "native-compiler/asm/bcplmem.asm"),
        ("BCPLBYTE", "native-compiler/asm/bcplbyte.asm"),
        ("BCPLAPT", "native-compiler/asm/bcplapt.asm"),
        ("BCPLIO", "native-compiler/asm/bcplio.asm"),
    ):
        expression = rf"^\s+{key}:\s+{re.escape(path)}\s*$"
        if len(re.findall(expression, mapping, flags=re.M)) != 1:
            raise ValueError(f"unexpected NATIVE_ASM mapping: {key}")
        if not (ROOT / path).is_file():
            raise ValueError(f"manifest assembler source missing: {path}")
    subprocess.run([sys.executable, str(ROOT / "tools/checks/check-asm-source.py"),
                    str(CANONICAL)], check=True)
    print("PASS: BCPLMAIN source naming, DEVOBJ/OBJ boundary and IFOX cards")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"canonical BCPLMAIN: FAIL: {exc}")
