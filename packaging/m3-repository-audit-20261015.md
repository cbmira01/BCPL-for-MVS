# M3 repository and manifest review — 15 October 2026

**Scope:** repository layout, manifest consistency, executable/tool entry points, authoritative JCL, operator documentation, and readiness for a complete clean-room MR10-to-native rebuild.

## Audit results

| Area | Finding | Disposition |
| --- | --- | --- |
| Managed dataset manifest | 24 logical datasets: 9 `MR10_*`, 9 `CAMB_*`, 6 `NATIVE_*` | Consistent with accepted M3 topology |
| Text mapping paths | 151 manifest source-to-member mappings; all corresponding paths found in Git tree at audit | No missing mapped source paths |
| Native JCL authority | 13 `BOOT_JCL` mapped JCL bodies reside in `bootstrap-toolchain/jcl/` | Correct |
| Production M3 JCL | `CAMBBLD`, `BLDBMAIN`, `BLIBBLD`, `BLDDEVA`, `BLDDEVB`, `BLDDEVI` | Reconciled and exercised on TK5 |
| Rebuildable binaries | `BOOT_INTCODE`, `BOOT_OBJ`, `BOOT_DEVOBJ`, `MR10_OBJ`, `MR10_LOAD` are not text-populated | Build, do not migrate |
| Production/dev acceptance boundary | `BOOT_OBJ` has accepted main/memory/BLIB; `BOOT_DEVOBJ` has service candidates | Preserve separation |
| Optional diagnostic JCL | `CG370DB` retained old `SOURCE/LOAD/INTCODE` DSNs | Reconciled to MR10 + NATIVE; **not yet tested live** |
| Host obsolete tooling | Deleted build-cambridge and build-blib in prior M3 marches; additional source bootstrap and one-shot relocation helpers were stale | Retired `tools/native/compile-bootstrap`, `packaging/finish-tools-refactor.py` |
| Regression driver | Old fallback selected `compile-bootstrap`; M3 wrapper already selects `compile-mvs` | Fallback corrected to `compile-mvs` |
| Operator documentation | Root README and tools/config/packaging entry points referenced earlier paths, incomplete build status or dataset counts | Updated to accepted M3 and clean-room runbook |
| Full native regression | Operator ran full 124-test panel after reconstructed M3 builds | **123 PASS, 0 FAIL, 1 expected SKIP (083)** |

## Canonical clean-room procedure

Use [**clean-room-mvs-reconstruction.md**](clean-room-mvs-reconstruction.md) for the complete ordered command sequence, including clean disposable `workarea/`, protected manifest-only PDS purge, new allocation, manifest population, interpreter version 19, MR10 interpreted suites, demoted Cambridge stages, native compiler and runtime rebuild, and all native regressions.

This procedure does not use the `CAMB_*` PDSes, although manifest-based init creates them as reserved empty resources. The *single complete destructive sequence* has not yet been executed from start to finish after its consolidation. That is the remaining independent reproducibility check; this audit is not a substitute for that live test.

## Items explicitly outside current M3 acceptance

1. **Optional CG370 diagnostic rebuild**: `BOOT_JCL(CG370DB)` now has correct dataset references but needs separate generated `CGAD` through `CGED` source staging from `workarea/bootstrap-cambridge/demoted-diag/` and a future live run if diagnostics are needed. It is **not** a prerequisite for `CAMBCOMP` or the 124-test panel.
2. **Historical source-mode regressions**: the accepted installed-object regression mode passes. Older source-instrumented and opt-in experimental test routes may still refer to pre-refactor paths. Keep them outside M3 acceptance unless separately audited and exercised; regression 083 is deliberately skipped for this reason.
3. **Dataset portability**: the manifest supports installation-local overrides, but numerous authoritative job bodies use literal `HERC02` dataset names. The clean-room procedure is validated for the canonical TK5/HLQ environment, **not** arbitrary HLQs.
4. **Installed JCL freshness**: `dspal populate all` or explicit `dspal put` must be performed after tracked JCL changes. The stale-JCL episode during development demonstrates that clean return codes alone are inadequate for verifying dataset target selection.
5. **Native Cambridge compiler/M4**: no `CAMB_*` artifact population or native execution of the compiler is claimed.

## Recommended closure checkpoint

On the operator's TK5 host, follow the new clean-room runbook once from a freshly cleared `workarea/` and an intentionally purged managed PDS set; capture the Git revision, interpreted completion codes, JOB summaries, inventories and final 123/0/1 native result. Do not rerun destructive purge merely to refresh documentation.
