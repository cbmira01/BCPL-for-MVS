#!/usr/bin/env python3
"""PDS/member I/O commands for dspal."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import os
import re
import secrets
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "tools" / "dspal-core.py"


def load_core():
    spec = importlib.util.spec_from_file_location("dspal_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load_core()
DspalError = core.DspalError


def validate_member(member: str) -> str:
    value = member.strip().upper()
    if not re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}", value):
        raise DspalError(f"invalid PDS member name: {member}")
    return value


def resolve_pds(config: dict[str, Any], operand: str, *, text_required: bool = False):
    dsn, logical = core.resolve_dsn(config, operand)
    spec = config["datasets"].get(logical) if logical else None
    if spec is not None:
        if str(spec.get("dsorg", "")).upper() != "PO":
            raise DspalError(f"not a partitioned data set: {dsn}")
        if text_required and str(spec.get("content_type", "")).lower() == "object":
            raise DspalError(f"binary object library {dsn}: text cat/get/put prohibited")
        if text_required and str(spec.get("recfm", "")).upper() == "U":
            raise DspalError(f"text member transfer is not supported for load library {dsn}")
    return dsn, logical, spec


def list_members_deck(config: dict[str, Any], dsn: str, redact_password: bool = False) -> str:
    lines = core.authenticated_job_card(
        config, "DSPALLS", "DSPAL LS", redact_password=redact_password
    )
    lines.extend(
        [
            "//* LIST PDS MEMBERS WITH TSO LISTDS MEMBERS",
            "//LIST     EXEC PGM=IKJEFT01",
            "//SYSTSPRT DD  SYSOUT=*",
            "//SYSTSIN  DD  *",
            f" LISTDS '{dsn}' MEMBERS",
            "/*",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_members(report: str, dsn: str) -> list[str]:
    lines = report.splitlines()
    candidates: list[int] = []
    for index, line in enumerate(lines):
        if "--MEMBERS--" in line.upper():
            prefix = "\n".join(lines[max(0, index - 15) : index]).upper()
            if dsn.upper() in prefix:
                candidates.append(index)
    if not candidates:
        return []

    members: list[str] = []
    for line in lines[candidates[-1] + 1 :]:
        text = line.strip().upper()
        if not text:
            continue
        if text == "END" or text.startswith("--") or text.startswith("IEF") or text.startswith("$HASP"):
            break
        token = text.split()[0]
        if re.fullmatch(r"[A-Z@$#][A-Z0-9@$#]{0,7}", token):
            members.append(token)
        else:
            break
    return members


def choose_sentinels() -> tuple[str, str]:
    token = secrets.token_hex(6).upper()
    return f"DSPALBEGIN{token}", f"DSPALEND{token}"


def member_read_deck(
    config: dict[str, Any], dsn: str, member: str, begin: str, end: str,
    redact_password: bool = False,
) -> str:
    lines = core.authenticated_job_card(
        config, "DSPALGET", "DSPAL GET", redact_password=redact_password
    )
    lines.extend(
        [
            "//* COPY ONE FB TEXT MEMBER TO SYSOUT BETWEEN SENTINELS",
            "//COPY     EXEC PGM=IEBGENER",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            "//SYSUT2   DD  SYSOUT=*,DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)",
            "//SYSUT1   DD  DATA,DLM=Z9",
            begin,
            "Z9",
            f"//         DD  DSN={dsn}({member}),DISP=SHR",
            "//         DD  DATA,DLM=Z9",
            end,
            "Z9",
        ]
    )
    return "\n".join(lines) + "\n"


def extract_member_text(report: str, begin: str, end: str) -> str:
    lines = report.splitlines()
    starts = [i for i, line in enumerate(lines) if line.rstrip() == begin]
    if not starts:
        raise DspalError("member transfer completed but begin sentinel was not found in SYSOUT")
    start = starts[-1]
    stop = None
    for i in range(start + 1, len(lines)):
        if lines[i].rstrip() == end:
            stop = i
            break
    if stop is None:
        raise DspalError("member transfer completed but end sentinel was not found in SYSOUT")
    records = [line.rstrip(" ") for line in lines[start + 1 : stop]]
    return "\n".join(records) + ("\n" if records else "")


def normalize_input_text(config: dict[str, Any], text: str, lrecl: int) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    records = normalized.split("\n")
    if records and records[-1] == "":
        records.pop()

    mvs_encoding = str(config["text"].get("mvs_encoding", "cp037"))
    for number, record in enumerate(records, 1):
        try:
            encoded = record.encode(mvs_encoding, errors="strict")
        except UnicodeEncodeError as exc:
            raise DspalError(
                f"input line {number} contains a character not representable in {mvs_encoding}"
            ) from exc
        if len(encoded) > lrecl:
            raise DspalError(
                f"input line {number} is {len(encoded)} bytes in {mvs_encoding}; LRECL is {lrecl}; refusing to truncate"
            )
        try:
            record.encode("ascii", errors="strict")
        except UnicodeEncodeError as exc:
            raise DspalError(
                f"input line {number} contains non-ASCII text; the current TK5 socket-reader transfer path accepts only the ASCII subset of {mvs_encoding}"
            ) from exc
    return records


def choose_dlm(records: list[str]) -> str:
    candidates = [f"{a}{b}" for a in "ZQXYWVUTSR" for b in "0123456789"]
    for candidate in candidates:
        if all(not record.startswith(candidate) for record in records):
            return candidate
    raise DspalError("could not choose a safe two-character JCL DLM for input")


def member_put_deck(
    config: dict[str, Any], dsn: str, member: str, records: list[str],
    redact_password: bool = False,
) -> str:
    dlm = choose_dlm(records)
    lines = core.authenticated_job_card(
        config, "DSPALPUT", "DSPAL PUT", redact_password=redact_password
    )
    lines.extend(
        [
            "//* REPLACE OR CREATE ONE FB TEXT MEMBER WITH IEBGENER",
            "//COPY     EXEC PGM=IEBGENER",
            "//SYSPRINT DD  SYSOUT=*",
            "//SYSIN    DD  DUMMY",
            f"//SYSUT2   DD  DSN={dsn}({member}),DISP=SHR",
            f"//SYSUT1   DD  DATA,DLM={dlm}",
        ]
    )
    lines.extend(records)
    lines.append(dlm)
    return "\n".join(lines) + "\n"


def cmd_list(config: dict[str, Any]) -> int:
    for logical, spec in config["datasets"].items():
        print(f"{logical:<9} {core.full_dsn(config, spec):<26} {spec['description']}")
    return 0


def cmd_ls(config: dict[str, Any], dataset: str, show_jcl: bool, raw: bool) -> int:
    dsn, _, _ = resolve_pds(config, dataset)
    if show_jcl:
        sys.stdout.write(list_members_deck(config, dsn, redact_password=True))
        return 0
    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, list_members_deck(config, dsn), max_rc=8)
    report = core.job_report(job)
    if raw:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            print()
        return 0
    if core.dataset_missing(report, dsn):
        raise DspalError(f"data set not found: {dsn}")
    for member in parse_members(report, dsn):
        print(member)
    return 0


def read_member(config: dict[str, Any], dataset: str, member: str, show_jcl: bool = False):
    dsn, _, spec = resolve_pds(config, dataset, text_required=True)
    member = validate_member(member)
    if spec is not None:
        if str(spec.get("recfm", "")).upper() != "FB":
            raise DspalError(f"text transfer currently requires RECFM=FB: {dsn}")
        if int(spec.get("lrecl", 0) or 0) != 80:
            raise DspalError(f"text transfer currently requires LRECL=80: {dsn}")
    begin, end = choose_sentinels()
    deck = member_read_deck(config, dsn, member, begin, end, redact_password=show_jcl)
    if show_jcl:
        return None, deck
    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, deck, max_rc=0)
    report = core.job_report(job)
    return job, extract_member_text(report, begin, end)


def cmd_cat(config: dict[str, Any], dataset: str, member: str, show_jcl: bool) -> int:
    _, result = read_member(config, dataset, member, show_jcl=show_jcl)
    sys.stdout.write(result)
    return 0


def cmd_get(config: dict[str, Any], dataset: str, member: str, destination: str, show_jcl: bool) -> int:
    job, result = read_member(config, dataset, member, show_jcl=show_jcl)
    if show_jcl:
        sys.stdout.write(result)
        return 0
    if destination == "-":
        sys.stdout.write(result)
    else:
        path = Path(destination)
        path.write_text(result, encoding=str(config["text"].get("host_encoding", "utf-8")), newline="\n")
        print(f"get completed as JOB {job}: {dataset.upper()}({member.upper()}) -> {path}", file=sys.stderr)
    return 0


def source_text(config: dict[str, Any], source: str) -> str:
    encoding = str(config["text"].get("host_encoding", "utf-8"))
    if source == "-":
        return sys.stdin.read()
    path = Path(source)
    try:
        return path.read_text(encoding=encoding)
    except OSError as exc:
        raise DspalError(f"cannot read {path}: {exc}") from exc


def cmd_put(config: dict[str, Any], dataset: str, member: str, source: str, show_jcl: bool) -> int:
    dsn, _, spec = resolve_pds(config, dataset, text_required=True)
    member = validate_member(member)
    if spec is None:
        raise DspalError("put currently requires a managed PDS logical name so LRECL can be validated")
    if str(spec.get("recfm", "")).upper() != "FB":
        raise DspalError(f"put currently requires RECFM=FB: {dsn}")
    lrecl = int(spec.get("lrecl", 0) or 0)
    if lrecl <= 0:
        raise DspalError(f"put requires a positive LRECL: {dsn}")

    records = normalize_input_text(config, source_text(config, source), lrecl)
    deck = member_put_deck(config, dsn, member, records, redact_password=show_jcl)
    if show_jcl:
        sys.stdout.write(deck)
        return 0
    core.require_reader_ready(config)
    job, _ = core.submit_and_wait(config, deck, max_rc=0)
    print(f"put completed as JOB {job}: {source} -> {dsn}({member})")
    return 0


def build_parsers():
    parser = argparse.ArgumentParser(description="Manage BCPL project datasets on MVS/TK5.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list managed BCPL datasets from the manifest")

    ls = sub.add_parser("ls", help="list members of a PDS")
    ls.add_argument("dataset", help="managed logical name or PDS DSN")
    ls_mode = ls.add_mutually_exclusive_group()
    ls_mode.add_argument("--show-jcl", action="store_true", help="emit LISTDS MEMBERS JCL without submitting")
    ls_mode.add_argument("--raw", action="store_true", help="print the complete JES report")

    cat = sub.add_parser("cat", help="write one text PDS member to stdout")
    cat.add_argument("dataset")
    cat.add_argument("member")
    cat.add_argument("--show-jcl", action="store_true")

    get = sub.add_parser("get", help="copy one text PDS member to a host file or -")
    get.add_argument("dataset")
    get.add_argument("member")
    get.add_argument("destination")
    get.add_argument("--show-jcl", action="store_true")

    put = sub.add_parser("put", help="replace/create one text PDS member from a host file or -")
    put.add_argument("dataset")
    put.add_argument("member")
    put.add_argument("source")
    put.add_argument("--show-jcl", action="store_true")

    help_parser = sub.add_parser("help", help="show dspal command help")
    help_parser.add_argument("topic", nargs="?")

    return parser, {name: sub.choices[name] for name in sub.choices}


def print_global_help() -> None:
    print("usage: dspal COMMAND [options]")
    print()
    print("Manage BCPL project datasets on MVS/TK5.")
    print()
    print("Commands:")
    rows = [
        ("help [COMMAND]", "show this help or command-specific help"),
        ("info", "show effective dspal configuration"),
        ("status", "check local MVS/TK5 readiness"),
        ("stat [DATASET]", "show MVS dataset attributes; no operand means all managed datasets"),
        ("list", "list managed datasets from the manifest"),
        ("ls DATASET", "list PDS members"),
        ("cat DATASET MEMBER", "write a text member to stdout"),
        ("get DATASET MEMBER FILE", "copy a text member to a host file; FILE may be -"),
        ("put DATASET MEMBER FILE", "replace/create a text member; FILE may be -"),
        ("initbcpl", "create missing managed datasets after attribute preflight"),
    ]
    for name, description in rows:
        print(f"  {name:<27} {description}")
    print()
    print("Use: dspal help COMMAND")


def cmd_help(topic: str | None, parsers: dict[str, argparse.ArgumentParser]) -> int:
    if topic is None:
        print_global_help()
        return 0
    topic = topic.lower()
    if topic in {"info", "status", "stat", "initbcpl"}:
        os.execv(sys.executable, [sys.executable, str(CORE_PATH), topic, "--help"])
    parser = parsers.get(topic)
    if parser is None:
        raise DspalError(f"unknown help topic: {topic}")
    parser.print_help()
    return 0


def main() -> int:
    try:
        parser, parsers = build_parsers()
        args = parser.parse_args()
        config = core.load_config()

        if args.command == "list":
            return cmd_list(config)
        if args.command == "ls":
            return cmd_ls(config, args.dataset, args.show_jcl, args.raw)
        if args.command == "cat":
            return cmd_cat(config, args.dataset, args.member, args.show_jcl)
        if args.command == "get":
            return cmd_get(config, args.dataset, args.member, args.destination, args.show_jcl)
        if args.command == "put":
            return cmd_put(config, args.dataset, args.member, args.source, args.show_jcl)
        if args.command == "help":
            return cmd_help(args.topic, parsers)
        raise DspalError(f"unimplemented command: {args.command}")
    except (DspalError, OSError, ValueError) as exc:
        print(f"dspal: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
