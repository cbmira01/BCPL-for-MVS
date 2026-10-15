#!/usr/bin/env python3
"""Prepare (but never submit) an installed-runtime-object linkage probe.

Requires HERC02.BCPL.OBJ members BCPLMAIN/BCPLBYTE/BCPLAPT/BCPLMEM/BLIB.
Input is a recovered Cambridge application assembler file (e.g. test 069).
"""
from pathlib import Path
import argparse
import importlib.util

ROOT = Path(__file__).resolve().parents[2]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("generated_assembly", type=Path)
    p.add_argument("output_jcl", type=Path)
    args = p.parse_args()
    args.output_jcl.unlink(missing_ok=True)
    stage = module(ROOT / "native-compiler/regression/069-independent-blib-object/prepare-linkage.py",
                   "blib_app_cards")
    core = module(ROOT / "tools/datasets/dspal-core.py", "obj_consumer_dspal")
    cfg = core.load_config()
    obj, _ = core.resolve_dsn(cfg, "OBJ")
    if obj.upper() != "HERC02.BCPL.OBJ":
        raise ValueError(f"unexpected object library {obj}")
    app = stage.app_cards(args.generated_assembly)
    cards = [
        *core.authenticated_job_card(cfg, "BCOBJP69", "BCPL OBJ LINK",
                                    redact_password=False),
        "//* INSTALLED OBJECT PROBE; DOES NOT UPDATE OBJECT LIBRARY.",
        "//* REQUIRES ALL FIVE MEMBERS AND STARTUP BLIB REGISTRATION.",
        "//ASMAP    EXEC PGM=IFOX00,REGION=256K,",
        "//             PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'",
        "//SYSLIB   DD DSN=SYS1.MACLIB,DISP=SHR",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1700,(600,100))",
        "//SYSUT2   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSUT3   DD UNIT=SYSDA,SPACE=(1700,(300,50))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSPUNCH DD DUMMY",
        "//SYSGO    DD DSN=&&APOBJ,UNIT=SYSDA,",
        "//             SPACE=(80,(300,100)),DISP=(NEW,PASS),",
        "//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
        "//SYSIN    DD *",
        *app.rstrip("\n").splitlines(),
        "/*",
        "//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
        "//             COND=(0,NE,ASMAP)",
        f"//OBJ      DD DSN={obj},DISP=SHR",
        "//SYSLIN   DD DSN=&&APOBJ,DISP=(OLD,DELETE)",
        "//         DD *",
        " INCLUDE OBJ(BCPLMAIN)",
        " INCLUDE OBJ(BCPLBYTE)",
        " INCLUDE OBJ(BCPLAPT)",
        " INCLUDE OBJ(BCPLMEM)",
        " INCLUDE OBJ(BLIB)",
        " ENTRY BCRG0069",
        " NAME BCOBJ069(R)",
        "/*",
        "//SYSLMOD  DD DSN=&&GOSET(BCOBJ069),UNIT=SYSDA,",
        "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
        "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
        "//SYSPRINT DD SYSOUT=*",
        "//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,3),",
        "//             COND=((0,NE,ASMAP),(0,NE,LKED))",
        "//SYSPRINT DD SYSOUT=*,DCB=(RECFM=FB,LRECL=132,BLKSIZE=132)",
        "//SYSUDUMP DD SYSOUT=*",
        "//",
    ]
    for i, line in enumerate(cards, 1):
        if len(line) > 71 or not line.isascii():
            raise ValueError(f"invalid JCL card {i}: {line!r}")
    args.output_jcl.parent.mkdir(parents=True, exist_ok=True)
    args.output_jcl.write_text("\n".join(cards) + "\n",
                               encoding="ascii", newline="\n")
    print(f"Prepared installed-object consumer: {args.output_jcl}")
    print("Requires installed members; no submission or PDS writes performed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(f"installed-object-consumer: {error}")
