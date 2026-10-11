#!/usr/bin/env python3
"""Prepare a standalone BCPLMEM linkage job from a successful normal test.

Run tools/run-native-regression N first. The script reads its generated
workarea/native-test.asm and produces a separate, noncanonical assembly.
This proof deliberately excludes regression 083's inline RELMEM instrumentation.
"""
import argparse
from pathlib import Path
import subprocess

CASES = {
    27: "27-getvec",
    28: "28-freevec",
    29: "29-multiple-allocations",
    30: "30-getvec-failure",
    31: "31-dynamic-vector-across-calls",
    32: "32-dynamic-pointer-return",
    39: "39-freevec-storage-release",
    82: "082-outstanding-vectors-at-termination",
    88: "088-stop-outstanding-vectors",
}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("test",type=int,choices=sorted(CASES))
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[2]
    work=root/"workarea/native-regression"/CASES[args.test]
    source=work/"native-test.asm"
    if not source.is_file():
        raise ValueError(f"run normal regression {args.test} first: {source}")
    out=work/"bcplmem-object-probe"
    out.mkdir(parents=True,exist_ok=True)
    modified=out/"native-external-bcplmem.asm"
    deck=out/"bcplmem-object-probe.jcl"
    subprocess.run(["python3",str(root/"tools/checks/externalize-bcplmem.py"),
                    str(source),str(modified)],check=True)
    checker=root/"tools/checks/check-asm-source.py"
    memsrc=root/"tools/checks/bcplmem-linkage-probe.asm"
    for path in (modified,memsrc):
        subprocess.run(["python3",str(checker),str(path)],check=True)
    subprocess.run(["python3",
                    str(root/"native-compiler/regression/make-two-object-job.py"),
                    str(modified),str(memsrc),str(deck),
                    "--entry",f"BCRG{args.test:04d}",
                    "--job-name",f"MM{args.test:03d}R"],check=True)
    print(f"Prepared: {deck}")
    print("Separate BCPLMEM object exports GETVEC/FREEVEC/MEMDRAIN.")
    print("BCPLMAIN owns final DYNBASE/DYNLEN free, calls MEMDRAIN.")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        raise SystemExit(f"bcplmem-object-probe: FAIL: {exc}")
