# Milestone Runtime Extensions — R.4 — IEWL-Driven Extension Selection

**Status:** Investigation approved by owner (22 October 2026); no
replacement implementation, object-PDS installation, or acceptance
result is implied.

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
