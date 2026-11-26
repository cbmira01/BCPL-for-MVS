#!/usr/bin/env python3
"""Numbered read-only installed BCPLRGS regressions, derived from the full probe."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DRIVER = runpy.run_path(str(ROOT / "tools/checks/run-dr5-registrar-fix.py"))
require, run, submit = (DRIVER[x] for x in ("require", "run", "submit"))
CASE_NAMES = {
    194: "194-registrar-multiple-dependencies",
    195: "195-registrar-dependency-ordinal",
    196: "196-registrar-structural-preflight",
    197: "197-registrar-dependency-versions",
}
ORACLES = {
    194: [(1, 0), (2, 1014), (3, 1010), (17, 1009), (18, 0)],
    195: [(1, 0), (4, 1012)],
    196: [(5, 1004), (6, 1004), (7, 1005), (8, 1005), (9, 1006)],
    197: [(10, 1014), (11, 1014), (12, 1014), (13, 1011),
          (14, 1011), (15, 1014), (16, 1014)],
}
# Reduce the effective C descriptor to exactly one dependency. The
# second record still exists in storage but lies outside its linked span.
SINGLE = """         MVC   DESCC+12(4),=F'72'
         MVC   DESCC+40(4),=F'1'
         L     3,=A(DEP2)
         ST    3,PAIR+20
"""


def source_for(number, original):
    require(number in CASE_NAMES, "unknown registrar case")
    first = "* 1: TWO DISTINCT DEPENDENCIES;"
    finish = "         WTO   'DR5 REGISTRAR 18 CASES PASS'\n"
    require(original.count(first) == original.count(finish) == 1,
            "shared probe boundaries changed")
    head, tail = original.split(first, 1)
    middle, end = (first + tail).split(finish, 1)
    matches = list(re.finditer(r"(?m)^\* (\d+): ", middle))
    require([int(m[1]) for m in matches] == list(range(1, 19)),
            "shared probe assertion identities changed")
    blocks = {i + 1: middle[m.start():matches[i + 1].start()
                            if i + 1 < len(matches) else len(middle)]
              for i, m in enumerate(matches)}
    if number == 194:
        body = "".join(blocks[n] for n in (1, 2, 3, 17, 18))
    elif number == 195:
        # B has ordinal 1; its index must not be compared as byte offset 8.
        body = SINGLE + "         MVC   DEP1(8),=CL8'TESTB'\n"
        body += blocks[1].replace("* 1: TWO DISTINCT DEPENDENCIES; ALL THREE EXPORTS PUBLISHED.",
                                  "* 1: SINGLE DEPENDENCY ON ORDINAL ONE; ALL EXPORTS.")
        # When C is first, update its end field after copying FORWARD.
        body += blocks[4].replace("         MVC   PAIR(24),FORWARD\n",
                                  "         MVC   PAIR(24),FORWARD\n"
                                  "         L     3,=A(DEP2)\n"
                                  "         ST    3,PAIR+4\n")
    elif number == 196:
        body = "         MVC   PAIR(24),FORWARD\n"
        body += "".join(blocks[n] for n in range(5, 10))
    else:
        # Single earlier dependency on A: duplicate or ordinal bugs
        # cannot mask the version validation being tested.
        body = SINGLE + "".join(blocks[n] for n in range(10, 17)).replace(
            "DEP2", "DEP1").replace("=CL8'TESTB'", "=CL8'TESTA'")
    marker = f"         WTO   'DR5 REGISTRAR {number} PASS'\n"
    source = head + body + marker + end
    actual = [(int(n), int(status or 0)) for n, status in re.findall(
        r"LA    6,(\d+)\n         (?:LA    7,(\d+)|SR    7,7)\n"
        r"         BAL   8,CHECK", source)]
    require(actual == ORACLES[number], "numbered registrar oracle mismatch")
    require(source.count("         BAL   8,FINAL") ==
            sum(status == 0 for _, status in actual), "missing finalization check")
    require("DR5 REGISTRAR 18 CASES PASS" not in source, "incorrect success marker")
    DRIVER["TRAIL"]["checked_asm"](source, f"registrar {number}")
    return source


def fixture(number, directory):
    wanted = ROOT / "tests/runtime-extensions" / CASE_NAMES[number]
    require(directory.resolve() == wanted.resolve() and wanted.is_dir(),
            "wrong registrar fixture directory")
    require((wanted / "registrar-native.txt").read_text("ascii").strip() == str(number),
            "wrong registrar fixture marker")
    return source_for(number, DRIVER["PROBE"].read_text("ascii"))


def deck_for(config, number, source, redact=True):
    name, cards, steps = DRIVER["probe_cards"](
        config, True, redact, source=source, job_name=f"RG{number}R")
    require(steps == [("ASMT", "IFOX00"), ("LKED", "IEWL"), ("GO", None)],
            "incorrect numbered probe steps")
    require(" INCLUDE OBJ(BCPLRGS)\n" in cards and "&&RGPRIV" not in cards
            and source.rstrip("\n") in cards, "incorrect installed linkage")
    return name, cards, steps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", type=int, choices=CASE_NAMES)
    parser.add_argument("directory", type=Path)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--run", action="store_true")
    args = parser.parse_args()
    number = args.number
    try:
        source = fixture(number, args.directory)
        if args.check:
            config = {"mvs": {"hlq": "DR5", "batch_user": "TEST"},
                      "datasets": {"BOOT_OBJ": {"dsn": "BCPL.BOOT.OBJ",
                                                "dsorg": "PO", "recfm": "FB",
                                                "lrecl": 80, "content_type": "object"}}}
            deck_for(config, number, source)
            print(f"Registrar {number} CHECK PASS ({len(ORACLES[number])} assertions)")
            return 0
        env = dict(os.environ)
        require(env.get("BCPL_RUNTIME_PDS", "1") == "1"
                and env.get("BCPL_RUNTIME_LIBRARY") == "OBJ"
                and env.get("BCPL_RUNTIME_CANDIDATE", "0") == "0"
                and not env.get("BCPL_RUNTIME_CANDIDATE_MEMBER"),
                "numbered registrar requires production OBJ")
        os.umask(0o077)
        location = env.get("BCPL_REGISTRAR_LOG_DIR")
        parent = Path(location) if location else ROOT / "workarea/registrar-regressions"
        require(parent.is_absolute(), "registrar evidence path must be absolute")
        parent.mkdir(parents=True, exist_ok=True)
        folder = Path(tempfile.mkdtemp(prefix=f"registrar-{number}-", dir=parent))
        result = {"status": "FAIL", "case": number,
                  "source_sha256": hashlib.sha256(source.encode("ascii")).hexdigest(),
                  "oracles": ORACLES[number]}
        try:
            result["git_head"] = run(["git", "rev-parse", "HEAD"],
                                     folder / "revision.log", env).strip()
            config = DRIVER["CORE"]["load_config"]()
            name, cards, steps = deck_for(config, number, source, redact=False)
            deck = folder / (name + ".jcl")
            deck.write_text(cards, encoding="ascii")
            (folder / "probe.asm").write_text(source, encoding="ascii")
            run(["tools/reconstruction/jes-idle", "--live"], folder / "idle.log", env)
            job, _ = submit(folder, name, deck, steps, env)
            result.update(status="PASS", job=job, assertions=len(ORACLES[number]))
            print(f"{name} JOB {job} PASS ({len(ORACLES[number])} registrar assertions)")
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            result["reason"] = str(exc)
        (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print("Evidence: " + str(folder))
        if result["status"] != "PASS":
            print(result["reason"])
            return 1
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"registrar {number}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
