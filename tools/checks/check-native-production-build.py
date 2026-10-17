#!/usr/bin/env python3
"""Fail-closed static preflight for the complete production OBJ rebuild.

No MVS access or installation. Only checks Git sources, JCL destinations,
and regression profile wiring; operational acceptance still needs JES proof.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
JCL = ROOT / "native-compiler/jcl"
ASM = ROOT / "native-compiler/asm"
RUNTIME = (
    ("BCPLMAIN", "ASMMMAIN", "PUTMAIN"),
    ("BCPLMEM", "ASMMMEM", "PUTMEM"),
    ("BCPLBYTE", "ASMMBYTE", "PUTBYTE"),
    ("BCPLAPT", "ASMMAPT", "PUTAPT"),
    ("BCPLIO", "ASMMIO", "PUTIO"),
)


def require(predicate: bool, message: str) -> None:
    if not predicate:
        raise ValueError(message)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT /
        "tools/checks/check-native-jcl-manifest.py")], check=True)
    subprocess.run([sys.executable, str(ROOT /
        "tools/checks/check-bcplmain-canonical.py")], check=True)
    build = (JCL / "bldbmain.jcl").read_text(encoding="ascii")
    for member, asm_step, put_step in RUNTIME:
        asm = ASM / (member.lower() + ".asm")
        require(asm.is_file(), f"missing source {asm}")
        require(bool(re.search(
            rf"^//{asm_step}\s+EXEC PGM=IFOX00,", build, re.M
        )), f"missing assembly step {asm_step}")
        require(f"//SYSIN    DD DSN=HERC02.BCPL.NATIVE.ASM({member}),"
                in build, f"wrong source for {member}")
        require(bool(re.search(
            rf"^//{put_step}\s+EXEC PGM=IEBGENER,COND=\(0,NE\)$",
            build, re.M,
        )), f"{put_step} must gate binary install on prior RC=0")
        require(f"//SYSUT2   DD DSN=HERC02.BCPL.NATIVE.OBJ({member}),"
                in build, f"wrong production target for {member}")
    require(build.count(" EXEC PGM=IFOX00,") == 5,
            "BLDBMAIN must assemble exactly five modules")
    require(build.count(" EXEC PGM=IEBGENER,COND=(0,NE)") == 5,
            "BLDBMAIN must install exactly five modules")
    require("NATIVE.DEVOBJ" not in build, "BLDBMAIN must not use DEVOBJ")
    blib = (JCL / "blibbld.jcl").read_text(encoding="ascii")
    require("NATIVE.SOURCE(BLIB)" in blib, "BLIB source missing")
    require("NATIVE.OBJ(BLIB)" in blib, "BLIB production target missing")
    require("NATIVE.DEVOBJ" not in blib, "BLIBBLD must not use DEVOBJ")
    generator = (ROOT /
        "tools/checks/prepare-runtime-pds-regression.py"
    ).read_text(encoding="ascii")
    require('or library == "OBJ"' in generator,
            "production BCPLIO linkage branch not found")
    require("INCLUDE OBJ(BCPLBYTE)" in generator and
            "INCLUDE OBJ(BCPLAPT)" in generator,
            "production BYTE/APT must link from OBJ")
    runner = (ROOT /
        "tools/native/run-regression").read_text(encoding="utf-8")
    require("candidate_env or production_env" in runner,
            "production dynamic-stream case gate not found")
    wrapper = ROOT / "tools/native/run-production-regression"
    require(wrapper.is_file() and
            "BCPL_RUNTIME_LIBRARY=OBJ" in wrapper.read_text(
                encoding="ascii"), "production runner missing")
    print("PASS: five canonical ASM modules + BLIB target NATIVE_OBJ")
    print("PASS: all-OBJ native regression profile staged")
    print("NOT EXECUTED: no MVS assembly, link, GO, or PDS purge")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError) as exc:
        sys.exit(f"production OBJ preflight FAIL: {exc}")
