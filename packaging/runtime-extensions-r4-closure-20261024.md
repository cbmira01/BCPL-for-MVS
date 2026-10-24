# Milestone Runtime Extensions — R.4 owner closure (24 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Runtime Extensions  
**March:** **R.4 — IEWL-Driven Extension Selection**  
**Owner disposition:** **CLOSE R.4 — IEWL-Driven Extension Selection**  
**Authority:** Explicit owner approval in the project conversation after review of the investigation, JOBs 3720 and 3722, failed JOB 3721, and the known-package limitation.  
**Official source:** GitHub `main`; prior JES reports and proof objects remain historical evidence.

## Formal decision

**R.4 is CLOSED.** Its assignment was an investigation and technical recommendation, not a mandate to implement a replacement registrar. A negative conclusion regarding unrestricted IEWL-only discovery is a valid outcome under the original [R.4 investigation gate](runtime-extensions-r4-investigation.md).

The owner accepts the following conclusions:

1. **IEWL `INCLUDE` by itself did not provide a mechanism to enumerate arbitrary, previously unknown BCEX v1 descriptors.** Combined two-CSECT objects simplify packaging; known-symbol `WXTRN` references and the investigated common/CSECT mechanisms do not furnish an extensible, append-only descriptor inventory. Do not extrapolate this tested finding to an unqualified assertion about every conceivable linker mechanism.
2. **The approved practical mechanism is MVS-native IFOX macro/PUNCH selection for known packages.** `BCXSEL` selects/registers an extension; `BCXREQ` additionally marks it as directly required. `BCXCAT` supplies the known package's IEWL member expression and BCEX begin/end symbols. The macros punch matching `INCLUDE` records and construct the existing BCRG version-1 `BCPLREG` registration object.
3. **Preserve BCEX/BCRG v1, `BCPLMAIN`, `BCPLRGS`, and the owner-approved R.0 A–H contract.** No compiler modifications, host-generated production registry, independent startup registrar or incompatible ABI are approved by closing R.4.

The implementation/installation packaging and subsequent full production acceptance of this mechanism belong to the separately **CLOSED R.5 — Optional Extension Packaging and Regression**, not a retroactive expansion of R.4's experimental gate.

## Acceptance evidence

| Test or event | Git revision / job | Actual observation |
| --- | --- | --- |
| MVS-native `BCXSEL`/`BCXREQ` macro, PUNCH and IEWL matrix | `b2a1411bd05c4c60e96185f459bcc7ffbaabf8b3`, **JOB 3720** | All 21 EXEC steps completed with the intended return codes; all five selection profiles behaved as specified |
| Initial integrated compiled BCPL test | `764ac6648d7a99e28c8ad4f74d729815014fabfe`, **JOB 3721** | Compiler, IFOX and IEWL RC=0000; GO **ABEND S0C1** because IEWL entered `BCPLMAIN` at `B0` instead of the compiled client |
| Corrected integrated MVS-native compiled BCPL test | `40655b004c027f82c5eab6d6fb9d182e013c6128`, **JOB 3722** | All 11 EXEC steps RC=0000; `ENTRY R4APP` selected address zero; actual BCPL `START` called the G!203 `BCPLDEMO` dispatcher and printed `R4 BCX BCPL START PASS` |

The five JOB 3720 selection profiles and their observed BCRG extents were:

| Profile | Requested selection | `N` selected | `M` required | Observed GO RC (BCRG bytes) |
| --- | --- | ---: | ---: | ---: |
| 0 | No packages | 0 | 0 | 0028 |
| A | `BCXREQ BCPLDEMO` | 1 | 1 | 0044 |
| B | `BCXREQ R2TESTB` | 1 | 1 | 0044 |
| S | `BCXSEL BCPLDEMO`; `BCXREQ R2TESTB` | 2 | 1 | 0052 |
| X | S plus `BCXREQ BCPLDEMO` | 2 | 2 | 0060 |

Nonzero GO return codes in these standalone profiles measure a successful BCRG byte length; they are not execution failures. Selection-to-required upgrade does not duplicate the IEWL `INCLUDE` or descriptor pair.

In JOB 3722 the linker MAP/XREF included `BCPLMAIN`, `RGINIT`, `DMODESC`, `DMODISP`, and the 44-byte `BCPLREG` object. IFOX-generated BCRG references to `DMOBEG`/`DMOEND` relocated correctly, and the compiled BCPL application used the registered dispatcher. The zero-entry correction was made in test JCL, without changing the compiler's generated code.

Primary retained evidence:
- [JOB 3720 macro/PUNCH/IEWL report review](runtime-extensions-r4-job-3720-evidence-20261023.md)
- [JOB 3721 failure and analysis](runtime-extensions-r4-job-3721-evidence-20261023.md)
- [JOB 3722 compiled-BCPL integration acceptance](runtime-extensions-r4-job-3722-evidence-20261023.md)
- [MVS-only experimental source and run instructions](../bootstrap-toolchain/probes/r4-bcx-macros/README.md)

## Technical limits and future ownership

- The demonstrated method resolves **known catalog entries**. It does not automatically discover an extension never entered in the catalog, or compute transitive dependency selection.
- `R2TESTB` at G!299 was **test-only**; no production global allocation or user-facing package is granted.
- R.4 alone did not validate every negative/failure case, independent User/Site Library catalogs, or final installation in permanent object PDSes. Those are not R.4 exit requirements. The later R.5 installed-mode tests and full production panel are accepted under the distinct [R.5 closure](runtime-extensions-r5-closure-20261024.md).
- The completed R.4 tests used temporary object/load datasets and read-only production objects; no permanent object installation or production ABI modification is attributed to R.4.
- Potential independent User/Site Library catalogs, automatic dependency expansion, and arbitrary-package discovery remain **future design questions**, not unfinished R.4 marches. No R.6 is established.
- No MVS resubmission, source change, compiler/runtime update or PDS write is required to record this closure.

## Relationship to the milestone

**R.0, R.1, R.2, R.3, R.4 and R.5 are all individually CLOSED.**
The previous R.0–R.3 milestone closure and R.5 owner closure remain intact.

**Formal closure of the expanded Milestone Runtime Extensions as a whole is a separate owner decision**, not implicit in approving R.4 alone. The milestone index may now state that every approved march is closed, while reserving the final milestone-level disposition for that decision.

## Final owner disposition

**R.4 — IEWL-Driven Extension Selection: CLOSED, 24 October 2026, owner-approved.**
