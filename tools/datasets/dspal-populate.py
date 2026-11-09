#!/usr/bin/env python3
"""Manifest-driven population of ready managed PDS members.

Absent generated bootstrap members are reported with nonzero status *after*
ready static members have been written. Other preflight errors block writes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "tools" / "datasets" / "dspal-core.py"
IO_PATH = ROOT / "tools" / "datasets" / "dspal-io.py"


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
IODspalError = io.DspalError


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


def validate_generated_sources(paths: list[Path]) -> None:
    """Verify present generated files against prepare-bootstrap's SHA-256 inventory.

    Missing generated files are handled separately by preflight: a clean first
    population is expected to be incomplete. A present generated file without
    trustworthy provenance must never be installed.
    """
    if not paths:
        return
    manifest_path = ROOT / "workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json"
    if not manifest_path.is_file():
        raise DspalError(
            "generated files exist but prepare-bootstrap-manifest.json is absent; "
            "rerun tools/bootstrap/prepare-bootstrap --with-trnilrg"
        )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise DspalError(f"invalid generated bootstrap manifest: {exc}") from exc

    if not isinstance(data, dict) or data.get("format") != 1 \
            or not isinstance(data.get("inputs"), dict) \
            or not isinstance(data.get("outputs"), dict):
        raise DspalError("invalid generated bootstrap manifest structure")

    for name, expected in data["inputs"].items():
        path = source_path(name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise DspalError(f"bootstrap input changed since generation: {name}")

    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        expected = data["outputs"].get(rel)
        if not isinstance(expected, str) or \
                hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise DspalError(
                f"generated bootstrap output is stale or not inventoried: {rel}"
            )


def preflight(config: dict[str, Any], target: str, generated_only: bool = False):
    selected = selected_datasets(config, target)
    actions: list[dict[str, Any]] = []
    problems: list[str] = []
    unmapped: list[str] = []
    missing_generated: list[str] = []
    present_generated: list[Path] = []

    for logical, spec in selected:
        static = spec.get("members", {})
        generated = spec.get("generated_members", {})
        if "members" not in spec and "generated_members" not in spec:
            if not generated_only:
                unmapped.append(logical)
            continue

        if not isinstance(static, dict) or not isinstance(generated, dict):
            problems.append(f"{logical}: members and generated_members must be mappings")
            continue

        seen: set[str] = set()
        lrecl = int(spec.get("lrecl", 0) or 0)
        if str(spec.get("recfm", "")).upper() != "FB" or lrecl <= 0:
            problems.append(f"{logical}: populate currently requires FB with positive LRECL")
            continue

        for group, mappings in (("tracked", static), ("generated", generated)):
            for raw_member, raw_path in mappings.items():
                member = str(raw_member).upper()
                if not MEMBER_RE.fullmatch(member):
                    problems.append(f"{logical}: invalid member name {raw_member!r}")
                    continue
                if member in seen:
                    problems.append(f"{logical}: duplicate member mapping for {member}")
                    continue
                seen.add(member)

                # Filter after name/collision checks, but before any tracked
                # source I/O. Generated provenance still checks its inputs.
                if generated_only and group == "tracked":
                    continue

                try:
                    path = source_path(raw_path)
                except DspalError as exc:
                    problems.append(f"{logical}({member}): {exc}")
                    continue
                if group == "generated" and not (
                    str(raw_path).startswith("workarea/bootstrap-cambridge/")
                ):
                    problems.append(
                        f"{logical}({member}): generated source must be in "
                        "workarea/bootstrap-cambridge/"
                    )
                    continue
                if not path.is_file():
                    rel = path.relative_to(ROOT)
                    if group == "generated":
                        missing_generated.append(f"{logical}({member}) <- {rel}")
                    else:
                        problems.append(f"{logical}({member}): source file not found: {rel}")
                    continue

                try:
                    text = path.read_text(encoding=str(config["text"].get("host_encoding", "utf-8")))
                    records = io.normalize_input_text(config, text, lrecl)
                except (OSError, UnicodeError, DspalError, IODspalError) as exc:
                    rel = path.relative_to(ROOT)
                    problems.append(f"{logical}({member}) <- {rel}: {exc}")
                    continue

                if group == "generated":
                    present_generated.append(path)
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

    # All errors except absent generated files remain atomic preflight failures.
    if problems:
        raise DspalError("populate preflight failed:\n  " + "\n  ".join(problems))
    validate_generated_sources(present_generated)
    return selected, actions, unmapped, missing_generated


def report_missing_generated(missing: list[str], generated_only: bool = False) -> bool:
    if not missing:
        return False
    command = "dspal populate all --generated-only" if generated_only \
        else "dspal populate all"
    print(
        f"dspal: {len(missing)} generated member(s) unavailable; "
        "run prepare-bootstrap --with-trnilrg "
        f"after installing ICINT19, then repeat '{command}':",
        file=sys.stderr,
    )
    for item in missing:
        print(f"  MISSING GENERATED: {item}", file=sys.stderr)
    return True


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


def report_says_missing(report: str, dsn: str) -> bool:
    upper = report.upper()
    name = re.escape(dsn.upper())
    patterns = (
        rf"IKJ58503I\s+DATA\s+SET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"DATA\s+SET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"DATASET\s+['\"]?{name}['\"]?\s+NOT\s+IN\s+CATALOG",
        rf"['\"]?{name}['\"]?\s+NOT\s+FOUND",
    )
    return any(re.search(pattern, upper) for pattern in patterns)


def require_target_datasets(config: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    # The same one-job inventory used by purgebcpl: never one LISTDS job per PDS.
    _, _, inventory = core.managed_inventory(config)
    seen: set[str] = set()
    for action in actions:
        logical = action["logical"]
        if logical in seen:
            continue
        seen.add(logical)
        attrs = inventory[logical]
        if attrs is None:
            raise DspalError(f"populate target {action['dsn']} is missing")
        differences = core.mismatches(action["spec"], attrs)
        if differences:
            raise DspalError(
                f"populate target {action['dsn']} has incompatible attributes: "
                + "; ".join(differences)
            )


# Opt-in batching preserves one-PDS-per-job ownership and bounds JCL input.
BATCH_MAX_STEPS = 60
BATCH_MAX_CARDS = 4000


def population_batches(actions: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    cards = 0
    for action in actions:
        # Six control/comment cards and a data-card delimiter.
        cost = len(action["records"]) + 7
        if cost > BATCH_MAX_CARDS:
            raise DspalError(
                f"{action['logical']}({action['member']}): {cost} cards exceed "
                f"batch limit {BATCH_MAX_CARDS}; use member-by-member population"
            )
        if current and (action["logical"] != current[0]["logical"]
                        or len(current) >= BATCH_MAX_STEPS
                        or cards + cost > BATCH_MAX_CARDS):
            batches.append(current)
            current = []
            cards = 0
        current.append(action)
        cards += cost
    if current:
        batches.append(current)
    return batches


def batched_put_deck(
    config: dict[str, Any], batch: list[dict[str, Any]],
    redact_password: bool = False,
) -> str:
    if not batch or len({action["logical"] for action in batch}) != 1:
        raise DspalError("batched population requires one nonempty PDS group")
    lines = core.authenticated_job_card(
        config, "DSPALPOP", "DSPAL BATCH POPULATE",
        redact_password=redact_password,
    )
    for index, action in enumerate(batch, 1):
        step = f"P{index:04d}"
        dlm = io.choose_dlm(action["records"])
        lines.extend([
            f"//* {step}: {action['logical']}({action['member']})",
            f"//{step:<8} EXEC PGM=IEBGENER,COND=(0,NE)",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            f"//SYSUT2   DD  DSN={action['dsn']}({action['member']}),DISP=SHR",
            f"//SYSUT1   DD  DATA,DLM={dlm}",
        ])
        lines.extend(action["records"])
        lines.append(dlm)
    return "\n".join(lines) + "\n"


def verify_batch_summary(summary: str, expected_count: int) -> None:
    # tools/mvs/job-summary prints one STEP/PROGRAM/RC line per executed step.
    observed = re.findall(r"(?m)^P(\d{4})\s+\S+\s+RC=0000\s*$", summary)
    expected = [f"{number:04d}" for number in range(1, expected_count + 1)]
    if observed != expected or "JOB RESULT: SUCCESS" not in summary:
        raise DspalError(
            f"batch job has {len(observed)} verified steps; expected "
            f"{expected_count} consecutive RC=0000 steps. Inspect JES output"
        )


def cmd_populate(
    config: dict[str, Any], target: str, dry_run: bool, show_jcl: bool,
    generated_only: bool = False, batch: bool = False,
) -> int:
    _, actions, unmapped, missing_generated = preflight(
        config, target, generated_only=generated_only
    )

    if dry_run:
        display_plan(actions, unmapped)
        print(f"Dry run: {len(actions)} ready member(s) would be written.")
        return 2 if report_missing_generated(missing_generated, generated_only) else 0

    if show_jcl:
        if batch and actions:
            for group in population_batches(actions):
                sys.stdout.write(batched_put_deck(config, group, redact_password=True))
        else:
            sys.stdout.write(combined_jcl(config, actions))
        return 2 if report_missing_generated(missing_generated, generated_only) else 0

    if not actions:
        display_plan(actions, unmapped)
        print("No mapped members ready; nothing to populate.")
        return 2 if report_missing_generated(missing_generated, generated_only) else 0

    core.require_reader_ready(config)
    require_target_datasets(config, actions)
    completed = 0
    if batch:
        groups = population_batches(actions)
        for number, group in enumerate(groups, 1):
            start = time.monotonic()
            deck = batched_put_deck(config, group)
            job, summary = core.submit_and_wait(config, deck, max_rc=0)
            verify_batch_summary(summary, len(group))
            elapsed = time.monotonic() - start
            print(f"JOB {job}: batch {number}/{len(groups)} "
                  f"{group[0]['logical']} ({len(group)} members), {elapsed:.1f}s")
            for index, action in enumerate(group, 1):
                rel = action["path"].relative_to(ROOT)
                print(f"  P{index:04d} {action['logical']}({action['member']}) <- {rel}")
            completed += len(group)
    else:
        for action in actions:
            deck = io.member_put_deck(
                config,
                action["dsn"],
                action["member"],
                action["records"],
                redact_password=False,
            )
            job, _ = core.submit_and_wait(config, deck, max_rc=0)
            completed += 1
            rel = action["path"].relative_to(ROOT)
            print(f"JOB {job}: {action['logical']}({action['member']}) <- {rel}")

    for logical in unmapped:
        print(f"{logical}: no population mappings defined; skipped")
    print(f"populate completed: {completed} ready member(s) written")
    return 2 if report_missing_generated(missing_generated, generated_only) else 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Populate managed BCPL PDS libraries from repository files."
    )
    parser.add_argument("target", help="managed logical dataset name or all")
    parser.add_argument(
        "--generated-only", action="store_true",
        help="populate only generated_members mappings; skip tracked member writes",
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="OPT-IN: submit bounded multi-step IEBGENER jobs; requires MVS verification",
    )
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
        return cmd_populate(
            config, args.target, args.dry_run, args.show_jcl,
            generated_only=args.generated_only, batch=args.batch,
        )
    except (DspalError, IODspalError, OSError, ValueError, UnicodeError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
