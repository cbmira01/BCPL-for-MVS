#!/usr/bin/env python3
"""Stage Gate B reproducible resident MVS source, without any MVS writes."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "workarea/runtime-object-candidates"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    main = OUT / "bcplmain-pds.asm"
    main.unlink(missing_ok=True)
    subprocess.run([sys.executable, str(ROOT / "tools/checks/externalize-bcplmem.py"),
                    str(ROOT / "native-compiler/asm/history/bcplmain-wip.asm"), str(main)], check=True)
    src = main.read_text(encoding="ascii")
    needle = "BCPLMAIN CSECT\n"
    if src.count(needle) != 1 or "STKOVFL" not in src:
        raise RuntimeError("unexpected BCPLMAIN source")
    # Promote the previously proven 069 stage-2 BLIB trailer registration
    # into the *installed runtime source*, not monolithic regression WIP.
    # The WIP remains untouched because many source-mode link jobs do not
    # INCLUDE BLIB and cannot resolve an unconditional EXTRN BLIB.
    marker = "GIDONE   L     4,4(12)"
    if src.count(marker) != 1:
        raise RuntimeError("unexpected global trailer insertion point")
    from importlib.util import spec_from_file_location, module_from_spec
    injector_path = (ROOT / "native-compiler/regression/"
                     "069-independent-blib-object/prepare-stage2.py")
    spec = spec_from_file_location("blib_stage2", injector_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    src = module.inject_runtime(src)
    src = src.replace(needle, needle + "         ENTRY STKOVFL\n", 1)
    if src.count("EXTRN BLIB") != 1:
        raise RuntimeError("BLIB registration is missing")
    main.write_text(src, encoding="ascii", newline="\n")
    files = [main, ROOT / "native-compiler/asm/bcplmem.asm",
             ROOT / "jcl/build-bcplmain-objects.jcl"]
    for path in files[:2]:
        subprocess.run([sys.executable, str(ROOT / "tools/checks/check-asm-source.py"),
                        str(path)], check=True)
    for path in files:
        for line in path.read_text(encoding="ascii").splitlines():
            if len(line) > 80:
                raise RuntimeError(f"overlong PDS record in {path}")
    commit = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT,
                                     text=True).strip()
    manifest = OUT / "bldbmain-gate-b.manifest"
    manifest.write_text(
        "Git HEAD: " + commit + "\n"
        + "Gate B: text PDS staging ONLY; no OBJ PDS installation\n"
        + "".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n"
                  for f in files), encoding="ascii")
    print("Staged:", *files, sep="\n  ")
    print("Manifest:", manifest)
    print("Next: explicit dspal rm batch, compress once per PDS, then put all.")


if __name__ == "__main__":
    main()
