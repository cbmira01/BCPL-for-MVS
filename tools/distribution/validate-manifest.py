#!/usr/bin/env python3
"""Read-only TA.0 manifest preflight. No JES, MVS, Git writes, or media I/O."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required on the development host: pip install PyYAML") from exc

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "packaging/distribution/manifest/ta0-inventory.yaml"
DSPAL = ROOT / "config/dspal.yaml"
MEMBER = re.compile(r"^[A-Z@$#][A-Z0-9@$#]{0,7}$")
DSN_PART = re.compile(r"^[A-Z@$#][A-Z0-9@$#]{0,7}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
VOLSER = re.compile(r"^[A-Z0-9@$#]{6}$")
GROUPS = {"common", "mr10", "native", "cambridge"}
PROFILES = {
    "mr10-only": {"common", "mr10"},
    "native-only": {"common", "native"},
    "combined": {"common", "mr10", "native"},
}
FORBIDDEN = {"BOOT_DEVOBJ", "BOOT_INTCODE"}
CAMBRIDGE_KEYS = {"CAMB_SOURCE", "CAMB_ASM", "CAMB_JCL", "CAMB_LIBRARY",
                  "CAMB_BCPLDEMO", "CAMB_LANGDEMO", "CAMB_TESTS",
                  "CAMB_OBJ", "CAMB_LOAD"}
BINARY_KEYS = {"BOOT_OBJ", "EXT_OBJ", "MR10_OBJ", "MR10_LOAD"}
REQUIRED_COUNTS = {
    "DIST_DOCS": 7,
    "MR10_SOURCE": 5, "MR10_ASM": 1, "MR10_JCL": 4,
    "MR10_LIBRARY": 9, "MR10_LANGDEMO": 11,
    "MR10_BCPLDEMO": 21, "MR10_TESTS": 26,
    "MR10_OBJ": 1, "MR10_LOAD": 1,
    "BOOT_OBJ": 10, "BOOT_ASM": 9, "BOOT_SOURCE": 4,
    "BOOT_JCL": 6, "EXT_OBJ": 3, "EXT_ASM": 3,
    "EXT_SOURCE": 3, "EXT_MAC": 3,
}
REQUIRED_OBJECTS = {"BCPLMAIN", "BCPLMEM", "BCPLBYTE", "BCPLAPT",
                    "BCPLIO", "BCPLRGS", "BCPLREG", "BLIB", "BCPLCO", "COROUTIN"}
REQUIRED_EXTENSIONS = {"BCPLDEMO", "BCPLTIME", "BCPLQSAM"}
FORBIDDEN_MEMBERS = {
    "MR10_SOURCE": {"ICLIBC"},
    "MR10_LIBRARY": {"COCAND"},
}


class ManifestError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    """Forbid duplicate YAML keys instead of silently overwriting them."""


def _mapping(loader: StrictLoader, node: yaml.MappingNode) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise ManifestError(f"duplicate YAML mapping key: {key}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ManifestError(why)


def unique_strings(items: Any, where: str) -> list[str]:
    require(isinstance(items, list) and bool(items), f"{where}: expected nonempty list")
    require(all(isinstance(i, str) for i in items), f"{where}: non-string member")
    require(len(set(items)) == len(items), f"{where}: duplicate member")
    require(all(MEMBER.fullmatch(i) for i in items), f"{where}: invalid MVS member")
    return items


def safe_git_source(root: Path, path: Any) -> bool:
    """Reject absolute, parent-traversing and symlink-escaping source paths."""
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        return False
    if any(part in {"..", ""} for part in Path(path).parts):
        return False
    source = root / path
    return source.resolve().is_relative_to(root.resolve()) and source.is_file()


def valid_dsn(s: str) -> bool:
    return isinstance(s, str) and 1 <= len(s) <= 44 and all(
        DSN_PART.fullmatch(p) for p in s.split(".")
    )


def load(path: Path) -> dict[str, Any]:
    try:
        doc = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise ManifestError(f"cannot read YAML {path}: {exc}") from exc
    require(isinstance(doc, dict), f"{path}: expected mapping")
    return doc


def check_dcb(d: Any, kind: str, where: str) -> None:
    require(isinstance(d, dict), f"{where}: missing DCB")
    org = "PS" if kind == "sequential_text" else "PO"
    require(d.get("dsorg") == org, f"{where}: expected DSORG {org}")
    require(d.get("recfm") in ("FB", "U"), f"{where}: invalid RECFM")
    require(all(type(d.get(k)) is int for k in ("lrecl", "blksize")), f"{where}: LRECL/BLKSIZE")
    if d["recfm"] == "FB":
        require(d["lrecl"] == 80 and d["blksize"] == 800, f"{where}: expected FB 80/800")
    else:
        require(kind == "pds_unload" and d["lrecl"] == 0 and d["blksize"] == 6144,
                f"{where}: expected U 0/6144 load library")


def check(manifest: dict[str, Any], dspal: dict[str, Any], root: Path, *, release: bool = False) -> dict[str, Any]:
    require(manifest.get("schema_version") == 1, "schema_version must be 1")
    require(manifest.get("phase") in {"design", "candidate"}, "phase must be design/candidate")
    if release:
        require(manifest["phase"] == "candidate", "cannot freeze a design-only manifest")
    rel, vol = manifest.get("release"), manifest.get("volume")
    require(isinstance(rel, dict) and isinstance(vol, dict), "release/volume sections required")
    native = rel.get("native_compiler")
    require(native in {"absent", "included"}, "native_compiler must be absent/included")
    require(vol.get("format") == "aws" and vol.get("labeling") == "SL", "expected AWS standard-label")
    require(vol.get("volume_ordinal") == 1, "only single-volume release is designed")
    if release:
        require(isinstance(rel.get("version"), str) and bool(rel["version"]), "missing release version")
        require(isinstance(rel.get("candidate_id"), str) and bool(rel["candidate_id"]), "missing candidate ID")
        require(isinstance(rel.get("source_commit"), str) and SHA.fullmatch(rel["source_commit"]), "missing full frozen Git SHA")
        require(isinstance(vol.get("volser"), str) and VOLSER.fullmatch(vol["volser"]), "missing valid six-character VOLSER")
        require(vol.get("registry_reservation") is not None, "missing VOLSER registry reservation")
    profiles = manifest.get("profiles")
    require(isinstance(profiles, dict) and set(profiles) == set(PROFILES), "exactly three installation profiles required")
    for k, groups in PROFILES.items():
        expected = set(groups)
        if native == "included" and k != "mr10-only":
            expected.add("cambridge")
        require(isinstance(profiles[k], list) and len(profiles[k]) == len(set(profiles[k])) and
                set(profiles[k]) == expected, f"invalid {k} dependency closure")
    entries = manifest.get("datasets")
    require(isinstance(entries, list) and len(entries) >= 3, "missing dataset inventory")
    managed = dspal.get("datasets", {})
    require(isinstance(managed, dict), "invalid dspal datasets")
    seen_dsn: set[str] = set()
    seen_key: set[str] = set()
    owner_count: dict[str, int] = {}
    total = 0
    for n, row in enumerate(entries, 1):
        where = f"dataset {n}"
        require(isinstance(row, dict), f"{where}: entry not mapping")
        require(type(row.get("sequence")) is int and row["sequence"] == n and n <= 9999, f"{where}: non-contiguous logical tape sequence")
        require(row.get("group") in GROUPS, f"{where}: invalid group")
        require(isinstance(row.get("owner"), str) and bool(row["owner"]), f"{where}: owner required")
        key = row.get("dspal_key")
        kind = row.get("kind")
        require(kind in {"sequential_text", "pds_unload"}, f"{where}: kind must be sequential_text/pds_unload")
        require(row.get("transfer") == ("sequential_standard_label" if n == 1 else "iebcopy_unload"),
                f"{where}: incorrect transfer/position")
        if n == 1:
            require(kind == "sequential_text" and row.get("generator") == "bootstrap_fb80" and row["group"] == "common",
                    "BT0001 must be read-only EBCDIC FB80 bootstrap")
        elif n == 2:
            require(kind == "pds_unload" and row.get("generator") == "installer_pds" and row["group"] == "common",
                    "BT0002 must be installer PDS unload")
        else:
            require(kind == "pds_unload" and isinstance(key, str) and key in managed,
                    f"{where}: source dspal key missing/unknown")
            require(key not in seen_key, f"{where}: duplicate dspal key {key}")
            seen_key.add(key)
            require(key not in FORBIDDEN, f"{where}: development-only dataset {key}")
            require(not (key.startswith("CAMB_") and native == "absent"), f"{where}: compiler placeholder not permitted")
            suffix = managed[key].get("dsn")
            require(valid_dsn(suffix), f"{where}: invalid dspal DSN")
            target = row.get("target_dsn_template")
            require(target == "{HLQ}." + suffix and len("ABCDEFGH." + suffix) <= 44,
                    f"{where}: target HLQ template mismatch")
            require(target not in seen_dsn, f"{where}: duplicate recipient dataset")
            seen_dsn.add(target)
            group = ("mr10" if key.startswith("MR10_") else
                     "native" if key.startswith(("BOOT_", "EXT_")) else
                     "cambridge" if key.startswith("CAMB_") else "common")
            require(row["group"] == group, f"{where}: wrong group for {key}")
            d = row.get("target_dcb")
            check_dcb(d, kind, where)
            for field in ("dsorg", "recfm", "lrecl", "blksize"):
                require(d[field] == managed[key].get(field), f"{where}: {field} disagrees with dspal")
            members = unique_strings(row.get("members"), where)
            if key in REQUIRED_COUNTS:
                require(len(members) == REQUIRED_COUNTS[key],
                        f"{where}: incorrect TA.0 member count for {key}")
            if key == "BOOT_OBJ":
                require(set(members) == REQUIRED_OBJECTS,
                        "BOOT_OBJ differs from accepted ten-member production contract")
            if key == "EXT_OBJ":
                require(set(members) == REQUIRED_EXTENSIONS,
                        "EXT_OBJ differs from accepted three-member extension contract")
            require(not (set(members) & FORBIDDEN_MEMBERS.get(key, set())), f"{where}: candidate member selected")
            present = managed[key].get("members", {}) or {}
            generated = managed[key].get("generated_members", {}) or {}
            extra_generated = row.get("generated_members", {}) or {}
            require(isinstance(extra_generated, dict) and set(extra_generated) <= set(members),
                    f"{where}: generated_members must only name selected members")
            for member in members:
                if member in present:
                    require(safe_git_source(root, present[member]),
                            f"{where}: missing or unsafe Git-backed source {present[member]}")
                else:
                    require(member in generated or member in extra_generated or
                            (key in BINARY_KEYS and
                             managed[key].get("populate") is False),
                            f"{where}: unmapped member {member}")
                if member in extra_generated:
                    require(isinstance(extra_generated[member], str) and extra_generated[member],
                            f"{where}: missing generated provenance for {member}")
            if managed[key].get("populate") is True:
                require(not (set(members) - set(present) - set(generated) - set(extra_generated)),
                        f"{where}: untracked populated member")
            owners = row.get("member_owners", {}) or {}
            require(isinstance(owners, dict) and set(owners) <= set(members), f"{where}: invalid member owners")
            require(all(isinstance(v, str) and v for v in owners.values()), f"{where}: invalid logical owner")
            for member in members:
                owner = owners.get(member, row["owner"])
                owner_count[owner] = owner_count.get(owner, 0) + 1
            total += len(members)
            if release:
                require(row.get("mvs_inventory_receipt") is not None, f"{where}: no MVS inventory evidence")
                require(row.get("unload_dcb") is not None, f"{where}: unload DCB unknown")
                require(isinstance(row.get("member_provenance"), dict) and
                        set(row["member_provenance"]) == set(members),
                        f"{where}: incomplete per-member rights/build provenance")
                for member in members:
                    prov = row["member_provenance"][member]
                    require(isinstance(prov, dict) and prov.get("redistribution") == "approved" and
                            prov.get("rights_ref") and prov.get("source_ref"),
                            f"{where}({member}): rights/source provenance not accepted")
        if n <= 2:
            check_dcb(row.get("target_dcb"), kind, where)
    require(entries[0].get("sequence") == 1 and entries[1].get("sequence") == 2, "bootstrap sequence mismatch")
    require(set(seen_key) == set(REQUIRED_COUNTS) if native == "absent" else
            set(REQUIRED_COUNTS) <= seen_key,
            "TA.0 selected dataset inventory is missing/extra")
    require(len([x for x in entries if x.get("group") == "mr10"]) == 9, "all nine MR10 PDSes required")
    require(len([x for x in entries if x.get("group") == "native"]) == 8, "all eight native component PDSes required")
    if native == "included":
        require(CAMBRIDGE_KEYS <= seen_key,
                "native compiler included but nine compiler datasets are not selected")
    else:
        require(not any(x["group"] == "cambridge" for x in entries), "no-native compiler must have no compiler payload")
    require(sum(len(x.get("members", [])) for x in entries if x["group"] == "mr10") == 79,
            "MR10 member inventory must contain 79 selected members")
    require(total > 0, "empty selected members")
    return {"phase": manifest["phase"], "native_compiler": native,
            "logical_datasets": len(entries), "selected_members": total,
            "mr10_members": sum(len(x.get("members", [])) for x in entries if x["group"] == "mr10"),
            "owners": owner_count, "last_tape_alias": f"BCPL.BT{len(entries):04d}"}



def provenance_report(manifest: dict[str, Any], dspal: dict[str, Any]) -> dict[str, Any]:
    """Derived TA.0 audit worksheet. Never certifies any right or MVS build."""
    sources: list[dict[str, Any]] = []
    counts = {"git_source": 0, "generated": 0, "resident_binary": 0}
    for row in manifest["datasets"][2:]:
        key = row["dspal_key"]
        mapping = dspal["datasets"][key]
        tracked = mapping.get("members", {}) or {}
        generated = mapping.get("generated_members", {}) or {}
        special = row.get("generated_members", {}) or {}
        owners = row.get("member_owners", {}) or {}
        for member in row["members"]:
            if member in tracked:
                kind, ref = "git_source", tracked[member]
                hint = None
            elif member in generated:
                kind, ref = "generated", generated[member]
                hint = None
            elif member in special:
                kind, ref = "generated", special[member]
                hint = None
            else:
                kind, ref = "resident_binary", None
                if key in {"MR10_OBJ", "MR10_LOAD"}:
                    hint = f"MR10_ASM({member})"
                elif key == "EXT_OBJ":
                    hint = f"EXT_ASM({member})"
                elif key == "BOOT_OBJ":
                    hint = (f"BOOT_SOURCE({member})" if member == "BLIB" else
                            f"BOOT_ASM({member})")
                else:
                    hint = None
            counts[kind] += 1
            sources.append({"tape_sequence": row["sequence"],
                            "dataset_key": key, "member": member,
                            "logical_owner": owners.get(member, row["owner"]),
                            "source_class": kind, "source_reference": ref,
                            "source_hint_not_evidence": hint,
                            "mvs_build_receipt": None,
                            "redistribution_review": "UNREVIEWED"})
    return {"status": "TA.0 DESIGN ONLY; NOT RIGHTS OR MVS ACCEPTANCE",
            "summary": {"members": len(sources), **counts,
                        "rights_unreviewed": len(sources),
                        "mvs_receipts_recorded": 0},
            "members": sources}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=DRAFT)
    p.add_argument("--dspal", type=Path, default=DSPAL)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--release", action="store_true", help="fail closed unless candidate fully validated")
    p.add_argument("--audit-json", action="store_true",
                   help="print derived member provenance gaps; never rights approval")
    args = p.parse_args(argv)
    try:
        manifest, dspal = load(args.manifest), load(args.dspal)
        info = check(manifest, dspal, args.root, release=args.release)
    except ManifestError as exc:
        print(f"TA.0 MANIFEST FAIL: {exc}", file=sys.stderr)
        return 1
    if args.audit_json:
        print(json.dumps(provenance_report(manifest, dspal), indent=2, sort_keys=True))
        return 0
    print(f"TA.0 MANIFEST PASS ({info['phase']} only): {info['logical_datasets']} logical datasets, "
          f"{info['selected_members']} selected PDS members, {info['mr10_members']} MR10; "
          f"last proposed alias {info['last_tape_alias']}; native compiler {info['native_compiler']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
