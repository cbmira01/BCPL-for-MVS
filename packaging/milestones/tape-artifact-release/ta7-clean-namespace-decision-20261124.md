# TA.7 — Owner-approved clean-namespace acceptance — 24 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.7 — Clean-Target Integration and Release Acceptance  
**Status:** Implementation staged; actual MVS acceptance pending.

## Binding owner decision

The owner directs use of the existing Docker image, container and MVS 3.8J system. Do not duplicate the MVS system, IPL another system, or replace development DASD. Namespace isolation supersedes the independently IPLed recipient requirement in the original kickoff. Acceptance is **qualified clean-namespace installation on existing MVS**, not independent-system certification.

Use the frozen RC4 tape BC0004 (SHA-256 7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1). No tape production or manifest change. Tape DSNs BCPL.BT0001–BCPL.BT0021 remain site independent. The recipient uses the existing authorized HERC02 HLQ with new, disjoint site qualifiers rather than requiring another TSO account.

| Profile | Target prefix | PDSes | Members |
| --- | --- | ---: | ---: |
| MR10 | HERC02.BCPL.T7MR | 11 | 94 |
| NATIVE | HERC02.BCPL.T7NT | 11 | 71 |
| COMBINED | HERC02.BCPL.T7CB | 20 | 150 |

Read BT0001, restore BT0002, read actual tape-resident profile and COPY records using MVS, and override only the documented SITE symbol on the EXEC card. Verify exact MVS directory inventories and DCBs using the accepted manifest. No overwriting, deleting or purging any existing PDS. Preserve all previous accepted namespaces, tapes and receipts. Use the existing container/reader/printer interfaces.

Execute MR10 functional suites independently in T7MR and T7CB: 11 language demos, 17 BCPL demos and 12 MRREGRES cases in each (six functional jobs, 326 ordered MVS steps, 24 automatic semantic verdicts). Read the installed JCL members back through MVS and compare ordered cards with canonical JCL before namespace substitution. All persistent MR10 DDs must be read-only and belong to the selected profile. Use the distributed ICINT19, not a rebuilt interpreter. Native distribution remains inventory/installation only, including eight native PDSes and 41 members in each applicable profile, plus Cambridge source. TA.6 remains N/A.

The new runner is packaging/distribution/install-from-tape/scripts/ta7-clean-namespace. Default is offline plan; --run checks both tape checksums, accepted RC4 production receipt, transport and exact absence of all 42 new PDSes, then asks one explicit operator confirmation. A durable exclusive TA.7 no-retry marker precedes the first media/install operation. Retain per-job actual JES and semantic reports under workarea/ta7-clean-namespace. Do not retry a consumed attempt; inspect evidence and authorize only missing work. Publication remains separately gated.

## Offline verification and limits

Assistant workspace: Python syntax and 18 focused assertions passed (profile SITE override, incomplete readback refusal, MR10 namespace and step-count guard, foreign DSN and write-disposition refusals). Inspected authoritative Git JCL: 38/62/63 steps, five IEBGENER stages each, 33/57/58 ICINT19 STEPLIB references respectively, no unexpected persistent DD disposition or retargeted control-card overflow. Full repository integration and actual MVS execution have not been performed in the assistant workspace; live MVS results remain authoritative. No new TA.7 MVS jobs have been executed. No publication is authorized.


## Subsequent MVS result — 24 November 2026

The owner reported a successful complete campaign. See the [TA.7 technical acceptance record](ta7-clean-namespace-acceptance-20261124.md). The earlier pending status above records the implementation checkpoint, not the current technical result. TA.7 technical PASS (qualified); formal owner closure remains separate.
