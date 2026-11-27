#!/usr/bin/env python3
"""Native numbered QSAM regressions 163..176 and 198..200; no simulated target results.

Each case compiles BCPL with the resident demoted Cambridge compiler,
builds real source- or installed-mode IFOX/IEWL JCL, submits one JES job and checks
actual steps, records and relevant independent QSAM/IEWL evidence.
Permanent MVS datasets are read-only; no retry after uncertain submit.
Q4_PUNCH_RESUME=1 permits one guarded $S PUN1 only for isolated case 175.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "tests/system-extensions/bcplqsam"
EXT = ROOT / "system-extensions/bcplqsam"
TOOLS = ROOT / "tools"
WORK = ROOT / "workarea/native-regression"

# Number: generator kind, canonical source, original native job, GO marker(s).
CASES = {
  163: ("query", "test-q4-query.bcpl", "Q2QUERY",
        ("BCPLQSAM Q4 QUERY CARRIAGE PASS",)),
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
  170: ("mix", "test-q4-mix.bcpl", "Q2MIX",
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
  175: ("punch", "test-q4-punch.bcpl", "Q4PUNCH",
        ("BCPLQSAM Q4 FB80 PUNCH DUAL WRITE PASS",
         "BCPLQSAM Q4 FB80 TEMP EXACT 3 PASS")),
  176: ("fba", "test-q4-fba.bcpl", "Q4FBA",
        ("BCPLQSAM Q4 FBA133 DUAL WRITE PASS",
         "BCPLQSAM Q4 FBA133 TEMP EXACT 3 PASS")),
  198: ("rollback", "test-q5-open-rollback.bcpl", "Q5RBFIN",
        ("BCPLQSAM Q5 OPEN ROLLBACK PASS",)),
  199: ("getmain", "test-q5-open-rollback.bcpl", "Q5RGM",
        ("BCPLQSAM Q5 OPEN ROLLBACK PASS",)),
  200: ("combined", "test-dr5-combined-rollback.bcpl", "DR5QCOM",
        ("BCPLQSAM DR5 COMBINED ROLLBACK PASS",)),
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
SYSOUT_STEPS = ("ASMA", "ASMV", "ASMN", "ASMR", "ASMQ", "ASMG",
                "LKVR", "LKED", "WGO", "VGO")
SYSOUT_PATHS = {
    "punch": ROOT / "mvs-state/pch/pch00d.txt",
    "fba": ROOT / "mvs-state/prt/prt00e.txt",
}
LIMIT_CASES = ("vread", "vwrite", "vbread", "vbwrite")
INSTALLED = runpy.run_path(str(TOOLS / "checks/qsam-installed-mode.py"))
FAULTS = runpy.run_path(str(TOOLS / "checks/qsam-fault-regressions.py"))


def expected_steps(kind):
    return (SYSOUT_STEPS if kind in SYSOUT_PATHS
            else LIMIT_READ if kind in ("vread", "vbread")
            else LIMIT_WRITE if kind in ("vwrite", "vbwrite")
            else FULL if kind == "full"
            else LIFE if kind in ("finish", "stop", *FAULTS["KINDS"])
            else STOP if kind in ("stopflush", "mix") else BASIC)


def execution_mode():
    mode = os.environ.get("BCPL_QSAM_EXTENSION_MODE", "source")
    if mode not in ("source", "installed"):
        raise ValueError("invalid BCPL_QSAM_EXTENSION_MODE")
    return mode


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


def printer_args_for_attempt(attempt: Path) -> list[str]:
    """Select a safe pre-submission JES printer cursor for this attempt."""
    trial = os.environ.get("BCPL_PRINTER_WINDOW_TRIAL", "1")
    if trial not in ("0", "1"):
        raise ValueError("BCPL_PRINTER_WINDOW_TRIAL must be 0 or 1")
    return (["--cursor-file", str(attempt / "native-printer.cursor")]
            if trial == "1" else [])


def checked_fixture(case: Path, filename: str, original: str) -> Path:
    target = case / filename
    canonical = EXT / original
    if not target.is_file() or target.read_bytes() != canonical.read_bytes():
        raise ValueError(
            f"{target}: must exactly match canonical extension source {original}")
    return target


def prepare(kind: str, generated: str, reader: str | None,
            mode="source", config=None) -> str:
    query = load("prepare-q1-query.py")
    core = query.time_helper().trailer_helper().load_core()
    if mode not in ("source", "installed", "private-diagnostic"):
        raise ValueError("invalid QSAM mode")
    if (kind in FAULTS["KINDS"]) != (mode == "private-diagnostic"):
        raise ValueError("diagnostic requires explicit private mode")
    cfg = core.load_config() if config is None else config
    def object_dsn(name: str) -> str:
        obj = cfg["datasets"][name]
        if (obj.get("dsorg") != "PO" or obj.get("recfm") != "FB"
            or obj.get("content_type") != "object"
            or int(obj.get("lrecl", 0)) != 80):
            raise ValueError("unapproved FB80 object library: " + name)
        return core.full_dsn(cfg, obj)
    obj = object_dsn("BOOT_OBJ")
    ext_obj = object_dsn("EXT_OBJ") if kind == "mix" or mode == "installed" else None
    if mode == "installed":
        spec = cfg["datasets"]["EXT_MAC"]
        if (spec.get("dsorg") != "PO" or spec.get("recfm") != "FB"
                or int(spec.get("lrecl", 0)) != 80):
            raise ValueError("EXT_MAC must be an approved FB80 PDS")
        mac = core.full_dsn(cfg, spec)
        if config is None:
            for key, value in (("BCPL_QSAM_EXTENSION_DSN", ext_obj),
                               ("BCPL_QSAM_MACRO_DSN", mac)):
                if os.environ.get(key) != value:
                    raise ValueError(key + " must match manifest DSN")
    original_job = next(job for k, _, job, _ in CASES.values() if k == kind)
    title = ("Q4 NATIVE REG" if kind in SYSOUT_PATHS else
             "Q3 NATIVE REG" if kind in LIMIT_CASES else "Q2 NATIVE REG")
    card = core.authenticated_job_card(
        cfg, "Q16FIN" if kind in FAULTS["KINDS"] else original_job,
        title, redact_password=config is not None)
    if kind in FAULTS["KINDS"]:
        deck = FAULTS["prepare"](kind, generated, card, obj, load, EXT)
    elif kind == "query":
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
    elif kind == "punch":
        deck = load("prepare-q4-punch.py").make_deck(generated, card, obj)
    elif kind == "fba":
        deck = load("prepare-q4-fba.py").make_deck(generated, card, obj)
    else:
        raise ValueError("unknown native QSAM campaign " + kind)
    for line in deck.splitlines():
        if not line.isascii() or len(line) > 71:
            raise ValueError("JCL card width/encoding invalid")
        if ("CATLG" in line or "DISP=MOD" in line or
            (line.startswith("//") and not line.startswith("//*") and
             "BOOT_DEVOBJ" in line)):
            raise ValueError("permanent MVS output forbidden")
    if mode == "installed":
        deck = INSTALLED["transform"](deck, kind, expected_steps(kind), obj, ext_obj, mac)
    return deck


def evidence(number: int, summary: str, report: str, mode="source") -> list[str]:
    kind, _, job, markers = CASES[number]
    issues: list[str] = []
    if len(re.findall(rf"^JOB\s+\d+\s+{job}\s*$", summary, re.M)) != 1:
        issues.append("wrong/missing native JES job name")
    steps = expected_steps(kind)
    if mode == "installed":
        steps = INSTALLED["installed_steps"](steps)
        if any(re.search(r"^\s*" + name + r"\s+.*RC=", summary, re.M)
               for name in INSTALLED["PRIVATE"]):
            issues.append("unexpected private assembler step")
        issues += INSTALLED["map_issues"](report, kind, steps)
    elif mode not in ("source", "private-diagnostic"):
        raise ValueError("invalid evidence mode")
    if (kind in FAULTS["KINDS"]) != (mode == "private-diagnostic"):
        raise ValueError("diagnostic evidence mode mismatch")
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
                       (step == "GO" and kind in ("stop", "combined"))) else 0
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
            summary, report, installed=(mode == "installed"))
    if kind == "mix":
        issues += load("check-q2-mix-evidence.py").check(summary, report, installed=(mode == "installed"))
    if kind in ("negative", "output"):
        good, errors = load("check-q1-campaign-evidence.py").review(
            kind, summary, report, installed=(mode == "installed"))
        if not good:
            issues += errors
    if kind in FAULTS["KINDS"]:
        actual_steps = re.findall(r"^\s*([A-Z0-9]{2,8})\s+\S.*?\bRC=\d{4}\s*$",
                                  summary, re.M)
        if tuple(actual_steps) != steps:
            issues.append("wrong private diagnostic step order")
        if kind == "rollback" and not load("check-q5-rollback-finish.py").fallthrough_confirmed(report):
            issues.append("Q5RBFIN IFOX fall-through proof missing")
        if kind == "combined":
            issues += FAULTS["registrar_issues"](summary, report)
    return issues




def maybe_resume_punch_writer(offset: int, attempt: Path, job_number: str) -> list[str]:
    """Release only this run's class-B output after proving an exclusive queue.

    The opt-in is selected by run-suite for authorized case 175 (or by the
    historical standalone Q4_PUNCH_RESUME=1 flag). The separate JES2 display
    inquiries must prove PUNCH1 paused and exactly this Q4PUNCH job pending.
    A queue/status mismatch fails closed; no writer command is sent.
    """
    if os.environ.get("Q4_PUNCH_RESUME") != "1":
        return []
    path = SYSOUT_PATHS["punch"]
    if not path.is_file():
        return ["cannot resume PUNCH1: capture file absent"]
    if path.stat().st_size != offset:
        print("Punch capture already changed; no writer command sent")
        return []

    console_log = ROOT / "mvs-state/log/3033.log"
    if not console_log.is_file():
        return ["cannot verify PUNCH1: Hercules console log missing"]

    rc, status = invoke(
        [str(TOOLS / "mvs/mvs-console"), "--settle", "2",
         "jes2", "punches"],
        attempt / "punch-device-before.log", 30)
    if rc or not re.search(
        r"\$HASP000\s+PUNCH1\s+00D\s+PAUSED\b[^\n]*\bP=Y\b[^\n]*\bQ=B\b",
        status,
    ):
        return ["PUNCH1 not verified PAUSED with P=Y and Q=B; writer not started"]

    rc, queue = invoke(
        [str(TOOLS / "mvs/mvs-console"), "--yes", "--settle", "2",
         "jes2", "$DN,Q=PPU"],
        attempt / "punch-queue-before.log", 30)
    # Reject *all* other queued jobs, including unfamiliar PUN routing.
    # Unrecognized entries are not silently treated as an empty queue.
    queued = re.findall(
        r"\bJOB\s+(\d+)\s+\$HASP000\s+([A-Z0-9]+)\b([^\n]*)",
        queue,
    )
    exclusive = (len(queued) == 1 and
                 queued[0][:2] == (job_number, "Q4PUNCH") and
                 re.search(r"\bPUN\s+LOCAL\b", queued[0][2]) is not None)
    if rc or not exclusive:
        return [f"PUNCH1 queue not exclusive to Q4PUNCH JOB {job_number}: {queued!r}"]

    if path.stat().st_size != offset:
        print("Punch capture changed during inquiries; no writer command sent")
        return []
    before = console_log.stat().st_size
    rc, response = invoke(
        ["docker", "exec", "-i", "mvs38j", "curl", "-sS", "-f", "-G",
         "--data-urlencode", "cmd=/$S PUN1",
         "http://127.0.0.1:8038/cgi-bin/tasks/cmd"],
        attempt / "punch-writer-start.log", 30)
    if rc or "HHC00013I" not in response or "$S PUN1" not in response:
        return ["JES2 PUNCH1 start not acknowledged; do not retry automatically"]

    observed = ""
    marker = re.compile(
        rf"\bJOB\s+{re.escape(job_number)}\s+\$HASP150\s+"
        r"Q4PUNCH\s+ON\s+PUNCH1\s+3 CARDS\b")
    for _ in range(12):
        with console_log.open("rb") as handle:
            handle.seek(0, 2)
            if handle.tell() < before:
                return ["Hercules console log rotated during punch verification"]
            handle.seek(before)
            observed = handle.read().decode("utf-8", errors="replace")
        if marker.search(observed):
            break
        time.sleep(1)
    (attempt / "punch-writer-result.log").write_text(
        observed, encoding="utf-8")
    if not marker.search(observed):
        return [f"JES2 did not confirm JOB {job_number} on PUNCH1; "
                "do not retry automatically"]
    print(f"JES2 PUNCH1 released JOB {job_number}; exact capture still required")
    return []


def check_sysout_capture(kind: str, offset: int, attempt: Path) -> list[str]:
    """Check newly generated Hercules device output, not prior spool data.

    QSAM temporary byte fidelity is checked independently by IFOX VGO.
    Class-A ASCII printer output proves visible ASA presentation only.
    """
    path = SYSOUT_PATHS[kind]
    issues: list[str] = []
    fresh = b""
    for _ in range(12):
        if not path.is_file() or path.stat().st_size < offset:
            issues = ["Hercules SYSOUT device capture absent or truncated"]
            break
        # The pre-JES capture offset is enough: avoid a full Hercules file read.
        with path.open("rb") as stream:
            stream.seek(offset)
            fresh = stream.read()
        if kind == "punch":
            expected = (
                b"Q4CARD01\n"
                + b"Q4CARD02" + b" " * 71 + b"X\n"
                + b"Q4CARD03" + b" " * 71 + b"Y\n"
                + b"\n"
            )
            issues = ([] if fresh == expected else
                      [f"class-B punch mismatch: got {len(fresh)} bytes, "
                       f"expected {len(expected)}"])
        else:
            labels = (b"Q4FBA001", b"Q4FBA002", b"Q4FBA003")
            issues = []
            if any(fresh.count(label) != 1 for label in labels):
                issues.append("class-A printer card labels absent/duplicated")
            if b"Q4FBA001\n\nQ4FBA002" not in fresh:
                issues.append("ASA 0 double-space presentation missing")
            if b"X\x0cQ4FBA003" not in fresh:
                issues.append("ASA 1 form-feed presentation missing")
        if not issues:
            break
        time.sleep(1)
    capture = attempt / "sysout-capture.bin"
    capture.write_bytes(fresh)
    (attempt / "sysout-inspection.txt").write_text(
        f"kind={kind} offset={offset} capture={len(fresh)} bytes\n"
        + ("PASS" if not issues else "\n".join(issues)) + "\n",
        encoding="ascii")
    print(f"Hercules {kind} capture: {len(fresh)} new bytes; "
          + ("PASS" if not issues else "NOT VERIFIED"))
    return issues


def run(number: int, case: Path) -> int:
    if number not in CASES or not case.resolve().is_relative_to(REG.resolve()):
        raise ValueError("invalid QSAM case identity")
    kind, original, job, markers = CASES[number]
    profile_mode = execution_mode()
    mode = "private-diagnostic" if kind in FAULTS["KINDS"] else profile_mode
    if mode == "installed":
        check()
    if mode == "private-diagnostic":
        check_faults()
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
    # Native regressions default to bounded reads, including direct QSAM runs.
    # Explicit 0 retains the legacy reader; export so the Cambridge compiler agrees.
    os.environ.setdefault("BCPL_PRINTER_WINDOW_TRIAL", "1")
    printer_args = printer_args_for_attempt(attempt)
    print(f"QSAM case {number}, {mode}-mode, JES job {job}, evidence {attempt}", flush=True)
    (attempt / "mode.txt").write_text(mode + "\n", encoding="ascii")

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
                   generated[1] if len(generated) > 1 else None, mode)
    jcl = attempt / "native.jcl"
    with jcl.open("x", encoding="ascii", newline="\n") as out:
        out.write(deck)
    jcl.chmod(0o600)
    print(f"{mode.capitalize()}-mode MVS deck: {len(deck.splitlines())} cards", flush=True)
    offset: int | None = None
    if kind in SYSOUT_PATHS:
        path = SYSOUT_PATHS[kind]
        if not path.is_file():
            raise ValueError("missing Hercules capture before JES: " + str(path))
        offset = path.stat().st_size
        (attempt / "sysout-before.bytes").write_text(
            str(offset) + "\n", encoding="ascii")
    fault_cursors = FAULTS["cursors"](ROOT) if mode == "private-diagnostic" else None
    rc, response = invoke(
        [str(TOOLS / "mvs/submit-jcl"), "--timeout", "120",
         *printer_args, str(jcl)],
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
             "--verbose", *printer_args], attempt / "summary.txt", 30)
        if printer_args and "printer-window:" in summary:
            print("QSAM printer cursor invalid; inspect JES before retrying",
                  file=sys.stderr)
            return 1
        if summary_rc != 2:
            break
        time.sleep(2)
    report_rc, report = invoke(
        [str(TOOLS / "mvs/dump-report-for-job"), job_number,
         *printer_args],
        attempt / "report.txt", 45)
    print(f"JES job {job_number}: summary RC={summary_rc}, report RC={report_rc}")
    if summary_rc or report_rc:
        return 1
    errors = evidence(number, summary, report, mode)
    if fault_cursors is not None:
        errors += FAULTS["console_issues"](ROOT, attempt, fault_cursors, job_number, kind)
    if kind == "punch" and offset is not None and not errors:
        errors += maybe_resume_punch_writer(offset, attempt, job_number)
    if offset is not None:
        errors += check_sysout_capture(kind, offset, attempt)
    if errors:
        for error in errors:
            print("QSAM evidence NOT VERIFIED: " + error)
        return 1
    print(f"QSAM native case {number} PASS; job {job_number}")
    print("=== Regression result ===")
    print(f"TEST: {case.name}")
    print("RESULT: PASS")
    return 0


def synthetic_config():
    return {"mvs": {"hlq": "DR5", "batch_user": "TEST"},
              "datasets": {alias: {"dsn": dsn, "dsorg": "PO", "recfm": "FB",
                                   "lrecl": 80, "content_type": content}
                           for alias, dsn, content in (
                               ("BOOT_OBJ", "BCPL.BOOT.OBJ", "object"),
                               ("EXT_OBJ", "BCPL.EXT.OBJ", "object"),
                               ("EXT_MAC", "BCPL.EXT.MAC", "text"))}}


def check():
    query = load("prepare-q1-query.py")
    sample = query.time_helper().trailer_helper().sample_generated()
    config = synthetic_config()
    for number, (kind, _, _, _) in CASES.items():
        if kind in FAULTS["KINDS"]:
            continue
        reader = sample if kind == "full" else None
        source = prepare(kind, sample, reader, "source", config)
        installed = prepare(kind, sample, reader, "installed", config)
        if INSTALLED["transform"](source, kind, expected_steps(kind),
                                  "DR5.BCPL.BOOT.OBJ", "DR5.BCPL.EXT.OBJ",
                                  "DR5.BCPL.EXT.MAC") != installed:
            raise ValueError("installed adapter changed unexpectedly")
        # All GO DDs and independent verifier steps must remain unchanged.
        if installed.count(" INCLUDE OBJ(BCPLRGS)") != len(INSTALLED["application_links"](kind)):
            raise ValueError("installed registrar not selected")
        print(f"CHECK {number}: source={len(source.splitlines())}, installed={len(installed.splitlines())} cards")
    print("QSAM dual-mode synthetic JCL CHECK PASS (14 cases; no MVS)")
    return 0


def check_faults():
    query = load("prepare-q1-query.py")
    sample = query.time_helper().trailer_helper().sample_generated()
    for number in (198, 199, 200):
        kind, _, job, _ = CASES[number]
        deck = prepare(kind, sample, None, "private-diagnostic", synthetic_config())
        rows = deck.splitlines()
        if tuple(INSTALLED["STEP"].match(r).group(1) for r in rows
                 if INSTALLED["STEP"].match(r)) != LIFE:
            raise ValueError("private diagnostic step order changed")
        if not rows[0].startswith("//" + job + " "):
            raise ValueError("private diagnostic identity changed")
        if any("SYSOUT=B" in r or "SYSOUT=A" in r or "//EXTLIB" in r for r in rows):
            raise ValueError("private diagnostic cannot select devices or installed extensions")
        print(f"CHECK {number}: private diagnostic {len(rows)} cards; no MVS")
    return 0


def review_combined(attempt: Path) -> int:
    """Recheck retained case 200 evidence; no JES, no writes or resubmission."""
    attempt = attempt.resolve()
    case_root = (WORK / "200-qsam-combined-rollback-quarantine").resolve()
    if attempt.parent != case_root or not attempt.name.startswith("native-"):
        raise ValueError("review requires a saved case 200 native attempt")
    if (attempt / "mode.txt").read_text("ascii").strip() != "private-diagnostic":
        raise ValueError("saved attempt was not private-diagnostic mode")
    job = (attempt / "job-number.txt").read_text("ascii").strip()
    summary = (attempt / "summary.txt").read_text("latin-1")
    report = (attempt / "report.txt").read_text("latin-1")
    if not job.isdecimal() or re.findall(r"^JOB\s+(\d+)\s+DR5QCOM\s*$",
                                         summary, re.M) != [job]:
        raise ValueError("saved JES identity mismatch")
    issues = evidence(200, summary, report, "private-diagnostic")
    for name in FAULTS["LOGS"]:
        observed = FAULTS["job_markers"](
            (attempt / (name + ".diagnostic.txt")).read_text("latin-1"),
            job, "DR5QCOM", "combined")
        if observed != FAULTS["TRACE"]["combined"]:
            issues.append(name + ": saved job-bounded markers not verified")
    for issue in issues:
        print("QSAM evidence NOT VERIFIED: " + issue)
    if issues:
        return 1
    print(f"CASE 200 JOB {job}: RETAINED NATIVE EVIDENCE PASS (no JES submission)")
    return 0


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--review-combined":
        try:
            return review_combined(Path(sys.argv[2]))
        except (ValueError, OSError, UnicodeError, KeyError) as exc:
            print("QSAM evidence review FAILED: " + str(exc), file=sys.stderr)
            return 1
    if sys.argv[1:] in (["--check"], ["--check-faults"]):
        try:
            return check() if sys.argv[1:] == ["--check"] else check_faults()
        except (ValueError, OSError, UnicodeError, KeyError) as exc:
            print("QSAM CHECK FAILED: " + str(exc), file=sys.stderr)
            return 1
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
