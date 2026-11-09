# Multi-dataset tape writing, retention and append behavior — discussion (8 November 2026)

**Status:** Deferred experiment and producer-design guidance. **No multi-dataset append test has
been executed or approved for live MVS operation.** This record captures discussion following
the accepted single-dataset FB80 documentation-PDS and relocatable object-library tape
round trips. It creates no official milestone or march and authorizes no JES job, media
mount, tape write, or resident dataset change.

## Observed one-dataset MVS evidence

The following is observed evidence, *not* proof of why the device was unloaded:

- `TO02UNLD` JOB **2486** wrote one standard-labeled IEBCOPY object-PDS unload
  dataset `HERC02.BCTO01` at MVS tape unit `480`, VOLSER `BTO001`, to
  `mvs-state/tape/bcpl-objtest-20261108-01.aws`. IEBCOPY RC=0000.
- The job's output DD specified `DISP=(NEW,KEEP)`. `KEEP` preserves the
  dataset's disposition; it does **not** request that removable media remain mounted.
- After the write, a fresh Hercules `devlist` showed `0:0480 3420 *`,
  and MVS `D U,TAPE` showed `480 3400 O-NRD` with `/REMOV` in the unit report.
  Thus **the image was no longer mounted/ready**. This is consistent with normal
  tape volume release/demount at step end, but the supplied logs did not contain
  the precise MVS demount command/event; do **not** claim the causal sequence
  was independently traced.
- `hetmap --all` then identified `VOL1 BTO001`, `HDR1/EOF1 HERC02.BCTO01`,
  `HDR2/EOF2` record format V, `BLKSIZE=820`, `LRECL=816`, with
  **52 data blocks**. The full AWS image had **four Hercules physical tape
  files**: header labels (3 blocks), unload data (52), EOF labels (2), and
  a terminal empty file (0). This represents **one logical MVS dataset**.
- The operator explicitly remounted the **same already-written** AWS image using
  `tools/mvs/mvs-console tape mount 0480 bcpl-objtest-20261108-01.aws`
  (without `hetinit`). Hercules then showed the image `[1:00000000] IO[0] open`;
  MVS reported unit `480` `O`. `TO03REST` JOB **2488** completed RC=0000
  and the restored PDS was independently inventoried.
- The earlier documentation-PDS experiment showed similar post-write
  `*` / `O-NRD` and successful explicit remount/readback.
  See the [FB80 PDS acceptance](create-tape/scratch-pds-roundtrip-acceptance-20261108.md)
  and [object-library acceptance](create-tape/object-library-tape-roundtrip-acceptance-20261108.md).

**Not yet observed:** A second *logical* standard-labeled MVS dataset written to
the same tape, a controlled tape retention between write steps, or any safe
post-failure append/resume procedure.

## Concepts to keep separate

1. **Sequential production on a new blank volume:** writing multiple logical
   datasets (`BCPL.BT0001`, `BCPL.BT0002`, ...) in order onto a **new**
   tape. This is required for the intended distribution producer.
2. **Continuing across execution boundaries:** arranging for the next
   dataset write in a later step of the same job, or in a separate JES
   job, with the correct mount, volume, labels, and position.
3. **Appending to an existing partially or fully written volume:**
   adding data without replacing earlier datasets. This is a stronger
   and riskier operation; particularly after failure, it requires a
   verified integrity, positioning and recovery protocol. It is **not**
   required for normal immutable release publication.
4. **Hercules media state versus MVS state:** the host AWS file existing,
   the Hercules 3420 being configured/mounted via `devinit`, and MVS
   allocating/closing a volume are distinct. `attach/detach` are not
   synonyms for mounting/unmounting the tape image.
5. **Logical dataset sequence versus physical files:** the approved
   position-based `BCPL.BTnnnn` convention uses 1-based MVS **logical
   dataset** sequence, matched by standard-label
   `LABEL=(n,SL)`. It does **not** match Hercules `hetmap`
   physical file numbers. One logical dataset already produced four
   physical files in the accepted test.

## Questions for the deferred live experiment

| Question | Variants / evidence needed |
| --- | --- |
| End-of-step demount | Observe Hercules `devlist`, MVS `D U,TAPE`, and operator console/messages before, between and after allocation/close. Verify how and when the written volume is unloaded. |
| `VOLUME=RETAIN` | Check whether it retains the specific volume for another step and under what MVS 3.8J limits; not assume that it holds an AWS image mounted across JES jobs. |
| `DISP=PASS` | Determine whether passing a dataset/volume between steps changes retention and positioning, compared with `DISP=(NEW,KEEP)`. Do not assume it works across unrelated jobs. |
| Writing later logical datasets | Test explicit standard-label dataset sequences `LABEL=(1,SL)` and `LABEL=(2,SL)`, checking whether MVS locates the correct position and keeps both existing data and labels intact. |
| Step and job boundaries | Compare two write steps in a single job against two independently submitted jobs; record mount/demount, volume allocation and possible operator actions. |
| Physical tape structure | Inspect `VOL1`, `HDR1/HDR2`, `EOF1/EOF2`, data blocks, filemarks and `hetmap --all` physical file numbers after each successful write. |
| Independent restoration | Read back **both** logical datasets into new scratch DASD datasets; compare attributes, records/member inventories and utility RCs. |
| Failure/recovery | In a subsequent *separately approved* negative experiment, characterize failure/timeout, partial labels, wrong position, a missing/unready tape, or interruption. Do **not** test destructive resume on the successful two-dataset image. |
| Safety and production design | Determine whether the producer can run independent jobs or must generate a coordinated multi-step job; define stop/fail-closed behavior and preservation of partial images. |

`VOLUME=RETAIN`, `DISP=PASS`, `LABEL=(n,SL)` and the consequences
of different step/job arrangements are **candidate behaviors to verify**
against the MVS 3.8J documentation and the real TK5 guest. No exact
syntax, retention guarantee or automatic append behavior is accepted
by this note.

## Suggested bounded test sequence (not authorization)

1. **Design/review first:** inspect the installed MVS/JCL manuals, volume
   and labeling conventions, and existing operator safeguards; settle
   source fixtures, new unique six-character VOLSER and AWS filename,
   MVS unit, exact JCL, source/restore PDS names and acceptance reports.
   Pin Git revision; verify the scratch image, VOLSER and output
   datasets do not already exist.
2. **Start clean:** create a dedicated blank AWS tape **only once**, as
   the actual Hercules runtime UID/GID to avoid the earlier
   `root:root` permission failure. Inspect the initialized image,
   mount with an explicit operator confirmation, and independently
   check Hercules and MVS ready state. Never reinitialize after writing.
3. **First logical dataset:** write a small known sequential fixture as
   `BCPL.BT0001`, standard-label dataset sequence 1, with an
   operator-approved JCL job/step. Record job, step RC, console status,
   label and tape-map evidence after close.
4. **Second logical dataset:** using a reviewed retention/positioning
   method, write a second known fixture as `BCPL.BT0002`, dataset
   sequence 2, **without overwriting dataset 1**. If any prerequisite
   is unclear, **stop**. Observe status between steps/jobs rather than
   silently remounting or retrying.
5. **Read/compare:** independently inspect all volume/dataset labels and
   physical filemarks, then restore **both** datasets to distinct new
   scratch DASD targets and compare contents/attributes. Preserve
   the media SHA-256 and all job/console results.
6. **Compare variants:** on **separate fresh scratch media**, repeat
   the relevant scenarios for same-job multi-step versus separate-job
   operations, `VOLUME=RETAIN`, and `DISP=PASS`. Never use a
   previously accepted media image for retries, destructive tests or
   variation experiments.
7. **Only afterward** decide producer job structure and recovery policy
   from observed results. Obtain separate owner approval for every
   operational action and any later negative test.

The two-fixture proposal is **diagnostic**. It does not override the
release convention in which `BCPL.BT0001` is reserved for a readable
installation bootstrap and `BCPL.BT0002` for installation JCL.
A production-like test may instead use those payload types, provided
the experiment is explicitly designed and authorized.

## Producer architecture implications and decisions

- **Agreed preference:** Generate a complete **new** release tape
  sequentially from its frozen release manifest, not by modifying a
  previously published tape image.
- The manifest remains the **only** inventory for logical sequence,
  `BCPL.BTnnnn` alias, source/installed dataset mapping, method,
  DCB and validation rules; producer and installer JCL derive from it.
- The producer must verify labels and the actual logical sequence,
  not confuse them with physical `hetmap` file indices. It must
  check completion, mount state, correct VOLSER, dataset positioning,
  read-back, and integrity at each appropriate checkpoint.
- **A successful first write does not imply a safe next append.** Media
  retention alone does not guarantee safe repositioning or preservation
  of previous datasets.
- **Recovery policy is deliberately open.** Until negative testing
  demonstrates otherwise, treat an incomplete, timed-out or partly
  written image as an invalid candidate. Prefer restarting production
  on a **new** unique scratch image rather than attempting to resume
  or append after a failure.
- Do not automatically remount, reinitialize, seek, retry writes, or
  append to accepted media in a launcher. The operator must see
  meaningful state and authorize the appropriate operation.
- Acceptance of a two-dataset scratch experiment would prove that
  bounded operation only. Multi-dataset release production and
  clean-target installation would require their own end-to-end tests.

## Related project records

- [Native compiler distribution decisions](native-cambridge-compiler-distribution-decisions-20261108.md) —
  approved `BCPL.BTnnnn` logical dataset aliases and manifest authority.
- [Tape production automation design](tape-production-automation-design-discussion-20261103.md) —
  earlier proposal to fail closed on incomplete output and produce
  from a frozen release inventory.
- [Tape operations discussion](tape-operations-design-discussion-20261103.md) —
  Hercules device/media/MVS allocation distinction and safety gates.
- [Object-library round-trip acceptance](create-tape/object-library-tape-roundtrip-acceptance-20261108.md) —
  real MVS one-dataset observed demount/remount, labels and comparison.
