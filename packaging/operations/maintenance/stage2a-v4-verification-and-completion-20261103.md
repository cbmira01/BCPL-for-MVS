# Stage 2A — V4 MVS verification and completion decision

**Project:** BCPL for MVS 3.8 Reconstruction  
**Operator evidence:** 3 November 2026 local / 4 November 2026 UTC  
**Decision:** **Stage 2A COMPLETE — V1–V4 verified within their explicitly tested scope.**  
**GitHub source baseline used for WSL/MVS execution:** `9f88ea7603c55d0afd34542b86fad354a6d17fe1` (`main`)  
**Owner approval:** Explicit approval to commit the V4 verification record and Stage 2A completion, following separately authorized read-only inventories and temporary-dataset native regression jobs.

This is completion of the **Stage 2A repository relocation work package**, not creation, opening or closure of an official milestone/march. The accepted Runtime Extensions R.0–R.5, BCPLTIME T.0–T.1 and QSAM Q.0–Q.5 records and contracts remain unchanged. Read this alongside the [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md), [relocation review](repository-module-stage2a-precommit-review-20261103.md) and [V1–V3 verification](stage2a-v1-v3-verification-20261103.md).

## V4.1 — resident MVS inventory: PASS within inventory scope

Operator WSL command `tools/datasets/dspal ls <dataset>` submitted a read-only TSO `LISTDS MEMBERS` job for each managed PDS. All four calls reported RC=0 at `9f88ea76`.

| PDS alias | Actual member inventory |
| --- | --- |
| `BOOT_OBJ` | `BCPLAPT`, `BCPLBYTE`, `BCPLIO`, `BCPLMAIN`, `BCPLMEM`, `BCPLREG`, `BCPLRGS`, `BLIB` |
| `EXT_OBJ` | `BCPLDEMO`, `BCPLQSAM`, `BCPLTIME` |
| `EXT_MAC` | `BCXCAT`, `BCXPOST`, `BCXPRE` |
| `EXT_ASM` | `BCPLDEMO`, `BCPLQSAM`, `BCPLTIME` |

**Operator-local evidence directory:** `workarea/stage2a-v4-inventory-20261103T235103Z-85417`.

The member inventories establish **presence**, not member byte identity, build provenance, or parity with current Git text sources. In particular, `EXT_OBJ(BCPLQSAM)` presence alone is not a verified installed-mode `Q5QVFY` execution.

## V4.2–V4.4 — native regression: 16 PASS / 0 FAIL

The owner authorized native jobs that may create **temporary** MVS data sets; no permanent object installation or JES2 device-state change was authorized. The operator ran each selected case individually using:

```sh
tools/bootstrap/run-installed-r5-t1-regression CASE_NUMBER
```

At each run the WSL guard checked the complete `9f88ea76` commit ID and empty `git status --porcelain`. All individual commands reported **RC=0**, `PASS 1`, `FAIL 0`, `SKIP 0` in their displayed terminal summaries.

| Campaign | Native case IDs | Reported result | Operator-local evidence |
| --- | --- | --- | --- |
| **V4.2 — baseline / optional extension** | 000, 146, 147, 158 | **4 PASS / 0 FAIL** | `workarea/stage2a-v4-native-20261103T235927Z-85417` |
| **V4.3 — BCPLTIME / BCPLQSAM contract** | 159, 160, 161, 162, 163, 164 | **6 PASS / 0 FAIL** | `workarea/stage2a-v4-integration-20261104T000257Z-85417` |
| **V4.4 — QSAM record processing** | 168, 170, 171, 172, 173, 174 | **6 PASS / 0 FAIL** | `workarea/stage2a-v4-records-20261104T000823Z-85417` |
| **Selected native total** | **16 distinct cases** | **16 PASS / 0 FAIL / 0 SKIP** | All three directories above |

Selected behavior includes minimal BCPL execution (000); optional absence/selection/exclusion and installed BCPLDEMO (146, 147, 158); BCPLTIME and cross-extension selection (159–162); BCPLQSAM QUERY and negative contract (163–164); fixed sequential record read/write (168), BCPLQSAM/BCPLDEMO interoperability (170), and V/VB read/write (171–174).

**Profile precision:** `run-installed-r5-t1-regression` uses production `BOOT_OBJ` and selects installed `EXT_OBJ` / `EXT_MAC` profiles for the R.5/BCPLDEMO and T.1/BCPLTIME paths. Numbered **BCPLQSAM 163–176 remain source-selected**, not independently proven to load the installed `EXT_OBJ(BCPLQSAM)`.

**Evidence precision:** The owner shared the runner's PASS/FAIL/RC summaries and retained output in the listed local workarea directories. The complete individual JES reports and each IFOX/IEWL/GO step were **not independently re-audited in this record**. Consequently, the accepted finding is that the existing native regression harness reported all selected cases successful, not a separately reproduced line-by-line object/load-map audit.

## Boundaries and deferred coverage

1. This is a **selected 16-case campaign**, not a fresh uninterrupted **00–176** full production regression; 165–167 and 169 were also not included in this V4 selection.
2. Native cases **175–176** were deliberately deferred because of JES punch/printer device considerations. No `--resume-punch`, `$S PUN1` or device-state change was authorized.
3. No **installed-mode BCPLQSAM `Q5QVFY`** acceptance follows from source-selected QSAM cases; its separate Q.5 evidence boundaries remain as documented.
4. The Stage 2A source relocation did **not** populate `EXT_ASM`, `EXT_MAC`, `EXT_SOURCE`, `EXT_OBJ` or `BOOT_OBJ`. Installed member presence is not a new source-to-resident equality proof.
5. No additional MVS dataset promotion, Core Runtime/BLIB modification, compiler redesign, new global-number allocation, or revision of the official historical milestones is implied.
6. The earlier QSAM Q.5 full panel remains faithfully recorded as **175 PASS / 1 FAIL (175) / 1 expected SKIP (083)** followed by a **separate successful case-175 rerun**; do not retroactively report one uninterrupted full-panel PASS.

## Stage 2A disposition and next boundary

**The owner explicitly directs committing the V4 verification record and Stage 2A completion.** V1 source/tree relocation, V2 host tests, V3 synthetic-deck checks/parity, and this V4 selected native execution meet the **bounded Stage 2A source-location verification gate**. Stage 2A is **COMPLETE with the qualifications above**.

The next planned work package is **Stage 2B — regression-suite ownership without moving cases**, as specified in the [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md) and [regression-suite separation design](../../architecture/regression-suite-separation-20261103.md). It should first introduce explicit, reviewed suite manifests and independent reporting/selection under root `tests/`, retaining all 177 numbered native case directories at `bootstrap-toolchain/regression/` and the existing MR10 panel at `mr10-kit-compiler/tests/`. Treat Stage 2B's format, suite attribution, cross-extension tags, installed/source prerequisites, expected SKIP handling, and run-scoped logs as **design choices to review with the owner before implementation**. No new JES authorization or code change is granted by this completion record.
