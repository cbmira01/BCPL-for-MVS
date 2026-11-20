#!/usr/bin/env python3
"""TA.2 read-only preflight for historical Cambridge source population.

Verify the rc2 release selection, immutable Git source identity, FB80
representability, and a *saved* MVS directory observation. This tool never
runs MVS, allocates data sets, or populates PDS members. The existing
'dspal populate CAMB_SOURCE --batch' remains the MVS-facing writer.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source-selection.json"
EXPECTED_DSN = "HERC02.BCPL.CAMBRIDG.SOURCE"
FROZEN = "78baec9a8546e4ab09caee779aa2b675379272f3"
MAX_CARDS = 4000  # tools/datasets/dspal-populate.py BATCH_MAX_CARDS
MEMBER = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}\Z")


class Refusal(ValueError):
    pass


def require(test: bool, message: str) -> None:
    if not test:
        raise Refusal(message)


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "missing canonical helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inspect_listing(text: str, members: list[str]) -> str:
    """Recognize only the normalized single-PDS output from dspal ls."""
    lines = text.splitlines()
    require(lines and lines[0] == EXPECTED_DSN + ":",
            "saved MVS listing is not for the approved Cambridge source PDS")
    require(all(line.startswith("    ") and line.strip() for line in lines[1:]),
            "unexpected saved MVS directory output")
    observed = [line.strip() for line in lines[1:]]
    if observed == ["(empty)"]:
        return "empty"
    require(observed and all(MEMBER.fullmatch(x) for x in observed),
            "MVS directory has malformed member names")
    require(len(observed) == len(set(observed)), "MVS directory lists duplicate members")
    require(set(observed) <= set(members), "MVS directory contains unselected members")
    return "complete" if set(observed) == set(members) else "partial"


def saved_listing(path: Path) -> str:
    workarea = ROOT / "workarea"
    require(not path.is_symlink() and path.is_file() and
            path.stat().st_size <= 65536 and
            path.resolve().is_relative_to(workarea.resolve()) and
            workarea.is_dir() and not workarea.is_symlink(),
            "MVS listing must be an existing private workarea report")
    return path.read_text(encoding="ascii")


def source_manifest() -> tuple[dict, dict]:
    contract = import_module("ta2_cambsource_contract",
                             HERE / "successor-contract.py")
    rc1 = contract.read_yaml(contract.RC1)
    rc2 = contract.read_yaml(contract.RC2)
    dspal = contract.read_yaml(contract.DSPAL)
    registry = contract.read_yaml(contract.REGISTRY)
    selection = json.loads(SOURCE.read_text(encoding="utf-8"))
    contract.verify(rc1, rc2, dspal, registry, selection,
                    contract.RC2.read_bytes())
    require(rc2["release"]["source_commit"] == FROZEN,
            "source revision differs from approved Git freeze")
    return rc2, dspal


def check_frozen_source(path: str) -> bytes:
    require(isinstance(path, str) and path.startswith("richards-bcpltape/"),
            "only original historical Git-source paths may be populated")
    relative = Path(path)
    require(not relative.is_absolute() and ".." not in relative.parts,
            "unsafe source path")
    source = ROOT / relative
    require(source.is_file() and not source.is_symlink() and
            source.resolve().is_relative_to(ROOT.resolve()),
            "historical source file missing or outside repository")
    local = source.read_bytes()
    try:
        result = subprocess.run(
            ["git", "show", f"{FROZEN}:{path}"], cwd=ROOT,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"cannot read frozen Git source {path}: {exc}") from exc
    require(result.returncode == 0 and result.stdout == local,
            f"{path}: current source bytes do not match frozen Git revision")
    return local


def batch_plan(rows: list[tuple[str, int]]) -> list[list[str]]:
    """Read-only mirror of dspal-populate's 4000-card batching boundary."""
    batches: list[list[str]] = []
    group: list[str] = []
    count = 0
    for member, records in rows:
        cost = records + 7
        require(cost <= MAX_CARDS, f"{member}: too large for a batch")
        if group and count + cost > MAX_CARDS:
            batches.append(group)
            group = []
            count = 0
        group.append(member)
        count += cost
    if group:
        batches.append(group)
    return batches


def verify_sources(manifest: dict, dspal: dict) -> tuple[list[tuple[str, int]], list[list[str]]]:
    # Use the same canonical dataset map and member order as dspal populate.
    mapped = dspal["datasets"]["CAMB_SOURCE"]
    selected = manifest["datasets"][20]["members"]
    require(len(selected) == 15 and set(mapped["members"]) == set(selected) and
            not mapped.get("generated_members"), "unexpected source PDS contents")
    pack = import_module("ta2_cambsource_fb80", HERE / "pack.py")
    actions = []
    for name, path in mapped["members"].items():
        raw = check_frozen_source(path)
        _, records = pack.encode_fb80(raw, name)
        actions.append((name, records))
    require(len(actions) == 15, "source record inventory incomplete")
    # Check current canonical batching policy, rather than assume it is stable.
    population = (ROOT / "tools/datasets/dspal-populate.py").read_text()
    require("BATCH_MAX_CARDS = 4000" in population and
            "cost = len(action[\"records\"]) + 7" in population,
            "dspal population batching policy has changed")
    return actions, batch_plan(actions)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-members", type=Path, required=True,
                        help="existing dspal ls CAMB_SOURCE report inside workarea")
    args = parser.parse_args(argv)
    try:
        manifest, dspal = source_manifest()
        rows, batches = verify_sources(manifest, dspal)
        state = inspect_listing(saved_listing(args.saved_members),
                                manifest["datasets"][20]["members"])
        print(f"TA.2 RC2 CAMB_SOURCE: {len(rows)} historical files, "
              f"{sum(n for _, n in rows)} FB80 records; "
              f"{len(batches)} prospective IEBGENER batches")
        for i, batch in enumerate(batches, 1):
            print(f"  Batch {i}: {', '.join(batch)}")
        if state == "empty":
            print("MVS DIRECTORY EMPTY: source population required; no changes made")
            return 3
        if state == "partial":
            print("MVS DIRECTORY PARTIAL: refuse automatic population or staging")
            return 2
        print("MVS DIRECTORY NAMES MATCH: record-level readback still required")
        return 0
    except (Refusal, OSError, ValueError, KeyError, UnicodeError) as exc:
        print(f"TA.2 RC2 SOURCE PREFLIGHT REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
