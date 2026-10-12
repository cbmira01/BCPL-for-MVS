#!/usr/bin/env python3
"""Non-installing BCPLMAIN/BCPLMEM candidate link probe; no GO and no OBJ writes."""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "workarea/runtime-object-candidates"
def load_candidate():
    p = ROOT / "tools/checks/prepare-runtime-object-candidates.py"
    spec = importlib.util.spec_from_file_location("candidate", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def main():
    mod = load_candidate()
    mainasm = OUT / "bcplmain-external-mem.asm"
    memasm = ROOT / "asm/bcplmem.asm"
    target = OUT / "link-candidates.jcl"
    target.unlink(missing_ok=True)
    if not mainasm.is_file():
        raise ValueError("first run prepare-runtime-object-candidates.py")
    # Probe does not execute; external BCPLMAIN reference forces its inclusion.
    linked_main = OUT / "bcplmain-link-export.asm"
    source = mainasm.read_text(encoding="ascii")
    anchor = "BCPLMAIN CSECT\\n"
    if source.count(anchor) != 1 or "STKOVFL" not in source:
        raise ValueError("candidate BCPLMAIN STKOVFL anchor missing")
    linked_main.write_text(source.replace(anchor, anchor + "         ENTRY STKOVFL\\n", 1), encoding="ascii")
    caller = OUT / "runtime-link-caller.asm"
    caller.write_text("BCOLINK  CSECT\n"
                      "         EXTRN BCPLMAIN\n"
                      "         DC    A(BCPLMAIN)\n"
                      "         END   BCOLINK\n", encoding="ascii")
    lines = [
      "//BCOLINK  JOB (MVS),'BCPL LINK',CLASS=A,MSGCLASS=A,",
      "//             MSGLEVEL=(1,1)",
      "//* NON-INSTALLING LINK CHECK; NO GO OR PRODUCTION PDS WRITES.",
      *mod.asm("ASMMMAIN","MAINOBJ",linked_main),
      *mod.asm("ASMMMEM","MEMOBJ",memasm,"ASMMMAIN"),
      *mod.asm("ASMPROBE","PROBOBJ",caller,"ASMMMEM"),
      "//LKED     EXEC PGM=IEWL,PARM='LIST,XREF,MAP',",
      "//             COND=((0,NE,ASMMMAIN),(0,NE,ASMMMEM),",
      "//             (0,NE,ASMPROBE))",
      "//SYSLIB   DD DSN=HERC02.BCPL.OBJ,DISP=SHR",
      "//SYSLIN   DD DSN=&&PROBOBJ,DISP=(OLD,DELETE)",
      "//         DD DSN=&&MAINOBJ,DISP=(OLD,DELETE)",
      "//         DD DSN=&&MEMOBJ,DISP=(OLD,DELETE)",
      "//         DD *",
      " INCLUDE OBJ(BCPLBYTE)",
      " INCLUDE OBJ(BCPLAPT)",
      " INCLUDE OBJ(BLIB)",
      " ENTRY BCOLINK",
      " NAME BCOLINK(R)",
      "/*",
      "//SYSLMOD  DD DSN=&&GOSET(BCOLINK),UNIT=SYSDA,",
      "//             SPACE=(1024,(50,20,1)),DISP=(NEW,PASS)",
      "//SYSUT1   DD UNIT=SYSDA,SPACE=(1024,(50,20))",
      "//SYSPRINT DD SYSOUT=*",
      "//",
    ]
    if any(len(row)>71 for row in lines):
        raise ValueError("generated JCL card over 71 columns")
    target.write_text("\n".join(lines)+"\n",encoding="ascii",newline="\n")
    print(f"Prepared non-installing link probe: {target}")
    print("Require all three IFOX steps and IEWL RC=0000; inspect XREF.")
    print("This proves neither GO behavior nor rollback.")
if __name__=="__main__":
    try:
        main()
    except (OSError,ValueError) as e:
        sys.exit(f"runtime-object-link-probe: {e}")
