#!/usr/bin/env python3
"""Copy selected BCPLIO milestone evidence from workarea into packaging.

Default: read-only preview. --apply: copy metadata without deleting originals.
Generated JCL, JES output and ordinary per-test logs are never copied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "packaging/bcplio-dynamic-stream-evidence"
WORK = ROOT / "workarea/native-regression"
FILES = {
    "m5.1/m51-class-route.json":
        "114-interleaved-stream-records/m51-class-route.json",
    "m5.1/m51-class-route-result.json":
        "114-interleaved-stream-records/m51-class-route-result.json",
    "m5.1/m51-fb132-dataset-v2.json":
        "124-dynamic-dd-selected-output/m51-fb132-dataset-v2.json",
    "m5.2/m52-padding-negative.json":
        "124-dynamic-dd-selected-output/m52-padding-negative.json",
    "historical/m5.1/m51-fb132-dataset-v1.json":
        "124-dynamic-dd-selected-output/m51-fb132-dataset.json",
    "historical/m5.5/m55-begin-before-fix.json":
        "m55-begin-before-fix.json",
    "m5.5/m55-verification.json": "m55-verification.json",
    "m5.5/m55-begin.json": "m55-begin.json",
    "m5.5/m44-00-145-jobs.tsv": "m44-00-145-jobs.tsv",
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_metadata(src: Path) -> bytes | None:
    if not src.exists():
        return None
    if not src.is_file() or src.is_symlink():
        raise ValueError(f"Not a regular file: {src}")
    if src.stat().st_size > 2_000_000:
        raise ValueError(f"Unexpectedly large metadata: {src}")
    data = src.read_bytes()
    data.decode("utf-8")
    if src.suffix == ".json":
        json.loads(data)
    return data

def main(apply: bool) -> int:
    if not (ROOT / "packaging/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md").is_file():
        raise ValueError("BCPLIO milestone repository not found")
    receipt_data = read_metadata(WORK / "m55-verification.json")
    receipt = json.loads(receipt_data) if receipt_data else None
    if receipt and receipt.get("schema") != "bcpl-m55-fresh-panel-receipt-v1":
        raise ValueError("Unexpected M5.5 verification receipt schema")
    pending: list[tuple[Path, bytes]] = []
    found: list[Path] = []
    for target, source in FILES.items():
        src = WORK / source
        data = read_metadata(src)
        if data is None:
            print("MISSING", src.relative_to(ROOT))
            continue
        if target.endswith("m55-begin.json"):
            checkpoint = json.loads(data)
            if not receipt or checkpoint.get("git_sha") != receipt.get("git_sha"):
                print("SKIP-UNVERIFIED", src.relative_to(ROOT),
                      "(checkpoint Git SHA does not match receipt)")
                continue
        if target.endswith(".tsv"):
            if not receipt or digest(data) != receipt.get("audit_manifest_sha256"):
                print("SKIP-UNVERIFIED", src.relative_to(ROOT),
                      "(TSV hash does not match accepted receipt)")
                continue
        dst = DEST / target
        if dst.is_symlink():
            raise ValueError(f"Destination is symlink: {dst}")
        if dst.exists():
            if not dst.is_file() or dst.read_bytes() != data:
                raise ValueError(f"Destination differs; refusing overwrite: {dst}")
            print("EXISTS", dst.relative_to(ROOT))
        else:
            print("COPY" if apply else "WOULD-COPY",
                  src.relative_to(ROOT), "->", dst.relative_to(ROOT))
            pending.append((dst, data))
        found.append(dst)

    transcript = WORK / "m55-full-panel.log"
    if receipt and transcript.is_file():
        match = digest(transcript.read_bytes()) == receipt.get("runner_transcript_sha256")
        print("M5.5 transcript matches receipt:", "YES" if match else "NO")
        print("Transcript excluded from archive regardless; review separately.")

    if (ROOT / "workarea").exists():
        for path in sorted((ROOT / "workarea").rglob("*")):
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in (
                ".md", ".markdown", ".rst"
            ):
                print("REVIEW-NOTE", path.relative_to(ROOT))

    print("Excluded: generated ASM/JCL, JES/printer output, case logs and binaries.")
    if not apply:
        print("Preview only. --apply copies selected evidence; never deletes originals.")
        return 0

    # Before extending the archive, verify every previously hashed evidence file.
    # Git already versions README.md and other explanatory documentation.
    sums = DEST / "sha256sums.txt"
    if sums.exists():
        if not sums.is_file() or sums.is_symlink():
            raise ValueError("Checksum manifest is not a regular file")
        for line in sums.read_text(encoding="utf-8").splitlines():
            old_sha, sep, rel = line.partition("  ")
            if not sep or len(old_sha) != 64 or any(c not in "0123456789abcdef" for c in old_sha):
                raise ValueError("Invalid previous checksum manifest")
            old_path = Path(rel)
            if old_path.is_absolute() or ".." in old_path.parts:
                raise ValueError("Unsafe entry in previous checksum manifest")
            old_file = DEST / old_path
            # Backward-compatible with the original manifest that also listed
            # README.md. Ordinary documentation is not an evidence hash target.
            if old_path.as_posix() == "README.md":
                continue
            if not old_file.is_file() or old_file.is_symlink() or digest(old_file.read_bytes()) != old_sha:
                raise ValueError(f"Archived file has changed: {old_path}")
    for dst, data in pending:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("xb") as fh:
            fh.write(data)
    if not found:
        print("No matching evidence found; nothing archived.")
        return 0
    entries = sorted(p for p in DEST.rglob("*")
                     if p.is_file() and not p.is_symlink()
                     and p.suffix.lower() in (".json", ".tsv"))
    listing = "".join(f"{digest(p.read_bytes())}  {p.relative_to(DEST)}\n"
                      for p in entries)
    # The preexisting inventory has been verified; extend it to new evidence.
    sums.write_text(listing, encoding="utf-8")
    print("Copied selected metadata into packaging; originals remain in workarea.")
    print("Review all archived files before staging or committing to Git.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="copy selected metadata without removing originals")
    args = parser.parse_args()
    try:
        sys.exit(main(args.apply))
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as err:
        sys.exit(f"archive-bcplio-evidence: {err}")
