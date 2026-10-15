#!/usr/bin/env python3
"""Finish tool-subdirectory refactoring in a local Git checkout.

Default dry run; --apply updates tracked callers and removes old tool files.
No MVS dataset allocation, compiler builds, or JES submission.
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = {
    "native": {
        "build-blib-object": "build-blib",
        "build-cambridge-mvs": "build-cambridge",
        "cambridge-compile": "compile-bootstrap",
        "cambridge-compile-mvs": "compile-mvs",
        "capture-writef-cg370": "capture-writef-cg370",
        "prepare-bootstrap": "prepare-bootstrap",
        "run-native-regression": "run-regression",
    },
    "mr10": {
        "compile-and-run": "compile-and-run",
        "compile-and-run-core.py": "compile-and-run-core.py",
        "current-icint": "current-icint",
        "run-intcode": "run-intcode",
        "run-mr10kit-demo-suite": "run-demo-suite",
        "run-mr10kit-language-demos": "run-language-demos",
        "run-mr10kit-regression-panel": "run-regression-panel",
    },
    "mvs": {
        "start-tk5": "start-tk5",
        "shutdown-tk5": "shutdown-tk5",
        "submit-jcl": "submit-jcl",
        "job-summary": "job-summary",
        "dump-report-for-job": "dump-report-for-job",
        "make-asm-job": "make-asm-job",
        "make-asm-job.py": "make-asm-job.py",
    },
    "datasets": {
        "dspal": "dspal",
        **{f"dspal-{p}.py": f"dspal-{p}.py" for p in
           ("core", "init", "io", "ls", "maint", "populate",
            "purge", "read", "space", "submit")},
    },
}
DEST = {old: f"tools/{section}/{name}"
        for section, entries in DIRECTORIES.items()
        for old, name in entries.items()}
SUFFIXES = {".py", ".sh", ".md", ".rst", ".txt", ".yaml",
            ".yml", ".jcl", ".json", ".toml", ".cfg", ".ini"}
EXCLUDED = {"workarea", "mvs-state", "richards-bcpltape"}
SELF = "packaging/finish-tools-refactor.py"


def git(*args):
    p = subprocess.run(["git", "-C", str(ROOT), *args],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip())
    return p.stdout


def transform(text):
    for old, new in sorted(DEST.items(), key=lambda v: -len(v[0])):
        section, basename = new.split("/")[1:]
        text = text.replace(
            f'/ "tools" / "{old}"',
            f'/ "tools" / "{section}" / "{basename}"',
        )
        text = text.replace(
            f"/ 'tools' / '{old}'",
            f"/ 'tools' / '{section}' / '{basename}'",
        )
    for old, new in sorted(DEST.items(), key=lambda v: -len(v[0])):
        text = re.sub(
            rf"(?<![A-Za-z0-9_./-])tools/{re.escape(old)}(?![A-Za-z0-9_.-])",
            lambda m, value=new: value, text,
        )
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    opts = ap.parse_args()
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise RuntimeError("tracked working tree must be clean")
    missing = [p for p in DEST.values() if not (ROOT / p).is_file()]
    if missing:
        raise RuntimeError("missing canonical files: " + ", ".join(missing))
    lost_exec = [p for old, p in DEST.items()
                 if (ROOT / "tools" / old).is_file()
                 and os.access(ROOT / "tools" / old, os.X_OK)
                 and not os.access(ROOT / p, os.X_OK)]
    if lost_exec:
        raise RuntimeError("nonexecutable relocated files: " + ", ".join(lost_exec))
    tracked = [p for p in git("ls-files", "-z").split("\0") if p]
    old_paths = {"tools/" + old for old in DEST}
    edits = []
    for rel in tracked:
        if rel in old_paths or rel == SELF:
            continue
        if rel.split("/")[0] in EXCLUDED or Path(rel).suffix not in SUFFIXES:
            continue
        file = ROOT / rel
        if not file.is_file():
            continue
        try:
            original = file.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        updated = transform(original)
        if updated != original:
            edits.append((file, updated))
    print(f"Old tool files to remove: {len(old_paths)}")
    print(f"References to update in tracked files: {len(edits)}")
    for file, _ in edits:
        print("  ", file.relative_to(ROOT))
    if not opts.apply:
        print("Dry run. Use --apply to make changes.")
        return 0
    for file, updated in edits:
        file.write_text(updated, encoding="utf-8", newline="")
    git("rm", "--", *sorted(old_paths))
    cache = ROOT / "tools" / "__pycache__"
    if cache.is_dir():
        shutil.rmtree(cache)
    leftovers = [f.name for f in (ROOT / "tools").iterdir()
                 if f.is_file() and f.name != "README.md"]
    if leftovers:
        raise RuntimeError("root tool files remain: " + ", ".join(leftovers))
    for py in (ROOT / "tools").rglob("*.py"):
        compile(py.read_bytes(), str(py), "exec")
    git("diff", "--check")
    print("Applied. Review git diff and run subsystem smoke tests.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, SyntaxError) as exc:
        print(f"finish-tools-refactor: {exc}", file=sys.stderr)
        sys.exit(2)
