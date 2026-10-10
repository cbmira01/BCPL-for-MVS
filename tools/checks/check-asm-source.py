#!/usr/bin/env python3
"""Pre-flight IBM assembler source for repository hygiene rules.

Checks:
- ASCII-only text;
- no tab characters;
- no trailing spaces or tabs;
- no source text beyond column 71;
- no defined IFOX/Assembler F symbol longer than eight characters.

Exit status is zero when all inputs pass and nonzero when any violation is
found.  Diagnostics are stable and intended for both humans and automation.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys


MAX_SOURCE_COLUMN = 71
MAX_SYMBOL_LENGTH = 8
SYMBOL = re.compile(r"^[A-Za-z@$#_][A-Za-z0-9@$#_]*$")


def check_symbol_definitions(path: Path, text: str) -> list[str]:
    """Check the Assembler F name field; not operands or continuation cards."""
    issues: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line or line[0].isspace() or line.startswith(("*", ".*")):
            continue
        label = line.split(None, 1)[0]
        if label.startswith("//"):
            continue
        if len(label) > MAX_SYMBOL_LENGTH and SYMBOL.fullmatch(label):
            issues.append(
                f"{path}:{lineno}: IFOX symbol '{label}' exceeds "
                f"{MAX_SYMBOL_LENGTH} characters (length {len(label)})"
            )
    return issues


def iter_files(paths: list[Path]):
    for path in paths:
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*.asm") if p.is_file())
        else:
            yield path


def check_file(path: Path) -> list[str]:
    problems: list[str] = []

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [f"{path}: cannot read: {exc}"]

    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        problems.append(
            f"{path}:{exc.start + 1}: non-ASCII byte 0x{raw[exc.start]:02X}"
        )
        text = raw.decode("ascii", errors="replace")

    for lineno, line in enumerate(text.splitlines(), 1):
        if "\t" in line:
            columns = [str(i + 1) for i, ch in enumerate(line) if ch == "\t"]
            problems.append(
                f"{path}:{lineno}: tab character at column(s) {','.join(columns)}"
            )

        if line.endswith((" ", "\t")):
            problems.append(f"{path}:{lineno}: trailing whitespace")

        if len(line) > MAX_SOURCE_COLUMN:
            tail = line[MAX_SOURCE_COLUMN:]
            problems.append(
                f"{path}:{lineno}: text extends past column "
                f"{MAX_SOURCE_COLUMN} (length {len(line)}; tail={tail!r})"
            )

    problems.extend(check_symbol_definitions(path, text))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check assembler source for BCPL-for-MVS pre-flight rules."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="assembler file(s) or directories; directories recurse over *.asm",
    )
    args = parser.parse_args()

    files = list(iter_files(args.paths))
    if not files:
        print("check-asm-source: no input files", file=sys.stderr)
        return 2

    problems: list[str] = []
    for path in files:
        if not path.exists():
            problems.append(f"{path}: does not exist")
            continue
        problems.extend(check_file(path))

    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(
            f"check-asm-source: FAILED ({len(problems)} violation(s))",
            file=sys.stderr,
        )
        return 1

    print(f"check-asm-source: OK ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
