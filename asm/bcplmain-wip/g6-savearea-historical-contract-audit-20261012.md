# G6 SAVEAREA: historical contract audit (2026-10-12)

Status: **source investigation, not implementation approval**. Production baseline retained: commit `4db53782e7521ebfa193e41f2ca6c4720ef552f4`, reported 121/121 native regressions passing. No assembler or object-library changes in this audit.

## Primary sources examined

- `richards-bcpltape/sys3/bcpl/libhdr`: G6 = SAVEAREA.
- `richards-bcpltape/bcplib/bcpl/blib`: MAPSTORE, INPROGRAM, VALIDPOINTER, BACKTRACE, ABORT.
- `richards-bcpltape/km10/comacro`: later/different `USERSAVE` macro with `FREEBASE`.
- `richards-bcpltape/km10/bcplmac`: alternative `USERSAVE` with `VECLIST`; **not identical** to COMACRO.
- `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag` and `30-control-data-and-end.asmfrag`: reconstructed BCPLMAIN.

The inspected BLIB source directly references `SAVEAREA` in MAPSTORE, INPROGRAM and VALIDPOINTER. BACKTRACE and ABORT have indirect dependencies via INPROGRAM/MAPSTORE; neither directly reads the SAVEAREA symbol in the inspected definitions.

## Historical location and representation

Both KM10 macro variants define `USA DSECT`, beginning with 18 standard MVS save-area words (72 bytes), followed by BCPL-specific task data. `SAVEAREA` is a **BCPL word address** of the *beginning* of this extended structure. The fields at indices 29 and 48 contain native **byte addresses** (subsequently shifted right two by BLIB).

### Verified key offsets (COMACRO variant)

| Expression / field | Offset from USA (bytes) | BCPL index | Representation and use | Evidence |
|---|---:|---:|---|---|
| standard linkage words | 0..71 | 0..17 | MVS register save/linkage | USERSAVE |
| `LOADLIST` | 116 | 29 | native byte-address head of linked load-module descriptors; zero = empty | COMACRO USERSAVE; BLIB MAPSTORE/INPROGRAM |
| `FREEBASE` | 192 | 48 | native byte address of vector-management area; zero = absent | COMACRO USERSAVE; BLIB VALIDPOINTER |

Offset 116 follows 72-byte save area, 12-byte DATESTR, 10-byte string-name workspace (plus alignment/SDW), 8-byte DWORD, 8-byte DDMEMBER and 4-byte interrupt/error counters. Offset 192 follows the subsequent stream, stack, list, time and task fields. The BCPL expressions corroborate both positions. Final assembler DSECT expansion should be used to cross-check all offsets before implementation.

**Version caveat:** BCPLMAC substitutes `VECLIST` for the COMACRO `FREEBASE` scheme and has differing surrounding fields. Which macro variant matches the precise original SYS3 BLIB build is not fully proven by the currently inspected evidence. Do not merge their layouts.

## BLIB consumer compatibility

| Consumer | Access | Meaning | Consequence with 18F MSVSAVE |
|---|---|---|---|
| MAPSTORE | `P := (SAVEAREA!29)>>2`; then `P!9`, `P!3`, `P!4`, `P := !P>>2` | Byte-pointer load-list head and byte-address node links/extents; high bit of `P!9` marks BCPL module | Out-of-bounds header read; may falsely report a list or traverse invalid storage; potential protection/operation exception |
| INPROGRAM | same `!29` head and node traversal; compares `P!3 <= (N<<2) < P!4` | Tests pointer against dynamically loaded executable extents | Out-of-bounds header read; incorrect validity results or invalid traversal |
| VALIDPOINTER | `SAVEAREA<=N<STACKEND`, then INPROGRAM, then `P := (SAVEAREA!48)>>2`, `!P <= N < P+(P!1>>2)`, `P := P!2>>2` | Storage-region linked traversal; precise node producer/layout requires further validation | Direct OOB read at word 48 if earlier tests fail; possible invalid traversal |
| BACKTRACE | calls INPROGRAM on frame return-address expressions | Validates BCPL frame linkage | Indirect SAVEAREA!29 risk |
| ABORT | calls BACKTRACE and MAPSTORE for diagnostics | Fatal error reporting | Indirect traversal risk during already-failing execution |

Other indirect calls (e.g., WRITEARG invoking INPROGRAM) can expose the same defect. This table covers direct occurrences in the inspected BLIB; a full cross-file consumer census remains an independent task.

## Present BCPLMAIN

`10-bootstrap-and-system.asmfrag`: R13 is changed to point at `MSVSAVE` via `L 1,=A(MSVSAVE)`, and G6 is assigned R13 shifted right two at G-vector byte offset 24. `30-control-data-and-end.asmfrag`: `MSVSAVE DS 18F`.

Therefore the G6 **base-address units** are plausible, but the object at that address has only the standard 72-byte save area and lacks all required extended fields. This is a concrete incompatibility; ordinary passing application regressions do not exercise or resolve it. The current initial-stack bounds used by VALIDPOINTER also require separate attention.

## Risk and proposed bounded next step

1. **Do not call G6 compatible.** Do not read historical fields 29/48 under the existing 18F allocation; they lie beyond its extent.
2. First establish exact COMACRO `USERSAVE` DSECT offsets and decide explicitly which historical version to target. Check related producer layouts for load-list and vector-management nodes; absence of actual allocated nodes is not itself a reason to invent dummy pointers.
3. Next design an extended, named runtime descriptor whose *initial* 18 words preserve MVS linkage, with verified fields at 116 and 192 initialized to zero. This is a **proposal**, not yet an authorization to implement. Confirm any use of static/save-area storage across invocation and reentrancy.
4. Proposed focused source-mode probe: run a native BCPL program that evaluates VALIDPOINTER on a deliberately invalid but aligned word pointer, and separately exercises INPROGRAM outside the main extent; ensure both return false without an abend. Instrument only if needed to confirm the exact G6 backing storage. Preserve the 121/121 regression baseline.
5. Later introduce valid list nodes and producer/consumer contracts for GETVEC/LOAD only when recovered from sources.

## Known unknowns

- Complete historical user-save-area alignment and exact size across KM10 variants.
- Which macro variant directly corresponds to the compiled BLIB in this reconstruction.
- The producer and node format for COMACRO FREEBASE storage blocks and dynamic LOADLIST records.
- Behavior of historical recovery-state fields and whether any must be live before high-level diagnostics are invoked.
- The precise first-frame/LEVEL invariants for safe BACKTRACE traversal.

No production code, object PDS member, or installed regression was modified by this audit.
