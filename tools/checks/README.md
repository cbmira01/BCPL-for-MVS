# Pre-flight checks

This directory contains small, durable validators used while reconstructing
BCPL for MVS.  They are intentionally separate from the historical source and
from the compiler/runtime product itself.

## Breadcrumb for future work

Before inventing an ad-hoc checker in a temporary execution environment, look
here first.  If a scratch validation script proves useful more than once, or
materially improves the accuracy of generated/edited code, promote it into this
directory and document it here.

The purpose is to preserve accumulated engineering discipline across sessions
and execution environments.

## Assembler source

`check-asm-source.py` enforces the source hygiene rules currently used for
hand-written and generated IBM assembler in this project:

- ASCII-only source;
- no tab characters;
- no trailing whitespace;
- no source text past column 71.

Examples:

```sh
python3 tools/checks/check-asm-source.py asm/icintv19.asm
python3 tools/checks/check-asm-source.py asm/
```

The checker returns a nonzero exit status for any violation, so callers may use
it as a pre-flight gate before generating JCL, committing assembler changes, or
running a regression.

## Scope

Keep these tools conservative and mechanical.  A pre-flight checker should
detect repository or language-format hazards, not silently rewrite historical
source or make semantic changes.

One-off diagnostics still belong in `workarea/` or a temporary environment.
Only reusable checks should graduate here.
