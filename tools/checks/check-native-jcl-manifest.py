#!/usr/bin/env python3
"""Check canonical BOOT_JCL manifest/source names; never submit MVS jobs."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config/dspal.yaml"
DIRECTORY = ROOT / "bootstrap-toolchain/jcl"
MEMBERS = (
    "BLIBBLD",
    "BLDBMAIN",
    "BLDDEVM",
    "BLDDEVN",
    "BLDDEVB",
    "BLDDEVI",
    "BLDDEVA",
    "BLDDEVL",
    "CAMBBLD",
    "CG370DB",
    "BLDRGCHK",
    "R5DINST",
    "T1TINST",
)


def main() -> None:
    config = MANIFEST.read_text(encoding="utf-8")
    begin = config.index("\n  BOOT_JCL:\n")
    end = config.index("\n  BOOT_OBJ:\n", begin)
    section = config[begin:end].split("    members:\n", 1)[1]
    entries = re.findall(
        r"^      ([A-Z0-9]+): (bootstrap-toolchain/jcl/[a-z0-9-]+\.jcl)\s*$",
        section, flags=re.M,
    )
    expected = [(name, f"bootstrap-toolchain/jcl/{name.lower()}.jcl")
                for name in MEMBERS]
    if entries != expected:
        raise ValueError(f"noncanonical BOOT_JCL mapping:"
                         f"\n  actual: {entries}\n  expected: {expected}")
    other_mappings = [
        line for line in section.splitlines()
        if re.match(r"^      [A-Za-z][A-Za-z0-9]*:", line)
        and not any(line.lstrip().startswith(name + ":")
                    for name in MEMBERS)
    ]
    if other_mappings:
        raise ValueError(f"unexpected BOOT_JCL member: {other_mappings}")
    actual_files = sorted(p.name for p in DIRECTORY.glob("*.jcl"))
    expected_files = sorted(f"{name.lower()}.jcl" for name in MEMBERS)
    if actual_files != expected_files:
        raise ValueError(f"top-level JCL files are not canonical:"
                         f"\n  actual: {actual_files}\n"
                         f"  expected: {expected_files}")
    for name, relative in expected:
        if len(name) > 8:
            raise ValueError(f"MVS member exceeds 8 characters: {name}")
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing regular JCL source: {path}")
        data = path.read_bytes()
        if b"\r" in data or b"\t" in data:
            raise ValueError(f"invalid JCL control characters: {path}")
        data.decode("ascii")
        if any(len(line) > 80 for line in data.splitlines()):
            raise ValueError(f"JCL record exceeds FB80: {path}")
    print("PASS: 13 canonical BOOT_JCL members and same-named JCL sources")
    print("No MVS jobs were submitted; production OBJ remains unchanged.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as err:
        sys.exit(f"native JCL manifest check FAIL: {err}")
