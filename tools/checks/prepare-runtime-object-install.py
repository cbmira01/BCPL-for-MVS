#!/usr/bin/env python3
"""STAGE ONLY: prepare controlled paired BCPLMAIN/BCPLMEM object installation.

The generated JCL WRITES HERC02.BCPL.OBJ if submitted. This tool NEVER submits.
"""
from pathlib import Path
import hashlib
import importlib.util
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "workarea/runtime-object-candidates"
INSTALL = OUT / "install-runtime-objects.jcl"
MANIFEST = OUT / "install-runtime-objects.manifest.txt"


def main():
    INSTALL.unlink(missing_ok=True)
    MANIFEST.unlink(missing_ok=True)
    # Regenerate from Git-tracked canonical source; never consume stale workarea.
    subprocess.run([sys.executable, str(ROOT / "tools/checks/prepare-runtime-object-candidates.py")],
                   check=True)
    source = OUT / "bcplmain-external-mem.asm"
    original = source.read_text(encoding="ascii")
    anchor = "BCPLMAIN CSECT\n"
    if original.count(anchor) != 1 or "STKOVFL" not in original:
        raise ValueError("missing BCPLMAIN section / stack overflow handler")
    main_src = OUT / "bcplmain-install-export.asm"
    main_src.write_text(original.replace(anchor, anchor + "         ENTRY STKOVFL\n", 1),
                        encoding="ascii", newline="\n")
    mem_src = ROOT / "asm/bcplmem.asm"
    for src in (main_src, mem_src):
        subprocess.run([sys.executable, str(ROOT / "tools/checks/check-asm-source.py"),
                        str(src)], check=True)
    path = ROOT / "tools/checks/prepare-runtime-object-candidates.py"
    spec = importlib.util.spec_from_file_location("runtime_candidates", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cards = [
        "//BCOIPAIR JOB (MVS),'BCPL PAIR',CLASS=A,MSGCLASS=A,",
        "//             MSGLEVEL=(1,1)",
        "//* WARNING: SUBMISSION REPLACES TWO PRODUCTION OBJECT MEMBERS.",
        "//* SOURCE: EXTERNALIZED BCPLMAIN + EXPORTED STKOVFL; BCPLMEM.",
        *module.asm("ASMMMAIN", "MAINOBJ", main_src),
        *module.asm("ASMMMEM", "MEMOBJ", mem_src, "ASMMMAIN"),
        "//* FIRST WRITE: ONLY IF BOTH ASSEMBLIES COMPLETED AT RC 0.",
        "//PUTMAIN  EXEC PGM=IEBGENER,",
        "//             COND=((0,NE,ASMMMAIN),(0,NE,ASMMMEM))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSIN    DD DUMMY",
        "//SYSUT1   DD DSN=&&MAINOBJ,DISP=(OLD,DELETE)",
        "//SYSUT2   DD DSN=HERC02.BCPL.OBJ(BCPLMAIN),DISP=SHR",
        "//* SECOND WRITE: ONLY IF FIRST WRITE COMPLETED AT RC 0.",
        "//PUTMEM   EXEC PGM=IEBGENER,",
        "//             COND=((0,NE,ASMMMAIN),(0,NE,ASMMMEM),",
        "//             (0,NE,PUTMAIN))",
        "//SYSPRINT DD SYSOUT=*",
        "//SYSIN    DD DUMMY",
        "//SYSUT1   DD DSN=&&MEMOBJ,DISP=(OLD,DELETE)",
        "//SYSUT2   DD DSN=HERC02.BCPL.OBJ(BCPLMEM),DISP=SHR",
        "//",
    ]
    if any(len(card) > 71 or not card.isascii() for card in cards):
        raise ValueError("non-card-safe JCL")
    # Working tree state is evidence, not necessarily clean; do not invent provenance.
    gitrev = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                      text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT,
                                      text=True).strip()
    tracked = [ROOT / "asm/bcplmain-wip.asm", mem_src,
               ROOT / "tools/checks/externalize-bcplmem.py",
               ROOT / "tools/checks/prepare-runtime-object-candidates.py"]
    hashed = tracked + [main_src]
    data = [f"git HEAD: {gitrev}",
            f"working-tree status: {status if status else 'clean'}",
            "MVS target: HERC02.BCPL.OBJ(BCPLMAIN)/(BCPLMEM)",
            "accepted executable model: JOB 9342 (RC=0; output 42)",
            "incumbent object provenance: NOT ESTABLISHED",
            "recovery: rebuild/redeploy both from known-good Git revision; no exact rollback guarantee",
            "required manual pre-submit check: tools/dspal stat OBJ ; tools/dspal ls OBJ",
            "required manual pre-submit review: inspect JCL, source hashes and operator approval",
            "The generated JCL is NOT atomic and does not itself verify ESD after writing.",
            ""]
    data.extend(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}"
                for p in hashed)
    MANIFEST.write_text("\n".join(data)+"\n", encoding="utf-8")
    INSTALL.write_text("\n".join(cards)+"\n", encoding="ascii", newline="\n")
    print(f"STAGED (NOT SUBMITTED): {INSTALL}")
    print(f"Manifest: {MANIFEST}")
    print("DANGER: Submitting JCL replaces both production members.")
    print("Gate B / operator decision must precede submission.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"runtime-pair-install: {exc}")
