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

## Status

**TA.3 remains IN PROGRESS.** RC4 design and source generation are
implemented, subject to MVS PROC proof, production, and recipient
acceptance. TA.4/TA.5/TA.7/TA.8 retain their separate scope.
