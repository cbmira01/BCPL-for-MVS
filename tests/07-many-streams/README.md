# 07 - Many simultaneous streams

This regression stresses ICINT V16's GETMAIN-managed generic input streams independently of SYN's nested `GET` mechanism.

The BCPL test program opens twelve ordinary DDNAME input streams (`DD01` through `DD12`) with `FINDINPUT` and keeps all twelve handles live simultaneously. It verifies that every open succeeds, then selects each stream in turn, reads its identifying text, prints it, and closes the stream with `ENDREAD`.

Each fixture contains one short record:

- `DD01` -> `STREAM 01`
- ...
- `DD12` -> `STREAM 12`

Run from the repository root:

```sh
tools/compile-and-run \
    --listing heavy \
    --results \
    --job-name MANYSTRM \
    --dd DD01=tests/07-many-streams/dd01.txt \
    --dd DD02=tests/07-many-streams/dd02.txt \
    --dd DD03=tests/07-many-streams/dd03.txt \
    --dd DD04=tests/07-many-streams/dd04.txt \
    --dd DD05=tests/07-many-streams/dd05.txt \
    --dd DD06=tests/07-many-streams/dd06.txt \
    --dd DD07=tests/07-many-streams/dd07.txt \
    --dd DD08=tests/07-many-streams/dd08.txt \
    --dd DD09=tests/07-many-streams/dd09.txt \
    --dd DD10=tests/07-many-streams/dd10.txt \
    --dd DD11=tests/07-many-streams/dd11.txt \
    --dd DD12=tests/07-many-streams/dd12.txt \
    asm/icintv16.asm \
    tests/07-many-streams/main.bcpl
```

Expected program output includes:

```text
OPENED 12 STREAMS
DD1 = STREAM 01
DD2 = STREAM 02
DD3 = STREAM 03
DD4 = STREAM 04
DD5 = STREAM 05
DD6 = STREAM 06
DD7 = STREAM 07
DD8 = STREAM 08
DD9 = STREAM 09
DD10 = STREAM 10
DD11 = STREAM 11
DD12 = STREAM 12
ALL 12 STREAMS READ AND CLOSED
```

A successful run demonstrates that the generic stream ceiling is no longer tied to V15's fixed descriptor pool and also exercises repeated unlink/FREEMAIN operations while other dynamic stream objects remain live.
