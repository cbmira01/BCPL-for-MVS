# TA.3 qualified technical acceptance and TA.4 preparation — 23 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Candidate:** `BCPL-0.1.0-rc4` / `BC0004`  
**Status:** **TA.3 technical gate PASS (qualified)**; formal TA.3 closure and TA.4 kickoff **await owner direction**.

## TA.3 closure evidence

The [actual MVS all-profile installation record](../../distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md)
demonstrates that the final RC4 tape has:

- Human-readable MVS-only `BT0001` bootstrap.
- Operable tape-resident MVS `BT0002` JCL for `MR10`, `NATIVE`,
  `COMBINED` including the shared `COPY` control member.
- MVS `IEBGENER` readback of the on-tape profile JCL, exact
  card comparison and real JES execution of the read-back members.
- A tested, no-overwrite, individually isolated three-profile
  installation with real MVS DCB and directory verification.
- **42 PDSes / 315 members** across `R4MR` (11/94),
  `R4NT` (11/71) and `R4CB` (20/150).
- Actual installed MR10 `ICINT19` SCALVEC
  `TEST:`/`EXP:`/`RP:`/`CODE=0` PASS.
- Previously accepted MVS standard-label tape production
  (21 logical datasets / 64 AWS physical files), and unchanged
  SHA-256 `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.

The original interrupted one-shot is retained, not repeated.
A new incident-bounded continuation authenticated its original
sealed MVS evidence, independently verified the recovered first
profile with actual MVS LISTDS/directory and completed only the
two unexecuted profiles. Operator-reported successful continuation:
`workarea/ta3-rc4-continuation/20261123T163929Z-37828`.
Private sealed JES reports were not directly retrieved in this
assistant session; no unreported MVS job IDs are asserted.

**Qualified limitations:** tested site `HERC02`/`TSO002`,
not every symbolic site override. Isolated namespaces on the
existing MVS installation are not an independent clean IPL,
which is deliberately reserved for **TA.7**.
Complete MR10 demos/regression and rebuilt interpreter belong
to **TA.4**; included native library and runtime link/execute
belong to **TA.5**. The candidate does not include a native
Cambridge Compiler (`native_compiler: absent`), therefore **TA.6 N/A**.

No accepted stage, tape write or recipient job may be repeated
just for ceremony. Publication is not authorized.

## Proposed next march: TA.4 — MR10 Kit Compiler Distribution and Verification

The formal milestone defines TA.4 acceptance as **all** of:

1. MVS-independent use of the distributed `ICINT19`, plus
   verified rebuild from distributed `MR10KIT.ASM(ICINT19)`,
   `MR10KIT.OBJ(ICINT19)`, and
   `MR10KIT.JCL(IC19BLD)` via IFOX/IEWL as appropriate.
2. Actual MVS compile/run of **11** language demonstrations from
   `MR10KIT.LANGDEMO` under `MR10KIT.JCL(MRLANGDM)` and
   **17** selected BCPL demonstrations under
   `MR10KIT.JCL(MRBCDEMO)`. Source PDS carries additional
   related support/data members; do not equate all 20 members
   with the 17 required demonstration cases without inspecting
   the canonical execution JCL.
3. The **12-case** installed `MRREGRES` panel against the
   accepted literal `EXP:` records, computed `RP:` values
   and interpreted `CODE=0`, preserving the previously accepted
   automated WSL `RP:`/`CODE=` check. The accepted RC3
   63-step MVS JOB 9369 and its 12/12 semantic comparison
   are valuable predecessor evidence; **do not rerun them**.
4. **Twelve explicit human PASS/FAIL decisions and an identified
   overall sign-off**, as mandated by the owner-approved
   [EXP/manual verification decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md).
   Earlier operator `cm` reviewed twelve cases but the
   case-sensitive terminal `SIGN` gate was not completed,
   so there is **no accepted sealed human sign-off yet**.
   Obtain a new signature from saved immutable MVS output
   rather than repeat accepted MVS regression jobs.

### Safe initial TA.4 sequence

- **Read-only source/evidence preflight first:** inspect the exact
  restored `R4MR` or `R4CB` distributions, canonical
  `IC19BLD`, `MRLANGDM`, `MRBCDEMO`, `MRREGRES`
  MVS JCL, input datasets, expected step counts, target
  sources and already-sealed MR10 evidence. Confirm missing
  accepted gates before creating work.
- Implement Git-controlled, MVS-native **site-retargeted**
  build/demo job bodies and a consolidated guarded operator
  runner with one uncomplicated approval before any **new**
  MVS allocation or execution. Reuse the existing
  accepted target namespaces without replacing them.
- MVS rebuild/interpreter/demos drive further engineering,
  with exact JES/IFOX/IEWL/ICINT19 evidence saved under
  repository `workarea/`. Avoid unnecessary WSL printouts.
- Keep the complete 12-case human sign-off independent of
  automatic comparison; permit the owner to review the
  already accepted original JOB 9369 through its sealed
  read-only reviewer after the separate design approval.
- Do not claim TA.4 PASS until the 11+17 cases,
  interpreter rebuild, 12-case actual verified semantics,
  and identified human signature are all accepted.

**Owner decision requested:** formal **TA.3 CLOSED (qualified)** on
the technical MVS evidence above and proceed into
**TA.4 — MR10 Kit Compiler Distribution and Verification**
with this read-only-first plan. Until explicitly approved,
this document is **preparation**, not a formal march transition.

## Superseding owner decision — formal closure accepted 23 November 2026 EST

The owner subsequently directed **“Close TA3 and open TA4.”**
Accordingly the review-ready status above is now **superseded**:
**TA.3 — MVS Bootstrap and Installation formally CLOSED
(qualified)**; **TA.4 — MR10 Kit Compiler Distribution and
Verification OPEN / IN PROGRESS**. The governing decision is the
[formal closure and TA.4 transition](ta3-formal-qualified-closure-and-ta4-transition-20261123.md);
the [TA.4 kickoff](ta4-kickoff-20261123.md) establishes the
next read-only-first work. Preserve all accepted media and
one-shot MVS receipts.
