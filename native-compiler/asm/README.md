# Native System/370 assembler runtime sources

This directory holds the **one maintained source per native runtime module**:

| Canonical Git file | CSECT / responsibility |
|---|---|
| [`bcplmain.asm`](bcplmain.asm) | BCPLMAIN bootstrap, termination and service dispatch |
| [`bcplio.asm`](bcplio.asm) | Independent BCPL character-stream / QSAM interface |
| [`bcplmem.asm`](bcplmem.asm) | Runtime memory services |
| [`bcplbyte.asm`](bcplbyte.asm) | Byte operations |
| [`bcplapt.asm`](bcplapt.asm) | Argument vectors and stack support |

**Current BCPLMAIN source:** `bcplmain.asm` contains the unchanged D6
candidate that was accepted with dynamic-stream M5.5 as DEVOBJ(BCPLM6).
Further BCPLMAIN development belongs in this file, not in another
`bcplmain-dN-candidate.asm` beside it. Keep other modules on their
canonical paths as well.

## Canonical Git source = canonical MVS source member

`config/dspal.yaml` maps only five `NATIVE_ASM` source members, each
matching the basename of the canonical assembler file above.
For example, `bcplmain.asm` populates `NATIVE_ASM(BCPLMAIN)`.
**BCPLM6, BCPLM7 and BCMWIP are no longer manifest-managed sources.**
Earlier variants remain under [`history/`](history/) in Git.

The canonical `bcplmain.asm` is the accepted D6/M5.5 candidate source.
Source population alone does not change an object library. However,
the existing `NATIVE_JCL(BLDBMAIN)` **would now assemble D6 into
`NATIVE_OBJ(BCPLMAIN)` if submitted**. Such production promotion has
not been authorized; do not execute BLDBMAIN without a separate decision.

The optional historical `build-dev-bcplm6.jcl` reads the canonical
`NATIVE_ASM(BCPLMAIN)` and writes only `NATIVE_DEVOBJ(BCPLM6)`.
It is **not in the manifest**; stage its JCL explicitly only when
reproducing the accepted M5.5 development profile. The versioned
DEVOBJ object name remains for regression compatibility and does
not imply a second assembler source.

The accepted M2.1 D7 source is retained as
[`history/bcplmain-d7-candidate.asm`](history/bcplmain-d7-candidate.asm).
Its stack-overflow RC=0012 differs from D6's RC=0000 and it is not
populated by the current manifest.

Earlier D3–D5, pre-D6, and WIP sources are retained in
[`history/`](history/). The WIP fragments remain in
[`bcplmain-wip/`](bcplmain-wip/) for historical reconstruction; they
are not the source of new BCPLMAIN development.

The obsolete standalone M1-era `*-probe.asm` experiments and matching
JCL decks were removed after the 00..145 regression and focused M4/M5
verification became the retained tests. Git history preserves the
older experiments. M4.2 and M5 verification under `native-compiler/probes/`
and `tools/checks/` remain available.

Run `python3 tools/checks/check-bcplmain-canonical.py` to check the
manifest/source relationship and IFOX card formatting without installing
or running any MVS program.

For the authoritative clean-room build and candidate reproduction see
[`packaging/clean-room-mvs-reconstruction.md`](../../packaging/clean-room-mvs-reconstruction.md).
