# Stage 2A — V1–V3 repository, host tooling and deck-equivalence verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 3 November 2026  
**Authority:** [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md), [Stage 2A relocation review](repository-module-stage2a-precommit-review-20261103.md), [V2/V3 remediation](stage2a-v2-v3-host-check-remediation-20261103.md)  
**Disposition:** **V1–V3 VERIFIED (host-side scope)**. **V4 native MVS execution remains OPEN.** This is not a closure of a project milestone or any formal R./T./Q. march.

## Repository provenance

- Authoritative GitHub repository: `cbmira01/BCPL-for-MVS`, branch `main`.
- Original pre-relocation commit: `efb461f3c90a8de93e7d7ddc4dcc3529a9a60a4c`.
- Stage 2A relocation commit: `d8a2588dd3ee6076acc14bcd43dc8e59641b44f8`.
- Corrective host-check commit tested under WSL: `acc4c5cc36a1b401d3377e7c3d850212c7f7f366`.
- Operator WSL environment: `~/Source/Repos/BCPL-for-MVS` on `Morkies`, as reported in the supplied shell transcript.
- Submitted evidence location on operator machine: `workarea/stage2a-verify-20261103T233420Z-85417`. **This local ignored workarea is not a GitHub attachment or committed log**; preserve it separately. This record captures the displayed summary and return codes.

The WSL operator confirmed a successful `git pull --ff-only origin main` from `d8a2588` to `acc4c5cc`. The command block checked that `HEAD` matched the full corrective commit ID before invoking the tests.

## V1 — repository integrity: VERIFIED

A Git tree inspection comparing the relocation commit with its parent established:

- All **147** tracked files from `bootstrap-toolchain/extensions/` existed under the corresponding `system-extensions/` path; no original extension files remained at the old path.
- No file-mode changes or unrelated deletions were introduced by the relocation.
- All **177** numbered native regression cases 00–176 remained in their original location.
- The **61** relocated implementation/source-contract files and all **20** tracked `bootstrap-toolchain/jcl/` files were byte-identical.
- `config/dspal.yaml` was byte-identical after normalizing only the relocated Git source prefix. Existing `EXT_*` and `BOOT_*` dataset aliases/member identities were preserved.

These are Git source/inventory facts, **not** evidence that installed MVS PDS members were refreshed.

## V2 — host tooling: VERIFIED

The owner executed and reported the following after pulling `acc4c5cc`:

| WSL operation | Reported return code | Reported result |
| --- | ---: | --- |
| `python3 -B -m unittest discover -s tools/checks -p 'test_*.py' -v` | **0** | **106 tests; OK** |
| `python3 -B -m unittest discover -s system-extensions/bcplqsam -p 'test_*.py' -v` | **0** | Passed. The displayed transcript tail did not include the case count; do not infer a number. |
| `python3 -B -m unittest discover -s system-extensions/template -p 'test_*.py' -v` | **0** | **8 tests; OK** |

An earlier WSL invocation on `d8a2588` additionally recorded **Python compilation RC=0** and **shell syntax RC=0**; subsequent commit `acc4c5cc` changed Python test/host-side generator source, but did not change the two checked shell wrappers. The subsequent successful Python test imports/execution provide additional syntax coverage. Do not represent the earlier syntax invocation as a new post-remediation syntax run.

The earlier reported V2 failures (outdated QSAM 163–170 assumptions, obsolete documentation links, inappropriate 71-column restrictions on canonical installation-JCL comments, and Q.2 source-contract assertions) were remediated in `acc4c5cc`. No MVS code change was required.

## V3 — generated-deck equivalence: VERIFIED for covered generators

| WSL operation | Reported return code | Reported result |
| --- | ---: | --- |
| `python3 -B system-extensions/bcplqsam/prepare-q5-release-campaign.py --check` | **0** | `PASS: Q5PKG temporary binary PDS + selected/unselected JCL 4722 cards; no JES` |
| `python3 -B tools/checks/verify-stage2a-deck-parity.py` | **0** | `49 before, 49 after` and `V3: PASS — all synthetic IFOX/IEWL/JCL decks byte-identical` |

The exact deck comparison covers: T.0 source (1); R.5 146–158 source and installed (26); T.1 159–162 source and installed (8); BCPLQSAM 163–176 source (14). **49/49 identical** proves the generated outputs of these synthetic cases did not change across the repository relocation.

**Qualification:** `Q5PKG` is not among those 49 old/new comparisons. Its pre-relocation `--check` had a false positive: a harmless assembler comment containing `BOOT_DEVOBJ` was treated as an active permanent output operation. The correction ignores full-line comments but retains rejection of active permanent `CATLG`, `DISP=MOD`, and `BOOT_DEVOBJ` references. The repaired Q5PKG synthetic 4,722-card generation and focused positive/negative unit tests passed. Neither generated-deck checks nor the 49-case comparison constitutes IFOX assembly, IEWL linkage or native GO execution.

## Evidence constraints and transition to V4

V1–V3 establish repository/source integrity, host tooling operation, and the **stated** synthetic deck equivalence. They do not establish MVS-resident source deployment, current installed `EXT_OBJ` member provenance, IFOX/IEWL return codes, execution of optional dispatcher services or QSAM record device behavior.

**V4 remains OPEN**, requiring a separately authorized, bounded native MVS 3.8J regression campaign and actual JES/IFOX/IEWL/GO reports. Before submitting any job, inspect current resident MVS configuration and confirm whether `BOOT_OBJ`, `EXT_OBJ` and `EXT_MAC` match the intended approved profile. Keep source-selected BCPLQSAM 163–176 distinct from installed BCPLDEMO/BCPLTIME 146–162. Do not infer installed BCPLQSAM `Q5QVFY` acceptance from source-mode regression.

No job was submitted, no MVS dataset was modified and no JES console device operation was authorized or performed as part of V1–V3. **This record preserves prior QSAM Q.5 qualified closure**: its full 00–176 panel had **175 PASS / 1 FAIL (175) / 1 expected SKIP (083)**, followed by a separate **175 PASS** rerun; it was not one uninterrupted green full panel.
