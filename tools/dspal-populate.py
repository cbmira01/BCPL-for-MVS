#!/usr/bin/env python3
"""Manifest-driven population of managed BCPL PDS libraries."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "tools" / "dspal-core.py"
IO_PATH = ROOT / "tools" / "dspal-io.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_module("dspal_core", CORE_PATH)
io = load_module("dspal_io", IO_PATH)
DspalError = core.DspalError


MEMBER_RE = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}")


def selected_datasets(config: dict[str, Any], target: str) -> list[tuple[str, dict[str, Any]]]:
    target = target.upper()
    if target == "ALL":
        return [
            (logical, spec)
            for logical, spec in config["datasets"].items()
            if bool(spec.get("populate", False))
        ]

    spec = config["datasets"].get(target)
    if spec is None:
        raise DspalError(f"unknown managed dataset: {target}")
    if not bool(spec.get("populate", False)):
        raise DspalError(f"managed dataset {target} does not participate in population")
    return [(target, spec)]


def source_path(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise DspalError("population member path must be a non-empty string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise DspalError(f"population path must remain inside the repository: {value}")
    return ROOT / path


def preflight(config: dict[str, Any], target: str):
    selected = selected_datasets(config, target)
    actions: list[dict[str, Any]] = []
    problems: list[str] = []
    unmapped: list[str] = []

    for logical, spec in selected:
        members = spec.get("members")
        if members is None:
            unmapped.append(logical)
            continue
        if not isinstance(members, dict):
            problems.append(f"{logical}: members must be a mapping")
            continue

        seen: set[str] = set()
        lrecl = int(spec.get("lrecl", 0) or 0)
        if str(spec.get("recfm", "")).upper() != "FB" or lrecl <= 0:
            problems.append(f"{logical}: populate currently requires FB with positive LRECL")
            continue

        for raw_member, raw_path in members.items():
            member = str(raw_member).upper()
            if not MEMBER_RE.fullmatch(member):
                problems.append(f"{logical}: invalid member name {raw_member!r}")
                continue
            if member in seen:
                problems.append(f"{logical}: duplicate member mapping for {member}")
                continue
            seen.add(member)

            try:
                path = source_path(raw_path)
            except DspalError as exc:
                problems.append(f"{logical}({member}): {exc}")
                continue
            if not path.is_file():
                problems.append(f"{logical}({member}): source file not found: {path.relative_to(ROOT)}")
                continue

            try:
                text = path.read_text(encoding=str(config["text"].get("host_encoding", "utf-8")))
                records = io.normalize_input_text(config, text, lrecl)
            except (OSError, UnicodeError, DspalError) as exc:
                problems.append(f"{logical}({member}): {exc}")
                continue

            actions.append(
                {
                    "logical": logical,
                    "spec": spec,
                    "dsn": core.full_dsn(config, spec),
                    "member": member,
                    "path": path,
                    "records": records,
                }
            )

    if problems:
        raise DspalError("populate preflight failed:\n  " + "\n  ".join(problems))
    return selected, actions, unmapped


def display_plan(actions: list[dict[str, Any]], unmapped: list[str]) -> None:
    for action in actions:
        rel = action["path"].relative_to(ROOT)
        print(f"{action['logical']:<9} {action['member']:<8} <- {rel}")
    for logical in unmapped:
        print(f"{logical:<9} (no population mappings defined)")


def combined_jcl(config: dict[str, Any], actions: list[dict[str, Any]]) -> str:
    if not actions:
        return "//* DSPAL POPULATE: NO MAPPED MEMBERS SELECTED\n"
    decks: list[str] = []
    for index, action in enumerate(actions, 1):
        decks.append(f"//* ---- DSPAL POPULATE {index}: {action['logical']}({action['member']}) ----\n")
        decks.append(
            io.member_put_deck(
                config,
                action["dsn"],
                action["member"],
                action["records"],
                redact_password=True,
            )
        )
    return "".join(decks)


def cmd_populate(
    config: dict[str, Any], target: str, dry_run: bool, show_jcl: bool
) -> int:
    _, actions, unmapped = preflight(config, target)

    if dry_run:
        display_plan(actions, unmapped)
        print(f"Dry run: {len(actions)} member(s) would be written.")
        return 0

    if show_jcl:
        sys.stdout.write(combined_jcl(config, actions))
        return 0

    if not actions:
        display_plan(actions, unmapped)
        print("No mapped members selected; nothing to populate.")
        return 0

    core.require_reader_ready(config)
    completed: list[tuple[int, dict[str, Any]]] = []
    for action in actions:
        deck = io.member_put_deck(
            config,
            action["dsn"],
            action["member"],
            action["records"],
            redact_password=False,
        )
        job, _ = core.submit_and_wait(config, deck, max_rc=0)
        completed.append((job, action))
        rel = action["path"].relative_to(ROOT)
        print(
            f"JOB {job}: {action['logical']}({action['member']}) <- {rel}"
        )

    for logical in unmapped:
        print(f"{logical}: no population mappings defined; skipped")
    print(f"populate completed: {len(completed)} member(s) written")
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Populate managed BCPL PDS libraries from repository files."
    )
    parser.add_argument("target", help="managed logical dataset name or all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run", action="store_true", help="validate and report actions without submitting jobs"
    )
    mode.add_argument(
        "--show-jcl", action="store_true", help="validate and emit redacted generated JCL without submitting"
    )
    return parser


def main() -> int:
    try:
        args = make_parser().parse_args()
        config = core.load_config()
        return cmd_populate(config, args.target, args.dry_run, args.show_jcl)
    except (DspalError, OSError, ValueError, UnicodeError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
