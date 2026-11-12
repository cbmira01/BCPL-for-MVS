# CO.0 — Native coroutine ownership, descriptor and stack decision briefing

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.0 — Historical Research and Behavioral Contract (**IN PROGRESS**)  
**Source checkpoint:** GitHub `main` at `88002022da5316f6d048893f6fc49bfacccfbd1b`  
**Evidence class:** SOURCE-OBSERVED and design alternatives, **not** approved CO.1 ABI or native test results.

## Purpose and governing boundary

Prepare the owner review of **CO0-U09** without beginning CO.1 —
Native ABI and Stack Architecture. The [milestone](milestone-implement-coroutine-support-for-native-compiler.md)
requires an owner-reviewed native design before implementation. The
[CO.0 descriptor audit](co0-u04-descriptor-validation-and-source-safety-audit-20261112.md)
shows that reconstructed MR10 routines may read a descriptor before
establishing membership; this does not settle a safe native policy.

The [accepted CO0-U08 oracle matrix](co0-u08-interpreted-to-native-oracle-matrix-20261112.md)
provides **40/40** exact interpreted records across JOBS 5331–5333.
That evidence does not establish native register preservation, descriptor
validity or native stack isolation.

## Direct native source and contract findings

| Item | Verified source/contract observation | Implication / remaining decision |
| --- | --- | --- |
| Compiler calling convention | [Native runtime contract](../../architecture/runtime-contract-v1.md): R5 current BCPL frame; R6 BCPL return; R7–R9 argument/results; R4 restored from 0(R5); R11 generated-code system-vector base | CO.1 must inspect actual CG370 call/return and live-register sequences before specifying the saved context; no fixed save set is inferred here |
| Current BCPLMAIN stack | [BCPLMAIN](../../../bootstrap-toolchain/asm/bcplmain.asm) allocates global vector + **65,536-byte** tested work stack + **256-byte** clearance; sets `DYNWORK`, `STKLIM`, `DYNEND` and paints the original stack | One presently installed stack does **not** imply separate per-coroutine stack bounds; avoid treating the clearance as available worker stack |
| Checked procedure entry | [Stack-check contract](../../architecture/stack-check-contract.md): generated entry carries callee frame-size inline after `BAL 14,60(11)`; checked code must use the full callee size, not only the call-site displacement | CO.1 needs a coroutine-specific bound and safe-limit strategy compatible with the checked-entry mechanism |
| Memory manager | [BCPLMEM](../../../bootstrap-toolchain/asm/bcplmem.asm) uses MVS GETMAIN/FREEMAIN for vectors; explicitly states **static singleton allocator, not reentrant**; exposes native GETVEC/FREEVEC and private MEMBIND/MEMDRAIN/MEMSTAT | Cooperative scheduling alone does not prove safe allocation during a switch or while a coroutine owns memory; define scheduling, ownership and terminal cleanup |
| Native global namespace | [Global Number Registry](../../architecture/global-number-registry.md) preserves historical LIBHDR and existing allocations; runtime contract places **G6 SAVEAREA**, **G87–88 GETVEC/FREEVEC**, while MR10 uses CHANGECO:6, CURRCO:7, GETVEC:87 and CREATECO..RESUMECO:91–95 | MR10 slots are **not** the native mapping; registry collision review must precede any allocation |
| Coroutine history | [Historical audit](co0-historical-source-audit-20261110.md) identifies historical KM10 members but not `KM10.COMAIN` | An unrecovered native switching algorithm cannot be described as historical fact |
| Control-flow validation | [MR10 library](../../../mr10-kit-compiler/library/coroutines.bcpl) has no null/membership check before `CALLCO` or `RESUMECO` target dereference; `DELETECO` dereferences nonzero inactive target before membership scan | An equivalent native public API must either document live-handle preconditions or design validation *prior* to the first descriptor dereference |

These findings support **separation of concerns**, not a particular
implementation: a machine-dependent Core Runtime switch, a BCPL
coroutine library where evidence permits, and native BCPLMEM rather than
the MR10 private arena allocator. No specific new CSECT, global number
or descriptor word offset is assigned here.

## Decision alternatives for owner discussion

**A — Native descriptor validity**

- **A1. Documented valid-live-descriptor precondition:** Small
  implementation surface; null, arbitrary and stale pointers outside
  the contract unless explicitly guarded. Does not satisfy a broad
  safe-invalid-handle API.
- **A2. Managed handles with membership/lifecycle validation:**
  Runtime-owned registry and an explicit lifecycle model. Must validate
  before unsafe dereference; generation/reuse questions remain. It
  increases complexity and does not magically make arbitrary unreadable
  addresses safe.

**B — Stack ownership and safe limits**

- **B1. One runtime-managed, independently allocated stack per
  coroutine:** Fits the observed need to retain nested frame chains;
  requires checked-entry bound selection, initial stack frame, current
  stack metadata, cleanup and high-water reporting for each context.
- **B2. A managed shared arena partitioned into fixed stack regions:**
  Offers predictable limits but requires documented partitioning,
  fragment/reuse rules and an independent checked-entry bound for
  each region. Sharing *the same live frame region* is not acceptable.

**C — Context switch, lifecycle and integration**

- Decide the actual machine state live across generated BCPL calls,
  including correct R5/R6/R4/R11 treatment, from CG370 and native
  execution evidence rather than a guessed full-register save.
- Decide who owns the active-context record, per-context
  `STKLIM`-equivalent values and initial continuation before
  implementing CHANGECO.
- Define whether normal worker return permits re-entry, as in
  accepted interpreted JOB 5324, and when storage may be reclaimed.
  Do not treat an inactive parent or finished worker as necessarily
  dead without an explicit lifecycle rule.
- Decide how the native callable exports bind to the approved Global
  Number Registry and the existing compiler-generated registration
  trailer. `GLOBAL` declarations, IEWL inclusion and actual global
  registration are distinct checks.

## Native test gates after owner approval — not yet executed

1. Inspect/save CG370 generated calling sequences and validate register
   assumptions using an **isolated native IFOX/IEWL/GO probe**.
2. Verify independent stack initialization, boundary equality and
   overflow/refusal without weakening the native checked-entry path.
3. Port the three CO0-U08 BCPL programs against the approved native
   header/stack initializer; compare only exact ordered program
   records (8, 14 and 18), not ICINT19 cycle counts or its 12 JES steps.
4. Exercise valid busy-target and ordinary deletion paths; only test
   invalid/stale inputs that the approved native validity contract
   explicitly supports. Capture source revision, JES step RCs, SYSOUT,
   generated code and runtime diagnostics.

The next action is **owner choice and CO.1 review**, not implementation
or routine JES submission.

## 12 November 2026 — JOB 5325 independent JES recheck

At Git `main` revision
`88002022da5316f6d048893f6fc49bfacccfbd1b`, the operator
re-ran `tools/mvs/job-summary 5325`. It reported JOB **5325**
(`BCCO0VAL`) SUCCESS, highest RC=0000, **14/14** JES steps RC=0000
(IFOX00 ASM, IEWL LKED, five IEBGENER staging steps, three RUNMOD
compile steps, three RUNMOD code-generation steps and RUNMOD execution),
and **job-summary shell RC=0**. CPU 1.11 sec, SRB 0.16 sec, SYSOUT 892.
This is a **recheck of the accepted interpreted job's JES receipt**, not
a rerun of the program or additional native test. The program's
previously accepted valid-descriptor oracle retains its existing
INTERPRETED-MVS-TESTED classification.

**Disposition:** CO.0 IN PROGRESS, CO.1–CO.5 NOT STARTED. No
native global allocation, new descriptor ABI, runtime modification,
regression enrollment, installed MVS dataset change or march closure.
