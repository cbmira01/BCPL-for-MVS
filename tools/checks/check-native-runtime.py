#!/usr/bin/env python3
"""Gate edits to BCPLMAIN before expensive TK5 regression runs."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CHECKS = Path(__file__).resolve().parent

# The existing checker has a hyphenated filename.
_spec = importlib.util.spec_from_file_location("asm_checker", CHECKS / "check-asm-source.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load assembler checker")
_checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_checker)
check_file = _checker.check_file


def load_injector(path: Path):
    spec = importlib.util.spec_from_file_location("blib_stage2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load stage-2 preparer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inject_runtime


def validate(runtime: Path, injector: Path) -> list[str]:
    problems = check_file(runtime)
    if problems:
        return problems
    source = runtime.read_text(encoding="ascii")
    try:
        injected = load_injector(injector)(source)
    except Exception as exc:
        return [f"{injector}: runtime injection failed: {exc}"]
    for lineno, line in enumerate(injected.splitlines(), 1):
        if len(line) > 71:
            problems.append(
                f"injected BCPLMAIN:{lineno}: column 71 exceeded "
                f"(length {len(line)})"
            )
    return problems


def main() -> int:
    runtime = ROOT / "asm/bcplmain-wip.asm"
    injector = (ROOT / "native-compiler/regression/"
                "069-independent-blib-object/prepare-stage2.py")
    try:
        problems = validate(runtime, injector)
    except (OSError, UnicodeError, ImportError) as exc:
        problems = [str(exc)]
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print("check-native-runtime: FAILED", file=sys.stderr)
        return 1
    print("check-native-runtime: OK (source and BLIB injection)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
