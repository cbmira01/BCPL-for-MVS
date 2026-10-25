# Milestone QSAM — Q.0 integrated native 16-DCB batch

**PREPARED, NOT MVS EXECUTED.** Q.0 — Reconnaissance & contract remains **IN PROGRESS**. Q.1 — Linkage & OPEN/CLOSE skeleton remains **NOT STARTED**.

## Purpose and scope

The accepted standalone Q.0 JOBs 2183–2186 held sixteen F1024 QSAM DCBs and sixteen separately acquired 1024-byte stages at GO REGION=256K. Runtime Extensions R.1 independently proved the BCEX/BCRG v1 finalizer ABI, reverse order, and FINISH/STOP return policies. This small integration probe tests their coexistence **inside a native BCPL executable**, using read-only installed Core Runtime and Base Library objects.

The test-only `Q0PROBE` BCEX descriptor exports temporary G!299 (not production G!200 or a new Global Number Registry allocation) and a conventional MVS finalizer. The native BCPL caller invokes only its private operation 1. It conditionally allocates sixteen stages, OPENs sixteen QSAM input DCBs and checks one F1024 record from each. All sixteen are intentionally still open on FINISH or STOP(8). The accepted generic `RGFINI` is expected to invoke the package finalizer, which CLOSEs all sixteen DCBs in reverse order, releases stages, and checks accounting.

The already-tested Q.0 standalone F1024 writer supplies two records to each of sixteen temporary `&&` datasets. The first records have unique headers and end-byte sentinels. The demoted Cambridge compiler (interpreted INTCODE under ICINT19) generates the native assembler used for each BCPL caller. No new historical compatibility is inferred.

## One consolidated operator batch

Run the host-only checks first; these never contact MVS:

```sh
python3 -m unittest discover -s bootstrap-toolchain/probes/q0-integrated-16-dcb -p 'test_*.py' -v
bash bootstrap-toolchain/probes/q0-integrated-16-dcb/run-batch.sh --check
```

After local MVS availability, execute the approved disposable jobs together:

```sh
bash bootstrap-toolchain/probes/q0-integrated-16-dcb/run-batch.sh --execute
```

This compiles both callers, generates authenticated JCL under ignored `workarea/qsam-q0-integrated`, submits `Q0NFIN` followed by `Q0NSTP`, saves each JES job ID/summary/full report, and validates required step return codes and **live GO** markers. It fails rather than suppressing absent or abnormal evidence.

| Profile | GO RC | Expected actual GO output |
|---|---:|---|
| `finish` | 0000 | `Q0 NATIVE 16 OPEN READ PASS`, `Q0 NATIVE BCPL FINISH PASS`, `Q0 FINALIZER FINISH 16 CLOSE FREE PASS` |
| `stop` | 0008 | `Q0 NATIVE 16 OPEN READ PASS`, `Q0 NATIVE BCPL STOP PASS`, `Q0 FINALIZER STOP 16 CLOSE FREE PASS` |

All assembly, writer link, production-runtime link, and writer GO steps must be RC=0000. Review actual IEWL MAP/XREF for the selected `Q0TDESC`, `Q0TDISP`, `Q0TFIN`, the 44-byte BCRG and existing Core Runtime `BCPLMAIN`/`RGINIT`. The report verifier checks marker and CSECT presence but does not independently prove every MAP byte or MVS storage-release outcome. Retain full operator JES and any ABEND diagnostics.

The `finish-512` and `stop-512` variants are prepared **diagnostic fallbacks** to generate with `make-jobs.py PROFILE --generated workarea/qsam-q0-integrated/{finish|stop}.asm` if a 256K region test fails. Run separately and retain the distinct evidence; never describe 512K as a successful 256K configuration.

## Safety and evidence boundary

All newly assembled objects and linked loads are temporary. `BOOT_OBJ` is read-only and `BOOT_DEVOBJ`, `EXT_OBJ`, `EXT_ASM`, `EXT_MAC`, and all accepted installed BCPLDEMO/BCPLTIME objects are unchanged. No PDS purge, resident install, compiler change, QSAMSVC implementation or production regression addition is made.

GETMAIN refusal before OPEN takes a checked private-stage rollback path. This does **not** establish generic CLOSE-error recovery: the returned-CLOSE uncertain-ownership policy remains approved and QSAM exceptional outcomes must not be misrepresented as ordinary returns. Public INFO, QUERY, handles, pending READ, and all production lifecycle tests are allocated to existing implementation marches after Q.0 gate acceptance.

See [the consolidated gate matrix](../../../packaging/qsam-q0-consolidated-gate-review.md). A passing probe is **not** approval to close Q.0 or begin Q.1.
