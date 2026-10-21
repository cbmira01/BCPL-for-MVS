#!/usr/bin/env python3
"""Decode actual R0TRACE QOUT records from an MVS JES job report."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "workarea/runtime-extensions-r0-trailers"
PATTERN = re.compile(
    r"^R0TR (APP|BLIB)\s+"
    r"(?:(BEGIN)|(OFF=([0-9A-F]{8}) ADDR=([0-9A-F]{8}))|"
    r"(LIMIT=([0-9A-F]{8}))|(END COUNT=([0-9A-F]{8}))|"
    r"(ERROR INVALID TRAILER))\s*$"
)
# Explicit stores in canonical bootstrap BCPLMAIN: source-derived only.
CORE_DIRECT = {
    0, 6, 11, 12, 13, 14, 15, 16, 17, 30, 33, 39, 40, 41,
    42, 46, 47, 52, 53, 54, 55, 76, 85, 86, 87, 88, 150,
}
# G!76 belongs to the historical conditional fallback, not a
# mandatory overwrite; this static set is used only for REVIEW warnings.


def parse_report(report: str) -> dict:
    states = {key: {"started": False, "ended": False, "limit": None,
                    "entries": []} for key in ("APP", "BLIB")}
    order = []
    passed = False
    for raw in report.replace("\f", "").splitlines():
        text = raw.rstrip()
        if text == "R0TR PASS APP AND INSTALLED BLIB":
            if passed:
                raise ValueError("duplicate GO PASS marker")
            passed = True
            order.append(("PASS", ""))
            continue
        if not text.startswith("R0TR "):
            continue
        match = PATTERN.fullmatch(text)
        if not match:
            raise ValueError(f"malformed R0TR QOUT record: {text!r}")
        module = match[1]
        state = states[module]
        if match[2]:
            if state["started"] or module != ("APP" if not order else "BLIB"):
                raise ValueError(f"unexpected BEGIN {module}")
            state["started"] = True
            order.append((module, "BEGIN"))
            continue
        if not state["started"] or state["ended"]:
            raise ValueError(f"out-of-order {module} trailer record")
        if match[4]:
            if state["limit"] is not None:
                raise ValueError("pair after sentinel")
            offset = int(match[4], 16)
            address = int(match[5], 16)
            if offset == 0 or offset > 2796 or offset % 4 or address == 0:
                raise ValueError(f"invalid exported pair {module}: {text}")
            state["entries"].append({"global": offset // 4,
                                     "byte_offset": offset,
                                     "relocated_address_hex": f"{address:08X}"})
        elif match[6]:
            if state["limit"] is not None:
                raise ValueError(f"duplicate {module} sentinel")
            value = int(match[7], 16)
            if value == 0 or value > 2796 or value % 4:
                raise ValueError(f"invalid sentinel {module}: {value}")
            state["limit"] = value
        elif match[8]:
            if state["limit"] is None:
                raise ValueError(f"{module}: missing LIMIT")
            recorded = int(match[9], 16)
            if recorded != len(state["entries"]):
                raise ValueError(f"{module}: count mismatch {recorded}")
            if any(e["byte_offset"] > state["limit"] for e in state["entries"]):
                raise ValueError(f"{module}: export exceeds maximum")
            state["ended"] = True
            order.append((module, "END"))
        else:
            raise ValueError(f"MVS observer diagnosed invalid {module} trailer")

    if order != [("APP", "BEGIN"), ("APP", "END"),
                 ("BLIB", "BEGIN"), ("BLIB", "END"), ("PASS", "")]:
        raise ValueError(f"missing/out-of-order QOUT records: {order!r}")
    if not passed:
        raise ValueError("missing actual GO PASS marker")
    for name, state in states.items():
        slots = [r["global"] for r in state["entries"]]
        duplicates = [n for n, count in Counter(slots).items() if count > 1]
        if duplicates:
            raise ValueError(f"{name}: duplicate actual export slots: {duplicates}")
    if 1 not in [e["global"] for e in states["APP"]["entries"]]:
        raise ValueError("APP does not export START G!1")
    app = {e["global"] for e in states["APP"]["entries"]}
    blib = {e["global"] for e in states["BLIB"]["entries"]}
    return {
        "evidence_class": "actual linked relocated R0TRACE GO/QOUT data",
        "production_registration_test": False,
        "application": {
            "max_global": states["APP"]["limit"] // 4,
            "exports": states["APP"]["entries"]},
        "installed_blib": {
            "max_global": states["BLIB"]["limit"] // 4,
            "exports": states["BLIB"]["entries"]},
        "app_blib_overlaps": sorted(app & blib),
        "app_core_direct_potential_overlaps": sorted(app & CORE_DIRECT),
        "blib_core_direct_potential_overlaps": sorted(blib & CORE_DIRECT),
        "limitations": [
            "core direct slots are source-derived, not instrumented writes",
            "installed BOOT_OBJ(BLIB) was linked; provenance/build SHA "
            "must be independently recorded",
            "conditional G!76 fallback needs end-to-end regression evidence",
            "does not test pre-START collision rejection or installation",
            "does not prove safe handling of arbitrary forged pointers",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    p.add_argument("--output", type=Path, default=WORK / "ledger.json")
    p.add_argument("--job-number", type=int)
    args = p.parse_args()
    ledger = parse_report(args.report.read_text(encoding="utf-8"))
    ledger["report_file"] = str(args.report)
    if args.job_number is not None:
        ledger["jes_job_number"] = args.job_number
    digest_path = WORK / "generated-sha256.txt"
    if digest_path.exists():
        ledger["generated_application_sha256"] = digest_path.read_text("ascii").strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    tsv = args.output.with_suffix(".tsv")
    with tsv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["owner", "G", "byte_offset", "relocated_address_hex"])
        for key, owner in (("application", "APP"), ("installed_blib", "BLIB")):
            for entry in ledger[key]["exports"]:
                writer.writerow([owner, entry["global"], entry["byte_offset"],
                                 entry["relocated_address_hex"]])
    print("R.0 observed export trailers:")
    print("  application: ", len(ledger["application"]["exports"]), "exports")
    print("  installed BLIB:", len(ledger["installed_blib"]["exports"]), "exports")
    print("  app/BLIB overlapping globals:", ledger["app_blib_overlaps"])
    print("  source-derived native overlaps require review")
    print(f"Evidence: {args.output} ; {tsv}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError) as exc:
        raise SystemExit(f"R.0 trailer parse FAILED: {exc}")
