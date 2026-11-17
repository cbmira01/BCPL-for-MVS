# TA.0 — Retained MVS build evidence intake contract

**Milestone:** Tape artifact release; **march:** TA.0 — Release Architecture, Inventory, and Manifest
**Status:** Read-only design/prototype; not an accepted release candidate or live MVS result.

## Purpose

The [TA.0 inventory](ta0-inventory.yaml) selects **15 object/load members**
in four source MVS datasets: MR10_OBJ, MR10_LOAD, BOOT_OBJ and EXT_OBJ.
The [existing build-chain audit](../../../tools/distribution/audit-binary-build-chain.py)
identifies the eight reconstruction build jobs: IC19BLD, BLDBMAIN, BLIBBLD,
BLDCORCO, BLDCORLB, BCPLDEMO, BCPLTIME and BCPLQSAM.

The [read-only retained-evidence inspector](../../../tools/distribution/audit-mvs-build-evidence.py)
reuses the authoritative `tools/reconstruction/verify.py` verification contract
for JES payload identity, exact step/program lists, RC, IFOX severity, interpreted
CODE=0 records and IEBCOMPR failure indicators. It also verifies four
saved `dspal ls` directory inventories. It does **not** run a job or touch tape.

## Required operator-supplied evidence

An independent evidence directory must contain one `index.json` and **20**
SHA-256-pinned **UTF-8 text attachments**: eight `job-summary` outputs,
eight `dump-report-for-job` outputs, and four saved `dspal ls` outputs.
Preserve the source output bytes, not reconstructed excerpts.

| Index field | Required meaning |
| --- | --- |
| `schema_version` | Integer 1 |
| `source_git_sha` | Full 40-character lowercase Git revision **claimed** to have built the MVS inputs |
| `hlq` | MVS HLQ appearing in the four saved inventory headings |
| `jobs` | Exactly one entry for each of the eight jobs above |
| `inventories` | Exactly one entry for each of MR10_OBJ, MR10_LOAD, BOOT_OBJ and EXT_OBJ |

A job entry has exactly `name`, `payload_job`, `launcher_job`,
`summary` and `report`. The two job numbers are distinct positive
JES job numbers (1–9999). Each report attachment is an object with exactly
`path` (relative to the index directory) and `sha256` (64 lowercase hex digits).
An inventory entry has exactly `dataset_key` and `file` (the same
path+SHA-256 object). Duplicate or unexpected entries fail closed.

**Critical qualification:** The source SHA is compared with an independent
**operator-provided** CLI value, not cryptographically linked to MVS-resident
source bytes. The retained report's association with the correct live JES
session and the launcher job ID also require independent operator review.
An exact member-name listing cannot prove binary member record identity, DCB,
linkage or GO. Passing this preflight is **not release acceptance**.

## Host-only read-only inspection

The following command reads already collected files; it does not create the
index, collect evidence, submit a JES job, or modify Git/DASD/tape.

```sh
python3 -B tools/distribution/audit-mvs-build-evidence.py \
    --index /path/to/saved-evidence/index.json \
    --source-sha FULL_40_CHARACTER_SOURCE_GIT_SHA \
    --json
```

The index and every attachment must be non-symlinked, stay under the specified
directory, have unique safe relative paths, match SHA-256, and satisfy the
existing strict reconstruction verifier. The inspector is **read-only**.

## Still unsatisfied

Member-by-member relocatable/load record bytes and independently obtained
content hashes; actual source-to-MVS revision binding; source, unloaded and
restored DCBs; executable linkage/GO; historical BLIB and generated COROUTIN
reconstruction provenance; redistribution rights and notices; multi-dataset
tape validation; and separate owner publication approval.

Historical CO.5 qualified acceptance remains valid in its own scope, but its
operator-local receipts cannot silently be promoted to a new tape candidate.
TA.0 remains **IN PROGRESS**; TA.1 tape writes remain separately gated.
