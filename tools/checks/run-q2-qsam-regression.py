#!/usr/bin/env python3
"""Native numbered QSAM regressions 163..174; no simulated target results.

Each case compiles BCPL with the resident demoted Cambridge compiler,
builds real source-mode IFOX/IEWL JCL, submits one JES job and checks
actual steps, records and relevant independent QSAM/IEWL evidence.
Permanent MVS datasets are read-only; no retry after uncertain submit.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "bootstrap-toolchain/regression"
EXT = ROOT / "bootstrap-toolchain/extensions/bcplqsam"
TOOLS = ROOT / "tools"
WORK = ROOT / "workarea/native-regression"

# Number: generator kind, canonical source, original native job, GO marker(s).
CASES = {
  163: ("query", "test-q3-query.bcpl", "Q2QUERY",
        ("BCPLQSAM Q3 QUERY VARIABLE PASS",)),
  164: ("negative", "test-q1-negative.bcpl", "Q1NEG",
        ("BCPLQSAM Q1 NEGATIVE PASS",)),
  165: ("output", "test-q1-output.bcpl", "Q1OUT",
        ("BCPLQSAM Q1 OUTPUT PASS",)),
  166: ("finish", "test-q1-finish.bcpl", "Q16FIN",
        ("BCPLQSAM Q1 16 FINISH PASS",)),
  167: ("stop", "test-q1-stop.bcpl", "Q16STP",
        ("BCPLQSAM Q1 16 STOP PASS",)),
  168: ("full", "test-q2-write.bcpl", "Q2FULL",
        ("BCPLQSAM Q2 WRITE 23 F80 FB80 PASS",
         "BCPLQSAM Q2 READ COPY EOF RETRY PASS",
         "BCPLQSAM Q2 COPY 23 FB80 EXACT PASS")),
  169: ("stopflush", "test-q2-stop-flush.bcpl", "Q2STOP",
        ("BCPLQSAM Q2 STOP FB80 WRITTEN PASS",
         "BCPLQSAM Q2 STOP FLUSH FB80 EXACT PASS")),
  170: ("mix", "test-q3-mix.bcpl", "Q2MIX",
        ("Q2 MIX BCPLQSAM BCPLDEMO WRITTEN PASS",
         "Q2 MIX BCPLQSAM BCPLDEMO FB80 EXACT PASS")),
  171: ("vread", "test-q3-limit-read.bcpl", "Q3VLRED",
        ("BCPLQSAM Q3 1024 V/VB READ 7 PASS",)),
  172: ("vwrite", "test-q3-limit-write.bcpl", "Q3VLWRT",
        ("BCPLQSAM Q3 1024 V/VB WRITE 7 PASS",
         "BCPLQSAM Q3 1024 V/VB IFOX RDW 7 PASS")),
  173: ("vbread", "test-q3-limit-read.bcpl", "Q3VBRED",
        ("BCPLQSAM Q3 1024 V/VB READ 7 PASS",)),
  174: ("vbwrite", "test-q3-limit-write.bcpl", "Q3VBWRT",
        ("BCPLQSAM Q3 1024 V/VB WRITE 7 PASS",
         "BCPLQSAM Q3 1024 V/VB IFOX RDW 7 PASS")),
}
BASIC = ("ASMA", "ASMN", "ASMR", "ASMQ", "ASMG", "LKED", "GO")
LIFE = ("ASMWR", "LKWR", "ASMA", "ASMN", "ASMR",
        "ASMQ", "ASMG", "LKED", "WGO", "GO")
FULL = ("ASMA", "ASMB", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
        "LKED", "LKRD", "LKVR", "WGO", "RGO", "VGO")
STOP = ("ASMA", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
        "LKED", "LKVR", "BGO", "VGO")
LIMIT_READ = ("ASMA", "ASML", "ASMN", "ASMR", "ASMQ", "ASMG",
              "LKWR", "LKED", "WGO", "RGO")
LIMIT_WRITE = ("ASMA", "ASML", "ASMN", "ASMR", "ASMQ", "ASMG",
               "LKVR", "LKED", "WGO", "VGO")
LIMIT_CASES = ("vread", "vwrite", "vbread", "vbwrite")


def load(name: str):
    file = EXT / name
    spec = importlib.util.spec_from_file_location(
        "qsam_reg_" + name.replace("-", "_").replace(".", "_"), file)
    if spec is None or spec.loader is None:
        raise ValueError("missing native source generator " + str(file))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke(args: list[str], out: Path, limit: int) -> tuple[int, str]:
    try:
        with out.open("w", encoding="utf-8") as stream:
            result = subprocess.run(
                args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                check=False, timeout=limit)
        rc = result.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    except OSError as exc:
        out.write_text(str(exc) + "\n", encoding="utf-8")
        rc = 127
    value = out.read_text("utf-8", errors="replace")
    if out.name != "report.txt":
        print(value, end="" if value.endswith("\n") else "\n", flush=True)
    return rc, value


def checked_fixture(case: Path, filename: str, original: str) -> Path:
    target = case / filename
    canonical = EXT / original
    if not target.is_file() or target.read_bytes() != canonical.read_bytes():
        raise ValueError(
            f"{target}: must exactly match canonical extension source {original}")
    return target


def prepare(kind: str, generated: str, reader: str | None) -> str:
    query = load("prepare-q1-query.py")
    core = query.time_helper().trailer_helper().load_core()
    cfg = core.load_config()
    def object_dsn(name: str) -> str:
        obj = cfg["datasets"][name]
        if (obj.get("dsorg") != "PO" or obj.get("recfm") != "FB"
            or obj.get("content_type") != "object"
            or int(obj.get("lrecl", 0)) != 80):
            raise ValueError("unapproved FB80 object library: " + name)
        return core.full_dsn(cfg, obj)
    obj = object_dsn("BOOT_OBJ")
    ext_obj = object_dsn("EXT_OBJ") if kind == "mix" else None
    original_job = next(job for k, _, job, _ in CASES.values() if k == kind)
    title = "Q3 NATIVE REG" if kind in LIMIT_CASES else "Q2 NATIVE REG"
    card = core.authenticated_job_card(
        cfg, original_job, title, redact_password=False)
    if kind == "query":
        deck = load("prepare-q2-query.py").make_deck(generated, card, obj)
    elif kind in ("negative", "output", "finish", "stop"):
        deck = load("prepare-q1-campaign.py").make_deck(
            kind, generated, card, obj)
    elif kind == "full":
        if reader is None:
            raise ValueError("Q2FULL requires independently compiled reader")
        deck = load("prepare-q2-consolidated.py").make_deck(
            generated, reader, card, obj)
    elif kind == "stopflush":
        deck = load("prepare-q2-stop-flush.py").make_deck(
            generated, card, obj)
    elif kind == "mix":
        deck = load("prepare-q2-mix.py").make_deck(
            generated, card, obj, ext_obj)
    elif kind in LIMIT_CASES:
        fmt = "vb" if kind.startswith("vb") else "v"
        writing = kind.endswith("write")
        deck = load("prepare-q3-v-read.py").make_limit_deck(
            generated, card, obj, fmt, writing)
    else:
        raise ValueError("unknown native QSAM campaign " + kind)
    for line in deck.splitlines():
        if not line.isascii() or len(line) > 71:
            raise ValueError("JCL card width/encoding invalid")
        if ("CATLG" in line or "DISP=MOD" in line or
            (line.startswith("//") and not line.startswith("//*") and
             "BOOT_DEVOBJ" in line)):
            raise ValueError("permanent MVS output forbidden")
    return deck


def evidence(number: int, summary: str, report: str) -> list[str]:
    kind, _, job, markers = CASES[number]
    issues: list[str] = []
    if len(re.findall(rf"^JOB\s+\d+\s+{job}\s*$", summary, re.M)) != 1:
        issues.append("wrong/missing native JES job name")
    steps = (LIMIT_READ if kind in ("vread", "vbread")
             else LIMIT_WRITE if kind in ("vwrite", "vbwrite")
             else FULL if kind == "full"
             else LIFE if kind in ("finish", "stop")
             else STOP if kind in ("stopflush", "mix") else BASIC)
    found: dict[str, list[int]] = {}
    for line in summary.splitlines():
        match = re.match(
            r"^\s*([A-Z0-9]{2,8})\s+\S.*?\bRC=(\d{4})\s*$", line)
        if match and match.group(1) in set(steps):
            found.setdefault(match.group(1), []).append(int(match.group(2)))
    if set(found) != set(steps):
        issues.append("missing/unexpected IFOX/IEWL/GO step coverage")
    for step in steps:
        wanted = 8 if (step == "BGO" or
                       (step == "GO" and kind == "stop")) else 0
        if found.get(step) != [wanted]:
            issues.append(f"{step}: expected RC={wanted:04d}, got {found.get(step)}")
    if "JOB RESULT: SUCCESS" not in summary:
        issues.append("native JES JOB RESULT not SUCCESS")
    for text in ("Statements flagged", "Highest severity"):
        m = re.search(rf"{text}:\s*(\d+)", summary)
        if m is None or int(m.group(1)) != 0:
            issues.append(text + " not proven zero")
    records = [s.strip() for s in report.replace("\f", "").splitlines()]
    for marker in markers:
        if records.count(marker) != 1:
            issues.append("missing or duplicate exact output: " + marker)
    positions = [records.index(m) for m in markers if m in records]
    if len(positions) == len(markers) and positions != sorted(positions):
        issues.append("record order incorrect")
    if kind == "full":
        issues += load("check-q2-consolidated-evidence.py").check(
            summary, report)
    if kind == "mix":
        issues += load("check-q2-mix-evidence.py").check(summary, report)
    if kind in ("negative", "output"):
        good, errors = load("check-q1-campaign-evidence.py").review(
            kind, summary, report)
        if not good:
            issues += errors
    return issues


def run(number: int, case: Path) -> int:
    if number not in CASES or not case.resolve().is_relative_to(REG.resolve()):
        raise ValueError("invalid QSAM case identity")
    kind, original, job, markers = CASES[number]
    if not case.name.startswith(f"{number:03d}-"):
        raise ValueError("case number/directory mismatch")
    source = checked_fixture(case, "source.bcpl", original)
    if (case / "expected.txt").read_text("ascii").splitlines() != list(markers):
        raise ValueError("case expected.txt differs from native evidence contract")
    if (case / "qsam-native.txt").read_text("ascii").strip() != kind:
        raise ValueError("wrong QSAM native profile fixture")
    extra = (checked_fixture(case, "reader.bcpl", "test-q2-read.bcpl")
             if kind == "full" else None)

    work = WORK / case.name
    work.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix="native-", dir=work))
    print(f"QSAM case {number}, JES job {job}, evidence {attempt}", flush=True)

    generated: list[str] = []
    for index, src in enumerate([source, *([extra] if extra else [])]):
        path = attempt / ("generated.asm" if index == 0 else "reader.asm")
        jobname = f"RG{number:03d}{'C' if index == 0 else 'D'}"
        rc, _ = invoke(
            [sys.executable, str(TOOLS / "bootstrap/compile-mvs"),
             str(src), "--job-name", jobname, "--output", str(path)],
            attempt / ("compile.log" if index == 0 else "reader-compile.log"),
            300)
        print(f"{jobname} Cambridge compiler RC={rc}", flush=True)
        if rc or not path.is_file() or path.stat().st_size == 0:
            return 1
        generated.append(path.read_bytes().decode("latin-1"))

    deck = prepare(kind, generated[0],
                   generated[1] if len(generated) > 1 else None)
    jcl = attempt / "native.jcl"
    with jcl.open("x", encoding="ascii", newline="\n") as out:
        out.write(deck)
    jcl.chmod(0o600)
    print(f"Source-mode MVS deck: {len(deck.splitlines())} cards", flush=True)
    rc, response = invoke(
        [str(TOOLS / "mvs/submit-jcl"), "--timeout", "120", str(jcl)],
        attempt / "submit.log", 180)
    jobs = re.findall(r"^JOB ([0-9]+)$", response, re.M)
    if rc or len(jobs) != 1:
        print("Submission uncertain: inspect JES; never resubmit this attempt")
        return 1
    job_number = jobs[0]
    (attempt / "job-number.txt").write_text(job_number + "\n", "ascii")
    summary = ""
    summary_rc = 2
    for _ in range(45):
        summary_rc, summary = invoke(
            [str(TOOLS / "mvs/job-summary"), job_number, "--max-rc", "8",
             "--verbose"], attempt / "summary.txt", 30)
        if summary_rc != 2:
            break
        time.sleep(2)
    report_rc, report = invoke(
        [str(TOOLS / "mvs/dump-report-for-job"), job_number],
        attempt / "report.txt", 45)
    print(f"JES job {job_number}: summary RC={summary_rc}, report RC={report_rc}")
    if summary_rc or report_rc:
        return 1
    errors = evidence(number, summary, report)
    if errors:
        for error in errors:
            print("QSAM evidence NOT VERIFIED: " + error)
        return 1
    print(f"QSAM native case {number} PASS; job {job_number}")
    print("=== Regression result ===")
    print(f"TEST: {case.name}")
    print("RESULT: PASS")
    return 0


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: run-q2-qsam-regression.py NUMBER CASE_DIR")
        return 64
    try:
        return run(int(sys.argv[1]), Path(sys.argv[2]))
    except (ValueError, OSError, UnicodeError, KeyError) as exc:
        print("QSAM native regression FAILED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
