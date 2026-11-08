# Tape structure inspection — available tools and future design

**Date:** 8 November 2026
**Status:** Existing `hetmap` utility verified for labels on the accepted
scratch AWS image. Other documented modes and any new project-native
tape-map tool remain to be tested/design-reviewed. No new milestone.

## Existing tool: Hercules HETMAP

Our TK5 container includes Hercules `hetmap` version `4.9.1.0-SDL`.
The operator used `hetmap -l` with RC=0 on a real 16 KiB AWS image.
It identified the volume and IBM standard dataset labels, including
VOL1, HDR1, HDR2, EOF1, EOF2, the sequential dataset name, VOLSER and
the 25-block EOF1 count.

Hercules documentation describes these HETMAP reporting options:

| Option | Documented purpose |
| --- | --- |
| `-a` | All label and file information (default) |
| `-l` | Labels only; verified in our environment |
| `-f` | Tape physical-file summary, blocks and sizes |
| `-d` | Dataset-oriented summary |
| `-t` | TAPEMAP-compatible text |
| `-h` | Installed utility usage/help |

Because only `-l` was executed in the observed test, **confirm the
actual installed `hetmap -h` output** before relying on the other
options on the local Hercules build. The utility is a *read-only
examiner of an existing image*, not a tape creation or mount command.

Example operator inquiries from the repository root (no JES):

    docker exec mvs38j hetmap -h
    docker exec mvs38j hetmap -a /tk5/tape/bcpl-pdstest-20261108-01.aws
    docker exec mvs38j hetmap -f /tk5/tape/bcpl-pdstest-20261108-01.aws
    docker exec mvs38j hetmap -d /tk5/tape/bcpl-pdstest-20261108-01.aws

Do not run these while a tape image is actively being written; the
report may capture a partial state. The `mvs-state/tape/` bind mount
is the authoritative image location. Files in that folder are ignored
by Git, except structural `.gitkeep` placeholders.

## What an eventual project tape-map tool would add

The desired operator experience is a single, read-only report that
can **dump tape structure** without involving JES, MVS jobs or a
mounted virtual drive. Before writing another parser, first test
whether `hetmap -a`, `-f` and `-t` already answer the need.

If those reports are insufficient, propose an independent AWS
structure inspector, separate from distribution production:

1. Accept only an explicitly named existing image; read only.
2. Identify AWS header records, physical block lengths and positions;
   enumerate tape marks and logical tape-file boundaries.
3. Extract known IBM standard VOL/HDR/EOF/EOV label fields, retaining
   unknown or malformed labels in a raw diagnostic view.
4. Flag malformed/truncated AWS headers, invalid lengths, unexpected
   tape-mark patterns and suspicious file counts; never repair data.
5. Show simple operator output (volume, file number, dataset, DCB,
   block counts, tape-mark positions) and optional detailed records;
   consider machine-readable output if release validation needs it.
6. Keep the parser independent of MVS dataset content interpretation:
   IEBCOPY unload records must not be confused with the original
   PDS-member records. Do not overclaim verification from label text.
7. Never automatically initialize, truncate, mount, reposition,
   unmount or rewrite an image; never store tape images in Git.
8. Test parser logic on small synthetic AWS fixtures, corrupted
   headers, duplicate marks, and a separate known-good MVS image.

Only implement this after confirming which detail is missing from
Hercules itself. The full physical map is a **future design choice**,
not required to accept the completed single-PDS round trip.

## References

- Accepted run: `create-tape/scratch-pds-roundtrip-acceptance-20261108.md`.
- Hercules Operations and Utilities guide, HETMAP section 5.17
  (options, mapping and semantics):
  https://codex.retro1.org/_media/ibm:hercules:herculesoperationsandutilities.pdf
- Emulator documentation for AWS format and tape marks:
  https://hercules-390.github.io/html/hercconf.html
