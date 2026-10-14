# M3 — dspal namespace migration and operator execution

Status: **manifest rebuilt and statically checked; MVS allocation/population NOT YET EXECUTED** (14 October 2026).

The Git-tracked `config/dspal.yaml` defines **23** datasets under `HERC02.BCPL.MR10KIT` (9), `HERC02.BCPL.CAMBRIDG` (9), and `HERC02.BCPL.NATIVE` (5). It has **142** explicit source-to-member mappings in 11 mapped, populated-by-default source/JCL/library/test PDSes. The remaining 12 PDS/load libraries have no mapped text members and use `populate: false`. The staging source paths for Cambridge's demoted/bootstrap artifacts are intentionally omitted until available in the host workarea.

## Static validation completed

- All 23 logical dataset keys are unique and have DSNs with valid <=8-character qualifiers.
- All 142 member identifiers are unique within their dataset and at most eight characters.
- All 142 explicit source paths exist as tracked Git blobs in the repository state at manifest creation.
- Empty and binary object/load libraries are not text-populated.
- No MVS dataset was renamed, deleted, allocated, populated or read by ChatGPT: the GitHub connection does not reach the user's Hercules/DASD instance.

## Execute on the Hercules host (operator)

Update Git first, then run local preflight/inspection:

```sh
git pull --ff-only
tools/dspal info
tools/dspal initbcpl --show-jcl
tools/dspal status --probe
```

Confirm the local private `config/dspal.local.yaml` supplies the required batch password before commands that submit authenticated JCL. Do **not** commit that file. Inspect the generated allocation deck, particularly 23 physical DSNs, extents, catalog and user privileges.

When MVS is running and the above preflight passes:

```sh
tools/dspal initbcpl
tools/dspal stat
tools/dspal populate all --dry-run
tools/dspal populate all
```

The real `initbcpl` preflights attributes, allocates **only missing** managed datasets and then verifies the new definitions by catalog inspection. The real `populate` writes mapped text members. Confirm that the dry run shows only the intended tracked mappings. Save JES JOB IDs and step RCs and summarize dataset/membership verification before declaring M3 migration accepted.

**Existing `HERC02.BCPL.SOURCE`, `HERC02.BCPL.ASM`, `HERC02.BCPL.JCL`, `HERC02.BCPL.OBJ`, `HERC02.BCPL.DEVOBJ`, etc. are deliberately outside the new manifest.** They remain on MVS; neither `initbcpl` nor `populate` deletes them. No automatic copying of existing binary object members from old OBJ/DEVOBJ is provided by this text-file manifest. Plan and verify binary migrations separately before changing native runtime regression link targets.

## Required acceptance evidence

Record (a) `dspal info` listing 23 DSNs; (b) `initbcpl` preflight and allocation JOB IDs with RCs; (c) `dspal stat` showing expected PDS/loadlib DCB; (d) `populate` counts and any errors; (e) representative round-trip `dspal get`/member inspections; (f) existing accepted D7 object libraries remain intact. No deletion or retirement of the old libraries until explicit authorization.

The native regression configuration still points to old `HERC02.BCPL.DEVOBJ` until separately migrated and retested. Cambridge compiler reconstruction remains deferred to M4.

## 14 October 2026 — failed initial allocation and repair

- JOB 3779, DSPALINI: `IEF452I JOB NOT RUN - JCL ERROR`, with `IEF618I` and `IEF605I` on overlong DD statement records; **zero new datasets allocated** in that job. The DD generator was changed to put `DISP` on a separate continuation card.
- JOB 3780, DSPALST: 23 `IKJ58503I ... NOT IN CATALOG` messages, RC=0008. `dataset_missing` was fixed to recognize quoted DSNs.
- `tools/submit-jcl` was modified to report `IEF452I ... JOB NOT RUN` immediately rather than waiting for `$HASP373` until timeout.
- The correct population invocation is `tools/dspal populate all --dry-run` and then `tools/dspal populate all`; the target argument is mandatory.
- These fixes are **committed but not yet tested against the user's Hercules instance**. Repeat the operator preflight and allocation checks before population. Preserve the original acceptance status as pending.

## 14 October 2026 — allocation gate accepted

Operator report following the corrected generator:

- Preflight jobs 3781–3803 completed; all 23 datasets were initially absent.
- JOB **3804** allocated all 23 newly managed data sets. `dspal initbcpl` reported creation of each one.
- JOB **3805** (`dspal stat`) verified all 23 cataloged libraries with the expected attributes: 21 FB80 PDSes (`DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800`), and the two loadlibs (`DSORG=PO,RECFM=U,LRECL=0,BLKSIZE=6144`).
- **Allocation gate PASS.** Content population, member inspection and binary object migration remain pending. Older datasets are preserved.

Next operator commands: `tools/dspal populate all --dry-run` and, if clean, `tools/dspal populate all`. Save population job evidence before accepting the population gate.
