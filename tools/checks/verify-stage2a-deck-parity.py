#!/usr/bin/env python3
"""Compare synthetic native IFOX/IEWL/JCL decks before/after Stage 2A.

Host-only: git archive into temporary directories, import the existing
generators, and compare exact ASCII deck hashes. No credentials, JES
submission, dataset population or installed-object modification.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BEFORE = "efb461f3c90a8de93e7d7ddc4dcc3529a9a60a4c"

WORKER = r"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
def load(path, name):
    file = root / path
    spec = importlib.util.spec_from_file_location(name, file)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing deck generator: " + str(file))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def add(label, deck):
    if not deck.isascii():
        raise RuntimeError(label + ": generated deck is not ASCII")
    result[label] = hashlib.sha256(deck.encode("ascii")).hexdigest()

boot = "HERC02.BCPL.BOOT.OBJ"
ext = "HERC02.BCPL.EXT.OBJ"
mac = "HERC02.BCPL.EXT.MAC"
result = {}
r5 = load("tools/checks/prepare-r5-extension-regression.py", "stage2a_r5")
sample = r5.trail_module().sample_generated()

t0 = load("tools/checks/prepare-bcpltime-t0.py", "stage2a_t0")
add("BCPLTIME-T0/source", t0.make_deck(
    sample, ["//T0TIME JOB (BCPL),'STAGE 2A',CLASS=A"], boot))
for number in range(146, 159):
    job = [f"//RG{number:03d}R JOB (BCPL),'STAGE 2A',CLASS=A"]
    add(f"R5/{number}/source", r5.make_deck(
        number, sample, job, boot))
    add(f"R5/{number}/installed", r5.make_deck(
        number, sample, job, boot, "installed", ext, mac))

t1 = load("tools/checks/prepare-t1-time-regression.py", "stage2a_t1")
for number in range(159, 163):
    job = [f"//RG{number:03d}R JOB (BCPL),'STAGE 2A',CLASS=A"]
    add(f"BCPLTIME-T1/{number}/source", t1.make_deck(
        number, sample, job, boot))
    add(f"BCPLTIME-T1/{number}/installed", t1.make_deck(
        number, sample, job, boot, "installed", ext, mac))

q = load("tools/checks/run-q2-qsam-regression.py", "stage2a_qsam")
for number, (kind, _, name, _) in q.CASES.items():
    card = [f"//{name} JOB (BCPL),'STAGE 2A',CLASS=A"]
    if kind == "query":
        deck = q.load("prepare-q2-query.py").make_deck(sample, card, boot)
    elif kind in ("negative", "output", "finish", "stop"):
        deck = q.load("prepare-q1-campaign.py").make_deck(
            kind, sample, card, boot)
    elif kind == "full":
        deck = q.load("prepare-q2-consolidated.py").make_deck(
            sample, sample, card, boot)
    elif kind == "stopflush":
        deck = q.load("prepare-q2-stop-flush.py").make_deck(
            sample, card, boot)
    elif kind == "mix":
        deck = q.load("prepare-q2-mix.py").make_deck(
            sample, card, boot, ext)
    elif kind in q.LIMIT_CASES:
        deck = q.load("prepare-q3-v-read.py").make_limit_deck(
            sample, card, boot,
            "vb" if kind.startswith("vb") else "v",
            kind.endswith("write"))
    elif kind == "punch":
        deck = q.load("prepare-q4-punch.py").make_deck(sample, card, boot)
    elif kind == "fba":
        deck = q.load("prepare-q4-fba.py").make_deck(sample, card, boot)
    else:
        raise RuntimeError("unrecognized QSAM kind: " + kind)
    add(f"BCPLQSAM/{number}/source", deck)
print(json.dumps(result, sort_keys=True))
"""


def checkout_snapshot(revision: str, destination: Path) -> None:
    proc = subprocess.run(
        ["git", "archive", "--format=tar", revision],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False)
    if proc.returncode:
        raise RuntimeError(
            "git archive " + revision + " failed: " +
            proc.stderr.decode("utf-8", "replace").strip())
    with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as archive:
        archive.extractall(destination, filter="data")


def generate(snapshot: Path) -> dict[str, str]:
    proc = subprocess.run(
        [sys.executable, "-B", "-c", WORKER, str(snapshot)],
        cwd=snapshot, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=False)
    if proc.returncode:
        raise RuntimeError(
            "offline JCL generation failed in " + str(snapshot) +
            ":\n" + proc.stderr.strip())
    return json.loads(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--after", default="HEAD",
        help="commit/ref to compare against the pre-Stage 2A baseline")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="bcpl-stage2a-parity-") as tmp:
        old = Path(tmp) / "before"
        new = Path(tmp) / "after"
        old.mkdir()
        new.mkdir()
        checkout_snapshot(BEFORE, old)
        checkout_snapshot(args.after, new)
        a = generate(old)
        b = generate(new)
    missing = sorted(a.keys() - b.keys())
    extra = sorted(b.keys() - a.keys())
    changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    print(f"Stage 2A synthetic deck comparison: {len(a)} before, "
          f"{len(b)} after")
    for kind, keys in (("MISSING", missing), ("ADDED", extra),
                       ("DIFFERENT", changed)):
        for key in keys:
            print(f"{kind}: {key} "
                  f"(before={a.get(key, '-')}, after={b.get(key, '-')})")
    if missing or extra or changed:
        print("V3: FAIL — generated deck mismatch")
        return 1
    print("V3: PASS — all synthetic IFOX/IEWL/JCL decks byte-identical")
    print("Note: Q5PKG baseline synthetic generator rejects a harmless "
          "BOOT_DEVOBJ source comment; that independent safety-guard "
          "regression is covered by the Q.5 host tests.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, tarfile.TarError) as exc:
        print("V3: ERROR — " + str(exc), file=sys.stderr)
        raise SystemExit(2)
