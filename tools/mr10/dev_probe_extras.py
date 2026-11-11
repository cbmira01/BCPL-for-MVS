#!/usr/bin/env python3
"""Additional MR10 development-probe contracts and evidence checks.

This module does not invoke JES. Its caller supplies an explicit execution
selection, an isolated evidence directory and the completed job output.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ADDITIONAL = (
    "01-echo-test",
    "02-honors-thesis-and-mapstore/honors-thesis",
    "02-honors-thesis-and-mapstore/mapstore",
    "03-compile-richards-factorial/compile",
    "03-compile-richards-factorial/v14-intcode",
    "08-character-translation",
    "10-coroutines/compiler-probe",
    "10-coroutines/frame-layout-probe",
    "10-coroutines/fixed-stack-producer-consumer",
    "10-coroutines/resumeco-chain",
    "10-coroutines/create-delete-static-pool",
)

TRACE = {
    "10-coroutines/compiler-probe": ("COROUTINE COMPILER PROBE COMPILED",),
    "10-coroutines/frame-layout-probe": ("COROUTINE FRAME PROBE COMPILED",),
    "10-coroutines/fixed-stack-producer-consumer": tuple(
        line for i in range(1, 6)
        for line in (f"PRODUCER: {i}", f"CONSUMER: {i}")
    ),
    "10-coroutines/resumeco-chain": (
        "A START", "B START WITH 111", "ROOT GOT 222",
        "A RESUMED WITH 333", "ROOT GOT 444",
        "B RESUMED WITH 555", "ROOT GOT 666",
    ),
    "10-coroutines/create-delete-static-pool": (
        "CREATED 2", "LIST COUNT 3", "A RETURNED 11",
        "B RETURNED 21", "DELETED A", "LIST COUNT 2",
        "DELETED B", "LIST COUNT 1", "C RETURNED 31",
        "LIST COUNT 2", "DELETED C", "FINAL LIST COUNT 1",
    ),
}
ACCEPTED_COROUTINES = tuple(TRACE)

FACTORIAL = (1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800)
METADATA = re.compile(
    r"^(?:PROGRAM SIZE|PROGVEC CAPACITY|FREE STACK/WORK|STACKBASE|"
    r"STACKEND|GLOBAL CAPACITY|GLOBALS USED|HIGHEST GLOBAL)\s*="
)
CODE_RE = re.compile(r"EXECUTION CYCLES\s*=\s*\d+,\s*CODE\s*=\s*(-?\d+)")
JOB_RE = re.compile(r"(?m)^JOB\s+(\d+)\s*$")


class ExtraError(ValueError):
    """A candidate probe is invalid or its observed behavior deviates."""


def interpreter(root: Path, current: Path, row: dict[str, str]) -> Path:
    choice = row["interpreter"]
    if choice == "current":
        return current
    if choice not in ("v12", "v13", "v14"):
        raise ExtraError(f"unsupported historical ICINT selector: {choice}")
    path = (root / "mr10-kit-compiler/asm" / f"icint{choice}.asm").resolve()
    if not path.is_file() or not path.is_relative_to(root.resolve()):
        raise ExtraError(f"missing pinned {choice} interpreter: {path}")
    return path


def command(root: Path, row: dict[str, str], current: Path, jcl: Path,
            job: str, artifact_dir: Path) -> list[str]:
    ident = row["case_id"]
    if ident not in ADDITIONAL:
        raise ExtraError(f"{ident}: unsupported additional probe")
    if ident in ACCEPTED_COROUTINES:
        golden = f"mr10-kit-compiler/tests/10-coroutines/{ident.split('/')[-1]}.expected"
        if (row["verification"] != "ACCEPTED" or
                row.get("oracle") != "file:" + golden):
            raise ExtraError(f"{ident}: accepted coroutine golden contract required")
    elif row["verification"] != "UNVERIFIED":
        raise ExtraError(f"{ident}: expected unverified experimental contract")
    engine = row["engine"]
    if engine not in ("compile-and-run", "run-intcode"):
        raise ExtraError(f"unsupported engine for {ident}: {engine}")
    exe = root / "tools/mr10" / engine
    if not exe.is_file():
        raise ExtraError(f"missing MR10 engine: {exe}")
    cmd = [str(exe), "--results", "--jcl", str(jcl), "--job-name", job]
    if row["artifacts"] == "ocode,intcode":
        if engine != "compile-and-run":
            raise ExtraError(f"{ident}: invalid compiler artifacts for INTCODE test")
        cmd.extend(("--save-ocode", "--save-intcode", "--artifact-dir", str(artifact_dir)))
    elif row["artifacts"] != "none":
        raise ExtraError(f"{ident}: unsupported artifact declaration")
    if row["sysin"]:
        if engine != "run-intcode":
            raise ExtraError(f"{ident}: SYSIN declared for wrong engine")
        cmd.extend(("--sysin", str(root / row["sysin"])))
    if row["dd_bindings"]:
        if engine != "compile-and-run":
            raise ExtraError(f"{ident}: named DD binding not supported by {engine}")
        for item in row["dd_bindings"].split(";"):
            dd, file = item.split("=", 1)
            cmd.extend(("--dd", f"{dd}={root / file}"))
    cmd.extend((str(interpreter(root, current, row)), str(root / row["source"])))
    for module in row["modules"].split(";") if row["modules"] else []:
        cmd.append("+" + str(root / module))
    return cmd


def program_lines(output: str) -> list[str]:
    lines = [line.strip() for line in output.splitlines()]
    starts = [i for i, line in enumerate(lines) if line == "INTCODE SYSTEM ENTERED"]
    if len(starts) != 1:
        raise ExtraError(f"expected one final ICINT banner, got {len(starts)}")
    codes = [i for i, line in enumerate(lines) if CODE_RE.fullmatch(line)]
    if len(codes) != 1 or codes[0] <= starts[0]:
        raise ExtraError("expected one final ICINT completion code")
    return [line for line in lines[starts[0]+1:codes[0]]
            if line and not METADATA.match(line)]


def exact_lines(actual: list[str], expected: list[str], ident: str) -> None:
    if actual != expected:
        raise ExtraError(f"{ident}: semantic output mismatch: expected {expected!r}, got {actual!r}")


def check_artifacts(root: Path, ident: str, row: dict[str, str],
                    artifact_dir: Path) -> dict[str, str]:
    if row["artifacts"] != "ocode,intcode":
        return {}
    stem = Path(row["source"]).stem
    found = {}
    for kind, suffix in (("ocode", ".ocode"), ("intcode", ".intcode")):
        path = artifact_dir / (stem + suffix)
        if not path.is_file() or not path.read_text(encoding="ascii").strip():
            raise ExtraError(f"{ident}: missing or empty generated {kind} artifact")
        content = path.read_text(encoding="ascii")
        if ident in ("10-coroutines/compiler-probe", "10-coroutines/frame-layout-probe"):
            historical = root / "mr10-kit-compiler/tests/10-coroutines/evidence" / (stem + suffix)
            if not historical.is_file():
                raise ExtraError(f"{ident}: historical structural evidence missing")
            # Whitespace wraps in the 80-column JCL capture may vary.
            if content.split() != historical.read_text(encoding="ascii").split():
                raise ExtraError(f"{ident}: generated {kind} differs from archived structural evidence")
        elif kind == "ocode":
            if "GLOBAL" not in content or "STACK" not in content:
                raise ExtraError(f"{ident}: generated OCODE missing structure markers")
        else:
            if "G1L" not in content or not content.rstrip().endswith("Z"):
                raise ExtraError(f"{ident}: generated INTCODE missing entry/trailer")
        found[kind] = str(path.relative_to(root))
    return found


def assess(root: Path, row: dict[str, str], output: str, returncode: int,
           artifact_dir: Path) -> dict[str, object]:
    ident = row["case_id"]
    if ident not in ADDITIONAL:
        raise ExtraError(f"not an additional probe: {ident}")
    if returncode != 0:
        raise ExtraError(f"{ident}: MR10 engine RC={returncode}")
    if len(JOB_RE.findall(output)) != 1:
        raise ExtraError(f"{ident}: missing/ambiguous JES job number")
    codes = CODE_RE.findall(output)
    if len(codes) != 1 or codes[0] != row["expected_code"]:
        raise ExtraError(f"{ident}: interpreted CODE expected {row['expected_code']}, got {codes}")
    lines = program_lines(output)
    if ident == "01-echo-test":
        expected = [line for line in (root / row["sysin"]).read_text(encoding="ascii").splitlines() if line]
        exact_lines(lines, expected, ident)
    elif ident == "02-honors-thesis-and-mapstore/honors-thesis":
        expected = [f"F({i}) = {value}" for i, value in enumerate(FACTORIAL, 1)]
        exact_lines(lines, expected, ident)
    elif ident == "02-honors-thesis-and-mapstore/mapstore":
        upper = output.upper()
        if "MAPSTORE" not in upper or "X38" not in upper:
            raise ExtraError(f"{ident}: expected MAPSTORE and invalid X38 diagnostic")
    elif ident in ("03-compile-richards-factorial/compile",
                   "03-compile-richards-factorial/v14-intcode"):
        expected = [f"F({i}), = {value}" for i, value in enumerate(FACTORIAL, 1)]
        exact_lines(lines, expected, ident)
    elif ident == "08-character-translation":
        if len(lines) < 6 or lines[:6] != [
            "BACKSLASH OPERATORS", "LOGICAL OR  = -1", "LOGICAL AND = -1",
            "NOT EQUAL   = -1", "LOGICAL NOT = -1", "RDCH CHARACTER CODES"]:
            raise ExtraError(f"{ident}: wrong operator diagnostics")
        values = lines[6:]
        if len(values) < 9 or any(not v.isdecimal() or not 0 <= int(v) <= 255 for v in values):
            raise ExtraError(f"{ident}: expected numeric RDCH byte values")
    elif ident in TRACE:
        exact_lines(lines, list(TRACE[ident]), ident)
    else:
        raise ExtraError(f"{ident}: no semantic oracle")
    artifacts = check_artifacts(root, ident, row, artifact_dir)
    return {"status": "OBSERVED", "reason": "source-derived candidate oracle matched; UNVERIFIED",
            "interpreted_code": int(codes[0]), "artifacts": artifacts}


STEP_RE = re.compile(r"^([A-Z0-9]+)\s+([A-Z0-9]+)\s+RC=(\d{4})$")


def capture_jes(root: Path, row: dict[str, str], job_number: str,
                expected_job_name: str, folder: Path, slug: str) -> dict[str, object]:
    """Preserve real JES evidence and require a complete RC=0 job.

    This reads only the printer output; it never submits a job. The negative
    MAPSTORE test still expects a normal JES step RC, with interpreted CODE=-1.
    """
    printer = root / "mvs-state/prt/prt00e.txt"
    summary_tool = root / "tools/mvs/job-summary"
    report_tool = root / "tools/mvs/dump-report-for-job"
    if any(not path.is_file() for path in (printer, summary_tool, report_tool)):
        raise ExtraError("JES evidence tools or printer log are missing")
    summary = subprocess.run([str(summary_tool), str(job_number), "--file", str(printer),
                              "--max-rc", "0"], cwd=root, capture_output=True,
                             text=True, check=False)
    report = subprocess.run([str(report_tool), str(job_number)], cwd=root,
                            capture_output=True, text=True, check=False)
    summary_path = folder / f"{slug}-jes-summary.txt"
    report_path = folder / f"{slug}-jes-report.txt"
    summary_path.write_text(summary.stdout + summary.stderr, encoding="utf-8")
    if report.stdout:
        report_path.write_text(report.stdout, encoding="utf-8")
    if summary.returncode or report.returncode:
        raise ExtraError(f"JES report utilities failed: summary RC={summary.returncode}, "
                         f"report RC={report.returncode}")
    lines = summary.stdout.splitlines()
    if not lines or lines[0].strip() != f"JOB {job_number}  {expected_job_name}":
        raise ExtraError("JES report job identity mismatch")
    if "JOB RESULT: SUCCESS" not in lines or "HIGHEST RC: 0000" not in lines:
        raise ExtraError("JES did not report all steps successful at RC=0000")
    steps = [m.groups() for line in lines if (m := STEP_RE.fullmatch(line.strip()))]
    if not steps or any(code != "0000" for _, _, code in steps):
        raise ExtraError("JES step return codes missing or nonzero")
    names = [name for name, _, _ in steps]
    if row["engine"] == "run-intcode":
        required = {"ASM", "LKED", "GO"}
        expected_codes = [int(row["expected_code"])]
    else:
        required = {"ASM", "LKED", "STGSYNI", "STGTRNI", "STGCGI",
                    "STGBLIB", "STGICLIB", "RUN"}
        count = 1 + (len(row["modules"].split(";")) if row["modules"] else 0)
        if count == 1:
            required.update(("COMP", "CG"))
        else:
            required.update(f"COMP{i:02d}" for i in range(1, count+1))
            required.update(f"CG{i:02d}" for i in range(1, count+1))
        expected_codes = [0] * (2 * count + 1)
    if not required.issubset(set(names)) or len(names) != len(set(names)):
        raise ExtraError(f"JES step structure missing, duplicated or unexpected: {names}")
    phase_codes = [int(v) for v in CODE_RE.findall(report.stdout)]
    if phase_codes != expected_codes:
        raise ExtraError(f"JES interpreted phase codes: {phase_codes!r} != {expected_codes!r}")
    return {"jes_summary": str(summary_path.relative_to(root)),
            "jes_report": str(report_path.relative_to(root)),
            "jes_step_codes": [{"step": name, "program": prog, "rc": int(rc)}
                               for name, prog, rc in steps],
            "jes_phase_codes": phase_codes}
