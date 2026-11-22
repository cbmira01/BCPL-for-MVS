# Install from tape

Consumer-side source intended to be carried on distribution media.

- `jcl/`: MVS dataset allocation, IEBCOPY restore, and verification jobs.
- `scripts/`: installation-support source, if needed; any tape-resident executable dependency must be available on the target MVS installation.
- `tests/`: clean-target restoration and verification cases.

The installer must be usable without GitHub, WSL, Python, TSO or project development utilities. The tape bootstrap arrangement must make installation instructions and JCL accessible before BCPL is installed. Per the [approved distribution direction](../native-cambridge-compiler-distribution-decisions-20261108.md), the recipient supplies a site-specific HLQ and the installation uses the same position-based `BCPL.BTnnnn` mapping as the producer. The initial read-only bootstrap and all installation procedures remain to be implemented and verified. No executable installation procedure or overwrite policy is approved yet.

The [expanded release scope](../release-payload-scope-decision-20261116.md) requires **independent MVS-only installation and verification** for both the native Cambridge Compiler and the MR10 Kit Compiler. MR10 must ship with its 11 language demonstrations, 17 BCPL demonstrations, and 12-case regression panel. Its existing `MRREGRES` job runs on MVS. The [subsequent owner decision](../mr10-regression-exp-manual-verification-decision-20261116.md) requires fixed `EXP:` and actual `RP:` report records and **human per-case review of all 12 plus interpreted `CODE=`** on MVS, with recorded PASS/FAIL and sign-off; an automatic MVS semantic comparator is **not** required. This report format and manual acceptance procedure remain to be implemented and proven. Host-side `dspal` and Python verification are not acceptable recipient dependencies.

## TA.2 proposed installer materials; recipient acceptance pending

The manifest-derived [offline installer material generator](../create-tape/ta2-bootstrap-installer-materials-20261119.md)
now provides four proposed MVS PDS members (INSTALL, DATASETS, RELEASE,
RESTORE), an 18-step IEBCOPY restoration template, and the BT0002
bootstrap restoration job body. This is an **unexecuted, site-parametric
proposal**; placeholders for HLQ, tape unit, DASD unit and each allocation
must be supplied and checked before use. TA.3 must still establish safe
recipient installations and independent profile selection on actual MVS.
No installer PDS has yet been created or written to tape.

## Proposed pre-staging installer job preparation

The [TA.2 preparatory material and target preflight](../create-tape/ta2-bootstrap-prestaging-mvs-preflight-20261119.md)
adds a **not-submitted** MVS IEBGENER/IEFBR14 staging job for BT0001
bootstrap text and four BT0002 installer PDS members. `DD DATA,DLM=ZZ`
preserves the proposed RESTORE member's JCL statements as in-stream
**data**. It is not a recipient installation approval. The recipient
must still supply site parameters, and TA.3 must verify actual installation
with MVS-only tools. No live stage or tape test has been executed.

## TA.2 BC0002 isolated installation/usage pilot — designed, not executed

The [consolidated acceptance record](ta2-rc2-consolidated-acceptance-20261121.md)
and tested `scripts/ta2-rc2-acceptance` provide a single MVS-facing entry
point. `--live` performs a read-only catalog/DCB preflight of the 21
JOB-9343 readback datasets and confirms 21 new installation destinations
absent. The consolidated `--run` phase performs the same read-only preflight and
then requires one explicit operator **Y** confirmation before allocating a new `HERC02.BCPL.TA2INS.*` environment,
copy all 21 restored datasets with IEBGENER/IEBCOPY, and run the canonical
12-case MRREGRES from the independently installed MR10 inputs/load module.
The installation is a same-system pilot, not a clean-target TA.3/TA.7 PASS.
No new MVS operation is claimed.

The first operator invocation of `--run` refused at a redundant Git approval-file gate (RC=2, no MVS operation or one-shot marker). The revised procedure removes that gate; the explicit `[y/N]` response is the sole stateful authorization and the durable no-retry marker is created only after `Y`. No stateful MVS installation result has been reported.

## Post-run semantic review of installed MR10 (read-only)

Owner-reported JOBS **9344** (21 source DCBs and 21 absent targets PASS), **9345** (21 installed datasets, RC=0000) and **9346** (`MRREGRES` 12 execution steps, JES RC=0000) completed on 22 November 2026; no rerun is permitted. Run the **same** `scripts/ta2-rc2-acceptance` entry point with **`--review`** to inspect its original SHA-256-sealed JOB 9346 report; this performs no MVS submission. It writes only a fresh sealed semantic comparison under repository `workarea/`. Its golden `RP:` and interpreted `CODE=` comparison is diagnostic; current BCPL tests do **not** emit the owner-approved `EXP:` lines, and individual human sign-off remains pending. See [consolidated acceptance record](ta2-rc2-consolidated-acceptance-20261121.md).
