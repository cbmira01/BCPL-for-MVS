#!/usr/bin/env python3
"""Prepare NON-INSTALLING IFOX assembly JCL for the BCPLMAIN/BCPLMEM pair.

Produces disposable transformed BCPLMAIN source and temporary FB80 object
datasets in one MVS job. Does not copy to HERC02.BCPL.OBJ.
"""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

def cards(path):
    text = path.read_text(encoding="ascii")
    rows = text.splitlines()
    if not rows or any(len(x) > 71 or "\t" in x or x == "/*"
                       or x.startswith("//") for x in rows):
        raise ValueError(f"invalid assembler cards: {path}")
    return rows

def asm(name, obj, source, cond=None):
    result = [f"//{name:<8} EXEC PGM=IFOX00,REGION=256K,"]
    if cond:
        result.append(f"//             COND=(0,NE,{cond}),")
    result += [
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
        *cards(source),
        "/*",
    ]
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path,
                   default=ROOT / "workarea/runtime-object-candidates")
    args = p.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    mainasm = out / "bcplmain-external-mem.asm"
    deck = out / "assemble-candidates.jcl"
    # Never leave an old JCL ready after a failed transformation.
    deck.unlink(missing_ok=True)
    mainasm.unlink(missing_ok=True)
    subprocess.run([sys.executable, str(ROOT/"tools/checks/externalize-bcplmem.py"),
                    str(ROOT/"native-compiler/asm/history/bcplmain-wip.asm"), str(mainasm)], check=True)
    memasm = ROOT/"native-compiler/asm/bcplmem.asm"
    for source in (mainasm, memasm):
        subprocess.run([sys.executable,
                        str(ROOT/"tools/checks/check-asm-source.py"),
                        str(source)], check=True)
    main_text = mainasm.read_text(encoding="ascii")
    mem_text = memasm.read_text(encoding="ascii")
    for symbol in ("GETVEC","FREEVEC","MEMDRAIN","MEMBIND","MEMSTAT"):
        if symbol not in main_text or symbol not in mem_text:
            raise ValueError(f"missing boundary symbol {symbol}")
    lines = [
        "//BCOBCAND JOB (MVS),'BCPL CAND',CLASS=A,MSGCLASS=A,",
        "//             MSGLEVEL=(1,1)",
        "//* NONINSTALLING BUILD. TEMP OBJECT DECKS DELETED AT JOB END.",
        *asm("ASMMMAIN", "MAINOBJ", mainasm),
        *asm("ASMMMEM", "MEMOBJ", memasm, "ASMMMAIN"),
        "//VERIFY   EXEC PGM=IEFBR14,COND=((0,NE,ASMMMAIN),",
        "//             (0,NE,ASMMMEM))",
        "//SYSPRINT DD SYSOUT=*",
        "//",
    ]
    if any(len(line) > 71 for line in lines):
        raise ValueError("generated JCL exceeds column 71")
    deck.write_text("\n".join(lines)+"\n", encoding="ascii", newline="\n")
    print(f"Prepared non-installing candidate assembler: {deck}")
    print("Expect ASMMMAIN and ASMMMEM IFOX RC=0000; no PDS write.")
    print("For Gate F1 inspect BCPLMEM ESD for LD MEMSTAT.")
    print("This is NOT installation or cross-object link acceptance.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"runtime-object-candidates: FAIL: {exc}")
