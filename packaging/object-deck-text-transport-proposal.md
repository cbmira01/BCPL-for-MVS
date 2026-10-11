# Deferred proposal: reversible MVS object-deck text transport

**Status:** Design note only. No implementation, JCL, object-library mutation,
or change to the WSL-controlled regression panel is authorized.

## Motivation

We may eventually need to export relocatable object modules assembled under
MVS 3.8 into printable files suitable for versioning in Git, then import
those files back into MVS as byte-for-byte equivalent object records for
link-editing. The first candidates are the five installed modules under
`HERC02.BCPL.OBJ` (BCPLMAIN, BCPLBYTE, BCPLAPT, BCPLMEM, BLIB).

## Recommended initial experiment

* Begin with one existing IFOX object module, e.g. `BCPLMEM`.
* Preserve its **binary FB/80 record bytes** exactly, including EBCDIC,
  control bytes, zero bytes, trailing blanks, and ESD/TXT/RLD/END fields.
* Encode each 80-byte record as 160 ASCII hex digits (for example, two
  80-character printable records), plus an unambiguous record framing
  convention. Strictly define text encoding and line endings.
* Export printable text to WSL using the existing Hercules/JES workflow;
  commit the result as a reproducible artifact **alongside**, not instead
  of, authoritative assembler source.
* Provide the inverse MVS decoder, reconstruct a sequential FB/80 object
  dataset, validate all characters, lengths, counts, and checksum, then
  link the restored object using IEWL.
* Require byte-for-byte source/restored record comparison and a live
  assembler/link-edit/regression execution before declaring success.

IFOX OBJECT/SYSGO or DECK/SYSPUNCH can provide object records. IFOX
LIST/ESD/RLD and IEWL MAP/XREF listings are diagnostic displays, **not**
lossless object transport.

## Distinct load-module problem

Load-library members must not be treated as ordinary FB/80 object decks.
Investigate IEBCOPY UNLOAD/LOAD as a separate round-trip path, including
unload dataset framing, PDS directory metadata, and any record-format
requirements. Printable serialization of a load-library unload dataset
is a separate, unproven proposal.

## Constraints and unanswered questions

* Establish actual dataset record formats and utility availability in the
  running TK5 installation before prescribing executable JCL.
* Decide whether a simple hex assembler utility is sufficient or whether
  an existing supported MVS utility or transfer facility provides a proven
  lossless alternative.
* Define ordering, framing, version marker, counts, and checksum so transfer
  corruption cannot silently produce a valid-looking object.
* Keep Git/WSL authoritative; transported binary objects are build
  evidence and optional reproducibility resources, not source truth.
* Do not move the current regression panel into PDS members as part of
  this work.

**Decision:** Preserve this option for future use; defer implementation
until a specific object-export/import requirement arises.
