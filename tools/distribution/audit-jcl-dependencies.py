#!/usr/bin/env python3
"""Read-only TA.0 audit of selected MR10/native release JCL dependencies.

This audits Git JCL source, NOT the site-adapted or executed MVS jobs.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
_VALIDATOR_PATH = Path(__file__).with_name("validate-manifest.py")
_spec = importlib.util.spec_from_file_location("ta0_manifest_validation", _VALIDATOR_PATH)
assert _spec and _spec.loader
_validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validation)

MANIFEST = ROOT / "packaging/distribution/manifest/ta0-inventory.yaml"
DSPAL = ROOT / "config/dspal.yaml"
JCL_KEYS = ("MR10_JCL", "BOOT_JCL")
SYSTEM_PROGRAMS = {"IFOX00", "IEWL", "IEBGENER", "IEBCOMPR"}
SYSTEM_DSN = {"SYS1.MACLIB"}
JCL_DSN = re.compile(r"\b(?:DSN|DSNAME)\s*=\s*([A-Z0-9@$#&.]+)(?:\(([A-Z0-9@$#]+)\))?", re.I)
JCL_PGM = re.compile(r"\bPGM\s*=\s*([A-Z0-9@$#]+)", re.I)
JCL_JOB = re.compile(r"^//[A-Z0-9@$#]{1,8}\s+JOB\b", re.I)


class JCLAuditError(ValueError):
    pass


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def audit(manifest: dict[str, Any], dspal: dict[str, Any], root: Path,
          *, site_hlq: str = "HERC02") -> dict[str, Any]:
    """Trace selected permanent DSN/member references, program and site prerequisites.

    Refuse unknown datasets, unselected members, or cross-profile references.
    Preserve job-card/HLQ deficiencies as *adaptation blockers*, not fake PASSes.
    """
    if not _validation.DSN_PART.fullmatch(site_hlq):
        raise JCLAuditError(f"invalid site HLQ: {site_hlq!r}")
    selected = {}
    for row in manifest["datasets"][2:]:
        suffix = row["target_dsn_template"].removeprefix("{HLQ}.")
        selected[suffix] = (row["dspal_key"], row["group"], set(row["members"]))

    problems: list[str] = []
    jobs: list[dict[str, Any]] = []
    for row in manifest["datasets"]:
        key = row.get("dspal_key")
        if key not in JCL_KEYS:
            continue
        mapping = dspal["datasets"][key].get("members", {})
        for name in row["members"]:
            where = f"{key}({name})"
            source = mapping.get(name)
            if not _validation.safe_git_source(root, source):
                problems.append(f"{where}: missing/unsafe Git JCL source: {source!r}")
                continue
            try:
                lines = (root / source).read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeError) as exc:
                problems.append(f"{where}: cannot read JCL text: {exc}")
                continue
            active = [line for line in lines if line.startswith("//") and not line.startswith("//*")]
            programs = _unique([match.upper() for line in active
                                for match in JCL_PGM.findall(line)])
            has_job = any(JCL_JOB.match(line) for line in active)
            refs: list[dict[str, Any]] = []
            temporary: set[str] = set()
            system: set[str] = set()
            development_hlq: set[str] = set()
            errors: list[str] = []
            for line in active:
                for match in JCL_DSN.finditer(line):
                    dsn, member = match.group(1).upper(), match.group(2)
                    member = member.upper() if member else None
                    if dsn.startswith("&&"):
                        temporary.add(dsn)
                        continue
                    if dsn in SYSTEM_DSN:
                        system.add(dsn)
                        continue
                    if dsn.startswith(site_hlq + "."):
                        if site_hlq == "HERC02":
                            development_hlq.add("HERC02")
                        suffix = dsn[len(site_hlq) + 1:]
                    else:
                        errors.append(f"external permanent DSN {dsn}")
                        continue
                    if suffix not in selected:
                        errors.append(f"unselected permanent DSN {dsn}")
                        continue
                    target_key, target_group, members = selected[suffix]
                    if target_group != row["group"]:
                        errors.append(f"cross-profile reference {dsn} ({target_group})")
                    if member is not None and member not in members:
                        errors.append(f"unselected PDS member {dsn}({member})")
                    refs.append({"dataset_key": target_key,
                                 "member": member, "source_dsn": dsn})
            if not programs:
                errors.append("no EXEC PGM identified")
            for pgm in programs:
                if pgm in SYSTEM_PROGRAMS:
                    continue
                if pgm == "ICINT19" and row["group"] == "mr10":
                    if not any(ref["dataset_key"] == "MR10_LOAD" for ref in refs):
                        errors.append("ICINT19 executed without selected MR10_LOAD reference")
                else:
                    errors.append(f"program dependency not in verified scope: {pgm}")
            adaptations = []
            if not has_job:
                adaptations.append("site JOB card required")
            if development_hlq:
                adaptations.append("replace development HERC02 HLQ")
            problems.extend(f"{where}: {e}" for e in _unique(errors))
            jobs.append({"dataset_key": key, "member": name,
                         "source_path": source, "group": row["group"],
                         "executed_programs": programs,
                         "selected_references": _unique([f"{ref['dataset_key']}({ref['member']})"
                                                         if ref["member"] else ref["dataset_key"]
                                                         for ref in refs]),
                         "temporary_datasets": sorted(temporary),
                         "external_system_datasets": sorted(system),
                         "has_job_card": has_job,
                         "development_hlq_present": bool(development_hlq),
                         "adaptations_required": adaptations,
                         "errors": _unique(errors)})
    if len(jobs) != 10:
        problems.append(f"expected 10 selected release JCL jobs, inspected {len(jobs)}")
    return {"status": "TA.0 GIT SOURCE AUDIT ONLY; NO RECIPIENT ACCEPTANCE",
            "summary": {"jobs": len(jobs),
                        "unresolved_dependencies": len(problems),
                        "jobs_requiring_site_adaptation": sum(bool(x["adaptations_required"])
                                                                for x in jobs),
                        "jobs_referencing_sys1_maclib": sum("SYS1.MACLIB" in x["external_system_datasets"]
                                                               for x in jobs),
                        "mr10_jobs": sum(x["group"] == "mr10" for x in jobs),
                        "native_jobs": sum(x["group"] == "native" for x in jobs)},
            "problems": problems, "jobs": jobs}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--dspal", type=Path, default=DSPAL)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--hlq", default="HERC02",
                        help="HLQ present in inspected JCL; HERC02 design sources require adaptation")
    parser.add_argument("--json", action="store_true", help="print detailed read-only dependency worksheet")
    parser.add_argument("--strict", action="store_true", help="fail on missing JOB cards/HLQ adaptation too")
    args = parser.parse_args(argv)
    try:
        manifest, dspal = _validation.load(args.manifest), _validation.load(args.dspal)
        _validation.check(manifest, dspal, args.root)
        report = audit(manifest, dspal, args.root, site_hlq=args.hlq)
    except (_validation.ManifestError, JCLAuditError) as exc:
        print(f"TA.0 JCL AUDIT FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        s = report["summary"]
        print(f"TA.0 JCL AUDIT: {s['jobs']} selected jobs, "
              f"{s['unresolved_dependencies']} dependency errors, "
              f"{s['jobs_requiring_site_adaptation']} require site adaptation; "
              f"{s['jobs_referencing_sys1_maclib']} depend on SYS1.MACLIB")
        for issue in report["problems"]:
            print(f"  ERROR: {issue}")
    blocked = report["problems"] or (args.strict and report["summary"]["jobs_requiring_site_adaptation"])
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
