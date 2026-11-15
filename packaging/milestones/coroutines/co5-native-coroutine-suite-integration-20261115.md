# CO.5 — Native coroutine regression suite integration

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Status:** IN PROGRESS (host integration stage only)
**Baseline:** GitHub main ff48f6d12bdff59d4108d4f9a52b59f532fa68f5
**Date:** 15 November 2026

## Change boundary

Added fifth native regression suite `coroutines`: cases 177–189, retaining
all 177 previously assigned native case IDs, expected SKIP 083 and BCPLQSAM
device-opt-in 175–176. Coordinator includes five native suites plus MR10 and
MR10-probes, seven total. Individual named tests reuse the accepted CO.2–CO.4
candidate-native Cambridge/IFOX/IEWL/GO drivers. The six CO.4 batch scenarios
select one case at a time; no three-case batch amplification.

Each fixture references a canonical accepted BCPL source and exact ordered
JES output oracle. Python dispatch validates a complete zero-RC IFOX/IEWL/GO
step receipt and independent compiler job IDs; raw evidence stays in workarea.
No existing native regression case is changed and no canonical candidate BCPL,
assembly, permanent globals, public ABI or installed MVS PDS member is changed.

## Checks actually performed (host only)

- Bundled installer: 4 host unit tests passed; fail-closed anchor replacement,
  exact base revision and 64-file staging tested in synthetic checkout
- Coroutine native adapter: 5 host unit tests passed; source/ID validation,
  malformed and duplicate oracles, IFOX/IEWL/GO receipts, independent compiler
  jobs, and one selected batch case rather than an entire batch
- All 13 referenced canonical candidate BCPL sources verified present on
  GitHub main at the baseline revision
- Eight edit anchors checked against GitHub main; no MVS submission
- Bundle overlay: 56 files, 13 fixture identities and exact output oracles;
  packed transport verified roundtrip before Git tree staging

**Evidence limits:** These checks do not constitute a native MVS PASS.
The full native suite (13 cases), MR10 and other project suites, clean-room
reconstruction, installed-object promotion and release readiness are pending.
Do not claim CO.5 closure until real JES evidence and owner acceptance.

## Native verification gate

After operator updates to the new main revision and grants JES execution:
`tools/tests/run-project-regressions --run --suite coroutines --profile production --progress`

Run with retained per-case evidence, then investigate only actual BCPL,
IFOX, IEWL and GO/JES failures. Do not promote BOOT_OBJ or use destructive
clean-room rebuild under this integration action.

## Native MVS result — 15 November 2026

The operator ran all 13 numbered coroutine cases on GitHub `main` at
`53a4e4feebfec3f41223288416d2f0a3011bb77a` and reported **13/13 PASS** with coordinator RC=0.
This supersedes only the earlier statement that native-suite execution
was pending. See [CO.5 integrated native PASS](co5-integrated-coroutine-native-pass-20261115.md).
Remaining full-project, clean-room and release gates are not accepted.
