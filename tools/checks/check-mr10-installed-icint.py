#!/usr/bin/env python3
"""Offline regression for MR10 interpreter acquisition modes; submits no jobs."""
from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "tools/mr10/compile-and-run-core.py"
spec = importlib.util.spec_from_file_location("mr10_compile_core", PATH)
assert spec is not None and spec.loader is not None
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

def run():
    src = ROOT / "mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl"
    asm = ROOT / "mr10-kit-compiler/asm/icintv19.asm"
    kwargs = dict(sources=[src], job_name="TSTICINT", listing="light",
                  named_dds=[], save_ocode=True, save_intcode=True)
    legacy = core.build_deck(interpreter=asm, **kwargs)
    installed = core.build_deck(interpreter=None,
                                installed_load="HERC02.BCPL.MR10KIT.LOAD", **kwargs)
    assert "//ASM      EXEC PGM=IFOX00" in legacy
    assert "//LKED     EXEC PGM=IEWL" in legacy
    assert "EXEC PGM=RUNMOD" in legacy
    assert "&&GOSET" in legacy
    assert "//ASM      EXEC" not in installed
    assert "//LKED     EXEC" not in installed
    assert "EXEC PGM=RUNMOD" not in installed
    assert installed.count("EXEC PGM=ICINT19") == 3
    assert installed.count("DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR") == 3
    for token in ("STGSYNI", "STGTRNI", "STGCGI", "STGBLIB",
                  "STGICLIB", "SVOC", "SVIN", "COMP", "CG", "RUN"):
        assert token in installed, token
    assert "SAVE INTCODE: YES" in installed
    assert "ASM       BUILD" not in installed
    # One source and seven +MODULE operands exercise the TRNILRG command form.
    items = ["trn0", "+trn1", "+trn2", "+trn3",
             "+trn4", "+trn5", "+trn6"]
    args = core.make_parser().parse_args(
        ["--installed-icint", "MR10_LOAD", *items]
    )
    core.normalize_installed_positionals(args)
    assert args.interpreter is None
    assert args.source == "trn0"
    assert args.modules == items[1:]
    assert len(core.parse_modules(args.modules)) == 6
    # The original two-position argument mode must remain unchanged.
    old_args = core.make_parser().parse_args(["icint.asm", "example.bcpl"])
    assert old_args.interpreter == "icint.asm"
    assert old_args.source == "example.bcpl"
    print("PASS: legacy and installed MR10 compile JCL modes; no MVS jobs")

if __name__ == "__main__":
    run()
