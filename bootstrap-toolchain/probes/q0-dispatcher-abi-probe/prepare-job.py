#!/usr/bin/env python3
"""Q.0 probe-only G!200 trailer binding and BOOT_OBJ/DEVOBJ JCL maker.

Run from a BCPL-for-MVS checkout.  Does not change the runtime, PDS objects,
compiler, Global Number Registry, or source files.  Generated GO JCL uses
IEWL inclusion from the manifest-managed BOOT_OBJ/BOOT_DEVOBJ PDSs.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ENTRY = "Q0APPL"
SYMBOL = "Q0DISP"
GLOBAL = 200


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapt_generated(generated: str) -> str:
    """Inject one G!200 export whose address relocates to Q0DISP."""
    helper = load(ROOT / "bootstrap-toolchain/regression/prepare-native-global.py",
                  "native_global_q0")
    text = "".join(c if ord(c) < 128 else "?" for c in generated)
    lines = text.splitlines()
    csect = helper.one_index(lines, helper.CSECT, "generated CSECT")
    extrn = helper.one_index(lines, helper.EXTRN_MAIN, "EXTRN BCPLMAIN")
    ending = helper.one_index(lines, helper.END_STMT, "END")
    lines[csect] = f"{ENTRY} CSECT"
    lines.insert(csect + 1, f"         EXTRN {SYMBOL}")
    # Keep original EXTRN BCPLMAIN for separately linked BOOT_OBJ.
    assert helper.EXTRN_MAIN.fullmatch(lines[extrn + 1])
    del lines[ending + 1]
    start, maximum, pairs = helper.find_trailer(lines)
    offset = 4 * GLOBAL
    if any(g == offset for g, _ in pairs):
        raise ValueError("G!200 already exported; refuse duplicate binding")
    last = helper.one_index(lines, helper.L998, "L998")
    export = [f"         DC F'{max(maximum, offset)}'", "         DC F'0'"]
    for old_off, address in pairs:
        export.extend((f"         DC F'{old_off}'",
                       f"         DC A({address})"))
    export.extend((f"         DC F'{offset}'", f"         DC A({SYMBOL})"))
    lines[start:last] = export
    lines.append(f"         END   {ENTRY}")
    result = "\n".join(lines).rstrip() + "\n"
    validate_cards(result, "generated BCPL application")
    # Ensure exactly one new binding and the original BCPLMAIN external.
    if result.count("         DC F'800'\n         DC A(Q0DISP)") != 1:
        raise ValueError("no unique G!200/Q0DISP export")
    if sum(bool(helper.EXTRN_MAIN.fullmatch(line))
           for line in result.splitlines()) != 1:
        raise ValueError("lost or duplicate EXTRN BCPLMAIN")
    return result


def validate_cards(source: str, label: str) -> None:
    if not source.strip():
        raise ValueError(f"{label}: empty")
    for n, line in enumerate(source.splitlines(), 1):
        if (len(line) > 71 or line in ("/*",) or line.startswith("//")
                or not line.isascii() or "\t" in line):
            raise ValueError(f"{label}:{n}: invalid assembler card")


def asm_step(step: str, obj: str, source: str, condition: str = "") -> list[str]:
    cond = f",COND=(0,NE,{condition})" if condition else ""
    # Keep EXEC < 71 chars even when conditional.
    return [
        f"//{step:<8} EXEC PGM=IFOX00,REGION=256K{cond},",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        f"//SYSGO    DD DSN=&&{obj},UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD *",
        *source.rstrip("\n").splitlines(),
        "/*",
    ]


def make_deck(application: str, native: str, profile: str, core) -> str:
    config = core.load_config()
    for item in ("BOOT_OBJ", "BOOT_DEVOBJ"):
        ds = config["datasets"][item]
        if (ds.get("content_type") != "object" or ds.get("recfm") != "FB"
                or int(ds.get("lrecl", 0)) != 80 or ds.get("dsorg") != "PO"):
            raise ValueError(f"{item} is not FB80 object PDS")
    obj = core.full_dsn(config, config["datasets"]["BOOT_OBJ"])
    dev = core.full_dsn(config, config["datasets"]["BOOT_DEVOBJ"])
    includes = ([" INCLUDE OBJ(BCPLMAIN)", " INCLUDE OBJ(BCPLIO)",
                 " INCLUDE OBJ(BCPLBYTE)", " INCLUDE OBJ(BCPLAPT)",
                 " INCLUDE OBJ(BCPLMEM)", " INCLUDE OBJ(BLIB)"]
                if profile == "OBJ" else
                [" INCLUDE DEVOBJ(BCPLM6)", " INCLUDE DEVOBJ(BCPLIO)",
                 " INCLUDE DEVOBJ(BCPLBYTE)", " INCLUDE DEVOBJ(BCPLAPT)",
                 " INCLUDE OBJ(BCPLMEM)", " INCLUDE OBJ(BLIB)"])
    cards = [
        *core.authenticated_job_card(config, "QS0DISPR", "QSAM Q0 ABI",
                                    redact_password=False),
        "//* Q.0 ABI PROBE: NO QSAM I/O; NO PDS MEMBER IS OVERWRITTEN",
        f"//* CORE LINK PROFILE: {profile}",
        *asm_step("ASMAP", "APOBJ", application),
        *asm_step("ASMNAT", "NATOBJ", native, "ASMAP"),
        "//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
        "//             COND=((0,NE,ASMAP),(0,NE,ASMNAT))",
        f"//OBJ      DD DSN={obj},DISP=SHR",
        *([f"//DEVOBJ   DD DSN={dev},DISP=SHR"]
          if profile == "DEVOBJ" else []),
        "//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)",
        "//         DD DSN=&&NATOBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        *includes,
        f" ENTRY {ENTRY}",
        " NAME Q0APPL(R)",
        "/*",
        "//SYSLMOD  DD DSN=&&GOSET(Q0APPL),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,1),",
        "//             COND=((0,NE,ASMAP),(0,NE,ASMNAT),(0,NE,LKED))",
        "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    for n, line in enumerate(cards, 1):
        if len(line) > 71 or not line.isascii():
            raise ValueError(f"JCL:{n}: card longer than 71 / non-ASCII")
    return "\n".join(cards) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generated", required=True, type=Path,
                    help="S/370 assembler recovered by tools/bootstrap/compile-mvs")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--profile", choices=("OBJ", "DEVOBJ"), default="OBJ")
    args = ap.parse_args()
    core = load(ROOT / "tools/datasets/dspal-core.py", "q0_dspal_core")
    raw = args.generated.read_bytes().decode("latin-1")
    app = adapt_generated(raw)
    native = (HERE / "dispatcher.asm").read_text(encoding="ascii")
    validate_cards(native, "test dispatcher")
    deck = make_deck(app, native, args.profile, core)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(deck, encoding="ascii", newline="\n")
    print(f"Wrote test-only Q.0 GO deck: {args.output}")
    print("Verified one G!200 export with relocatable external Q0DISP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
