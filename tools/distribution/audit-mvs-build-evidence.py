#!/usr/bin/env python3
"""Read-only TA.0 preflight of operator-supplied MVS build evidence.

Validates captured file hashes, exact inventory listings and the existing strict
reconstruction build-job report contracts. This is NOT release/binary acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
INDEX_LIMIT = 1024 * 1024
TEXT_LIMIT = 32 * 1024 * 1024
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _module(name: str, source: Path):
    spec = importlib.util.spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load trusted local verifier {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # needed for verify.VerifiedPayload dataclass
    spec.loader.exec_module(module)
    return module


chain = _module("ta0_binary_evidence_chain", HERE / "audit-binary-build-chain.py")
verify = _module("ta0_binary_evidence_verify", ROOT / "tools/reconstruction/verify.py")


class EvidenceError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def strict_json(text: str) -> dict[str, Any]:
    def unique_pairs(pairs):
        obj = {}
        for k, value in pairs:
            if k in obj:
                raise EvidenceError(f"duplicate JSON property: {k}")
            obj[k] = value
        return obj
    try:
        result = json.loads(text, object_pairs_hook=unique_pairs,
                            parse_constant=lambda v: (_ for _ in ()).throw(EvidenceError(f"invalid constant {v}")))
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"invalid evidence index JSON: {exc}") from exc
    require(type(result) is dict, "evidence index must be a JSON object")
    return result


def safe_file(directory: Path, info: Any, *, used: set[str]) -> bytes:
    """Read a SHA-256-pinned regular file without following symlinked paths."""
    require(type(info) is dict and set(info) == {"path", "sha256"},
            "file reference must have exact path and sha256 properties")
    name, digest = info["path"], info["sha256"]
    require(type(name) is str and name and "\\" not in name and "\x00" not in name,
            "invalid attachment path")
    require(not name.startswith("/") and all(p not in {".", "..", ""} for p in name.split("/"))
            and str(PurePosixPath(name)) == name, "unsafe attachment path")
    require(name not in used, f"attachment reused: {name}")
    used.add(name)
    require(type(digest) is str and SHA256.fullmatch(digest) is not None,
            f"invalid SHA-256 for {name}")
    base = directory.resolve(strict=True)
    require(directory.is_dir() and not directory.is_symlink(), "evidence directory is not a plain directory")
    path = directory
    for part in name.split("/"):
        path /= part
        require(not path.is_symlink(), f"symbolic link forbidden: {name}")
    require(path.is_file() and path.resolve().is_relative_to(base), f"missing/unsafe attachment {name}")
    require(path.stat().st_size <= TEXT_LIMIT, f"attachment exceeds {TEXT_LIMIT} bytes: {name}")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"attachment digest mismatch: {name}")
    return data


def text_file(directory: Path, info: Any, *, used: set[str]) -> str:
    data = safe_file(directory, info, used=used)
    require(b"\x00" not in data, "NUL bytes in text evidence")
    try:
        return data.decode("utf-8")
    except UnicodeError as exc:
        raise EvidenceError("evidence attachment is not UTF-8 text") from exc


def inspect(index_path: Path, *, expected_source_sha: str, manifest: dict,
            dspal: dict, repo_root: Path, verification_path: Path | None = None) -> dict[str, Any]:
    """Inspect an explicit, separately pinned source revision and saved reports."""
    require(SHA40.fullmatch(expected_source_sha) is not None,
            "--source-sha must be an independently supplied 40-character Git commit SHA")
    require(index_path.is_file() and not index_path.is_symlink() and
            index_path.stat().st_size <= INDEX_LIMIT, "missing/unsafe evidence index")
    index = strict_json(index_path.read_text(encoding="utf-8"))
    require(set(index) == {"schema_version", "source_git_sha", "hlq", "jobs", "inventories"},
            "index must contain schema_version, source_git_sha, hlq, jobs, inventories only")
    require(type(index["schema_version"]) is int and index["schema_version"] == 1,
            "unsupported evidence index schema")
    require(type(index["source_git_sha"]) is str and index["source_git_sha"] == expected_source_sha,
            "source Git SHA claim disagrees with independent --source-sha")
    hlq = index["hlq"]
    require(type(hlq) is str and chain.validation.DSN_PART.fullmatch(hlq) is not None,
            "invalid evidence HLQ")
    chain.validation.check(manifest, dspal, repo_root)
    plan = chain.build_plan(manifest, dspal, repo_root, verification_path=verification_path)
    expected_jobs = set(chain.BUILDER_KEYS)
    jobs = index["jobs"]
    require(type(jobs) is list and len(jobs) == len(expected_jobs),
            "eight unique build jobs are required")
    require(all(type(j) is dict and set(j) == {"name", "payload_job", "launcher_job", "summary", "report"}
                for j in jobs), "invalid build-job record fields")
    names = [j["name"] for j in jobs]
    require(all(type(x) is str for x in names) and set(names) == expected_jobs,
            "missing, duplicated, or unexpected build job")
    used: set[str] = set()
    verified_jobs = []
    for job in jobs:
        name = job["name"]
        payload, launcher = job["payload_job"], job["launcher_job"]
        require(type(payload) is int and type(launcher) is int and
                1 <= payload <= 9999 and 1 <= launcher <= 9999 and payload != launcher,
                f"{name}: invalid launcher/payload JES job identity")
        summary = text_file(index_path.parent, job["summary"], used=used)
        report = text_file(index_path.parent, job["report"], used=used)
        try:
            result = verify.verify_payload(name, payload, launcher, summary, report)
        except verify.VerificationError as exc:
            raise EvidenceError(f"{name}: reconstruction job verification failed: {exc}") from exc
        verified_jobs.append({"name": name, "payload_job": payload, "launcher_job": launcher,
                              "steps_verified": len(result.step_codes),
                              "interpreter_code_zero_records": result.interpreter_codes})
    inventory_rows = index["inventories"]
    require(type(inventory_rows) is list and len(inventory_rows) == len(chain.BINARY_KEYS),
            "exactly four binary inventory listings required")
    require(all(type(x) is dict and set(x) == {"dataset_key", "file"} for x in inventory_rows),
            "invalid binary inventory record")
    keys = [x["dataset_key"] for x in inventory_rows]
    require(all(type(x) is str for x in keys) and set(keys) == set(chain.BINARY_KEYS),
            "missing, duplicate or unexpected binary inventory")
    rows = {x["dspal_key"]: x for x in manifest["datasets"] if x.get("dspal_key")}
    for row in inventory_rows:
        key = row["dataset_key"]
        contents = text_file(index_path.parent, row["file"], used=used)
        dsn = hlq + "." + dspal["datasets"][key]["dsn"]
        # Existing inventory parser's accepted format, without touching MVS.
        try:
            found = verify.inventory_members(contents, dsn)
        except verify.VerificationError as exc:
            raise EvidenceError(f"{key}: invalid retained MVS member listing: {exc}") from exc
        require(found == set(rows[key]["members"]), f"{key}: MVS member listing differs from TA.0 inventory")
    return {
        "status": "OFFLINE REPORT STRUCTURE AND SHA-256 PASS; NOT BINARY/RELEASE ACCEPTANCE",
        "source_sha_claim": index["source_git_sha"],
        "source_sha_matched_cli_claim": True,
        "build_jobs_verified": len(verified_jobs),
        "binary_inventories_verified": len(inventory_rows),
        "binary_members_with_actual_readback_hashes": 0,
        "candidate_specific_rights_approvals": 0,
        "verified_job_receipts": verified_jobs,
        "binary_provenance_plan_members": plan["summary"]["binary_members"],
        "qualifications": [
            "Source SHA was compared to an operator-supplied expected SHA, not independently to MVS inputs.",
            "Saved JES reports were checked against source reconstruction contracts, not executed on MVS here.",
            "Inventory listings prove only names, not DCB, bytes, linkage, or executable integrity.",
            "No target binary readback, rights decision, release candidate, or TA.0 closure is established.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--index", required=True, type=Path, help="operator-provided evidence index.json")
    p.add_argument("--source-sha", required=True, help="independently specified source Git commit SHA")
    p.add_argument("--manifest", type=Path, default=chain.MANIFEST)
    p.add_argument("--dspal", type=Path, default=chain.DSPAL)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        doc, dmap = chain.validation.load(a.manifest), chain.validation.load(a.dspal)
        result = inspect(a.index, expected_source_sha=a.source_sha, manifest=doc,
                         dspal=dmap, repo_root=a.root)
    except (EvidenceError, chain.ChainError, chain.validation.ManifestError, OSError,
            ValueError, UnicodeError, KeyError, TypeError, RuntimeError) as exc:
        print(f"TA.0 BUILD EVIDENCE FAIL: {exc}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("TA.0 RETAINED EVIDENCE CHECK: "
              f"{result['build_jobs_verified']} JES report pairs, "
              f"{result['binary_inventories_verified']} member listings; "
              "ZERO binary readbacks or redistribution approvals established")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
