# Milestone Runtime Extensions — R.0 Decision A, trusted-link stage 1

**Owner approval:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Disposition:** **stage 1 isolated MVS panel PASSED, JOBs 2207–2216** (ten profiles). See the [actual execution record](runtime-extensions-r0-decision-a-jobs-2207-2216-evidence-20261021.md). The separate installed-object identity check remains open.
**Next march:** **R.1 — Generic registration foundation (not started)**.

The owner approved the staged Decision A plan: first obtain trusted,
independently relocated registry/descriptor/callable-target link evidence;
then separately select a binary-safe method to compare a temporary
rebuild with installed `BOOT_OBJ` records **without replacing either**.
The accepted [Decision A contract](runtime-extensions-r0-owner-abi-decisions.md)
is unchanged. The [R.0 gate review](runtime-extensions-r0-gate-review-20261021.md)
continues to list current-object provenance and other R.0 obligations.

## Stage 1 — prepared experiment, subsequently accepted MVS evidence

Tracked [trusted-link probe](../bootstrap-toolchain/probes/r0-trusted-link-probe/README.md)
assembles four *independent* IFOX inputs: `R0ATST` validator,
`R0AREG` (symbols `R0RB/R0RE`), `R0APKG` (`R0PB/R0PE`)
and `R0AFUN` (`R0FUNC/R0FIN`). IEWL uses `NCAL,LIST,XREF,MAP`
into a temporary `&&` load module. No `BOOT_OBJ`, `BOOT_DEVOBJ`,
`BCPLMAIN` or compiler object is modified.

The generator checks CSECT/symbol-source ownership before writing an
authenticated JCL deck. Its local manifest records SHA-256 of the four
rendered assembler inputs and an exact source Git revision. Those
hashes are **source provenance**, not proof of installed object bytes.

Host verification completed **11 Python tests** and **10** credential-free
synthetic profiles, each **263 JCL cards**; shell syntax and Python
source compilation also passed. Actual IFOX, IEWL MAP/XREF, relocation,
GO/QOUT and finalizer-pointer checks **subsequently PASSED under MVS in JOBs 2207–2216**; full JOB 2207 MAP/XREF was examined. The literal per-profile source-hash manifest values were not supplied for independent comparison; see the [execution record](runtime-extensions-r0-decision-a-jobs-2207-2216-evidence-20261021.md).

| Profile | Intended internal Decision G result |
| --- | --- |
| valid, goodhook | 0 |
| regzero, regunal | 1001 (registry extent/alignment) |
| regvers | 1002 (registry fixed header) |
| reglen | 1003 (registry length) |
| pkgbound | 1004 (descriptor extent) |
| pkgvers | 1005 (descriptor fixed header) |
| pkglen | 1006 (descriptor length) |
| badhook | 1013 (untrusted finalizer target) |

Negative profiles either alter a test driver's observed registry
pointer, change a registry descriptor pointer or alter bounded
static headers; they **never purposely dereference an unknown
arbitrary MVS address**. A wrong, missing or duplicate source symbol
fails pre-submit guard tests. This does not establish security against
hostile object code, external overwrites or forged runtime pointers.

## Original MVS acceptance conditions (completed for test-only scope)

Start with **valid** only, then inspect its actual IEWL MAP/XREF
relative CSECT addresses, lengths and external symbol ownership
against the tracked source manifest. Require ASMD/ASMR/ASMP/ASMF/
LKED/GO RC=0000 and the **unique actual QOUT record**
`R0 A VALID LINK PASS`. Only then proceed with other profiles.
An internal 1001/1004/etc expected rejection produces GO RC=0000
**only if the validator matched the expected identifier**.
The GO record must originate from runtime QOUT, not IFOX listing text.
After owner execution, record actual JOB numbers, step codes,
source hashes and relevant IEWL MAP/XREF evidence separately.
Do not claim PASS from a generated deck.

## Stage 2 — [design review](runtime-extensions-r0-decision-a-stage2-design-20261021.md), not implemented

Establish first whether a binary-safe **MVS-side** FB/80 record-by-record
comparison against an independently rebuilt temporary object is
available. Ordinary `dspal cat/get` intentionally prohibits
binary object members; text-mode retrieval or a print-oriented
IEWL map is **not** a byte-identical comparison. Reconcile the
17 October clean-room source/build ledger with subsequent installed
object changes before asserting current `BOOT_OBJ` member identity.
No installation, replacement or binary round-trip is approved by this
stage-1 preparation.

**Status:** Isolated stage-1 MVS panel complete; stage-2 method is a proposal. R.0 open; R.1 not started.
