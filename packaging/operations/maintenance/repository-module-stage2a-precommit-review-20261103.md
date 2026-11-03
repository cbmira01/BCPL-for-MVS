# Stage 2A — System Extension source relocation (precommit review)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 3 November 2026  
**Status:** UNCOMMITTED candidate Git tree, not installed, not executed under MVS  
**Starting GitHub main:** `efb461f3c90a8de93e7d7ddc4dcc3529a9a60a4c`  
**Authority:** [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md)

## Scope

This candidate establishes top-level `system-extensions/` and a documentation-only `standard-library/` placeholder. The six existing directories `bcpldemo/`, `bcpltime/`, `bcplqsam/`, `bcx/`, `r2testb/`, and `template/` move from `bootstrap-toolchain/extensions/` **with their contents preserved**, including BCPLQSAM's historical diagnostic/test scripts and runbooks. Keeping these diagnostic companions with their package is a transitional choice; future formal regression suite ownership remains a separate Stage 2B/2C decision. `r2testb` remains a historical R.2 test fixture, not a new supported production extension.

All 147 original tracked files are mapped to their corresponding new relative paths. The old directories are removed in the candidate; no symlink aliases or duplicate canonical sources are introduced. Executable and regular-file modes are preserved.

## Updated source-path consumers

- `config/dspal.yaml`: exact new Git source paths for `EXT_MAC`, `EXT_ASM`, `EXT_SOURCE`; leave MVS `EXT_*` and `BOOT_*` aliases, DSNs and member names unchanged.
- Host-side preparation/checking: `tools/bootstrap/run-bcpltime-t0`, `run-r3-acceptance`, and relevant `tools/checks` R.5, T.0, T.1 and QSAM preparers and assertions.
- Bootstrap R.2 interoperability `make-job.py`, `make-matrix.py` and `test_demo.py`.
- Package-local BCPLQSAM preparation scripts, Q.5 run wrappers, test fixtures and runbooks that used explicit old extension paths.
- Rebased package-local repository-root calculations affected by the depth change: `HERE.parents[2]` to `HERE.parents[1]`, `Path(__file__).resolve().parents[3]` to `parents[2]`, and shell wrapper directory traversals from `../../..` to `../..`. Adjusted the extension template test similarly.
- Moved package documentation: relative links updated for the shorter directory depth and the unchanged bootstrap probe tree.
- Root `system-extensions/README.md` and `standard-library/README.md` document the separation.

**Unchanged by design:** formal native regression case directories `bootstrap-toolchain/regression/00–176`, bootstrap runner, `tools/mr10` and MR10 tests, compiler and Core Runtime source, `BOOT_JCL` install JCL contents, `EXT_OBJ` binary objects, and accepted milestone/closure records.

## Candidate static checks completed

1. Recursive Git tree audit: **147 moved files**, all original-to-destination mappings present, original extension paths absent, no Git mode changes.
2. Candidate has no unexpected additions or deletions outside the extension relocation and two new root README files.
3. The 16 inspected active `tools/`, bootstrap probe, and `dspal.yaml` path consumers use `system-extensions/` and no longer contain `bootstrap-toolchain/extensions/`.
4. Git tree inspection of the moved Markdown files: all parsed local Markdown link destinations resolve within the candidate tree.
5. The 177 formal native numbered case directories remain untouched.
6. GitHub `main` has not been advanced by the candidate.

This static inspection does **not** prove an exhaustive codebase-wide reference migration, successful source compilation, correct generated decks, or native runtime parity.

## Required verification before accepting the migration

- In a working checkout, run a **complete tracked-source reference sweep** with `git grep -n 'bootstrap-toolchain/extensions/'`; classify remaining old references as historical documentation, intentional archived evidence, or active defects. Correct all active defects before promotion.
- Check `config/dspal.yaml` with `dspal`'s non-writing validation path; compare the ordered `EXT_ASM`, `EXT_SOURCE` and `EXT_MAC` member identities and source byte content before/after path migration.
- Execute host-side Python unit tests for T.0/T.1/R.5/BCPLQSAM, R.2 probe generation, BCX template checks and path-related tools. Inspect failures rather than suppressing checks.
- Compare generated IFOX/IEWL/JCL source-mode and installed-mode decks against the unchanged baseline, including negative branches and DD/input fixtures.
- Audit all Git paths for case-sensitive imports and file discovery; verify source-only/installed `EXT_OBJ` profiles and whether MVS-installed modules are unaffected.
- After separately obtaining operator authorization, run native MVS verification, preserving per-job RC, load/object provenance, and the QSAM device prerequisites. Do not submit JES jobs, change operator device states or update installed PDS objects under Stage 2A permission.

## Acceptance and rollback

No historical milestone or regression acceptance changes. In particular, QSAM Q.5's full panel **175 PASS / 1 FAIL (case 175) / 1 expected SKIP (083)** and a *separate successful case 175 rerun* remain accurately reported.

The candidate is **not yet committed or pushed**. Stage 2A source promotion requires explicit owner approval for the commit and follow-up verification. For rollback before promotion, discard the candidate tree; after an authorized commit, restore the source locations and mapping changes using a separately reviewed reversal (never silently reset or delete accepted history).

Future Stage 2B should introduce independent suite manifests under root `tests/` without immediately moving cases. `standard-library/` remains documentation-only until BSL design and APIs are approved.
