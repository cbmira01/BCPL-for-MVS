# DR.5 — Shared QUERY authority transfer and BCPLQSAM rollback decision proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Source checkpoint:** `1ea630fc8ed1a188d8a7533824006731b41f5d43`  
**Disposition:** PROPOSED — not effective; explicit owner review required.

## 1. Shared QUERY v1 — proposed individual authority transfer

Under the [DR.1 owner decision](dr1-reference-authority-owner-decision-20261125.md),
transfer only the common QUERY v1 public interface from the
[approved R.0 QUERY contract](../../archive/runtime-extensions/runtime-extensions-r0-query-abi-decision-20261021.md)
to chapter 1 of the [Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md).
Other R.0 decisions, package-specific operations, global allocations,
registration/finalization and tool contracts are not transferred here.

| Existing normative clause | Destination in chapter 1 | Reconciliation / evidence |
| --- | --- | --- |
| Common dispatcher, opcode 0, R7/R8/R9, signed R7, word pointer/capacity | Opening paragraphs | All three dispatchers and native calls; one dispatcher normally, exception requires documented approval |
| Already linked/registered; no discovery of absence | Opening and prefix explanation | Selection/exclusion cases 146, 156–158 and installed QSAM JOBs 1261/1263 |
| Side-effect-free except successful caller-vector writes; no hidden init, clock read, I/O, allocation or package state mutation | QUERY paragraph and closing paragraph | All three assembler QUERY branches write only descriptor words and ordinary call workspace; source-observed, not exhaustive side-effect instrumentation |
| Caller-owned accessible storage, no general pointer protection | Opening and closing paragraphs | Source checks null/capacity, not arbitrary nonnull addresses |
| Six-word format 1 prefix, API version matches BCEX, operation bitmap, package-owned flags | Prefix table and explanation | BCPLDEMO (1,1,0,6,1,0), BCPLTIME (1,1,0,6,3,0), BCPLQSAM (1,1,0,6,31,7); all source descriptors API 1.0 |
| Compatible major/minor; implemented opcode bits; unassigned bits zero; >32 documented appended map | Prefix explanation | Version/bitmap declarations reviewed; not a new allocation |
| Append-only compatible extension, full length, no partial prefix, incompatible interpretation needs new format | Prefix explanation; proposed explicit clarification below | Isolated JOB 2206 eight-word test, not an extended descriptor shipped by a maintained package |
| Null/zero size; adequate buffer returns full count; trailing words untouched | Return table | Source and native cases 147–150, 159–163, 170; exact sentinel checks in 163 and 170 |
| Nonnull short including zero -1/no write; unsupported opcode -2; null/nonzero or negative capacity -3/no write; negative argument before shortage | Return table and closing paragraph | Source branches in all three dispatchers; focused negative cases, including exact 163 assertions |
| Ordinary operations package-specific, no imposed common result vector | Closing paragraph | Separate DEMO/TIME count-return and QSAM ordinary vector contracts |

Before effective transfer, make the explicit clarification that a compatible
descriptor preserves the meaning of all six words, reports the entire
length, and requires a new format version for incompatible reinterpretation.
Do not claim an exhaustive register-preservation or complete
cross-package negative matrix. The [R.0 JOB 2206 record](../../archive/runtime-extensions/runtime-extensions-r0-query-job-2206-evidence-20261021.md)
and [DR.5 extension evidence](dr2-extension-manual-migration-20261125.md)
remain evidence authorities. [Native suite manifests](../../../../tests/README.md)
and expected fixtures retain their own authority.

**Recommendation:** approve this bounded transfer after that explicit
clarification. Record the effective revision and exact destination, keep
the historical source contract intact and link it from the current reference.

## 2. BCPLQSAM — primary OPEN failure versus rollback CLOSE failure

This is a separate new normative decision, not an authority transfer.
The [Q.0 public interface](../qsam/bcplqsam-public-interface.md) section 12
already approves -14 for returned explicit CLOSE error, handle invalidation,
uncertain ownership, no blind retry/unsafe free, and generic finalization
before IOFIN/MEMDRAIN (FINISH RC8 on returned error, STOP(n) preserves n).
It does not explicitly settle primary OPEN failure versus secondary
rollback CLOSE error.

The [current assembler](../../../../system-extensions/bcplqsam/bcplqsam.asm)
QCCLEAN saves R7 in QCERRPRI, calls QSMCLS1, and restores the primary status
before return. QSMCLS1 sets closing state 3 before CLOSE; QSCQUAR sets
quarantine state 4, clears the public ID and increments QSQUAR when R15
is nonzero. The rollback exit does not free or recycle that uncertain slot.

**Proposed policy:** on recoverable OPEN failure after successful underlying
OPEN, retain the original primary OPEN/geometry/resource status even when
the rollback CLOSE returns a failure. Publish no handle. Quarantine uncertain
ownership, do not retry CLOSE or free possibly referenced storage, and let
generic finalization report the unresolved error under the existing
FINISH/STOP rule. Do not infer the actual DCB's open/closed state. No new
public status or result-field encoding. A directly requested CLOSE that
returns an identifiable error continues to report -14.

Case 198 verifies injected stage refusal and real rollback CLOSE; case 199
verifies real conditional GETMAIN refusal. Case 200 JOB 1300 exercises
combined injected failure status after a real successful CLOSE, returns -11
rather than the secondary -14, publishes no handle, preserves surviving I/O
and checks quarantine/no repeated CLOSE and expected FINISH RC8. The original
host-parser FAIL receipt is retained; corrected automated review passed
without new JES submission. See the [DR.5 extension ledger](dr2-extension-manual-migration-20261125.md).
These cases are private diagnostic assemblies, not fault injection into the
installed object. Genuine exceptional MVS CLOSE remains explicitly unverified.

**Recommendation:** approve the existing primary-status policy as normative
at its returned-control boundary; retain genuine exceptional CLOSE as a
qualification rather than forcing an MVS failure or reopening accepted tests.
After approval, update reference chapter 5.4 and the provisional assembler
comments without altering instructions or oracles. Keep the Q.0 design
history unchanged pending a separate full QSAM interface transfer.

## 3. Pending other transfers

This proposal does not transfer the language, compiler, Core Runtime,
Base Library, coroutine, registry, package-specific or Project Tools
contracts. Their clause-level mapping and qualification disposition remain
separate DR.5 work. The Global Number Registry, release/configuration
registries, manifests and frozen release documentation retain authority.
No MVS operation, code change, new test number, release action or march
closure is authorized by this proposal.
