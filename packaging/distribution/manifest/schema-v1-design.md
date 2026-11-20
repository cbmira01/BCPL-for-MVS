# TA.0 — Canonical manifest schema v1 design

**Status:** Owner-approved architecture; technical schema design, not yet a production candidate or implemented validator.

Each candidate will have **one** authoritative Git-controlled `packaging/distribution/manifest/releases/<candidate-id>.yaml`; `config/dspal.yaml` supplies development source aliases/DCB, not release selection. A single cross-release `packaging/distribution/registry/` maintains version/VOLSER/artifact lifecycle. Producer JCL, MVS-only bootstrap/installer, DATASETS/COMPILE/RELEASE docs and independent verification expectations **must all derive from the same manifest**. Never maintain competing manual tape maps.

## Mandatory fields

| Field | Contract |
| --- | --- |
| `schema_version` | Exact supported schema version, initially `1` |
| `release` | Product title, frozen version and candidate ID, 40-digit Git source SHA, `native_compiler: absent\|included`, prerequisite/capability disclosures |
| `volume` | `format: aws`, `labeling: SL`, unique 6-character reserved VOLSER, volume ordinal 1 |
| `profiles` | Explicit `mr10-only`, `native-only`, `combined` group/dependency closure |
| `datasets` | Ordered `sequence`, one physical owner/group, kind, source `dspal_key` or tracked generator, target DSN template, transport, **separate source/unload/target DCB**, exact selected member list and validation |
| `members` | Name, logical owner, source Git path or generated inputs, project/historical/derived/generated origin, rights reference, transformation/build evidence for object/load modules |
| `verification` | Exact inventories and content comparison, tape label/readback, per-profile clean-target tests, human MR10 12-case review, native compiler self-compilation **only if included** |
| `generation` | Deterministic MVS EBCDIC/FB80 text transformation, JCL/installer/document output and generator identity |

## Illustrative (intentionally non-producible) YAML

```yaml
schema_version: 1
release:
  product: "Cambridge BCPL Programming System for MVS 3.8J"
  version: null
  candidate_id: null
  source_commit: null
  native_compiler: absent
volume:
  format: aws
  labeling: SL
  volser: null
  volume_ordinal: 1
profiles:
  mr10-only: [common, mr10]
  native-only: [common, native]
  combined: [common, mr10, native]
datasets:
  - sequence: 1
    owner: distribution
    group: common
    kind: sequential_text
    generator: bootstrap_fb80
    target_dcb: {dsorg: PS, recfm: FB, lrecl: 80, blksize: 800}
    transfer: sequential_standard_label
  - sequence: 2
    owner: distribution
    group: common
    kind: pds_unload
    generator: installer_pds
    transfer: iebcopy_unload
  # Subsequent selected PDSes, exact members and source lineage
  # are frozen only after real MVS inventory verification.
```

**Alias rule:** compute `BCPL.BT` + four-digit zero-padded **logical** sequence (1..N), and enforce MVS `LABEL=(n,SL)`. Do not independently edit aliases. Entry 1 is mandatory EBCDIC FB80 read-only bootstrap and entry 2 mandatory installer JCL PDS unload. `hetmap` physical file numbers are *not* the logical dataset sequence.

## Validation: fail closed

1. Schema and identity complete: no null version, SHA, candidate ID, VOLSER; every new candidate uses a unique reserved VOLSER, even when prior candidate was rejected. No duplicate aliases, target datasets, members or missing/gap positions.
2. Exact curated source/member/owner/provenance selection; reject old MR10 probes, `BOOT_DEVOBJ`, pending `CAMB_*` placeholders, absent generated evidence and any uncertain redistribution record. Every referenced Git source and MVS-generated build input must exist and be traceable to the frozen revision.
3. `native_compiler: absent` forbids selected `CAMB_*`, native BCPL compilation and self-hosting claims. `included` requires actual runnable compiler, sources, object/load and TA.6 evidence. Both require all 12 MR10 regression programs, 11+17 demos, ten accepted `BOOT_OBJ` and three `EXT_OBJ` objects and exact applicable source/procedure prerequisites.
4. Three installation dependency closures: MR10-only independent of Core Runtime/Cambridge, native-only independent of MR10/`CAMBCOMP`, combined deduplicated; native-only without compiler is accurately described as native components only. The three System Extensions ship but are optional at IEWL application linkage.
5. Separate source/restored PDS `PO/FB/80/800`, load `PO/U/0/6144` and **sequential IEBCOPY unload DCB**; never assume the earlier one-object experiment's `V/816/820` unload DCB applies universally. TA.1 must separately prove load-library restore and executable use.
6. No `HERC02` operational dependency in generated recipient JCL. Validate recipient `{HLQ}`, permitted DASD/SPACE/JOB settings, no-overwrite policy, FB80 record width, EBCDIC text encoding and strict binary record fidelity.
7. Pre-production MVS listing/DCB/build checks; tape `VOL1`, `HDR1/HDR2`, `EOF1/EOF2`, filemarks and label sequence; clean-target compare and execution. MR10 MVS verification is **human review of each `TEST:`/`EXP:`/`RP:`/`CODE=`** with recorded verdict, not an invented automatic semantic checker. Preserve WSL automatic checks unchanged.
8. After closure, record complete-image AWS SHA-256, byte count, provenance and acceptance in an **external immutable receipt**, not as a self-referential image checksum. Publish **exact tested bytes** after separate owner approval; an altered image needs new identity/VOLSER and full acceptance.

All selected source, relocatable object, executable, documentation and fixtures must be assigned correct historical/project provenance and redistribution status. Version and VOLSER registry implementation, manifest parser, generated installer, candidate reservation, TA.1 tests and TA.4 source modifications remain outstanding. This design authorizes no MVS/tape writes or release publication.

## TA.0 design-stage implementation checkpoint

`ta0-inventory.yaml` implements `phase: design` with a curated
no-native-compiler selection and null release identities. Exact member names
and source `dspal_key` mappings are checked statically. `member_owners`
distinguishes the historical Base Library and Coroutine Support even when
sharing a physical PDS. Generated assembler, object/load modules, release JCL
and rights decisions remain incomplete, not assumed.

`tools/distribution/validate-manifest.py` is a **read-only prototype**.
`--release` is a strict preflight for candidates and rejects the design file;
the future producer/installer and independent MVS/TA.1/TA.7 checks remain
separate acceptance obligations. PyYAML is required only on the development host.

## Member provenance worksheet (derived, not authoritative selection)

`python3 -B tools/distribution/validate-manifest.py --audit-json` creates an on-demand 127-member JSON worksheet from the canonical TA.0 design inventory and `dspal` mappings. It marks **all redistribution reviews `UNREVIEWED`** and build receipts absent, preserving candidate source hints as investigation leads rather than proof. See the [TA.0 provenance and JCL dependency audit](ta0-provenance-and-dependency-audit.md). The read-only validator additionally rejects unsafe Git paths, unselected generated members and a claim that the native Cambridge Compiler is included without all nine reserved compiler datasets. Its 24 offline tests use synthetic mappings, not resident MVS inventories.

## TA.2 source-only Cambridge extension (approved 20 November 2026)

This is an explicit, backward-compatible **schema-v1 addition** to the
earlier TA.0 blanket `CAMB_*` exclusion for `native_compiler: absent`.
The optional `release.cambridge_source: absent | included` defaults to
`absent`, preserving `BCPL-0.1.0-rc1` behavior. When it is `included`,
exactly `CAMB_SOURCE` and `CAMB_DEMOTED` are permitted as two
`cambridge-source` group source PDSes, with no native compiler
executable or `CAMB_OBJ`/`CAMB_LOAD` inclusion. The combination of
`native_compiler: included` and `cambridge_source: included` requires
a separate future schema/selection review and is currently refused.

The MR10-only profile remains `[common, mr10]`; the native-components
and combined profiles include the two source PDSes. `BT0001` and
`BT0002` retain their reserved bootstrap/installation roles. Historical
source, generated demoted sections, three bootstrap support members and
`SNOTICE` are physically separate from the historical Base Library
and the executable native compiler. Both new source PDS DCBs are
PO/FB/80/800. This extension is selection/validation code, **not**
permission to stage new MVS data sets, release historical material, or
produce an AWS image.

See `../compiler-source/README.md` and the approved canonical
`releases/BCPL-0.1.0-rc2.yaml`. The existing strict
`tools/distribution/validate-manifest.py --release` and
`create-tape/scripts/ta2-offline --candidate` gates stay fail-closed
until actual new-stage MVS evidence, member provenance, correct
rc2-specific installer/docs and required build receipts exist.
