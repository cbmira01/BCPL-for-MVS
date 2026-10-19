#!/usr/bin/env python3
"""M5.1 class-separated JES printer ROUTE probe; never submits a job.

Commands:
  inspect             Read live TK5 device lines and host printer status.
  prepare             Clone the *DEVOBJ candidate* regression 114 GO deck,
                      capture pre-submission printer offsets and provenance.
  verify JOB_NUMBER   Check the submitted job's A/Z printer sections and
                      preserve evidence; DOES NOT verify raw FB132 bytes.

Submission, after inspect/prepare, is an explicit operator action via
tools/mvs/submit-jcl. No MVS/PDS state is modified by this tool.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import runpy
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "workarea/native-regression/114-interleaved-stream-records"
SOURCE = WORK / "runtime-pds-go.jcl"
DECK = WORK / "m51-class-route.jcl"
STATE = WORK / "m51-class-route.json"
EVIDENCE = WORK / "m51-class-route-result.json"
A = ROOT / "mvs-state/prt/prt00e.txt"
Z = ROOT / "mvs-state/prt/prt00f.txt"
EXPECTED_A = ROOT / "bootstrap-toolchain/regression/114-interleaved-stream-records/expected.txt"
EXPECTED_Z = ROOT / "bootstrap-toolchain/regression/114-interleaved-stream-records/expected-alt.txt"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def printer_state(path: Path) -> dict:
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"not a regular printer file: {path}")
    return {"path": str(path.relative_to(ROOT)), "offset": info.st_size,
            "dev": info.st_dev, "ino": info.st_ino}


def check_source(text: str) -> None:
    checks = {
        "regression 114 GO job": bool(re.search(
            r"^//RG114R\s+JOB\b", text, re.M)),
        "DEVOBJ PDS candidate": (
            "RUNTIME LIBRARY: DEVOBJ; APP ASSEMBLY ONLY" in text
            and "D3 BCPLMAIN+BCPLIO CANDIDATE: 1" in text
        ),
        "BCPLM6 linked once": text.count(" INCLUDE OBJ(BCPLM6)") == 1,
        "BCPLIO linked once": text.count(" INCLUDE OBJ(BCPLIO)") == 1,
        "one GO step": len(re.findall(r"^//GO\s+EXEC\b", text, re.M)) == 1,
        "GO SYSPRINT DD": bool(re.search(
            r"^//SYSPRINT\s+DD\s+SYSOUT=\*", text, re.M)),
        "GO BCPALT DD": bool(re.search(
            r"^//BCPALT\s+DD\s+SYSOUT=\*", text, re.M)),
    }
    invalid = [name for name, ok in checks.items() if not ok]
    if invalid:
        raise ValueError("candidate 114 source deck rejected: "
                         + ", ".join(invalid))


def inspect() -> int:
    print("M5.1 read-only TK5 route inspection")
    ready = True
    for desc, path in (("class A / PRINTER1", A),
                       ("class Z / PRINTER2", Z)):
        try:
            info = printer_state(path)
            print(f"  {desc}: {info['path']} ({info['offset']} bytes)")
        except (OSError, ValueError) as exc:
            print(f"  {desc}: UNAVAILABLE: {exc}")
            ready = False

    # TK5 config lives inside Docker and is deliberately excluded from Git.
    # This is inspection only; not proof of live JES class assignment.
    try:
        result = subprocess.run(
            ["docker", "exec", "mvs38j", "cat", "/tk5/conf/tk5.cnf"],
            text=True, capture_output=True, timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"  Live config: UNAVAILABLE: {exc}")
        ready = False
    else:
        if result.returncode != 0:
            print("  Live config: UNAVAILABLE "
                  f"(docker exec rc {result.returncode})")
            print("  " + result.stderr.strip()[:400])
            ready = False
        else:
            for address, wanted in (("000E", "prt00e.txt"),
                                    ("000F", "prt00f.txt")):
                # Show the active device declaration; do not infer
                # spool SYSOUT-class routing from a device line.
                matched = [line.strip() for line in result.stdout.splitlines()
                           if re.search(rf"^\s*{address}\s+1403\b",
                                        line, re.I)]
                if len(matched) != 1 or wanted not in matched[0].lower():
                    print(f"  Device {address}: UNCONFIRMED (1403 / {wanted})")
                    ready = False
                else:
                    print(f"  Device {address}: {matched[0]}")
    print("  JES class A/Z -> physical device mapping: NOT YET PROVED")
    print("  Original FB132 bytes: NOT CAPTURED by printer images")
    print("  MVS/JES jobs submitted: 0")
    return 0 if ready else 1


def prepare() -> int:
    if STATE.exists() or DECK.exists():
        raise ValueError("probe already staged; preserve previous artifacts "
                         "before preparing a fresh one")
    if not SOURCE.is_file():
        raise ValueError("missing candidate GO deck: "
                         f"{SOURCE.relative_to(ROOT)}; do not substitute "
                         "native-test-heavy.jcl; a new 114 test run "
                         "requires separate authorization")
    origin = SOURCE.read_text(encoding="ascii")
    check_source(origin)
    for path in (EXPECTED_A, EXPECTED_Z):
        if not path.is_file() or not path.read_bytes():
            raise ValueError(f"missing/empty expected fixture: {path}")
    printers = {"A": printer_state(A), "Z": printer_state(Z)}
    if (printers["A"]["dev"], printers["A"]["ino"]) == (
            printers["Z"]["dev"], printers["Z"]["ino"]):
        raise ValueError("A and Z resolve to the same printer file")

    # Import only the pure deck transformation, without calling its main.
    transform = runpy.run_path(
        str(ROOT / "tools/checks/prepare-dd-attribution-probe.py"),
        run_name="m51_non_submitting_transform",
    )["prepare"]
    transform(SOURCE, DECK)
    built = DECK.read_text(encoding="ascii")
    if not re.search(r"^//AT114R\s+JOB\b", built, re.M):
        raise ValueError("transformed JOB identity incorrect")
    if built.count("SYSOUT=Z") != 1:
        raise ValueError("expected exactly one class Z GO allocation")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=True)
    manifest = {
        "schema": "bcpl-m51-class-route-v1", "prepared_utc": now(),
        "git_sha": head.stdout.strip(), "jobname": "AT114R",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": digest(SOURCE.read_bytes()),
        "deck": str(DECK.relative_to(ROOT)),
        "deck_sha256": digest(DECK.read_bytes()),
        "expected_a_sha256": digest(EXPECTED_A.read_bytes()),
        "expected_z_sha256": digest(EXPECTED_Z.read_bytes()),
        "printers": printers,
        "status": "STAGED_ONLY_NOT_SUBMITTED",
        "limit": "printer routing probe; no raw QSAM FB132 byte fidelity"
    }
    STATE.write_text(json.dumps(manifest, indent=2) + "\n",
                     encoding="utf-8")
    print(f"Captured offsets in {STATE.relative_to(ROOT)}")
    print("  A:", printers["A"]["offset"],
          "  Z:", printers["Z"]["offset"])
    print("No MVS job submitted. After confirming real JES class routing:")
    print(f"  tools/mvs/submit-jcl {DECK.relative_to(ROOT)}")
    print("  python3 tools/checks/m51-route-probe.py verify JOB_NUMBER")
    return 0


def segment(path: Path, offset: int) -> bytes:
    with path.open("rb") as stream:
        stream.seek(offset)
        return stream.read()


def verify(job: int) -> int:
    if not STATE.is_file():
        raise ValueError("prepare metadata missing")
    metadata = json.loads(STATE.read_text(encoding="utf-8"))
    if metadata.get("schema") != "bcpl-m51-class-route-v1":
        raise ValueError("unsupported or missing metadata schema")
    if metadata["deck_sha256"] != digest(DECK.read_bytes()):
        raise ValueError("staged JCL changed after offset capture")
    if metadata["expected_a_sha256"] != digest(EXPECTED_A.read_bytes()):
        raise ValueError("SYSPRINT expected fixture changed")
    if metadata["expected_z_sha256"] != digest(EXPECTED_Z.read_bytes()):
        raise ValueError("BCPALT expected fixture changed")
    captures = {}
    for queue, path in (("A", A), ("Z", Z)):
        current = printer_state(path)
        original = metadata["printers"][queue]
        if (current["dev"], current["ino"]) != (
                original["dev"], original["ino"]):
            raise ValueError(f"{queue} printer was replaced/rotated")
        if current["offset"] <= original["offset"]:
            raise ValueError(f"{queue} printer did not grow")
        captures[queue] = segment(path, original["offset"])

    # Archive both *formatted* printer sections for reproducibility.
    # They must NOT be represented as the original QSAM FB132 records.
    for queue, data in captures.items():
        (WORK / f"m51-printer-{queue}-formatted.bin").write_bytes(data)
    checker = runpy.run_path(
        str(ROOT / "tools/checks/check-dd-attribution.py"),
        run_name="m51_route_verifier",
    )["verify"]
    evidence = {"schema": "bcpl-m51-class-route-result-v1",
                "observed_utc": now(), "job": job, "jobname": "AT114R",
                "prepared_sha": metadata["git_sha"],
                "results": {}, "status": "FAIL"}
    for queue, data in captures.items():
        evidence["results"][queue] = {
            "relative_capture": f"m51-printer-{queue}-formatted.bin",
            "formatted_bytes": len(data), "sha256": digest(data),
            "start_offset": metadata["printers"][queue]["offset"]}
    try:
        checker(A, Z, metadata["printers"]["A"]["offset"],
                metadata["printers"]["Z"]["offset"], job,
                "AT114R", EXPECTED_A, EXPECTED_Z)
    except (OSError, ValueError) as exc:
        evidence["reason"] = str(exc)
        EVIDENCE.write_text(json.dumps(evidence, indent=2)+"\n",
                            encoding="utf-8")
        print(f"M5.1 class-route probe FAIL: {exc}", file=sys.stderr)
        return 1
    evidence["status"] = "PRINTER_ROUTE_PASS_ONLY"
    EVIDENCE.write_text(json.dumps(evidence, indent=2)+"\n",
                        encoding="utf-8")
    print("M5.1 route evidence: PASS for separate A/Z printer images")
    print("Saved: " + str(EVIDENCE.relative_to(ROOT)))
    print("LIMIT: DD-labelled raw JES2 spool and original QSAM FB132 "
          "bytes remain UNVERIFIED")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="operation", required=True)
    sub.add_parser("inspect", help="read live printer/device evidence")
    sub.add_parser("prepare", help="prepare GO deck and save offsets ONLY")
    check = sub.add_parser("verify", help="verify one manually submitted job")
    check.add_argument("job", type=int)
    args = p.parse_args()
    try:
        if args.operation == "inspect":
            return inspect()
        if args.operation == "prepare":
            return prepare()
        if args.job < 0:
            raise ValueError("invalid JES job number")
        return verify(args.job)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError,
            UnicodeError, json.JSONDecodeError) as exc:
        print(f"m51-route-probe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
