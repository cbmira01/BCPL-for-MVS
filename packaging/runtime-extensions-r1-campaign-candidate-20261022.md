# Milestone Runtime Extensions — R.1 consolidated acceptance campaign

**Historical status:** This document describes the R.1 candidate and
its original acceptance gate, not the current milestone disposition.
**Superseded 22 October 2026:** R.1 — Generic registration foundation
**CLOSED by explicit owner approval** after the 24-job MVS campaign
and 145 PASS / 0 FAIL / 1 expected SKIP 083 native panel.
See [R.1 closure evidence](runtime-extensions-r1-closure-20261022.md).
R.2 — Selective interoperability is next for planning; R.3 remains separate.

## Purpose and evidence already obtained

One operator command must exercise the candidate and preserve an independent
JES record for every case. Existing MVS evidence: JOBs 2226/2228 passed
empty/selected registrations; 2232 passed no-output FINISH; 2233–2246
passed integrated diagnostics 1001–1014 at GO RC=0012; JOB 2247 passed
finalizer error diagnostic 2001 at GO RC=0008. The old S322 rejection
failures in 2229/2230 were corrected by preserving R10 around IOFIN.

The current campaign re-executes **24** integrated jobs on temporary
IFOX/IEWL objects: two positive cases, 15 diagnostic IDs, three real
collision owners (application G!1, installed BLIB G!76, Core Runtime
G!30), and four two-package FINISH/STOP(7) reverse-finalizer cases.
It then launches the established native regression 00..145 with a
**temporary R.1 BCPLMAIN / RGINIT / empty BCPLREG overlay**, not the
accepted `BOOT_OBJ(BCPLMAIN)` and not a production-only regression.

## Source-controlled execution; no deployment bundle

The following command is valid **only after these files have been
explicitly reviewed, committed to GitHub main with owner approval, and
pulled into the local repository**:

```sh
git pull --ff-only
python3 tools/bootstrap/run-r1-acceptance --execute
```

Do not use ZIPs, unpack commands, installer scripts, blind repository
rewrites, or assumptions about the local clone state. The new workflow
requires direct, ordinary tracked scripts in their canonical folders.
All compiled application candidates, generated JCL and results are
created in `workarea/`, never under `BOOT_OBJ` or `BOOT_DEVOBJ`.
The official dataset manifest governs the actual read-only PDS name.

The run creates `workarea/runtime-extensions-r1/acceptance/<UTC run ID>/`
containing `SUMMARY.md`, `results.json`, job-number manifest, run-scoped
compiler assembler outputs in `generated/`, all 24 JCL decks in `jcl/` (credential-sensitive; 0600), per-job summaries,
full reports, native regression-case outputs and a transcript. A failed
case does not suppress independently runnable later cases. A preflight
or compilation failure produces an explicit failure summary.

Only return the resulting `SUMMARY.md` initially; raw reports remain
on the operator's machine for selective follow-up.

## Acceptance gate verification

The candidate R.1 adapter records **all** imported CG370 application
and installed BLIB global writers, plus the enumerated explicit native
Core Runtime global stores, in a private 700-byte origin bitmap:
bit 1 application, bit 2 BLIB, bit 4 Core Runtime. It keeps bits for
previous writers when a later writer overwrites the same G slot.
RGINIT checks the bitmask **and** the effective initialized G value.
The owner-collision jobs independently verify actual attribution
for G!1 (application), G!76 (BLIB) and G!30 (Core Runtime).
The Core Runtime writer census is exact and source-guarded; unexpected
changes fail closed during candidate generation.

Link preparation checks BCRG begin/end and BCEX finalizer/dispatcher
addresses are actual `A(SYMBOL)` relocations referring to exported
`ENTRY` symbols in the selected source objects. Arbitrary aligned
numeric finalizers are rejected by the build guard. The deliberate
runtime negative fixture 1013 is a narrowly approved exception.
The MVS verifier also matches corresponding linker symbol owners in
IEWL MAP/XREF, not just the diagnostic RCs.
**This is source and link provenance, not general runtime protection
against malicious binary descriptors**; changing that assumption
would require a separate ABI/security design decision.

The full campaign report separates five gates: registration/diagnostics,
origin-ledger ownership, FINISH/STOP finalizer lifecycle, source/link
provenance, and the fresh R.1 native regression. Each must PASS before
the report can say READY FOR OWNER REVIEW. Otherwise it is BLOCKED or
FAIL and returns a nonzero exit status. A `--skip-regression` run cannot
pass the complete acceptance gate.

The host checks verify 26 enumerated native startup writers (including
the conditional G!76 fallback), source card bounds, and explicit
provenance rejection. Only **actual MVS JOB results** prove integration.

## Boundary and authority

The campaign does not itself close R.1, authorize R.2, or promote any
accepted runtime object. The owner must review the actual evidence
and explicitly approve the R.1 gate disposition. R.2 remains Selective
interoperability; R.3 remains Packaging and acceptance.
The separate full Cambridge compiler FORMTREE/DEBUGINT G!150 conflict
remains unresolved and is not silently declared fixed by this work.

Only tracked GitHub `main` files are suitable for this operation.
There is **no ZIP file and no installer script**. Until approval to
commit the candidate, no operator command should be run.
