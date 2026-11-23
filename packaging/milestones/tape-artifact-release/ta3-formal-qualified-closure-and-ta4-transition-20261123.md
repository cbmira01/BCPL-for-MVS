# TA.3 formal qualified closure and TA.4 transition — 23 November 2026 EST

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**Owner decision:** **“Close TA3 and open TA4. Give me a handoff prompt.”**  
**TA.3 — MVS Bootstrap and Installation:** **FORMALLY CLOSED (qualified)**  
**TA.4 — MR10 Kit Compiler Distribution and Verification:** **OPEN / IN PROGRESS**  
**Authoritative source:** GitHub `main`

## Accepted TA.3 evidence

The owner expressly accepts the [qualified technical MVS installation gate](../../distribution/install-from-tape/ta3-rc4-all-profiles-accepted-20261123.md)
as sufficient to **formally close TA.3 on a qualified basis**.
This closure is limited to the actual completed installation scope,
not the entire tape artifact release.

The approved `BCPL-0.1.0-rc4` / `BC0004` candidate has:

- **21 standard-labeled logical tape datasets** and **64 AWS
  physical tape files**, written on actual MVS 3.8J
  by owner-reported **JOBS 9393–9397**.
- Immutable AWS SHA-256:
  `7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`.
- MVS-only `BT0001` bootstrap and an eight-member `BT0002`
  installer, with executable on-tape JCL profiles `MR10`,
  `NATIVE`, `COMBINED` and shared `COPY`.
  Profile source was read from the restored MVS PDS using
  `IEBGENER`, verified card-for-card, and submitted as the
  actual recipient JCL; Python/WSL/Git/`dspal` is not
  required **inside the recipient MVS installation procedure**.
- Owner-reported recipient preflight **JOB 9398**:
  42 distinct target PDSes absent. The original one-shot run
  halted at a redundant host-side `IEBCOPY` program-label
  check **after** the first MR10 procedure's MVS
  `IEF142I` step evidence; its sealed evidence is retained.
- Separately authorized, **no-replay** continuation preflight
  **JOB 9403** verified the first restored MR10 profile:
  **11 PDSes / 94 members**, with remaining 31 targets absent.
  The owner then approved only the remaining two installations:
  **NATIVE 11 PDSes / 71 members / 10 MVS IEBCOPY steps PASS**
  and **COMBINED 20 PDSes / 150 members /
  19 MVS IEBCOPY steps PASS**.
- Overall **42 restored PDSes / 315 verified members**.
  Actual combined installed `ICINT19` SCALVEC execution
  produced matching `TEST:`, `EXP:`, `RP:`, and
  `CODE=0` **PASS**.
- Both accepted AWS volumes remained unchanged. Original
  `BC0003` SHA-256:
  `6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

**Private immutable evidence retained by the owner:**

- Production: `workarea/ta3-rc4-production/20261123T130731Z-36363`
- Original interrupted recipient (not replayed):
  `workarea/ta3-rc4-recipient/20261123T133542Z-36979`
- Accepted continuation:
  `workarea/ta3-rc4-continuation/20261123T163929Z-37828`

The MVS job numbers not displayed in the supplied terminal
transcripts are preserved in the local evidence and are
**not inferred here**. The assistant has not independently
read these private workarea receipts.

## Qualification and preservation

The MVS test used **fresh isolated namespaces on the existing
MVS 3.8J system** and default site values
`HERC02` / `TSO002`. This qualifies TA.3 installation
acceptance; it does **not** establish a separate
clean-system IPL or every possible site override.
Those requirements remain under **TA.7 —
Clean-Target Integration and Release Acceptance**.

The native-running Cambridge Compiler is **absent**;
no native compiler/self-compilation claim is made.
**TA.6 is N/A for this candidate, not PASS.**
Installed native Core Runtime, BLIB, Coroutine Support and System
Extensions still require TA.5 execution/linkage verification.

**Do not rerun** the consumed TA.2 staging/write/restore,
TA.3 `ta3-rc4-production --run`,
`ta3-rc4-recipient --run`,
or `ta3-rc4-continuation --run`.
Do not mutate either AWS volume, historical source staging,
accepted MVS recipient PDSes, one-shot markers, or evidence.
A future genuinely new experiment requires independent safeguards,
fresh targets and separate owner authorization.

TA.3 closure does not imply TA.4, TA.5, TA.7 or TA.8
acceptance and is **not release-publication approval**.

## Formal TA.4 transition

Per explicit owner direction, **TA.4 — MR10 Kit Compiler Distribution
and Verification is now OPEN / IN PROGRESS**. The formal acceptance
criteria are those already defined in
[milestone-tape-artifact-release.md](milestone-tape-artifact-release.md)
and the owner-approved
[MR10 `EXP:` manual verification decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md).

The new march begins with **read-only review** of the exact RC4
installed MR10 sources, object/load modules, canonical build and
demo JCL, prior MR10 MVS `MRREGRES` evidence, and human sign-off
status. The accepted predecessor `BC0003` MVS
**JOB 9369** already passed its 63 ordered utility/interpreter
steps and 12/12 automated `TEST:`/`EXP:`/`RP:`/`CODE=0`
semantic comparisons; do not re-execute that accepted job.
Earlier 12 case human review did **not** produce an accepted signed
receipt because its final `SIGN` token was not completed.
Full TA.4 sign-off remains open.

See [TA.4 kickoff](ta4-kickoff-20261123.md) for precise
accepted inputs, outstanding acceptance gates and first actions.
