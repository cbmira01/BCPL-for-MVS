# Cambridge runtime components and observability — architectural note

Status: **design discussion and historical-evidence inventory**, 12 October 2026. No implementation decision, production-source change, PDS promotion, or new ABI is authorized by this note.

## Why record this

Regression 083 verifies teardown by instrumenting temporary assembler source copies to count returns from `FREEMAIN`. Its expected output is `42` followed by `V=2 M=1`: two vector-release paths in `MEMDRAIN` and one combined global/stack-release path in BCPLMAIN. The counter proves execution returned from those macro expansions; it does **not** independently prove MVS storage-manager success. The MEMBIND-compatible source/object probe passed on TK5 on 12 October 2026 using `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1`.

Installed production objects in `HERC02.BCPL.OBJ` are already assembled and have no counter symbols or generic interception interface. Consequently 083's **installed-PDS mode remains deliberately excluded** pending a genuine mechanism for observing the same installed objects. No test should be relabeled PASS merely by substituting instrumented objects without disclosing that substitution. See `bootstrap-toolchain/regression/083-instrumented-storage-reclamation/README.md`.

## Historical component inventory: evidence versus inference

The surviving Cambridge `MAKELIB`/BCPLMAC material, as summarized in the BCPLMAIN reconstruction notes, indicates a multi-member native runtime/object library:

| Name | Evidence status / role |
| --- | --- |
| `BCPLMAIN` | Historical machine-code runtime entry; initial environment, system services, shutdown. Reconstruction currently in `asm/bcplmain-wip.asm`. |
| `BLIB` | Historical BCPL-language library routines; link-edit object resource in our implementation. |
| `$IOS$` | Historical object-library member, plausibly I/O services; precise calling interface and boundaries **not yet recovered**. |
| `PM` | Historical object-library member; **postmortem/diagnostics is a plausible interpretation**, not an established complete contract. Verify its source, member, and callers. |
| `$LOAD$` | Linkage-editor-extracted member from BCPLMAIN, plausibly dynamic loading; contract pending. |
| `$BLOCK$` | Linkage-editor-extracted member from BCPLMAIN, possibly block I/O; contract pending. |
| `$TPUT$` | Linkage-editor-extracted member from BCPLMAIN, plausibly TSO TPUT/TGET services; contract pending. |
| `BCPLMEM` | **Our reconstruction-specific** independently assembled GETVEC/FREEVEC/MEMDRAIN/MEMBIND allocator; **not** asserted as an original Cambridge library member. |

The fact that `$LOAD$`, `$BLOCK$`, and `$TPUT$` were carved out by link-edit from BCPLMAIN is significant: a historical object-library member need not correspond to an independent original source module.

Other historical diagnostic contracts visible in the surviving BCPL context include `STACKHWM`, `MAPSTORE`, `BACKTRACE`, `USERPOSTMORTEM`, `ABORT`, and use of `SAVEAREA` and loader bookkeeping. BCPLMAC also describes STAE/SPIE structures and I/O control blocks. These establish that inspection, recovery and postmortem operations matter to the original environment, **not** that a general event-stream observer already existed.

## Design question: does observability belong in PM?

**Working hypothesis:** PM may be the appropriate architectural owner for diagnosis, trace collection and reporting, more faithful than adding a new permanent top-level library member called `BCPLOBS`. But the expansion and exact historical duties of `PM` must be verified first. The question remains open.

Distinguish **event producers** (BCPLMAIN, BCPLMEM, ultimately loader, I/O and recovery) from an **observer/consumer** (possibly PM). An independently assembled IFOX module can record events without using the BCPL stack or global vector during teardown. A BCPL routine can consume/query recorded information while the BCPL environment is valid, but is a poor low-level shutdown callback after its workspace has become unsafe.

Neither simply linking an IFOX observer nor linking a BCPL procedure exposes internal `FREEMAIN` events. Runtime code must contain explicit, documented observation points or a validated external tracing mechanism.

## Future verification opportunities

| Area | Potential observations | What a test could establish |
| --- | --- | --- |
| GETVEC/FREEVEC/MEMDRAIN | attempts, outcomes, list-head changes, outstanding blocks, free-return events | accounting, order, leak/double-free diagnostics |
| BCPLMAIN exit | ordered teardown, resources still outstanding, completed release attempts | correct lifecycle, including abnormal exits |
| Stack | checks, limit faults, measured high-water | stack policy and capacity |
| LOAD/UNLOAD | module acquisitions, relocations, imported-global changes, releases | loader lifecycle and rollback on failure |
| I/O: $IOS$, $BLOCK$, $TPUT$ | OPEN/CLOSE, DCB/stream lifetimes, error paths | resource ownership, cleanup |
| Recovery/PM | SPIE/STAE entries, abnormal conditions, postmortem sequence | diagnostics and recovery behavior |
| Global-vector installation | bindings, changes and uninitialized-global detections | module/runtime integration |

Carefully distinguish **attempt**, **service returned**, **return code indicates success**, and **independently corroborated OS effect**. Counters alone should not be described as proof of successful storage release.

## Proposed architectural properties (NOT settled implementation)

1. Preserve historical compiler-facing BCPLMAIN linkage, global slots and semantics; label any extension as reconstructed/optional.
2. Favor a small machine-level event ABI, initially IFOX, with explicit event IDs, register preservation, calling convention, initialization, shutdown, and error/no-op behavior.
3. Do not assume that a permanent global-vector slot is available: the current user/runtime namespace is not fully partitioned and some runtime globals sit above G99 (e.g. G150 DEBUGINT).
4. Ordinary programs must work correctly when observation is disabled or absent; instrumentation must not become a mandatory dependency or affect allocation/cleanup correctness.
5. Avoid BCPL callbacks during final teardown, reentrancy into storage or I/O allocators, observer allocations inside release hooks, recursive logging and any dependency on already freed workspace.
6. Prefer clear optional link-time or runtime activation with low overhead. Decide how the same installed production objects can be observed **before** claiming installed-object 083 acceptance. An unresolved external observer reference in ordinary programs would be an unacceptable accidental dependency.
7. Keep test-only source instrumentation as an independent cross-check of the observer itself.
8. If PM proves to be a purely postmortem formatter, consider PM as a consumer of a smaller recorder rather than conflating PM with all instrumentation mechanics.
9. Scope production-facing facilities to useful stable counters and diagnostics; retain invasive event tracing as explicitly enabled engineering functionality. No compiler changes should be required merely to observe runtime services.

## Research and implementation gates

- Locate original `MAKELIB` member lists, `PM` implementation/objects, calls and documentation; explicitly classify established facts versus interpretation.
- Inspect `$IOS$`, `$LOAD$`, `$BLOCK$`, `$TPUT$` actual exported contracts before assigning observer event types.
- Define a minimal observer ABI and failure-isolation rules on paper, including treatment of MVS return codes and assembler register/base conventions.
- Decide how a **production** BCPLMAIN+BCPLMEM object pair supports optional diagnostics without requiring an observer at ordinary link-edit.
- Prototype with the two 083 events; test observer disabled, enabled, and failing; verify with existing source instrumentation.
- Require real installed-PDS execution with unchanged installed objects before removing the 083 exception.
- Only broaden to loader, streams, stack and recovery once their functional contracts are established.

## Near-term sequencing

Do not interrupt the current full `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1` 124-test acceptance panel. The observer is a **subsequent architectural investigation**, not a prerequisite to accepting the current independently linked allocator source-mode milestone. Installed PDS promotion remains governed by the existing gates.

## Source-mode external BCPLMEM full-panel acceptance (12 October 2026)

Operator-reported run of `BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 tools/native/run-regression` completed **124 PASS, 0 FAIL, 124 TOTAL**, covering regressions 00 through 123 inclusive. This includes 083's independent-instrumentation path and 122/123's G6!48 compatibility and automatic publication. This is the completed source-mode external-allocator milestone, **not** evidence that newly built BCPLMAIN/BCPLMEM members have been installed and exercised from `HERC02.BCPL.OBJ`. The installed-object 083 observation exception remains. No new PDS promotion is authorized solely by this result.
