#!/usr/bin/env python3
"""M1.6: fail closed unless canonical BCPLMAIN matches the proven staging recipe."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "asm/bcplmain.asm"

def main() -> None:
    with tempfile.TemporaryDirectory(prefix="bcplmain-m16-") as temp:
        staged = Path(temp) / "bcplmain-pds.asm"
        subprocess.run(
            [sys.executable, str(ROOT / "tools/checks/externalize-bcplmem.py"),
             str(ROOT / "asm/bcplmain-wip.asm"), str(staged)],
            check=True)
        text = staged.read_text(encoding="ascii")
        marker = "GIDONE   L     4,4(12)"
        needle = "BCPLMAIN CSECT\n"
        if text.count(marker) != 1 or text.count(needle) != 1:
            raise ValueError("unexpected staging anchors")
        import importlib.util
        path = ROOT / "native-compiler/regression/069-independent-blib-object/prepare-stage2.py"
        spec = importlib.util.spec_from_file_location("stage2_m16", path)
        if spec is None or spec.loader is None:
            raise ValueError("cannot import proven BLIB injection")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        text = module.inject_runtime(text).replace(
            needle, needle + "         ENTRY STKOVFL\n", 1)
        actual = CANONICAL.read_text(encoding="ascii")
        if actual != text:
            import difflib
            diff = "".join(difflib.unified_diff(
                text.splitlines(keepends=True), actual.splitlines(keepends=True),
                fromfile="legacy staged", tofile="canonical"))
            raise ValueError("canonical BCPLMAIN differs from staging recipe:\n" + diff[:4000])
        subprocess.run([sys.executable, str(ROOT / "tools/checks/check-asm-source.py"),
                        str(CANONICAL)], check=True)
    print("M1.6 canonical BCPLMAIN: exact staging equivalence PASS")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"M1.6 canonical check FAIL: {exc}")
