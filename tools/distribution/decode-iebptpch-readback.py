#!/usr/bin/env python3
"""Read-only, fail-closed decoder for a verified TA.0 IEBPTPCH FB80 pilot.

This consumes an *entire* dump-report-for-job report, not a SYSOUT excerpt.
It does not verify source ancestry, member-to-original-byte equality or rights.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from ta0_evidence_paths import guard as guard_evidence_path

MEMBER = re.compile(r"[A-Z@$#][A-Z0-9@$#]{0,7}\Z")
HEX8 = r"[0-9A-F]{8}"
FIRST = re.compile(rf"^(?:{HEX8}  ){{11}}{HEX8}$")
SECOND = re.compile(rf"^((?:{HEX8}  ){{7}}{HEX8})(\*\*|\*)$")
HEADER = re.compile(r"^MEMBER NAME  ([A-Z@$#][A-Z0-9@$#]{0,7})\s*$")
PAGE = re.compile(r"^\s*PAGE\s+[0-9]{4}\s*$")
JES_STEP = re.compile(r"^\s*\S+\s+JOB\s+(\d+)\s+TA0READ\s+TA0HEX\s+IEBPTPCH\s+RC=\s*0000\s*$", re.M)
JOBLOG = re.compile(r"\bJOB\s+(\d+)\s+\$HASP373\s+TA0READ\s+STARTED\b")
MAX_REPORT = 32 * 1024 * 1024
MAX_RECORDS = 100000


class ReadbackError(ValueError):
    """Report malformed, incomplete or inconsistent with its declared run."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadbackError(message)


def decode(text: str, *, member: str, job: int, expected_records: int) -> tuple[bytes, dict]:
    """Strictly decode 12+8 eight-digit groups / record, with * or ** endings.

    `**` denotes a physical block boundary, NOT the end of a PDS member.
    An independent expected record count is required to detect truncation.
    """
    require(MEMBER.fullmatch(member) is not None, "invalid uppercase MVS member")
    require(type(job) is int and 1 <= job <= 9999, "invalid JES job number")
    require(type(expected_records) is int and 1 <= expected_records <= MAX_RECORDS,
            "expected record count must be independently supplied and positive")
    require("END OF DATA FOR SDS OR MEMBER" in text,
            "missing IEBPTPCH end-of-data report")
    require(re.search(r"^\s*PRINT TYPORG=PO,TOTCONV=XE,MAXNAME=1\s*$", text, re.M) is not None,
            "unexpected IEBPTPCH print settings")
    require(re.search(rf"^\s*MEMBER NAME={re.escape(member)}\s*$", text, re.M) is not None,
            "unexpected IEBPTPCH selected member")
    require(job in [int(m) for m in JOBLOG.findall(text)], "incorrect/missing JES START job identity")
    require(job in [int(m) for m in JES_STEP.findall(text)], "JES IEBPTPCH RC=0000 missing")
    require(re.search(r"^IEF142I TA0READ TA0HEX - STEP WAS EXECUTED - COND CODE 0000\s*$", text, re.M) is not None,
            "MVS IEF142I successful completion missing")
    lines = text.replace("\r", "").replace("\f", "\n").splitlines()
    matches = [(i, m.group(1)) for i, line in enumerate(lines)
               if (m := HEADER.fullmatch(line)) is not None]
    require(len(matches) == 1 and matches[0][1] == member,
            "expected exactly one matching SYSUT2 member header")
    i = matches[0][0] + 1
    raw = bytearray()
    boundaries: list[int] = []
    for record_number in range(1, expected_records + 1):
        # The printer may insert a page number between logical records.
        while i < len(lines) and (not lines[i].strip() or PAGE.fullmatch(lines[i])):
            i += 1
        require(i < len(lines) and FIRST.fullmatch(lines[i].rstrip(" ")) is not None,
                f"record {record_number}: missing/malformed first 48-byte print line")
        first = lines[i].rstrip(" ")
        i += 1
        # We intentionally do not silently skip unknown content within a record.
        require(i < len(lines) and SECOND.fullmatch(lines[i].rstrip(" ")) is not None,
                f"record {record_number}: missing/malformed final 32-byte print line/marker")
        second, marker = SECOND.fullmatch(lines[i].rstrip(" ")).groups()
        i += 1
        pieces = first.split("  ") + second.split("  ")
        require(len(pieces) == 20 and all(len(piece) == 8 for piece in pieces),
                f"record {record_number}: invalid number of hexadecimal groups")
        raw.extend(bytes.fromhex("".join(pieces)))
        if marker == "**":
            boundaries.append(record_number)
    require(boundaries and boundaries[-1] == expected_records,
            "expected final physical FB block boundary (**) missing")
    # Reject any extra record or member headings anywhere in the remaining
    # report. An optional Hercules/TK5 printer banner is not binary payload.
    for line in lines[i:]:
        rest = line.rstrip(" ")
        require(FIRST.fullmatch(rest) is None and SECOND.fullmatch(rest) is None,
                "more hexadecimal data exists after expected record count")
        require(HEADER.fullmatch(rest) is None,
                "unexpected second member in print output")
    digest = hashlib.sha256(raw).hexdigest()
    return bytes(raw), {
        "status": "DECODED IEBPTPCH FB80 PRINTER REPORT; NOT INDEPENDENT BINARY/RELEASE ACCEPTANCE",
        "job": job,
        "member": member,
        "record_count": expected_records,
        "record_length": 80,
        "byte_count": len(raw),
        "sha256_of_decoded_print": digest,
        "block_end_records": boundaries,
        "qualifications": [
            "Expected record count remains an operator-provided assertion.",
            "MVS object bytes were decoded from printer text, not independently fetched from DASD.",
            "No Git source revision binding or redistribution determination was established.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--member", required=True)
    parser.add_argument("--job", required=True, type=int)
    parser.add_argument("--expected-records", required=True, type=int)
    parser.add_argument("--expected-sha256",
                        help="optional independent expected digest of decoded bytes; mismatch fails closed")
    parser.add_argument("--output", required=True, type=Path,
                        help="new binary output path under ignored repository workarea/")
    args = parser.parse_args(argv)
    try:
        try:
            guard_evidence_path(args.report.parent, new=False, root=ROOT)
        except ValueError as exc:
            raise ReadbackError("report must be under repository workarea/") from exc
        require(args.report.is_file() and not args.report.is_symlink(),
                "report must be an existing plain file")
        require(args.report.stat().st_size <= MAX_REPORT, "report exceeds size limit")
        data = args.report.read_bytes()
        require(b"\x00" not in data, "NUL bytes in report")
        text = data.decode("utf-8")
        raw, receipt = decode(text, member=args.member, job=args.job,
                              expected_records=args.expected_records)
        receipt['sha256_of_saved_report'] = hashlib.sha256(data).hexdigest()
        if args.expected_sha256 is not None:
            require(re.fullmatch(r'[0-9a-f]{64}', args.expected_sha256) is not None,
                    "expected SHA-256 must be 64 lowercase hex digits")
            require(receipt['sha256_of_decoded_print'] == args.expected_sha256,
                    "decoded bytes do not match the independently expected SHA-256")
            receipt['independent_expected_sha256_matched'] = True
        destination = args.output
        require(destination.is_absolute() and not destination.exists() and
                not destination.is_symlink() and '..' not in destination.parts,
                "output must be an unused absolute file under workarea/")
        try:
            guard_evidence_path(destination.parent, new=False, root=ROOT)
        except ValueError as exc:
            raise ReadbackError("output parent must be inside repository workarea/") from exc
        receipt_path = destination.with_suffix(destination.suffix + ".json")
        require(not receipt_path.exists() and not receipt_path.is_symlink(),
                "receipt exists; cannot overwrite")
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as file:
            file.write(raw)
        fd = os.open(receipt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    except (ReadbackError, OSError, UnicodeError) as exc:
        print(f"TA.0 IEBPTPCH DECODE FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"TA.0 {args.member} JOB {args.job}: {receipt['record_count']} FB80 records, "
          f"{receipt['byte_count']} bytes, decoded SHA-256={receipt['sha256_of_decoded_print']}")
    print("Printer-output decode only; resident member/source lineage not independently verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
