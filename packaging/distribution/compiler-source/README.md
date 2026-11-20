# TA.2 — historical Cambridge source PDS for rc2

**Current approved release design (20 November 2026):**
`BCPL-0.1.0-rc2`, reserved VOLSER `BC0002`, has **21 logical
tape datasets**. Only `BT0021` is added to the original 20.
It carries **15 historical Cambridge Compiler source members** in
`CAMB_SOURCE`, targeting `{HLQ}.BCPL.CAMBRIDG.SOURCE`
(PO/FB/80/800). This is historical source preservation,
**not a native-running Cambridge Compiler executable**.

The owner specifically **excluded the demoted/compiler-instrumented
development derivative**. No `CAMB_DEMOTED` PDS, generated `CGA`–`CGE`
or other demoted section, `BOOTHOST`, `CAMBPARM`, `CAMBBLD`,
or demoted-specific `SNOTICE` member is selected for the tape.
That entire reconstruction process depends on GitHub source history,
transformation filters, generator configuration and regression tests;
restoring its output as isolated MVS PDS members would omit that context.
It remains development material in GitHub, not MVS installable content.

The **historical** selected members are `BCPL`, `BLIB`, `CG`, `CGHDR`,
`EDITMAIN`, `IOS`, `LIBHDR`, `PM`, `SYN`, `SYNHDR`, `TRN`,
`TRNHDR`, `MAKEOBJ`, `MAKELIB`, and `PROGRAM`.
The archival `MAKEOBJ`/`MAKELIB` texts are not ready-made MVS JCL.
The Cambridge source-only inclusion flag is
`release.cambridge_source: included`; the executable flag remains
`release.native_compiler: absent`.

**Canonical source selection:** `../manifest/releases/BCPL-0.1.0-rc2.yaml`;
the original 20 positions are identical to `rc1`. `config/dspal.yaml`
maps only `CAMB_SOURCE` as the extra MVS PDS.
`successor-contract.py` checks the single-PDS selection, the historical
member lineage and the SHA-256-pinned registry. `rc2-stage-draft.py`
may generate a **JOB-less draft** for only `BT0021`; no JES submission,
MVS allocation, AWS writing or acceptance is implied.

`source-selection.json` and the existing `make-demoted.py` remain
**GitHub development worksheets**, not competing release manifests.
`pack.py` can audit the other source families in GitHub but permits
export of **historical-only FB80 decks**. Generated and support material
cannot be exported as distribution decks. CP037 FB80 record generation
is not proof of identity to records on the MVS system.

**Provenance and rights:** see `LICENSE.md`,
`THIRD-PARTY-NOTICES.md`, `PUBLIC-RELEASE-AUDIT.md`, and the current
MVS `DIST_DOCS(LICENSE)`. Archival existence is not blanket
redistribution permission. The accepted historical-source layout is
**not** a rights approval; candidate release gating must remain
fail-closed pending per-member rights evidence and adequate on-tape
notices.

**MVS status:** The owner reported `dspal stat CAMB_SOURCE` RC=0 and
`dspal stat CAMB_DEMOTED` RC=2 on 20 November 2026. A successful
`stat` return is not proof of the 15 required members, exact records,
or free space. The latter key is no longer a release input and needs no
further investigation for the tape. The original 20 staging inputs are
accepted; do not restage them. New `BT0021` staging and any `BC0002`
AWS operation require their own evidence and authorization.

See the [rc2 historical-only correction evidence](rc2-historical-source-correction-evidence-20261120.md)
for the source freeze, registry digest, offline tests and pending MVS gates.

The current read-only MVS source directory is empty (owner-reported
`dspal ls CAMB_SOURCE`, RC=0). See
[BT0021 empty-source evidence and proposed population batches](rc2-cambsource-empty-source-evidence-20261120.md).
The new `rc2-cambsource-readiness.py` checks a saved MVS listing,
the exact 15 frozen Git source files and the existing `dspal`
4000-card batch boundaries without writing anything. Its 10 focused
synthetic tests pass; the original `dspal populate CAMB_SOURCE --batch`
remains the only intended source-population mechanism.

**Population operation approved on 20 November 2026.**
Use the tracked [one-shot CAMB_SOURCE population runner](rc2-populate-cambsource-once.py)
only under this specific authorization. The original owner-reported
source PDS is empty. Its runner verifies a fresh MVS empty directory,
the exact frozen 15-member source plan, runs the existing 8+7-member
`dspal` IEBGENER batches once, preserves private MVS receipts and
checks the resulting member directory. The attempt marker is
persistent; failures are **not automatically retryable**.
See [owner authorization and local tests](rc2-source-population-authorization-20261120.md).
It does not stage BT0021 or produce an AWS tape.
