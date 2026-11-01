# Milestone QSAM — Q.5 installed reconstruction and verification

**Status of this 1 November 2026 design:** Git source/decks prepared, not installed or MVS-tested by the design change. **Later owner disposition:** [Q.5 and Milestone QSAM CLOSED with explicit exceptions](qsam-q5-closure-20261101.md). No Q5QINST/Q5QVFY installed-mode native acceptance was supplied for that closure; this document remains the separate future verification procedure.  
**Authority:** [Milestone QSAM](milestone-qsam.md), [Q.5 release campaign](qsam-q5-release-packaging-campaign-20261031.md), [clean-room runbook](clean-room-mvs-reconstruction.md).  
**Scope:** optional **BCPLQSAM** System Extension, not a Core Runtime replacement or a compiler change.

**Post-closure JCL maintenance:** `BOOT_JCL(BCPLQSAM)` is now the canonical
installation job, replacing the former `Q5QINST`. The historical
`Q5QVFY` verification deck was removed from the active inventory.
Its intended ten-step test remains documented below as historical design,
not an executable current verification procedure or accepted evidence.

## What a clean rebuild reproduces

The `config/dspal.yaml` manifest maps `EXT_ASM(BCPLQSAM)` to
`bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm`,
`EXT_SOURCE(QSAMHDR)` to the public `bcplqsam.h`, and
`BOOT_JCL(BCPLQSAM)` to tracked native installation JCL. The former
`BOOT_JCL(Q5QVFY)` is no longer populated or available for submission.
`EXT_MAC(BCXCAT)` recognizes `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`
with corresponding member-qualified `EXTLIB` requests. The public
entry remains `QSAMSVC` at **G!200**; the BCEX v1 descriptor spans
`QSMBEG`/`QSMEND`. The `EXT_OBJ` binary PDS is deliberately
`populate: false`: its objects must be assembled on MVS.

The Git-sourced text population must precede the native build. The
read-only installed-object consumer test must follow successful
installation and readback. Old accepted `BOOT_OBJ` members and
`EXT_OBJ(BCPLDEMO)`/`EXT_OBJ(BCPLTIME)` must survive unchanged.

## Native installation job — BCPLQSAM

`bootstrap-toolchain/jcl/bcplqsam.jcl` is a **JOB-body deck** for
`tools/datasets/dspal submit BOOT_JCL BCPLQSAM`. dspal supplies the
site's authenticated JOB card; no credentials belong in Git.

| Step | Program | Acceptance |
| --- | --- | --- |
| ASMQ | IFOX00 | Assembles resident `EXT_ASM(BCPLQSAM)` to temporary FB80 object; RC=0000, severity 0 |
| PUTQSAM | IEBGENER | Only permanent write: `EXT_OBJ(BCPLQSAM)`; RC=0000 |
| READBACK | IEBGENER | Copies installed binary member into temporary FB80 dataset; RC=0000 |
| VERIFY | IEBCOMPR | Original vs readback FB80 object records identical; RC=0000 |

This update **does not authorize these permanent MVS writes**. Do
not submit without separate permission, especially during an
existing incremental installation. If IFOX or copy/compare fails,
stop; do not publish an installed-mode acceptance claim. A PDS
member replacement is not atomic. Recovery is a fresh, authorized
rebuild from a pinned Git revision; do not overwrite unrelated
packages while repairing BCPLQSAM.

## Historical installed-mode link/absence design — Q5QVFY (retired)

The former `bootstrap-toolchain/jcl/q5qvfy.jcl` was designed as a
separate **read-only** installed-mode campaign after the approved
installation; it is preserved in Git history, not the current checkout.
Its historical design specifies ten steps: `SCOMP`, `NCOMP`, `SASMA`, `NASMA`, `SASMG`,
`SLKED`, `SGO`, `NASMG`, `NLKED`, `NGO`.

The resident compiler `CAMBCOMP` (under `ICINT19`) produces native
assembler for the accepted BCPL 163 QUERY client and the BCPL 146
unselected client. IFOX assembles those applications and distinct
BCPLREG tables; the registrar source is read **from installed
`EXT_MAC(BCXPRE/BCXCAT/BCXPOST)`**. IEWL reads accepted
`BOOT_OBJ` and, for the selected link only, the **installed read-only
`EXT_OBJ`**. All new object/load datasets are temporary.

Acceptance requires all ten steps RC=0000 and the following **actual
MVS output**, not merely the command's return code:

- `SLKED` MAP/XREF: BCPLQSAM via `INCLUDE EXTLIB(BCPLQSAM)`,
  `QSMDESC`/`QSMDISP`, and `QSMBEG`/`QSMEND`; native
  `SGO` prints exactly `BCPLQSAM Q4 QUERY CARRIAGE PASS`.
- `NLKED` MAP/XREF: no BCPLQSAM INCLUDE, QSAM CSECT or G!200
  registration; native `NGO` prints exactly `R5 EXT 146 PASS`.
- No unexpected IEWL warning, unresolved external, IFOX error, abend,
  or permanent PDS write.

Use `tools/mvs/dump-report-for-job <JOBNO>` to examine the real
JES payload report. Record the source Git revision, job number,
all step RCs, IFOX severity, IEWL maps and standalone PASS records.
A future independently executed, separately approved equivalent test
would be required for **installed-mode** evidence; the deleted `Q5QVFY`
deck is not runnable from the active manifest. The earlier `Q5PKG`
temporary-PDS proof is not an installed-object proof.

## Fresh clean-room and regression gate

During a *separately authorized* destructive reconstruction, install
`BCPLDEMO`, `BCPLTIME` and `BCPLQSAM` using their canonical
`BOOT_JCL` members before the final production native **00–176**
panel. A new installed-mode selection/absence verification must be
separately specified and authorized; it is no longer a resident job. Expected
full-panel result is **176 PASS / 0 FAIL / 1 documented SKIP 083**.

The current numbered QSAM regression cases 163–176 exercise a
source-selected temporary BCPLQSAM candidate, even when BCPLDEMO
and BCPLTIME use installed-mode harness settings. Thus a green
00–176 panel does **not** by itself establish installed BCPLQSAM
linkage; only actual separate installed-mode MVS verification could
establish that boundary. The retired `Q5QVFY` design did not do so.

The previously reported `Q5PKG` JOB **8155** completed its 17
temporary packaging/link/GO steps RC=0000. The owner reported a
separate full **00–176** panel at 176 PASS/0 FAIL/1 SKIP on the
prior `main` revision `72a5da31`. These are valid earlier campaign
evidence, **not** proof of the newly staged installed-mode workflow.

No Q.5 closure or permanent object promotion is inferred from
the preparation of these decks. Record a deliberate installed-object
disposition and obtain explicit owner acceptance after MVS evidence.
