# Milestone Runtime Extensions — R.4 — IEWL-Driven Extension Selection

**Status:** **R.4 CLOSED by explicit owner approval, 24 October 2026.** The original investigation was approved 22 October and the MVS-native macro/PUNCH refinement was approved 23 October. See the [formal closure and technical disposition](runtime-extensions-r4-closure-20261024.md). No compiler/runtime ABI replacement or permanent PDS write is implied by R.4.

## Objective

Investigate whether ordinary MVS 3.8 IEWL `INCLUDE` statements can
select self-describing optional object members and make their BCEX v1
descriptors reliably visible to the generic startup registrar **without
assembling an application-specific `BCPLREG` table**. The intended user
experience is a simple linkage editor selection, such as
`INCLUDE EXTLIB(BCPLDEMO)`, where `EXTLIB` is an illustrative DD name.

## Existing decisions protected

R.0–R.3 and their owner-approved closure remain accepted, including
BCEX/BCRG version 1; the ownership ledger; API version and dependency
validation; transactional registration before `START`; and reverse-
order finalization. Accepted R.3 behavior uses an application-specific
BCRG and temporary MVS objects. Persistent `BOOT_OBJ`/`BOOT_DEVOBJ`
installation remains **DEFERRED**. No changes to `BCPLMAIN`, production
`BCPLRGS`, or compiler source are authorized by this investigation.

GitHub `main` at initial review: `123de7930df37f49bbd7c950b40ce3f00d3bb3d5`
(source consolidation after the accepted R.3 campaign). JOB 3417
assembly-check success is reported in the handoff; a *fresh native
regression of that consolidated source* is not established by the
materials reviewed here. Do not conflate R.3 acceptance at `a246063`
with source-consolidation acceptance.

## Candidate mechanisms

1. **One combined object:** Assemble BCEX descriptor and dispatcher
   in two CSECTs, stored as one optional object member. Good candidate
   for easier packaging, but does not itself enumerate descriptors.
2. **`WXTRN`:** A reference to a *known* descriptor symbol may resolve
   when the module is explicitly included without automatically
   calling a library member when it is absent. Test actual IFOX/IEWL
   semantics; this does not scale to completely unknown packages.
3. **Common/CSECT organization:** Contemporary IBM documentation says
   same-named ordinary CSECTs are not accumulated; later ones are
   bypassed. Same-named common areas use the largest area. Neither
   mechanism, by itself, yields an append-only descriptor list.
4. **Other documented IEWL mechanisms:** Investigate only with a
   specific, period-correct reference; no arbitrary memory scan, hidden
   compiler convention or utility that generates a registry is assumed.

## First experiment

The independently executable
[`iewl-optional-discovery`](../bootstrap-toolchain/probes/iewl-optional-discovery/README.md)
probe tests 0/A/B/A+B using BCPLDEMO (G!203) and test-only R2TESTB
(G!299). It checks combined CSECT inclusion, descriptor layout,
IEWL relocation, and resolution of known weak externals. A positive
outcome only establishes selective *known-name* discovery, not a
complete extensible registration mechanism. Evidence must include
IEF/IEWL/GO results, not only host-side generated JCL.

## Gate before further development

Review actual MVS results and the scalability limitation. Only if a
**documented and reproducible** method can discover arbitrary selected
BCEX descriptors should a new registrar design be proposed. Otherwise
record the limitation and retain the accepted BCRG mechanism, or seek
owner approval for the smallest viable alternative. Dependencies,
missing extensions, duplicate globals, finalizer order and omitted
BCPL globals require separate live tests before claiming a
replacement is acceptable.

## Completion criterion

Deliver a technical recommendation identifying the exact IEWL/IFOX
mechanism, proof results, compatibility with BCEX v1 and R.0 A–H,
and the minimum future changes. A negative finding is valid.
No production code may change merely because the investigation passes.

## Owner-approved MVS-native BCX macro candidate (23 October 2026)

The owner rejected a WSL/Python/host-side application-build tool and
approved a **test-only MVS-native** IFOX macro/PUNCH experiment.
The short programmer interface is `BCXSEL package` or `BCXREQ package`;
MVS assembler prefix/catalog/postfix sources produce the existing BCRG
version-1 `BCPLREG` object and matching IEWL `INCLUDE` cards.

The [source and standalone MVS-only test JCL](../bootstrap-toolchain/probes/r4-bcx-macros/README.md)
cover no extensions, A only, B only, selected-only A plus required B,
and upgrading a selection to required. The macro/PUNCH/IEWL candidate **PASSED JOB 3720** (23 October 2026),
all 21 steps with expected results. See the [JOB 3720 evidence](runtime-extensions-r4-job-3720-evidence-20261023.md).
Integrated JOB 3721 (23 October 2026) compiled and linked all
inputs at RC=0000 but GO **ABEND S0C1**: IEWL chose `BCPLMAIN`
at offset `B0`, bypassing the unnamed compiled client at zero.
The test-only JCL exports R4APP from the anonymous client CSECT
and specifies it explicitly to IEWL. JOB 3722 (23 October 2026)
**PASSED**: all eleven EXEC steps RC=0000; IEWL entry 0; the native
BCPL START verified BCPLDEMO G!203 and printed the expected marker.
See [JOB 3722 evidence](runtime-extensions-r4-job-3722-evidence-20261023.md). See the
[test-only MVS-native candidate](../bootstrap-toolchain/probes/r4-bcx-macros/r4-bcx-integrated-mvs.jcl).
The first catalog knows BCPLDEMO and test-only R2TESTB; this does not
claim discovery of unknown packages or automatic transitive dependencies.
No production BCPLMAIN/BCPLRGS, BCEX/BCRG ABI, or persistent MVS object
library is changed. Prior R.0-R.3 closure remains intact.

## Technical recommendation after JOB 3722 (23 October 2026)

IEWL INCLUDE alone does not enumerate entirely unknown package
BCEX descriptor pairs. The documented WXTRN and common/DXD/CXD
experiments did not produce an automatic, extensible descriptor list.

The owner-approved alternative has now been demonstrated on MVS:
short BCXSEL / BCXREQ statements select *known* packages through an
MVS-resident catalog, IFOX generates both BCRG v1 and PUNCH-based
IEWL INCLUDE cards, and the accepted BCPLMAIN/BCPLRGS startup
registers an actual BCPLDEMO package (JOB 3722).

Recommendation: retain BCEX/BCRG v1 and the accepted generic
registrar. Treat the macro method as a proven concise known-package
selection workflow, not as arbitrary package discovery. Automatic
dependency selection, independently developed User/Site Library
catalog entries, and production deployment remain distinct decisions.
No runtime or compiler changes were necessary. R.4 remains OPEN
until the owner formally disposes of the investigation.

## Final owner disposition — 24 October 2026

The owner explicitly **CLOSED R.4 — IEWL-Driven Extension Selection**
after considering the original negative IEWL-only discovery finding,
JOB 3720's five-profile macro/PUNCH/IEWL PASS, JOB 3721's documented
ENTRY-related S0C1, and JOB 3722's successful native BCPL startup.

The accepted technical recommendation is to preserve BCEX/BCRG v1
and BCPLMAIN/BCPLRGS while using the MVS-native BCXSEL/BCXREQ
known-package catalog mechanism. Independent unknown-package
discovery and transitive dependency selection are not claimed and
are not outstanding R.4 exit criteria. No new JES job was needed.

See [R.4 owner closure](runtime-extensions-r4-closure-20261024.md).
The earlier "R.4 remains OPEN" statement above records the state
*before* owner disposition; it is superseded by this closure.
R.5 is also CLOSED under its [separate accepted scope](runtime-extensions-r5-closure-20261024.md).
