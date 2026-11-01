# Milestone QSAM — Q.5 closure (1 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** **QSAM — native BCPL sequential-record I/O**  
**March:** **Q.5 — Hardening & release**  
**Owner disposition:** **Q.5 CLOSED — 1 November 2026**, by the owner's explicit direction in the project conversation: **"Record these runs, close out Q.5."**  
**Milestone disposition:** **Milestone QSAM CLOSED**, with the accepted evidence scope and exclusions below.  
**Git authority:** `cbmira01/BCPL-for-MVS`, branch `main`. Documentation baseline before this closure: `e5076dd755d632dc03fef9606481ce1791a6e13b`. The exact WSL checkout HEAD used for the latest native panel was **not** included in the posted excerpt; this documentation baseline is **not** asserted to be a cryptographically confirmed execution revision.  
**Latest native evidence:** [Full-panel failure and focused punch rerun](qsam-q5-regression-evidence-20261101.md).

## Owner acceptance and technical scope

The owner closes **Q.5 — Hardening & release** after the documented native error-path hardening, optional-extension packaging/link-edit campaign, Git-backed reconstruction workflow and complete **combined** numbered native regression coverage. This is an **owner-directed qualified closure**: certain proposed installed-object and exceptional-MVS-error proofs are **not** accepted as having occurred. The March's narrower acceptance does not convert missing target evidence into PASS results.

The accepted optional **BCPLQSAM System Extension** is a source-controlled System/370 QSAM record-access facility using `QSAMSVC` at **G!200**, the BCEX/BCRG v1 selected-package registration/finalization scheme, the existing interpreter-hosted **demoted Cambridge compiler**, IFOX, IEWL and MVS 3.8J. This does **not** replace Core Runtime `BCPLIO`, reconstruct the later native/self-hosted Cambridge compiler, introduce dynamic allocation, or assert VBA/VSAM support.

### Q.5 native hardening and packaging chain

| Gate evidence | Owner-recorded result | Precise accepted scope |
| --- | --- | --- |
| [STOP(8) finalizer accounting](qsam-q5-stop-finalizer-job-8140-evidence-20261030.md), **JOB 8140** | PASS with expected GO RC=8 | Sixteen handles; finalizer counters return to zero on the tested STOP path |
| [Failed-OPEN rollback](qsam-q5-failed-open-rollback-acceptance-20261031.md), **JOB 8145** | PASS, GO RC=0 | Injected post-OPEN stage refusal and real rollback CLOSE |
| [Returned-CLOSE quarantine](qsam-q5-returned-close-quarantine-acceptance-20261031.md), **JOB 8147** | PASS with expected GO RC=8 | Quarantine after a **test-injected** nonzero return **following an actual successful CLOSE** |
| [Geometry negatives](qsam-q5-geometry-negative-acceptance-20261031.md), **JOB 8152** | PASS, GO RC=0 | Incompatible/oversized/incomplete JFCB geometry rejected before inappropriate OPEN |
| [Real conditional GETMAIN refusal](qsam-q5-real-getmain-acceptance-20261031.md), **JOB 8154** | PASS, GO RC=0 | Returned-control 1024-byte `GETMAIN RC` refusal and rollback with surviving independent handle |
| [Temporary binary packaging and optional link selection](qsam-q5-release-packaging-campaign-20261031.md), **Q5PKG JOB 8155** | Owner-reported **17 native steps RC=0000** | Temporary-PDS object packaging/readback, selected and unselected native link/GO; **not** installed `EXT_OBJ` proof |
| [Production 00–176 and rerun 175](qsam-q5-regression-evidence-20261101.md), **JOB 9201** in failing initial 175 | Full **175 PASS / 1 FAIL / 1 SKIP**, then focused **1 PASS / 0 FAIL** (runner RC=0) | **176 unique executable cases passed** across distinct runs, plus one expected SKIP 083 |

The native numbered tests 163–176 continue to consume a **source-selected** BCPLQSAM candidate. The accepted Q5PKG campaign demonstrated temporary-PDS optional link selection; neither result proves a separately installed BCPLQSAM object.

## Git-backed reconstruction and release packaging

The canonical source and manifest are retained in GitHub `main`: `bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm`, its public BCPL header, `config/dspal.yaml`, the production BCX selection macros and the `Q5QINST`/`Q5QVFY` installation/verification JCL. The [clean-room reconstruction runbook](clean-room-mvs-reconstruction.md) specifies regeneration of managed datasets, the MR10 interpreter, demoted Cambridge compiler, Core Runtime/Base Library, optional packages and full production test panel.

The owner supplied final regression output in the context of running that reconstruction. The supplied excerpt does **not** include the complete new purge/reallocation/build/install JOB ledger, source hashes or a separately reviewed full-stage acceptance report. The closure accepts the owner's reconstruction status at that reported scope; it **does not claim** independent proof of every new clean-from-Git build step or a verified single-revision end-to-end reconstruction.

**Object-promotion disposition for this closure:** The verified release artifact is **Git source plus reproducible packaging/test procedure**, not a newly accepted installed BCPLQSAM binary. The source-backed `EXT_OBJ(BCPLQSAM)` installation pathway is prepared; its successful execution is **not established** by the supplied closure evidence. No object promotion, installation or update to permanent MVS datasets is authorized by this documentation decision.

## Explicitly unverified / excluded claims

1. **Installed-object link/absence proof:** No `Q5QINST` installation/readback receipt or `Q5QVFY` ten-step native selected/unselected IEWL MAP/XREF and GO evidence was supplied in this closure transcript. These remain separate *post-closure verification work*, not Q.5 PASS results. Neither installed object content nor installed catalog linkage is certified by this record.
2. **Actual exceptional MVS CLOSE:** JOB 8147 verified the production quarantine decision only under a **test-only R15 override after successful CLOSE**. A genuine MVS CLOSE nonzero return, uncertain OS DCB ownership after real failure, and unrecovered abend recovery remain unverified.
3. **Regression chronology:** The latest full panel **did fail** on zero Hercules punch-capture bytes, despite all ten JOB 9201 MVS steps returning RC=0. Only the later focused `--resume-punch 175` test returned PASS. Do not report the two runs as an uninterrupted 176/0/1 panel. A conditional `$S PUN1` operation is *permitted* by that flag; its actual issuance was not shown in the excerpt.
4. **Reconstruction provenance:** The provided excerpts do not prove exact Git execution SHA, all clean-room MVS job IDs, or a raw audit of each native case/JES listing. Reproduce or audit these independently before making stronger deployment claims.
5. **Feature boundaries:** No general VBA, VSAM, random positioning, dynamic allocation, arbitrary record geometry, untested storage-shortage outcomes or historical full-BCPL compatibility is claimed.

These are retained **limitations/deferrals accepted by the owner-directed closure**, not silently completed acceptance gates. Future installed-mode acceptance or exceptional-path work requires its own evidence and authorization. The official Q.0–Q.5 numbering is unchanged; no Q.6 is created.

## Final disposition

**Q.5 — Hardening & release: CLOSED by explicit owner instruction, with qualifications above.**  
**Milestone QSAM — native BCPL sequential-record I/O: CLOSED.**

Previous Q.0–Q.4 owner closures remain intact. This documentation action does not submit a JES job, issue a console command, alter MVS datasets, or modify production BCPL/assembler/JCL code. GitHub `main` remains the official project source.
