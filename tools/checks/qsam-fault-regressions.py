"""Private numbered QSAM fault diagnostics; no installed writes or devices."""
from pathlib import Path
import re
import time

KINDS = ("rollback", "getmain", "combined")
JOBS = {"rollback": "Q5RBFIN", "getmain": "Q5RGM", "combined": "DR5QCOM"}
TRACE = {
    "rollback": (
        "Q5R:E:00000001:00000002:00000002:00000001",
        "Q5R:L:00000001:00000001:00000001:00000001:00000000",
        "Q5R:P:POST-CLEAN", "Q5R:R:ROLL-RETURN", "Q5R:T:CORE-EPILOGUE",
        "Q5R:X:00000000:00000000:00000000:00000000:00000000",
        "Q5R:P:POST-CLEAN",
    ),
    "getmain": ("Q5RGM:REAL:GM1024-RC4:ALL-FREED", "DR5G:FINAL:ZERO"),
    "combined": ("DR5C:CLOSE:INJECTED", "DR5C:PRIMARY:11:QUAR:1",
                 "DR5C:FINAL:QUAR:1:RC8"),
}
LOGS = ("3033.log", "hardcopy.log")


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError("changed diagnostic assembler anchor: " + old[:60])
    return source.replace(old, new, 1)


def final_check(source, kind):
    # QFSTAT is reloaded after WTO; the production result is untouched.
    if kind == "getmain":
        checks = (("QFSTAT", 0), ("QSLIVE", 0), ("QSDCBS", 0),
                  ("QSSTAGES", 0), ("QSQUAR", 0))
        marker = TRACE[kind][-1]
        lines = []
    else:
        checks = (("QFSTAT", 8), ("QSLIVE", 1), ("QSDCBS", 1),
                  ("QSSTAGES", 0), ("QSQUAR", 1))
        marker = TRACE[kind][-1]
        lines = ["         L     6,=A(Q5DCONC)",
                 "         CLC   0(4,6),=F'1'",
                 "         BNE   D5FEXIT",
                 "         L     6,=A(Q5DCALL)",
                 "         CLC   0(4,6),=F'1'",
                 "         BNE   D5FEXIT",
                 "         LA    4,QS01",
                 "         CLC   0(4,4),=F'4'",
                 "         BNE   D5FEXIT",
                 "         CLC   4(4,4),=F'0'",
                 "         BNE   D5FEXIT",
                 "         CLC   12(4,4),=F'0'",
                 "         BNE   D5FEXIT"]
    for field, value in checks:
        lines += [f"         CLC   {field}(4),=F'{value}'",
                  "         BNE   D5FEXIT"]
    lines += [f"         WTO   '{marker}'", "D5FEXIT  L     15,QFSTAT"]
    return once(source, "QFEXIT   L     15,QFSTAT\n",
                "QFEXIT   DS    0H\n" + "\n".join(lines) + "\n")


def combined_overlay(source):
    # Q01 stage refusal is deliberately injected AFTER actual OPEN.
    source = once(source, "         GETMAIN RC,LV=1024\n",
                  """         CLC   QCNAME(8),=CL8'Q01'
         BNE   D5CGET
         CLC   D5ONCE(4),=F'0'
         BNE   D5CGET
         LA    0,1
         ST    0,D5ONCE
         B     QCSTFAIL
D5CGET   GETMAIN RC,LV=1024
""")
    source = once(source, "QCERRPRI DC   F'0'\n",
                  "QCERRPRI DC   F'0'\nD5ONCE   DC   F'0'\n")
    # Count even attempted close calls on the unpublished second slot.
    source = once(source, "         ST    4,QSCCUR\n",
                  """         ST    4,QSCCUR
         LA    0,QS01
         CR    4,0
         BNE   D5CCHK
         L     0,Q5DCALL
         A     0,=F'1'
         ST    0,Q5DCALL
D5CCHK   DS    0H
""")
    source = once(source, "QSCEXEC  ST    2,QSCDCB\n         CLOSE ((2))\n",
                  """QSCEXEC  ST    2,QSCDCB
         CLOSE ((2))
* Never synthesize a successful OS CLOSE or override a real error.
         LTR   15,15
         BNZ   D5CNORM
         L     4,QSCCUR
         LA    0,QS01
         CR    4,0
         BNE   D5CNORM
         CLC   4(4,4),=F'0'
         BNE   D5CNORM
         CLC   12(4,4),=F'0'
         BNE   D5CNORM
         CLC   Q5DCONC(4),=F'0'
         BNE   D5CNORM
         LA    0,1
         ST    0,Q5DCONC
         WTO   'DR5C:CLOSE:INJECTED'
         LA    15,4
D5CNORM  DS    0H
""")
    source = once(source, "QSCDCB   DC    F'0'\n",
                  "QSCDCB   DC    F'0'\nQ5DCONC  DC    F'0'\nQ5DCALL  DC    F'0'\n")
    # Require the real cleanup path to have returned -14, preserving -11.
    source = once(source, "         BALR  14,15\n         L     7,QCERRPRI\n",
                  """         BALR  14,15
         C     15,=F'-14'
         BNE   D5CPRI
         CLC   QCERRPRI(4),=F'-11'
         BNE   D5CPRI
         CLC   QSQUAR(4),=F'1'
         BNE   D5CPRI
         CLC   QSLIVE(4),=F'2'
         BNE   D5CPRI
         CLC   QSDCBS(4),=F'2'
         BNE   D5CPRI
         CLC   QSSTAGES(4),=F'1'
         BNE   D5CPRI
         L     4,QCCUR
         CLC   0(4,4),=F'4'
         BNE   D5CPRI
         CLC   4(4,4),=F'0'
         BNE   D5CPRI
         WTO   'DR5C:PRIMARY:11:QUAR:1'
D5CPRI   L     7,QCERRPRI
""")
    return final_check(source, "combined")


def prepare(kind, generated, card, obj, load, ext):
    campaign = load("prepare-q1-campaign.py")
    baseline = (ext / "bcplqsam.asm").read_text("ascii")
    template = campaign.make_deck("finish", generated, card, obj)
    if kind == "rollback":
        return load("prepare-q5-rollback-finish.py").instrument_deck(template, baseline)
    rows = template.splitlines()
    start, end = campaign.source_span(rows, "ASMQ")
    if rows[start:end] != baseline.splitlines():
        raise ValueError("private ASMQ does not match controlled baseline")
    source = (final_check(load("prepare-q5-real-getmain.py").instrument(baseline),
                          "getmain") if kind == "getmain" else combined_overlay(baseline))
    load("prepare-q5-returned-close.py").validate_cards(source)
    rows[start:end] = source.splitlines()
    job = JOBS[kind]
    rows[0] = once(rows[0], "//Q16FIN ", f"//{job} ")
    campaign.replace_one(rows, " NAME Q16FIN(R)", f" NAME {job}(R)")
    campaign.replace_one(rows, "//SYSLMOD  DD  DSN=&&Q1LOAD(Q16FIN),",
                         f"//SYSLMOD  DD  DSN=&&Q1LOAD({job}),")
    return campaign.verify(rows, job, "finish")


def registrar_issues(summary, report):
    """JES message sections precede IFOX/IEWL output; require both exact forms."""
    jobs = re.findall(r"^JOB\s+(\d+)\s+DR5QCOM\s*$", summary, re.M)
    if len(jobs) != 1:
        return ["combined registrar message: ambiguous JES identity"]
    marker = "BCPLREG 2001 FINALIZER RETURNED NONZERO"
    rows = [r.strip() for r in report.replace("\f", "").splitlines()]
    wto = re.compile(r"(?:\d{1,2}\.\d{2}\.\d{2}\s+)?JOB\s+"
                     + re.escape(jobs[0]) + r"\s+\+" + re.escape(marker))
    issues = []
    if sum(bool(wto.fullmatch(r)) for r in rows) != 1:
        issues.append("combined job-attributed registrar WTO missing/duplicated")
    if rows.count(marker) != 1:
        issues.append("combined standalone registrar message missing/duplicated")
    return issues


def cursors(root):
    offsets = {}
    for name in LOGS:
        path = root / "mvs-state/log" / name
        stat = path.stat()
        offsets[name] = (stat.st_dev, stat.st_ino, stat.st_size)
    return offsets


def job_markers(text, job, name, kind):
    rows = text.splitlines()
    ident = rf"\bJOB\s+{re.escape(job)}\s+"
    start = [i for i, row in enumerate(rows) if re.search(
        ident + rf"\$HASP373\s+{name}\s+STARTED\b", row)]
    end = [i for i, row in enumerate(rows) if re.search(
        ident + rf"\$HASP395\s+{name}\s+ENDED\b", row)]
    if len(start) != 1 or len(end) != 1 or start[0] >= end[0]:
        return None
    prefix = {"rollback": "Q5R:", "getmain": "Q5RGM:|DR5G:",
              "combined": "DR5C:"}[kind]
    pattern = re.compile(ident + rf"\+((?:{prefix}).*)\s*$")
    return tuple(m.group(1).strip() for row in rows[start[0]:end[0]+1]
                 if (m := pattern.search(row)))


def console_issues(root, attempt, offsets, job, kind):
    issues = []
    for name, (device, inode, offset) in offsets.items():
        path = root / "mvs-state/log" / name
        markers = None
        for _ in range(15):
            with path.open("rb") as stream:
                import os
                stat = os.fstat(stream.fileno())
                if (stat.st_dev, stat.st_ino) != (device, inode) or stat.st_size < offset:
                    raise ValueError("diagnostic console rotated/truncated: " + name)
                stream.seek(offset)
                raw = stream.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise ValueError("diagnostic console window exceeds 8 MiB")
            text = raw.decode("latin-1")
            markers = job_markers(text, job, JOBS[kind], kind)
            if markers is not None:
                break
            time.sleep(1)
        (attempt / (name + ".diagnostic.txt")).write_text(text, encoding="latin-1")
        if markers != TRACE[kind]:
            issues.append(f"{name}: expected {TRACE[kind]!r}, got {markers!r}")
        else:
            print(f"{name}: JOB {job} diagnostic markers PASS")
    return issues
