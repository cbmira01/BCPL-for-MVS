# TA.3 — RC4 tape-resident operational installer

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** **TA.3 — MVS Bootstrap and Installation (IN PROGRESS)**  
**Owner approval:** 23 November 2026; replace the incomplete tape-resident
installer in a **new candidate**, retaining immutable `BC0003` and
every accepted TA.2/TA.3 receipt.

## Candidate and scope

- Candidate **`BCPL-0.1.0-rc4`**, reserved VOLSER **`BC0004`**,
  registered in `registry/releases.yaml` using the SHA-256 of the
  new candidate manifest.
- **21 standard-labeled logical datasets** retain `BCPL.BT0001`–`BT0021`
  order and existing DCBs.
- `BT0003`–`BT0021` are copied directly from the accepted
  **`HERC02.BCPL.TA2R3S.BTnnnn`** RC3 staging datasets. No re-encoding
  or new historical-source transformation is proposed.
- Only `BT0001` bootstrap text and `BT0002` installer PDS are
  changed for this corrective candidate.
- The compiler remains exactly the **MR10 Kit Compiler** with INTCODE /
  `ICINT19`. The **native Cambridge Compiler remains absent**;
  the Cambridge source material is still work in progress.

## Installation design: genuine MVS JCL in BT0002

The new installer library has **eight** FB80 members:

| Member | Purpose |
| --- | --- |
| `INSTALL` | MVS-native site and profile instructions |
| `DATASETS` | Tape dataset map |
| `RELEASE` | Identity, scope, and provenance notes |
| `RESTORE` | Profile-selection guidance (replaces the inert template) |
| `COPY` | One-record `COPY OUTDD=OUTPDS,INDD=INTAPE` IEBCOPY SYSIN |
| `MR10` | Ten-step MR10-only in-stream JCL procedure |
| `NATIVE` | Ten-step native-component/source-only procedure |
| `COMBINED` | Nineteen-step combined procedure |

`MR10`, `NATIVE`, and `COMBINED` are genuine **JOB-card-less
MVS job bodies** consisting of a `PROC` with symbolic defaults,
a `PEND` and a calling `EXEC`. Each supports:
`HLQ` (root), `SITE` (isolated recipient qualifier), `TU`
(tape unit), `DU` (DASD unit), and `DV` (DASD volume).
The recipient operator supplies a site-valid JOB card and may
override these symbols on the one procedure invocation.

Defaults for proof use `HLQ=HERC02`, `TU=480`, `DU=SYSDA`,
`DV=TSO002`, with distinct `SITE=R4MR`, `R4NT`, `R4CB`.
Every output uses `DISP=(NEW,CATLG,DELETE)`; pre-existing target
catalog entries must cause the separate preflight to refuse execution.

**OS/VS2 MVS JCL-specific constraint:** in-stream procedures may not
contain `SYSIN DD *` or `DD DATA` input. Therefore **each IEBCOPY
step's SYSIN is `DSN=&HLQ..BCPL.&SITE..DIST.INST(COPY),DISP=SHR`**,
referencing the already restored tape-resident one-record member.
This relies on original MVS PROC symbolic substitution rather than
modern `SET`, `JCLLIB`, or z/OS-only facilities.

Reference: IBM **OS/VS2 MVS Job Control Language**, GC28-0692-5,
sections *Cataloged and In-Stream Procedures* and *Using Symbolic
Parameters*. The project must still verify behavior against actual
MVS 3.8J rather than treating documentation alone as acceptance.

## Production strategy and safety

The source-controlled offline producer
`scripts/ta3-rc4-installer` constructs all eight members, BT0001,
an MVS staging deck limited to **two** new datasets
`HERC02.BCPL.TA3R4S.BT0001` and `BT0002`, and a 21-position
standard-label tape writer deck. It reuses the accepted canonical
`ta2-offline` tape JCL renderer and selects the original RC3 stage
datasets for every unchanged payload. The new member total is **150**,
including 8 installer entries and 142 unchanged other PDS members.

**No RC4 DASD staging, media initialization, tape write, or installed
recipient execution has occurred.** Only committed source/manifest/
registry and offline structural review exist.

Before any state-changing production operation:

1. Run the new **read-only** `scripts/ta3-rc4-proc-probe` MVS job
   to prove `PROC` symbolic substitution and PDS-member IEBGENER
   against the accepted `TA3N1` installer. Preserve its JES output.
2. Verify the 19 original staged payload PDSes and their directories
   on MVS; verify the two new stage DSNs absent; inspect free DASD
   space and tape drive/media identity, and detect duplicate VOLSERs
   without altering any image.
3. Require a fresh, one-shot, no-retry authorization gate before
   staging `BT0001`/`BT0002` and writing a **new** AWS image
   `bcpl-0.1.0-rc4-BC0004.aws`.
4. Verify full standard-label/physical AWS layout independently,
   restore all three profiles into new isolated recipients, verify
   DCBs, member directories, and actual installed BCPL program use.
5. Preserve original `BC0003`, accepted TA.2/TA.3 datasets, and
   consumed markers. Never overwrite or replay them.

The read-only probe is the immediate next MVS-facing operation.
The RC4 generator's `--prepare` option writes preview data **only**
under project `workarea/`, not JES or media. It is not an installation
or a successful new tape build.

## Verified MVS prerequisite and next production operation

The owner executed the read-only RC4 symbolic-procedure probe on
actual MVS 3.8J on **23 November 2026 EST**:

```text
TA.3 RC4 MVS PROC PASS: JOB 9392; symbolic PDS member read RC0000.
Evidence: workarea/ta3-rc4-proc-probe/20261123T054327Z-35363
```

**This proves** an in-stream `PROC`, symbolic DSN substitution and
IEBGENER from the previously accepted
`HERC02.BCPL.TA3N1.DIST.INST(INSTALL)` work together on MVS 3.8J.
This was a read-only probe; no BC0004 staging or tape write was
performed. It does not yet prove the full 10/19-step profile procedure.

The source-controlled
`scripts/ta3-rc4-production --run` now implements one guarded,
stateful **new** RC4 stage/write attempt. It first confirms:

- The original BC0003 AWS SHA-256 remains unchanged.
- The frozen RC4 manifest and new reservation match.
- All 19 original RC3 staged payload PDSes have the expected MVS
  DCB/volume and the new two RC4 stage datasets are absent.
- A BC0004 image and VOLSER are not already in use.
- Tape drive 0480 is idle and either empty or mounted with the exact
  verified original BC0003. Only that original is automatically
  unmounted, **after** owner consent and just before initializing
  the new tape.

**One owner `Y` confirmation** creates a no-retry marker before
any allocation or tape initialization. The runner executes one
11-step stage job (BT0001, new BT0002 allocation, eight installer
members); rechecks MVS DCBs and the eight-member directory; initializes
a previously nonexistent `BC0004` AWS; then submits the 21-step
IEBGENER/IEBCOPY standard-label tape write job. Its independent
`hetmap` audit requires **21 logical datasets and 64 physical
AWS files**, followed by an original-BC0003 SHA check.

MVS JOB numbers and full JES evidence are retained under
`workarea/ta3-rc4-production/`; only compact outcomes are printed.
**A successful write does not establish full TA.3 recipient acceptance.**
The next gate will restore the *actual BC0004 tape-resident members*
into fresh isolated recipient datasets and execute at least the combined
profile's installed BCPL example. No existing TA.2/TA.3 job is replayed.

Six source-controlled offline production refusal/safety tests and
eight RC4 generator contract tests cover the design. Actual new
MVS staging, tape write and recipient execution are **pending**.

## Status

**TA.3 remains IN PROGRESS.** RC4 design and source generation are
implemented, subject to MVS PROC proof, production, and recipient
acceptance. TA.4/TA.5/TA.7/TA.8 retain their separate scope.
