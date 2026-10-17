# BCPLIO dynamic streams — design rationale

**Decision baseline:** owner-approved M0, 16 October 2026. **Disposition:**
implemented and scoped by the formally accepted M5.5 milestone on
17 October 2026. Historical M0 text:
[original accepted contract](https://github.com/cbmira01/BCPL-for-MVS/blob/2164a4ef163c9d757c5b2f5d37c95481839287c5/docs/Milestone-BCPLIO-dynamic-stream-M0-contract.md).

## Architecture and ownership

BCPLMAIN is responsible for bootstrap, G-vector installation,
FINISH/STOP orchestration and core runtime services. The independent
BCPLIO CSECT owns character streams, stream selection, active
descriptors, QSAM DCBs and record buffers, and cleanup. Existing BCPL
calling conventions and GLOBAL numbering are unchanged. This is a
character-stream facade over QSAM, **not** a general-purpose record-access
library, VSAM interface, or dynamic dataset allocator.

## Five durable M0 decisions

1. **Stable handle identity.** Opaque word-address control records are
   never recycled during one program run. Closing retires a handle and
   releases its larger descriptor/DCB/buffer. A stale handle cannot
   silently designate a newly opened stream; retired records may be
   reclaimed on final termination. Cumulative opens therefore consume
   some storage.
2. **Duplicate FIND identity.** Repeating FINDINPUT/FINDOUTPUT for the
   same normalized DD name and direction while open returns the same
   live handle; a close followed by reopening establishes a new handle.
3. **DD-name normalization.** The application supplies a counted BCPL
   string of 1–8 valid MVS DD characters. Lowercase becomes uppercase;
   names are compared as EBCDIC, space-padded to eight bytes. Invalid,
   empty or overlong names are rejected rather than truncated. JCL
   allocates the DD; FIND does not enumerate allocations.
4. **Returned-control failures.** Ordinary unsuccessful FIND operations
   return zero and leave stream selection unchanged, with cleanup where
   control returns. The runtime cannot promise to recover from MVS
   abends on unrecoverable OPEN/GET/PUT/CLOSE paths.
5. **Historical stream behavior.** FB80 input right-trims EBCDIC blank
   padding and synthesizes character 10 at record boundaries; RDCH
   returns -1 at EOF. FB132 output is independently buffered, with
   record emission and length-limit behavior established by regression.
   Trailing input blanks remain an acknowledged limitation.

M0 considered the ICINT19 DYNFIND/DYFALLOC path a conceptual reference,
not an ABI-compatible implementation. Implementation and failure
boundaries were validated in later marches, not at M0 design approval.

## Governing references

- [Accepted current runtime contract](BCPLIO-dynamic-runtime-contract.md)
- [QSAM and JCL responsibility boundary](BCPLIO-JCL-QSAM-stream-contract.md)
- [Final milestone acceptance](Milestone-BCPLIO-dynamic-stream-final-acceptance.md)
- [Milestone progression and evidence](Milestone-BCPLIO-dynamic-stream.md)

This document records design intent and rationale, not a new or broader
acceptance assertion.
