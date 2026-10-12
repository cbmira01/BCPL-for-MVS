#!/usr/bin/env python3
"""Prepare test-only BCPLMEM reclamation instrumentation for regression 083.

Requires successful canonical regression 083 and its native-test.asm.
Restores the copied runtime from monolithic 083 instrumentation before
externalizing it; never modifies canonical sources or regression 083.
"""
from pathlib import Path
import subprocess
import sys

def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"expected one exact anchor (found {text.count(before)}): {before[:90]!r}")
    return text.replace(before, after, 1)

def check(text):
    for i, line in enumerate(text.splitlines(), 1):
        if len(line) > 71 or "\t" in line or line.rstrip() != line:
            raise ValueError(f"invalid assembler card {i}: {line[:90]!r}")
    return text

def main():
    root = Path(__file__).resolve().parents[2]
    case = root / "workarea/native-regression/083-instrumented-storage-reclamation"
    source = case / "native-test.asm"
    out = case / "bcplmem-object-probe"
    out.mkdir(parents=True, exist_ok=True)
    clean = out / "native-before-bcplmem.asm"
    mainasm = out / "native-external-bcplmem.asm"
    memasm = out / "bcplmem-083-instrumented.asm"
    deck = out / "bcplmem-083-object-probe.jcl"
    # A failed preparation must not leave an old, apparently valid job.
    for file in (deck, clean, mainasm, memasm):
        file.unlink(missing_ok=True)
    from importlib.util import spec_from_file_location, module_from_spec
    instrument = root / "native-compiler/regression/083-instrumented-storage-reclamation/instrument-reclaim.py"
    spec = spec_from_file_location("instrument_reclaim_083", instrument)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    text = source.read_text(encoding="ascii")
    # Undo the test's *known* monolithic annotations in a disposable copy.
    # Strict anchors ensure a changed 083 cannot be silently misinterpreted.
    for old, new in ((module.VEC_NEW,module.VEC),
                     (module.MAIN_NEW,module.MAIN),
                     (module.RETURN_NEW,module.RETURN),
                     (module.DATA_NEW,module.DATA),
                     ("FINRETN  EQU   *","FINRETN  CLOSE (BCPOUT)")):
        text = once(text, old, new)
    clean.write_text(check(text), encoding="ascii", newline="\n")
    subprocess.run([sys.executable,str(root/"tools/checks/externalize-bcplmem.py"),
                    str(clean),str(mainasm)],check=True)
    text = mainasm.read_text(encoding="ascii")
    # Keep BCPOUT open for a final diagnostic emitted at RELDONE,
    # after both MEMDRAIN and BCPLMAIN's own FREEMAIN have returned.
    text = once(text,"FINRETN  CLOSE (BCPOUT)","FINRETN  EQU   *")
    text = once(text,"         EXTRN GETVEC,FREEVEC,MEMDRAIN,MEMBIND",
                "         EXTRN GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMDCNT")
    text = once(text,module.MAIN,module.MAIN_NEW)
    # Count *only* FREEMAIN calls made in MEMDRAIN, not explicit FREEVEC.
    # Fetch externally owned counter by address through the local literal.
    ret = """RELDONE  L     14,RELRET
         BR    14"""
    diag = """RELDONE  MVC   OUTBUF(7),TRTXT83
         L     1,=A(MEMDCNT)
         L     2,0(1)
         LA    2,240(2)
         STC   2,OUTBUF+2
         L     2,TRM083
         LA    2,240(2)
         STC   2,OUTBUF+6
         PUT   BCPOUT,OUTBUF
         CLOSE (BCPOUT)
         L     14,RELRET
         BR    14"""
    text = once(text,ret,diag)
    text = once(text,"RELRET   DC    F'0'",
                "RELRET   DC    F'0'\nTRM083   DC    F'0'\nTRTXT83  DC    CL7'V=0 M=0'")
    mainasm.write_text(check(text),encoding="ascii",newline="\n")
    mem = (root/"asm/bcplmem.asm").read_text(encoding="ascii")
    mem = once(mem,"         ENTRY GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMSTAT",
               "         ENTRY GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMSTAT,MEMDCNT")
    mem = once(mem,"         FREEMAIN R,LV=(4),A=(1)\n         B     MEMLOOP",
               """         FREEMAIN R,LV=(4),A=(1)
         L     9,MEMDCNT
         LA    9,1(9)
         ST    9,MEMDCNT
         B     MEMLOOP""")
    mem = once(mem,"MEMWSAV  DC    F'0'",
               "MEMWSAV  DC    F'0'\nMEMDCNT DC   F'0'")
    memasm.write_text(check(mem),encoding="ascii",newline="\n")
    checker=root/"tools/checks/check-asm-source.py"
    for path in (mainasm,memasm):
        subprocess.run([sys.executable,str(checker),str(path)],check=True)
    subprocess.run([sys.executable,str(root/"native-compiler/regression/make-two-object-job.py"),
                    str(mainasm),str(memasm),str(deck),
                    "--entry","BCRG0083","--job-name","MM083R"],check=True)
    print(f"Prepared: {deck}")
    print("Expected two records: 42 and V=2 M=1")
    print("V counts returned FREEMAINs in MEMDRAIN only.")
    print("M counts BCPLMAIN's returned global/stack FREEMAIN only.")

if __name__=="__main__":
    try:
        main()
    except (OSError,ValueError,subprocess.CalledProcessError) as e:
        raise SystemExit(f"prepare-bcplmem-083-probe: FAIL: {e}")
