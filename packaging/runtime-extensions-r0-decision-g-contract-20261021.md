# Milestone Runtime Extensions — R.0 Decision G approved contract

**March:** **R.0 — Evidence and contract (open)**.
**Decision:** The owner **approved Decision G numerical limits and
numeric diagnostic assignments on 21 October 2026**. This freezes
version-1 design choices for isolated R.0 tests and the later R.1
implementation; it does **not** claim the registrar exists or that MVS
has exercised every check. Decisions A–F and H remain in the
[owner ABI record](runtime-extensions-r0-owner-abi-decisions.md).
The older 40-byte descriptor draft is **superseded**.

## Hard v1 limits

| Element | Accepted maximum / valid interval |
| --- | --- |
| Selected package count `N` | 0–32 |
| Application-required IDs `M` | 0–32 |
| Exports per selected package `K` | 1–8 |
| Dependencies per selected package `D` | 0–16 |
| Registry `BCRG` extent | `28+8*N+8*M`, **28–540 bytes** |
| Descriptor `BCEX` extent | `48+8*K+16*D`, **56–368 bytes** |
| Registry plus all selected descriptors | **12,316 bytes** worst-case (`540+32*368`) |
| Public global index | **G!1–G!699** only if owned and assigned |

`G!0` is reserved global-vector metadata. The current 700-word Core
Runtime global vector makes 699 the present implementation maximum,
**not** a guarantee that any slot is vacant or a permanent historical
limit. Consult [Global Number Registry](global-number-registry.md).
A real no-extension registry has **N=M=0 and exactly 28 bytes**.
A selected package must export at least one entry, but may have no
dependencies. The default remains **one dispatcher export**; 2–8
exports require a documented exception under approved Decision C.
There is no separate restriction on aggregate descriptor bytes less
than the algebraic maximum above.

## Diagnostic identifiers (not MVS return codes)

| ID | Meaning |
| ---: | --- |
| 1001 | Invalid registry independently linked extent/alignment |
| 1002 | Invalid registry magic/version/header/reserved field |
| 1003 | Registry count, calculated size or declared length invalid |
| 1004 | Invalid package independently linked extent/alignment |
| 1005 | Invalid package magic/version/header/reserved field |
| 1006 | Package count, calculated size or declared length invalid |
| 1007 | Invalid or duplicate package identifier |
| 1008 | Invalid or duplicate exported global number or entry address |
| 1009 | Unauthorized global ownership collision |
| 1010 | Required package not selected / missing dependency |
| 1011 | Incompatible package API major or minimum minor |
| 1012 | Dependency-first order violation or dependency cycle |
| 1013 | Invalid or untrusted nonzero finalizer address |
| 1014 | Invalid, duplicate or self-referential dependency record |
| 2001 | Finalizer returned nonzero status |

Reserve diagnostic ID bands **1000–1099** for registration/startup
and **2000–2099** for finalization. Do not confuse these IDs with
internal status values 4/8/12/etc. in the earlier test-only JOBs
2187–2195, with BCPLQSAM's package-level negative errors, or with
JES return codes. The observable future policy is **MVS RC=12 on
startup registration rejection before START**, with zero optional
globals installed. A returned nonzero finalizer keeps the approved
Decision F policy: FINISH yields RC=8, STOP(n) retains `n` and a
2001 diagnostic. Unrecovered abends are not treated as returned errors.

## Defensive validation and deterministic precedence

Validate in this order: (1) independently resolved registry span and
alignment; (2) registry fixed header; (3) registry counts and exact
length; (4) each independently linked descriptor span; (5) its fixed
header; (6) its counts/length; (7) identities and entries; (8) effective
ownership and dependencies, including transitive requirements. Within
a category, report the **first** offending record in linked table order.
Do not publish **any** optional G!N until all selections succeed.

Guard unsigned 32-bit fields **before multiplication**, perform bounded
length arithmetic after count checks, and require exact equality among
calculated length, declared length and externally resolved span. Reject
zero, reversed, misaligned, oversized and incomplete spans before
reading variable entries. A zero finalizer is allowed. A nonzero
finalizer requires a properly aligned linker-resolved, source-trusted
callable target (subject to Decision A's build/link evidence); numeric
alignment alone cannot prove executable ownership. The same limitation
applies to exported callable entries.

Preserve verified legacy BLIB-present G!76 precedence (JOB 2199),
without allowing an optional-package override. Build an actual
per-executable ownership ledger (Decision E), not a list inferred from
headers. A first-error diagnostic requires a startup-safe output path;
**its MVS implementation is still an R.1 design/testing obligation**,
not proof that BCPLIO is available before initialization.

## Testing and evidence

[Isolated R.0 G test harness](../bootstrap-toolchain/probes/r0-g-limits-probe/README.md)
checks host-side binary-layout boundary/negative cases and prepares a
**separately linked IFOX numeric-envelope batch** for MVS. Tests are
**not** a production registrar, cannot establish general pointer safety,
and must not alter accepted BOOT_OBJ members. The actual MVS job must be
observed before it is claimed to PASS. This decision record is approval
of the contract; **R.0 remains open, R.1 not started**.
