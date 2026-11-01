# Milestone QSAM — Q.4 numbered punch regression diagnostic (30 October 2026)

**March:** **Q.4 — SYSOUT devices**
**Status:** **CASE 175 NATIVE PASS AND DELAYED PUNCH OUTPUT VERIFIED; FIRST FOCUSED RUNNER FAILED; Q.4 REMAINS OPEN.**

## Operator-reported focused production panel

The owner ran `tools/bootstrap/run-production-regression 163 176` on GitHub
`main` commit `9d8b4e0af6214b5ef210ab98b63aade097259fb2`.
All offline gating and numbering checks passed. The native focused runner
reported **13 PASS, 1 FAIL (175), 0 SKIP, 14 TOTAL, RC=1**; the
full 00–176 panel was correctly skipped. Cases 163 and 170 verified
QUERY capability bitmap `7`, and case 176 FBA133 printer passed.

For case 175, the resident demoted Cambridge compiler succeeded in
**JOB 7754**, generating assembler; the native **JOB 7755 Q4PUNCH**
reported `JOB RESULT: SUCCESS`, ten IFOX/IEWL/BCPL/IFOX execution
steps all `RC=0000`, zero assembler flags/severity and
the two required exact application PASS markers:

```text
BCPLQSAM Q4 FB80 PUNCH DUAL WRITE PASS
BCPLQSAM Q4 FB80 TEMP EXACT 3 PASS
```

The independent IFOX verifier confirmed three exact FB80 temporary
QSAM records and EOF. Nevertheless, the numbered runner reported
`Hercules punch capture: 0 new bytes; NOT VERIFIED` because
`mvs-state/pch/pch00d.txt` remained exactly **172 bytes**,
unchanged from the earlier standalone JOB 7726.
This was a **real failure of timely JES2 device delivery**, not an
accepted 175 regression PASS.

## MVS/JES2 diagnosis and recovery

Read-only JES2 operator commands `$DU,PUNS`, `$DN,Q=PPU`,
and `$D J7755` issued via the resident Hercules port 8038 showed:

```text
$HASP000 PUNCH1 00D PAUSED F=0001,AUTOM P=Y R=LOCAL S=N LIM=0-* Q=B
$HASP000 Q4PUNCH PRT LOCAL PUN LOCAL PRIO 1 ANY
```

The owner explicitly sent `$S PUN1` once via the same Hercules console.
The resident MVS console then reported:

```text
JOB 7755 $HASP150 Q4PUNCH ON PUNCH1 3 CARDS
         $HASP175 PUNCH1 PAUSED
JOB 7755 $HASP250 Q4PUNCH IS PURGED
```

The ASCII punch capture grew from **172 to 344 bytes**.
The **new 172-byte segment** matched exactly the established
three FB80 card images and blank separator, with
`JOB 7755 punch image: PASS` and inspection RC=0.
No recompilation, new JES job, permanent dataset change or
Hercules device change was required to recover the queued output.

The punch is configured to pause after a group (`P=Y`), so
`PUNCH1` returned to PAUSED. This explains why the original native
regression runner's 12-second capture check had seen no new bytes.

## Regression-harness follow-up

The native runner now offers an **operator opt-in** `Q4_PUNCH_RESUME=1`
to send exactly one `$S PUN1` via Hercules HTTP port 8038 after
the case-175 JES job has passed native step/marker verification and
the expected punch capture has not yet appeared. This opt-in can
release other eligible class-B queued output; it does not change
the JES2 pause policy and is not an implied authorization for
unrelated system operations. The result still requires exact
Hercules capture byte comparison.

**No success is claimed for a rerun yet.** The required fresh
focused 163–176 and full 00–176 native panels remain pending.
The operator's local logs, console and capture artifacts are not
checked into Git; this record summarizes the directly supplied evidence.
