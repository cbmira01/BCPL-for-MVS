# Milestone QSAM — Q.2 kickoff (28 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.2 — Fixed logical records**  
**Status:** **OPEN / NOT ACCEPTED**, explicit owner approval on 28 October 2026  
**Previous march:** [Q.1 — Linkage & OPEN/CLOSE skeleton CLOSED](qsam-q1-closure-20261028.md)  
**Starting GitHub implementation:** [main 7f00ff897c94](https://github.com/cbmira01/BCPL-for-MVS/commit/7f00ff897c947d2140e5df6db95a935f18b4de41)

## Objective and boundaries

Implement **byte-accurate READ and WRITE of F/FB logical records** in the existing optional BCPLQSAM System Extension. Preserve **QSAMSVC:200**, the version-1 BCPL word request/result vector ABI, accepted BCEX/BCRG selection and generic finalization, sixteen private handles, and the tested OPEN/INFO/CLOSE foundation. Follow the [BCPLQSAM Public Interface Specification](bcplqsam-public-interface.md) and [approved Q.0 staging/resource decision](qsam-q0-staging-resource-design-decision.md). No new global number or public opcode is required: **READ=2** and **WRITE=3** are already assigned.

## Q.2 deliverables

1. **READ from input F/FB handles:** one logical record per new QSAM GET; preserve data bytes exactly, including nulls, EBCDIC blanks and 0xFF. Report actual logical byte length, without newline, terminator, translation, trim or application-visible block data.
2. **Capacity and private pending retry:** if the caller's capacity is too small, report required record length without modifying its buffer; retain the *entire* record in that handle's private checked stage; retry without another GET, including repeated insufficient retries.
3. **EOF:** return an EOF status distinct from success/error; leave caller data unchanged and continue reporting EOF on repeated READ calls until CLOSE.
4. **WRITE to output F/FB handles:** one logical record per PUT; require the supplied byte count to equal effective fixed LRECL exactly. Reject shorter or longer data before PUT; no silent pad, truncation or translation.
5. **Lifecycle and errors:** reject wrong mode, closed/stale/invalid handles, invalid reserved arguments, inappropriate record format, and invalid size/capacity; release pending records on CLOSE. Propagate recognized GET/PUT return errors according to the existing public contract.
6. **Native MVS verification:** isolated source-controlled F/FB decks, multi-record FB deblocking, first/last record, byte-accurate round trip/copy, empty input, repeated EOF, undersized-buffer retry, boundary records and negative errors. Preserve IFOX/IEWL/GO and native record comparisons.

The owner-approved initial **1024 total private staging bytes per handle** remains the implementation ceiling; F/FB LRECL must lie within the supported effective data bounds, not a claimed universal MVS size limit. Continue the Q.1 fail-closed pre-OPEN geometry policy: explicit F1024 GO reader geometry is proven, missing or contradictory geometry must not be guessed. Production OBTAIN/DSCB recovery is not included in Q.2 by default.

**Out of scope:** variable V/VB/RDW records (Q.3), FBA/SYSOUT/SYSPUNCH-specific record behavior (Q.4), broad release hardening/object promotion (Q.5), and changes to the Cambridge compiler or accepted Core Runtime.

## Design review before implementation

Review the existing assembler's GET/EODAD and PUT call paths, byte/word-pointer conversion, private-stage state transitions, fixed-length validation and ordinary failure results against the approved interface. Update the QUERY supported-operation bitmap **only when** native READ/WRITE are implemented and verified. Discuss any major choice that would change the approved byte semantics or failure ownership with the owner before changing source.

## Deferred Q.1 coverage and Q.2 acceptance gate

The [Q.1 closure](qsam-q1-closure-20261028.md) expressly deferred, rather than passed, its ordinary negative/STOP and full-regression obligations. Fold the known Q1NEG test-caller fix and expected argument/missing-DD/invalid-handle checks, normal FINISH and STOP(8) finalization evidence, and Q.1 lifecycle/output regression into the next consolidated native panel. Continue to track rare failed-OPEN/returned-CLOSE injection, optional omitted-DCB geometry recovery and console-log normalization for later hardening rather than claiming those cases passed.

The **unchanged Q.2 acceptance gate** requires byte-accurate fixed-record READ/WRITE, observed EOF, overflow and invalid-handle tests, and the passing full native baseline regression panel (including its documented expected skip). Previous pre-Q.2 panel results are not a substitute for testing after Q.2 implementation.

Opening Q.2 authorizes its planning scope only. **No JES job, permanent MVS dataset change, object promotion, or Q.2 code modification is authorized merely by this kickoff.** GitHub main remains authoritative; future source changes require owner approval and testing.

**Q.2 — Fixed logical records OPEN / NOT ACCEPTED.**
