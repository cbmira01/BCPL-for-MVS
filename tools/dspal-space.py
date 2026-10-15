#!/usr/bin/env python3
"""Read-only MVS 3.8 IEHLIST PDS space reporting for dspal.

VTOC "empty tracks" reflects end-of-data high-water mark, NOT live-member
allocation. Never infer reusable space after member replacement from it.
"""
from __future__ import annotations
import re

TRKS_PER_CYL = 15  # TK5 3390-class DASD, as shown by the VTOC probe

def probe_deck(core, config, volume: str, dsns: list[str]) -> str:
    lines = core.authenticated_job_card(config, "DSPALSP", "DSPAL SPACE")
    lines += [
        "//* READ-ONLY IEHLIST SPACE/ DIRECTORY REPORT",
        "//SPACE    EXEC PGM=IEHLIST",
        "//SYSPRINT DD SYSOUT=*",
        f"//VOL      DD UNIT=SYSDA,VOL=SER={volume},DISP=SHR",
        "//SYSIN    DD *",
        f" LISTVTOC FORMAT,VOL=SYSDA={volume}",
    ]
    for dsn in dsns:
        lines.append(f" LISTPDS DSN={dsn},VOL=SYSDA={volume},FORMAT")
    return "\n".join(lines + ["/*", ""])

def _vtoс_entry(report: str, dsn: str):
    # Exact name at start of VTOC FORMAT-1 listing, rather than JCL echo.
    start = re.search(r"(?m)^\s*" + re.escape(dsn) +
                      r"\s+1\s+[A-Z0-9]{1,6}\s+1\s+\d{5}", report)
    if not start:
        return None
    after = report[start.end():]
    next_entry = re.search(r"(?m)^\s*---------------DATA SET NAME", after)
    item = after[:next_entry.start()] if next_entry else after
    # A dataset's own extent list may occupy multiple rows and columns.
    extpart = item.split("EXTENTS  NO  LOW(C-H)", 1)
    if len(extpart) < 2:
        return None
    extent_text = extpart[1].split("----", 1)[0]
    extent_lines = extent_text.splitlines()
    total = 0
    number = 0
    for line in extent_lines:
        values = [int(x) for x in re.findall(r"\d+", line)]
        if not values or len(values) % 5:
            continue
        for k in range(0, len(values), 5):
            idx, cl, hl, ch, hh = values[k:k+5]
            if not (0 <= hl < TRKS_PER_CYL and 0 <= hh < TRKS_PER_CYL):
                return None
            n = (ch-cl)*TRKS_PER_CYL + hh-hl+1
            if n <= 0:
                return None
            total += n
            number += 1
    empty = re.search(r"THERE ARE\s+(\d+)\s+EMPTY TRACK\(S\)", item)
    if not number or not empty:
        return None
    free = int(empty.group(1))
    if free > total:
        return None
    return dict(allocated=total, used_hwm=total-free, free_tail=free, extents=number)

def _directory(report: str, dsn: str):
    marker = re.search(r"(?m)^\s*DIRECTORY INFO FOR SPECIFIED PDS ON VOL\s+\S+\s*\n\s*"+
                       re.escape(dsn)+r"\s*$", report)
    if not marker:
        return None
    after = report[marker.end():]
    next_marker = re.search(r"(?m)^\s*DIRECTORY INFO FOR SPECIFIED PDS", after)
    text = after[:next_marker.start()] if next_marker else after
    m = re.search(r"OF THE\s+(\d+)\s+DIRECTORY BLOCKS ALLOCATED TO THIS PDS,\s*"
                  r"(\d+)\s+ARE\(IS\) COMPLETELY UNUSED", text)
    if not m:
        return None
    allocated, free = map(int, m.groups())
    if free > allocated:
        return None
    members = len(re.findall(r"IEH112I MEMBERS OF SPECIFIED PDS NOT CREATED", text))
    return dict(dir_allocated=allocated, dir_used=allocated-free,
                dir_free=free, members=members)

def parse_space(report: str, dsn: str):
    allocation = _vtoс_entry(report, dsn)
    directory = _directory(report, dsn)
    if not allocation and not directory:
        return None
    return {**(allocation or {}), **(directory or {})}

def space_inventory(core, config, inventory):
    groups = {}
    for logical, attrs in inventory.items():
        if attrs and attrs.get("dsorg") == "PO" and attrs.get("volume"):
            volume = attrs["volume"]
            dsn = core.full_dsn(config, config["datasets"][logical])
            groups.setdefault(volume, []).append((logical, dsn))
    results = {}
    for volume, members in groups.items():
        try:
            job, _ = core.submit_and_wait(
                config, probe_deck(core, config, volume, [d for _, d in members]),
                max_rc=0)
            report = core.job_report(job)
            for logical, dsn in members:
                results[logical] = parse_space(report, dsn)
        except (core.DspalError, OSError, ValueError) as exc:
            for logical, _ in members:
                results[logical] = None
    return results

def show_space(fields):
    if fields is None:
        print("    Space: unavailable (IEHLIST query or parsing failed)")
        return
    if "allocated" in fields:
        total, used, free = (fields[k] for k in ("allocated", "used_hwm", "free_tail"))
        print(f"    Tracks: allocated {total}, through HWM {used}, tail free {free}, "
              f"utilization {used/total:.1%}, extents {fields['extents']}")
    else:
        print("    Tracks: unavailable")
    if "dir_allocated" in fields:
        print(f"    Directory blocks: allocated {fields['dir_allocated']}, "
              f"used {fields['dir_used']}, unused {fields['dir_free']}")
    else:
        print("    Directory blocks: unavailable")
