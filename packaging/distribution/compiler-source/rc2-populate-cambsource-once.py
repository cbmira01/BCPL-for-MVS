#!/usr/bin/env python3
"""Owner-authorized, one-shot MVS population of rc2 historical CAMB_SOURCE.

Never stages BT0021, creates an AWS tape, or modifies earlier staged inputs.
All MVS communication is via the established dspal commands; no automatic
retry after a failed/ambiguous write. Private receipts remain under workarea.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / "workarea"
ATTEMPT = WORK / "ta2-rc2-cambsource-population-once"
DSPAL = ROOT / "tools/datasets/dspal"
MEMBER = "CAMB_SOURCE"
EXPECTED_COUNT = 15
EXPECTED_BATCHES = [(1, 8), (2, 7)]


class Refusal(ValueError):
    pass


def require(value: bool, reason: str) -> None:
    if not value:
        raise Refusal(reason)


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing {name}")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def check_effective_config(canonical: dict, effective: dict) -> None:
    require(effective["mvs"]["hlq"] == "HERC02", "wrong effective MVS HLQ")
    source = canonical["datasets"][MEMBER]
    active = effective["datasets"][MEMBER]
    for field in ("dsn", "type", "dsorg", "recfm", "lrecl", "blksize",
                  "populate", "members", "generated_members"):
        require(active.get(field) == source.get(field),
                f"effective CAMB_SOURCE mapping differs in {field}")
    require(effective["text"]["host_encoding"].lower() == "utf-8" and
            effective["text"]["mvs_encoding"].lower() == "cp037" and
            effective["text"]["conversion_errors"] == "strict",
            "expected strict UTF-8 source and CP037 transfer settings")


def check_population_plan(plan: str, mapped: dict) -> None:
    expected = [f"{MEMBER:<9} {name:<8} <- {path}"
                for name, path in mapped.items()]
    expected.append(f"Dry run: {EXPECTED_COUNT} ready member(s) would be written.")
    require(plan.splitlines() == expected,
            "dspal dry-run does not match the frozen 15-member selection")


def check_population_receipt(report: str) -> list[int]:
    jobs = re.findall(r"(?m)^JOB (\d+): batch (\d+)/(\d+) CAMB_SOURCE "
                      r"\((\d+) members\), [\d.]+s$", report)
    require(len(jobs) == 2 and
            [(int(batch), int(members)) for _, batch, total, members in jobs]
            == EXPECTED_BATCHES and
            all(total == "2" for _, batch, total, members in jobs) and
            len({number for number, _, _, _ in jobs}) == 2 and
            report.rstrip().endswith(
                f"populate completed: {EXPECTED_COUNT} ready member(s) written"),
            "MVS population receipt does not confirm both approved batches")
    return [int(number) for number, _, _, _ in jobs]


def command(args: list[str], *, timeout: int = 900) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              check=False, timeout=timeout,
                              env={**os.environ, "TMPDIR": str(WORK)})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"command failed or timed out (MVS state may be ambiguous): {exc}") from exc


def run() -> int:
    preflight = module("cambsource_readiness", HERE / "rc2-cambsource-readiness.py")
    manifest, canonical = preflight.source_manifest()
    rows, batches = preflight.verify_sources(manifest, canonical)
    require(len(rows) == EXPECTED_COUNT and [len(x) for x in batches] == [8, 7],
            "unexpected Cambridge source member counts/batch boundaries")
    require(WORK.is_dir() and not WORK.is_symlink(), "repository workarea absent/unsafe")
    require(not ATTEMPT.exists() and not ATTEMPT.is_symlink(),
            "one-time population already reserved or attempted; no retry")
    branch = command(["git", "branch", "--show-current"], timeout=15)
    require(branch.returncode == 0 and branch.stdout.strip() == "main",
            "population must run from local main branch")
    core = module("dspal_core_for_cambsource", ROOT / "tools/datasets/dspal-core.py")
    check_effective_config(canonical, core.load_config())
    dry = command([str(DSPAL), "populate", MEMBER, "--dry-run"], timeout=120)
    require(dry.returncode == 0, "dspal population dry-run failed: " + dry.stderr.strip())
    check_population_plan(dry.stdout, canonical["datasets"][MEMBER]["members"])
    listing = command([str(DSPAL), "ls", MEMBER], timeout=240)
    require(listing.returncode == 0,
            "fresh MVS directory inquiry failed: " + listing.stderr.strip())
    require(preflight.inspect_listing(listing.stdout,
            manifest["datasets"][20]["members"]) == "empty",
            "fresh MVS source directory is not empty: do not rewrite")

    # Atomic, persistent attempt reservation BEFORE any MVS writer. Keep it
    # after failure: a partial IEBGENER operation must never be retried blindly.
    ATTEMPT.mkdir(mode=0o700)
    (ATTEMPT / "before-members.txt").write_text(listing.stdout, encoding="utf-8")
    (ATTEMPT / "offline-plan.txt").write_text(dry.stdout, encoding="utf-8")
    (ATTEMPT / "attempt.txt").write_text(
        "TA.2 rc2 historical Cambridge source population, one authorized attempt\n"
        "Target: HERC02.BCPL.CAMBRIDG.SOURCE\n"
        "Frozen source: 78baec9a8546e4ab09caee779aa2b675379272f3\n"
        "15 historical members; 2 bounded IEBGENER batches; no BT0021 staging\n",
        encoding="ascii")
    print("TA.2 RC2: source selected, frozen and MVS directory EMPTY; one-time write reserved", flush=True)
    population = command([str(DSPAL), "populate", MEMBER, "--batch"])
    (ATTEMPT / "populate.stdout.txt").write_text(population.stdout, encoding="utf-8")
    (ATTEMPT / "populate.stderr.txt").write_text(population.stderr, encoding="utf-8")
    require(population.returncode == 0,
            "MVS populate failed; inspect private evidence, do not retry")
    jobs = check_population_receipt(population.stdout)
    print(f"MVS population jobs: {', '.join(str(n) for n in jobs)}; 15 member writes reported", flush=True)
    after = command([str(DSPAL), "ls", MEMBER], timeout=240)
    (ATTEMPT / "after-members.txt").write_text(after.stdout, encoding="utf-8")
    (ATTEMPT / "after.stderr.txt").write_text(after.stderr, encoding="utf-8")
    require(after.returncode == 0 and preflight.inspect_listing(
        after.stdout, manifest["datasets"][20]["members"]) == "complete",
        "MVS source directory is not the exact 15-member selection")
    (ATTEMPT / "directory-verified.txt").write_text(
        "MVS LISTDS MEMBERS returned the exact 15 selected names; "
        "record content and binary fidelity are NOT yet verified.\n",
        encoding="ascii")
    print("MVS directory: 15/15 selected historical names PASS; record fidelity remains pending")
    print(f"Original evidence: {ATTEMPT.relative_to(ROOT)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True,
                        help="perform owner-approved CAMB_SOURCE-only one-time MVS operation")
    parser.parse_args(argv)
    try:
        return run()
    except (Refusal, OSError, ValueError, KeyError, UnicodeError) as exc:
        print(f"TA.2 RC2 POPULATION HALTED: {exc}", file=sys.stderr)
        if ATTEMPT.is_dir():
            print(f"Do not retry automatically. Evidence: {ATTEMPT.relative_to(ROOT)}",
                  file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
