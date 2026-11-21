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

**MVS population accepted (20 November 2026):** the owner executed the
one-shot 15-member Cambridge source population in JOBS 9325/9326;
the runner independently verified the exact 15-member MVS directory.
Do not rerun population. The new [read-only historical source record
readback](rc2-cambsource-record-readback.py) uses the existing
`dspal get` MVS service to compare each normalized FB80 record with
frozen historical Git source. See [population acceptance and record
readback evidence](rc2-population-accepted-readback-design-20261120.md).
Record readback and BT0021 staging remain pending. Raw CP037 bytes
are not claimed verified by the text readback.

**Readback mismatch (20 November 2026):** the owner ran the
15-member read-only MVS source readback; its normalized source-content
comparison failed. The saved MVS evidence is preserved in
`workarea/ta2-rc2-cambsource-record-readback/`. Do not rerun source
population, overwrite the readback, or stage `BT0021`. The
[read-only saved-evidence diagnostic](rc2-cambsource-diagnose-readback.py)
prints the first differing record/column and hashes without reading
MVS again or printing source. See the
[TA.2 mismatch evidence and diagnostic gate](rc2-readback-mismatch-evidence-20261120.md).

**End-of-member record diagnostic (20 November 2026):** the saved
MVS `dspal get` result for `BLIB` ended at record 472; the
frozen original has two more empty records. `LIBHDR` and
`TRNHDR` also have trailing empty records. Do **not** assume
that the source PDS lost them or that the SYSOUT text extractor did.
The new read-only [QSAM FB80 fingerprint verifier](rc2-qsam-fidelity.py)
uses [IFOX assembly](rc2-qsam-fidelity.asm) to report actual
MVS record counts, consecutive trailing all-blank records, FNV-1a
and additive checksums for all 15 historical sources. Results
stay in `workarea/ta2-rc2-cambsource-qsam-fidelity/`.
See the [TA.2 investigation evidence](rc2-qsam-fidelity-investigation-20261120.md).
No population repeat, BT0021 stage or BC0002 tape is authorized.

**MVS JOB 9330 transport reconciliation:** all 15 historical
`CAMB_SOURCE` members have the frozen source's FB80 record and
trailing-blank counts. The eight raw CP037 checksum differences
were precisely reproduced, including order-sensitive FNV, by three
observed reader character mappings: `|` → `6A`, `[` → `AD`,
`]` → `BD` (other tested ASCII uses CP037). The original
7/15 CP037 result is preserved; it is not a byte-for-byte
CP037 PASS. Run
[the saved-MVS-evidence reconciliation](rc2-qsam-reconcile-transport.py)
to check JOB 9330's retained actual JES report and receipt
without another MVS run. Details and release design decision:
[TA.2 JOB 9330 transport evidence](rc2-qsam-job9330-transport-reconciliation-20261120.md).
The BT0021 stage and encoding-policy decision remain open.

**TA.2 MVS record-fidelity reconciliation accepted (qualified):** the owner
executed the saved JOB 9330 reconciliation at GitHub `main` and received
RC=0, **15/15 selected Cambridge historical FB80 source members** and
**6,577 source records reconciled** under the observed MVS reader
encoding. Original literal CP037 verification remains **7/15**;
the three measured special-character byte mappings remain documented.
There is no evidence supporting re-population of the accepted source PDS.

The [reconciliation acceptance and source-encoding decision proposal](rc2-job9330-reconciliation-acceptance-and-encoding-decision-20261120.md)
recommends **preserving the actual MVS source bytes through IEBCOPY**,
not converting them to CP037 merely to satisfy a host-codepage check.
The owner has not yet approved this encoding policy or any `BT0021`
staging operation. The release manifest, rights limitations and
`BT0001`–`BT0020` acceptance remain unchanged.
