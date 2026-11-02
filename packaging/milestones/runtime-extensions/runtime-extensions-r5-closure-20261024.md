# Milestone Runtime Extensions — R.5 owner closure (24 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Runtime Extensions  
**March:** R.5 — Optional Extension Packaging and Regression  
**Owner disposition:** **CLOSE R.5 — Optional Extension Packaging and Regression**  
**Decision:** The owner explicitly approved closure in the project conversation following review of the clean-room evidence, including the stated raw IEWL-report audit limitation.  
**Official source:** GitHub `main`; the operator's MVS installation and run logs are evidence, not canonical project source.

## Decision and accepted scope

**R.5 is CLOSED.** The owner accepts the Git-controlled and MVS-installed `BCPLDEMO` optional System Extension, its public interface, BCX package-selection catalog/macros, the source/installed-mode regression infrastructure, and the demonstrated clean-room reconstruction and 00–158 native production regression result.

Acceptance covers the interpreter-hosted **demoted Cambridge compiler** running under `ICINT19`, the reconstructed native Core Runtime/Base Library, and selected optional-extension linkage on MVS 3.8J under Hercules. It **does not** claim reconstruction or self-hosting of the separate native Cambridge compiler, historical full BCPL compatibility, dynamic runtime package loading, package auto-discovery, or transitive dependency selection.

This owner decision leaves **R.4 — IEWL-Driven Extension Selection** pending *formal* closure. It preserves the already-closed R.0–R.3 scope and their respective records. It is not authority to create R.6 or to declare the expanded Milestone Runtime Extensions fully closed while R.4 is outstanding.

## Exact source chronology

One clean-room reconstruction crossed a controlled source-state update:

1. **Initial checkout:** `7fff89f17767770b0a3a3dc9c11f0890918e3cc0`. The operator cleared `workarea/`, purged/recreated 28 managed MVS datasets, reconstructed `ICINT19`, rebuilt the demoted Cambridge compiler, and installed the native production runtime and Base Library.
2. **Final installation/regression checkout:** [`00379e002c934ea16b06bc275b187bcf1cffa9f0`](https://github.com/cbmira01/BCPL-for-MVS/commit/00379e002c934ea16b06bc275b187bcf1cffa9f0). The operator pulled this revision before installation of `BCPLDEMO`; it adds `BOOT_JCL(R5DINST)`, the managed `dspal submit` path and accompanying checks. The operator's five offline installation tests and canonical 12-member JCL check passed. There was no further Git update before payload JOB 5108 and the installed-mode full regression.
3. **Post-test documentation revision:** [`d38cf60d3c3eb3dcb1c37f04a999db1053eae81e`](https://github.com/cbmira01/BCPL-for-MVS/commit/d38cf60d3c3eb3dcb1c37f04a999db1053eae81e) was pulled **after** the successful regression. This later current-checkout SHA **must not** be cited as the revision executed for the native panel.

Accordingly the operator demonstrated a clean-room **Git-based reconstruction with a documented mid-run update**, not a strictly single-revision end-to-end run. The JCL migration did not alter the previously assembled Core Runtime sources.

## MVS construction and verification evidence

The operator-supplied transcript documents these MVS payload jobs (MVS dates **24 October 2026**):

| Activity | Payload JOB | Observed result |
| --- | ---: | --- |
| Delete the 28 managed PDSes | 4659 | All 28 deleted |
| Allocate the 28 managed PDSes | 4688 | All 28 recreated; `dspal stat` confirmed attributes |
| Build `ICINT19` | 4873 | ASM, LKED and SAVEOBJ RC=0000; IFOX severity 0 |
| MR10 language demos | 4879 | SUCCESS, highest RC=0000 |
| MR10 BCPL demos | 4882 | SUCCESS, highest RC=0000 |
| MR10 regression suite | 4885 | SUCCESS, highest RC=0000 |
| Build demoted `CAMBCOMP` | 5073 | 22 interpreted COMP/CG steps and PACKCOMP RC=0000 |
| Build/install Core Runtime plus empty `BCPLREG` | 5081 | Seven IFOX and seven IEBGENER steps RC=0000; IFOX severity 0 |
| Build/install historical Base Library `BLIB` | 5085 | Six steps RC=0000; IFOX severity 0 |
| Assemble/install/read back/compare `BCPLDEMO` | **5108** | Four steps RC=0000; record comparison completed |

The first manifest population wrote 156 tracked members, with 12 expected generated members absent. After `tools/bootstrap/prepare-bootstrap --with-trnilrg`, the second population wrote 168 members, including generated demoted-compiler sources. The generated SHA-256 inventory is operator-local at `workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json`.

### `R5DINST` — original installation report

The authenticated `dspal submit BOOT_JCL R5DINST` was launcher **JOB 5107**, payload **JOB 5108** at MVS 24 Oct 2026 01:06:51.

| Step | Program | RC |
| --- | --- | --- |
| `ASMDEMO` | `IFOX00` | `0000` |
| `PUTDEMO` | `IEBGENER` | `0000` |
| `READBACK` | `IEBGENER` | `0000` |
| `VERIFY` | `IEBCOMPR` | `0000` |

The report shows **zero IFOX flagged statements**, **severity zero**, **10 object records punched**, and IEBCOMPR's **10 records compared**. The verified destination is `HERC02.BCPL.EXT.OBJ(BCPLDEMO)`; the `PUTDEMO` step performs the permanent member installation and `READBACK`/`VERIFY` compare the object against the assembled temporary records. The original evidence was recovered from the operator's transcript; **no additional R5DINST reinstall was required**.

### Final managed PDS inventories

The operator's `dspal ls` evidence confirms:

| PDS alias | Accepted member inventory |
| --- | --- |
| `BOOT_OBJ` | `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLIO`, `BCPLRGS`, `BCPLREG`, `BLIB` (exactly eight) |
| `BOOT_DEVOBJ` | Empty |
| `EXT_OBJ` | `BCPLDEMO` |
| `EXT_MAC` | `BCXPRE`, `BCXCAT`, `BCXPOST` |
| `EXT_ASM` | `BCPLDEMO` |
| `EXT_SOURCE` | `DEMOHDR` |
| `BOOT_JCL` | Twelve canonical members, including `R5DINST` |

The accepted package uses the separate optional-extension object PDS and does not require a package-specific change to `BCPLMAIN` or `BCPLRGS`.

## Native installed-mode regression acceptance

The operator used the explicit installed-mode settings:

```sh
export BCPL_R5_EXTENSION_MODE=installed
export BCPL_R5_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
export BCPL_R5_MACRO_DSN=HERC02.BCPL.EXT.MAC
tools/bootstrap/run-production-regression 0 158
```

**Accepted operator result: 158 PASS, 0 FAIL, one expected SKIP 083, TOTAL 159.** The full transcript shows all **158 distinct expected PASS case numbers**, including **146–158**; the only skipped case is the known production-profile source-instrumentation case **083**. All pre-existing cases **00–145** retained their expected outcome.

The verified test runner invokes `tools/checks/check-r5-extension-report.py` on each R.5 case's saved **actual JES report** before issuing PASS. Its gate checks the IEWL cross-reference table, required `R0APP`, `BCPLMAIN` and `RGINIT` control sections, selected/absent `DMODESC` and `DMODISP`, expected `BCPLREG` length (28, 36 or 44 bytes as appropriate), and zero IEWL entry address. Accordingly, the 146–158 PASS results include **automated IEWL MAP verification**, not merely the expected BCPL output markers.

## R.5 exit criteria disposition

| Owner-approved deliverable | Acceptance basis |
| --- | --- |
| One-object `BCPLDEMO` with descriptor and dispatcher | Git-controlled assembler package; successful IFOX installation and MVS test |
| Separately managed optional object installation | `EXT_OBJ(BCPLDEMO)` installed by JOB 5108, read-back/IEBCOMPR RC=0000 |
| MVS-native `BCXSEL`, `BCXREQ`, known-package catalog | Installed `EXT_MAC` members; resident-macro selected-mode regressions passed |
| Public header, contract and programmer documentation | Git-controlled `DEMOHDR`, package and installation documents |
| Independent native cases 146–158 | All 13 individual cases PASS in the full transcript |
| Individual/range/full-runner integration and regression preservation | Full production panel 00–158: 158 PASS, 0 FAIL, 1 expected SKIP |
| Installed-member selection, not source-mode only | Installed-mode environment and resident `EXT_OBJ`/`EXT_MAC` verified |
| Clean Git-based MVS reconstruction | All 28 PDSes recreated, binaries rebuilt; two explicit Git states documented |
| JES/IFOX/IEWL/GO evidence | Build/installation jobs, original IEBCOMPR receipt, actual-run harness' JES/MAP gates; raw per-case map audit limitation below |

## Limits and retained obligations

- **Raw IEWL MAP/XREF/GO reports for every R.5 regression were not independently reviewed.** They remain operator-local in `workarea/native-regression/`; the per-case automated JES/IEWL verifier passed. This distinction is expressly accepted by the owner for R.5 closure.
- The full original `R5DINST` JES report and its ten-record binary comparison **were reviewed**. Do not conflate the two audit levels.
- A physical failed-install rollback was not tested. The accepted recovery procedure is deletion/recreation of approved optional-package PDSes from the Git-backed source, reassembly, reinstall, comparison and retesting. The owner previously chose no backup PDS or member-level rollback system.
- The closure does **not** authorize a future write to `BOOT_OBJ`, `BOOT_DEVOBJ`, or `EXT_OBJ` without the applicable owner approval and operating procedure.
- The accepted ABI remains **BCEX/BCRG v1**, the registry supports explicitly selected/required known packages, and `BCXCAT` currently catalogs `BCPLDEMO`. This is not a general dynamic loader or independent site-package discovery mechanism.
- R.4 technical PASS evidence remains intact, but **R.4 formal closure is a separate pending owner decision**. R.0–R.3 remain closed in their accepted scopes. No additional Runtime Extensions march is established by this record.

## Final owner disposition

**R.5 — Optional Extension Packaging and Regression: CLOSED, owner-approved.**

The owner's explicit **“Approve”** followed review of the complete R.5 closure proposal, reconstruction transcript, JOB 5108, full-panel regression evidence, and acknowledged raw-IEWL-audit limitation. No new JES jobs, PDS writes, compiler/runtime changes, or test execution is implied by this documentation closeout.
