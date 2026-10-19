#!/usr/bin/env python3
"""Verify canonical native assembler member mapping without PDS changes.

Each NATIVE_ASM member must correspond to exactly one maintained .asm file.
Historical D3-D7 variants are not manifest members. This tool does not
assemble, submit jobs, or promote any production object.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config/dspal.yaml"
ASM = ROOT / "bootstrap-toolchain/asm"
CANONICAL = ("BCPLMAIN", "BCPLIO", "BCPLMEM", "BCPLBYTE", "BCPLAPT")


def main() -> None:
    yaml = MANIFEST.read_text(encoding="utf-8")
    start = yaml.index("\n  NATIVE_ASM:\n")
    end = yaml.index("\n  NATIVE_JCL:\n", start)
    section = yaml[start:end]
    member_lines = section.split("    members:\n", 1)[1]
    entries = re.findall(r"^      ([A-Z0-9]+):\s+(\S+)\s*$",
                         member_lines, re.M)
    expected = [(member, f"bootstrap-toolchain/asm/{member.lower()}.asm")
                for member in CANONICAL]
    if entries != expected:
        raise ValueError(f"NATIVE_ASM mappings differ from canonical list:"
                         f"\n  actual: {entries}\n  wanted: {expected}")
    for _, path in expected:
        source = ROOT / path
        if not source.is_file():
            raise ValueError(f"missing assembler source: {source}")
        subprocess.run([sys.executable,
                        str(ROOT / "tools/checks/check-asm-source.py"),
                        str(source)], check=True)
    main_source = (ASM / "bcplmain.asm").read_text(encoding="ascii")
    if main_source.count("BCPLMAIN CSECT") != 1 or (
        main_source.count("         END   BCPLMAIN") != 1
    ):
        raise ValueError("unexpected BCPLMAIN CSECT/END structure")
    candidate = (ROOT / "bootstrap-toolchain/jcl/history/build-dev-bcplm6.jcl"
                 ).read_text(encoding="ascii")
    if "NATIVE.ASM(BCPLMAIN)" not in candidate:
        raise ValueError("historical BCPLM6 job does not read canonical source")
    if "NATIVE.DEVOBJ(BCPLM6)" not in candidate or (
        "NATIVE.OBJ(BCPLM6)" in candidate
    ):
        raise ValueError("historical BCPLM6 job targets unexpected library")
    jcl = yaml[end:yaml.index("\n  NATIVE_OBJ:\n", end)]
    if "BLDDEVM6:" in jcl:
        raise ValueError("historical versioned JCL is still manifest-mapped")
    print("PASS: 5 canonical ASM sources, 5 matching PDS members;"
          " historical versions unmapped")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"canonical runtime manifest FAIL: {exc}")
