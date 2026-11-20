#!/usr/bin/env python3
"""TA.2 source-family preflight and optional *offline* FB80 deck conversion.

This is a design worksheet consumer, not an alternative release manifest or
an MVS PDS/tape writer. Historical and demoted material are never conflated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
SELECTION = Path(__file__).with_name("source-selection.json")
MEMBER = re.compile(r"[A-Z@#$][A-Z0-9@#$]{0,7}\Z")
EXPECTED_ROLES = {"historical", "derived", "support"}
PREFIX = {
    "historical": "richards-bcpltape/",
    "derived": "workarea/bootstrap-cambridge/demoted/",
    "support": "bootstrap-toolchain/",
}


class InvalidSource(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidSource(message)


def safe_path(root: Path, value: str, role: str) -> Path:
    require(isinstance(value, str) and value.startswith(PREFIX[role]),
            f"{role}: source outside approved family")
    rel = Path(value)
    require(not rel.is_absolute() and ".." not in rel.parts and
            "." not in rel.parts, f"{role}: unsafe source path")
    path = root / rel
    require(path.resolve().is_relative_to(root.resolve()),
            f"{role}: source path escapes repository")
    if path.exists():
        require(not any(part.is_symlink() for part in
                        (path, *list(path.parents)[:len(rel.parts) - 1])),
                f"{role}: symlink in source path")
    return path


def parse_selection(data: dict, root: Path) -> list[tuple[str, str, Path]]:
    require(isinstance(data, dict) and data.get("schema_version") == 1,
            "source selection schema version must be 1")
    cap = data.get("capabilities", {})
    require(cap == {"cambridge_compiler_source": "proposed",
                    "native_cambridge_executable": "absent"},
            "source selection must not assert an installed compiler")
    require("candidate_id" not in data and "volser" not in data and
            "source_commit" not in data, "do not assign release identities here")
    gen = data.get("generation", {})
    require(gen == {
        "generator": "bootstrap-toolchain/bootstrap-cambridge/make-demoted.py",
        "derived_root": "workarea/bootstrap-cambridge/demoted"},
        "unknown or drifting Cambridge source generator")
    groups = data.get("source_sets")
    require(isinstance(groups, list) and len(groups) == 3,
            "exactly three separate source families required")
    roles = set()
    selected = []
    for group in groups:
        require(isinstance(group, dict) and group.get("role") in EXPECTED_ROLES,
                "unknown source family")
        role = group["role"]
        require(role not in roles, "duplicate source family")
        roles.add(role)
        require(isinstance(group.get("provenance"), str) and
                len(group["provenance"]) > 30, "provenance qualification missing")
        members = group.get("members")
        require(isinstance(members, dict) and members,
                f"{role}: missing selected members")
        for member, src in members.items():
            require(isinstance(member, str) and MEMBER.fullmatch(member) is not None,
                    f"{role}: invalid MVS member")
            selected.append((role, member, safe_path(root, src, role)))
    require(roles == EXPECTED_ROLES, "missing source family")
    return selected


def encode_fb80(source: bytes, label: str) -> tuple[bytes, int]:
    """Encode ASCII LF text to exact EBCDIC CP037 fixed 80-byte records.

    This is a potential staging interchange, not a claim that MVS records
    or byte-for-byte historical archive files have been verified on MVS.
    """
    require(source and source.endswith(b"\n"), f"{label}: missing terminal LF")
    require(b"\r" not in source and b"\t" not in source,
            f"{label}: CR or TAB is not an FB80 source record")
    lines = source[:-1].split(b"\n")
    result = bytearray()
    for n, line in enumerate(lines, 1):
        require(len(line) <= 80, f"{label}: line {n} exceeds 80 columns")
        require(all(32 <= c <= 126 for c in line),
                f"{label}: line {n} contains nonprintable or non-ASCII bytes")
        result.extend(line.decode("ascii").encode("cp037").ljust(80, b"\x40"))
    return bytes(result), len(lines)


def evaluate(root: Path, selection: dict, *, include_generated: bool = False):
    entries = parse_selection(selection, root)
    report, decks = [], {}
    for role, member, path in entries:
        if role == "derived" and not include_generated:
            report.append({"role": role, "member": member, "status": "requires-derivation"})
            continue
        require(path.is_file(), f"{role}({member}): source missing")
        raw = path.read_bytes()
        deck, count = encode_fb80(raw, f"{role}({member})")
        report.append({"role": role, "member": member, "status": "record-check-passed",
                       "source": str(path.relative_to(root)),
                       "source_sha256": hashlib.sha256(raw).hexdigest(),
                       "fb80_sha256": hashlib.sha256(deck).hexdigest(),
                       "records": count})
        decks[(role, member)] = deck
    return report, decks


def write_decks(root: Path, destination: Path, report: list, decks: dict) -> None:
    workarea = (root / "workarea").resolve()
    dest = destination.resolve()
    require(dest.is_relative_to(workarea) and dest != workarea,
            "generated evidence must remain under repository workarea")
    require(not destination.exists(), "output directory already exists; no overwrite")
    require(destination.parent.is_dir() and not destination.parent.is_symlink(),
            "output parent must already exist and not be a symlink")
    destination.mkdir(mode=0o700)
    for (role, member), data in sorted(decks.items()):
        (destination / f"{role}-{member}.fb80").write_bytes(data)
    (destination / "source-receipt.json").write_text(
        json.dumps({"status": "offline, not MVS accepted", "members": report},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--include-generated", action="store_true",
                   help="require generated sources from accepted demotion path")
    p.add_argument("--write-decks", type=Path,
                   help="new, nonexisting directory beneath workarea (offline only)")
    args = p.parse_args(argv)
    try:
        require(args.write_decks is None or args.include_generated,
                "--write-decks requires --include-generated")
        selection = json.loads(SELECTION.read_text(encoding="utf-8"))
        report, decks = evaluate(ROOT, selection,
                                 include_generated=args.include_generated)
        if args.write_decks is not None:
            write_decks(ROOT, args.write_decks, report, decks)
        counts = {role: sum(x["role"] == role for x in report)
                  for role in sorted(EXPECTED_ROLES)}
        print(f"TA.2 CAMBRIDGE SOURCE: {counts['historical']} historical, "
              f"{counts['derived']} derived, {counts['support']} support members; "
              f"derived {'checked' if args.include_generated else 'pending'}")
        print("DESIGN-ONLY: no successor identity, MVS staging, rights approval or tape")
        return 0
    except (InvalidSource, OSError, ValueError) as exc:
        print(f"TA.2 CAMBRIDGE SOURCE HALTED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
