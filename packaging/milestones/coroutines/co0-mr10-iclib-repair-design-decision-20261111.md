# CO.0 — Design decision: repair reconstructed MR10 ICLIB coroutine switch

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.0 — Historical Research and Behavioral Contract
**Decision date:** 11 November 2026
**Status:** APPROVED IN PRINCIPLE by owner, 11 November 2026;
candidate implementation and MVS acceptance remain separate gates.

## Decision and authority

Repair the project-reconstructed MR10 `ICLIB` `CHANGECO` behavior to
preserve independent coroutine continuations rather than accepting the
observed restriction to return-compatible switching sites. This is a
deliberate correctness improvement to the reconstruction, not proof of
the absent historical `KM10.COMAIN` interface or implementation.

Owner direction: retain the failing MR10 experiment as evidence; make
a separately reviewable repair decision. The owner subsequently
instructed "Commit, proceed." This approves this design direction
and preparation of a repair candidate. It does not authorize JES
submission, modification of resident MVS members, object promotion,
or closure of CO.0.

## Evidence and original boundary

- The original source remains `mr10-kit-compiler/source/iclib.int`.
- The unmodified counterexample is
  `mr10-kit-compiler/tests/10-coroutines/continuation-divergence.bcpl`
  with `mr10-kit-compiler/jcl/co0-continuation-divergence.jcl`.
- [JOB 5231 evidence review](co0-changeco-continuation-divergence-jes-5231-review-20261111.md)
  records 14/14 zero-RC JES steps, seven interpreted CODE=0 phases,
  but `STAGEDWAIT RETURNED 201` before `ROOT B1 201`.
- The operator subsequently supplied the generated `SVINMAIN` listing:
  STAGEDWAIT's post-call path includes
  `LIG6 K5 SP4 LL499 ...`; `SP4` begins immediately after
  the CHANGECO call and leads into the premature WRITEF.
- The reconstructed `ICLIB` saves outgoing `P!0` in the descriptor
  and resumes via outgoing `P!1` in shared `G!10`. That produces
  incompatible continuation behavior across distinct call sites.
- The original MR10 kit's intended unrestricted CHANGECO contract is
  not proven by recovered primary sources; the reconstructed
  implementation's limitation is independently observed under ICINT19.

## Options

1. **Retain tail-return-only behavior:** smallest change, but retains
   the observed failure when CHANGECO is used with subsequent work.
2. **Keep two permanent implementations:** supports compatibility
   experiments but doubles maintenance and expands tests indefinitely.
3. **Correct the canonical reconstruction after a gated candidate:**
   preferred. Git history, the unchanged failing probe, and recorded
   JOB 5231 output preserve the pre-repair implementation and evidence.

## Candidate implementation architecture — review before promotion

The existing coroutine descriptor has words 0, 1 and 2 and
`P=C+3` as the synthetic first frame. Do **not** add a descriptor
continuation word at `C!3`: it aliases the synthetic frame's `P!0`.

Instead, investigate storing the pointer to the **outgoing CHANGECO
call frame P** in descriptor `C!0`, rather than only `P!0`.
The call frame already records the caller's `P!0` and `P!1`.
On resume, read both fields from that saved call frame and install
the incoming `(P,C)` together, then supply the transfer result.

**First activation requires a coordinated BCPL change:** the
synthetic frame must have a valid frame pointer and an explicit
startup function continuation. The old CREATECO trick deliberately
ran a continuation borrowed from the switching-out coroutine; it
cannot serve as the general corrected contract. A separately
compiled startup function may execute the initial `COWAIT` and
repeat the worker function, preserving existing re-entry semantics.
The existing accepted static MAKECO probe also depends on its own
startup layout and needs an isolated corrected candidate.

The candidate must keep the original three-word descriptor contract,
avoid changing `ICINT19` or the INTCODE instruction set, and preserve
the existing MR10 global assignments for this experimental variant.
**Do not silently overwrite canonical ICLIB, COROUTIN, or accepted
test fixtures before an MVS-verified candidate review.**

## Verification and acceptance gates

1. Preserve original sources and historical evidence, including the
   original JOB 5231 reproduction path.
2. Prepare a separately named ICLIB and BCPL library candidate and
   host-side source/assembly invariants. Test the construction without
   JES where practical.
3. Stage and run only with fresh operator approval. Compare generated
   OCODE/INTCODE and interpreted CODE values, not merely JES RC.
4. The new version of the continuation probe must defer
   `STAGEDWAIT RETURNED 27` until **after** `ROOT B1 201`.
   The previous premature `STAGEDWAIT RETURNED 201` is a failure.
5. Repeat the five accepted MR10 coroutine probes, including
   static-stack first activation, then the existing MR10 panels and
   other affected interpreted workloads. Preserve golden behavior
   or separately review deviations.
6. Only after evidence-backed owner review replace canonical
   `ICLIB` and matching library/startup sources, update manifests,
   and promote a new accepted regression oracle. The original
   failing experiment and original evidence must remain identifiable.

**Disposition:** repair direction approved; candidate not accepted.
CO.0 IN PROGRESS; CO.1–CO.5 NOT STARTED. No native System/370
coroutine implementation is approved by this MR10 decision.
