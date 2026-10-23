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
JCL = ROOT / "bootstrap-toolchain/jcl"
ASM = ROOT / "bootstrap-toolchain/asm"
# Six Core Runtime assembler modules plus the empty BCPLREG table.
# The Base Library BLIB is compiled and installed separately.
RUNTIME = (
    ("BCPLMAIN", "bcplmain.asm", "ASMMMAIN", "PUTMAIN"),
    ("BCPLMEM", "bcplmem.asm", "ASMMMEM", "PUTMEM"),
    ("BCPLBYTE", "bcplbyte.asm", "ASMMBYTE", "PUTBYTE"),
    ("BCPLAPT", "bcplapt.asm", "ASMMAPT", "PUTAPT"),
    ("BCPLIO", "bcplio.asm", "ASMMIO", "PUTIO"),
    ("BCPLRGS", "bcplrgs.asm", "ASMRGS", "PUTRGS"),
    ("BCPLREG", "bcplreg-empty.asm", "ASMREG", "PUTREG"),
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
    for member, filename, asm_step, put_step in RUNTIME:
        asm = ASM / filename
        require(asm.is_file(), f"missing source {asm}")
        require(bool(re.search(
            rf"^//{asm_step}\s+EXEC PGM=IFOX00,", build, re.M
        )), f"missing assembly step {asm_step}")
        require(f"//SYSIN    DD DSN=HERC02.BCPL.BOOT.ASM({member}),"
                in build, f"wrong source for {member}")
        require(bool(re.search(
            rf"^//{put_step}\s+EXEC PGM=IEBGENER,COND=\(0,NE\)$",
            build, re.M,
        )), f"{put_step} must gate binary install on prior RC=0")
        require(f"//SYSUT2   DD DSN=HERC02.BCPL.BOOT.OBJ({member}),"
                in build, f"wrong production target for {member}")
    require(build.count(" EXEC PGM=IFOX00,") == 7,
            "BLDBMAIN must assemble six Core Runtime modules plus BCPLREG")
    require(build.count(" EXEC PGM=IEBGENER,COND=(0,NE)") == 7,
            "BLDBMAIN must install seven assembler object members")
    require("HERC02.BCPL.BOOT.DEVOBJ" not in build, "BLDBMAIN must not use DEVOBJ")
    blib = (JCL / "blibbld.jcl").read_text(encoding="ascii")
    require("HERC02.BCPL.BOOT.SOURCE(BLIB)" in blib, "BLIB source missing")
    require("HERC02.BCPL.BOOT.OBJ(BLIB)" in blib, "BLIB production target missing")
    require("HERC02.BCPL.BOOT.DEVOBJ" not in blib, "BLIBBLD must not use DEVOBJ")
    generator = (ROOT /
        "tools/checks/prepare-runtime-pds-regression.py"
    ).read_text(encoding="ascii")
    require('or library == "OBJ"' in generator,
            "production BCPLIO linkage branch not found")
    require("INCLUDE OBJ(BCPLBYTE)" in generator and
            "INCLUDE OBJ(BCPLAPT)" in generator,
            "production BYTE/APT must link from OBJ")
    require("INCLUDE OBJ(BCPLRGS)" in generator and
            "INCLUDE OBJ(BCPLREG)" in generator and
            'os.environ.get("R1_ACCEPTANCE") != "1"' in generator,
            "production requires registrar and exactly one empty table")
    runner = (ROOT /
        "tools/bootstrap/run-regression").read_text(encoding="utf-8")
    require("candidate_env or production_env" in runner,
            "production dynamic-stream case gate not found")
    wrapper = ROOT / "tools/bootstrap/run-production-regression"
    require(wrapper.is_file() and
            "BCPL_RUNTIME_LIBRARY=OBJ" in wrapper.read_text(
                encoding="ascii"), "production runner missing")
    compiler_driver = ROOT / "tools/bootstrap/compile-mvs"
    require(compiler_driver.is_file(), "bootstrap compiler driver missing")
    mvs_runner = (ROOT / "bootstrap-toolchain/regression/run-test-mvs.sh"
                  ).read_text(encoding="ascii")
    require('export CAMBRIDGE_COMPILE="$root/tools/bootstrap/compile-mvs"'
            in mvs_runner, "MVS test wrapper has stale compiler driver")
    case_runner = (ROOT / "bootstrap-toolchain/regression/run-test.sh"
                   ).read_text(encoding="ascii")
    require('$root/tools/bootstrap/compile-mvs' in case_runner,
            "test harness has stale compiler fallback")
    for source in (mvs_runner, case_runner):
        require("tools/native/" not in source,
                "obsolete tools/native/ reference in regression harness")
    print("PASS: six Core Runtime ASM modules, BCPLREG and BLIB target BOOT_OBJ")
    print("PASS: all-OBJ native regression profile staged")
    print("NOT EXECUTED: no MVS assembly, link, GO, or PDS purge")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError) as exc:
        sys.exit(f"production OBJ preflight FAIL: {exc}")
