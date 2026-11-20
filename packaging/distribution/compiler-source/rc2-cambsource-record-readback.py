#!/usr/bin/env python3
"""TA.2 read-only MVS CAMB_SOURCE record-text verification for rc2.

Compare all fifteen independently retrieved MVS members to the approved Git
sources. Use the established dspal get path (IEBGENER, with unique sentinels)
and retain results under repository workarea. This checks logical FB80 record
contents after dspal's documented trailing-blank removal, NOT raw EBCDIC bytes.
No PDS population, BT0021 staging, or AWS write is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORK = ROOT / "workarea"
POPULATION = WORK / "ta2-rc2-cambsource-population-once"
READBACK = WORK / "ta2-rc2-cambsource-record-readback"
DSPAL = ROOT / "tools/datasets/dspal"
EXPECTED_JOBS = (9325, 9326)  # Accepted owner-reported actual MVS jobs.


class Refusal(ValueError):
    pass


def require(test: bool, message: str) -> None:
    if not test:
        raise Refusal(message)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "missing required preflight")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_existing(path: Path) -> None:
    require(path.is_file() and not path.is_symlink() and
            path.resolve().is_relative_to(WORK.resolve()),
            f"missing or unsafe private evidence: {path}")


def verify_population(population, readiness, manifest: dict) -> tuple[int, int]:
    """Trust retained MVS receipts, without re-running already accepted jobs."""
    require(POPULATION.is_dir() and not POPULATION.is_symlink(),
            "one-time MVS population evidence directory is absent")
    for name in ("populate.stdout.txt", "after-members.txt", "directory-verified.txt"):
        safe_existing(POPULATION / name)
    receipt = (POPULATION / "populate.stdout.txt").read_text(encoding="utf-8")
    jobs = population.check_population_receipt(receipt)
    require(tuple(jobs) == EXPECTED_JOBS,
            "MVS population JOB identity differs from accepted 9325/9326")
    listing = (POPULATION / "after-members.txt").read_text(encoding="utf-8")
    require(readiness.inspect_listing(listing,
            manifest["datasets"][20]["members"]) == "complete",
            "retained MVS source directory is not the selected 15 members")
    return jobs[0], jobs[1]


def normalize_expected(raw: bytes) -> tuple[str, int, int]:
    """Match documented dspal get semantics: strip EBCDIC FB80 pad blanks."""
    require(raw and raw.endswith(b"\n") and b"\r" not in raw,
            "frozen source lacks canonical LF record termination")
    try:
        lines = raw[:-1].decode("ascii").split("\n")
    except UnicodeDecodeError as exc:
        raise Refusal("frozen source is not ASCII") from exc
    require(all(len(line) <= 80 and "\t" not in line and
                all(32 <= ord(char) <= 126 for char in line) for line in lines),
            "frozen source cannot be represented as plain FB80 records")
    trimmed = sum(line != line.rstrip(" ") for line in lines)
    return "\n".join(line.rstrip(" ") for line in lines) + "\n", len(lines), trimmed


def verify_text(expected: str, actual: str) -> None:
    """Full logical record content equality, not hash-only comparison."""
    require(actual == expected, "MVS readback differs from frozen normalized source")


def get_job_id(stderr: str, member: str, dest: Path) -> int:
    # dspal get writes the decoded member to dest and the real MVS JOB ID
    # to stderr. Reject ambiguity rather than inferring success from RC alone.
    expected = (f"get completed as JOB (\\d+): CAMB_SOURCE\\({re.escape(member)}\\) "
                f"-> {re.escape(str(dest))}")
    m = re.fullmatch(expected, stderr.strip())
    require(m is not None, f"dspal get did not confirm MVS JOB for {member}")
    return int(m.group(1))


def mvs_get(member: str, relative: Path):
    try:
        return subprocess.run(
            [str(DSPAL), "get", "CAMB_SOURCE", member, str(relative)],
            cwd=ROOT, text=True, capture_output=True,
            encoding="utf-8", errors="replace", check=False, timeout=360,
            env={**os.environ, "TMPDIR": str(WORK)},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"MVS readback failed or timed out for {member}: {exc}") from exc


def run() -> int:
    require(WORK.is_dir() and not WORK.is_symlink(), "workarea missing or unsafe")
    require(not READBACK.exists() and not READBACK.is_symlink(),
            "readback evidence directory already exists: do not overwrite")
    readiness = load("ta2_source_readiness", HERE / "rc2-cambsource-readiness.py")
    population = load("ta2_source_population", HERE / "rc2-populate-cambsource-once.py")
    manifest, dspal = readiness.source_manifest()
    actions, batches = readiness.verify_sources(manifest, dspal)
    require(len(actions) == 15 and [len(batch) for batch in batches] == [8, 7],
            "frozen historical selection/counts drifted")
    jobs = verify_population(population, readiness, manifest)
    names = manifest["datasets"][20]["members"]
    mapped = dspal["datasets"]["CAMB_SOURCE"]["members"]
    require(set(names) == set(mapped), "source map selection differs")

    # Reserve a new private evidence directory; never overwrite MVS readbacks.
    READBACK.mkdir(mode=0o700)
    report = {
        "candidate_id": "BCPL-0.1.0-rc2", "source_commit": readiness.FROZEN,
        "population_jobs": list(jobs), "evidence_type": "logical-FB80-record-text",
        "raw_ebcdic_byte_fidelity": "not-asserted",
        "status": "incomplete", "members": [],
    }
    evidence = READBACK / "receipt.json"
    evidence.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for name in names:
        raw = readiness.check_frozen_source(mapped[name])
        expected, count, stripped = normalize_expected(raw)
        relative = Path("workarea/ta2-rc2-cambsource-record-readback") / (name + ".txt")
        dest = ROOT / relative
        require(not dest.exists() and not dest.is_symlink(),
                f"readback destination already exists: {name}")
        proc = mvs_get(name, relative)
        (READBACK / (name + ".stderr.txt")).write_text(proc.stderr, encoding="utf-8")
        if proc.stdout:
            (READBACK / (name + ".stdout.txt")).write_text(proc.stdout, encoding="utf-8")
        require(proc.returncode == 0, f"MVS readback failed for {name} (RC={proc.returncode})")
        job_id = get_job_id(proc.stderr, name, relative)
        safe_existing(dest)
        actual = dest.read_text(encoding="utf-8")
        result = {
            "member": name, "job": job_id, "records": count,
            "trailing_blank_source_records": stripped,
            "frozen_sha256": hashlib.sha256(raw).hexdigest(),
            "normalized_sha256": hashlib.sha256(expected.encode("utf-8")).hexdigest(),
            "readback_sha256": hashlib.sha256(actual.encode("utf-8")).hexdigest(),
            "match": actual == expected,
        }
        report["members"].append(result)
        evidence.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        verify_text(expected, actual)
    require(len(report["members"]) == 15, "not all members were read")
    report["status"] = "pass"
    report["total_records"] = sum(x["records"] for x in report["members"])
    evidence.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"TA.2 RC2: 15/15 MVS historical member texts PASS, "
          f"{report['total_records']} normalized records")
    print("MVS readback uses dspal's trailing-blank normalization; "
          "raw EBCDIC byte identity not claimed")
    print(f"Evidence: {READBACK.relative_to(ROOT)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only", action="store_true", required=True)
    parser.parse_args(argv)
    try:
        return run()
    except (Refusal, OSError, ValueError, KeyError, UnicodeError) as exc:
        print("TA.2 RC2 READBACK HALTED: " + str(exc), file=sys.stderr)
        if READBACK.is_dir():
            print(f"Inspect retained readback evidence: {READBACK.relative_to(ROOT)}",
                  file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
