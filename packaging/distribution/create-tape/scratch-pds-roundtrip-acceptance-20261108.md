# Scratch PDS tape round-trip acceptance — 8 November 2026

**Status:** ACCEPTED — bounded, operator-executed FB80 PDS round trip on
MVS 3.8J/TK5. This is not a full distribution release, a load-library
acceptance, or a clean-target installation qualification.

## Evidence and authority

The operator executed the four Git-controlled JCL bodies from
`packaging/distribution/create-tape/jcl/` using
`packaging/distribution/create-tape/scripts/submit-scratch-job`.
The JCL was at GitHub `main` commit
`aab0279d9679b653230c8680a8c17190a797b228`.
The previous JCL/test-source commit was `9a9e173f67b79f3288e5e3b221bac9b7687aa6b9`.

The following values are taken from operator-provided console, JES
job-summary, `dspal` and `hetmap` outputs, not from a simulated test.
The original full JES SYSPRINT listings were not provided for independent
review; the recorded step RCs and inventories are the evidence available
in this discussion.

| Stage | JES job | Utility / step | Result |
| --- | ---: | --- | --- |
| `TP01PRE` | 2469 | IEBCOPY / COPY | RC=0000 |
| `TP02UNLD` | 2472 | IEBCOPY / UNLOAD | RC=0000 |
| `TP03REST` | 2474 | IEBCOPY / RESTORE | RC=0000 |
| `TP04COMP` | 2477 | IEBCOMPR / COMPARE | RC=0000 |

All four job summaries reported SUCCESS, highest RC 0000.
The source and restored PDS inventories, separately obtained by live
`dspal ls`, each listed the same seven members:

    COMPILE DATASETS INSTALL LICENSE README RELEASE VERIFY

Source: `HERC02.BCPL.DIST.DOCS` (read-only).
Scratch copy: `HERC02.BCPL.TPTEST.SRC`.
Restored copy: `HERC02.BCPL.TPTEST.RESTORE`.
Both scratch PDSes were newly allocated and cataloged on `TSO003`.
The restored PDS was independently inspected using `dspal stat`:

    DSORG=PO RECFM=FB LRECL=80 BLKSIZE=800

`TP04COMP` ran `COMPARE TYPORG=PO` against the two scratch PDSes and
returned RC=0000. This is the accepted MVS comparison evidence for the
seven-member fixture; it is not a generic proof that arbitrary object
or load modules will survive the same transfer.

## Virtual tape and physical label evidence

- Host media: `mvs-state/tape/bcpl-pdstest-20261108-01.aws`, created
  exclusively for this test. It was never committed to Git.
- Existing `mvs-state/tape/bcpl01.aws` was not used or overwritten.
- Emulated tape: Hercules `0480`, model `3420`; MVS unit `480`.
- Initialized via installed `hetinit` version `4.9.1.0-SDL` with
  `-d -i`, VOLSER `BTP001`; `hetinit` RC=0.
- Mounted through `tools/mvs/mvs-console tape mount` (`devinit`).
- The tape image was approximately 16 KiB after the write.
- Recorded SHA-256 following TP02UNLD:
  `1aece83f8130b342f2e09e5d5cd87980f4fe17a6f0db77cabf75c82e7f289666`.
  The same SHA-256 was observed again before the restore.
- `hetmap -l` on the resulting AWS image returned RC=0 and identified
  `VOL1`: BTP001, `HDR1`: HERC02.BCTP01, volume sequence 0001,
  dataset sequence 0001, `HDR2`, `EOF1` and `EOF2`.
- `HDR2` reported Record Format V, Block Attribute S,
  BLKSIZE 00820, LRECL 00816, and job/step `TP02UNLD/UNLOAD`.
  This is the IEBCOPY sequential *unload* representation, not the
  FB80 DCB of the original and restored PDS.
- `EOF1` recorded 25 data blocks. The tape record count and AWS
  filemarks were not independently enumerated in the supplied output.
- The pre-write `hetinit` image had a dummy `HDR1` dataset identifier
  `00000000000000000`. After successful writing the actual
  `HERC02.BCTP01` labels replaced that placeholder in the observed map.

After TP02UNLD, a fresh Hercules `devlist` reported `0:0480 3420 *`
and MVS `D U,TAPE` reported `480 3400 O-NRD`: the tape was no longer
mounted, despite successful IEBCOPY RC=0. The operator explicitly
remounted the **same image without reinitializing it** for TP03REST.
Before that restore, Hercules showed the image mounted and MVS status
`O` (online). No post-TP03REST tape-device status was supplied; do not
infer its current mount state.

## Reproducible manual operating lessons

1. Distinguish *host image*, *Hercules mounted media*, and *MVS/JES
   allocation*. An MVS online drive or an AWS file alone is not proof
   that the correct volume is mounted and addressable.
2. Verify an unused image path and reserved six-character VOLSER before
   running `hetinit`. Never reinitialize the written image before
   readback. The existing image is **not** a disposable retry target.
3. Check the actual installed utility help, runtime file ownership and
   `mvs-state/tape/` permissions. The Hercules runtime user must be able
   to write the file.
4. Use the repository `mvs-console` interface to mount media, with a
   fresh device-status inquiry and an interactive confirmation. A
   `devinit` command changes Hercules media, not guest MVS allocation.
5. Check MVS `D U,TAPE` separately: `O-NRD` means online/not ready,
   `O` means online/ready; neither alone proves a particular VOLSER.
6. Submit each independent JCL job with the existing authenticated
   `dspal-core.py` method, keeping passwords in ignored
   `config/dspal.local.yaml`. `tools/mvs/submit-jcl` transports a
   *complete* deck; it does not itself supply the JOB card.
7. Use `dspal stat` for live catalog/DCB checks and `dspal ls` for
   member inventories. `dspal list` shows the configured manifest;
   `dspal list --probe` is unsupported. `dspal status --probe` is
   a different operation and submits a JES status probe.
8. Preserve JES job numbers, step RCs and the full reports. An HTTP
   request or launcher success does not prove that the payload worked.
9. A zero IEBCOPY RC plus matching member names/DCBs is not enough by
   itself to assert content equality; perform the independent IEBCOMPR
   test and inspect its return code/messages.
10. A successfully written tape may be automatically unmounted by the
    guest/emulator path. Before a new tape job, inspect both Hercules
    and MVS, remount intentionally when needed, and never blindly retry
    a failed, timed-out or partially completed tape write.
11. Use `hetmap` to inspect labels and file structure independently
    of the MVS utilities. Do not confuse label block-count metadata
    with a complete physical filemark/block inventory.
12. Keep all AWS/HET image files under ignored `mvs-state/` or
    `workarea/`. Never commit virtual tapes or local credentials.
    Store only source, tests, redacted instructions and text evidence
    in Git.

## Acceptance boundary and subsequent verification

**Accepted now:** one new AWS tape image with an IBM-standard-labeled
single IEBCOPY unload file, written by MVS 3.8J; remounted and restored
to a different FB80 PDS; verified with MVS IEBCOMPR RC=0.

**Not established by this experiment:**

- IEBGENER sequential FB80 documentation as first physical tape file
  (the future installer bootstrap contract).
- Multiple logical tape datasets, sequence numbers and filemarks on
  one AWS volume.
- FB80 relocatable object libraries and subsequent successful
  assemble/link/run of restored members.
- RECFM=U MVS load libraries and load/execute of restored programs.
- Installation into a clean MVS environment using only tape-resident
  text/JCL/utilities; no WSL/Git/Python requirement on the consumer.
- Release manifest completeness, provenance, acceptance of included
  components, or an installable Cambridge Compiler distribution.
- Negative tests (wrong VOLSER, truncated data, tape not ready,
  missing file, accidental overwrite refusal).
- A separate byte-level AWS structure report enumerating filemarks,
  physical record lengths and boundaries.

Do not infer an official project milestone or production release
closure from this bounded scratch test. Follow the separately
documented distribution design gates.

## Verification pointers

- `create-tape/jcl/TP01PRE.jcl` through `TP04COMP.jcl`.
- `create-tape/tests/test_scratch_tape_jcl.py` and
  `create-tape/tests/test_submit_scratch_job.py`:
  12 offline tests passed in the operator's run (structural and
  mock-submission tests, not MVS tape tests).
- `create-tape/README.md`: operator procedure and safeguards.
- `tape-inspection-capabilities-20261108.md`: existing Hercules
  tape-map capabilities and possible project-native extensions.
- IBM *OS/VS2 MVS Utilities*, Release 3.8 (GC26-3902-1),
  IEBCOPY unload/load examples 13–14 and IEBCOMPR.
