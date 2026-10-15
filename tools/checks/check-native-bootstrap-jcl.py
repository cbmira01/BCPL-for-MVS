#!/usr/bin/env python3
"""Offline M3 native bootstrap allocation and generated-JCL contract check."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
script = ROOT / "tools/native/build-cambridge"
spec = importlib.util.spec_from_file_location("native_bootstrap", script)
if spec is None or spec.loader is None:
    # Source filename has no .py extension: use the Python source loader.
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader("native_bootstrap", str(script))
    spec = importlib.util.spec_from_loader("native_bootstrap", loader)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
config = module.core.load_config()
deck = module.build_deck(config, redact_password=True)
datasets = config["datasets"]
full = lambda key: module.core.full_dsn(config, datasets[key])
assert "HERC02.BCPL.SOURCE" not in deck
assert "HERC02.BCPL.INTCODE" not in deck
assert "HERC02.BCPL.LOAD" not in deck
assert "BCPL.CAMBRIDG." not in deck
assert "//ASM      EXEC" not in deck
assert "//LKED     EXEC" not in deck
assert deck.count("EXEC PGM=ICINT19") == len(module.CAMBRIDGE_UNITS) * 2
for member in ("SYNI", "CGI", "BLIBI", "ICLIB"):
    assert f"{full('MR10_SOURCE')}({member})" in deck
assert f"{full('NATIVE_INTCODE')}(TRNILRG)" in deck
assert f"{full('NATIVE_INTCODE')}(CAMBCOMP)" in deck
assert f"{full('MR10_LOAD')},DISP=SHR" in deck
for src, target in module.CAMBRIDGE_UNITS:
    assert f"{full('NATIVE_SOURCE')}({src})" in deck
    assert f"{full('NATIVE_INTCODE')}({target})" in deck
print("PASS: M3 native bootstrap JCL uses only NATIVE_* and MR10_* PDSes")
