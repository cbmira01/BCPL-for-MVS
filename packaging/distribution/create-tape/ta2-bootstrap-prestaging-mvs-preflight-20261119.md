# TA.2 — Bootstrap pre-staging cycle and read-only MVS target inquiry

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026 EST / 20 November 2026 UTC  
**Status:** Offline implementation and read-only live MVS inquiry prepared; **no new MVS execution or media creation accepted**.

## Concrete producer dependency and correction

The previous `ta2-bootstrap-installer` entry point required a final
`ta2-offline --candidate` PASS *before rendering BT0001 and BT0002*. That
strict final producer gate in turn requires saved MVS `stat`/`ls` evidence for
**all 20 sources**, including these two not-yet-created inputs. Thus an
unintended circular dependency prevented preparing the very inputs
needed to pass final candidate gating.

The existing producer's strict validation **must remain authoritative for
tape creation**. Accordingly the bootstrap generator now has two
explicitly different paths:

1. **`--prepare`**: offline, preparatory material generation from an
   identity-complete, 20-position proposed candidate manifest in the
   canonical `packaging/distribution/manifest/releases/` location. It checks
   safe candidate ID/version/source SHA/VOLSER, exact TA.0 member selection,
   DCBs, target templates, 127 curated members and native-compiler
   disclosure. It **does not** claim registry reservation, source
   provenance approval, available MVS staging inputs, candidate freeze or
   tape authorization. It creates **only** exclusive files under repository
   `workarea/`.
2. **Default final mode** (no `--prepare`): still executes the existing
   `ta2-offline --candidate` canonical frozen Git, manifest/registry
   and saved MVS evidence gate **before output**. It remains fail-closed.

**Neither** mode submits JES or creates a candidate image.

## Proposed new MVS staging deck

The offline material set now includes
`STAGE-NEW-BT0001-BT0002.jcl`. This is a **JOB-card-free,
not-submitted proposal** for a new, one-shot MVS job with six steps:

- IEBGENER to create `HERC02.BCPL.TA2STG.BT0001` as PS/FB/80/800,
  with `DISP=(NEW,CATLG,DELETE)`.
- IEFBR14 to allocate **new** `HERC02.BCPL.TA2STG.BT0002` as
  PO/FB/80/800, including PDS directory blocks.
- Four IEBGENER steps to populate only the PDS members `INSTALL`,
  `DATASETS`, `RELEASE`, and `RESTORE`.

The job is tied to the accepted staging volume `TSO002`. Later steps
carry `COND=(0,NE)`. Each in-stream member uses
`DD DATA,DLM=ZZ`, including literal `//` and `/*` JCL cards
inside RESTORE as **data**, not executable job steps. The generator rejects
delimiter collisions and invalid card widths. This is not an IBM
IEBGENER reimplementation; actual JES/IEBGENER results will establish
whether the integration is correct.

**Do not submit** until the owner separately approves the specific
provisional candidate identity, two new target allocations and one-shot
JCL. A partial or ambiguous job must stop for actual MVS evidence
review, not automatic resubmission. No stage job is authorized by this
document. Existing accepted staging `BT0003–BT0020` (JOB 9310, then
JOBS 9311/9312) must not be rerun or modified.

## Ready read-only MVS preflight

`packaging/distribution/create-tape/scripts/ta2-bootstrap-target-preflight`
is an independent, **read-only**, two-job MVS inquiry. On `--live` it
uses the existing authenticated `dspal-core` submission and existing
`ta2-target-preflight` IEHLIST/VTOC interpretation:

- TSO `LISTDS` confirms both **exact** proposed DSNs are not
  already cataloged.
- `IEHLIST LISTVTOC` captures the actual TSO002 VTOC and refuses
  visible uncataloged target-name collisions.

Saved full original JES reports, job/cursor evidence and SHA-256
receipts remain **only** under ignored
`workarea/ta2-bootstrap-target-preflight/`. Temporary JES input
is also confined to that directory; raw reports are **not dumped to
the WSL console**. The summary is compact. The inquiry does not grant
space-allocation approval, assert adequate VTOC free tracks, create a
dataset, mount tape or change an accepted stage.

## Verification and next gates

**43/43 synthetic focused local tests PASS** (30 bootstrap/generator and
13 read-only preflight tests). Includes offline EBCDIC FB80, exact
20-dataset map/127 members, JCL/column limits, five `DD DATA` in-stream
panels, six actual stage steps, exceptional MR10 load DCB, preparatory
versus strict candidate gates, non-overwrite output, MVS catalog
absence/contradiction, original read-only report saving and JES temporary
file placement inside repository `workarea/`. Python code compilation
also passed.

These synthetic checks are **not** actual JES/IEBGENER staging evidence.
Next, run the new **read-only** two-target MVS preflight once and review
its saved output. After the release identity/rights/source freeze and
separate explicit staging approval, generate and execute the six-step
proposed stage job once, inspect its real MVS results, collect actual
BT0001 and BT0002 `stat`/`ls` evidence, and only then run the
**existing strict final producer gate**. The 20-dataset AWS candidate
needs separate write/mount authority and real label/readback evidence.

**TA.2 remains IN PROGRESS.** TA.0 and TA.1 qualified closures are
unchanged. No march TA.0–TA.8 renumbering, premature TA.3 acceptance or
publication.
