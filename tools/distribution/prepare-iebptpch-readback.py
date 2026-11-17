#!/usr/bin/env python3
"""TA.0: render a single-member, read-only MVS IEBPTPCH FB80 hex print job BODY.

Does not submit JES, access MVS, decode SYSOUT, or prove binary fidelity.
The caller must prepend a site-authorized JOB card before submission.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML is required (host-side only)", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "packaging/distribution/manifest/ta0-inventory.yaml"
DSPAL = ROOT / "config/dspal.yaml"
# RECFM=U load modules have different record and directory semantics.
ALLOWED = frozenset({"MR10_OBJ", "BOOT_OBJ", "EXT_OBJ"})
MVS_MEMBER = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}\Z")
MVS_QUALIFIER = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}\Z")


class PreparationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreparationError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeError) as exc:
        raise PreparationError(f"cannot read {path}: {exc}") from exc
    require(type(doc) is dict, f"{path} must contain a YAML mapping")
    return doc


def make_job_body(manifest: dict[str, Any], dspal: dict[str, Any], *,
                  dataset_key: str, member: str, hlq: str | None = None) -> str:
    """Use only canonical selected members and the development DCB mapping."""
    require(dataset_key in ALLOWED,
            "only the three FB80 object PDSes are permitted; load libraries are excluded")
    require(type(member) is str and MVS_MEMBER.fullmatch(member) is not None,
            "member must be an uppercase, legal MVS PDS member name")
    datasets = manifest.get("datasets")
    require(type(datasets) is list, "manifest datasets must be a list")
    rows = [row for row in datasets if type(row) is dict and row.get("dspal_key") == dataset_key]
    require(len(rows) == 1, f"manifest must select exactly one {dataset_key} dataset")
    row = rows[0]
    members = row.get("members")
    require(type(members) is list and member in members,
            f"{dataset_key}({member}) is not selected by canonical manifest")
    require(row.get("kind") == "pds_unload" and row.get("transfer") == "iebcopy_unload",
            f"{dataset_key}: unsupported manifest transport")
    require(row.get("target_dcb") == {"dsorg": "PO", "recfm": "FB", "lrecl": 80, "blksize": 800},
            f"{dataset_key}: selected DCB differs from FB80/800")

    definitions = dspal.get("datasets")
    require(type(definitions) is dict and type(definitions.get(dataset_key)) is dict,
            f"{dataset_key}: missing dspal dataset mapping")
    source = definitions[dataset_key]
    require(source.get("dsorg") == "PO" and source.get("recfm") == "FB" and
            source.get("lrecl") == 80 and source.get("blksize") == 800 and
            source.get("content_type") == "object",
            f"{dataset_key}: dspal source is not a binary FB80/800 object PDS")

    if hlq is None:
        settings = dspal.get("mvs")
        require(type(settings) is dict, "missing dspal mvs settings")
        hlq = settings.get("hlq")
    require(type(hlq) is str and MVS_QUALIFIER.fullmatch(hlq) is not None,
            "HLQ must be a single valid uppercase MVS qualifier")
    suffix = source.get("dsn")
    require(type(suffix) is str and suffix and all(
        MVS_QUALIFIER.fullmatch(part) is not None for part in suffix.split(".")),
        f"{dataset_key}: invalid dspal dataset suffix")
    dsn = f"{hlq}.{suffix}"
    require(len(dsn) <= 44, "MVS DSN exceeds 44 characters")
    require(len(f"//SYSUT1   DD DSN={dsn},DISP=SHR") <= 71,
            "SYSUT1 JCL exceeds safe fixed-card statement width")
    lines = [
        "//* TA.0 READ-ONLY BINARY FB80 PRINT; NOT BINARY PROOF.",
        "//* PREPEND SITE-AUTHORIZED JOB CARD; DO NOT STAGE TO MVS PDS.",
        "//* RECORD PAYLOAD JOB ID AND PRESERVE ORIGINAL PRINTER BYTES.",
        "//TA0HEX   EXEC PGM=IEBPTPCH",
        "//SYSPRINT DD SYSOUT=*",
        f"//SYSUT1   DD DSN={dsn},DISP=SHR",
        "//SYSUT2   DD SYSOUT=*",
        "//SYSIN    DD *",
        "         PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1",
        f"         MEMBER NAME={member}",
        "/*",
    ]
    require(all(len(line) <= 80 for line in lines), "generated JCL exceeds 80 columns")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-key", required=True,
                        choices=(*sorted(ALLOWED), "MR10_LOAD"),
                        help="source object PDS; MR10_LOAD is intentionally rejected")
    parser.add_argument("--member", required=True, help="selected member name; uppercase")
    parser.add_argument("--hlq", help="override the development HLQ for READ ONLY")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--dspal", type=Path, default=DSPAL)
    args = parser.parse_args(argv)
    try:
        deck = make_job_body(load_yaml(args.manifest), load_yaml(args.dspal),
                             dataset_key=args.dataset_key, member=args.member, hlq=args.hlq)
    except PreparationError as exc:
        print(f"TA.0 IEBPTPCH PREPARE FAIL: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(deck)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
